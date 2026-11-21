# Discovery questionnaire

Discovery turns an idea into decisions an Implementer can follow. It is a fixed set of questions in eleven stages. Voltran asks them, the product owner answers and approves each stage, and nothing downstream becomes ready until the stages it depends on are complete. The questions are our policy, drawn from the sources of the [UI design process](../ui/design-process.md), [schema design](../operations/schema-design.md) and [planning](sources.md) standards.

| ID | Required control | Check and rejection example |
| --- | --- | --- |
| DQ01 | Keep one discovery record per project, in the project repository, started from the [template](discovery.template.json). | Reject decisions that exist only in a conversation. |
| DQ02 | Every question is `answered`, or `not_applicable` with a reason. An unknown stays `open` with an owner in the open-decision list ([RQ05](requirements.md)). | Reject an empty answer, a placeholder, or "not applicable" with no reason. |
| DQ03 | Stages are approved in order by the product owner, with a date. An agent cannot approve a stage. | Reject stage 6 approved while stage 4 is open; approval by an agent identity. |
| DQ04 | Work that depends on a stage is not ready until that stage is approved: UI tasks need stages 1–7, schema and backend tasks need stages 1–4 and 8–9, release needs all. | Reject a ready UI task while screen specifications are open. |
| DQ05 | An answer that is a lasting decision links its decision record ([AR02](architecture.md)), requirement or design packet through `decision_ref`. | Reject a framework choice recorded only as a questionnaire sentence. |
| DQ06 | A changed answer follows the change rule of [RQ06](requirements.md): recorded, approved again, and affected tasks and evidence reviewed. | Reject an edited answer under an old approval date. |

## Stages

| Stage | Decides | Feeds |
| --- | --- | --- |
| 1 Strategy | Users, problem, objective, evidence, constraints | Brief |
| 2 Scope and MVP | First end-to-end journey, inclusions, explicit exclusions | Scope, roadmap |
| 3 Roles and access | Sign-in, role-to-capability matrix, tenancy | Requirements, UX02 |
| 4 Journeys | Steps and examples per role, failure branches | Requirements with examples (RQ02) |
| 5 Information architecture and navigation | Destinations, labels, navigation pattern | UX03, UX04 |
| 6 Screen specifications | Screens, states, tables, forms, actions, approved prototype | Design packet, UX05–UX11 |
| 7 Visual design | Design system, tokens, supported environments, accessibility | UX12–UX13, frontend profile |
| 8 Data model | Ownership, entities, keys, types, history, tenancy, queries | DD01–DD20 |
| 9 Backend and architecture decisions | Language, deployable units, boundaries, API, integrations | Decision records, project profile |
| 10 Quality, security and privacy targets | Measurable targets, abuse cases, personal data, providers | Test plan, PV01–PV05 |
| 11 Delivery and operations | Target, release authority, recovery, first task list | Task packets |

The 65 questions are in the [template](discovery.template.json); the validator holds the canonical list and rejects a record whose questions differ.

## Validation

```sh
planning-standard discovery discovery.json            # all stages
planning-standard discovery discovery.json --stage 7   # complete through stage 7
```

It rejects open or placeholder answers, missing reasons, changed or missing questions, stages approved out of order and approval by anyone but the named product owner. Its result is "complete through stage N". It does not judge whether an answer is good and does not authenticate the approver; an independent review of the answers is still required for material decisions.
