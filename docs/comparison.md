# Pi 5 + Ethernet vs. phone + fastboot

Short answer: **for self-testing, debugging and booting, the Pi 5 + Ethernet is the better
platform.** Fastboot is an excellent image-loading pipe, but the phone platform is much more
complex and much harder to recover and automate.

## Scorecard

| Dimension | Pi 5 + Ethernet | Phone + fastboot |
|---|---|---|
| Load an image without flashing | TFTP, ~1 s / 15 MB | `fastboot boot`, USB, faster pipe |
| Unlock / secure boot | none by default | unlock, AVB, anti-rollback, vendor locks |
| Boot chain | ROM → EEPROM → TF-A → kernel | PBL → XBL → ABL → hypervisor → kernel, AVB/DTBO/A-B |
| Recovery from a bad image | EEPROM/`rpiboot`/SD; low risk | EDL/DFU; risk of brick, ARB, data loss |
| Power-cycle / automation | smart plug or USB relay; no battery | battery/PMIC; a hung phone may need manual reset |
| Debug console | documented 3-pin UART, PL011 | UART often disabled or test-point only |
| Interrupt controller / timer | GIC-400 + ARM generic timer, documented | GICv3 + vendor PMIC/interconnect/SMMU |
| Storage | standard SDHCI on BCM2712 | UFS + vendor PHY/clock/regulator stack |
| Display/input | firmware framebuffer + UART-injected HID | panel/touch/PMIC; or HakiOS-style drivers |
| Hardware documentation | DTS + datasheets + open firmware | mostly downstream/vendor, NDAs |
| Cost / risk | cheap, replaceable | expensive, daily driver, data loss |
| Existing userland work | tvOS is the target; Pi 4 XNU prior art | ios-sweet/HakiOS already boot iOS on phones |
| CPU/GPU | 4× A76 2.4 GHz; no V3D driver | faster; Adreno has HakiOS Metal work |
| Fit to the payload | tvOS expects an Apple TV, not a Pi | iOS expects an iPhone; both need identity/stubs |

## What fastboot is genuinely better at

- **Raw transfer speed.** USB 3 beats TFTP for a 15 MB image, though both are seconds.
- **A mature "load to RAM" command.** `fastboot boot boot.img` is a well-defined way to run a
  custom image without touching storage.
- **Existing bring-up.** `ios-sweet` and HakiOS have already solved the iOS userland, ADT identity,
  AMFI/sandbox, HFS+ root and much of the display/input stack.
- **Real target hardware.** If the goal is "iOS on a phone", only a phone will do.

## What the Pi 5 is better at

- **Autonomy.** Network boot + serial + a relay = a fully remote test rig. No unlock, no cable to a
  phone, no battery.
- **Recovery.** A bad payload cannot brick the board; the EEPROM bootloader, SD fallback and
  `rpiboot` are independent of what you boot.
- **A short, documented boot chain.** ROM → EEPROM → TF-A → your loader. No iBoot, SEP, AVB,
  hypervisor or vendor XBL in the way.
- **Standard peripherals.** PL011, GIC-400, ARM generic timer, SDHCI; the addresses are in the
  public DTS. The phone equivalents are a reverse-engineering project.
- **Cost and risk.** A Pi 5 is cheap and replaceable; an unlocked phone is not.
- **Repeatability.** The same files, the same TFTP tree, the same serial protocol; a CI runner can
  drive it.

## The nuance

These are not competing targets. **The Pi 5 is the hardware; the phone projects are the software
references.** For tvOS on a Pi 5:

- the Pi 5 gives you the open boot path, network boot, UART and standard peripherals;
- `ios-sweet`/HakiOS give you the techniques for the tvOS/iOS userland: ADT identity, HFS+ root,
  permissive AMFI/sandbox, `AppleKeyStore` stub, display/IOSurface, HID.

If the goal were "run iOS on a phone", the phone + fastboot is the only path. For "run tvOS on a
Pi 5", the Pi 5 is the right target, and it is also the easier platform to test by yourself.

## Verdict

Use the Pi 5 over Ethernet as the primary hardware loop; keep fastboot/phone work as a reference
and as the eventual porting target for the same techniques. The Pi 5 wins on **how much you can
test, debug and boot on your own**; fastboot wins only on the raw USB pipe.
