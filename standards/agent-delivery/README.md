# Agent delivery and GitHub provisioning v0.1

Adopt this standard with the [backend task and evidence contract](../backend/adoption.md), [UI delivery workflow](../ui/delivery-workflow.md) and [operational security controls](../operations/security.md). It governs planning, delivery coordination and scoped authority over GitHub actions.

| ID | Required control | Owner and acceptance evidence |
| --- | --- | --- |
| AD01 | Store a versioned brief, adopted standards and project decisions. Map each accepted requirement to bounded tasks, dependencies, cases and expected evidence. | Planner and product authority review traceability and demonstrate that unresolved inputs block readiness. |
| AD02 | Keep authoritative acceptance/task definitions in GitHub. Maintain one durable Coordinator ledger for active leases, attempts and pending external writes. Labels are views derived from the ledger. | Coordinator demonstrates two simultaneous claim attempts, one eligible owner, restart recovery and obsolete-token rejection. |
| AD03 | Give each implementer an isolated workspace, fresh context, fixed task scope, permitted tools/paths and budgets. Send pinned decisions and retrieve more artifacts only as needed. Preserve concise same-task handoff and redact secrets. | Coordinator tests revoked ownership, restart/resume and an unrelated task starting without the previous transcript. |
| AD04 | Resolve owner, repository name and visibility, existing repository versus new/template strategy, default branch, environment, issue source and authority before any GitHub write. | Operator verifies approved target, existing-resource identity, effective API capabilities and actual installation permissions. |
| AD05 | Reserve stable operation keys before creating repositories, issues or pull requests. Reconcile an interrupted operation using authoritative GitHub reads and control-lane ownership. | Coordinator runs lost-response and conflicting-intent cases. Replaying a completed request returns the original resource. |
| AD06 | Require protected workflow/policy and candidate-bound, non-empty real test evidence plus an independent review. Re-evaluate the latest base before integration and compare the merge result with the accepted tree. | Trusted CI and reviewer prove failed, zero, stale, skipped, forged or wrong-base evidence cannot advance the task. |
| AD07 | Bound lease duration, task attempts, repair cost and total elapsed time. Cancellation/expiry fences agent submissions. Only the Coordinator advances or reopens the task using trusted receipts and audit events. | Coordinator exercises concurrent expiry/recovery, exhausted budget, missing handoff and failure of external state publication. |
| AD08 | Approve integration and release at their respective stages. Measure queue, implementation, local test, CI, review, integration, smoke and external wait separately. | Coordinator records verified integration and applicable target checks, phase timing, cost, rework and escaped defects. |

## Readiness, ownership and integration

1. The Planner produces the ready packet using the adopted version and records unresolved inputs in draft state. The Coordinator resolves trusted dependency status, validates the packet and profile, and binds the ready packet digest before any claim.
2. The Coordinator claims an attempt transactionally. Bind repository, worktree, base revision, worker, budget, expiry and a fence token to that attempt. Enforce workspace and credential controls at the real execution boundary. A stale worker must lose both submission authority and access to mutable infrastructure.
3. The implementer verifies changes locally then submits candidate identity, actual results, open findings and a durable handoff using its current token. A timed-out attempt is recovered into a new owner/context only after expiry, isolation and budget checks.
4. Trusted CI tests the current integration candidate. A separate reviewer inspects the same candidate against the requirement and case IDs. A rejected candidate enters deliberate bounded repair; a new source or base forces renewed evidence. The [backend evidence verifier](../backend/adoption.md#developer-delivery-and-independent-acceptance) checks records under protected policy.
5. After authorized integration, compare the integrated tree and rerun required checks on the target branch. Release additionally requires [observed environment evidence](../operations/platform.md#release-evidence-verification). Only then transition the applicable scope to Done.

The [GitHub App adoption profile](../adoption/github.md) defines webhook, installation, replay and live reconciliation tests.

## GitHub operation contract

Use one configured GitHub host and authorized installation or account for each control lane. Workers receive scoped checkout/diff capabilities and the minimum write access for their branch. Keep create/admin/merge authority in the Coordinator or release lane. Verify the chosen tool, token type, owner, scopes, repository tenancy and branch policy with actual provider receipts before activating the lane.

| Operation | Stable intent scope | Reconciliation |
| --- | --- | --- |
| Repository | GitHub host, owner, normalized name and provisioning decision ID | Resolve owner/name, then verify repository identity, visibility and bootstrap revision before adopting it. |
| Issue | Repository ID and stable task ID | Search by owner-controlled task marker plus repository and issue type. Confirm content/author provenance and persist the returned issue ID. |
| Pull request | Repository ID, head repository/ref, base and task ID | Verify repository, both refs and task marker. Reuse the matching PR and record its number; conflicting ownership blocks. |

Persist the normalized desired payload fingerprint before dispatching the first external write. An identical request reads the receipt or reconciles. A different fingerprint on the same key is a conflict. After a timeout, a missing search hit alone cannot authorize another create. Verify authoritative readback under the same lane, account for provider visibility and indexing delay, and block when external state cannot be disambiguated. Record numeric repository and resource identifiers after reconciliation.

## Executable reference

[`DispatchLedger`](../../src/backend_standard/dispatch.py) demonstrates transactional local claims, expiry, attempt budgets, fenced candidate staging and operation reservations with Python SQLite. Use one trusted Coordinator-owned local database file. A repeated claim request from the same worker returns the active lease, a concurrent different request cannot take it, and an expired token cannot stage the next attempt's candidate. An unresolved repository/issue/PR intent enters reconciliation and cannot be reserved for a blind repeat write.

Run `uv run --no-sync pytest tests/unit/test_dispatch.py`. It uses independent SQLite connections, tests concurrent claims and verifies recovery after reopening the database. The ledger persists its greatest observed lease timestamp, including observations that caused an expired submission to fail. A backward or non-finite sample blocks lease actions. The library's staged state stops at review handoff. Workspace isolation, worker cancellation, review/repair orchestration, protected report acquisition and live GitHub provisioning remain operator bindings. Store SQLite on local disk with protected access and a trusted host clock. Providers and multi-host controllers require their own transactional/permission verification.

## Sources

- SQLite [transaction semantics](https://www.sqlite.org/lang_transaction.html), including write serialization and immediate transactions. The file/clock and trust policies in this standard are our reference choices.
- GitHub REST endpoints for [repositories](https://docs.github.com/en/rest/repos/repos#create-a-repository-for-the-authenticated-user), [issues](https://docs.github.com/en/rest/issues/issues#create-an-issue) and [pull requests](https://docs.github.com/en/rest/pulls/pulls#create-a-pull-request). Inspect the selected endpoint, API version, token type and actual repository rules separately. The reservation and recovery protocol is a project control.
- [Research and method comparison](../../research/method-comparison.md) records the evaluated snapshots and the open runtime selection.
