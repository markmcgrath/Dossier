#!/bin/bash
# Run the Dossier test suite
# Usage: ./tests/run_tests.sh [--verbose]

set -e

# Get directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set vault environment variable
export DOSSIER_VAULT="$VAULT_DIR"

# Run pytest with arguments passed through
python -m pytest "$SCRIPT_DIR" -v "$@"
