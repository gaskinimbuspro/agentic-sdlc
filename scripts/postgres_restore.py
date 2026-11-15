"""Exercise PostgreSQL logical recovery using independent disposable instances."""

import hashlib
import json
import os
import secrets
import subprocess
import time
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from pathlib import Path

import psycopg
from reference_acceptance import POSTGRES_IMAGE

from backend_standard.migrations import migrate

ROOT = Path(__file__).resolve().parents[1]
DATABASE = "recovery_reference"
CUSTOMER = "cbd33c84-7f91-4c3e-83ba-6182f0acf2c5"
TENANT = "e61a6983-e97f-4733-9e5f-6dc86c545ae1"


@contextmanager
def database() -> Iterator[tuple[str, psycopg.Connection]]:
    password = secrets.token_urlsafe(32)
    container = subprocess.check_output(
        [
            "docker",
            "run",
            "--rm",
            "--detach",
            "-p",
            "127.0.0.1::5432",
            "--env",
            "POSTGRES_PASSWORD",
            "--env",
            "POSTGRES_DB",
            POSTGRES_IMAGE,
        ],
        env=dict(os.environ, POSTGRES_PASSWORD=password, POSTGRES_DB=DATABASE),
        text=True,
        timeout=180,
    ).strip()
    try:
        port = (
            subprocess.check_output(
                ["docker", "port", container, "5432/tcp"], text=True, timeout=10
            )
            .strip()
            .rsplit(":", 1)[1]
        )
        deadline = time.monotonic() + 45
        while True:
            try:
                connection = psycopg.connect(
                    host="127.0.0.1",
                    port=port,
                    dbname=DATABASE,
                    user="postgres",
                    password=password,
                    connect_timeout=1,
                    autocommit=True,
                )
                break
            except psycopg.OperationalError:
                if time.monotonic() >= deadline:
                    raise RuntimeError(
                        "Recovery database did not become ready"
                    ) from None
                time.sleep(0.2)
        with connection:
            yield container, connection
    finally:
        subprocess.run(
            ["docker", "rm", "--force", container],
            check=True,
            timeout=20,
            stdout=subprocess.DEVNULL,
        )


def snapshot(connection: psycopg.Connection) -> dict[str, list]:
    return {
        "customers": connection.execute(
            "SELECT id, tenant_id, name, email FROM customers ORDER BY id"
        ).fetchall(),
        "audit": connection.execute(
            "SELECT customer_id, created_at FROM customer_audit ORDER BY customer_id"
        ).fetchall(),
        "migrations": connection.execute(
            "SELECT * FROM schema_migrations ORDER BY 1"
        ).fetchall(),
    }


def restore(container: str, archive: bytes) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            container,
            "pg_restore",
            "--single-transaction",
            "--exit-on-error",
            "--no-owner",
            "--no-privileges",
            "-U",
            "postgres",
            "-d",
            DATABASE,
        ],
        input=archive,
        capture_output=True,
        check=False,
        timeout=60,
    )


def main() -> None:
    with ExitStack() as stack:
        source_id, source = stack.enter_context(database())
        target_id, target = stack.enter_context(database())
        migrate(source, ROOT / "reference/migrations")
        with source.transaction():
            source.execute(
                "INSERT INTO customers VALUES (%s, %s, %s, %s)",
                (CUSTOMER, TENANT, "Recovery fixture", "restore@example.invalid"),
            )
            source.execute(
                "INSERT INTO customer_audit (customer_id) VALUES (%s)", (CUSTOMER,)
            )
        expected = snapshot(source)
        backup_started = time.monotonic()
        archive = subprocess.check_output(
            [
                "docker",
                "exec",
                source_id,
                "pg_dump",
                "-Fc",
                "-U",
                "postgres",
                "-d",
                DATABASE,
            ],
            timeout=60,
        )
        backup_seconds = time.monotonic() - backup_started
        # A truncated archive must fail before a valid restore can be trusted.
        corrupted = restore(target_id, archive[: len(archive) // 2])
        if corrupted.returncode == 0:
            raise RuntimeError("A damaged archive was accepted")
        if target.execute("SELECT to_regclass('public.customers')").fetchone() != (
            None,
        ):
            raise RuntimeError("A failed restore left application objects")
        restore_started = time.monotonic()
        result = restore(target_id, archive)
        result.check_returncode()
        if snapshot(target) != expected:
            raise RuntimeError("Restored data or migration history diverged")
        try:
            target.execute(
                "INSERT INTO customers VALUES (%s, %s, %s, %s)",
                (
                    "bb5e9c47-ff14-4d21-8d0c-3fde11fc538a",
                    TENANT,
                    "Duplicate",
                    "restore@example.invalid",
                ),
            )
        except psycopg.errors.UniqueViolation as error:
            if error.diag.constraint_name != "customers_tenant_email":
                raise
        else:
            raise RuntimeError(
                "Restored uniqueness constraint did not reject duplicate"
            )
        restore_seconds = time.monotonic() - restore_started
    report = {
        "candidate_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=5
        ).strip(),
        "postgres_image": POSTGRES_IMAGE,
        "archive_sha256": hashlib.sha256(archive).hexdigest(),
        "archive_bytes": len(archive),
        "backup_seconds": round(backup_seconds, 3),
        "restore_and_validation_seconds": round(restore_seconds, 3),
        "checks": {
            "truncated_archive_rejected": "passed",
            "failed_restore_left_no_customer_table": "passed",
            "customer_audit_and_migrations_restored": "passed",
            "restored_unique_constraint_enforced": "passed",
        },
        "status": "passed",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
