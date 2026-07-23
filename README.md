# nubo-skills

Governed skill registry for Nubo development teams. **nubo-skills** is the single source of truth for every agent skill consumed across the SDLC. Upstream skills (SpecKit, addyosmani, anthropics, trailofbits, vendor) are composed into unified `nb-{command}` commands with version pinning, integrity tracking, validation, and SpecKit-native workflow orchestration.

Projects should not install upstream skills directly. Depend on this repo instead.

## Features

- **19 governed commands** — 9 core, 9 extended, 1 utility, all in [agentskills.io](https://agentskills.io) layout (`nb-{command}/SKILL.md`)
- **8 scenario workflows** — greenfield, feature pipeline, brownfield onboarding, hotfix, review-only, security audit, docs catch-up, architecture alignment
- **3 methodology presets** — conventions, TDD, frontend
- **Version pinning** — `registry.yml` declares upstream refs; `nubo-skills.lock` records SHA256 hashes
- **Agent-agnostic distribution** — SpecKit bundle (primary) or fallback `install.sh` for Cursor, Claude, Codex, Gemini, Copilot, Devin
- **CI validation** — 14 automated checks plus optional SkillSpector security scanning

## Quick start

### SpecKit projects (primary)

Install the full SDLC bundle:

```bash
specify bundle install nb-sdlc-full
```

Run a scenario workflow:

```bash
specify workflow run nb-greenfield
specify workflow run nb-feature-pipeline
```

Invoke a single command:

```bash
/nb.nb-specify
/nb.nb-plan
/nb.nb-implement
```

### Non-SpecKit projects (fallback)

Clone with submodules, then use the fallback installer:

```bash
git clone --recurse-submodules https://github.com/nuboai/nubo-skills.git
cd nubo-skills
pip install -r requirements.txt

# Install all commands for Cursor
./scripts/install.sh --agent cursor-agent

# Install specific phases only
./scripts/install.sh --agent cursor-agent --phases specify,plan,implement

# Auto-detect all supported agents
./scripts/install.sh --auto
```

## Commands

All commands live under `commands/{core,extended,utilities}/nb-{command}/SKILL.md`.

### Core (SpecKit wrap)

| Command | Phase | Description |
|---------|-------|-------------|
| `nb-constitution` | constitution | Project principles and constraints |
| `nb-specify` | specify | Feature specification from requirements |
| `nb-clarify` | clarify | Resolve ambiguities in a spec |
| `nb-plan` | plan | Technical implementation plan |
| `nb-tasks` | tasks | Break plan into actionable tasks |
| `nb-implement` | implement | Execute tasks and produce code |
| `nb-analyze` | analyze | Cross-artifact consistency analysis |
| `nb-converge` | converge | Reconcile divergent artifacts |
| `nb-checklist` | checklist | Quality gate checklist |

### Extended (merged upstream skills)

| Command | Phase | Upstream sources |
|---------|-------|------------------|
| `nb-interview` | specify | addyosmani (interview-me, idea-refine) |
| `nb-review-code` | review | addyosmani (code-review, simplification, perf) |
| `nb-review-security` | review | addyosmani + trailofbits (semgrep) |
| `nb-review-arch` | review | SpecKit extensions (architecture-guard, architect-preview, spec-kit-arch) |
| `nb-test` | test | addyosmani (testing) |
| `nb-deploy` | deploy | addyosmani (shipping, CI/CD, observability, git, deprecation) |
| `nb-mcp` | implement | anthropics (mcp-builder) |
| `nb-docs` | docs | addyosmani (documentation) |
| `nb-review-skill` | review | SkillSpector governance scan |

### Utility

| Command | Phase | Description |
|---------|-------|-------------|
| `nb-debug` | debug | Systematic debugging with minimal scope |

## Workflows

Scenario workflows orchestrate commands with gates and prompts. See `workflows/registry.yml` for when to use each.

| Workflow | Scenario | Entry |
|----------|----------|-------|
| `nb-greenfield` | New repo, no SDD artifacts | `specify workflow run nb-greenfield` |
| `nb-feature-pipeline` | SDD-ready project, next feature | `specify workflow run nb-feature-pipeline` |
| `nb-brownfield-onboard` | Existing code, adopt governance | `specify workflow run nb-brownfield-onboard` |
| `nb-hotfix` | Small scoped fix | `specify workflow run nb-hotfix` |
| `nb-review-only` | Review pass without implementation | `specify workflow run nb-review-only` |
| `nb-security-audit` | Security audit or pre-release hardening | `specify workflow run nb-security-audit` |
| `nb-docs-catchup` | Document existing codebase | `specify workflow run nb-docs-catchup` |
| `nb-arch-alignment` | Fix architecture drift | `specify workflow run nb-arch-alignment` |

## Presets

Methodology presets inject additional guidance into commands via SpecKit composition:

| Preset | Strategy | Effect |
|--------|----------|--------|
| `nb-conventions` | wrap (priority 50) | Nubo naming, v2 completion response, context-engineering |
| `nb-tdd` | merge into `nb-implement` | Test-driven development practices |
| `nb-frontend` | merge into `nb-implement` | Frontend design and component patterns |

## Repository structure

```
nubo-skills/
├── registry.yml              # Command catalog, composition, hooks, presets
├── nubo-skills.lock          # Pinned SHA256 hashes (generated)
├── bundle.yml                # SpecKit bundle definition (nb-sdlc-full)
├── commands/
│   ├── core/                 # 9 SpecKit-wrapped commands
│   ├── extended/             # 9 merged upstream commands
│   └── utilities/            # nb-debug
├── presets/                  # nb-conventions, nb-tdd, nb-frontend
├── workflows/                # 8 scenario YAML workflows + registry
├── scripts/
│   ├── validate.sh           # 14 validation checks
│   ├── sync-upstream.sh      # Regenerate lock file
│   ├── upgrade.sh            # Bump upstream ref + sync + validate
│   ├── install.sh            # Fallback agent installer
│   └── generate_skills.py    # Regenerate SKILL.md templates
├── integrations/
│   ├── agents.yml            # Agent discovery paths
│   ├── prompts-guide.md      # User prompt conventions
│   └── context-files/        # Per-agent governance context
├── upstream/                 # Git submodules + local stubs
└── examples/vendor/          # Vendor command example (nb-pimcore)
```

## Development

### Prerequisites

```bash
pip install -r requirements.txt
git submodule update --init --recursive
```

### Validate

```bash
./scripts/validate.sh
```

Runs 14 checks: naming conventions, layer paths, completion contract, registry consistency, hook wiring, workflow validity, bundle integrity, frontmatter schema, and progressive disclosure rules.

### Sync upstream and regenerate lock file

```bash
./scripts/sync-upstream.sh
```

### Upgrade an upstream dependency

```bash
./scripts/upgrade.sh <command> <upstream_name> <new_ref>

# Example
./scripts/upgrade.sh nb-review-code code-review-and-quality fefc408
```

### Regenerate command templates

```bash
python3 scripts/generate_skills.py
```

## Upstream sources

| Source | Submodule | Pinned ref |
|--------|-----------|------------|
| [github/spec-kit](https://github.com/github/spec-kit) | `upstream/speckit` | v0.9.5 |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `upstream/addyosmani` | fefc407 |
| [anthropics/skills](https://github.com/anthropics/skills) | `upstream/anthropics` | pinned commit |
| [trailofbits/skills](https://github.com/trailofbits/skills) | `upstream/trailofbits` | cfe5d7b |

Local stubs in `upstream/local/` cover upstream gaps (e.g. `speckit-converge`, `frontend-design`).

## Governance model

Each command in `registry.yml` declares:

- **layer** — `core`, `extended`, or `utility`
- **tier** — `green` (approved), `amber` (review required), `red` (restricted)
- **owner** — responsible team
- **composes** — upstream sources with pinned refs
- **review_by** — deprecation or re-review date

Composition strategies:

| Strategy | Used by | Behavior |
|----------|---------|----------|
| wrap | Core commands | Nubo governance injected around SpecKit template |
| merge | Extended commands | Multiple upstream skills combined into one command |
| sequence | `nb-review-arch` | Sub-skills run in defined order |
| standalone | `nb-mcp`, `nb-docs`, `nb-review-skill` | Single upstream, no merge |
| utility | `nb-debug` | Standalone debugging command |

## Completion response protocol

Every command emits a v2 completion response when finished:

```json
{
  "status": "complete",
  "command": "nb-specify",
  "artifacts": ["specs/001-feature/spec.md"],
  "metrics": { "files_created": 1 },
  "next_command": "nb-clarify",
  "findings": []
}
```

Followed by a visual summary markdown block. See any `commands/*/SKILL.md` for the full contract.

## Adding a vendor command

1. Add upstream source under `upstream/vendor/` or `examples/vendor/`
2. Register in `registry.yml` with `composes` entry
3. Create `commands/{layer}/nb-{command}/SKILL.md`
4. Run `./scripts/validate.sh` and `./scripts/sync-upstream.sh`
5. Open a PR — CI must pass

See `examples/vendor/nb-pimcore/` for a reference implementation.

## CI

GitHub Actions runs on every push and pull request:

- **validate** — `./scripts/validate.sh` (required)
- **skillspector** — security scan of `commands/` with SARIF output (informational)

## License

Internal Nubo repository. Upstream skills retain their original licenses (see respective submodule repos).
