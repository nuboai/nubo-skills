---
name: nb-debug
description: "Debug failures and recover from errors reactively."
metadata:
  phase: utilities
  strategy: utility
  tier: green
  composes:
    - debugging-and-error-recovery
  nubo_version: "1.0.0"
  read_only: false
---

# nb-debug

## Purpose

Diagnose test failures, runtime errors, and unexpected behavior. Reactive utility — not a pipeline command.

## Conventions

- Output the Completion Response when done.




## Procedure

{CORE_TEMPLATE}



## Completion Response

```json
{
  "command": "nb-debug",
  "status": "success",
  "phase": "utilities",
  "artifacts": [],

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
### nb-debug  |  SUCCESS
**Phase:** utilities  |  **Duration:** 0s  |  **Files:** 0 read, 0 written

**Next:** `null`
---
