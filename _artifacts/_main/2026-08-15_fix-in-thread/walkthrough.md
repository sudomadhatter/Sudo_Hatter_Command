# SCC-160 follow-on — survivors are fixed in thread; a review never produces a ticket

**Branch:** `chore/SCC-160-fix-in-thread` · **Base:** `0b46c62` (main) · **Ticket:** SCC-160 (its own key — a follow-on is never a new ticket)
**Close:** `/smh-close-task-merge-tree` on the operator's word

## The ruling (operator, 2026-08-15, verbatim — after the first SCC-160 landing merged)

> "160 was not a fix. we will give you the updates once 38 finishes. the notes will be done then.
> but no it did not fix the problem. we need the fixes made in thread not a ticket made every story
> thats an endless loop that never finishes." · "we are not saying true or false — just that its
> not the full fix." · "we can start on this in parallel. we know the problem lets fix it"

Plan-gate: the literal `approved` was not typed; "we can start on this in parallel. we know the
problem lets fix it" is the recorded go (same override shape the first lane recorded). The ruling
itself is on the ticket (SCC-160 comment, 2026-08-15) — the operator develops from Jira, not memory.

## The flaw, located

The first landing built the relevance gate (what is NOT worth doing dies in triage) and retired the
residue ticket — but its survivor path still read *"fixed in this lane, or ledgered, or — rarely —
proposed to the operator as a decided chore ticket."* That third leg is a ticket the operator has to
rule on, every story. SCC-160's own walkthrough ended in a `Rule on Ticket A and Ticket B` row,
which is what held it on `Review Required`. Same loop, new adjective. And `defer` read "pre-existing
and not caused by this change" — a parking lot with a nicer name.

## What changed — the law

| File | Change |
|---|---|
| `code-review-engine/steps/step-03-triage.md` | `patch` = applied by the caller in this lane before its verdict; pre-existing is not an exemption. `defer` = real, worth fixing, **and this lane structurally cannot hold the fix** — ONE named blocker (another live lane owns the file · another repo needing its own key · an open `decision_needed`); "pre-existing" is no longer a defer reason. ⛔ residue RETIRED body recut: survivors are fixed here, full stop. New law: **⛔ A review never produces a ticket** — not residue, not proposed, not decided, not a ticket-ruling row; the first cut's own close-out named as the counter-example. |
| `code-review-engine/steps/step-04-record.md` | `[Review][Defer]` bullet carries the blocker (`blocked by <live lane | repo | decision>`), not "rides <lane class>"; the record is the worklist for fixes that happen NOW; the ledger is not a ticket queue **and not a proposal source**; the boundary names the caller's fix-in-thread obligation. |
| `code-review-engine/SKILL.md` | "produce a ticket" added to what the engine never does. |
| `smh-code-review.md` · `cicd-code-review.md` | Step 1 gains **"Fix in thread"**: every `patch` applied and every `decision_needed` walked with the operator NOW, before any gate; nothing that survived the gate leaves the lane as future work. Disposition wording `applied @ sha / deferred — blocked by … / dismissed`. Step 5 ⛔ widened to ANY finding-born ticket row and names the `jira_feed` hold as the loop it creates. |
| `cicd-code-review-AP.md` | The "never produces a ticket" sentence ported into its fix paragraph; header re-stamped; `ap_reconciled` at the primary's commit. |
| `jira.md` §Who mints · `artifacts-always-first.md` · SOP ⓘ aside · `deferred-work.md` header | Same recut in each surface's voice; the SOP tells the operator what they should never see again: a ticket-ruling row born from a review. Ledger header: blocker-only; entry format changed. |
| `test_review_engine.py` | `defer` pin's counter_old refreshed + THREE new self-falsifying pins (a review never produces a ticket · survivors fixed in this lane before the verdict · defer is a structural blocker) — each rejects the exact sentence the first cut shipped. |
| `_artifacts/_memory/review-findings-are-not-a-work-queue.md` + `MEMORY.md` | Pointer memory: the law lives on the ticket. |

## The law applied to its own subject — the 11 open items, fixed or dropped HERE

Every item below came from the SCC-156/154 reviews, survived the relevance gate on 2026-08-15, and
was parked as "Ticket A/B" or ledgered. Under the recut law each is fixed in this lane or dropped
with a reason. **Zero tickets.**

| # | Item (origin) | Disposition | What / why |
|---|---|---|---|
| A1 | `--case` over-match — a 1-letter label matches 40 blocks, sweep records "killed by case P" (156 #1) | **fixed @ df39c96** | `_harness.py`: every matched label is recorded and `finish()` prints `-- matched blocks: A \| B --` whenever >1 ran — attribution reads names, never a count. Substring stays (a family prefix is a legitimate multi-select). Pinned: 3 rows in `test_suite_runner`; mutant (drop the line) killed. |
| A2 | Block labels truncated at 64 chars mid-word (156 #2) | **dropped** | Only mattered as the enabler of an exact-match-ONLY mode; substring keeps a truncated label usable and A1 makes the multi-match visible. Un-truncating 37 labels buys nothing. |
| A3 | `--case=<label>` form had no coverage row (156 #3) | **fixed @ df39c96** | Two rows: `--case=BETA` selects only BETA; `--case=<typo>` is exit 3. |
| A4 | Ctrl-C drains the pool instead of stopping (156 #4, ledgered) | **fixed @ df39c96** | `run_all.py`: `run_pool` + `stop_running` — on interrupt the queue is cancelled AND every running child is terminated; results are polled at 250 ms so the interrupt lands promptly on both machines. **The review's one-word fix (`cancel_futures=True`) was measured insufficient while pinning it** — `Executor.map` already cancels the queue; the 88 s was the wait for in-flight children. Pinned with a REAL interrupt (`_thread.interrupt_main`) into sleeping children: propagates / children ended ~1 s into a 6 s sleep / queued file never starts / uninterrupted control. Both mutants (drop `stop_running`; drop the cancel) killed. |
| A7 | Zero-file suite prints `0/0` and exits 0 (156 #7, ledgered) | **fixed @ df39c96** | exit 2 with a reason, no `files passed` line. Pinned + mutant killed. |
| A8 | No invariant stops an orphan `c.check` outside every block (156 #8) | **fixed @ df39c96** | `ORPHAN` AST meta-case over every wired file + a planted-orphan control that must be flagged at its line. |
| A9 | `wf.same_tree` untested while authorizing gate skips (156 #9) | **fixed @ df39c96** | `test_closeout_preflight`: identical tree under a new sha → True; content change → False; unknown sha → None. |
| B12 | Stale refusal sentence ("never with a story or chore lane") on an incident↔incident refusal + INC5 satisfied by the stale sentence (156 #12) | **fixed @ df39c96** | `merge-target-guard.sh` destination names "a story, chore, or sibling incident lane"; INC5 asserts `sibling incident lane` and FAILS on the old sentence (mutant run: 4/6). |
| B13 | Multi-name incident+story sha into a non-main target unpinned (156 #13) | **dropped** | Every such pairing is refused by two independently pinned arms (INC2's unknown-never-launders + INC3/INC5); a case would pass for two reasons and discriminate nothing — the coverage-for-symmetry class. |
| B14 | Multi-lane STALLED LANDING mid-flight (156 #14) | **fixed @ df39c96** (message) | Re-read against the code: the check is RIGHT — after lane N merges unpushed, main IS ahead and the remedy IS `git push origin main`; `--accept-unpushed-main` is the deliberate exit. What was missing is the operator recognising it mid-run, so the message now says so: "In a multi-lane run this is usually the lane you JUST merged and have not pushed yet — push main, then continue." No arm that guesses intent. |
| L7 | `dirty_paths` readback: rename-row and quoted-path parses uncovered (154 #7, ledgered) | **fixed @ df39c96** | `gate_receipt.py` reads `porcelain -z` — unquoted names, BOTH sides of a rename. Direction measured with the old parser: a non-ASCII `_artifacts/` path kept its C-quoting (safe false full-gate); a rename OUT of code INTO `_artifacts/` recorded only the artifacts side and **would have authorized a gate skip on moved code** (unsafe). Pins 9c–9e on exact filenames; old parser fails all three. |

The two walkthroughs this closes: `2026-08-15_triage-owns-relevance/walkthrough.md` — Ticket A/B row
struck as resolved, "Proposed decided tickets" section marked SUPERSEDED in place (verdict line
untouched); `deferred-work.md` — its three entries closed as fixed; the ledger is empty, which is its
correct resting state.

## Evidence

| Check | Result |
|---|---|
| `run_all.py` | PASS 27/27 files, exit 0, 88.0 s @ `b100d00` (`gates/suite.json`) |
| `workflow_lint --toolkit-only` | PASS 0 errors 0 warnings, exit 0 @ `aacddf4` (`gates/lint.json`) |
| `check_maps --depth3-only --strict` | PASS exit 0 @ `c475fb1` (`gates/maps.json`) |
| Contract pins | `test_review_engine.py` 792/792 after sync — 3 new self-falsifying pins each reject the first cut's sentence |
| Mutants | every new guard measured red first: matched-blocks line · zero-file guard · `stop_running` · queue cancel · old porcelain parse · stale guard sentence — six mutants, six kills, then the closing green |
| Assertion evidence | `test_suite_runner` 52/52 · `test_gate_receipt` 34/34 · `test_closeout_preflight` 29/29 · `test_git_hooks --case INC5` 6/6 · `test_task_preflight --case STALLED` 6/6 |
| SOP currency | armed hook; the code commit staged the SOP (sweep aside); law/record commits `[sop-ok]` with rationale |

## Code Review (2026-08-15)

_(appended after the lens fan-out — see below)_

## Your Actions

- [ ] **The merge itself** — `/smh-close-task-merge-tree` on your word. Nothing else is open: no
      ticket to rule on, no ledger entry owed. Landing order vs `chore/SCC-38-…`: this lane touches
      `run_all.py` / `gate_receipt.py` / `task_preflight.py` / `merge-target-guard.sh` (gate + script
      machinery) — per the multi-lane rule it lands AFTER any lane that does not.
