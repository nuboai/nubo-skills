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
VALID_STEP_TYPES = {
    "command", "shell", "prompt", "gate", "if",
    "switch", "while", "do-while", "fan-out", "fan-in",
}
VALID_STRATEGIES = {"wrap", "merge", "sequence", "standalone", "utility"}
REF_LINK_RE = re.compile(r"\]\((references/[^)]+)\)")
SUBMODULE_MAP = {
    "github/spec-kit": "upstream/speckit",
    "addyosmani/agent-skills": "upstream/addyosmani",
    "anthropics/skills": "upstream/anthropics",
    "trailofbits/skills": "upstream/trailofbits",
}


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
    layer = entry.get("layer")
    if layer == "utility" and strategy != "utility":
        err(f"{name}: utility layer requires strategy utility")
    elif layer == "core" and strategy != "wrap":
        err(f"{name}: core layer requires strategy wrap")
    elif layer == "extended" and strategy not in {"merge", "sequence", "standalone"}:
        err(f"{name}: extended layer requires merge, sequence, or standalone strategy")
    elif strategy not in VALID_STRATEGIES:
        err(f"{name}: invalid strategy {strategy!r}")
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

    for ref in REF_LINK_RE.findall(content):
        ref_path = path.parent / ref
        if not ref_path.exists():
            err(f"{name}: unresolved reference link {ref}")


def resolve_compose_path(entry: dict) -> Path | None:
    t = entry.get("type")
    if t == "local":
        return ROOT / entry["path"]
    if t == "speckit":
        return ROOT / "upstream/speckit" / entry["path"]
    if t == "external":
        sub = SUBMODULE_MAP.get(entry.get("repo", ""))
        if sub:
            return ROOT / sub / entry["path"]
    return None


def check_upstream_paths(registry: dict) -> None:
    for name, entry in registry.get("commands", {}).items():
        for compose in entry.get("composes", []):
            if compose.get("type") == "speckit-extension":
                continue
            path = resolve_compose_path(compose)
            if path is None:
                continue
            if not path.exists():
                err(f"{name}: upstream path missing: {path.relative_to(ROOT)}")
    for preset_name, preset in registry.get("presets", {}).items():
        for compose in preset.get("composes", []):
            path = resolve_compose_path(compose)
            if path and not path.exists():
                err(f"preset {preset_name}: upstream path missing: {path.relative_to(ROOT)}")


def check_hooks(registry: dict) -> None:
    reg_cmds = registry.get("commands", {})
    for hook_name, entries in registry.get("hooks", {}).items():
        if not isinstance(entries, list):
            err(f"hook {hook_name}: must be a list")
            continue
        for entry in entries:
            cmd = entry.get("command", "")
            if not cmd.startswith("nb."):
                err(f"hook {hook_name}: invalid command ref {cmd!r}")
                continue
            cmd_name = cmd.split(".", 1)[1]
            if cmd_name not in reg_cmds:
                err(f"hook {hook_name}: unknown command {cmd_name}")


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


def _workflow_meta(wf: dict) -> tuple[dict, list]:
    workflow = wf.get("workflow", wf)
    steps = wf.get("steps", workflow.get("steps", []))
    return workflow, steps


def check_workflow_schema(wf_file: Path, wf: dict, reg_cmds: set[str]) -> int:
    gate_count = 0
    workflow, steps = _workflow_meta(wf)
    schema_version = wf.get("schema_version")
    if schema_version not in ("1.0", "1", 1, 1.0):
        err(f"{wf_file.name}: missing or invalid schema_version")
    if not workflow.get("id"):
        err(f"{wf_file.name}: missing workflow.id")
    if not workflow.get("name"):
        err(f"{wf_file.name}: missing workflow.name")
    version = workflow.get("version", "")
    if not re.match(r"^\d+\.\d+\.\d+$", str(version)):
        err(f"{wf_file.name}: workflow.version must be semver (got {version!r})")
    profile = workflow.get("hooks_profile")
    if profile and profile not in VALID_HOOK_PROFILES:
        err(f"{wf_file.name}: invalid hooks_profile {profile}")
    if not isinstance(steps, list) or not steps:
        err(f"{wf_file.name}: steps must be a non-empty list")
        return gate_count

    for step in steps:
        if not isinstance(step, dict):
            err(f"{wf_file.name}: step must be a mapping")
            continue
        step_id = step.get("id")
        if not step_id:
            err(f"{wf_file.name}: step missing id")
            continue
        step_type = step.get("type", "command")
        if step_type not in VALID_STEP_TYPES:
            err(f"{wf_file.name}: step {step_id} has invalid type {step_type!r}")
            continue
        if step_type == "gate":
            gate_count += 1
            if not step.get("message"):
                err(f"{wf_file.name}: gate {step_id} missing message")
            options = step.get("options", ["approve", "reject"])
            if not isinstance(options, list) or not options:
                err(f"{wf_file.name}: gate {step_id} options must be non-empty list")
            on_reject = step.get("on_reject", "abort")
            if on_reject not in ("abort", "skip", "retry"):
                err(f"{wf_file.name}: gate {step_id} invalid on_reject {on_reject!r}")
        elif step_type == "command":
            if not step.get("command"):
                err(f"{wf_file.name}: command step {step_id} missing command")
            cmd = step.get("command", "")
            if cmd.startswith("nb."):
                cmd_name = cmd.split(".", 1)[1]
                if cmd_name not in reg_cmds:
                    err(f"{wf_file.name}: unknown command {cmd_name}")
        if "continue_on_error" in step and not isinstance(step["continue_on_error"], bool):
            err(f"{wf_file.name}: step {step_id} continue_on_error must be boolean")
    return gate_count


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
    wf_reg_gates = {
        wf_id: meta.get("gates")
        for wf_id, meta in wf_reg.get("workflows", {}).items()
    }
    for wf_file in (ROOT / "workflows").glob("nb-*.yml"):
        with open(wf_file) as f:
            wf = yaml.safe_load(f)
        workflow, _ = _workflow_meta(wf)
        wf_id = workflow.get("id") or wf.get("id")
        gate_count = check_workflow_schema(wf_file, wf, reg_cmds)
        expected_gates = wf_reg_gates.get(wf_id)
        if expected_gates is not None and gate_count != expected_gates:
            err(
                f"{wf_file.name}: gate count {gate_count} != "
                f"workflows/registry.yml gates {expected_gates}"
            )


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
    check_upstream_paths(registry)
    check_hooks(registry)
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
