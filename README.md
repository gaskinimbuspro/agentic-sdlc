# Agentic SDLC

A reusable method for turning a project brief into requirements, architecture, bounded development tasks, and verified delivery.

The current priority is the [backend standard v0.1](standards/backend/README.md): shared rules, Python/.NET/Go profiles, required test cases, completion criteria, and agent responsibilities. The method is a draft specification; an executing dispatcher and backend CI enforcement are still to be implemented and tested in a pilot.

## Where a new project starts

Give the Coordinator a project brief plus working settings. The Backend Architect/Planner clarifies behavior, records decisions, prepares the project profile/test plan, and splits work. The Coordinator dispatches ready tasks. One Implementer owns a coding task; independent review and trusted CI evidence control completion.

Start with [delivery workflow](standards/backend/delivery-workflow.md), [test case matrix](standards/backend/test-case-matrix.md), and [Definition of Done](standards/backend/definition-of-done.md).

## Repository map

- [Goals and requirements](docs/goals-and-requirements.md)
- [Backend standard and language profiles](standards/backend/README.md)
- [Research plan](research/plan.md)
- [Research sources](research/sources.md)
- [Method comparison criteria](research/comparison-criteria.md)
- [Research tasks and GitHub links](research/backlog.json)
- [Draft process and architecture diagrams](docs/diagrams/README.md)

![Backend agent responsibilities](docs/diagrams/02-agent-structure.png)

## Working method

Keep source claims, experiments, and our proposed policies distinct. A vendor article or attractive diagram is not proof of production reliability. Compare methods using the same brief and independent acceptance criteria before selecting the orchestration implementation.

[GitHub Issues](https://github.com/gaskinimbuspro/agentic-sdlc/issues) is the current task-status source. `research/backlog.json` records task definitions and links, not a competing status database. Future projects may use a different tracker through a deliberate integration policy.

All repository content is maintained in English. Framework, model routing, deployment topology, and final runtime/tool versions remain project decisions.
