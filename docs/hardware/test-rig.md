# Test rig inventory

Fill this in before hardware testing. An AI agent needs the actual values, not "a Pi 5".

## Board

| Item | Value |
|---|---|
| Model | Raspberry Pi 5 Model B |
| RAM | `<4 / 8 / 16 GB>` |
| Board revision | `<from /proc/cpuinfo or the silkscreen>` |
| EEPROM/bootloader | `<rpi-eeprom-update output>` |
| Power supply | `<official 5V/5A?>` |
| Cooling | `<active cooler / heatsink>` |
| Storage | `<microSD / NVMe / USB>` |
| Ethernet | `<1 Gbps, same switch as host>` |

## Serial

| Item | Value |
|---|---|
| Adapter | `<model>` |
| Chip | `<FT232 / CP210x / CH340 / RP2040>` |
| Max baud | `<from datasheet>` |
| Voltage | `3.3 V only` |
| Connector | `3-pin JST-SH (UART10)` |
| Host device | `/dev/ttyUSB0` |

## Power control

| Item | Value |
|---|---|
| Relay / smart plug | `<model>` |
| Command | `POWER_CMD="..."` |
| Cycle time | `<seconds>` |

## Host

| Item | Value |
|---|---|
| OS | `<Linux distro/kernel>` |
| CPU | `<x86_64 / Apple silicon>` |
| QEMU | `<version, qemu-system-aarch64>` |
| Cross compiler | `<aarch64-linux-gnu-gcc version>` |
| Python | `<version>` |
| TFTP server | `<tftpd-hpa / dnsmasq>` |
| TFTP root | `/srv/darwintv-tftp` |

## Network boot

| Item | Value |
|---|---|
| Host IP | `<192.168.x.x>` |
| Pi IP | `<DHCP or static>` |
| `BOOT_ORDER` | `0xf12` |
| `TFTP_IP` | `<host IP>` |
| `TFTP_PREFIX` | `1` |
| `TFTP_PREFIX_STR` | `darwintv/` |

## Safety checklist

- [ ] 3.3 V adapter, no VCC on the debug connector.
- [ ] Known-good SD fallback and a backup of the boot partition.
- [ ] EEPROM recovery method known (`rpiboot`/recovery image).
- [ ] No `dd` to a mounted device.
- [ ] Thermal solution fitted.

See `docs/safety.md`.
