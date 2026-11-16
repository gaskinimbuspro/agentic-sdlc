# Measurement and learning

These controls are our policy, informed by the [measurement sources](sources.md#measurement). They define what is measured so that a change to the method can be judged by results. They extend [AD08](README.md).

| ID | Required control | Owner and acceptance evidence |
| --- | --- | --- |
| ME01 | Measure delivery from trusted records: lead time from ready task to integrated change, integration frequency, change failure rate and time to restore. Define each term and its data source once per project. | Coordinator derives values from the ledger, CI and incident records. Reject a hand-entered figure or a metric with no stated definition. |
| ME02 | Measure agent delivery per accepted task: wall time by phase, model cost or compute time, repair rounds, human interventions and their reason, and review findings by severity. | Coordinator records per-attempt values under [AS07](security.md). Reject totals that omit abandoned or failed attempts. |
| ME03 | Track false completion: a task reported complete that then fails required checks, independent review or acceptance. Track escaped defects: failures found after the task was accepted. Link each to the control that should have caught it. | Reviewer and Coordinator classify each case. Reject a count that excludes cases repaired before anyone recorded them. |
| ME04 | Record a baseline on a fixed set of representative tasks before changing the method. State sample size and conditions. Do not present one run or a different task mix as an improvement. | Planner defines the set; operator preserves the raw records. Reject a before/after claim without the same tasks and conditions. |
| ME05 | Rerun the fixed task set when the instruction files, an adopted standard, a role's model or its serving settings change. Compare against the baseline before adopting the change for all projects. | Operator runs the set; independent reviewer compares results. Reject a model or instruction change adopted on impression alone. |
| ME06 | Turn each recurring human correction, false completion or escaped defect into a recorded proposal: a changed requirement template, a new check, a changed rule or a decision to accept the risk. Review proposals on a schedule and version the outcome. | Human and Planner review the proposal list. Reject a correction that was repeated in chat a third time without a recorded proposal. |

## Use of the numbers

The purpose is to answer whether the method reduces repeated correction at acceptable cost. Volume measures such as lines changed, pull requests opened or tokens consumed do not answer it. Published surveys and vendor reports motivate these measures; they do not predict results for a particular team, model or hardware.

No metric collection is implemented in this repository. The [dispatch ledger](README.md#executable-reference) records claims and attempts only.
