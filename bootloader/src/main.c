#include "board.h"
#include "pl011.h"

#include <stdint.h>

static void put_hex(uintptr_t value)
{
	static const char digits[] = "0123456789abcdef";
	char buffer[2 + sizeof(uintptr_t) * 2];
	unsigned int i;

	buffer[0] = '0';
	buffer[1] = 'x';
	for (i = 0; i < sizeof(uintptr_t) * 2; i++) {
		unsigned int shift = (unsigned int)(sizeof(uintptr_t) * 8 - 4 - i * 4);
		buffer[2 + i] = digits[(value >> shift) & 0xfu];
	}
	for (i = 0; i < sizeof(buffer); i++) {
		pl011_putc(PL011_BASE, buffer[i]);
	}
}

void loader_main(void)
{
	pl011_init(PL011_BASE);

	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "DarwinTV loader\n");
	pl011_puts(PL011_BASE, "board:  " BOARD_NAME "\n");
	pl011_puts(PL011_BASE, "load:   ");
	put_hex((uintptr_t)LOAD_ADDR);
	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "uart:   ");
	put_hex((uintptr_t)PL011_BASE);
	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "hello from the other side of the SoC\n");

	for (;;) {
		__asm__ volatile("wfe");
	}
}
