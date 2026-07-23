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
- Output the Completion Response when done.

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

Verify the following SpecKit extensions are installed (auto-installed by `scripts/install.sh` when `.specify/` exists):

1. Check `.specify/extensions/architecture-guard/` exists.
   If missing: `specify extension add architecture-guard --from https://github.com/DyanGalih/spec-kit-architecture-guard/archive/refs/tags/v1.15.0.zip`
2. Check `.specify/extensions/architect-preview/` exists.
   If missing: `specify extension add architect-preview --from https://github.com/UmmeHabiba1312/spec-kit-architect-preview/archive/refs/tags/v1.0.0.zip`
3. Check `.specify/extensions/arch/` exists.
   If missing: `specify extension add arch --from https://github.com/bigsmartben/spec-kit-arch/archive/refs/tags/v1.2.2.zip`

If any extension cannot be installed, report status "error" with details.


## Context

Before starting, gather:
- The feature spec at `specs/{NNN}-{feature}/spec.md` (if available).
- Prior artifacts from earlier pipeline phases (plan, tasks, etc.).
- Project-level conventions and constitution at `.specify/memory/constitution.md`.


## Procedure

Run these extension commands sequentially and compile a unified report:

1. `/speckit.architecture-guard.architecture-review` — Detect drift from architecture constitution.
2. `/speckit.architect-preview` — Preview architectural impact and complexity.
3. `/speckit.arch.generate` — Validate or update the architecture planning contract.

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


## Completion Response

```json
{
  "command": "nb-review-arch",
  "status": "success",
  "phase": "review",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/arch-review.md",
          "action": "created",
          "lines": 0
      },
      {
          "path": ".specify/memory/architecture.md",
          "action": "created",
          "lines": 0
      }
  ],

  "findings": [
    { "severity": "P1", "category": "quality", "message": "...", "location": "file:line" }
  ],
  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": "nb-implement",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-review-arch  |  SUCCESS
**Phase:** review  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-implement`
---
