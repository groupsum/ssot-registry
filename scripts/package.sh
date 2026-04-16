#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-ssot-registry}"

if [[ -d "$TARGET" ]]; then
  PROJECT_PATH="$TARGET"
else
  PROJECT_PATH="pkgs/$TARGET"
fi

if [[ ! -f "$PROJECT_PATH/pyproject.toml" ]]; then
  echo "Unknown package target: $TARGET" >&2
  exit 1
fi

uv build --project "$PROJECT_PATH"
