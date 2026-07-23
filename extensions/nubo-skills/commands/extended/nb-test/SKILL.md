---
name: nb-test
description: "Browser and webapp testing for the implementation."
metadata:
  phase: test
  strategy: merge
  tier: green
  composes:
    - browser-testing-with-devtools
    - webapp-testing
  nubo_version: "1.0.0"
---

# nb-test

## Purpose

Execute browser and webapp tests to verify the implementation works correctly.

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
| Test results | `specs/{NNN}-{feature}/test-results.md` | Browser and webapp test outcomes |


## Completion Response

```json
{
  "command": "nb-test",
  "status": "success",
  "phase": "test",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/test-results.md",
          "action": "created",
          "lines": 0
      }
  ],

  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": "nb-analyze",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-test  |  SUCCESS
**Phase:** test  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-analyze`
---
