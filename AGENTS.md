# Repository instructions

This repository defines an agentic SDLC method and backend standard. All authored documents, issue/PR text, diagrams, and code comments must be in English. Preserve personal names, source titles, and third-party license notices as needed.

## Read first

- README.md for scope and current implementation status.
- standards/backend/README.md for the backend standard.
- standards/backend/delivery-workflow.md and agent-contract.md for role/dispatch responsibilities.
- The task's acceptance criteria, selected language profile, and referenced decisions.

## Work rules

Keep standard IDs and source attribution stable. Separate cited guidance, vendor observations, and our proposed policies. Do not present draft workflow diagrams or templates as running automation.

For backend adoption, use one bounded coding task per implementation owner/workspace/context, with a separate independent review. Do not infer a requirement to spawn agents merely because roles are described. Actual tool/permission and dispatch policy must be configured by the project.

Do not weaken tests, acceptance criteria, or required checks to claim success. Record unavailable checks as blocked. Completion requires the candidate-bound Definition of Done and trusted evidence; an agent's own statement is not evidence.

For repository maintenance, validate Markdown links/anchors, JSON templates, rule IDs, and source/diagram consistency. Regenerate diagrams after editing their generator and inspect the previews. Do not claim application test execution when this repository contains no backend application.

The product owner follows the project through a Turkish system map at https://claude.ai/artifact/BYTBwSDVRp5bmStVJwRzj2. It mirrors the step statuses of diagram view 07, the trial table in `platform/README.md`, the decision tables in `docs/architecture/README.md` and the cast. When any of these changes, update the map in the same session: read the artifact, change only what changed, set its last-updated date and republish to the same link. Keep the Turkish page out of this repository.

Never commit credentials or sensitive environment output. Preserve unrelated user changes. Use focused branches/PRs; do not merge or deploy without task authorization. Update the PR description to its final scope.
