# DarwinTV status

**Snapshot:** 2026-11-08 · **Phase:** pre-alpha · **XNU on a Pi 5:** not yet.

**Test target:** Raspberry Pi 5 Model B, 8 GB, board revision `d04171` (rev 1.1, Sony UK),
Raspberry Pi Debug Probe on `/dev/ttyACM0`, first boot from **TFTP** via host `192.168.9.103`.

This is the first file a new contributor or AI agent should read. It separates what is built
from what is assumed, and lists what is blocked on hardware.

## What exists and is verified in this repo

| Item | State | Evidence |
|---|---|---|
| Host tooling | works | `pytest` (19 tests), `ruff`, `shellcheck`, `clang-format`, `mkdocs --strict` |
| ADT writer | works on the host | `tools/adt/adt.py`, tests; not yet consumed by XNU |
| IPSW listing/extraction | works on local ZIPs | `tools/ipsw/extract.py`, tests |
| M1 loader | builds | `make loader BOARD=pi5`, `qemu-raspi4b`, `qemu-virt`; ~9.1 KB raw image (vectors + payload validator) |
| M1 loader on QEMU | **verified** | `raspi4b` (local QEMU 11) and `virt` (CI) boot the banner; payload validator prints a synthetic payload |
| M1 loader on hardware | **not run** | no Pi 5 boot yet |
| Payload packer/validator | works | `tools/payload`, 6 tests; `payload.bin` round-trips |
| XNU patches | none yet | `patches/` is empty; `docs/patches.md` is the plan |
| XNU build | not attempted | needs macOS/Xcode; `docs/building-xnu.md` |
| tvOS IPSW extraction | researched, not automated | `docs/ipsw.md`; `OS`/DeviceTree roles verified from the ZIP |
| tvOS root image | not built | `tools/rootfs/README.md` is the plan; `scripts/make-rootfs.sh` exits 2 |
| Pi 5 network boot | host ready, not hardware-tested | `docs/network-boot.md`; `tftpd.service`; EEPROM `BOOT_ORDER=0xf12` |
| TFTP DTB | fetched and verified | `make fetch-dtb`; blob `30c8179…`; published with `make netboot` |
| Hardware facts | catalogued with confidence | `docs/facts.md` — read the confidence column |
| Open research | listed | `docs/open-questions.md` |
| Prior-art/plan review | recorded | BCM2837 support and the newer BCM2712 branch in `docs/facts.md`, ADR 0009, and the [review addendum](https://github.com/Vincas94/darwintv/blob/main/docs/research/2026-11-08-review-addendum.md) |

## What is not done

- No XNU source tree is pinned/fetched in this workspace (`third_party/xnu` is empty).
- No `patches/0001-*.patch` exists.
- No XNU kernel has been built for BCM2712.
- The loader validates and prints a payload, but does not copy the segments or jump yet (M2).
- The loader prints a banner, preserves the DTB pointer, and validates/prints a payload; it does
  not parse `/memory`, copy segments, build `boot_args`, or jump to XNU yet.
- No SDHCI, HFS+, framebuffer, HID or RP1 driver.
- No tvOS root image or `PineBoard` run.

## Blocked on the UART cable / hardware

1. Confirm the Pi 5 debug UART clock and usable baud rates on the actual board.
2. Confirm the Debug Probe's maximum reliable baud and signal integrity at 460800/576000.
3. Dump the firmware FDT (`/memory`, `/reserved-memory`) and read `CNTFRQ_EL0` to replace the
   placeholder memory/timer values.
4. Read `GICD_PIDR2`, `GICD_TYPER`, `GICC_IIDR` to confirm the GIC-400 revision.
5. Confirm the EEPROM network-boot TFTP file flow, including the DTB, on the Pi 5 firmware.
6. Run the M1 loader on the Pi 5 and capture the banner.

## Immediate task queue

1. **M1 on hardware:** TFTP-boot `loader8.img`, capture the banner at 115200, record the DTB
   pointer and `CNTFRQ_EL0`.
2. **Fact pass:** replace every `C` confidence row in `docs/facts.md` that the board can answer.
3. **M2 loader:** parse the firmware `/memory`, copy payload segments to `0x02004000`, build
   `boot_args` from the embedded ADT, and jump to XNU.
4. **XNU build:** pin `xnu-8796.141.3`, base the BCM2712 board config on Apple's BCM2837 port,
   and add the platform expert/GICv2 path (ADR 0009).

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
