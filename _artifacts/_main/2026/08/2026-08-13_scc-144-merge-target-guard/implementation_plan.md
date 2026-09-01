# SCC-144 — Make the merge-target guard mechanical

- **Ticket:** SCC-144 (Task) — *"Make the merge-target guard mechanical: `.githooks/pre-merge-commit` + pre-push backstop"*
- **Lane:** `chore/SCC-144-merge-target-guard`, worktree `.claude/worktrees/merge-target-guard`, cut from `main` @ `5dadcd6`
- **Sibling lane:** `chore/SCC-129-gate-the-gate` (in dev, **zero commits** — plan only)
- **Date:** 2026-08-13

---

## 0. What this closes, in one line

Every gate in this system checks the branch you merge **from**. Nothing checks the branch you merge
**into**. A `cd` that silently reverts between two tool calls plus a bare `git merge` puts production
work on a sibling lane, prints success, and is caught only by suspicion (SCC-97, 2026-08-11). The
push-time gates cannot see it, because a merge onto the wrong *local* branch is never pushed.

---

## 1. Acceptance list (from the ticket's own ACCEPTANCE block — authority order 1)

Every item is checkable by a command. Item → the assertion that proves it:

| # | Acceptance | The assertion |
|---|---|---|
| A1 | A merge whose target is the wrong branch is REFUSED by mechanism, no agent choosing to check | `test_git_hooks.py` drives a **real `git merge`** through `core.hooksPath` in a temp repo; `chore→chore` exits non-zero and no merge commit exists afterwards |
| A2 | The refusal names the target, the source, and the rule broken | assert all three substrings in the hook's own stderr |
| A3 | The fast-forward gap has a **named** `pre-push` backstop, not a silent absence | one case pins that a `--ff-only` merge fires **no** `pre-merge-commit` at all (tracer file absent); a second drives a real `git push` of a contaminated lane and asserts REFUSED |
| A4 | `--no-verify` remains an override, and the hook says so in its own header | a case runs the same refused merge with `--no-verify` and asserts it succeeds; a case greps the header for the word |
| A5 | The new hook is in the `hooks_armed` accounting, so a fresh clone reports it OFF rather than green | `hooks_armed.scan()` on a repo with the flag deleted from disk reads `armed is False` and names `MERGE-TARGET-ENFORCE` |
| A6 | `test_git_hooks.py` covers all six ticket fixtures, both ALLOW and REFUSE halves, every check proven red first | the file itself in `run_all.py`, plus pasted RED output per check in the walkthrough |
| A7 | The three folds are in the command body | `grep` for each fold in `.agents/commands/smh-merge-multiple-workingtrees.md`; `test_command_surfaces.py` green after `/smh-sync-agents` |
| A8 | Full gate bare and green at the landing sha; case total additive | `run_all.py`, `workflow_lint.py --toolkit-only`, `check_maps.py --depth3-only --strict` — each run **bare**, exit code read directly |

---

## 2. Measurements already taken (this plan rests on these, not on belief)

**M1 — `pre-merge-commit` fires on a true merge, and HEAD is the TARGET.** Probed in a throwaway
repo (`scratchpad/hookprobe`): a `--no-ff` merge fired `pre-merge-commit`, `prepare-commit-msg`,
`commit-msg`, `post-merge`, and `git rev-parse --abbrev-ref HEAD` inside the hook read
`chore/SCC-2-b` — the receiving branch. So the target is readable with no arguments, as the ticket says.

**M2 — a fast-forward fires NO blocking hook.** The same probe, `git merge --ff-only`: only
`post-merge` ran. `post-merge` is after the fact and cannot refuse, so it is **not** a candidate for
the backstop — considered and rejected here so it is not re-proposed later. The backstop must be at
push time. (This is ticket blind spot 1, measured rather than assumed.)

**M3 — the SOP-gate open question is ANSWERED, and the ticket's premise is wrong.** The ticket says
*"neither `.githooks/commit-msg` nor `sop_currency.py` has a merge carve-out."* The carve-out exists,
one layer down, in the dispatcher `.agents/scripts/git-hooks/sop-currency.sh:46` — `[ -f
.git/MERGE_HEAD ] || [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] → exit 0`, plus a subject
test for `Merge `/`Revert "`/`fixup! `/`squash! `. `commit-msg-jira.sh:51` carries the identical pair.
So the three landing merges were **skipped by design**, not passed. That is the sentence fold 1 needs.

⚠ **And the measurement found a defect in that carve-out** — see §6, item F1. It is a probe of
`.git/MERGE_HEAD` as a **path**, and in a worktree `.git` is a *file*, so the probe is false there.

**M4 — the branch model rule named in the ticket does not exist under that name.**
`.agents/rules/git-branch-model-standard.md` is not on disk; the law lives in
`.agents/rules/git-policy.md` §"Branch model". The hook cites the file that exists.

**M5 — sibling-lane overlap.** `chore/SCC-129-gate-the-gate` has **no commits** (its plan is
untracked in its own artifacts dir). Committed overlap today: **none**. Declared future overlap:
`docs/_scc_sops_prds/workflows_testing_SOP.md` and `_artifacts/_main/INDEX.md` — the two files every
lane touches. **Landing order: either.** Both files are append-shaped (a table row, a section); a
conflict there is a hand-resolve of two adjacent rows, and the `check_maps` missing-row gate catches
a dropped ledger row (it did exactly that on 2026-08-13). If SCC-129 lands first, this lane absorbs
`main` and re-gates, per `/smh-close-task-merge-tree`.

---

## 3. The build

### 3.1 `.agents/scripts/git-hooks/merge-target-guard.sh` (new) — the logic

POSIX `sh`, no interpreter probe, no Python. That is not style: `pre-push-main-approval.sh`'s header
records that five Claude hooks were wired to `powershell`+`python` and exited 127 silently for weeks
on the Mac. **A gate must not depend on the class of thing that broke the last gate.**

Resolution:

```
TARGET = git rev-parse --abbrev-ref HEAD          # the branch RECEIVING (M1)
SOURCE = candidate names for MERGE_HEAD:
           git branch      --points-at MERGE_HEAD --format='%(refname:short)'
           git branch -r   --points-at MERGE_HEAD --format='%(refname:short)'
           fallback: the `Merge branch 'X'` / `Merge remote-tracking branch 'origin/X'` line
                     in "$(git rev-parse --git-path MERGE_MSG)"
```

⛔ `git rev-parse --git-path MERGE_MSG`, **never** the literal `.git/MERGE_MSG` — that is the exact
bug F1 below. Every git-dir path in this lane goes through `--git-path`.

Classification (`origin/X` is stripped to `X` first), from `git-policy.md` §Branch model:

| name | class |
|---|---|
| `main` | `main` |
| `epic/*` | `epic` |
| `chore/*` | `chore` |
| `claude/*` | `story` |
| anything else (`incident-*`, a tag, a bare sha) | `unknown` |

The verdict table — **target ← source**:

| target ↓ / source → | `main` | `epic` | `chore` | `story` | `unknown` |
|---|---|---|---|---|---|
| **`main`** | allow (self/origin) | **allow** | **allow** | REFUSE | allow¹ |
| **`epic`** | allow (absorb main) | allow *iff same name* | REFUSE | **allow** | allow¹ |
| **`chore`** | allow (absorb main) | REFUSE | **allow iff same name**, else ⛔ **REFUSE — the SCC-97 signature** | REFUSE | allow¹ |
| **`story`** | allow | allow (absorb the epic) | REFUSE | allow iff same name, else REFUSE | allow¹ |
| **`unknown`** | allow¹ | allow¹ | allow¹ | allow¹ | allow¹ |

¹ *allow, with one printed line saying it declined to judge and why.* **The guard refuses only
known-bad topologies.** This system's memory is full of gates that hard-blocked on a false red and
got routed around (`hooks_armed`'s `README.md`, its `.gitignore`, its `~` expansion, `check_maps` in
a worktree). `incident-*` branches are explicitly outside the branch model per `git-policy.md`, and a
gate that fires on them is a gate that gets disarmed.

**Ambiguity rule, stated because it is a real decision:** several branches can point at one sha.
Evaluate every candidate — **any ALLOW wins; only if there is at least one REFUSE and no ALLOW does
it refuse.** Deliberately biased toward the false negative. A guard that blocks a correct merge costs
more than one that misses an ambiguous case, and the ambiguous case is still caught at push time by
§3.2.

Arming, matching every other gate here exactly:
- `.agents/scripts/git-hooks/DISABLE` → exit 0 (the kill switch all gates honor)
- `.agents/scripts/git-hooks/MERGE-TARGET-ENFORCE` absent → **warn, do not refuse**
- header states **`git merge --no-verify` is the auditable override**, same posture as `[sop-ok]`,
  in the file itself so nobody "fixes" it later (A4)

The refusal names the **target**, the **source**, the **rule** (`git-policy.md` §Branch model), the
correct destination for that source class, and the override (A2).

### 3.2 `.agents/scripts/git-hooks/pre-push-merge-backstop.sh` (new) — the fast-forward net

M2: a ff merge creates no commit, so no hook can refuse it. What it *does* leave is evidence:
**another lane's unlanded commits are now contained in your lane.** That is the check, and it is one
check, not two:

> For a pushed ref `refs/heads/<lane>` where `<lane>` is `chore/*` or `claude/*`: if any **other**
> local `chore/*`/`claude/*` branch is an ancestor of the pushed sha **and is not** an ancestor of
> `origin/main`, REFUSE.

- The `origin/main` half is what removes the false red: after a sibling lands and you absorb `main`,
  its commits are ancestors of `origin/main`, so they are invisible to this check.
- ⛔ **Only lane branches are checked, never `main` or `epic/*`.** Pushing `main` after
  `/smh-close-task-merge-tree` merges `chore/X` means `chore/X` is contained and unlanded **by
  definition** — that is the legitimate landing, and gating it would refuse the system's primary
  shipping path. Same for a story landing on `epic/*`.
- No `origin/main` (or no `git`) → print one line, allow. Refusing on the absence of a reference
  point is the vacuous-red mirror of the vacuous green.

Considered and rejected: re-classifying every merge commit in the pushed range by
`git name-rev`-guessed branch names. Historical merge commits do not carry the branch names they were
made on; the guesses drift, and every wrong guess is a false red on the shipping path. The ancestor
check above already subsumes the non-ff case.

### 3.3 `.githooks/pre-merge-commit` (new) — the dispatcher

The house shape, byte-for-byte in spirit with `.githooks/pre-commit`: resolve
`$(git rev-parse --show-toplevel)/.agents/scripts/git-hooks/merge-target-guard.sh`, and if it is not
executable **say so and allow** (SCC-32 — a worktree cut before the script existed must not have its
merges killed by a bare `exec` on a missing file).

### 3.4 `.githooks/pre-push` (edit) — two gates, one stdin

⛔ **The hazard that makes this more than a copy of `commit-msg`'s two-gate shape:** `pre-push`
receives one line per ref **on stdin**, and stdin can be consumed exactly once. The first gate to read
it leaves the second gate reading EOF — which would silently allow everything, i.e. this ticket's own
failure class inside this ticket's own fix. So the dispatcher reads stdin **once** into a temp file
under `$(git rev-parse --git-path .)`, feeds each gate from it, and removes it on exit.

Order: the backstop first (a topology refusal should not consume the approval token), then
`pre-push-main-approval.sh` — which stays the **last** gate, and stays `exec`'d, so its exit code is
still the hook's. Missing-script → warn, allow (unchanged contract).

### 3.5 `.agents/scripts/hooks_armed.py` (edit) — the accounting (A5)

One row: `"MERGE-TARGET-ENFORCE": ("merge-target-guard.sh", "pre-merge-commit")`.

**ONE flag governs both halves**, and the header of each script says so. A second flag would let an
operator disarm the pre-merge half while believing the push half still covered it — the two-flag,
one-gate ambiguity `ARM_FLAGS`'s own comment warns about. The backstop is therefore flagless in the
table and falls under layer 2's executability check, which is the *stated, existing* known gap in
that file's docstring (`pre-commit-encoding.sh` is in exactly the same position). It is not a new hole
and the plan does not pretend it is closed.

The new dispatcher is picked up by `expected` automatically — that set is derived from `git ls-files`,
never hardcoded, and `test_hooks_armed.py` case G pins that property.

### 3.6 `.agents/scripts/tests/test_git_hooks.py` (new) — the RED

Stdlib + `_harness.Cases`/`TempDir`, auto-discovered by `run_all.py`. Every case drives **real git**
in a temp repo with `core.hooksPath` pointed at a copy of the real `.githooks/` — a source-grep guard
would prove nothing here (`prose-pinning-guards-are-vacuous`, SCC-125), and a hook that git never
invokes is decorative (`test_main_push_gate.py`'s own end-to-end case exists for that reason).

The six ticket fixtures, plus what they force:

| Case | Fixture | Half |
|---|---|---|
| A | `chore → main` | **ALLOW** (negative control) |
| B | `chore → chore` | **REFUSE** — the SCC-97 signature; message names target + source + rule |
| C | `epic → main` | **ALLOW** (negative control) |
| D | `claude story → epic` | **ALLOW** (negative control) |
| E | fast-forward | **no hook call at all** — pinned via a tracer the hook writes; asserts the *absence* |
| F | `--no-verify` on case B's merge | succeeds — the override, documented |
| G | backstop: lane carrying another **unlanded** lane's commits, pushed | **REFUSE** |
| H | backstop: lane that absorbed `main` after a sibling landed, pushed | **ALLOW** (the false-red control) |
| I | backstop: pushing `main` carrying the lane it is landing | **ALLOW** (the shipping-path control) |
| J | `MERGE-TARGET-ENFORCE` deleted | warns, does not refuse |
| K | `DISABLE` present | silent allow |
| L | `hooks_armed` reports NOT ARMED naming the new flag when it is off disk | accounting (A5) |
| M | ambiguity: source sha carrying both an allowed and a forbidden name | ALLOW, per §3.1 |
| N | unclassified (`incident-*`) target | ALLOW with the declined-to-judge line |

**Both halves are mandatory. A gate that refuses everything is as broken as one that refuses
nothing** — A, C, D, H, I, M, N are the negative-control half and they outnumber the refusals on
purpose.

⛔ **Every check proven red first, and the actual red pasted into the walkthrough.** For the ALLOW
cases, "red first" means the *mutation* proof: the assertion is shown failing against a guard
deliberately broken in the direction that case defends (a table row inverted, the ambiguity rule
flipped to any-REFUSE-wins, the `origin/main` half of the backstop deleted). `all()` over an empty
set is `True`, and that exact shape has already let a case pass against a gutted detector in this
repo — so each case also asserts the fixture it is measuring actually exists.

**Convention dependency (SCC-129):** its negative-control convention (`_negative_control: true`, `NC_`
ids, a permanent fixture dir) is designed for the review engine's *fixture*, not for a hook test.
What this lane adopts is the **rule**: a check that cannot fail is a finding, and the ALLOW half is a
first-class deliverable rather than an afterthought. If SCC-129 settles anything that binds test
files generally, this file adopts it rather than inventing a second convention — stated here so the
commitment is on the record before either lane lands.

### 3.7 The three folds — `.agents/commands/smh-merge-multiple-workingtrees.md`

1. **`[sop-ok]`** — one sentence at the fix-on-branch step (4b), carrying M3's answer: merge commits
   are exempt by dispatcher carve-out, so `[sop-ok]` is not needed for the merge itself — it is needed
   for the **hand fixes** made on the branch during reconciliation, which are ordinary commits and
   which the armed gate will refuse if they touch a usage surface without staging the SOP doc.
   ⚠ Plus the worktree caveat from F1 if F1 is not taken.
2. **The eligibility table** — one line: dump Step 3's table, landing order and conflict decisions to
   a scratch file. Not a durable-state mechanism: a session *was* compacted mid-landing on 2026-08-13
   and nothing was lost, because the set is cheap to re-derive and the decisions were already in the
   commit messages.
3. **The re-measurement stamp** — one worked example at 4b, in the shape invented during the
   2026-08-13 run (`_artifacts/_main/2026-08-13_scc-127-verify-wave/walkthrough.md`
   §"Post-absorb re-measurement").

Then **`/smh-sync-agents`**, because the command has doors on four platforms and they are generated
(`test_command_surfaces.py` gates it).

### 3.8 Docs — the SOP is not optional here

`.githooks/` and `.agents/scripts/git-hooks/` are both **usage surfaces**: the armed `sop_currency`
gate refuses these commits unless `docs/_scc_sops_prds/workflows_testing_SOP.md` is staged with them.
That is not a chore to route around — it is the doc most likely to be read by the person who trips
this gate. Edits:

- §10 — *"four git hooks"* → five, the row in "The checks, and what each one refuses", and the
  mermaid node
- §7 "⛔ And the merge has to land where you think it does (SCC-97)" — it currently ends with
  *"assert the target before merging"*, a discipline. It gains the sentence that says a mechanism now
  does it, and what `--no-verify` costs
- `.agents/scripts/INDEX.md` — the git-hooks paragraph
- `_artifacts/_main/INDEX.md` — this session's row (`check_maps --depth3-only --strict` gates it)

---

## 4. Order of work

| Step | Does | Proves |
|---|---|---|
| 1 | Write `test_git_hooks.py` cases A–F against **nothing** | RED: no `pre-merge-commit`, no guard script (A6) |
| 2 | Build the dispatcher + `merge-target-guard.sh` | A–F GREEN (A1, A2, A4) |
| 3 | Add cases G–I, RED | the backstop does not exist (A3) |
| 4 | Build the backstop + rewire `.githooks/pre-push` (stdin tee) | G–I GREEN; `test_main_push_gate.py` still green |
| 5 | Add cases J–N + `hooks_armed` row | A5 |
| 6 | Mutation pass: break the guard six ways, each must kill a case | the guard is not prose |
| 7 | The three folds + `/smh-sync-agents` | A7 |
| 8 | SOP + INDEX + the full gate, bare | A8 |

---

## 5. Risks, each with what is done about it

| Risk | What is done |
|---|---|
| **A false red on the shipping path is worse than the hole** | refuse only known-bad topologies; unknown always allows; ambiguity resolves to allow; the backstop exempts `main` and `epic/*` explicitly, and case I is a permanent control on exactly that |
| **stdin is consumed once** (§3.4) — a silent allow-everything | the dispatcher tees; case G drives a **real `git push`**, which is the only thing that proves the second gate still sees its input |
| `test_main_push_gate.py` regression — this edits a shipped gate's dispatcher | its fixtures copy only three scripts, so the backstop is absent there and takes the warn-and-allow path; the suite is run bare after step 4, not at the end |
| A `pre-merge-commit` hook in every clone slows merges | two `git rev-parse` calls and a `git branch --points-at`; no network, no Python, no interpreter probe |
| Windows | POSIX `sh` under git-for-windows' bundled shell, like every other gate here; no `chmod`-dependent assertion in the tests (the `POSIX_ONLY` lesson from SCC-140) |
| The guard passes because git never called it | every case drives real `git merge` / `git push` through `core.hooksPath` |

---

## 6. Open decisions for the operator — F1 is a real defect found while planning

**F1 — the merge carve-out is blind inside a worktree, and every lane in this system is a worktree.**

`sop-currency.sh:46` and `commit-msg-jira.sh:51` both test `[ -f .git/MERGE_HEAD ]`. In a **worktree**
`.git` is a *file*, not a directory — the real path is `.git/worktrees/<name>/MERGE_HEAD` — so that
probe is **always false there**. The subject fallback does not cover it either: it matches `'Merge '*`
(capital, case-sensitive), while this repo's own merge subjects read `merge: chore/... -> main` and
`SCC-127 merge: absorb main`. So the absorb-`main` merge that `/smh-merge-multiple-workingtrees` Step
4b performs **inside the lane** is not exempt from either armed gate, while the same merge performed
in the shared checkout is.

The one-line fix is `git rev-parse --git-path MERGE_HEAD` in both scripts, plus a case pinning it.

**It is in scope by the ticket's own words** (fold 1 is *"determine which before writing the
sentence"*, and this is what the determination found) **and out of scope by the ticket's title.**
Recommendation: **take it** — it is two one-line changes plus two test cases, it lives in the same two
files this lane is already registering hooks against, and leaving it means fold 1's sentence has to
document a bug instead of a rule. If declined, fold 1 documents the worktree caveat verbatim and F1
is filed as its own ticket.

> ✅ **OPERATOR RULING, 2026-08-13: TAKEN.** *"approved and yes fix F-D we dont want blind spots."*
> Both carve-outs move to `git rev-parse --git-dir`, and each gets a case driving a **real merge
> inside a real worktree** — the environment where the probe is blind. Acceptance item **A9**:
> *a merge commit made inside a worktree is exempt from the Jira and SOP gates, exactly as the same
> merge made in the shared checkout already is.*

**F2 — no `MERGE-PUSH-ENFORCE`.** One flag disarms both halves (§3.5). Flagged because it is a
deliberate asymmetry with the rest of `ARM_FLAGS`, not an oversight.

---

## 7. Out of scope, explicitly

- The `pre-commit` / `commit-msg` / `post-commit` hooks, other than F1 if taken
- Project repos (`Projects/*`) — the branch model is shared but the hooks are repo-local by law
  (`repo-local-enforcement-never-centralizes`); propagating is its own ticket with its own key
- The GitHub-side `main-write-gate` — it already refuses a merge from a non-`epic`/`chore` branch, and
  it cannot see a local merge onto a lane, which is the whole reason this ticket exists
- Making `--no-verify` unavailable. It stays. An auditable override is the design.

---

## Self-Audit (2026-08-13)

**Right-size: FULL.** It ships a gate and a hook, edits a script other scripts import
(`hooks_armed.py` → `task_preflight.py:826`), edits a shipped dispatcher (`.githooks/pre-push`),
and changes a command body carrying four platform doors. Every trigger in the Phase 0 table fires.

**Phase 0 — scope + checkable list.** Change set: 4 new files (`.githooks/pre-merge-commit`,
`merge-target-guard.sh`, `pre-push-merge-backstop.sh`, `MERGE-TARGET-ENFORCE`), 1 new test file,
5 edits (`.githooks/pre-push`, `hooks_armed.py`, `smh-merge-multiple-workingtrees.md`, the SOP,
two INDEXes), plus generated doors. Acceptance list = the ticket's own ACCEPTANCE block (authority
1), mapped A1–A8 in §1. **Lane check: CLEAR** — no `backend/`, `frontend/`, `firebase/`,
`functions/`, `mobile/` or `.github/` path is touched, so this closes through
`/smh-close-task-merge-tree`. Traceability both directions: every acceptance item has a step;
**one step traces to no acceptance item — F1 — flagged below.**

**Phase 1 — blast radius**, measured, not assumed:

| Touched | Checked | Result |
|---|---|---|
| `.githooks/pre-push` | `test_main_push_gate.py:35,82,113,268,300` | copies the dispatcher into fixtures and drives a **real** `git push`; the backstop script is absent there → warn-and-allow path. **Must stay green after step 4, run bare.** |
| `hooks_armed.py` `ARM_FLAGS` | `task_preflight.py:826`, `test_hooks_armed.py`, `test_main_push_gate.py:136` | the new row is additive; the loop skips a flag that is neither tracked nor shipped, so existing seeded fixtures are unaffected |
| a 5th hook in `.githooks/` | `test_hooks_armed.py:419,442` | both assert with `<=` (subset), not equality — a 5th dispatcher does not break them; case G pins that the set is derived, never hardcoded |
| an **older worktree** after this lands | `hooks_armed` `expected` ← `git ls-files` | a worktree's index reflects its own commit, so a tree cut before this lands does not "expect" the new hook — **no false red**, verified by reading the derivation, not by hoping |
| `smh-merge-multiple-workingtrees.md` | 4 doors exist: `.claude/skills/`, `.agents/skills/`, `.opencode/commands/`, `.agents/workflows/` | **`/smh-sync-agents` is mandatory**; `test_command_surfaces.py` gates content, not just presence |
| `.githooks/` + `git-hooks/` as usage surfaces | `sop_currency.py` surface list | the SOP doc **must be staged in the same commit** — not optional here |
| `_artifacts/_main/INDEX.md` | `check_maps.py --depth3-only --strict` | this session needs its row or the close-out blocks |
| `.agents/hooks/session-start-context.sh:30`, `require-push-approval.py:99` | read | both *describe* the push gate; neither calls it. **Cleared, no edit owed.** |

**Sibling lanes:** `chore/SCC-129-gate-the-gate` — **zero commits**, plan only. No committed overlap
today. Declared future overlap: the SOP doc and `_artifacts/_main/INDEX.md`. **Landing order: either**
(§2 M5). If SCC-129 lands first this lane absorbs `main` and re-gates; the conflicts are adjacent
appended rows, and the `check_maps` missing-row gate catches a dropped ledger row.

**Phase 2 — over-engineering gate.** Two tripwires examined:
- *"A new script where an existing one grows a subcommand"* — the backstop could have been folded into
  `pre-push-main-approval.sh`. **Rejected:** that file is the token gate, its tests drive it directly
  as a unit, and merging a topology check into an authorisation check makes both harder to disarm
  independently. The house pattern is one concern per script with a dispatcher composing them, exactly
  as `.githooks/commit-msg` composes two. **Stated, not accidental.**
- *"A gate that cannot fail"* — the `unknown → allow` cell and the any-ALLOW-wins ambiguity rule are
  deliberate holes. They are justified in §3.1, and **F-G below makes them loud and pinned** so they
  cannot widen silently.

Nothing else fires. No new command, no new rule, no config flag, no N=1 generalization.

**Phase 3 — pre-mortem:**

| Scenario | Handled? | |
|---|---|---|
| The other machine | POSIX `sh`, no interpreter probe, no Python — but see **F-B** (`mktemp`) | ⚠ |
| A fresh clone | ships OFF until `core.hooksPath` is set, like every gate here — and **A5 is the requirement that it reports OFF rather than green** | ✅ |
| Fires on someone else's commit | the refusal must carry a remedy, not just a diagnosis — see **F-C** | ⚠ |
| The escape hatch | `git merge --no-verify` / `git push --no-verify`, stated in each header (A4) | ✅ |
| Empty input reads as PASS | the designed holes — see **F-G** | ⚠ |
| Four platform caches | `/smh-sync-agents` in step 7; `test_command_surfaces.py` gates it | ✅ |
| A sibling lane lands first | §2 M5; both overlaps are append-shaped | ✅ |
| Rollback | delete two scripts, one dispatcher, one flag, one `ARM_FLAGS` row. Nothing irreversible; no history rewrite, no `main` merge, no Jira transition beyond `In Progress` | ✅ |

**Findings**

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| **F-A** | §3.6 case E | HIGH | Case E pinned the ff blind spot with a **tracer file the hook writes** — which means the fixture's hook is not the real hook, and the case would assert something about the fixture instead of about git. Worse, it pins an *absence*, which is the shape that passes against a gutted detector. **Rewrite:** construct a merge whose topology is **forbidden** (`chore/B` fast-forwarding to `chore/A`) with the guard fully ARMED, and assert it **SUCCEEDS**. That pins the blind spot as a measured fact about git, and it is the standing justification for the backstop existing at all. | **BAKED IN** |
| **F-B** | §3.4 | HIGH | The stdin tee used `mktemp`. This system's defining gate scar is a gate that depended on a binary that was not there (`powershell`+`python`, exit 127, silent, for weeks). **Use `"$(git rev-parse --git-path pre-push-stdin.$$)"` with a `trap` to remove it** — inside `.git/`, so it never travels and never lands in a commit, and it depends on nothing but git, which is already running. | **BAKED IN** |
| **F-C** | §3.1, §3.2 | MED | A2 asks for target + source + rule. That is a **diagnosis with no remedy** — `test_hooks_armed.py` case B exists for exactly this class ("an operator who cannot see the fix will not apply it"). Both refusals must also print what to do: `git merge --abort` (and the correct destination for that source class) for the guard; `git reset --hard origin/<lane>` or the `--no-verify` override for the backstop. **A2's assertion is widened to include the remedy string.** | **BAKED IN** |
| **F-D** | §6 F1 | MED | F1 (the `.git/MERGE_HEAD` worktree blindness in `sop-currency.sh:46` / `commit-msg-jira.sh:51`) traces to **no acceptance item**. By Phase 2's default disposition that is scope creep and gets **CUT**. It is a real defect and the ticket's own fold-1 instruction is what surfaced it, so it is **not** dropped silently — it is the operator's call at the approval gate. **Default if the operator says nothing: NOT built; fold 1 documents the caveat and F1 is filed as its own ticket.** | **OPERATOR'S CALL** |
| **F-E** | §3.5 | MED | `ARM_FLAGS` declares a `via` hook per flag, and `test_hooks_armed.py` case V asserts that a flag whose `via` hook is **untracked** reads NOT ARMED. So committing `MERGE-TARGET-ENFORCE` + the `ARM_FLAGS` row **without** `.githooks/pre-merge-commit` in the same commit turns the live-repo case A red mid-lane, on the whole suite. **The flag, the guard script, the dispatcher and the `ARM_FLAGS` row land in ONE commit.** | **BAKED IN** |
| **F-G** | §3.1, §3.2 | MED | Both designed holes (unclassified topology; missing `origin/main`) currently just allow. An unpinned hole widens silently. **Each must print one line saying it declined to judge and why, and each gets its own case** — N for the unclassified target, and a new **case O** for a backstop with no `origin/main` reference point. | **BAKED IN** |
| **F-F** | `session-start-context.sh:30` | LOW | Describes the push gate in prose; does not call it. No edit owed. | **CLEARED** |

**Four quick gates**
- **Verification strategy present?** Yes — §1 maps every acceptance item to the command that proves
  it, and §4 orders the work RED-first with a dedicated mutation pass (step 6).
- **Anything irreversible?** No. No delete, no rename, no force-push, no `main` merge, no Jira
  transition beyond `In Progress` (already done, idempotent).
- **Any step vague enough that the builder will guess?** The verdict table (§3.1) and the single
  backstop predicate (§3.2) are stated cell by cell. The ambiguity rule and both designed holes are
  written as rules, not as intentions.
- **Convention fit?** POSIX `sh` gate + dumb dispatcher + `*-ENFORCE` flag + `DISABLE` kill switch +
  `hooks_armed` row (the house shape); stdlib `Cases`/`TempDir` test auto-discovered by `run_all.py`;
  artifacts under `_artifacts/_main/<date>_<slug>/`; the SOP staged in the same commit.

**Audit verdict: GO**

Conditional on F-A, F-B, F-C, F-E and F-G being built as written above (they are now part of the
plan), and on **F-D being answered by the operator at the approval gate** — build it, or fold 1
documents the caveat and F1 becomes its own ticket.
