# Security and software supply chain

The security owner records the application/runtime trust boundaries and selects the relevant requirements from a pinned security baseline. Map applicability, mechanism, test/review evidence, owner and blocker to each requirement. Cite the actual requirement ID from the adopted publication when making a compliance claim.

| ID | Required control | Owner and acceptance evidence |
| --- | --- | --- |
| SEC01 | Maintain a threat model for identities, trust boundaries, data classes, abuse cases and privileged operations. Refresh it after design or risk changes. | Planner/security reviews misuse cases and maps mitigations to executable or manual verification. |
| SEC02 | Require least privilege, short-lived access where supported, server-side authorization and isolation across actors/tenants/environments. Manage secrets outside source, images and logs. | Security tests unauthorized and cross-boundary actions, secret rotation/revocation and redaction. |
| SEC03 | Lock dependencies and build tooling. Verify dependency sources, scan selected assets, record findings and SBOM where required, and remediate against a defined severity/risk policy. | CI preserves scanner/tool/input identity and actual findings. Test a known prohibited dependency or a controlled policy violation. |
| SEC04 | Isolate untrusted code from privileged runners, write-capable tokens, production identities and publish/sign steps. Pin reusable actions to full commits under reviewed workflows. | Platform checks effective permissions/triggers and shows an untrusted contribution cannot mutate trusted evidence or release state. |
| SEC05 | Use protected artifact provenance verification before promotion. Bind approved builder identity, source and artifact digest to the eligible environment. | Release controller validates trusted provenance and rejects wrong source, builder or digest. An artifact hash alone does not establish authorship. |
| SEC06 | Verify secure transport, sessions, configuration, input/output boundaries and error/log disclosure against the real application and environment. | Independent review and integration tests verify applicable controls under the adopted threat model. |
| SEC07 | Publish a vulnerability reporting channel and owned triage, remediation, disclosure and incident/recovery procedures. Document approved, time-limited exceptions. | Security checks routing and response, verifies remediation evidence and records expiry/compensating controls. |
| SEC08 | Protect the checks, accepted baseline and reviewer authority from the implementation identity. Retain minimally scoped evidence and keep the protected policy separate from worker claims. | Coordinator verifies provenance, candidate/base identity and independent approval, and rejects stale, missing or contested evidence. |

[Security sources](sources.md#platform-and-security)
