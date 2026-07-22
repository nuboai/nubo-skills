---
name: nb-implement
description: "Implement the feature according to spec, plan, and tasks."
metadata:
  phase: implement
  strategy: wrap
  tier: green
  composes:
    - speckit-implement
  nubo_version: "1.0.0"
---

# nb-implement

## Purpose

Implement the feature according to the approved spec, plan, and task list.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Output the Completion Response when done.

## User Prompts

### Prompt: strategy-confirmation
- **When:** Before writing code
- **Question:** "Proceed with this implementation approach?"
- **Options:**
  - `proceed` -- Start implementation
  - `revise` -- Revise approach before coding
  - `split` -- Break into smaller implementation steps
- **Default:** `proceed`
- **Blocks:** Code changes



## Context

Before starting, gather:
- The feature spec at `specs/{NNN}-{feature}/spec.md` (if available).
- Prior artifacts from earlier pipeline phases (plan, tasks, etc.).
- Project-level conventions and constitution at `.specify/memory/constitution.md`.


## Procedure

{CORE_TEMPLATE}


## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Implementation | `specs/{NNN}-{feature}/` | Source code and implementation artifacts |


## Completion Response

```json
{
  "command": "nb-implement",
  "status": "success",
  "phase": "implement",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/",
          "action": "created",
          "lines": 0
      }
  ],

  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": "nb-analyze",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-implement  |  SUCCESS
**Phase:** implement  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-analyze`
---
