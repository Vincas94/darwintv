# tvOS notes

## Target

Use an **arm64, non-PAC** userland. The Pi 5's Cortex-A76 is ARMv8.2 and does **not** implement
ARMv8.3 pointer authentication (PAC). Do not use an A12/A15 (Apple TV 4K 2nd/3rd gen) userland if
it is arm64e.

| Device | SoC | Board | Why |
|---|---|---|---|
| **Apple TV HD (`AppleTV5,3`)** | A8 (t7000) | `j42dap` | arm64, no PAC, 1080p UI, checkm8-vulnerable, tvOS 16.x–26.x available |
| **Apple TV 4K 1st gen (`AppleTV6,2`)** | A10X | `j105aap` | arm64, no PAC, 4K |

The reference target is **Apple TV HD, tvOS 16.6 (20M73)**:

```text
AppleTV5,3_16.6_20M73_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-18272/3CE91CB7-2332-42B7-AEF8-37478A767E90/AppleTV5,3_16.6_20M73_Restore.ipsw
```

The XNU generation is **`xnu-8796.141.3`** (Darwin 22.6.0). Do not assume the current
`tansanrao/xnu` `xnu-on-pi` branch uses that tag: it diverges from `rel/xnu-8796` (merge base
`xnu-8796.101.5`) and carries a separate BCM2712 port. See
[`docs/decisions/0009-bcm2712-backport.md`](decisions/0009-bcm2712-backport.md).

## What is in the IPSW

Verified from the ZIP central directory:

| Entry | Role |
|---|---|
| `096-56462-077.dmg` (3.6 GB) | `OS` — the main tvOS system image (LZFSE/UDIF, APFS inside) |
| `096-56444-077.dmg` (79.7 MB) | `RestoreRamDisk` |
| `096-56456-077.dmg` (116 MB) | additional system/app image plus `.mtree`/`.root_hash`/`.trustcache` |
| `Firmware/all_flash/DeviceTree.j42dap.im4p` | the real Apple device tree; extract `/product` identity |
| `kernelcache.release.j42d` | encrypted kernelcache — not needed if you build XNU |
| `iBoot`, `iBSS`, `iBEC`, `LLB`, `sep-firmware` | Apple boot chain / SEP — not used |

No Apple files are committed. Download the IPSW yourself and keep it out of git.

## Userland

- tvOS 9+ uses **`PineBoard` / `HeadBoard`** instead of SpringBoard; `backboardd` is the same
  display/event daemon.
- The stack is still UIKit + CoreAnimation + IOSurface + IOMobileFramebuffer.
- Apple TV HD UI is **1920×1080**; 4K models are 3840×2160. CPU rendering targets 1080p.
- Input is the **Siri Remote over Bluetooth**. The Pi 5 BT controller is on BCM2712 (`uarta`), but
  a BT stack is a lot of work; inject HID events over the debug UART for bring-up.

## Root image

The planned pipeline is in `tools/rootfs/README.md`:

1. decompress the `OS` DMG,
2. mount the APFS volumes with `apfs-fuse`,
3. copy the system volume, dyld shared cache and required cryptexes into a case-sensitive
   journaled HFS+ image,
4. apply the bring-up tweaks (skip Setup, seed activation, disable daemons for hardware the Pi
   does not have),
5. `fsck.hfsplus -fy` and `img2simg`.

`ios-sweet/tools/mkiosroot.sh` and `sweet-root-tweaks.py` are the reference.

## Identity

Extract `DeviceTree.j42dap.im4p`, decompress the ADT payload, and copy the root and `/product`
properties into the Pi ADT. HakiOS's `xnuloader/mkidentity.py` is the reference. The goal is that
`MobileGestalt` sees:

```text
hw.product = AppleTV5,3
hw.target  = J42dAP
isAppleTV  = true
```

`PineBoard` will then select the TV UI rather than the phone UI.

## What will not work at first

- GPU acceleration (V3D / VideoCore VII): CPU rendering only.
- USB, Ethernet, 40-pin GPIO: RP1, M6.
- Bluetooth remote, Wi-Fi, audio, HDMI CEC, IR, AirPlay.
- SEP / AppleKeyStore: stubbed; security is off.
- Activation, Apple ID, iCloud, App Store: not supported and not a goal.

## Legal

Apple's XNU is APSL-2.0. The tvOS userland, IPSW, device tree and firmware are Apple's
copyrighted material. Download them yourself for personal research; do not redistribute them.
Bypassing activation/DRM may be illegal where you live. Nothing here is legal advice.
