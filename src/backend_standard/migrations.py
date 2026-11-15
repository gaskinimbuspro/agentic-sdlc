"""PostgreSQL reference migrations: atomic, serialized, checksum-verified."""

import hashlib
from pathlib import Path

import psycopg


def migrate(conn: psycopg.Connection[tuple[object, ...]], directory: Path) -> None:
    if not directory.is_dir():
        raise ValueError("Migration directory is missing")
    paths = sorted(directory.glob("[0-9][0-9][0-9]_*.sql"))
    versions = [path.name[:3] for path in paths]
    if not paths or len(set(versions)) != len(versions):
        raise ValueError("Migrations must be nonempty with unique version numbers")
    scripts = [(path.name, path.read_text()) for path in paths]
    with conn.transaction():
        conn.execute("SELECT pg_advisory_xact_lock(278401)")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (name text PRIMARY KEY, sha256 text NOT NULL)"
        )
        history = [
            (str(row[0]), str(row[1]))
            for row in conn.execute(
                "SELECT name,sha256 FROM schema_migrations ORDER BY name"
            ).fetchall()
        ]
        names = [name for name, _ in scripts]
        if [name for name, _ in history] != names[: len(history)]:
            raise ValueError(
                "Applied migration history was removed, renamed or backfilled"
            )
        applied = dict(history)
        for name, body in scripts:
            digest = hashlib.sha256(body.encode()).hexdigest()
            if name in applied:
                if applied[name] != digest:
                    raise ValueError("Applied migration checksum changed: " + name)
                continue
            conn.execute(body)
            conn.execute("INSERT INTO schema_migrations VALUES (%s,%s)", (name, digest))
