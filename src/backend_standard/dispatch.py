"""Single-host reference for exclusive task attempts and external operation intents."""

import re
import secrets
import sqlite3
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from backend_standard.gates import Rejected, require, text


@dataclass(frozen=True)
class Claim:
    worker: str
    attempt: int
    token: str = field(repr=False)
    expires_at: float


@dataclass(frozen=True)
class Operation:
    state: str
    external_id: str | None


class DispatchLedger:
    """Use an operator-owned database on local disk and a trusted host clock."""

    def __init__(self, path: Path, clock: Callable[[], float] = time.time) -> None:
        self.path = path
        self.clock = clock
        with self._transaction() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    packet_digest TEXT NOT NULL,
                    attempt_budget INTEGER NOT NULL,
                    lease_seconds INTEGER NOT NULL,
                    candidate_sha TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS attempts (
                    task TEXT NOT NULL REFERENCES tasks(id),
                    attempt INTEGER NOT NULL,
                    request TEXT NOT NULL,
                    worker TEXT NOT NULL,
                    token TEXT NOT NULL,
                    expires REAL NOT NULL,
                    PRIMARY KEY (task, attempt),
                    UNIQUE (task, request),
                    UNIQUE (token)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS operation_intents (
                    key TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL,
                    external_id TEXT
                )
                """
            )

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("BEGIN IMMEDIATE")
            with connection:
                yield connection
        finally:
            connection.close()

    def register(
        self, task: str, packet_digest: str, attempt_budget: int, lease_seconds: int
    ) -> None:
        text(task, "Task ID")
        require(
            re.fullmatch(r"[0-9a-f]{64}", packet_digest), "Invalid ready-packet digest"
        )
        for value in (attempt_budget, lease_seconds):
            require(
                type(value) is int and value > 0,
                "Positive attempt and lease budgets required",
            )
        with self._transaction() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO tasks VALUES (?, ?, ?, ?, NULL)",
                (task, packet_digest, attempt_budget, lease_seconds),
            )
            existing = connection.execute(
                "SELECT packet_digest, attempt_budget, lease_seconds FROM tasks WHERE id = ?",
                (task,),
            ).fetchone()
            require(
                tuple(existing) == (packet_digest, attempt_budget, lease_seconds),
                "Task registration conflicts with the protected packet",
            )

    def claim(self, task: str, worker: str, request: str) -> Claim:
        """Retries using the same request return the same still-active claim."""
        text(worker, "Worker ID")
        text(request, "Claim request ID")
        with self._transaction() as connection:
            now = self.clock()
            task_row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (task,)
            ).fetchone()
            if task_row is None:
                raise Rejected("Unknown ready task")
            require(
                task_row["candidate_sha"] is None, "Task has a candidate for review"
            )
            current = connection.execute(
                "SELECT * FROM attempts WHERE task = ? ORDER BY attempt DESC LIMIT 1",
                (task,),
            ).fetchone()
            if current is not None and current["expires"] > now:
                require(
                    (current["request"], current["worker"]) == (request, worker),
                    "Task already has an active owner",
                )
                return Claim(
                    worker, current["attempt"], current["token"], current["expires"]
                )
            expired_request = connection.execute(
                "SELECT 1 FROM attempts WHERE task = ? AND request = ?", (task, request)
            ).fetchone()
            require(expired_request is None, "Claim request has expired")
            attempt = 1 if current is None else current["attempt"] + 1
            require(attempt <= task_row["attempt_budget"], "Attempt budget exhausted")
            result = Claim(
                worker,
                attempt,
                secrets.token_urlsafe(32),
                now + task_row["lease_seconds"],
            )
            connection.execute(
                "INSERT INTO attempts VALUES (?, ?, ?, ?, ?, ?)",
                (task, attempt, request, worker, result.token, result.expires_at),
            )
            return result

    def submit(self, task: str, token: str, candidate_sha: str) -> None:
        """Stage exactly one candidate from the current owner for trusted review."""
        require(re.fullmatch(r"[0-9a-f]{40}", candidate_sha), "Invalid candidate SHA")
        with self._transaction() as connection:
            now = self.clock()
            current = connection.execute(
                "SELECT token, expires FROM attempts WHERE task = ? ORDER BY attempt DESC LIMIT 1",
                (task,),
            ).fetchone()
            require(
                current is not None
                and current["token"] == token
                and current["expires"] > now,
                "Stale or expired task claim",
            )
            staged = connection.execute(
                "UPDATE tasks SET candidate_sha = ? WHERE id = ? AND candidate_sha IS NULL",
                (candidate_sha, task),
            )
            if staged.rowcount == 0:
                previous = connection.execute(
                    "SELECT candidate_sha FROM tasks WHERE id = ?", (task,)
                ).fetchone()
                require(
                    previous["candidate_sha"] == candidate_sha,
                    "Candidate is already staged",
                )

    def reserve(self, key: str, fingerprint: str) -> Operation:
        """Reserve one external write, or require reconciliation on replay."""
        text(key, "Operation key")
        require(
            re.fullmatch(r"[0-9a-f]{64}", fingerprint), "Invalid intent fingerprint"
        )
        with self._transaction() as connection:
            created = connection.execute(
                "INSERT OR IGNORE INTO operation_intents VALUES (?, ?, NULL)",
                (key, fingerprint),
            )
            if created.rowcount:
                return Operation("reserved", None)
            record = connection.execute(
                "SELECT fingerprint, external_id FROM operation_intents WHERE key = ?",
                (key,),
            ).fetchone()
            require(
                record["fingerprint"] == fingerprint, "Conflicting operation intent"
            )
            if record["external_id"] is None:
                return Operation("reconcile", None)
            return Operation("observed", record["external_id"])

    def observe(self, key: str, fingerprint: str, external_id: str) -> None:
        """Record a verified external receipt, allowing an identical retry."""
        text(external_id, "Verified external ID")
        with self._transaction() as connection:
            updated = connection.execute(
                """
                UPDATE operation_intents SET external_id = ?
                WHERE key = ? AND fingerprint = ? AND (external_id IS NULL OR external_id = ?)
                """,
                (external_id, key, fingerprint, external_id),
            )
            require(updated.rowcount == 1, "Receipt does not match reserved intent")
