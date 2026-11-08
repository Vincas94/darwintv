# CI

## What CI does

| Workflow | Runs | Checks |
|---|---|---|
| `ci.yml` | push/PR | host tests, lint, docs, loader build for `pi5`, `qemu-raspi4b`, `qemu-virt`, and a QEMU `virt` smoke test with a synthetic payload (`raspi4b` is tested locally; Ubuntu 24.04 QEMU 8.2 does not expose it in the aarch64 binary) |
| `docs.yml` | push to `main` | MkDocs build + GitHub Pages deploy |
| `codeql.yml` | push/PR/weekly | Python CodeQL analysis |
| `scorecard.yml` | weekly | OpenSSF Scorecard |
| `xnu.yml` | manual | fetch XNU and apply `patches/` on Linux |

## What CI does **not** do

- It does not build XNU. That needs macOS/Xcode; see `docs/building-xnu.md`.
- It does not run on a Pi 5. Hardware tests are local or on a self-hosted runner.
- It does not download Apple IPSWs or userland.

## Adding a hardware job

A self-hosted runner can run the same loop as `docs/testing.md`:

```sh
make loader BOARD=pi5
make netboot
rsync -a build/netboot/darwintv/ /srv/darwintv-tftp/darwintv/
./scripts/power-cycle.sh
./scripts/serial-capture.sh
```

Keep the runner isolated, use a relay/smart plug with a known `POWER_CMD`, and never expose the
UART or TFTP server to the public internet.

## Local equivalents

```sh
make check
make loader BOARD=pi5
make loader BOARD=qemu-raspi4b
make loader BOARD=qemu-virt
make docs
make netboot
```

## Hardening

Actions are currently pinned to release tags. Pinning every `uses:` to a commit SHA is a
future hardening step; Dependabot keeps the tags current.
