# Third-party licenses

DarwinTV does not vendor third-party source at this time. The table records the
upstreams it fetches, patches, or references.

| Upstream | License | How it is used |
|---|---|---|
| [apple-oss-distributions/xnu](https://github.com/apple-oss-distributions/xnu) | APSL-2.0 | Fetched at a pinned tag; `patches/` are applied to it |
| [tansanrao/xnu](https://github.com/tansanrao/xnu) | APSL-2.0 (XNU fork) | Research reference for non-Apple arm64, GICv2 and timer work |
| [tansanrao/xnu-on-pi](https://github.com/tansanrao/xnu-on-pi) | No explicit license | Design reference only; no code is copied |
| [dipa-studio/ios-sweet](https://github.com/dipa-studio/ios-sweet) | No explicit license | Research reference only; no code is copied |
| [oosexgang/hakios-xnu-kernel](https://github.com/oosexgang/hakios-xnu-kernel) | MIT + APSL-2.0 | Research reference for loader, GIC and userland bring-up |
| [Raspberry Pi Linux](https://github.com/raspberrypi/linux) | GPL-2.0 | Device-tree facts and hardware addresses; no code is copied |
| [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/) | CC BY-SA 4.0 / custom | Hardware and boot-flow reference |

If you believe a file is missing an attribution, open an issue and it will be
fixed.
