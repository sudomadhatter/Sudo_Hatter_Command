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

Verdict: PASS @ 53ad33c
Suite evidence measured @ 53ad33c (`gates/suite.json`, 27/27 exit 0, 87.8 s); receipts commits after it are artifacts-only.

- **Scope:** `origin/main...HEAD` — 35 files: the engine steps + SKILL, both review commands + AP twin, quick-dev ×2, clean-code audits ×2, close-out, jira.md, artifacts-always-first, SOP, ledger, memory; scripts `run_all.py`, `_harness.py`, `gate_receipt.py`, `wf_common.py`, `merge-target-guard.sh`, `task_preflight.py` + 5 test files.
- **Method:** the house engine's lens fan-out — Blind Hunter (diff only, no intent), Edge Case Hunter (boundary walk + `python3 -c` / throwaway-repo probes), Acceptance Auditor (law consistency + plan A1–A5) — three clean contexts in parallel, then triage under the relevance gate. `lenses_run: 3/3 (ok · ok · ok)`. Every survivor was **fixed in this lane before this verdict** — this section IS the law the lane ships, run on itself. `findings: 0 decision · 19 patch · 0 defer (0 noise · 3 relevance kills)`. `severity_floor: none` after fixes (pre-fix: FAIL — one critical).

### ONE findings table (authoritative)

| # | Lens | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|---|
| 1 | Edge | `run_all.py` child Popen (live edit) | **critical** | `encoding="utf-8"` on the child pipe: children write with the LOCALE (cp1252 on the PC) → `·` decodes to U+FFFD → run_all's own cp1252 stdout raises → the whole gate red-walls on the PC | applied @ 91e6095 — reverted to the shared-locale form; comment names why |
| 2 | Blind | `_harness.py` `--case " "` | important | whitespace-only value is truthy, `"" in label` matches everything → `matched 3/3`, exit 0, sweep records "killed by case ' '" | applied @ 91e6095 — strip at parse → lost label, exit 3; pinned |
| 3 | Blind | `wf_common.git` (via `gate_receipt -z`) | important | `text=True` decodes with the locale; on the PC `café.md` → `cafÃ©.md`, receipt "exact filename" false, 9c red on Windows | applied @ 91e6095 — `encoding="utf-8"` in `wf.git` (git writes UTF-8) |
| 4 | Edge | `test_suite_runner` interrupt pins | important | `interrupt_main` is a no-op under an inherited SIG_IGN (`&`, cron, wrapper) → children run to completion → 3 false reds | applied @ 91e6095 — default SIGINT handler installed for the block, restored after |
| 5 | Edge | `_harness.py` matched-blocks line | important | labels carry `⛔`/`⭐`; on a cp1252 pipe `finish()` raises AFTER the rows → exit 1 → a sweep reads "killed" for a survivor (unsafe direction) | applied @ 91e6095 — encoded for the stream with `backslashreplace` |
| 6 | Edge | `test_suite_runner` 2nd interrupt block | important | fixed 1.0 s timer; under load j1's marker not yet written → false red "runner lost a file" | applied @ 91e6095 — fire only once both markers exist / both children registered, 8 s cap |
| 7 | Acc | `cicd-quick-dev.md:95` (+ `smh-quick-dev` `--followon`) | important | "append deferrals to the deferred-work file" with no blocker rule — a defer-without-blocker path outside the engine; `--followon` carries the pile | applied @ 91e6095 — defer only against a named blocker; `--followon` = blocked items only, never a pile |
| 8 | Blind | `run_all.py` Popen window | suggestion | Ctrl-C between "future started" and "child registered" → that child invisible to cancel and stop | applied @ 91e6095 — `_STOPPING` latch refuses to spawn; a late spawn terminates itself |
| 9 | Blind | ORPHAN walker | suggestion | a `c.check` in the `else:` of `if c.block()` scored guarded — runs under every non-matching filter | applied @ 91e6095 — only the If BODY guards; planted else-orphan control |
| 10 | Edge | `run_all.py` submits outside `try` | suggestion | Ctrl-C during submission escapes → false "cancelled" message, files run silently to completion | applied @ 91e6095 — submits inside the try |
| 11 | Edge | `run_all.py` runner exception | suggestion | a Popen `OSError` propagates with no stop → traceback, hang at exit | applied @ 91e6095 — `except BaseException:` cancels + stops |
| 12 | Edge | `stop_running` → `terminate` | suggestion | SIGTERM cuts children's `with TempDir()` unwind → leaked scratch repos on every Ctrl-C | applied @ 91e6095 — POSIX: SIGINT first, 1 s grace, then terminate |
| 13 | Edge | `_STOPPING` never reset | suggestion | a second `run_pool` in-process returns 130 for everything | applied @ 91e6095 — reset at `run_pool` entry |
| 14 | Edge | ORPHAN walker idioms | suggestion | `if not c.block(): continue` / BoolOp / walrus read as orphans — a false red that misdirects | applied @ 91e6095 — the message names the one idiom recognised (fails toward a red at the exact line; the convention is documented) |
| 15 | Acc | step-03 no-spec paragraph | suggestion | "otherwise `defer`" = a fourth, blocker-less defer path two paragraphs under "No blocker → patch" | applied @ 91e6095 — no-spec keeps `decision_needed` (the operator is the spec); pin recut @ 53ad33c |
| 16 | Acc | step-03 floor table | suggestion | defer rationale "not this change's defect" is the retired pre-existing reading | applied @ 91e6095 |
| 17 | Acc | step-03 `jira.md §cross-repo` | suggestion | dangling section reference | applied @ 91e6095 — points at §The map |
| 18 | Acc + Blind | step-03 vs callers: `decision_needed` the operator does not take in-thread | suggestion | three exits (walk now / open Your Actions row / ledger defer), none wins | applied @ 91e6095 — stated once: walked now → patch/dismiss; not taken (or headless) → an open DECISION row (theirs, may hold, not a ticket) and the defer bullet points at it |
| 19 | Acc | `jira.md:503` "maybe" items | suggestion | contradicts the blocker-only ledger | applied @ 91e6095 — no "maybe" bucket |
| 20 | Acc | memory + MEMORY.md | suggestion | carried in saying "do NOT pre-empt, recut owed" while this lane IS the recut | applied @ 91e6095 |
| 21 | Acc | clean-code audits ×2 · close-out:252 · SOP:828 | suggestion | unconstrained "deferred" in review-adjacent surfaces | applied @ 91e6095 — a deferral names its blocker; close-out findings fixed before the merge |
| 22 | Acc | this walkthrough's merge row + `smh-close-task-merge-tree` | nitpick | `finish` reads THIS walkthrough and would HOLD on the merge box the ceremony itself represents | applied @ 91e6095 — the close-out now ticks the merge row before `finish` (law), and this row is ticked by the ceremony below |
| 23 | Blind + Edge | `test_closeout_preflight` same_tree | nitpick | comment said "merge"; fixture was an empty commit | applied @ 91e6095 — a real two-parent merge with an identical tree |
| 24 | Blind | `gate_receipt.py` comment | nitpick | "rename rows record the NEW path" — stale | applied @ 91e6095 |
| 25 | Acc | `deferred-work.md` title | nitpick | "judged ride-along" is first-cut vocabulary | applied @ 91e6095 |
| 26 | Acc + Edge | `test_review_engine.py` new pins | nitpick | prose pins on heading sentences (SCC-125 class); `\s+` reflow sensitivity | **dismissed — relevance:** the pin table is the house's accepted engine contract; each pin's counter-example rejection is the falsification the framework offers, and every other pin in the file has the same shape; asking for a different kind of guard is a proposal for the pin framework, not a defect of these three rows |
| 27 | Edge | 1st interrupt block `timer.cancel()` placement | nitpick | superseded — the fixed timer no longer exists (fire-when thread, daemon) | dismissed — moot after #6 |
| 28 | Edge | grandchild pipes / already-dead terminate / `status.renames=false` / porcelain `-z` boundaries | — | verified handled by the lens (no finding) | — |

Noise-dismissed: 0. Relevance kills: 2 (#26, #27), each with its reason above. **Tickets produced: 0. Deferred: 0.**

### Gates (each run bare, actual output)

| Check | Result |
|---|---|
| Enforcement suite | `run_all.py` **27/27 files passed**, exit 0, 87.8 s @ `53ad33c` — `gates/suite.json` |
| Toolkit lint | `workflow_lint --toolkit-only` **0 error(s), 0 warning(s)**, exit 0 @ `24fde11` — `gates/lint.json` |
| Maps | `check_maps --depth3-only --strict` exit 0 @ `b57d406` — `gates/maps.json` |
| Assertion evidence (named cases, green) | `test_suite_runner` 54/54 · `test_gate_receipt` 34/34 · `test_closeout_preflight` 29/29 · `test_review_engine` 792/792 · `test_workflow_lint` 49/49 · `--case INC5` 6/6 · `--case STALLED` 6/6 |
| Mutants (red first, then green) | matched-blocks line · zero-file guard · `stop_running` (twice, after the SIGINT-first rewrite) · queue cancel · old porcelain parse · stale guard sentence — six kills |
| Link + anchor | every new path in the walkthrough/plan/INDEX resolves; `jira.md` §The map exists |
| SOP currency | armed hook: usage commits staged the SOP; law/record/receipt commits `[sop-ok]` |
| Door parity | no command added/renamed/deleted; caches re-synced (`sync-agents.ps1`), `test_review_engine` byte-identical check green |
| Step 0.7 re-derivation | `origin/main` = `0b46c62` = this lane's base; nothing moved under the diff. Sibling lane `chore/SCC-38-flight-recorder-autopilot-spec` (d7658e5) is live: **landing order — this lane touches gate/script machinery (`run_all`, `gate_receipt`, `task_preflight`, `merge-target-guard`), so per the multi-lane rule it lands AFTER any lane that does not; SCC-38 is still open, so no conflict today** |

### Honest note on the receipt trail

Three receipt commits (`c588cb9`, `905fd7d`, `e57400a`) were labelled PASS in their subjects while the
suite and lint they stamped were RED (a stale pin + a stale AP stamp after the review-fix commit
re-edited the primary). The receipts themselves recorded `fail` truthfully; the commit subjects did
not. Fixed at `53ad33c` and re-stamped honestly (`suite pass @ 53ad33c` · `lint pass @ 24fde11` ·
`maps pass @ b57d406`). Left in history rather than rewritten.

Changes applied: 25 (table). Walkthrough body refreshed: evidence table above supersedes the
pre-review one; the `## Evidence` block earlier in this file records the pre-review stamps.

## Your Actions

- [x] **The merge itself** — signed off 2026-08-15: you invoked `/smh-close-task-merge-tree` (door 3)
      this turn; this ceremony's own act. Nothing else is open: no ticket to rule on, no ledger entry
      owed. Landing order vs `chore/SCC-38-…`: SCC-38 is still open, so this lands on `main` first
      and SCC-38 absorbs it.
