---
name: nb-clarify
description: "Clarify ambiguities in the current feature specification."
metadata:
  phase: clarify
  strategy: wrap
  tier: green
  composes:
    - speckit-clarify
  nubo_version: "1.0.0"
---

# nb-clarify

## Purpose

Resolve ambiguities and gaps in the feature spec before planning begins.

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
| Clarifications | `specs/{NNN}-{feature}/clarifications.md` | Resolved questions and decisions |


## Completion Response

```json
{
  "command": "nb-clarify",
  "status": "success",
  "phase": "clarify",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/clarifications.md",
          "action": "created",
          "lines": 0
      }
  ],

  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": "nb-plan",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-clarify  |  SUCCESS
**Phase:** clarify  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-plan`
---
