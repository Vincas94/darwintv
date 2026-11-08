SHELL := /bin/bash
.DEFAULT_GOAL := help

BOARD ?= pi5
XNU_VERSION ?= xnu-8796.141.3
KERNEL ?= build/kernel.development.bcm2712

.PHONY: help bootstrap check lint test fmt docs loader qemu xnu-fetch xnu-patches netboot publish-netboot payload hw-smoke clean

help:
	@echo "DarwinTV"
	@echo "  make bootstrap      install host dependencies in .venv"
	@echo "  make check          lint + tests + docs + shell/C checks"
	@echo "  make loader         build bootloader/build/$(BOARD)/loader8.img"
	@echo "  make qemu           hello loader under QEMU raspi4b"
	@echo "  make docs           build the MkDocs site"
	@echo "  make xnu-fetch      fetch XNU $(XNU_VERSION) into third_party/xnu"
	@echo "  make xnu-patches    apply patches/ to third_party/xnu"
	@echo "  make clean          remove build output"

bootstrap:
	./scripts/bootstrap.sh

check:
	./scripts/check.sh

lint:
	ruff check .
	ruff format --check .
	shellcheck scripts/*.sh
	clang-format --dry-run --Werror bootloader/src/*.c bootloader/include/*.h

test:
	pytest -q

fmt:
	ruff check --fix .
	ruff format .
	clang-format -i bootloader/src/*.c bootloader/include/*.h

docs:
	mkdocs build --strict

loader:
	$(MAKE) -C bootloader BOARD=$(BOARD)

qemu:
	./scripts/run-qemu.sh

xnu-fetch:
	./scripts/fetch-xnu.sh $(XNU_VERSION)

xnu-patches:
	./scripts/apply-patches.sh

payload:
	./scripts/mkpayload.sh $(KERNEL)

netboot:
	./scripts/make-netboot-dir.sh

publish-netboot: netboot
	./scripts/publish-netboot.sh

hw-smoke:
	./scripts/flash-payload.sh
	./scripts/power-cycle.sh
	./scripts/serial-capture.sh

clean:
	$(MAKE) -C bootloader clean
	rm -rf site .pytest_cache .ruff_cache .mypy_cache
