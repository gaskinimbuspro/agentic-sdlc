# Adopting the backend standard

The backend package now includes language/framework bindings, runnable references, acceptance tests and input/evidence validators. It does not supply an unattended agent orchestrator or configure a repository's trust/merge policy automatically. This document is the reusable entry point for a new backend project.

## Project preparation

1. Record product behavior, actors/permissions, data ownership, API/event contracts and operational targets. Use the existing standard rules; do not invent or revise them in an implementation chat.
2. Choose the relevant language profile and record framework/runtime versions and architecture trade-offs. Start from a [reference profile](../../reference/README.md#profiles-and-task-packets) where it fits, replace reference product decisions, and add a reviewed binding before using a different framework. Copying the customer example does not establish a new product's requirements.
3. Complete the [project profile](project-profile.template.json), decisions/contracts and rule applicability. Bind checks to actual files, pinned dependencies, trusted report sources and named review authority. `backend-standard profile` rejects incomplete/malformed bindings. Semantic/design suitability still requires planning and independent review.
4. The Planner produces bounded vertical tasks with acceptance outcomes, applicable TC families, dependencies and commands. Use the [task packet](templates/task-packet.template.json); `backend-standard task ... --profile ...` validates ready-stage inputs and rejects unfinished dependencies supplied by the Coordinator. Do not require a future candidate SHA before implementation.
5. The Coordinator must enforce exclusive ownership, a task-specific workspace, a fresh task context and bounded recovery. These responsibilities are specified in [delivery workflow](delivery-workflow.md); the reference verifier does not implement dispatch or enforce process permissions.

## Developer delivery and independent acceptance

The Implementer runs the adopted local verification before a verified handoff, includes code and meaningful tests, and supplies actual results. CI repeats the required checks against the current integration candidate. A failed/blocked/missing/stale result is not accepted. Ordinary repair stays within the task's budget; changed candidate/base identities require current evidence.

The [input/evidence CLI](../../src/backend_standard/cli.py) offers three separate checks:

- `backend-standard profile <profile.json> --root <repository>`: completeness, schema/types, decision/contract paths, named gate bindings and execution-policy inputs.
- `backend-standard task <packet.json> --profile <profile.json> --root <repository> [--completed-dependency <id>]`: ready-stage scope/criteria/cases/dependencies/budgets and approved command bindings. The completed-dependency list must come from the trusted Coordinator, not a worker's unchecked claim.
- `backend-standard evidence <index.json> --policy <trusted-policy.json> --reports <trusted-report-root> --candidate <sha> --base <sha>`: required check set, report hashes, real executed-test counts, exact candidate/base identity and a separately trusted independent-review record. This validates structure/content, not provenance or authorship.

Do not run the evidence command on worker-controlled files and treat a successful exit as external attestation. The operator must retrieve CI/review results through trusted infrastructure and protect the policy that names required checks and reviewers. The current CLI deliberately blocks exception records and skipped required tests rather than inventing exception approval; documented exceptions need a separately implemented, independently authorized integration before they can be used operationally.

Apply [D01-D10](definition-of-done.md) to the integrated candidate after requirements-based independent review. Opening a PR, passing the local runner, validating an input packet or producing an evidence index cannot close a task by itself. Release and deployed checks apply when in scope.

## Operator prerequisites for unattended use

- Require the adopted CI check names on the integration branch and protect baseline, workflow, test-policy and acceptance-fixture changes with independent review. Do not allow the implementing identity to approve an exception or waive its own checks. Select stale-approval dismissal and bypass policy explicitly.
- Run workers with scoped credentials/workspaces and no production release authority. Run trusted acceptance controls from a protected policy/implementation version; candidate-controlled workflows alone are not a security boundary.
- Retrieve actual runner reports and review identities; preserve artifact/source/base identities and report retention. An agent-authored JSON file is only an index.
- Configure exclusive claims, dependency scheduling, cancellation/context handoff, repair budgets and idempotent GitHub updates in the selected orchestrator. The backend standards do not select a vendor or require a fixed number of model processes.
- Record the adopted baseline/profile revision. Review upgrades and affected exceptions; central documentation changes must not silently alter a running project's rules.

These prerequisites are an explicit operational boundary, not a claim that repository protection or an agent dispatcher has been installed here. Backend rule/profile/test definitions are reusable independently of later OpenHands/AI-DLC/Spec Kit/BMad integration.

## Verification scope and sources

The [verification matrix](verification-matrix.md) and [test case matrix](test-case-matrix.md) remain the requirements-to-check map. The [reference](../../reference/README.md) supplies executable examples. [Sources](sources.md) distinguish published guidance from our mandatory policy/tool choices. Unit/negative tests in this repository exercise readiness, evidence and scanner rejection; real PostgreSQL tests exercise the selected reference behavior.

A validated reference is not a certificate of security, performance or production readiness for every future project. UI standards, complete database operations, platform/GitOps rollout, production identity-provider integration and full agent scheduling remain their own scoped contracts.
