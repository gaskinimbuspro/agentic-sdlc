"""One independent acceptance suite is run against each packaged language backend."""

import base64
import concurrent.futures
import hmac
import json
import time
import uuid

import httpx
import psycopg
import pytest
from jsonschema import Draft202012Validator, FormatChecker

from backend_standard.migrations import migrate

TENANT_A = "11111111-1111-4111-8111-111111111111"
TENANT_B = "22222222-2222-4222-8222-222222222222"


def token(key, tenant=TENANT_A, scope="customers:write customers:read", **overrides):
    claims = {
        "iss": "backend-reference",
        "aud": "customers",
        "sub": "synthetic-member",
        "exp": int(time.time()) + 120,
        "tenant_id": tenant,
        "scope": scope,
    } | overrides

    def encoded(value):
        return base64.urlsafe_b64encode(json.dumps(value).encode()).rstrip(b"=")

    body = encoded({"alg": "HS256", "typ": "JWT"}) + b"." + encoded(claims)
    signature = base64.urlsafe_b64encode(
        hmac.digest(key.encode(), body, "sha256")
    ).rstrip(b"=")
    return {"Authorization": "Bearer " + (body + b"." + signature).decode()}


def body(tenant=TENANT_A, **changes):
    return {"tenant_id": tenant, "name": "Ada", "email": "ada@example.test"} | changes


def rows(database, table="customers"):
    config, _ = database
    assert table in {"customers", "customer_audit"}
    with psycopg.connect(**config) as conn:
        return conn.execute("SELECT count(*) FROM " + table).fetchone()[0]


def test_valid_create_and_contract(service, database):
    url, key, _ = service
    response = httpx.post(
        url + "/customers",
        headers=token(key),
        json=body(name=" Ada ", email=" ADA@EXAMPLE.TEST "),
    )
    assert response.status_code == 201
    value = response.json()
    from pathlib import Path

    contract = json.loads(
        (Path(__file__).resolve().parents[2] / "reference/openapi.json").read_text()
    )
    Draft202012Validator(
        contract["components"]["schemas"]["Customer"], format_checker=FormatChecker()
    ).validate(value)
    assert set(value) == {"id", "tenant_id", "name", "email"}
    assert uuid.UUID(value["id"])
    assert value | {"id": "ignored"} == {
        "id": "ignored",
        "tenant_id": TENANT_A,
        "name": "Ada",
        "email": "ada@example.test",
    }
    assert uuid.UUID(response.headers["X-Request-ID"])
    assert rows(database) == rows(database, "customer_audit") == 1


@pytest.mark.parametrize(
    "change",
    [
        {"name": ""},
        {"name": "x" * 101},
        {"name": None},
        {"email": "invalid"},
        {"email": "x" * 255},
        {"extra": "forbidden"},
    ],
)
def test_invalid_input_has_no_side_effects(service, database, change):
    url, key, _ = service
    response = httpx.post(url + "/customers", headers=token(key), json=body(**change))
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["status"] == 400
    assert rows(database) == rows(database, "customer_audit") == 0


@pytest.mark.parametrize("case", ["missing", "forged", "expired", "issuer", "audience"])
def test_authentication(service, database, case):
    url, key, _ = service
    headers = token(key)
    if case == "missing":
        headers = {}
    if case == "forged":
        headers = token("wrong-signing-key" * 3)
    if case == "expired":
        headers = token(key, exp=int(time.time()) - 30)
    if case == "issuer":
        headers = token(key, iss="wrong-issuer")
    if case == "audience":
        headers = token(key, aud="wrong-audience")
    response = httpx.post(url + "/customers", headers=headers, json=body())
    assert response.status_code == 401
    assert rows(database) == 0


@pytest.mark.parametrize("case", ["tenant", "role"])
def test_authorization(service, database, case):
    url, key, _ = service
    headers = token(key, scope="customers:read") if case == "role" else token(key)
    response = httpx.post(
        url + "/customers",
        headers=headers,
        json=body(TENANT_B if case == "tenant" else TENANT_A),
    )
    assert response.status_code == 403
    assert rows(database) == 0


def test_list_isolation(service):
    url, key, _ = service
    for tenant in (TENANT_A, TENANT_B):
        assert (
            httpx.post(
                url + "/customers", headers=token(key, tenant), json=body(tenant)
            ).status_code
            == 201
        )
    for tenant in (TENANT_A, TENANT_B):
        response = httpx.get(url + "/customers", headers=token(key, tenant))
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["tenant_id"] == tenant


def test_duplicate_race(service, database):
    url, key, _ = service

    def create(_):
        return httpx.post(
            url + "/customers", headers=token(key), json=body()
        ).status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as workers:
        assert sorted(workers.map(create, range(2))) == [201, 409]
    assert rows(database) == rows(database, "customer_audit") == 1


def test_atomicity_on_second_write_failure(service, database):
    url, key, _ = service
    config, _ = database
    with psycopg.connect(**config, autocommit=True) as conn:
        conn.execute(
            "CREATE OR REPLACE FUNCTION fail_audit() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'synthetic failure'; END $$"
        )
        conn.execute(
            "CREATE TRIGGER force_audit_failure BEFORE INSERT ON customer_audit FOR EACH ROW EXECUTE FUNCTION fail_audit()"
        )
    response = httpx.post(url + "/customers", headers=token(key), json=body())
    assert response.status_code == 503
    assert rows(database) == rows(database, "customer_audit") == 0
    assert "synthetic failure" not in response.text


@pytest.mark.parametrize("limit", ["0", "101", "invalid"])
def test_query_limits(service, limit):
    url, key, _ = service
    assert (
        httpx.get(
            url + "/customers", headers=token(key), params={"limit": limit}
        ).status_code
        == 400
    )


def test_payload_limit(service, database):
    url, key, _ = service
    response = httpx.post(
        url + "/customers", headers=token(key), json=body(name="x" * 9000)
    )
    assert response.status_code == 413
    assert rows(database) == 0


def test_injection_is_data(service, database):
    url, key, _ = service
    name = "Robert'); DROP TABLE customers;--"
    assert (
        httpx.post(
            url + "/customers", headers=token(key), json=body(name=name)
        ).status_code
        == 201
    )
    result = httpx.get(url + "/customers", headers=token(key)).json()
    assert result[0]["name"] == name
    assert rows(database) == 1


def test_logs_do_not_contain_credentials_or_customer_data(service):
    url, key, log = service
    canary = "sensitive-customer-canary"
    httpx.post(url + "/customers", headers=token(key), json=body(name=canary))
    output = log.read_text()
    assert (
        key not in output
        and token(key)["Authorization"] not in output
        and canary not in output
    )


def test_database_constraints(database):
    config, _ = database
    with psycopg.connect(**config, autocommit=True) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute(
                "INSERT INTO customers VALUES (%s,%s,%s,%s)",
                (uuid.uuid4(), TENANT_A, "", "a@b.test"),
            )


def test_upgrade_and_checksum_protection(database, tmp_path):
    from pathlib import Path

    from psycopg import sql

    migration_root = Path(__file__).resolve().parents[2] / "reference/migrations"
    first = tmp_path / "001_customers.sql"
    first.write_text((migration_root / first.name).read_text())
    config, _ = database
    schema = "upgrade_" + uuid.uuid4().hex
    with psycopg.connect(**config, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
        try:
            migrate(conn, tmp_path)
            customer_id = uuid.uuid4()
            conn.execute(
                "INSERT INTO customers VALUES (%s,%s,%s,%s)",
                (customer_id, TENANT_A, "Existing", "existing@example.test"),
            )
            second = tmp_path / "002_audit.sql"
            second.write_text((migration_root / second.name).read_text())
            migrate(conn, tmp_path)
            assert (
                conn.execute(
                    "SELECT name FROM customers WHERE id=%s", (customer_id,)
                ).fetchone()[0]
                == "Existing"
            )
            assert (
                conn.execute("SELECT count(*) FROM schema_migrations").fetchone()[0]
                == 2
            )
            first.write_text(first.read_text() + "\n-- changed after application\n")
            with pytest.raises(ValueError, match="checksum"):
                migrate(conn, tmp_path)
        finally:
            conn.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )


def test_failed_migration_is_atomic(database, tmp_path):
    from psycopg import sql

    (tmp_path / "001_broken.sql").write_text(
        "CREATE TABLE partial_write(id int); SELECT 1/0;"
    )
    config, _ = database
    schema = "failed_" + uuid.uuid4().hex
    with psycopg.connect(**config, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
        try:
            with pytest.raises(psycopg.errors.DivisionByZero):
                migrate(conn, tmp_path)
            assert (
                conn.execute("SELECT to_regclass('partial_write')").fetchone()[0]
                is None
            )
            assert (
                conn.execute("SELECT to_regclass('schema_migrations')").fetchone()[0]
                is None
            )
        finally:
            conn.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )
