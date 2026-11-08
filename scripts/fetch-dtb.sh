#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/build/bcm2712-rpi-5-b.dtb}"
URL="https://raw.githubusercontent.com/raspberrypi/firmware/master/boot/bcm2712-rpi-5-b.dtb"
EXPECTED_BLOB="30c817961c891893003657bf6d9010f577cf8ebe"

mkdir -p "$(dirname "$OUT")"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

curl -fsSL "$URL" -o "$tmp"
got="$(git hash-object "$tmp")"
if [ "$got" != "$EXPECTED_BLOB" ]; then
    echo "error: DTB blob mismatch: $got != $EXPECTED_BLOB" >&2
    exit 1
fi
mv "$tmp" "$OUT"
trap - EXIT
echo "==> $OUT ($(stat -c%s "$OUT") bytes, blob $got)"
