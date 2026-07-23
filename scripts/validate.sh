#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
"$ROOT/scripts/ensure-deps.sh"
exec python3 "$ROOT/scripts/validate.py" "$@"
