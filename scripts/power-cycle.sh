#!/usr/bin/env bash
set -euo pipefail

# Runs the power-cycle command you provide. No hardcoded device is touched.
#
# Examples:
#   POWER_CMD="uhubctl -a cycle -p 1"
#   POWER_CMD="usbrelay ABCDE_1=0; sleep 2; usbrelay ABCDE_1=1"
#   POWER_CMD="curl -s http://smartplug.local/reboot"

if [ -z "${POWER_CMD:-}" ]; then
    echo "error: set POWER_CMD to your relay/smart-plug command" >&2
    echo "       example: POWER_CMD='uhubctl -a cycle -p 1'" >&2
    exit 1
fi

echo "==> power cycle: $POWER_CMD"
bash -c "$POWER_CMD"
