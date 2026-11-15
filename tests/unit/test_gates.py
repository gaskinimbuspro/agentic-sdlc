import copy
import hashlib
import json
from pathlib import Path

import pytest

from backend_standard.gates import Rejected, profile_ready, verify_evidence
from backend_standard.gates import test_counts as parse_counts

ROOT = Path(__file__).resolve().parents[2]
SHA = "a" * 40
BASE = "b" * 40


def inputs(tmp_path: Path) -> tuple[dict, dict]:
    report = tmp_path / "unit.xml"
    report.write_text('<testsuite tests="1"><testcase name="invariant"/></testsuite>')
    policy = {
        "required_checks": {"unit": {"format": "junit"}},
        "reviewers": ["reviewer"],
    }
    evidence = {
        "status": "passed",
        "candidate_sha": SHA,
        "integration_base_sha": BASE,
        "implementation_owner": "worker",
        "exceptions": [],
        "checks": [
            {
                "name": "unit",
                "status": "passed",
                "exit_code": 0,
                "candidate_sha": SHA,
                "report": "unit.xml",
                "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            }
        ],
        "review": {
            "reviewer": "reviewer",
            "candidate_sha": SHA,
            "verdict": "approved",
            "blocking_findings": 0,
        },
    }
    return policy, evidence


def test_accepts_valid_index(tmp_path: Path) -> None:
    policy, evidence = inputs(tmp_path)
    verify_evidence(policy, evidence, tmp_path, SHA, BASE)


@pytest.mark.parametrize(
    "failure",
    [
        "stale_candidate",
        "stale_base",
        "missing_check",
        "duplicate_check",
        "failed_check",
        "missing_report",
        "tampered_report",
        "self_review",
        "stale_review",
        "blocking_review",
        "untrusted_review",
        "no_approval",
        "exception",
        "path_escape",
        "blocked_check",
    ],
)
def test_rejects_false_completion(tmp_path: Path, failure: str) -> None:
    policy, evidence = inputs(tmp_path)
    match failure:
        case "stale_candidate":
            evidence["candidate_sha"] = "c" * 40
        case "stale_base":
            evidence["integration_base_sha"] = "c" * 40
        case "missing_check":
            evidence["checks"] = []
        case "duplicate_check":
            evidence["checks"] *= 2
        case "failed_check":
            evidence["checks"][0]["exit_code"] = 1
        case "missing_report":
            (tmp_path / "unit.xml").unlink()
        case "tampered_report":
            (tmp_path / "unit.xml").write_text("changed")
        case "self_review":
            evidence["implementation_owner"] = "reviewer"
        case "stale_review":
            evidence["review"]["candidate_sha"] = "c" * 40
        case "blocking_review":
            evidence["review"]["blocking_findings"] = 1
        case "untrusted_review":
            evidence["review"]["reviewer"] = "stranger"
        case "no_approval":
            evidence["review"]["verdict"] = "commented"
        case "exception":
            evidence["exceptions"] = [{"approved": True}]
        case "path_escape":
            evidence["checks"][0]["report"] = "../unit.xml"
        case "blocked_check":
            evidence["checks"][0]["status"] = "blocked"
    with pytest.raises(Rejected):
        verify_evidence(policy, evidence, tmp_path, SHA, BASE)


@pytest.mark.parametrize(
    "body",
    [
        '<testsuite tests="0"/>',
        "<testsuite><testcase><failure/></testcase></testsuite>",
        "<testsuite><testcase><skipped/></testcase><testcase/></testsuite>",
        '<!DOCTYPE x [<!ENTITY y "x">]><testsuite><testcase/></testsuite>',
    ],
)
def test_rejects_invalid_test_evidence(tmp_path: Path, body: str) -> None:
    report = tmp_path / "invalid.xml"
    report.write_text(body)
    with pytest.raises(Rejected):
        parse_counts(report, "junit")


def test_trx_and_go_formats(tmp_path: Path) -> None:
    report = tmp_path / "unit.trx"
    report.write_text(
        '<TestRun xmlns="urn:test"><Results><UnitTestResult outcome="Passed"/></Results></TestRun>'
    )
    assert parse_counts(report, "trx")["executed"] == 1
    report.write_text(json.dumps({"Action": "pass", "Test": "TestInvariant"}) + "\n")
    assert parse_counts(report, "go-json")["executed"] == 1


def test_template_cannot_be_made_ready_by_changing_its_flag() -> None:
    template = json.loads(
        (ROOT / "standards/backend/project-profile.template.json").read_text()
    )
    with pytest.raises(Rejected):
        profile_ready(template, ROOT)
    forged = copy.deepcopy(template)
    forged["readiness"] = "ready"
    with pytest.raises(Rejected):
        profile_ready(forged, ROOT)
