import struct

import pytest

from tools.payload.payload import (
    HEADER_SIZE,
    MAGIC,
    VERSION,
    build_payload,
    info_text,
    parse_macho,
    parse_payload,
)


def make_macho() -> tuple[bytes, int, int]:
    vmaddr = 0xFFFFFFF007004000
    entry = vmaddr + 0x100

    segment = struct.pack(
        "<II16s4QIIII",
        0x19,  # LC_SEGMENT_64
        72,
        b"__TEXT".ljust(16, b"\0"),
        vmaddr,
        0x1000,
        0,
        0x1000,
        7,
        5,
        0,
        0,
    )
    unix_thread = bytearray(288)
    struct.pack_into("<II", unix_thread, 0, 0x5, 288)  # LC_UNIXTHREAD
    struct.pack_into("<II", unix_thread, 8, 6, 68)  # ARM_THREAD_STATE64
    struct.pack_into("<Q", unix_thread, 272, entry)

    commands = segment + bytes(unix_thread)
    header = struct.pack(
        "<IiiIIIII",
        0xFEEDFACF,
        0x0100000C,
        0,
        2,
        2,
        len(commands),
        0,
        0,
    )
    image = bytearray(0x1000)
    image[:32] = header
    image[32 : 32 + len(commands)] = commands
    image[0x800:0x808] = b"DTVKRNL!"
    return bytes(image), vmaddr, entry


def test_parse_macho_finds_segment_and_entry() -> None:
    image, vmaddr, entry = make_macho()
    macho = parse_macho(image)
    assert macho.entry == entry
    assert len(macho.segments) == 1
    assert macho.segments[0].vmaddr == vmaddr
    assert macho.segments[0].source_offset == 0
    assert macho.segments[0].file_size == 0x1000


def test_pack_and_parse_roundtrip() -> None:
    image, vmaddr, entry = make_macho()
    blob, header = build_payload(
        image,
        virt_base=0xFFFFFFF006000000,
        phys_base=0x02000000,
        mem_size=0x0FE000000,
        cmdline="debug=0xc serial=1",
    )
    assert header.magic == MAGIC
    assert header.version == VERSION
    assert header.header_size == HEADER_SIZE
    assert header.nsegs == 1
    assert header.entry_va == entry
    assert header.phys_base == 0x02000000
    assert header.virt_base == 0xFFFFFFF006000000
    assert len(blob) == header.total_size

    parsed, segments, adt, cmdline = parse_payload(blob)
    assert parsed.crc32 == header.crc32
    assert len(segments) == 1
    assert segments[0].vmaddr == vmaddr
    assert blob[segments[0].file_offset + 0x800 : segments[0].file_offset + 0x808] == b"DTVKRNL!"
    assert b"brcm,bcm2712" in adt
    assert cmdline == b"debug=0xc serial=1"


def test_crc_detects_corruption() -> None:
    image, _, _ = make_macho()
    blob, _ = build_payload(image)
    corrupted = bytearray(blob)
    corrupted[-1] ^= 0xFF
    with pytest.raises(ValueError, match="CRC"):
        parse_payload(bytes(corrupted))


def test_bad_macho_magic_is_rejected() -> None:
    with pytest.raises(ValueError, match="Mach-O"):
        parse_macho(b"\0" * 64)


def test_ramdisk_property_reaches_the_adt() -> None:
    image, _, _ = make_macho()
    blob, _ = build_payload(image, ramdisk=(0x100000000, 0x100000))
    _, _, adt, _ = parse_payload(blob)
    assert b"RAMDisk" in adt


def test_info_text_mentions_segments() -> None:
    image, _, _ = make_macho()
    blob, _ = build_payload(image)
    text = info_text(blob)
    assert "segments:   1" in text
    assert "phys_base:  0x0000000002000000" in text
