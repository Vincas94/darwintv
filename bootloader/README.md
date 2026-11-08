# bootloader

The M1 loader: a freestanding AArch64 image that parks secondary cores, drops
EL3/EL2 to EL1, and prints a banner on the PL011 console.

| Board | `BOARD=` | Load address | UART |
|---|---|---|---|
| Raspberry Pi 5 | `pi5` | `0x00200000` | `0x107d001000` (UART10 debug connector) |
| QEMU `raspi4b` | `qemu-raspi4b` | `0x00080000` | `0xfe201000` (PL011) |
| QEMU `virt` | `qemu-virt` | `0x40000000` | `0x09000000` (PL011) |

```sh
make BOARD=pi5            # -> build/pi5/loader8.img
make BOARD=qemu-raspi4b   # -> build/qemu-raspi4b/loader8.img
make clean
```

The loader deliberately does **not** touch `IBRD`/`FBRD`: the firmware has
already configured 115200 8N1, and the BCM2712 UART reference clock is not yet
modelled here.

## Current M2 state

The loader now:

1. saves the firmware DTB pointer (`x0`) in `x19` and prints it,
2. validates `payload.bin` at `PAYLOAD_ADDR` (magic, version, bounds, CRC32),
3. prints the entry, bases, segments and command line,
4. spins.

Next:

1. parse `/memory` from the firmware FDT,
2. copy the payload segments to `phys_base + (vmaddr - virt_base)`,
3. build `boot_args` behind the ADT,
4. jump to the entry with `x0 = boot_args` at EL1.
