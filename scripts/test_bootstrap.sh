#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
CACHE="$(mktemp -d)"
trap 'rm -rf "$TMP" "$CACHE"' EXIT

cd "$ROOT"
chmod +x bootstrap.sh scripts/*.sh scripts/lib/common.sh

echo "==> bootstrap-target with --source (local checkout)"
./scripts/bootstrap-target.sh --source "$ROOT" --target "$TMP" --agent cursor-agent

count="$(ls -1d "$TMP/.cursor/skills"/nb-* 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$count" != "19" ]]; then
  echo "FAIL: expected 19 cursor skills, got $count" >&2
  exit 1
fi

echo "==> bootstrap-target --check"
./scripts/bootstrap-target.sh --source "$ROOT" --target "$TMP" --check

echo "==> bootstrap-target --uninstall"
./scripts/bootstrap-target.sh --source "$ROOT" --target "$TMP" --uninstall

if [[ -e "$TMP/.cursor/skills" ]] || [[ -f "$TMP/.nubo-skills.state.json" ]]; then
  echo "FAIL: uninstall left artifacts behind" >&2
  exit 1
fi

echo "==> bootstrap.sh entrypoint (local)"
./bootstrap.sh --target "$TMP" --agent cursor-agent

count="$(ls -1d "$TMP/.cursor/skills"/nb-* 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$count" != "19" ]]; then
  echo "FAIL: bootstrap.sh expected 19 skills, got $count" >&2
  exit 1
fi

echo "==> bootstrap-target via cache clone"
rm -rf "$TMP/.cursor" "$TMP/.nubo-skills.state.json" "$CACHE" 2>/dev/null || true
mkdir -p "$CACHE"
NUBO_SKILLS_USE_CACHE=true \
NUBO_SKILLS_CACHE="$CACHE/checkout" \
NUBO_SKILLS_REPO="file://${ROOT}" \
NUBO_SKILLS_REF="$(git -C "$ROOT" rev-parse HEAD)" \
  bash -c 'cd /tmp && "'"$ROOT"'/scripts/bootstrap-target.sh" --target "'"$TMP"'" --agent cursor-agent'

count="$(ls -1d "$TMP/.cursor/skills"/nb-* 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$count" != "19" ]]; then
  echo "FAIL: cache bootstrap expected 19 skills, got $count" >&2
  exit 1
fi

echo "OK: bootstrap smoke tests passed"
