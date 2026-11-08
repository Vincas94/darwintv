# Raspberry Pi 5 hardware

The Pi 5 uses a **BCM2712** SoC: 4× Cortex-A76 (ARMv8.2-A, 2.4 GHz), 4/8/16 GB LPDDR4X,
a GIC-400 (GICv2) interrupt controller, and an **RP1** southbridge for USB, Ethernet and the
40-pin header. The debug UART, HDMI, microSD and Wi-Fi/Bluetooth are on BCM2712.

## Address map

The Linux `bcm2712.dtsi` maps the `soc` node's child address `0x7c000000` to the parent
`0x10_7c000000`.

| Block | Physical address | Notes |
|---|---|---|
| RAM | `0x0` … (from firmware FDT) | parse `/memory` |
| `soc` base | `0x10_7c000000` | `arm-io/ranges` parent base |
| **Debug UART (UART10 / `_uart0`)** | **`0x10_7d001000`** | PL011, 0x200, IRQ SPI 121 |
| **GIC-400 GICD** | **`0x10_7fff9000`** | 0x1000 |
| **GIC-400 GICC** | **`0x10_7fffa000`** | 0x2000 |
| GIC-400 GICH | `0x10_7fffc000` | 0x2000 |
| GIC-400 GICV | `0x10_7fffe000` | 0x2000 |
| ARM generic timer | `CNTFRQ_EL0`, `CNTV_*` | GIC **INTID 27** (DT PPI 11), virtual timer |
| **SDHCI `sdio1` (microSD)** | **`0x10_00fff000`** | 0x260 host, IRQ SPI 273 |
| Wi-Fi `sdio2` | `0x10_01100000` | SDHCI, IRQ SPI 274 |
| Bluetooth `uarta` | `0x10_7d50c000` | `brcm,bcm7271-uart`, IRQ SPI 276 |
| Firmware mailbox | `0x10_7c013880` | property tags / framebuffer |
| HDMI0 | `0x10_7c701400` | first of nine `hdmi@7ef00700` ranges; firmware framebuffer is simpler |
| HDMI1 | `0x10_7c706400` | first of nine `hdmi@7ef05700` ranges |
| **RP1** | PCIe2 | USB, Ethernet, 40-pin GPIO, UART0 |

!!! note "RP1 is not needed for the first boot"
    The **debug UART, HDMI, microSD, Wi-Fi and Bluetooth are on BCM2712**. The **USB-A ports,
    Ethernet and 40-pin header are on RP1**, behind PCIe. The serial/HDMI/SD milestones do not
    need an RP1 driver. A USB keyboard or Ethernet does; that is M6 work.

## Serial console

The Pi 5 primary debug UART is **UART10**, a PL011 at `0x107d001000`, exposed on the **3-pin
JST-SH connector** between the microHDMI ports. It is **3.3 V only**.

| Pin | Signal | Adapter |
|---|---|---|
| 1 | RX / SC (into the Pi) | adapter **TX** |
| 2 | GND | adapter **GND** |
| 3 | TX / SD (out of the Pi) | adapter **RX** |

- **Do not connect VCC/3.3 V/5 V.**
- **115200 baud, 8 data bits, 1 stop bit, no parity, no flow control.**
- `picocom -b 115200 /dev/ttyACM0` or `minicom -b 115200 -D /dev/ttyACM0`.
- The debug connector has **no RTS/CTS**, so high-speed transfers must use a protocol with
  per-block acknowledgement (XMODEM/YMODEM), not hardware flow control.

### UART clock and maximum baud

The BCM2712 DTS gives the debug UART a **9.216 MHz** reference clock (`clk_uart`). The DTS does
not give the ARM generic timer frequency, so the loader must read `CNTFRQ_EL0`. The PL011
uses 16× oversampling, so:

```text
max baud = 9_216_000 / 16 = 576_000
```

| Baud | Divisor (`IBRD`/`FBRD`) | Note |
|---|---|---|
| 115200 | 5 / 0 | firmware default |
| 230400 | 2 / 32 | |
| 460800 | 1 / 16 | good practical target |
| 576000 | 1 / 0 | hardware maximum |

There is no 921600 or 3 Mbaud mode on this UART. The loader must program `IBRD`/`FBRD` before
using a higher rate; the M1 loader leaves the firmware's 115200 in place.

To see firmware logs:

```sh
sudo rpi-eeprom-config --edit     # add BOOT_UART=1
```

`config.txt` sets `uart_2ndstage=1`.

The 40-pin header UART (`UART0`, GPIO 14/15) is on **RP1** and is not the debug UART. Do not use
it for the bare-metal loader.

## Boot configuration

The Pi 5 firmware lives in the SPI EEPROM and loads `kernel_2712.img` (or `kernel8.img`) from the
FAT boot partition. It passes the firmware DTB address in `x0` and enters at EL2 via TF-A.

`config.txt`:

```ini
kernel=loader8.img
kernel_address=0x200000
uart_2ndstage=1
framebuffer_width=1920
framebuffer_height=1080
framebuffer_depth=32
```

`kernel_address=0x200000` is the documented 64-bit load address. If the loader starts at
`0x80000` instead, the Pi 5 EEPROM is old (pre-2023-10-30 firmware used that address): update the
EEPROM rather than changing the loader. The loader prints a clear error if its runtime address
does not match `LOAD_ADDR`. The QEMU `raspi4b` target intentionally uses `0x80000`.

`arm_64bit=1` is unnecessary on the Pi 5: the firmware supports only 64-bit kernels and ignores
the flag.

## Troubleshooting

| Symptom | Check |
|---|---|
| Nothing on the UART | adapter is 3.3 V; TX/RX crossed; GND connected; 115200 8N1 |
| Nothing at all | `kernel=loader8.img`, `kernel_address=0x200000`, file on the FAT partition |
| Firmware log missing | `BOOT_UART=1` in the EEPROM config, `uart_2ndstage=1` in `config.txt` |
| Garbage characters | baud rate or adapter voltage |
| Pi boots Linux instead | `kernel=` filename or the boot partition was not updated |

## Sources

- BCM2712 device tree (`uart0`, `gic-400`, `sdio1`, `sdio2`, `uarta`, HDMI, mailbox):
  <https://github.com/raspberrypi/linux/blob/rpi-6.6.y/arch/arm64/boot/dts/broadcom/bcm2712.dtsi>
- Raspberry Pi 5 board tree (`uart10` alias, Wi-Fi on `sdio2`, BT on `uarta`):
  <https://github.com/raspberrypi/linux/blob/rpi-6.6.y/arch/arm64/boot/dts/broadcom/bcm2712-rpi-5-b.dts>
- RP1 I/O controller: <https://www.raspberrypi.com/documentation/computers/io-controllers/rp1.html>
- UART configuration and the Pi 5 debug connector:
  <https://www.raspberrypi.com/documentation/computers/configuration.html#configure-uarts>
- 3-pin debug connector specification:
  <https://pip.raspberrypi.com/documents/RP-008189-DS-debug-connector-specification.pdf>
- `config.txt` boot options:
  <https://www.raspberrypi.com/documentation/computers/config_txt.html>
- Revision codes: <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-revision-codes>
- 16K `kernel_2712.img`: <https://www.raspberrypi.com/documentation/computers/config_txt.html#kernel>
- Kernel load address: <https://www.raspberrypi.com/documentation/computers/legacy_config_txt.html#kernel-address>
