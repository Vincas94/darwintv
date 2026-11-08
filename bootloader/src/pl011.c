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
	while ((mmio_read32(base, PL011_FR) & PL011_FR_BUSY) != 0) {
	}
	mmio_write32(base, PL011_CR, 0);
	mmio_write32(base, PL011_LCRH, PL011_LCRH_WLEN_8 | PL011_LCRH_FEN);
	mmio_write32(base, PL011_IMSC, 0);
	mmio_write32(base, PL011_ICR, 0x7ff);
	mmio_write32(base, PL011_CR, PL011_CR_UARTEN | PL011_CR_TXE | PL011_CR_RXE);
}

void pl011_set_baud(uintptr_t base, uint32_t uartclk, uint32_t baud)
{
	uint32_t div64 = (uartclk * 4u + baud / 2u) / baud;
	uint32_t ibrd = div64 / 64u;
	uint32_t fbrd = div64 % 64u;
	uint32_t cr = mmio_read32(base, PL011_CR);

	mmio_write32(base, PL011_CR, cr & ~PL011_CR_UARTEN);
	mmio_write32(base, PL011_IBRD, ibrd);
	mmio_write32(base, PL011_FBRD, fbrd);
	mmio_write32(base, PL011_LCRH, PL011_LCRH_WLEN_8 | PL011_LCRH_FEN);
	mmio_write32(base, PL011_CR, cr | PL011_CR_UARTEN | PL011_CR_TXE | PL011_CR_RXE);
}

int pl011_rx_ready(uintptr_t base)
{
	return (mmio_read32(base, PL011_FR) & PL011_FR_RXFE) == 0;
}

char pl011_getc(uintptr_t base)
{
	uint32_t dr;

	while (pl011_rx_ready(base) == 0) {
	}
	dr = mmio_read32(base, PL011_DR);
	if ((dr & PL011_DR_ERR_MASK) != 0) {
		mmio_write32(base, PL011_ECR, 0);
	}
	return (char)(dr & 0xffu);
}

void pl011_putc(uintptr_t base, char c)
{
	while ((mmio_read32(base, PL011_FR) & PL011_FR_TXFF) != 0) {
	}
	mmio_write32(base, PL011_DR, (uint8_t)c);
}

void pl011_put_hex(uintptr_t base, uintptr_t value)
{
	static const char digits[] = "0123456789abcdef";
	unsigned int i;

	pl011_puts(base, "0x");
	for (i = 0; i < sizeof(uintptr_t) * 2; i++) {
		unsigned int shift = (unsigned int)(sizeof(uintptr_t) * 8 - 4 - i * 4);
		pl011_putc(base, digits[(value >> shift) & 0xfu]);
	}
}

void pl011_put_hex32(uintptr_t base, uint32_t value)
{
	static const char digits[] = "0123456789abcdef";
	unsigned int i;

	pl011_puts(base, "0x");
	for (i = 0; i < 8; i++) {
		unsigned int shift = 28u - i * 4u;
		pl011_putc(base, digits[(value >> shift) & 0xfu]);
	}
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
