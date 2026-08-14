# Implementation Plan — SCC-156 + SCC-159 (one lane, one landing)

**Lane**: `chore/SCC-156-lane-speed` off `main` @ `61f2a24` · worktree `.claude/worktrees/lane-speed`
**Ruling (operator, 2026-08-14, this session)**: SCC-156 and its subtask SCC-159 are worked in ONE
working tree, ONE push — SCC-156 to completion first, then SCC-159. Same shape as the SCC-154
precedent (two tickets, one lane, explicit ruling). Lane key / `--expect-key`: **SCC-156**.

**Tickets**:
- SCC-156 (Task) — Sweep + suite speed: harness `--case` filter, targeted-kill mutation sweeps,
  parallel `run_all`, whale split, command-body edits, close-out overlap, verify-wave grouping,
  template fixtures. Scoped by the 3-agent lifecycle audit; all baselines MEASURED (Mac).
- SCC-159 (Subtask of SCC-156) — Merge-gate residue, the 3 items that survived the operator's
  2026-08-14 wontfix ruling: stuck-landing early warning · ff-variant incident coherence (C3
  sequencing binding) · incident:incident policy.

---

## Step 1 — The checkable acceptance list

Authority order: the tickets' own ACCEPTANCE blocks, restated checkable. SCC-156 items:

- **C1** (A1): Replaying the SCC-154 17-mutant sweep with targeted kills yields IDENTICAL kill
  verdicts in ≤ 6 min (was ~21); the width-sweep replay ≤ 2 min (was ~11.5). Checked by running
  both replays and pasting timed output.
- **C2** (A2): `run_all.py` wall ≤ 110 s pre-split and ≤ 60 s post-split on this Mac; the summary
  line and exit semantics are byte-identical to today's contract; `--serial` works; one
  parallel-vs-serial comparison run pasted.
- **C3** (A3): `--case` with zero matching blocks exits NON-zero — proven by a test in the suite,
  plus the harness's own RED paste.
- **C4** (A4): every doctrine/command-body edit lands in the SAME commit as the mechanism it
  describes; `sop_currency` satisfied by staging (checked: commits enumerated in the walkthrough,
  gate did not refuse).
- **C5** (A5): every baseline number is RE-MEASURED at landing and pasted in the walkthrough —
  measured, never asserted.
- **C6** (A6): the closing full-file green remains MANDATORY in the doctrine text and in the sweep
  script template — checked by grep of the landed rule + template.

SCC-159 items (restated checkable; the subtask has no lettered block):

- **C7**: close-out preflight refuses-or-warns when local `main` is ahead of `origin/main` before a
  lane merges — a test seeds that exact state and asserts the verdict; the friendly path (local ==
  origin) still passes.
- **C8**: the ff-variant incident hole is CLOSED-or-DOCUMENTED per the ticket's either/or, with the
  C3 sequencing honored: target-side INC pins + width mutants land FIRST (their own commit), then
  the behavior change. Both halves gated by named tests.
- **C9**: incident:incident gets a pinned verdict in BOTH directions (refuse expected), with tests
  proving both gates now speak with one voice on the pair.

Cross-cutting:

- **C10**: full enforcement suite green through `gate_receipt.py` on the final code-touching commit;
  `workflow_lint.py --toolkit-only` 0/0; `check_maps.py --depth3-only --strict` exit 0.
- **C11**: the EXPLICITLY-KEPT list in SCC-156 is untouched — no relitigated cut lands (checked in
  review against the diff).
- **C12** (audit F5): ticket scope items 6a–6d, 7 and 8 each map to a landed sentence-level diff,
  cited by file:line in the walkthrough's evidence table — inspection-checkable, so the review's
  acceptance audit can walk the row without re-deriving intent.

## Step-to-assertion map — SCC-156

Grounded by recon 2026-08-14 (three parallel agents over this worktree; file:line refs are current
at 61f2a24). Each step lands as ONE commit carrying its mechanism + its doctrine/SOP edit (C4).

### S1 — `--case` block filter (ticket item 1; proves C3, feeds C1)

- `_harness.py`: `Cases` gains `block(label) -> bool` (an `if` guard — cases are inline
  `with TempDir():` blocks, so a context manager cannot skip a body) and `--case <substring>`
  parsing (harness-level; a file opts in by calling `c.block(...)`). Match = substring against the
  block label. `finish()` keeps the `-- P/T passed --` tally byte-identical when unfiltered; under a
  filter it appends a filter note line.
- **⚠️ AUDIT FINDING F1 — the exit-code contract, pinned**: exit `0` = filter matched, all run
  cases passed · `1` = matched cases had failures · **`3` = zero blocks matched OR a matched run
  executed zero cases** (the vacuous-green edge: a matching block with no `check()` rows must not
  read as pass). Sweep scripts treat exit 3 as a HARD error — never as "survived", never as
  fallback-to-full-file; fallback fires only on exit 0 (mutant survived its named case).
- **⚠️ AUDIT FINDING F2 — block independence proven, not assumed**: `test_task_preflight.py` has a
  documented cross-block leak shape (`preflight()` re-seeds the board stub because env survives
  TempDirs). After wiring labels, run EVERY block solo (`for L in <labels>: file --case L`) once
  and paste the tally; a block that fails solo gets self-seeding fixed before any sweep trusts its
  label. This loop is also the first live zero-match proof (a bogus label exits 3).
- Wire blocks into the two whales only (77 % of wall): `test_git_hooks.py` already carries
  `TOKEN · ` case prefixes and `# ── TOKEN · … ──` headers (e.g. :211/:221) — labels reuse those
  tokens. `test_task_preflight.py` block labels invented at wrap time from its `# ── … ──` section
  headers (:197–:1509 map is in recon); the sweep table gains a block-label column.
- **Assertion (RED first)**: ONE new file `test_suite_runner.py` (audit F3 — one new suite file,
  not two; blocks `CASE·` and `RUNALL·` inside it) — builds a mini tests dir in a TempDir (copies
  `_harness.py` + a 3-block fake test file), asserts: filtered run executes only the matching
  block; unfiltered output byte-identical to today's contract; **zero-match and zero-cases-run
  exit 3** (C3/F1). RED before the harness edit.
- Same commit: command-body sentences naming the FOUR consumers of `--case` (ticket item 3):
  `smh-quick-dev.md` Step 2 (RED proofs: run the new cases only) + Step 3 fix-loop wording;
  `smh-code-review.md` :190 assertion-evidence row (cite named cases, full file not required);
  doctrine cross-ref for mutant kills; matching SOP nodes (`workflows_testing_SOP.md` :1119–:1120,
  :1206–:1208).

### S2 — targeted-kill sweep doctrine (item 2; proves C6, feeds C1)

- `.agents/rules/tests-must-gate-for-real.md` § Mutation Testing: new subsection after the
  techniques block (:88/:93 seam): **targeted kills** (per mutant run ONLY its named killer case
  via `--case`; a non-kill auto-falls-back to the full file; NEVER parallelize the mutant loop —
  mutants mutate shared files on disk) + **width-mutant discipline** (narrowings, not just
  deletions — SCC-154 compound-6) + **the closing green is MANDATORY: the affected test FILES bare,
  after all restores** — recon confirms no closing-green sentence exists in the rule today, so C6
  *adds* it, and the sweep-script contract (restore-from-copies, sha256 verify, named-case kill
  classification) is written into doctrine as the required script shape (scripts stay
  scratchpad-only per the SCC-145 ruling).
- Same commit: SOP § Mutation (:1129–:1152).
- **Assertion**: grep-level — the landed rule contains the closing-green mandate + targeted-kill
  rules (C6); the real proof is C1's replay in S9.

### S3 — parallel `run_all.py` (item 4; proves C2)

- `ThreadPoolExecutor` over the EXISTING per-file subprocesses (work is in child processes; threads
  are Windows-safe for the PC). `--jobs N` default `os.cpu_count()`, `--serial` escape hatch.
  Output stays buffered per file and prints in today's alphabetical order (submit all, print in
  `FILES` order as each future resolves) — byte-identical summary `N/N files passed` + exit
  semantics; **the CI invocation string `python3 .agents/scripts/tests/run_all.py` is pinned by
  `test_main_write_gate_ci.py:93` and does not change** (flags all default).
- Share-nothing audit RECORDED with its true exceptions (ticket's "no file writes the live repo" is
  wrong in detail): `test_check_maps.py:132–155` creates+removes a live-tree probe dir and
  :260–316 a detached live-repo worktree — parallel-safe (single instance, unique paths, brief git
  locks) but stated in the walkthrough, not asserted away. `os.environ`/`os.chdir` writes are
  per-child-process — irrelevant under process-per-file.
- **Assertion (RED first)**: the `RUNALL·` block of `test_suite_runner.py` (F3) — mini tests-dir
  fixture (copied `run_all.py` + `_harness.py` + fake pass/fail files): parallel and `--serial`
  produce identical summary lines + exit codes; a failing file reds both modes; output order
  deterministic. RED before the executor lands. Then the A2 measurement: one parallel-vs-serial
  comparison on the real suite, pasted (target ≤ 110 s pre-split).
- Audit F6: `.agents/scripts/INDEX.md`'s rotted suite row ("1861 cases across 23 files, ~140 s")
  is IN-diff once run_all changes — updated in this commit, with the new measured numbers.

### S4 — split the whale (item 5; feeds C2's ≤ 60 s target)

- `test_task_preflight.py` (1,527 lines) splits at the recon-mapped seam: :194–:972 (lane / shape /
  artifacts / manifest / secondary-repos) stays `test_task_preflight.py`; :973–:1524 (SCC-146/154
  verdict + receipt gate — sole consumer of `ADIR`/`stamp_and_verdict`) becomes
  `test_task_preflight_receipts.py`. Module-level helpers (`git write commit make_repo branch
  BOARD_STUB board preflight`, consts) hoist to `_pf_fixtures.py` (non-`test_*` name ⇒ run_all
  ignores it); nested `secondary`/`with_secondary` stay with their section.
- **Assertion**: both new files green standalone; case-count conservation — 135 checks before ⇒
  135 across the two after (counted from the tally lines); `run_all` discovers both automatically;
  re-measured wall ≤ 60 s (C2).

### S5 — command-body one-sentence fixes (item 6; C4)

All four located verbatim by recon; ONE commit (+ SOP :740–:820, :1030–:1039):
- 6a `smh-quick-dev.md` :233–:246 — stamp-first: never pre-flight `run_all` bare before the receipt
  run; a red receipt is evidence working.
- 6b `smh-code-review.md` :202–:204 — DELETE the false auto-invalidation sentence (freshness is a
  TREE comparison — `wf_common.same_tree()`, `gate_receipt.py:201`); state: ONE re-stamp after the
  LAST code-touching change; artifact-only commits and no-op absorbs do NOT re-run. Fix the SAME
  stale claim at `smh-merge-multiple-workingtrees.md:198` (same falsehood, SCC-154 precedent).
- 6c `smh-close-task-merge-tree.md` :216–:224 — when the verdict is code-fresh, cite the review's
  link/anchor + SOP sweeps instead of re-walking them (armed hook + CI stay the net).
- 6d `smh-merge-multiple-workingtrees.md` :187–:199 (4b) + :288–:299 (Step 5) — the FINAL lane's 4b
  suite and Step 5's combined gate run on a byte-identical tree ⇒ skip one, gated on the existing
  `wf.same_tree` helper (`wf_common.py:198`; note: helper currently untested — S7's sweep adds a
  named killer for the sentence's gate condition via the run_all fixture, not a new module test).
- **Assertion**: `workflow_lint.py --toolkit-only` 0/0 after `/smh-sync-agents`; the review's
  acceptance audit maps each sentence to its ticket line.

### S6 — close-out overlap + verify-wave grouping (items 7–8)

- 7: `smh-close-task-merge-tree.md` — push the CI gate ref the moment the merge commit exists, THEN
  write the merge summary / draft the Dev Record during the ~50 s CI wall; poll
  `gh run watch --exit-status`. **Token mint stays strictly post-green** (TTL ordering
  load-bearing — sentence stays put). Same commit: SOP close-out mermaid (:745–:764).
- 8: `code-review-engine/steps/step-02-verify.md` — findings with identical `file:line` AND
  identical claimed behavior group into ONE verification query as **query-fan-in / result-fan-out**
  (N findings → 1 query → N indexed results), preserving the two recon-confirmed invariants: the
  BY-INDEX join (:66–:68) and the RAW pre-dedupe count for the self-gate (:24–:27). Step-03's
  merge rule untouched. Mirror `.claude/skills/code-review-engine/` moves via sync.
  **⚠️ AUDIT FINDING F7**: `test_review_engine.py:397-443` pins step-02 sentences (role wave, gate
  table, prompt routing, dossier assembly). The grouping edit must be ADDITIVE — no pinned
  sentence reworded — and `test_review_engine.py`'s green tally is this step's named assertion.
- **Assertion**: lint 0/0 + door parity; `test_review_engine.py` stays green (it pins engine
  structure); the grouping text names both preserved invariants explicitly.

### S7 — mutation sweep over the NEW machinery (doctrine-shaped, first live targeted-kill run)

- Declared table BEFORE mutating, drawn from the CODE: ≥ 8 mutants across `_harness.py` (filter
  match inverted; zero-match exit forced 0), `run_all.py` (jobs forced 1 silently; summary line
  altered; failure list dropped; deterministic-order removed), `_pf_fixtures.py` hoist (template
  cache returns stale tree — if S8 lands first), each with its NAMED killer case + block label.
  Run in the new targeted-kill mode — this sweep is itself C1's mechanism proof — closing green =
  affected test FILES bare.

### S8 — template-repo fixtures (item 9; last, smallest)

- `_pf_fixtures.py`: `make_repo` builds each kwargs-variant ONCE per run into a per-process
  template dir, then `shutil.copytree` per call site (13 ms vs 119–260 ms measured);
  post-copy `git remote set-url origin <copied bare>` re-points the absolute remote path;
  template tracked-state verified once per run. `test_task_preflight` first (78 call sites /
  89 TempDirs); `test_git_hooks` only if its 3-builder shape ports cleanly — otherwise named
  as deferred residue, not smuggled.
- **Assertion**: both files green with identical case counts; re-measured wall pasted.

### S9 — measurements + receipts (C1, C2, C5)

- Replay the SCC-154 17-mutant sweep targeted (identical kill verdicts, ≤ 6 min) + the 7-mutant
  width sweep (≤ 2 min) — timed, pasted (C1). `run_all` timed serial vs parallel, pre- and
  post-split (C2). Every ticket baseline re-measured and pasted (C5). Suite stamped through
  `gate_receipt.py` on the clean tree (C10).

## Step-to-assertion map — SCC-159

Grounded by recon: the guard's pair table is `merge-target-guard.sh:171-203` (four refuse pairs
:185, incident wildcard :191 — order load-bearing, the M-B2 mutant shape); the backstop's incident
skip arm is `pre-push-merge-backstop.sh:110-121`, correctly BELOW the :108 zero-deletion check;
`task_preflight.py` has NO `main...origin/main` comparison anywhere (only the lane-vs-upstream pair
at :640-649 and `base_ref` at :146-150); both close-out commands only check `0 0` AFTER the push,
and `pull --ff-only` succeeds silently when local main is merely ahead — the hole is real.

Three decisions the subtask leaves open, PROPOSED here for the operator's approval with the plan:

- **D1 (stuck-landing severity)**: `check_sync` gains the `main...origin/main` comparison. Local
  main AHEAD (or diverged) with a fresh fetch ⇒ **err** (exit 2 — a stalled landing, named, with
  the remedy `git push origin main` / inspect); fetch failed or absent ⇒ **warn** only. Behind-only
  stays silent (normal mid-flow state).
  **⚠️ AUDIT FINDING F4 — the satellite hole in the fetch-based split**: on the operator's plane
  uplink READS pass while pushes die mid-upload (documented recall), so "fresh fetch ⇒ err" alone
  would hard-block every close-out exactly when pushing is impossible. The err path therefore
  carries an auditable exit: `--accept-unpushed-main`, which downgrades this ONE check to a warn,
  prints a loud ⓘ line naming the flag in the preflight output (so the walkthrough/close-out
  record shows it was used), and is documented in the close-out command as the deliberate-offline
  exit. Default stays err — the flag is typed per invocation, never sticky.
- **D2 (ff-variant)**: TEACH, not just document — the backstop's blanket incident skip narrows to
  a four-pair containment check: an incident ref carrying an UNLANDED story/chore tip refuses with
  the re-route remedy (the exact class the commit-time judge refuses); carrying main/epic content
  stays allowed; a bare incident ref stays allowed (G6 is the false-red control and must stay
  green). G7 already covers the reverse direction — unchanged.
- **D3 (incident:incident)**: REFUSE, both gates. Guard: `incident:incident` arm added ABOVE the
  :191 wildcard; comment :186-190 loses "incident with incident" from the unjudged set;
  `destination()` :213 remedy extended; header charter :51-63 updated. Backstop: D2's containment
  class includes a FOREIGN incident tip (two concurrent incidents + a cd-slip is the scenario).

### S10 — pins + width mutants FIRST (C8's sequencing, its own commit)

- Characterization-green pins beside the existing INC2/INC4/G6/G7 blocks in `test_git_hooks.py`:
  G6 re-pinned as the false-red control for D2 (bare incident push allowed, pipeline named),
  incident-ref-carrying-main/epic-content allowed, plus target-side pins for the D3 surfaces.
- Declared WIDTH mutants (narrowings, from the code) for every surface S12/S13 will touch — skip
  arm widened/narrowed both directions, allow arm drops `incident:epic` (the W4 shape), refuse
  arm below-wildcard reorder — swept AT THIS SHA killing by named case, proving the pins bite
  before any behavior moves.

### S11 — stuck-landing early warning (C7)

- `task_preflight.py` `check_sync` (:609-649 seam, same `rev-list --left-right --count` idiom,
  same `"sync"` section) per D1. A worktree resolves the shared `refs/heads/main` directly.
- **Assertion (RED first)**: new cases in the "Clean + pushed + current" block (:377-434; the
  existing un-absorbed case :395-401 is the fixture shape MINUS the push): local-main-ahead +
  fresh fetch ⇒ exit 2 naming the stalled landing; fetch-failed variant ⇒ warn/exit 1; local ==
  origin ⇒ still `clear to close out and merge`. Lands in whichever split file holds the block
  post-S4, with its block label in the sweep table.
- Same commit: `smh-close-task-merge-tree.md` + `smh-merge-multiple-workingtrees.md` preflight
  sections note the new check; SOP close-out section.

### S12 — ff-variant incident coherence (C8, behavior AFTER S10)

- `pre-push-merge-backstop.sh` :110-121: skip arm becomes the D2 containment check (still BELOW
  the zero-deletion check — the SCC-154 placement ruling holds).
- **Assertion (RED first)**: incident ref carrying an unlanded chore tip ⇒ REFUSED with the
  four-pair remedy; carrying story tip ⇒ REFUSED; bare / main-content-only ⇒ allowed (G6 class
  green). Real git, real push, per the file's own header law.

### S13 — incident:incident policy (C9, behavior AFTER S10)

- Guard + backstop edits per D3.
- **Assertion (RED first)**: INC3's 4-tuple loop extends with the pair driven BOTH directions
  (two distinct incident branch names); backstop refuses incident-B pushing incident-A's unlanded
  tip; INC2/INC4 allow pins stay green as false-red controls.
- Same commit: SOP rows :1321/:1329 + `.agents/scripts/INDEX.md:48` (both currently state the
  "deliberately unjudged" claim D3 narrows).

## Sequencing

1. S1 → S2 → S3 → S4 → S5 → S6 (SCC-156 rank order; each RED → GREEN → ONE commit with its
   doctrine/SOP text; `/smh-sync-agents` after the last command-body edit, door parity checked).
2. S7 sweep, then S8, then S9 measurements.
3. SCC-159: S10 (pins FIRST — C8's order) → S11 → S12 → S13, then its own sweep rows + re-measure.
4. Review gate over the COMBINED diff (`/smh-code-review`, expect-key SCC-156) → walkthrough,
   `task.yaml`, Dev Records for BOTH keys → STOP merge-ready (close-out is the operator's).

## Out of scope, named to keep the diff honest

- The EXPLICITLY-KEPT list in SCC-156 (C11) — nothing there is touched.
- SOP :1245–:1250 stale clean-code-audit claim — pre-existing rot outside this lane's sections;
  recorded as review-note residue, not fixed here. (The `.agents/scripts/INDEX.md` suite row moved
  INTO scope via audit F6 — run_all is in-diff; likewise its guard/backstop and task_preflight
  paragraphs update in S13/S11's commits, whose changes those paragraphs describe.)
- `docs/migrations/` hard-coded "6/6 files passed" prose — rotted long before this lane; residue.

## Self-Audit (2026-08-14)

Mode PRE-WORK · right-size **Full** (rules + two armed gates + shared scripts + four platform
surfaces). Repo/branch echoed from command output: `Repo: lane-speed | Branch:
chore/SCC-156-lane-speed`.

- **Phase 0** — change set named per S-step; checkable list C1–C12 traces both directions (F5
  closed the items-6–8 gap with C12). Lane check: no deployable path in the change set —
  `.github/` is NOT touched (S3 keeps the CI invocation string byte-identical, verified against
  `test_main_write_gate_ci.py:93`'s pin). Task lane is correct.
- **Phase 1** — blast radius walked row by row: commands → four doors via `/smh-sync-agents` +
  door-parity gate (S5/S6); rule edit → `tests-must-gate-for-real` is NOT in `workflow_lint.py`'s
  `_RULE_POINTERS` (verified :70-78), citing commands keep their § anchors; scripts → tests named
  per step, `scripts/INDEX.md` rows folded in (F6); gates ship riding the EXISTING armed hooks (no
  new arming surface, no new fresh-clone silent-off); no file moves except the whale split, which
  keeps the original filename live (no orphaned links; `sop_currency` exempts tests, SOP :1343);
  SOP same-commit named in every S; memory store untouched. **Sibling lane**: `label-tasks`
  (`chore/SCC-155-label-tasks`) appeared after this lane opened — holds ONLY its untracked
  artifacts dir, zero committed diff, zero file overlap today; its eventual shape (new command +
  SOP section) shares the two ledger files (`workflows_testing_SOP.md`, `commands/INDEX.md`) —
  re-diff at absorb (review Step 0.7 re-derives mechanically); **no landing-order dependency**.
- **Phase 2** — tripwires: two planned new test files collapsed to one (F3); every flag traces to
  an acceptance item (`--case`→A3, `--jobs`/`--serial`→ticket item 4, `--accept-unpushed-main`→C7's
  "warns-or-refuses" + the documented satellite reality, F4); block wiring limited to the two
  whales (N=2, ticket-scoped); vacuous-green edges closed by F1's exit-3 contract; no new command,
  no new rule file, no clone-and-tweak. Templates/sweep scripts stay scratchpad per the standing
  SCC-145 ruling — doctrine carries the contract, not a tree-shipped runner.
- **Phase 3** — pre-mortem: both machines (list-form subprocess + pathlib + ThreadPoolExecutor —
  Windows-safe; `python3`/`python` convention held); fresh clone adds no new silent-off gate;
  first victim of the stuck-landing err is the NEXT lane's close-out and the message names the
  stalled landing + remedy + the F4 exit; empty input closed by F1; four caches via sync + parity
  gate; sibling-lands-first re-checked at review Step 0.7; rollback — all git-revertible, no
  history rewrite, Jira `start` already idempotent. Surviving named risks: (1) parallel run_all
  exposes latent cross-file contention not visible serially — mitigated by the recorded
  share-nothing audit with its two true exceptions (`test_check_maps` live-tree probe + detached
  worktree; unique paths, single instance) and by `--serial` as the escape; (2) `test_git_hooks`
  fixture-port for template fixtures may not be clean — S8 explicitly allows deferring that half
  as named residue.
- **Phase 4 quick gates** — verification strategy: every C-item names its proving command (C1–C3,
  C5–C10 command-produced; C4 gate-produced; C11–C12 inspection rows in the review). Irreversible:
  none inside the lane; the merge itself is the operator's close-out. Vague steps: F1/F4 pinned
  the two the builder would have guessed. Convention fit: naming law untouched, door model via
  sync, artifacts in `_artifacts/_main/2026-08-14_lane-speed/`.

Findings table:

| # | Where | Severity | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | S1 exit contract | HIGH | typo'd/empty filter reads green or SURVIVED | baked: exit 3 class |
| F2 | S1 whale wiring | HIGH | cross-block leak makes solo blocks fail → sweeps lie | baked: solo-block loop pasted |
| F3 | S1/S3 new files | LOW | two suite files where one serves | baked: `test_suite_runner.py` |
| F4 | S11 / D1 | HIGH | satellite: reads pass, push dies → close-out bricked offline | baked: auditable `--accept-unpushed-main` |
| F5 | C-list | MED | items 6–8 land untraceable → read as drift | baked: C12 |
| F6 | INDEX.md rows | LOW | rotted suite row survives a run_all change | baked into S3/S11/S13 |
| F7 | S6 item 8 | MED | rewording a pinned step-02 sentence reds the engine suite | baked: additive-only + named assertion |

Sibling-lane landing-order dependency: none (see Phase 1).

Audit verdict: GO

