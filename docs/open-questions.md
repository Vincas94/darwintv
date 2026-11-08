# Open questions and research backlog

Each item has a priority, a reason, and a concrete way to answer it. When it is answered, move the
fact to `docs/facts.md` with a confidence level and close the item here.

## P0 — before the first hardware boot

| ID | Question | Why it matters | How to answer |
|---|---|---|---|
| Q1 | What is the actual debug UART clock and maximum reliable baud? | The DTS says 9.216 MHz; the real firmware clock and signal integrity may differ | Loopback at 115200/460800/576000; measure with a scope if possible; update `facts.md` |
| Q2 | Does the user's USB-UART adapter support 460800/576000? | Determines the recovery/kernel transfer speed | Check the adapter datasheet; loopback test; `stty -F /dev/ttyUSB0 460800` |
| Q3 | What is the Pi 5 RAM size and revision? | The kernel window, `memSize`, and RAM-disk viability depend on it | `cat /proc/device-tree/model` and `free -h` on Raspberry Pi OS; fill `docs/hardware/test-rig.md` |
| Q4 | What are the firmware `/memory` and `/reserved-memory` ranges? | The loader must not hand reserved regions to XNU | Dump the DTB from the firmware or a Pi 5 Linux boot; parse with `dtc`; update `facts.md` |
| Q5 | What are `GICD_PIDR2`, `GICD_TYPER`, `GICC_IIDR` on the Pi 5? | Confirms GIC-400 revision and line count | Read via a small bare-metal loader or `/dev/mem` on Linux |
| Q6 | Which SDHCI is the microSD: `sdio1` or `sdio2`? | The root driver must bind the right controller | On Pi 5 Linux: `ls -l /sys/class/mmc_host`, `dmesg`, card removal test |
| Q7 | Does the Pi 5 EEPROM TFTP boot fetch `config.txt`, `kernel8.img` and `ramfsfile`? | The network-boot loop depends on it | `tcpdump -i eth0 port 67 or 69` during a network boot; update `docs/network-boot.md` |
| Q8 | Does the Pi 5 firmware honor `TFTP_PREFIX` for `config.txt`? | Determines the TFTP directory layout | Try `TFTP_PREFIX=1` with `darwintv/`; if not, root layout |
| Q9 | Does XNU accept the M1 ADT and boot args on BCM2712? | The first real XNU milestone | M2 loader + XNU build; serial banner |
| Q10 | Does the A76 accept the 16K XNU build and non-PAC code? | The Pi 5 is ARMv8.2, not Apple silicon | Build and boot; check for PAC/illegal-instruction faults |

## P1 — first XNU bring-up

| ID | Question | Why it matters | How to answer |
|---|---|---|---|
| Q11 | Does `pe_gicv2.c` (Pi 4) work unchanged on the Pi 5 GIC-400? | GIC/timer is the hardest early driver | Port the addresses, boot QEMU `raspi4b`, then hardware |
| Q12 | Is the virtual timer PPI 27 correct on the Pi 5? | XNU's rtclock needs it | Read `GICD_ISENABLER`/timer; test timer ticks |
| Q13 | Does PSCI `CPU_ON` work through the Pi 5 TF-A? | SMP is deferred, but needed later | `smc` call test from the loader; start secondary cores |
| Q14 | Does the PL011 driver match the `uart0` ADT node and clock? | The console is the primary debug channel | Serial banner; test RX |
| Q15 | What is the correct `arm-io/ranges` and `soc` base for the ADT? | The serial/GIC nodes are offsets from it | 0x107c000000 from the DTS; verify by mapping the UART |
| Q16 | What is the exact BCM2712 SDHCI quirk set (`cfg`, `busisol`, `lcpll`)? | The microSD root depends on it | Read the Linux `sdhci-of-dwcmshc`/`brcm` driver and the DTS; test on hardware |
| Q17 | Does the firmware framebuffer mailbox path work under XNU? | The tvOS UI needs a framebuffer | Mailbox `FB_ALLOCATE`/`FB_GET_INFO`; test a solid color |
| Q18 | What is the exact `/product` identity of `AppleTV5,3`? | `MobileGestalt`/`PineBoard` need it | Extract `DeviceTree.j42dap.im4p`, decompress the ADT, read `/product` |

## P2 — tvOS and long tail

| ID | Question | Why it matters | How to answer |
|---|---|---|---|
| Q19 | Is the tvOS 16.6 userland arm64 or arm64e? | PAC would fault on A76 | Inspect the dyld shared cache and a few binaries with `otool`/`lief`/`ipsw` |
| Q20 | What are the APFS volumes inside `096-56462-077.dmg`? | The HFS+ root build needs the system/data layout | Decompress the UDIF; `apfs-fuse`; list volumes |
| Q21 | What does `PineBoard` require from IOKit (display, HID, keybag)? | The UI will crash-loop without them | `launchd` logs, `dyld` traces, `ios-sweet`/HakiOS analogues |
| Q22 | Which daemons must be disabled for the Pi 5? | Avoid crash loops and slow boot | Compare `ios-sweet` `sweet-root-tweaks.py`; test |
| Q23 | What is the RP1/PCIe topology for USB/Ethernet/GPIO? | M6 input/network | RP1 docs, Linux `lspci`, DTS |
| Q24 | Is V3D/VideoCore VII feasible under XNU? | GPU acceleration | Mesa V3D driver, Linux DRM; long-term |
| Q25 | What is the legal boundary for the tvOS userland? | Avoid distributing Apple files | `NOTICE`, `THIRD_PARTY_LICENSES.md`, `docs/tvos.md`; not legal advice |

## Answered questions

Move answered items here with a one-line answer and a link to the fact row. Do not delete the
history; it is how the next agent knows what was already tried.
