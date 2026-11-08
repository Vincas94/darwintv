# Review addendum — BCM2837 and the newer BCM2712 branch

*2026-11-08. This supplements the [initial survey](2026-11-08-initial-survey.md) after an external
review. All claims below were checked against the pinned Apple tag and the prior-art branches.*

## 1. Apple's XNU already has a Raspberry Pi board

The pinned tag **`xnu-8796.141.3`** ships a Raspberry Pi 3 (BCM2837) board port:

- `pexpert/pexpert/arm64/BCM2837.h`
- `config/MASTER.arm64.bcm2837`
- `MACHINE_FLAGS_ARM64_BCM2837` and `SUPPORTED_ARM64_MACHINE_CONFIGS` in
  `makedefs/MakeInc.def`
- `#ifdef BCM2837` guards in:
  - `osfmk/arm64/start.s` — timer routing before the MMU is enabled
  - `osfmk/kern/startup.c` — trust-cache init skipped
  - `iokit/Kernel/IOStartIOKit.cpp` — no RTC wait
  - `pexpert/arm/pe_serial.c` — mini UART

This is the closest in-tree example of XNU on a non-Apple SoC. The BCM2712 board config should be
based on it, not on a third-party RPi4 header. The serial path differs (PL011 vs mini UART), and
the Pi 5 needs its own GIC/timer wiring, but the guard pattern is directly applicable.

## 2. The newer prior art is `xnu-on-pi`, not `xnu-on-pi5`

`tansanrao/xnu` branch **`xnu-on-pi`** (head `0c7ff382`, 2026-09-05) contains a BCM2712 port:

- `config/MASTER.arm64.bcm2712`, `pexpert/pexpert/arm64/BCM2712.h`
- `iokit/Kernel/arm/BCM2712PlatformExpert.cpp`, `BCM2712InterruptController.cpp`,
  `BCM2712Serial.cpp`, `BCM2712CPU.cpp`
- `osfmk/arm64/machine_routines_bcm2712.c`, `bcm2712_interrupt.h`, `bcm2712_entropy.c`

It is **not** descended from `xnu-8796.141.3`: its merge base is `aca3bea`
(`xnu-8796.101.5`), 33 commits ahead / 2 behind `rel/xnu-8796`. It uses a **4 KiB** granule and an
**IOKit** interrupt controller. The older `xnu-on-pi5` branch is still the RPI4 port.

DarwinTV stays pinned to `xnu-8796.141.3` and treats this branch as a backport reference; see
[ADR 0009](../decisions/0009-bcm2712-backport.md).

## 3. Corrections to the initial survey

- The survey said `xnu-on-pi5` was "the intended Pi 5 line"; it is the older RPI4 line.
- The survey's `docs/tvos.md` claim that `xnu-on-pi` uses `xnu-8796.141.3` is not true of the
  newer branch.
- The survey's plan to copy an "RPi4/RPI4 config" from Apple's tree was wrong: Apple has BCM2837,
  not RPI4. The RPI4 files come from the third-party fork.
- The initial GIC plan assumed `pe_gicv2.c`; the newer branch uses an IOKit GIC driver. ADR 0009
  chooses the pexpert GICv2 path first and defers the IOKit path.
- The 54 MHz figure for the ARM generic timer is not in the DTS. The loader must read
  `CNTFRQ_EL0`; add a `C` fact and an open question.

## 4. What this changes in the plan

- `docs/building-xnu.md`: base the board config on Apple's BCM2837 files, then add BCM2712.
- `docs/patches.md`: add a BCM2837-style guards patch; keep GICv2 as the first path.
- `docs/facts.md`: record the BCM2837 support, the `xnu-on-pi` branch state and the 4 KiB/IOKit
  differences.
- `docs/open-questions.md`: add the backport, GIC-path and page-size questions.
