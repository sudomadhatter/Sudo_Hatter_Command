# SCC-197 — rolling ticket, cycle 2 · walkthrough

**Lane:** `chore/SCC-197-rolling-cycle2` · **riders:** SCC-198 (Part A), SCC-200 (Part B),
SCC-202 (Part C, unplanned), SCC-203 (Part D, unplanned) · **base:** `5123e81`
**Plan + Self-Audit:** [implementation_plan.md](implementation_plan.md) · **manifest:** [task.yaml](task.yaml)

⛔ **`landing_mode: partial` — WAVE 1 of 2.** SCC-205 (the `/cicd-*` parity audit) is a subtask of
SCC-197 and is **not** a rider here. Riders A–D flip to Done on this landing; **SCC-197 stays open**
carrying wave 2.

<!-- The commit count is deliberately not restated here. It read `aad4d82..591fa76 (4)` while the
     lane was already past eight, because a range written mid-lane is a fact with an expiry date and
     nothing re-reads it. `git log --oneline 5123e81..HEAD` is the answer that cannot go stale. -->

---

## Task Checklist

- [x] **Part A (SCC-198) — `cmd_start` clones the next rolling ticket and hands the baton on**
  - The cycle instruction lived only in the ticket's description (first line, capitals) and did not
    fire. The operator's words were the brief: *"its writen in the ticket I just dont know if you
    will read it."*
  - ⭐ **The operator's ruling replaced my design mid-build.** I had two permanent labels — identity
    plus trigger. The ruling: *"I dont like the two tags — once you move it to In Progress we switch
    the tag … it now clones, it moves the original, and switches the tag to the bugs-and-updates."*
    One marker, and it **moves**.
  - The invariant everything falls out of: **a rolling ticket holds `running-bug-list` until its
    successor EXISTS, and not one moment longer.** Clone before swapping (a clone carries labels —
    that *is* the handoff); swap even when the operator's prompt did the cloning; withhold the swap
    when the clone failed, so the cycle self-heals instead of ending silently.
  - Why it is stronger than what I built: a permanent trigger can fire twice, so every guard against
    a second clone must **ask the board**. A baton is consumed by use — the common re-fire (the
    post-commit recorder) cannot clone, with nothing to query and nothing to get wrong.
- [x] **Part C (SCC-202) — unplanned, and forced by Part A**
  - ⛔ Measured live: **`acli edit --labels` ADDS. It does not replace.** `--remove-labels` is a
    separate flag; acli honours both in one call.
  - The stub had modelled a **replace**, and that lie hid a shipped defect — `cmd_finish`'s
    `user-tasks` strip built the reduced set and sent it via `--labels`, re-adding what was already
    there and removing nothing. **The strip has never worked on the board.**
  - It also meant **Part A was wrong in production for an hour** and all 18 of its cases passed.
- [x] **Part B (SCC-200) — every artifact handed back as a clickable link**
  - ⭐ **Recon reframed the part.** The plan assumed the rule was silent. It was not — the duty had
    been in `artifacts-always-first.md` all along, in one blockquote. It still did not fire.
  - So the defect is **where** it is stated, and the fix is placement: the duty now sits at each of
    the three seams where an artifact is produced.
- [x] **Part D (SCC-203) — unplanned, and found by this lane's own code review**
  - The review reported `review-runtime: inline`, justified by *"a standing session directive
    forbids subagent fan-out unless the operator asks"*. That is a **policy** answer to a
    **capability** question — the subagent tool existed and worked the whole time.
  - The directive was **not the operator's**: absent from `.agents/rules/`, every settings file and
    all 127 memory files. Operator: *"i never made a rule not to spawn sub agents unless I ask ?
    this is something that makes this dev faster why would I stop that ?"*
  - So the Blind Hunter — the one lens whose value is **not** knowing what the builder knows — ran
    holding the plan and the walkthrough, and the flow recorded that as a legitimate review.
  - ⭐ **The ruling:** subagents are the DEFAULT and invoking the review IS the request. Where the
    order cannot protect the lens, it is **DROPPED** and recorded on `lenses_na`, never faked.
    `ok (not blind — context held <what>)` is retired. *Dropping one lens is a smaller review;
    faking it is a false one.*
  - The gap that mattered: the engine was told to record a drop and **nothing downstream could read
    it**. `walkthrough_roster.py` now does, and refuses a drop under a declared `fan-out`.
- [x] Gates green, both sweeps clean, INDEX row added, SOP updated (gate-enforced, twice)

---

## What changed

| File | Why |
|---|---|
| [.agents/scripts/jira_feed.py](../../../.agents/scripts/jira_feed.py) | `roll_the_cycle()` + the `cmd_start` seam; `user-tasks` strip via `--remove-labels`; the sibling add site sends one label, not the union |
| [.agents/scripts/tests/test_jira_feed.py](../../../.agents/scripts/tests/test_jira_feed.py) | stub models the **measured** add/remove semantics; 18 baton cases |
| [.agents/rules/artifacts-always-first.md](../../../.agents/rules/artifacts-always-first.md) | `## Hand It Back` section + the duty at §2, §3, §5 |
| [.agents/rules/work-consolidation.md](../../../.agents/rules/work-consolidation.md) | rung 3 queries **BOTH** markers with `labels` on `--fields`; the cycle section records the automatic successor **and both ways the baton breaks** |
| [.agents/scripts/tests/test_command_surfaces.py](../../../.agents/scripts/tests/test_command_surfaces.py) | the SCC-200 placement block + **5** negative controls (3 on the marker, 2 on the link form) |
| [.agents/scripts/label_tasks.py](../../../.agents/scripts/label_tasks.py) | **Part C, third site** — `set_labels()` sent the reduced set to strip a label; now derives adds and removes from the plan and sends both |
| [.agents/scripts/tests/test_label_tasks.py](../../../.agents/scripts/tests/test_label_tasks.py) | stub corrected from *replace* to the measured *add* + `--remove-labels` |
| [.agents/scripts/walkthrough_roster.py](../../../.agents/scripts/walkthrough_roster.py) | **Part D** — reads `lenses_na:` at last; a drop is legal only under `inline`, and only with a reason |
| [.agents/scripts/tests/test_walkthrough_roster.py](../../../.agents/scripts/tests/test_walkthrough_roster.py) | the `NA` block — 6 cases incl. the hyphen control that stops `blind-hunter` being split into a lens named `blind` |
| [.agents/scripts/tests/test_review_engine.py](../../../.agents/scripts/tests/test_review_engine.py) | SCC-203 CHECKS rows + the twin **byte-identity drift check**, which found real drift on its first run |
| [.agents/commands/smh-code-review.md](../../../.agents/commands/smh-code-review.md) · [cicd-code-review.md](../../../.agents/commands/cicd-code-review.md) · [cicd-code-review-AP.md](../../../.agents/commands/cicd-code-review-AP.md) · [smh-quick-dev.md](../../../.agents/commands/smh-quick-dev.md) | capability-vs-policy law; the AP twin's retired instruction removed and `ap_reconciled` restamped |
| [.agents/skills/code-review-engine/steps/step-01-review.md](../../../.agents/skills/code-review-engine/steps/step-01-review.md) | `ok (not blind — context held …)` **retired**; a contaminated Blind Hunter is DROPPED to `lenses_na` |
| `.opencode/commands/*` (3 doors) | regenerated by `sync-agents -NoGlobals` so the mirrors match their brains |
| [docs/_scc_sops_prds/workflows_testing_SOP.md](../../../docs/_scc_sops_prds/workflows_testing_SOP.md) | all four parts, in operator-facing terms |
| [_artifacts/_main/INDEX.md](../INDEX.md) | the session row (`check_maps` caught its absence) |

---

## Evidence

| # | Acceptance | Evidence |
|---|---|---|
| A1 | The trigger fires on the tagged ticket, not on ordinary ones | `A1`, `A2`, `A2b` — both directions |
| A2 | The handoff actually happens, both ends | `A1b` successor holds the baton · `A1c` original gives it up |
| A3 | Zero extra board reads on the normal path | `A3`/`A3b` **counted**: baseline 2, unchanged |
| A4 | Idempotent, and one holder never two | `A4`/`A4b`/`A4c` |
| A5 | A clone failure never fails the start, and never loses the cycle | `A5`/`A5b`/`A5c` |
| A6/A7 | A failed swap and a failed search are loud, not fatal | `A6`, `A7`/`A7b` |
| C1 | The strip actually strips | `finish: closing clean STRIPS user-tasks` — **RED against the old writer** |
| B1 | The duty sits at all three seams | `SCC-200 …ALL THREE seams` + **5** controls — 3 on the marker, 2 on the link form |
| C2 | The strip works on the OTHER script too | `test_label_tasks.py` 101/101 with the stub corrected to the measured semantics |
| D1 | A dropped lens is readable, and only `inline` may drop one | `NA1`–`NA4`; `D-M1`/`D-M4` killed |
| D2 | A drop carries a reason, and the lens NAME survives its own hyphen | `NA3`/`NA5`; `D-M2`/`D-M3`/`D-M5` killed |
| D3 | The two callers carry the SAME law, and the check can FAIL | section 2a + both counter-examples — it found real drift on its first run |

**Suite Ledger**

| Scope | Command | Result |
|---|---|---|
| full | `python3 .agents/scripts/tests/run_all.py` | **33/33 files**, exit 0 |
| lint | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **0 errors, 0 warnings**, 8 info, exit 0 |
| maps | `python3 .agents/scripts/check_maps.py --depth3-only --strict` | **clean**, exit 0 |
| sweep A/C | `mutation_sweep.py --table sweep-partAC.json` | **7/7 killed**, restore verified |
| sweep B | `mutation_sweep.py --table sweep-partB.json` | **5/5 killed**, restore verified |
| sweep D | `mutation_sweep.py --table sweep-partD.json` | **5/5 killed**, each by its **declared** case |

Every gate was run **bare** — never piped — because a pipe reports the pipe's exit code and not
the gate's (`piping-a-gate-hides-its-exit-code`). Output went to a file and the exit code was read
from the command itself.

⭐ **`sweep-partD.json` records a refusal worth keeping.** `D-M3` (the row separator loses its
required spaces) was first declared against `NA5`, and the sweep **rejected the kill**: something
died, but not the declared case. It was right. An unspaced separator corrupts a *reasonless* row
first — bare `blind-hunter` parses as lens `blind` with reason `hunter`, manufacturing a reason out
of the second half of the lens's own name — so `NA3` is the case that catches it. `D-M5` was then
added to isolate `NA5`, which is the only case that asserts the exact name. A kill from the wrong
case is not evidence about the right one, and the tool would not let that pass.

`git rev-parse HEAD` → `9e9c2eac39d96867fd404830f1858dba77125533` (14 commits off `5123e81`)

---

## What the reds actually caught

Three things went red that I would otherwise have shipped, and each was found by running rather
than reading:

1. **`A3` asserted a baseline I had invented.** I pinned "exactly one board read" from the plan;
   `cmd_start` has always made two (status, then the post-transition read-back). The case was
   measuring my expectation, not the program. Fixed to pin the real baseline — which is what makes
   it a cost gate: a third call now reds it.
2. **The stub lied, and the lie was load-bearing.** Fixing `--labels` to match the live board
   reddened four cases at once: the `user-tasks` strip (a **shipped** no-op) and three of Part A's.
   331/335 → 335/335. This file's own comment states the rule that was broken: *a stub more
   generous than the tool it stands in for cannot fail on the bug it exists to catch.*
3. **A negative control caught its own vacuity.** With the base green, the PLAN-seam control went
   red — a decorative `→ ## Hand It Back` pointer left a second marker in the section, so stripping
   the duty did not strip the evidence. The pointers are gone.

Also worth recording: the SCC-200 cases were first written into `test_workflow_lint.py`, where the
**sweep could not address them** (`--case` matches block labels only; every mutant scored exit 3).
Adding one block there was worse — a file is *wired* the moment it contains any `c.block(`, and
`ORPHAN` then demands all 46 of its checks be guarded. Moved to `test_command_surfaces.py`, which is
already fully blocked and already owns the sibling rule's assertions.

---

## The one gap this does NOT close

Neither the prompt nor the tag **detects its own failure.** If a hand-off fails, two tickets carry
`running-bug-list` and nothing says so — the code warns at the moment it happens and the rule tells
you what to do about it, but no gate asserts the board's shape. A board assertion (*exactly one open
ticket carries the trigger*) in `task_preflight.py check_children` would make it loud. Recorded on
SCC-198, deliberately unbuilt.

---

## Your Actions

- [ ] **Decide whether the redundant gate is worth changing.** Measured: `test_sops_prds_folder.py`
      is listed as a separate gate by `/smh-quick-fix` and `/smh-quick-dev`, but it already runs
      inside `run_all.py`. Removing it saves **0.27s** against a 128s full run — real redundancy,
      negligible payoff. My recommendation is to leave it: the line also documents *when* it
      matters. Your call, and it is the only thing here that is not already done.
- [x] The live board was corrected to the baton state by hand, since SCC-201 was cloned before the
      code existed: **SCC-197 → `bugs-and-updates`**, **SCC-201 → `running-bug-list`**.
- [x] Plan, walkthrough and manifest are linked at the top of this document and in chat.

---

review-runtime: fan-out

<!-- ⛔ THIS HEADER WAS WRONG ONCE, AND CORRECTING IT IS WHY SCC-203 EXISTS.
     It first read `review-runtime: inline`, justified as "a standing session directive forbids
     subagent fan-out unless the operator asks for it". That is a POLICY answer to a CAPABILITY
     question, and the two are not interchangeable: the subagent tool was present and working the
     whole time. The consequence was not cosmetic — the entire review ran inside the builder's own
     context, the Blind Hunter was handed the plan it is defined by NOT having, and the flow
     recorded the result as a legitimate `inline` review. Nothing in the system objected. The
     operator caught it by reading the chat and asked the question that unpicked it: "the threat is
     the preconceived ideas, I need the code review to run in a clean context window."
     The directive itself turned out not to be the operator's at all — it comes from the session-init
     layer, and it is absent from `.agents/rules/`, every settings file, and all 127 memory files.
     Under the SCC-203 ruling subagents are the DEFAULT and invoking the review IS the request, so
     the review was re-run properly: five lenses, five clean subagent contexts. -->

## Code Review (2026-08-17)

Run through `code-review-engine` after the correction above, as a real fan-out — each lens in its
own subagent, the Blind Hunter given the diff and nothing else.

review-runtime:  fan-out
lenses_run:
- Blind Hunter · ok — the diff alone, in its own context; found the vacuous R2/R2c guards without ever seeing the plan that claimed they worked
- Edge Case Hunter · ok — found the stranded-predecessor path, where repairing two holders produces zero
- Literal-Correctness Hunter · ok — found that `statusCategory != Done` matches the ticket asking the question
- Acceptance Auditor · ok — found the plan's "resend every other label" step contradicted by Part C's own measurement
- Test-Adequacy Auditor · ok — found the stub ignored the JQL entirely, so no query mutant could ever fail
lenses_counted:  5/5
lenses_na:       none
severity_floor:  none

<!-- ⛔ NOT FENCED, ON PURPOSE. `walkthrough_roster.py` calls `strip_fenced()` before it reads
     anything, because the review instructions teach this block fenced and a doc example must not
     satisfy a gate. Fencing the real roster here would delete it from the parser's view and the
     close-out would refuse the lane for having no roster at all. Verified by running the parser
     against this file rather than by assuming: it reported `lenses: []` while the block was
     fenced. -->

### Step 0.7 — re-derivation against current `origin/main`

- **What moved:** nothing. `origin/main` is `5123e81`, which is also this lane's merge-base, so
  `git rev-list --count HEAD..origin/main` is **0** and there is nothing to absorb. Re-measured at
  the verdict sha, not carried forward from the plan.
- **What it changes:** nothing in scope or content. No sibling lane landed while this one ran, so
  the gates-not-files hazard (`lane-collision-is-gates-not-files`) has no other lane's blobs to run
  this lane's gates against.
- **What was re-measured:** everything, at `9e9c2ea` — the full suite (33/33, exit 0), the toolkit
  lint (0 errors, 0 warnings), the map gate (`--depth3-only --strict`, clean), and all **three**
  mutation tables (7/7 + 5/5 + 5/5), each mutant killed by its own declared case.

**What the fan-out bought, stated as evidence rather than as a claim.** Findings converged across
independent contexts, which is the signal a single-context review cannot produce: the vacuous R2/R2c
guards were found by **four** lenses independently, and the false-retry promise in `cmd_start` by
**three**. A review that had run inside the builder's context would have inherited the belief that
those guards worked, because the builder wrote them.

**The two most serious defects were caught by MUTATION, not by reading** — both survived every
lens's read of the code and only died when the assertion was tested against a deliberately broken
tree:

- deleting `AND key != {key}` from the successor search left the suite **18/18 green**. On a live
  board that mutant is terminal: the ticket matches its own query, skips its clone, swaps its label
  anyway, and prints "a successor already exists" while naming itself. The baton is consumed with
  no successor minted.
- moving the roll above the `--apply` guard also left **18/18 green** — a dry run would have cloned
  a real ticket on the real board.

Both are now pinned (A4c–A4g), and the stub honours the JQL so a query mutant can no longer pass.

**Findings were fixed in this lane, not deferred and not ticketed** (`work-consolidation` rule 1 +
the operator's 2026-08-15 ruling that review findings are fixed in thread).

### What the review changed

| # | Finding | Disposition |
|---|---|---|
| 1 | The successor search matched the ticket ITSELF, a stranded predecessor, and any project | fixed — `statusCategory = "To Do"` + project scope + `key != {key}` |
| 2 | "The next `start` tries again" was unreachable — bound to the transition edge | fixed — the roll is bound to STATE (A4d) |
| 3 | `R2`/`R2c` were vacuous: my own comment lines satisfied the guard | fixed — comment lines stripped before matching |
| 4 | `label_tasks.py` `set_labels()` was the third `--labels` no-op site | fixed — adds and removes derived from the plan |
| 5 | The `LINK` half of the hand-back guard was pinned by nothing | fixed — 2 controls, verified by mutation |
| 6 | `lenses_na` had no machine reader; a `fan-out` could drop a lens and gate green | fixed — `walkthrough_roster.py` reads it and refuses |
| 7 | The twin byte-identity check could not fail; the drop clause was unpinned | fixed — 3 clauses named, 2 counter-examples |
| 8 | rung 3 could not tell two identically-named rolling tickets apart | fixed — `labels` on `--fields` |
| 9 | Zero-holder was undocumented and silent | fixed — rule + SOP |
| 10 | The AP twin taught the retired state, and its stamp was stale | fixed — reconciled and restamped |
| 11 | `artifacts-always-first.md` pointed at the wrong test file | fixed |
| 12 | SOP had a spliced sentence with a dangling "it" | fixed |

**Nothing was deferred.** No residue ticket was minted — the engine does not produce tickets, and
every finding above was inside this lane's own surface.

---

Verdict: PASS @ 9e9c2eac39d96867fd404830f1858dba77125533
