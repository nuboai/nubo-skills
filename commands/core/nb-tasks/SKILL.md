---
name: nb-tasks
description: "Break the plan into ordered, actionable implementation tasks."
metadata:
  phase: tasks
  strategy: wrap
  tier: green
  composes:
    - speckit-tasks
  nubo_version: "1.0.0"
---

# nb-tasks

## Purpose

Decompose the approved plan into ordered, actionable tasks for implementation.

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
| Tasks | `specs/{NNN}-{feature}/tasks.md` | Ordered implementation tasks |


## Completion Response

```json
{
  "command": "nb-tasks",
  "status": "success",
  "phase": "tasks",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/tasks.md",
          "action": "created",
          "lines": 0
      }
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
### nb-tasks  |  SUCCESS
**Phase:** tasks  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-implement`
---
