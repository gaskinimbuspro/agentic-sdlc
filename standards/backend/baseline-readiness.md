# Backend baseline readiness

Status: implementation candidate under review. The standard now has executable reference bindings, input/evidence validation, real-database acceptance and CI definitions. Actual results belong to candidate-bound CI/runner reports, not this checklist. No deployment, independent approval or v1 release is established by this document.

## What is complete at this stage

- The draft defines B01-B18 common rules, T01-T10 testing rules, 22 Python/.NET/Go profile rules, TC01-TC14 scenario families and D01-D10 completion conditions.
- The [verification matrix](verification-matrix.md) now maps all 28 common/testing rules to applicability, methods/evidence, responsible roles, blocking gates, rejection examples and existing source references.
- The [delivery workflow](delivery-workflow.md) and [agent contract](agent-contract.md) specify proposed decomposition, dispatch, isolated implementation, independent review and evidence ownership.

The [reference](../../reference/README.md) adds complete example profiles, real applications and executable checks. The [adoption guide](adoption.md) explains how those controls fit a new project and where independent/trusted infrastructure is still required.

## The next work, in order

| Step | Deliverable | Acceptance condition | Current status |
| --- | --- | --- | --- |
| 1. Review common rules and applicability | Reviewed rule-to-control inventory, source/policy distinctions, explicit unresolved decisions | Every applicable rule has an evidence method and accountable owner; no silent conflicts with accepted requirements | Specified in the matrix; baseline adoption review remains open |
| 2. Bind a selected language/framework profile | Supported pinned toolchain, actual paths, analyzers, dependency policy, test host/lifecycle, validation, persistence/migrations and error behavior | Existing profile rules map to usable commands and semantic review; no required field is an example or unresolved placeholder | Python/FastAPI, Go/net-http and .NET/ASP.NET Core reference bindings and lock files implemented |
| 3. Implement project checks and evidence validation in an authorized pilot | Real `backend-verify`, trusted CI/report collection and independent review/exception authority | Selected required controls run; failure, zero tests, missing/stale evidence and unauthorized weakening are rejected | Runner, CI and input/index validators implemented; protected acceptance authority and exception integration are operator responsibilities |
| 4. Exercise a reference backend | Small real application and accepted cases; relevant real dependency and packaged-artifact checks | Correct behavior passes; agreed negative cases fail; actual commands/reports and exact identities are preserved | Common real-PostgreSQL/HTTP suite and rejection tests implemented; use current CI reports for pass/fail status |
| 5. Publish the validated baseline/profile scope | Versioned baseline and selected profiles, example bindings, known limitations and upgrade process | Evidence supports exactly the released scope; unvalidated profiles stay draft | Not released |

Keep this order without treating all design decisions as permanent. New requirements, support/security changes or measured problems may justify a reviewed revision. Agents must not silently reinterpret an adopted baseline during ordinary implementation.

## What stays common and what each project decides

| Reuse from the baseline | Decide once for the project before affected work |
| --- | --- |
| Verification responsibilities, evidence trust and completion conditions | Selected standard/profile revisions, integration target and release authority |
| API contract, validation, error and compatibility obligations | Actual endpoints, payloads/statuses, public/protected operations and compatibility window |
| Authentication/authorization and isolation obligations | Identity provider/mechanism, roles, ownership/tenant rules and allowed visibility |
| Data consistency, duplicate handling and migration obligations | Engine/version, uniqueness, transaction/compensation, idempotency and supported upgrades |
| Time/resource bounds, telemetry and safe startup/shutdown obligations | Actual timeout/retry/load targets, telemetry destinations and lifecycle behavior |
| Scoped task ownership and independent verification | Permitted tools/paths, model routing, budgets, workspace/runtime configuration and required checks |

Use the [project profile](project-profile.template.json) as the existing decision entry point and link accepted contracts/architecture records rather than copying contradictory versions into every task. Each task receives a pinned standard/profile revision and relevant references. Updates require a reviewed migration/decision; changing the central repository does not silently change active projects.

At G0, validate the decisions, dependencies, environment/permissions and execution plan that can exist before implementation. Do not require a future candidate SHA or future test reports. At G1 and later, require real candidate-bound results. A ready task is not an accepted implementation.

## Worked acceptance design: create a customer

This design example is implemented by the [reference](../../reference/README.md), not imposed as a universal API definition. The following product decisions are illustrative and must be explicitly adopted or replaced before use:

- An authenticated tenant member may create customers only within a tenant for which they have the create permission. The request's tenant identifier never grants access by itself.
- A customer has a name and email. This example chooses unique canonicalized email within a tenant; the accepted contract must define normalization and validation exactly.
- Successful creation returns the agreed `201` response; validation failures use the agreed `400`, missing/invalid credentials `401`, denied creation `403`, and the selected duplicate case `409`. Error-body details and any concealment policy are recorded separately in the contract.
- Creation is atomic: validation/authorization rejection and a known pre-commit rollback leave no customer or dependent record. A lost response or connection during commit can leave an unknown outcome; it must not be treated as proof that nothing committed or blindly retried. This reference uses per-tenant email uniqueness and no automatic retry. Audit/security logs may record denied attempts under the accepted telemetry policy.

Before a task is ready, the Planner must resolve those choices, record concrete fixtures/expected outputs and link the selected checks. An unknown required decision keeps the task in `draft`; the Implementer cannot invent it to make a test pass.

| Case | Setup and action | Expected evidence/assertions | Mapped rules |
| --- | --- | --- | --- |
| EX01: valid create | Tenant A member with create permission submits valid synthetic customer data | `201`, correct response contract, exactly one tenant A customer with accepted normalized values; no tenant B record | B04, B05, B06, B08; TC01 |
| EX02: invalid data | Same member submits a name/email that violates the accepted contract | `400` with selected safe error shape; no customer or unintended dependent record | B05, B07, B12; TC02, TC11 |
| EX03: anonymous | Submit the create request without valid credentials | `401`; no customer write and no sensitive disclosure | B06, B07; TC03 |
| EX04: cross-tenant attempt | Tenant A member requests creation in tenant B without permission | `403` under this example's contract; no tenant B customer and no unintended write | B06, B08; TC04 |
| EX05: duplicate race | Two valid concurrent requests use the same accepted canonical email in tenant A | Exactly one permitted customer; one success and one agreed duplicate outcome. Real-engine constraints and transaction behavior are exercised | B08; TC05, TC07 |
| EX06: intermediate failure | Controlled failure occurs after an intermediate write inside the declared create operation | Agreed safe error; rollback/accepted compensation leaves no unintended partial state. Capture state from a fresh verification transaction/connection | B07, B08; TC06, TC11 |
| EX07: upgrade | Load synthetic customers using a supported prior schema, then apply the proposed migration | Existing identities and required values remain correct; selected uniqueness/compatibility rules still hold | B09; TC10 |
| EX08: invalid submission evidence | Submit EX01-EX07 reports from another commit, or an empty required report, to the future verifier | Submission is rejected as stale/invalid evidence; task cannot become done | T08, T10; D04, D09 |

For EX05, asserting only status codes is insufficient: inspect persisted effects. For EX06, recording a failure response is insufficient without checking state. For EX08, a written `passed` status is insufficient without trusted execution and identity verification. Add feature-specific cases from TC01-TC14 where applicable; this example is not an exhaustive security or performance assessment.

## How we will know the controls work

For each selected new gate or critical invariant, run a focused negative demonstration in the authorized pilot, preserve the actual failed result, restore the correct implementation and preserve the passing result. Where a deterministic reproduction is not feasible, the independent review must assess an explained equivalent under T07.

At minimum the reference scope must reject missing configuration/decisions, unauthorized data access, unintended partial writes, a blocking security finding under the selected policy, missing/zero required tests, stale candidate evidence and self-approved exceptions. Select additional dependency, migration and lifecycle demonstrations from the matrix rather than pretending every backend uses every feature.

If the Implementer can change the required-check definition or report expectations without independent approval, this control is not ready for unattended use. Runner/CI authority and repository protections must enforce the selected trust boundary; instructions alone cannot provide it.

Measure accepted-task duration, repair rounds, human interventions, escaped defects and total token/compute cost. Targets must come from the pilot's actual workload and environment; this document promises no fixed duration or model quality.

## Language and broader-domain boundaries

Python, .NET and Go drafts each need their own framework binding and verification. Success in one profile does not validate the others. Additional languages require a reviewed profile rather than agent-selected conventions.

Data/security requirements needed for backend acceptance are included now. A complete database operations standard, UI/UX standard and platform/GitOps standard remain separate work. Their selected contracts must be consistent with the backend, especially authorization, data migration, artifact identity, deployment compatibility and recovery.

Selecting AWS AI-DLC, Spec Kit, BMad or OpenHands does not complete these controls. Evaluate reusable execution mechanisms against the same baseline and acceptance cases before selecting or building workflow ownership. Planning-only review remains separate from installation or runtime trials.
