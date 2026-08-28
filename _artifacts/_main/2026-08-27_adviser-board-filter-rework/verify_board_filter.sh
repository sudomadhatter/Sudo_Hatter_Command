#!/bin/bash
# SCC-340 — Adviser Board filter rework: machine-runnable acceptance assertions.
# Usage: verify_board_filter.sh <repo-root-to-check>
# Exit 0 = all assertions pass. Any failure prints FAIL lines and exits 1.
set -u
ROOT="${1:?usage: verify_board_filter.sh <repo-root>}"
cd "$ROOT" || { echo "FAIL: cannot cd $ROOT"; exit 1; }
rc=0

BRAIN=".agents/commands/smh-adviser-board.md"
FOLDER=".agents/commands/adviser-board"
AG=".agents/workflows/smh-adviser-board.md"
SKILL=".claude/skills/smh-adviser-board/SKILL.md"
OC=".opencode/commands/smh-adviser-board.md"

# ---------------------------------------------------------------- (c) vocabulary grep gate
# Retired vocabulary: triad, caucus, stage room, stage change, default triad,
# three minds, team (case-insensitive). 'floor' is adjudicated separately (plan §8.2).
# Justified exceptions live in the allowlist below (exact line content after the hit).
ALLOWED=(
  # (populated during GREEN if a justified exception survives — each with a reason)
)
pattern='triad|caucus|stage room|stage change|three minds|\bteam\b'
hits=$(grep -rinE "$pattern" "$BRAIN" "$FOLDER" "$AG" 2>/dev/null | grep -v "$FOLDER/minds/")
if [ -n "$hits" ]; then
  while IFS= read -r line; do
    keep=0
    for a in "${ALLOWED[@]:-}"; do
      [ -n "$a" ] && case "$line" in *"$a"*) keep=1;; esac
    done
    if [ "$keep" -eq 0 ]; then
      echo "FAIL(vocab): $line"
      rc=1
    fi
  done <<< "$hits"
fi
[ "$rc" -eq 0 ] && echo "PASS(vocab): zero unjustified retired-vocabulary hits"

# 'floor' — scoped adjudication: only floor-as-caucus-log / floors-to-file senses fail.
floor_hits=$(grep -rinE 'floor' "$BRAIN" "$FOLDER" "$AG" 2>/dev/null | grep -v "$FOLDER/minds/" \
  | grep -iE 'floor file|floors-to-file|floor-circulation|true of the floor|no floor|floor section|floor/card|the floor\b')
if [ -n "$floor_hits" ]; then
  echo "FAIL(floor): $floor_hits"
  rc=1
else
  echo "PASS(floor): no caucus-log sense of 'floor'"
fi

# ---------------------------------------------------------------- (d) door parity
# opencode mirror must be byte-identical to the brain.
if cmp -s "$BRAIN" "$OC"; then
  echo "PASS(door): opencode mirror byte-identical to brain"
else
  echo "FAIL(door): $OC differs from $BRAIN"
  rc=1
fi
# Claude skill launcher must embed the brain's frontmatter description verbatim.
brain_desc=$(awk '/^description:/{print substr($0,14); exit}' "$BRAIN")
skill_desc=$(awk '/^description:/{print substr($0,14); exit}' "$SKILL")
if [ -n "$brain_desc" ] && [ "$brain_desc" = "$skill_desc" ]; then
  echo "PASS(door): claude skill description matches brain description"
else
  echo "FAIL(door): claude skill description differs from brain description"
  rc=1
fi
# Antigravity launcher description within the ~135-char menu budget.
ag_desc=$(awk '/^description:/{print substr($0,14); exit}' "$AG")
ag_len=${#ag_desc}
if [ "$ag_len" -le 135 ] && [ "$ag_len" -gt 0 ]; then
  echo "PASS(door): AG launcher description ${ag_len} chars (budget 135)"
else
  echo "FAIL(door): AG launcher description ${ag_len} chars (budget 135)"
  rc=1
fi

exit "$rc"
