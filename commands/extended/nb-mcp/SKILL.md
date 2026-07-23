---
name: nb-mcp
description: "Build MCP servers and tools following best practices."
metadata:
  phase: implement
  strategy: standalone
  tier: green
  composes:
    - mcp-builder
  nubo_version: "1.0.0"
---

# nb-mcp

## Purpose

Build MCP servers and tools following MCP SDK conventions and best practices.

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
| MCP implementation | `{project-specific}` | MCP server/tool source files |


## Completion Response

```json
{
  "command": "nb-mcp",
  "status": "success",
  "phase": "implement",
  "artifacts": [
      {
          "path": "{project-specific}",
          "action": "created",
          "lines": 0
      }
  ],

  "metrics": {
    "duration_s": 0,
    "files_read": 0,
    "files_written": 0
  },
  "next_command": "nb-review-code",
  "message": "<human-readable summary>"
}
```

After emitting the JSON, render the visual summary block:

---
### nb-mcp  |  SUCCESS
**Phase:** implement  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `nb-review-code`
---
