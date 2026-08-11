#!/bin/sh
# post-commit-jira-start — the first commit on a keyed branch moves its ticket to
# `In Progress`. Once per branch, ever. (SCC-113)
#
# Why this exists: of the five transition seams in the toolkit, four wrote `Done` and exactly
# one wrote `In Progress` — the BMAD story lane. Every non-epic SCC ticket is a `Task`, so in
# the command centre nothing was ever visible as in flight: a chore/* lane sat in `To Do`
# while it was built, then teleported to `Done` at merge.
#
# ─── WHY THE TRIGGER IS A COMMIT, NOT A COMMAND ────────────────────────────────────────────
# /smh-quick-dev is not always run, and a fix that depends on remembering to run it re-creates
# the defect. Work provably starts when the first commit lands on a keyed branch — whatever
# path got there, including a bare `git commit` with no workflow at all. The command body
# calls `jira_feed.py start` too; neither layer is load-bearing alone, which is the point.
#
# ─── WHY post-commit AND NOT THE ARMED commit-msg GATE ──────────────────────────────────────
# commit-msg-jira.sh forbids growing itself, in its own header: "a live 'does AVCH-57 exist?'
# call would put a network round-trip on every commit and would fail closed on a plane."
# post-commit carries the opposite contract — it fires AFTER the commit is sealed, so it can
# never block or corrupt one, and every error is swallowed. A network call is safe HERE.
#
# ─── THE COST, AND WHY IT IS PAID ONCE ──────────────────────────────────────────────────────
# A marker under the git dir short-circuits every later commit before any network call. So
# this is ONE acli round-trip per branch, ever — not one per commit. The marker is written
# ONLY on success, so a commit made offline retries on the next one: self-healing by
# construction. (A failed call that wrote the marker anyway would silence the ticket forever.)
#
# Kill switch: create .agents/scripts/git-hooks/DISABLE (untracked) to turn it off entirely.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f scripts/git-hooks/DISABLE ] && exit 0
[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0

# ─── Which keys does THIS repo answer to? ──────────────────────────────────────────────────
# Same tracked declaration the armed commit-msg gate reads. A repo with no jira.conf has no
# board binding and therefore nothing to move — graceful degradation, not a failure.
JIRA_KEYS=""
[ -f .agents/jira.conf ] && . ./.agents/jira.conf
[ -n "$JIRA_KEYS" ] || exit 0

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || exit 0

# The three keyed prefixes (operator ruling 2026-08-11). `main` and any unkeyed spike branch
# fall straight through — there is no ticket to move and guessing one is how the wrong ticket
# gets decorated.
case "$BRANCH" in
  chore/*|claude/*|epic/*) ;;
  *) exit 0 ;;
esac

# ─── The key, from the branch name — never invented ────────────────────────────────────────
# <prefix>/<KEY>-<n>-<slug>. Matched against this repo's OWN declared projects, so a branch
# carrying another project's key is ignored rather than mis-filed.
REST=${BRANCH#*/}
KEY=""
for k in $JIRA_KEYS; do
  case "$REST" in
    "$k"-[0-9]*)
      num=${REST#"$k"-}
      num=${num%%-*}
      case "$num" in
        ''|*[!0-9]*) ;;
        *) KEY="$k-$num" ;;
      esac
      ;;
  esac
done
[ -n "$KEY" ] || exit 0

# ─── Once per BRANCH — not once per key ────────────────────────────────────────────────────
# --absolute-git-dir resolves per-worktree (.git/worktrees/<name>), so two lanes keep their
# own markers and neither silences the other.
#
# The marker is named for the BRANCH, and that is load-bearing: a key-named marker suppresses
# a SECOND branch carrying the same key, which is exactly what a re-opened ticket gets. A
# `Bug` flag moves a ticket Done -> To Do and the fix is cut as a fresh lane; a stale
# key-marker would leave it sitting in `To Do` for the whole rebuild. Re-firing costs
# nothing — `start` is idempotent.
GITDIR=$(git rev-parse --absolute-git-dir 2>/dev/null) || exit 0
SAFE=$(printf '%s' "$BRANCH" | tr '/' '-')
MARKER="$GITDIR/jira-started-$SAFE"
[ -f "$MARKER" ] && exit 0

# Same probe order as the two armed gates (SCC-49): python3 -> python -> py. The Mac has no
# bare `python`; the PC has no `python3`. Two probe orders in one repo is how they drift.
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || exit 0

# stdout passes through so a terminal shows the move; stderr is swallowed so an unreachable
# board is invisible. `start` is idempotent and refuses a `Done` key, so the worst case of a
# spurious run is a no-op.
if "$PY" .agents/scripts/jira_feed.py start --key "$KEY" --apply 2>/dev/null; then
  : > "$MARKER"
fi

# post-commit's contract: a broken recorder is invisible to your workflow. Never block.
exit 0
