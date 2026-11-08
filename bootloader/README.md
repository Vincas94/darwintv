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

## Next step (M2)

Replace the final `wfe` loop with:

1. parse the firmware FDT (`/memory`) passed in `x0`,
2. copy the XNU Mach-O to `0x02004000`,
3. build the ADT and `boot_args` behind the kernel,
4. jump to the XNU entry with `x0 = boot_args` at EL1.
