# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial repository scaffold: docs, ADRs, CI, devcontainer, AI-agent instructions.
- Architecture, hardware and tvOS research notes.
- Apple Device Tree writer and IPSW listing tools.
- M1 bare-metal AArch64 loader: EL3/EL2→EL1, PL011 console, Pi 5 and QEMU targets.
- Update workflow: FAT32 boot files, separate `payload.bin`, incremental root updates, A/B slots.
- Large-image strategy: block-backed root, RAM-disk bring-up path, U-Boot/EDK2 first stage.
- Testing strategy: test pyramid, QEMU-first, fast hardware smoke, UART as fallback.
- Ethernet-first network boot loop, TFTP tree helper, and Pi 5 vs phone comparison.
- Status, canonical facts, open questions, AI handoff, XNU build, IPSW, patch, glossary,
  test-rig, safety and CI docs.
- `qemu-virt` loader target; anchored `.gitignore` so `tools/ipsw` and `tools/rootfs` are tracked.
- Payload format, packer/inspector (`tools/payload`), 6 tests, and loader-side CRC/bounds validation.
- TFTP first-boot EEPROM config, no-payload M1 config, and the detected host/network values.
- QEMU smoke CI for `raspi4b`/`virt` with a synthetic payload; dependency/action bumps.

## [0.0.1] - 2026-11-08

### Added

- Project created as a fresh repository rather than a fork of an existing port.
