#!/bin/sh
# pre-commit-maps — regenerate the generated maps and stage them with the commit. (SCC-290)
#
# `docs/repo-map.md`'s AUTO block and `docs/doc-graph.*` are machine-generated, and nothing
# regenerated them between manual runs of `/smh-update-maps-indexes` — so they were stale almost
# always, and a stale map is worse than no map because it is read as current. This delegate makes
# the GENERATED layer self-refreshing on every commit. The CURATED layer (one-line purposes, INDEX
# prose, the AGENTS.md pointers) is still the ceremony's, because a hook cannot write prose.
#
# It also runs the two truth checks refresh_maps.py owns — the broken-reference RATCHET and the
# "every house door is named in the SOP" REVERSE check — and refuses the commit on either.
#
# Kill switch: create .agents/scripts/git-hooks/DISABLE (untracked). Bypass once: --no-verify.
# Both are honoured inside refresh_maps.py, so this file stays a launcher and the policy lives in
# one place.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT" || exit 0

[ -f scripts/git-hooks/DISABLE ] && exit 0
[ -f .agents/scripts/git-hooks/DISABLE ] && exit 0

# The script lives in the toolkit; a repo without it simply has no maps refresh.
REFRESH=".agents/scripts/refresh_maps.py"
[ -f "$REFRESH" ] || exit 0

# Probe, never assume — the SAME order as pre-commit-encoding.sh and sop-currency.sh, or the
# gates disagree about which machines they run on (SCC-49). The Mac has only `python3`, a
# python.org PC has only `python`, and `py` is the Windows launcher.
PY=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  printf '  ! pre-commit-maps: no python interpreter found - maps not refreshed, commit allowed.\n'
  exit 0
fi

"$PY" "$REFRESH" --staged
exit $?
