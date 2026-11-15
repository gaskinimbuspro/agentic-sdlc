# Backend acceptance review handoff

This packet prepares an independent review of [PR #6](https://github.com/gaskinimbuspro/agentic-sdlc/pull/6). It is an implementation handoff, not an approval, a released baseline or permission to merge. The author of the implementation cannot provide its independent acceptance verdict.

## Scope to review

Review the common rules, Python/FastAPI, Go/net-http and .NET/ASP.NET Core bindings, shared PostgreSQL acceptance suite, input/evidence validators and new-project adoption instructions. Preserve existing rule IDs and distinguish source guidance from our chosen mandatory controls. Start with [adoption](adoption.md), [verification matrix](verification-matrix.md), [Definition of Done](definition-of-done.md) and the [reference decisions](../../reference/README.md).

The expected output is a candidate-bound review with blocking findings or an explicit approval. Green CI is necessary evidence; it does not establish requirement suitability, independent approval or integration.

## Obtain current evidence

1. Read the current PR head, target base and tested merge candidate from GitHub. Do not reuse a prior run merely because its branch name matches.
2. Verify that all four checks (`backend-tools`, `backend-python`, `backend-go`, `backend-dotnet`) passed for that head and the current integration candidate. Reports must identify the actual merge checkout with `dirty: false`.
3. Read the per-profile `results.json`, logs, JUnit/TRX/Go reports and artifact identities from the linked CI run. The runner stops at the first failed dependency; omitted later checks cannot be interpreted as passed.
4. For this reference revision, expect at least 73 tool tests, 6 Python unit tests, 1 parent Go table-driven unit test and 4 .NET unit tests, plus 55 HTTP/PostgreSQL acceptance cases per language. All mandatory cases in `reference/acceptance-policy.json` must be present. Zero/failed/skipped/interrupted results prevent acceptance; counts alone do not demonstrate meaningful coverage.
5. Reproduce relevant cases in an isolated checkout using the pinned setup in the reference README. `uv run --no-sync backend-verify all` runs the same required commands; unavailable SDKs, Docker or scanners are blockers, not successful checks.

## Decisions and adversarial checks

| Review concern | Inspect or independently challenge |
| --- | --- |
| Architecture and contract | Domain validation stays independent of transport/storage. The actual packaged processes implement the recorded API decisions; avoid imposing speculative infrastructure. |
| Authorization and confidentiality | Invalid credentials, wrong scopes and cross-tenant access cannot write/read unauthorized records. Logs and error bodies exclude credentials and customer data. |
| Persistence | Unique races, second-write failure and pre-commit deadlines preserve declared invariants on real PostgreSQL. A lost response during commit is an unknown outcome, not proof of rollback. |
| Schema history | Existing customer data survives upgrade. Changed/deleted applied files, backfilled versions, duplicate version numbers and empty/missing input are rejected. Rejected migration attempts preserve schema/history. |
| Test evidence | A passed case cannot override a failed/aborted TRX run, JUnit suite error, incomplete Go stream or duplicate Go result. Check omitted mandatory cases as well as totals. |
| Independent review | Evidence names an explicit implementation owner. Missing owners, self-review, untrusted reviewers, stale identities, invalid finding counts and unresolved findings must fail. |
| Trust boundary | Worker-authored JSON and candidate-controlled checks cannot attest to themselves. Protect policy/acceptance changes and retrieve reports/review identities through the adopting project's trusted controls. |
| Operations and support | Pinned versions, security findings, bounded resources, health/lifecycle behavior and documented limitations match the actual implementation. Functional deadlines do not prove production load/SLOs. |

## Follow-up hardening reproduction

Against implementation `de6e9502712ec43977dc36ea47e9265ec28d54be`, new regression tests exposed 18 missing report/owner rejections and five migration-history rejections. These were observed failures before the fixes, not simulated scanner or database results. A positive control also verifies successful complete Go/TRX runs remain accepted.

The report regression cases are in `tests/unit/test_gates.py`. The migration cases are `test_migration_history_changes_are_rejected` in `tests/acceptance/test_customers.py`; they run against the actual disposable PostgreSQL container. The PR records the final candidate's CI results. An independent reviewer should reproduce or challenge these controls rather than treating this author's observations as an approval.

## Required review record

Record reviewer identity, implementation owner, source/head SHA, integration base, tested candidate, CI run/report links, relevant requirement/case IDs, findings and their severity, outstanding decisions and verdict. Invalidate the verdict when relevant source/base changes. Leave the issue open while independent approval or required integration remains outstanding. Merge/release authority follows the adopting project's explicit policy.

This backend handoff does not install an agent dispatcher, repository protection, production identity provider/TLS, complete database operations, UI standards or GitOps deployment. Those remain separate contracts; do not make their completion an implicit claim of this review.
