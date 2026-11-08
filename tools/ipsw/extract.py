"""List and extract entries from a local Apple IPSW.

An IPSW is a ZIP file. This module deliberately works on a local file only:
downloading Apple firmware is the user's responsibility, and no Apple data is
committed to this repository.

Remote range extraction is a future feature; see ``docs/tvos.md`` for the
``curl --range`` recipe used during the initial survey.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def list_entries(path: Path) -> list[zipfile.ZipInfo]:
    """Return the ZIP entries of an IPSW, in central-directory order."""
    with zipfile.ZipFile(path) as archive:
        return archive.infolist()


def extract(path: Path, name: str, destination: Path) -> Path:
    """Extract one entry to ``destination`` and return the written path."""
    with zipfile.ZipFile(path) as archive:
        info = archive.getinfo(name)
        target = destination / Path(info.filename).name
        target.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info) as source, target.open("wb") as sink:
            while chunk := source.read(1024 * 1024):
                sink.write(chunk)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List or extract an IPSW")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list entries")
    list_parser.add_argument("ipsw", type=Path)

    extract_parser = subparsers.add_parser("extract", help="extract one entry")
    extract_parser.add_argument("ipsw", type=Path)
    extract_parser.add_argument("name")
    extract_parser.add_argument("--out", type=Path, default=Path("build/ipsw"))

    args = parser.parse_args(argv)

    if args.command == "list":
        for info in list_entries(args.ipsw):
            print(f"{info.file_size:>12}  {info.filename}")
        return 0

    target = extract(args.ipsw, args.name, args.out)
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
