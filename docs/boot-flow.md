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

The BCM2712 `soc` block at `0x10_7c000000` sits above 4 GB. On 8 GB/16 GB boards that address is
inside the physical RAM range, so the firmware reserves it. The first boot caps the kernel window
below 4 GB to keep `memSize` one contiguous range; high memory is a later patch.

## Why the loader is at 0x200000

The Pi 5 firmware's documented 64-bit load address is `0x200000`. The loader must end before
`0x02000000`, where the XNU Mach-O begins. The linker script asserts this.
