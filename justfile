set shell := ["bash", "-euo", "pipefail", "-c"]

default:
    @just --list

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

loader board="pi5":
    make -C bootloader BOARD={{board}}

qemu:
    ./scripts/run-qemu.sh

xnu-fetch:
    ./scripts/fetch-xnu.sh

xnu-patches:
    ./scripts/apply-patches.sh

clean:
    make -C bootloader clean
    rm -rf site .pytest_cache .ruff_cache .mypy_cache
