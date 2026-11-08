# GitHub Copilot instructions

DarwinTV is a from-source XNU bring-up for the Raspberry Pi 5. Follow `AGENTS.md`.

- Never suggest committing Apple binaries, IPSWs, kernelcaches, device trees, userland or keys.
- Never suggest activation/DRM circumvention.
- Hardware addresses must match `docs/hardware/pi5.md`; do not invent them.
- Kernel changes belong in `patches/`, not in a vendored XNU tree.
- Prefer C11 freestanding code for the loader; Python 3.11+ with type hints for host tools.
- Suggest `make check` and `make loader BOARD=pi5` before a PR.
