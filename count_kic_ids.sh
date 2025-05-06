#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="download_files"

if [[ ! -d "$SCRIPTS_DIR" ]]; then
  echo "Error: '$SCRIPTS_DIR' not found." >&2
  exit 1
fi

declare -A all_ids

echo "Counting KIC IDs in each script:"
for script in "$SCRIPTS_DIR"/*.sh; do
  # Extract unique 9-digit IDs after $ROOT/<group>/
  mapfile -t ids < <(
    grep -oP '\$ROOT/[^/]+/\K[0-9]{9}' "$script" | sort -u
  )
  count=${#ids[@]}
  echo "  $(basename "$script"): $count KIC IDs"
  for id in "${ids[@]}"; do
    all_ids["$id"]=1
  done
done

total=${#all_ids[@]}
echo
echo "Total unique KIC IDs across all scripts: $total"
