#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/build/netboot/darwintv"
TFTP_ROOT="${TFTP_ROOT:-/srv/tftp}"
TFTP_USER="${TFTP_USER:-tftp}"

if [ ! -d "$SRC" ]; then
    echo "error: $SRC is missing; run make netboot first" >&2
    exit 1
fi

SUDO=()
if [ "$(id -u)" -ne 0 ]; then
    SUDO=(sudo)
fi

"${SUDO[@]}" mkdir -p "$TFTP_ROOT/darwintv"
"${SUDO[@]}" cp -r "$SRC/." "$TFTP_ROOT/darwintv/"

if id "$TFTP_USER" >/dev/null 2>&1; then
    "${SUDO[@]}" chown -R "$TFTP_USER:$TFTP_USER" "$TFTP_ROOT/darwintv"
else
    echo "warning: user '$TFTP_USER' does not exist; leaving ownership unchanged" >&2
fi
"${SUDO[@]}" chmod -R a+rX "$TFTP_ROOT/darwintv"

echo "==> published $SRC -> $TFTP_ROOT/darwintv"
echo "    test: tftp 127.0.0.1 -c get darwintv/config.txt /tmp/tftp-test.txt"
