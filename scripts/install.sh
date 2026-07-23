#!/usr/bin/env bash
# Fallback installer for non-SpecKit projects
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

AGENTS=""
PHASES="all"
AUTO=false
TARGET_DIR="."
SPECKIT=false

usage() {
  cat <<EOF
Usage: $0 [--agent cursor-agent,claude,...] [--phases specify,plan,...] [--auto] [--target DIR] [--speckit]

Copies nb-{command}/SKILL.md directories to agent discovery paths.
With --speckit (or when .specify/ exists in target), also bootstraps SpecKit
extensions, workflows, and presets via the specify CLI.
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENTS="$2"; shift 2 ;;
    --phases) PHASES="$2"; shift 2 ;;
    --auto) AUTO=true; shift ;;
    --target) TARGET_DIR="$2"; shift 2 ;;
    --speckit) SPECKIT=true; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

python3 - "$ROOT" "$AGENTS" "$PHASES" "$AUTO" "$TARGET_DIR" "$SPECKIT" <<'PY'
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

root, agents, phases, auto, target, speckit_flag = sys.argv[1:7]
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
speckit_enabled = str(speckit_flag).strip().lower() in ("true", "1", "yes") or (target / ".specify").is_dir()

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

speckit_extensions: list[str] = []
bootstrap = root / "scripts" / "bootstrap_speckit.py"
if speckit_enabled and bootstrap.exists():
    proc = subprocess.run(
        [sys.executable, str(bootstrap), "install", str(root), str(target)],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    if proc.returncode == 0:
        for line in proc.stdout.splitlines():
            if line.strip().startswith("- "):
                ext = line.strip()[2:].split(" ", 1)[0]
                speckit_extensions.append(ext)

state = {
    "installed": installed,
    "agents": selected,
    "phases": phases,
    "speckit_extensions": speckit_extensions,
}
(target / ".nubo-skills.state.json").write_text(json.dumps(state, indent=2) + "\n")
print(f"Installed {len(installed)} skill(s) across {len(selected)} agent(s)")
PY
