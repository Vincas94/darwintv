#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/build/netboot/darwintv}"
LOADER="$ROOT/bootloader/build/pi5/loader8.img"
PAYLOAD="${PAYLOAD:-$ROOT/build/payload.bin}"

if [ ! -f "$LOADER" ]; then
    echo "error: build the loader first: make loader BOARD=pi5" >&2
    exit 1
fi

mkdir -p "$OUT"
cp "$ROOT/configs/pi5/config-netboot.txt" "$OUT/config.txt"
cp "$LOADER" "$OUT/kernel8.img"

if [ -f "$PAYLOAD" ]; then
    cp "$PAYLOAD" "$OUT/payload.bin"
else
    echo "warning: no payload at $PAYLOAD yet (M2); the loader will still boot"
fi

chmod -R a+rX "$ROOT/build/netboot"
echo "==> TFTP tree: $ROOT/build/netboot"
echo "    serve it with tftpd-hpa from /srv/darwintv-tftp,"
echo "    or copy darwintv/ there."
