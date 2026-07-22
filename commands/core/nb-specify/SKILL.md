---
name: nb-specify
description: "Create or update a feature specification from requirements."
metadata:
  phase: specify
  strategy: wrap
  tier: green
  composes:
    - speckit-specify
  nubo_version: "1.0.0"
---

# nb-specify

## Purpose

Create or update a feature specification that captures requirements, acceptance criteria, and scope for the current feature.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Output the Completion Response when done.

## User Prompts

### Prompt: spec-review
- **When:** Before writing final spec artifact
- **Question:** "Approve this spec?"
- **Options:**
  - `approve` -- Finalize spec.md
  - `revise` -- Revise spec based on feedback
  - `clarify` -- Run nb-clarify before finalizing
- **Default:** `approve`
- **Blocks:** Spec artifact write



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
| Feature spec | `specs/{NNN}-{feature}/spec.md` | Requirements and acceptance criteria |


## Completion Response

```json
{
  "command": "nb-specify",
  "status": "success",
  "phase": "specify",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/spec.md",
          "action": "created",
          "lines": 0
      }
  ],

  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": "nb-clarify",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-specify  |  SUCCESS
**Phase:** specify  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-clarify`
---
