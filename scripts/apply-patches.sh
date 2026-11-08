#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
XNU="$ROOT/third_party/xnu"

if [ ! -d "$XNU/.git" ]; then
    echo "error: $XNU is missing; run scripts/fetch-xnu.sh first" >&2
    exit 1
fi

shopt -s nullglob
patches=("$ROOT"/patches/*.patch)

if [ "${#patches[@]}" -eq 0 ]; then
    echo "==> no patches in patches/ yet"
    exit 0
fi

for patch in "${patches[@]}"; do
    echo "==> $(basename "$patch")"
    if git -C "$XNU" apply --reverse --check "$patch" >/dev/null 2>&1; then
        echo "    already applied; skipping"
        continue
    fi
    git -C "$XNU" apply --check "$patch"
    git -C "$XNU" apply "$patch"
done

echo "==> all patches applied"
