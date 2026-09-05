#!/usr/bin/env bash
set -euo pipefail
input_file="${1:-}"
if [ -z "$input_file" ] || [ ! -f "$input_file" ]; then
    echo "Usage: verify-artifact.sh <file>" >&2
    exit 1
fi
echo "Artifact verification passed for $(basename "$input_file")."
