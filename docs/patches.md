# XNU patch plan

The repository does not fork XNU. `scripts/fetch-xnu.sh` checks out `xnu-8796.141.3`, and
`scripts/apply-patches.sh` applies `patches/*.patch` in order. Each patch is one logical change.

## Proposed series

| # | Patch | Files | Depends on | Purpose |
|---|---|---|---|---|
| 0001 | BCM2712 board config | `makedefs/MakeInc.def`, `config/MASTER.arm64.bcm2712.MacOSX`, `pexpert/pexpert/arm64/BCM2712.h` | — | `-mcpu=cortex-a76`, 16K pages, non-PAC, GICv2, PL011, timer |
| 0002 | Platform expert | `iokit/Kernel/arm/BCM2712PlatformExpert.cpp`, `iokit/KernelConfigTables.cpp`, `iokit/conf/files.arm64` | 0001 | Match `brcm,bcm2712`, publish CPU/device nubs |
| 0003 | PL011 console | `pexpert/arm/pe_serial.c`, `pexpert/arm/pl011.h` | 0001 | Debug console at `0x107d001000` |
| 0004 | GICv2 | `pexpert/arm/pe_gicv2.c`, `pexpert/arm/protos.h`, config | 0001 | GICD/GICC, timer PPI 27, SPI attach |
| 0005 | Timer wiring | `osfmk/arm/arm_timer.c` and the FIQ path | 0004 | Architectural timer to rtclock |
| 0006 | Non-Apple arm64 | toolchain stubs, no PAC, no PPL/KTRR/CTRR, no Apple-internal headers | 0001 | Build and boot on A76 |
| 0007 | mockfs + static userland | `bsd/miscfs/mockfs/*`, build config | 0002 | First `launchd`/shell from RAM |
| 0008 | SDHCI | new `bsd/dev/arm64`/IOKit driver, ADT node | 0004 | microSD block device |
| 0009 | HFS+ | config + Apple's open-source HFS+ | 0008 | tvOS root mount |
| 0010 | Display | `MiniIOSurface`, `MiniIOMobileFramebuffer` (adapted) | 0002 | `backboardd`/`PineBoard` display |
| 0011 | HID | `IOHIDFamily` + UART-injected events | 0010 | Input for bring-up |
| 0012 | Security stubs | permissive AMFI/sandbox, `AppleKeyStore` stub | 0007 | Userland daemons start |

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
