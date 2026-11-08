> **Post-review update (2026-11-08):** Where this survey conflicts with the
> [review addendum](2026-11-08-review-addendum.md) or `docs/facts.md`, those win. The addendum
> covers Apple's in-tree BCM2837 support and the newer `xnu-on-pi` BCM2712 branch.

> **Provenance.** This is the initial survey that motivated DarwinTV, written on
> 2026-11-08 before the repository existed. It is kept verbatim (minor formatting
> only) so later decisions can be traced back to their sources.

# tvOS / Apple TV on a Raspberry Pi 5 — research notes and bring-up plan

*Written 2026-11-08. This is a research/engineering plan, not a claim that a working Pi 5 port exists.*

---

## 0. The one-paragraph answer

You cannot boot an Apple TV IPSW as-is on a Pi 5: the kernelcache is encrypted and signed,
the boot chain is iBoot/SecureROM, and the hardware is an Apple A8/A10X/A12/A15 SoC, not a
BCM2712. What *is* possible is the same thing `ios-sweet` and HakiOS do: **build Apple's
open-source XNU kernel from source, port it to the Pi 5, and put the unmodified tvOS userland
on top of it.** The closest existing work is Tanuj Rao's XNU-on-Pi (Raspberry Pi 4, BCM2711),
which already has a boot loader, Apple device tree, PL011 UART, GICv2 interrupt controller and
architectural timer. A Pi 5 port is an adaptation of that, not a from-scratch project. Booting
XNU to a serial console is a realistic few-week project; booting the tvOS `PineBoard` home
screen is a multi-month research project, because the Pi 5 has no GPU/USB/BT drivers under
XNU and tvOS expects Apple hardware.

---

## 1. First, disambiguate "Apple TV"

| What you might mean | Can it "boot natively" on a Pi 5? |
|---|---|
| **tvOS**, the Apple TV operating system | Only by porting XNU + running the tvOS userland. This is the subject of this document. |
| **The Apple TV app** (the streaming app) | It is not an OS and cannot boot. On Linux you use a browser/DRM stack or a real Apple TV; there is no native Linux app. |
| **An Apple TV device IPSW / kernelcache** | No. Encrypted, signed, and written for Apple SoCs. You rebuild XNU from Apple's source instead. |
| A **Darwin/XNU** kernel on the Pi 5 | Yes — this is the tractable first goal. |

This document assumes **tvOS**.

---

## 2. What `ios-sweet` and HakiOS actually do

### 2.1 `ios-sweet` — iOS 16 on a Redmi Note 10 Pro (SM7150)

Repo: <https://github.com/dipa-studio/ios-sweet> · notes: `NOTES.md` in that repo.

Its boot chain:

```
Xiaomi ABL (unlocked bootloader)
  -> fastboot boot shim-boot.img          (temporary; nothing flashed to boot)
     -> shim: own MMU setup, reads the live FDT, loads payload from ramdisk
        -> XNU Mach-O + generated Apple Device Tree (ADT) + boot-args
           -> XNU -> UFS driver -> HFS+ root in userdata
              -> dyld + shared cache -> launchd -> backboardd + SpringBoard
```

Key facts that transfer to any non-Apple port:

- **It builds XNU from Apple's source** (`xnu-8796`, iOS 16 generation) with a patch series.
  It does **not** decrypt the phone's kernelcache.
- **16K pages, non-PAC arm64**, `-mcpu` for the SoC; Apple's ARM64 kernel is patched to run on
  a non-Apple CPU.
- **The loader builds an Apple Device Tree (ADT)**, not an FDT. XNU only understands ADT.
  `tools/mkadt.py` is the generator; it copies the real iPhone's `/product` node so
  `MobileGestalt` believes it is an iPhone X.
- **The root is an HFS+ image built on the host from the IPSW's `OS`/`SystemOS`/`AppOS`
  DMGs** (`tools/mkiosroot.sh`). HFS+ is used instead of APFS to keep the kernel side simple.
- **Security is off**: permissive AMFI/code signing, permissive sandbox, stub AppleKeyStore,
  no data protection. `launchd_unsecure_cache=1`, `wdt=-1`, etc.
- **No GPU**: CoreAnimation is rendered on the CPU and copied into the bootloader's
  framebuffer. Touch over I2C, power/volume over PMIC.
- **Activation** uses the native "Hactivation" path by seeding the activation state and
  `chosen` security properties in the ADT; no Apple servers.
- Current state: boots to the iOS home screen, Settings, Control Center; no Wi-Fi/BT/cellular/
  audio/camera/SEP; ~4–5 minute boot. It took a long engineering log and a team.

### 2.2 HakiOS — XNU on a POCO X5 Pro (SM7325 / SC7280)

Repo: <https://github.com/oosexgang/hakios-xnu-kernel> · docs: `docs/` in that repo.

Its boot chain:

```
Android fastboot
  -> HakiOS UEFI (Mu-Silicium with HakiOS changes)
     -> xnuloader (loader.efi)
        -> XNU + HakiOS drivers
           -> launchd -> userland (Darwin 16.5 from your own IPSW)
```

Key facts:

- **UEFI loader approach**: `xnuloader` is a UEFI application that copies the Mach-O segments,
  builds the ADT and `boot_args`, drops the MMU and jumps to XNU. It is a very close model for
  a Pi 5 UEFI loader (the Pi 5 can run EDK2/U-Boot).
- **The ADT is generated from the phone's own device tree and the IPSW's identity**
  (`xnuloader/mkidentity.py`): it copies the root and `/product` properties from
  `DeviceTree.<board>.im4p` so `MobileGestalt`/`PineBoard` see the right device.
- **GICv3 + PSCI SMP + generic timer** support in `xnu/files/osfmk/arm64/gic_v3_irq.c`.
  Open-source XNU has no generic interrupt-controller driver; this file is the missing piece.
- **Modular drivers** (`CONFIG_HAKIOS_*`), APFS, UFS, Adreno GPU/Metal, Wi-Fi, audio, modem.
- **QEMU `virt`** target and a tiny open `hello` userland let you develop without a phone.
- Current state: POCO X5 Pro runs the Darwin 16.5 userland and draws through Metal on the
  Adreno; many things still missing.

### 2.3 XNU-on-Pi (Tanuj Rao) — the closest prior art for a Pi 5

- Project repo: <https://github.com/tansanrao/xnu-on-pi> (loader, Pi 4 DTB, Swift loader)
- XNU fork: <https://github.com/tansanrao/xnu>, branch **`xnu-on-pi5`**
  (latest commits are still labelled RPI4, but the branch is the intended Pi 5 line)
- Blog: <https://tansanrao.com/writing/2026/07/xnu-architecture-and-build-overview>

What already works / exists there:

- **A Pi 4 (BCM2711) load path**: a loader linked at `0x80000`, embedding the XNU Mach-O,
  parsing the firmware FDT, building an ADT and `boot_args`, dropping EL2→EL1, jumping to XNU.
- **GIC-400 / GICv2 support** in `pexpert/arm/pe_gicv2.c`: CPU 0, Group 0/FIQ, architectural
  virtual timer PPI 27. This is exactly the interrupt controller the Pi 5 also has.
- **PL011 UART support** in `pexpert/arm/pe_serial.c` + `pl011.h`, matched by the
  `arm,pl011` compatible and a `defaults/serial-device` phandle.
- **Board header** `pexpert/pexpert/arm64/RPI4.h` with `HAS_GIC_V2`, `PL011_UART`,
  `ARM_ARCH_TIMER`, `NO_MONITOR`, `RPI4_UP_ONLY`.
- **Build config** `config/MASTER.arm64.rpi4.MacOSX`, including `mockfs` (RAM root) and a
  static userland; `MACHINE_FLAGS_ARM64_RPI4 = -mcpu=cortex-a72`.
- **QEMU `raspi4b`** run target.

This is the best base for a Pi 5 port: the hard parts (GICv2, timer, PL011, ADT, loader,
non-Apple arm64 XNU build) are already written for a Broadcom Pi.

---

## 3. What is specific to tvOS / Apple TV

### 3.1 Pick the right Apple TV target

Use an **arm64, non-PAC** userland, because the Pi 5's Cortex-A76 is ARMv8.2 and does **not**
implement ARMv8.3 pointer authentication (PAC). Do not use an A12/A15 (Apple TV 4K 2nd/3rd
gen) userland if it is arm64e.

Recommended targets:

| Device | SoC | Board | Why |
|---|---|---|---|
| **Apple TV HD (`AppleTV5,3`)** | A8 (t7000) | `j42dap` | arm64, no PAC, 1080p UI, checkm8-vulnerable (useful for research), tvOS 16.x/17.x/18.x/26.x available |
| **Apple TV 4K 1st gen (`AppleTV6,2`)** | A10X | `j105aap` | arm64, no PAC, 4K; slightly faster userland |

The concrete IPSW used for the notes below:

```
AppleTV5,3_16.6_20M73_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-18272/3CE91CB7-2332-42B7-AEF8-37478A767E90/AppleTV5,3_16.6_20M73_Restore.ipsw
```

The XNU generation is the iOS/tvOS 16 generation: **`xnu-8796.141.3`** (Darwin 22.6.0).
That is the same tag `ios-sweet` and Tanuj use, so their patch series is directly applicable.

### 3.2 What is inside the tvOS IPSW (verified from the ZIP central directory)

For `AppleTV5,3_16.6_20M73_Restore.ipsw`:

| ZIP entry | Role |
|---|---|
| `096-56462-077.dmg` (3.6 GB) | `OS` — the main tvOS system image (LZFSE-compressed UDIF), contains the root filesystem |
| `096-56444-077.dmg` (79.7 MB) | `RestoreRamDisk` |
| `096-56456-077.dmg` (116 MB) | additional system/app image with `.mtree`, `.root_hash`, `.trustcache` |
| `Firmware/all_flash/DeviceTree.j42dap.im4p` | the real Apple device tree; extract the ADT from it |
| `kernelcache.release.j42d` | encrypted kernelcache — **you do not need it** if you build XNU |
| `Firmware/all_flash/iBoot...`, `iBSS`, `iBEC`, `LLB`, `sep-firmware...` | Apple boot chain / SEP firmware — not used |
| `BuildManifest.plist` | maps roles (`OS`, `RestoreRamDisk`, `DeviceTree`, `KernelCache`, ...) |

The system volume is Apple's copyrighted userland. The XNU source is APSL-2.0. Keep Apple
files out of any public repo; download the IPSW yourself.

### 3.3 tvOS userland structure

- tvOS 9+ replaced `SpringBoard` with **`PineBoard` / `HeadBoard`**; `backboardd` is the same
  event/display daemon as on iOS. The UI stack is still UIKit + CoreAnimation + IOSurface +
  IOMobileFramebuffer.
- The Apple TV HD UI is **1920×1080**; the 4K models are 3840×2160. For CPU rendering, 1080p
  is the sane target.
- Input is normally the **Siri Remote over Bluetooth**. The Pi 5's BT controller is on BCM2712
  (`uarta`, `brcm,bcm43438-bt`), but a Bluetooth stack is a lot of work; for bring-up inject
  HID events over the debug UART instead.
- tvOS has no baseband/cellular. Many daemons (Wi-Fi, Bluetooth, audio, camera, HDMI CEC, IR,
  AirPlay) will fail or crash-loop; disable or stub them exactly as `ios-sweet` does.

---

## 4. Raspberry Pi 5 hardware facts you need

### 4.1 SoC and CPU

- **BCM2712**, 4× **Cortex-A76**, ARMv8.2-A, 2.4 GHz, 4/8/16 GB LPDDR4X.
- **16K translation granule is supported** on A76 (and Pi 5 Linux uses 16K pages). This is a
  much better match for XNU/iOS than the Pi 4's A72 or Pi 3's A53. Define `__ARM_16K_PG__`.
- **No PAC** (ARMv8.3), so use non-PAC arm64 XNU and a non-arm64e userland.
- **PSCI** is provided by the firmware's TF-A BL31 stub (`method = "smc"`).
- **GIC-400 (GICv2)**, not GICv3.

### 4.2 Memory map (BCM2712)

The Linux DTS gives the offsets; the `soc` node maps `0x7c000000` to parent `0x10_7c000000`.

| Block | Physical address | Notes |
|---|---|---|
| RAM | `0x0` ... (size from firmware DTB) | parse `/memory` in the FDT |
| `soc` base | `0x10_7c000000` | `arm-io/ranges` parent base |
| **Debug UART `uart10` / `_uart0`** | **`0x10_7d001000`** | PL011, 0x200, IRQ SPI 121 |
| **GIC-400 GICD** | **`0x10_7fff9000`** | 0x1000 |
| **GIC-400 GICC** | **`0x10_7fffa000`** | 0x2000 |
| GIC-400 GICH | `0x10_7fffc000` | 0x2000 |
| GIC-400 GICV | `0x10_7fffe000` | 0x2000 |
| ARM generic timer | `CNTFRQ_EL0` / `CNTV_*` | virtual timer PPI 27 |
| **SDHCI `sdio1` (microSD)** | **`0x10_00fff000`** | 0x260 host; IRQ SPI 273 |
| Firmware mailbox | `0x10_7c013880` | property tags, framebuffer |
| HDMI0 | `0x10_7c701400` | firmware framebuffer is simpler |
| HDMI1 | `0x10_7c706400` | |
| Wi-Fi `sdio2` | `0x10_01100000` | BCM2712 SDHCI; IRQ SPI 274 |
| Bluetooth `uarta` | `0x10_7d50c000` | BCM2712 `brcm,bcm7271-uart`; IRQ SPI 276 |
| **RP1** | PCIe2 (`pcie2`) | USB, Ethernet, 40-pin GPIO, UART0 — **avoid for first boot** |

Important: on the Pi 5 the **40-pin header, USB-A ports and Ethernet are on RP1**, behind
PCIe. The **debug UART, HDMI, microSD, Wi-Fi (`sdio2`) and Bluetooth (`uarta`) are on
BCM2712**. That means the minimal tvOS demo (serial + HDMI framebuffer + SD root) does
**not** need an RP1 driver. USB keyboard/remote and Ethernet do; Wi-Fi/BT need BCM2712
drivers plus their firmware/stacks.

### 4.3 Pi 5 boot flow

```
BCM2712 boot ROM
  -> SPI EEPROM bootloader (rpi-eeprom)
     -> reads config.txt from the FAT boot partition
     -> loads kernel_2712.img (or kernel8.img) at the documented 64-bit load address
        (default 0x200000; set kernel_address=0x200000 explicitly)
     -> loads the DTB and passes its address in x0
     -> TF-A BL31 armstub runs at EL3, drops to EL2
        -> your loader runs at EL2, x0 = DTB
```

The firmware on Pi 5 is self-contained in the EEPROM; there is no `start4.elf` on the boot
partition. It loads `kernel_2712.img` if present, otherwise `kernel8.img`.

---

## 5. The boot plan (milestones)

### M0 — before the USB-UART adapter arrives

1. Put Raspberry Pi OS on the Pi 5 and verify HDMI/SD.
2. On your Linux PC, build and run Tanuj's Pi 4 XNU port in QEMU:
   ```sh
   git clone https://github.com/tansanrao/xnu-on-pi
   cd xnu-on-pi
   # follow the Makefile; QEMU raspi4b, -serial stdio
   ```
   This proves the loader/ADT/XNU toolchain before touching the Pi 5.
3. Fork `tansanrao/xnu` and check out `xnu-on-pi5`; build it on a macOS GitHub Actions
   runner (XNU cannot be built on Linux; `blacktop/darwin-xnu-build` works).
4. Download the AppleTV5,3 16.6 IPSW. Extract `BuildManifest.plist`,
   `Firmware/all_flash/DeviceTree.j42dap.im4p`, and the `OS` DMG (`096-56462-077.dmg`).
5. Install `apfs-fuse`, `hfsprogs`, `lzfse`, `dmg2img`/`7z`, `ipsw` (blacktop/ipsw).
6. Adapt `ios-sweet`'s `tools/mkiosroot.sh` to build an HFS+ root from the tvOS `OS` DMG.
7. Read: HakiOS `docs/porting/index.md`, `ios-sweet/NOTES.md`, Tanuj's blog.

### M1 — hello world on the Pi 5 UART (1–2 days after the adapter)

- Write a minimal AArch64 loader linked at `0x200000`:
  - park secondary cores (`MPIDR_EL1` Aff0),
  - drop EL3→EL2→EL1 (the Pi 5 starts at EL2 via TF-A; handle EL3 too),
  - set `CNTFRQ_EL0` if zero,
  - initialize/write the PL011 at `0x107d001000` (the firmware already set 115200 8N1;
    just poll TXFF and write `UARTDR`),
  - print `hello from Pi 5`.
- `config.txt`:
  ```ini
  arm_64bit=1
  kernel=loader8.img
  kernel_address=0x200000
  uart_2ndstage=1
  # optional for later:
  # framebuffer_width=1920
  # framebuffer_height=1080
  # framebuffer_depth=32
  ```
- EEPROM config: `BOOT_UART=1` to see the bootloader log on the debug connector.
- If the loader never runs, try linking at `0x80000` (some Pi firmware revisions / QEMU
  `raspi4b` use that); the Pi 5 docs say `0x200000` for 64-bit.

### M2 — XNU to a serial console (1–3 weeks)

Port Tanuj's Pi 4 work:

- Add `ARM64_BOARD_CONFIG_RPI5` / `BCM2712`:
  - `makedefs/MakeInc.def`: `MACHINE_FLAGS_ARM64_RPI5 = -DARM64_BOARD_CONFIG_RPI5 -mcpu=cortex-a76`
  - `SUPPORTED_ARM64_MACHINE_CONFIGS` += `RPI5`
  - create `pexpert/pexpert/arm64/RPI5.h` from `RPI4.h`, but:
    - `#define __ARM_16K_PG__ 1`
    - `#define ARM_VM_PAGE_SIZE_FIXED_TO_HW 1`
    - `#define HAS_GIC_V2 1`
    - `#define PL011_UART`
    - `#define ARM_ARCH_TIMER`
    - `#define NO_MONITOR 1`
    - keep `RPI5_UP_ONLY` for the first boot
    - copy the `CONFIG_ZONE_MAP_*` sizing from `RPI4.h`, adjust if needed
  - create `config/MASTER.arm64.rpi5.MacOSX` from the RPI4 file (mockfs, no Apple drivers,
    corecrypto/pthread stubs).
- Reuse `pexpert/arm/pe_gicv2.c` unchanged except the ADT addresses.
- Reuse `pexpert/arm/pe_serial.c` + `pl011.h` unchanged.
- Loader: copy Tanuj's loader logic, but:
  - `kernelPhysicalBase = 0x02000000`
  - `kernelHeaderOffset = 0x4000` (16K page)
  - `physicalMemorySize` from the Pi 5 FDT `/memory` (cap at 4 GB for the first boot)
  - UART base `0x107d001000`
- ADT nodes (behind the kernel):
  ```
  /device-tree
    /chosen
      dram-base = 0x02000000
      dram-size = usable_ram - 0x02000000
      random-seed = 256 bytes (counter mix for bring-up)
      /memory-map
    /cpus/cpu0
      state = "running"
      reg = 0
      timebase-frequency = CNTFRQ_EL0
      bus-frequency = 100000000
      memory-frequency = 400000000
      peripheral-frequency = 100000000
      fixed-frequency = CNTFRQ_EL0
      clock-frequency = 2400000000
    /arm-io
      ranges = <0, 0x107c000000, 0x04000000>
      /uart0
        compatible = "arm,pl011"
        reg = <0x001001000, 0x200>
        AAPL,phandle = 1
      /gic
        device_type = "interrupt-controller"
        compatible = "arm,gic-400"
        interrupt-controller = "master"
        #interrupt-cells = 3
        AAPL,phandle = 2
        reg = <0x003ff9000,0x1000, 0x003ffa000,0x2000,
               0x003ffc000,0x2000, 0x003ffe000,0x2000>
      /timer
        device_type = "timer"
        compatible = "arm,armv8-timer"
        interrupt-parent = 2
        interrupts = <1 11 0xf08>   /* virtual timer PPI 27 */
    /defaults
      serial-device = 1
  ```
- `boot_args`: Revision 2, Version 2, `virtBase` = kernel link base,
  `physBase` = `0x02000000`, `memSize` = RAM end − physBase, `topOfKernelData` = end of
  ADT+boot_args, `deviceTreeP` = `virtBase + (adt_pa − physBase)`, `deviceTreeLength`,
  `CommandLine = "debug=0xc serial=1 cpus=1 keepsyms=1 -noprogress"`,
  `memSizeActual` = full RAM size.
- Build XNU on macOS CI with the patch series adapted from `xnu-on-pi5` +
  `ios-sweet`/HakiOS for non-PAC and no Apple security.
- **Done when:** XNU prints its banner and reaches `bsd_init` / an idle loop on the debug UART.

### M3 — interrupts, timer, GIC (1–3 weeks)

- `pe_gicv2.c` already does CPU0/Group 0/FIQ and timer PPI 27. Adapt:
  - `GICD`/`GICC` addresses come from the ADT `reg` + `soc` base; no code change.
  - Verify `GICD_TYPER`, `GICD_PIDR2`, `GICC_IIDR` on the Pi 5.
- Add SPI attach for UART (SPI 121 → INTID 153) and later SDHCI (SPI 273 → INTID 305):
  - `GICD_ISENABLER(n)`, `GICD_IPRIORITYR(n)`, `GICD_ICFGR(n)`, `GICC_IAR`/`GICC_EOIR`.
  - The Pi 4 code is timer-only and panics on unexpected IRQs; extend it.
- SMP is optional: the Pi 5's TF-A provides PSCI `CPU_ON` (`0xc4000003` via SMC). Start with
  `cpus=1`; add PSCI + GIC SGIs later (HakiOS's `gic_v3_irq.c` + `psci_smp.c` are the model,
  but the GIC part must be ported to GICv2).
- **Done when:** timer ticks and UART RX interrupts work, and the system stays up.

### M4 — root filesystem: mockfs, then HFS+ (1–2 weeks, then 1–2 months)

- First use Tanuj's **mockfs** + static raw-syscall userland to get `launchd`/a shell running
  from RAM. This isolates storage drivers.
- Then add **SDHCI** for `sdio1` (`0x1000fff000`, IRQ SPI 273):
  - standard SDHCI registers + the BCM2712 `cfg`/`busisol`/`lcpll` quirks,
  - expose an `IOBlockStorageDevice`/`IOMedia`,
  - mount an HFS+ image built from the tvOS `OS` DMG.
- Alternative if SDHCI is painful: NVMe over PCIe or USB over RP1 — both much more work.
- **Done when:** `bsd_init` mounts the HFS+ root and `launchd` starts.

### M5 — tvOS userland to `PineBoard` (months)

- Build the tvOS root on the host:
  - decompress `096-56462-077.dmg` (LZFSE/UDIF),
  - use `apfs-fuse` to read the APFS volumes,
  - copy the system volume + dyld shared cache + cryptex contents into a case-sensitive
    journaled HFS+ image (adapt `ios-sweet/tools/mkiosroot.sh`),
  - apply root tweaks: skip Setup, seed activation, remove/disable baseband, Wi-Fi, BT,
    audio, camera, HDMI CEC, IR, AirPlay daemons that cannot work.
- Identity: extract `DeviceTree.j42dap.im4p` → ADT; copy the root and `/product` properties
  into the Pi ADT (HakiOS `xnuloader/mkidentity.py` is exactly this). Present
  `hw.product = AppleTV5,3`, `hw.target = J42dAP`, `isAppleTV = true`.
- Kernel services needed by `backboardd`/`PineBoard`:
  - `IOSurface` + `IOMobileFramebuffer` (HakiOS `MiniIOSurface.cpp` /
    `MiniIOMobileFramebuffer.cpp` are the templates),
  - `IOHIDFamily` (Apple's open source; HakiOS uses `IOHIDFamily-1915.140.3`),
  - `AppleKeyStore` stub + permissive AMFI + permissive sandbox,
  - `launchd_unsecure_cache=1`.
- Display: present 1920×1080 through the firmware framebuffer. The Pi 5 firmware can
  allocate a linear framebuffer via the mailbox property tags
  (`MBOX_BASE = 0x107c013880`; `FB_ALLOCATE`/`FB_GET_INFO` family). Copy CoreAnimation's
  surfaces into it; fake a 60 Hz vsync if needed.
- Input: inject HID events from the debug UART (arrow keys + select) until you have RP1 USB
  or Bluetooth.
- **Done when:** `PineBoard` draws the tvOS home screen.

### M6 — the long tail

- RP1/PCIe: USB, Ethernet, 40-pin GPIO, UART0 (huge).
- V3D GPU (VideoCore VII): a Mesa/V3D port to XNU — huge; CPU rendering is the fallback.
- Wi-Fi/BT, HDMI audio, HDMI CEC, Siri Remote, AirPlay.
- Activation, Apple ID, App Store: not supported and not a goal.

---

## 6. Serial adapter wiring (Pi 5 debug UART)

The Pi 5's primary debug UART is **`UART10`**, a PL011 at **`0x107d001000`**, exposed on the
**3-pin JST-SH debug connector** (between the microHDMI ports). It is **3.3 V only**.

3-pin debug connector pinout (Raspberry Pi 3-pin Debug Connector spec):

| Pin | Signal | Connect to USB-UART |
|---|---|---|
| 1 | RX / SC (input to Pi) | adapter **TX** |
| 2 | GND | adapter **GND** |
| 3 | TX / SD (output from Pi) | adapter **RX** |

- **Do not connect VCC/3.3V/5V.** Only GND, TX, RX.
- Set the adapter to **3.3 V** (many are 5 V/3.3 V selectable). A 5 V adapter can damage the
  Pi.
- **115200 baud, 8 data bits, 1 stop bit, no parity, no flow control.**
- Terminal: `picocom -b 115200 /dev/ttyUSB0` or `minicom -b 115200 -D /dev/ttyUSB0`.
- To see firmware logs:
  - EEPROM: `sudo rpi-eeprom-config --edit` → `BOOT_UART=1`
  - `config.txt`: `uart_2ndstage=1`
- To use the 40-pin header UART instead (RP1, Linux only):
  - `enable_uart=1` + `dtoverlay=uart0-pi5`; `/dev/ttyAMA0`; but **not** useful for bare-metal
    because it is behind RP1.
- The official **Raspberry Pi Debug Probe** is the least fuss: it includes the 3-pin JST-SH
  cable and is 3.3 V.

---

## 7. Reality check: effort and risk

| Milestone | Realistic effort (experienced kernel dev) | Main risk |
|---|---|---|
| M1 hello UART | 1–2 days | wrong load address / wiring |
| M2 XNU console | 1–3 weeks | 16K page layout, ADT/clock details |
| M3 GICv2/timer | 1–3 weeks | GIC-400 quirks, FIQ routing |
| M4 root + launchd | 1–2 months | SDHCI, HFS+, dyld cache |
| M5 PineBoard | 3–6+ months | no GPU/USB/BT, tvOS daemons, identity |
| Full usable tvOS | 12–24+ months, team-scale | RP1, V3D, Wi-Fi/BT, activation |

The phone projects (`ios-sweet`, HakiOS) are team efforts with long engineering logs; the Pi 4
XNU port is a solo research project that reached mockfs/static userland. A Pi 5 port has a
much better starting point than a blank page, but **do not expect a usable Apple TV
replacement**. The realistic win is a serial-console Darwin kernel on the Pi 5, then a shell,
then a very slow software-rendered tvOS UI.

---

## 8. Before the adapter arrives — concrete checklist

- [ ] Install Raspberry Pi OS on the Pi 5; update the EEPROM (`rpi-eeprom-update`).
- [ ] Buy/verify a **3.3 V** USB-UART adapter with TX/RX/GND, and a **JST-SH 1.0 mm 3-pin**
      cable (or a Raspberry Pi Debug Probe).
- [ ] Clone `tansanrao/xnu-on-pi`; build and boot it in QEMU `raspi4b` on your Linux PC.
- [ ] Fork `tansanrao/xnu`, branch `xnu-on-pi5`; build `xnu-8796.141.3` on a macOS GitHub
      Actions runner.
- [ ] Download the AppleTV5,3 16.6 IPSW; verify the SHA1 from the Apple Wiki.
- [ ] Extract `BuildManifest.plist`, `DeviceTree.j42dap.im4p`, `096-56462-077.dmg`.
- [ ] Install `apfs-fuse`, `hfsprogs`, `lzfse`, `ipsw`, `qemu-system-aarch64`,
      `gcc-aarch64-linux-gnu`.
- [ ] Read HakiOS `docs/porting/index.md` and `docs/concepts/architecture.md`.
- [ ] Read `ios-sweet/NOTES.md` (the boot/crash log is the real tutorial).
- [ ] Write the M1 loader and test it under QEMU `raspi4b`/`virt` before the Pi 5.

---

## 9. Sources / links

**Reference projects**
- ios-sweet: <https://github.com/dipa-studio/ios-sweet>
- HakiOS: <https://github.com/oosexgang/hakios-xnu-kernel>
- HakiOS docs: <https://github.com/oosexgang/hakios-xnu-kernel/tree/main/docs>
- XNU-on-Pi loader: <https://github.com/tansanrao/xnu-on-pi>
- XNU-on-Pi kernel fork: <https://github.com/tansanrao/xnu> (branch `xnu-on-pi5`)
- Tanuj's write-up: <https://tansanrao.com/writing/2026/07/xnu-architecture-and-build-overview>

**Apple source / firmware**
- XNU: <https://github.com/apple-oss-distributions/xnu> (tag `xnu-8796.141.3`)
- Apple TV firmware index: <https://theapplewiki.com/wiki/Firmware/Apple_TV/16.x>
- IPSW API: <https://api.ipsw.me/v4/device/AppleTV5,3?type=ipsw>

**Raspberry Pi 5**
- Boot flow: <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html>
- config.txt: <https://www.raspberrypi.com/documentation/computers/config_txt.html>
- UART / debug connector: <https://www.raspberrypi.com/documentation/computers/configuration.html#configure-uarts>
- 3-pin debug connector spec: <https://pip.raspberrypi.com/documents/RP-008189-DS-debug-connector-specification.pdf>
- BCM2712 DTS: <https://github.com/raspberrypi/linux/blob/rpi-6.6.y/arch/arm64/boot/dts/broadcom/bcm2712.dtsi>
- RP1: <https://www.raspberrypi.com/documentation/computers/io-controllers/rp1.html>
- TF-A RPi5: <https://trustedfirmware-a.readthedocs.io/en/v2.11/plat/rpi5.html>

**Related prior art**
- Inokinoki XNU on Pi 3: <https://github.com/Inokinoki/xnu-bcm2837-hackintosh>
- UniXNU (UEFI XNU on non-Apple ARM64): <https://github.com/UniXNU/UniXNU>
- PureDarwin: <https://www.puredarwin.org>

---

## 10. Legal note

Apple's XNU is published under the Apple Public Source License 2.0. The tvOS userland, the
IPSW contents, and the device tree are Apple's copyrighted material; this plan assumes you
download them yourself for personal research and do not redistribute them. Bypassing
activation/DRM may be illegal in your jurisdiction. Nothing here is legal advice.
