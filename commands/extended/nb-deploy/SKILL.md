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
- Pipeline routing belongs only in each command's `## Pipeline` section — never write `Next command` or `proceed to` in feature artifacts.

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

Follow each sub-procedure below and combine outputs into the command artifacts.

1. [Shipping And Launch](references/shipping-and-launch.md)
2. [Ci Cd And Automation](references/ci-cd-and-automation.md)
3. [Git Workflow And Versioning](references/git-workflow-and-versioning.md)
4. [Observability And Instrumentation](references/observability-and-instrumentation.md)
5. [Deprecation And Migration](references/deprecation-and-migration.md)

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


## Pipeline

**Terminal command** — no pipeline successor.


