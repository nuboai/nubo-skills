# Architecture Contract Steps

Operational guide for step 3 of `nb-review-arch`. Full extension contract:
`.specify/extensions/arch/commands/speckit.arch.full-generate.md`.

## Delegate command

`/speckit.arch.full-generate`

Use the full forward-generation workflow to validate or refresh the planning contract.

## Mode

Writes architecture memory only. Allowed targets:
`.specify/memory/architecture*.md` (views and synthesis). Do not modify feature
specs, plans, tasks, or source code.

## Inputs

- Validated findings from steps 1–2
- Feature context from `specs/{NNN}-{feature}/`
- Existing architecture memory under `.specify/memory/`

## Outputs to capture

- Updated `.specify/memory/architecture.md` synthesis (when validator passes)
- View-level gaps recorded explicitly when evidence is insufficient
- Validator `ready_gate` result and blocker codes

## Merge into `arch-review.md`

Add a **Contract validation** section. Record whether the contract was refreshed,
which views changed, synthesis readiness, and any gaps blocking refresh.

Respect the user prompt from `nb-review-arch`: only write contract updates when
`apply-updates` is selected; otherwise report findings only.
