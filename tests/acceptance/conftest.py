import json
import os
import secrets
import socket
import subprocess
import time
from pathlib import Path

import httpx
import psycopg
import pytest

from backend_standard.migrations import migrate

ROOT = Path(__file__).resolve().parents[2]


class SafeFixture(tuple):
    """Pytest tracebacks must not render generated passwords/signing keys."""

    def __repr__(self):
        return "<reference fixture: credentials redacted>"


@pytest.fixture(scope="session")
def database():
    config = {
        "host": os.environ["DB_HOST"],
        "port": os.environ["DB_PORT"],
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "connect_timeout": 3,
    }
    with psycopg.connect(**config, autocommit=True) as conn:
        migrate(conn, ROOT / "reference/migrations")
        # A fixed role is scoped to this disposable database/container only.
        from psycopg import sql

        password = secrets.token_urlsafe(32)
        conn.execute(
            sql.SQL("CREATE ROLE backend_app LOGIN PASSWORD {}").format(
                sql.Literal(password)
            )
        )
        conn.execute(
            "GRANT CONNECT ON DATABASE "
            + sql.Identifier(config["dbname"]).as_string(conn)
            + " TO backend_app"
        )
        conn.execute("GRANT USAGE ON SCHEMA public TO backend_app")
        conn.execute("GRANT SELECT,INSERT ON customers,customer_audit TO backend_app")
    yield SafeFixture((config, password))


@pytest.fixture(scope="session")
def service(database, tmp_path_factory):
    config, password = database
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    key = secrets.token_urlsafe(48)
    env = dict(
        os.environ,
        DB_USER="backend_app",
        DB_PASSWORD=password,
        JWT_KEY=key,
        PORT=str(port),
    )
    command = json.loads(os.environ["REFERENCE_COMMAND"])
    log = tmp_path_factory.mktemp("service") / "service.log"
    with log.open("w") as output:
        process = subprocess.Popen(command, env=env, stdout=output, stderr=output)
        url = f"http://127.0.0.1:{port}"
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    pytest.fail(
                        "Reference process exited before readiness: "
                        + log.read_text()[-3000:]
                    )
                try:
                    if httpx.get(url + "/health/ready", timeout=1).status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.1)
            else:
                pytest.fail("Reference did not become ready")
            yield SafeFixture((url, key, log))
        finally:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
                pytest.fail("Reference exceeded the graceful shutdown deadline")


@pytest.fixture(autouse=True)
def clean_data(database):
    config, _ = database
    with psycopg.connect(**config, autocommit=True) as conn:
        conn.execute("DROP TRIGGER IF EXISTS force_audit_failure ON customer_audit")
        conn.execute("TRUNCATE customer_audit,customers")
    yield
