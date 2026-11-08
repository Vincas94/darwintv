# ADR 0004 — QEMU before hardware

- **Status:** accepted
- **Date:** 2026-11-08

## Context

Bare-metal bring-up is slow to debug: a wrong register or a missing cache maintenance operation
can hang the board with no output. QEMU can run the loader and the kernel in seconds, and can
expose a GIC-400/PL011 environment close enough to the Pi 5 for early work.

## Decision

- Every loader/kernel change must first run under **QEMU `raspi4b`** (BCM2711, GIC-400, PL011)
  or `virt` with a GICv2.
- The loader has two build targets: `BOARD=pi5` (real hardware) and `BOARD=qemu-raspi4b`.
- The M1 hello loader is the first QEMU smoke test; later milestones add QEMU kernel tests.
- Real-hardware testing is still required for anything QEMU cannot model (SDHCI quirks, firmware
  framebuffer, RP1).

## Consequences

- Most bugs are caught before touching the Pi.
- QEMU `raspi4b` is not BCM2712; addresses and page size differ. The `pi5` target remains the
  source of truth, and every hardware fact is documented in `docs/hardware/pi5.md`.
