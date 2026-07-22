#!/usr/bin/env python3
"""Structural validation for nubo-skills governance rules."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []
WARNINGS: list[str] = []

REQUIRED_SECTIONS_PIPELINE = [
    "## Purpose",
    "## Conventions",
    "## Context",
    "## Procedure",
    "## Artifacts",
    "## Completion Response",
]
REQUIRED_SECTIONS_UTILITY = [
    "## Purpose",
    "## Conventions",
    "## Procedure",
    "## Completion Response",
]
FINDINGS_COMMANDS = {
    "nb-review-code", "nb-review-security", "nb-review-arch", "nb-analyze", "nb-checklist"
}
USER_PROMPT_COMMANDS = {
    "nb-interview", "nb-specify", "nb-plan", "nb-implement",
    "nb-review-code", "nb-review-security", "nb-review-arch", "nb-deploy",
}
EXECUTION_MODEL_COMMANDS = {"nb-review-code", "nb-review-arch", "nb-deploy"}
VALID_HOOK_PROFILES = {"full", "default", "arch-only", "review-only", "none"}


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content
    meta = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return meta, body


def load_registry() -> dict:
    with open(ROOT / "registry.yml") as f:
        return yaml.safe_load(f)


def find_commands() -> dict[str, Path]:
    found = {}
    for layer in ("core", "extended", "utilities"):
        layer_dir = ROOT / "commands" / layer
        if not layer_dir.exists():
            continue
        for cmd_dir in layer_dir.iterdir():
            if not cmd_dir.is_dir():
                continue
            skill = cmd_dir / "SKILL.md"
            if skill.exists():
                found[cmd_dir.name] = skill
    return found


def check_naming(registry: dict, on_disk: dict[str, Path]) -> None:
    reg_cmds = registry.get("commands", {})
    for name, entry in reg_cmds.items():
        layer = entry.get("layer")
        if layer == "utility":
            layer = "utilities"
        expected = ROOT / "commands" / layer / name / "SKILL.md"
        if name not in on_disk:
            err(f"registry command {name} missing on disk at {expected}")
            continue
        if on_disk[name] != expected:
            err(f"{name}: SKILL.md at wrong path {on_disk[name].relative_to(ROOT)}")
        if not re.match(r"^nb-[a-z0-9-]+$", name) or len(name) > 64:
            err(f"{name}: invalid command name")
        tmpl = entry.get("command_template", "")
        if tmpl != f"commands/{layer}/{name}/SKILL.md":
            err(f"{name}: command_template mismatch: {tmpl}")

    for name in on_disk:
        if name not in reg_cmds:
            err(f"on-disk command {name} not in registry.yml")


def check_skill(name: str, path: Path, entry: dict) -> None:
    content = path.read_text()
    fm, body = parse_frontmatter(content)
    if fm is None:
        err(f"{name}: missing YAML frontmatter")
        return
    if fm.get("name") != name:
        err(f"{name}: frontmatter name '{fm.get('name')}' != directory '{name}'")
    meta = fm.get("metadata") or {}
    strategy = meta.get("strategy")
    if strategy != entry.get("layer") and entry.get("layer") == "utility" and strategy != "utility":
        err(f"{name}: utility layer requires strategy utility")
    if meta.get("phase") != entry.get("phase"):
        err(f"{name}: metadata.phase mismatch with registry")
    if meta.get("tier") != entry.get("tier"):
        err(f"{name}: metadata.tier mismatch with registry")
    reg_composes = [c.get("upstream_name") for c in entry.get("composes", [])]
    skill_composes = meta.get("composes") or []
    if skill_composes != reg_composes:
        err(f"{name}: metadata.composes {skill_composes} != registry {reg_composes}")

    is_utility = strategy == "utility"
    sections = REQUIRED_SECTIONS_UTILITY if is_utility else REQUIRED_SECTIONS_PIPELINE
    for sec in sections:
        if sec not in content:
            err(f"{name}: missing section {sec}")

    if name in USER_PROMPT_COMMANDS:
        if "## User Prompts" not in content:
            err(f"{name}: missing ## User Prompts section")
    if strategy == "sequence":
        if "## Prerequisites" not in content:
            err(f"{name}: sequence strategy requires ## Prerequisites")
    elif "## Prerequisites" in content and name != "nb-review-arch":
        warn(f"{name}: ## Prerequisites present but strategy is {strategy}")

    if name in EXECUTION_MODEL_COMMANDS:
        if "## Execution Model" not in content:
            err(f"{name}: missing ## Execution Model")

    if strategy in ("merge", "wrap", "standalone") and "{CORE_TEMPLATE}" not in content:
        if strategy != "sequence":
            err(f"{name}: {strategy} strategy requires {{CORE_TEMPLATE}} in Procedure")
    if strategy == "sequence" and "{CORE_TEMPLATE}" in content:
        err(f"{name}: sequence strategy must not use {{CORE_TEMPLATE}}")

    if not is_utility and "| Path |" not in content:
        err(f"{name}: missing Artifacts table with Path column")

    if "## Completion Response" in content:
        if '"command"' not in content or '"metrics"' not in content or '"next_command"' not in content:
            err(f"{name}: completion response missing v2 fields")
        if name in FINDINGS_COMMANDS and '"findings"' not in content:
            err(f"{name}: missing findings in completion response")
        if "### " not in content.split("## Completion Response")[-1]:
            warn(f"{name}: missing visual summary block after completion JSON")

    body_lines = [l for l in body.splitlines() if l.strip()]
    if len(body_lines) > 500:
        err(f"{name}: SKILL.md body exceeds 500 lines ({len(body_lines)})")
    elif len(body_lines) > 400:
        warn(f"{name}: SKILL.md body approaching limit ({len(body_lines)} lines)")

    if meta.get("read_only") is True:
        tools = meta.get("allowed_tools") or []
        if "write_file" in tools:
            err(f"{name}: read_only=true but write_file in allowed_tools")


def check_governance(registry: dict) -> None:
    today = date.today()
    for name, entry in registry.get("commands", {}).items():
        for field in ("tier", "owner", "review_by"):
            if field not in entry:
                err(f"{name}: missing governance field {field}")
        rb = entry.get("review_by")
        if rb:
            try:
                review_date = datetime.strptime(rb, "%Y-%m-%d").date()
                days = (review_date - today).days
                if days <= 30:
                    warn(f"{name}: review_by {rb} within 30 days")
            except ValueError:
                err(f"{name}: invalid review_by date {rb}")


def check_bundle_and_workflows(registry: dict) -> None:
    bundle_path = ROOT / "bundle.yml"
    if not bundle_path.exists():
        err("bundle.yml missing")
        return
    with open(bundle_path) as f:
        bundle = yaml.safe_load(f)
    wf_reg_path = ROOT / "workflows" / "registry.yml"
    if not wf_reg_path.exists():
        err("workflows/registry.yml missing")
        return
    with open(wf_reg_path) as f:
        wf_reg = yaml.safe_load(f)
    for wf_id in wf_reg.get("workflows", {}):
        wf_file = ROOT / "workflows" / f"{wf_id}.yml"
        if not wf_file.exists():
            err(f"workflow file missing: {wf_file.name}")
    bundle_wfs = [w["id"] for w in bundle.get("components", {}).get("workflows", [])]
    for wf_id in wf_reg.get("workflows", {}):
        if wf_id not in bundle_wfs:
            err(f"workflow {wf_id} not in bundle.yml")

    reg_cmds = set(registry.get("commands", {}))
    for wf_file in (ROOT / "workflows").glob("nb-*.yml"):
        with open(wf_file) as f:
            wf = yaml.safe_load(f)
        profile = wf.get("hooks_profile")
        if profile and profile not in VALID_HOOK_PROFILES:
            err(f"{wf_file.name}: invalid hooks_profile {profile}")
        for step in wf.get("steps", []):
            if step.get("type") == "gate" and not step.get("approvers"):
                err(f"{wf_file.name}: gate step {step.get('id')} missing approvers")
            cmd = step.get("command", "")
            if cmd.startswith("nb."):
                cmd_name = cmd.split(".", 1)[1]
                if cmd_name not in reg_cmds:
                    err(f"{wf_file.name}: unknown command {cmd_name}")


def check_lock(registry: dict) -> None:
    lock_path = ROOT / "nubo-skills.lock"
    if not lock_path.exists():
        warn("nubo-skills.lock missing — run scripts/sync-upstream.sh")
        return
    with open(lock_path) as f:
        lock = yaml.safe_load(f) or {}
    for name in registry.get("commands", {}):
        if name not in lock:
            warn(f"{name}: missing from nubo-skills.lock")


def main() -> int:
    registry = load_registry()
    on_disk = find_commands()
    check_naming(registry, on_disk)
    for name, path in on_disk.items():
        entry = registry.get("commands", {}).get(name, {})
        check_skill(name, path, entry)
    check_governance(registry)
    check_bundle_and_workflows(registry)
    check_lock(registry)

    for w in WARNINGS:
        print(f"WARN: {w}")
    for e in ERRORS:
        print(f"ERROR: {e}")

    if ERRORS:
        print(f"\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
        return 1
    print(f"OK: all checks passed ({len(WARNINGS)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
