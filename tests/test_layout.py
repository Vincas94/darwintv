from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "STATUS.md",
    "LICENSE",
    "NOTICE",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "docs/index.md",
    "docs/facts.md",
    "docs/open-questions.md",
    "docs/ai-handoff.md",
    "docs/building-xnu.md",
    "docs/ipsw.md",
    "docs/patches.md",
    "docs/glossary.md",
    "docs/safety.md",
    "docs/hardware/pi5.md",
    "docs/hardware/test-rig.md",
    "docs/boot-flow.md",
    "docs/tvos.md",
    "bootloader/linker.ld",
    "bootloader/src/start.S",
    "configs/pi5/config.txt",
    "patches/README.md",
    "tools/adt/adt.py",
    "tools/ipsw/extract.py",
    "tools/payload/payload.py",
    "scripts/mkpayload.sh",
    "tools/rootfs/README.md",
]


def test_required_files_exist() -> None:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    assert missing == []


def test_no_apple_firmware_is_committed() -> None:
    forbidden = {".ipsw", ".dmg", ".im4p", ".im4p.plist", ".trustcache"}
    found = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and any(path.name.endswith(suffix) for suffix in forbidden)
    ]
    assert found == []


def test_required_files_are_tracked() -> None:
    import subprocess

    if not (ROOT / ".git").exists():
        import pytest

        pytest.skip("not a git checkout")
    tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
    missing = [name for name in REQUIRED if name not in tracked]
    assert missing == []
