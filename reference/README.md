# Executable backend reference

This is a verification example for backend standard v0.1, not an application generator or production customer-management product. Python/FastAPI, Go/net-http, and C#/ASP.NET Core implement the same small contract and run against the same independently maintained acceptance suite and real PostgreSQL.

## Recorded architecture and behavior decisions

- Use one small service and Transaction Script. Domain input validation does not depend on HTTP or PostgreSQL. No CQRS, event sourcing, generic repository, cache or message broker is required by this example.
- Accept authenticated create/list operations. HS256 tokens are synthetic test credentials generated at runtime; issuer, audience, signature algorithm, expiration, tenant and scopes are validated. The application has no token-issuing endpoint. Production identity provider, key rotation/revocation and TLS require a project-specific binding; the test identity adapter is not a production IAM recommendation.
- Use only disposable loopback processes/databases. Database TLS is disabled for this local reference boundary. Production TLS/credential administration and backup/restore operations are not exercised here. Application database credentials use a separate role with only SELECT/INSERT on the two tables; migration/setup uses a distinct test administrator.
- Contract: [OpenAPI 3.1](openapi.json). Create returns 201; invalid input 400; invalid/missing credentials 401; denied tenant/scope 403; duplicate 409; oversized body 413; unavailable/timed-out persistence 503. Error bodies contain only safe Problem Details fields.
- Trim names and count at most 100 Unicode scalars; trim/lowercase ASCII email with a deliberately small documented email syntax and a 254-byte limit. This is a reference product decision, not a universal email-address validator. Email uniqueness is per tenant.
- Create customer and audit in one transaction. A duplicate race creates exactly one pair. The controlled second-write failure/deadline tests occur before commit and leave neither record. Connection loss during commit or a lost HTTP response can have an unknown outcome; atomicity does not prove that a reported transport failure left no complete transaction. Do not retry automatically; projects requiring retry must specify idempotency and outcome reconciliation.
- List only the token's tenant, ordered by ID, with default limit 20 and range 1..100. This example does not implement cursor pagination or other CRUD operations; projects must specify their own interface behavior.
- Bound body to 8192 bytes, database work to approximately 3 seconds, and test startup/shutdown. Liveness is process-local; readiness checks database availability. Functional timeout tests are not a throughput/SLO benchmark.
- SQL migrations are ordered, serialized by a transaction-level advisory lock, checksum checked and applied atomically. Tests exercise installation, upgrade preservation, rejected history changes and rollback of a failed migration. Production migration/recovery review remains mandatory.
- Runtime logs must not contain credentials, JWTs or customer bodies. Request correlation is visible; richer production metrics/tracing require a project decision.

## Supported bindings and commands

| Binding | Pinned inputs | Check entry point |
| --- | --- | --- |
| Python | Python 3.12.14, uv 0.12.23, FastAPI 0.163.1; runtime/dev dependencies in [uv.lock](python/uv.lock) | `uv run --no-sync python scripts/backend_verify.py python` |
| Go | Go 1.27.3; app/scanner module versions in [go.mod](go/go.mod) and [go.sum](go/go.sum) | `uv run --no-sync python scripts/backend_verify.py go` |
| .NET | SDK 10.0.404 without roll-forward; .NET runtime/auth package 10.0.15; NuGet lock files | `uv run --no-sync python scripts/backend_verify.py dotnet` |
| Database | PostgreSQL 18.7 official image pinned by digest in the acceptance runner | Same acceptance runner for each language |

From the repository root, install locked build/runtime tools first with `uv sync --locked --group dev --no-install-project`, then install the toolkit with `uv sync --locked --group dev --no-build-isolation`. For Python repeat these two commands with `--project reference/python`. Hatchling and its build dependencies are in the locks; package builds use `--no-build-isolation` so they do not silently resolve new build tools. Go/.NET checks require their selected SDK on PATH. Acceptance requires Docker access; the runner creates a random-password disposable PostgreSQL container, binds it to loopback and removes it in a finally block. It does not deploy to an existing cluster/server.

Run `uv run --no-sync backend-verify tools` for the standard's own code/document/rejection checks, or select `all` to run every profile. The `scripts/backend_verify.py` entry point forwards to the same packaged runner. An unavailable SDK, database, scanner or report returns nonzero. Independent jobs in [CI](../.github/workflows/backend.yml) use the same commands and upload per-profile results.

## Profiles and task packets

[Python](profiles/python.json), [Go](profiles/go.json) and [.NET](profiles/dotnet.json) are structurally complete reference profiles. They select this example's accepted scope, not arbitrary future production decisions. Multiple named obligations can point to one check group; run the aggregate once and preserve its individual results rather than executing the same acceptance suite repeatedly.

Validate a profile with `uv run --no-sync backend-standard profile reference/profiles/python.json`. Validate the illustrative [task packet](task-packet.json) with `uv run --no-sync backend-standard task reference/task-packet.json --profile reference/profiles/python.json`. The packet's historical base SHA and example budgets illustrate ready-stage inputs and must be replaced for real dispatch. Input validation cannot authenticate a decision-maker, prove a task is appropriately scoped, claim a task or start an agent.

## Test and evidence boundary

The acceptance suite starts a built/installed wheel, Go binary or published .NET assembly over actual HTTP. Assertions cover responses and persisted/forbidden effects, not only status codes. It also exercises concurrency, SQL injection as data, log redaction, database constraints, schema evolution, timeouts, liveness/readiness and invalid startup configuration. This is a reference portfolio, not proof that every behavior/risk of a future product is covered.

`artifacts/<profile>/results.json` records command outcomes, durations, test counts, report hashes, source SHA and dirty-worktree state. A local dirty run is useful feedback but not clean CI acceptance. `backend-standard evidence` only validates a supplied index against separately supplied policy/identities; it cannot turn arbitrary agent-authored files into trusted evidence. No check runner marks GitHub issues done, approves a review, merges or deploys.

The operator must obtain evidence from an appropriately isolated trusted runner, protect acceptance policy/check changes and verify independent review/integration. See [adoption](../standards/backend/adoption.md).

The standard's architecture gate protects the declared reference domain files against selected direct transport/data dependencies; it is not whole-program semantic analysis. New projects must bind their own module policy. The known-pattern secret scanner is a minimum control, not a guarantee of discovering every credential. Bandit blocks medium/high findings; dependency scanners reject all reported findings for this reference scope. These boundaries do not remove independent security/design review.
