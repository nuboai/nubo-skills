#!/usr/bin/env bash
# Pull pinned upstream versions and regenerate nubo-skills.lock
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 <<'PY'
from __future__ import annotations
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(".")
REGISTRY = yaml.safe_load((ROOT / "registry.yml").read_text())
LOCK: dict = {}

SUBMODULE_MAP = {
    "github/spec-kit": "upstream/speckit",
    "addyosmani/agent-skills": "upstream/addyosmani",
    "anthropics/skills": "upstream/anthropics",
    "trailofbits/skills": "upstream/trailofbits",
    "anthropics/claude-code": "upstream/anthropics-claude-code",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return "sha256-" + h.hexdigest()


def resolve_upstream_path(entry: dict) -> Path | None:
    t = entry.get("type")
    if t == "local":
        return ROOT / entry["path"]
    if t == "speckit":
        return ROOT / "upstream/speckit" / entry["path"]
    if t == "external":
        repo = entry["repo"]
        sub = SUBMODULE_MAP.get(repo)
        if not sub:
            return None
        return ROOT / sub / entry["path"]
    if t == "speckit-extension":
        return None
    return None


def git_rev(path: Path) -> str:
    if not path.exists():
        return "missing"
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    except subprocess.CalledProcessError:
        return "unknown"


for cmd_name, cmd in REGISTRY.get("commands", {}).items():
    composes_lock = []
    for c in cmd.get("composes", []):
        upstream_name = c.get("upstream_name", "")
        p = resolve_upstream_path(c)
        integrity = "sha256-missing"
        resolved_ref = c.get("ref", "")
        if p and p.exists():
            integrity = sha256_file(p)
            resolved_ref = git_rev(p.parent if p.is_file() else p)
        composes_lock.append({
            "upstream_name": upstream_name,
            "resolved_ref": resolved_ref,
            "integrity": integrity,
        })
    LOCK[cmd_name] = {
        "composes": composes_lock,
        "synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

(ROOT / "nubo-skills.lock").write_text("# Auto-generated. Do not edit manually.\n" + yaml.dump(LOCK, sort_keys=False))
print("Generated nubo-skills.lock")
PY
