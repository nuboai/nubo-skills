---
name: nb-docs
description: "Generate documentation and architecture decision records."
metadata:
  phase: cross-cutting
  strategy: standalone
  tier: green
  composes:
    - documentation-and-adrs
  nubo_version: "1.0.0"
---

# nb-docs

## Purpose

Generate or update project documentation and architecture decision records.

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
| Documentation | `docs/` | ADRs, API docs, and README updates |


## Completion Response

```json
{
  "command": "nb-docs",
  "status": "success",
  "phase": "cross-cutting",
  "artifacts": [
      {
          "path": "docs/",
          "action": "created",
          "lines": 0
      }
  ],

  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": null,
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-docs  |  SUCCESS
**Phase:** cross-cutting  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `null`
---
