#!/bin/sh
# pre-push-maps-verify — refuse a push whose generated maps are stale. (SCC-290)
#
# WHY A SECOND LAYER AT ALL, when pre-commit-maps.sh already refreshes on every commit: because
# three commits never pass through it.
#
#   1. A MERGE COMMIT made on github.com. No local hook runs at all, so `main` can carry a stale
#      AUTO block the moment two lanes land.
#   2. `git commit --no-verify`. One flag, both gates skipped.
#   3. A tree whose hooks are not armed — `core.hooksPath` is LOCAL config, so a fresh clone has
#      no gates until someone sets it, per machine.
#
# This is the net under all three, and it is cheap: a regeneration in memory and a byte compare,
# ~0.2 s. It writes nothing — a hook that repaired the tree mid-push would create a commit the
# operator never made.
#
# ⛔ STDIN. pre-push is handed its refs on stdin and a stream is consumable exactly once; the
# dispatcher reads them into a file for the gates that need them. This gate needs NO refs — it is
# a statement about the tree, not about what is being pushed — so the dispatcher feeds it
# /dev/null and its stdin is never the shared one.
#
# Kill switch: .agents/scripts/git-hooks/DISABLE. Bypass once: git push --no-verify.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f scripts/git-hooks/DISABLE ] && exit 0
[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0

REFRESH=".agents/scripts/refresh_maps.py"
[ -f "$REFRESH" ] || exit 0

PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  printf '  ! pre-push-maps-verify: no python interpreter found - check skipped, push allowed.\n'
  exit 0
fi

if ! "$PY" "$REFRESH" --verify; then
  printf '\n'
  printf '  PUSH REFUSED - the generated maps do not match this tree.\n'
  printf '  Regenerate and commit them:\n'
  printf '      %s .agents/scripts/refresh_maps.py --repair\n' "$PY"
  printf '      git commit --amend --no-edit      # or a new commit, either is fine\n'
  printf '  Bypass once: git push --no-verify\n'
  printf '\n'
  exit 1
fi
exit 0
