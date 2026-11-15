import copy
import json
from pathlib import Path

import pytest

from backend_standard.gates import Rejected, profile_ready, task_ready

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("language", ["python", "go", "dotnet"])
def test_complete_reference_profiles(language):
    profile_ready(
        json.loads((ROOT / f"reference/profiles/{language}.json").read_text()), ROOT
    )


def test_ready_task_does_not_need_a_future_candidate():
    profile = json.loads((ROOT / "reference/profiles/python.json").read_text())
    packet = json.loads((ROOT / "reference/task-packet.json").read_text())
    assert packet["candidate_sha"] is None
    task_ready(packet, profile, ROOT, set())


@pytest.mark.parametrize(
    "failure",
    [
        "unresolved",
        "outside_contract",
        "missing_command",
        "no_criteria",
        "unmapped_requirement",
        "unknown_case",
        "dependency",
        "path_escape",
        "no_budget",
    ],
)
def test_rejects_invalid_ready_task(failure):
    profile = json.loads((ROOT / "reference/profiles/python.json").read_text())
    packet = copy.deepcopy(
        json.loads((ROOT / "reference/task-packet.json").read_text())
    )
    match failure:
        case "unresolved":
            packet["goal"] = "TBD"
        case "outside_contract":
            packet["contract_references"] = ["../outside.json"]
        case "missing_command":
            packet["required_commands"].pop("unit")
        case "no_criteria":
            packet["acceptance_criteria"] = []
        case "unmapped_requirement":
            packet["acceptance_criteria"][0]["requirement_id"] = "unknown"
        case "unknown_case":
            packet["test_case_ids"] = ["TC99"]
        case "dependency":
            packet["dependency_task_ids"] = ["not-finished"]
        case "path_escape":
            packet["allowed_paths"] = ["../outside"]
        case "no_budget":
            packet["budget"]["max_repair_attempts"] = None
    with pytest.raises(Rejected):
        task_ready(packet, profile, ROOT, set())
