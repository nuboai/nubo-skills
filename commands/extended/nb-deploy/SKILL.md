---
name: nb-deploy
description: "Ship, CI/CD, versioning, observability, and deprecation lifecycle."
metadata:
  phase: deploy
  strategy: merge
  tier: green
  composes:
    - shipping-and-launch
    - ci-cd-and-automation
    - git-workflow-and-versioning
    - observability-and-instrumentation
    - deprecation-and-migration
  nubo_version: "1.0.0"
---

# nb-deploy

## Purpose

Execute the full deployment lifecycle: shipping, CI/CD, versioning, observability setup, and deprecation planning.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Output the Completion Response when done.

## User Prompts

### Prompt: environment-confirmation
- **When:** Before deployment execution
- **Question:** "Deploy to {env}?"
- **Options:**
  - `deploy` -- Proceed with deployment
  - `dry-run` -- Run deployment dry-run only
  - `cancel` -- Cancel deployment
- **Default:** `deploy`
- **Blocks:** Deployment execution



## Context

Before starting, gather:
- The feature spec at `specs/{NNN}-{feature}/spec.md` (if available).
- Prior artifacts from earlier pipeline phases (plan, tasks, etc.).
- Project-level conventions and constitution at `.specify/memory/constitution.md`.


## Procedure

{CORE_TEMPLATE}

See references/ for shipping, CI/CD, git workflow, observability, and deprecation sub-procedures.

## Execution Model

**Parallel execution:** When the runtime supports subagents (Cursor Task tool, Claude Code subagents),
the following procedure steps MAY run in parallel:

| Step | Subagent | Scope |
|------|----------|-------|
| 5.1 Lint | deploy-lint | Changed files |
| 5.2 Test | deploy-test | Test suite |
| 5.3 Build | deploy-build | Release artifacts |

**Merge strategy:** Collect all subagent findings into the unified `findings` array.
Deduplicate by `location`. Highest severity wins on conflicts.

**Fallback:** If subagents are unavailable, run steps sequentially.


## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Deploy log | `specs/{NNN}-{feature}/deploy.md` | Deployment execution log |


## Completion Response

```json
{
  "command": "nb-deploy",
  "status": "success",
  "phase": "deploy",
  "artifacts": [
      {
          "path": "specs/{NNN}-{feature}/deploy.md",
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
### nb-deploy  |  SUCCESS
**Phase:** deploy  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `null`
---
