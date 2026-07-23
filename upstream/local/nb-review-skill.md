# Skill governance review procedure

Review nubo-skills command definitions for structural and governance compliance.

1. Load `registry.yml` and compare each registered command to its on-disk `SKILL.md`.
2. Verify naming (`nb-{command}`), layer path, strategy, and `composes` alignment.
3. Check required sections for the command's strategy and output mode.
4. Confirm artifact paths follow `specs/{NNN}-{feature}/` conventions.
5. Record findings by severity in `specs/{NNN}-{feature}/skill-review.md`.
