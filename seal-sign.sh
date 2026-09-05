#!/usr/bin/env bash
set -euo pipefail
input_file="${1:-}"
signer="${2:-user:jason}"
if [ -z "$input_file" ] || [ ! -f "$input_file" ]; then
    echo "Usage: seal-sign.sh <file> <signer>" >&2
    exit 1
fi
echo "{\"artifact\": \"$(basename "$input_file")\", \"sha256\": \"$(sha256sum "$input_file" | awk '{print $1}')\", \"signer\": \"$signer\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
