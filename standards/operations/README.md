# Operations and secure delivery standard v0.1

Adopt this standard alongside the [backend](../backend/README.md) and [UI](../ui/README.md) standards when a project stores data or ships artifacts into a managed environment. Record the adopted revision, applicable controls, owner, required evidence and independent acceptance authority for each environment.

| Domain | Standard | Reference evidence |
| --- | --- | --- |
| Database operations | [Database lifecycle and PostgreSQL profile](database.md) | Versioned migration history, engine constraints, real HTTP/PostgreSQL acceptance and an isolated logical restore drill |
| Schema design | [Relational schema design](schema-design.md) | DD01–DD20; a static lint for part of it, shown against the reference migrations |
| Platform and GitOps | [Platform delivery and recovery](platform.md) | Artifact identity, promotion/reconciliation decisions, observed revision and smoke evidence |
| Security | [Security and supply chain](security.md) | Threat/risk decisions, dependency and secret checks, provenance verification, isolation and negative tests |
| Reliability | [Reliability, telemetry and progressive delivery](reliability.md) | Specified controls RL01–RL06; not exercised by the reference |
| Personal data and AI use | [Personal data and AI use](privacy.md) | Specified controls PV01–PV05; legal applicability is a project determination |
| Sources | [Primary-source ledger](sources.md) | Version, applicability and limits of each cited reference |

Use the [production adoption profiles](../adoption/README.md) for environment-specific identity, GitOps and remote acceptance.

Before implementation, resolve the environment inventory, data classification, recovery targets, release plan and authority. Before release, verify the built artifact and applicable controls against the current candidate. After rollout, verify the observed environment and critical behavior. A failing or unavailable required result blocks advancement. Record an approved exception with the affected control, scope, risk, compensating action, owner and expiry before relying on it.

The [recovery reference](../../reference/README.md#postgresql-restore-drill) uses synthetic data and disposable PostgreSQL. Production restore, point-in-time recovery, platform reconciliation, identity provider, TLS and cloud permissions require environment-specific drills and trusted evidence.
