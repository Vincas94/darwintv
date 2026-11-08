import zipfile
from pathlib import Path

from tools.ipsw.extract import extract, list_entries


def _make_ipsw(tmp_path: Path) -> Path:
    path = tmp_path / "AppleTV5,3_16.6_20M73_Restore.ipsw"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("BuildManifest.plist", b"plist")
        archive.writestr(
            "Firmware/all_flash/DeviceTree.j42dap.im4p",
            b"dtree",
        )
    return path


def test_list_entries(tmp_path: Path) -> None:
    names = [info.filename for info in list_entries(_make_ipsw(tmp_path))]
    assert "BuildManifest.plist" in names
    assert "Firmware/all_flash/DeviceTree.j42dap.im4p" in names


def test_extract_flattens_paths(tmp_path: Path) -> None:
    ipsw = _make_ipsw(tmp_path)
    target = extract(
        ipsw,
        "Firmware/all_flash/DeviceTree.j42dap.im4p",
        tmp_path / "out",
    )
    assert target.name == "DeviceTree.j42dap.im4p"
    assert target.read_bytes() == b"dtree"
