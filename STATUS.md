# DarwinTV status

**Snapshot:** 2026-11-08 · **Phase:** pre-alpha · **XNU on a Pi 5:** not yet.

**Test target:** Raspberry Pi 5 Model B, 8 GB, board revision `d04171` (rev 1.1, Sony UK),
Raspberry Pi Debug Probe on `/dev/ttyACM0`, first boot from **TFTP**.

This is the first file a new contributor or AI agent should read. It separates what is built
from what is assumed, and lists what is blocked on hardware.

## What exists and is verified in this repo

| Item | State | Evidence |
|---|---|---|
| Host tooling | works | `pytest` (12 tests), `ruff`, `shellcheck`, `clang-format`, `mkdocs --strict` |
| ADT writer | works on the host | `tools/adt/adt.py`, tests; not yet consumed by XNU |
| IPSW listing/extraction | works on local ZIPs | `tools/ipsw/extract.py`, tests |
| M1 loader | builds | `make loader BOARD=pi5` and `BOARD=qemu-raspi4b`; ~1.6 KB raw image |
| M1 loader on hardware | **not run** | no Pi 5 boot or QEMU run in this workspace |
| XNU patches | none yet | `patches/` is empty; `docs/patches.md` is the plan |
| XNU build | not attempted | needs macOS/Xcode; `docs/building-xnu.md` |
| tvOS IPSW extraction | researched, not automated | `docs/ipsw.md`; `OS`/DeviceTree roles verified from the ZIP |
| tvOS root image | not built | `tools/rootfs/README.md` is the plan; `scripts/make-rootfs.sh` exits 2 |
| Pi 5 network boot | documented, not tested | `docs/network-boot.md`; EEPROM `BOOT_ORDER=0xf12` |
| Hardware facts | catalogued with confidence | `docs/facts.md` — read the confidence column |
| Open research | listed | `docs/open-questions.md` |

## What is not done

- No XNU source tree is pinned/fetched in this workspace (`third_party/xnu` is empty).
- No `patches/0001-*.patch` exists.
- No XNU kernel has been built for BCM2712.
- No payload packer (`tools/payload`) exists yet; M2.
- The loader prints a banner and spins; it does not parse the FDT, load a payload, build
  `boot_args`, or jump to XNU.
- No SDHCI, HFS+, framebuffer, HID or RP1 driver.
- No tvOS root image or `PineBoard` run.

## Blocked on the UART cable / hardware

1. Confirm the Pi 5 debug UART clock and usable baud rates on the actual board.
2. Confirm the adapter's maximum baud and signal integrity at 460800/576000.
3. Dump the firmware FDT (`/memory`, `/reserved-memory`) to replace the placeholder memory map.
4. Read `GICD_PIDR2`, `GICD_TYPER`, `GICC_IIDR` to confirm the GIC-400 revision.
5. Confirm which SDHCI (`sdio1` vs `sdio2`) is the microSD slot.
6. Confirm the EEPROM network-boot TFTP file flow on the Pi 5 firmware revision.
7. Run the M1 loader on the Pi 5 and capture the banner.

## Immediate task queue

1. **M1 on hardware:** flash/copy `loader8.img`, capture the banner at 115200.
2. **Fact pass:** replace every `C` confidence row in `docs/facts.md` that the board can answer.
3. **M2 payload:** define `payload.bin` (magic, length, CRC, Mach-O, ADT, boot args).
4. **M2 loader:** FDT `/memory`, copy segments to `0x02004000`, ADT + `boot_args`, EL1 jump.
5. **XNU build:** pin `xnu-8796.141.3`, add the BCM2712 board config and platform expert.

## Confidence legend

Used in `docs/facts.md` and `docs/open-questions.md`:

- **A — primary source.** Datasheet, DTS line, XNU source, measured on hardware, or a directly
  inspected file (e.g. IPSW central directory).
- **B — strong secondary source.** Documentation, upstream project behavior, or a well-supported
  inference from an A fact.
- **C — unverified assumption.** Must be checked before it is relied on.

## Read next

1. `docs/facts.md` — what is known, with sources and confidence.
2. `docs/open-questions.md` — what is not known and how to answer it.
3. `docs/ai-handoff.md` — how to continue without guessing.
4. `docs/patches.md` — the kernel patch plan.
5. `docs/hardware/test-rig.md` — fill in your actual hardware.
