#ifndef DARWINTV_PL011_H
#define DARWINTV_PL011_H

#include <stdint.h>

#define PL011_DR 0x00u
#define PL011_ECR 0x04u
#define PL011_FR 0x18u
#define PL011_IBRD 0x24u
#define PL011_FBRD 0x28u
#define PL011_LCRH 0x2cu
#define PL011_CR 0x30u
#define PL011_IMSC 0x38u
#define PL011_ICR 0x44u

#define PL011_FR_RXFE (1u << 4)
#define PL011_FR_TXFF (1u << 5)
#define PL011_DR_ERR_MASK (0xfu << 8)
#define PL011_CR_UARTEN (1u << 0)
#define PL011_CR_TXE (1u << 8)
#define PL011_CR_RXE (1u << 9)

#define PL011_LCRH_FEN (1u << 4)
#define PL011_LCRH_WLEN_8 (3u << 5)

#define PL011_UARTCLK 9216000u
#define PL011_MAX_BAUD (PL011_UARTCLK / 16u)

void pl011_init(uintptr_t base);
void pl011_set_baud(uintptr_t base, uint32_t uartclk, uint32_t baud);
void pl011_putc(uintptr_t base, char c);
void pl011_put_hex(uintptr_t base, uintptr_t value);
int pl011_rx_ready(uintptr_t base);
char pl011_getc(uintptr_t base);
void pl011_puts(uintptr_t base, const char *s);

#endif /* DARWINTV_PL011_H */
