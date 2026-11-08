# Contributing

The canonical guide is [`CONTRIBUTING.md`](https://github.com/Vincas94/darwintv/blob/main/CONTRIBUTING.md).

Quick version:

```sh
./scripts/bootstrap.sh
source .venv/bin/activate
make check
make loader BOARD=pi5
```

- Use Conventional Commits and DCO sign-off (`git commit -s`).
- Kernel changes go in `patches/`, one logical change per patch.
- No Apple firmware, IPSWs, kernelcaches, device trees, userland or keys in git.
- New hardware facts need a source in [Raspberry Pi 5 hardware](hardware/pi5.md) or an ADR.
- AI-assisted contributions are welcome when disclosed and understood.

Read [`AGENTS.md`](https://github.com/Vincas94/darwintv/blob/main/AGENTS.md) if you use an AI agent.
