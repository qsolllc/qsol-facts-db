#!/usr/bin/env bash
set -euo pipefail
export SOVEREIGN_ROOT="/data/data/com.termux/files/home/sovereign"
export PATH="$SOVEREIGN_ROOT/bin:$PATH"

echo "[1/4] Generating valid feature spec..."
echo '{"spec_id": "MNT4992-FEATURE-001", "version": "1.0.0", "target": "QSOL-CORE-V1", "invariant": "333"}' > feature_spec.json

echo "[2/4] Executing seal-hash..."
./seal-hash.sh feature_spec.json feature_spec > feature_spec.sealed.json

echo "[3/4] Executing seal-sign..."
./seal-sign.sh feature_spec.sealed.json user:jason > feature_spec.final.json

echo "[4/4] Verifying artifacts and signatures..."
./verify-artifact.sh feature_spec.final.json
./verify-signature.sh feature_spec.final.json
echo "Pipeline execution completed successfully."
