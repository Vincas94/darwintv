# IPSW extraction

No Apple firmware is committed. Download the IPSW yourself and keep it outside the repository.

## Target

```text
AppleTV5,3_16.6_20M73_Restore.ipsw
```

Verify the hashes before using it:

```text
SHA1    51da650aa4858042c0a6d7bb85674e304114a3d0
SHA256  dc1bac6533e61f92cf98a2b29507088d385d823e9764ab0bffc7a02b08b6cdc4
```

```sh
sha1sum "$IPSW_PATH"
sha256sum "$IPSW_PATH"
# or, with the expected values:
python -m tools.ipsw verify "$IPSW_PATH" \
  --sha1 51da650aa4858042c0a6d7bb85674e304114a3d0 \
  --sha256 dc1bac6533e61f92cf98a2b29507088d385d823e9764ab0bffc7a02b08b6cdc4
```

Both are listed by `ipsw.me` for AppleTV5,3 16.6 (20M73).

## Roles (verified from the ZIP central directory and BuildManifest)

| Entry | Role |
|---|---|
| `096-56462-077.dmg` (3.6 GB) | `OS` — main tvOS system image, LZFSE/UDIF |
| `096-56444-077.dmg` (79.7 MB) | `RestoreRamDisk` |
| `096-56456-077.dmg` (116 MB) | additional image with `.mtree`/`.root_hash`/`.trustcache`; role still to verify |
| `Firmware/all_flash/DeviceTree.j42dap.im4p` | the real Apple device tree (identity and `/product`) |
| `kernelcache.release.j42d` | encrypted kernelcache; not needed if you build XNU |
| `Firmware/all_flash/iBoot...`, `iBSS`, `iBEC`, `LLB`, `sep-firmware...` | Apple boot chain / SEP; not used |
| `BuildManifest.plist` | role map (`OS`, `RestoreRamDisk`, `DeviceTree`, `KernelCache`, ...) |

## Local list and extract

```sh
python -m tools.ipsw list "$IPSW_PATH"
python -m tools.ipsw extract "$IPSW_PATH" \
    Firmware/all_flash/DeviceTree.j42dap.im4p --out build/ipsw
python -m tools.ipsw extract "$IPSW_PATH" BuildManifest.plist --out build/ipsw
```

The extractor works on a local ZIP. Remote range extraction is a future feature; the initial
survey used HTTP range requests to read the central directory without downloading 3.9 GB.

## Device tree

```sh
ipsw img4 im4p extract \
  build/ipsw/DeviceTree.j42dap.im4p \
  -o build/ipsw/DeviceTree.j42dap.bin
```

The IM4P payload is an Apple Device Tree. Use `tools/adt` or HakiOS's `mkidentity.py` approach to
copy the root and `/product` properties into the Pi ADT. Do not expect an FDT.

## `OS` DMG

The `OS` entry is an LZFSE-compressed UDIF. On Linux:

```sh
# one of:
dmg2img 096-56462-077.dmg os.img
7z x 096-56462-077.dmg -obuild/os
```

Then inspect the APFS volumes:

```sh
apfs-fuse os.img /mnt/apfs
```

The planned HFS+ root build is in `tools/rootfs/README.md`; `ios-sweet/tools/mkiosroot.sh` is the
reference pipeline. The 3.6 GB root is never transferred over UART; see `docs/large-images.md`.

## Legal

The IPSW, device tree, kernelcache and userland are Apple's copyrighted material. Use them for
personal research; do not redistribute them. XNU is APSL-2.0. Nothing here is legal advice.
