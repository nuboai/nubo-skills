#!/usr/bin/env bash
# Bootstrap nubo-skills into a target project (private-repo safe).
#
# Run from a local nubo-skills clone:
#   ./bootstrap.sh --target /path/to/project
#
# Remote bootstrap without cloning nubo-skills first (dev-workspace style):
#   gh api repos/nuboai/nubo-skills/contents/bootstrap.sh?ref=master \
#     --jq .content | base64 -d | bash -s -- --target /path/to/project
#
# Prerequisites: git, python3
# Private repo: gh auth login  OR  export NUBOAI_GITHUB_TOKEN=...
set -euo pipefail

NUBO_SKILLS_REPO="${NUBO_SKILLS_REPO:-https://github.com/nuboai/nubo-skills.git}"
NUBO_SKILLS_REF="${NUBO_SKILLS_REF:-master}"
NUBO_SKILLS_CACHE="${NUBO_SKILLS_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/nubo-skills}"

_configure_git_auth() {
  local token="${NUBOAI_GITHUB_TOKEN:-${GITHUB_TOKEN:-}}"
  [[ -n "$token" ]] || return 0
  git config --global url."https://x-access-token:${token}@github.com/nuboai/".insteadOf \
    "https://github.com/nuboai/" 2>/dev/null || true
}

_clone_to_cache() {
  _configure_git_auth
  if [[ -d "$NUBO_SKILLS_CACHE/.git" ]]; then
    git -C "$NUBO_SKILLS_CACHE" fetch --depth 1 origin "$NUBO_SKILLS_REF"
    git -C "$NUBO_SKILLS_CACHE" checkout --detach FETCH_HEAD
    return
  fi
  echo "==> Cloning nubo-skills (ref=$NUBO_SKILLS_REF) into $NUBO_SKILLS_CACHE"
  mkdir -p "$(dirname "$NUBO_SKILLS_CACHE")"
  if ! git clone --depth 1 --branch "$NUBO_SKILLS_REF" "$NUBO_SKILLS_REPO" "$NUBO_SKILLS_CACHE" 2>/dev/null; then
    rm -rf "$NUBO_SKILLS_CACHE"
    git clone --depth 1 "$NUBO_SKILLS_REPO" "$NUBO_SKILLS_CACHE"
    git -C "$NUBO_SKILLS_CACHE" fetch --depth 1 origin "$NUBO_SKILLS_REF"
    git -C "$NUBO_SKILLS_CACHE" checkout --detach FETCH_HEAD
  fi
}

# Piped via gh api / curl | bash — no local checkout yet.
if [[ -z "${BASH_SOURCE[0]:-}" || "${BASH_SOURCE[0]}" == "bash" ]]; then
  command -v git &>/dev/null || { echo "ERROR: git is required" >&2; exit 1; }
  _clone_to_cache
  exec bash "$NUBO_SKILLS_CACHE/scripts/bootstrap-target.sh" --source "$NUBO_SKILLS_CACHE" "$@"
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$ROOT/scripts/bootstrap-target.sh" --source "$ROOT" "$@"
