#!/usr/bin/env bash
# Give Argo CD read-only access to the project deploy repositories in Forgejo.
#
# Stores a credential template for every repository under FORGEJO_URL. Use a
# Forgejo user that can only read deploy repositories (read:repository scope).
# The token is read from DEPLOY_READER_TOKEN and is never printed.
set -euo pipefail

FORGEJO_URL=${FORGEJO_URL:-http://forgejo-http.forgejo.svc.cluster.local:3000}
DEPLOY_READER=${DEPLOY_READER:-deploy-reader}
: "${DEPLOY_READER_TOKEN:?set DEPLOY_READER_TOKEN}"

kubectl -n argocd create secret generic forgejo-repo-creds \
  --from-literal=type=git \
  --from-literal=url="$FORGEJO_URL/" \
  --from-literal=username="$DEPLOY_READER" \
  --from-literal=password="$DEPLOY_READER_TOKEN" \
  --dry-run=client -o yaml |
  kubectl label --local -f - argocd.argoproj.io/secret-type=repo-creds -o yaml |
  kubectl apply -f - >/dev/null
echo "Argo CD can read $FORGEJO_URL/* as $DEPLOY_READER"
