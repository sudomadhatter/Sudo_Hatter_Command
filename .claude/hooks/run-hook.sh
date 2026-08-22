#!/bin/sh
# run-hook — the one seam between Claude Code's hook wiring and the scripts it runs.
#
# ─── The bug this exists to make impossible ────────────────────────────────────────────────
# Every hook in `.claude/settings.json` was wired as:
#     powershell -NoProfile -Command "python (Join-Path $env:CLAUDE_PROJECT_DIR '...')"
# This Mac has NEITHER `powershell` NOR `python` — only `pwsh` and `python3`. So all five hooks —
# the push-approval gate and four SessionStart hooks — exited **127, silently**, on every single
# invocation for weeks. Nothing surfaced, because a hook that fails to launch looks exactly like a
# hook with nothing to say. Six merges reached `main` on one sign-off because of it (SCC-71/SCC-77).
#
# Two rules follow, and this file enforces both:
#   1. NEVER name one platform's binary. Probe, in preference order, every time.
#   2. NEVER fail silently. No interpreter → say so on stdout and exit 0. A hook that cannot run
#      must announce it. Silence is reserved for a hook that ran and found nothing wrong.
#
# Usage:  sh .agents/hooks/run-hook.sh <script-path> [args...]
#         Dispatches on extension: .py -> python3|python|py   ·   .ps1 -> pwsh|powershell
#         <script-path> is relative to CLAUDE_PROJECT_DIR (or the repo root if that is unset).
#
# ⚠ This is the CLAUDE-ONLY layer, and nothing depends on it. The `main` write gate is
# `.githooks/pre-push` (pure sh, no interpreter at all) precisely so that a repeat of the 127 bug
# degrades the prompt, never the gate. See `.agents/rules/git-policy.md` § "The write gate".

SCRIPT="$1"
[ -n "$SCRIPT" ] || { echo "[hook] run-hook.sh: no script given"; exit 0; }
shift

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] || ROOT="."

case "$SCRIPT" in
  /*) TARGET="$SCRIPT" ;;
  *)  TARGET="$ROOT/$SCRIPT" ;;
esac

if [ ! -f "$TARGET" ]; then
  echo "[hook] $SCRIPT not found — skipped."
  exit 0
fi

case "$SCRIPT" in
  *.py)  CANDIDATES="python3 python py" ;;
  *.ps1) CANDIDATES="pwsh powershell" ;;   # pwsh FIRST: it is the cross-platform one
  *)     echo "[hook] $SCRIPT: unknown script type — skipped."; exit 0 ;;
esac

RUNNER=""
for c in $CANDIDATES; do
  if command -v "$c" >/dev/null 2>&1; then RUNNER="$c"; break; fi
done

if [ -z "$RUNNER" ]; then
  echo "[hook] $SCRIPT needs one of: $CANDIDATES — none found on this machine. Hook SKIPPED."
  echo "       (This message is the fix for the silent exit-127 class of bug. SCC-77.)"
  exit 0
fi

cd "$ROOT" || exit 0
exec "$RUNNER" "$TARGET" "$@"
