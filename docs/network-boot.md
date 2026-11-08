# Network boot over Ethernet

Both the Pi 5 and the build host are wired, so the fastest hardware loop is **TFTP network boot**:
no SD card removal, no USB cable to a phone, no flashing. Change `payload.bin` on the host,
power-cycle the Pi, and the EEPROM bootloader fetches the files over Ethernet.

On the Pi 4 and Pi 5, network boot is implemented in the **second-stage bootloader in the EEPROM**
(not in the ROM). Update the EEPROM first:

```sh
sudo rpi-eeprom-update
sudo rpi-eeprom-config --edit
```

## 1. EEPROM settings

For a network-first boot with an SD fallback:

```ini
BOOT_ORDER=0xf12
BOOT_UART=1
TFTP_IP=192.168.1.50
TFTP_PREFIX=1
TFTP_PREFIX_STR=darwintv/
```

`BOOT_ORDER` is read right to left: `2` = NETWORK, `1` = SD, `f` = RESTART. So this tries network,
then SD, then loops.

- `TFTP_IP` is the **build host's** address. It overrides the DHCP server address, so you can keep
  your router as DHCP and run `tftpd-hpa` on the PC.
- `TFTP_PREFIX=1` + `TFTP_PREFIX_STR=darwintv/` keeps the files in a fixed directory. If your
  firmware ignores the prefix, put the files at the TFTP root and set `TFTP_PREFIX=0`.
- `BOOT_UART=1` prints the bootloader log on the debug UART.

Apply and reboot:

```sh
sudo rpi-eeprom-config --edit    # edit and apply; then reboot
# or: sudo rpi-eeprom-config --apply boot.conf
sudo reboot
```

Verify with `sudo rpi-eeprom-config`.

## 2. Build the TFTP tree

```sh
make loader BOARD=pi5
make netboot
# -> build/netboot/darwintv/{config.txt,kernel8.img,payload.bin}
```

`configs/pi5/config-netboot.txt` is used as `config.txt`:

```ini
arm_64bit=1
kernel=kernel8.img
kernel_address=0x200000
ramfsfile=payload.bin
ramfsaddr=0x08000000
uart_2ndstage=1
framebuffer_width=1920
framebuffer_height=1080
framebuffer_depth=32
```

The M1 loader does not read `payload.bin` yet; the network boot still proves the firmware → loader
→ UART path. M2 adds the payload handoff.

## 3. Serve it

### Option A: `tftpd-hpa` (keep your router as DHCP)

```sh
sudo apt-get install tftpd-hpa
sudo mkdir -p /srv/darwintv-tftp
sudo cp -r build/netboot/darwintv /srv/darwintv-tftp/
sudo chown -R tftp:tftp /srv/darwintv-tftp
```

`/etc/default/tftpd-hpa`:

```ini
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/srv/darwintv-tftp"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="--secure --create"
```

```sh
sudo systemctl restart tftpd-hpa
tftp localhost -c get darwintv/config.txt   # smoke test
```

### Option B: `dnsmasq` (DHCP + TFTP on the PC)

Use this only if the PC can be the DHCP server for the Pi's segment:

```ini
interface=eth0
dhcp-range=192.168.50.100,192.168.50.200,12h
enable-tftp
tftp-root=/srv/darwintv-tftp
```

Run it, point the Pi at the PC's address, and use `BOOT_ORDER=0xf12`.

## 4. The loop

```sh
export SERIAL_DEV=/dev/ttyACM0
export SERIAL_BAUD=115200
export POWER_CMD="uhubctl -a cycle -p 1"   # or usbrelay / smart plug
export WAIT_FOR="DarwinTV"

make loader BOARD=pi5
make netboot
sudo cp -r build/netboot/darwintv /srv/darwintv-tftp/   # or rsync
./scripts/power-cycle.sh
./scripts/serial-capture.sh
```

With a 1 Gbps link, a 15 MB `payload.bin` is ~1 second; the boot to the serial banner is ~1–3
seconds. The SD card is only a fallback.

## 5. Troubleshooting

```sh
sudo tcpdump -i eth0 -nn port 67 or port 69
```

- See DHCP but no TFTP: `TFTP_IP` missing/wrong, or the firewall blocks UDP/69.
- TFTP `file not found`: check `TFTP_PREFIX` and the directory name; files must be readable by the
  `tftp` user.
- TFTP works but the loader does not start: check `kernel=kernel8.img` and `kernel_address`.
- Nothing on UART: `BOOT_UART=1`, adapter 3.3 V, TX/RX crossed, 115200.
- Network boot fails every time: `BOOT_ORDER=0xf12` falls back to SD; keep a known-good SD.

## 6. Why this beats a card reader

- no card removal or wear,
- the host is the source of truth; one `rsync` updates the tree,
- the same loop can run from a self-hosted CI runner,
- the SD slot stays free for the persistent root (M4b).

## 7. HTTP boot

The Pi 5 EEPROM also supports HTTP boot (`BOOT_ORDER` mode `0x7`), which downloads `boot.img` and
`boot.sig`. That is aimed at signed firmware images, not a custom XNU payload; use TFTP for
DarwinTV.
