# ADR 0007 — Test pyramid, hardware smoke, UART as fallback

- **Status:** accepted
- **Date:** 2026-11-08

## Context

The UART can carry a 15 MB kernel in ~5.5 minutes at 460800, and a 3.6 GB root is not viable at
all. If every change required a full hardware boot over UART, the project would stall. Most bugs,
however, are in logic that QEMU or host tests can exercise in seconds.

## Decision

1. **L0 host tests** cover every host-side format and script.
2. **L1/L2 QEMU** covers the loader, GICv2, PL011, timer, ADT/`boot_args`, and early XNU.
3. **L3 real Pi 5** uses a file-based payload (FAT/SD/USB/NVMe/TFTP), not UART, and a **test mode**
   that stops at a marker.
4. **L4 driver work** is batched with persistent logs and a known-good slot.
5. **UART** is for recovery, no-card iterations, and compressed/delta payloads — not the primary
   kernel loop.
6. Hardware automation is a first-class goal: `flash-payload.sh`, `power-cycle.sh`,
   `serial-capture.sh`, and a self-hosted CI runner.

## Consequences

- Most changes test in milliseconds to seconds.
- Hardware boots are seconds, not minutes, because the payload is on a filesystem/network.
- A small amount of loader/kernel test-mode plumbing pays for itself quickly.
- The remaining slow paths are the XNU build and full tvOS integration; those are batched.
