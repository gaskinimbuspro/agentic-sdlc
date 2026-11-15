# Agentic delivery method comparison

Use the [shared customer directory brief](customer-brief.md) and the [comparison criteria](comparison-criteria.md) for every candidate. This is a source inspection. Runtime behavior, accepted-task cost and effectiveness require controlled trials.

## Examined versions

| Method | Pinned input | Primary references |
| --- | --- | --- |
| BMad Method stable | `bab9082c3e884e0d72c759bcd1a6d90bcc01be84` | [Readiness reference](https://github.com/bmad-code-org/BMAD-METHOD/blob/bab9082c3e884e0d72c759bcd1a6d90bcc01be84/src/bmm-skills/plan/bmad-sprint-planning/references/readiness-gate.md) |
| AWS AI-DLC | `8c4f79b4b77c5a64738b01b350be2bf72c357dae` | [Lifecycle](https://github.com/awslabs/aidlc-workflows/blob/8c4f79b4b77c5a64738b01b350be2bf72c357dae/docs/guide/04-phases-and-stages.md), [state and audit](https://github.com/awslabs/aidlc-workflows/blob/8c4f79b4b77c5a64738b01b350be2bf72c357dae/docs/guide/10-state-and-audit.md) |
| GitHub Spec Kit | `2ee2b1e8005905db05f5717300a469b3068b908f` | [Task template](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/templates/tasks-template.md), [analysis](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/templates/commands/analyze.md), [workflow documentation](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/docs/workflows/overview.md) |

## Same-brief mapping

| Area and requirements | BMad stable | AWS AI-DLC | Spec Kit |
| --- | --- | --- | --- |
| Intake, requirements, design and traceability (R01–R03, R06, R09) | Use product/UX/architecture work and readiness assessment to identify missing directory decisions and trace CR01–CR06 to implementation stories. | Carry the directory intent through inception and construction stages. Record service boundaries, role decisions and evaluated cases in versioned outputs. | Capture CR01–CR06 in the specification and map them to the plan, tasks and cross-artifact analysis. Overlay templates with the selected case/evidence contract. |
| Profiles, architecture standards, upgrades, diagrams (R02–R06, R13–R14) | Supply pinned adopted rules and existing editable diagram conventions as project inputs. Their technical enforcement needs the project checks. | Lifecycle artifacts can record selected architecture and profiles. Bind supported versions, upgrade policy and diagrams to project tools. | Constitution, presets and plan can carry standards. Bind supported profiles and diagram source checks independently and reject an incomplete constitution at readiness. |
| Roles, context, readiness and durable recovery (R07, R09, R12) | Use distinct planning roles and the readiness rubric. Validate the task packet and protect assignment outside the planning session. | Inspect the documented deterministic engine, session boundaries, intent state and audit events as possible coordination machinery. Verify actual harness recovery and independent identities. | Workflows combine agent/shell steps and pause for reviews. Add the prepared project packet and separate implementation/review authority. Documented resume behavior requires idempotent external side effects. |
| Claims, GitHub provisioning and tracking (R08, R12) | Transactional claim/external-write integration requires demonstration. | Evaluate whether state transitions can support fencing and recovery under our test cases. Verify the GitHub adapter and repository permissions separately. | A YAML flow can invoke a GitHub adapter. Prove exclusive ownership, lost-response reconciliation and protected repository settings outside the plan. |
| Testing, completion and operations (R10–R11) | Map story acceptance to real HTTP/database/browser cases and require trusted candidate reports and independent review. | Structured state and review inputs are promising. Verify rejection of stale, missing, forged, skipped and zero-test evidence with our protected collector. | The inspected task template permits optional tests. Override that default for applicable requirements and verify candidate-bound evidence and target smoke independently. |
| Decision effort, token/runtime cost, recovery and defects | Measure planning artifacts, revisions, token usage and escapes. | Measure stage/guard overhead, handoffs, recovery and model interactions. | Measure artifacts, workflow pauses/restarts, shell execution cost and escapes. |

Use BMad's readiness rubric as a comparison input. Test Spec Kit for artifact-oriented planning and AI-DLC for stateful coordination using the same synthetic cases and one authorized integration lane. Keep one authoritative task ledger during trials. The local [reference ledger](../standards/agent-delivery/README.md#executable-reference) tests control semantics for comparison. It does not select a production framework.

Record blind requirements-based review, real test/report identity, wall time by phase, total cost/tokens, repair rounds, human interventions and escaped defects for each trial. R01–R14 coverage remains unmeasured where the evidence is documentation only.
