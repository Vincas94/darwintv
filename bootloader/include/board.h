#ifndef DARWINTV_BOARD_H
#define DARWINTV_BOARD_H

/*
 * Board-specific constants for the M1 hello-world loader.
 *
 * The Pi 5 debug UART is UART10, a PL011 on BCM2712 at 0x107d001000. It is
 * exposed on the 3-pin debug connector and is initialized by the firmware at
 * 115200 8N1. The 40-pin header UART is on RP1 and is deliberately not used.
 */
#if defined(BOARD_QEMU_RASPI4B)
#define BOARD_NAME "qemu-raspi4b"
#define PL011_BASE 0xfe201000UL
#define LOAD_ADDR 0x00080000UL
#elif defined(BOARD_QEMU_VIRT)
#define BOARD_NAME "qemu-virt"
#define PL011_BASE 0x09000000UL
#define LOAD_ADDR 0x40000000UL
#else
#define BOARD_NAME "raspberry-pi-5"
#define PL011_BASE 0x107d001000UL
#define LOAD_ADDR 0x00200000UL
#endif

#endif /* DARWINTV_BOARD_H */
