#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAYLOAD="${1:-$ROOT/build/payload.bin}"
BOOT_MNT="${BOOT_MNT:-/mnt/pi5-boot}"

if [ ! -f "$PAYLOAD" ]; then
    echo "error: payload not found: $PAYLOAD" >&2
    exit 1
fi

if [ ! -d "$BOOT_MNT" ]; then
    echo "error: mount the Pi 5 boot partition at $BOOT_MNT first" >&2
    echo "       or set BOOT_MNT to the mount point" >&2
    exit 1
fi

cp "$PAYLOAD" "$BOOT_MNT/payload.bin"
sync
echo "==> copied $PAYLOAD -> $BOOT_MNT/payload.bin"
