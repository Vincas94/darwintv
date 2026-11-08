# Open questions and research backlog

Each item has a priority, a reason, and a concrete way to answer it. When it is answered, move the
fact to `docs/facts.md` with a confidence level and close the item here.

## P0 — before the first hardware boot

| ID | Question | Why it matters | How to answer |
|---|---|---|---|
| Q1 | What is the actual debug UART clock and maximum reliable baud? | The DTS says 9.216 MHz; the real firmware clock and signal integrity may differ | Loopback at 115200/460800/576000; measure with a scope if possible; update `facts.md` |
| Q2 | Does the Raspberry Pi Debug Probe support 460800/576000? | Determines the recovery/kernel transfer speed | Loopback test on `/dev/ttyACM0`; `stty -F /dev/ttyACM0 460800`; update `facts.md` |
| Q4 | What are the firmware `/memory` and `/reserved-memory` ranges? | The loader must not hand reserved regions to XNU | Dump the DTB from the firmware or a Pi 5 Linux boot; parse with `dtc`; update `facts.md` |
| Q5 | What are `GICD_PIDR2`, `GICD_TYPER`, `GICC_IIDR` on the Pi 5? | Confirms GIC-400 revision and line count | Read via a small bare-metal loader or `/dev/mem` on Linux |
| Q7 | Does the Pi 5 EEPROM TFTP boot fetch `config.txt`, `kernel8.img`, the DTB and `ramfsfile`? | The network-boot loop depends on it | `tcpdump -i <interface> port 67 or 69` during a network boot; update `docs/network-boot.md` |
| Q8 | Does the Pi 5 firmware honor `TFTP_PREFIX` for `config.txt`? | Determines the TFTP directory layout | Try `TFTP_PREFIX=1` with `darwintv/`; if not, root layout |
| Q9 | Does XNU accept the M1 ADT and boot args on BCM2712? | The first real XNU milestone | M2 loader + XNU build; serial banner |
| Q10 | Does the A76 accept the 16K XNU build and non-PAC code? | The Pi 5 is ARMv8.2, not Apple silicon | Build and boot; check for PAC/illegal-instruction faults |

## P1 — first XNU bring-up

| ID | Question | Why it matters | How to answer |
|---|---|---|---|
| Q11 | Should the first interrupt path be `pe_gicv2.c` or the IOKit `BCM2712InterruptController`? | GIC/timer is the hardest early driver; the prior-art branch chose IOKit | Start with `pe_gicv2.c` for timer/console (ADR 0009), then evaluate the IOKit driver for SPI/userland |
| Q12 | Is GIC INTID 27 (DT PPI 11) the virtual timer on the Pi 5? | XNU's rtclock needs it | Read `GICD_ISENABLER`/timer; test timer ticks; verify `CNTFRQ_EL0` |
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
| Q26 | Can PSCI `CPU_ON` start cores that the loader parked in `wfe`? | SMP is deferred, but the parked-core model may block it | Test on QEMU/Pi 5; compare with TF-A held state; update `docs/boot-flow.md` |
| Q27 | Which closed kexts/services are required by tvOS (AMFI, Sandbox, AppleKeyStore, etc.)? | The plan stubs security, but the exact dependency set is unverified | Read `launchd`/`dyld` failures, `ios-sweet`/HakiOS stubs; add to `docs/open-questions.md` and patches |
| Q28 | Should the BCM2712 port be backported to `xnu-8796.141.3` or repin to `xnu-on-pi`? | The prior branch diverges (merge base .101.5), uses 4K and IOKit GIC | ADR 0009 chose backport; revisit only if backport cost is prohibitive |
| Q29 | What is the ARM generic timer frequency (`CNTFRQ_EL0`)? | The DTS has no timer frequency; the ADT currently assumes 54 MHz | Loader reads/prints `CNTFRQ_EL0`; update `facts.md` and the ADT/payload |
| Q30 | Does Pi 5 TFTP firmware load `bcm2712-rpi-5-b.dtb` from the TFTP tree? | The loader needs the firmware DTB for `/memory` | Add the DTB to the TFTP tree; `tcpdump`; serial `dtb:` pointer |
| Q31 | What is the measured TFTP time for a 15 MB payload? | Stop-and-wait TFTP is not line-rate; current docs have no measurement | Measure after the first network boot; update `docs/network-boot.md` and `docs/facts.md` |

## Answered questions

Move answered items here with a one-line answer and a link to the fact row. Do not delete the
history; it is how the next agent knows what was already tried.

- **Q3 — Pi 5 RAM/revision:** 8 GB, board revision `d04171` (rev 1.1, Sony UK). See
  `docs/facts.md` and `docs/hardware/test-rig.md`.
- **Q6 — microSD controller:** `sdio1`; the Pi 5 board DTS says "SDIO1 is used to drive the SD
  card" and "SDIO2 drives the WLAN interface". See `docs/facts.md`.
