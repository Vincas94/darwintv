# AGENTS.md — instructions for AI coding agents

This file is the contract for AI-assisted work in DarwinTV. Read it before changing anything.

## Read first

1. `README.md`
2. `ARCHITECTURE.md`
3. `docs/hardware/pi5.md`
4. `docs/boot-flow.md`
5. `docs/decisions/`

## Hard rules

- **Never commit Apple binaries.** No IPSWs, DMGs, kernelcaches, IM4P/IM4P payloads, device
  trees, userland, keys or certificates. `third_party/xnu/` is fetched, not committed.
- **No activation/DRM circumvention.** Do not add code whose purpose is to impersonate an Apple
  device to Apple's servers.
- **Do not invent hardware facts.** Every address, IRQ or register claim must be traceable to
  `docs/hardware/pi5.md`, the Raspberry Pi DTS, a datasheet, or a captured serial log.
- **Do not break the patch model.** Kernel changes go in `patches/`, one logical change per
  patch, exported with `git format-patch`.
- **Do not run destructive commands on hardware.** No `dd` to a boot disk without an explicit
  human confirmation. No flashing, no EEPROM writes, no `rm -rf` on mounted volumes.
- **QEMU before hardware.** If a change cannot be tested under QEMU, say so and list the exact
  hardware test.

## Build and test

```sh
./scripts/bootstrap.sh
source .venv/bin/activate
make check
make loader BOARD=pi5
make loader BOARD=qemu-raspi4b
make qemu                 # needs qemu-system-aarch64
```

- `make check` must pass before proposing a PR.
- New host-side Python code needs a test in `tests/`.
- New C code must build with `-Wall -Wextra -Werror` and `clang-format`.

## Style

- C11, freestanding, tabs (8 columns), `clang-format` (`.clang-format`).
- AArch64 assembly: one instruction per line, comments explain the architectural state.
- Python 3.11+, type hints, `ruff` (`.ruff.toml` via `pyproject.toml`).
- Shell: `#!/usr/bin/env bash`, `set -euo pipefail`, `shellcheck` clean.
- Markdown: one sentence per line is welcome; keep links valid for `mkdocs --strict`.

## Documentation

- New architectural decision → add `docs/decisions/NNNN-title.md`.
- New hardware fact → add a row to `docs/hardware/pi5.md` with a source.
- New milestone/status change → update `ROADMAP.md` and `CHANGELOG.md`.

## PRs

- Conventional Commits, DCO sign-off (`git commit -s`).
- Describe the test environment: QEMU version, board revision, EEPROM version, serial log.
- Disclose AI tools used. You are responsible for every line.
- Keep PRs small and reviewable; do not mix refactors with behavior changes.

## When unsure

Ask. A wrong register address costs days of bring-up. A question costs minutes.
