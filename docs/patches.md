# XNU patch plan

The repository does not fork XNU. `scripts/fetch-xnu.sh` checks out `xnu-8796.141.3`, and
`scripts/apply-patches.sh` applies `patches/*.patch` in order. Each patch is one logical change.

## Proposed series

| # | Patch | Files | Depends on | Purpose |
|---|---|---|---|---|
| 0001 | BCM2712 board config | `makedefs/MakeInc.def`, `config/MASTER.arm64.bcm2712.MacOSX`, `pexpert/pexpert/arm64/BCM2712.h` | — | Based on Apple's `BCM2837`/`MASTER.arm64.bcm2837`; `-mcpu=cortex-a76`, 16K pages, non-PAC |
| 0002 | BCM2837-style guards | `osfmk/kern/startup.c`, `iokit/Kernel/IOStartIOKit.cpp`, `osfmk/arm64/start.s`, `pexpert/arm/pe_serial.c` | 0001 | Mirror only the guards the Pi 5 needs (no trust cache, no RTC, timer, serial) |
| 0003 | Platform expert | `iokit/Kernel/arm/BCM2712PlatformExpert.cpp`, `iokit/KernelConfigTables.cpp`, `iokit/conf/files.arm64` | 0001 | Match `brcm,bcm2712`, publish CPU/device nubs |
| 0004 | PL011 console | `pexpert/arm/pe_serial.c`, `pexpert/arm/pl011.h` | 0001 | Debug console at `0x107d001000` |
| 0005 | GICv2 | `pexpert/arm/pe_gicv2.c`, `pexpert/arm/protos.h`, config | 0001 | GICD/GICC, timer **INTID 27 (DT PPI 11)**, SPI attach |
| 0006 | Timer wiring | `osfmk/arm/arm_timer.c` and the FIQ path | 0005 | Architectural timer to rtclock |
| 0007 | Non-Apple arm64 | toolchain stubs, no PAC, no PPL/KTRR/CTRR, no Apple-internal headers | 0001 | Build and boot on A76 |
| 0008 | mockfs + static userland | `bsd/miscfs/mockfs/*`, build config | 0003 | First `launchd`/shell from RAM |
| 0009 | SDHCI | new `bsd/dev/arm64`/IOKit driver, ADT node | 0005 | microSD block device |
| 0010 | HFS+ | config + Apple's open-source HFS+ | 0009 | tvOS root mount |
| 0011 | Display | `MiniIOSurface`, `MiniIOMobileFramebuffer` (adapted) | 0003 | `backboardd`/`PineBoard` display |
| 0012 | HID | `IOHIDFamily` + UART-injected events | 0011 | Input for bring-up |
| 0013 | Security stubs | permissive AMFI/sandbox, `AppleKeyStore` stub | 0008 | Userland daemons start |

## Backport reference

The newer `tansanrao/xnu` branch **`xnu-on-pi`** (head `0c7ff382`) has a BCM2712 port. It is not
descended from our pin (merge base `xnu-8796.101.5`, 33 ahead / 2 behind), uses **4 KiB** pages,
and uses an **IOKit** GIC driver. Treat it as a reference for files and hardware sequencing, not
as a cherry-pick source. See [ADR 0009](decisions/0009-bcm2712-backport.md).

## Interrupt path

Start with the pexpert **GICv2** path from the Pi 4 work (`pe_gicv2.c`) for the timer and console.
The IOKit `BCM2712InterruptController.cpp` from `xnu-on-pi` is the alternative for full
SPI/userland support; record the choice in an ADR when SDHCI/display IRQs land.

The exact file names and order will change; the dependency order is the important part.

## Rules

- One logical change per patch; no mixed refactors.
- Export with `git -C third_party/xnu format-patch -1 --stdout > patches/NNNN-name.patch`.
- Name `NNNN-short-description.patch`.
- `scripts/apply-patches.sh` must apply the whole series to a fresh checkout.
- Patches derived from XNU are APSL-2.0; keep Apple's notices.
- Do not add a 175 MB XNU tree to git.
- If a patch changes a documented fact, update `docs/facts.md`.

## Validation

```sh
scripts/fetch-xnu.sh
scripts/apply-patches.sh
```

CI's `XNU patches` workflow does the same on Linux. A macOS build workflow is planned; see
`docs/building-xnu.md`.
