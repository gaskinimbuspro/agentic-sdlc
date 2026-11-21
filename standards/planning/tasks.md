# Task plan

The task plan turns approved requirements and design into tasks that Iris can hand to the builder one at a time. It is one file, `plan/tasks.json`, in the project repository, started from the [template](tasks.template.json). These controls are our policy, built on the [delivery workflow](../backend/delivery-workflow.md) and its task packet fields.

| ID | Required control | Check and rejection example |
| --- | --- | --- |
| TP01 | The plan file is the source of truth. The architect changes it in a pull request; the product owner's merge approves it. Issues in Forgejo are a view generated from it. | Reject a task that exists only as a hand-written issue; reject an edited issue body as a plan change. |
| TP02 | Each task has one outcome: a goal, scope, non-goals, requirement IDs, acceptance criteria and test case IDs, with no placeholder. | Reject a task whose acceptance criteria say "works correctly" or "TBD", or that names no test case. |
| TP03 | Dependencies name existing tasks and form no cycle. A planned task does not depend on a draft task. | Reject T02 → T03 → T02; reject a planned task waiting on a task with an open decision. |
| TP04 | A task with an open decision has status `draft` and states the decision. A draft task is never handed to the builder. | Reject a draft task without `open_decision`; reject a draft issue labelled `ready`. |
| TP05 | Every task fits one builder run: size S or M, its allowed paths named, and its change expected within Iris's diff budget. Larger work is split. | Reject size L; reject a task with no allowed paths. |
| TP06 | A task becomes `ready` only when every dependency issue is closed by a merged pull request. Promotion is done by code, not by hand. | Reject a ready task whose dependency is still open. |

## How it runs

| Step | Who | What happens |
| --- | --- | --- |
| 1 | Voltran | Writes or changes `plan/tasks.json` in a pull request. |
| 2 | Cerberus | Runs `planning-standard tasks validate` on the pull request. |
| 3 | Gökhan | Reviews and merges the plan. |
| 4 | Cerberus, with the planner token | On main, runs `planning-standard tasks sync`. It creates or updates one issue per task, marked with its task ID, adds Forgejo issue dependencies, and labels the issue `draft`, `waiting` or `ready`. Running it again changes nothing. |
| 5 | Iris | Before each claim, turns `waiting` into `ready` for tasks whose dependency issues are closed, then takes the oldest `ready` issue. |

Issues that Iris is working on (`in-progress`, `review`, `blocked`) keep their label; sync only refreshes their text. A task removed from the plan is reported, not deleted. The validator checks structure and order. It cannot judge whether a task is well chosen; that stays with the review of the plan.
