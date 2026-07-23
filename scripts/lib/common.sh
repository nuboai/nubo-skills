#!/usr/bin/env bash
# Shared helpers for nubo-skills install/bootstrap scripts.

log()     { echo "==> $1" >&2; }
verbose() { [[ "${NUBO_SKILLS_VERBOSE:-false}" == true ]] && echo "    $1" >&2 || true; }
warn()    { echo "WARNING: $1" >&2; }
fail()    { echo "ERROR: $1" >&2; exit 1; }

require_tool() {
  command -v "$1" &>/dev/null || fail "$1 is required but not installed"
}

configure_git_auth() {
  local token="${NUBOAI_GITHUB_TOKEN:-${GITHUB_TOKEN:-}}"
  [[ -n "$token" ]] || return 0

  local instead_of="https://github.com/nuboai/"
  local rewrite="https://x-access-token:${token}@github.com/nuboai/"
  if ! git config --global --get-all url."${rewrite}".insteadOf 2>/dev/null | grep -qxF "$instead_of"; then
    git config --global url."${rewrite}".insteadOf "$instead_of"
    verbose "Configured git URL rewrite for github.com/nuboai/"
  fi
}

nubo_skills_repo_url() {
  printf '%s' "${NUBO_SKILLS_REPO:-https://github.com/nuboai/nubo-skills.git}"
}

nubo_skills_ref() {
  printf '%s' "${NUBO_SKILLS_REF:-master}"
}

nubo_skills_cache_dir() {
  printf '%s' "${NUBO_SKILLS_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/nubo-skills}"
}

resolve_target_dir() {
  local target="${1:-.}"
  local resolved
  resolved="$(cd "$target" && pwd)"
  printf '%s' "$resolved"
}

ensure_nubo_skills_checkout() {
  local ref cache repo
  ref="$(nubo_skills_ref)"
  cache="$(nubo_skills_cache_dir)"
  repo="$(nubo_skills_repo_url)"

  require_tool git
  configure_git_auth

  if [[ -d "$cache/.git" ]]; then
    verbose "Updating cached checkout at $cache (ref=$ref)"
    git -C "$cache" fetch --depth 1 origin "$ref"
    git -C "$cache" checkout --detach FETCH_HEAD
  else
    log "Cloning nubo-skills into $cache (ref=$ref)"
    mkdir -p "$(dirname "$cache")"
    if git clone --depth 1 --branch "$ref" "$repo" "$cache" 2>/dev/null; then
      :
    else
      rm -rf "$cache"
      git clone --depth 1 "$repo" "$cache"
      git -C "$cache" fetch --depth 1 origin "$ref"
      git -C "$cache" checkout --detach FETCH_HEAD
    fi
  fi

  [[ -f "$cache/registry.yml" ]] || fail "Checkout at $cache is missing registry.yml"
  printf '%s' "$cache"
}

can_access_nubo_skills_repo() {
  if command -v gh &>/dev/null && gh repo view nuboai/nubo-skills &>/dev/null; then
    return 0
  fi
  local repo
  repo="$(nubo_skills_repo_url)"
  git ls-remote --heads "$repo" "$(nubo_skills_ref)" &>/dev/null
}
