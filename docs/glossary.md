# Glossary

| Term | Meaning |
|---|---|
| **ADT** | Apple Device Tree. XNU's flattened tree format, not an FDT. |
| **AMFI** | Apple Mobile File Integrity; code-signing enforcement. Stubbed/permissive in bring-up. |
| **APFS** | Apple File System. The tvOS system image is APFS; HFS+ is used for the first root. |
| **AIC** | Apple Interrupt Controller, used on Apple SoCs. The Pi 5 has a GIC-400 instead. |
| **boot_args** | The `struct boot_args` XNU receives in `x0`: memory, ADT, command line, video. |
| **DTB / DTS** | Flattened Device Tree / Device Tree Source. The firmware passes a DTB to the loader. |
| **dyld shared cache** | Apple's prelinked system libraries; needed by `launchd`/`PineBoard`. |
| **fastboot** | Android bootloader protocol; `fastboot boot` loads an image into RAM without flashing. |
| **FDT** | Flattened Device Tree. XNU does not parse it; the loader converts/bridges to an ADT. |
| **GIC-400 / GICv2** | ARM Generic Interrupt Controller, v2. Pi 5 uses it for SPIs/PPIs. |
| **HFS+** | Apple's older filesystem; simpler than APFS for the first tvOS root. |
| **IM4P** | Apple's image container (`IM4P` magic) used for device trees, firmware, kernelcache. |
| **iBoot / iBSS / iBEC / LLB** | Apple's boot chain stages. Not used by DarwinTV. |
| **IPSW** | Apple's firmware restore ZIP. Contains `OS`, `DeviceTree`, `kernelcache`, etc. |
| **kernelcache** | Apple's prelinked kernel image. Encrypted/personalized; DarwinTV builds XNU instead. |
| **M1/M2/...** | DarwinTV milestones, not Apple's M-series chips. |
| **mockfs** | A minimal in-memory filesystem used for the first userland bring-up. |
| **PAC** | Pointer Authentication Codes (ARMv8.3). A76 has no PAC; use arm64, non-arm64e. |
| **PineBoard / HeadBoard** | tvOS's UI process pair; replaces SpringBoard. |
| **PL011** | ARM's standard UART. Pi 5 debug UART is a PL011. |
| **PPI / SPI / SGI** | GIC interrupt classes: per-processor, shared peripheral, software-generated. |
| **PSCI** | Power State Coordination Interface; TF-A provides `CPU_ON` on the Pi 5. |
| **RP1** | Raspberry Pi 5's southbridge: USB, Ethernet, 40-pin GPIO, UART0 over PCIe. |
| **SDHCI** | Standard SD host controller interface. Pi 5 microSD is `sdio1`. |
| **SEP** | Secure Enclave Processor. Not present/usable on the Pi 5; stubbed. |
| **TF-A** | ARM Trusted Firmware-A (BL31). Pi 5 runs it at EL3 and drops to EL2. |
| **TFTP** | Trivial File Transfer Protocol; used for Pi 5 network boot. |
| **XNU** | Apple's kernel (Mach + BSD + IOKit). APSL-2.0. |
