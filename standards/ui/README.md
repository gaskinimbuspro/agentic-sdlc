# UI/UX standard v0.1

This candidate defines how a project brief becomes explicit user journeys, screen designs, frontend tasks and verified delivery. Apply common UI rules independently of the selected framework. A TypeScript/React binding is described as a project option, not an imposed choice for every project.

## Start here

1. Supply the product brief, actors, permissions, constraints and backend contracts to the Coordinator.
2. The UX Planner prepares journeys, screen/route inventory, interaction outcomes, state designs, accessibility requirements and acceptance cases. The UI Designer supplies visual assets, component/token decisions and responsive behavior.
3. Validate the [design packet](design-packet.template.json), then obtain product/design acceptance and independent technical review. A structurally complete packet is **reviewable**, not approved or ready to deploy.
4. Bind the [frontend profile](frontend-profile.template.json) to actual pinned tools, app paths, commands and environments. The Planner splits accepted journeys into vertical implementation tasks; each includes its tests.
5. Implementers run local checks; CI checks the built candidate; independent review controls acceptance under the [Definition of Done](definition-of-done.md).

## Documents

| Document | Purpose |
| --- | --- |
| [Common rules](common.md) | Mandatory behavior, design, accessibility, security and engineering obligations |
| [Design process and screen patterns](design-process.md) | UX01–UX14: how screens are decided, approved and frozen, and the patterns each screen follows |
| [Delivery workflow](delivery-workflow.md) | Inputs/outputs, owners, design acceptance, task breakdown and change policy |
| [Testing](testing.md) | Test portfolio, environments, evidence, fast feedback and failure policy |
| [Case matrix](test-case-matrix.md) | Scenario families to select for the actual product |
| [Definition of Done](definition-of-done.md) | Separate design completion and implementation acceptance |
| [Frontend profile](frontend-profile.template.json) | Deliberately incomplete technology/check bindings |
| [Design packet](design-packet.template.json) | Deliberately incomplete project-specific design input |
| [Customer-admin example](examples/customer-admin/design.md) | Two-screen design example tied to the existing customer API |
| [Sources](sources.md) | Inspected primary sources and limits of attribution |

## What is fixed and what varies

Reuse U01–U16, UT01–UT10, UC01–UC12 and UD01–UD10. Each project supplies its own product behavior, brand, layout, supported devices, identity provider, technology, versions, contracts and budgets. Adopt the reviewed standard revision explicitly; upgrades require a reviewed change. Exceptions require a rule, rationale, accountable independent reviewer, compensating control and expiry. Workers cannot waive their own checks.

Our accessibility baseline is WCAG 2.2 AA for the defined product scope, with human evaluation as well as automated checks. This is our chosen baseline, not a claim that a screenshot, scanner or design packet establishes WCAG conformance. Legal and contractual requirements must be determined for the project.

Use the [manual accessibility and visual adoption profile](../adoption/accessibility.md) for evaluator assignments, candidate evidence and baseline approval.

## Additional project decisions to record

Record these with the design packet before affected work is ready. They add no U rule; they make existing [U04, U06, U09 and U12](common.md) decisions explicit.

- Token format and source of truth for design tokens, and how tools exchange them. [SUI17](sources.md#sui17).
- Legal accessibility scope: which regulation or contract applies, determined by the project's accountable owner. [SUI18](sources.md#sui18).
- Supported languages, scripts and text direction, and whether content must be translatable. [SUI19](sources.md#sui19).
- Consent, cookies and client-side storage of personal data, consistent with [personal data controls](../operations/privacy.md).

## Executable scope

`ui-standard design <packet.json> --root <repository>` checks schema, reference integrity, route/ID uniqueness, journey connectivity, screen/state decisions, interaction destinations, API-response mappings and acceptance-case coverage. It rejects incomplete templates. It does not evaluate aesthetics/usability, authenticate approvals, run a browser or grant dispatch/release authority.

For request interactions, map every response key in the bound OpenAPI operation and use `http_status: null` for outcomes without an HTTP response, such as an interrupted connection. Every outcome needs an acceptance case tied to a requirement from a journey using that interaction.

The example is a reviewable design specification, not a running frontend. This change does not claim UI component, browser, visual, accessibility or performance tests have executed. Bind and exercise an actual frontend profile before accepting an implementation; preserve that distinction in task/PR evidence.

Polymet, Figma or another design tool can contribute drafts after deliberate selection. No paid account, external service or subscription is required by this baseline. Keep editable, exportable, version-bound designs in an accessible project location. Verify export rights, privacy, code quality and costs before adopting a vendor; no vendor trial is claimed here.
