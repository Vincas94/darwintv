# DarwinTV M1 loader.
#
#   make BOARD=pi5            -> build/loader8.img at 0x00200000
#   make BOARD=qemu-raspi4b   -> build/loader8.img at 0x00080000

CROSS_COMPILE ?= aarch64-linux-gnu-
CC := $(CROSS_COMPILE)gcc
OBJCOPY := $(CROSS_COMPILE)objcopy

BOARD ?= pi5

ifeq ($(BOARD),qemu-raspi4b)
BOARD_DEFINE := -DBOARD_QEMU_RASPI4B
LOAD_ADDR := 0x00080000
else ifeq ($(BOARD),qemu-virt)
BOARD_DEFINE := -DBOARD_QEMU_VIRT
LOAD_ADDR := 0x40000000
else
BOARD_DEFINE := -DBOARD_RASPBERRY_PI_5
LOAD_ADDR := 0x00200000
endif

BUILD := build/$(BOARD)
ELF := $(BUILD)/loader.elf
IMG := $(BUILD)/loader8.img

CFLAGS := -std=c11 -O2 -g -Wall -Wextra -Werror -ffreestanding \
          -fno-stack-protector -fno-pic -fno-pie -mgeneral-regs-only \
          $(BOARD_DEFINE) -Iinclude
LDFLAGS := -T linker.ld -nostdlib -nostartfiles -Wl,--build-id=none \
           -Wl,--no-warn-rwx-segments -Wl,--defsym=LOAD_ADDR=$(LOAD_ADDR)

SRCS := src/start.S src/main.c src/pl011.c src/payload.c
OBJS := $(patsubst src/%,$(BUILD)/%.o,$(SRCS))

.PHONY: all clean

all: $(IMG)

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%.S.o: src/%.S | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/%.c.o: src/%.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(ELF): $(OBJS) linker.ld
	$(CC) $(LDFLAGS) $(OBJS) -o $@

$(IMG): $(ELF)
	$(OBJCOPY) -O binary $< $@
	@echo "built $@ for BOARD=$(BOARD) (load $(LOAD_ADDR))"

clean:
	rm -rf build
