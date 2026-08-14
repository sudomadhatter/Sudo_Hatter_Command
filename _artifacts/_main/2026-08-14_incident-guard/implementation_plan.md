# Implementation Plan — SCC-148: task_preflight misroutes a live incident branch

**Branch:** `chore/SCC-148-incident-guard` · **Worktree:** `.claude/worktrees/incident-guard`
**Sibling lane:** `chore/SCC-147-lens-budget` (0 commits, no file overlap with this lane's touch set — dev in parallel)

## The defect, confirmed against source

- `.agents/commands/cicd-mobile-error-team.md:47` — the incident command writes **only**
  `claude/incident-<short-id-lower>`.
- `.agents/scripts/task_preflight.py:59-63` — `WRONG_LANE` is an insertion-ordered dict scanned
  first-match-wins by `startswith` (line 146-149), in the order `epic/`, `claude/`, `incident/`.
  A real incident branch `claude/incident-abc123` matches the generic `claude/` entry first and is
  refused with *"a story branch lands on its EPIC branch at close-out, never on main. Use
  /cicd-update-sprint-memory."* — wrong command, told with confidence. `incident/` (bare) is never
  reached by anything that creates branches — dead entry.
- **A third surface also disagrees**, found while grounding this plan: `.agents/rules/git-policy.md:209`
  says `(`incident-*` branches come from the Epic-16 incident pipeline...)` — that pattern matches
  neither the command's real `claude/incident-<id>` nor the script's `incident/`. All three surfaces
  must agree on the one true prefix `claude/incident-`.
- The existing test (`test_task_preflight.py:277-283`) parametrizes over `"incident/SCC-11-thing"`,
  a shape nothing creates — it has never exercised the real bug.

## Fix direction — Option 1 (ticket's own recommendation: smallest change)

Reorder `WRONG_LANE` so the more specific `claude/incident-` prefix is checked **before** the generic
`claude/` entry (dict insertion order + first-match-wins scan means order alone carries the fix — no
change to the scan loop itself). Remove the dead `incident/` entry. Point both remaining incident
mentions (script + git-policy.md) at the one real prefix.

Rejected: Option 2 (rename the branch shape to `incident/<id>`) — a branch-shape change touching
git-policy.md's branch model and anything else pattern-matching `claude/`, for no behavioral gain over
Option 1.

## Acceptance list (checkable)

1. **RED test, first.** A new case in `test_task_preflight.py` feeds `task_preflight` a branch shaped
   exactly as `/cicd-mobile-error-team` creates it (`claude/incident-<short-id-lower>`) and asserts it
   is **refused naming `/cicd-mobile-error-team`**, not routed to `/cicd-update-sprint-memory`. On
   today's source this assertion fails (proves the bug, not a typo in the test).
   *(Review F1)* The **stale tuple `("incident/SCC-11-thing", "/cicd-mobile-error-team")` at
   test_task_preflight.py:281 is REWRITTEN in the same edit**, not left behind: after the fix that
   branch falls through to the shape regex and its "names /cicd-mobile-error-team" half goes RED —
   a broken suite the plan must predict, not discover. The new case also gets a **distinct label**
   (the loop labels via `name.split('/')[0]`, so `claude/incident-…` inside the same tuple would
   collide with the existing `claude/ branch refused` row name).
2. **After the fix**, that same branch is refused and names `/cicd-mobile-error-team` (WRONG_LANE's
   own established remedy for incident branches — task_preflight closes chore/ branches only, an
   incident branch is never its business). The pre-existing `claude/SCC-11-thing` (ordinary story
   branch) case still refuses naming `/cicd-update-sprint-memory` — the reorder must not break the
   case it already got right.
3. **No dead entry left in `WRONG_LANE` — guarded against BOTH ways an entry dies.** Two assertions,
   importing the actual `WRONG_LANE` dict from the module (import-safe per its own docstring; not
   grepped from prose):
   - **Key-set pin** — exactly `{"epic/", "claude/incident-", "claude/"}` — kills
     dead-by-nonexistence (an entry no command creates, like today's `incident/`). Fails today.
   - ***(Review F2)* Shadowing assertion** — for every entry, **no earlier entry is a prefix of
     it** (derived from the scan loop's own first-match `startswith` semantics). Kills
     dead-by-shadowing: a set pin is order-blind, and ORDER is this ticket's actual bug — an
     alphabetical "tidy" putting `claude/` back before `claude/incident-` would re-kill the fix
     under a green set pin. This guard also generalizes to any future lane added behind a generic
     prefix. Fails today (`claude/incident-` isn't present; on the ordering alone the current dict
     passes — which is WHY the set pin and the shadow check are both needed).
4. **`git-policy.md` and the command agree on one prefix, same commit.** git-policy.md's `incident-*`
   parenthetical (line 210) becomes `claude/incident-*`, landed in the same commit as the script fix.
5. ***(Review F3)* The commit clears the armed SOP-currency gate as a decision, not a scramble.**
   This diff touches two usage surfaces (`.agents/rules/*.md`, `.agents/scripts/*.py`;
   sop_currency.py:71-77) so the gate demands the SOP staged or `[sop-ok]`. Verified: the SOP's
   `task_preflight.py` row (workflows_testing_SOP.md:1307) does not enumerate the WRONG_LANE
   prefixes, so nothing in it becomes false — **`[sop-ok]` is the honest exit, pre-declared here**,
   with the message noting the routing-message correction alters no operator-typed surface. (The
   test file is exempt via `_EXEMPT_PREFIXES`; `scripts/INDEX.md` is `.md` and outside the
   `.py|.ps1` surface filter.)

## Steps

| Step | Action | Assertion that proves it |
|---|---|---|
| 1 | Add RED cases to `test_task_preflight.py`: real incident-branch shape (distinct label), key-set pin, shadowing assertion — **and rewrite the stale `incident/SCC-11-thing` tuple in the same edit (F1)** | `run_all.py` shows the new cases FAILING, each for the right reason (misrouted / wrong keys / — the shadow check alone passes today and is red only via the key-set half, stated as such) |
| 2 | Reorder `WRONG_LANE` in `task_preflight.py`: `claude/incident-` before `claude/`; drop `incident/` | new cases GREEN |
| 3 | Fix `git-policy.md:210` parenthetical to `claude/incident-*`; update `scripts/INDEX.md:46` prose | grep/read confirms one prefix system-wide |
| 4 | Commit with `[sop-ok]` pre-declared (F3), explicit paths, key-led subject | armed sop_currency gate accepts; hook output clean |
| 5 | Re-run full `run_all.py` | full suite green, count reported vs main's baseline |
| 6 | Mutation sweep drawn from the code — candidates: swap the two `claude/*` entries back; delete the `claude/incident-` entry; reintroduce `incident/`; `startswith` → `==` | table declared before mutating, in the walkthrough; 0 survivors or each survivor is a finding; restore verified via `git status` |

## Out of scope (flagged, not silently dropped)

The operator's Jira note about `task_preflight` appearing to run twice (review + close-out) was
assessed and does **not** hold against current source — `task_preflight.py` is invoked exactly once,
at `/smh-close-task-merge-tree` Step 1. Not carried into this lane's diff; reported to the operator
separately.

## Files touched

- `.agents/scripts/task_preflight.py`
- `.agents/scripts/tests/test_task_preflight.py`
- `.agents/rules/git-policy.md`
- `.agents/scripts/INDEX.md` (added by the audit below — its prose describes the exact behavior
  this lane is changing)

No overlap with SCC-147's stated touch set (`.agents/commands/cicd-code-review.md`,
`.agents/commands/smh-code-review.md`, `.agents/scripts/tests/test_review_engine.py`).

---

## Self-Audit (2026-08-14)

**Mode:** PRE-WORK. **Right-size:** touches a rule (`git-policy.md`) → **Full** (all phases).

### Phase 0 — Scope
Change set as listed above (script logic reorder, one new-vs-dead dict key, one rule-doc line, one
INDEX-prose line, plus new/fixed test cases). Traceability checked both directions: every acceptance
item (1–4) maps to a plan step; no plan step traces to nothing. Lane check: no `backend/ ·
frontend/ · firebase/ · functions/ · mobile/ · .github/` in the touch set → stays Task lane, closes
via `/smh-close-task-merge-tree`.

### Phase 1 — Blast-radius trace
- **Script** (`task_preflight.py`): grepped every caller. It runs as a subprocess from
  `/smh-close-task-merge-tree`, `/smh-merge-multiple-workingtrees`, and platform doors
  (`.opencode/commands/*`); no module imports it, so the `WRONG_LANE` reorder cannot break an
  import-time contract. `.agents/scripts/INDEX.md:46` prose currently says the script "refuses
  `epic/`, `claude/` and `incident/` branches by name" — **this becomes wrong the moment the code
  changes**, so it is added to the touch set (⚠️ AUDIT FINDING, folded into Files touched above).
  `hooks_armed.py` imports nothing from `task_preflight.py`'s `WRONG_LANE` — unaffected.
- **Rule** (`git-policy.md`): 23 command files cite the rule file generally; none cites the specific
  `incident-*` parenthetical by content — grepped for `incident` across `.agents/commands/*.md` and
  `.agents/rules/*.md` and found only prose mentions, no code that parses that line. Editing one
  clause inside an existing line is not a rule *rename* (Phase 1's rename row doesn't apply) and
  `workflow_lint.py`'s `_RULE_POINTERS` matches on the rule filename, not clause content — unaffected.
- **⚠️ AUDIT FINDING, explicitly cut:** `.agents/scripts/git-hooks/merge-target-guard.sh:51` and
  `docs/_scc_sops_prds/workflows_testing_SOP.md:1304` both describe the incident carve-out with the
  same wrong bare pattern (`incident-*`, no `claude/` prefix). Checked whether this is a live
  functional bug like this ticket's: it is not — that script never *parses* the string, it only
  documents in a comment that anything outside the classified prefixes (`epic/`, `chore/`, `claude/`)
  is let through unjudged, and a `claude/incident-*` branch is never merged through a local `git
  merge` in the first place (the incident lane lands via a GitHub PR, which never runs local hooks).
  **Disposition: CUT from this lane.** The ticket's ACCEPTANCE block names `git-policy.md`
  specifically, not this script or the SOP prose; folding in a second gate's doc-accuracy issue is
  the kind of adjacent-and-unasked expansion Phase 2 defaults to cutting. Recorded as a follow-on
  below instead.
- **Sibling lanes:** `git worktree list` shows only `chore/SCC-147-lens-budget` live, 0 commits,
  0 uncommitted files, touch set (`cicd-code-review.md`, `smh-code-review.md`,
  `test_review_engine.py`) disjoint from this lane's. No landing-order dependency either direction.

### Phase 2 — Over-engineering gate
Walked every tripwire: no new command, no new rule file, no new script, no clone-and-tweak, no new
flag, no N-for-1 generalization, no dead-state error handling, no gate-that-cannot-fail introduced.
The plan reorders three dict entries, deletes one, and corrects two prose lines — smaller than the
acceptance list, not larger. **None fire.**

### Phase 3 — Pre-mortem
| Scenario | Handled? |
|---|---|
| Other machine (python3 vs python) | N/A — no shell invocation changes, pure Python dict + one markdown line |
| Fresh clone / `core.hooksPath` off | N/A — not a hook, doesn't change arming |
| Fires on someone else's commit | The refusal message itself changes for incident branches only (now correctly names `/cicd-mobile-error-team` instead of `/cicd-update-sprint-memory`); every other branch shape's message is byte-identical, verified by keeping the pre-existing `claude/SCC-11-thing` case in the suite |
| Escape hatch | N/A — not a gate being armed/disarmed, a routing message being corrected |
| Empty input reads as PASS | N/A — no empty-input path touched |
| Four platform caches | N/A — no command/menu surface changed |
| Sibling lane lands first | Checked above — none live with overlapping files |
| Rollback | Fully reversible: `git revert`, no delete, no history rewrite, no irreversible Jira transition beyond the normal `Done` flip at close-out |

Failure modes considered and none survive: the fix is data-and-doc-only, exercised by a real
subprocess test against real script output, so a silent-green outcome would require the new test
itself to be vacuous — guarded against by requiring it RED first (Step 2 of the dev cycle) and by the
`WRONG_LANE`-key-set pin catching a reintroduced dead entry regardless of ordering.

### Phase 4 — Verdict
- Verification strategy present? Yes — every acceptance item names the exact assertion in the Steps
  table.
- Anything irreversible? No.
- Any step vague enough to guess wrong? No — the fix direction (Option 1) is pinned, not left open.
- Convention fit? Yes — RED-then-GREEN, mutation sweep drawn from code, walkthrough carries the
  evidence, matches this lane's own established shape (SCC-144/145/129 in this same repo).

**Follow-on (not this ticket):** `merge-target-guard.sh`'s comment and the SOP's §16 prose both use
the bare `incident-*` pattern in documentation only (not executable matching) — worth a small
doc-accuracy fix, filed separately if the operator wants it swept in the same pass as this bug family.

**Audit verdict: GO**

---

## Plan Review (2026-08-14 — operator-requested fresh deep dive, findings baked in above)

Independent re-derivation of every plan claim from source. Three real defects found in the plan
itself; each is folded into the acceptance list / steps table, marked *(Review F1/F2/F3)*:

| # | Finding | Where fixed |
|---|---|---|
| F1 | The existing tuple `("incident/SCC-11-thing", "/cicd-mobile-error-team")` (test_task_preflight.py:281) goes RED after the fix — falls through to the shape regex, stops naming the command. Plan said "add cases", never "rewrite the stale one". Plus: the loop's `name.split('/')[0]` labeling makes a new `claude/incident-…` case collide with the existing `claude/ branch refused` row name. | Acceptance 1; Step 1 |
| F2 | **Acceptance 3's key-set pin was a check that cannot fail for this ticket's own bug class**: a set is order-blind, and the defect is ORDER. An alphabetical re-sort re-shadowing `claude/incident-` behind `claude/` would pass the set pin green. Added the shadowing assertion (no earlier entry is a prefix of a later one), modeled on the scan loop's real first-match semantics; generalizes to any future lane behind a generic prefix. | Acceptance 3; Step 1 |
| F3 | The armed SOP-currency gate was unaddressed — this diff touches `.agents/rules/*.md` + `.agents/scripts/*.py`, both surfaces per sop_currency.py:71-77. Verified the SOP's task_preflight row (line 1307) doesn't enumerate WRONG_LANE prefixes, so nothing in it goes stale → `[sop-ok]`, pre-declared. | Acceptance 5; Step 4 |

**Re-verified sound (walked, not assumed):** first-match `startswith` scan at task_preflight.py:146-149
and py-dict insertion order carry the fix with no loop change · no module imports `task_preflight`
(subprocess callers only) so the reorder breaks no import contract · `claude/incident-` cannot
shadow a real story branch (the Jira key sits uppercase immediately after `claude/`) · the module is
documented import-safe for the new structural assertions · WRONG_LANE refusals are `rep.err` → exit 2
· rollback is a clean revert, nothing irreversible.

**Follow-on upgraded (same defect class, one gate over — proposes a NEW ticket, not scope here):**
`merge-target-guard.sh:51` *declares* `incident-*` outside the branch model, but no case arm exists
and the real `claude/incident-*` matches the `claude/*)` arm (line 151) → an incident hotfix is
classified a STORY lane, so a local emergency merge to `main` would be refused with "a claude/* story
lane merges into ITS epic/* branch" — confidently wrong under incident pressure, dead carve-out
attached. Low reach (incident merges land via GitHub PR; local hooks never fire) but it is SCC-148's
shape verbatim. Related visibility: `/cicd-resume`'s `claude/*` ls-remote sweep lists incident
branches as "parked story work" — the corrected git-policy line at least lets a reader see that.
