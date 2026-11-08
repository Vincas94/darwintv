# Raspberry Pi 5 boot configuration

## 1. Wire the debug UART

The Pi 5 primary debug UART is **UART10**, a PL011 at `0x107d001000`, on the
3-pin JST-SH connector between the microHDMI ports. It is **3.3 V only**.

| Debug connector pin | Signal | USB-UART adapter |
|---|---|---|
| 1 | RX (into the Pi) | adapter **TX** |
| 2 | GND | adapter **GND** |
| 3 | TX (out of the Pi) | adapter **RX** |

Do **not** connect VCC. Use 115200 8N1:

```sh
picocom -b 115200 /dev/ttyUSB0
# or: minicom -b 115200 -D /dev/ttyUSB0
```

## 2. Show the firmware log

Edit the EEPROM config:

```sh
sudo rpi-eeprom-config --edit
# add: BOOT_UART=1
sudo reboot
```

`config.txt` also sets `uart_2ndstage=1`.

## 3. Copy the loader

```sh
make loader BOARD=pi5
sudo cp bootloader/build/pi5/loader8.img /media/$USER/bootfs/
sudo cp configs/pi5/config.txt /media/$USER/bootfs/config.txt
sync
```

Keep a backup of the original `config.txt` and the boot partition. The loader
does not write to the SD card; it only prints to the UART and spins.

## Expected output

```text
DarwinTV loader
board:  raspberry-pi-5
load:   0x00200000
uart:   0x107d001000
hello from the other side of the SoC
```

## If you see nothing

- Check the adapter is 3.3 V and TX/RX are crossed.
- Check the baud rate is 115200.
- Check `kernel=loader8.img` and `kernel_address=0x200000`.
- Try `BOOT_UART=1` and `uart_2ndstage=1` to see whether the firmware itself is talking.
- The 40-pin header UART is on RP1 and is not the debug UART; do not use it for
  this loader.

## Updating without reflashing

The boot partition is FAT32. To update the loader, copy `loader8.img`; to update the kernel, copy
`payload.bin` (see `configs/pi5/config-payload.txt`). The root filesystem lives on its own
partition and is updated with `rsync` or `bmaptool`. See [Updating images](../../docs/updates.md).
