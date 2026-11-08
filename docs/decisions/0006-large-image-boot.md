# ADR 0006 — Large images are block-backed; RAM disk only for bring-up

- **Status:** accepted
- **Date:** 2026-11-08

## Context

The debug UART is a 9.216 MHz PL011, so it tops out at 576000 baud. A full tvOS root is ~3.6 GB.
UART is suitable for a 10–40 MB kernel payload, not for a root filesystem. The Pi 5's microSD is
on BCM2712 `sdio1` (standard SDHCI), so a persistent root does not require the RP1 stack.

XNU already supports a memory-disk root: `/chosen/memory-map/RAMDisk = <physical base, size>`
creates `/dev/md0`, and `rd=md0` roots on it.

## Decision

1. **UART is for the kernel payload only** (and small test kernels). Never for the full root.
2. **Persistent large roots live on block storage** (microSD first, NVMe/USB later) and are
   mounted by XNU's SDHCI + HFS+ drivers. This is the normal path and the M4b target.
3. **A RAM-disk root is allowed for bring-up** on an 8 GB (or larger) Pi: U-Boot/EDK2 loads the
   root image into RAM, the loader adds the `RAMDisk` memory-map property, and `rd=md0` roots on
   it. This is M4a, before the SDHCI driver exists.
4. **U-Boot/EDK2 may be the first stage** when we need FAT/ext4/NVMe/USB/TFTP and a recovery
   shell. The Pi firmware loads U-Boot as `kernel8.img`.
5. **A/B updates** use two root partitions (or two RAM-disk files) plus the Pi firmware
   `tryboot`/`autoboot.txt` or a loader `boot.cfg`.

## Consequences

- M4a can reach `PineBoard` without waiting for SDHCI/HFS+; M4b makes it a real system.
- The 4 GB Pi cannot boot the full root from RAM; it needs the persistent path.
- A/B roots double the storage requirement; plan for 8–16 GB per slot or use file-level updates.
- The loader must reserve the RAM-disk range so the VM does not allocate over it.
- Network root is M6, after an Ethernet/Wi-Fi driver exists.
