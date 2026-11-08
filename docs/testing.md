# Testing and the development loop

## First: separate transfer time from boot time

The minutes in the UART numbers are **transfer** time, not XNU boot time.

| Step | UART 460800 | microSD / FAT | TFTP | QEMU |
|---|---:|---:|---:|---:|
| 15 MB `payload.bin` transfer | ~5.5 min | < 1 s | ~1 s | n/a |
| Firmware + loader | ~1 s | ~1 s | ~1 s | seconds |
| XNU to serial banner | ~1–3 s | ~1–3 s | ~1–3 s | seconds–minutes (TCG) |
| XNU to `launchd` (tiny root) | seconds | seconds | seconds | minutes |
| Full 3.6 GB tvOS root | ~100 h | ~40 s (SD) | ~33 s | not practical |

So: **do not use UART for the kernel in the inner loop.** Put `payload.bin` on the FAT partition
(or serve it over TFTP), and the whole build→boot cycle is seconds. UART is the recovery path.

## The test pyramid

| Level | What | Time | When |
|---|---|---:|---|
| **L0 host** | ADT writer, IPSW parsing, payload packing, baud math, scripts | ms | every save |
| **L1 QEMU loader** | EL drop, PL011, FDT parse, ADT/`boot_args`, jump | seconds | every commit |
| **L2 QEMU XNU** | XNU banner, platform expert, timer, early `bsd_init` | seconds–minutes | every commit |
| **L3 Pi 5 smoke** | same payload on real hardware, boot to a marker | seconds | every PR / batch |
| **L4 Pi 5 drivers** | SDHCI, display, HID, panic paths | minutes | nightly / batched |
| **L5 tvOS** | `PineBoard` integration | 10s–minutes | milestone, not per change |

Most bugs should die at L0/L1/L2. Hardware is for the things QEMU cannot model.

## L0 — host tests

```sh
source .venv/bin/activate
pytest -q
```

These run in milliseconds and should cover every host-side format: ADT bytes, IPSW entry names,
payload header/CRC, baud divisor, config generation. Add a test for every bug fix that can be
reproduced on the host.

## L1/L2 — QEMU first

QEMU `raspi4b` is close enough for the generic bring-up:

- GIC-400 / GICv2,
- PL011,
- architectural timer,
- EL2→EL1,
- FDT/ADT and `boot_args`.

```sh
make loader BOARD=qemu-raspi4b
qemu-system-aarch64 -M raspi4b \
  -kernel bootloader/build/qemu-raspi4b/loader8.img \
  -serial stdio -display none -monitor none
```

For XNU, use QEMU `virt` with a GICv2. The loader has a `qemu-virt` target linked at
`0x40000000` with the PL011 at `0x09000000`:

```sh
make loader BOARD=qemu-virt
qemu-system-aarch64 -M virt,gic-version=2 -cpu cortex-a76 -smp 4 -m 2G \
  -kernel bootloader/build/qemu-virt/loader.elf \
  -serial stdio -display none -s -S
```

Attach `gdb-multiarch` with `target remote :1234`. Use `-d int,guest_errors` when the GIC is
misbehaving. QEMU is slower than hardware for a full userland, but it is much faster than a
physical power-cycle for early kernel logic.

## L3 — fast Pi 5 smoke, no card removal

The hardware loop should be:

```text
build payload -> copy payload.bin to p1 -> power-cycle -> capture serial -> check marker
```

A USB SD reader, a mounted boot partition, or a USB/NVMe boot medium all work. The repo scripts
wrap the safe parts:

```sh
export BOOT_MNT=/mnt/pi5-boot
export SERIAL_DEV=/dev/ttyACM0
export SERIAL_BAUD=460800
export POWER_CMD="uhubctl -a cycle -p 1"     # or usbrelay / smart plug curl
export WAIT_FOR="DarwinTV"

./scripts/flash-payload.sh build/payload.bin
./scripts/power-cycle.sh
./scripts/serial-capture.sh
```

`flash-payload.sh` only copies to a mounted directory; it never writes a block device.
`power-cycle.sh` runs the command you provide; it has no hardcoded destructive action.

For a self-hosted GitHub Actions runner, the same three steps become a `hw-smoke` job: build,
copy, power-cycle, capture, grep. That is how you stop doing this by hand.

## Make the boot tell you what you need, then stop

Do not boot the full userland to test a GIC change. Add a **test mode**:

- boot args: `debug=0xc serial=1 cpus=1 keepsyms=1 -noprogress`
- a `test=` boot argument, or a `DARWINTV_TEST` kernel option, selects a stage;
- the stage prints `TEST:PASS <name>` or `TEST:FAIL <name> <reason>` and halts/resets;
- the host waits for the marker and fails the job.

This turns a 30-second integration boot into a 1–3 second targeted test. It also gives you a
stable serial protocol for CI.

## L4 — driver tests, batched

Some things QEMU cannot model: BCM2712 SDHCI quirks, the firmware framebuffer, RP1, V3D. For
these:

- batch related changes into one boot;
- use a test menu (`test=sdhci,fb,hid`) and run several probes per session;
- log to a persistent ring (a reserved RAM region or a small SD partition) so a panic does not
  lose the evidence;
- keep a known-good payload slot.

## UART is still useful

- **Recovery** when the boot medium is broken.
- **No-card-removal** iterations with a small test kernel.
- **Compressed payloads**: LZ4/LZFSE can take a 15 MB kernel to ~5 MB; at 460800 that is ~1.8 min.
- **Delta payloads** (optional): bsdiff between two kernel builds; the loader applies the patch to
  the previous payload. Worth it only if UART is your only channel.

But the primary loop is FAT/SD/USB/NVMe/TFTP, not UART.

## Build time is the other bottleneck

A full XNU build on a macOS runner is 10–20 minutes. Reduce it:

- cache the XNU object tree between CI runs;
- build only the kernel target (not the whole SDK);
- use `ccache` if your runner supports it;
- use a self-hosted macOS runner or a Mac mini for frequent kernel work;
- batch host-tool changes so you do not rebuild XNU for an ADT tweak.

Host tools build in seconds; keep them separate from the kernel build.

## The recommended inner loop

1. Change host tool or ADT → `pytest` (ms).
2. Change loader/generic kernel → QEMU `raspi4b`/`virt` (seconds).
3. Change Pi 5-specific code → build payload, copy to p1, power-cycle, serial capture (seconds +
   build time).
4. Driver milestones → batched hardware tests, persistent logs, known-good slot.
5. Full tvOS integration → milestone runs only.

That keeps the edit/test cycle in seconds for most changes, and minutes only when you are
actually testing hardware-specific behavior.
