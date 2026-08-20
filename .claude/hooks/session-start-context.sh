#!/bin/sh
# session-start-context — inject home-base continuity + the standing gates at SessionStart.
#
# Ported from an inline PowerShell one-liner in `.claude/settings.json` (SCC-77). That version
# invoked `powershell`, which does not exist on the Mac, so it exited 127 in silence and this
# context was injected into exactly zero sessions on this machine. POSIX sh, no interpreter.
#
# Kept deliberately dumb: read files, print text, exit 0. A SessionStart hook must never block.

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] || exit 0
cd "$ROOT" || exit 0

echo "# Home-base continuity + gate (auto-injected at SessionStart)"

[ -f _artifacts/_main/active-context.md ] && cat _artifacts/_main/active-context.md

cat <<'EOF'

ARTIFACTS GATE: no edits outside _artifacts/ without an approved implementation_plan.md (see AGENTS.md section 3).

GIT: every commit-producing lane opens its own git worktree BEFORE editing files, and a fresh chat
resuming in-flight work RE-ENTERS the existing worktree (git worktree list) — never a second one and
never the shared checkout. Commit freely inside it: explicit paths, never `git add -A`.

  claude/<KEY>-<slug>   story  -> lands on its epic branch via /cicd-close-story-merge-tree
  chore/<KEY>-<slug>    task   -> lands on main via /smh-close-task-merge-tree
  epic/<KEY>-<slug>     epic   -> lands on main via /cicd-push-e2e

MAIN IS GATED, MECHANICALLY (SCC-77). `.githooks/pre-push` refuses any push landing on `main`
without a single-use approval token. Only /cicd-push-e2e and /smh-close-task-merge-tree mint one,
at their sign-off step; the operator's direct in-the-moment "approved" is the third door.
/cicd-close-story-merge-tree is NOT a main door — it lands on the epic branch.
One invocation authorises ONE merge and never carries forward (SCC-71). Merge-ready means STOP and
hand it back. Canonical table: .agents/rules/git-policy.md § "The write gate".
EOF

# Flight-recorder proposals (SCC-133): action-required recurrences across closed lanes, one line
# each, or nothing. The script is resolved from $ROOT first (works from EITHER copy of this hook -
# .agents/hooks/ or the generated .claude/hooks/ mirror), then beside this hook (so a test can
# point CLAUDE_PROJECT_DIR at a seeded temp repo and still run the real script). python3 on the
# Mac, python on the PC. `surface` always exits 0 and never blocks; nothing it prints is owed
# (SCC-160 - the operator's word mints). Output is captured so an empty ledger prints NOTHING.
HERE=$(cd "$(dirname "$0")" && pwd)
PY=$(command -v python3 || command -v python)
FR="$ROOT/.agents/scripts/flight_recorder.py"
[ -f "$FR" ] || FR="$HERE/../scripts/flight_recorder.py"
if [ -n "$PY" ] && [ -f "$FR" ]; then
  FR_OUT=$("$PY" "$FR" surface --repo "$ROOT" 2>/dev/null) || FR_OUT=""
  [ -n "$FR_OUT" ] && printf '\n%s\n' "$FR_OUT"
fi

if [ -f docs/repo-map.md ]; then
  echo ""
  echo "# Repo map (navigation index):"
  cat docs/repo-map.md
fi

exit 0
