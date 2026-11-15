# UI Definition of Done

Design completion and implementation completion are distinct. Passing `ui-standard design` establishes structural reviewability only. A human-readable prototype or signed-looking local JSON is not independent approval or runtime evidence.

## Before implementation can start

Product intent, journeys, screen/state designs, visual direction, component/token choices, API mappings, accessibility/browser scope and acceptance outcomes are accepted and versioned. Necessary user-research gaps and material decisions are resolved. The frontend profile binds actual supported/pinned tools, commands, app/test paths, environments and trusted acceptance authority. The Coordinator validates the bounded task and dependencies.

## Implementation acceptance

| ID | Required condition |
| --- | --- |
| UD01 | Accepted requirement, journey, screen, interaction, design and case IDs are explicit and consistent with current contracts. |
| UD02 | Applicable U/UT/profile rules and independently approved exceptions are satisfied; accepted behavior was not silently rewritten. |
| UD03 | Locked install, formatting, lint/static/type/security checks and production build succeed under pinned inputs. |
| UD04 | Required unit/component/integration/browser suites execute meaningful cases; missing, failed, zero or unapproved skipped/flaky results block acceptance. |
| UD05 | Critical built-artifact journeys verify visible outcomes and real owned-backend effects, including applicable permission and failure cases. |
| UD06 | Design/responsive/visual acceptance is recorded for the candidate; visual-baseline changes and masks have independent review. |
| UD07 | Required automated and manual accessibility evaluation is recorded, with no unresolved blocking criterion failure. |
| UD08 | Performance/privacy/observability/session behavior meets the accepted profile, with actual evidence appropriate to each target. |
| UD09 | An independent reviewer approves the current candidate; no unresolved blocking findings or self-approved waiver. Source/base/artifact/report identities agree. |
| UD10 | Integrate into the configured target and provide a factual handoff. Conditional release/smoke/rollback checks are complete when deployment is part of the task. |

Use the adopting project's trusted review/CI sources. The Implementer cannot approve its own design exception, waive required checks or mark a task Done on a prose claim. Release authority remains explicit. No UI implementation in this standards change is declared to meet UD01–UD10.
