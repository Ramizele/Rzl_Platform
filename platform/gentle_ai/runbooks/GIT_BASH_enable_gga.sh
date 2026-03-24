#!/usr/bin/env bash
set -euo pipefail

if ! command -v gga >/dev/null 2>&1; then
  echo "gga not found. Install gentle-ai with the gga component first."
  exit 1
fi

gga init
gga install

echo "GGA enabled for this repository."
