#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <HERMES_PROFILE_HOME> [config-template-path]" >&2
  exit 1
fi

TARGET_HOME="$1"
USER_CONFIG_TEMPLATE="${2:-}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO_ROOT/hooks/telegram-mention-gate"
DST="$TARGET_HOME/hooks/telegram-mention-gate"
DEFAULT_TEMPLATE="$SRC/config.example.yaml"

mkdir -p "$TARGET_HOME/hooks"
rm -rf "$DST"
cp -R "$SRC" "$DST"

if [[ -n "$USER_CONFIG_TEMPLATE" ]]; then
  cp "$USER_CONFIG_TEMPLATE" "$DST/config.yaml"
  echo "Installed custom config template to: $DST/config.yaml"
elif [[ ! -f "$DST/config.yaml" ]]; then
  cp "$DEFAULT_TEMPLATE" "$DST/config.yaml"
  echo "Installed default config template to: $DST/config.yaml"
fi

echo "Installed telegram-mention-gate hook to: $DST"
echo "Edit $DST/config.yaml to adapt rules for any Hermes profile/bot deployment."
