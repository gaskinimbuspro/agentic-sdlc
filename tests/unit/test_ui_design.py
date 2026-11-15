import copy
import json
import sys
from pathlib import Path

import pytest

from backend_standard.gates import Rejected
from backend_standard.ui import main, validate_design

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "standards/ui/examples/customer-admin/design-packet.json"


def test_example_is_reviewable_not_approved():
    validate_design(json.loads(EXAMPLE.read_text()), ROOT)


@pytest.mark.parametrize(
    "failure",
    [
        "draft",
        "duplicate_requirement",
        "duplicate_route",
        "unknown_actor",
        "missing_state",
        "inapplicable_destination",
        "unknown_destination",
        "missing_api_response",
        "unknown_api",
        "missing_case",
        "orphan_requirement",
        "disconnected_journey",
        "unknown_case_family",
        "missing_visual",
        "path_escape",
        "unresolved_decision",
        "unreachable_screen",
        "unused_interaction",
        "duplicate_case",
        "api_on_navigation",
    ],
)
def test_rejects_incomplete_or_inconsistent_design(failure):
    packet = json.loads(EXAMPLE.read_text())
    match failure:
        case "draft":
            packet["status"] = "draft"
        case "duplicate_requirement":
            packet["requirements"].append(copy.deepcopy(packet["requirements"][0]))
        case "duplicate_route":
            packet["screens"][1]["route"] = packet["screens"][0]["route"]
        case "unknown_actor":
            packet["screens"][0]["actor_ids"] = ["unrecorded-role"]
        case "missing_state":
            packet["screens"][0]["states"].pop("error")
        case "inapplicable_destination":
            packet["interactions"][1]["outcomes"][0]["state"] = "empty"
        case "unknown_destination":
            packet["interactions"][1]["outcomes"][0]["screen_id"] = "UNKNOWN"
        case "missing_api_response":
            packet["interactions"][0]["outcomes"].pop()
        case "unknown_api":
            packet["interactions"][0]["api"]["path"] = "/not-in-contract"
        case "missing_case":
            packet["test_cases"].pop()
        case "orphan_requirement":
            packet["requirements"].append(
                {"id": "ORPHAN", "description": "Unmapped requested behavior"}
            )
        case "disconnected_journey":
            packet["journeys"][1]["steps"][1] = {
                "interaction_id": "CANCEL",
                "outcome_id": "list",
            }
        case "unknown_case_family":
            packet["test_cases"][0]["family"] = "UC99"
        case "missing_visual":
            packet["visual_assets"] = ["missing-wireframe.svg"]
        case "path_escape":
            packet["visual_assets"] = ["../outside.svg"]
        case "unresolved_decision":
            packet["quality"]["session_and_privacy"] = "TBD"
        case "unreachable_screen":
            screen = copy.deepcopy(packet["screens"][0])
            screen.update(id="ORPHAN", route="/orphan")
            packet["screens"].append(screen)
        case "unused_interaction":
            interaction = copy.deepcopy(packet["interactions"][1])
            interaction["id"] = "UNUSED"
            packet["interactions"].append(interaction)
        case "duplicate_case":
            packet["test_cases"].append(copy.deepcopy(packet["test_cases"][0]))
        case "api_on_navigation":
            packet["interactions"][1]["api"] = {"method": "GET", "path": "/customers"}
    with pytest.raises(Rejected):
        validate_design(packet, ROOT)


@pytest.mark.parametrize("change_flag", [False, True])
def test_template_cannot_be_accepted_by_changing_its_status(change_flag):
    packet = json.loads((ROOT / "standards/ui/design-packet.template.json").read_text())
    if change_flag:
        packet["status"] = "reviewable"
    with pytest.raises(Rejected):
        validate_design(packet, ROOT)


def test_cli_blocks_incomplete_input_and_limits_success_claim(
    tmp_path, monkeypatch, capsys
):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}")
    monkeypatch.setattr(sys, "argv", ["ui-standard", "design", str(invalid)])
    assert main() == 1
    assert json.loads(capsys.readouterr().err)["status"] == "blocked"
    monkeypatch.setattr(
        sys, "argv", ["ui-standard", "design", str(EXAMPLE), "--root", str(ROOT)]
    )
    assert main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "reviewable"
    assert "approval and runtime verification required" in output["scope"]
