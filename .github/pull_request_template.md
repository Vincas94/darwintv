## What changed

<!-- One or two sentences. Link the issue if there is one. -->

## Why

<!-- The problem, the hardware fact, or the failure this fixes. -->

## How it was tested

- [ ] `make check`
- [ ] `make loader BOARD=pi5`
- [ ] `make loader BOARD=qemu-raspi4b`
- [ ] QEMU `raspi4b` boot (attach log)
- [ ] Real Pi 5 (board revision, EEPROM version, serial log)

## Checklist

- [ ] No Apple firmware, IPSW, kernelcache, device tree, userland or keys committed
- [ ] Hardware facts cite `docs/hardware/pi5.md` or an ADR
- [ ] `CHANGELOG.md` updated
- [ ] `ROADMAP.md` updated if a milestone changed
- [ ] AI tools disclosed (if used)
- [ ] Commits are signed off (`git commit -s`)

## Serial log

```text
<paste from power-on to the failure or success>
```
