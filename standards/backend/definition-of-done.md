# Backend Definition of Done

The Coordinator may mark an implementation task done only when all applicable conditions below are met for the exact integrated candidate. A narrative success claim, coverage percentage, or opened PR cannot substitute for evidence.

Use the [verification matrix](verification-matrix.md) to bind applicable B/T controls to checks, trusted evidence and independent review. [Baseline readiness](baseline-readiness.md) records the remaining implementation/pilot gaps; the existence of this document or the matrix does not satisfy the conditions below.

| ID | Required condition |
| --- | --- |
| D01 | Scope, requirement IDs, acceptance criteria, and applicable test cases are explicit and unchanged unless a reviewed requirement change exists. |
| D02 | Common rules, selected language/framework profile, and approved exceptions are satisfied; no silent rule/test weakening. |
| D03 | Required format, static/type/build, security, and dependency checks pass under pinned configuration. Scanner findings are evaluated against policy, not just command exit status. |
| D04 | Every required suite actually executes meaningful tests. Reports expose failures, skips, and flaky outcomes. Zero required tests, missing reports, expired exceptions, or blocked checks prevent completion. |
| D05 | The acceptance matrix covers relevant positive, negative, boundary, authorization, data, and failure behavior. Actual dependency behavior is independently exercised where applicable. |
| D06 | Fixes have regression evidence; critical invariants/new gates have an appropriate negative demonstration. Tests do not merely reproduce the implementation's assumptions. |
| D07 | Contracts, migrations, configuration, telemetry, and recovery notes are updated when affected. No secret/sensitive data exposure is introduced. |
| D08 | An Independent Reviewer has no unresolved blocking findings for this candidate. The Implementer cannot self-approve review or exception records. |
| D09 | Trusted CI results, source/base/candidate SHAs and artifact identity agree. Integration checks cover the current target; stale review or evidence is not reused. |
| D10 | The change is integrated into the configured target, the handoff is factual, and release checks are complete if deployment is part of the task. No required follow-up is hidden in a completion note. |

## Evidence requirements

Use the [verification record template](templates/verification-record.template.json). The future verifier must read trusted runner/CI reports, validate required check names and counts, match candidate/base/artifact identity, and evaluate approved exceptions. A JSON file written by an agent is an index of evidence, not proof that commands ran.

For each acceptance criterion, record case IDs, expected outcomes, test/report references, and result. Expected outcomes are derived from requirements before implementation where possible. A reviewer may add adversarial cases without rewriting product requirements to match the code.

An unavailable test database is blocked, not passed. Unsupported local race detection must run on a supported runner. A rerun that passes does not erase a flaky failure. Do not let a pipeline's final successful command hide an earlier failure.

## Acceptance boundary

Task completion requires integration into the target defined by the project. A deployable artifact need not be deployed unless deployment is in scope. Release authorization and post-deployment checks remain separate controls.

No mechanism in this repository currently evaluates these conditions automatically. The pilot must implement the verifier and demonstrate rejection of missing evidence, zero executed tests, failed checks, stale SHAs, and unresolved blocking findings.
