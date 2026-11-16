# Production adoption standard v0.1

Apply the [backend](../backend/README.md), [UI](../ui/README.md), [operations](../operations/README.md) and [agent delivery](../agent-delivery/README.md) standards first. The profiles below define the additional decisions, rejection cases and environment evidence needed before production adoption.

| Profile ID | Binding | Prerequisite for acceptance |
| --- | --- | --- |
| `identity` | [OIDC, API authorization and browser sessions](identity.md) | Registered provider, HTTPS callback, measured session and key lifecycle, and tenant authorization evidence |
| `gitops` | [Flux and Kubernetes rollout](gitops.md) | Approved target, pinned controller, observed revisions and digests, and drift, failure and recovery drills |
| `github` | [GitHub App dispatch and task evidence](github.md) | Restricted app installation, durable delivery handling, write reconciliation and separately protected integration authorization |
| `accessibility` | [Manual accessibility and visual acceptance](accessibility.md) | Qualified evaluator, approved scope and environment matrix, dated observations and reviewed visual baselines |
| `remote` | [Remote operations and Hetzner pilot](../../docs/remote-execution.md) | Authorized disposable target, uninterrupted observation coverage, verified off-host restore and measured operating decision |

The release owner selects the applicable profiles and their authorized reviewers in protected policy before the run. Start with the [policy template](policy.template.json) and [evidence index template](evidence.template.json). Record exclusions in the project decision record with rationale and approval. A project adopting all five selects all five. CI and observers collect reports from the targets, the reviewers independently inspect the results, and the release owner obtains actual deployment authority.

## Evidence gate

Run `operations-standard adoption evidence.json --policy policy.json --reports /trusted/report-root`. The policy defines `candidate_sha` (40 lowercase hexadecimal characters), `environment`, `run_id`, and a nonempty `profiles` object mapping each selected profile ID to a stable authorized reviewer identity. The release owner issues a unique run ID before execution. The evidence index has a `reports` object mapping each selected profile to its `report` relative path and `sha256` digest in `sha256:…` form. Provide each profile exactly once.

Each protected report is a JSON object with `profile`, `candidate_sha`, `environment`, `run_id`, `operator`, `reviewer`, and `cases`. A case has an `id`, `status` equal to `passed` and a concrete `observation` describing the outcome and locating its evidence. Include every case in the selected profile's table and use distinct operator and reviewer identities. The `remote` report also has the [soak record](../../docs/remote-execution.md#soak-record), bound to a `remote_window` in the protected policy. A failed, skipped, blocked or missing case stays open until successful execution and review for the matching candidate. Redact secrets and personal data before applying retention policy.

The gate returns `consistent` with the selected profile IDs when identity, file digest, case coverage and the remote observation schedule match. Obtain the reports and reviewer identity from protected sources. A digest verifies bytes, while provenance and the actual truth of observations depend on trusted collectors and reviewers. For deployment additionally run the [release gate](../operations/platform.md#release-evidence-verification) against the observed target and smoke results.

The repository tests the evidence gate with synthetic records. Each profile gains operational acceptance on its authorized target from actual evidence.
