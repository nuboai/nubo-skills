---
name: nb-interview
description: "Stakeholder interview and idea refinement before specification."
metadata:
  phase: specify
  strategy: merge
  tier: green
  composes:
    - interview-me
    - idea-refine
  nubo_version: "1.0.0"
---

# nb-interview

## Purpose

Conduct multi-round stakeholder interviews and refine the idea before formal specification.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Output the Completion Response when done.

## User Prompts

### Prompt: scope-confirmation
- **When:** After interview rounds complete
- **Question:** "Is this scope complete?"
- **Options:**
  - `complete` -- Finalize scope and proceed to constitution/specify
  - `continue` -- Run another interview round
  - `revise` -- Revise scope summary before continuing
- **Default:** `complete`
- **Blocks:** Scope finalization



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
| Interview notes | `specs/{NNN}-{feature}/interview.md` | Stakeholder input and refined scope |


## Completion Response

```json
{
  "command": "nb-interview",
  "status": "success",
  "phase": "specify",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/interview.md",
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
### nb-interview  |  SUCCESS
**Phase:** specify  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-specify`
---
