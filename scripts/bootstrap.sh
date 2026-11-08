#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> DarwinTV bootstrap"

if command -v apt-get >/dev/null 2>&1; then
    SUDO=""
    if [ "$(id -u)" -ne 0 ]; then
        SUDO="sudo"
    fi
    $SUDO apt-get update
    $SUDO apt-get install -y \
        build-essential \
        clang-format \
        shellcheck \
        gcc-aarch64-linux-gnu \
        binutils-aarch64-linux-gnu \
        qemu-system-arm \
        device-tree-compiler
else
    echo "!! apt-get not found; install an AArch64 cross compiler and QEMU manually."
fi

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

if command -v pre-commit >/dev/null 2>&1; then
    pre-commit install || true
fi

echo "==> done"
echo "    source .venv/bin/activate"
echo "    make check"
echo "    make loader BOARD=pi5"
