# Vendor Upstreams

Project-specific vendor skills are added here as git submodules.

## Example: Pimcore

```bash
git submodule add https://github.com/pimcore/skills.git upstream/vendor/pimcore
```

Then create a composed command following the `nb-{command}` convention:

```
commands/extended/nb-pimcore/
  SKILL.md
```

Register in `registry.yml` with `tier: amber` and project-specific `owner`.

See `examples/vendor/nb-pimcore/` for a reference template (not part of the default 19-command catalog).
