"""Check observed release records against an independently supplied policy."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import ParseError

from defusedxml import ElementTree as ET

from backend_standard.adoption import read_adoption_record, verify_adoption
from backend_standard.gates import (
    Rejected,
    confined,
    document,
    require,
    text,
)
from backend_standard.schema_lint import lint_directory


def smoke_names(raw: bytes, expected: dict[str, str]) -> set[str]:
    try:
        tree = ET.fromstring(
            raw, forbid_dtd=True, forbid_entities=True, forbid_external=True
        )
    except (ParseError, ValueError, LookupError) as error:
        raise Rejected("Invalid or unsafe smoke report") from error
    if tree.tag == "testsuite":
        suites = [tree]
    elif tree.tag == "testsuites":
        suites = list(tree)
    else:
        raise Rejected("Invalid smoke report root")
    require(
        suites and all(suite.tag == "testsuite" for suite in suites),
        "Invalid smoke suite layout",
    )
    require(
        not any(
            node.tag.split("}")[-1] in {"error", "failure", "skipped"}
            for node in tree.iter()
        ),
        "Failed or skipped smoke case",
    )
    for summary in [tree] if tree.tag == "testsuite" else [tree, *suites]:
        for field in ("failures", "errors", "skipped", "disabled"):
            require(summary.get(field, "0") == "0", f"Smoke report declares {field}")
    require(
        not any(
            node.tag.split("}")[-1].casefold()
            in {"flakyerror", "flakyfailure", "rerunerror", "rerunfailure", "rerun"}
            for node in tree.iter()
        ),
        "Flaky or rerun smoke case",
    )
    names: set[str] = set()
    for suite in suites:
        properties = suite.findall("properties")
        require(len(properties) == 1, "Smoke suite requires one properties element")
        for field in (
            "environment",
            "desired_revision",
            "artifact_digest",
            "rollout_id",
        ):
            values = [
                prop.get("value")
                for prop in properties[0].findall("property")
                if prop.get("name") == field
            ]
            require(values == [expected[field]], f"Smoke suite: {field} mismatch")
        for case in suite.findall("testcase"):
            name = text(case.get("name"), "Smoke case name")
            require(name not in names, "Duplicate smoke case name")
            names.add(name)
    require(
        len(names)
        == sum(node.tag.split("}")[-1] == "testcase" for node in tree.iter()),
        "Smoke testcase outside its suite",
    )
    require(names, "Zero executed tests")
    return names


def verify_release(
    policy: dict[str, Any], evidence: dict[str, Any], root: Path
) -> dict[str, int]:
    expected = {
        field: text(policy.get(field), field)
        for field in (
            "environment",
            "source_sha",
            "desired_revision",
            "artifact_digest",
            "builder",
            "deployer",
            "rollout_id",
        )
    }
    for field in ("source_sha", "desired_revision"):
        require(re.fullmatch(r"[0-9a-f]{40}", expected[field]), f"Invalid {field}")
    require(
        re.fullmatch(r"sha256:[0-9a-f]{64}", expected["artifact_digest"]),
        "An immutable SHA-256 artifact digest is required",
    )
    smoke_cases = policy.get("required_smoke_cases")
    if not isinstance(smoke_cases, list) or not smoke_cases:
        raise Rejected("Required smoke cases must be configured")
    required_cases = {text(case, "Smoke case") for case in smoke_cases}
    require(len(required_cases) == len(smoke_cases), "Duplicate required smoke case")

    stages = (
        ("build", "verified", ("builder", "source_sha", "artifact_digest")),
        (
            "observed",
            "healthy",
            (
                "deployer",
                "environment",
                "desired_revision",
                "artifact_digest",
                "rollout_id",
            ),
        ),
        (
            "smoke",
            "passed",
            ("environment", "desired_revision", "artifact_digest", "rollout_id"),
        ),
    )
    for stage, status, fields in stages:
        record = evidence.get(stage)
        if not isinstance(record, dict):
            raise Rejected(f"Missing {stage} record")
        require(record.get("status") == status, f"{stage} did not pass")
        for field in fields:
            require(record.get(field) == expected[field], f"{stage}: {field} mismatch")

    smoke = evidence["smoke"]
    report = confined(root, text(smoke.get("report"), "Smoke report"))
    with report.open("rb") as handle:
        raw = handle.read(20_000_001)
    require(len(raw) <= 20_000_000, "Smoke report exceeds size limit")
    actual_digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    require(smoke.get("report_digest") == actual_digest, "Smoke report digest mismatch")
    names = smoke_names(raw, expected)
    require(required_cases <= names, "Missing smoke case")
    return {"executed": len(names), "failed": 0, "skipped": 0}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("release", "adoption"):
        gate = sub.add_parser(command)
        gate.add_argument("evidence", type=Path)
        gate.add_argument("--policy", type=Path, required=True)
        gate.add_argument("--reports", type=Path, required=True)
    lint = sub.add_parser("schema-lint")
    lint.add_argument("directory", type=Path)
    args = parser.parse_args()
    result: dict[str, list[str] | dict[str, int]]
    if args.command == "schema-lint":
        try:
            findings = lint_directory(args.directory)
        except (OSError, ValueError) as error:
            reason = {"status": "blocked", "reason": str(error)}
            print(json.dumps(reason), file=sys.stderr)
            return 1
        scope = "static CREATE TABLE checks only"
        status = "findings" if findings else "clean"
        print(json.dumps({"status": status, "scope": scope, "findings": findings}))
        return 1 if findings else 0
    try:
        if args.command == "adoption":
            profiles = verify_adoption(
                read_adoption_record(args.policy),
                read_adoption_record(args.evidence),
                args.reports,
            )
            result = {"profiles": profiles}
        else:
            counts = verify_release(
                document(args.policy), document(args.evidence), args.reports
            )
            result = {"smoke": counts}
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "blocked", "reason": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps({"status": "consistent", "scope": "supplied records", **result}))
    return 0
