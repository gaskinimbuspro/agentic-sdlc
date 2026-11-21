# GitOps rollout adoption

Extends [PL01–PL08](../operations/platform.md). Select a pinned Argo CD/Kubernetes version, deployment topology, controller service accounts, a reviewed deploy repository separate from the source repository, secret source, namespace and resource/network policies. Argo CD replaces Flux as the controller by decision of the product owner, so that workflows, CI and deployment share one Kubernetes platform; the cases below do not depend on the controller. Keep the authorized reconciliation identity separate from CI and contributor identities. Test with a disposable staging target before assigning production authority.

Build and verify an immutable OCI digest once. Commit the digest in reviewed desired configuration and pin the manifest source or record the exact resolved revision. Grant the controller only required rights for its application and source. Lock access to reconciliation and prune settings. Keep credentials out of manifests and retained traces.

For Argo CD Applications observe the synced revision (`status.sync.revision`), sync status, health status and the last operation's result, and confirm that automated sync, prune and self-heal settings match the approved policy. Run schema migrations as a `PreSync` hook Job so a failed migration stops the sync. Correlate the reconciler observation with workload rollout, the actual running digest and target identity. For a multi-platform OCI index, record and verify the permitted mapping from index digest to platform image digest. Execute a real business smoke check on the observed revision and pass its JUnit report through the [release gate](../operations/platform.md#release-evidence-verification).

Define maximum convergence time, soak/traffic thresholds, alert owners and stop conditions. Abort promotion on drift beyond the window, failed health or smoke, stale observations, unexpected digest or unusable evidence. Roll back via a reviewed revision and repeat target verification. For incompatible data changes use the separate [data recovery procedure](../operations/database.md).

| Case | Action and required evidence |
| --- | --- |
| GT01 | Promote the same tested digest to the isolated target. Record protected provenance, desired source revision and effective runtime image identity. |
| GT02 | Cause an authorized drift and demonstrate reconciliation within the bound. Verify desired/observed revision and capture the event and duration. |
| GT03 | Introduce a broken dependency or unhealthy rollout. Observe alerting and verify that no promotion occurs. |
| GT04 | Reject stale or wrong-target observation, changed digest and absent/failed smoke. Preserve the gate outputs. |
| GT05 | Revert a failing application rollout while honoring schema compatibility. Verify the recovered image and actual critical journey. |
| GT06 | Exercise an unprivileged change and a forbidden cross-namespace action against the approved access policy. Verify the controller and secret roles are scoped. |

Primary sources. [OpenGitOps principles](https://opengitops.dev/) · [Argo CD best practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/) (separate configuration repository) · [Argo CD resource hooks](https://argo-cd.readthedocs.io/en/stable/user-guide/resource_hooks/) · [Flux Kustomization specification](https://fluxcd.io/flux/components/kustomize/kustomizations/) (the earlier controller)

Our implementation of this profile for the work server, tried in a sandbox, is described in [platform/templates](../../platform/templates/README.md): one deploy repository per project, staging set by the release pipeline, prod changed only by a pull request the product owner approves and merges.
