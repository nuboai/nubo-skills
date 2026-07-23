#!/usr/bin/env bash
# Pull pinned upstream versions and regenerate nubo-skills.lock
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CHECKOUT=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --checkout) CHECKOUT=true; shift ;;
    -h|--help)
      echo "Usage: $0 [--checkout]"
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

"$ROOT/scripts/ensure-deps.sh"

python3 - "$CHECKOUT" <<'PY'
from __future__ import annotations
import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

checkout = sys.argv[1].lower() == "true"
ROOT = Path(".")
REGISTRY = yaml.safe_load((ROOT / "registry.yml").read_text())
LOCK: dict = {"commands": {}, "presets": {}}

SUBMODULE_MAP = {
    "github/spec-kit": "upstream/speckit",
    "addyosmani/agent-skills": "upstream/addyosmani",
    "anthropics/skills": "upstream/anthropics",
    "trailofbits/skills": "upstream/trailofbits",
}
UNVERIFIABLE_INTEGRITY = "sha256-unverifiable"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def collect_compose_entries() -> list[dict]:
    entries: list[dict] = []
    for cmd in REGISTRY.get("commands", {}).values():
        entries.extend(cmd.get("composes", []))
    for preset in REGISTRY.get("presets", {}).values():
        entries.extend(preset.get("composes", []))
    return entries


def pinned_submodule_refs() -> dict[str, str]:
    refs: dict[str, str] = {}
    for entry in collect_compose_entries():
        t = entry.get("type")
        ref = entry.get("ref")
        if not ref:
            continue
        if t == "speckit":
            refs["upstream/speckit"] = ref
        elif t == "external":
            sub = SUBMODULE_MAP.get(entry.get("repo", ""))
            if sub:
                refs[sub] = ref
    return refs


def checkout_submodules() -> None:
    for sub_path, ref in pinned_submodule_refs().items():
        path = ROOT / sub_path
        if not (path / ".git").exists():
            continue
        print(f"Checking out {sub_path} @ {ref}")
        run(["git", "fetch", "--tags", "origin"], cwd=path)
        run(["git", "checkout", ref], cwd=path)


if checkout:
    checkout_submodules()


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
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        return "unknown"


def lock_compose(entry: dict) -> dict:
    upstream_name = entry.get("upstream_name", "")
    declared_ref = entry.get("ref", "")
    if entry.get("type") == "speckit-extension":
        return {
            "upstream_name": upstream_name,
            "extension_id": entry.get("extension_id", ""),
            "resolved_ref": declared_ref,
            "integrity": UNVERIFIABLE_INTEGRITY,
        }
    path = resolve_upstream_path(entry)
    integrity = "sha256-missing"
    resolved_ref = declared_ref
    if path and path.exists():
        integrity = sha256_file(path)
        resolved_ref = git_rev(path.parent if path.is_file() else path)
    return {
        "upstream_name": upstream_name,
        "resolved_ref": resolved_ref,
        "integrity": integrity,
    }


for cmd_name, cmd in REGISTRY.get("commands", {}).items():
    composes_lock = [lock_compose(c) for c in cmd.get("composes", [])]
    LOCK["commands"][cmd_name] = {
        "composes": composes_lock,
        "synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

for preset_name, preset in REGISTRY.get("presets", {}).items():
    composes_lock = [lock_compose(c) for c in preset.get("composes", [])]
    LOCK["presets"][preset_name] = {
        "composes": composes_lock,
        "synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

(ROOT / "nubo-skills.lock").write_text(
    "# Auto-generated. Do not edit manually.\n" + yaml.dump(LOCK, sort_keys=False)
)
print("Generated nubo-skills.lock")
PY
