/*
 * DarwinTV AArch64 entry point.
 *
 * The Pi 5 firmware starts the image at EL2 (TF-A BL31) with x0 = DTB.
 * QEMU raspi4b also enters at EL2. Handle EL3 as well so the same image can
 * be started by a debugger or a different armstub.
 *
 * The hello loader only needs a stack and a C environment. The XNU jump will
 * replace the final wfe loop with the boot_args handoff.
 */

#include "board.h"

.section .text.boot, "ax"
.global _start
.type _start, %function

_start:
    /* The firmware passes the DTB in x0; keep it in a callee-saved register. */
    mov x19, x0

    /*
     * Fail loudly if the firmware loaded us at a different address than the
     * one we were linked for (old Pi 5 EEPROMs used 0x80000). Use only
     * PC-relative references and a corrected stack so this can print even
     * when the image has been relocated.
     */
    adr x20, _start
    ldr x21, =LOAD_ADDR
    cmp x20, x21
    b.eq .Lload_ok

    sub x22, x20, x21
    ldr x0, =__stack_top
    add sp, x0, x22
    ldr x0, =PL011_BASE
    adr x1, wrong_load
    bl pl011_puts
    b .Lpark

.Lload_ok:
    ldr x0, =__stack_top
    mov sp, x0

    /* Park every core except CPU 0 (MPIDR_EL1.Aff0). */
    mrs x0, mpidr_el1
    and x0, x0, #0xff
    cbz x0, .Lboot_cpu

.Lpark:
    wfe
    b .Lpark

.Lboot_cpu:
    /* EL3 -> EL2: non-secure, AArch64 lower levels, HVC enabled. */
    mrs x0, CurrentEL
    lsr x0, x0, #2
    cmp x0, #3
    b.ne .Lel2

    mov x0, #((1 << 10) | (1 << 8) | (1 << 0)) /* SCR_EL3: RW, HCE, NS */
    msr scr_el3, x0
    mov x0, #0x3c9                             /* EL2h, DAIF masked */
    msr spsr_el3, x0
    adr x0, .Lel2
    msr elr_el3, x0
    eret

.Lel2:
    /* EL2 -> EL1: AArch64 EL1, no traps, timer and counter reachable. */
    mrs x0, CurrentEL
    lsr x0, x0, #2
    cmp x0, #2
    b.ne .Lel1

    /* Exceptions in the EL2 setup path should report instead of hanging. */
    adrp x0, exception_vectors
    add x0, x0, :lo12:exception_vectors
    msr vbar_el2, x0

    /* EL1 reads of MIDR/MPIDR return the EL2 values; XNU uses them. */
    mrs x0, midr_el1
    msr vpidr_el2, x0
    mrs x0, mpidr_el1
    msr vmpidr_el2, x0

    mov x0, #(1 << 31) /* HCR_EL2.RW */
    msr hcr_el2, x0
    msr cptr_el2, xzr
    mrs x0, cnthctl_el2
    orr x0, x0, #3
    msr cnthctl_el2, x0
    msr cntvoff_el2, xzr

    ldr x0, =0x30d00800 /* SCTLR_EL1 RES1 bits; M=C=I=0 */
    msr sctlr_el1, x0
    mov x0, #0x3c5      /* EL1h, DAIF masked */
    msr spsr_el2, x0
    adr x0, .Lel1
    msr elr_el2, x0
    eret

.Lel1:
    ldr x0, =0x30d00800
    msr sctlr_el1, x0
    isb

    adrp x0, exception_vectors
    add x0, x0, :lo12:exception_vectors
    msr vbar_el1, x0

    ldr x0, =__stack_top
    mov sp, x0

    /* Clear .bss. */
    ldr x0, =__bss_start
    ldr x1, =__bss_end
.Lbss:
    cmp x0, x1
    b.hs .Lrun
    str xzr, [x0], #8
    b .Lbss

.Lrun:
    mov x0, x19
    bl loader_main

.Lhalt:
    wfe
    b .Lhalt

.size _start, . - _start

/*
 * Exception vectors. All 16 entries report and park; the loader does not try
 * to recover. This turns a silent fault into a useful ESR/ELR/FAR line.
 */
.section .text.vectors, "ax"
.align 11
exception_vectors:
.rept 16
    b fault_handler
    .space 0x7c
.endr

.align 2
fault_handler:
    msr daifset, #0xf

    mrs x4, CurrentEL
    lsr x4, x4, #2
    cmp x4, #2
    b.eq .Lfault_el2

    mrs x0, esr_el1
    mrs x1, elr_el1
    mrs x2, far_el1
    mrs x3, spsr_el1
    b .Lfault_report

.Lfault_el2:
    mrs x0, esr_el2
    mrs x1, elr_el2
    mrs x2, far_el2
    mrs x3, spsr_el2

.Lfault_report:
    bl fault_report
.Lfault_halt:
    wfe
    b .Lfault_halt

.section .rodata
wrong_load:
    .asciz "DarwinTV: wrong load address; update EEPROM\r\n"
