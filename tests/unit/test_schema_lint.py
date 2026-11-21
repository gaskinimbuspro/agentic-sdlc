from pathlib import Path

import pytest

from backend_standard.schema_lint import lint_directory, lint_sql

ROOT = Path(__file__).resolve().parents[2]

GOOD = """
CREATE TABLE tenants (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL
);
CREATE TABLE invoices (
    id uuid PRIMARY KEY,
    tenant_id bigint NOT NULL REFERENCES tenants (id) ON DELETE RESTRICT,
    amount numeric(12, 2) NOT NULL,
    currency text NOT NULL CHECK (length(currency) = 3),
    issued_at timestamptz NOT NULL,
    details jsonb,
    parent_id uuid,
    CONSTRAINT invoices_parent FOREIGN KEY (parent_id)
        REFERENCES invoices (id) ON DELETE SET NULL
);
"""


def test_conforming_schema_has_no_findings() -> None:
    assert lint_sql(GOOD) == []


@pytest.mark.parametrize(
    ("column", "rule"),
    [
        ("id serial PRIMARY KEY", "DD03"),
        ("price double precision", "DD10"),
        ("total money", "DD10"),
        ("created_at timestamp DEFAULT now()", "DD11"),
        ("created_at timestamp(0) without time zone", "DD11"),
        ("opens timetz", "DD11"),
        ("payload json", "DD14"),
        ("code char(2)", "DD08"),
        ("surname varchar(20)", "DD08"),
        ('"Name" text', "DD01"),
        ("owner_id bigint REFERENCES owners (id)", "DD05"),
        ("owner_id bigint NOT NULL", "DD05"),
    ],
)
def test_each_violation_is_reported(column: str, rule: str) -> None:
    extra = "" if "PRIMARY KEY" in column else "pk bigint PRIMARY KEY, "
    findings = lint_sql(f"CREATE TABLE things ({extra}{column});")
    assert any(f" {rule} " in finding for finding in findings), findings


def test_table_without_primary_key_is_reported() -> None:
    assert any("DD02" in f for f in lint_sql("CREATE TABLE notes (body text);"))


def test_table_level_foreign_key_needs_on_delete() -> None:
    sql = "CREATE TABLE a (id uuid PRIMARY KEY, b_id uuid, FOREIGN KEY (b_id) REFERENCES b (id));"
    assert sum("ON DELETE" in f for f in lint_sql(sql)) == 1


def test_timestamptz_is_not_mistaken_for_timestamp() -> None:
    sql = "CREATE TABLE e (id uuid PRIMARY KEY, at timestamp with time zone, at2 timestamptz);"
    assert lint_sql(sql) == []


def test_reference_migrations_show_the_recorded_gaps() -> None:
    findings = lint_directory(ROOT / "reference/migrations")
    assert findings == [
        "001_customers.sql: customers.tenant_id: DD05 id-like column without a"
        " declared foreign key",
        "002_audit.sql: customer_audit.customer_id: DD05 foreign key without an"
        " explicit ON DELETE",
    ]


def test_empty_directory_is_blocked(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        lint_directory(tmp_path)
