# Goals and requirements

The method lets Gökhan prepare and develop new projects with agents under repeatable engineering rules. A separate project brief supplies product-specific intent; shared standards and working settings supply reusable constraints.

## Intended use

A brief may describe an API, web application, or several services. The method identifies gaps and assumptions, clarifies behavior, prepares architecture/contracts, creates ready tasks, and provisions repositories/tracking only through authorized tools. Humans retain product and material risk decisions.

## Requirements

| ID | Requirement |
| --- | --- |
| R01 | Derive scenarios, scope, non-goals, and acceptance criteria from project intent; expose important gaps. |
| R02 | Manage shared standards, working settings, and project requirements separately. |
| R03 | Establish source-based backend and UI engineering standards. |
| R04 | Justify language/framework choices and maintain separate Python, .NET, and Go profiles initially. |
| R05 | Apply selected profiles consistently and record justified standard changes. |
| R06 | Design module/service boundaries, data ownership, contracts, security, operations, and UI flows to the depth the project needs. |
| R07 | Define role inputs/outputs, tool permissions, handoffs, and task-context boundaries. The Planner splits work; the Coordinator dispatches it. |
| R08 | Define GitHub owner, naming, visibility, repository strategy, and bootstrap checks. |
| R09 | Link tasks to requirements, decisions, dependencies, acceptance criteria, and verification evidence. |
| R10 | Distinguish developer-local, CI, independent acceptance, smoke, and release/post-deployment responsibilities. |
| R11 | Bind actual results and reports to source/candidate/artifact identity. Blocked, skipped, empty, or failed required checks cannot be reported as passed. |
| R12 | Preserve durable context across sessions, isolate active coding work, bound repair loops, and prevent duplicate claims/repositories/issues/PRs. |
| R13 | Record adopted standard versions and deliberate upgrades across projects. |
| R14 | Provide consistent, versioned process, agent, and project architecture diagrams with sourced icons and editable assets. |

## Diagram outputs

The [draft views](diagrams/README.md) cover the system map, lifecycle ownership, placement, project start, delivery flow, backend roles, and an illustrative project architecture. The [target architecture](architecture/README.md) explains them. Maintain readable labels, consistent colors, explicit arrows/boundaries, source/license attribution, SVG, PNG, and the editable generator. Draft views do not claim a running system or finalized topology.

## Current settings and scope

- GitHub owner/repository: `gaskinimbuspro/agentic-sdlc`.
- Repository visibility: public.
- Task tracking: GitHub.
- Current priority: backend standards, test cases, completion gates, and scoped agent workflow; then a real pilot.
- One bounded coding task per implementation owner/workspace/context is the proposed default, with independent review and durable handoffs.

## Remaining implementation decisions

Select orchestration framework, model routing, framework adapters, runtime versions, dispatch/evidence enforcement, and repository automation through research and a pilot. MCP, n8n, Jira, Kubernetes, GPUs, and RAG are not automatic prerequisites.
