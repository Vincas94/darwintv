"""List and extract entries from a local Apple IPSW.

An IPSW is a ZIP file. This module deliberately works on a local file only:
downloading Apple firmware is the user's responsibility, and no Apple data is
committed to this repository.

Remote range extraction is a future feature; see ``docs/tvos.md`` for the
``curl --range`` recipe used during the initial survey.
"""

from __future__ import annotations

import argparse
import hashlib
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


def verify(path: Path, *, sha1: str | None = None, sha256: str | None = None) -> tuple[str, str]:
    """Hash an IPSW, optionally comparing against expected values."""
    h1 = hashlib.sha1()
    h256 = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            h1.update(chunk)
            h256.update(chunk)
    got1 = h1.hexdigest()
    got256 = h256.hexdigest()
    if sha1 is not None and got1.lower() != sha1.lower():
        raise ValueError(f"sha1 mismatch: {got1} != {sha1}")
    if sha256 is not None and got256.lower() != sha256.lower():
        raise ValueError(f"sha256 mismatch: {got256} != {sha256}")
    return got1, got256


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List or extract an IPSW")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list entries")
    list_parser.add_argument("ipsw", type=Path)

    extract_parser = subparsers.add_parser("extract", help="extract one entry")
    extract_parser.add_argument("ipsw", type=Path)
    extract_parser.add_argument("name")
    extract_parser.add_argument("--out", type=Path, default=Path("build/ipsw"))

    verify_parser = subparsers.add_parser("verify", help="check IPSW hashes")
    verify_parser.add_argument("ipsw", type=Path)
    verify_parser.add_argument("--sha1")
    verify_parser.add_argument("--sha256")

    args = parser.parse_args(argv)

    if args.command == "list":
        for info in list_entries(args.ipsw):
            print(f"{info.file_size:>12}  {info.filename}")
        return 0

    if args.command == "verify":
        got1, got256 = verify(args.ipsw, sha1=args.sha1, sha256=args.sha256)
        print(f"sha1:   {got1}")
        print(f"sha256: {got256}")
        return 0

    target = extract(args.ipsw, args.name, args.out)
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
