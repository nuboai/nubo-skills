#!/usr/bin/env python3
"""Generate all nb-* command SKILL.md files from catalog definitions."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

SUBMODULE_MAP = {
    "github/spec-kit": "upstream/speckit",
    "addyosmani/agent-skills": "upstream/addyosmani",
    "anthropics/skills": "upstream/anthropics",
    "trailofbits/skills": "upstream/trailofbits",
}

USER_PROMPT_COMMANDS = {
    "nb-interview": {
        "prompt_id": "scope-confirmation",
        "when": "After interview rounds complete",
        "question": "Is this scope complete?",
        "options": [
            ("complete", "Finalize scope and proceed to constitution/specify"),
            ("continue", "Run another interview round"),
            ("revise", "Revise scope summary before continuing"),
        ],
        "default": "complete",
        "blocks": "Scope finalization",
    },
    "nb-specify": {
        "prompt_id": "spec-review",
        "when": "Before writing final spec artifact",
        "question": "Approve this spec?",
        "options": [
            ("approve", "Finalize spec.md"),
            ("revise", "Revise spec based on feedback"),
            ("clarify", "Run nb-clarify before finalizing"),
        ],
        "default": "approve",
        "blocks": "Spec artifact write",
    },
    "nb-plan": {
        "prompt_id": "approach-selection",
        "when": "Multiple valid design approaches exist",
        "question": "Which approach should we use?",
        "options": [
            ("approach-a", "Use recommended approach A"),
            ("approach-b", "Use alternative approach B"),
            ("hybrid", "Combine elements from both approaches"),
        ],
        "default": "approach-a",
        "blocks": "Plan artifact write",
    },
    "nb-implement": {
        "prompt_id": "strategy-confirmation",
        "when": "Before writing code",
        "question": "Proceed with this implementation approach?",
        "options": [
            ("proceed", "Start implementation"),
            ("revise", "Revise approach before coding"),
            ("split", "Break into smaller implementation steps"),
        ],
        "default": "proceed",
        "blocks": "Code changes",
    },
    "nb-review-code": {
        "prompt_id": "fix-delegation",
        "when": "Findings with severity P0-P2 are detected",
        "question": "Create fix tasks for these P1-P2 issues?",
        "options": [
            ("create-tasks", "Generate nb-tasks entries for each finding"),
            ("report-only", "Keep findings in review report only"),
            ("dismiss", "Acknowledge and dismiss non-critical findings"),
        ],
        "default": "create-tasks",
        "blocks": "Post-review task generation",
    },
    "nb-review-security": {
        "prompt_id": "remediation-delegation",
        "when": "Security findings are detected",
        "question": "Create remediation tasks for these findings?",
        "options": [
            ("create-tasks", "Generate remediation tasks for nb-implement"),
            ("report-only", "Keep findings in security report only"),
            ("escalate", "Escalate critical findings for immediate action"),
        ],
        "default": "create-tasks",
        "blocks": "Remediation task generation",
    },
    "nb-review-arch": {
        "prompt_id": "action-selection",
        "when": "Architecture review completes with findings",
        "question": "Apply architecture updates or create refactor tasks?",
        "options": [
            ("apply-updates", "Update architecture contract and generate refactor tasks"),
            ("tasks-only", "Create refactor tasks without updating contract"),
            ("report-only", "Keep findings in review report only"),
        ],
        "default": "apply-updates",
        "blocks": "Architecture contract update",
    },
    "nb-deploy": {
        "prompt_id": "environment-confirmation",
        "when": "Before deployment execution",
        "question": "Deploy to {env}?",
        "options": [
            ("deploy", "Proceed with deployment"),
            ("dry-run", "Run deployment dry-run only"),
            ("cancel", "Cancel deployment"),
        ],
        "default": "deploy",
        "blocks": "Deployment execution",
    },
}

ARCH_REFERENCE_GUIDES = {
    "arch-guard-steps.md": """# Architecture Guard Steps

Operational guide for step 1 of `nb-review-arch`. Full extension contract:
`.specify/extensions/architecture-guard/commands/architecture-review.md`.

## Delegate command

`/speckit.architecture-guard.architecture-review`

## Mode

Read-only analysis. Do not modify source files. Output findings and non-blocking refactor tasks.

## Inputs

- Feature spec: `specs/{NNN}-{feature}/spec.md`
- Plan and tasks: `specs/{NNN}-{feature}/plan.md`, `tasks.md`
- Constitutions: `.specify/memory/constitution.md`, `.specify/memory/architecture_constitution.md`
- Changed implementation files (when reviewing in-flight work)

## Outputs to capture

- Constitution drift findings with file/line evidence
- Boundary and dependency violations
- Non-blocking refactor task suggestions

## Merge into `arch-review.md`

Add a **Drift detection** section. Normalize each finding to:
`severity`, `category`, `message`, `location`, `evidence`, `recommendation`.
""",
    "arch-preview-steps.md": """# Architect Preview Steps

Operational guide for step 2 of `nb-review-arch`. Full preset contract:
`.specify/presets/architect-preview/templates/commands/preview.md`.

## Delegate command

`/speckit.architect-preview`

Pass the feature scope or change summary as arguments (e.g. plan summary, affected modules).

## Mode

Read-only impact analysis. Do not modify architecture memory or source files.

## Inputs

- Current feature artifacts under `specs/{NNN}-{feature}/`
- Existing architecture memory under `.specify/memory/architecture*.md`
- Optional: diff summary or list of affected components

## Outputs to capture

- Architectural impact areas (modules, boundaries, data flows)
- Complexity and risk assessment
- Coupling, migration, or operational risks

## Merge into `arch-review.md`

Add an **Impact preview** section. Summarize blast radius, risk level, and
pre-implementation concerns before contract validation runs.
""",
    "arch-contract-steps.md": """# Architecture Contract Steps

Operational guide for step 3 of `nb-review-arch`. Full extension contract:
`.specify/extensions/arch/commands/speckit.arch.full-generate.md`.

## Delegate command

`/speckit.arch.full-generate`

Use the full forward-generation workflow to validate or refresh the planning contract.

## Mode

Writes architecture memory only. Allowed targets:
`.specify/memory/architecture*.md` (views and synthesis). Do not modify feature
specs, plans, tasks, or source code.

## Inputs

- Validated findings from steps 1–2
- Feature context from `specs/{NNN}-{feature}/`
- Existing architecture memory under `.specify/memory/`

## Outputs to capture

- Updated `.specify/memory/architecture.md` synthesis (when validator passes)
- View-level gaps recorded explicitly when evidence is insufficient
- Validator `ready_gate` result and blocker codes

## Merge into `arch-review.md`

Add a **Contract validation** section. Record whether the contract was refreshed,
which views changed, synthesis readiness, and any gaps blocking refresh.

Respect the user prompt from `nb-review-arch`: only write contract updates when
`apply-updates` is selected; otherwise report findings only.
""",
}

GOVERNED_REFERENCE_ALIASES: dict[str, dict[str, tuple[str, str]]] = {
    "nb-deploy": {
        "deploy-shipping.md": ("Shipping And Launch", "shipping-and-launch.md"),
        "deploy-cicd.md": ("CI/CD And Automation", "ci-cd-and-automation.md"),
        "deploy-git.md": ("Git Workflow And Versioning", "git-workflow-and-versioning.md"),
        "deploy-observability.md": (
            "Observability And Instrumentation",
            "observability-and-instrumentation.md",
        ),
        "deploy-deprecation.md": ("Deprecation And Migration", "deprecation-and-migration.md"),
    },
    "nb-review-code": {
        "review-perf.md": ("Performance Optimization", "performance-optimization.md"),
        "review-simplification.md": ("Code Simplification", "code-simplification.md"),
    },
}

EXECUTION_MODELS = {
    "nb-review-code": [
        ("5.1 Code quality review", "review-quality", "All changed files"),
        ("5.2 Performance review", "review-perf", "Hot paths only"),
        ("5.3 Simplification review", "review-simplify", "Files > 200 lines"),
    ],
    "nb-review-arch": [
        ("5.1 Architecture guard", "arch-guard", "Constitution drift detection"),
        ("5.2 Architect preview", "arch-preview", "Impact and risk assessment"),
        ("5.3 Architecture contract", "arch-contract", "Planning contract validation"),
    ],
    "nb-deploy": [
        ("5.1 Lint", "deploy-lint", "Changed files"),
        ("5.2 Test", "deploy-test", "Test suite"),
        ("5.3 Build", "deploy-build", "Release artifacts"),
    ],
}

CAPABILITY_HINTS = {
    "nb-review-code": {
        "read_only": True,
        "allowed_tools": ["read_file", "grep", "list_files"],
        "globs": ["**/*.{ts,py,go,rs,java}"],
    },
    "nb-review-security": {
        "read_only": True,
        "allowed_tools": ["read_file", "grep"],
        "globs": ["**/*.{ts,py,go,rs,java}"],
    },
    "nb-review-arch": {
        "read_only": False,
        "allowed_tools": ["read_file", "grep", "list_files", "write_file"],
        "globs": ["**/spec*.md", "**/arch*.md"],
    },
    "nb-analyze": {
        "read_only": True,
        "allowed_tools": ["read_file", "grep"],
    },
    "nb-debug": {
        "read_only": False,
    },
}

FINDINGS_COMMANDS = {
    "nb-review-code",
    "nb-review-security",
    "nb-review-arch",
    "nb-analyze",
    "nb-checklist",
}

CATALOG: list[dict] = [
    # Core (wrap)
    {"name": "nb-constitution", "layer": "core", "phase": "constitution", "strategy": "wrap", "tier": "green",
     "description": "Define or verify project-wide invariants and architecture rules.",
     "purpose": "Define or verify the project constitution — project-wide invariants, architecture rules, and constraints that all subsequent work must respect.",
     "composes": ["speckit-constitution"], "next": "nb-specify",
     "artifacts": [("Constitution", ".specify/memory/constitution.md", "Project-wide rules and invariants")]},
    {"name": "nb-specify", "layer": "core", "phase": "specify", "strategy": "wrap", "tier": "green",
     "description": "Create or update a feature specification from requirements.",
     "purpose": "Create or update a feature specification that captures requirements, acceptance criteria, and scope for the current feature.",
     "composes": ["speckit-specify"], "next": "nb-clarify",
     "artifacts": [("Feature spec", "specs/{NNN}-{feature}/spec.md", "Requirements and acceptance criteria")]},
    {"name": "nb-clarify", "layer": "core", "phase": "clarify", "strategy": "wrap", "tier": "green",
     "description": "Clarify ambiguities in the current feature specification.",
     "purpose": "Resolve ambiguities and gaps in the feature spec before planning begins.",
     "composes": ["speckit-clarify"], "next": "nb-plan",
     "artifacts": [("Clarifications", "specs/{NNN}-{feature}/clarifications.md", "Resolved questions and decisions")]},
    {"name": "nb-plan", "layer": "core", "phase": "plan", "strategy": "wrap", "tier": "green",
     "description": "Design the technical approach and architecture for the feature.",
     "purpose": "Produce a technical plan describing architecture, components, and implementation approach for the feature.",
     "composes": ["speckit-plan"], "next": "nb-tasks",
     "artifacts": [("Plan", "specs/{NNN}-{feature}/plan.md", "Technical design and approach")]},
    {"name": "nb-tasks", "layer": "core", "phase": "tasks", "strategy": "wrap", "tier": "green",
     "description": "Break the plan into ordered, actionable implementation tasks.",
     "purpose": "Decompose the approved plan into ordered, actionable tasks for implementation.",
     "composes": ["speckit-tasks"], "next": "nb-implement",
     "artifacts": [("Tasks", "specs/{NNN}-{feature}/tasks.md", "Ordered implementation tasks")]},
    {"name": "nb-implement", "layer": "core", "phase": "implement", "strategy": "wrap", "tier": "green",
     "description": "Implement the feature according to spec, plan, and tasks.",
     "purpose": "Implement the feature according to the approved spec, plan, and task list.",
     "composes": ["speckit-implement"], "next": "nb-analyze",
     "artifacts": [("Implementation", "specs/{NNN}-{feature}/", "Source code and implementation artifacts")]},
    {"name": "nb-analyze", "layer": "core", "phase": "analyze", "strategy": "wrap", "tier": "green",
     "description": "Analyze implementation against spec for gaps and conformance.",
     "purpose": "Analyze the implementation against the specification to identify gaps, drift, and conformance issues.",
     "composes": ["speckit-analyze"], "next": "nb-converge",
     "artifacts": [("Analysis report", "specs/{NNN}-{feature}/analysis.md", "Gap analysis and conformance findings")]},
    {"name": "nb-converge", "layer": "core", "phase": "converge", "strategy": "wrap", "tier": "green",
     "description": "Iterate on gaps until spec and implementation converge.",
     "purpose": "Drive iteration cycles until the implementation converges with the specification.",
     "composes": ["speckit-converge"], "next": "nb-checklist",
     "artifacts": [("Convergence log", "specs/{NNN}-{feature}/convergence.md", "Iteration history and resolution")]},
    {"name": "nb-checklist", "layer": "core", "phase": "checklist", "strategy": "wrap", "tier": "green",
     "description": "Run final release checklist before shipping.",
     "purpose": "Execute the final release checklist to verify all requirements are met before shipping.",
     "composes": ["speckit-checklist"], "next": "nb-deploy",
     "artifacts": [("Checklist", "specs/{NNN}-{feature}/checklist.md", "Release readiness checklist results")]},
    # Extended
    {"name": "nb-interview", "layer": "extended", "phase": "specify", "strategy": "merge", "tier": "green",
     "description": "Stakeholder interview and idea refinement before specification.",
     "purpose": "Conduct multi-round stakeholder interviews and refine the idea before formal specification.",
     "composes": ["interview-me", "idea-refine"], "next": "nb-specify",
     "artifacts": [("Interview notes", "specs/{NNN}-{feature}/interview.md", "Stakeholder input and refined scope")]},
    {"name": "nb-review-code", "layer": "extended", "phase": "review", "strategy": "merge", "tier": "green",
     "description": "Comprehensive code review covering quality, simplification, and performance.",
     "purpose": "Run a comprehensive code review covering quality issues, simplification opportunities, and performance concerns.",
     "composes": ["code-review-and-quality", "code-simplification", "performance-optimization"], "next": "nb-implement",
     "artifacts": [("Review report", "specs/{NNN}-{feature}/review.md", "Findings by quality, simplification, performance")]},
    {"name": "nb-review-security", "layer": "extended", "phase": "review", "strategy": "merge", "tier": "green",
     "description": "Security hardening review and static analysis.",
     "purpose": "Run security hardening review combined with static analysis for vulnerability detection.",
     "composes": ["security-and-hardening", "static-analysis"], "next": "nb-implement",
     "artifacts": [("Security report", "specs/{NNN}-{feature}/security-review.md", "Security findings and SARIF output")]},
    {"name": "nb-review-arch", "layer": "extended", "phase": "review", "strategy": "sequence", "tier": "green",
     "description": "Architecture review: drift detection, impact preview, and contract validation.",
     "purpose": "Run a three-part architecture review: detect drift, preview impact, and validate the architecture contract.",
     "composes": ["architecture-guard", "architect-preview", "arch"], "next": "nb-implement",
     "artifacts": [
         ("Architecture review", "specs/{NNN}-{feature}/arch-review.md", "Unified architecture review report"),
         ("Architecture contract", ".specify/memory/architecture.md", "Updated planning contract"),
     ]},
    {"name": "nb-test", "layer": "extended", "phase": "test", "strategy": "merge", "tier": "green",
     "description": "Browser and webapp testing for the implementation.",
     "purpose": "Execute browser and webapp tests to verify the implementation works correctly.",
     "composes": ["browser-testing-with-devtools", "webapp-testing"], "next": "nb-analyze",
     "artifacts": [("Test results", "specs/{NNN}-{feature}/test-results.md", "Browser and webapp test outcomes")]},
    {"name": "nb-deploy", "layer": "extended", "phase": "deploy", "strategy": "merge", "tier": "green",
     "description": "Ship, CI/CD, versioning, observability, and deprecation lifecycle.",
     "purpose": "Execute the full deployment lifecycle: shipping, CI/CD, versioning, observability setup, and deprecation planning.",
     "composes": ["shipping-and-launch", "ci-cd-and-automation", "git-workflow-and-versioning",
                  "observability-and-instrumentation", "deprecation-and-migration"], "next": None,
     "artifacts": [("Deploy log", "specs/{NNN}-{feature}/deploy.md", "Deployment execution log")]},
    {"name": "nb-mcp", "layer": "extended", "phase": "implement", "strategy": "standalone", "tier": "green",
     "description": "Build MCP servers and tools following best practices.",
     "purpose": "Build MCP servers and tools following MCP SDK conventions and best practices.",
     "composes": ["mcp-builder"], "next": "nb-review-code",
     "artifacts": [("MCP implementation", "{project-specific}", "MCP server/tool source files")]},
    {"name": "nb-docs", "layer": "extended", "phase": "cross-cutting", "strategy": "standalone", "tier": "green",
     "description": "Generate documentation and architecture decision records.",
     "purpose": "Generate or update project documentation and architecture decision records.",
     "composes": ["documentation-and-adrs"], "next": None,
     "artifacts": [("Documentation", "docs/", "ADRs, API docs, and README updates")]},
    {"name": "nb-review-skill", "layer": "extended", "phase": "review", "strategy": "standalone", "tier": "amber",
     "description": "Review nubo-skills command definitions for governance compliance.",
     "purpose": "Review skill/command definitions in nubo-skills for governance, naming, and completion contract compliance.",
     "composes": ["nubo-review-skill"], "next": None,
     "artifacts": [("Skill review", "specs/{NNN}-{feature}/skill-review.md", "Governance review findings")]},
    # Utility
    {"name": "nb-debug", "layer": "utilities", "phase": "utilities", "strategy": "utility", "tier": "green",
     "description": "Debug failures and recover from errors reactively.",
     "purpose": "Diagnose test failures, runtime errors, and unexpected behavior. Reactive utility — not a pipeline command.",
     "composes": ["debugging-and-error-recovery"], "next": None, "utility": True},
]


def load_registry() -> dict:
    return yaml.safe_load((ROOT / "registry.yml").read_text())


def output_mode(registry: dict | None = None) -> str:
    reg = registry or load_registry()
    mode = (reg.get("generation") or {}).get("output_mode", "plain")
    return mode if mode in ("plain", "governed") else "plain"


def resolve_upstream_path(entry: dict) -> Path | None:
    t = entry.get("type")
    if t == "local":
        return ROOT / entry["path"]
    if t == "speckit":
        return ROOT / "upstream/speckit" / entry["path"]
    if t == "external":
        sub = SUBMODULE_MAP.get(entry.get("repo", ""))
        if not sub:
            return None
        return ROOT / sub / entry["path"]
    return None


def extract_procedure_body(path: Path) -> str:
    text = path.read_text()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2].lstrip("\n")
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        text = "\n".join(lines[1:]).lstrip("\n")
    return text.rstrip() + "\n"


def materialize_merge_references(cmd: dict, registry_entry: dict) -> list[tuple[str, str]]:
    layer = cmd["layer"]
    refs_dir = ROOT / "commands" / layer / cmd["name"] / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)
    links: list[tuple[str, str]] = []
    for compose in registry_entry.get("composes", []):
        upstream_name = compose.get("upstream_name", "upstream")
        path = resolve_upstream_path(compose)
        ref_rel = f"references/{upstream_name}.md"
        ref_path = refs_dir / f"{upstream_name}.md"
        if path and path.exists():
            ref_path.write_text(extract_procedure_body(path))
        else:
            ref_path.write_text(
                f"# {upstream_name}\n\nUpstream content missing. "
                f"Run `scripts/sync-upstream.sh --checkout` in nubo-skills.\n"
            )
        label = upstream_name.replace("-", " ").title()
        links.append((label, ref_rel))
    return links


def resolve_core_template(cmd: dict, registry_entry: dict) -> str:
    composes = registry_entry.get("composes", [])
    if not composes:
        return "<!-- no upstream composes defined -->\n"

    strategy = cmd["strategy"]
    if strategy == "merge" or len(composes) > 1:
        links = materialize_merge_references(cmd, registry_entry)
        lines = [
            "Follow each sub-procedure below and combine outputs into the command artifacts.",
            "",
        ]
        for index, (label, ref) in enumerate(links, start=1):
            lines.append(f"{index}. [{label}]({ref})")
        return "\n".join(lines) + "\n"

    bodies: list[str] = []
    for compose in composes:
        path = resolve_upstream_path(compose)
        name = compose.get("upstream_name", "upstream")
        if path and path.exists():
            bodies.append(extract_procedure_body(path))
        else:
            bodies.append(
                f"<!-- upstream missing: {name}. "
                f"Run scripts/sync-upstream.sh --checkout in nubo-skills. -->\n"
            )
    return "\n\n---\n\n".join(bodies)

    pad = " " * indent
    return "\n".join(f"{pad}- {item}" for item in items)


def render_user_prompts(name: str) -> str:
    p = USER_PROMPT_COMMANDS.get(name)
    if not p:
        return ""
    opts = "\n".join(f"  - `{k}` -- {v}" for k, v in p["options"])
    return f"""## User Prompts

### Prompt: {p['prompt_id']}
- **When:** {p['when']}
- **Question:** "{p['question']}"
- **Options:**
{opts}
- **Default:** `{p['default']}`
- **Blocks:** {p['blocks']}

"""


def render_prerequisites(name: str, strategy: str, mode: str) -> str:
    if name != "nb-review-arch":
        return ""
    speckit_note = (
        "Verify the following SpecKit extensions are installed "
        "(install with `scripts/install.sh --speckit` when needed):\n"
        if mode == "plain"
        else "Verify the following SpecKit extensions are installed "
        "(auto-installed by `scripts/install.sh --speckit`):\n"
    )
    return f"""## Prerequisites

{speckit_note}
1. Check `.specify/extensions/architecture-guard/` exists.
   If missing: `specify extension add architecture-guard --from https://github.com/DyanGalih/spec-kit-architecture-guard/archive/refs/tags/v1.15.0.zip`
2. Check `.specify/presets/architect-preview/preset.yml` exists.
   If missing: re-run `scripts/install.sh --speckit`.
3. Check `.specify/extensions/arch/` exists.
   If missing: `specify extension add arch --from https://github.com/bigsmartben/spec-kit-arch/archive/refs/tags/v1.2.2.zip`

If any extension cannot be installed, report the failure clearly before continuing.

"""


def render_context(cmd: dict) -> str:
    if cmd.get("utility"):
        return ""
    return """## Context

Before starting, gather:
- The feature spec at `specs/{NNN}-{feature}/spec.md` (if available).
- Prior artifacts from earlier pipeline phases (plan, tasks, etc.).
- Project-level conventions and constitution at `.specify/memory/constitution.md`.

"""


def render_procedure(cmd: dict, registry_entry: dict, mode: str) -> str:
    strategy = cmd["strategy"]
    if strategy == "sequence" and cmd["name"] == "nb-review-arch":
        return """## Procedure

Run these extension commands sequentially and compile a unified report:

1. `/speckit.architecture-guard.architecture-review` — Detect drift from architecture constitution.
2. `/speckit.architect-preview` — Preview architectural impact and complexity.
3. `/speckit.arch.full-generate` — Validate or update the architecture planning contract.

See [architecture guard steps](references/arch-guard-steps.md), [architect preview steps](references/arch-preview-steps.md), and [architecture contract steps](references/arch-contract-steps.md) for detailed procedures.

Combine outputs into a single architecture review report.

"""
    extra = ""
    if cmd["name"] == "nb-deploy" and mode == "governed":
        extra = """
See [shipping](references/deploy-shipping.md), [CI/CD](references/deploy-cicd.md), [git workflow](references/deploy-git.md), [observability](references/deploy-observability.md), and [deprecation](references/deploy-deprecation.md) for detailed sub-procedures.
"""
    if strategy in ("wrap", "merge", "standalone", "utility"):
        if mode == "plain":
            core = resolve_core_template(cmd, registry_entry)
            return f"## Procedure\n\n{core}{extra}"
        if cmd["name"] == "nb-review-code":
            extra = "\nSee [performance review](references/review-perf.md) and [simplification review](references/review-simplification.md) for detailed sub-procedures.\n"
        return f"""## Procedure

{{CORE_TEMPLATE}}
{extra}"""
    return """## Procedure

{CORE_TEMPLATE}
"""


def render_execution_model(name: str) -> str:
    steps = EXECUTION_MODELS.get(name)
    if not steps:
        return ""
    rows = "\n".join(f"| {s} | {a} | {sc} |" for s, a, sc in steps)
    return f"""## Execution Model

**Parallel execution:** When the runtime supports subagents (Cursor Task tool, Claude Code subagents),
the following procedure steps MAY run in parallel:

| Step | Subagent | Scope |
|------|----------|-------|
{rows}

**Merge strategy:** Collect all subagent findings into the unified `findings` array.
Deduplicate by `location`. Highest severity wins on conflicts.

**Fallback:** If subagents are unavailable, run steps sequentially.

"""


def render_artifacts(cmd: dict) -> str:
    if cmd.get("utility"):
        return ""
    rows = "\n".join(f"| {a} | `{p}` | {d} |" for a, p, d in cmd["artifacts"])
    return f"""## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
{rows}

"""


def render_pipeline(cmd: dict) -> str:
    if cmd.get("utility"):
        return ""
    next_cmd = cmd.get("next")
    if next_cmd is None:
        return """## Pipeline

**Terminal command** — no pipeline successor.

"""
    return f"""## Pipeline

**Next command:** `/{next_cmd}`

- Use only this successor — do not invent, skip, or substitute pipeline steps in summaries or feature artifacts.
"""


def render_nubo_appendix(cmd: dict) -> str:
    if cmd["name"] == "nb-checklist":
        return """## Nubo release gate

For `specs/{NNN}-{feature}/checklist.md`:

- Record gate result (`SHIP` / `NO SHIP`), pre-ship checks, and validation log only.
- Do **not** write pipeline routing in `checklist.md` — routing is in `## Pipeline` above.

"""
    return ""


def render_completion(cmd: dict) -> str:
    name = cmd["name"]
    phase = cmd["phase"]
    next_cmd = cmd.get("next")
    next_json = json.dumps(next_cmd)
    artifacts = []
    if not cmd.get("utility"):
        for _, path, _ in cmd["artifacts"]:
            artifacts.append({"path": path, "action": "created", "lines": 0})
    findings_block = ""
    if name in FINDINGS_COMMANDS:
        findings_block = """
  "findings": [
    { "severity": "P1", "category": "quality", "message": "...", "location": "file:line" }
  ],"""
    artifacts_json = json.dumps(artifacts, indent=4)
    artifacts_indented = "\n".join("  " + line for line in artifacts_json.splitlines())
    return f"""## Completion Response

```json
{{
  "command": "{name}",
  "status": "success",
  "phase": "{phase}",
  "artifacts": {artifacts_indented.strip()},
{findings_block}
  "metrics": {{
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  }},
  "next_command": {next_json},
  "message": "<human-readable summary>"
}}
```

After emitting the JSON, render the visual summary block:

---
### {name}  |  SUCCESS
**Phase:** {phase}  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `{next_cmd or 'null'}`
---
"""


def render_frontmatter(cmd: dict) -> str:
    hints = CAPABILITY_HINTS.get(cmd["name"], {})
    lines = [
        "---",
        f"name: {cmd['name']}",
        f"description: \"{cmd['description']}\"",
        "metadata:",
        f"  phase: {cmd['phase']}",
        f"  strategy: {cmd['strategy']}",
        f"  tier: {cmd['tier']}",
        "  composes:",
    ]
    lines.extend(f"    - {c}" for c in cmd["composes"])
    lines.append('  nubo_version: "1.0.0"')
    if "allowed_tools" in hints:
        lines.append("  allowed_tools:")
        lines.extend(f"    - {t}" for t in hints["allowed_tools"])
    if "read_only" in hints:
        lines.append(f"  read_only: {str(hints['read_only']).lower()}")
    if "globs" in hints:
        lines.append("  globs:")
        lines.extend(f'    - "{g}"' for g in hints["globs"])
    lines.append("---")
    return "\n".join(lines)


def render_skill(cmd: dict, registry_entry: dict, mode: str) -> str:
    name = cmd["name"]
    if cmd.get("utility"):
        conventions = "- Reactive utility — respond with a clear summary of diagnosis and fixes."
    elif mode == "plain":
        conventions = (
            "- Work in `specs/{NNN}-{feature}/` for all artifacts.\n"
            "- Follow Nubo naming conventions for generated files.\n"
            "- Pipeline routing belongs only in each command's `## Pipeline` section — "
            "never write `Next command` or `proceed to` in feature artifacts."
        )
    else:
        conventions = (
            "- Work in `specs/{NNN}-{feature}/` for all artifacts.\n"
            "- Follow Nubo naming conventions for generated files.\n"
            "- Pipeline routing belongs only in each command's `## Pipeline` section — "
            "never write `Next command` or `proceed to` in feature artifacts.\n"
            "- Output the Completion Response when done."
        )
    parts = [
        render_frontmatter(cmd),
        "",
        f"# {name}",
        "",
        "## Purpose",
        "",
        cmd["purpose"],
        "",
        "## Conventions",
        "",
        conventions,
        "",
        render_user_prompts(name),
        render_prerequisites(name, cmd["strategy"], mode),
        render_context(cmd),
        render_procedure(cmd, registry_entry, mode),
        render_execution_model(name),
        render_artifacts(cmd),
        render_pipeline(cmd),
        render_nubo_appendix(cmd),
    ]
    if mode == "governed":
        parts.append(render_completion(cmd))
    return "\n".join(p for p in parts if p is not None)


REF_LINK_RE = re.compile(r"\]\((references/[^)]+)\)")


def linked_references(skill_path: Path) -> set[str]:
    return set(REF_LINK_RE.findall(skill_path.read_text()))


def prune_orphan_references(skill_path: Path) -> None:
    refs_dir = skill_path.parent / "references"
    if not refs_dir.exists():
        return
    linked = linked_references(skill_path)
    for ref_file in refs_dir.glob("*.md"):
        rel = f"references/{ref_file.name}"
        if rel not in linked:
            ref_file.unlink()


def governed_alias_body(title: str, canonical: str) -> str:
    return f"""# {title}

Progressive-disclosure alias for governed output mode.

## Canonical procedure

See [{title}]({canonical}) for the full sub-procedure.

## When to use this file

Governed-mode installs link short alias names for subagent routing.
Follow the canonical reference above — do not duplicate its content here.

## Subagent handoff

Load the canonical reference, execute its procedure, and return findings scoped
to the alias topic only.
"""


def write_references(cmd: dict, skill_path: Path, mode: str) -> None:
    refs_dir = skill_path.parent / "references"
    if cmd["name"] == "nb-review-arch":
        refs_dir.mkdir(parents=True, exist_ok=True)
        for filename, body in ARCH_REFERENCE_GUIDES.items():
            (refs_dir / filename).write_text(body.rstrip() + "\n")
    if mode == "governed":
        aliases = GOVERNED_REFERENCE_ALIASES.get(cmd["name"], {})
        if aliases:
            refs_dir.mkdir(parents=True, exist_ok=True)
            for alias, (title, canonical) in aliases.items():
                (refs_dir / alias).write_text(governed_alias_body(title, canonical))
    prune_orphan_references(skill_path)


def parse_skill_description(skill_path: Path) -> str:
    text = skill_path.read_text()
    if not text.startswith("---"):
        return skill_path.parent.name
    parts = text.split("---", 2)
    if len(parts) < 3:
        return skill_path.parent.name
    meta = yaml.safe_load(parts[1]) or {}
    return str(meta.get("description") or skill_path.parent.name)


def generate_extension() -> None:
    registry = yaml.safe_load((ROOT / "registry.yml").read_text())
    ext_root = ROOT / "extensions" / "nubo-skills"
    ext_commands = ext_root / "commands"
    if ext_commands.exists():
        shutil.rmtree(ext_commands)
    ext_commands.mkdir(parents=True, exist_ok=True)

    provides: list[dict[str, str]] = []
    for name, entry in registry.get("commands", {}).items():
        layer = entry["layer"]
        if layer == "utility":
            layer = "utilities"
        src = ROOT / "commands" / layer / name
        dst = ext_commands / layer / name
        shutil.copytree(src, dst)
        skill = dst / "SKILL.md"
        provides.append({
            "name": f"speckit.nubo-skills.{name}",
            "file": f"commands/{layer}/{name}/SKILL.md",
            "description": parse_skill_description(skill),
        })

    manifest = {
        "schema_version": "1.0",
        "extension": {
            "id": "nubo-skills",
            "name": "Nubo Skills",
            "version": "1.0.0",
            "description": "Governed nb-{command} skills for the full Nubo SDLC pipeline",
            "author": "Nubo SDLC Team",
            "repository": "https://github.com/nuboai/nubo-skills",
            "license": "Proprietary",
        },
        "requires": {
            "speckit_version": ">=0.8.5",
        },
        "provides": {
            "commands": provides,
        },
        "tags": ["nubo", "governance", "sdlc"],
    }
    (ext_root / "extension.yml").write_text(yaml.dump(manifest, sort_keys=False))
    print(f"generated {ext_root.relative_to(ROOT)}/extension.yml")


def main() -> None:
    registry = load_registry()
    mode = output_mode(registry)
    print(f"generation.output_mode={mode}")
    for cmd in CATALOG:
        registry_entry = registry.get("commands", {}).get(cmd["name"], {})
        path = ROOT / "commands" / cmd["layer"] / cmd["name"] / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_skill(cmd, registry_entry, mode))
        write_references(cmd, path, mode)
        print(f"generated {path.relative_to(ROOT)}")
    generate_extension()


if __name__ == "__main__":
    main()
