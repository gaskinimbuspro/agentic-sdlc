# Backend standard v0.1

This draft defines how agents design, implement, test, review, and integrate a backend. Apply the common rules, the selected language profile, and the project's framework decisions together. Initial language coverage is Python, C#/.NET, and Go. Add a profile before adopting another language.

## Start here

1. The human supplies the project brief to the **Coordinator**.
2. The **Backend Architect/Planner** clarifies requirements, selects architecture and language, prepares the project profile and test plan, and splits work into bounded tasks.
3. The **Coordinator** dispatches a ready task to one **Implementer** with its own workspace and context packet.
4. An **Independent Reviewer** checks the exact candidate against requirements; **CI** supplies execution evidence.
5. The Coordinator advances the task only when the [Definition of Done](definition-of-done.md) is satisfied. Failed checks return to implementation; unresolved decisions or exhausted budgets become blockers.

See [delivery workflow](delivery-workflow.md) for ownership, task states, context policy, and dispatch rules. These are logical roles, not a requirement for four permanent processes or four model vendors.

## Standard documents

| Document | Purpose |
| --- | --- |
| [Common rules](common.md) | Architecture, interfaces, security, data, failure handling, and operations |
| [Verification matrix](verification-matrix.md) | Applicability, check/evidence, owner, blocking gate, and rejection example for every common/testing rule |
| [Baseline readiness](baseline-readiness.md) | Current gaps, ordered adoption steps, and a concrete requirements-to-evidence example |
| [Adoption](adoption.md) | New-project entry point, executable validators, and operator trust prerequisites |
| [Review handoff](review-handoff.md) | Candidate-bound independent review inputs, adversarial checks and expected evidence |
| [Executable reference](../../reference/README.md) | Python/FastAPI, Go/net-http, and .NET/ASP.NET Core bindings with one real-PostgreSQL acceptance suite |
| [Testing](testing.md) | Test responsibilities, gates, and evidence |
| [Test case matrix](test-case-matrix.md) | Required scenario families and applicability |
| [Definition of Done](definition-of-done.md) | Conditions for accepting a backend task |
| [Python](profiles/python.md) | Packaging, typing, formatting, linting, and pytest |
| [.NET](profiles/dotnet.md) | Nullability, analyzers, DI, async, and tests |
| [Go](profiles/go.md) | Packages, interfaces, errors, contexts, and concurrency |
| [Agent contract](agent-contract.md) | Inputs, responsibilities, and mandatory outputs |
| [Project profile](project-profile.template.json) | Project decisions, pinned versions, real commands, and execution policy |
| [Task packet](templates/task-packet.template.json) | Scoped input for one implementation session |
| [Verification record](templates/verification-record.template.json) | Evidence attached to a candidate |
| [Sources](sources.md) | Primary references and limits of attribution |

## Normative meaning

For a project adopting v0.1, applicable B, T, and selected PY/NET/GO rules are mandatory. Conditional requirements apply when their feature exists. A service without persistent storage does not need migrations; a money-handling service must address precision and duplicate operations.

Exceptions require a rule ID, rationale, risk, compensating control, accountable reviewer, and expiry/review date. An Implementer cannot approve its own exception or silently disable a test. Existing codebases need an explicit migration baseline; existing violations do not justify hiding new ones.

Fowler's architecture/testing principles and language documentation are separate sources. uv, Ruff, mypy strict, pytest, xUnit/VSTest, and 88-character formatting are choices in this draft, not universal requirements imposed by Fowler or the languages.

## Adoption and enforcement

Complete the project profile, record architecture/API/data decisions, select applicable test cases, and bind commands to real paths and pinned tools. The generated project must provide a `backend-verify` entry point and required CI checks. Preserve each check's result and test count; prove new quality gates reject the relevant negative case.

Use the [verification matrix](verification-matrix.md) to bind all applicable B/T rules and the selected language profile. Follow [adoption](adoption.md) and [baseline readiness](baseline-readiness.md) to distinguish specification, reference implementation, CI evidence and project-specific operational acceptance.

The templates deliberately start incomplete. Changing `readiness` to `ready` is not evidence. A validation step must check the required decisions, commands, permissions, and test environment before dispatch.

## Implementation status

This repository contains the standard, workflow/role specifications, templates, and executable verification tools. The [reference](../../reference/README.md) binds Python/FastAPI, Go/net-http and .NET/ASP.NET Core to the same OpenAPI contract and real-PostgreSQL acceptance suite. The [CI workflow](../../.github/workflows/backend.yml) runs required format/static/type/build, security, unit and packaged-process acceptance checks and preserves individual outcomes. Readiness/evidence validators reject incomplete, failed, stale and insufficient inputs.

These implementations do not authenticate arbitrary local evidence, configure branch protection, supply independent approval or run an agent dispatcher. Those trust/dispatch integrations are explicit [operator prerequisites](adoption.md#operator-prerequisites-for-unattended-use). The backend package remains under PR review; no deployment or v1 release is implied by green reference checks.

Projects record their adopted standard version. Updates require a reviewed migration; editing this repository does not silently change active projects.
