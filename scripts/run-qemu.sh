#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v qemu-system-aarch64 >/dev/null 2>&1; then
    echo "error: qemu-system-aarch64 not found" >&2
    echo "       Debian/Ubuntu: sudo apt-get install qemu-system-arm" >&2
    exit 1
fi

BOARD="${1:-qemu-raspi4b}"
make -C "$ROOT/bootloader" BOARD="$BOARD"

if [ "$BOARD" = "qemu-virt" ]; then
    exec qemu-system-aarch64 \
        -M virt,gic-version=2 -cpu cortex-a76 -smp 4 -m 2G \
        -kernel "$ROOT/bootloader/build/qemu-virt/loader.elf" \
        -serial stdio -display none -monitor none
fi

exec qemu-system-aarch64 \
    -M raspi4b \
    -kernel "$ROOT/bootloader/build/qemu-raspi4b/loader8.img" \
    -serial stdio \
    -display none \
    -monitor none
