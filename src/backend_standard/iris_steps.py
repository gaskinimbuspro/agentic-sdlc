"""Iris as separate steps, for a workflow engine such as Argo Workflows.

Each step runs in its own pod. Only claim, prepare, publish and finish receive
the git token; build receives only the model variables; check and guard receive
no secret at all. Steps share a work directory that holds the repository
checkout and a small state file. A step that finds an outcome already recorded
does nothing, so the workflow can always run to the end and let finish report.

The serial ``iris run-once`` command remains for a single host without a
workflow engine; both use the same functions from ``backend_standard.iris``.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from backend_standard.iris import (
    BLOCKED_NOTE,
    BUILDER_EMAIL,
    BUILDER_NAME,
    PROGRESS_NOTE,
    PROMPT_FILE,
    Config,
    Forgejo,
    IrisError,
    build_prompt,
    change_guards,
    git,
    load_config,
    require_builder_env,
    run_builder,
    run_checks,
)

STEPS = ("claim", "prepare", "build", "check", "guard", "publish", "finish")


def _state_path(work: Path) -> Path:
    return work / "state.json"


def _repo(work: Path) -> Path:
    return work / "repo"


def load_state(work: Path) -> dict[str, Any]:
    path = _state_path(work)
    return json.loads(path.read_text()) if path.is_file() else {}


def save_state(work: Path, state: dict[str, Any]) -> None:
    work.mkdir(parents=True, exist_ok=True)
    temporary = _state_path(work).with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2))
    temporary.replace(_state_path(work))


def _labels(config: Config, forge: Forgejo) -> dict[str, int]:
    ids = forge.label_ids()
    missing = [name for name in config.labels.values() if name not in ids]
    if missing:
        raise IrisError(f"Missing labels in Forgejo: {', '.join(missing)}")
    return {key: ids[name] for key, name in config.labels.items()}


def claim(config: Config, work: Path) -> str:
    """Take the oldest ready issue. Return its number, or "none"."""
    forge = Forgejo(config)
    label = _labels(config, forge)
    issues = forge.ready_issues(config.labels["ready"])
    if not issues:
        return "none"
    issue = issues[0]
    number = int(issue["number"])
    forge.relabel(number, label["in_progress"], label["ready"])
    save_state(
        work,
        {
            "issue": number,
            "title": str(issue.get("title", "")),
            "body": str(issue.get("body") or ""),
            "branch": f"iris/issue-{number}",
            "started": time.time(),
            "attempts": 0,
            "outcome": None,
        },
    )
    return str(number)


def prepare(config: Config, work: Path) -> str:
    state = load_state(work)
    if state.get("outcome"):
        return "skipped"
    repo = _repo(work)
    repo.mkdir(parents=True, exist_ok=True)
    token = config.token
    branch = state["branch"]
    git(repo, "clone", "--quiet", config.git_url, ".", token=token)
    if git(repo, "ls-remote", "--heads", "origin", branch, token=token).strip():
        state.update(outcome="blocked", reason=f"branch {branch} already exists")
        save_state(work, state)
        return "blocked"
    git(repo, "checkout", "--quiet", "-b", branch, f"origin/{config.base_branch}")
    git(repo, "config", "user.name", BUILDER_NAME)
    git(repo, "config", "user.email", BUILDER_EMAIL)
    # Remove the remote URL's credentials path entirely: the builder must not
    # find a way to reach the server from this checkout.
    git(repo, "remote", "set-url", "origin", "https://invalid.invalid/no-push")
    exclude = repo / ".git/info/exclude"
    exclude.write_text(exclude.read_text() + "\n.iris/\n")
    (repo / ".iris").mkdir(exist_ok=True)
    git(repo, "update-ref", "refs/iris/base", "HEAD")
    save_state(work, state)
    return "ready"


def build(config: Config, work: Path, attempt: int) -> str:
    state = load_state(work)
    if state.get("outcome"):
        return "skipped"
    require_builder_env(config)
    repo = _repo(work)
    state["attempts"] = attempt
    issue = {"number": state["issue"], "title": state["title"], "body": state["body"]}
    prompt = build_prompt(config, issue, state.get("feedback", ""))
    (repo / PROMPT_FILE).write_text(prompt)
    log = work / f"builder-{attempt}.log"
    status, code = run_builder(config, repo, prompt, log, f"iris-build-{attempt}")
    state["builder_exit"] = code
    note = repo / BLOCKED_NOTE
    if status == "timeout":
        state.update(
            outcome="blocked", reason=f"builder exceeded {config.wall_time_seconds} s"
        )
    elif note.is_file():
        question = note.read_text().strip()[:2000]
        state.update(outcome="blocked", reason=f"builder asks:\n\n{question}")
    elif code != 0:
        meaning = config.exit_reasons.get(str(code))
        reason = f"builder exited with {code}" + (f": {meaning}" if meaning else "")
        state.update(outcome="blocked", reason=reason)
    else:
        commits = int(git(repo, "rev-list", "--count", "refs/iris/base..HEAD").strip())
        state["commits"] = commits
        if commits == 0:
            state.update(outcome="blocked", reason="builder made no commit")
    save_state(work, state)
    return "blocked" if state.get("outcome") else "built"


def check(config: Config, work: Path, attempt: int) -> str:
    """Return passed, retry or blocked."""
    state = load_state(work)
    if state.get("outcome"):
        return "blocked"
    repo = _repo(work)
    if git(repo, "status", "--porcelain").strip():
        git(repo, "stash", "--include-untracked", "--quiet")
    passed, tail = run_checks(
        config, repo, work / f"check-{attempt}.log", f"iris-check-{attempt}"
    )
    state["checks_passed"] = passed
    (repo / PROGRESS_NOTE).write_text(
        f"Attempt {attempt}: checks {'passed' if passed else 'failed'}.\n\n{tail}\n"
    )
    if passed:
        state.pop("feedback", None)
        result = "passed"
    elif attempt > config.repair_rounds:
        state.update(
            outcome="blocked",
            reason=(
                f"checks still fail after {config.repair_rounds} repair round(s)."
                f" Last output:\n\n```\n{tail[-1500:]}\n```"
            ),
        )
        result = "blocked"
    else:
        state["feedback"] = tail
        result = "retry"
    save_state(work, state)
    return result


def guard(config: Config, work: Path) -> str:
    state = load_state(work)
    if state.get("outcome"):
        return "skipped"
    reason, files, lines = change_guards(config, _repo(work), "refs/iris/base")
    state.update(changed_files=files, changed_lines=lines)
    if reason:
        state.update(outcome="blocked", reason=reason)
    save_state(work, state)
    return "blocked" if reason else "clean"


def publish(config: Config, work: Path) -> str:
    state = load_state(work)
    if state.get("outcome"):
        return "skipped"
    if not state.get("checks_passed"):
        state.update(outcome="blocked", reason="checks did not pass")
        save_state(work, state)
        return "blocked"
    repo = _repo(work)
    forge = Forgejo(config)
    branch = state["branch"]
    git(repo, "remote", "set-url", "origin", config.git_url)
    git(
        repo,
        "push",
        "--quiet",
        "origin",
        f"HEAD:refs/heads/{branch}",
        token=config.token,
    )
    body = (
        f"Closes #{state['issue']}\n\n"
        f"Built by {BUILDER_NAME}, coordinated by Iris. "
        f"{state.get('commits', 0)} commit(s), {state.get('changed_files', 0)} "
        f"file(s) and {state.get('changed_lines', 0)} line(s) changed, checks "
        f"passed on attempt {state.get('attempts', 1)}. "
        "Cerberus runs the required checks; Argus reviews; Gökhan approves."
    )
    title = re.sub(r"\s+", " ", state["title"]).strip()
    state["pull"] = forge.open_pull(
        branch, config.base_branch, f"#{state['issue']}: {title}", body
    )
    state["outcome"] = "review"
    save_state(work, state)
    return "review"


def finish(config: Config, work: Path, workflow_status: str) -> str:
    """Report the outcome on the issue. Runs even when a step failed."""
    state = load_state(work)
    if not state.get("issue"):
        return "idle"
    if not state.get("outcome"):
        state.update(
            outcome="blocked",
            reason=f"workflow ended with status {workflow_status} before a decision",
        )
    forge = Forgejo(config)
    label = _labels(config, forge)
    number = int(state["issue"])
    state["ended"] = time.time()
    state["seconds"] = round(state["ended"] - state["started"], 1)
    if state["outcome"] == "review":
        forge.relabel(number, label["review"], label["in_progress"])
        forge.comment(
            number,
            f"Iris opened pull request #{state['pull']} from `{state['branch']}` "
            f"after {state['seconds']} s.",
        )
    else:
        forge.relabel(number, label["blocked"], label["in_progress"])
        forge.comment(number, f"Iris stopped: {state['reason']}")
    save_state(work, state)
    record = {key: value for key, value in state.items() if key not in {"body"}}
    print(json.dumps({"iris_run": record}))
    return str(state["outcome"])


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="iris-step", description=__doc__.splitlines()[0]
    )
    parser.add_argument("step", choices=STEPS)
    parser.add_argument("config", type=Path)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--workflow-status", default="Unknown")
    parser.add_argument(
        "--result-file", type=Path, help="also write the step result here"
    )
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if args.step == "claim":
            result = claim(config, args.work)
        elif args.step == "prepare":
            result = prepare(config, args.work)
        elif args.step == "build":
            result = build(config, args.work, args.attempt)
        elif args.step == "check":
            result = check(config, args.work, args.attempt)
        elif args.step == "guard":
            result = guard(config, args.work)
        elif args.step == "publish":
            result = publish(config, args.work)
        else:
            result = finish(config, args.work, args.workflow_status)
    except (IrisError, OSError, subprocess.SubprocessError, ValueError) as error:
        if args.step not in {"claim", "finish"}:
            state = load_state(args.work)
            if state.get("issue") and not state.get("outcome"):
                state.update(
                    outcome="blocked", reason=f"Iris error in {args.step}: {error}"
                )
                save_state(args.work, state)
                result = "blocked"
                print(result)
                if args.result_file:
                    args.result_file.write_text(result)
                return 0
        print(json.dumps({"status": "error", "reason": str(error)}), file=sys.stderr)
        return 1
    print(result)
    if args.result_file:
        args.result_file.write_text(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
