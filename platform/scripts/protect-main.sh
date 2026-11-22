#!/usr/bin/env bash
# Protect a project's main branch in Forgejo.
#
#   protect-main.sh OWNER/REPO
#
# - Nobody pushes to main directly; changes arrive by pull request.
# - The Woodpecker pull-request checks must pass (contexts ci/woodpecker/pr/<workflow>).
# - One approval from the product owner; stale approvals are dismissed on new commits.
# - Only the product owner may merge. Agents (Debora, the builder) never merge.
#
# Required: FORGEJO_ADMIN_PASSWORD. Optional: FORGEJO_URL, FORGEJO_ADMIN,
# PRODUCT_OWNER (default: FORGEJO_ADMIN), CHECK_WORKFLOWS (default: "checks plan").
set -euo pipefail

repo=${1:?usage: protect-main.sh OWNER/REPO}
FORGEJO_URL=${FORGEJO_URL:-http://forgejo-http.forgejo.svc.cluster.local:3000}
FORGEJO_ADMIN=${FORGEJO_ADMIN:-forge-admin}
PRODUCT_OWNER=${PRODUCT_OWNER:-$FORGEJO_ADMIN}
CHECK_WORKFLOWS=${CHECK_WORKFLOWS:-checks plan}
: "${FORGEJO_ADMIN_PASSWORD:?set FORGEJO_ADMIN_PASSWORD}"

rule=$(python3 -c '
import json, sys
owner, checks = sys.argv[1], sys.argv[2].split()
print(json.dumps({
    "rule_name": "main",
    "enable_push": False,
    "enable_status_check": True,
    "status_check_contexts": [f"ci/woodpecker/pr/{c}" for c in checks],
    "required_approvals": 1,
    "enable_approvals_whitelist": True,
    "approvals_whitelist_username": [owner],
    "enable_merge_whitelist": True,
    "merge_whitelist_usernames": [owner],
    "block_on_rejected_reviews": True,
    "block_on_outdated_branch": True,
    "dismiss_stale_approvals": True,
}))' "$PRODUCT_OWNER" "$CHECK_WORKFLOWS")

auth=(--silent --show-error --noproxy '*' --user "$FORGEJO_ADMIN:$FORGEJO_ADMIN_PASSWORD" -H 'Content-Type: application/json')
api="$FORGEJO_URL/api/v1/repos/$repo/branch_protections"
if curl "${auth[@]}" --fail "$api/main" >/dev/null 2>&1; then
  curl "${auth[@]}" --fail -X PATCH -d "$rule" "$api/main" >/dev/null
else
  curl "${auth[@]}" --fail -X POST -d "$rule" "$api" >/dev/null
fi
echo "main protected in $repo: checks ($CHECK_WORKFLOWS), approval and merge by $PRODUCT_OWNER"
