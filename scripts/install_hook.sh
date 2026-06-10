#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <HERMES_PROFILE_HOME>" >&2
  exit 1
fi

TARGET_HOME="$1"
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO_ROOT/hooks/telegram-mention-gate"
DST="$TARGET_HOME/hooks/telegram-mention-gate"

mkdir -p "$TARGET_HOME/hooks"
rm -rf "$DST"
cp -R "$SRC" "$DST"

echo "Installed telegram-mention-gate hook to: $DST"
echo "If needed, copy config.example.yaml to config.yaml and customize it."
