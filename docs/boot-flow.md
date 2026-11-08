# Boot flow

## From power-on to XNU

```text
BCM2712 boot ROM
  └─ SPI EEPROM bootloader (rpi-eeprom)
      ├─ reads config.txt from the FAT boot partition
      ├─ loads kernel8.img / kernel_2712.img at 0x200000
      ├─ loads the DTB and passes its address in x0
      └─ TF-A BL31 armstub runs at EL3, drops to EL2
          └─ DarwinTV bootloader (EL2)
              ├─ parks secondary cores
              ├─ parses the firmware FDT (/memory)
              ├─ copies the XNU Mach-O to 0x02000000 + 0x4000
              ├─ builds the ADT and boot_args behind the kernel
              └─ EL2 → EL1, x0 = boot_args, jump
                  └─ XNU → platform expert → bsd_init
```

## `boot_args`

XNU arm64 expects a `struct boot_args` (Revision 2, Version 2) in `x0`, with the MMU and caches
off at EL1. The fields the loader must fill:

| Field | Value |
|---|---|
| `virtBase` | kernel link base (for example `0xfffffff006000000`) |
| `physBase` | kernel physical base (`0x02000000`) |
| `memSize` | usable RAM end minus `physBase` |
| `topOfKernelData` | end of ADT + `boot_args`, page-aligned |
| `deviceTreeP` | ADT virtual address (`virtBase + (adt_pa - physBase)`) |
| `deviceTreeLength` | ADT size |
| `CommandLine` | `debug=0xc serial=1 cpus=1 keepsyms=1 -noprogress` |
| `memSizeActual` | full RAM size |

## Apple Device Tree

XNU does **not** understand an FDT. The loader builds an ADT with:

```text
/device-tree
  /chosen
    dram-base, dram-size, boot-args, random-seed
    /memory-map
  /cpus/cpu0
    state = "running", reg, timebase-frequency, clock frequencies
    # timebase-frequency must come from CNTFRQ_EL0; the 54 MHz clk_osc in the
    # DTS is not the ARM generic timer frequency.
  /arm-io
    ranges = <0, 0x107c000000, 0x04000000>
    /uart0    compatible "arm,pl011", reg <0x001001000, 0x200>
    /gic      compatible "arm,gic-400", reg <4×u64>
    /timer    compatible "arm,armv8-timer", interrupts <1 11 0xf08>
  /defaults
    serial-device = 1
```

The host-side reference is `tools/adt/adt.py`. The real identity later copies `/product` from the
Apple TV's `DeviceTree.j42dap.im4p` so `MobileGestalt` and `PineBoard` see the right device.

## Memory layout

| Region | Address |
|---|---|
| Loader | `0x00200000` |
| XNU Mach-O | `0x02004000` (16K header offset) |
| ADT | after the kernel |
| `boot_args` | after the ADT |
| Kernel RAM window | `0x02000000` … min(RAM, 4 GB) |

The BCM2712 `soc` block at `0x10_7c000000` is about 65.9 GiB, well above the 16 GiB maximum RAM
(the 16 GiB end is `0x4_0000_0000`). It is not a RAM conflict. The first boot caps the kernel
window at 4 GiB as a conservative bring-up choice pending a dump of the firmware `/memory` and
`/reserved-memory` nodes. High-memory support is a later patch; the real reason for the cap is
marked `C` in `docs/facts.md`.

## Why the loader is at 0x200000

The Pi 5 firmware's documented 64-bit load address is `0x200000`. The loader must end before
`0x02000000`, where the XNU Mach-O begins. The linker script asserts this.


## Secondary cores

The loader parks secondary cores in a `wfe` loop before the EL drop. A core parked that way cannot
later be started by PSCI `CPU_ON`; it must be left in the state the firmware/TF-A expects, or
started by the kernel. On the Pi 5 the TF-A stub likely holds secondaries off, so this mainly
matters under QEMU. First boot uses `cpus=1`; SMP is a separate milestone (Q26 in
`docs/open-questions.md`).
