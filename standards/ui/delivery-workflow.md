# UI design and delivery workflow

Roles are responsibilities, not a fixed number of agents or model subscriptions. The Coordinator owns work state; the Planner decomposes work; implementers own tests as well as code. Use the existing [scoped-context and claim policy](../backend/delivery-workflow.md#one-coding-task-per-scoped-context).

| Stage | Owner | Required output and exit |
| --- | --- | --- |
| Product discovery | Human/product owner with UX Planner | Actors, needs, scope, constraints, stable requirements and accepted outcomes; unresolved material product decisions block affected work. |
| Journey design | UX Planner | Entry points, ordered actions, navigation/back/refresh behavior, permission rules and alternative/error paths mapped to requirements. |
| Screen and visual design | UI Designer with Planner | Screen/state inventory, editable/exported visual references, tokens/components, content, responsive and accessibility behavior. |
| Design review | Product owner, designer and independent technical reviewer | Reviewable packet validated; intended behavior and visual direction accepted; backend contract gaps resolved; applicable accessibility requirements and cases selected. |
| Technical readiness | Frontend Architect/Planner and Coordinator | Complete frontend profile, pinned tools, real commands, browser/data environments, task dependencies and evidence plan. A design-only packet cannot satisfy this stage. |
| Implementation | One Implementer per task | Code and behavior tests, local checks, actual outputs and scoped handoff. |
| CI and independent acceptance | CI and Independent Reviewer | Current built candidate passes required checks/cases; design/requirements reviewed independently; no unresolved blocker. |
| Integration/release | Coordinator and release authority | Agreed target integration and conditional release/post-deployment checks; explicit source/artifact identity. |

## Task decomposition

Split an accepted journey into independently testable vertical outcomes. A customer example can have shared accessible shell/components, then create-customer behavior with validation/error states and tests, then listing with isolation/empty/error states and tests. An API change is a visible dependency, not an assumption for the frontend worker to invent. Shared component/API/schema work needs an integration order before parallelism.

Each packet references the adopted UI/backend revisions, relevant requirement/journey/screen/interaction IDs, design revision/assets, acceptance cases, allowed paths, dependencies, actual commands and bounded budget. A click's destination, side effect and failure behavior must be known before the affected task is ready. Do not dispatch every screenshot as a separate task if its behavior cannot be verified independently.

The Coordinator enforces exclusive claims and a fresh scoped implementation context. Ordinary repairs stay in that task while context and budget remain useful; interrupted work gets a factual durable handoff. CI and the independent reviewer use the exact candidate. The design tool or LLM does not own an implicit Done transition.

## Design changes

Validate and version changed behavior/design/contracts, assess affected tasks/tests, obtain appropriate acceptance and invalidate stale review/evidence. Freeze the accepted revision for implementation, not for the lifetime of the product. New evidence, accessibility defects and security/support changes can require a deliberate revision. Never silently approve generated designs, regenerate snapshots or rewrite acceptance criteria to fit a failing implementation.

An AI design service can draft alternatives, export components or support prototyping. The Designer remains accountable for complete states and coherent visuals; the product owner accepts intent; the technical reviewer checks feasibility and contracts. Store the accepted artifacts with traceable revisions, regardless of vendor.
