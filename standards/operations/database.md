# Database lifecycle and PostgreSQL profile

Use the selected engine's actual constraints, transaction semantics and recovery mechanisms. The [backend rules](../backend/common.md) continue to govern application behavior. The following controls govern ownership and operation.

| ID | Required control | Owner and acceptance evidence |
| --- | --- | --- |
| DB01 | Register the data owner, writers/readers, classification, residency, retention/deletion and restore exceptions for each dataset. Follow deletion through replicas, exports and backup expiry. | Data owner and security reviewer approve inventory, access boundaries and retention/deletion drill. |
| DB02 | Version schema changes and review preconditions, lock duration, rewrite/backfill time and compatibility with both deployed versions. Use expand/migrate/contract when old and new software must coexist. | Database engineer runs migration on representative prior data. Prove old/new compatibility, preserved values, bounded interruption and a recovery/roll-forward path. |
| DB03 | Enforce integrity and ownership across concurrent writers. Define transaction scope, isolation, uniqueness, query/index budgets and ambiguous-commit policy. | Engineering runs real-engine contention and negative cases, verifies invariants and reviews plans using representative cardinality. |
| DB04 | Separate runtime, migrations, backup and restore authority. Bind network, TLS, credential rotation, privileges and access audit to the environment. | Platform/security verifies denied operations for each least-privilege identity and tests rotation/revocation. |
| DB05 | Record numeric RPO and RTO per system. Select logical, physical or point-in-time recovery against those targets. Encrypt backups, protect retention, preserve required keys/configuration and separate failure domains. | Data owner approves targets. Operations verifies backup/archival freshness, access controls, retention and alert routing. |
| DB06 | Restore in isolation on a schedule and after material changes. Verify artifact identity, recovery boundary, schema/migration history, constraints, representative rows and application behavior before promotion. | Operator records source, backup, target, scope, actual lost interval and elapsed recovery time. Independent reviewer compares measured results with targets. |
| DB07 | Monitor connection pressure, locks, query latency, storage, replication/archive lag and maintenance. Escalate according to owned thresholds and retain protected, redacted evidence. | Operations records measured thresholds, routing, runbook and a safe alert/recovery exercise. |
| DB08 | Reassess data restoration after destructive changes. Application rollback requires a compatible schema. Use separately authorized data recovery when rollback cannot restore correctness. | Release/data owners record stop conditions, compatible artifact, write fencing, recovery cutoff and post-recovery reconciliation. |

## PostgreSQL binding

- Pin the server and supported client versions and record extensions, roles/grants, database parameters and settings that a per-database archive does not cover. Reset runtime privileges from reviewed configuration where appropriate.
- A logical archive is suitable when restore time, acceptable data loss and supported object scope fit the target. Use a tested base-backup/WAL chain if the selected RPO needs point-in-time recovery. Measure both from backup selection through validated service recovery.
- Verify the archive and its manifest using trust rooted outside the source writer. Treat a restore as execution of SQL selected by the source and restore with bounded privileges into a disposable target first.
- The reference runs real `pg_dump` and `pg_restore` on two isolated database instances. It restores synthetic rows and migration history, exercises constraints, and requires a deliberately damaged archive to fail. Use the reference as a starting procedure for the adopting project's own recovery plan.

[PostgreSQL and migration sources](sources.md#database)
