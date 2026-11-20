# Iris: the serial coordinator

Iris is the [cast](cast.md)'s coordinator: a small program, not a model. One run takes the oldest issue labelled `ready` in Forge, has Daedalus build it in a sandbox, and either opens a pull request or marks the issue `blocked` with the reason. It implements Phase 3 of the [pilot runbook](pilot-runbook.md).

Status: **written and tested against a fake Forgejo API, a local git repository and stand-in builders. Not yet run against a real Forgejo, Docker sandbox or Qwen Code.** Its Forgejo calls follow the Gitea-compatible REST API and must be confirmed on the installed version.

Code: [`src/backend_standard/iris.py`](../../src/backend_standard/iris.py). Tests: [`tests/unit/test_iris.py`](../../tests/unit/test_iris.py).

## One run

1. Take a host lock so only one Iris runs at a time.
2. Find the oldest open issue labelled `ready` and relabel it `in-progress`.
3. Clone the repository into a fresh temporary workspace and create `iris/issue-<n>`. If that branch already exists on the server, stop; Iris never overwrites one.
4. Write the prompt: fixed rules first, then the issue text between markers as data. Run the builder in the sandbox with only the listed model variables and a wall-time limit.
5. Decide:

| Builder result | Outcome |
| --- | --- |
| Wrote `.iris/BLOCKED.md` | `blocked`, and its question is posted on the issue |
| Timed out, exited non-zero or made no commit | `blocked` with the reason |
| Changed a protected path such as the CI file | `blocked`; nothing is pushed |
| Committed, exited cleanly, touched nothing protected | Branch pushed, pull request opened with `Closes #<n>`, issue relabelled `review` |

6. Comment on the issue and append a record to `runs.jsonl` in the log directory: issue, branch, seconds, builder exit code, commits, changed files, pull request. These feed the pilot's [measurement table](pilot-runbook.md#phase-4--measure).

## What keeps it safe

- The Forgejo token is passed to git through environment configuration, never on the command line, and is never in the builder's environment. A test checks the builder's environment directly.
- The builder has no git server access; only Iris pushes. Injected text in an issue cannot make the model push or open pull requests ([AS01, AS02, AS04](../../standards/agent-delivery/security.md)).
- The docker sandbox drops all capabilities, forbids privilege escalation, runs as the invoking user and mounts only the workspace. Restricting outbound traffic is done by the Docker network named in `docker_network`, which the operator must create with an allowlist ([AS03](../../standards/agent-delivery/security.md)).
- `local` sandbox mode runs the builder directly on the host. It exists for tests and trusted development only.

Tests also demonstrate the controls failing when broken: removing the protected-path check or passing the host environment to the builder makes the corresponding tests fail.

## Use

```sh
export IRIS_FORGEJO_TOKEN=...   # token of Iris's Forgejo user
uv run --no-sync iris check iris.json
uv run --no-sync iris run-once iris.json
```

Start from [the example configuration](iris.example.json). `check` verifies the API, repository, labels and builder executable. `run-once` exits 0 when it opened a pull request or found nothing ready, 2 when the issue was blocked and 1 on an error. Run it by hand during the pilot, or from a timer once it behaves.

Create the four labels in the repository first: `ready`, `in-progress`, `review` and `blocked`.

## Not yet

No claims across hosts, attempt budgets across runs, retries, crash recovery of a half-finished run, or parallel builders. A run interrupted after relabelling leaves the issue `in-progress` for a human to reset. Add these from the [dispatch ledger](../../src/backend_standard/dispatch.py) before running more than one builder.
