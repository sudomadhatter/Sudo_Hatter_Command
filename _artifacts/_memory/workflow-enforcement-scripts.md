---
name: workflow-enforcement-scripts
description: Wave 1 shipped 4 stdlib scripts under .agents/scripts/ that make sudo-flow invariants executable
metadata: 
  node_type: memory
  type: project
  originSessionId: d9adc5bc-e814-4396-b913-62eac264ecce
  modified: 2026-08-04T03:35:35.144Z
---

Shipped 2026-08-03 (lobby commit `63c211c`), script-only by design — **zero command edits**,
so it cannot collide with the pending story-artifact rollout ("Plan A"). Governing principle
of the approved plan: *an instruction may only be deleted after a script enforces it.*

| Script | Answers |
|---|---|
| `workflow_lint.py` | is the toolkit + a project self-consistent? |
| `story_status.py` | do a story's TWO status surfaces agree — and flip both atomically |
| `gate_receipt.py` | did this gate actually run, at this commit? |
| `closeout_preflight.py` | is this story safe to close out? |

**Why:** these encode failure classes that already have memories — [[story-status-flip-contract]],
[[landing-is-not-closeout]], [[commit-and-push-are-one-action]], [[pruned-worktree-leaves-a-blocking-shell]],
[[agy-epic-keys-rot-silently]] — as checks instead of prose an agent must remember.

**How to apply:** `python .agents/scripts/tests/run_all.py` (39 cases, stdlib, no pytest) is
the gate before touching any of them. Two design rules that are load-bearing, not style:
`gate_receipt.py` has **no `--result` flag** — it executes the gate and writes the receipt
from the real exit code, so a verdict cannot be handed in; and every flag must precede `--`
(anything after it is the gate command verbatim). `unrunnable` is a third result distinct
from `fail`, because a missing tool is a finding, not a skip.

**ALL FIVE WAVES DONE** (2026-08-03). Wave 4 (the board split) ran last, from its own audited plan
(`_artifacts/_main/2026-08-03_sprint-status-split/`): AGY board 363,334 → 62,040 B, byte-verified
lossless at every stage — see [[board-narrative-lives-in-history]] for where narrative lives now.
The audit's three blockers (two-byte-streams F1, note-carry F2, unpinned verify F4) were fixed
BEFORE migrating; `split_sprint_status.py` is the 5th script (suite now 94 cases / 5 files).
⏳ Flip owed: drop `--advisory` from the close-out receipt gate after the first full sprint.
⏳ Owed: one real close-out (`/sudo-update-sprint-memory`) against the split board — the next
story's close-out is the live test; watch the CHANGELOG re-point and the auto note-drop.

**Wave 3.1 landed INVERTED from the plan, and the reason generalizes.** The plan wanted a shared
`command-preamble.md` extracted and the inline Step-0 prose deleted. But `sudo-target-resolution.md`,
`git-policy.md` and `worktree-per-story.md` already existed, and the inline restatements are
deliberate ([[restate-alwayson-obligations-in-command-bodies]]). The real defect was the **inverse**:
23 commands DID the thing without POINTING at the rule — 13 mutated git with no reference to
git-policy. So `workflow_lint.check_rule_pointers()` enforces *"the pointer exists"*, never *"the
prose is deleted"*. The command surface GREW 3.2% (341,171 → 352,066 B) against a forecast −30%;
correctness cost bytes and the forecast rested on a false premise.

Wave 1 shipped with 6 defects, all found by the self-audit (`ff22dd2`) and fixed the same day
(`c7678a4`, tests 39 → 60). The lesson worth keeping: **every one was invisible in the fixtures and
obvious the moment the script ran against the real tree.** Two failure shapes, both fatal:
a checker that *cannot fire* (branch matching by story slug, when branches here are named
descriptively — `claude/xdist-tail-hang`) reads exactly like a clean pass; a checker that fires on
correctly-closed history (no legacy-verdict fallback → every pre-08-02 story BLOCKs) or on 115
untouchable files gets muted. Gate staleness must compare **trees, not SHAs** — a merge commit has a
new HEAD and identical content. Verify against the live tree before calling any of these done.

**`run_all.py` IS the lobby's merge gate (confirmed 2026-08-07).** The lobby has **no `frontend/`**, so
it has no E2E harness and never will — `/sudo-e2e` stops at Step 1 when `frontend/e2e/run-e2e.mjs` is
missing. Do not go hunting for one, and never improvise a substitute and call it the gate. Per-repo:
lobby → `python3 .agents/scripts/tests/run_all.py`; AviationChat → light gate + `/sudo-e2e`. Green reads
`5/5 files passed` and `20/20 passed`, ~2 s. Both `chore/SCC-10-*` merges on 2026-08-07 were gated on
exactly this. See [[jira-integration-live]].
