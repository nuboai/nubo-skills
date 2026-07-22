---
name: nb-review-code
description: "Comprehensive code review covering quality, simplification, and performance."
metadata:
  phase: review
  strategy: merge
  tier: green
  composes:
    - code-review-and-quality
    - code-simplification
    - performance-optimization
  nubo_version: "1.0.0"
  allowed_tools:
    - read_file
    - grep
    - list_files
  read_only: true
  globs:
    - "**/*.{ts,py,go,rs,java}"
---

# nb-review-code

## Purpose

Run a comprehensive code review covering quality issues, simplification opportunities, and performance concerns.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Output the Completion Response when done.

## User Prompts

### Prompt: fix-delegation
- **When:** Findings with severity P0-P2 are detected
- **Question:** "Create fix tasks for these P1-P2 issues?"
- **Options:**
  - `create-tasks` -- Generate nb-tasks entries for each finding
  - `report-only` -- Keep findings in review report only
  - `dismiss` -- Acknowledge and dismiss non-critical findings
- **Default:** `create-tasks`
- **Blocks:** Post-review task generation



## Context

Before starting, gather:
- The feature spec at `specs/{NNN}-{feature}/spec.md` (if available).
- Prior artifacts from earlier pipeline phases (plan, tasks, etc.).
- Project-level conventions and constitution at `.specify/memory/constitution.md`.


## Procedure

{CORE_TEMPLATE}

See [performance review](references/review-perf.md) and [simplification review](references/review-simplification.md) for detailed sub-procedures.

## Execution Model

**Parallel execution:** When the runtime supports subagents (Cursor Task tool, Claude Code subagents),
the following procedure steps MAY run in parallel:

| Step | Subagent | Scope |
|------|----------|-------|
| 5.1 Code quality review | review-quality | All changed files |
| 5.2 Performance review | review-perf | Hot paths only |
| 5.3 Simplification review | review-simplify | Files > 200 lines |

**Merge strategy:** Collect all subagent findings into the unified `findings` array.
Deduplicate by `location`. Highest severity wins on conflicts.

**Fallback:** If subagents are unavailable, run steps sequentially.


## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Review report | `specs/{NNN}-{feature}/review.md` | Findings by quality, simplification, performance |


## Completion Response

```json
{
  "command": "nb-review-code",
  "status": "success",
  "phase": "review",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/review.md",
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
### nb-review-code  |  SUCCESS
**Phase:** review  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-implement`
---
