# UI testing and evidence

Required portfolios follow behavior/risk, not a fixed pyramid percentage or coverage score. This is our blocking policy, informed by [Testing Library](sources.md#sui15) and [Playwright](sources.md#sui09). Developers execute relevant checks before delivery; independent acceptance is separate.

| ID | Requirement | Owner / stage and evidence |
| --- | --- | --- |
| UT01 | Validate requirements, screen/action graph, state decisions, API outcome mappings and case coverage before implementation. | Planner/Coordinator at design readiness; validator result plus human semantic/design acceptance. |
| UT02 | Unit-test meaningful pure behavior such as state transitions, formatting boundaries or validation decisions. Avoid tests of incidental component internals. | Implementer local/CI; actual nonempty reports where that behavior exists. |
| UT03 | Component tests exercise rendered names, labels, interaction, validation, loading/errors and relevant keyboard behavior. Simulated DOM tests do not prove actual browser layout or assistive-technology support. | Implementer local/CI; component results, declared test-double scope. |
| UT04 | Verify serialization, API outcome handling, authentication/tenant boundaries and actual owned integration. Maintain real-engine coverage for backend effects. | Implementer/CI; contract and real API/dependency reports tied to selected versions. |
| UT05 | Run critical journeys in actual supported browsers against the built app and owned backend; verify visible outcome and intended/forbidden persisted effects. | CI/independent acceptance; candidate-bound browser traces and nonempty counts. |
| UT06 | Run automated accessibility checks and manual keyboard/focus/zoom/assistive-technology evaluation under the agreed scope. Track criterion-level defects. | CI plus qualified human reviewer; separate automated and manual records. A scan cannot certify conformance. |
| UT07 | Compare accepted visual states in controlled browser/OS/fonts/viewport/data environments. Explain dynamic-region masks and reviewed tolerances. | CI/designer; expected/actual/diff images, independently reviewed baseline changes. |
| UT08 | Test responsive/content extremes, route refresh/back/deep links and relevant locale/session/cache lifecycle behavior. | CI plus selected manual/device checks; browser/environment matrix and case references. |
| UT09 | Check agreed bundle/request/startup/runtime budgets using recorded environments. Keep lab and field measurements distinct. | CI/operations; measured values and thresholds, not an invented production percentile. |
| UT10 | Preserve failures/skips/flaky retries, artifacts and exact source/base/candidate identity; reject missing/stale/zero required results. Demonstrate regression/control rejection before claiming the fix. | Implementer, trusted CI and independent reviewer; reports plus disposition of every required blocker. |

## Fast feedback and environments

Run design/input checks, formatting, lint/type checks and focused unit/component tests early. Run independent CI groups with safe fixture isolation and resource budgets. Use one built artifact for its acceptance/visual/a11y checks; verify current integration rather than accepting unrelated branch results. Pin browser binaries/test images and dependencies in the selected profile.

Use observable locators and assertions with bounded waits, not fixed sleep delays. Keep identity, storage, service workers/cache and test data isolated. Retries reveal instability and must not erase it. Component tests may use controlled doubles; label them. Critical owned-backend acceptance uses actual integration. External provider contracts/sandboxes are deliberate integrations; never use production customer data or test third-party uptime as if it were our behavior.

Collect console/page errors, relevant failed requests and redacted traces without exposing tokens, personal data or session storage. Independently approve trace retention/access and visual-baseline changes. Required exceptions need explicit authority and expiry; do not silently mark unavailable tools or human evaluation as passed.

## Current implementation boundary

This repository runs the design validator's rejection tests and documentation checks. The customer example is a specification. No frontend app, component runner, browser suite, axe scan, screenshot comparison, manual accessibility session or performance benchmark is supplied as executed evidence here. Those checks become mandatory under a completed adopting-project frontend profile.
