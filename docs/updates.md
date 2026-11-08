# Updating images without reflashing

The Pi 5 does **not** have a monolithic "OS image" that must be written with `dd` on every
change. The SPI EEPROM contains the bootloader; the boot medium is a FAT32 partition that the
firmware reads as files. Updating DarwinTV is therefore a file copy or a partition write, not a
full-card reflash.

## The layers

| Layer | Where it lives | How you update it |
|---|---|---|
| Bootloader EEPROM | SPI flash on the board | `rpi-eeprom-update` (rare) |
| Firmware config | FAT32 partition, `config.txt` | copy a file |
| DarwinTV loader | FAT32 partition, `loader8.img` | copy a file |
| XNU + ADT + boot args | FAT32 partition, `payload.bin` | copy a file |
| tvOS root | separate raw partition or image file | `bmaptool`, `rsync`, or block write |
| Rescue tools | optional ext4 partition | normal Linux package updates |

Only the EEPROM is "flashed". The SD card is a normal disk you can mount.

## Recommended layout

```text
/dev/sdX
  p1  FAT32   boot       config.txt, cmdline.txt, loader8.img,
                         payload.bin, payload-a.bin, payload-b.bin, boot.cfg
  p2  raw     tvos       HFS+ root image (AppleTV5,3 16.6 userland)
  p3  ext4    rescue     optional Linux + tools for updating p1/p2 from the Pi
```

The firmware only needs p1. XNU only needs p2 once the SDHCI/HFS+ driver exists. p3 is optional
and is never touched by the DarwinTV loader.

## 1. Update the loader (rare)

The loader is stable. When it changes:

```sh
make loader BOARD=pi5
sudo mount /dev/sdX1 /mnt/boot
sudo cp bootloader/build/pi5/loader8.img /mnt/boot/
sync
sudo umount /mnt/boot
```

No `dd`, no reflash, no repartitioning.

## 2. Update the kernel (every build)

Keep the loader and the payload separate. The firmware can load an extra file at a fixed address
with `ramfsfile`/`ramfsaddr` (or `initramfs`):

```ini
# config.txt
arm_64bit=1
kernel=loader8.img
kernel_address=0x200000
ramfsfile=payload.bin
ramfsaddr=0x08000000
uart_2ndstage=1
```

`payload.bin` is the M2 packer's output: the XNU Mach-O, the ADT, and the boot arguments, with a
magic header. The loader reads it from `0x08000000`, copies the segments, and jumps. Updating the
kernel is then:

```sh
# on the build host, after the macOS/GitHub Actions XNU build
python -m tools.payload pack \
    --kernel kernel.development.bcm2712 \
    --adt build/pi5.adt \
    --cmdline "debug=0xc serial=1 cpus=1 keepsyms=1 -noprogress" \
    --out payload.bin

sudo mount /dev/sdX1 /mnt/boot
sudo cp payload.bin /mnt/boot/
sync
sudo umount /mnt/boot
```

The 15 MB kernel is a single file copy. The firmware's `ramfsfile` loader puts it in RAM before
the loader runs.

!!! note "Firmware support"
    `ramfsfile`/`ramfsaddr` are documented `config.txt` options. Verify them on your Pi 5
    firmware revision; the fallback is to embed the payload in `loader8.img` (still a file copy)
    or to let U-Boot load it (below).

## 3. Update the root filesystem

The tvOS root is large. Do not rewrite the whole card:

- **Mount and rsync** (best for file changes):
  ```sh
  sudo mount -t hfsplus /dev/sdX2 /mnt/tvos
  sudo rsync -a --delete /path/to/new-root/ /mnt/tvos/
  sync
  sudo umount /mnt/tvos
  ```
- **bmaptool** (best for a new image): `bmaptool create` once, then
  `sudo bmaptool copy root.img /dev/sdX2` writes only the mapped blocks.
- **Sparse/seek writes** for a single file inside a raw image:
  `dd if=file of=/dev/sdX2 bs=1M seek=OFFSET conv=notrunc`.

For early bring-up, skip p2 entirely: use a **RAM-disk root** (`mockfs` + a static userland, or a
small HFS+ image) packed into `payload.bin`. Then updating the "root" is the same single-file
copy as the kernel.

## 4. No card removal: serial download

The USB-UART adapter is already connected. Add XMODEM-CRC (or a small custom protocol) to the
loader:

1. At boot, wait ~1 second for a `D` key on the UART.
2. Receive `payload.bin` into `0x08000000`.
3. Verify the magic and CRC, then boot it.

At 115200 baud, 8N1, the theoretical throughput is ~11.5 KB/s, so a 15 MB kernel takes ~22
minutes. A 512 KB test kernel takes ~45 seconds. At 921600 baud (if the adapter and PL011 clock
allow it), the 15 MB kernel is ~2.7 minutes. This is the "no SD card at all" loop for kernel
bring-up; use the FAT copy for full builds.

## 5. A/B slots and safe updates

Keep a known-good payload and a new one:

```text
payload-a.bin   known good
payload-b.bin   candidate
boot.cfg        "slot=a" or "slot=b"
```

Two ways to select:

- **Pi firmware `tryboot` / `autoboot.txt`**: boot `tryboot.txt` once; if it fails, the next boot
  returns to the known-good config. Good for atomic updates.
- **Loader `boot.cfg`**: the loader reads a tiny config file from the FAT partition (a read-only
  FAT32 driver is a small M3 task) and chooses `payload-a.bin` or `payload-b.bin`. Good for
  interactive bring-up.

A third option is **U-Boot/EDK2** as the first stage: U-Boot already has FAT/ext4/TFTP, a shell,
and a boot menu. The Pi 5 firmware loads U-Boot as `kernel8.img`; U-Boot loads the DarwinTV
loader/payload from a file or the network. You update files, not the card.

## 6. Network and USB boot

- The Pi 5 firmware supports network boot (TFTP) on supported firmware revisions. Serve
  `kernel8.img`, `config.txt` and `payload.bin`; no boot-medium writes at all.
- U-Boot can also TFTP the payload, or read it from a USB stick or NVMe SSD.
- Booting the **boot partition** from NVMe/USB avoids SD wear and is faster. XNU still needs its
  own storage driver for the root; the firmware reads the boot files, not XNU.

## 7. What still needs a "reflash"

- Corrupt SPI EEPROM bootloader: use `rpiboot`/the EEPROM recovery image.
- Repartitioning the card: one-time.
- A completely bricked boot medium: restore p1 from a backup.

Normal DarwinTV development is: build → copy `payload.bin` (or XMODEM it) → reboot. The root
filesystem is updated with `rsync`/`bmaptool`, not a full image write.

## 8. Wear and recovery

- Keep the root mounted read-only for normal use; put logs and mutable state on a small writable
  partition or a RAM disk.
- Use a high-endurance SD card, or boot from NVMe/USB.
- Keep `payload-a.bin` as a known-good slot and a `config-recovery.txt` on p1.
- The serial console is the recovery console: if a payload panics, power-cycle and pick the other
  slot, or XMODEM a known-good payload.
