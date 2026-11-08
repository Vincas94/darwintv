# Hardware safety

## Electrical

- The Pi 5 debug UART is **3.3 V only**. Do not connect VCC/3.3 V/5 V from the adapter.
- Connect GND, adapter TX → Pi RX, adapter RX → Pi TX.
- Use a 3.3 V adapter or level shifter. A 5 V adapter can damage the Pi.
- Keep wires short at 460800/576000 baud; long dupont wires corrupt data.

## Storage

- Back up the boot partition and keep a known-good SD card.
- Do not `dd` to a device while it is mounted.
- `flash-payload.sh` only copies to a mounted directory; it never writes a block device.
- Keep a known-good payload slot and a `config-recovery.txt`.

## EEPROM

- The SPI EEPROM bootloader is separate from the OS. A bad payload cannot brick it.
- If the EEPROM is corrupted, use `rpiboot`/the EEPROM recovery image.
- `rpi-eeprom-config --edit` changes the bootloader config; back up the current config first.

## Power and thermal

- Use the official 5V/5A supply for a Pi 5 with USB/NVMe peripherals.
- Fit a heatsink or active cooler; XNU bring-up will spin all cores.
- A smart plug/USB relay is safer than manually yanking power; use `power-cycle.sh`.

## Legal

- Do not distribute Apple IPSWs, kernelcaches, device trees, userland, keys or certificates.
- Do not bypass activation/DRM.
- See `NOTICE`, `THIRD_PARTY_LICENSES.md`, `docs/tvos.md`.
