#!/bin/bash

set -euo pipefail

LOGFILE=$(mktemp --tmpdir install_log.XXXXXX)
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

run_script() {
  local script_name="$1"
  echo "Running local: $script_name"
  "$BASE_DIR/install/$script_name" >> "$LOGFILE"
}

# Run install scripts
run_script "packages.sh"
run_script "packages-extn.sh"
run_script "packages-manual.sh"
run_script "dotfiles.sh"

echo "DONE"
