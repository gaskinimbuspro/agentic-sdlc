# Target architecture

Status: **proposed, not installed**. This document describes how the method is intended to run on real projects. No server has been ordered, no program written for it is running and no agent has executed a task under it. Tool, model, provider and price statements are candidates to verify in the [pilot](pilot-runbook.md); see [open decisions](#open-decisions-and-unverified-assumptions).

The actors have names; see [the cast](cast.md).

![How the system works](../diagrams/04-system-map.png)

## Who does what

| Character | Role | Does | Does not |
| --- | --- | --- | --- |
| Gökhan | Product Owner | States the idea, answers product and risk questions, approves scope, requirements, design and merge | Remind agents to test, review routine code |
| Atlas (Claude) | Architect | Runs discovery, writes requirements and architecture, prepares the UI packet, splits work into tasks, helps when a task is blocked | Write the implementation, run continuously |
| Argus (Claude, separate session) | Reviewer | Reviews each pull request against the requirements and examples | Review its own work, merge |
| Iris (a program, not a model) | Coordinator | Picks ready issues, opens sandboxes, starts Daedalus with limits, pushes branches, opens pull requests | Decide product behavior, judge design quality |
| Daedalus (Qwen Code + Qwen model) | Builder | Implements one task with its tests in an isolated sandbox | Pick tasks, push, change requirements, workflows or its own permissions |
| Cerberus (Woodpecker) | CI gate | Runs the required checks on each pull request | Give opinions |

The split follows the existing [role contract](../../standards/backend/agent-contract.md). Reviewing with a different model from the one that implements reduces shared mistakes; it does not replace the gates.

![Who does what](../diagrams/05-who-does-what.png)

## Lifecycle

| Stage | Owner | Output | Gate before the next stage |
| --- | --- | --- | --- |
| Discover | Gökhan with Atlas | Brief with scope and non-goals | Gökhan agrees the scope |
| Specify | Atlas, Gökhan approves | Requirements with concrete examples | [RQ01–RQ06](../../standards/planning/requirements.md) |
| Design | Atlas, Gökhan approves | Architecture records and, for a UI, the design packet | [AR01–AR05](../../standards/planning/architecture.md), [UI design validation](../../standards/ui/README.md#executable-scope) |
| Plan | Atlas | Issues in Forge, with dependencies and case IDs | [G0 Ready](../../standards/backend/testing.md#gates) |
| Build | Daedalus, started by Iris | Code, tests, local commits; Iris opens the pull request | G1 Local |
| Verify | Cerberus, then Argus | Check reports and a review verdict | G2 Clean CI and G3 Independent acceptance |
| Release | Gökhan authorizes | Merged change, and a running version when deployment is in scope | G4 and G5, when in scope |

A failed check returns the task to Build within its repair budget. A missing decision, exhausted budget or missing access blocks the task and reaches Gökhan. Recurring corrections become standard changes under [ME06](../../standards/agent-delivery/measurement.md).

## Why Claude is not the always-on manager

Supervising agents around the clock with a hosted model would consume the budget the design is meant to save. Iris handles the continuous, mechanical part: queue, claims, time limits, pushing and opening pull requests. Claude is called at four points only: discovery and planning as Atlas, task breakdown as Atlas, review as Argus, and a blocked task that needs judgment. Everything it needs is read from versioned files and the issue, not from a long conversation.

Iris is deliberately not a model. A model given the git token and the task queue would set its own limits and could be steered by text inside an issue ([AS01 and AS02](../../standards/agent-delivery/security.md)).

## Where it runs

![Where it runs](../diagrams/06-where-it-runs.png)

| Place | Runs | Must not hold |
| --- | --- | --- |
| GPU server (RunPod for the pilot) | Pythia: vLLM serving the pinned model behind an API key ([AS08](../../standards/agent-delivery/security.md)) | Source code, git credentials |
| Work server, no GPU | Forge (Forgejo), Cerberus (Woodpecker server and agent), Iris, one sandbox per Daedalus task, a local container registry, a disposable `kind` cluster and preview deployments | Production credentials; git tokens inside a sandbox |
| GitHub | The agentic-sdlc standards repository, and Echo's mirror copies of project code | Project CI, pull requests or issues |
| Claude | Atlas and Argus, called when needed | Standing access to the servers |

Each sandbox has an outbound allowlist ([AS03](../../standards/agent-delivery/security.md)). The `kind` cluster is for tests and previews; it is not a production target. Production deployment uses the project's own [GitOps profile](../../standards/adoption/gitops.md).

## Source of truth and mirroring

| Repository | Primary | Copy | What the copy carries |
| --- | --- | --- | --- |
| agentic-sdlc (standards) | GitHub | Read-only pull mirror in Forge, so agents read standards locally | Code only |
| Each project | Forge | Echo pushes to GitHub on a schedule | Code and branches only |

Rules:

- Nobody develops on a copy. If two places accept changes, they diverge.
- GitHub Actions stay disabled on mirror repositories; GitHub runs no project CI.
- Echo does not copy issues, pull requests or CI history. Back up Forge's own data separately; the mirror does not replace that backup.
- Each project pins a released tag of agentic-sdlc. A change to the standards reaches a project only through a deliberate upgrade ([R13](../goals-and-requirements.md#requirements)).

## Two loops

![Two loops](../diagrams/09-two-loops.png)

**Inner loop, minutes, inside the sandbox.** Daedalus edits code, runs the same check scripts the project uses in CI, builds the image, pushes it to the local registry and deploys it to a preview in `kind`. Gökhan or a tester can open the preview at once. Nothing in this loop waits for CI.

**Outer loop, acceptance.** Iris pushes the branch and opens a pull request in Forge. Cerberus runs the same scripts in a clean container. Argus reviews. Forge's branch protection blocks the merge until the checks pass and Gökhan approves.

The check logic lives in scripts in the repository, as with this repository's `backend-verify`. The Woodpecker file only calls them. The same command therefore runs in the sandbox, in CI and on a laptop, and replacing the CI tool or the git server does not change the checks.

## How a project starts

![How a project starts](../diagrams/07-project-start.png)

1. Gökhan describes the idea.
2. Atlas runs the [discovery sequence](../../standards/planning/README.md#discovery-sequence) until every in-scope behavior has an example or an open decision.
3. Gökhan approves the requirements.
4. Gökhan approves the architecture and, for a UI, the design packet: every screen, state, action destination and API outcome.
5. Iris creates the repository and issues in Forge and configures Echo's mirror to GitHub, under the [operation contract](../../standards/agent-delivery/README.md#github-operation-contract).
6. The project environment is prepared: sandbox image, `kind` namespace, preview route, Woodpecker pipeline.
7. Iris gives the first ready issue to Daedalus; Cerberus checks the pull request.
8. Argus reviews and Gökhan merges the first change.

### Task structure

| Level | Meaning | Stored as |
| --- | --- | --- |
| Journey | What a user achieves | Parent issue in Forge |
| Task | One vertical slice with its own tests, independently verifiable | Issue |
| Sub-task | Only when a task has separable steps | Issue linked to its parent; Forgejo's dependency feature to be verified |

There is no separate "write tests later" task. A task that depends on an open decision stays in draft.

## Scale

Start with one Daedalus and one Argus, working serially, until gates and evidence behave as specified. Move to two or three parallel builders only for tasks with compatible contracts and non-overlapping changes, and compare the result under [ME04](../../standards/agent-delivery/measurement.md). At that point Iris needs exclusive claims, expiry and recovery, either from the repository's [`DispatchLedger`](../../src/backend_standard/dispatch.py) or an existing orchestrator.

## Build order

| Phase | Deliverable | Exit condition |
| --- | --- | --- |
| 0. Decide | Model, provider account and budget | Recorded decisions with verified prices |
| 1. Pythia | vLLM on a rented GPU, authenticated | A scripted prompt and a tool call return; an unauthenticated request is refused |
| 2. Work server | Forge, Cerberus, Echo, sandbox runtime, registry, `kind`; Daedalus connected to Pythia | Daedalus completes a trivial task in a sandbox with no host access; a failing check blocks a merge |
| 3. Iris | The serial coordinator script for one repository | One issue becomes a reviewed pull request with nobody editing the branch |
| 4. Pilot | One small real project from idea to accepted change | Measured under [ME01–ME04](../../standards/agent-delivery/measurement.md) |
| 5. Scale | Parallel builders and a fixed-price GPU if the numbers justify it | Reviewed capacity, cost and defect comparison |

Phases 1 to 4 are described in the [pilot runbook](pilot-runbook.md). Provision cloud resources with Terraform and configure servers with a configuration tool, so the environment can be rebuilt. No infrastructure code exists in this repository yet.

## Open decisions and unverified assumptions

| Topic | Choice | Status |
| --- | --- | --- |
| Git server (Forge) | Forgejo | Chosen by the product owner. Push mirror schedule and branch protection with Woodpecker to be verified on install. |
| CI (Cerberus) | Woodpecker | Chosen. Supports Forgejo according to its repository; not installed. |
| Builder tool (Daedalus) | Qwen Code in headless mode; OpenCode run on the same tasks for comparison | Chosen for trial. Documentation describes `qwen -p` and OpenAI-compatible endpoints; tool calls through vLLM are unverified. OpenHands is the fallback. |
| Model (Pythia) | An open-weight model from the Qwen family | Search results indicated that Qwen 3.7 has no open weights; confirm on the publisher's model card. |
| GPU for the pilot | RunPod, about 48 GB | Chosen. Rates differed between sources; verify on the provider's page. |
| GPU after the pilot | A fixed-price dedicated server | Decide from pilot utilization. |
| Coordinator (Iris) | A small script written for the pilot | Not written. Serial only; no exclusive claims or recovery until the parallel stage. |
| Mirror (Echo) | Forgejo push mirror to GitHub | Interval to be chosen. Forge's own backup is a separate, open task. |
| Benefit of the split | Hosted Atlas and Argus, local Daedalus | The strongest independent study found gains from planner-executor designs uneven. Measure in the pilot. |
