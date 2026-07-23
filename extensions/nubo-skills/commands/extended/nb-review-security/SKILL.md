---
name: nb-review-security
description: "Security hardening review and static analysis."
metadata:
  phase: review
  strategy: merge
  tier: green
  composes:
    - security-and-hardening
    - static-analysis
  nubo_version: "1.0.0"
  allowed_tools:
    - read_file
    - grep
  read_only: true
  globs:
    - "**/*.{ts,py,go,rs,java}"
---

# nb-review-security

## Purpose

Run security hardening review combined with static analysis for vulnerability detection.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Output the Completion Response when done.

## User Prompts

### Prompt: remediation-delegation
- **When:** Security findings are detected
- **Question:** "Create remediation tasks for these findings?"
- **Options:**
  - `create-tasks` -- Generate remediation tasks for nb-implement
  - `report-only` -- Keep findings in security report only
  - `escalate` -- Escalate critical findings for immediate action
- **Default:** `create-tasks`
- **Blocks:** Remediation task generation



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
| Security report | `specs/{NNN}-{feature}/security-review.md` | Security findings and SARIF output |


## Completion Response

```json
{
  "command": "nb-review-security",
  "status": "success",
  "phase": "review",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/security-review.md",
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
  "next_command": "nb-implement",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-review-security  |  SUCCESS
**Phase:** review  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-implement`
---
