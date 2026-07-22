#!/usr/bin/env bash
# Fallback installer for non-SpecKit projects
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

AGENTS=""
PHASES="all"
AUTO=false
TARGET_DIR="."

usage() {
  cat <<EOF
Usage: $0 [--agent cursor-agent,claude,...] [--phases specify,plan,...] [--auto] [--target DIR]

Copies nb-{command}/SKILL.md directories to agent discovery paths.
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENTS="$2"; shift 2 ;;
    --phases) PHASES="$2"; shift 2 ;;
    --auto) AUTO=true; shift ;;
    --target) TARGET_DIR="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

python3 - "$ROOT" "$AGENTS" "$PHASES" "$AUTO" "$TARGET_DIR" <<'PY'
import json
import shutil
import sys
from pathlib import Path
import yaml

root, agents, phases, auto, target = sys.argv[1:6]
root = Path(root)
target = Path(target)
registry = yaml.safe_load((root / "registry.yml").read_text())
agents_cfg = yaml.safe_load((root / "integrations/agents.yml").read_text())["agents"]

if auto:
    selected = list(agents_cfg.keys())
elif agents:
    selected = [a.strip() for a in agents.split(",") if a.strip()]
else:
    selected = ["cursor-agent"]

phase_filter = None if phases == "all" else set(p.strip() for p in phases.split(","))

installed = []
for name, entry in registry["commands"].items():
    if phase_filter and entry.get("phase") not in phase_filter:
        continue
    layer = entry["layer"]
    if layer == "utility":
        layer = "utilities"
    src = root / "commands" / layer / name
    if not (src / "SKILL.md").exists():
        continue
    for agent in selected:
        cfg = agents_cfg.get(agent)
        if not cfg:
            continue
        dest = target / cfg["skills_dir"] / name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        installed.append({"agent": agent, "command": name, "path": str(dest)})

# Generate extensions.yml hooks
hooks_out = {"hooks": {}}
for hook, entries in registry.get("hooks", {}).items():
    hooks_out["hooks"][hook] = []
    for e in entries:
        hooks_out["hooks"][hook].append({
            "command": e["command"],
            "extension": "nubo-skills",
            "enabled": True,
            "optional": e.get("optional", True),
            "priority": e.get("priority", 10),
            "condition": None,
        })

specify_dir = target / ".specify"
specify_dir.mkdir(parents=True, exist_ok=True)
ext_yml = specify_dir / "extensions.yml"
existing = {}
if ext_yml.exists():
    existing = yaml.safe_load(ext_yml.read_text()) or {}
merged = existing.get("hooks", {})
for k, v in hooks_out["hooks"].items():
    merged.setdefault(k, [])
    merged[k] = [h for h in merged[k] if h.get("extension") != "nubo-skills"] + v
ext_yml.write_text(yaml.dump({"hooks": merged}, sort_keys=False))

state = {
    "installed": installed,
    "agents": selected,
    "phases": phases,
}
(target / ".nubo-skills.state.json").write_text(json.dumps(state, indent=2))
print(f"Installed {len(installed)} skill(s) across {len(selected)} agent(s)")
PY

# Install governance context files
for agent in $(echo "$AGENTS" | tr ',' ' '); do
  [[ -z "$agent" ]] && continue
  case "$agent" in
    cursor-agent)
      mkdir -p "$TARGET_DIR/.cursor/rules"
      cp "$ROOT/integrations/context-files/cursor.md" "$TARGET_DIR/.cursor/rules/nubo-governance.md"
      ;;
    claude)
      touch "$TARGET_DIR/CLAUDE.md"
      if ! grep -q "nubo-skills governance" "$TARGET_DIR/CLAUDE.md" 2>/dev/null; then
        cat "$ROOT/integrations/context-files/claude.md" >> "$TARGET_DIR/CLAUDE.md"
      fi
      ;;
    codex)
      touch "$TARGET_DIR/AGENTS.md"
      if ! grep -q "nubo-skills governance" "$TARGET_DIR/AGENTS.md" 2>/dev/null; then
        cat "$ROOT/integrations/context-files/codex.md" >> "$TARGET_DIR/AGENTS.md"
      fi
      ;;
  esac
done
