# Booting large images

"Image" means three very different things. They do not share a transport.

| Image | Typical size | Boot path |
|---|---:|---|
| XNU kernel + ADT + boot args (`payload.bin`) | 10–40 MB | UART, FAT copy, or RAM |
| Small bring-up root / initramfs | 64 MB – 1 GB | FAT copy, U-Boot/EDK2, or RAM disk |
| Full tvOS root (HFS+/APFS) | 2.5–3.6 GB | **block storage** (microSD, NVMe, USB) |
| Anything larger than RAM | > 4/8/16 GB | block storage only |

UART is only for the first row. A 3.6 GB root at 460800 baud is roughly **100 hours** — not a
transport, a prank.

## Option A — persistent block root (the real answer, M4)

This is how every normal OS does it, and it is the target:

```text
p1 FAT32  boot     loader8.img, payload.bin, config.txt
p2 raw    tvos     HFS+ root, 8–16 GB
p3 ext4   rescue   optional Linux
```

1. The Pi firmware reads p1 and loads `payload.bin`.
2. The loader builds the ADT, including an `sdio1`/SDHCI node.
3. XNU's SDHCI driver creates an `IOMedia` for p2.
4. XNU's HFS+ driver mounts it as the root (`rd=sd0` or the `rootdev` selected by
   `IOFindBSDRoot`).
5. No root image is transferred at boot; only the 15 MB kernel is loaded.

The root is 3.6 GB, but it is read from the microSD at boot and paged in as needed. The Pi 5's
microSD is on **BCM2712 `sdio1`** (`0x10_00fff000`, IRQ SPI 273), not RP1, so this does not
require the RP1 stack. The controller is standard SDHCI with a few BCM2712 quirks.

Updates are incremental:

```sh
sudo mount -t hfsplus /dev/sdX2 /mnt/tvos
sudo rsync -a --delete new-root/ /mnt/tvos/
sync
sudo umount /mnt/tvos
```

A new image can be written with `bmaptool copy root.img /dev/sdX2`, which writes only the mapped
blocks. No full-card reflash.

**This is the critical M4 work.** Until SDHCI + HFS+ exist, large roots need Option B or C.

## Option B — RAM-disk root (bring-up shortcut, 8 GB Pi)

XNU can root from a memory disk. The mechanism is already in the open-source kernel:

- `IOKitBSDInit.cpp` looks for a **`RAMDisk`** property in `/chosen/memory-map`.
- The property is two native words: **physical base**, **size**.
- It creates `/dev/md0`; `rd=md0` makes it the root.
- The filesystem on it is still HFS+ (or whatever the image is).

So the loader can boot a 3.6 GB root image **without an SDHCI driver**:

1. U-Boot or EDK2 reads `root.img` from FAT/NVMe/USB/TFTP into RAM at a page-aligned address.
2. The DarwinTV loader adds `/chosen/memory-map/RAMDisk = <base, size>` to the ADT and reserves
   that range so the VM does not allocate over it.
3. Boot args include `rd=md0`.
4. XNU creates `md0`, mounts HFS+, and `PineBoard` starts.

```text
8 GB Pi:  3.6 GB root + ~15 MB kernel + ADT + page tables + XNU overhead  → fits, but tight
4 GB Pi:  not viable for the full root; use Option A or a much smaller bring-up root
16 GB Pi: comfortable; also lets you keep a second A/B root in RAM if you really want
```

Boot time is dominated by reading the root into RAM once:

| Source | Approx. 3.6 GB read |
|---|---:|
| microSD (UHS-I, ~90 MB/s) | ~40 s |
| USB 3 SSD (~400 MB/s) | ~9 s |
| NVMe (~1–2 GB/s) | ~2–4 s |
| Gigabit TFTP (~110 MB/s) | ~33 s |
| UART 460800 | ~100 hours |

This is a **bring-up** path, not the daily driver: every boot reloads the whole root, and a
4 GB Pi cannot hold it.

## Option C — U-Boot or EDK2 as the first stage

The Pi firmware can load U-Boot as `kernel8.img` (one file copy). U-Boot then has:

- FAT and ext4 filesystem drivers,
- microSD, USB and NVMe block drivers,
- TFTP/network boot,
- a shell and a boot menu.

That lets you keep the kernel, payload and root as ordinary files, and update them from any OS
without touching the card. It also gives you a recovery shell when a payload panics.

```text
Pi firmware → u-boot.bin → (FAT/ext4/NVMe/USB/TFTP)
                            ├─ payload.bin  → DarwinTV loader → XNU
                            └─ root.img     → RAM disk (Option B)
```

The trade-off is one more component to build and configure; HakiOS uses this pattern on phones.

## Option D — network root (later)

Once XNU has a network driver for the Pi 5's Ethernet (RP1) or Wi-Fi, a network root becomes
possible: NFS, HTTP, or a small network block device. That is M6 work. It does not remove the
need for a storage driver for local boot; it replaces the root transport, not the kernel's block
stack.

## What not to do

- **Do not send a 3.6 GB root over UART.** At 460800 it is ~100 hours; at 576000 it is still
  ~87 hours, plus protocol overhead and retries.
- **Do not expect the firmware's `ramfsfile` to replace a storage driver.** It is fine for the
  15 MB kernel payload; large roots belong on a block device or in a U-Boot-loaded RAM disk.
- **Do not load a 3.6 GB root into a 4 GB Pi.** There is no room for the kernel, page tables and
  XNU overhead.
- **Do not put the root on the FAT boot partition.** FAT32 has a 4 GB file limit, no permissions
  and no HFS+ semantics; use p2.

## How this lands in the roadmap

| Milestone | Large-image capability |
|---|---|
| M2 | `payload.bin` via FAT/`ramfsfile`; no root yet |
| M4a | RAM-disk root via U-Boot/EDK2 on an 8 GB Pi → `PineBoard` bring-up |
| M4b | SDHCI + HFS+ persistent root on microSD → normal boot |
| M6 | NVMe/USB root and network root |

The M4a/M4b split is deliberate: the RAM disk gets `PineBoard` running without waiting for the
storage driver, and the persistent root makes it usable.
