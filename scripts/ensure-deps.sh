#!/usr/bin/env bash
# Ensure Python and git submodule dependencies are available.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

UPGRADE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --upgrade) UPGRADE=true; shift ;;
    -h|--help)
      echo "Usage: $0 [--upgrade]"
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if ! python3 -c "import yaml" 2>/dev/null; then
  echo "Installing Python dependencies from requirements.txt"
  if [[ "$UPGRADE" == true ]]; then
    python3 -m pip install --upgrade -r "$ROOT/requirements.txt"
  else
    python3 -m pip install -r "$ROOT/requirements.txt"
  fi
fi

if [[ ! -f "$ROOT/upstream/speckit/.git" ]]; then
  echo "Initializing git submodules"
  git submodule update --init --recursive
fi
