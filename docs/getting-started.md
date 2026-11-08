# Getting started

## Prerequisites

- A Raspberry Pi 5 (4 GB is enough for the serial milestones; 8 GB is comfortable later).
- A **3.3 V** USB-to-UART adapter and a **3-pin JST-SH** cable for the Pi 5 debug connector.
- A Linux host (or the provided devcontainer) with Python 3.11+.
- Optional: a second SD card you can erase.

## 1. Bootstrap the host

```sh
git clone https://github.com/Vincas94/darwintv.git
cd darwintv
./scripts/bootstrap.sh
source .venv/bin/activate
```

This installs the AArch64 cross compiler, QEMU (where available), `clang-format`,
`shellcheck`, Python dev dependencies and pre-commit hooks.

## 2. Build the M1 loader

```sh
make loader BOARD=pi5
# -> bootloader/build/pi5/loader8.img
```

The loader is a freestanding AArch64 image linked at `0x00200000`. It parks secondary cores,
drops EL3/EL2 to EL1, initializes the PL011 and prints a banner.

## 3. Wire the serial console

See [Raspberry Pi 5 hardware](hardware/pi5.md). The short version:

| Debug connector | Adapter |
|---|---|
| pin 1 RX | adapter TX |
| pin 2 GND | adapter GND |
| pin 3 TX | adapter RX |

**3.3 V only. Do not connect VCC.** 115200 8N1.

```sh
picocom -b 115200 /dev/ttyACM0
```

## 4. Boot the Pi 5

Back up the boot partition, then copy:

```sh
sudo cp bootloader/build/pi5/loader8.img /media/$USER/bootfs/
sudo cp configs/pi5/config.txt /media/$USER/bootfs/config.txt
sync
```

Expected output:

```text
DarwinTV loader
board:  raspberry-pi-5
load:   0x00200000
uart:   0x107d001000
hello from the other side of the SoC
```

If you see nothing, see the troubleshooting section in
[Raspberry Pi 5 hardware](hardware/pi5.md).

## 5. Test under QEMU first (optional)

```sh
make qemu
```

This builds the `qemu-raspi4b` variant and runs it with `-serial stdio`. The loader is the same
code with a different UART base and load address.

## 6. Fetch XNU and build the host tools

```sh
make xnu-fetch          # third_party/xnu at xnu-8796.141.3
make xnu-patches        # applies patches/ (currently empty)
python -m tools.adt --out build/pi5.adt
python -m tools.ipsw list "$IPSW_PATH"
```

## 7. Updating without reflashing

The boot partition is FAT32; the loader and payload are files. See [Updating images](updates.md).

## 8. Next milestone

M2 replaces the final `wfe` loop with the XNU handoff: parse the firmware FDT, copy the Mach-O,
build the ADT and `boot_args`, and jump. See [Boot flow](boot-flow.md).
