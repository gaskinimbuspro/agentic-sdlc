#!/usr/bin/env bash
# Install a single-node k3s cluster for the platform. Run as root on the work server.
# The version is pinned and the binary is checked against the published checksum.
set -euo pipefail

K3S_VERSION="${K3S_VERSION:-v1.37.2+k3s1}"
DATA_DIR="${DATA_DIR:-/var/lib/rancher/k3s}"
KUBECONFIG_OUT="${KUBECONFIG_OUT:-/etc/rancher/k3s/k3s.yaml}"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
# Set only on hosts that still use cgroup v1, such as some sandboxes.
ALLOW_CGROUP_V1="${ALLOW_CGROUP_V1:-false}"
# Set only where the host forbids lowering oom_score_adj (CAP_SYS_RESOURCE missing).
RESTRICT_OOM_SCORE_ADJ="${RESTRICT_OOM_SCORE_ADJ:-false}"

url="https://github.com/k3s-io/k3s/releases/download/${K3S_VERSION/+/%2B}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
curl -fsSL -o "$tmp/k3s" "$url/k3s"
curl -fsSL -o "$tmp/sums" "$url/sha256sum-amd64.txt"
(cd "$tmp" && grep -E ' k3s$' sums | sha256sum -c -)
install -m 0755 "$tmp/k3s" "$BIN_DIR/k3s"

if [ "$RESTRICT_OOM_SCORE_ADJ" = "true" ]; then
  dropin="$DATA_DIR/agent/etc/containerd/config-v3.toml.d"
  mkdir -p "$dropin"
  printf "[plugins.'io.containerd.cri.v1.runtime']\n  restrict_oom_score_adj = true\n" > "$dropin/10-restrict-oom.toml"
fi

args=(server --disable traefik --data-dir "$DATA_DIR" --write-kubeconfig "$KUBECONFIG_OUT" --write-kubeconfig-mode 600)
if [ "$ALLOW_CGROUP_V1" = "true" ]; then
  args+=(--kubelet-arg=fail-cgroupv1=false)
fi

echo "Starting: $BIN_DIR/k3s ${args[*]}"
echo "On a server with systemd, run the same arguments from a unit file instead of in the foreground."
exec "$BIN_DIR/k3s" "${args[@]}"
