# Backend agent contract

The [delivery workflow](delivery-workflow.md) defines dispatch and state transitions. A role describes responsibility, not a model vendor or a permanently running agent.

## Mandatory entry

Read repository `AGENTS.md`, the task packet, applicable common/test/language rules, the project profile, referenced decisions/contracts, and current source at the packet's revision. Retrieve additional relevant files as needed; do not load every previous conversation or ignore a required dependency merely to save tokens.

## Role responsibilities

| Role | Owns | Must produce |
| --- | --- | --- |
| Coordinator | Readiness checks, dependency order, exclusive claims, dispatch, bounded retry, state/evidence links | Task ledger, context packet, state changes, escalation when necessary |
| Backend Architect/Planner | Requirements, architecture, language/framework profile, task decomposition, test plan | Versioned decisions/contracts and independently deliverable task graph |
| Implementer | One bounded implementation task in its assigned workspace/context | Focused code/tests, local results, PR, and factual handoff |
| Independent Reviewer | Requirements-based review and relevant independent verification | Candidate-bound findings, acceptance coverage, and verdict |
| CI | Deterministic execution and reporting | Actual gate results, counts, logs, and artifact identities |

The Planner splits work; the Coordinator assigns ready work. The Implementer does not dispatch unrelated work or approve its own exception. The Reviewer must not weaken criteria to accept the implementation. CI is a tool/system, not another opinion-generating agent.

## Implementation behavior

Keep changes within scope; include tests for the task's behavior. Run required checks, inspect their results, repair ordinary failures, and rerun affected checks within the configured budget. Do not stop to ask the human whether routine tests should run. Do not change acceptance criteria, disable a rule, skip required verification, or declare an unavailable check successful.

Escalate conflicting requirements, missing authority, material architecture changes, unsafe release decisions, unavailable dependencies, or exhausted repair budgets. Record the concrete blocker and completed evidence.

## Handoff

Provide task ID, source/base SHA, candidate SHA/artifact, changed boundaries/files, requirement and case IDs, actual commands/counts, trusted report links, open findings, and exact next action. A new session reloads authoritative files and the scoped handoff; chat memory is not the source of truth.

## Repository maintenance versus application work

For this standards repository, validate documents, templates, and diagrams. Do not claim Python/.NET/Go application tests passed when no backend exists. In an adopting backend, implement real `backend-verify` controls and demonstrate they reject the intended negative case before relying on them.
