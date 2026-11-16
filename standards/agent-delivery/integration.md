# Branching and integration

These controls are our policy, informed by the [integration sources](sources.md#integration). They bound how long agent work stays apart from the integration branch. They extend [AD06](README.md) and the [parallelism rules](../backend/delivery-workflow.md#parallelism-and-integration).

| ID | Required control | Owner and acceptance evidence |
| --- | --- | --- |
| IN01 | Use one short-lived branch per task, created from the current integration branch. Record a maximum branch age and a maximum change size in project settings before dispatch. | Coordinator records age and size at submission. Reject a task branch that outlives its budget without a recorded decision. |
| IN02 | Keep the integration branch releasable. Every merged change passes the required checks on the resulting integration candidate, not only on the task branch. | Trusted CI on the merge candidate and on the integration branch after merge. Reject a merge whose checks ran against an older base. |
| IN03 | Integrate incomplete features behind a recorded toggle or an internal abstraction instead of holding a long-lived branch. Test both toggle states that can reach users. | Implementer supplies tests for each reachable state; reviewer checks the default. Reject unfinished behavior reachable by default. |
| IN04 | Give each toggle an owner, a purpose, a default and a removal date or condition. Remove it when the feature is complete. | Planner tracks toggles as tasks; reviewer checks expired toggles. Reject a toggle with no owner or removal condition. |
| IN05 | Split a task that exceeds its age or size budget, or that cannot be reviewed in one sitting, into smaller independently verifiable tasks. Rebase or merge the current base before submission and resolve conflicts in the owning task. | Planner re-plans; Coordinator blocks the oversized task. Reject a bundled change that mixes unrelated outcomes to avoid re-planning. |

## Reconciling review gates with frequent integration

Continuous integration in [F08](../backend/sources.md#f08) means frequent integration into a shared mainline. Independent review and candidate-bound evidence add waiting time to each change. IN01 and IN05 keep that cost bounded by keeping changes small; they do not remove the review. Measure the resulting lead time under [ME01](measurement.md) and adjust the budgets from data.

Merge-queue, branch protection and toggle tooling are project bindings. None is configured by this document.
