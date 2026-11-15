# Common backend rules

Scope: HTTP APIs, workers, and services. HTTP, storage, messaging, and tenant-specific rules apply only where relevant. The verification column specifies checks to implement in each project; it does not claim those application checks already exist here.

The [verification matrix](verification-matrix.md#common-backend-controls) expands B01-B18 into applicability, check/evidence, responsible gate, rejection examples and source links without changing their IDs or selecting a framework.

## Architecture basis

Separate transport/presentation, business behavior, and data access responsibilities. Their physical representation depends on the language and problem; no fixed number of folders, projects, or services is required. [F01](sources.md#f01).

Consider Transaction Script for simple use cases and Domain Model for behavior-rich domains. Select Repository when it provides a useful domain/data-mapping boundary. Do not introduce generic repositories, CQRS, event sourcing, or microservices automatically. [F02](sources.md#f02), [F03](sources.md#f03), [F04](sources.md#f04), [F09](sources.md#f09).

Use module boundaries that tooling can check where practical; folder names and reviewer discipline alone do not establish modularity. Simon Brown discusses component boundaries and compiler/build-time enforcement. Architecture decisions must record alternatives and consequences; Mark Richards' ADR lesson summary supports that practice. [A01](sources.md#a01), [A02](sources.md#a02).

## Rules

| ID | Requirement and scope | Project verification | Basis |
| --- | --- | --- | --- |
| B01 | Before implementation, record language, framework, versions, architecture decisions, and required checks. Incomplete/example values cannot establish readiness. | Profile/design review and task readiness check | Project policy |
| B02 | Keep meaningful business rules outside HTTP handlers/controllers. Keep SQL and external-service details behind declared data/integration boundaries. Make module dependencies explicit. | Transport-independent behavior tests and structural/dependency checks | F01, A01 |
| B03 | Organize modules around business capabilities. Justify domain logic patterns, Repository, and service boundaries. Avoid unused abstractions. | Architecture decisions and dependency review | F02–F04, F09; project policy |
| B04 | Define external inputs, outputs, failures, and compatibility. Use OpenAPI for HTTP APIs and an appropriate contract for other protocols. Define pagination, filtering, ordering, and resource limits. | API/contract tests and breaking-change checks | Project policy |
| B05 | Validate untrusted inputs at runtime. Static typing is not runtime validation. Protect business invariants beyond UI/transport validation. | Malformed, missing, oversized, boundary-value, and invariant tests | S02, P02 |
| B06 | Enforce identity and resource-level authorization in the backend. Isolate tenants where applicable. A supplied owner/tenant identifier is not authority. | Anonymous, insufficient-role, cross-user, and cross-tenant scenarios | S02, S03 |
| B07 | Preserve and map errors at the boundary. Default REST JSON APIs to RFC 9457 Problem Details. Do not disclose stack traces or sensitive internals. | Failure contract/status and disclosure tests | S01, S02; format selection is project policy |
| B08 | Define transaction/consistency boundaries where data persists. Use suitable data constraints. Specify duplicate and concurrent-operation behavior. | Real-engine rollback, constraint, duplicate, and concurrency tests | Project policy |
| B09 | Version schema changes as migrations. Test supported upgrades and deployment compatibility. Document rollback or forward recovery and data preservation. | Empty-database installation and previous-version migration tests | Project policy |
| B10 | Bound external I/O connection/operation time. Propagate cancellation where supported; clean resources within their lifetimes. | Timeout, cancellation, and cleanup scenarios | N03, N04, G06; generalized project policy |
| B11 | Retry only safe/idempotent operations or operations with a defined idempotency mechanism. Bound attempts/time/backoff and prevent duplicate side effects. | Transient failure, exhausted retry, and duplicate-operation tests | Project policy |
| B12 | Keep secrets and sensitive personal data out of source, fixtures, logs, and error bodies. Use parameterized/safe APIs rather than executing concatenated input. | Secret/static scanning and relevant injection/redaction tests | S02 |
| B13 | Provide structured logs and request/job correlation. Select metrics, tracing where needed, and measurable quality targets. | Controlled failure/telemetry inspection and target-based measurements | Project policy |
| B14 | Validate required configuration at startup. Separate test/production settings. Define precision/time-zone/conversion rules for relevant domains. | Invalid-startup and applicable domain boundary tests | Project policy |
| B15 | Record toolchain/dependency versions. Use locked restore in CI; verification must not silently upgrade dependencies. Select supported stable versions using current official support information. | Clean restore/build and lock/worktree diff checks | P03, P07, N06, G02, G03 |
| B16 | Define packaged artifact, startup/shutdown, and health/readiness semantics. Do not blindly tie process liveness to remote service health. | Packaged-artifact startup, safe smoke, and graceful shutdown | Project policy |
| B17 | Keep changes focused, understandable, and refactorable. Protect fixes with appropriate regression tests; avoid production abstractions needed only by mocks. | PR/regression review | F05, F09, G01 |
| B18 | Select dependency/security scanners, blocking policy, and time-bounded exceptions. Producing a report does not itself prove a security gate passed. | Demonstrate rejection of a blocking finding and preserve the actual report | S02; gate policy is a project choice |

## Project-specific decisions

Choose framework, persistence tools, authentication, pagination, migrations, telemetry, and deployment in the project profile. Simple CRUD does not automatically require a rich domain model; one service does not automatically require a queue, cache, or Kubernetes.
