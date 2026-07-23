---
name: nb-constitution
description: "Define or verify project-wide invariants and architecture rules."
metadata:
  phase: constitution
  strategy: wrap
  tier: green
  composes:
    - speckit-constitution
  nubo_version: "1.0.0"
---

# nb-constitution

## Purpose

Define or verify the project constitution — project-wide invariants, architecture rules, and constraints that all subsequent work must respect.

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
| Constitution | `.specify/memory/constitution.md` | Project-wide rules and invariants |


## Completion Response

```json
{
  "command": "nb-constitution",
  "status": "success",
  "phase": "constitution",
  "artifacts": [
      {
          "path": ".specify/memory/constitution.md",
          "action": "created",
          "lines": 0
      }
  ],

  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": "nb-specify",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-constitution  |  SUCCESS
**Phase:** constitution  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-specify`
---
