# Architecture decision records

An ADR records a decision that is expensive to reverse. Add one when you change the target,
the boot medium, the test strategy, the XNU pin, or the legal boundary.

| ADR | Decision |
|---|---|
| [0001](0001-fresh-repo.md) | Fresh repository; pinned XNU + patches, not a fork |
| [0002](0002-pinned-xnu-and-patches.md) | Pin `xnu-8796.141.3`; carry a patch series |
| [0003](0003-target-appletv5-3-tvos-16.md) | Target Apple TV HD / tvOS 16.6 |
| [0004](0004-qemu-first.md) | QEMU before hardware |
| [0005](0005-update-workflow.md) | File-based updates, not reflashing |
| [0006](0006-large-image-boot.md) | Block-backed large images; RAM disk for bring-up |
| [0007](0007-test-strategy.md) | Test pyramid; hardware smoke; UART fallback |
| [0008](0008-ethernet-first.md) | Ethernet/TFTP as the primary hardware loop |
| [0009](0009-bcm2712-backport.md) | Backport BCM2712 to `xnu-8796.141.3`; 16 KiB pages; GICv2 first |

## Template

```markdown
# ADR NNNN — Title

- **Status:** proposed | accepted | superseded
- **Date:** YYYY-MM-DD
- **Deciders:** ...

## Context
...
## Decision
...
## Consequences
...
## Alternatives considered
...
```
