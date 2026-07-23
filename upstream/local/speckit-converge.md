# Convergence Procedure (Nubo-local until SpecKit ships converge command)

Iterate between implementation and analysis until spec and code converge.

1. Run gap analysis against the feature spec.
2. Identify unresolved gaps and classify by severity.
3. Generate fix tasks for P0-P1 gaps.
4. Re-implement and re-analyze until no P0-P1 gaps remain.
5. Document convergence history in `specs/{NNN}-{feature}/convergence.md`.

## Artifact rules

- `convergence.md` records **status only** (`CONVERGED` / `NOT CONVERGED`), iteration history, gates, and accepted deviations.
- Do **not** write `Next command`, `proceed to`, or pipeline routing in `convergence.md` or other feature artifacts — routing lives in each command's `## Pipeline` section.
- If a later pipeline artifact already exists (e.g. `checklist.md` is SHIP), note that status in the iteration log; do not skip ahead to a later command in summaries.
