"""Fail-closed checks. Trust in the caller and runner is an external boundary."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import ParseError

from defusedxml import ElementTree as ET
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


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
    schema = document(Path(__file__).parent / "schemas/profile.schema.json")
    try:
        Draft202012Validator(schema).validate(profile)
    except ValidationError as error:
        raise Rejected("Profile schema: " + ".".join(map(str, error.path))) from error
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
        running_tests: set[tuple[str, str]] = set()
        running_packages: set[str] = set()
        finished_tests: set[tuple[str, str]] = set()
        for line in path.read_text().splitlines():
            event = json.loads(line)
            require(isinstance(event, dict), "Invalid Go test event")
            action = event.get("Action")
            require(action not in {"fail", "build-fail"}, "Go test/package failed")
            package = str(event.get("Package", ""))
            identity = (package, str(event.get("Test", "")))
            if action == "start":
                running_packages.add(package)
            if event.get("Test") and action == "run":
                running_tests.add(identity)
            if event.get("Test") and event.get("Action") in {"pass", "fail", "skip"}:
                require(identity not in finished_tests, "Duplicate Go test result")
                finished_tests.add(identity)
                running_tests.discard(identity)
                action = event["Action"]
                counts["skipped" if action == "skip" else "executed"] += 1
                counts["failed"] += action == "fail"
            elif not event.get("Test") and action in {"pass", "skip"}:
                running_packages.discard(package)
        require(not running_tests and not running_packages, "Incomplete Go test run")
    else:
        require(path.stat().st_size <= 20_000_000, "Report exceeds size limit")
        raw = path.read_text()
        require("<!DOCTYPE" not in raw and "<!ENTITY" not in raw, "DTD/ENTITY rejected")
        try:
            tree = ET.fromstring(
                raw, forbid_dtd=True, forbid_entities=True, forbid_external=True
            )
        except (ParseError, ValueError) as error:
            raise Rejected("Invalid/unsafe XML report") from error
        if report_format == "junit":
            require(
                tree.tag.split("}")[-1] in {"testsuite", "testsuites"},
                "Invalid JUnit root",
            )
            for suite in tree.iter():
                if suite.tag.split("}")[-1] in {"testsuite", "testsuites"}:
                    require(
                        not any(
                            n.tag.split("}")[-1] in {"error", "failure", "skipped"}
                            for n in suite
                        ),
                        "JUnit suite-level failure or skip",
                    )
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
            require(tree.tag.split("}")[-1] == "TestRun", "Invalid TRX root")
            for summary in tree.iter():
                tag = summary.tag.split("}")[-1]
                if tag == "ResultSummary":
                    require(
                        summary.attrib.get("outcome") in {"Passed", "Completed"},
                        "TRX run did not complete successfully",
                    )
                elif tag == "Counters":
                    for field in (
                        "failed",
                        "error",
                        "timeout",
                        "aborted",
                        "notExecuted",
                        "disconnected",
                        "inProgress",
                        "pending",
                        "inconclusive",
                    ):
                        require(
                            int(summary.attrib.get(field, "0")) == 0,
                            f"TRX reports {field}",
                        )
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


def task_ready(
    packet: dict[str, Any],
    profile: dict[str, Any],
    root: Path,
    completed_dependencies: set[str],
) -> None:
    """Check ready-stage inputs; claiming/execution remains the Coordinator's job."""
    profile_ready(profile, root)
    require(packet.get("status") == "ready", "Task is not ready")
    require(
        packet.get("standard_version") == profile["backend_standard"],
        "Standard mismatch",
    )
    require(packet.get("language_profile") == profile["language"], "Language mismatch")
    for field in ("task_id", "goal", "repository"):
        text(packet.get(field), field)
    require(
        bool(re.fullmatch(r"[0-9a-f]{40}", str(packet.get("base_sha")))),
        "Base SHA required",
    )
    for field in (
        "scope",
        "non_goals",
        "requirement_ids",
        "test_case_ids",
        "allowed_paths",
        "decision_references",
        "contract_references",
    ):
        values = packet.get(field)
        if not isinstance(values, list) or not values:
            raise Rejected(f"{field}: non-empty list required")
        for value in values:
            text(value, field)
    require(
        set(packet["test_case_ids"]) <= {f"TC{i:02}" for i in range(1, 15)},
        "Unknown case family",
    )
    for field in ("decision_references", "contract_references"):
        for reference in packet[field]:
            confined(root, reference)
    for relative in packet["allowed_paths"]:
        require(
            not Path(relative).is_absolute()
            and (root / relative).resolve().is_relative_to(root.resolve()),
            "Allowed path escapes workspace",
        )
    dependencies = packet.get("dependency_task_ids")
    require(
        isinstance(dependencies, list) and set(dependencies) <= completed_dependencies,
        "Unfinished task dependencies",
    )
    criteria = packet.get("acceptance_criteria")
    if not isinstance(criteria, list) or not criteria:
        raise Rejected("Acceptance criteria required")
    seen = set()
    for criterion in criteria:
        require(isinstance(criterion, dict), "Structured acceptance criterion required")
        identifier = text(criterion.get("id"), "criterion id")
        require(identifier not in seen, "Duplicate acceptance criterion")
        seen.add(identifier)
        text(criterion.get("expected"), "expected outcome")
        require(
            criterion.get("requirement_id") in packet["requirement_ids"],
            "Orphan criterion",
        )
        require(
            bool(criterion.get("case_ids"))
            and set(criterion["case_ids"]) <= set(packet["test_case_ids"]),
            "Unmapped acceptance cases",
        )
    require(
        packet.get("required_commands") == profile["gates"],
        "Task omitted or changed an approved check binding",
    )
    for name, command in packet["required_commands"].items():
        require(command == profile["gates"].get(name), "Task changed an approved check")
    require(bool(packet.get("required_evidence")), "Evidence plan missing")
    budget = packet.get("budget", {})
    for field in ("max_wall_time_minutes", "max_repair_attempts", "max_context_tokens"):
        require(
            type(budget.get(field)) is int and budget[field] > 0,
            f"{field}: positive budget required",
        )
    require(
        type(budget.get("max_cost")) in {int, float} and budget["max_cost"] > 0,
        "Cost budget required",
    )
    require(budget.get("cost_currency") == "USD", "Explicit USD cost currency required")


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
    require(
        all(isinstance(check, dict) for check in checks),
        "Each check result must be an object",
    )
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
            counts = test_counts(path, expected_format)
            require(
                counts["executed"] >= wanted[name].get("minimum_tests", 1),
                f"{name}: required test count not met",
            )
            required_names = wanted[name].get("required_test_names", [])
            if required_names:
                require(
                    set(required_names) <= report_names(path, expected_format),
                    f"{name}: missing required acceptance cases",
                )
    require(not evidence.get("exceptions"), "Unverified exception record")
    owner = text(evidence.get("implementation_owner"), "Implementation owner")
    review = evidence.get("review", {})
    require(isinstance(review, dict), "Review record must be an object")
    require(review.get("reviewer") in policy.get("reviewers", []), "Untrusted reviewer")
    require(review.get("reviewer") != owner, "Self-review")
    require(review.get("candidate_sha") == candidate, "Stale review")
    require(
        type(review.get("blocking_findings")) is int
        and review["blocking_findings"] == 0,
        "Unresolved/invalid review findings",
    )
    require(review.get("verdict") == "approved", "Independent approval required")


def report_names(path: Path, report_format: str) -> set[str]:
    """Stable case names are supplied by protected acceptance policy, not a worker."""
    if report_format == "go-json":
        events = [json.loads(line) for line in path.read_text().splitlines()]
        return {
            str(e["Test"])
            for e in events
            if e.get("Test") and e.get("Action") == "pass"
        }
    raw = path.read_text()
    tree = ET.fromstring(
        raw, forbid_dtd=True, forbid_entities=True, forbid_external=True
    )
    if report_format == "junit":
        return {
            n.attrib["name"]
            for n in tree.iter()
            if n.tag.split("}")[-1] == "testcase" and "name" in n.attrib
        }
    if report_format == "trx":
        return {
            n.attrib["testName"]
            for n in tree.iter()
            if n.tag.split("}")[-1] == "UnitTestResult"
            and n.attrib.get("outcome") == "Passed"
        }
    raise Rejected("Unknown report format")
