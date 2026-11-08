#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-${XNU_VERSION:-xnu-8796.141.3}}"
DEST="$ROOT/third_party/xnu"

mkdir -p "$ROOT/third_party"

if [ -d "$DEST/.git" ]; then
    echo "==> updating XNU in $DEST to $VERSION"
    git -C "$DEST" fetch --depth 1 origin "refs/tags/$VERSION:refs/tags/$VERSION" || true
    git -C "$DEST" checkout -q "$VERSION"
else
    echo "==> cloning XNU $VERSION"
    git clone --depth 1 --branch "$VERSION" \
        https://github.com/apple-oss-distributions/xnu.git "$DEST"
fi

echo "==> XNU at $DEST"
git -C "$DEST" describe --tags --always
