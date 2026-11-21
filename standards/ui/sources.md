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

## Additions of 16 November 2026

Identified through search summaries on 16 November 2026. The network policy of the authoring session blocked these sites, so **the pages themselves were not opened in that session**. Inspect each page before a compliance or attribution claim relies on it. SUI01–SUI16 above were inspected earlier and are unchanged.

## SUI17

Design Tokens Community Group, [Design Tokens Format Module](https://www.designtokens.org/tr/drafts/format/). A vendor-neutral JSON format for exchanging design tokens between tools. Its publication status must be checked before adoption. The example `tokens.json` in this repository does not claim to follow it.

## SUI18

European Union, [Directive (EU) 2019/882, European Accessibility Act](https://eur-lex.europa.eu/eli/dir/2019/882/oj), and ETSI [EN 301 549](https://www.etsi.org/human-factors-accessibility/en-301-549-v3-the-harmonized-european-standard-for-ict-accessibility). Legal accessibility obligations for certain products and services in the EU and the harmonised ICT accessibility standard. Whether they apply is a legal determination for the project.

## SUI19

W3C Internationalization Activity, [Localization vs. Internationalization](https://www.w3.org/International/questions/qa-i18n). Designing so that content can be adapted to languages, scripts and regions, including text direction. Informs the language and direction decision.

## Additions of 21 November 2026

Read in full on 21 November 2026 unless marked. Books by Alan Cooper, Don Norman, Steve Krug and Jeff Patton could not be opened and no rule here depends on them.

## SUI20

Jesse James Garrett, *The Elements of User Experience* diagram, 30 March 2000 (read from a university mirror; the author's site was unreachable). Five planes from strategy to surface. Garrett states the model "does not describe a development process".

## SUI21

Nielsen Norman Group: [IA vs. Navigation](https://www.nngroup.com/articles/ia-vs-navigation/), [Left-Side Vertical Navigation](https://www.nngroup.com/articles/vertical-nav/), [Tabs, Used Right](https://www.nngroup.com/articles/tabs-used-right/), [Wireflows](https://www.nngroup.com/articles/wireflows/), [UX Prototypes: Low Fidelity vs. High Fidelity](https://www.nngroup.com/articles/ux-prototype-hi-lo-fidelity/). Several were read as summaries and headings only.

## SUI22

Nielsen Norman Group: [Data Tables: Four Major User Tasks](https://www.nngroup.com/articles/data-tables/), [Designing Empty States in Complex Applications](https://www.nngroup.com/articles/empty-state-interface-design/), [Progress Indicators](https://www.nngroup.com/articles/progress-indicators/), [Skeleton Screens 101](https://www.nngroup.com/articles/skeleton-screens/), [Confirmation Dialogs](https://www.nngroup.com/articles/confirmation-dialog/), [Indicators, Validations, and Notifications](https://www.nngroup.com/articles/indicators-validations-notifications/), [Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/).

## SUI23

GOV.UK, [Recover from validation errors](https://design-system.service.gov.uk/patterns/validation/) and [Structuring forms](https://www.gov.uk/service-manual/design/form-structure); Luke Wroblewski, [Inline Validation in Web Forms](https://alistapart.com/article/inline-validation-in-web-forms/). They disagree on when to validate: GOV.UK validates on submit unless research supports inline; Wroblewski's small study favoured inline validation for difficult fields. UX07 requires the project to record its choice.

## SUI24

IBM Carbon Design System patterns: [empty states](https://carbondesignsystem.com/patterns/empty-states-pattern/), [loading](https://carbondesignsystem.com/patterns/loading-pattern/), [notifications](https://carbondesignsystem.com/patterns/notification-pattern/), [dialogs](https://carbondesignsystem.com/patterns/dialog-pattern/).

## SUI25

[shadcn/ui](https://ui.shadcn.com/docs) documentation and changelog. Component source is copied into the consuming repository; its primitives handle focus and keyboard behavior, while contrast, labels and composition remain the project's responsibility. Choosing it as the default base is our policy.

## SUI26

Design Tokens Community Group, [Design Tokens Format Module 2025.10](https://www.designtokens.org/TR/2025.10/format/), a W3C Community Group Final Report, not a W3C Recommendation. Atlassian, [Spacing](https://atlassian.design/foundations/spacing). This supersedes the status note in SUI17.

## SUI27

Nielsen Norman Group, [How to Conduct a Heuristic Evaluation](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/): independent evaluators; not a replacement for user research. Vendor documentation and terms for AI design tools, including Polymet, were read for the [research record](../../research/2026-11-21-ui-and-database-design-research.md).
