# GitHub App dispatch adoption

Extends the [GitHub operation contract](../agent-delivery/README.md#github-operation-contract). Bind numeric app installation and repository IDs, exact GitHub host/API version, reviewed branch, event allowlist and least privileges for each lane. Keep dispatch, deployment and integration roles separate. Mint installation tokens for the allowed repositories and permission set; use returned expiry and treat token format as opaque. Keep the app signing key out of workers, payload logs and CI artifacts.

Validate the HMAC-SHA256 signature of the untouched request body with a constant-time comparison before parsing or queueing. Limit body size and validate the signed installation/repository identities against policy. Bind the expected event and action to allowed payload shapes and confirm current resource state with the GitHub API before taking action. Webhook headers help route and deduplicate messages. A body HMAC cannot authenticate a caller-supplied replacement delivery header.

Record the delivery ID and payload digest in a durable inbox before returning success. An identical delivery can reuse the receipt. Reject a conflicting digest for the same delivery ID. Use a resource/operation key independent of the delivery header to prevent header substitution from producing a second external write. Reconcile ambiguous creates through authoritative reads and the [intent ledger](../agent-delivery/README.md#executable-reference). Keep preview or untrusted jobs away from privileged runners and write credentials.

| Case | Action and required evidence |
| --- | --- |
| GH01 | Exercise allowed installation and repo scopes, token expiry and forbidden writes. Record provider results for each lane. |
| GH02 | Reject tampered body, missing/wrong signature, and signed but unapproved installation or repository. Verify no durable eligible task is created. |
| GH03 | Redeliver signed content, replay it with a replaced delivery header and send a conflicting payload for the same delivery ID. Verify one effective operation and a conflict record. |
| GH04 | Interrupt processing before and after acknowledgement. Restart and prove fenced, durable claims and current-resource reconciliation. |
| GH05 | Lose the response to an issue or PR write. Verify authoritative readback and one retained provider resource ID, including a denied ambiguous retry. |
| GH06 | Attempt to advance a stale, failed, skipped or unreviewed candidate, and try from an untrusted job. Confirm protected CI and independent review control integration. |

Primary sources. [Installation tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app) · [Validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries) · [Webhook practices](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)
