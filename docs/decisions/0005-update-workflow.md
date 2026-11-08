# ADR 0005 — File-based updates, not reflashing

- **Status:** accepted
- **Date:** 2026-11-08

## Context

Bare-metal projects often assume the OS image is written to the boot medium with `dd` for every
change. That makes the edit/build/test loop slow and wears out SD cards. The Pi 5 firmware reads
`config.txt` and the kernel from a FAT32 partition as files, and can load an extra `ramfsfile` at
a fixed address.

## Decision

1. The boot partition is a normal FAT32 filesystem. The loader and the payload are files.
2. The loader stays stable; the XNU Mach-O, ADT and boot args live in a separate `payload.bin`.
3. The firmware loads `payload.bin` with `ramfsfile`/`ramfsaddr` (or `initramfs`).
4. The tvOS root lives on its own raw partition and is updated with `rsync`, `bmaptool` or sparse
   writes, never a full-card image.
5. Early bring-up may use a RAM-disk root packed into `payload.bin`; moving to SDHCI/HFS+ is M4.
6. A/B slots (`payload-a.bin`/`payload-b.bin`) plus `tryboot` or a loader `boot.cfg` provide a
   known-good fallback.
7. A serial XMODEM path is a stretch goal for no-card-removal kernel iterations.

## Consequences

- Kernel updates are single-file copies; root updates are incremental.
- The loader does not need a FAT driver at M1; the firmware loads the payload.
- If a firmware revision lacks `ramfsfile`, embed the payload in the loader or use U-Boot.
- The first-stage loader remains the only file that changes rarely, which keeps the recovery
  surface small.
