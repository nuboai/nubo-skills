# Convergence Procedure (Nubo-local until SpecKit ships converge command)

Iterate between implementation and analysis until spec and code converge.

1. Run gap analysis against the feature spec (`nb-analyze` or equivalent).
2. Identify unresolved gaps and classify by severity (P0–P3).
3. Generate fix tasks for P0–P1 gaps and route back to implementation.
4. Re-implement and re-analyze until convergence criteria are met.
5. Document each iteration in `specs/{NNN}-{feature}/convergence.md`.

## Convergence criteria

Declare **CONVERGED** only when all of the following hold:

- No open P0 or P1 gaps in the latest analysis
- Remaining P2+ gaps are explicitly accepted as documented deviations
- Latest analysis artifact exists and is referenced in the convergence log

Declare **NOT CONVERGED** when any P0/P1 gap remains or when analysis was skipped.

## Iteration limits

- After **5 iterations** without reducing the P0+P1 count, stop and escalate with a summary of blocking gaps.
- Do not loop indefinitely on the same unresolved finding without a changed approach.

## Artifact rules

- `convergence.md` records **status only** (`CONVERGED` / `NOT CONVERGED`), iteration history, gates, and accepted deviations.
- Do **not** write `Next command`, `proceed to`, or pipeline routing in `convergence.md` or other feature artifacts — routing lives in each command's `## Pipeline` section.
- If a later pipeline artifact already exists (e.g. `checklist.md` is SHIP), note that status in the iteration log; do not skip ahead to a later command in summaries.

## Iteration log format

Each iteration entry must include:

- Iteration number and date
- Analysis source (`analysis.md` path or summary)
- Gaps found by severity
- Fixes applied or tasks created
- Gate result (`CONVERGED` / `NOT CONVERGED` for that iteration)
