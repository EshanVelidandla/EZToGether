#!/usr/bin/env bash
# Run the full pipeline: raw downloads to figures.
set -euo pipefail
cd "$(dirname "$0")"
for step in places acs atlas merge summarize plot; do
  echo "==> $step"
  python "scripts/$step.py"
done
