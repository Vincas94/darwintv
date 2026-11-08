from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "LICENSE",
    "NOTICE",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "docs/index.md",
    "docs/hardware/pi5.md",
    "docs/boot-flow.md",
    "docs/tvos.md",
    "bootloader/linker.ld",
    "bootloader/src/start.S",
    "configs/pi5/config.txt",
    "tools/adt/adt.py",
    "tools/ipsw/extract.py",
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
