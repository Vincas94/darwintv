#!/usr/bin/env bash
set -euo pipefail

SERIAL_DEV="${SERIAL_DEV:-/dev/ttyACM0}"
SERIAL_BAUD="${SERIAL_BAUD:-115200}"
WAIT_FOR="${WAIT_FOR:-DarwinTV}"
TIMEOUT="${TIMEOUT:-30}"
LOG="${LOG:-logs/serial-$(date +%Y%m%d-%H%M%S).log}"

mkdir -p "$(dirname "$LOG")"

if ! command -v picocom >/dev/null 2>&1 && ! command -v tio >/dev/null 2>&1; then
    echo "error: install picocom or tio" >&2
    exit 1
fi

echo "==> capturing $SERIAL_DEV at $SERIAL_BAUD for ${TIMEOUT}s -> $LOG"
if command -v tio >/dev/null 2>&1; then
    timeout "$TIMEOUT" tio -b "$SERIAL_BAUD" -l "$LOG" "$SERIAL_DEV" || true
else
    timeout "$TIMEOUT" picocom -b "$SERIAL_BAUD" --logfile "$LOG" "$SERIAL_DEV" || true
fi

if grep -q "$WAIT_FOR" "$LOG"; then
    echo "==> PASS: saw '$WAIT_FOR'"
    exit 0
fi

echo "==> FAIL: did not see '$WAIT_FOR' in $TIMEOUT s" >&2
tail -40 "$LOG" >&2 || true
exit 1
