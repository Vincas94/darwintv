ENTRY(_start)

SECTIONS
{
    /* Pi 5 firmware loads kernel8.img at 0x200000; QEMU raspi4b uses 0x80000. */
    . = DEFINED(LOAD_ADDR) ? LOAD_ADDR : 0x00200000;

    .text : ALIGN(16) {
        KEEP(*(.text.boot))
        *(.text .text.*)
    }

    .rodata : ALIGN(16) {
        *(.rodata .rodata.*)
    }

    .data : ALIGN(16) {
        *(.data .data.*)
    }

    .bss (NOLOAD) : ALIGN(16) {
        __bss_start = .;
        *(.bss .bss.*)
        *(COMMON)
        . = ALIGN(16);
        __bss_end = .;
    }

    . = ALIGN(16);
    . += 0x4000;
    __stack_top = .;

    /DISCARD/ : {
        *(.comment)
        *(.note*)
        *(.eh_frame*)
    }

    ASSERT(__stack_top <= 0x02000000 || LOAD_ADDR >= 0x40000000, "loader overlaps the XNU load window")
}
