# SCC-160 — Review triage owns implement-relevance; the residue-ticket practice is retired

**Branch:** `chore/SCC-160-triage-owns-relevance` · **Base:** `f963be3` (main)
**Ticket:** SCC-160 · **Close:** `/smh-close-task-merge-tree` (parked until the operator's word)

## The ruling (operator, 2026-08-15, verbatim)

> "this whole create a ticket for all the random little findings is not effective and is a waste
> of time and resources. we need the agent who reviews the code review to decide which are
> actually relivant to impliment. the agents who review this have the goals of finding things,
> this doesnt mean they are all actually relivant to impliment this is a flaw in our process."

The flaw, located: the engine's step-02 verifies whether a finding is TRUE, but nothing owned the
question of whether it is WORTH IMPLEMENTING — so verified-true-but-unfixed findings banked into
"deferred residue owed to ONE follow-on ticket" piles (SCC-156: 16 items; SCC-154: 9 items), each
ending as a walkthrough action row asking the operator to commission a ticket. Two standing rules
already pointed the right way and were being out-conventioned: `jira.md` ("never mint speculative
work — a ticket asserts a decision already made") and the review command's own "taste does not
block" split.

## What changed (the law)

| File | Change |
|---|---|
| `.agents/skills/code-review-engine/steps/step-03-triage.md` | **The core.** New `### The relevance gate` inside §4: a true finding must pass one of three legs — (1) a realistic damage path TODAY (named actor + moment, no hypothetical chains), (2) it undermines evidence the house cites as proof (verdicts, receipts, mutation-kill attribution, suite totals), (3) the operator asked. Fails all three → `dismiss` with a one-line reason. Severity never bypasses the gate; §5's floor reads only survivors. Named default-dead classes: doc symmetry, coverage-for-symmetry, style preference, prose pins (SCC-125). ⛔ The residue class is RETIRED — "owed to a follow-on ticket" and variants banned from walkthroughs. Bucket definitions tightened: `patch` = real AND worth making; `defer` = real, worth fixing, pre-existing; `dismiss` gains the true-but-not-worth-it class, counted AND named. |
| `.agents/skills/code-review-engine/steps/step-04-record.md` | `defer` bullets are JUDGED items — why it matters + the lane class it rides, never a bare title. The ledger is not a ticket queue: nothing in it is owed, no close-out mints a ticket from it as a pile. Dismissed stays out of builder worklists; relevance kills live as one-liners in the walkthrough findings table only. Summary format: `(<n> noise-dismissed · <k> relevance kills)`. |
| `.agents/skills/code-review-engine/SKILL.md` | Summary-format mirror of the step-04 change. |
| `.agents/commands/smh-code-review.md` | Findings-table disposition wording (relevance kill carries its reason; noise is count-only) + ⛔ ban on residue-ticket action rows in `## Your Actions` triage. |
| `.agents/commands/cicd-code-review.md` | Same two changes, this command's phrasing. |
| `.agents/commands/cicd-code-review-AP.md` | Twin diff-header re-stamped (SCC-160, 2026-08-15): nothing to port — the law lives in the shared engine steps this twin already invokes; its body never carried the residue habit. Previous stamp preserved as history. |
| `.agents/rules/jira.md` | §Who mints tickets: review findings named the canonical speculative case; the both-directions ban (agent never mints a residue ticket, and never leaves the minting as an operator action row). |
| `.agents/rules/artifacts-always-first.md` | Findings-table disposition mirror. |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | New ⓘ aside under ③'s verdict table: "Found ≠ owed" — the operator-facing story of the ruling and what they should never see again. |
| `_artifacts/_main/deferred-work.md` | **Created** — the center's deferred-work ledger the engine contract names (`DEFERRED_WORK`) existed nowhere; the judged ride-alongs from the first live run are its first entries. |
| `_artifacts/_main/2026-08-14_lane-speed/walkthrough.md` · `2026-08-14_gate-edges/walkthrough.md` | The two standing residue sections superseded in place (headings marked, the lane-speed "One follow-on ticket" action row struck). Verdict lines untouched. |

No script changed; no test changed. This is law + record surgery — the mechanical gates
(`run_all`, `workflow_lint --toolkit-only`, `check_maps --depth3-only --strict`) certify the lane.

## First live run — the 25 standing items, re-triaged under the gate

Legend: **leg 1** = realistic damage path today · **leg 2** = undermines cited evidence ·
**leg 3** = operator asked. Verdicts: **SURVIVES** (proposed decided ticket) · **DEFER** (judged
ride-along, ledgered) · **KILLED** (one-line reason) · **N/A** (not triage's jurisdiction).

### SCC-156's sixteen (lane-speed review @ cade703)

| # | Item | Verdict | Reason |
|---|---|---|---|
| 1 | `--case` over-match (a 1-letter label matches 40 blocks; sweep records "killed by case P" when 22 ran) | **SURVIVES → A** | Leg 2: mutation-kill attribution is evidence the house cites in merge messages; today it can lie. |
| 2 | Block labels hard-truncated at 64 chars mid-word | **SURVIVES → A** | Enabler of 1 — you cannot exact-match a label you cannot see. Items 1–3 are one change (standing note). |
| 3 | `--case=<label>` form had no coverage row | **SURVIVES → A** | Same change; the form now carries behavior (exit-3 class) that deserves its own pin. |
| 4 | Ctrl-C drains the pool instead of stopping (`cancel_futures=True`) | **DEFER** | Leg 1 weakly (real actor, minor damage — an uninterruptible 88 s run). One-word fix; rides ticket A's lane or the next `run_all` lane. Ledgered. |
| 5 | `run_all` exit 2 classified as suite `fail` vs docstring's "unrunnable" | **KILLED** | Fails legs 1+2: misclassifies in the SAFE direction — an under-promising receipt blocks, it cannot bless a wrong merge. |
| 6 | `--serial --jobs 0` silently coerced | **KILLED** | Leg 1: no realistic actor passes both flags together; the guard exists for the flag that matters. |
| 7 | Zero-file suite prints `0/0` and exits 0 | **DEFER** | Leg 2 arguable (a 0-file PASS receipt could authorize a SKIP) but the trigger needs the tests dir to vanish while all else works — exotic today. 2-line floor guard; rides ticket A's lane. Ledgered. |
| 8 | No invariant stops an orphan `c.check` outside every block | **SURVIVES → A** | Leg 2 with a PROVEN trigger: the reviewer created one live during the SCC-156 review and caught it only by reading a count. Attribution integrity of the harness the mutation records ride on. |
| 9 | `wf.same_tree` untested while two commands authorize skipping the 25-file gate on its word | **SURVIVES → A** | Leg 2 squarely: the suite-skip fired live at SCC-156's own close; an untested predicate grants gate skips. |
| 10 | Verify-wave grouping carries no regex pin | **KILLED** | Named dead class: pins on prose — vacuous by the house's own measurement (SCC-125: opposite-meaning file scored 323/323). The finding asks for more of a proven-vacuous guard. |
| 11 | The 6d suite-skip landed in 4b only; Step 5 never learned it | **KILLED** | Leg 1: no damage path — Step 5 runs the full gate, which is slower and safe. An unextended optimization is not a defect. |
| 12 | `merge-target-guard` refusal prints a stale rule sentence ("never with a story or chore lane") that reads as a misfire, and INC5's assertion is satisfied by the stale sentence | **SURVIVES → B** | Leg 1: actor = operator mid-incident reading a refusal that misdescribes the rule — the moment a gate most needs to be believed; plus a test that cannot fail its subject (leg 2). |
| 13 | Incident ref carrying an unlanded STORY tip — one quarter of the refused class unpinned | **SURVIVES → B** | Suspected hole, not symmetry: this classifier's arms have provably misrouted before (SCC-154: pairs fell to the unknown arm; narrowing alone did NOT re-refuse). |
| 14 | Multi-lane transient: lane N+1's preflight hard-errors "STALLED LANDING" while lane N's push is mid-flight | **SURVIVES → B** | Leg 1: actor = operator invoking `/smh-merge-multiple-workingtrees` (a real command); a false red in a shipping path — the exact class the guard charter prices above a miss. |
| 15 | A6's phrasing (sweep-script template vs SCC-145's no-sweep-scripts ruling) | **N/A** | An open OPERATOR ruling row in lane-speed's Your Actions — leg 3 is theirs to exercise, not triage's to kill. Stays where it is. |
| 16 | `scripts/INDEX.md` still writes rot-prone counts | **KILLED** | Leg 1: no damage path — counts drift harmlessly beside a lint that never reads them. Housekeeping preference. |

### SCC-154's nine (gate-edges review)

| # | Item | Verdict | Reason |
|---|---|---|---|
| 1 | ff-variant coherence: the backstop skips the four-pair check for incident refs; divergence stated nowhere | **KILLED** | The divergence IS the design ruling (emergency absorb must not be walled; false red priced above a miss). A one-sentence doc note rides any future backstop lane — not work. |
| 2 | `incident:incident` falls to the unknown arm | **KILLED** | Leg 1: needs two SIMULTANEOUS incident lanes plus a cd-slip in a solo-operator system — cannot name the moment. Revisit if incident lanes ever overlap. |
| 3 | G7 story-direction pin (only chore direction tested) | **KILLED** | Coverage-for-symmetry, the named dead class — no suspected hole in that direction (contrast 156-#13, where the suspicion is documented). |
| 4 | Rename dirt across the `_artifacts/` boundary records only the NEW path | **KILLED** | Leg 1: requires deliberately `git mv`-ing tracked code INTO `_artifacts/` mid-stamp — accidents do not do that. Revisit if any flow ever relocates code across that boundary. |
| 5 | Latest-stamp-governs is FILE order; a re-review inserted ABOVE makes the stale verdict govern | **KILLED** | Leg 1: every flow appends (written convention); the actor is an agent hand-prepending against written law — a hypothetical chain. Revisit on the first prepend seen in the wild. |
| 6 | Reader-parity test binding `check_receipt` ↔ `receipt_defect` | **KILLED** | The unification landed — one shared function; the test would prove a function equals itself. The refactor that re-splits them owns that test. |
| 7 | `dirty_paths` readback: rename-row and quoted-path parses uncovered | **DEFER** | Leg 2: receipts are cited evidence and the failure DIRECTION of a misparse is unverified — that uncertainty on the evidence spine is the case for 3 cheap cases. Rides the next receipts lane. Ledgered. |
| 8 | A validly-earned SKIP evaporates when `gate_plan` lacks `run_all.py` | **KILLED** | Fails safe: the punishment for the gap is a redundant full gate run in a repo with no suite. The finder called it a nitpick; the gate agrees. |
| 9 | Boot-prompt behavior (no judge tier for agent-facing prose) | **KILLED** | The finder's own verdict was "likely wontfix"; legs 1 and 2 both fail — there is no judge tier to run it against. |

**Tally: 25 items → 8 survive (2 proposed decided tickets) · 3 judged ride-alongs ledgered ·
13 killed with reasons · 1 stays an open operator ruling.** Zero residue tickets.

## Proposed decided tickets — SUPERSEDED 2026-08-15 (operator ruling: "not the full fix")

> ⛔ **This section is the defect the follow-on lane fixed.** The operator ruled, after this lane
> merged: *"160 was not a fix … we need the fixes made in thread not a ticket made every story
> thats an endless loop that never finishes."* A "proposed decided ticket" the operator must rule
> on is still a ticket every story spawns. Under the recut law (`chore/SCC-160-fix-in-thread`,
> `_artifacts/_main/2026-08-15_fix-in-thread/walkthrough.md`) every survivor below was **fixed
> in that lane or dropped with a reason** — 9 fixed, 2 dropped, zero tickets. The list stays as
> history of what the first cut got wrong.

- **Ticket A — evidence-integrity fixes** (`run_all` harness + close-out scripts, one lane):
  `--case` exact-match with over-match refusal + un-truncated labels + `--case=` row (156 #1–3,
  one change), orphan-`c.check` AST meta-case (#8), `wf.same_tree` pins (#9). Ride-alongs #4 and
  #7 fold in free — same files. Every item passed leg 2: these protect mutation-kill attribution
  and gate-skip evidence the merge messages already cite as proof.
- **Ticket B — merge-gate truth** (`merge-target-guard` + `task_preflight`, one lane): stale
  refusal sentence + INC5 made falsifiable (#12), the story-tip quarter pinned (#13), a
  mid-flight arm for the multi-lane STALLED LANDING false red (#14). Every item is either an
  operator-facing gate lying at a high-stress moment or a false red in a shipping path.

## Evidence

| Check | Result |
|---|---|
| `run_all.py` | PASS 27/27 files, exit 0, 86.9 s @ `8ae3f55` (`gates/suite.json`) — post-absorb |
| `workflow_lint --toolkit-only` | PASS 0 errors 0 warnings, exit 0 @ `fe20441` (`gates/lint.json`) |
| `check_maps --depth3-only --strict` | PASS exit 0 @ `9aa0404` (`gates/maps.json`) |
| Contract pins | the suite's own `test_review_engine.py` pins the law: 2 rewritten sentences re-pinned + 3 NEW self-falsifying pins (gate exists · severity cannot bypass · residue retired) — each proven able to reject its counter-example by the framework itself |
| LLM review | none — the only script change is the pin table in `test_review_engine.py` (test-only); law + record surgery otherwise, certified by the mechanical gates above |

## Your Actions

- [x] ~~**Rule on Ticket A and Ticket B**~~ — **struck 2026-08-15 by the operator's ruling**
      ("we need the fixes made in thread not a ticket made every story"): this row was the retired
      defect wearing a new name, and it is what held SCC-160 on `Review Required`. Resolved
      in-thread on `chore/SCC-160-fix-in-thread`: A #1/#3/#4/#7/#8/#9 and B #12/#14 fixed with
      pins, A #2 and B #13 dropped with reasons — see
      `_artifacts/_main/2026-08-15_fix-in-thread/walkthrough.md`. No ticket was minted.
- [x] **The merge itself.** Signed off 2026-08-15: you invoked `/smh-close-task-merge-tree`
      (door 3), this ceremony's own act — the token quotes the invocation and Step 6's
      verification is the landing record.

**Landing order vs `chore/SCC-155-label-tasks`: resolved live.** SCC-155 landed first
(`9237d28`); this lane absorbed origin/main at `89cdc86` on the operator's word ("155 just
pushed / make a pull from main"). One conflict, the predicted class: both lanes' new
`_artifacts/_main/INDEX.md` rows — resolved keeping both, newest first; jira.md / MEMORY.md /
SOP auto-merged. Doors + caches re-synced post-absorb (20 launchers regenerated). Of note:
SCC-155 shipped `jira_feed finish`, which HOLDS a ticket whose walkthrough has open
`## Your Actions` boxes — the machinery this lane's close-out will meet by design, since the
Ticket A/B ruling rows above stay open until your word.
