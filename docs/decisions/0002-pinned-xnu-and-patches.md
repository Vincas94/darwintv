# ADR 0002 — Pin XNU and carry a patch series

- **Status:** accepted
- **Date:** 2026-11-08

## Context

The Pi 5 port needs changes across XNU: board config, platform expert, GICv2, PL011, timer,
SDHCI, stubs and userland-facing services. Keeping a full XNU fork in the repository makes the
project huge and the diff unreviewable.

## Decision

- Pin **`xnu-8796.141.3`** (the iOS/tvOS 16 generation).
- `scripts/fetch-xnu.sh` clones it into `third_party/xnu` (gitignored).
- `patches/NNNN-description.patch` is the only place kernel changes live.
- `scripts/apply-patches.sh` applies the series to a fresh checkout; `make xnu-patches` wraps it.
- CI's `XNU patches` workflow fetches the tag and checks that the series applies cleanly.
- Patches derived from XNU are **APSL-2.0**; keep Apple's notices.

## Consequences

- The main repo is small and the kernel diff is reviewable.
- A new XNU tag requires a patch refresh; that is deliberate and visible.
- The build itself still happens on macOS (XNU needs Xcode/Apple clang); CI only validates that
  the patches apply on Linux. A macOS build workflow can be added when the first patch lands.
