#!/usr/bin/env bash
# install-git-hooks.sh — Arm and verify Git hooks across all repositories (SCC-115).
#
# Usage:
#   bash docs/migrations/scripts/install-git-hooks.sh
#   bash docs/migrations/scripts/install-git-hooks.sh --verify-only
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

PY=""
for cand in python3 python py; do
    if command -v "$cand" >/dev/null 2>&1; then
        PY="$cand"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "ERROR: Python 3 is required but was not found on PATH." >&2
    exit 1
fi

exec "$PY" "${SCRIPT_DIR}/install_git_hooks.py" --root "${ROOT_DIR}" "$@"
