# Backend delivery workflow

This is the proposed operational contract for an adopting project. It defines what a future dispatcher, agent sessions, and CI must do; it is not a running orchestration service.

## Entry point and roles

Give the project brief to the Coordinator together with repository/organization settings and the adopted backend standard. The Coordinator requests planning, tracks authoritative artifacts, and dispatches ready work. The human owns product intent and material risk decisions.

| Responsibility | Owner | Output |
| --- | --- | --- |
| Clarify behavior and constraints | Backend Architect/Planner with the human | Requirements and explicit acceptance criteria |
| Select boundaries, contracts, language/framework | Backend Architect/Planner | Project profile, decisions, API/data contracts |
| Design acceptance coverage | Planner, reviewed independently for high-risk work | Applicable case IDs and expected results |
| Split and order work | Backend Architect/Planner | Bounded tasks with dependencies and integration criteria |
| Assign ready tasks and manage retries | Coordinator | Exclusive claim, task packet, workspace/context, budget |
| Implement behavior and its tests | One Implementer per coding task | Code, tests, local evidence, PR, handoff |
| Execute reproducible checks | CI | Trusted results tied to the candidate |
| Independently evaluate the candidate | Independent Reviewer | Findings and candidate-bound verdict |
| Accept task completion | Coordinator applying policy | Done transition only after all required evidence |

Roles are model-independent. CI is deterministic infrastructure, not an LLM reviewer. The Coordinator may use an LLM for reasoning, but readiness, exclusive claims, dependency completion, and gate evaluation must be enforced by code/state controls rather than a prompt alone.

## Planning before dispatch

Write requirements and architecture records under the [planning standard](../planning/README.md). The Planner produces requirements with stable IDs, architecture decisions including trade-offs, contracts, a completed project profile, and a test plan. It then breaks features into small vertical slices that each include relevant implementation and tests. Do not create a coding task that omits developer testing because a later QA task exists.

A task must have one clear outcome, scope/non-goals, acceptance criteria, applicable case IDs, dependencies, allowed change boundaries, actual commands, expected evidence, and a bounded execution budget. Split a task if it spans unrelated outcomes or cannot be independently verified. Keep genuinely atomic contract/schema changes together instead of splitting only to make tickets smaller.

Validate fields at their lifecycle stage: a ready packet needs its source/base revision and verification plan; claim/workspace/owner fields are completed on assignment; candidate and report identities are recorded after implementation. Do not require a future candidate SHA before coding or accept missing evidence after verification. Define cost currency and budget units in project settings.

For example, an illustrative customer API might have a contract/authorization decision task, then a create-customer slice with its validation/permission/persistence tests, then a list-customers slice with visibility/pagination tests. These are examples; product requirements determine the actual behavior.

## State transitions

| State | Meaning and transition owner |
| --- | --- |
| draft | Planner is still resolving requirements, dependencies, or environment decisions |
| ready | Coordinator verifies the packet, accepted prerequisites, commands, permissions, and test environment |
| claimed | Coordinator records an exclusive implementation owner and workspace |
| implementing | Implementer changes code/tests and repairs routine failures within budget |
| verifying | CI executes required checks on the exact candidate; failures return to implementing |
| reviewing | Independent Reviewer checks the candidate and evidence; blocking findings return to implementing |
| done | Required evidence and review are valid for the integrated candidate and the Definition of Done passes |
| blocked | A concrete prerequisite, authority, decision, or execution budget prevents progress |

`PR open`, `tests reported green`, and `agent finished` are not done states. `Done` and `deployed` are distinct: deployment is required only when it is part of the task contract. Release authorization remains a separate configured policy.

Maintain task state in GitHub plus a durable execution ledger in the future dispatcher. Labels are views, not exclusive locks. One dispatcher may serialize claims; multiple dispatchers require transactional/compare-and-swap semantics. Record claim ownership, expiry/heartbeat, attempt identity, and recovery; do not trust two agents to avoid duplicate claims by convention.

GitHub remains authoritative for task definitions and accepted task status. The execution ledger owns active claims/attempts and publishes linked status updates; it is not a second independently editable backlog. Reconcile interrupted updates idempotently. A GitHub label alone cannot authorize execution or completion while the ledger/evidence is inconsistent.

## One coding task per scoped context

Default policy: one implementation task, one current coding owner, one isolated worktree/branch, and a fresh scoped context at task start. Independent review uses a separate session. A session must not silently switch to an unrelated task.

Keep the same session for ordinary repairs of that task while its context remains useful and the budget allows it. Reset or compact when context is polluted, a window is exhausted, or progress stalls; write a factual handoff first. Do not reset after every command and repeatedly reload the same repository.

The packet includes requirement/decision references, contracts, current base/candidate revisions, allowed paths, dependencies, commands, and evidence expectations. Load mandatory small guidance first and retrieve relevant code just in time. Do not copy the entire repository or all previous chats into every prompt. Do not omit necessary contracts to save tokens.

Persist decisions and progress outside the context window. The next session reads the actual repository and task state, not merely the previous agent's confidence. Human chat is input to record, not the sole durable source of requirements.

These are our proposed task-isolation rules. Anthropic discusses focused contexts, compaction, and durable handoffs; those engineering reports do not prove that a new context for every task always reduces cost or improves quality. [H01](sources.md#h01), [H02](sources.md#h02).

Measure total tokens including repeated context, wall time, accepted-task cost, repair loops, integration failures, escaped defects, and false-completion rate during the pilot. Select model/role budgets from those results; do not choose a role count or universal token limit from analogy alone.

## Parallelism and integration

Start serially until task boundaries and evidence gates work. Parallelize only ready tasks with compatible contracts and non-conflicting changes. Declare affected files/modules/schema; serialize overlapping contract and migration changes or provide a reviewed integration plan.

Do not let concurrent workers edit one checkout. After changes, build the current integration candidate and rerun required checks. A new candidate or relevant base change invalidates stale evidence/review. Merge-queue or equivalent integration protection belongs in the adopting project; it is not configured by this document.

## Failure handling and human involvement

Repair ordinary test/build failures automatically within project limits. Escalate only unresolved product ambiguity, material design/risk decisions, missing access/dependencies, unsafe release changes, or exhausted limits. Record the blocker, evidence, attempted fixes, and next action. Never ask the human to remind a worker to run its standard checks.

The workflow reduces routine supervision; it cannot guarantee zero defects or eliminate human product/security judgment. An AI-written test suite passing by itself is insufficient evidence of the intended behavior. [H03](sources.md#h03).
