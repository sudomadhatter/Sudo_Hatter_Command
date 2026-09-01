#!/usr/bin/env bash
# SCC-205 - the acceptance assertions for Parts B, C and E, as one scripted pass.
# Every row reads a file through `src`, so the SAME rows can be run against the PRE-EDIT
# blobs (`--red <ref>`) to prove each one actually failed before the edit. A check that was
# never seen red is not a gate, it is a description.
LOBBY="$(cd "$(dirname "$0")/../../.." && pwd)"
REF=""
[ "$1" = "--red" ] && REF="$2"
src() { if [ -n "$REF" ]; then git -C "$LOBBY" show "$REF:$1" 2>/dev/null; else cat "$LOBBY/$1"; fi; }
fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS | $1"; else echo "FAIL | $1  (got '$2', want '$3')"; fail=1; fi; }
# ⛔ PRESENCE, not a count. A row keyed on an exact tally reds the day someone states the same
# law twice on purpose - which is what C1b and E4 did on their first run. Count only where the
# number IS the assertion (there must be exactly ONE rules-in-force block, not two).
atleast() { if [ "$2" -ge "$3" ] 2>/dev/null; then echo "PASS | $1"; else echo "FAIL | $1  (got '$2', want >= '$3')"; fail=1; fi; }

CR=.agents/commands/cicd-code-review.md
SA=.agents/commands/cicd-self-audit.md
QD=.agents/commands/cicd-quick-dev.md
CC=.agents/commands/cicd-clean-code-audit.md
SC=.agents/commands/smh-clean-code-audit.md

# ── Part B - the vehicle ───────────────────────────────────────────────────────
chk "B1 cicd-code-review carries a rules-in-force block" \
    "$(src $CR | grep -c 'Rules in force for this command')" "1"
chk "B2 cicd-self-audit carries a rules-in-force block" \
    "$(src $SA | grep -c 'Rules in force for this command')" "1"

# ── Part C - the safety defects ────────────────────────────────────────────────
chk "C1 no same-session main merge language in cicd-quick-dev" \
    "$(src $QD | grep -c 'merged back to .main. in the same')" "0"
atleast "C1b the real door is named" \
    "$(src $QD | grep -c 'smh-close-task-merge-tree')" "1"
chk "C2 the no-worktree instruction is gone" \
    "$(src $QD | grep -cE '^.*branch off .main., no worktree')" "0"
chk "C3 a fired eject re-arms the plan-first gate" \
    "$(src $QD | grep -c 'RE-ARMS the plan-first gate')" "1"
chk "C4 the review routes through the house engine" \
    "$(src $QD | grep -c 'code-review-engine')" "1"
chk "C4b lens_budget is named explicitly" \
    "$(src $QD | grep -c 'lens_budget')" "1"
chk "C5 the Dev Record no longer invites a free-text slug" \
    "$(src $QD | grep -c 'story <id-or-slug>')" "0"

# ── Part E - the hoists: rule AND restatement, never a pointer alone ───────────
atleast "E1 the three-question disposition test resolves from a rule" \
    "$(src .agents/rules/code-standards.md | grep -ci 'change BEHAVIOUR')" "1"
atleast "E1b ...and is restated inline in an audit command" \
    "$(src $CC | grep -ci 'change BEHAVIOUR')" "1"
chk "E2 a gate that cannot fail is a finding - in the rule" \
    "$(src .agents/rules/tests-must-gate-for-real.md | grep -ci 'a gate that cannot fail is a finding')" "1"
# ⛔ Keyed on the LADDER ROW, not on the phrase: `cannot fail` already appears in this
# file at :108 ("Defensive try/except around code that cannot fail") - a different sentence
# entirely, and it made the first draft of this row pass before the edit existed.
chk "E2b ...and in the cicd FAIL ladder" \
    "$(src $CC | grep -c 'a new gate that cannot fail')" "1"
chk "E3 run gates bare - in the rule" \
    "$(src .agents/rules/tests-must-gate-for-real.md | grep -c 'Run gates BARE')" "1"
atleast "E4 both-machines awareness in the cicd clean-code scan" \
    "$(src $CC | grep -ci 'both machines')" "1"
# ⛔ Reads through `src`, not through `git grep HEAD` - the first draft always read HEAD, so it
# stayed RED against a working tree that already had the fix, and would have gone GREEN against a
# ref that never did. A row that ignores the mode it was given is not measuring the subject.
n=0
for r in artifacts-always-first code-standards tests-must-gate-for-real constitution \
         work-consolidation git-policy worktree-per-story 000-PLAN-FIRST-GATE; do
  src ".agents/rules/$r.md" | grep -q '_artifacts/_memory' && n=$((n+1))
done
atleast "E5 more than one rule names the memory store" "$n" "2"

# ── The both-machines class (operator, 2026-08-18: "we are on a mac now so thats not good") ──
chk "E6 no authored surface hardcodes the Windows venv path" \
    "$(for f in $(git -C "$LOBBY" ls-files '.agents/commands/*.md' '.agents/rules/*.md' '.agents/skills/**/*.md'); do
         src "$f" | grep -n '\.venv[\\/]Scripts' | while IFS=: read -r n _; do
           src "$f" | sed -n "$((n>1?n-1:1)),$((n+1))p" | grep -q 'bin\|POSIX' || echo "$f:$n"
         done
       done | wc -l | tr -d ' ')" "0"
chk "E7 the lint carries the guard that keeps it that way" \
    "$(src .agents/scripts/workflow_lint.py | grep -c 'def check_both_machines')" "1"

exit $fail
