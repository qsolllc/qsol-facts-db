#!/usr/bin/env bash
set -euo pipefail

in="$1"
kind="$2"

canon="$(jq -S '.' "$in")"
hash="sha256:$(printf '%s' "$canon" | sha256sum | awk '{print $1}')"

case "$kind" in
  feature_spec)
    jq --arg h "$hash" '.hashes.feature_hash = $h' <<<"$canon"
    ;;
  conductor_plan)
    jq --arg h "$hash" '.hashes.plan_hash = $h' <<<"$canon"
    ;;
  tool_invocation)
    jq --arg h "$hash" '.hashes.tool_hash = $h' <<<"$canon"
    ;;
  prompt_artifact)
    jq --arg h "$hash" '.hashes.prompt_hash = $h' <<<"$canon"
    ;;
  optimizer_job)
    jq --arg h "$hash" '.hashes.job_hash = $h' <<<"$canon"
    ;;
  zk_proof)
    jq --arg h "$hash" '.hashes.zk_hash = $h' <<<"$canon"
    ;;
  provenance_record)
    jq --arg h "$hash" '.hashes.provenance_hash = $h' <<<"$canon"
    ;;
  *)
    echo "unknown kind: $kind" >&2
    exit 1
    ;;
esac
