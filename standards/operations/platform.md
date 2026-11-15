# Platform delivery and GitOps

The release owner records the target, trusted build and review authorities, protected configuration source, deployment principal, candidate revision, immutable artifact digest, smoke/health criteria, stop conditions and recovery procedure. Separate test fixtures, preview workloads and production authority.

| ID | Required control | Owner and acceptance evidence |
| --- | --- | --- |
| PL01 | Build once from approved source and promote the same immutable artifact. Preserve provenance, candidate revision and dependency inputs. | CI publishes digest and protected evidence. Release verification rejects a substituted digest or provenance from an unauthorized builder. |
| PL02 | Keep desired environment configuration declarative and versioned. Record runtime inputs, network boundaries, resource limits, availability topology and secrets references. | Platform review and environment validation show the selected target, configuration and identity boundaries are valid. |
| PL03 | For GitOps, use immutable desired revisions, automatic pull and reconciliation. Record controller identity, drift ownership and alerting, and time bounds for observable convergence. | Platform exercises an allowed change, drift and reconciliation failure. Evidence records the observed revision, artifact and workload health. |
| PL04 | Promote through authorized environments with scoped identities and explicit target policy. Review migrations and readiness before shifting traffic. | Release controller records target, allowed transition, actual candidate identity and decision. Privileged actions are isolated from untrusted changes. |
| PL05 | Verify the effective revision, running artifact and a critical business journey. Define checks for failure, elapsed time and traffic/error thresholds. | Release CI observes health plus meaningful smoke checks with safe synthetic input and cleans up test effects. Failure stops promotion. |
| PL06 | Exercise rollout failure and application rollback/roll-forward under the actual schema compatibility plan. Fence writes before incompatible data recovery. | Operator demonstrates abort/recovery, verifies effective revision and business behavior, and records timings. See [DB08](database.md). |
| PL07 | Set service and release objectives with actionable monitoring and on-call ownership. Track deployment events, error rates, latency, saturation and recovery. | Operations maps alerts to runbooks, captures redacted evidence and exercises a representative incident. |
| PL08 | Provision through reviewed IaC, detect drift and reconstruct non-secret configuration. Bootstrap release/reconciliation identities with least privilege. | Platform validates plans, privileges, repeatability and reconstruction in an isolated environment. |

A pull request merge is source integration. A release additionally requires evidence from the target environment. A reconciliation controller reporting a healthy deployment must be paired with current identity and behavior evidence for PL05. For an environment using a push-based deployment, apply the other platform controls and record GitOps as inapplicable.

[GitOps and supply-chain sources](sources.md#platform-and-security)

## Release evidence verification

Run `uv run --no-sync operations-standard release evidence.json --policy policy.json --reports /trusted/report-root` after collecting the policy and observations through protected channels. The JSON policy has `environment`, `source_sha`, `desired_revision`, `artifact_digest` (with `sha256:` prefix), `builder`, `deployer`, a unique `rollout_id` per execution, and `required_smoke_cases` (a list of JUnit case names).

The evidence contains three objects. Include the named fields and observed statuses below.

| Record | Required identity and status |
| --- | --- |
| `build` | `builder`, `source_sha`, `artifact_digest`, status `verified` after trusted provenance verification |
| `observed` | `deployer`, `environment`, `desired_revision`, `artifact_digest`, `rollout_id`, status `healthy` from the target observer |
| `smoke` | `environment`, `desired_revision`, `artifact_digest`, `rollout_id`, status `passed`, report path relative to the report root, and `report_digest` with `sha256:` prefix |

The verifier compares record identities, hashes the smoke report and checks case names and actual results. `consistent` means the supplied records satisfy these checks. Protect the policy, authenticate the build and deployment observations, and collect smoke results from the actual environment before relying on that verdict.
