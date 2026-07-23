---
name: nb-plan
description: "Design the technical approach and architecture for the feature."
metadata:
  phase: plan
  strategy: wrap
  tier: green
  composes:
    - speckit-plan
  nubo_version: "1.0.0"
---

# nb-plan

## Purpose

Produce a technical plan describing architecture, components, and implementation approach for the feature.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Output the Completion Response when done.

## User Prompts

### Prompt: approach-selection
- **When:** Multiple valid design approaches exist
- **Question:** "Which approach should we use?"
- **Options:**
  - `approach-a` -- Use recommended approach A
  - `approach-b` -- Use alternative approach B
  - `hybrid` -- Combine elements from both approaches
- **Default:** `approach-a`
- **Blocks:** Plan artifact write



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
| Plan | `specs/{NNN}-{feature}/plan.md` | Technical design and approach |


## Completion Response

```json
{
  "command": "nb-plan",
  "status": "success",
  "phase": "plan",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/plan.md",
          "action": "created",
          "lines": 0
      }
  ],

  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": "nb-tasks",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-plan  |  SUCCESS
**Phase:** plan  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-tasks`
---
