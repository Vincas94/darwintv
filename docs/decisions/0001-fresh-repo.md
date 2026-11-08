# ADR 0001 — Start a fresh repository, not a fork

- **Status:** accepted
- **Date:** 2026-11-08
- **Deciders:** DarwinTV maintainers

## Context

There are three relevant upstreams:

- `apple-oss-distributions/xnu` — the kernel itself (APSL-2.0, ~175 MB tree).
- `tansanrao/xnu-on-pi` — a Raspberry Pi 4 loader/research project.
- `tansanrao/xnu` — an XNU fork with branches `rpi4b-bringup` and `xnu-on-pi5`.
- `ios-sweet` and HakiOS — phone ports with mature userland bring-up notes.

Forking one of them would make that project's scope, history and release process the center of
DarwinTV. DarwinTV needs a different center: a Pi 5 port, a tvOS target, a reproducible loader,
and a documented patch series.

## Decision

1. Start a **fresh repository** (`darwintv`).
2. Pin Apple's XNU at **`xnu-8796.141.3`** and fetch it into `third_party/xnu` (gitignored).
3. Keep kernel changes in **`patches/`** as `git format-patch` files.
4. Treat `xnu-on-pi`, `ios-sweet` and HakiOS as **references**, not forks.
5. If the port needs to be contributed upstream, maintain a **separate fork** of
   `tansanrao/xnu` (or Apple's XNU) for that purpose; the main repo exports the same patches.

## Consequences

- The repository stays small and reviewable; CI can apply the patch series to a fresh XNU.
- Rebase to a newer XNU is a patch refresh, not a merge of two forks.
- We lose upstream fork conveniences (GitHub's "compare across forks", submodule history). The
  `patches/` + `scripts/fetch-xnu.sh` flow replaces them.
- Attribution is explicit in `NOTICE` and `THIRD_PARTY_LICENSES.md`.

## Alternatives considered

- **Fork `xnu-on-pi`:** rejected; it centers a Pi 4 loader and has no tvOS scope.
- **Fork `tansanrao/xnu` as the main repo:** rejected; a 175 MB fork hides the loader, tools,
  docs and rootfs work, and makes review hard.
- **Git submodule of XNU:** rejected for now; submodules complicate CI and are easy to leave
  dirty. `scripts/fetch-xnu.sh` is simpler and explicit.
