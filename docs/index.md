# DarwinTV

**Apple TV's tvOS userland on a Raspberry Pi 5, via a from-source XNU port.**

DarwinTV is an independent research project. It ports Apple's open-source XNU kernel to the
Raspberry Pi 5 (BCM2712) and, eventually, runs the unmodified tvOS 16 userland — `launchd`,
`backboardd`, `PineBoard` — on top of it.

!!! warning "Pre-alpha"
    There is no working Pi 5 port yet. The first milestone is XNU printing its banner on the
    Pi 5 debug UART. Expect panics, missing drivers and slow software rendering for a long time.

## Start here

- [Getting started](getting-started.md) — build the M1 loader and wire the serial console.
- [Raspberry Pi 5 hardware](hardware/pi5.md) — addresses, UART, boot configuration.
- [Boot flow](boot-flow.md) — firmware → loader → XNU → userland.
- [tvOS notes](tvos.md) — which Apple TV to target, what is in the IPSW, what `PineBoard` needs.
- [Initial survey](research/2026-11-08-initial-survey.md) — the research that motivated the project.
- [Decisions](decisions/0001-fresh-repo.md) — why this is a fresh repo and not a fork.

## The shape of the project

```text
Pi 5 firmware → DarwinTV loader → XNU (patched xnu-8796.141.3)
                                      ├─ PL011 console
                                      ├─ GIC-400 + architectural timer
                                      ├─ SDHCI + HFS+ root
                                      └─ launchd → backboardd → PineBoard
```

## What we do not do

- We do not distribute Apple firmware, IPSWs, kernelcaches, device trees or userland.
- We do not bypass activation, DRM or Apple's security model.
- We do not pretend the Pi 5 is an Apple TV to Apple's servers.

See [tvOS notes](tvos.md) for the legal and practical boundaries.
