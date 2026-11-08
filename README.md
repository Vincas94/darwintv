<div align="center">
  <img src="assets/logo.svg" alt="DarwinTV logo" width="128">
  <h1>DarwinTV</h1>
  <p><strong>Apple TV's tvOS userland on a Raspberry Pi 5, via a from-source XNU port.</strong></p>
  <p>
    <img alt="status" src="https://img.shields.io/badge/status-pre--alpha-orange">
    <img alt="license" src="https://img.shields.io/badge/license-MIT-blue">
    <img alt="platform" src="https://img.shields.io/badge/platform-Raspberry%20Pi%205-c51a4a">
    <img alt="XNU" src="https://img.shields.io/badge/XNU-xnu--8796.141.3-lightgrey">
    <a href="https://github.com/Vincas94/darwintv/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/Vincas94/darwintv/actions/workflows/ci.yml/badge.svg"></a>
  </p>
</div>

## Start here

| If you are... | Read |
|---|---|
| New to the project | [`STATUS.md`](STATUS.md) |
| Checking a hardware claim | [`docs/facts.md`](docs/facts.md) |
| Looking for the next task | [`docs/open-questions.md`](docs/open-questions.md) |
| An AI agent | [`AGENTS.md`](AGENTS.md) + [`docs/ai-handoff.md`](docs/ai-handoff.md) |

> **Status: pre-alpha research.** There is no working Pi 5 port yet. The first milestone is
> XNU printing its banner on the Pi 5 debug UART. The long-term target is the unmodified
> tvOS 16 `PineBoard` userland on a Raspberry Pi 5.

## What this is

DarwinTV is an independent, reproducible bring-up of Apple's open-source **XNU** kernel on the
**Raspberry Pi 5** (BCM2712, 4× Cortex-A76), with the **tvOS 16 userland** as the eventual
payload. It is the natural next step after:

- [`ios-sweet`](https://github.com/dipa-studio/ios-sweet) — iOS 16 on a Redmi Note 10 Pro,
- [HakiOS](https://github.com/oosexgang/hakios-xnu-kernel) — XNU on a POCO X5 Pro,
- [`xnu-on-pi`](https://github.com/tansanrao/xnu-on-pi) — XNU on a Raspberry Pi 4.

## What this is not

- Not a fork of XNU. Apple's kernel is fetched at a pinned tag and patched in `patches/`.
- Not a distribution of Apple firmware, IPSWs, kernelcaches, device trees or userland.
- Not a way to bypass activation, DRM or Apple's security model.
- Not a usable Apple TV replacement (yet). Expect serial consoles, panics and slow software
  rendering first.

## Architecture

```text
BCM2712 boot ROM
  └─ SPI EEPROM bootloader
      └─ kernel8.img / kernel_2712.img at 0x200000 (x0 = DTB)
          └─ TF-A BL31 armstub: EL3 → EL2
              └─ DarwinTV bootloader (bootloader/)
                  ├─ parse the firmware FDT
                  ├─ copy the XNU Mach-O to 0x02000000 + 0x4000
                  ├─ build an Apple Device Tree (ADT) and boot_args
                  └─ EL2 → EL1, jump to XNU
                      └─ XNU (patched xnu-8796.141.3)
                          ├─ PL011 console @ 0x107d001000
                          ├─ GIC-400 / GICv2 + architectural timer
                          ├─ SDHCI @ 0x1000fff000 → HFS+ root
                          └─ launchd → backboardd → PineBoard (tvOS)
```

## Quick start

```sh
git clone https://github.com/Vincas94/darwintv.git
cd darwintv

./scripts/bootstrap.sh
source .venv/bin/activate

make loader                 # build bootloader/build/pi5/loader8.img
make qemu                   # hello-world loader under QEMU raspi4b (optional)
make check                  # lint + tests + docs
```

On the Pi 5, copy `bootloader/build/pi5/loader8.img` to the boot partition and use
`configs/pi5/config.txt`. Connect a **3.3 V** USB-UART adapter to the 3-pin debug connector at
**115200 8N1** — see [`docs/hardware/pi5.md`](docs/hardware/pi5.md).

## Updating without reflashing

The boot partition is FAT32 and the loader/payload are files. Kernel updates are a single
`payload.bin` copy; root updates are incremental. See [`docs/updates.md`](docs/updates.md).

## Repository layout

| Path | What |
|---|---|
| `bootloader/` | Bare-metal AArch64 loader: EL drop, PL011 console, ADT/boot_args (M1 now, XNU later) |
| `patches/` | `git format-patch` series applied to the pinned XNU tree |
| `tools/adt/` | Apple Device Tree writer used by the loader and tests |
| `tools/ipsw/` | Local IPSW listing/extraction helpers |
| `tools/payload/` | Payload packer/inspector and the loader-side format |
| `tools/rootfs/` | Planned tvOS root-image pipeline |
| `configs/` | `config.txt`, QEMU and Pi 5 boot configuration |
| `docs/` | Hardware, boot flow, tvOS, research notes and ADRs |
| `tests/` | Python tests for the host-side tools |
| `third_party/` | Fetched upstreams (XNU); never committed |

## Roadmap

See [`ROADMAP.md`](ROADMAP.md). The short version:

| Milestone | Exit criterion |
|---|---|
| M0 | QEMU `raspi4b` reference and IPSW extraction work |
| M1 | `hello` on the Pi 5 debug UART |
| M2 | XNU banner on the Pi 5 debug UART |
| M3 | GICv2 + timer interrupts stable |
| M4 | HFS+ root + `launchd` |
| M5 | `PineBoard` draws the tvOS home screen |
| M6 | RP1/USB/BT/GPU long tail |

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md), [`AGENTS.md`](AGENTS.md) and the ADRs in
[`docs/decisions/`](docs/decisions/). AI-assisted contributions are welcome when disclosed and
when the contributor can explain the change.

## Legal

DarwinTV is independent and not affiliated with or endorsed by Apple, Raspberry Pi, or the
projects it references. XNU is APSL-2.0; the original code here is MIT. **No Apple firmware or
userland is distributed.** See [`NOTICE`](NOTICE), [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md)
and [`docs/tvos.md`](docs/tvos.md).
