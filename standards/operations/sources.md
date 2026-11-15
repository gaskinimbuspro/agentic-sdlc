# Operations primary sources

The operational gates, IDs, thresholds and choice of a PostgreSQL reference are project policy. The sources provide mechanism definitions and guidance. An adopting project records its compliance scope and evidence separately.

## Database

- PostgreSQL Global Development Group, PostgreSQL 18 [Backup and Restore](https://www.postgresql.org/docs/18/backup.html). Covers logical dumps, physical backup and continuous archiving. A logical restore alone supplies no evidence about WAL retention or point-in-time recovery.
- PostgreSQL Global Development Group, PostgreSQL 18 [pg_restore](https://www.postgresql.org/docs/18/app-pgrestore.html). Defines restore behavior, error modes, archive scope and the source-code trust boundary.
- Pramod Sadalage and Martin Fowler, [Evolutionary Database Design](https://martinfowler.com/articles/evodb.html). Guidance for versioned migrations, automated verification and compatible evolution.

## Platform and security

- CNCF OpenGitOps [principles v1.0.0](https://opengitops.dev/). Defines declarative, versioned and immutable desired state, automatic pull and continuous reconciliation. Tool and rollout choice remain project decisions.
- NIST [SP 800-218, SSDF v1.1](https://csrc.nist.gov/pubs/sp/800/218/final). Secure-development practice guidance for the lifecycle and response to vulnerabilities.
- OWASP [Application Security Verification Standard](https://asvs.owasp.org/). Versioned verification requirements. Select exact requirement IDs and applicability for the project.
- OpenSSF [SLSA v1.2](https://slsa.dev/spec/v1.2/). Supply-chain assurance tracks and provenance terminology. Adopting selected provenance controls establishes no SLSA level.
