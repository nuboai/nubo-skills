#!/usr/bin/env bash
# Bump a pinned ref in registry.yml, sync upstream, validate
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET="${1:-}"
NAME="${2:-}"
UPSTREAM="${3:-}"
NEW_REF="${4:-}"

usage() {
  cat <<EOF
Usage:
  $0 command <command> <upstream_name> <new_ref>
  $0 preset <preset> <upstream_name> <new_ref>

Examples:
  $0 command nb-review-code code-review-and-quality fefc408
  $0 preset nb-conventions context-engineering fefc408
EOF
  exit 1
}

if [[ -z "$TARGET" || -z "$NAME" || -z "$UPSTREAM" || -z "$NEW_REF" ]]; then
  usage
fi

if [[ "$TARGET" != "command" && "$TARGET" != "preset" ]]; then
  echo "Target must be 'command' or 'preset'" >&2
  usage
fi

"$ROOT/scripts/ensure-deps.sh"

python3 - "$TARGET" "$NAME" "$UPSTREAM" "$NEW_REF" <<'PY'
import sys
from pathlib import Path
import yaml

target, name, upstream, new_ref = sys.argv[1:5]
path = Path("registry.yml")
data = yaml.safe_load(path.read_text())

if target == "command":
    section = data.get("commands", {})
    label = "command"
elif target == "preset":
    section = data.get("presets", {})
    label = "preset"
else:
    raise SystemExit(f"Unknown target: {target}")

entry = section.get(name)
if not entry:
    raise SystemExit(f"Unknown {label}: {name}")

updated = False
for compose in entry.get("composes", []):
    if compose.get("upstream_name") == upstream:
        compose["ref"] = new_ref
        updated = True

if not updated:
    raise SystemExit(f"Upstream {upstream} not found in {label} {name}")

path.write_text(yaml.dump(data, sort_keys=False))
print(f"Updated {label} {name} -> {upstream} ref to {new_ref}")
PY

"$ROOT/scripts/sync-upstream.sh"
"$ROOT/scripts/validate.sh"
