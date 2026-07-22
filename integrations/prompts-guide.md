# Agent Prompt Mapping Guide

Maps Nubo `## User Prompts` sections to agent-specific interactive APIs.

| Feature | Cursor | Claude Code | Codex CLI / others |
|---------|--------|-------------|-------------------|
| Structured prompts | `AskQuestion` tool with `options` array | `AskUserQuestion` tool | Plain text prompt with numbered options |
| Multi-select | `allow_multiple: true` | Multiple `AskUserQuestion` calls | Comma-separated numbers |
| Free-text fallback | Automatic "Other" option | Open-ended question | Default text input |

## Cursor Example

Use the `AskQuestion` tool:

```json
{
  "questions": [{
    "id": "spec-review",
    "prompt": "Approve this spec?",
    "options": [
      {"id": "approve", "label": "Finalize spec.md"},
      {"id": "revise", "label": "Revise spec based on feedback"}
    ]
  }]
}
```

## Claude Code Example

Use the `AskUserQuestion` tool with the same options structure.

## Generic Fallback

Present numbered options in plain text and wait for user response before proceeding to the gated Procedure step.
