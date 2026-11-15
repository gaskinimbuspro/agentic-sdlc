"""Run the opt-in browser suite against a packaged Python API and PostgreSQL."""

import os
import socket
import subprocess
import time
from pathlib import Path

import httpx
import psycopg

from backend_standard.gates import test_counts as report_counts

from .test_customers import TENANT_A, TENANT_B, body, token

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "reference/frontend"


def test_customer_admin_browser_pilot(service, database):
    api, key, _ = service
    for tenant, label in ((TENANT_A, "Current tenant"), (TENANT_B, "Other tenant")):
        response = httpx.post(
            api + "/customers",
            headers=token(key, tenant),
            json=body(tenant, name=label + " fixture", email="fixture@example.test"),
            timeout=8,
        )
        assert response.status_code == 201
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = str(listener.getsockname()[1])
    auth = token(key, TENANT_A, exp=int(time.time()) + 600)["Authorization"]
    report = FRONTEND / "test-results/browser.xml"
    report.unlink(missing_ok=True)
    result = subprocess.run(
        ["npm", "run", "browser"],
        cwd=FRONTEND,
        env=dict(
            os.environ,
            REFERENCE_UI_API=api,
            REFERENCE_UI_TENANT=TENANT_A,
            REFERENCE_UI_AUTHORIZATION=auth,
            REFERENCE_UI_PORT=port,
        ),
        timeout=240,
        check=False,
    )
    assert result.returncode == 0
    counts = report_counts(report, "junit")
    assert counts == {"executed": 15, "failed": 0, "skipped": 0}
    config, _ = database
    with psycopg.connect(**config) as connection:
        rows = connection.execute(
            """
            SELECT email, count(customer_audit.customer_id)
            FROM customers LEFT JOIN customer_audit ON customers.id = customer_audit.customer_id
            WHERE tenant_id = %s GROUP BY email ORDER BY email
            """,
            (TENANT_A,),
        ).fetchall()
    expected = [("fixture@example.test", 1)]
    for browser in ("chromium", "firefox", "webkit"):
        expected.extend(
            (
                (f"pilot-{browser}@example.test", 1),
                (f"uncertain-{browser}@example.test", 1),
            )
        )
    assert rows == sorted(expected)
