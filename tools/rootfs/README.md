# rootfs

Planned home of the tvOS root-image builder (M4).

The pipeline is deliberately host-side and non-destructive:

1. Decompress the IPSW's `OS` entry (`096-56462-077.dmg` for AppleTV5,3 16.6).
   The image is an LZFSE-compressed UDIF; `dmg2img` or 7-Zip can unpack it.
2. Mount the APFS system volume with `apfs-fuse`.
3. Copy the system volume, dyld shared cache and the cryptexes that the userland
   needs into a case-sensitive journaled HFS+ image.
4. Apply the tvOS bring-up tweaks: skip Setup, seed activation state, disable
   daemons for hardware the Pi does not have (baseband, Wi-Fi, BT, audio,
   camera, HDMI CEC, IR, AirPlay).
5. `fsck.hfsplus -fy` and `img2simg` for the SD card.

Reference: `ios-sweet/tools/mkiosroot.sh` and `sweet-root-tweaks.py`.

No Apple files are committed. `scripts/make-rootfs.sh` is a placeholder until
the pipeline is implemented.
