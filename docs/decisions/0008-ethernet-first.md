# ADR 0008 — Ethernet-first hardware loop

- **Status:** accepted
- **Date:** 2026-11-08

## Context

The Pi 5 and the build host are wired on the same Ethernet segment. The Pi 5 EEPROM bootloader
supports TFTP network boot (`BOOT_ORDER` mode `0x2`), and the board has a documented 3-pin UART.
A phone + fastboot alternative offers a faster raw pipe, but a much more complex platform:
unlock/AVB/anti-rollback, vendor boot chain, proprietary PMIC/interconnect/SMMU, hard power
cycling, and brick risk.

## Decision

1. **TFTP network boot is the primary Pi 5 hardware loop.** No SD writes, no card removal.
2. **UART is the console and the recovery channel**, not the normal image transport.
3. **A smart plug or USB relay** provides remote power cycling; `scripts/power-cycle.sh`.
4. **Serial capture + marker grep** is the pass/fail signal; `scripts/serial-capture.sh`.
5. The SD card is a fallback (`BOOT_ORDER=0xf12`) and, later, the persistent root.
6. Phone + fastboot remains a **reference** for the tvOS/iOS userland techniques, not the target.

## Consequences

- The hardware loop is seconds, not minutes, and can run unattended.
- The host is the source of truth for `config.txt`, `kernel8.img` and `payload.bin`.
- A self-hosted CI runner can build, sync the TFTP tree, power-cycle, capture and assert.
- The Pi 5's open boot chain and recovery make it the safer platform for solo bring-up.
