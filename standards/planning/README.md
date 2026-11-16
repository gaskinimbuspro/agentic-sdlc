# Planning standard v0.1

Apply this standard before any implementation task becomes ready. It defines how a project idea becomes written requirements and recorded architecture that an Implementer can follow without inventing product decisions. The [backend](../backend/delivery-workflow.md#planning-before-dispatch) and [UI](../ui/delivery-workflow.md) workflows consume its outputs.

| Document | Purpose |
| --- | --- |
| [Requirements](requirements.md) | RQ01–RQ06: how behavior, examples, non-goals and quality targets are written and frozen |
| [Architecture](architecture.md) | AR01–AR05: views, decision records, boundary selection and automated architecture checks |
| [Sources](sources.md) | References that inform these controls and the limits of their inspection |

## Discovery sequence

1. The human states the idea, the users and the outcome that matters. The Architect/Planner asks questions until every in-scope behavior has a concrete example or an explicit open decision. The human answers product and material risk questions; the Planner does not guess them.
2. The Planner writes the requirements under RQ01–RQ06 and the human accepts them. Open decisions stay visible and keep the affected work in `draft`.
3. The Planner records architecture under AR01–AR05 and, where a UI exists, prepares the [design packet](../ui/README.md). The human accepts material trade-offs.
4. The Planner splits accepted requirements into bounded tasks using the existing [task packet](../backend/templates/task-packet.template.json). The Coordinator dispatches only ready packets.

A discovery conversation is input. The accepted, versioned requirement and decision files are the authority that later sessions read. This sequence is our proposed process; it is not a running intake service.
