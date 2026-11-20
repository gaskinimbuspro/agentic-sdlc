# Iris: the serial coordinator

Iris is the [cast](cast.md)'s coordinator: a small program, not a model. One run takes the oldest issue labelled `ready` in Forge, has Daedalus build it in a sandbox, and either opens a pull request or marks the issue `blocked` with the reason. It implements Phase 3 of the [pilot runbook](pilot-runbook.md).

Status: **written and tested against a fake Forgejo API, a local git repository and stand-in builders. Not yet run against a real Forgejo, Docker sandbox or Qwen Code.** Its Forgejo calls follow the Gitea-compatible REST API and must be confirmed on the installed version.

Code: [`src/backend_standard/iris.py`](../../src/backend_standard/iris.py) for the single-host `iris run-once`, and [`src/backend_standard/iris_steps.py`](../../src/backend_standard/iris_steps.py) for the same stages as separate `iris-step` commands used by the [Argo Workflows template](../../platform/components/iris/workflowtemplate.yaml). There, only claim, prepare, publish and finish receive the git token; the builder pod receives only the model variables and a checkout without a usable remote; check and guard receive no secret. Tests: [`tests/unit/test_iris.py`](../../tests/unit/test_iris.py). Trial results on a real Forgejo: [platform README](../../platform/README.md#what-was-tested-and-where).

## One run

1. Take a host lock so only one Iris runs at a time.
2. Find the oldest open issue labelled `ready` and relabel it `in-progress`.
3. Clone the repository into a fresh temporary workspace and create `iris/issue-<n>`. If that branch already exists on the server, stop; Iris never overwrites one.
4. Write the prompt: fixed rules first, then the issue text between markers as data. Run the builder in the sandbox with only the listed model variables and a wall-time limit.
5. Run the project's check command itself, in the same sandbox image without any secret, on the committed state. The builder's own claim of success is not used. If the checks fail, start the builder again with the end of the check output and a progress note, up to `repair_rounds` times (default 2).
6. Apply the change guards, then decide:

| Result | Outcome |
| --- | --- |
| Builder wrote `.iris/BLOCKED.md` | `blocked`, and its question is posted on the issue |
| Builder timed out, exited non-zero or made no commit | `blocked` with the reason; known exit codes such as Qwen Code's 55 (budget) and 53 (turn limit) are explained |
| Checks still fail after the repair rounds | `blocked` with the last check output; nothing is pushed |
| A protected path such as the CI file changed | `blocked`; nothing is pushed |
| An existing test file was deleted, renamed or had lines removed | `blocked`; adding tests is allowed |
| The change exceeds `max_changed_files` or `max_changed_lines` (defaults 20 and 400) | `blocked` with a request to split the task |
| Checks pass and no guard fires | Branch pushed, pull request opened with `Closes #<n>`, issue relabelled `review` |

7. Comment on the issue and append a record to `runs.jsonl` in the log directory: issue, branch, seconds, attempts, builder exit code, whether checks passed, commits, changed files and lines, pull request. Each attempt's builder output and check output are kept as separate log files; with Qwen Code's `stream-json` format the builder log is the run's event stream. These feed the pilot's [measurement table](pilot-runbook.md#phase-4--measure).

## What keeps it safe

- The Forgejo token is passed to git through environment configuration, never on the command line, and is never in the builder's environment. A test checks the builder's environment directly.
- Iris refuses to start unless every variable in `builder_env` is set, because Qwen Code fills unset model variables from a `.env` file in the checkout.
- The builder has no git server access; only Iris pushes. Injected text in an issue cannot make the model push or open pull requests ([AS01, AS02, AS04](../../standards/agent-delivery/security.md)).
- The docker sandbox drops all capabilities, forbids privilege escalation, runs as the invoking user and mounts only the workspace. Restricting outbound traffic is done by the Docker network named in `docker_network`, which the operator must create with an allowlist ([AS03](../../standards/agent-delivery/security.md)).
- `local` sandbox mode runs the builder directly on the host. It exists for tests and trusted development only.

Tests also demonstrate the controls failing when broken: removing the protected-path check, passing the host environment to the builder, treating failed checks as passed, dropping the deleted-test guard or skipping the variable check each makes the corresponding tests fail.

## Use

```sh
export IRIS_FORGEJO_TOKEN=...   # token of Iris's Forgejo user
uv run --no-sync iris check iris.json
uv run --no-sync iris run-once iris.json
```

Start from [the example configuration](iris.example.json). `check` verifies the API, repository, labels and builder executable. `run-once` exits 0 when it opened a pull request or found nothing ready, 2 when the issue was blocked and 1 on an error. Run it by hand during the pilot, or from a timer once it behaves.

Create the four labels in the repository first: `ready`, `in-progress`, `review` and `blocked`.

## Not yet

The test guard works on file names and removed lines; it cannot tell a weakened assertion from a legitimate edit, so a blocked run may need a human decision, and Argus still reviews test quality. No claims across hosts, attempt budgets across runs, crash recovery of a half-finished run, or parallel builders. A run interrupted after relabelling leaves the issue `in-progress` for a human to reset. Add these from the [dispatch ledger](../../src/backend_standard/dispatch.py) before running more than one builder.
