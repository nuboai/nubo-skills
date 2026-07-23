#!/usr/bin/env bash
# Bump a pinned ref in registry.yml, sync upstream, validate
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMMAND="${1:-}"
UPSTREAM="${2:-}"
NEW_REF="${3:-}"

if [[ -z "$COMMAND" || -z "$UPSTREAM" || -z "$NEW_REF" ]]; then
  echo "Usage: $0 <command> <upstream_name> <new_ref>" >&2
  echo "Example: $0 nb-review-code code-review-and-quality fefc408" >&2
  exit 1
fi

python3 - "$COMMAND" "$UPSTREAM" "$NEW_REF" <<'PY'
import sys
from pathlib import Path
import yaml

command, upstream, new_ref = sys.argv[1:4]
path = Path("registry.yml")
data = yaml.safe_load(path.read_text())
cmd = data["commands"].get(command)
if not cmd:
    raise SystemExit(f"Unknown command: {command}")
updated = False
for c in cmd.get("composes", []):
    if c.get("upstream_name") == upstream:
        c["ref"] = new_ref
        updated = True
if not updated:
    raise SystemExit(f"Upstream {upstream} not found in {command}")
path.write_text(yaml.dump(data, sort_keys=False))
print(f"Updated {command} -> {upstream} ref to {new_ref}")
PY

"$ROOT/scripts/sync-upstream.sh"
"$ROOT/scripts/validate.sh"
