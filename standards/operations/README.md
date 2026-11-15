# Operations and secure delivery standard v0.1

Adopt this standard alongside the [backend](../backend/README.md) and [UI](../ui/README.md) standards when a project stores data or ships artifacts into a managed environment. Record the adopted revision, applicable controls, owner, required evidence and independent acceptance authority for each environment.

| Domain | Standard | Reference evidence |
| --- | --- | --- |
| Database operations | [Database lifecycle and PostgreSQL profile](database.md) | Versioned migration history, engine constraints, real HTTP/PostgreSQL acceptance and an isolated logical restore drill |
| Platform and GitOps | [Platform delivery and recovery](platform.md) | Artifact identity, promotion/reconciliation decisions, observed revision and smoke evidence |
| Security | [Security and supply chain](security.md) | Threat/risk decisions, dependency and secret checks, provenance verification, isolation and negative tests |
| Sources | [Primary-source ledger](sources.md) | Version, applicability and limits of each cited reference |

Before implementation, resolve the environment inventory, data classification, recovery targets, release plan and authority. Before release, verify the built artifact and applicable controls against the current candidate. After rollout, verify the observed environment and critical behavior. A failing or unavailable required result blocks advancement. Record an approved exception with the affected control, scope, risk, compensating action, owner and expiry before relying on it.

The [recovery reference](../../reference/README.md#postgresql-restore-drill) uses synthetic data and disposable PostgreSQL. Production restore, point-in-time recovery, platform reconciliation, identity provider, TLS and cloud permissions require environment-specific drills and trusted evidence.
