---
name: nb-analyze
description: "Analyze implementation against spec for gaps and conformance."
metadata:
  phase: analyze
  strategy: wrap
  tier: green
  composes:
    - speckit-analyze
  nubo_version: "1.0.0"
  allowed_tools:
    - read_file
    - grep
  read_only: true
---

# nb-analyze

## Purpose

Analyze the implementation against the specification to identify gaps, drift, and conformance issues.

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
| Analysis report | `specs/{NNN}-{feature}/analysis.md` | Gap analysis and conformance findings |


## Completion Response

```json
{
  "command": "nb-analyze",
  "status": "success",
  "phase": "analyze",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/analysis.md",
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
  "next_command": "nb-converge",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-analyze  |  SUCCESS
**Phase:** analyze  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-converge`
---
