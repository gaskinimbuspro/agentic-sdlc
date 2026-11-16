# Manual accessibility and visual adoption

Extends UT06, UT07, UD06 and UD07 in the [UI testing standard](../ui/testing.md) and [Definition of Done](../ui/definition-of-done.md). Before evaluation, fix the product scope, critical processes, supported environments, target conformance level, independent evaluator and visual baseline owner. For a website conformance decision, use WCAG-EM to explore the application and sample representative pages and complete processes. Report applicable success criteria with evidence, rationale and any exclusions. Include users with disabilities when appropriate to the product evaluation.

Use the built target candidate and approved fixtures. Capture environment, viewport and zoom, AT/browser versions, input modality, steps, expected and observed behavior, applicable success criteria, defects and re-test references. Select actual software/device pairs from the support matrix, such as VoiceOver and Safari, or NVDA and Firefox where supported. Record automated results and manual evaluation separately. Include denial, error, loading and recovery states. In the customer pilot exercise listing, creation, cancellation, field correction, session expiry and an uncertain save.

For visual comparisons pin browser, OS, fonts, viewport, device scale, fixture data and animation/time conditions. Approve baseline images by state and record their identity. Keep expected, actual and difference artifacts on a regression. Set narrowly scoped masks and tolerances before acceptance, and require independent approval of baseline updates.

| Case | Action and required evidence |
| --- | --- |
| AX01 | Define reviewed scope, complete processes, states, target criteria and representative support matrix. Retain criterion-level outcomes. |
| AX02 | Complete the selected journeys with keyboard. Verify focus order, visibility, route changes, error handling, recovery and escape from components. |
| AX03 | Use real assistive technology in selected environments. Verify names, roles, changes, error/status announcements and recovery. |
| AX04 | Check zoom, reflow, text and non-text contrast, content extremes and orientation as applicable. Record measured values or observable behavior. |
| AX05 | Run automated evidence on the same candidate. Correlate findings, manual results, fixes and re-tests with the evaluated criteria. |
| AX06 | Compare the built candidate against approved visual baselines. Exercise a deliberate visual change, preserve the difference and require an independent baseline verdict. |

Primary sources. [WCAG 2.2](https://www.w3.org/TR/WCAG22/) · [WCAG-EM](https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/) · [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots)
