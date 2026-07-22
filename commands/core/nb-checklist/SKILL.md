---
name: nb-checklist
description: "Run final release checklist before shipping."
metadata:
  phase: checklist
  strategy: wrap
  tier: green
  composes:
    - speckit-checklist
  nubo_version: "1.0.0"
---

# nb-checklist

## Purpose

Execute the final release checklist to verify all requirements are met before shipping.

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
| Checklist | `specs/{NNN}-{feature}/checklist.md` | Release readiness checklist results |


## Completion Response

```json
{
  "command": "nb-checklist",
  "status": "success",
  "phase": "checklist",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/checklist.md",
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
  "next_command": "nb-deploy",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-checklist  |  SUCCESS
**Phase:** checklist  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-deploy`
---
