#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -d .venv ]; then
    # shellcheck disable=SC1091
    . .venv/bin/activate
fi

for tool in ruff pytest; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "error: $tool not found; run scripts/bootstrap.sh" >&2
        exit 1
    fi
done

ruff check .
ruff format --check .
pytest -q

if command -v shellcheck >/dev/null 2>&1; then
    shellcheck scripts/*.sh
fi

if command -v clang-format >/dev/null 2>&1; then
    clang-format --dry-run --Werror bootloader/src/*.c bootloader/include/*.h
fi

if command -v mkdocs >/dev/null 2>&1; then
    mkdocs build --strict
fi

echo "==> all checks passed"
