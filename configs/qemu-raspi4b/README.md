# QEMU raspi4b

The same loader can be built for QEMU's `raspi4b` machine:

```sh
make loader BOARD=qemu-raspi4b
qemu-system-aarch64 \
  -M raspi4b \
  -kernel bootloader/build/qemu-raspi4b/loader8.img \
  -serial stdio \
  -display none \
  -monitor none
```

QEMU loads the raw image at `0x00080000` and exposes a PL011 at `0xfe201000`.
The loader prints the same banner with `board: qemu-raspi4b`.

If your QEMU refuses to start without a device tree, add a `bcm2711-rpi-4-b.dtb`
with `-dtb`; the M1 loader does not parse it, so any compatible Pi 4 DTB works
for the hello test.

`make qemu` wraps the commands above.
