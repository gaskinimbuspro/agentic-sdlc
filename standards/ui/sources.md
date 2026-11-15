# UI primary sources

Inspected 15 November 2026. These sources do not publish one universal frontend architecture. Mandatory gates, identifiers, task structure and technology defaults are our decisions. No usability trial, paid-product trial or accessibility certification is inferred from reading documentation. Public websites are living documents except the pinned Recommendation below.

## SUI01

GOV.UK Service Manual, [How the discovery phase works](https://www.gov.uk/service-manual/agile-delivery/how-the-discovery-phase-works). Understand users, the problem, constraints and scope before implementation. Its public-service process and typical schedules are not imposed as universal project durations here.

## SUI02

Jakob Nielsen, [10 Usability Heuristics for User Interface Design](https://www.nngroup.com/articles/ten-usability-heuristics/), published 1994, reviewed 30 January 2024. General heuristics inform status, consistency, recovery and user control; they are not a product-specific interaction specification or proof of usability.

## SUI03

GOV.UK Design System, [Check answers](https://design-system.service.gov.uk/patterns/check-answers/). An example of review/correction before submission when the journey needs it. We do not require a separate confirmation screen for every form.

## SUI04

GOV.UK Design System, [Styles](https://design-system.service.gov.uk/styles/). A mature system describes layout, spacing, typography and visual conventions. We adopt the obligation to record coherent project conventions, not GOV.UK branding or a universal font/spacing scale.

## SUI05

W3C, [WCAG 2.2 Recommendation, 12 December 2024](https://www.w3.org/TR/2024/REC-WCAG22-20241212/), with the [published entry point](https://www.w3.org/TR/WCAG22/). Technology-independent success criteria and conformance requirements. Our chosen AA baseline requires assessment of the full applicable scope, not a subset of convenient automated rules. Do not label a partial scan as conformance or legal compliance.

## SUI06

W3C WAI, [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/) and [Read Me First](https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/). Widget semantics, accessible names and keyboard/focus behavior. ARIA roles do not supply missing behavior. APG is guidance; its examples need browser/assistive-technology evaluation for the product.

## SUI07

W3C WAI, [Evaluating Web Accessibility Overview](https://www.w3.org/WAI/test-evaluate/). Evaluate throughout development using tools and knowledgeable human evaluation. An automated tool alone cannot determine accessibility conformance.

## SUI08

GOV.UK Design System, [Error summary](https://design-system.service.gov.uk/components/error-summary/) and [Text input](https://design-system.service.gov.uk/components/text-input/). Labels, field feedback and correction patterns inform our form obligations. Adopt exact patterns only where they fit the accepted interaction and accessibility requirements.

## SUI09

Microsoft Playwright, [Best Practices](https://playwright.dev/docs/best-practices). User-visible behavior, isolated tests, controlled owned boundaries, observable locators and bounded waiting inform our browser policy. Playwright is a candidate tool binding, not a requirement of WCAG or Nielsen.

## SUI10

Microsoft Playwright, [Visual comparisons](https://playwright.dev/docs/test-snapshots). Reference/actual rendering comparisons require controlled conditions and review. A generated initial screenshot is not an accepted product design; a changed baseline needs its own acceptance.

## SUI11

OWASP, [HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html). Browser storage, origin/message boundaries and client-side data are security concerns; do not store session identifiers in local storage or treat client storage as trusted. Session architecture and additional XSS/CSRF controls need project-specific review. No full ASVS compliance is claimed.

## SUI12

React, [Choosing the State Structure](https://react.dev/learn/choosing-the-state-structure). Avoid contradictory/redundant state and unnecessary duplication. Guidance is React-specific; applying its principles does not mandate React, Redux or another state library.

## SUI13

TypeScript, [strict compiler option](https://www.typescriptlang.org/tsconfig/strict.html). Strict checks evolve with compiler versions; they do not provide runtime input validation or security guarantees. Our TypeScript binding requires explicit supported versions and review of disabled subchecks.

## SUI14

Philip Walton, Google web.dev, [Web Vitals](https://web.dev/articles/vitals), updated 31 October 2024. Current good Core Web Vitals thresholds are LCP ≤2.5 seconds, INP ≤200 milliseconds and CLS ≤0.1 at the 75th percentile, segmented by device. These are field guidance; project lab/bundle budgets and evidence remain separately defined.

## SUI15

Testing Library, [Guiding Principles](https://testing-library.com/docs/guiding-principles/). Prefer interaction with rendered DOM/user behavior over component internals. A simulated DOM test is not an actual browser or assistive-technology session.

## SUI16

Microsoft Playwright, [Accessibility testing](https://playwright.dev/docs/accessibility-testing). Automated axe integration detects a subset of issues; combine it with manual assessment and inclusive user testing. The initially attempted `/docs/test-accessibility` path was unavailable; this is the inspected canonical page. No axe/Playwright application run is claimed in this standards change.
