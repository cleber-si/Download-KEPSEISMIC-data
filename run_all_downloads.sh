#!/bin/bash
set -e

SCRIPTS_DIR="download_files"

if [[ ! -d "$SCRIPTS_DIR" ]]; then
  echo "Error: directory '$SCRIPTS_DIR' not found."
  exit 1
fi

echo "Starting all group downloads…"
for script in "$SCRIPTS_DIR"/*.sh; do
  echo "→ Executing $script"
  bash "$script"
done

echo "✅ All group downloads complete."
