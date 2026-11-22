#!/usr/bin/env bash
# Connect Woodpecker (McCall) to Forgejo once both are installed.
#
# Creates a Forgejo OAuth2 application for Woodpecker and stores its client id
# and secret, and a gRPC signing secret, in the woodpecker-forgejo Secret that
# the Woodpecker server reads.
# Nothing secret is printed or written to Git. Run it again to rotate: the old
# application is deleted first.
#
# Required: kubectl access to the cluster and the Forgejo admin password in
# FORGEJO_ADMIN_PASSWORD (terraform output -raw forgejo_admin_password).
# Optional: FORGEJO_URL (default: the in-cluster service URL), FORGEJO_ADMIN,
# WOODPECKER_HOST (must match WOODPECKER_HOST in woodpecker.values.yaml).
set -euo pipefail

FORGEJO_URL=${FORGEJO_URL:-http://forgejo-http.forgejo.svc.cluster.local:3000}
FORGEJO_ADMIN=${FORGEJO_ADMIN:-forge-admin}
WOODPECKER_HOST=${WOODPECKER_HOST:-http://woodpecker-server.woodpecker.svc.cluster.local}
APP_NAME=woodpecker
: "${FORGEJO_ADMIN_PASSWORD:?set FORGEJO_ADMIN_PASSWORD}"

auth=(--silent --show-error --fail --noproxy '*' --user "$FORGEJO_ADMIN:$FORGEJO_ADMIN_PASSWORD")
api="$FORGEJO_URL/api/v1/user/applications/oauth2"

for id in $(curl "${auth[@]}" "$api?limit=50" |
  python3 -c "import json,sys; print(' '.join(str(a['id']) for a in json.load(sys.stdin) if a['name']=='$APP_NAME'))"); do
  curl "${auth[@]}" -X DELETE "$api/$id" >/dev/null
done

body=$(python3 -c "import json,sys; print(json.dumps({'name': '$APP_NAME', 'confidential_client': True, 'redirect_uris': [sys.argv[1] + '/authorize']}))" "$WOODPECKER_HOST")
created=$(curl "${auth[@]}" -X POST -H 'Content-Type: application/json' -d "$body" "$api")

client=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read())['client_id'])" <<<"$created")
secret=$(python3 -c "import json,sys; print(json.loads(sys.stdin.read())['client_secret'])" <<<"$created")

kubectl create namespace woodpecker --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl -n woodpecker create secret generic woodpecker-forgejo \
  --from-literal=WOODPECKER_FORGEJO_CLIENT="$client" \
  --from-literal=WOODPECKER_FORGEJO_SECRET="$secret" \
  --from-literal=WOODPECKER_GRPC_SECRET="$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl -n woodpecker rollout restart statefulset/woodpecker-server >/dev/null 2>&1 || true
echo "woodpecker-forgejo Secret written; OAuth redirect $WOODPECKER_HOST/authorize"
