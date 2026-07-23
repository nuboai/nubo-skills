#!/usr/bin/env bash
# Remove nubo-skills artifacts installed by scripts/install.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TARGET_DIR="."

usage() {
  cat <<EOF
Usage: $0 [--target DIR]

Removes skills and governance files recorded in .nubo-skills.state.json.
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET_DIR="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

python3 - "$ROOT" "$TARGET_DIR" <<'PY'
import json
import shutil
import sys
from pathlib import Path

import yaml

root, target_arg = sys.argv[1:3]
root = Path(root)
target = Path(target_arg)
state_path = target / ".nubo-skills.state.json"
if not state_path.exists():
    print("No .nubo-skills.state.json found — nothing to uninstall.")
    raise SystemExit(0)

state = json.loads(state_path.read_text())
removed = 0
for entry in state.get("installed", []):
    path = Path(entry["path"])
    if path.exists():
        shutil.rmtree(path)
        removed += 1

agents_cfg = yaml.safe_load((root / "integrations/agents.yml").read_text()).get("agents", {})

for agent in state.get("agents", []):
    context_rel = (agents_cfg.get(agent) or {}).get("context_file")
    if not context_rel:
        continue
    context_path = target / context_rel
    if agent == "cursor-agent" and context_path.exists():
        context_path.unlink()
        removed += 1

ext_yml = target / ".specify" / "extensions.yml"
if ext_yml.exists():
    data = yaml.safe_load(ext_yml.read_text()) or {}
    hooks = data.get("hooks", {})
    for hook, entries in list(hooks.items()):
        hooks[hook] = [e for e in entries if e.get("extension") != "nubo-skills"]
        if not hooks[hook]:
            del hooks[hook]
    if hooks:
        ext_yml.write_text(yaml.dump({"hooks": hooks}, sort_keys=False))
    else:
        ext_yml.unlink()

state_path.unlink()

for entry in state.get("installed", []):
    path = Path(entry["path"])
    parent = path.parent
    while parent != target and parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()
        parent = parent.parent

print(f"Removed {removed} installed artifact(s)")
PY
