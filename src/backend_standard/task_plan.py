"""Turn a reviewed task plan into Forgejo issues, and mark tasks ready in order.

The plan file (``plan/tasks.json`` in the project repository) is the source of
truth: the architect writes it in a pull request and the product owner's merge
approves it. Issues are a view of the plan. ``sync`` creates or updates one
issue per task, idempotently, and labels it ``draft``, ``waiting`` or
``ready``. ``promote`` turns ``waiting`` into ``ready`` once every dependency
issue is closed. Issues that Iris is working on (``in-progress``, ``review``,
``blocked``) keep their label; only their text is refreshed.
"""

from __future__ import annotations

import re
import urllib.parse
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol

from backend_standard.gates import Rejected, require, text

STANDARD = "0.1"
TASK_ID = re.compile(r"T\d{2,3}")
MARKER = re.compile(r"<!-- task: (T\d{2,3}) -->")
DEPENDS = re.compile(r"<!-- depends: ([\d, ]*) -->")
SIZES = {"S", "M"}
STATUSES = {"planned", "draft"}
MANAGED = ("ready", "waiting", "draft")
HANDS_OFF = ("in-progress", "review", "blocked")
LIST_FIELDS = (
    "scope",
    "requirement_ids",
    "acceptance_criteria",
    "test_case_ids",
    "allowed_paths",
)


def _strings(task: dict[str, Any], key: str, label: str, empty_ok: bool) -> list[str]:
    values = task.get(key)
    if not isinstance(values, list) or (not values and not empty_ok):
        raise Rejected(f"{label}: {key} must be a non-empty list")
    return [text(value, f"{label}: {key}") for value in values]


def validate(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the tasks in file order, or raise Rejected with the first problem."""
    require(plan.get("task_plan_standard") == STANDARD, "Unsupported task plan version")
    text(plan.get("project"), "project")
    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise Rejected("tasks must be a non-empty list")
    seen: dict[str, dict[str, Any]] = {}
    for task in tasks:
        require(isinstance(task, dict), "each task must be an object")
        identifier = task.get("id")
        require(
            isinstance(identifier, str) and TASK_ID.fullmatch(identifier),
            f"invalid task id: {identifier!r}",
        )
        require(identifier not in seen, f"{identifier}: duplicate id")
        title = text(task.get("title"), f"{identifier}: title")
        require(len(title) <= 80, f"{identifier}: title longer than 80 characters")
        text(task.get("goal"), f"{identifier}: goal")
        for key in LIST_FIELDS:
            _strings(task, key, identifier, empty_ok=False)
        _strings(task, "non_goals", identifier, empty_ok=True)
        require(
            task.get("size") in SIZES,
            f"{identifier}: size must be S or M; split larger tasks",
        )
        status = task.get("status")
        require(status in STATUSES, f"{identifier}: status must be planned or draft")
        if status == "draft":
            text(task.get("open_decision"), f"{identifier}: open_decision")
        depends = task.get("depends_on", [])
        require(
            isinstance(depends, list) and all(isinstance(d, str) for d in depends),
            f"{identifier}: depends_on must be a list of task ids",
        )
        require(identifier not in depends, f"{identifier}: depends on itself")
        require(len(set(depends)) == len(depends), f"{identifier}: repeated dependency")
        seen[identifier] = task
    for identifier, task in seen.items():
        for dependency in task.get("depends_on", []):
            require(
                dependency in seen, f"{identifier}: unknown dependency {dependency}"
            )
            if task["status"] == "planned":
                require(
                    seen[dependency]["status"] == "planned",
                    f"{identifier}: depends on draft task {dependency}",
                )
    _reject_cycles(seen)
    return list(seen.values())


def _reject_cycles(tasks: dict[str, dict[str, Any]]) -> None:
    state: dict[str, str] = {}

    def visit(identifier: str, path: list[str]) -> None:
        if state.get(identifier) == "done":
            return
        if state.get(identifier) == "active":
            loop = path[path.index(identifier) :] + [identifier]
            raise Rejected("dependency cycle: " + " -> ".join(loop))
        state[identifier] = "active"
        for dependency in tasks[identifier].get("depends_on", []):
            visit(dependency, [*path, identifier])
        state[identifier] = "done"

    for identifier in tasks:
        visit(identifier, [])


def render(task: dict[str, Any], numbers: dict[str, int]) -> tuple[str, str]:
    """Return the issue title and body for a task."""
    depends = [numbers[d] for d in task.get("depends_on", []) if d in numbers]
    lines = [
        f"<!-- task: {task['id']} -->",
        f"<!-- depends: {', '.join(str(n) for n in depends)} -->",
        f"**Goal.** {task['goal']}",
        "",
    ]
    if task["status"] == "draft":
        lines += [f"**Open decision.** {task['open_decision']}", ""]
    lines += [
        "**Acceptance criteria**",
        *[f"- {c}" for c in task["acceptance_criteria"]],
    ]
    lines += ["", f"**Test cases:** {', '.join(task['test_case_ids'])}"]
    lines += [f"**Requirements:** {', '.join(task['requirement_ids'])}", ""]
    lines += ["**Scope**", *[f"- {s}" for s in task["scope"]]]
    if task.get("non_goals"):
        lines += ["", "**Not in scope**", *[f"- {s}" for s in task["non_goals"]]]
    paths = ", ".join(f"`{p}`" for p in task["allowed_paths"])
    lines += ["", f"**Allowed paths:** {paths}", f"**Size:** {task['size']}"]
    if task.get("depends_on"):
        refs = ", ".join(
            f"#{numbers[d]} ({d})" if d in numbers else d for d in task["depends_on"]
        )
        lines += [f"**Depends on:** {refs}"]
    lines += [
        "",
        "_Generated from `plan/tasks.json`. Change the plan in a pull request, "
        "not this issue._",
    ]
    return f"{task['id']}: {task['title']}", "\n".join(lines) + "\n"


@dataclass
class Issue:
    number: int
    title: str
    body: str
    state: str
    labels: set[str] = field(default_factory=set)

    @property
    def task_id(self) -> str | None:
        match = MARKER.search(self.body)
        return match.group(1) if match else None

    @property
    def depends(self) -> list[int]:
        match = DEPENDS.search(self.body)
        if not match or not match.group(1).strip():
            return []
        return [int(n) for n in match.group(1).split(",") if n.strip()]


class Tracker(Protocol):
    def issues(self) -> list[Issue]: ...

    def create(self, title: str, body: str, label: str) -> Issue: ...

    def edit(self, number: int, title: str, body: str) -> None: ...

    def set_label(self, issue: Issue, label: str) -> None: ...

    def add_dependency(self, number: int, dependency: int) -> bool | None: ...


def _wanted(task: dict[str, Any], issue_of: dict[str, Issue]) -> str:
    if task["status"] == "draft":
        return "draft"
    done = all(
        issue_of[d].state == "closed"
        for d in task.get("depends_on", [])
        if d in issue_of
    )
    return "ready" if done else "waiting"


def sync(tasks: list[dict[str, Any]], tracker: Tracker) -> dict[str, Any]:
    """Make the issues match the plan. Safe to run again: it converges."""
    issue_of: dict[str, Issue] = {}
    for issue in tracker.issues():
        if issue.task_id:
            require(
                issue.task_id not in issue_of,
                f"two issues carry task {issue.task_id}: "
                f"#{issue_of.get(issue.task_id, issue).number} and #{issue.number}",
            )
            issue_of[issue.task_id] = issue
    report: dict[str, Any] = {
        "created": [],
        "updated": [],
        "relabelled": [],
        "dependencies_added": 0,
        "native_dependencies": True,
    }
    # Pass 1: every task gets an issue, so dependency numbers are known.
    for task in tasks:
        if task["id"] not in issue_of:
            title, body = render(task, {})
            label = "draft" if task["status"] == "draft" else "waiting"
            issue_of[task["id"]] = tracker.create(title, body, label)
            report["created"].append(task["id"])
    numbers = {identifier: issue.number for identifier, issue in issue_of.items()}
    # Pass 2: text, dependencies and state label.
    for task in tasks:
        issue = issue_of[task["id"]]
        title, body = render(task, numbers)
        if (issue.title, issue.body) != (title, body):
            tracker.edit(issue.number, title, body)
            issue.title, issue.body = title, body
            if task["id"] not in report["created"]:
                report["updated"].append(task["id"])
        if report["native_dependencies"]:
            for dependency in task.get("depends_on", []):
                added = tracker.add_dependency(issue.number, numbers[dependency])
                if added is None:
                    report["native_dependencies"] = False
                    break
                report["dependencies_added"] += int(added)
        if issue.state != "open" or issue.labels & set(HANDS_OFF):
            continue
        wanted = _wanted(task, issue_of)
        if wanted not in issue.labels or issue.labels & set(MANAGED) - {wanted}:
            tracker.set_label(issue, wanted)
            report["relabelled"].append(f"{task['id']}:{wanted}")
    planned = {task["id"] for task in tasks}
    report["not_in_plan"] = sorted(i for i in issue_of if i not in planned)
    return report


def promote(tracker: Tracker) -> list[int]:
    """Relabel waiting issues whose dependencies are all closed. Return them."""
    issues = tracker.issues()
    state = {issue.number: issue.state for issue in issues}
    promoted = []
    for issue in issues:
        if issue.state != "open" or "waiting" not in issue.labels:
            continue
        if all(state.get(number) == "closed" for number in issue.depends):
            tracker.set_label(issue, "ready")
            promoted.append(issue.number)
    return promoted


class ForgejoTracker:
    """Tracker backed by the Forgejo REST API, through Iris's client."""

    def __init__(self, forge: Any, owner: str, repo: str, names: dict[str, str]):
        self.forge = forge
        self.owner = owner
        self.repo = repo
        self.names = names
        self.path = f"/repos/{owner}/{repo}"
        ids = forge.label_ids()
        missing = [name for name in names.values() if name not in ids]
        if missing:
            raise Rejected(f"Missing labels in Forgejo: {', '.join(sorted(missing))}")
        self.ids = {key: ids[name] for key, name in names.items()}
        self.key_of = {name: key for key, name in names.items()}

    def _issue(self, raw: dict[str, Any]) -> Issue:
        names = {str(item["name"]) for item in raw.get("labels", [])}
        return Issue(
            number=int(raw["number"]),
            title=str(raw.get("title", "")),
            body=str(raw.get("body") or ""),
            state=str(raw.get("state", "open")),
            labels={self.key_of[name] for name in names if name in self.key_of},
        )

    def issues(self) -> list[Issue]:
        found: list[Issue] = []
        page = 1
        while True:
            query = urllib.parse.urlencode(
                {"state": "all", "type": "issues", "limit": 50, "page": page}
            )
            batch = self.forge.request("GET", f"{self.path}/issues?{query}")
            found += [self._issue(raw) for raw in batch if not raw.get("pull_request")]
            if len(batch) < 50:
                return found
            page += 1

    def create(self, title: str, body: str, label: str) -> Issue:
        raw = self.forge.request(
            "POST",
            f"{self.path}/issues",
            {"title": title, "body": body, "labels": [self.ids[label]]},
        )
        return self._issue(raw)

    def edit(self, number: int, title: str, body: str) -> None:
        self.forge.request(
            "PATCH", f"{self.path}/issues/{number}", {"title": title, "body": body}
        )

    def set_label(self, issue: Issue, label: str) -> None:
        for other in MANAGED:
            if other != label and other in issue.labels:
                self.forge.request(
                    "DELETE",
                    f"{self.path}/issues/{issue.number}/labels/{self.ids[other]}",
                )
        if label not in issue.labels:
            self.forge.request(
                "POST",
                f"{self.path}/issues/{issue.number}/labels",
                {"labels": [self.ids[label]]},
            )
        issue.labels = (issue.labels - set(MANAGED)) | {label}

    def add_dependency(self, number: int, dependency: int) -> bool | None:
        """Add a native Forgejo dependency. None when the server does not offer it."""
        from backend_standard.iris import IrisError

        route = f"{self.path}/issues/{number}/dependencies"
        try:
            current = self.forge.request("GET", route)
        except IrisError as error:
            if re.search(r"HTTP (404|405|403)", str(error)):
                return None
            raise
        if any(int(item.get("number", 0)) == dependency for item in current or []):
            return False
        self.forge.request(
            "POST", route, {"owner": self.owner, "repo": self.repo, "index": dependency}
        )
        return True


def label_names(overrides: Iterable[tuple[str, str]] = ()) -> dict[str, str]:
    names = {key: key for key in (*MANAGED, *HANDS_OFF)}
    names.update(dict(overrides))
    return names
