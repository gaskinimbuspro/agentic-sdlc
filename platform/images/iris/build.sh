#!/usr/bin/env bash
# Build the Debora step image from this repository's locked dependencies.
# Usage: platform/images/iris/build.sh [image-tag]
set -euo pipefail
tag="${1:-localhost/iris:0.1}"
root="$(git rev-parse --show-toplevel)"
ctx="$(mktemp -d)"
trap 'rm -rf "$ctx"' EXIT
mkdir "$ctx/wheels"
uv export --project "$root" --locked --no-dev --no-emit-project --format requirements-txt | sed -E "s/ ; python_full_version [^\\]*//" > "$ctx/requirements.txt"
uv build --project "$root" --wheel --no-build-isolation --out-dir "$ctx/wheels"
uv run --no-sync --project "$root" python -m pip download --quiet --only-binary=:all: \
  --python-version 3.12 --platform manylinux2014_x86_64 --platform manylinux_2_17_x86_64 \
  --dest "$ctx/wheels" -r "$ctx/requirements.txt"
cp "$root/platform/images/iris/Dockerfile" "$ctx/Dockerfile"
docker build --tag "$tag" "$ctx"
echo "built $tag"
