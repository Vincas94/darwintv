# Architecture

## Design principles

1. **Fresh repository, pinned upstreams.** The project is not a fork of XNU or of another port.
   Apple's source is fetched at a tag; our changes live in `patches/`.
2. **Serial first, display later.** Every milestone must be observable on the 3-pin debug UART.
3. **QEMU before hardware.** The loader and kernel changes are exercised under QEMU `raspi4b`
   (and `virt` for generic ARM64) before touching the Pi 5.
4. **No Apple binaries in git.** IPSWs, kernelcaches, device trees and userland are fetched or
   extracted locally; `.gitignore` and CI enforce it.
5. **One logical change per patch.** Patches are reviewable and rebasable.

## Components

| Component | Responsibility | Milestone |
|---|---|---|
| `bootloader/` | EL3/EL2→EL1, PL011 console, FDT parse, ADT + `boot_args`, jump to XNU | M1–M2 |
| `patches/` | XNU board config, platform expert, GICv2, timer, PL011, SDHCI, stubs | M2–M5 |
| `tools/adt/` | Host-side Apple Device Tree writer, shared with tests | M1 |
| `tools/ipsw/` | List/extract local IPSW entries | M0 |
| `tools/rootfs/` | Build an HFS+ root from the tvOS `OS` DMG | M4 |
| `configs/pi5/` | `config.txt`, serial settings, wiring | M1 |
| `docs/` | Hardware facts, boot flow, tvOS notes, ADRs | all |

## Boot chain

```text
BCM2712 boot ROM
  └─ SPI EEPROM bootloader (rpi-eeprom)
      └─ reads config.txt from the FAT boot partition
          └─ loads kernel8.img at 0x200000, DTB address in x0
              └─ TF-A BL31 runs at EL3, drops to EL2
                  └─ DarwinTV bootloader
                      ├─ parks secondary cores
                      ├─ parses the firmware FDT (/memory)
                      ├─ copies the XNU Mach-O to 0x02000000 + 0x4000
                      ├─ writes the ADT and boot_args behind the kernel
                      └─ EL2 → EL1, x0 = boot_args, jump
                          └─ XNU → platform expert → bsd_init
```

## Memory layout (first boot)

| Region | Address | Notes |
|---|---|---|
| Loader | `0x00200000` | Pi 5 `kernel_address`; must end before `0x02000000` |
| XNU Mach-O | `0x02004000` | 16K header offset (`kernelHeaderOffset = 0x4000`) |
| ADT | after the kernel | page-aligned |
| `boot_args` | after the ADT | `topOfKernelData` = end |
| RAM window | `0x02000000` … min(RAM, 4 GB) | cap below the BCM2712 peripheral hole |
| Debug UART | `0x107d001000` | PL011, not RP1 |
| GIC-400 | `0x107fff9000` / `0x107fffa000` | GICD / GICC |
| microSD | `0x1000fff000` | SDHCI `sdio1` |

## Why the kernel window is capped

The BCM2712 `soc` block is mapped at `0x10_7c000000`, about 65.9 GiB — above the 16 GiB maximum
RAM (`0x4_0000_0000`), so it is not a RAM conflict. The first boot caps the kernel window at 4 GiB
as a conservative bring-up choice pending the firmware `/memory` dump; high memory is a later
patch. This is a `C` fact in `docs/facts.md`.

## Why not a fork

See [`docs/decisions/0001-fresh-repo.md`](docs/decisions/0001-fresh-repo.md).
