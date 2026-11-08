# Canonical facts

This is the single place to check a hardware or platform claim. Every row has a source and a
confidence level (`A`/`B`/`C`, defined in `STATUS.md`). If you learn a new fact, add it here and
mark the confidence; do not leave it only in a chat or a code comment.

## Raspberry Pi 5 / BCM2712

| Fact | Value | Source | Confidence |
|---|---|---|---|
| SoC | Broadcom BCM2712 | BCM2712 DTS `compatible = "brcm,bcm2712"` | A |
| Board revision | `d04171` = Raspberry Pi 5 rev 1.1, 8 GB, Sony UK | Raspberry Pi revision-codes documentation | A (user-provided code + official table) |
| CPU | 4× Cortex-A76, ARMv8.2-A, 2.4 GHz | BCM2712 DTS `cpu@0..3`, `arm,cortex-a76`; Raspberry Pi docs | A |
| 16K translation granule | supported by A76; Pi 5 Linux uses `kernel_2712.img` with 16K pages | Raspberry Pi `config.txt` docs; ARM A76 TRM | A (CPU), B (XNU use) |
| Interrupt controller | ARM GIC-400 (GICv2): GICD `0x10_7fff9000`, GICC `0x10_7fffa000` | BCM2712 DTS `interrupt-controller@7fff9000`, `compatible = "arm,gic-400"` | A (DTS), C (silicon revision) |
| Debug UART | UART10, PL011, `0x10_7d001000`, IRQ SPI 121 | BCM2712 DTS `uart0: serial@7d001000`; `uart10` alias in the Pi 5 board DTS; Linux earlycon `0x107d001000` | A |
| UART reference clock | 9.216 MHz | BCM2712 DTS `clk_uart { clock-frequency = <9216000>; }` | A (DTS), B (actual firmware clock) |
| UART maximum baud | 576000 (9.216 MHz / 16, PL011 16× oversampling) | PL011 TRM formula + DTS clock | B (needs a hardware loopback check) |
| UART default | 115200 8N1, no RTS/CTS on the 3-pin debug connector | Raspberry Pi UART docs; debug connector spec | A |
| microSD controller | SDHCI `sdio1`, `0x10_00fff000`, IRQ SPI 273 | BCM2712 DTS `mmc@fff000`, `brcm,bcm2712-sdhci` | A (DTS), B (which slot) |
| Wi-Fi | `sdio2`, `0x10_01100000`, IRQ SPI 274 | BCM2712 DTS + Pi 5 board DTS (`sdio2` drives WLAN) | A |
| Bluetooth | `uarta`, `0x10_7d50c000`, IRQ SPI 276 | BCM2712 DTS `serial@7d50c000`; Pi 5 board DTS `uarta` = BT | A |
| RP1 | USB, Ethernet, 40-pin GPIO, UART0 behind PCIe2 | Raspberry Pi RP1 documentation | A |
| HDMI | HDMI0 `0x10_7c701400`, HDMI1 `0x10_7c706400` | BCM2712 DTS | A |
| Firmware mailbox | `0x10_7c013880` | BCM2712 DTS `mailbox@7c013880` | A |
| RAM map | placeholder in the Linux DTS; firmware fills `/memory` | Pi 5 board DTS `memory@0` comment; firmware behavior | C (actual ranges) |
| Firmware load address | `0x200000` for 64-bit kernels; `kernel_address` can override | Raspberry Pi `config.txt` docs | A (docs), C (Pi 5 firmware revision) |
| Entry state | EL2 via TF-A BL31, `x0` = firmware DTB | Raspberry Pi boot docs; TF-A RPi5 port | B (needs a serial dump) |
| Network boot | implemented in the EEPROM second-stage bootloader; `BOOT_ORDER` mode `0x2` | Raspberry Pi EEPROM/network-boot docs | A (docs), C (exact TFTP file flow) |

## Apple TV / tvOS target

| Fact | Value | Source | Confidence |
|---|---|---|---|
| Target device | Apple TV HD, `AppleTV5,3`, board `j42dap` | Apple Wiki / `ipsw.me` device database | A |
| SoC | Apple A8 (t7000), ARMv8.0, arm64, no PAC | `ipsw.me` board data (`t7000`) + ARMv8.0 architecture | A (SoC), B (no PAC in userland) |
| Target OS | tvOS 16.6, build `20M73` | Apple Wiki firmware index; IPSW filename | A |
| IPSW | `AppleTV5,3_16.6_20M73_Restore.ipsw`, 3,887,550,686 bytes | Apple CDN; ZIP central directory | A |
| `OS` entry | `096-56462-077.dmg`, 3,612,754,508 bytes, LZFSE/UDIF | ZIP central directory; `BuildManifest.plist` role `OS` | A |
| Restore ramdisk | `096-56444-077.dmg`, 79,691,803 bytes | `BuildManifest.plist` role `RestoreRamDisk` | A |
| Additional image | `096-56456-077.dmg`, 116,163,007 bytes + `.mtree`/`.root_hash`/`.trustcache` | ZIP central directory | A (existence), C (role) |
| Device tree | `Firmware/all_flash/DeviceTree.j42dap.im4p`, 16,437 bytes | ZIP central directory | A |
| Kernelcache | `kernelcache.release.j42d`, 18,961,716 bytes, IM4P `krnl` | ZIP central directory; IM4P header | A (entry), B (encrypted/personalized) |
| XNU generation | `xnu-8796.141.3` (Darwin 22.6.0) | iOS 16.6 open-source tag; tvOS 16.6 is the same generation (inferred) | B |
| UI process | `PineBoard` / `HeadBoard`, with `backboardd` | NewOSXBook tvOS 9 analysis; Apple TV platform docs | B |
| UI resolution | 1920×1080 for Apple TV HD; 4K for 4K models | Apple TV HD specs | B |
| Userland arch | arm64 (non-PAC) because A8 is ARMv8.0 | A8 architecture; `dyld` cache archive still to verify | B |

## XNU interfaces

| Fact | Value | Source | Confidence |
|---|---|---|---|
| `boot_args` | Revision 2 / Version 2, `BOOT_LINE_LENGTH` 608 | `pexpert/pexpert/arm64/boot.h` | A |
| ADT format | `{u32 nprops, u32 nchildren, props, children}`, property name 32 bytes, length + value | `pexpert/device_tree.c`; `tools/adt/adt.py` | A |
| RAM-disk root | `/chosen/memory-map` property `RAMDisk` = `<physical base, size>` creates `/dev/md0`; `rd=md0` roots on it | `iokit/bsddev/IOKitBSDInit.cpp`; `bsd/kern/bsd_init.c` | A |
| 16K pages | `__ARM_16K_PG__` selects `ARM_PGSHIFT 14` | `osfmk/arm64/proc_reg.h`; `osfmk/mach/arm/vm_param.h` | A |
| Non-PAC build | `-DARM64_BOARD_CONFIG_*` without `__ARM_PTRAUTH__`; no PAC instructions | XNU build config and board headers | A (mechanism), B (Pi 5 target) |
| Kernel build host | XNU requires macOS/Xcode/Apple clang; not buildable on Linux | Apple XNU build docs | A |

## Host tooling and pins

| Fact | Value | Source | Confidence |
|---|---|---|---|
| XNU pin | `xnu-8796.141.3` | `scripts/fetch-xnu.sh`; Apple open-source tag | A |
| tvOS IPSW pin | `AppleTV5,3_16.6_20M73` | `docs/tvos.md`; Apple CDN | A |
| Python | 3.11+ | `pyproject.toml` | A |
| QEMU reference | `raspi4b` (GIC-400/PL011) and `virt,gic-version=2` | `docs/testing.md`; QEMU docs | B |
| Cross compiler | `aarch64-linux-gnu-gcc` | `bootloader/Makefile`, CI | A |

## The rules for adding a fact

1. Put the **value**, **source**, and **confidence** in the table.
2. If it is `C`, also add it to `docs/open-questions.md` with a way to test it.
3. If a hardware test changes a `C` to `A`, update the row and the open question in the same commit.
4. Do not write "the Pi 5 does X" in a doc without a row here or a link to one.


## Source links

- BCM2712 DTS: <https://github.com/raspberrypi/linux/blob/rpi-6.6.y/arch/arm64/boot/dts/broadcom/bcm2712.dtsi>
- Raspberry Pi 5 board DTS: <https://github.com/raspberrypi/linux/blob/rpi-6.6.y/arch/arm64/boot/dts/broadcom/bcm2712-rpi-5-b.dts>
- RP1: <https://www.raspberrypi.com/documentation/computers/io-controllers/rp1.html>
- UART/debug connector: <https://www.raspberrypi.com/documentation/computers/configuration.html#configure-uarts>
- PL011 TRM: <https://developer.arm.com/documentation/ddi0183/g/>
- `boot_args`: <https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/boot.h>
- ADT parser: <https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/device_tree.c>
- `RAMDisk`/`rd=md0`: <https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/bsddev/IOKitBSDInit.cpp> and <https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/bsd/kern/bsd_init.c>
- 16K pages: <https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/osfmk/arm64/proc_reg.h>
- Apple TV firmware index: <https://theapplewiki.com/wiki/Firmware/Apple_TV/16.x>
- `ipsw.me` device data: <https://api.ipsw.me/v4/device/AppleTV5,3?type=ipsw>
- Pi 5 network boot / EEPROM: <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-bootloader-configuration>
- `config.txt`: <https://www.raspberrypi.com/documentation/computers/config_txt.html>
