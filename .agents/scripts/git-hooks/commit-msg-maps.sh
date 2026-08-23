#!/bin/sh
# commit-msg-maps — the two maps TRUTH checks, which need to see the commit message. (SCC-290)
#
#   RATCHET       the count of broken doc references may not RISE above what it is at HEAD.
#   REVERSE DOOR  every house door in .agents/commands/ must be named in the operator's SOP.
#
# The why, the checks, and the escape hatch all live in one place:
#   .agents/scripts/refresh_maps.py --truth
# This file is only the shell seam between git and that script. Keep it dumb.
#
# ⛔ IT RUNS FROM commit-msg AND NOT pre-commit FOR EXACTLY ONE REASON, the same one written into
# sop-currency.sh's header: the escape hatch is a token in the COMMIT MESSAGE ([maps-ok]), and
# pre-commit cannot see the message. The regeneration half still runs at pre-commit — it has to,
# because it stages files.
#
# That hatch is not decoration. The ratchet refused the very commit that introduced it (52 -> 77
# broken refs) because that commit WIDENED THE GRAPH'S SCOPE onto docs/, so the before and after
# numbers were not measurements of the same thing. Any future root addition does it again.
# [maps-ok] stays in the log forever, which is the design: a silent bypass teaches nothing.
#
# Kill switch: .agents/scripts/git-hooks/DISABLE   (same file the other gates honor)
# Bypass once: git commit --no-verify

MSG_FILE="$1"
[ -n "$MSG_FILE" ] || exit 0

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f scripts/git-hooks/DISABLE ] && exit 0
[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0

REFRESH=".agents/scripts/refresh_maps.py"
[ -f "$REFRESH" ] || exit 0

# A MERGE writes its own message and has no author to answer for the content — the other two
# gates on this hook carve merges out for the same reason, and a merge's maps are covered by the
# pre-push verify instead.
if [ -f "$(git rev-parse --git-path MERGE_HEAD 2>/dev/null)" ]; then
  exit 0
fi

# Probe, never assume — the SAME order as sop-currency.sh and pre-commit-encoding.sh (SCC-49).
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  printf '  ! commit-msg-maps: no python interpreter found - checks skipped, commit allowed.\n'
  exit 0
fi

"$PY" "$REFRESH" --truth "$MSG_FILE"
exit $?
