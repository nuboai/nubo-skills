---
name: nb-converge
description: "Iterate on gaps until spec and implementation converge."
metadata:
  phase: converge
  strategy: wrap
  tier: green
  composes:
    - speckit-converge
  nubo_version: "1.0.0"
---

# nb-converge

## Purpose

Drive iteration cycles until the implementation converges with the specification.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Output the Completion Response when done.



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
| Convergence log | `specs/{NNN}-{feature}/convergence.md` | Iteration history and resolution |


## Completion Response

```json
{
  "command": "nb-converge",
  "status": "success",
  "phase": "converge",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/convergence.md",
          "action": "created",
          "lines": 0
      }
  ],

  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": "nb-checklist",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-converge  |  SUCCESS
**Phase:** converge  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-checklist`
---
