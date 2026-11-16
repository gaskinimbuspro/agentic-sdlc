# Backend test case matrix

The Planner selects applicable cases from requirements before coding; an Independent Reviewer checks high-risk coverage. Each selected case needs concrete input/setup, expected status/result, expected persisted side effects, expected forbidden side effects, and a report reference. Applicability is reviewed; the Implementer cannot declare a failing requirement N/A.

| Case | Scenario family | Minimum checks when applicable | Typical level |
| --- | --- | --- | --- |
| TC01 | Successful behavior | Correct response and intended persisted result, not only an HTTP success code | Unit + API/integration |
| TC02 | Invalid/boundary input | Missing/null/empty, min/max, invalid enum/encoding, malformed JSON, oversized data; no partial side effects | Unit + API |
| TC03 | Authentication | Missing, invalid, expired, or revoked credentials according to the selected mechanism | API/integration |
| TC04 | Authorization/isolation | Insufficient role; cross-user/tenant object access; list/filter/export leakage; supplied owner ID cannot grant authority | API + real data |
| TC05 | Invariants and precision | Invalid transitions, uniqueness, rounding/money/time-zone limits, domain invariants | Unit + real data where needed |
| TC06 | Atomicity | Failure after an intermediate write rolls back or follows the documented compensation policy | Real dependency integration |
| TC07 | Concurrency/idempotency | Duplicate delivery/request, concurrent update, idempotency-key conflict, and forbidden duplicate effects | Integration/concurrency |
| TC08 | Dependency failure | Timeout, cancellation, unavailable/malformed dependency response, exhausted bounded retry, cleanup | Unit + integration/contract |
| TC09 | Contract compatibility | Request/response/error schemas, protocol semantics, supported consumer/provider versions | Contract + app/API |
| TC10 | Schema evolution | Fresh installation, supported prior-version upgrade, data preservation, rolling compatibility if required | Migration integration |
| TC11 | Error/telemetry safety | Correct mapped errors and correlation; no stack/secret/PII leakage; expected telemetry emitted | API + logging/security checks |
| TC12 | Resource/performance limits | Pagination and payload bounds, query growth/N+1 risks, agreed latency/load budget in a defined environment | API + performance |
| TC13 | Lifecycle and artifact | Real packaged artifact starts, rejects invalid config, becomes ready appropriately, and shuts down safely | Acceptance/smoke |
| TC14 | Optional infrastructure | Cache invalidation/staleness; messaging duplicate/ack/order/poison behavior; other selected infrastructure guarantees | Relevant integration |

## Concrete acceptance example

Illustrative requirement: an authenticated user may create a customer only in their authorized tenant, and a failed create must not leave partial data. The product must settle duplicate/uniqueness semantics before readiness.

- A valid request returns the agreed response and creates exactly the intended tenant-scoped record.
- Missing required data returns the agreed validation error and creates no record.
- Missing credentials are rejected; another tenant's identifier does not bypass authorization.
- A simulated write failure leaves no unintended partial record or follows the agreed recovery mechanism.
- Duplicate/concurrent behavior matches the documented uniqueness/idempotency policy.

These are example cases, not requirements automatically imposed on every product. Tests must check response bodies and state changes/absence of changes. Authorization coverage follows OWASP's object-level access-control concerns. [S03](sources.md#s03).

## Test portfolio

Use focused unit tests for business behavior, real-boundary integration tests for data/dependencies, contract tests for agreements, and a small set of critical packaged-artifact journeys. Backend end-to-end journeys do not require a UI. Smoke is an early health check after packaging/deployment; it does not replace business acceptance. UI testing belongs to the [UI standard](../ui/testing.md).

Map each acceptance criterion to cases and actual tests. Do not force a fixed unit/integration/E2E percentage or treat high coverage as proof. [F06](sources.md#f06).
