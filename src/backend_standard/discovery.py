"""Validate a project discovery record: every stage answered and approved in order.

This checks structure and completeness of supplied answers. It cannot judge
whether an answer is good, and it does not authenticate the approver.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from backend_standard.gates import Rejected, document, require, text

QUESTIONS = Path(__file__).parent / "schemas/discovery.questions.json"
STATUSES = {"answered", "open", "not_applicable"}


def canonical() -> list[dict[str, Any]]:
    stages = json.loads(QUESTIONS.read_text())["stages"]
    return list(stages)


def _stage_complete(stage: dict[str, Any], expected: dict[str, Any]) -> None:
    label = expected["id"]
    questions = stage.get("questions")
    if not isinstance(questions, list):
        raise Rejected(f"{label}: questions must be a list")
    wanted = [question["id"] for question in expected["questions"]]
    found = [q.get("id") if isinstance(q, dict) else None for q in questions]
    require(found == wanted, f"{label}: missing, unknown or reordered questions")
    for question in questions:
        identifier = question["id"]
        status = question.get("status")
        require(status in STATUSES, f"{identifier}: unknown status")
        require(status != "open", f"{identifier}: still open")
        if status == "answered":
            answer = text(question.get("answer"), f"{identifier}: answer")
            require(len(answer.strip()) >= 3, f"{identifier}: answer too short")
        else:
            text(question.get("reason"), f"{identifier}: reason for not applicable")


def verify_discovery(record: dict[str, Any], through: int | None = None) -> int:
    """Return the number of leading stages that are complete and approved."""
    require(record.get("discovery_standard") == "0.1", "Unsupported discovery version")
    text(record.get("project"), "project")
    owner = text(record.get("product_owner"), "product_owner")
    agents = record.get("agent_identities")
    if not isinstance(agents, list):
        raise Rejected("agent_identities must be a list")
    lowered = {str(agent).strip().casefold() for agent in agents}
    require(owner.strip().casefold() not in lowered, "Product owner cannot be an agent")
    expected = canonical()
    stages = record.get("stages")
    if not isinstance(stages, list):
        raise Rejected("stages must be a list")
    ids = [stage.get("id") if isinstance(stage, dict) else None for stage in stages]
    require(
        ids == [stage["id"] for stage in expected],
        "Missing, unknown or reordered stages",
    )
    target = len(expected) if through is None else through
    require(1 <= target <= len(expected), "Stage number out of range")
    complete = 0
    gap = False
    for stage, wanted in zip(stages, expected, strict=True):
        approved = stage.get("approved_by") is not None
        if approved:
            require(not gap, f"{wanted['id']}: approved before an earlier stage")
            require(
                stage.get("approved_by") == owner,
                f"{wanted['id']}: only the product owner approves a stage",
            )
            require(
                bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(stage.get("approved_at")))),
                f"{wanted['id']}: approval date required (YYYY-MM-DD)",
            )
            _stage_complete(stage, wanted)
            complete += 1
        else:
            gap = True
    require(
        complete >= target,
        f"Discovery is complete through stage {complete}; stage {target} required",
    )
    return complete


def main() -> int:
    parser = argparse.ArgumentParser(prog="planning-standard")
    sub = parser.add_subparsers(dest="command", required=True)
    discovery = sub.add_parser("discovery")
    discovery.add_argument("path", type=Path)
    discovery.add_argument("--stage", type=int, help="require completion through N")
    args = parser.parse_args()
    try:
        complete = verify_discovery(document(args.path), args.stage)
    except (Rejected, ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({"status": "blocked", "reason": str(error)}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "complete",
                "through_stage": complete,
                "scope": "answers present and approved in order; not a judgement"
                " of their quality or an authenticated approval",
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
