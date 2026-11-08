# Contributing to DarwinTV

Thanks for helping. This is a research project; correctness, reproducibility and a clear
paper trail matter more than speed.

## Scope

Good first contributions:

- hardware facts and corrections (with a source: DTS line, datasheet page, or serial log),
- host-side tools (`tools/adt`, `tools/ipsw`, `tools/rootfs`),
- documentation and ADRs,
- loader and driver code that can be tested under QEMU,
- reproductions and failure reports from real Pi 5 hardware.

Out of scope:

- distributing Apple IPSWs, kernelcaches, device trees, userland, keys or activation material,
- bypassing activation/DRM or Apple's security model,
- "make it look like an iPhone to Apple's servers".

## Development setup

```sh
./scripts/bootstrap.sh
source .venv/bin/activate
make check
```

`scripts/bootstrap.sh` installs the AArch64 cross compiler, QEMU (if available), Python dev
dependencies, `clang-format`, `shellcheck` and pre-commit hooks.

## Commit style

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat(bootloader): add PL011 console for the Pi 5
fix(adt): encode the GIC reg property as four u64s
docs(tvos): record the AppleTV5,3 IPSW layout
```

Sign off your commits with the Developer Certificate of Origin:

```sh
git commit -s
```

## Patches against XNU

We do **not** keep a 175 MB XNU fork in this repository.

1. `scripts/fetch-xnu.sh` checks out `apple-oss-distributions/xnu` at the pinned tag.
2. Make your change in `third_party/xnu`.
3. Export it:
   ```sh
   git -C third_party/xnu format-patch -1 --stdout > patches/0001-my-change.patch
   ```
4. Name patches `NNNN-short-description.patch`, one logical change per patch.
5. `scripts/apply-patches.sh` must apply the whole series cleanly to a fresh checkout.

Patches derived from XNU are APSL-2.0. Keep Apple's copyright notices.

## AI-assisted contributions

AI assistance is welcome. By opening a PR you assert that:

- you can explain every line of the change,
- you did not paste code from a project whose license forbids it,
- you disclosed the tools used in the PR description,
- you ran the checks and, for hardware changes, attached the serial log.

## Pull request checklist

- [ ] `make check` passes.
- [ ] `make loader` builds for `BOARD=pi5` and `BOARD=qemu-raspi4b`.
- [ ] New hardware facts cite a source in `docs/hardware/pi5.md` or an ADR.
- [ ] `CHANGELOG.md` updated.
- [ ] No Apple binaries, IPSWs, keys or generated images are committed.
- [ ] PR description says how the change was tested (QEMU version, board revision, firmware).

## Reporting hardware results

Include:

- Pi 5 model and RAM size,
- EEPROM/bootloader version (`rpi-eeprom-update`),
- `config.txt`,
- the full serial log from power-on,
- what you expected and what happened.

Do not open a public issue containing a device serial number, calibration data or Apple keys.
