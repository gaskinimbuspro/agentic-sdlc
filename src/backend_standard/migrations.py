"""PostgreSQL reference migrations: atomic, serialized, checksum-verified."""

import hashlib
from pathlib import Path

import psycopg


def migrate(conn: psycopg.Connection[tuple[object, ...]], directory: Path) -> None:
    with conn.transaction():
        conn.execute("SELECT pg_advisory_xact_lock(278401)")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (name text PRIMARY KEY, sha256 text NOT NULL)"
        )
        for path in sorted(directory.glob("[0-9][0-9][0-9]_*.sql")):
            body = path.read_text()
            digest = hashlib.sha256(body.encode()).hexdigest()
            existing = conn.execute(
                "SELECT sha256 FROM schema_migrations WHERE name=%s", (path.name,)
            ).fetchone()
            if existing:
                if existing[0] != digest:
                    raise ValueError("Applied migration checksum changed: " + path.name)
                continue
            conn.execute(body)
            conn.execute(
                "INSERT INTO schema_migrations VALUES (%s,%s)", (path.name, digest)
            )
