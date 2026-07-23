# Skill governance review procedure

Review nubo-skills command definitions for structural and governance compliance.

1. Load `registry.yml` and compare each registered command to its on-disk `SKILL.md`.
2. Verify naming (`nb-{command}`), layer path, strategy, and `composes` alignment.
3. Check required sections for the command's strategy and output mode.
4. Confirm artifact paths follow `specs/{NNN}-{feature}/` conventions.
5. Record findings by severity in `specs/{NNN}-{feature}/skill-review.md`.

## Structural checks

For each registered command verify:

- Frontmatter `name`, `metadata.strategy`, `metadata.phase`, `metadata.tier`, and `metadata.composes` match `registry.yml`
- Required sections exist for the command layer and `generation.output_mode`
- `## Pipeline` declares exactly one successor or is terminal
- Linked `references/*.md` files exist, are substantive (not stubs), and have no orphans

## Reference quality checks

- Every markdown link to a file under `references/` resolves to a file with real procedure content
- No duplicate alias files shadowing canonical upstream-named references
- Sequence commands (`nb-review-arch`) delegate to valid SpecKit extension/preset commands

## Governance checks

- `tier`, `owner`, and `review_by` are present for every command
- `speckit-extension` composes include `extension_id`, `ref`, and `download_url`
- `speckit-preset` composes include `preset_id`, `path`, and `command`
- Hooks reference registered `nb.*` commands only

## Finding format

Record each issue with: `severity` (P0–P3), `category`, `command`, `location`, `message`, `recommendation`.
