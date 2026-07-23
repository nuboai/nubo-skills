---
name: nb-review-skill
description: "Review nubo-skills command definitions for governance compliance."
metadata:
  phase: review
  strategy: standalone
  tier: amber
  composes:
    - nubo-review-skill
  nubo_version: "1.0.0"
---

# nb-review-skill

## Purpose

Review skill/command definitions in nubo-skills for governance, naming, and completion contract compliance.

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
| Skill review | `specs/{NNN}-{feature}/skill-review.md` | Governance review findings |


## Completion Response

```json
{
  "command": "nb-review-skill",
  "status": "success",
  "phase": "review",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/skill-review.md",
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
### nb-review-skill  |  SUCCESS
**Phase:** review  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `null`
---
