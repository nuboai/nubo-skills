---
name: nb-pimcore
description: "Pimcore MDM and syndication development patterns (vendor example)."
metadata:
  phase: implement
  strategy: standalone
  tier: amber
  composes:
    - pimcore-mdm
  nubo_version: "1.0.0"
---

# nb-pimcore

## Purpose

Vendor-specific example command for Pimcore MDM development. Project-opt-in — not part of the default catalog.

## Conventions

- Work in `specs/{NNN}-{feature}/` for all artifacts.
- Follow Nubo naming conventions for generated files.
- Output the Completion Response when done.

## Context

Before starting, gather:
- Pimcore project configuration and data model definitions.
- Feature spec at `specs/{NNN}-{feature}/spec.md`.

## Procedure

{CORE_TEMPLATE}

## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Implementation | `{project-specific}` | Pimcore-specific source files |

## Completion Response

```json
{
  "command": "nb-pimcore",
  "status": "success",
  "phase": "implement",
  "artifacts": [],
  "metrics": { "duration_s": 0, "files_read": 0, "files_written": 0 },
  "next_command": "nb-review-code",
  "message": "<human-readable summary>"
}
```
