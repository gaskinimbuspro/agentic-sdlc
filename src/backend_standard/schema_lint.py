"""Static checks on PostgreSQL migration files for the schema design standard.

Covers only what can be decided from CREATE TABLE text. It is a minimum gate:
it does not replace a migration linter such as squawk, catalog checks against a
live database, or review of the data model.
"""

from __future__ import annotations

import re
from pathlib import Path

CREATE = re.compile(
    r"create\s+table\s+(?:if\s+not\s+exists\s+)?(\"[^\"]+\"|[\w.]+)\s*\((.*?)\)\s*;",
    re.I | re.S,
)
COLUMN_RULES = [
    (r"\b(big|small)?serial\b", "DD03", "serial column; use an identity column"),
    (r"\b(money)\b", "DD10", "money type; use numeric with a currency"),
    (
        r"\b(real|float\d?|double\s+precision)\b",
        "DD10",
        "floating point column; use numeric for exact amounts",
    ),
    (
        r"\btimestamp\b(?!tz)(?!\s*(\(\d\)\s*)?with\s+time\s+zone)",
        "DD11",
        "timestamp without time zone; use timestamptz",
    ),
    (r"\btimetz\b|\btime\s+with\s+time\s+zone\b", "DD11", "time with time zone"),
    (r"\bjson\b", "DD14", "json column; use jsonb"),
    (r"\b(char|character)\s*\(", "DD08", "char(n) column; use text"),
    (r"\b(varchar|character\s+varying)\s*\(", "DD08", "varchar(n); use text"),
]
CONSTRAINT_WORDS = ("constraint", "primary", "unique", "foreign", "check", "exclude")


def _split(body: str) -> list[str]:
    parts, depth, current = [], 0, ""
    for char in body:
        depth += char == "("
        depth -= char == ")"
        if char == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += char
    return [part for part in parts + [current.strip()] if part]


def lint_sql(sql: str, source: str = "") -> list[str]:
    """Return findings as "<source>: <table>[.<column>]: <rule> <message>"."""
    sql = re.sub(r"--[^\n]*", "", sql)
    findings: list[str] = []

    def add(where: str, rule: str, message: str) -> None:
        findings.append(f"{source}: {where}: {rule} {message}".lstrip(": "))

    for match in CREATE.finditer(sql):
        table, body = match.group(1), match.group(2)
        if table.startswith('"') or table != table.lower():
            add(table, "DD01", "quoted or mixed-case identifier")
        parts = _split(body)
        if not any(re.search(r"\bprimary\s+key\b", part, re.I) for part in parts):
            add(table, "DD02", "table has no primary key")
        for part in parts:
            lowered = part.lower()
            first = lowered.split()[0]
            if first in CONSTRAINT_WORDS:
                if "foreign" in lowered and "on delete" not in lowered:
                    add(table, "DD05", "foreign key without an explicit ON DELETE")
                continue
            column = part.split()[0]
            where = f"{table}.{column.strip(chr(34))}"
            if column.startswith('"') or column != column.lower():
                add(where, "DD01", "quoted or mixed-case identifier")
            definition = lowered[len(column) :]
            for pattern, rule, message in COLUMN_RULES:
                if re.search(pattern, definition):
                    add(where, rule, message)
            references = "references" in definition
            if references and "on delete" not in definition:
                add(where, "DD05", "foreign key without an explicit ON DELETE")
            if (
                column.lower().endswith("_id")
                and not references
                and not re.search(
                    rf"foreign\s+key\s*\([^)]*\b{re.escape(column)}\b", body, re.I
                )
            ):
                add(where, "DD05", "id-like column without a declared foreign key")
    return findings


def lint_directory(directory: Path) -> list[str]:
    files = sorted(directory.glob("*.sql"))
    if not files:
        raise ValueError("No SQL migration files found")
    findings: list[str] = []
    for path in files:
        findings += lint_sql(path.read_text(), path.name)
    return findings
