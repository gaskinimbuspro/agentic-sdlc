# Backend testing and delivery rules

Derive tests from acceptance criteria and actual risks. Do not mirror implementation or manufacture a test for every getter. Developers own behavior-preserving automated checks as part of implementation. [F05](sources.md#f05).

## Rules

| ID | Rule | Required evidence |
| --- | --- | --- |
| T01 | Every behavior change includes risk-appropriate automated verification. Documentation-only changes and trivial DTO/getter code do not need artificial tests. | Acceptance criterion to scenario mapping |
| T02 | Protect meaningful business rules and failures with transport-independent unit/behavior tests. | Success, boundary, invalid-state, and relevant failure cases |
| T03 | Exercise real dependency boundaries where storage, HTTP, or queues are used. SQLite/in-memory tests are not PostgreSQL integration evidence. | Reports using the selected real engine/version and required features |
| T04 | Test actual routing, serialization, validation, error mapping, and authorization. An in-process app host is valid; network/package behavior requires separate acceptance/smoke evidence. | App-host reports and version-bound artifact checks |
| T05 | Test doubles are allowed for focused tests. Verify real provider compatibility separately through contracts or a sandbox. | Double scope and actual boundary verification |
| T06 | Isolate data/state and control clock, randomness, and external behavior. Do not conceal races with fixed sleeps. Bound test execution. | Independent/suite repeatability and fixture cleanup |
| T07 | For fixes, demonstrate the regression failure before the fix where feasible. Use focused negative cases/mutations for critical invariants or new gates. | Failure-before/success-after or an explained equivalent |
| T08 | Coverage identifies gaps; a percentage alone is not quality or acceptance evidence. A required suite executing zero tests cannot pass. | Counts, assertions, and critical behavior review |
| T09 | Keep skips/flaky outcomes visible. Quarantine of a required test needs a reason, owner, expiry, and compensating check. | Passed/failed/skipped/flaky counts and approved exceptions |
| T10 | Record actual commands, exit codes, counts, commit/artifact identity, environment, and reports. An unavailable required check is blocked, not passed. | Machine-readable results and accessible logs/artifacts |

Use the [test case matrix](test-case-matrix.md) to select scenarios and the [Definition of Done](definition-of-done.md) to decide completion. Testing responsibility stays with the Implementer even when an Independent Reviewer exists.

The [verification matrix](verification-matrix.md#testing-and-evidence-controls) maps T01-T10 to concrete evidence obligations, gate ownership and rejection examples. Its applicability/exception rules prevent absent infrastructure or failing tests from being silently reclassified as N/A. The [worked acceptance design](baseline-readiness.md#worked-acceptance-design-create-a-customer) illustrates expected outputs and forbidden side effects before implementation.

## Gates

| Gate | Owner | Exit condition |
| --- | --- | --- |
| G0 Ready | Coordinator, using Planner outputs | Complete profile, applicable contracts/decisions, explicit acceptance criteria, dependency graph, test plan, tools, and bounded task packet |
| G1 Local | Implementer | Formatting, static analysis, build/type check, relevant unit and changed-boundary integration checks pass |
| G2 Clean CI | CI and Implementer | Locked restore, all applicable required suites, contract/security checks, valid reports/counts, and exact candidate identity |
| G3 Independent acceptance | Independent Reviewer | Requirements-derived review on the exact candidate; no unresolved blocking findings |
| G4 Release readiness | Release policy owner | Packaged-artifact critical journey/smoke, migration compatibility, and recovery checks pass |
| G5 Post-deployment | Operations/automation | Deployed-version smoke and health signals pass; configured stop/recovery conditions apply |

Keep fast checks early. Place expensive race, performance, security, or mutation checks at appropriate required stages. Maintain frequent integration; a pipeline running only on a long-lived branch is not sufficient CI. [F08](sources.md#f08).

## Evidence and failures

A project must implement `backend-verify` to run applicable checks, preserve their separate outcomes, and return non-zero for a required failure. A pipe, shell substitution, report parser, or continue-on-error setting must not hide an error. Inspect reports and executed counts because some runners/scanners return zero without establishing acceptance.

Record command, exit code, executed/failed/skipped/flaky counts, source SHA, candidate/base identity, artifact digest where applicable, redacted environment/tool versions, report locations, and status. Inspect both per-case results and run/suite-level failures. Reject interrupted Go streams and duplicate test results; a passed case cannot override a failed/aborted TRX run or JUnit suite-level error. Require an explicit implementation owner and a well-typed independent review finding count. Do not trust an agent-authored success sentence as execution evidence. The acceptance integration must obtain trusted CI/runner results and match their identities; the [provided validators](adoption.md#developer-delivery-and-independent-acceptance) cannot establish that provenance for arbitrary local files.

A candidate change invalidates previous review/evidence as applicable. Integration against a changed base requires an updated integration candidate and corresponding checks. Required checks cannot disappear through relabeling, N/A declarations, or a weakened assertion.

Test doubles are supported by [F07](sources.md#f07), coverage limits by [F06](sources.md#f06), and fast feedback by [F08](sources.md#f08). TDD is useful for behavior changes and fixes; it does not require artificial tests for trivial changes. [A03](sources.md#a03).
