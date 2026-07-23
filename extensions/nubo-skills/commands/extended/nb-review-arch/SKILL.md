---
name: nb-review-arch
description: "Architecture review: drift detection, impact preview, and contract validation."
metadata:
  phase: review
  strategy: sequence
  tier: green
  composes:
    - architecture-guard
    - architect-preview
    - arch
  nubo_version: "1.0.0"
  allowed_tools:
    - read_file
    - grep
    - list_files
    - write_file
  read_only: false
  globs:
    - "**/spec*.md"
    - "**/arch*.md"
---

# nb-review-arch

## Purpose

Run a three-part architecture review: detect drift, preview impact, and validate the architecture contract.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Pipeline routing belongs only in each command's `## Pipeline` section — never write `Next command` or `proceed to` in feature artifacts.

## User Prompts

### Prompt: action-selection
- **When:** Architecture review completes with findings
- **Question:** "Apply architecture updates or create refactor tasks?"
- **Options:**
  - `apply-updates` -- Update architecture contract and generate refactor tasks
  - `tasks-only` -- Create refactor tasks without updating contract
  - `report-only` -- Keep findings in review report only
- **Default:** `apply-updates`
- **Blocks:** Architecture contract update


## Prerequisites

Verify the following SpecKit extensions are installed (install with `scripts/install.sh --speckit` when needed):

1. Check `.specify/extensions/architecture-guard/` exists.
   If missing: `specify extension add architecture-guard --from https://github.com/DyanGalih/spec-kit-architecture-guard/archive/refs/tags/v1.15.0.zip`
2. Check `.specify/presets/architect-preview/preset.yml` exists.
   If missing: re-run `scripts/install.sh --speckit`.
3. Check `.specify/extensions/arch/` exists.
   If missing: `specify extension add arch --from https://github.com/bigsmartben/spec-kit-arch/archive/refs/tags/v1.2.2.zip`

If any extension cannot be installed, report the failure clearly before continuing.


## Context

Before starting, gather:
- The feature spec at `specs/{NNN}-{feature}/spec.md` (if available).
- Prior artifacts from earlier pipeline phases (plan, tasks, etc.).
- Project-level conventions and constitution at `.specify/memory/constitution.md`.


## Procedure

Run these extension commands sequentially and compile a unified report:

1. `/speckit.architecture-guard.architecture-review` — Detect drift from architecture constitution.
2. `/speckit.architect-preview` — Preview architectural impact and complexity.
3. `/speckit.arch.full-generate` — Validate or update the architecture planning contract.

See [architecture guard steps](references/arch-guard-steps.md), [architect preview steps](references/arch-preview-steps.md), and [architecture contract steps](references/arch-contract-steps.md) for detailed procedures.

Combine outputs into a single architecture review report.


## Execution Model

**Parallel execution:** When the runtime supports subagents (Cursor Task tool, Claude Code subagents),
the following procedure steps MAY run in parallel:

| Step | Subagent | Scope |
|------|----------|-------|
| 5.1 Architecture guard | arch-guard | Constitution drift detection |
| 5.2 Architect preview | arch-preview | Impact and risk assessment |
| 5.3 Architecture contract | arch-contract | Planning contract validation |

**Merge strategy:** Collect all subagent findings into the unified `findings` array.
Deduplicate by `location`. Highest severity wins on conflicts.

**Fallback:** If subagents are unavailable, run steps sequentially.


## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Architecture review | `specs/{NNN}-{feature}/arch-review.md` | Unified architecture review report |
| Architecture contract | `.specify/memory/architecture.md` | Updated planning contract |


## Pipeline

**Next command:** `/nb-implement`

- Use only this successor — do not invent, skip, or substitute pipeline steps in summaries or feature artifacts.

