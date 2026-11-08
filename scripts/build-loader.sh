#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOARD="${1:-pi5}"

make -C "$ROOT/bootloader" BOARD="$BOARD"
echo "==> $ROOT/bootloader/build/$BOARD/loader8.img"
