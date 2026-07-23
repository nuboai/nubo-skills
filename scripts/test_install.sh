#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cd "$ROOT"
chmod +x scripts/install.sh scripts/uninstall.sh

echo "==> install cursor-agent only"
./scripts/install.sh --agent cursor-agent --target "$TMP"

agents="$(python3 -c "import json; print(json.load(open('$TMP/.nubo-skills.state.json'))['agents'])")"
if [[ "$agents" != "['cursor-agent']" ]]; then
  echo "FAIL: expected only cursor-agent, got $agents" >&2
  exit 1
fi

count="$(ls -1d "$TMP/.cursor/skills"/nb-* 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$count" != "19" ]]; then
  echo "FAIL: expected 19 cursor skills, got $count" >&2
  exit 1
fi

for stray in .claude .agents .gemini .devin .github/skills; do
  if [[ -e "$TMP/$stray" ]]; then
    echo "FAIL: unexpected agent path $stray" >&2
    exit 1
  fi
done

if [[ ! -f "$TMP/.cursor/rules/nubo-governance.md" ]]; then
  echo "FAIL: missing cursor governance file" >&2
  exit 1
fi

echo "==> uninstall"
./scripts/uninstall.sh --target "$TMP"

if [[ -e "$TMP/.cursor/skills" ]] || [[ -f "$TMP/.nubo-skills.state.json" ]]; then
  echo "FAIL: uninstall left artifacts behind" >&2
  exit 1
fi

echo "OK: install/uninstall smoke test passed"
