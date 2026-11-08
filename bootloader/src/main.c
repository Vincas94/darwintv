#include "board.h"
#include "payload.h"
#include "pl011.h"

#include <stdint.h>

void loader_main(uint64_t dtb)
{
	struct payload_info info;

	pl011_init(PL011_BASE);

	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "DarwinTV loader\n");
	pl011_puts(PL011_BASE, "board:   " BOARD_NAME "\n");
	pl011_puts(PL011_BASE, "load:    ");
	pl011_put_hex(PL011_BASE, (uintptr_t)LOAD_ADDR);
	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "uart:    ");
	pl011_put_hex(PL011_BASE, (uintptr_t)PL011_BASE);
	pl011_puts(PL011_BASE, "\n");
	pl011_puts(PL011_BASE, "dtb:     ");
	pl011_put_hex(PL011_BASE, (uintptr_t)dtb);
	pl011_puts(PL011_BASE, "\n");

	if (payload_validate((const void *)PAYLOAD_ADDR, PAYLOAD_MAX_SIZE, &info)) {
		payload_print(&info);
		pl011_puts(PL011_BASE, "payload valid; copy/jump is the next M2 step\n");
	} else {
		pl011_puts(PL011_BASE, "no valid payload at ");
		pl011_put_hex(PL011_BASE, (uintptr_t)PAYLOAD_ADDR);
		pl011_puts(PL011_BASE, "\n");
	}

	for (;;) {
		__asm__ volatile("wfe");
	}
}
