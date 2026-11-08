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

.section .text.boot, "ax"
.global _start
.type _start, %function

_start:
    /* Park every core except CPU 0 (MPIDR_EL1.Aff0). */
    mrs x0, mpidr_el1
    and x0, x0, #0xff
    cbz x0, 1f

0:
    wfe
    b 0b

1:
    /* EL3 -> EL2: non-secure, AArch64 lower levels, HVC enabled. */
    mrs x0, CurrentEL
    lsr x0, x0, #2
    cmp x0, #3
    b.ne 2f

    mov x0, #((1 << 10) | (1 << 8) | (1 << 0)) /* SCR_EL3: RW, HCE, NS */
    msr scr_el3, x0
    mov x0, #0x3c9                             /* EL2h, DAIF masked */
    msr spsr_el3, x0
    adr x0, 2f
    msr elr_el3, x0
    eret

2:
    /* EL2 -> EL1: AArch64 EL1, no traps, timer and counter reachable. */
    mrs x0, CurrentEL
    lsr x0, x0, #2
    cmp x0, #2
    b.ne 3f

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
    adr x0, 3f
    msr elr_el2, x0
    eret

3:
    ldr x0, =0x30d00800
    msr sctlr_el1, x0
    isb

    ldr x0, =__stack_top
    mov sp, x0

    /* Clear .bss. */
    ldr x0, =__bss_start
    ldr x1, =__bss_end
4:
    cmp x0, x1
    b.hs 5f
    str xzr, [x0], #8
    b 4b

5:
    bl loader_main

6:
    wfe
    b 6b

.size _start, . - _start
