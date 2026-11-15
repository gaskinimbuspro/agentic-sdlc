# Standards and agentic delivery: evidence review

Reviewed: 15 November 2026. Status: research findings and proposed adoption criteria, not an adopted standard release or running system.

Historical assessment: the gap tables below describe the specification snapshot before the executable reference work in this PR. For the current implementation and trust boundary, see [backend adoption](../standards/backend/adoption.md). The research findings do not claim the later implementation is a production deployment.

## Purpose and evidence boundary

Gökhan's requirement is to establish reusable engineering standards and a delivery process that preserve decisions across projects and agent sessions. Routine delivery should not depend on repeatedly reminding an agent about already accepted requirements.

This review inspected first-party engineering articles, official standards pages, and specific workflow documents/templates. It did not run the products, validate their security boundaries, read the authors' entire books, or benchmark Qwen. Vendor experience reports are evidence of a reported implementation, not independent proof of equivalent results in our environment.

The local repository contains a backend v0.1 specification, language profiles, task/evidence templates, and workflow research. It does not contain the application-level enforcement or dispatcher described by those documents. The gap assessment below concerns this local documentation snapshot; it does not certify the current GitHub default branch.

## Findings from practitioners

| Reference | Observed approach | Implication for our design | Limit of transfer |
| --- | --- | --- | --- |
| R01: Ryan Lopopolo, OpenAI | Repository knowledge is authoritative; a short instruction entry point navigates deeper documents. Structural checks enforce selected architecture boundaries. | Store decisions in discoverable, versioned files and implement relevant checks. | This is an internal beta experience report. Its minimal blocking merge policy is not our acceptance policy. |
| R02: Alistair Gray, Stripe | Isolated standardized devboxes; blueprints combine deterministic operations and agent steps; local feedback precedes bounded CI repair. | Execution should enforce mandatory steps rather than asking the model to remember them. Reuse development infrastructure and isolate work. | Stripe already has substantial infrastructure and tests. Its scale and retry choices do not establish our capacity or latency. |
| R03: Prithvi Rajasekaran, Anthropic | Planner/generator/evaluator experiments use explicit criteria and running-application checks. Harness simplification depends on model capability. | Separate intended behavior from implementation claims; evaluate actual interactions. Measure whether extra roles justify their cost. | Demonstrations still contain usability/functionality gaps. Fresh-context and evaluator policies are not universal optima. |
| R04: Wilson Lin, Cursor | Flat coordination caused locking and ownership problems. Planner/worker separation helped; an extra integrator caused bottlenecks. | Give ownership and coordination explicit semantics; add roles only when evidence supports them. | Experimental large-scale runs are not a recommended starting topology for one developer. |
| R05: Birgitta Böckeler, Thoughtworks | Distinguishes guidance from feedback, and deterministic checks from model judgment; maintainability checks do not establish intended behavior. | Evaluate maintainability, architecture characteristics, and functional acceptance separately. | Green generated tests do not establish that the product matches an underspecified request. |

These sources agree on useful mechanisms, not one universal architecture. They differ in merge policy, review intensity, task duration, context management, and coordination. We must resolve these differences deliberately rather than combine every role and tool.

## Current method implementations: important corrections

### GitHub Spec Kit

Snapshot: `2ee2b1e8005905db05f5717300a469b3068b908f`. Inspected README, task template, analysis command, and convergence command. Official workflow documentation was also read.

Spec Kit now describes reusable presets, extensions, and resumable YAML workflows combining agent and shell steps. Describing the current toolkit as only a collection of prompts would be incomplete. The analysis command checks consistency across requirements, plans, and tasks; convergence identifies missing, partial, contradictory, and unrequested implementation.

Two inspected defaults need adaptation before adoption:

- The task template makes tests optional unless requested in the specification. Our applicable behavior-verification requirements must be explicit and independently enforced.
- Convergence skips constitution checks when the constitution remains a template. Our readiness check must reject an incomplete governing profile before dispatch.

The official workflow documentation notes that an interrupted side effect can repeat before its completion checkpoint. Resume support therefore does not eliminate the need for idempotent external actions. These findings are document/template inspection, not an executed assessment.

### AWS AI-DLC

Snapshot: `8c4f79b4b77c5a64738b01b350be2bf72c357dae`; README advertises 2.11.4. Inspected README and phase/stage, state/audit, and session-management guides.

Current documentation describes a shared deterministic engine, persistent intent state, audit events, source-bound review evidence, and harness adapters. It is a candidate for reusing coordination machinery, not merely a planning checklist. Its approval behavior, configurable guards, and harness-specific lifecycle events must be evaluated against our desired unattended operation.

The state guide explicitly distinguishes guardrails from a security boundary. File permissions, CI authority, credentials, and independent evidence remain separate concerns. We have not inspected the complete engine or proved these controls in execution. Do not commit to building a replacement controller before comparing reusable implementations.

### BMad Method

The current main README distinguishes stable v6.12 from v7 preview alpha. Stable branch snapshot inspected: `bab9082c3e884e0d72c759bcd1a6d90bcc01be84` (commit message: v6.12.4). The readiness reference asks whether recorded work can be implemented without inventing missing decisions and requires intent/story traceability plus recorded architecture/UX decisions.

This is a useful readiness rubric. It is not proof that the instructions are enforced by a runtime. A main-branch preview and stable workflow must not be mixed implicitly. BMad's wider ecosystem and Loop require a separate pinned implementation review before runtime selection.

## Reusable standards structure proposed for evaluation

One centrally maintained baseline should supply common rules. Language/framework/data/deployment profiles activate relevant rules. A project records its own behavior and decisions against a pinned baseline. Project-specific requirements are not redefinitions of shared engineering standards.

| Layer | Contents | Change authority proposed |
| --- | --- | --- |
| Shared engineering baseline | Evidence rules, testing responsibilities, security, contracts, decision records, completion semantics | Reviewed baseline release |
| Approved profiles | Python/.NET/Go, chosen UI stack, supported databases, Kubernetes/GitOps; pinned tool configurations and checks | Reviewed profile release |
| Project decisions | Product behavior, roles/permissions, user flows, data ownership, selected profiles, operational targets | Project planning/change decision |
| Task packet | Exact scope, baseline/profile versions, decision references, acceptance cases, dependencies, permissions, commands | Planner plus readiness validation |
| Evidence record | Actual results, reports, source/candidate/artifact identities, review findings | Trusted execution and independent acceptance |

An adopting project must not silently follow the latest central rules. Upgrades need an explicit version change and impact review. A valid new requirement can change a project; an implementer's convenience cannot silently change its accepted meaning.

## Coverage and gaps in the current local draft

| Domain | Existing coverage | Work before adopting a baseline |
| --- | --- | --- |
| Backend | Common rules, Python/.NET/Go profiles, test cases, Definition of Done | Review framework-specific profiles, implement verification, and exercise a real reference application. Do not add more languages without a profile. |
| UI/UX | UI is named in research scope, not a separate standard | Specify journeys, navigation/actions, component states, design tokens, responsive behavior, accessibility, frontend boundaries, and functional/visual verification. A design tool is not the standard. |
| Data | Transactions, constraints, concurrency, migrations appear in backend rules | Establish ownership, engine profiles, query/index review, migration compatibility, retention/deletion, access controls, recovery objectives and restore drills. |
| Platform/GitOps | Proposed remote-execution and release concepts | Specify artifact identity/promotion, environments, reconciliation, deployment verification, configuration/secrets, resource/network policy, observability and recovery. Separate application rollback from data recovery. |
| Security | General backend controls and ASVS references | Map versioned applicable requirements to owners/checks; define threat modeling, dependency/supply-chain policy and exceptions. No full ASVS or SSDF conformity is established. |
| Agent delivery | Roles, bounded task packets, independent review and evidence requirements | Prove exclusive assignment, context/workspace isolation, failure recovery, permissions, evidence integrity and reporting in a selected implementation. |

Architectural grounding includes Simon Brown's component boundaries and Mark Richards' decision/trade-off records, alongside Fowler's alternatives. Data evolution draws on Pramod Sadalage and Fowler. The detailed existing language references remain in [backend sources](../standards/backend/sources.md); this review does not repeat a full language audit.

## Preventing repeated decision drift

The following are proposed controls, not mechanisms already implemented here:

| Failure Gökhan wants to avoid | Preventive control | Negative demonstration required |
| --- | --- | --- |
| Agent chooses a different framework or architecture | Pinned project profile, recorded decisions, selected dependency/structural checks | An unauthorized profile/dependency change is rejected. |
| Accepted behavior is forgotten | Requirement-to-task-to-acceptance mapping and scoped authoritative context | A requirement without a covering task/case prevents readiness. |
| Agent changes tests to fit its implementation | Independent expected outcomes, protected acceptance controls, review of test changes | A weakened assertion or removed required case cannot produce acceptance. |
| Work is declared complete without testing | Required suite/report/count and candidate checks | Missing report, zero tests, skipped required verification, and stale evidence are rejected. |
| Implementer changes the rules that judge its work | Protected baseline/check configurations, separate review/authority, trusted CI | The candidate cannot grant itself a new exception or approve its own evidence. |
| A new task inherits a confused long conversation | New task session with required decisions and task packet; explicit same-task handoff on recovery | Task B starts without task A's transcript while receiving necessary shared contracts. |
| Two workers perform the same task | Durable exclusive claim with recovery semantics | Duplicate delivery and worker restart do not create two accepted owners. |
| Recovery causes duplicate external actions | Idempotency keys and reconciliation for repository/issue/PR operations | Replaying an interrupted operation does not create a second issue/PR. |
| A UI is attractive but its main action does nothing | Recorded interaction contract and running-application verification | A display-only control fails its acceptance case. |
| Deployment looks healthy but functionality is broken | Version-bound health plus critical business-journey checks | A ready process with a broken required journey cannot pass release acceptance. |

Not every semantic requirement can be checked statically. Assign a real verification method or explicit review, rather than relabeling model confidence as proof. Protecting the acceptance process is as important as writing more tests.

## Reference standards: scope, not claimed compliance

| Reference inspected | Use in the proposed baseline | Boundary |
| --- | --- | --- |
| NIST SSDF SP 800-218 v1.1 final publication | Secure-development lifecycle practices | High-level guidance; this review did not establish an implementation mapping or that it is the newest publication in the series. |
| OWASP ASVS 5.0.0 stable overview | Versioned web application/security verification requirements | Select and map requirements explicitly; referencing ASVS is not compliance. |
| W3C WCAG 2.2 Recommendation | Accessibility requirements; proposed AA target for web UI profiles | Accessibility is only part of UX quality; automated checks are incomplete. |
| OpenGitOps principles v1.0.0 | Declarative, versioned/immutable, automatically pulled and continuously reconciled desired state | Does not select Argo CD/Flux or define the whole release/security process. |
| SLSA v1.2 approved specification overview | Artifact provenance and supply-chain assurance | No SLSA level is claimed; inspect the selected track's requirements before adoption. |

## Exit criteria for a reusable v1 baseline

Research is complete for a selected scope only when sources, alternatives, conflicts, selected policies, applicability, and verification ownership are recorded. A baseline is operationally validated only after an authorized pilot exercises it.

1. Resolve the proposed domain rule inventory and profiles; keep a visible gap list rather than filling unknowns with assumptions.
2. Compare pinned BMad, Spec Kit, and AI-DLC paths using the same brief and expected outcomes. Separate planning usefulness, reusable execution, and missing integration. Select one owner for workflow state; avoid stacked competing controllers.
3. Produce reviewable baseline/profile definitions, a complete project decision schema, task/evidence contracts and a rule-to-check matrix.
4. In a later authorized pilot, generate a small real API + UI + database project and exercise its agreed GitOps deployment path. Verify correct behavior and deliberately broken cases, context recovery and evidence rejection.
5. Measure accepted-task duration, repair rounds, human interventions, escaped defects, token/compute cost and resource pressure. Do not substitute PR volume, lines of code or a green badge for delivery quality.
6. Release only the validated profiles. Adopt other languages/topologies through additional reviewed profiles; do not imply that one pilot validates all stacks.

No numerical speed/cost target is established by these readings. No deployment, installation, model execution, or runtime trial was performed for this review.

## Sources and inspected scope

All accessed on 15 November 2026. Links to repository files are pinned where their contents support specific findings.

- **R01** Ryan Lopopolo, OpenAI, 11 February 2026: [Harness engineering](https://openai.com/index/harness-engineering/). Inspected repository knowledge, architecture enforcement, merge policy and limitations sections.
- **R02** Alistair Gray, Stripe, 19 February 2026: [Minions, Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2). Inspected devboxes, blueprints, scoped rules/tools and local/CI repair.
- **R03** Prithvi Rajasekaran, Anthropic, 24 March 2026: [Harness design for long-running application development](https://www.anthropic.com/research/harness-design-long-running-apps). Inspected context/evaluation, running-app checks, results and simplification limits.
- **R04** Wilson Lin, Cursor, 14 January 2026: [Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents). Inspected failed coordination, planner/workers and remaining problems.
- **R05** Birgitta Böckeler, 2 April 2026: [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html). This is Böckeler's article, not Fowler's authorship. Inspected guidance/feedback and maintainability/architecture/behavior distinctions.
- **R06** GitHub Spec Kit: [README](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/README.md), [task template](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/templates/tasks-template.md), [analysis](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/templates/commands/analyze.md), [convergence](https://github.com/github/spec-kit/blob/2ee2b1e8005905db05f5717300a469b3068b908f/templates/commands/converge.md), [official workflow guide](https://github.github.io/spec-kit/workflows/overview.html). The live guide is not an immutable snapshot.
- **R07** AWS AI-DLC: [README](https://github.com/awslabs/aidlc-workflows/blob/8c4f79b4b77c5a64738b01b350be2bf72c357dae/README.md), [phases](https://github.com/awslabs/aidlc-workflows/blob/8c4f79b4b77c5a64738b01b350be2bf72c357dae/docs/guide/04-phases-and-stages.md), [state/audit](https://github.com/awslabs/aidlc-workflows/blob/8c4f79b4b77c5a64738b01b350be2bf72c357dae/docs/guide/10-state-and-audit.md), [sessions](https://github.com/awslabs/aidlc-workflows/blob/8c4f79b4b77c5a64738b01b350be2bf72c357dae/docs/guide/11-session-management.md). Documentation review, not complete engine inspection.
- **R08** BMad Method: [current README](https://github.com/bmad-code-org/BMAD-METHOD) for release-line distinction; stable [readiness reference](https://github.com/bmad-code-org/BMAD-METHOD/blob/bab9082c3e884e0d72c759bcd1a6d90bcc01be84/src/bmm-skills/plan/bmad-sprint-planning/references/readiness-gate.md). No preview workflow adoption.
- **R09** Simon Brown: [Modular monolith / package by component](https://simonbrown.je/modular-monolith/). Inspected public article text; embedded talks were not reviewed.
- **R10** Mark Richards, 27 March 2023: [Incorporating ADRs into existing systems](https://www.developertoarchitect.com/lessons/lesson157.html). Inspected public lesson summary, not the video or books.
- **R11** Pramod Sadalage and Martin Fowler, May 2016: [Evolutionary Database Design](https://martinfowler.com/articles/evodb.html). Inspected migration/version-control/CI practices and treatment of change.
- **R12** NIST: [SSDF v1.1 final publication](https://csrc.nist.gov/pubs/sp/800/218/final). Publication overview.
- **R13** OWASP: [ASVS overview and stable version](https://asvs.owasp.org/). Overview and requirement-reference guidance; no exhaustive control assessment.
- **R14** W3C: [WCAG 2.2](https://www.w3.org/TR/WCAG22/). Recommendation scope and testable success-criteria model.
- **R15** [OpenGitOps](https://opengitops.dev/). Four principles and v1.0.0 reference.
- **R16** [SLSA v1.2](https://slsa.dev/spec/v1.2/). Approved specification overview; no claim of auditing every track requirement.
