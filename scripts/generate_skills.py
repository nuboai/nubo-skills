#!/usr/bin/env python3
"""Generate all nb-* command SKILL.md files from catalog definitions."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

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
     "composes": ["architecture-guard", "architect-preview", "spec-kit-arch"], "next": "nb-implement",
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


def yaml_list(items: list[str], indent: int = 2) -> str:
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


def render_prerequisites(name: str, strategy: str) -> str:
    if name != "nb-review-arch":
        return ""
    return """## Prerequisites

Verify the following SpecKit extensions are installed:

1. Check `.specify/extensions/architecture-guard/` exists.
   If missing: `specify extension add DyanGalih/spec-kit-architecture-guard`
2. Check `.specify/extensions/architect-preview/` exists.
   If missing: `specify extension add UmmeHabiba1312/spec-kit-architect-preview`
3. Check `.specify/extensions/spec-kit-arch/` exists.
   If missing: `specify extension add bigsmartben/spec-kit-arch`

If any extension cannot be installed, report status "error" with details.

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


def render_procedure(cmd: dict) -> str:
    strategy = cmd["strategy"]
    if strategy == "sequence" and cmd["name"] == "nb-review-arch":
        return """## Procedure

Run these extension commands sequentially and compile a unified report:

1. `/speckit.architecture-guard.architecture-review` — Detect drift from architecture constitution.
2. `/speckit.architect-preview` — Preview architectural impact and complexity.
3. `/speckit.arch.generate` — Validate or update the architecture planning contract.

See [architecture guard steps](references/arch-guard-steps.md), [architect preview steps](references/arch-preview-steps.md), and [architecture contract steps](references/arch-contract-steps.md) for detailed procedures.

Combine outputs into a single architecture review report.

"""
    if strategy in ("wrap", "merge", "standalone"):
        extra = ""
        if cmd["name"] == "nb-review-code":
            extra = "\nSee [performance review](references/review-perf.md) and [simplification review](references/review-simplification.md) for detailed sub-procedures.\n"
        if cmd["name"] == "nb-deploy":
            extra = """
See [shipping](references/deploy-shipping.md), [CI/CD](references/deploy-cicd.md), [git workflow](references/deploy-git.md), [observability](references/deploy-observability.md), and [deprecation](references/deploy-deprecation.md) for detailed sub-procedures.
"""
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


def render_skill(cmd: dict) -> str:
    name = cmd["name"]
    conventions = "- Output the Completion Response when done."
    if not cmd.get("utility"):
        conventions = (
            "- Work in `specs/{NNN}-{feature}/` for all artifacts.\n"
            "- Follow Nubo naming conventions for generated files.\n"
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
        render_prerequisites(name, cmd["strategy"]),
        render_context(cmd),
        render_procedure(cmd),
        render_execution_model(name),
        render_artifacts(cmd),
        render_completion(cmd),
    ]
    return "\n".join(p for p in parts if p is not None)


def write_references(cmd: dict) -> None:
    name = cmd["name"]
    base = ROOT / "commands" / cmd["layer"] / name / "references"
    if name == "nb-review-code":
        base.mkdir(parents=True, exist_ok=True)
        (base / "review-perf.md").write_text("# Performance Review\n\nDetailed performance review procedure from performance-optimization upstream skill.\n")
        (base / "review-simplification.md").write_text("# Simplification Review\n\nDetailed simplification procedure from code-simplification upstream skill.\n")
    elif name == "nb-review-arch":
        base.mkdir(parents=True, exist_ok=True)
        (base / "arch-guard-steps.md").write_text("# Architecture Guard Steps\n\nDetailed steps for architecture-guard extension.\n")
        (base / "arch-preview-steps.md").write_text("# Architect Preview Steps\n\nDetailed steps for architect-preview extension.\n")
        (base / "arch-contract-steps.md").write_text("# Architecture Contract Steps\n\nDetailed steps for spec-kit-arch extension.\n")
    elif name == "nb-deploy":
        base.mkdir(parents=True, exist_ok=True)
        for f in ["deploy-shipping", "deploy-cicd", "deploy-git", "deploy-observability", "deploy-deprecation"]:
            (base / f"{f}.md").write_text(f"# {f.replace('-', ' ').title()}\n\nDetailed sub-procedure.\n")


def main() -> None:
    for cmd in CATALOG:
        path = ROOT / "commands" / cmd["layer"] / cmd["name"] / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_skill(cmd))
        write_references(cmd)
        print(f"generated {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
