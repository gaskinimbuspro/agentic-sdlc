"""Validate a project discovery record: every stage answered and approved in order.

This checks structure and completeness of supplied answers. It cannot judge
whether an answer is good, and it does not authenticate the approver.
"""

from __future__ import annotations

import argparse
import json
import os
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


def _tasks(args: argparse.Namespace) -> int:
    from backend_standard.iris import Forgejo, IrisError
    from backend_standard.task_plan import ForgejoTracker, label_names, promote, sync
    from backend_standard.task_plan import validate as validate_plan

    try:
        tasks = [] if args.action == "promote" else validate_plan(document(args.path))
        if args.action == "validate":
            print(json.dumps({"status": "valid", "tasks": len(tasks)}))
            return 0
        require(args.forgejo_url and args.repo, "--forgejo-url and --repo are required")
        owner, _, name = str(args.repo).partition("/")
        require(owner and name, "--repo must be OWNER/NAME")
        token = os.environ.get(args.token_env, "").strip()
        forge = Forgejo.for_repo(args.forgejo_url, owner, name, token)
        tracker = ForgejoTracker(forge, owner, name, label_names())
        if args.action == "sync":
            result: dict[str, Any] = sync(tasks, tracker)
        else:
            result = {"promoted": promote(tracker)}
    except (Rejected, IrisError, ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({"status": "blocked", "reason": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps({"status": "done", "action": args.action, **result}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="planning-standard")
    sub = parser.add_subparsers(dest="command", required=True)
    discovery = sub.add_parser("discovery")
    discovery.add_argument("path", type=Path)
    discovery.add_argument("--stage", type=int, help="require completion through N")
    tasks = sub.add_parser("tasks", help="validate a task plan or sync it to Forgejo")
    tasks.add_argument("action", choices=("validate", "sync", "promote"))
    tasks.add_argument("path", type=Path, nargs="?", default=Path("plan/tasks.json"))
    tasks.add_argument("--forgejo-url", help="for sync and promote")
    tasks.add_argument("--repo", help="OWNER/NAME, for sync and promote")
    tasks.add_argument("--token-env", default="FORGEJO_TOKEN")
    args = parser.parse_args()
    if args.command == "tasks":
        return _tasks(args)
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
