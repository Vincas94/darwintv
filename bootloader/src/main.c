#include "board.h"
#include "payload.h"
#include "pl011.h"

#include <stdint.h>

void fault_report(uint64_t esr, uint64_t elr, uint64_t far, uint64_t spsr)
{
	pl011_puts(PL011_BASE, "\nFAULT\n");
	pl011_puts(PL011_BASE, "esr:  ");
	pl011_put_hex(PL011_BASE, esr);
	pl011_puts(PL011_BASE, "\nelr:  ");
	pl011_put_hex(PL011_BASE, elr);
	pl011_puts(PL011_BASE, "\nfar:  ");
	pl011_put_hex(PL011_BASE, far);
	pl011_puts(PL011_BASE, "\nspsr: ");
	pl011_put_hex(PL011_BASE, spsr);
	pl011_puts(PL011_BASE, "\n");

	for (;;) {
		__asm__ volatile("wfe");
	}
}

void loader_main(uint64_t dtb)
{
	struct payload_info info;
	uint64_t cntfrq;

	__asm__ volatile("mrs %0, cntfrq_el0" : "=r"(cntfrq));

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
	pl011_puts(PL011_BASE, "\ncntfrq:  ");
	pl011_put_hex(PL011_BASE, cntfrq);
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
