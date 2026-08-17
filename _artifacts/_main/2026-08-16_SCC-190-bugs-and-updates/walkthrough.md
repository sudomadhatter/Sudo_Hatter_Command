review-runtime: fan-out

# Walkthrough — SCC-190 · Bugs and Updates 2026-08, the rolling ticket RUN as one lane

**Lane:** `chore/SCC-190-bugs-and-updates-2026-08` · worktree `.claude/worktrees/SCC-190-bugs-and-updates` · cut off `origin/main` @ `654f7e2`
**Riders:** SCC-191 (R) · SCC-192 (S) · SCC-193 (T) · SCC-195 (U) — full landing, so every rider flips and the parent closes.
**Operator:** *"lets do SCC-190"* · *"this will be one tree and one branch for all of them, we will do them all then close it out"* · *"yeah its stuck there and thats why SCC-195 fixes it"* (on SCC-194) · *"i wording only"* (S6) · *"approved"*.

**What this lane is.** SCC-190 is the rolling ticket its own Part R writes the rule for, and running it is the first turn of the cycle that rule describes: four subtasks, one tree, one branch, one ceremony. Three of the four parts come from defects measured on **SCC-164's own landing** — the close-out that was hand-run instead of invoked, and left nothing behind to say so.

---

## Task Checklist

- [x] **Part S (SCC-192)** — the ceremony leaves receipts the PR gate requires
  - [x] S-A `task_preflight.py` writes `preflight-receipt.json`, keyed on the verdict sha
  - [x] S-B `main_write_gate.py --mode pr` refuses a close-out PR without the receipts
  - [x] S-C the door names the receipt at Step 1 and commits it at Step 2.5
  - ⚠️ **The ticket's own scoping would have bricked the lightweight lane** — found before a line was written, fixed in the design. See *What fought back* #1.
- [x] **Part T (SCC-193)** — the six slips: four one-shot fixes and the sign-off wording
  - [x] T-A fetch is the default; freshness is ON the verdict line; omitted and failed are one severity
  - [x] T-B `## Your Actions` refuses the ceremony's own steps
  - [x] T-C `--after-merge` warns when the door text being read may be the pre-merge copy
  - [x] T-D the SCC-175 merge-row pin, with and without `GITHUB_TOKEN` — **green both ways**
  - [x] T-wording the sign-off is the operator's DECISION, on every surface, pinned both directions
  - [x] S6 settled by the operator: **(i) wording only** — the click stays physical
- [x] **Part R (SCC-191)** — Rule 1's fourth rung and the run-or-split cycle
  - [x] SCC-190 labelled `bugs-and-updates`, read back through the rule's own jql:
    `acli ... --jql "project = SCC AND statusCategory != Done AND labels = bugs-and-updates"` returns SCC-190
- [x] **Part U (SCC-195)** — the Antigravity menu budget moves into the generator
  - ⚠️ The first cut applied the budget to the Claude/Codex skill doors too and turned 39 correct doors red. See *What fought back* #2.
- [x] Consequences of this lane's own edits: the AP twin, the ORPHAN block guards, the INDEX row, the hand-authored skill door

---

## Evidence

Every part was written RED first. Full transcripts are the pasted blocks below; the sweeps are in `sweep-part*.json` / `sweep-part*-result.txt` beside this file.

### Part S-A + T-A · the preflight receipt and the default fetch

**RED** — `python3 .agents/scripts/tests/test_task_preflight.py --case "SCC-192/193"`, before any edit to `task_preflight.py`:

```
[FAIL] R1 a preflight with NO flag fetches, and says the comparison is fresh: exit 0: md
[FAIL] R1 ...and leaves a receipt beside the lane's task.yaml: _artifacts/_main/2026-08-08_scc-11-thing/preflight-receipt.json
[FAIL] R1 the receipt records the key, the branch and the FLAGS IT RAN WITH: {}
[FAIL] R1 the receipt carries the VERDICT the agent acted on, and its exit: {}
[FAIL] R1 ⛔ keyed on the VERDICT sha, never on HEAD: {}
[FAIL] R4 a re-run rewrites byte-identical content (no churn commit): the receipt moved on a no-op run, or was never written
[FAIL] R2 ...the VERDICT line itself names the staleness, and the exit is non-zero: exit 2: usage: task_preflight.py [-h] --expect-key ...
[FAIL] R2 ...an omitted fetch is a WARN, not an info footnote
[FAIL] R2 ...and the receipt records that it ran without one: {}
[FAIL] R3 a FAILED fetch reaches the same verdict as an omitted one: exit 0: md
[FAIL] R3 ...and the receipt says the fetch was ASKED FOR but is not fresh: {}
[FAIL] R3 ...a failed fetch is still only a WARN — offline is not a defect
-- 4/16 passed --
```

⛔ **The first red DIED IN SETUP and was rewritten before it was believed.** `(repo / RECEIPT).read_bytes()` on a file that does not exist raises `FileNotFoundError`, which killed the file at R4 — four cases never ran, and a crash reads nothing like a failed assertion. The helper now returns `b""` for an absent receipt, and the block above is what a real red looks like: twelve assertions, every one of them reached.

**GREEN** — same command, after the implementation:

```
-- 16/16 passed --
```

**No regression** on the files that drive this script: `test_task_preflight.py` 173/173 · `test_task_preflight_receipts.py` 38/38 · `test_hooks_armed.py` 66/66 · `test_closeout_preflight.py` 29/29 · `test_door_preflight_order.py` 15/15 · `test_flight_recorder.py` 44/44.

**Two fixtures were re-aimed, and neither was weakened.** Two SCC-159 cases spelled *"not fresh"* as **omit `--fetch`** — true while the flag was opt-in, and the exact opposite once it defaults on. Left alone they would have asserted that a lane measured against a *fresh* fetch only warns about a stalled `main`, which is the one reading SCC-159 rules out. They now pass `--no-fetch`; the assertions are untouched. And `test_hooks_armed`'s live-repo case gained `--no-fetch --no-receipt`: it runs against the REAL repo, and without those flags the suite would fetch over the network on every run and write a receipt into the tree it is testing — which the next `gate_receipt` run would then record as `DIRTY`.

### Part S-B · the PR gate requires the receipts

**RED** — `--case "SCC-192"` on `test_main_write_gate_ci.py`, before `check_close_out_receipts` existed:

```
[PASS] A4 GREEN: both receipts present, keyed on the verdict sha, TWO artifacts-only commits after them
[FAIL] A1 RED: a reviewed close-out with NO flight event is refused, by name
[FAIL] A2 RED: no preflight receipt is refused, by name
[FAIL] A3 RED: a receipt whose comparison was NOT fresh is refused, naming the flag
[FAIL] A3b RED: a receipt from ANOTHER branch does not vouch for this lane
[FAIL] A3c RED: a receipt recording a BLOCKED verdict is not a pass
[PASS] A5 GREEN: a PR with no task.yaml is not a close-out and owes nothing
[PASS] A5b GREEN: a lightweight lane (manifest + receipt, no verdict stamp) lands
[PASS] A5c GREEN: a manifest naming another door owes this gate nothing
[PASS] A-mode GREEN: mode `gate` never asks for receipts (Road 2 untouched)
-- 43/48 passed --
```

The five GREEN controls pass **before** the change as well as after — that is what makes them controls: each one is a way the gate could become a loop nothing can push through, and each stays open by construction.

**GREEN** — `-- 48/48 passed --`.

### Part T-B · the ceremony's steps are not `Your Actions` entries

**RED** — `--case "SCC-193 B"`:

```
[FAIL] B0 the content check exists: jira_feed.ceremony_rows is missing - `## Your Actions` has no content rule
-- 0/1 passed --
```

⛔ Existence is its own case **because the first attempt crashed the file** with `AttributeError: module 'jira_feed' has no attribute 'ceremony_rows'`. A crashed file is not a red, and a mutant that deletes the detector outright would have sailed past it; B0 kills that mutant now.

**GREEN** — `-- 15/15 passed --`, and the whole file `-- 293/293 passed --`. The fixture is SCC-164's two rows verbatim from `5dcc1b7`:

```
- [ ] **Click **Merge** on the PR.** `main-write-gate` is a required check and `bypass_actors` is
  empty, so nothing lands until you do. That click is the sign-off.
- [ ] **Then re-invoke** `/smh-close-task-merge-tree --after-merge SCC-164`. That second call is
  what writes `Done` to SCC-164 and all six riders; the door opens the PR and **stops**.
```

Both refused, with *"this section holds what only the operator decides; the ceremony's steps are not entries."* Seven controls stay green, including the two boundary rows: the door's own ledger line, and a bare door invocation.

### Part T-D · the SCC-175 pin — **a characterization check, written GREEN, and said so**

`--case "SCC-193 D"` → `-- 6/6 passed --`, with and without `GITHUB_TOKEN` in the environment.

**This did not reproduce the suspected defect, and that is the reported result.** SCC-193 recorded that at SCC-164's `finish --apply` the ticket was HELD on 2 rows with **no** `merge row SATISFIED/HOLDS` line printed — i.e. `merge_row_state` returned `None` — while a dry run on the identical committed file the next day printed SATISFIED and held 1. The pin reproduces that shape (a ticked ledger row, an open click row, the lane landed) and `merge_row_state` resolves correctly **both ways**:

```
[PASS] D1 without GITHUB_TOKEN: the merge row RESOLVES (never a silent None)
[PASS] D1 without GITHUB_TOKEN: ...and the landed lane SATISFIES it
[PASS] D1 without GITHUB_TOKEN: the click row is NOT a merge row, so exactly 1 holds
[PASS] D1 with a stale GITHUB_TOKEN in env: (all three, identical)
```

Per the ticket's own instruction — *"if green, the --apply-time hold was environmental and the test says so forever"* — that is the finding: **environmental, not a defect in `merge_row_state`**, and now pinned either way. A green characterization check presented as a red would be the dishonest version of this section.

### Part T-C + T-wording

**RED** (`--case "SCC-193"`), before the door and the surfaces were rewritten:

```
[FAIL] S5 no surface still says the merge is the operator's to perform: 25 hit(s): git-policy.md:83 ...
[FAIL] S5 ...and .agents/rules/git-policy.md states the ruling positively: missing: 'decision to proceed is the sign-off'
[FAIL] S5 ...and .agents/commands/smh-close-task-merge-tree.md states the ruling positively
[FAIL] S5 ...and the door names the form: `approved`
[FAIL] C2 it measures the checkout against origin/main
[FAIL] C3 ...and says the door text may be the PRE-merge copy
```

**GREEN** — `-- 24/24 passed --`. The pin runs **both directions**: the retired phrases appear on no surface, *and* the ruling's sentence plus its three forms appear on the two surfaces an agent reads before it acts. A one-way pin is satisfied by deleting the sentence.

⚠️ **`per-merge sign-off` was in the first forbidden list and was taken out** — the pre-work audit's finding F2, confirmed by measurement. Two of the three forms the ruling names **are invocations**, so *"invoking it is the operator's per-merge sign-off"* is **true**; banning it would have deleted a true sentence from five surfaces while leaving the false ones standing.

### Part R · Rule 1's fourth rung

**RED** (`--case "SCC-191"`) → `-- 0/9 passed --`, including `R1a Rule 1 has FOUR rungs: 3: ["Does this lane's own ticket cover it?", 'Is there an OPEN parent...', 'Nothing fits?']`.
**GREEN** → `-- 11/11 passed --`, and the whole file `-- 110/110 passed --`.

### Part U · the Antigravity menu budget

**RED** → `[FAIL] U6 every .agents/workflows door fits Antigravity's menu budget: 34 over 135` — the same 34 files `chore/SCC-194-workflow-titles` tried to fix by hand.

**GREEN** → `-- 110/110 passed --`, after `sync-agents.ps1 -NoGlobals` regenerated the mirrors.

**The measurement that is the ticket:**

| | descriptions | total chars |
|---|---|---|
| before | 36 | **13,883** |
| after | 36 | **4,590** |

**−67%**, and no door over 135 characters. The commands keep their full descriptions — only the menu has a budget, and `U7` is the control that fails if the shortening ever leaks into `.agents/commands/` (41 long brains today).

### The lane's gates

Run **once**, at the tip, on a clean tree, through the receipt writer — the receipt run *is* the suite run, never a second opinion:

```
python3 .agents/scripts/gate_receipt.py run --task SCC-190 --gate suite \
    --root _artifacts/_main/2026-08-16_SCC-190-bugs-and-updates --cwd . \
    -- python3 .agents/scripts/tests/run_all.py

[PASS] suite exit=0 116.6s @ f9367660
        receipt: gates/suite.json

  (run_all's own last lines)
  -- 49/49 passed --
  ============================================================
  33/33 files passed
```

The receipt records `result: pass · exit_code: 0 · dirty_tree: false · sha f9367660 · 116.6s`, so the close-out and the review inherit this run instead of paying for it again.

```
python3 .agents/scripts/workflow_lint.py --toolkit-only      -> -- 0 error(s), 0 warning(s), 8 info --
python3 .agents/scripts/check_maps.py --depth3-only --strict -> exit 0
```

### The mutation sweeps

Four tables, one per part, declared **before** the sweep ran and drawn from the shipped code rather than from the cases (SCC-144: 14 case-derived mutants were all killed while a later set drawn from the code left 24 of 25 surviving). Records: `sweep-part{S,R,T,U}-result.txt`.

**⭐ ROUND 1: 13 killed, 8 SURVIVED — and eight of the eight were defects in this lane's own assertions.** That is the sweep working; a first sweep that kills everything is the result worth doubting. Each survivor is closed by a **case**, not by re-aiming the mutant — with one exception, named as such:

| survivor | why it survived | what closed it |
|---|---|---|
| **R-M2** delete the label from the search block | `"bugs-and-updates" in body` matched rung 3's **prose** — so deleting the jql line, the executable half an agent actually runs, was invisible | the check now reads the **fenced search block** only |
| **R-M3** retitle the cycle section | `"cycle" in body` matched the operator's quoted ruling (*"thats the cycle"*) | the cycle needs its own `###` **heading** — which is exactly how a cycle decays into a footnote |
| **T-M2** drop the ledger-row exemption | the canonical row trips **no pattern even without it**, so the control was passing for the wrong reason | `B3b` uses a row that *is* flagged without the exemption (`The merge itself — click Merge on the PR`) — the wedge the exemption exists to prevent |
| **T-M4** remove the re-invoke pattern | SCC-164's row also carries `--after-merge`, so it matched **two** patterns and removing one changed nothing | `B1b` trips exactly one |
| **T-M5** `finish` stops refusing | ⛔ **the sharpest.** Only `check-actions` was tested, so deleting the refusal from `cmd_finish` left every case green — the detector existed and the close-out ignored it. That is acceptance **S2** itself | `B6`: `finish` exits 2 **and the board stub proves nothing was written**, plus a control that an honest decision row still HOLDS (3), not refuses (2) |
| **U-M3** cut ignores the word boundary | "the cut is a prefix of the original" is true of a **hard** cut too | the character after the kept text must be a **space** |
| **U-M4** budget loop stops appending | "0 doors over budget" out of **0 doors read** is the vacuous green | `U6b` counts the doors; `U6c` asserts the whole menu payload (4,590 chars, was 13,883) |
| **S-M7** rewrite the receipt unconditionally | the only badly-aimed **mutant**: padding by `len(HEAD)` is a constant, since a sha is always 40 chars — it modelled nothing | re-aimed at the defect it meant to describe (a receipt that **embeds** HEAD), which `R1` and `R6` both kill |

**ROUND 2 — and it found one more of the same class, in the control written specifically to fix T-M2.** `B3b` used a **ticked** box (`- [x]`), and `open_actions` returns **unchecked** rows only — so the row never reached a pattern at all, exemption or not. A control that cannot fail is the thing this whole discipline exists to catch, and it appeared *inside the fix for a survivor*. The box is now open, and the row does match `click **Merge` without the exemption.

Round 2 also produced four `SWEEP ERROR`s rather than kills, and that is the harness being right: renaming a case to strengthen it breaks the table's **attribution**, and `mutation_sweep.py` refuses to credit a kill to a case that did not fail. The tables were re-aimed at the new names — selection and attribution are different namespaces, which this lane got wrong twice.

**ROUND 3 found two more of the same class in Part U**, and neither was a false alarm:

- **U-M3** passed against a *lucky string*: `LONG`'s 132nd character lands just after a full stop, so `rstrip` leaves a clean word boundary even with the boundary search **deleted**. `U3b` now puts a 27-letter word across the cut, where only a real backward search can end cleanly.
- **U-M4** exposed the shape of every live-tree sweep: a passing run is by definition a run with **nothing to report**, so a detector that stopped recording offenders reads exactly like a clean tree. `U6d` re-runs the predicate against a **fabricated** over-budget door, where it must fire. A live sweep plus a synthetic offender is what makes *"0 over budget"* mean anything.

**THE RECORD THAT STANDS — 22 mutants, 22 killed:**

```
SWEEP S  7/7   S-M1 receipt keyed on HEAD · S-M2 fetch back to opt-in · S-M3 freshness off the
               verdict line · S-M4 omitted fetch back to info · S-M5 self-dirt exemption widened
               to all of _artifacts/ · S-M6 receipt written with no live manifest · S-M7 the
               receipt embeds HEAD
SWEEP R  4/4   R-M1 rolling ticket dropped from rung 3 · R-M2 label dropped from the search block
               · R-M3 the cycle retitled to a footnote · R-M4 the engine's restatement goes stale
SWEEP T  6/6   T-M1 ceremony check disabled · T-M2 ledger-row exemption dropped (the wedge) ·
               T-M3 click pattern loses its verb binding · T-M4 re-invoke pattern removed ·
               T-M5 finish stops refusing · T-M6 the merge row read off the tick again
SWEEP U  5/5   U-M1 budget raised past every description · U-M2 ellipsis dropped · U-M3 cut
               ignores the word boundary · U-M4 the budget rule stops cutting · U-M5 door parity
               accepts any antigravity body (the check that made SCC-194 unlandable)

-- restore verified after every sweep: bytes match, nothing committed, `git diff --quiet` clean --
-- each sweep ends with the FULL file unfiltered: exit 0 --
```

**Three rounds, ten findings, and every one was an assertion of mine rather than a defect in the code.** That is the honest summary: the code the sweeps attacked held up; the checks guarding it did not, until they were made to.

---

## What fought back

**1 · SCC-192's own scoping would have made the lightweight lane unlandable — caught at plan time, not at review.** The ticket says the PR gate should demand a flight event from every PR whose `task.yaml` names this door. But `/smh-quick-fix` writes exactly that manifest and has **no review step**, so its walkthrough carries no `Verdict:` stamp — and `flight_recorder.py build_event` *dies* without one (`no canonical Verdict: ... @ <sha> line`). Measured before writing a line: **10 landed lobby lanes** have a door manifest and no stamp. Demanding the event unconditionally would have red-checked every lightweight landing forever — breaking SCC-192's own loop-3 constraint, on the ticket that was written to prevent exactly that. The receipt is required of every close-out; the event only of a lane that was **reviewed**, which is the lane that can produce one. `A5b` is that case.

**2 · The budget rule, applied one level too wide, turned 39 correct doors red in a single edit.** `is_launcher_for` is shared by the Antigravity workflow launchers *and* the Claude/Codex skill doors. Teaching it the truncation rule made every skill door read as drifted, because those carry the brain's **full** description and must keep doing so — Antigravity's menu cap is not a house style. `budgeted` is now a per-surface flag, and `launcher_ok` (true only on `.agents/workflows`) is what sets it.

**3 · The door Claude actually loads was stale, and no sync would ever have fixed it.** `.agents/skills/smh-close-task-merge-tree/SKILL.md` is **hand-authored** — no `GENERATED` marker — so `/smh-sync-agents` never rewrites it. Every generated door around it got the new wording while it went on saying *"Invoking this skill is the operator's per-merge sign-off"* beside a description claiming the click is the sign-off. Found by reading the door, not by running the sweep: the parity checks compare generated doors to their brains, and a hand-authored door is exempt from exactly that comparison.

**4 · Adding one `c.block` to a file makes every other check in it an ORPHAN.** `test_suite_runner.py` enforces that a file using block guards has *no* `c.check` outside one — so wiring the first block into `test_door_preflight_order.py` and `test_main_write_gate_ci.py` broke both. Correct rule, and the fix is right: every pre-existing section is now a named block (which also makes `--case` work there). Shared fixtures stayed **outside** the guards — under a filter a sibling block does not run at all, and SCC-156 paid for that lesson with five files.

**5 · The AP twin.** Editing `cicd-code-review.md` staled `cicd-code-review-AP.md`'s `ap_reconciled` stamp. The `## Your Actions` wording **was ported** rather than recorded as a deliberate divergence — it is a machine contract `jira_feed.py` now enforces, so a twin without it would write rows the close-out refuses.

**6 · `--case` filtering with an unset variable.** Two sweep runs early on selected nothing; the harness exit code 3 (not a kill, not a survivor) is what said so, and the `block` vs `case` namespace split in the table is what fixed it.

---

## Decisions

- **S6 — the click stays physical (operator: *"i wording only"*).** Reading (i) of the two: the sign-off is the **decision**, and the click on *Merge pull request* is how that decision reaches GitHub. SCC-183's mechanism — one click, one merge, held by something that cannot be talked out of it — is unchanged. Recorded in the door's Rule 1 with the operator's words.
- **The receipt is keyed on the verdict sha, not the resolved HEAD the ticket's Part A asked for.** A receipt carrying HEAD can never be byte-stable, because committing it moves HEAD; SCC-192's own loop-1 constraint says never key on HEAD, and it wins over its Part A wording.
- **`--no-receipt` exists, and the close-out never passes it.** It is for probes and harnesses that must not write into the tree they are measuring.
- **The hand-owned Antigravity door is shortened in place, not exempted.** The sync never rewrites `smh-adviser-board.md`, but Antigravity reads it into the same menu; exempting it would have left the single biggest row while the check reported the budget met.
- **`sync-agents.ps1 -NoGlobals`**, so this machine's opencode/Antigravity/Codex caches keep `main`'s content until this lane lands.

## Pitfalls

- A red that dies in setup looks exactly like a red that fails its assertion (`task_preflight.py` receipt case, and again on `ceremony_rows`). Both were rewritten before they were believed.
- `main_write_gate.py` had no artifact reader at all; it now imports `VERDICT_RE` / `strip_fenced` / `manifest_field` from `task_preflight` rather than re-typing them — a gate and a door disagreeing about what a verdict *is* is the defect class this file exists for.
- The full enforcement suite takes ~2 minutes and a mutation sweep several; both were run to completion rather than sampled.

---

## Memory files the operator may want to revisit (NOT edited — SCC-193 S7)

The wording ruling touches what four memories say. **None was changed by this lane** (standing ruling: no unasked memory writes). They are listed here for the operator to rule on:

- `close-out-command-is-daniels-signoff` — still true in substance; the ruling makes the *decision* the sign-off, of which invoking the command is one of three forms.
- `main-merge-needs-operator-verbatim-approval` — unchanged in force; `approved` is now explicitly one of the three forms.
- `landing-ceremony-is-the-block-not-the-gates` — unchanged.
- `git-branch-model-standard` — its "main reached only via …" line is unchanged; only the wording of *why* moved.

---

## Your Actions

- [x] **The merge itself** — lands via this branch's PR. Number-free by design: the PR number is assigned when the PR opens, which is after this commit is pushed. `jira_feed.py finish` does not take this tick's word for it (SCC-175) — it computes ancestry against `origin/main`.

**Nothing else is owed.** Every finding this lane's review produced was fixed in thread. The four memory files above are listed for your information, not as work: they are yours to rule on whenever you want, and nothing here is blocked on them.
