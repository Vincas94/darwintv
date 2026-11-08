# ADR 0009 — Backport the BCM2712 work to the pinned XNU tag

- **Status:** accepted
- **Date:** 2026-11-08
- **Deciders:** DarwinTV maintainers

## Context

Apple's `xnu-8796.141.3` already ships a **BCM2837** board port:

- `pexpert/pexpert/arm64/BCM2837.h`
- `config/MASTER.arm64.bcm2837`
- `MACHINE_FLAGS_ARM64_BCM2837` and `SUPPORTED_ARM64_MACHINE_CONFIGS` in `makedefs/MakeInc.def`
- guards in `osfmk/arm64/start.s`, `osfmk/kern/startup.c`, `iokit/Kernel/IOStartIOKit.cpp`,
  `pexpert/arm/pe_serial.c`

This is the closest in-tree example of XNU on a non-Apple SoC with no Apple CPU registers and no
trust cache.

A newer prior-art branch, `tansanrao/xnu` **`xnu-on-pi`** (head `0c7ff382`, 2026-09-05), contains a
BCM2712 port (`MASTER.arm64.bcm2712`, `BCM2712.h`, `BCM2712PlatformExpert.cpp`,
`BCM2712InterruptController.cpp`, `BCM2712Serial.cpp`, `BCM2712CPU.cpp`,
`machine_routines_bcm2712.c`). It **diverges** from our pin: its merge base is `aca3bea`
(`xnu-8796.101.5`), 33 commits ahead and 2 behind `rel/xnu-8796`. It is not descended from
`xnu-8796.141.3`.

That branch also:

- uses a **4 KiB** granule and explicitly says not to define `__ARM_16K_PG__`;
- uses an **IOKit** interrupt controller (`BCM2712InterruptController.cpp`), not
  `pexpert/arm/pe_gicv2.c`.

The older `xnu-on-pi5` branch is still the RPI4 port (`RPI4.h`, `pe_gicv2.c`,
`MASTER.arm64.rpi4.MacOSX`).

## Decision

1. **Stay pinned to `xnu-8796.141.3`.** It is a tag, reproducible, and matches the tvOS 16.6
   generation. Do not repin to a moving research branch.
2. **Backport the BCM2712 work** from `xnu-on-pi` as a reference, not a cherry-pick. Each patch
   must be rebased onto the pin and reviewed against Apple's `BCM2837` precedent.
3. **Keep 16 KiB pages** (`__ARM_16K_PG__`) because the tvOS userland is laid out for 16 KiB.
   Do not reuse the prior art's 4 KiB VA layout; adapt its CPU/platform code instead.
4. **Interrupt path:** start with the pexpert **GICv2** path (`pe_gicv2.c`) for the timer and
   console, because it is the smallest path to a serial boot. Evaluate the IOKit
   `BCM2712InterruptController.cpp` for full SPI/userland support; record that choice in a later
   ADR or open question.
5. **Mirror only the BCM2837 guards the Pi 5 needs:** no trust cache, no RTC wait, timer routing
   before the MMU, and the serial path. The mini-UART guard is not needed (the Pi 5 has a PL011).

## Consequences

- The kernel remains reproducible at one tag.
- The BCM2712 port is a visible, reviewable patch series rather than a second fork.
- 16 KiB pages constrain the VA layout and bootstrap mapping; the prior art's 4 KiB code cannot
  be used verbatim.
- The first interrupt implementation is deliberately minimal; a second IOKit path may replace it
  later for userland drivers.
- The `xnu-on-pi` branch is a reference, not a dependency; if it moves, our patches do not.

## Alternatives considered

- **Repin to `xnu-on-pi` head:** rejected; moving branch, different base, 4 KiB, unrelated
  commits, no tvOS alignment.
- **Fork `xnu-on-pi` as the main tree:** rejected; same reasons, plus the loader/docs/tools would
  be hidden in a 175 MB tree.
- **Adopt 4 KiB pages:** rejected for tvOS; the userland is 16 KiB. A 4 KiB kernel would need a
  different userland or a page-size translation layer.
- **IOKit GIC first:** deferred; more complete but a larger first step than the timer/console
  path. Revisit when SDHCI/display IRQs land.
