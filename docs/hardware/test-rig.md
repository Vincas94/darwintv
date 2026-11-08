# Test rig inventory

Fill this in before hardware testing. An AI agent needs the actual values, not "a Pi 5".

## Board

| Item | Value |
|---|---|
| Model | Raspberry Pi 5 Model B |
| RAM | **8 GB** |
| Board revision | **`d04171`** = Pi 5 rev 1.1, 8 GB, Sony UK |
| EEPROM/bootloader | `<rpi-eeprom-update output — fill on first boot>` |
| Power supply | `<official 5V/5A?>` |
| Cooling | `<active cooler / heatsink>` |
| Storage | microSD (first boot from **TFTP**) |
| Ethernet | `<1 Gbps, same switch as host>` |

## Serial

| Item | Value |
|---|---|
| Adapter | **Raspberry Pi Debug Probe** |
| Chip | RP2040 (Debug Probe) |
| Max baud | 115200 verified; 460800/576000 to test |
| Voltage | `3.3 V only` |
| Connector | `3-pin JST-SH (UART10)` |
| Host device | **`/dev/ttyACM0`** (Debug Probe is CDC-ACM) |

## Power control

| Item | Value |
|---|---|
| Relay / smart plug | `<model>` |
| Command | `POWER_CMD="..."` |
| Cycle time | `<seconds>` |

## Host

| Item | Value |
|---|---|
| OS | Linux (fill distro/kernel) |
| CPU | `<x86_64 / Apple silicon>` |
| QEMU | not installed in the current workspace; install `qemu-system-arm` |
| Cross compiler | `aarch64-linux-gnu-gcc` 16.2.0 (current workspace) |
| Python | `<version>` |
| TFTP server | `<tftpd-hpa / dnsmasq>` |
| TFTP root | `/srv/darwintv-tftp` |

## Network boot

| Item | Value |
|---|---|
| Host IP | **192.168.9.103** (`enp37s0`, gateway 192.168.9.1) |
| Pi IP | DHCP on 192.168.9.0/24 (fill after first boot) |
| `BOOT_ORDER` | `0xf12` (network, SD fallback, restart) |
| `TFTP_IP` | **192.168.9.103** (use a DHCP reservation/static address) |
| `TFTP_PREFIX` | `1` |
| `TFTP_PREFIX_STR` | `darwintv/` |

## Safety checklist

- [ ] 3.3 V adapter, no VCC on the debug connector.
- [ ] Known-good SD fallback and a backup of the boot partition.
- [ ] EEPROM recovery method known (`rpiboot`/recovery image).
- [ ] No `dd` to a mounted device.
- [ ] Thermal solution fitted.

See `docs/safety.md`.
