#!/usr/bin/env bash
# QSol LLC Production Telemetry Guard (Standard 333)
# Enforces real-time invariant filtering, stderr diversion, and atomic log rotation.

INVARIANT="${1:-state == ACTIVE}"
STANDARD="${2:-333}"
VERIFIED_LOG="qsol_verified.log"
BLOCKED_LOG="qsol_blocked.log"
MAX_LINES=50000

echo "[QSol Guard] Initializing stream guard with invariant: '$INVARIANT' (Standard $STANDARD)"

# Ensure log files exist
touch "$VERIFIED_LOG" "$BLOCKED_LOG"

rotate_logs() {
    if [ $(wc -l < "$VERIFIED_LOG") -gt $MAX_LINES ]; then
        echo "[QSol Guard] Rotating verified log (exceeded $MAX_LINES lines)..."
        tail -n $((MAX_LINES / 2)) "$VERIFIED_LOG" > "${VERIFIED_LOG}.tmp"
        mv "${VERIFIED_LOG}.tmp" "$VERIFIED_LOG"
    fi
}

# Main tail loop piping stdin/service output through facts-db tail
# Usage: your_service_stream | ./qsol_daemon_run.sh
while IFS= read -r line; do
    # Pass individual line through facts-db verify/tail guard logic
    echo "$line" | facts-db tail --invariant "$INVARIANT" --standard "$STANDARD" >> "$VERIFIED_LOG" 2>> "$BLOCKED_LOG"
    rotate_logs
done
