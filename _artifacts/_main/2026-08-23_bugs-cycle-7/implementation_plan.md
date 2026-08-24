# SCC-293 — Bugs and Updates, cycle 7 (CONSOLIDATED lane)

**Parent:** SCC-293 (Task) · **Riders:** SCC-301, SCC-302, SCC-303, SCC-306
**Branch:** `chore/SCC-293-bugs-cycle-7` · **Repo:** Sudo_Hatter_Command · **Date:** 2026-08-23
**Mode:** CONSOLIDATED — the ticket directs it verbatim (*"All Sub Tickets Are One Shot Under This
Ticket, Create One Branch And Working Tree"*), all four parts are same-repo toolkit files, and no
two parts share a source file.

**Cycle bookkeeping (done before this plan):** SCC-293 → In Progress; `jira_feed.py start --apply`
cloned **SCC-305** as cycle 8, handed `running-bug-list` to it, and SCC-293 now carries
`bugs-and-updates`. SCC-305's summary, INDEX and PREDECESSOR were rewritten with
`--description-file`, and it is parked in the **Rolling Tickets** column per operator convention.
SCC-295 and SCC-298 shipped as their own lanes earlier in this cycle and are **Done** — they are
not riders here.

⛔ **The start step could not run itself.** `jira_feed.py start` refused SCC-293 at exit 3 and the
roll never fired; the transition was hand-driven with `acli`. That is Part E.

---

## Build order

Measured, not preferred. **E → D → C → B.**

1. **E first** — it is the only part that fixes machinery this lane's own close-out will use, and it
   is the smallest diff. Landing it first means the cycle-8 roll is no longer hand-driven.
2. **D second** — `check_links.py` is a *gate* this lane runs at close-out. Its false-green is live
   today, so every later part is verified by a gate that can lie until D lands.
3. **C third** — `lane_qualify.py` changes which command the operator types; it depends on nothing
   here and touches the SOP, which D and E do not.
4. **B last** — the largest surface (engine prose + a `.claude/` mirror), and the only part whose
   subject is the review process itself. Landing it last means the earlier parts are reviewed by the
   engine as it exists today, and B's own change is reviewed once, cleanly.

⚠️ **C and E both edit `docs/_scc_sops_prds/workflows_testing_SOP.md`.** One lane, so they sequence
rather than collide — but each must re-read the file before editing; the second must not revert the
first. This is the only file two parts share.

---

## Part E — SCC-306 · `start` refuses before it rolls

**The measured defect.** `cmd_start` returns `3` at [`jira_feed.py:1634`](.agents/scripts/jira_feed.py#L1634)
for any status outside `STARTABLE` ([`:1407`](.agents/scripts/jira_feed.py#L1407) = `"to do"` /
`"to do next"`). That `return` sits **above** the `TRIGGER_LABEL` roll check at
[`:1672`](.agents/scripts/jira_feed.py#L1672), so a parked rolling ticket never clones its successor.
`Rolling Tickets` is a real operator column — SCC-186 *Standing Push Ticket* lives there permanently,
and SCC-305 is parked there now, as SCC-293 was. Reproduced on SCC-293 itself: the clone had to be
hand-driven.

**Why the file's own comment does not cover it.** The comment at `:1600` says the roll "is bound to
the ticket's **STATE**, not to the transition edge", and lists three routes that reached a dead end.
This is a **fourth**, and it is the one the operator's own board convention guarantees will recur
every cycle. The retry promised in `work-consolidation.md` and the SOP cannot fire from this column.

**SETTLED design question.** Operator convention (2026-08-23) parks the successor in `Rolling
Tickets`. So the column is correct and the code is wrong: the fix is **roll-before-refuse**, NOT
widening `STARTABLE`. `Rolling Tickets` must stay non-startable — SCC-186 lives there and must never
be transitioned — while still rolling.

**Acceptance**

| Row | Statement | Assertion that proves it |
|---|---|---|
| E1 | A ticket in a non-`STARTABLE` status holding `running-bug-list` clones its successor | stub-board test: status `Rolling Tickets` + trigger label → a clone call is issued |
| E2 | …and still exits `3`, having written **no transition** | same test asserts `code == 3` and no `transition` in the recorded argv |
| E3 | The existing held-status case keeps passing unchanged | `test_jira_feed.py:1374` green, untouched |
| E4 | A **spent** baton in the same status clones nothing | A2b control extended to the parked status; zero clone calls |
| E5 | The SOP no longer promises a retry that cannot fire | `sop_currency` staged; the rolling-cycle section states roll-before-refuse |

**Steps**

1. RED first: add the E1/E2/E4 cases to `tests/test_jira_feed.py` against today's code and watch E1
   and E4 fail for the right reason — E1 because no clone is issued, not because the stub errored.
   ⚠️ Scar `red-test-can-die-before-its-assertion`: assert the failure is the *absence of a clone*,
   not an `AttributeError`.
2. Move the `TRIGGER_LABEL` block above the `STARTABLE` refusal in `cmd_start`. It must run before
   the `return 3` and must not alter the returned code.
3. Confirm ordering against the two paths that already roll (`already In Progress`, post-transition)
   — three call sites must not become three copies; extract one helper if it reads better.
4. Update the SOP's rolling-cycle section to state what the code now does.

---

## Part D — SCC-303 · `check_links` reports clean on a set it narrowed silently

**The measured defect.** In default `--base` mode, `main()` builds its file list from
`git diff --name-only <base>...HEAD` ([`check_links.py:284-288`](.agents/scripts/check_links.py#L284-L288)),
which is **tracked-only by construction** — an untracked `.md` is invisible. On the SCC-295 lane the
walkthrough was untracked when the gate ran; the gate printed *"3 markdown file(s), 23 path claim(s)
checked / clean"* and exited 0. Once staged, that same file carried **four dead paths**.

**Why the existing guard does not catch it.** The author already knew empty scope is a false pass —
`if not files` at [`:293`](.agents/scripts/check_links.py#L293) says so in capitals. The **partial**
case has no equivalent, and partial is the case that ships. The success line reports a COUNT and
never the NAMES, so nothing in the output distinguishes "three files, all clean" from "four were in
scope and one was invisible".

**Acceptance**

| Row | Statement | Assertion that proves it |
|---|---|---|
| D1 | An untracked `.md` carrying a dead path does not produce a clean exit 0 | test: write an untracked `.md` with a dead path in a diff'd dir → non-zero, or named as skipped |
| D2 | Every run prints the scanned file **names**, not only a count | test asserts each scanned filename appears in stdout |
| D3 | `--base` mode detects untracked `*.md` under the diff's directories | test: untracked file in scope is either scanned or explicitly named |
| D4 | The empty-scope guard at `:293` still refuses to read as a pass | existing behaviour re-asserted |
| D5 | `--paths` and `--all` modes are unchanged | their existing cases stay green |

**Open decision for the build:** whether an untracked in-scope `.md` is a **warning** or a
**refusal**. It is a false green either way. Default to **refusal** — this gate's whole job is to be
believed, and D1 is written to accept either, so the choice is recorded in the walkthrough, not
smuggled.

---

## Part C — SCC-302 · `lane_qualify` sizes by path prefix, not blast radius

**The measured defect.** `classify()` decides by **path prefix alone**
([`lane_qualify.py:136-141`](.agents/scripts/lane_qualify.py#L136-L141)): any path under
`TOOLKIT_PREFIXES` returns `TASK` — the full `/smh-quick-dev` lane. A one-character string fix and a
forty-file rewrite are **indistinguishable** to it. SCC-295 was one line in one function; the
operator asked for `/smh-quick-fix`, the qualifier ejected it to the full lane, and the lane consumed
a whole session and an entire context window for a change the operator said they should have made by
hand.

**And there is nowhere to eject to.** The verdict set is `LIGHT` / `LIGHT-VCS` / `TASK` / `HANDOFF` /
`NOT-COMMAND-CENTRE` ([`:83`](.agents/scripts/lane_qualify.py#L83)) — a toolkit change is either the
lightest lane or the heaviest one, with nothing between.

**Acceptance**

| Row | Statement | Assertion that proves it |
|---|---|---|
| C1 | `classify()` takes a blast-radius signal (line count, file count, or explicit `--lines`) | signature + CLI flag exist and are exercised |
| C2 | A one-line toolkit edit and a multi-file toolkit rewrite return **different** verdicts | `test_lane_qualify.py`: two calls, two verdicts |
| C3 | A one-line change under a `PRODUCT_DIRS` path still returns `HANDOFF` | size never buys an exception |
| C4 | `NOT-COMMAND-CENTRE` still wins regardless of size | existing case, re-asserted with a size argument |
| C5 | The SOP says which command the operator now types | `sop_currency` staged |

⛔ **Hazard for C3/C4 — do not reach for `.github/` as the deployable fixture.** `lane_qualify`
imports `PRODUCT_DIRS`, **never** `DEPLOY_DIRS`, and the difference is a shipped incident (SCC-118,
argued at [`:65-77`](.agents/scripts/lane_qualify.py#L65-L77)): `DEPLOY_DIRS` is `PRODUCT_DIRS +
(".github/",)`, and `.github/` is *toolkit* here, not deployable. So `.github/` returns `TASK`, not
`HANDOFF`. C3's fixture must be a genuine `PRODUCT_DIRS` path or the test asserts the opposite of
what it claims. This lane touches no `.github/` path, so the tension itself is out of scope.

**Open decision for the build:** the **third door** — a new middle verdict, or a documented
small-toolkit rule *inside* `TASK` that skips the review fan-out. ⚠️ A new verdict needs an exit code,
and `VERDICTS` at `:83` maps verdicts to exit codes that callers already branch on — adding one is a
contract change with callers to find. Prefer the in-`TASK` rule unless the build proves it cannot
carry the signal. Decision recorded in the walkthrough either way.

⚠️ AUDIT FINDING (F3): `test_lane_qualify.py:141-148` pins *"never more permissive than the armed
commit gate"* — every path `sop_currency.classify()` calls a usage surface must come back
**non-LIGHT** from this script. Whatever the third door is, a toolkit path must never resolve to
`LIGHT`/`LIGHT-VCS`, or that cross-check fails and the drift it guards (an agent widening its own
lane) reopens. The middle verdict, if minted, sits strictly between — and the existing F3 case
(`the enforcement suite is TASK`) must keep passing, so `.agents/scripts/tests/` stays full-lane.

---

## Part B — SCC-301 · Review lenses run in the builder's worktree

**The measured defect.** Measured twice — the SCC-298 and SCC-295 lanes. The engine launches lenses
with a clean **context** but never an isolated **tree**
([`step-01-review.md:27`](.agents/skills/code-review-engine/steps/step-01-review.md#L27)), so every
lens inherits write access to the worktree under review. On SCC-295 three of five lenses edited the
builder's working tree mid-review, and one reported a RED test returning `rc/a.py` — **a result no
version of the code under review can produce.** The builder was reading a lens's own mutant and
nearly acted on it. A review that can rewrite its own subject cannot certify anything, and the roster
records it `ok` either way.

**Also live on main:** the sentence at `:27` is **duplicated** at `:29-31`, introduced by `aafe0d4`
(SCC-190). Confirmed present in this tree.

**Acceptance**

| Row | Statement | Assertion that proves it |
|---|---|---|
| B1 | Step 01 states the **tree** half, not only the context half | source assertion on the isolation wording |
| B2 | Isolation is decided **per lens** — Blind Hunter needs no tree (DIFF only); the three repo-reading lenses need a read-only copy, not the builder's | the lens table carries an isolation column, one row per lens |
| B3 | The engine's return states the isolation mode, as it already states `review-runtime` | `SKILL.md:69` and `step-04-record.md:52` carry the new field |
| B4 | A lens that writes to `WORKTREE` is a **hard failure**, not a warning | stated in the contract, and asserted |
| B5 | The duplicated sentence at `:27-31` is gone | source assertion: the sentence appears once |
| B6 | `.claude/skills/code-review-engine/` stays **byte-identical** | `git diff --no-index` between the two trees returns 0 |

⚠️ **Source-grep scars apply to B1/B4/B5.** A source-grep guard is blind three ways — a comment
matches first, it cannot see order, and prose-pinning is vacuous. Pin the **wiring** (the isolation
field, the per-lens column) and make each guard fail a mutant before trusting it.

---

## Port checklist — NOT TRIGGERED, proved not asserted

`.agents/rules/port-checklist.md` MANDATORY RULE 5 fires when a SCOPE file exists in more than one
repo. Checked all three scripts:

```
find Projects -path "*/.agents/scripts/lane_qualify.py"   -> no match
find Projects -path "*/.agents/scripts/check_links.py"    -> no match
find Projects -path "*/.agents/scripts/jira_feed.py"      -> no match
```

Each exists **once**, in this repo. No port section is owed.

The `code-review-engine` mirror is a **same-repo** pair, not a port, and it is byte-identical today:

```
git diff --no-index -- .agents/skills/.../step-01-review.md .claude/skills/.../step-01-review.md
differ=0
```

That is B6's baseline: the mirror is equal now and must be equal after.

---

## Declared Change Set

- EDIT `.agents/scripts/jira_feed.py` — move the roll check above the STARTABLE refusal in `cmd_start` → E1, E2, E4
- EDIT `.agents/scripts/tests/test_jira_feed.py` — parked-status roll cases and the extended A2b control → E1, E2, E3, E4
- EDIT `.agents/scripts/check_links.py` — print scanned names; detect untracked in-scope markdown in `--base` mode → D1, D2, D3
- EDIT `.agents/scripts/tests/test_check_links.py` — untracked dead-path case, name-printing case → D1, D2, D3, D4, D5
- EDIT `.agents/scripts/lane_qualify.py` — blast-radius signal into `classify()` and the third door → C1, C2, C3, C4
- EDIT `.agents/scripts/tests/test_lane_qualify.py` — size-separated toolkit verdicts; HANDOFF and NOT-COMMAND-CENTRE hold → C2, C3, C4
- EDIT `.agents/skills/code-review-engine/steps/step-01-review.md` — per-lens tree isolation; delete the duplicated sentence → B1, B2, B4, B5
- EDIT `.agents/skills/code-review-engine/SKILL.md` — the return states the isolation mode → B3
- EDIT `.agents/skills/code-review-engine/steps/step-04-record.md` — the recorded roster carries it → B3
- EDIT `.claude/skills/code-review-engine/steps/step-01-review.md` — byte-identical mirror → B6
- EDIT `.claude/skills/code-review-engine/SKILL.md` — byte-identical mirror → B6
- EDIT `.claude/skills/code-review-engine/steps/step-04-record.md` — byte-identical mirror → B6
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — C's command change and E's corrected retry promise → C5, E5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line per SOP delta, same commit (sop-currency habit 4) → C5, E5
- NEW `_artifacts/_main/2026-08-23_bugs-cycle-7/implementation_plan.md` — this plan → all
- NEW `_artifacts/_main/2026-08-23_bugs-cycle-7/task.yaml` — the lane manifest → all
- NEW `_artifacts/_main/2026-08-23_bugs-cycle-7/tickets/SCC-306.md` — Part E's ticket outline → E1

---

## Known scars this lane must not re-hit

- **`echo` truncates at `\c`** — use `printf` in any assertion output.
- **Piping a gate hides its exit code** — run gates bare.
- **A fixture naming a retired file is a live surface** to a source-grep guard (cost SCC-295 a `CS-15 G` trip).
- **`mutation_sweep.py`** needs `"unfiltered": true` for a test file declaring no `c.block()`.
- **Commit messages with backticks EXECUTE** — commit with `-F <file>`, never `-m "…"`.
- **Verify the OUTCOME of a board write, never the exit code** (`work-consolidation` rule 6).

---

## Self-Audit (2026-08-23)

**Level: LEDGER+BLAST** (scripts others import, a gate, a door surface, the SOP, a >1-platform mirror) · **Mode: PRE-WORK**

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  all 17 declared paths exist on disk · DCS parses (17 entries, 0 incomplete after F1 fix) ·
             plan line-refs spot-checked against the tree (lane_qualify.py:136-141, check_links.py:284-293,
             jira_feed.py:1407/1634/1672, step-01-review.md:27-31 duplication CONFIRMED present) ·
             lane fit: lane_qualify --paths <declared set> → TASK, zero deployable hits ·
             both-machines: plan runs python3/stdlib only, no venv
read:        declared_change_set.py parse output · lane_qualify.py · check_links.py · jira_feed.py ·
             step-01-review.md · task.yaml (riders re-parsed with task_preflight's own RIDERS_RE: 4/4)
verdict:     findings below (F1)
```

```
lens:        2 Parity + Blast
checks_run:  script callers: check_links ← 4 command bodies + SOP · lane_qualify ← quick-fix/non-crit doors,
             3 workflow launchers, rules, SOP · jira_feed ← .githooks/post-commit → post-commit-jira-start.sh ·
             hook contract read: marker written ONLY on settled (0), exit 3 re-asks — E preserves both, and
             NO test pins the current refusal-before-roll order (grep of test_jira_start_hook.py: no match) ·
             twins: engine is invoked BY both cicd- and smh-code-review; internals change, caller contract
             (verdict vocabulary, review-runtime) unchanged · gate pairing: SOP edit requires changelog line
             SAME commit (sop-currency habit 4) · siblings: fetched origin/main, then per-tree diff
read:        .githooks/post-commit · post-commit-jira-start.sh · test_jira_start_hook.py ·
             test_lane_qualify.py:112-148 · SOP_changelog.md header · sibling diffs (2 trees)
verdict:     findings below (F1, F2, F3)
```

```
lens:        3 Pre-Mortem (bounded — attaches only)
checks_run:  failure narratives attached to F1 and F2; nothing unanchored kept
read:        (the findings above)
verdict:     attachments below
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md:8` | "the delta description goes **here**, as one line, in the same commit" | plan edits the SOP twice (C5, E5) but never declared the changelog file — the review drift check reads the paired edit as undeclared drift, or the habit is skipped silently | important — **FIXED inline** (declared, 17th entry) |
| sibling `claude/teaching-edition` + `chore/SCC-304…` diffs | both lists contain `workflows_testing_SOP.md` + `…_changelog.md` | **landing-order dependency**: whichever of the three lanes lands last reconciles the SOP by hand; if a sibling lands mid-build, C5/E5 hunks may no longer apply | important — named, not fixable here |
| `test_lane_qualify.py:141` | "drift - never more permissive than the armed commit gate" | Part C's third door could resolve a usage surface lighter than sop_currency and fail this pinned case — the exact widening it exists to stop | important — **FIXED inline** (constraint baked into Part C) |
| `.agents/scripts/git-hooks/post-commit-jira-start.sh:29-31` | "The marker is written ONLY on a SETTLED result" | (pre-mortem attachment to E) if E accidentally changed exit 3→0 on the parked path, the hook would write its marker and never re-ask — E2 exists precisely to pin this | (attached to E2, no new finding) |

### Observations (uncounted)
- `risk_seam.py classify` returns `unclassified` here permanently and correctly (SCC-289) — judgments above taken from the diff, per the command.
- Part B's `.claude/` mirror write was probe-verified this session (sandbox off); SCC-300's block does not apply.
- The labeller (`/smh-label-tasks`) is skipped, stated per work-consolidation: one consolidated tree, 4 sequential parts, the only shared file (SOP + its changelog, C↔E) already sequenced by the build order. Nothing runs side by side, so `parallel-ok` has no set to describe.

Audit verdict: GO

**Batch approval (2026-08-23):** "approved" — given after the four-part breakdown (B/C/D/E) was
presented and Part E minted; reaffirmed after the plan was written: "continue with this fix this
one is important its costing us alot of time. we need to fix these" — covers the plans listed in
`/smh-plan-task SCC-293` Step 5: SCC-301, SCC-302, SCC-303, SCC-306 (one consolidated plan, four
part sections). — recorded at f13eef9
