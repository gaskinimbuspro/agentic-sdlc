Archived independent agent review. The commit identities and verdict below apply to the backend candidate named in the report, not to subsequent UI changes. Local paths in the original report are historical; both review reports are archived in this directory.

# Independent backend review — PR #6

- Reviewer: `/root/backend_independent_review`, a separately dispatched agent authorized by Gökhan. This is not the implementing agent's approval and is not a GitHub approval submitted under the PR author's account.
- Implementation owner: `/root` (Codex), publishing through `gaskinimbuspro`.
- Source head: `36ca6c37907a9bc6b66358eb333f41bf40fcb9cb`.
- Target base: `51a700c4c8795727308198b8b1bd81c2dbc5b9ea`.
- Tested PR merge candidate: `384f839fb90fb2a57db67bd093900ff06450b780`.
- CI: https://github.com/gaskinimbuspro/agentic-sdlc/actions/runs/43757805372
- Verdict: **REQUEST_CHANGES**. Blocking findings: **3 (P2)**. Nonblocking observations: **1 (P3)**.

## Scope and evidence

Read repository instructions, backend standard and D01–D10, review handoff, concrete reference decisions, input/evidence/report validators, migrations, runner/workflow, security/architecture controls, shared acceptance tests and all three application implementations. Scope is the documented reference/verification package, not a production platform, complete IAM/TLS solution or installed agent dispatcher.

Independently fetched current PR/base identities and the four CI jobs/logs through GitHub. All four CI jobs passed. Logs bind the clean checkout to the tested merge candidate and report 73 tools tests, 6 Python unit tests, 1 Go parent unit test, 4 .NET unit tests and 43 acceptance cases per language: **213**, zero failed/skipped required tests.

Independently reran `uv run --no-sync pytest tests/unit -q`: **73 passed**. Reran document validation: **198 local links**, **28 matrix rows**, no errors. Compiled the exact-source Go implementation with official Go 1.27.4 into `/tmp/backend-review-go`; exit 0. Started that binary and the installed Python reference wheel against a newly created official PostgreSQL 18.7 container pinned to the repository digest. Used synthetic runtime-generated credentials and HTTP probes independent of the shared acceptance suite. The temporary database container and processes were removed afterward. No source files were modified.

Local .NET SDK was unavailable; the .NET runtime conclusion below is based on source inspection plus existing candidate-bound CI, not a claimed local .NET probe.

## Blocking findings

### R1 — P2: case-insensitive payload decoding violates the strict shared request contract

Locations: `reference/go/main.go:135` and `reference/dotnet/CustomerApi/Program.cs:87`.

`reference/openapi.json:39` disallows unknown properties and requires lowercase `name`. The Go decoder's `DisallowUnknownFields` still accepts case-insensitive struct field matches; .NET selects case-insensitive matching through `JsonSerializerDefaults.Web` without overriding it. A payload with `NAME` instead of `name`, otherwise valid, is invalid against that contract.

Independent runtime result: Python **400**, Go **201**, with a real persisted customer. .NET has the same static configuration issue; its equivalent regression must run in CI. This violates the claimed common contract/strict payload behavior (B04/B05, TC02/TC09).

Requested fix: enforce exact accepted property names in Go and case-sensitive JSON matching in .NET, without weakening the accepted contract. Add a shared invalid-casing case asserting safe 400 and no customer/audit effects for each language.

### R2 — P2: malformed tenant claim escapes Python authentication error mapping

Location: `reference/python/src/customer_api/main.py:133`.

`uuid.UUID(claims["tenant_id"])` is called before validating the claim's type. With numeric `tenant_id: 123` in an otherwise correctly signed test JWT, `uuid.UUID` raises `AttributeError`, outside the caught exceptions. The middleware maps this to 500 instead of the documented invalid-identity 401.

Independent runtime result: Python **500**, Go **401**. No signing credentials were leaked; all tokens were synthetic. Relevant controls: B05/B06/B07; TC02/TC03/TC11.

Requested fix: validate the claim is a string before UUID normalization; reject wrong-type identity fields with safe 401. Add a shared malformed-claim regression with no writes.

### R3 — P2: supplied empty query limit is interpreted differently across bindings

Locations: `reference/go/main.go:180`, `reference/dotnet/CustomerApi/Program.cs:103`.

The contract specifies an optional integer `limit`. Go's `Query().Get` and .NET's `string.IsNullOrEmpty` treat supplied `?limit=` as absent and substitute 20. Python rejects the supplied non-integer value.

Independent runtime result: Python **400**, Go **200**. .NET's identical empty/default branch is established by inspection; exercise it in CI. Relevant controls: B04/B05; TC02/TC09.

Requested fix: distinguish missing query parameters from present empty values, and add a shared regression expecting safe 400. Preserve default 20 only when the parameter is absent.

## Nonblocking observation

### R4 — P3: Python oversized requests bypass correlation logging

Location: `reference/python/src/customer_api/main.py:98`.

The early 413 return precedes the common `X-Request-ID` assignment and structured request event. Independent oversized-body result: Python 413 with no correlation header; Go 413 with a header. This makes a useful failure path harder to investigate under B13. Route the rejection through the same response finalization/logging and extend the payload-cap case to inspect correlation. This is not a reason to weaken or remove the size cap.

## Acceptance boundary and next action

The trust limitations in the adoption/reference documents are material and accurately stated: a supplied JSON index cannot authenticate an agent or report, and policy/reviewer provenance must come from protected infrastructure. This review does not assert those external integrations are installed. No merge or deployment was performed.

Repair R1–R3, preferably R4 in the same focused correction, keep the criteria intact, obtain a new complete CI run tied to the new source/base/merge identities, and request independent re-review. This verdict does not carry forward to changed source or base revisions.

## Additional R1 contract reproduction

A second independent probe found the same request-contract equivalence gap for UUID syntax: sending the existing tenant UUID with all hyphens removed returned Python **201** but Go **400**. `jsonschema` with `FormatChecker()` rejects that value against this repository's `CreateCustomer` UUID format. Python's `tenant_id: UUID` conversion accepts several forms beyond the declared wire format. Keep canonical hyphenated UUID syntax (uppercase hex remains accepted/normalized as already specified), and add this case alongside the R1 strict-input regression. This extends R1's evidence rather than introducing a separate severity/count.

## Interim repair inspection (not final approval)

Inspected the implementing agent's uncommitted corrections and independently rebuilt Go from the repaired source. Repeated the real PostgreSQL/HTTP probes using the repaired Python source and fresh Go binary. Both now return: uppercase property 400, supplied empty limit 400, numeric tenant claim 401, hyphenless body UUID 400, oversized body 413 with `X-Request-ID` present. No approval is established for uncommitted source; final acceptance still requires immutable candidate identity and complete CI, especially .NET runtime coverage.

Recommended expanding the malformed-tenant claim fixture to a nonempty singleton array `[TENANT_A]`: .NET claim projection may flatten JSON arrays into string claims. This is a static concern awaiting runtime verification, not an independently observed .NET failure.
