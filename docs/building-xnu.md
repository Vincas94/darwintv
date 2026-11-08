# Building XNU

!!! warning "Status"
    This repository has not built XNU yet. This page is the intended procedure, based on the
    `xnu-on-pi`, `ios-sweet`, and HakiOS workflows. Treat every command as **planned**, not
    verified in this repo.

## Why macOS

Apple's XNU build requires Xcode, Apple clang, the macOS SDK and Apple's build tools. It does not
build on Linux. The practical options are:

1. **GitHub Actions macOS runner** — free for public repositories, ~10–20 minutes per kernel
   build. This is the recommended starting point.
2. **A self-hosted Mac or Mac mini** — faster iteration, cacheable object tree.
3. **A macOS VM** — check Apple's licensing; not recommended as the primary path.

## Pin

```text
xnu-8796.141.3
```

This is the iOS 16.6 generation and the closest open-source match for tvOS 16.6. See
`docs/decisions/0003-target-appletv5-3-tvos-16.md`.

## Step 1 — fetch and patch

```sh
scripts/fetch-xnu.sh          # third_party/xnu at the pinned tag
scripts/apply-patches.sh      # patches/ in order
```

`third_party/xnu` is gitignored. Patches are APSL-2.0; keep Apple's notices.

## Step 2 — add the BCM2712 board config

**Base it on Apple's in-tree BCM2837 port, not on a third-party RPi4 header.** The pinned tag
already has:

- `pexpert/pexpert/arm64/BCM2837.h`
- `config/MASTER.arm64.bcm2837`
- `MACHINE_FLAGS_ARM64_BCM2837` and `SUPPORTED_ARM64_MACHINE_CONFIGS` in `makedefs/MakeInc.def`
- `#ifdef BCM2837` guards in `osfmk/arm64/start.s`, `osfmk/kern/startup.c`,
  `iokit/Kernel/IOStartIOKit.cpp` and `pexpert/arm/pe_serial.c`

That is the only in-tree example of XNU on a non-Apple SoC. For BCM2712:

- `makedefs/MakeInc.def`: `MACHINE_FLAGS_ARM64_BCM2712 = -DARM64_BOARD_CONFIG_BCM2712 -mcpu=cortex-a76`
- `SUPPORTED_ARM64_MACHINE_CONFIGS` += `BCM2712`
- `pexpert/pexpert/arm64/BCM2712.h`: `__ARM_16K_PG__`, `HAS_GIC_V2`, `PL011_UART`,
  `ARM_ARCH_TIMER`, `NO_MONITOR`; keep `BCM2712_UP_ONLY` for the first boot
- `config/MASTER.arm64.bcm2712.MacOSX`: derive from `MASTER.arm64.bcm2837`, add `mockfs` and the
  BCM2712 memory/IRQ settings
- `iokit/Kernel/arm/BCM2712PlatformExpert.cpp`
- `pexpert/arm/pe_gicv2.c` (from the Pi 4 work) and the timer wiring
- `pexpert/arm/pe_serial.c` PL011 path

### The newer BCM2712 reference branch

`tansanrao/xnu` branch **`xnu-on-pi`** (head `0c7ff382`, 2026-09-05) already contains a BCM2712
port. It is a **backport reference**, not a base:

- its merge base is `xnu-8796.101.5`, not our `xnu-8796.141.3` tag (33 ahead / 2 behind);
- it uses a **4 KiB** granule and an **IOKit** GIC driver;
- we keep **16 KiB** pages for tvOS and start with the pexpert GICv2 path.

See [ADR 0009](decisions/0009-bcm2712-backport.md). Do not cherry-pick it wholesale.

### BCM2837 guards to evaluate

| Guard | Pi 5 need |
|---|---|
| `startup.c`: skip trust-cache init | likely yes (no trust cache) |
| `IOStartIOKit.cpp`: no RTC wait | likely yes (no RTC) |
| `start.s`: timer routing before MMU | adapt to BCM2712/GIC |
| `pe_serial.c`: mini UART | no — Pi 5 has a PL011 |

## Step 3 — build on a macOS runner

Use the `blacktop/darwin-xnu-build` workflow pattern used by the reference projects:

1. Fork the repository.
2. Add a workflow that fetches `xnu-8796.141.3`, applies `patches/`, and invokes the XNU build.
3. Run it manually (`workflow_dispatch`) or on a tag.
4. Download the `kernel.development.*` / `kernel.release.*` artifact.

The exact workflow is intentionally not committed yet: it needs the first patch to be meaningful,
and a failing workflow is worse than no workflow. `.github/workflows/xnu.yml` currently only
validates that the patch series applies on Linux.

## Step 4 — pack a payload

The loader expects a `payload.bin`:

```text
header (128 B: magic, version, totals, entry, virt/phys base, mem size,
        ADT/cmdline offsets, nsegs, CRC32)
segment table (nsegs × 40 B)
ADT (aligned 16)
command line (aligned 16, NUL-terminated)
segment data (aligned 16)
```

`tools/payload` is implemented and tested:

```sh
scripts/mkpayload.sh path/to/kernel.development.bcm2712
# or:
python -m tools.payload pack --kernel ... --out build/payload.bin
python -m tools.payload info build/payload.bin
```

The loader validates the magic/CRC, prints the payload, and (next M2 step) copies the segments to
`0x02004000`, builds `boot_args`, and jumps.

## Step 5 — boot

- QEMU `raspi4b`/`virt` first.
- Pi 5 via TFTP (`docs/network-boot.md`) or FAT (`docs/updates.md`).
- Boot args: `debug=0xc serial=1 cpus=1 keepsyms=1 -noprogress`.
- Success: XNU banner, platform expert, `bsd_init`, then a root or a panic with a useful log.

## Build-time tips

- Cache `BUILD/obj` between CI runs.
- Build only the kernel target, not the whole SDK.
- Use `ccache` if the runner supports it.
- Keep host-tool changes out of the XNU rebuild path.
- A self-hosted Mac is worth it once you are changing kernel code daily.

## Known unknowns

- Whether the first patch series needs the `iokitcpp`/`libkerncpp` pieces exactly as the phone
  ports use them.
- The exact `MACHINE_FLAGS` and `config/MASTER` entries for a 16K-page, non-PAC BCM2712 target.
- Whether XNU's `arm_vm_init` accepts the Pi 5 memory map without a high-memory patch.
