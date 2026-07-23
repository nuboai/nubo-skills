#!/usr/bin/env bash
# Install or uninstall nubo-skills into a target project directory.
# Works with private github.com/nuboai/nubo-skills via gh auth or NUBOAI_GITHUB_TOKEN.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

TARGET_DIR="."
AGENTS="cursor-agent"
PHASES="all"
SOURCE_ROOT=""
CHECK_ONLY=false
UNINSTALL=false
TRY_BUNDLE=false
AUTO=false
SPECKIT=false

usage() {
  cat <<EOF
Usage: $0 [options]

Install governed nb-* skills and SpecKit artifacts into a target repository.
Uses a local nubo-skills checkout when available, otherwise clones into
\${NUBO_SKILLS_CACHE} with git credentials (private-repo safe).

Options:
  --target DIR       Project to install into (default: current directory)
  --agent AGENTS     Comma-separated agents (default: cursor-agent)
  --phases PHASES    Comma-separated phases or "all" (default: all)
  --auto             Install for all supported agents
  --ref REF          Git ref to clone when no --source (default: master or \$NUBO_SKILLS_REF)
  --source DIR       Use an existing nubo-skills checkout instead of cloning
  --try-bundle       Run "specify bundle install" first; fall back to install.sh on failure
  --speckit          Also bootstrap SpecKit extensions/presets into .specify/
  --check            Validate prerequisites and access; make no changes
  --uninstall        Remove artifacts installed by a previous bootstrap/install
  --verbose, -v      Verbose output
  -h, --help         Show this help

Environment:
  NUBO_SKILLS_REPO    Git URL (default: https://github.com/nuboai/nubo-skills.git)
  NUBO_SKILLS_REF     Git ref to install (default: master)
  NUBO_SKILLS_CACHE   Clone cache directory (default: ~/.cache/nubo-skills)
  NUBO_SKILLS_USE_CACHE  When true, clone into cache even if running from a local checkout
  NUBOAI_GITHUB_TOKEN Token for private github.com/nuboai/* clones (CI/agents)
  GITHUB_TOKEN        Alias for NUBOAI_GITHUB_TOKEN

Examples:
  $0 --target /path/to/nfx
  NUBO_SKILLS_REF=v1.0.1 $0 --target .
  $0 --source /path/to/nubo-skills --target /path/to/nfx --agent cursor-agent
EOF
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET_DIR="$2"; shift 2 ;;
    --agent) AGENTS="$2"; shift 2 ;;
    --phases) PHASES="$2"; shift 2 ;;
    --ref) export NUBO_SKILLS_REF="$2"; shift 2 ;;
    --source) SOURCE_ROOT="$2"; shift 2 ;;
    --auto) AUTO=true; shift ;;
    --try-bundle) TRY_BUNDLE=true; shift ;;
    --speckit) SPECKIT=true; shift ;;
    --check) CHECK_ONLY=true; shift ;;
    --uninstall) UNINSTALL=true; shift ;;
    --verbose|-v) export NUBO_SKILLS_VERBOSE=true; shift ;;
    -h|--help) usage 0 ;;
    *) echo "Unknown option: $1" >&2; usage 1 ;;
  esac
done

TARGET_DIR="$(resolve_target_dir "$TARGET_DIR")"
[[ -d "$TARGET_DIR" ]] || fail "Target directory does not exist: $TARGET_DIR"

resolve_source_root() {
  if [[ -n "$SOURCE_ROOT" ]]; then
    SOURCE_ROOT="$(cd "$SOURCE_ROOT" && pwd)"
    [[ -f "$SOURCE_ROOT/registry.yml" ]] || fail "--source is not a nubo-skills checkout: $SOURCE_ROOT"
    printf '%s' "$SOURCE_ROOT"
    return
  fi

  local candidate
  candidate="$(cd "$SCRIPT_DIR/.." && pwd)"
  if [[ "${NUBO_SKILLS_USE_CACHE:-}" != true ]] \
    && [[ -f "$candidate/registry.yml" && -f "$candidate/scripts/install.sh" ]]; then
    verbose "Using local checkout: $candidate"
    printf '%s' "$candidate"
    return
  fi

  ensure_nubo_skills_checkout
}

check_mode() {
  local source_root="$1"
  log "Checking bootstrap prerequisites"
  require_tool python3
  verbose "Target: $TARGET_DIR"
  verbose "Source: $source_root"
  verbose "Ref: $(nubo_skills_ref)"

  if ! can_access_nubo_skills_repo; then
    fail "Cannot access nuboai/nubo-skills. Run 'gh auth login' or set NUBOAI_GITHUB_TOKEN."
  fi

  [[ -x "$source_root/scripts/install.sh" ]] || fail "install.sh missing in $source_root"
  [[ -f "$source_root/registry.yml" ]] || fail "registry.yml missing in $source_root"

  if [[ -d "$TARGET_DIR/.specify" ]]; then
    verbose "Target has .specify/ — pass --speckit to refresh SpecKit extensions"
  else
    verbose "Default install is skills-only (.cursor/skills/)"
  fi

  if command -v specify &>/dev/null; then
    verbose "specify CLI: $(specify --version 2>/dev/null | head -1 || echo present)"
  else
    verbose "specify CLI: not installed (community extensions skipped)"
  fi

  log "Check passed"
}

try_bundle_install() {
  command -v specify &>/dev/null || return 1
  [[ -d "$TARGET_DIR/.specify" ]] || return 1

  local catalog_url="${NUBO_SKILLS_BUNDLE_CATALOG_URL:-https://raw.githubusercontent.com/nuboai/nubo-skills/master/bundles/catalog.json}"
  local catalog_id="${NUBO_SKILLS_BUNDLE_CATALOG_ID:-nubo-skills}"

  if [[ ! -f "$TARGET_DIR/.specify/bundle-catalogs.yml" ]] \
    || ! grep -q "$catalog_id" "$TARGET_DIR/.specify/bundle-catalogs.yml" 2>/dev/null; then
    verbose "Registering bundle catalog: $catalog_url"
    if ! (cd "$TARGET_DIR" && specify bundle catalog add "$catalog_url" --id "$catalog_id" 2>/dev/null); then
      warn "Could not register bundle catalog (private raw URL may 404)"
      return 1
    fi
  fi

  log "Trying specify bundle install nb-sdlc-full"
  if (cd "$TARGET_DIR" && specify bundle install nb-sdlc-full); then
    log "Installed via SpecKit bundle"
    return 0
  fi

  warn "specify bundle install failed — falling back to install.sh"
  return 1
}

main() {
  local source_root
  source_root="$(resolve_source_root)"

  if [[ "$CHECK_ONLY" == true ]]; then
    check_mode "$source_root"
    exit 0
  fi

  if [[ "$UNINSTALL" == true ]]; then
    log "Uninstalling from $TARGET_DIR"
    "$source_root/scripts/uninstall.sh" --target "$TARGET_DIR"
    exit 0
  fi

  check_mode "$source_root"

  if [[ "$TRY_BUNDLE" == true ]]; then
    (cd "$TARGET_DIR" && try_bundle_install) && exit 0
  fi

  log "Installing into $TARGET_DIR"
  local install_args=(--target "$TARGET_DIR" --phases "$PHASES")
  if [[ "$AUTO" == true ]]; then
    install_args+=(--auto)
  else
    install_args+=(--agent "$AGENTS")
  fi
  if [[ "$SPECKIT" == true ]]; then
    install_args+=(--speckit)
  fi

  "$source_root/scripts/install.sh" "${install_args[@]}"
  log "Bootstrap complete"
}

main "$@"
