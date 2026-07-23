#!/usr/bin/env bash
# Bootstrap and sync all nubo-skills dependencies.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

UPGRADE=false
SKIP_GENERATE=false

usage() {
  cat <<EOF
Usage: $0 [--upgrade] [--skip-generate]

Installs Python dependencies, initializes upstream submodules, checks out
pinned refs from registry.yml, regenerates the extension manifest, and
refreshes nubo-skills.lock.
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --upgrade) UPGRADE=true; shift ;;
    --skip-generate) SKIP_GENERATE=true; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

chmod +x "$ROOT"/scripts/*.sh

if [[ "$UPGRADE" == true ]]; then
  "$ROOT/scripts/ensure-deps.sh" --upgrade
else
  "$ROOT/scripts/ensure-deps.sh"
fi

"$ROOT/scripts/sync-upstream.sh" --checkout

if [[ "$SKIP_GENERATE" == false ]]; then
  python3 "$ROOT/scripts/generate_skills.py"
  "$ROOT/scripts/sync-upstream.sh"
fi

echo "Setup complete."
