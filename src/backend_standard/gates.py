"""Fail-closed checks. Trust in the caller and runner is an external boundary."""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


class Rejected(ValueError):
    """The supplied decisions or evidence cannot establish acceptance."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise Rejected(message)


def text(value: object, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label}: required")
    result = str(value)
    require(
        not re.search(r"\b(TODO|TBD|CHANGEME|PLACEHOLDER)\b|<[^>]+>", result, re.I),
        f"{label}: unresolved placeholder",
    )
    return result


def document(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise Rejected(f"Cannot read JSON document: {path.name}") from exc
    require(isinstance(value, dict), "Expected a JSON object")
    return dict(value)


def confined(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    require(not Path(relative).is_absolute(), "Absolute report path rejected")
    require(candidate.is_relative_to(root.resolve()), "Path escapes evidence root")
    require(candidate.is_file(), f"Missing required file: {relative}")
    return candidate


def profile_ready(profile: dict[str, Any], root: Path) -> None:
    """Validate the existing profile shape and its actual decision/check bindings."""
    require(profile.get("readiness") == "ready", "Profile is not ready")
    require(profile.get("backend_standard") == "0.1", "Unsupported standard version")
    language = profile.get("language")
    require(language in {"python", "dotnet", "go"}, "Unsupported language profile")
    required_sections = {
        "toolchain": ("runtime_version", "test_runner", "tool_versions"),
        "framework": (
            "name",
            "version",
            "validation_and_error_policy",
            "test_host_and_lifecycle",
        ),
        "architecture": (
            "style",
            "domain_logic_pattern",
            "decision_document",
            "module_boundaries",
        ),
        "interfaces": (
            "http_api",
            "contract_path",
            "error_format",
            "compatibility_policy",
        ),
        "data": (
            "persistence",
            "engine",
            "version",
            "migration_tool",
            "transaction_policy",
        ),
        "security": (
            "authentication",
            "authorization",
            "dependency_scanner",
            "blocking_policy",
        ),
        "quality_targets": (
            "request_limits",
            "timeouts_and_retry_policy",
            "observability",
            "performance_budget",
        ),
    }
    for section, names in required_sections.items():
        values = profile.get(section)
        if not isinstance(values, dict):
            raise Rejected(f"{section}: required object")
        for name in names:
            value = values.get(name)
            require(
                value is not None and value != "" and value != [] and value != {},
                f"{section}.{name}: missing decision",
            )
            if isinstance(value, str):
                text(value, f"{section}.{name}")
    confined(root, profile["architecture"]["decision_document"])
    confined(root, profile["interfaces"]["contract_path"])
    gates = profile.get("gates", {})
    expected = {
        "format",
        "static_analysis",
        "build_or_typecheck",
        "unit",
        "integration",
        "contract",
        "security",
        "smoke",
        "backend_verify",
    }
    require(set(gates) == expected, "Profile must bind all named gates")
    for name, command in gates.items():
        require(isinstance(command, list) and bool(command), f"{name}: argv required")
        for arg in command:
            text(arg, f"{name}: argument")
    policy = profile.get("execution_policy", {})
    for name in (
        "dispatch_claim_policy",
        "integration_target",
        "model_routing",
        "coding_task_context",
        "workspace_isolation",
    ):
        text(policy.get(name), f"execution_policy.{name}")
    require(
        policy.get("independent_review_context") is True, "Independent review required"
    )
    require(bool(policy.get("required_ci_checks")), "Required CI checks missing")
    for name in ("max_parallel_tasks", "repair_budget"):
        require(
            type(policy.get(name)) is int and policy[name] > 0,
            f"execution_policy.{name}: positive integer required",
        )
    require(
        not profile.get("exceptions"), "Exceptions require an external approved policy"
    )


def test_counts(path: Path, report_format: str) -> dict[str, int]:
    """Count executed cases rather than trusting an exit status or root total."""
    counts = {"executed": 0, "failed": 0, "skipped": 0}
    if report_format == "go-json":
        for line in path.read_text().splitlines():
            event = json.loads(line)
            require(event.get("Action") != "fail", "Go test/package failed")
            if event.get("Test") and event.get("Action") in {"pass", "fail", "skip"}:
                action = event["Action"]
                counts["skipped" if action == "skip" else "executed"] += 1
                counts["failed"] += action == "fail"
    else:
        require(path.stat().st_size <= 20_000_000, "Report exceeds size limit")
        raw = path.read_text()
        require("<!DOCTYPE" not in raw and "<!ENTITY" not in raw, "DTD/ENTITY rejected")
        tree = ET.fromstring(raw)
        if report_format == "junit":
            for suite in tree.iter():
                if suite.tag.split("}")[-1] in {"testsuite", "testsuites"}:
                    for field in ("failures", "errors", "skipped", "disabled"):
                        require(
                            int(suite.attrib.get(field, "0")) == 0,
                            f"JUnit reports {field}",
                        )
            cases = [n for n in tree.iter() if n.tag.split("}")[-1] == "testcase"]
            for case in cases:
                tags = {n.tag.split("}")[-1] for n in case}
                counts["skipped" if "skipped" in tags else "executed"] += 1
                counts["failed"] += bool(tags & {"failure", "error"})
        elif report_format == "trx":
            cases = [n for n in tree.iter() if n.tag.split("}")[-1] == "UnitTestResult"]
            for case in cases:
                outcome = case.attrib.get("outcome")
                require(
                    outcome in {"Passed", "Failed", "NotExecuted"},
                    "Unknown TRX outcome",
                )
                counts["skipped" if outcome == "NotExecuted" else "executed"] += 1
                counts["failed"] += outcome == "Failed"
        else:
            raise Rejected("Unsupported test report format")
    require(counts["executed"] > 0, "Zero executed tests")
    require(counts["failed"] == 0, "Failed tests")
    require(
        counts["skipped"] == 0, "Skipped tests require externally approved exceptions"
    )
    return counts


def verify_evidence(
    policy: dict[str, Any],
    evidence: dict[str, Any],
    root: Path,
    candidate: str,
    base: str,
) -> None:
    """Validate a runner index under an independently supplied acceptance policy.

    This cannot authenticate a file written by an adversarial caller. A trusted
    CI/Coordinator must supply expected identities, policy, reports and review.
    """
    for label, expected in (
        ("candidate_sha", candidate),
        ("integration_base_sha", base),
    ):
        require(
            bool(re.fullmatch(r"[0-9a-f]{40}", expected)), f"Invalid expected {label}"
        )
        require(evidence.get(label) == expected, f"Stale/mismatched {label}")
    require(evidence.get("status") == "passed", "Evidence did not pass")
    wanted = policy.get("required_checks")
    if not isinstance(wanted, dict) or not wanted:
        raise Rejected("Required checks not configured")
    checks = evidence.get("checks", [])
    require(isinstance(checks, list), "Check results must be a list")
    names = [c.get("name") for c in checks]
    require(len(set(names)) == len(names), "Duplicate check result")
    require(set(names) == set(wanted), "Missing or unexpected required check")
    for check in checks:
        name = check["name"]
        expected_format = wanted[name]["format"]
        require(
            check.get("status") == "passed"
            and type(check.get("exit_code")) is int
            and check.get("exit_code") == 0,
            f"{name}: failed/blocked check",
        )
        require(check.get("candidate_sha") == candidate, f"{name}: stale result")
        path = confined(root, text(check.get("report"), f"{name}: report"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(check.get("sha256") == digest, f"{name}: report digest mismatch")
        if expected_format != "log":
            test_counts(path, expected_format)
    require(not evidence.get("exceptions"), "Unverified exception record")
    review = evidence.get("review", {})
    require(review.get("reviewer") in policy.get("reviewers", []), "Untrusted reviewer")
    require(
        review.get("reviewer") != evidence.get("implementation_owner"), "Self-review"
    )
    require(review.get("candidate_sha") == candidate, "Stale review")
    require(review.get("blocking_findings") == 0, "Unresolved review findings")
    require(review.get("verdict") == "approved", "Independent approval required")
