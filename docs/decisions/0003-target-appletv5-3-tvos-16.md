# ADR 0003 — Target Apple TV HD (`AppleTV5,3`) and tvOS 16.6

- **Status:** accepted
- **Date:** 2026-11-08

## Context

The Pi 5's Cortex-A76 is ARMv8.2-A and has **no pointer authentication** (ARMv8.3). Apple's
newer A12/A15 userlands may be arm64e (PAC), which would fault on the A76. The kernel generation
must match the userland's expectations.

## Decision

- Target **Apple TV HD (`AppleTV5,3`, A8, `j42dap`)**, **tvOS 16.6 (20M73)**.
- Build XNU from **`xnu-8796.141.3`**, non-PAC arm64, 16K pages.
- Use the Apple TV HD's 1080p UI as the display target.
- Keep `AppleTV6,2` (A10X) as a secondary target; both are arm64 and non-PAC.

## Consequences

- The userland is arm64 and runs on the A76 without PAC.
- 1080p software rendering is ~1.5× the pixels of a 1125×2436 phone panel; expect a slow UI.
- Apple TV 4K 2nd/3rd gen (A12/A15) userlands are out of scope until the PAC question is solved.
- tvOS 16.6's userland is old enough to be well documented by `ios-sweet`'s iOS 16 work.
