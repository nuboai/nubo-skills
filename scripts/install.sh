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

auto_enabled = str(auto).strip().lower() in ("true", "1", "yes")
if auto_enabled:
    selected = list(agents_cfg.keys())
elif agents.strip():
    selected = [a.strip() for a in agents.split(",") if a.strip()]
else:
    selected = ["cursor-agent"]

phase_filter = None if phases == "all" else set(p.strip() for p in phases.split(","))

CONTEXT_MARKERS = {
    "claude": "nubo-skills governance",
    "codex": "nubo-skills governance",
    "gemini": "nubo-skills governance",
    "copilot": "nubo-skills governance",
}


def install_context(agent: str) -> None:
    cfg = agents_cfg.get(agent, {})
    context_rel = cfg.get("context_file")
    if not context_rel:
        return

    context_src = root / "integrations" / "context-files"
    context_dest = target / context_rel

    if agent == "cursor-agent":
        context_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(context_src / "cursor.md", context_dest)
        return

    mapping = {
        "claude": "claude.md",
        "codex": "codex.md",
        "gemini": "gemini.md",
        "copilot": "copilot.md",
    }
    src_name = mapping.get(agent)
    if not src_name:
        return

    marker = CONTEXT_MARKERS.get(agent, "nubo-skills governance")
    context_dest.parent.mkdir(parents=True, exist_ok=True)
    if context_dest.exists():
        existing = context_dest.read_text()
        if marker in existing:
            return
        with context_dest.open("a") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write((context_src / src_name).read_text())
    else:
        shutil.copy2(context_src / src_name, context_dest)


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

for agent in selected:
    install_context(agent)

hooks_out = {"hooks": {}}
for hook, entries in registry.get("hooks", {}).items():
    hooks_out["hooks"][hook] = []
    for entry in entries:
        hooks_out["hooks"][hook].append({
            "command": entry["command"],
            "extension": "nubo-skills",
            "enabled": True,
            "optional": entry.get("optional", True),
            "priority": entry.get("priority", 10),
            "condition": None,
        })

specify_dir = target / ".specify"
specify_dir.mkdir(parents=True, exist_ok=True)
ext_yml = specify_dir / "extensions.yml"
existing = {}
if ext_yml.exists():
    existing = yaml.safe_load(ext_yml.read_text()) or {}
merged = existing.get("hooks", {})
for key, value in hooks_out["hooks"].items():
    merged.setdefault(key, [])
    merged[key] = [h for h in merged[key] if h.get("extension") != "nubo-skills"] + value
ext_yml.write_text(yaml.dump({"hooks": merged}, sort_keys=False))

state = {
    "installed": installed,
    "agents": selected,
    "phases": phases,
}
(target / ".nubo-skills.state.json").write_text(json.dumps(state, indent=2) + "\n")
print(f"Installed {len(installed)} skill(s) across {len(selected)} agent(s)")
PY
