import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

from backend_standard.adoption import PROFILE_CASES, verify_adoption
from backend_standard.gates import Rejected
from backend_standard.operations import main

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def records():
    policy = {
        "candidate_sha": "a" * 40,
        "environment": "isolated-adoption",
        "run_id": "adoption-17",
        "profiles": {profile: f"reviewer-{profile}" for profile in PROFILE_CASES},
    }
    reports = {
        profile: {
            **{key: value for key, value in policy.items() if key != "profiles"},
            "profile": profile,
            "operator": "independent-test-operator",
            "reviewer": policy["profiles"][profile],
            "cases": [
                {
                    "id": case_id,
                    "status": "passed",
                    "observation": "Observed the expected result in synthetic fixture 17.",
                }
                for case_id in sorted(cases)
            ],
        }
        for profile, cases in PROFILE_CASES.items()
    }
    start = 1_700_000_000
    reports["remote"]["soak"] = {
        "started_at": start,
        "ended_at": start + 86_400,
        "samples": [
            {
                "at": start + offset,
                "activity": "idle" if offset < 43_200 else "workload",
                "service": "healthy",
                "pressure": {
                    "cpu_some_pct": 0.1,
                    "memory_some_pct": 0,
                    "io_some_pct": 5,
                },
            }
            for offset in range(0, 86_401, 300)
        ],
    }
    return policy, reports


def write_reports(root, reports):
    references = {}
    for profile, report in reports.items():
        path = root / f"{profile}.json"
        raw = json.dumps(report).encode()
        path.write_bytes(raw)
        references[profile] = {
            "report": path.name,
            "sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        }
    return {"reports": references}


def test_adoption_matches_all_protected_profiles(records, tmp_path):
    policy, reports = records
    evidence = write_reports(tmp_path, reports)
    assert verify_adoption(policy, evidence, tmp_path) == sorted(PROFILE_CASES)


def test_adoption_accepts_only_the_explicitly_selected_profiles(records, tmp_path):
    policy, reports = records
    policy["profiles"] = {"identity": policy["profiles"]["identity"]}
    evidence = write_reports(tmp_path, {"identity": reports["identity"]})
    assert verify_adoption(policy, evidence, tmp_path) == ["identity"]


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("candidate_sha", "b" * 40, "candidate_sha mismatch"),
        ("environment", "wrong-target", "environment mismatch"),
        ("run_id", "previous-run", "run_id mismatch"),
        ("profile", "github", "profile mismatch"),
        ("reviewer", "unexpected-reviewer", "unauthorized reviewer"),
        ("operator", " REVIEWER-IDENTITY ", "reviewer must be independent"),
    ],
)
def test_adoption_blocks_wrong_identity(records, tmp_path, field, value, reason):
    policy, reports = records
    reports["identity"][field] = value
    with pytest.raises(Rejected, match=reason):
        verify_adoption(policy, write_reports(tmp_path, reports), tmp_path)


@pytest.mark.parametrize(
    "mutation", ["missing", "failed", "duplicate", "blank", "skip"]
)
def test_adoption_requires_complete_passing_cases(records, tmp_path, mutation):
    policy, reports = records
    cases = reports["accessibility"]["cases"]
    match mutation:
        case "missing":
            cases.pop()
        case "failed":
            cases[0]["status"] = "failed"
        case "duplicate":
            cases.append(cases[0])
        case "blank":
            cases[0]["observation"] = " "
        case "skip":
            cases[0]["status"] = "skipped"
    with pytest.raises(Rejected):
        verify_adoption(policy, write_reports(tmp_path, reports), tmp_path)


def test_adoption_rejects_conflicting_or_altered_files(records, tmp_path):
    policy, reports = records
    evidence = write_reports(tmp_path, reports)
    evidence["reports"]["accessibility"]["report"] = "../outside.json"
    with pytest.raises(Rejected, match="escapes"):
        verify_adoption(policy, evidence, tmp_path)
    evidence = write_reports(tmp_path, reports)
    (tmp_path / "identity.json").write_bytes(b"{}")
    with pytest.raises(Rejected, match="digest mismatch"):
        verify_adoption(policy, evidence, tmp_path)


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("short", "24 hours"),
        ("gap", "gap limit"),
        ("duplicate", "gap limit"),
        ("missing_boundary", "end at the window boundary"),
        ("only_idle", "idle and workload"),
        ("unhealthy", "Unhealthy soak sample"),
        ("nonnumeric", "Invalid soak pressure"),
        ("nonfinite", "Invalid soak pressure"),
        ("bad_time", "positive integer Unix seconds"),
    ],
)
def test_adoption_checks_actual_soak_samples(records, tmp_path, mutation, reason):
    policy, reports = records
    soak = reports["remote"]["soak"]
    samples = soak["samples"]
    match mutation:
        case "short":
            soak["ended_at"] -= 300
            samples.pop()
        case "gap":
            samples.pop(10)
        case "duplicate":
            samples.insert(10, samples[10])
        case "missing_boundary":
            samples.pop()
        case "only_idle":
            for sample in samples:
                sample["activity"] = "idle"
        case "unhealthy":
            samples[10]["service"] = "unhealthy"
        case "nonnumeric":
            samples[10]["pressure"]["cpu_some_pct"] = True
        case "nonfinite":
            samples[10]["pressure"]["cpu_some_pct"] = float("inf")
        case "bad_time":
            samples[10]["at"] = 1.5
    with pytest.raises(Rejected, match=reason):
        verify_adoption(policy, write_reports(tmp_path, reports), tmp_path)


def test_adoption_cli_rejects_draft_and_duplicate_members(
    tmp_path, monkeypatch, capsys
):
    docs = ROOT / "standards/adoption"
    policy = tmp_path / "policy.json"
    policy.write_text((docs / "policy.template.json").read_text())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "operations-standard",
            "adoption",
            str(docs / "evidence.template.json"),
            "--policy",
            str(policy),
            "--reports",
            str(tmp_path),
        ],
    )
    assert main() == 1
    assert json.loads(capsys.readouterr().err)["status"] == "blocked"
    policy.write_text('{"environment": "old", "environment": "new"}')
    assert main() == 1
    assert "Duplicate JSON member" in json.loads(capsys.readouterr().err)["reason"]


def test_executable_case_catalog_matches_adoption_docs():
    docs = {
        "identity": "standards/adoption/identity.md",
        "gitops": "standards/adoption/gitops.md",
        "github": "standards/adoption/github.md",
        "accessibility": "standards/adoption/accessibility.md",
        "remote": "docs/remote-execution.md",
    }
    for profile, document in docs.items():
        rows = re.findall(r"^\| ([A-Z]+\d{2}) \|", (ROOT / document).read_text(), re.M)
        assert len(rows) == len(set(rows))
        assert set(rows) == PROFILE_CASES[profile]
