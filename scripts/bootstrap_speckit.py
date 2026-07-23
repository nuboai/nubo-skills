#!/usr/bin/env python3
"""Install or remove SpecKit extensions, workflows, and presets for nubo-skills."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

NUBO_EXTENSION_ID = "nubo-skills"


def load_registry(root: Path) -> dict:
    return yaml.safe_load((root / "registry.yml").read_text())


def speckit_extensions(registry: dict) -> list[dict]:
    seen: set[str] = set()
    entries: list[dict] = []
    for cmd in registry.get("commands", {}).values():
        for compose in cmd.get("composes", []):
            if compose.get("type") != "speckit-extension":
                continue
            ext_id = compose.get("extension_id", "")
            if not ext_id or ext_id in seen:
                continue
            seen.add(ext_id)
            entries.append(compose)
    return entries


def merge_nubo_hooks(target: Path, registry: dict) -> None:
    hooks_out: dict[str, list] = {}
    for hook, hook_entries in registry.get("hooks", {}).items():
        hooks_out[hook] = [
            {
                "command": entry["command"],
                "extension": NUBO_EXTENSION_ID,
                "enabled": True,
                "optional": entry.get("optional", True),
                "priority": entry.get("priority", 10),
                "condition": None,
            }
            for entry in hook_entries
        ]

    ext_yml = target / ".specify" / "extensions.yml"
    existing = yaml.safe_load(ext_yml.read_text()) if ext_yml.exists() else {}
    if not isinstance(existing, dict):
        existing = {}
    merged = existing.get("hooks", {})
    if not isinstance(merged, dict):
        merged = {}
    for key, value in hooks_out.items():
        merged.setdefault(key, [])
        merged[key] = [
            h for h in merged[key] if h.get("extension") != NUBO_EXTENSION_ID
        ] + value
    existing["hooks"] = merged
    ext_yml.parent.mkdir(parents=True, exist_ok=True)
    ext_yml.write_text(yaml.dump(existing, sort_keys=False))


def copy_workflows_and_presets(root: Path, target: Path) -> None:
    wf_dst = target / ".specify" / "workflows" / "nubo"
    preset_dst = target / ".specify" / "presets"
    wf_dst.mkdir(parents=True, exist_ok=True)
    preset_dst.mkdir(parents=True, exist_ok=True)

    for wf in (root / "workflows").glob("nb-*.yml"):
        shutil.copy2(wf, wf_dst / wf.name)
    registry_yml = root / "workflows" / "registry.yml"
    if registry_yml.exists():
        shutil.copy2(registry_yml, wf_dst / registry_yml.name)
    (wf_dst / "active-profile.yml").write_text("profile: default\n")

    for preset in (root / "presets").glob("*/preset.yml"):
        preset_id = preset.parent.name
        dest = preset_dst / preset_id
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(preset, dest / "preset.yml")


def copy_nubo_extension_fallback(root: Path, target: Path) -> None:
    ext_src = root / "extensions" / NUBO_EXTENSION_ID
    ext_dst = target / ".specify" / "extensions" / NUBO_EXTENSION_ID
    if not (ext_src / "extension.yml").exists():
        raise FileNotFoundError(f"{ext_src / 'extension.yml'} missing — run scripts/generate_skills.py")
    ext_dst.parent.mkdir(parents=True, exist_ok=True)
    if ext_dst.exists():
        shutil.rmtree(ext_dst)
    shutil.copytree(ext_src, ext_dst)


def run_specify(target: Path, args: list[str]) -> bool:
    try:
        proc = subprocess.run(
            ["specify", *args],
            cwd=str(target),
            input="y\n",
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        print(f"WARN: specify {' '.join(args)} failed: {detail}", file=sys.stderr)
        return False
    return True


def install(root: Path, target: Path) -> list[str]:
    registry = load_registry(root)
    installed: list[str] = []
    specify_dir = target / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    nubo_src = root / "extensions" / NUBO_EXTENSION_ID
    if not (nubo_src / "extension.yml").exists():
        raise FileNotFoundError("extensions/nubo-skills/extension.yml missing — run scripts/setup.sh")

    if shutil.which("specify"):
        if run_specify(target, ["extension", "add", NUBO_EXTENSION_ID, "--dev", str(nubo_src), "--force"]):
            installed.append(NUBO_EXTENSION_ID)
        else:
            copy_nubo_extension_fallback(root, target)
            installed.append(f"{NUBO_EXTENSION_ID} (copied)")
    else:
        print("WARN: specify CLI not found — copying nubo-skills extension without registry", file=sys.stderr)
        copy_nubo_extension_fallback(root, target)
        installed.append(f"{NUBO_EXTENSION_ID} (copied)")

    for compose in speckit_extensions(registry):
        ext_id = compose["extension_id"]
        url = compose.get("download_url", "")
        if not url:
            print(f"WARN: {ext_id} missing download_url — skipped", file=sys.stderr)
            continue
        if not shutil.which("specify"):
            print(f"WARN: skipping {ext_id} — specify CLI not available", file=sys.stderr)
            continue
        if run_specify(target, ["extension", "add", ext_id, "--from", url, "--force"]):
            installed.append(ext_id)
        else:
            print(f"WARN: failed to install {ext_id} from {url}", file=sys.stderr)

    copy_workflows_and_presets(root, target)
    merge_nubo_hooks(target, registry)
    return installed


def uninstall(root: Path, target: Path) -> None:
    state_path = target / ".nubo-skills.state.json"
    ext_ids = {NUBO_EXTENSION_ID}
    if state_path.exists():
        state = json.loads(state_path.read_text())
        ext_ids.update(state.get("speckit_extensions", []))
    else:
        registry = load_registry(root)
        ext_ids.update(c["extension_id"] for c in speckit_extensions(registry))

    if shutil.which("specify"):
        for ext_id in sorted(ext_ids):
            if ext_id.endswith(" (copied)"):
                continue
            run_specify(target, ["extension", "remove", ext_id, "--force"])

    ext_root = target / ".specify" / "extensions"
    for ext_id in ext_ids:
        ext_id = ext_id.split(" ", 1)[0]
        path = ext_root / ext_id
        if path.exists():
            shutil.rmtree(path)

    wf_dst = target / ".specify" / "workflows" / "nubo"
    if wf_dst.exists():
        shutil.rmtree(wf_dst)

    preset_dst = target / ".specify" / "presets"
    if preset_dst.exists():
        for preset in preset_dst.glob("nb-*"):
            if preset.is_dir():
                shutil.rmtree(preset)

    ext_yml = target / ".specify" / "extensions.yml"
    if ext_yml.exists():
        data = yaml.safe_load(ext_yml.read_text()) or {}
        hooks = data.get("hooks", {})
        if isinstance(hooks, dict):
            for hook, entries in list(hooks.items()):
                hooks[hook] = [e for e in entries if e.get("extension") != NUBO_EXTENSION_ID]
                if not hooks[hook]:
                    del hooks[hook]
            data["hooks"] = hooks
            if hooks:
                ext_yml.write_text(yaml.dump(data, sort_keys=False))
            else:
                ext_yml.unlink()


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in {"install", "uninstall"}:
        print("Usage: bootstrap_speckit.py <install|uninstall> <nubo-skills-root> <target>", file=sys.stderr)
        return 1

    action, root_arg, target_arg = sys.argv[1:4]
    root = Path(root_arg).resolve()
    target = Path(target_arg).resolve()

    if action == "install":
        installed = install(root, target)
        print(f"SpecKit bootstrap: {len(installed)} extension(s)")
        for ext in installed:
            print(f"  - {ext}")
        return 0

    uninstall(root, target)
    print("SpecKit bootstrap: removed extensions, workflows, and presets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
