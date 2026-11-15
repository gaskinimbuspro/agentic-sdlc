# Context handoff — backend integration and UI standards

Recorded 16 November 2026, Europe/Istanbul. This is durable continuation context, not a release or review approval. Read current GitHub state before acting; the evidence identities below are historical and must not be relabeled for a newer commit.

## User intent and communication

Gökhan is a Cloud/DevOps consultant building a reusable, source-based agentic SDLC method. He wants common engineering rules with language/framework profiles, explicit planning/design/task ownership, meaningful tests and enforced completion. He does not want standards reinvented after each project starts or repeated reminders to run ordinary checks.

Reply to Gökhan in Turkish. Author repository documents, code/comments and issue/PR text in English. Keep work in this repository separate from his Voltran/Backstage repository. He asked to finish/save the current work and leave this handoff for a fresh conversation; do not restart the previous research or silently expand into product deployment.

## Repository and authoritative links

- Repository: <https://github.com/gaskinimbuspro/agentic-sdlc>.
- Instructions: [AGENTS.md](../../AGENTS.md).
- [Backend PR #6](https://github.com/gaskinimbuspro/agentic-sdlc/pull/6): merged.
- [Backend issue #3](https://github.com/gaskinimbuspro/agentic-sdlc/issues/3): closed as completed after explicit user authorization.
- [UI PR #9](https://github.com/gaskinimbuspro/agentic-sdlc/pull/9): open, branch `codex/ui-standard`, target `main`.
- [UI issue #8](https://github.com/gaskinimbuspro/agentic-sdlc/issues/8): open; current UI standards/design-readiness scope.
- GitHub owns task status. [Research backlog](../../research/backlog.json) records definitions/links; old draft descriptions are not current acceptance state.

## Backend: completed integration

PR #6 includes common/backend testing rules, Python/FastAPI, Go/net-http and .NET/ASP.NET Core profiles/reference implementations, shared real PostgreSQL acceptance, readiness/task/evidence validators and named check runners.

An explicitly authorized independent agent reviewed the package, found three P2 blockers and one P3 observation, and approved the repaired exact candidate with zero blocking findings. The reports are now archived: [initial findings](../reviews/backend-review-36ca6c3.md), [final independent approval](../reviews/backend-review-c6669ed.md). This is an independent agent review record, not a GitHub approval submitted using the author's identity.

Resolved defects include strict JSON property casing, canonical hyphenated UUID wire syntax, malformed identity types including singleton arrays, absent versus empty list limit, and correlation for Python413. Do not weaken those cases.

| Identity/evidence | Recorded value |
| --- | --- |
| Approved source | `c6669eda6e240ed120da17b90744d3f96ee7636c` |
| Reviewed target base | `51a700c4c8795727308198b8b1bd81c2dbc5b9ea` |
| Tested merge candidate | `02dabc114638f72991c9b145278cd371242d07ae` |
| Actual main integration | `dc78014b80c452ee2ebc5518b5e01d50e1ed2526` |
| Reviewed/tested and integrated tree | `0318eeb67fa3c2f15ba3c91669f2a4ece683937a` |
| Pre-merge CI | [43761064335](https://github.com/gaskinimbuspro/agentic-sdlc/actions/runs/43761064335), all four jobs passed |
| Main CI | [43761590962](https://github.com/gaskinimbuspro/agentic-sdlc/actions/runs/43761590962), passed |

Backend results: 73 tools tests, 6 Python unit tests, 1 Go parent table-driven test, 4 .NET unit tests and 55 real HTTP/PostgreSQL acceptance cases per stack = **249** executed results, zero failures/skips. The actual merged tree was checked against the reviewed merge tree; commit SHAs differ because merge metadata differs.

Gökhan explicitly authorized the separate backend review and merge. Closing issue #3 was initially rejected by automatic approval review as a separately unauthorized workflow-state change. He then explicitly authorized closing that issue; it is now closed. There is no pending permission question for backend integration/issue closure. Do not ask for these authorizations again.

## UI: saved implementation scope

Start at [UI/UX standard](../../standards/ui/README.md). The package contains:

- U01–U16 common UI rules, UT01–UT10 testing rules, UC01–UC12 scenario families and UD01–UD10 completion conditions.
- A [primary-source ledger](../../standards/ui/sources.md): W3C WCAG/WAI/APG, GOV.UK, Jakob Nielsen, OWASP and official TypeScript/React/Testing Library/Playwright/web.dev material. Mandatory tools/gates/task choices are our policy, not universal mandates attributed to those authors.
- [Delivery workflow](../../standards/ui/delivery-workflow.md): product intent → journeys → screen/visual design → acceptance → technical readiness → bounded implementation → CI/independent review → integration.
- Deliberately incomplete [design packet](../../standards/ui/design-packet.template.json) and [frontend profile](../../standards/ui/frontend-profile.template.json). Changing a flag does not complete them.
- A [two-screen customer-admin example](../../standards/ui/examples/customer-admin/design.md), [wireframe](../../standards/ui/examples/customer-admin/wireframes.svg), illustrative tokens, four interactions, three journeys and fifteen expected outcome cases tied to the actual customer API.
- `ui-standard design` in the existing Python tool package. It checks schema, local references, routes/IDs, screen states, connected journeys, action destinations, API response mappings and case coverage. Output is **reviewable**, not approved, implementation-ready, Done or deployed.
- 24 meaningful UI-validator tests, taking the tool unit suite to **97**. A dedicated CI job builds a wheel, installs it into a separate environment using hash-locked dependencies, verifies imports come from that environment, accepts the example and requires the incomplete template to fail.

The example is a low-fidelity design fragment, not accepted branding or a frontend application. No frontend component/browser/backend, visual regression, automated/manual accessibility or performance suite has been claimed as executed. The wireframe was rasterized and visually inspected as an illustration, not as application/browser acceptance.

No frontend framework/runtime has been selected for an adopting project. TypeScript/React is discussed as an option. The frontend profile intentionally remains draft until actual versions, commands, paths, environments and acceptance authority are bound. No Polymet/Figma account/vendor trial, paid service or design export has been performed.

## UI verification checkpoint before this handoff commit

Source `876aaa464ad4a0572305c9c67bf5c80be3027a22`, base `dc78014b80c452ee2ebc5518b5e01d50e1ed2526`, tested merge `5539adb6de968d2b062c2d65238c87352f7e5a7e`:

- [Backend/tool CI 43762476648](https://github.com/gaskinimbuspro/agentic-sdlc/actions/runs/43762476648): passed.
- [Installed UI artifact CI 43762476740](https://github.com/gaskinimbuspro/agentic-sdlc/actions/runs/43762476740): passed.
- Local maintenance: 247 Markdown links/anchors, 48 UI rule/case/Done IDs, 28 backend matrix rows, no errors.
- Local tools: format/lint/strict types, architecture/known-secret checks, Bandit, 97 unit tests and package build passed. Installed wheel accepted the example and rejected the incomplete template.

This handoff and archived review reports are added in a later documentation commit. **Fetch PR #9's current head/base/merge and current check results before acceptance.** The final PR description records the latest validation after that commit; do not reuse the older implementation checkpoint as proof for a different source identity.

## Reproduction and environment

In the fresh repository checkout, install the locked tools:

```sh
uv sync --locked --group dev --no-install-project
uv sync --locked --group dev --no-build-isolation
uv run --no-sync backend-verify tools
uv run --no-sync ui-standard design standards/ui/examples/customer-admin/design-packet.json
```

The incomplete design template must return exit1 with `status: blocked`. Actual acceptance tests require the documented language toolchain, packaged backend and disposable PostgreSQL; use `backend-verify <profile>` rather than running acceptance without its environment. The reference README records pinned versions and bootstrap.

The previous workspace used `/workspace/wt/ui-standard` for UI, `/workspace/wt/backend-controls-pr6` for backend, and the installed GitHub connector for authenticated API writes. Public git fetch worked. A new window may have a different filesystem: clone/fetch the repository and use its current branch/PR, not those paths as durable storage. Never read authentication files or print credentials to recover access.

## Next conversation: exact continuation

1. Read this note, AGENTS.md, PR #9's current description/diff/checks and the UI standard/source ledger. Confirm saved branch/head and any new reviewer/user changes.
2. Finish independent review/adoption of the UI standards candidate; address concrete findings. **UI PR #9 has not been independently approved or merged in this handoff.** The earlier merge authorization applied to backend PR #6, not blanket future PRs.
3. For executable frontend adoption, deliberately select/record a framework binding, complete the frontend profile and exercise a real UI against accepted design/API requirements. Do not claim the design validator substitutes for those tests or ask the user to redesign the already established baseline from scratch.
4. Complete broader database operations, DevOps/GitOps/security and agent dispatch/context/evidence integration as separately scoped work. Backend data/security obligations already exist, but full backup/restore, production identity/TLS, platform rollout and an unattended dispatcher have not been installed.

OpenHands, BMad, AWS AI-DLC, Spec Kit, model routing, GPU hosting, MCP/n8n and repository provisioning remain separate researched/undecided integrations. No framework choice or runtime reliability is established merely by diagrams/prompts. Preserve the distinction between guidance, our policy, implemented controls and actual trusted runtime evidence.

Suggested continuation instruction:

> Continue `gaskinimbuspro/agentic-sdlc` from `docs/handoffs/2026-11-16-ui-standard.md` and current PR #9 on `codex/ui-standard`. Verify current GitHub state, preserve completed backend integration and continue the saved UI standards work without restarting the previous decisions. Reply in Turkish and maintain repository artifacts in English.
