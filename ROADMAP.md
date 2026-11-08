# Roadmap

Status as of 2026-11-08. A milestone is done only when its exit criterion is reproducible by
someone else.

| Milestone | Status | Exit criterion | Main work |
|---|---|---|---|
| **M0 — Reference** | in progress | Pi 4 XNU reference boots under QEMU; tvOS 16.6 IPSW extracts cleanly | QEMU `raspi4b`, IPSW tooling, ADT writer |
| **M1 — Hello UART** | in progress | `DarwinTV loader` banner on the Pi 5 debug UART | `bootloader/`, `configs/pi5/` |
| **M2 — XNU console** | in progress | XNU banner and `bsd_init` on the Pi 5 UART | payload packer/validator done; FDT, segment copy, boot_args, jump |
| **M3 — Interrupts** | planned | GICv2 timer and UART RX IRQs stable | GIC-400 driver, PPI 27, SPI attach |
| **M4 — Root** | planned | HFS+ root mounts; `launchd` starts | M4a RAM-disk root via U-Boot; M4b SDHCI + HFS+ persistent root |
| **M5 — PineBoard** | planned | tvOS home screen drawn at 1080p | IOSurface, IOMobileFramebuffer, HID, identity |
| **M6 — Long tail** | planned | usable input/network/GPU | RP1/PCIe, USB, BT, V3D |

## Deliberately deferred

- SMP (`cpus=1` first; PSCI + GIC SGIs later).
- High memory above 4 GB (the first boot caps the kernel window below the BCM2712
  peripheral hole).
- RP1 (USB, Ethernet, 40-pin GPIO).
- GPU acceleration (CPU rendering first).

## Non-goals

- Apple ID, iCloud, the App Store, activation servers.
- Distributing Apple firmware or userland.
