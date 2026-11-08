# Claude instructions

Read `AGENTS.md` first; it is the source of truth. Claude-specific notes:

- Use plan mode for changes that touch more than one subsystem.
- Before proposing a PR, run `make check` and `make loader BOARD=pi5`.
- Never commit generated binaries (`build/`, `*.img`, `*.elf`).
- When you add a hardware fact, cite the DTS line or datasheet in the same commit.
- When a change is architectural, write an ADR in `docs/decisions/` instead of a long PR comment.
- Do not paste code from `xnu-on-pi`, `ios-sweet` or HakiOS unless the license allows it and the
  source is attributed. Prefer a clean-room implementation from the documented behavior.
