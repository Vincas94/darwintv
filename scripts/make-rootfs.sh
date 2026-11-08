#!/usr/bin/env bash
set -euo pipefail

cat <<'PLAN'
The tvOS root-image builder is not implemented yet.

Planned pipeline (M4):
  1. dmg2img / 7z the LZFSE-compressed UDIF from the IPSW's OS entry.
  2. apfs-fuse the APFS system volume and any cryptex volumes.
  3. Copy the system volume, dyld shared cache and required cryptexes into a
     case-sensitive journaled HFS+ image.
  4. Apply the tvOS root tweaks (skip Setup, seed activation, disable daemons
     for hardware that does not exist).
  5. fsck.hfsplus -fy and img2simg for the SD card.

Inputs: your own AppleTV5,3 16.6 IPSW. No Apple files are committed.
See docs/tvos.md and ios-sweet's tools/mkiosroot.sh for the reference pipeline.
PLAN
exit 2
