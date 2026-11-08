#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KERNEL="${1:-$ROOT/build/kernel.development.bcm2712}"
shift || true

if [ ! -f "$KERNEL" ]; then
    echo "error: kernel not found: $KERNEL" >&2
    echo "usage: $0 path/to/kernel.development.bcm2712 [pack options]" >&2
    exit 1
fi

cd "$ROOT"
PYTHONPATH="$ROOT" exec python3 -m tools.payload pack \
    --kernel "$KERNEL" \
    --out "$ROOT/build/payload.bin" \
    "$@"
