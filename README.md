# Agentic SDLC

A reusable method for turning a project brief into requirements, architecture, bounded development tasks, and verified delivery.

The [backend standard v0.1](standards/backend/README.md) includes shared rules, Python/.NET/Go reference bindings, real PostgreSQL acceptance tests and verification tools, integrated through independently reviewed [PR #6](https://github.com/gaskinimbuspro/agentic-sdlc/pull/6). The current focus is the [UI/UX standard](standards/ui/README.md): project journeys, screen/state/interaction design, accessibility, frontend readiness and acceptance. An executing agent dispatcher and protected project acceptance authority remain separate integrations.

## Where a new project starts

Continuing this repository's work in a fresh conversation? Read the [backend/UI context handoff](docs/handoffs/2026-11-16-ui-standard.md) and current PR state first.

Give the Coordinator a project brief plus working settings. The Backend Architect/Planner clarifies behavior, records decisions, prepares the project profile/test plan, and splits work. The Coordinator dispatches ready tasks. One Implementer owns a coding task; independent review and trusted CI evidence control completion.

Start with [delivery workflow](standards/backend/delivery-workflow.md), [test case matrix](standards/backend/test-case-matrix.md), and [Definition of Done](standards/backend/definition-of-done.md).

## Repository map

- [Goals and requirements](docs/goals-and-requirements.md)
- [Backend standard and language profiles](standards/backend/README.md)
- [UI/UX standard and design readiness](standards/ui/README.md)
- [Database, platform/GitOps and security standards](standards/operations/README.md)
- [Agent delivery and GitHub provisioning](standards/agent-delivery/README.md)
- [Customer-admin frontend reference and browser checks](reference/frontend/README.md)
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
