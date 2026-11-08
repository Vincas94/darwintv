#include "pl011.h"

#include <stdint.h>

static inline void mmio_write32(uintptr_t base, uint32_t offset, uint32_t value)
{
	*(volatile uint32_t *)(base + offset) = value;
}

static inline uint32_t mmio_read32(uintptr_t base, uint32_t offset)
{
	return *(volatile uint32_t *)(base + offset);
}

void pl011_init(uintptr_t base)
{
	/*
	 * The firmware already configured the debug UART for 115200 8N1. Do not
	 * touch IBRD/FBRD until the BCM2712 clock tree is known: reprogramming the
	 * divisor with the wrong reference clock produces garbage.
	 */
	mmio_write32(base, PL011_CR, 0);
	mmio_write32(base, PL011_LCRH, PL011_LCRH_WLEN_8 | PL011_LCRH_FEN);
	mmio_write32(base, PL011_IMSC, 0);
	mmio_write32(base, PL011_ICR, 0x7ff);
	mmio_write32(base, PL011_CR, PL011_CR_UARTEN | PL011_CR_TXE | PL011_CR_RXE);
}

void pl011_putc(uintptr_t base, char c)
{
	while ((mmio_read32(base, PL011_FR) & PL011_FR_TXFF) != 0) {
	}
	mmio_write32(base, PL011_DR, (uint8_t)c);
}

void pl011_puts(uintptr_t base, const char *s)
{
	while (*s != '\0') {
		if (*s == '\n') {
			pl011_putc(base, '\r');
		}
		pl011_putc(base, *s++);
	}
}
