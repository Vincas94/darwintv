# AI handoff

You are an AI agent picking up DarwinTV. This page tells you how to continue without guessing or
breaking the project.

## Read in this order

1. `STATUS.md` — what exists, what is blocked, the task queue.
2. `docs/facts.md` — canonical facts, sources, confidence.
3. `docs/open-questions.md` — what is unknown and how to answer it.
4. `AGENTS.md` — hard rules.
5. `ARCHITECTURE.md` and `docs/boot-flow.md`.
6. `docs/patches.md` — the kernel plan.
7. `docs/hardware/test-rig.md` — fill in the actual hardware.

## Current state in one paragraph

The host tools, docs, CI, and a freestanding M1 loader exist. The loader checks its runtime
address, saves the firmware DTB pointer, prints `CNTFRQ_EL0`, installs exception vectors,
sets `VPIDR_EL2`/`VMPIDR_EL2`, and validates/prints `payload.bin`. It does not parse `/memory`,
copy the segments, build `boot_args`, or jump to XNU yet. Apple's tag ships a BCM2837 port; the
newer `xnu-on-pi` branch is a BCM2712 backport reference (ADR 0009).
No XNU patch, build, or Pi 5 run exists yet. The immediate milestone is M2: payload format +
loader handoff + XNU board config/platform expert.

## Hard rules (short version)

- **Never commit Apple binaries.** No IPSW, DMG, kernelcache, IM4P payload, device tree, userland,
  keys or certificates.
- **No activation/DRM circumvention.**
- **Do not invent facts.** Every address, clock, IRQ or register claim needs a row in
  `docs/facts.md` with a source and confidence.
- **Do not run destructive hardware commands.** No `dd` to a device, no EEPROM writes, no
  repartitioning without an explicit human confirmation.
- **QEMU before hardware.** If a change cannot be tested under QEMU, say exactly what hardware
  test is required.
- **Kernel changes go in `patches/`**, one logical change per patch, exported with
  `git format-patch`.
- **Do not change the XNU pin** (`xnu-8796.141.3`) without an ADR.
- **Do not add a dependency** without updating `pyproject.toml`, `scripts/bootstrap.sh`, and CI.

## Definition of done

For a code change:

- `make check` passes.
- `make loader BOARD=pi5`, `BOARD=qemu-raspi4b`, and `BOARD=qemu-virt` build.
- New host code has a test; new C code is `clang-format` clean and builds with `-Werror`.
- The change is documented in `CHANGELOG.md`; a milestone change updates `ROADMAP.md`.

For a fact/research change:

- A row in `docs/facts.md` with source and confidence.
- If the fact is `C`, an entry in `docs/open-questions.md` with a test.
- If it is a decision, an ADR in `docs/decisions/`.

## How to answer a question

1. Check `docs/facts.md` first.
2. Check `docs/open-questions.md` — someone may have tried it.
3. Prefer a primary source: DTS line, datasheet, XNU source, measured serial log, inspected file.
4. If you cannot answer, add/keep it in `docs/open-questions.md` with a concrete test. Do not
   invent a number to "unblock" yourself.
5. If a source contradicts a fact, fix the fact and note the contradiction in the commit.

## Where to write

- New research: `docs/research/YYYY-MM-DD-short-title.md`.
- New fact: `docs/facts.md`.
- New unknown: `docs/open-questions.md`.
- New decision: `docs/decisions/NNNN-title.md` and the index.
- New hardware detail: `docs/hardware/pi5.md` + `docs/facts.md`.

## Testing protocol

- L0: `pytest`, `ruff`, `shellcheck`, `clang-format`, `mkdocs --strict`.
- L1: QEMU `raspi4b` for GIC/PL011/timer; `qemu-virt` for generic ARM64.
- L2: Pi 5 smoke via TFTP/FAT, serial marker, power cycle.
- L3: driver-specific hardware runs, batched, with logs.
- L4: full tvOS `PineBoard`, milestone only.

See `docs/testing.md` for the exact commands.

## Safety and legal

- 3.3 V only on the debug connector; no VCC.
- Keep a known-good payload slot and a bootable SD fallback.
- Do not distribute Apple firmware/userland; see `NOTICE`, `THIRD_PARTY_LICENSES.md`, `docs/tvos.md`.
- Nothing here is legal advice.

## If you are stuck

Record the question in `docs/open-questions.md`, state what you tried, and leave the repo in a
building state. A precise unknown is more useful than a confident guess.
