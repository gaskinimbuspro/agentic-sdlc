import hashlib

import pytest

from backend_standard.gates import Rejected
from backend_standard.operations import verify_release


@pytest.fixture
def release_records(tmp_path):
    policy = {
        "environment": "isolated-preview",
        "source_sha": "a" * 40,
        "desired_revision": "b" * 40,
        "artifact_digest": "sha256:" + "c" * 64,
        "builder": "protected-build",
        "deployer": "preview-controller",
        "rollout_id": "preview-rollout-42",
        "required_smoke_cases": ["create_customer"],
    }
    root = tmp_path
    report = root / "smoke.xml"
    report.write_text('<testsuite><testcase name="create_customer"/></testsuite>')
    evidence = {
        "build": {
            "status": "verified",
            "builder": policy["builder"],
            "source_sha": policy["source_sha"],
            "artifact_digest": policy["artifact_digest"],
        },
        "observed": {
            "status": "healthy",
            "deployer": policy["deployer"],
            "rollout_id": policy["rollout_id"],
            "environment": policy["environment"],
            "desired_revision": policy["desired_revision"],
            "artifact_digest": policy["artifact_digest"],
        },
        "smoke": {
            "status": "passed",
            "rollout_id": policy["rollout_id"],
            "environment": policy["environment"],
            "desired_revision": policy["desired_revision"],
            "artifact_digest": policy["artifact_digest"],
            "report": report.name,
            "report_digest": "sha256:"
            + hashlib.sha256(report.read_bytes()).hexdigest(),
        },
    }
    return policy, evidence, root


def test_accepts_consistent_release_records(release_records):
    assert verify_release(*release_records) == {
        "executed": 1,
        "failed": 0,
        "skipped": 0,
    }


@pytest.mark.parametrize(
    ("stage", "field", "value"),
    [
        ("build", "builder", "worker"),
        ("build", "source_sha", "d" * 40),
        ("observed", "environment", "wrong-preview"),
        ("observed", "desired_revision", "d" * 40),
        ("observed", "deployer", "worker"),
        ("observed", "artifact_digest", "sha256:" + "d" * 64),
        ("observed", "status", "progressing"),
        ("smoke", "artifact_digest", "sha256:" + "d" * 64),
        ("smoke", "rollout_id", "previous-rollout"),
        ("smoke", "report_digest", "sha256:" + "d" * 64),
        ("smoke", "report", "../outside.xml"),
    ],
)
def test_rejects_mismatched_release_records(release_records, stage, field, value):
    policy, evidence, root = release_records
    evidence[stage][field] = value
    with pytest.raises(Rejected):
        verify_release(policy, evidence, root)


@pytest.mark.parametrize(
    ("xml", "reason"),
    [
        ('<testsuite tests="1"/>', "Zero executed tests"),
        ('<testsuite><testcase name="other"/></testsuite>', "Missing smoke case"),
        (
            '<testsuite><testcase name="create_customer"><failure/></testcase></testsuite>',
            "Failed tests",
        ),
        (
            '<testsuite><testcase name="create_customer"><skipped/></testcase></testsuite>',
            "Zero executed tests",
        ),
    ],
)
def test_rejects_inadequate_smoke_report(release_records, xml, reason):
    policy, evidence, root = release_records
    report = root / "smoke.xml"
    report.write_text(xml)
    evidence["smoke"]["report_digest"] = (
        "sha256:" + hashlib.sha256(report.read_bytes()).hexdigest()
    )
    with pytest.raises(Rejected, match=reason):
        verify_release(policy, evidence, root)
