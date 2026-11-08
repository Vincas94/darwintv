import struct

import pytest

from tools.adt.adt import Node, pi5_adt, u32, u64


def test_empty_node_has_implicit_name_property() -> None:
    blob = Node("device-tree").build()
    nprops, nchildren = struct.unpack_from("<II", blob, 0)
    assert (nprops, nchildren) == (1, 0)


def test_property_name_is_padded_to_32_bytes() -> None:
    blob = Node("device-tree").build()
    assert blob[8:40].rstrip(b"\0") == b"name"


def test_u32_and_u64_are_little_endian() -> None:
    assert u32(0x01020304) == b"\x04\x03\x02\x01"
    assert u64(0x0102030405060708) == b"\x08\x07\x06\x05\x04\x03\x02\x01"


def test_property_name_must_fit() -> None:
    with pytest.raises(ValueError):
        Node("device-tree").prop("x" * 32, b"")


def test_pi5_adt_contains_required_nodes() -> None:
    blob = pi5_adt()
    assert b"brcm,bcm2712" in blob
    assert b"arm,pl011" in blob
    assert b"arm,gic-400" in blob
    assert b"arm,armv8-timer" in blob
    assert b"Raspberry Pi 5 Model B" in blob


def test_pi5_adt_is_deterministic() -> None:
    assert pi5_adt() == pi5_adt()


def test_pi5_adt_can_describe_a_ramdisk() -> None:
    blob = pi5_adt(ramdisk=(0x100000000, 0x100000))
    assert b"RAMDisk" in blob
    assert b"x0" not in blob  # sanity: no accidental textual address
