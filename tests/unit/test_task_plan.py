import copy
import json

import pytest

from backend_standard.gates import Rejected
from backend_standard.task_plan import Issue, promote, render, sync, validate


def task(identifier, depends=(), status="planned", **changes):
    value = {
        "id": identifier,
        "title": f"Task {identifier}",
        "goal": f"Deliver {identifier}.",
        "scope": ["One endpoint"],
        "non_goals": [],
        "requirement_ids": ["R-01"],
        "acceptance_criteria": ["Returns 201 with the created record"],
        "test_case_ids": ["TC01"],
        "depends_on": list(depends),
        "allowed_paths": ["src/app/*"],
        "size": "S",
        "status": status,
    }
    value.update(changes)
    return value


def plan(*tasks):
    return {"task_plan_standard": "0.1", "project": "demo", "tasks": list(tasks)}


VALID = plan(task("T01"), task("T02", ["T01"]), task("T03", ["T01"]))


class FakeTracker:
    def __init__(self, native=True):
        self.store = {}
        self.calls = []
        self.native = native
        self.deps = set()

    def issues(self):
        return [copy.deepcopy(issue) for issue in self.store.values()]

    def create(self, title, body, label):
        number = len(self.store) + 1
        self.store[number] = Issue(number, title, body, "open", {label})
        self.calls.append(("create", number))
        return copy.deepcopy(self.store[number])

    def edit(self, number, title, body):
        self.store[number].title, self.store[number].body = title, body
        self.calls.append(("edit", number))

    def set_label(self, issue, label):
        stored = self.store[issue.number]
        stored.labels = (stored.labels - {"ready", "waiting", "draft"}) | {label}
        issue.labels = set(stored.labels)
        self.calls.append(("label", issue.number, label))

    def add_dependency(self, number, dependency):
        if not self.native:
            return None
        if (number, dependency) in self.deps:
            return False
        self.deps.add((number, dependency))
        return True


def labels(tracker):
    return {n: sorted(i.labels) for n, i in tracker.store.items()}


def test_valid_plan_is_accepted():
    assert [t["id"] for t in validate(VALID)] == ["T01", "T02", "T03"]


def test_template_is_valid():
    with open("standards/planning/tasks.template.json") as handle:
        assert validate(json.load(handle))


@pytest.mark.parametrize(
    ("broken", "message"),
    [
        (plan(task("T01"), task("T01")), "duplicate id"),
        (plan(task("X1")), "invalid task id"),
        (plan(task("T01", ["T09"])), "unknown dependency T09"),
        (plan(task("T01", ["T02"]), task("T02", ["T01"])), "dependency cycle"),
        (plan(task("T01", ["T01"])), "depends on itself"),
        (plan(task("T01", goal="TBD")), "unresolved placeholder"),
        (plan(task("T01", acceptance_criteria=[])), "acceptance_criteria"),
        (plan(task("T01", test_case_ids=[])), "test_case_ids"),
        (plan(task("T01", size="L")), "split larger tasks"),
        (plan(task("T01", status="draft")), "open_decision"),
        (
            plan(
                task("T01", status="draft", open_decision="Pick a provider."),
                task("T02", ["T01"]),
            ),
            "depends on draft task T01",
        ),
        ({"task_plan_standard": "9", "project": "x", "tasks": []}, "version"),
    ],
)
def test_validation_rejects(broken, message):
    with pytest.raises(Rejected, match=message):
        validate(broken)


def test_sync_creates_issues_and_labels_by_dependency():
    tracker = FakeTracker()
    report = sync(validate(VALID), tracker)
    assert report["created"] == ["T01", "T02", "T03"]
    assert labels(tracker) == {1: ["ready"], 2: ["waiting"], 3: ["waiting"]}
    assert tracker.deps == {(2, 1), (3, 1)}
    assert "<!-- depends: 1 -->" in tracker.store[2].body
    assert tracker.store[2].title == "T02: Task T02"


def test_sync_is_idempotent():
    tracker = FakeTracker()
    sync(validate(VALID), tracker)
    tracker.calls.clear()
    report = sync(validate(VALID), tracker)
    assert tracker.calls == []
    assert report["created"] == report["updated"] == report["relabelled"] == []
    assert report["dependencies_added"] == 0


def test_sync_updates_only_changed_text():
    tracker = FakeTracker()
    sync(validate(VALID), tracker)
    changed = copy.deepcopy(VALID)
    changed["tasks"][2]["goal"] = "Deliver T03 with paging."
    report = sync(validate(changed), tracker)
    assert report["updated"] == ["T03"]
    assert "paging" in tracker.store[3].body


def test_sync_leaves_iris_labels_alone():
    tracker = FakeTracker()
    sync(validate(VALID), tracker)
    tracker.store[1].labels = {"in-progress"}
    changed = copy.deepcopy(VALID)
    changed["tasks"][0]["goal"] = "Deliver T01 again."
    report = sync(validate(changed), tracker)
    assert report["updated"] == ["T01"] and report["relabelled"] == []
    assert labels(tracker)[1] == ["in-progress"]


def test_draft_task_is_labelled_draft():
    tracker = FakeTracker()
    sync(
        validate(plan(task("T01", status="draft", open_decision="Pick one."))), tracker
    )
    assert labels(tracker) == {1: ["draft"]}
    assert "**Open decision.** Pick one." in tracker.store[1].body


def test_promote_after_dependency_closes():
    tracker = FakeTracker()
    sync(validate(VALID), tracker)
    assert promote(tracker) == []
    tracker.store[1].state = "closed"
    assert promote(tracker) == [2, 3]
    assert labels(tracker) == {1: ["ready"], 2: ["ready"], 3: ["ready"]}


def test_sync_marks_ready_when_dependency_already_closed():
    tracker = FakeTracker()
    sync(validate(VALID), tracker)
    tracker.store[1].state = "closed"
    sync(validate(VALID), tracker)
    assert labels(tracker)[2] == ["ready"]


def test_tasks_removed_from_the_plan_are_reported_not_deleted():
    tracker = FakeTracker()
    sync(validate(VALID), tracker)
    report = sync(validate(plan(task("T01"), task("T02", ["T01"]))), tracker)
    assert report["not_in_plan"] == ["T03"]
    assert 3 in tracker.store


def test_two_issues_for_one_task_are_rejected():
    tracker = FakeTracker()
    sync(validate(VALID), tracker)
    title, body = render(validate(VALID)[0], {})
    tracker.store[9] = Issue(9, title, body, "open", {"ready"})
    with pytest.raises(Rejected, match="two issues carry task T01"):
        sync(validate(VALID), tracker)


def test_missing_native_dependencies_are_reported():
    tracker = FakeTracker(native=False)
    report = sync(validate(VALID), tracker)
    assert report["native_dependencies"] is False
    assert labels(tracker) == {1: ["ready"], 2: ["waiting"], 3: ["waiting"]}
