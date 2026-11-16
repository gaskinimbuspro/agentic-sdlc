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

## Additions of 16 November 2026

Identified through search summaries on 16 November 2026. The network policy of the authoring session blocked these sites, so **the pages themselves were not opened in that session**. Inspect each page before a compliance or attribution claim relies on it. The entries above this heading were recorded earlier and are unchanged.

### Secure development updates

- NIST [SP 800-218A](https://csrc.nist.gov/pubs/sp/800/218/a/final), final July 2024. Community profile of the SSDF for generative AI and dual-use foundation models. Relevant where a project builds with or ships AI components.
- NIST [SSDF publications](https://csrc.nist.gov/projects/ssdf/publications). SP 800-218 Rev. 1 (SSDF v1.2) is listed as an initial public draft dated December 2025. The standard continues to cite the final v1.1 until a final revision is published and reviewed.

### Reliability and delivery

- Betsy Beyer, Chris Jones, Jennifer Petoff and Niall Richard Murphy (eds.), Google, [Site Reliability Engineering: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/). Indicators, objectives and their use in decisions. Informs RL01.
- Michael T. Nygard, *Release It!*, second edition (Pragmatic Bookshelf). Stability patterns including timeouts, circuit breaker and bulkheads. Informs RL02. The book was not read for this standard; only the published pattern names are used.
- OpenTelemetry, [Signals](https://opentelemetry.io/docs/concepts/signals/). Vendor-neutral traces, metrics and logs with context propagation. Informs RL03; selecting it is a project decision.
- Adam Wiggins, [The Twelve-Factor App](https://12factor.net/). Configuration in the environment, logs as event streams, disposability and build/release/run separation. Informs RL04.
- OWASP [CycloneDX](https://cyclonedx.org/specification/overview/) and Linux Foundation [SPDX](https://spdx.dev/). Bill-of-materials formats. Informs RL06; the format is a project choice.
- OpenSSF [Sigstore](https://docs.sigstore.dev/). Signing and verification of artifacts and attestations with identity-based keys. Informs RL06.

### Privacy and AI governance

- European Union, [General Data Protection Regulation](https://eur-lex.europa.eu/eli/reg/2016/679/oj). Principles including purpose limitation and data minimisation, and data-subject rights. Informs PV01, PV02 and PV04.
- Republic of Türkiye, Personal Data Protection Authority, [Law No. 6698 (KVKK)](https://www.kvkk.gov.tr/). The Turkish personal data protection law. Relevant to projects processing personal data in Türkiye.
- European Union, [Artificial Intelligence Act, Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj). Risk-based obligations for AI systems. Informs the classification question in PV05; classification is a legal determination.
- NIST, [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework), and ISO/IEC [42001](https://www.iso.org/standard/42001), AI management systems. Voluntary governance frameworks. Inform PV05.
