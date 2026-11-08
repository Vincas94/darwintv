"""DarwinTV payload format.

The bootloader loads ``payload.bin`` (from TFTP/FAT, usually at ``0x08000000``)
and validates it before copying anything. Layout, little-endian::

    header      128 bytes
    segments    nsegs * 40 bytes
    ADT         aligned 16
    cmdline     aligned 16, NUL-terminated
    segment data aligned 16

The header's CRC32 covers the whole file with the CRC field zeroed. The
bootloader can compute it without allocating a second copy.
"""

from __future__ import annotations

import argparse
import struct
import zlib
from dataclasses import dataclass, replace
from pathlib import Path

from tools.adt.adt import pi5_adt

MAGIC = b"DTVPLD01"
VERSION = 1
HEADER_SIZE = 128
SEGMENT_SIZE = 40
ALIGN = 16
HEADER_FORMAT = "<8sII9QII32s"
CRC_OFFSET = 92

LC_SEGMENT_64 = 0x19
LC_UNIXTHREAD = 0x5
LC_MAIN = 0x80000028
MH_MAGIC_64 = 0xFEEDFACF


def align_up(value: int, alignment: int = ALIGN) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


@dataclass(frozen=True)
class Segment:
    """One Mach-O segment copied by the bootloader."""

    file_offset: int
    file_size: int
    vmaddr: int
    vmsize: int
    reserved: int = 0

    def pack(self) -> bytes:
        return struct.pack(
            "<5Q", self.file_offset, self.file_size, self.vmaddr, self.vmsize, self.reserved
        )

    @classmethod
    def unpack_from(cls, data: bytes, offset: int) -> Segment:
        return cls(*struct.unpack_from("<5Q", data, offset))


@dataclass(frozen=True)
class PayloadHeader:
    magic: bytes
    version: int
    header_size: int
    total_size: int
    entry_va: int
    virt_base: int
    phys_base: int
    mem_size: int
    adt_offset: int
    adt_size: int
    cmdline_offset: int
    cmdline_size: int
    nsegs: int
    crc32: int = 0
    reserved: bytes = b"\0" * 32

    def pack(self) -> bytes:
        return struct.pack(
            HEADER_FORMAT,
            self.magic,
            self.version,
            self.header_size,
            self.total_size,
            self.entry_va,
            self.virt_base,
            self.phys_base,
            self.mem_size,
            self.adt_offset,
            self.adt_size,
            self.cmdline_offset,
            self.cmdline_size,
            self.nsegs,
            self.crc32,
            self.reserved,
        )

    @classmethod
    def unpack(cls, data: bytes) -> PayloadHeader:
        if len(data) < HEADER_SIZE:
            raise ValueError("payload header is truncated")
        fields = struct.unpack_from(HEADER_FORMAT, data, 0)
        return cls(*fields)


@dataclass(frozen=True)
class MachOSegment:
    """A segment in the source Mach-O file."""

    source_offset: int
    file_size: int
    vmaddr: int
    vmsize: int


@dataclass(frozen=True)
class MachO:
    entry: int
    segments: tuple[MachOSegment, ...]


def compute_crc(data: bytes) -> int:
    """CRC32 of the whole payload with the header CRC field zeroed."""
    if len(data) < HEADER_SIZE:
        raise ValueError("payload is shorter than the header")
    raw = bytearray(data)
    raw[CRC_OFFSET : CRC_OFFSET + 4] = b"\0\0\0\0"
    return zlib.crc32(raw) & 0xFFFFFFFF


def parse_macho(data: bytes) -> MachO:
    """Extract loadable segments and the entry point from an arm64 Mach-O."""
    if len(data) < 32:
        raise ValueError("Mach-O header is truncated")
    magic, _cputype, _cpusubtype, _filetype, ncmds, sizeofcmds, _flags, _res = struct.unpack_from(
        "<IiiIIIII", data, 0
    )
    if magic != MH_MAGIC_64:
        raise ValueError(f"not a little-endian 64-bit Mach-O: 0x{magic:08x}")
    if 32 + sizeofcmds > len(data):
        raise ValueError("Mach-O load commands extend past the file")

    segments: list[MachOSegment] = []
    entry = 0
    text_vmaddr = 0
    offset = 32
    for _ in range(ncmds):
        if offset + 8 > len(data):
            raise ValueError("Mach-O load command is truncated")
        cmd, cmdsize = struct.unpack_from("<II", data, offset)
        if cmdsize < 8 or offset + cmdsize > len(data):
            raise ValueError(f"invalid load command size {cmdsize}")
        if cmd == LC_SEGMENT_64:
            if cmdsize < 72:
                raise ValueError("LC_SEGMENT_64 is too small")
            name = data[offset + 8 : offset + 24].split(b"\0")[0].decode(errors="replace")
            vmaddr, vmsize, fileoff, filesize = struct.unpack_from("<4Q", data, offset + 24)
            if name == "__TEXT":
                text_vmaddr = vmaddr
            if filesize:
                if fileoff + filesize > len(data):
                    raise ValueError(f"segment {name} extends past the file")
                segments.append(MachOSegment(fileoff, filesize, vmaddr, vmsize))
        elif cmd == LC_UNIXTHREAD:
            if cmdsize < 288:
                raise ValueError("LC_UNIXTHREAD is too small")
            entry = struct.unpack_from("<Q", data, offset + 272)[0]
        elif cmd == LC_MAIN:
            if cmdsize < 16:
                raise ValueError("LC_MAIN is too small")
            entryoff = struct.unpack_from("<Q", data, offset + 8)[0]
            entry = text_vmaddr + entryoff
        offset += cmdsize

    if not segments:
        raise ValueError("Mach-O has no loadable segments")
    if entry == 0:
        raise ValueError("Mach-O has no entry point (LC_UNIXTHREAD or LC_MAIN)")
    return MachO(entry=entry, segments=tuple(segments))


def build_payload(
    kernel: bytes,
    *,
    virt_base: int = 0xFFFFFFF006000000,
    phys_base: int = 0x02000000,
    mem_size: int = 0x0FE000000,
    cmdline: str = "debug=0xc serial=1 cpus=1 keepsyms=1 -noprogress",
    adt: bytes | None = None,
    ramdisk: tuple[int, int] | None = None,
) -> tuple[bytes, PayloadHeader]:
    """Pack a kernel Mach-O, an ADT and a command line into payload.bin."""
    macho = parse_macho(kernel)

    if adt is None:
        adt = pi5_adt(
            dram_base=phys_base,
            dram_size=mem_size,
            cmdline=cmdline,
            ramdisk=ramdisk,
        )
    cmdline_bytes = cmdline.encode() + b"\0"

    for seg in macho.segments:
        if seg.vmaddr < virt_base:
            raise ValueError(f"segment 0x{seg.vmaddr:x} is below virt_base 0x{virt_base:x}")
        if seg.vmaddr - virt_base + seg.vmsize > mem_size:
            raise ValueError("segment does not fit in the kernel memory window")
    if macho.entry < virt_base:
        raise ValueError("entry point is below virt_base")

    nsegs = len(macho.segments)
    table_end = HEADER_SIZE + nsegs * SEGMENT_SIZE
    adt_offset = align_up(table_end)
    adt_size = len(adt)
    cmdline_offset = align_up(adt_offset + adt_size)
    cmdline_size = len(cmdline_bytes)
    data_offset = align_up(cmdline_offset + cmdline_size)

    out = bytearray(data_offset)
    out[adt_offset : adt_offset + adt_size] = adt
    out[cmdline_offset : cmdline_offset + cmdline_size] = cmdline_bytes

    built: list[Segment] = []
    for seg in macho.segments:
        out += b"\0" * (-len(out) & (ALIGN - 1))
        file_offset = len(out)
        out += kernel[seg.source_offset : seg.source_offset + seg.file_size]
        built.append(
            Segment(
                file_offset=file_offset,
                file_size=seg.file_size,
                vmaddr=seg.vmaddr,
                vmsize=seg.vmsize,
            )
        )

    header = PayloadHeader(
        magic=MAGIC,
        version=VERSION,
        header_size=HEADER_SIZE,
        total_size=len(out),
        entry_va=macho.entry,
        virt_base=virt_base,
        phys_base=phys_base,
        mem_size=mem_size,
        adt_offset=adt_offset,
        adt_size=adt_size,
        cmdline_offset=cmdline_offset,
        cmdline_size=cmdline_size,
        nsegs=nsegs,
        crc32=0,
    )
    out[0:HEADER_SIZE] = header.pack()
    for index, seg in enumerate(built):
        struct.pack_into(
            "<5Q",
            out,
            HEADER_SIZE + index * SEGMENT_SIZE,
            seg.file_offset,
            seg.file_size,
            seg.vmaddr,
            seg.vmsize,
            seg.reserved,
        )
    header = replace(header, crc32=compute_crc(bytes(out)))
    out[0:HEADER_SIZE] = header.pack()
    return bytes(out), header


def parse_payload(data: bytes) -> tuple[PayloadHeader, tuple[Segment, ...], bytes, bytes]:
    """Validate and decode a payload. Raises ValueError on any inconsistency."""
    header = PayloadHeader.unpack(data)
    if header.magic != MAGIC:
        raise ValueError(f"bad payload magic: {header.magic!r}")
    if header.version != VERSION:
        raise ValueError(f"unsupported payload version {header.version}")
    if header.header_size < HEADER_SIZE:
        raise ValueError("payload header size is too small")
    if header.total_size != len(data):
        raise ValueError(f"payload size mismatch: header {header.total_size}, file {len(data)}")
    if header.nsegs == 0 or header.nsegs > 64:
        raise ValueError(f"invalid segment count {header.nsegs}")
    table_end = header.header_size + header.nsegs * SEGMENT_SIZE
    if table_end > header.total_size:
        raise ValueError("segment table extends past the payload")
    if header.adt_offset + header.adt_size > header.total_size:
        raise ValueError("ADT extends past the payload")
    if header.cmdline_offset + header.cmdline_size > header.total_size:
        raise ValueError("command line extends past the payload")
    if compute_crc(data) != header.crc32:
        raise ValueError("payload CRC mismatch")

    segments = tuple(
        Segment.unpack_from(data, header.header_size + i * SEGMENT_SIZE)
        for i in range(header.nsegs)
    )
    for seg in segments:
        if seg.file_offset + seg.file_size > header.total_size:
            raise ValueError("segment data extends past the payload")
        if seg.vmaddr < header.virt_base:
            raise ValueError("segment is below virt_base")
        if seg.vmaddr - header.virt_base + seg.vmsize > header.mem_size:
            raise ValueError("segment does not fit in the kernel window")
    if header.entry_va < header.virt_base:
        raise ValueError("entry point is below virt_base")

    adt = data[header.adt_offset : header.adt_offset + header.adt_size]
    cmdline = data[header.cmdline_offset : header.cmdline_offset + header.cmdline_size].rstrip(
        b"\0"
    )
    return header, segments, adt, cmdline


def info_text(data: bytes) -> str:
    header, segments, adt, cmdline = parse_payload(data)
    lines = [
        f"magic:      {header.magic.decode(errors='replace')} v{header.version}",
        f"size:       {header.total_size} bytes",
        f"entry:      0x{header.entry_va:016x}",
        f"virt_base:  0x{header.virt_base:016x}",
        f"phys_base:  0x{header.phys_base:016x}",
        f"mem_size:   0x{header.mem_size:016x}",
        f"adt:        offset 0x{header.adt_offset:x}, {header.adt_size} bytes",
        f"cmdline:    {cmdline.decode(errors='replace')!r}",
        f"segments:   {header.nsegs}",
    ]
    for i, seg in enumerate(segments):
        lines.append(
            f"  [{i}] file 0x{seg.file_offset:08x}+0x{seg.file_size:x} "
            f"va 0x{seg.vmaddr:016x}+0x{seg.vmsize:x}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DarwinTV payload packer")
    sub = parser.add_subparsers(dest="command", required=True)

    pack = sub.add_parser("pack", help="pack a kernel Mach-O")
    pack.add_argument("--kernel", type=Path, required=True)
    pack.add_argument("--out", type=Path, required=True)
    pack.add_argument("--adt", type=Path)
    pack.add_argument("--cmdline", default="debug=0xc serial=1 cpus=1 keepsyms=1 -noprogress")
    pack.add_argument("--virt-base", type=lambda x: int(x, 0), default=0xFFFFFFF006000000)
    pack.add_argument("--phys-base", type=lambda x: int(x, 0), default=0x02000000)
    pack.add_argument("--mem-size", type=lambda x: int(x, 0), default=0x0FE000000)
    pack.add_argument("--ramdisk-base", type=lambda x: int(x, 0))
    pack.add_argument("--ramdisk-size", type=lambda x: int(x, 0))

    info = sub.add_parser("info", help="validate and print a payload")
    info.add_argument("payload", type=Path)

    args = parser.parse_args(argv)

    if args.command == "info":
        print(info_text(args.payload.read_bytes()))
        return 0

    ramdisk = None
    if args.ramdisk_base is not None or args.ramdisk_size is not None:
        if args.ramdisk_base is None or args.ramdisk_size is None:
            parser.error("--ramdisk-base and --ramdisk-size must be given together")
        ramdisk = (args.ramdisk_base, args.ramdisk_size)

    adt = args.adt.read_bytes() if args.adt else None
    blob, header = build_payload(
        args.kernel.read_bytes(),
        virt_base=args.virt_base,
        phys_base=args.phys_base,
        mem_size=args.mem_size,
        cmdline=args.cmdline,
        adt=adt,
        ramdisk=ramdisk,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(blob)
    print(f"wrote {args.out} ({header.total_size} bytes, {header.nsegs} segments)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
