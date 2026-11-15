"""Validate UI design completeness; never grant approval or execution authority."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import unquote_to_bytes

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from backend_standard.gates import Rejected, confined, document, require, text


def indexed(items: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result = {item["id"]: item for item in items}
    require(len(result) == len(items), f"Duplicate {label} ID")
    return result


def response_keys(api: dict[str, Any], binding: dict[str, str]) -> set[str]:
    paths = api.get("paths")
    if not isinstance(paths, dict):
        raise Rejected("API contract must declare a paths object")
    path = paths.get(binding["path"])
    if not isinstance(path, dict):
        raise Rejected("API path missing or invalid in contract")
    operation = path.get(binding["method"].lower())
    if not isinstance(operation, dict):
        raise Rejected("API operation missing from contract")
    responses = operation.get("responses")
    if not isinstance(responses, dict):
        raise Rejected("API responses must be an object")
    entries = {
        key: value for key, value in responses.items() if not key.startswith("x-")
    }
    require(
        entries
        and all(
            re.fullmatch(r"default|[1-5](?:[0-9]{2}|XX)", key)
            and isinstance(value, dict)
            for key, value in entries.items()
        ),
        "API contract must declare valid response entries",
    )
    return set(entries)


def validate_design(packet: dict[str, Any], root: Path) -> None:
    schema = document(Path(__file__).parent / "schemas/ui-design.schema.json")
    try:
        Draft202012Validator(schema).validate(packet)
    except ValidationError as error:
        raise Rejected("UI design schema: " + ".".join(map(str, error.path))) from error

    def resolved(value: Any) -> None:
        if isinstance(value, str):
            text(value, "Design decision")
        elif isinstance(value, dict):
            for child in value.values():
                resolved(child)
        elif isinstance(value, list):
            for child in value:
                resolved(child)

    resolved(packet)
    for path in [
        packet["design_document"],
        *packet["visual_assets"],
        packet["design_system"]["tokens_path"],
        packet["design_system"]["components_document"],
    ]:
        confined(root, path)
    requirements = indexed(packet["requirements"], "requirement")
    screens = indexed(packet["screens"], "screen")
    interactions = indexed(packet["interactions"], "interaction")
    journeys = indexed(packet["journeys"], "journey")
    cases = indexed(packet["test_cases"], "test case")
    actors = packet["actors"]
    require(len(actors) == len(set(actors)), "Duplicate actor")
    routes: set[tuple[bytes, ...]] = set()
    for screen in screens.values():
        require(set(screen["actor_ids"]) <= set(actors), "Unknown screen actor")
        route = screen["route"]
        require(
            route.startswith("/")
            and not route.startswith("//")
            and not any(c in route for c in "?#\\")
            and not re.search(r"[\x00-\x20\x7f]|%(?![0-9a-fA-F]{2})", route),
            "Expected an application route path",
        )
        segments = tuple(unquote_to_bytes(segment) for segment in route.split("/"))
        require(
            b"." not in segments and b".." not in segments,
            "Expected an application route path",
        )
        require(segments not in routes, "Duplicate screen route")
        routes.add(segments)

    def destination(screen_id: str, state: str) -> None:
        require(screen_id in screens, "Unknown screen destination")
        state_decision = screens[screen_id]["states"].get(state)
        require(
            state_decision and state_decision["kind"] == "designed",
            "Unknown or inapplicable interaction state",
        )

    api = (
        document(confined(root, packet["api_contract"]))
        if packet["api_contract"]
        else {}
    )
    outcomes: dict[tuple[str, str], dict[str, Any]] = {}
    for identifier, interaction in interactions.items():
        for state in interaction["source_states"]:
            destination(interaction["screen_id"], state)
        own_outcomes = indexed(interaction["outcomes"], "interaction outcome")
        for outcome in own_outcomes.values():
            destination(outcome["screen_id"], outcome["state"])
            outcomes[(identifier, outcome["id"])] = outcome
        if interaction["kind"] == "request":
            require(interaction["api"] is not None, "Request API binding missing")
            destination(interaction["screen_id"], interaction["pending_state"])
            contract_keys = response_keys(api, interaction["api"])
            statuses = {outcome["http_status"] for outcome in own_outcomes.values()}
            require(
                statuses - {None} == contract_keys,
                "API response mapping is incomplete or unexpected",
            )
            require(None in statuses, "Request has no outcome without an HTTP response")
        else:
            require(
                interaction["api"] is None and interaction["pending_state"] is None,
                "Non-request action declares API/loading binding",
            )
            require(
                all(
                    outcome["http_status"] is None for outcome in own_outcomes.values()
                ),
                "Non-request action declares HTTP status",
            )

    interaction_requirements: defaultdict[str, set[str]] = defaultdict(set)
    used_requirements, visited = set(), set()
    for journey in journeys.values():
        journey_requirements = set(journey["requirement_ids"])
        require(
            journey_requirements <= set(requirements),
            "Unknown journey requirement",
        )
        used_requirements.update(journey_requirements)
        current = (journey["entry_screen"], journey["entry_state"])
        destination(*current)
        visited.add(current[0])
        for step in journey["steps"]:
            require(
                step["interaction_id"] in interactions, "Unknown journey interaction"
            )
            interaction = interactions[step["interaction_id"]]
            require(
                current[0] == interaction["screen_id"]
                and current[1] in interaction["source_states"],
                "Disconnected journey step",
            )
            key = (step["interaction_id"], step["outcome_id"])
            require(key in outcomes, "Unknown journey outcome")
            outcome = outcomes[key]
            current = (outcome["screen_id"], outcome["state"])
            interaction_requirements[step["interaction_id"]].update(
                journey_requirements
            )
            visited.add(current[0])
    require(
        interaction_requirements.keys() == interactions.keys(),
        "An interaction has no declared journey",
    )
    require(used_requirements == set(requirements), "A requirement has no journey")
    # Error alternatives must also reference declared screens; all screens must
    # be reached through a journey entry/step or one of its mapped alternatives.
    visited.update(outcome["screen_id"] for outcome in outcomes.values())
    require(visited == set(screens), "A screen is unreachable from declared journeys")
    covered, tested_requirements = set(), set()
    for case in cases.values():
        key = (case["interaction_id"], case["outcome_id"])
        require(key in outcomes, "Test references unknown interaction/outcome")
        case_requirements = set(case["requirement_ids"])
        require(
            case_requirements <= interaction_requirements[case["interaction_id"]],
            "Test requirement is unrelated to the interaction's journeys",
        )
        tested_requirements.update(case_requirements)
        covered.add(key)
    require(covered == set(outcomes), "An interaction outcome has no acceptance case")
    require(
        tested_requirements == set(requirements), "A requirement has no acceptance case"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    design = sub.add_parser("design")
    design.add_argument("path", type=Path)
    design.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        validate_design(document(args.path), args.root)
    except (Rejected, ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({"status": "blocked", "reason": str(error)}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "reviewable",
                "scope": "design completeness only; approval and runtime verification required",
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
