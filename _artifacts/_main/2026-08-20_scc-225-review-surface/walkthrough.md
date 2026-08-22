---
IsArtifact: true
ArtifactMetadata:
  title: SCC-225 — Review-surface optimization, consolidated lane walkthrough
  type: walkthrough
  date: 2026-08-20
---

review-runtime: fan-out

# Walkthrough — SCC-225 (consolidated lane, riders SCC-226…SCC-233)

One worktree (`chore/SCC-225-review-surface`), one plan, eight riders + one ride-along, subtask
key leading each commit. Batch approval "approved" recorded at `dab054a` over the plan as of
`51ecbd3`; the operator placed the labeller fix in-lane with the first subtask ("just fix it in
this one").

## What landed, per rider

| Rider | Commits | What |
|---|---|---|
| SCC-226 A | `5e5dbd5`, `0e21e76` | ride-along: `label_tasks.py` `blocked_by` made directional (RED fixture: two declarers on one blocker; 104/104) · the `## Declared Change Set` fixed form + `declared_change_set.py` parser/diff (12/12 RED-first) · rule amendment at `artifacts-always-first.md` §plan contents · 3 emitters updated · both INDEX rows |
| SCC-228 C | `91643d6` | `risk_seam.py` placeholder behind the stable seam; `gates_audit()` False for every return, pinned (5/5) — SCC-223/224 swap in without touching the audit |
| SCC-227 B | `0bc8ecd` | both self-audit twins rewritten: 3 lenses, anchor grammar, coverage-not-findings, Scope Ledger, corroboration=sort-only, LEDGER/LEDGER+BLAST, amendment rule at top; deleted the phase skeleton, prose over-engineering critique, refutation phase, severity rubric. Contract test 32/32. SOP + quick-dev refs same commit |
| SCC-229 D | `468cfa5` | step-01's five lens-state sections → ONE roster contract; invariant stated once; mutation per scar (SCC-147/173/177/203, skip≠dead); `lenses_run` shape untouched. **Size honestly REPORTED: 39.6KB → 41.2KB (+1.6KB)** — the contract preamble outweighs the dedup; no byte target existed |
| SCC-230 E | `87cc128` | cost claim struck (measured Arm-A table cited to scoring.md; Literal-Correctness labelled unmeasured; Edge Case = most expensive AND the one unseeded true positive) · :440 scope-fenced, uncited pr-af figure and self-sealing clause removed; guards 25/25 |
| SCC-231 F | `cb4ea6c` | both review twins keep diff-vs-acceptance and gain diff-vs-declared-set (`drift.undeclared` important · `drift.unimplemented` suggestion · absent block = important, never silent); fixtures with A; twin checks 22/22; SOP same commit |
| SCC-232 G | `f592b4c` | **measurement first**: Literal-Correctness on the SHA-1-verified SCC-124 fixture, Arm A = 1,082.0 s (n=1; 3-round mean lower-bounded 360.7 s — decision invariant), 8.5× the 127.4 s threshold → quick = Test-Adequacy + Acceptance; LC → standard. Level DERIVED at each twin's Step 0.7, no caller flag, no budgets/caps; excluded lenses = skipped-by-mode; SOP same commit. Addendum: `lc-cost-measurement.md` |
| SCC-233 H | `4cd830c` | `src=<lens>` on every box (multi-lens `blind+edge`), per-lens `dispositions:` in the returned summary (survived/dismissed/relevance-killed), dead boxes still never reach the builder; SKILL.md mirrored (6/6) |

Door sync ran once after the last command edit (23 launchers regenerated, all four platform
caches published).

## Deviations and dispositions, stated

- **`cicd-quick-dev.md`, ground truth in two stages** — declared EDIT at plan time, deliberately
  not edited at build (it is a non-emitter: the fast lane skips plans by design; its eject defers
  to the full lane's plan machinery). The review wave then DID edit it, for a different reason:
  its record instruction gains the `dispositions:`/`drift:` lines, and the non-emitter status is
  now PINNED by `test_declared_change_set.py` rather than remembered. The plan's entry was
  rewritten to say exactly that.
- **`commands/INDEX.md` conditional entry CUT** (review finding 12): rows 47/51 re-read in full —
  they describe the dev flow's epic-kickoff/per-story split and the quick-dev ordering, not the
  audit's internal phase model, so the rewrite left them accurate and the conditional edit was
  never needed. The plan's own F1 characterization was loose; the entry is cut, per the drift
  law's first remedy.
- **Part I attribution record corrected** (review finding 38): the plan's amendment paragraph
  wrote "keyed to the parent SCC-225" — a recording error. The shipped commits, test banner and
  the rider table above were SCC-226-keyed throughout, matching the operator's final instruction
  ("fix it with the very first sub task"). The plan is amended; the work itself was right.
- **The `_AP` twins were not touched** (abandoned per the parent's constraints).
- **SCC-234 is a dead pointer**: the parent's index row I names a deleted key Jira cannot
  reissue; keys SCC-235…238 exist, so no mint can restore the number. The close-out-audit work
  (surface 3) remains un-run — the parent's own text says its scope is deliberately unspecified
  until its audit runs. Operator declined a new ticket for the labeller fix; the surface-3 row
  needs an operator ruling at close-out (fix the row, or run that audit as follow-on in-lane
  work).
- **Level names resolved to scope-named LEDGER / LEDGER+BLAST** (flagged for override at the
  stop; none given).
- **Measurement n=1, not 3 rounds** — recorded with the invariance argument in the addendum; the
  decision cannot change under any completion of the protocol.

## Gates

- Per-part suites RED-first, all green at their commits (104/104 · 12/12 · 5/5 · 32/32 · 25/25 ·
  22/22 · 6/6 → roster file 32/32 final).
- Full `run_all.py`: green pre-D (36/38 with the two known sync-drift rows); **post-review-fix
  full run: 39/39 files at `6d6fc42`** (twin parity 57/57 inside it). The pre-review run at
  `be37257` was green but its number went unrecorded — that omission is review finding 13, and
  recording THIS run is its fix.
- SOP currency: B, F, G staged the SOP in-commit; A, C, D, E, H carry `[sop-ok]` with reasons;
  the review-fix commit `6d6fc42` staged the SOP in-commit.

## Step 0.7 — blast-radius re-derivation (at verdict time, 2026-08-20)

1. **What moved:** nothing — `origin/main` fetched fresh (`env -u GITHUB_TOKEN git fetch`) is
   `ba7feb7`, which IS this lane's merge-base; no commit landed on main since the fork.
2. **What that changes here:** nothing — the Step 0.7 derivation stands: `review_level: standard`
   (rule + command + engine surfaces in the radius; 43 reviewed files, 50 after the fix wave).
3. **What was re-measured:** `merge-tree` vs `origin/main` — zero conflicts; sibling overlap
   re-diffed — the one live lane (`SCC-235-dual-surface-blast-radius` @ `dae82f8`) touches only
   its own planning folder, zero file overlap; gates-not-files cross-check: SCC-235 (lane dated
   2026-08-19) is EXEMPT from this lane's new dispo-era roster gate, and its future review runs
   this lane's new drift law — its pre-block plan will read `present: false`, one disposition,
   expected and not a collision. Landing order: THIS lane lands first.

## Code Review (2026-08-20)

Verdict: PASS @ 6d6fc42

Suite evidence measured at `6d6fc42`: full `run_all.py` **39/39 files** (twin parity 57/57).
The review ran on the lane diff at `be37257` (43 files, `review-diff.patch` here); every
surviving finding was fixed in-thread in `6d6fc42`, so this verdict describes the post-fix tree.

- scope: `origin/main...HEAD` @ `be37257` · `review_mode: full` (spec = this plan) ·
  `review_level: standard` (derived at Step 0.7: rule/command/engine surfaces in radius, 43
  files) · `lens_budget: standard`.
- method: code-review-engine fan-out — five lenses, then Evidence Verifier (all 42 grouped
  claims re-executed: 42/42 true, two severity revisions) and Compound Synthesis (9 compounds)
  concurrently; triage per step-03; fixes per the fix-in-thread contract.

review-runtime:  fan-out
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
findings:        0 decision · 50 patch · 0 defer   (0 noise-dismissed · 1 relevance kill)
dispositions:    per-lens: blind=7/0/0 · edge=10/0/0 · literal=8/0/0 · acceptance=10/0/0 · test-adequacy=6/0/1 · compound=9/0/0 (grouped-claim primary attribution; raw per-lens reports in the session transcripts)
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — measured post-repair at 6d6fc42; pre-repair this lane's own block returned 17 undeclared / 2 unimplemented / 1 incomplete (findings 2-3, fixed by the per-file rebuild)
severity_floor:  none — every critical/important finding was patched before this verdict

*(One stall on each of the five lenses and both step-2 roles — the 600 s stream watchdog, one
infrastructure transient; each was resumed with context intact and completed `ok`. Nothing was
rerun inline, so every state above is a true fan-out state.)*

### Findings and dispositions — 42 verified claims + 9 compounds

All severities are the verifier's (a revised severity outranks the hunter's). Every row marked
**fixed** landed in `6d6fc42`; the one relevance kill carries its leg per step-03.

| # | src | sev | finding | disposition |
|---|---|---|---|---|
| 1 | edge | important | parser prefilter silently drops non-dash bullets | fixed — ATTEMPT detection; star/no-space bullets report `incomplete` |
| 2 | blind | important | lane's own block fails its own parser (glob bullet; 17 undeclared) | fixed — block rebuilt per-file; tool now returns 0/0/0 on this lane |
| 3 | acceptance | important | two test files undeclared and undispositioned | fixed — declared in the block; dispositions here |
| 4 | literal | important | cicd drift snippet reads unbound `$REPO` | fixed — bound to `$PROJECT_ROOT`, same commit as the nargs change (compound-2 ordering held) |
| 5 | test-adequacy | important (was critical) | three-lens guard vacuous in the addition direction | fixed — both-direction count; Lens-4 mutant executed red |
| 6 | edge | important | `lens_budget` position guard anchors on first casual mention | fixed — anchored on the real h2; de-consolidation mutant now red |
| 7 | test-adequacy | important | `src=`/dispositions pins satisfied by prose | fixed — literal template-line pins; both executed mutants now red |
| 8 | blind | important | outside-run `blocked_by` promise had zero covering fixture | fixed — terminal-blocker fixture; follower-predicate mutant executed red |
| 9 | edge | important | scalar/case-slip `blocked_by` silently frees the declarer | fixed — shape normalisation + case-insensitive match + fixtures |
| 10 | blind | important | roster table routes LC "always" while quick excludes it | fixed — level-aware cells, symmetric pins, quick-membership pin |
| 11 | edge | important | level derivation is a partial function | fixed — anything-else row defaults HEAVIER in both twins; LEDGER excludes deployable paths |
| 12 | blind | suggestion (was important) | `commands/INDEX.md` conditional edit dropped without disposition | fixed — entry cut with grounds; disposition above |
| 13 | acceptance | important | gates line dangles; promised live regressions unevidenced | fixed — 39/39 recorded; both regressions executed below |
| 14 | acceptance | important | Part A's promised emitter structure check never materialized | fixed — three emitters pinned + non-emitter status pinned |
| 15 | acceptance | important | Part G assertions shipped as presence pins | fixed — addendum opened + number cross-checked; `--level` absence asserted; no-budget sentence pinned |
| 16 | test-adequacy | important | new shared twin law has no identity tier | fixed — review_level + declared-drift fenced in the code-review pair |
| 17 | edge | suggestion | arrow in why-prose corrupts the row | fixed — last-arrow split; fixture |
| 18 | edge | suggestion | empty re-taken diff dies exit 2 | fixed — nargs=*; boundary is now a defined state (landed WITH finding 4) |
| 19 | literal | suggestion | twins claim present:false for an absent plan FILE | fixed — twins state the loud exit-2 truth; CLI fixture pins it |
| 20 | literal | suggestion | six files cite a §plan-contents anchor that resolves to nothing | fixed — all six cite §2 Create the artifact folder + plan (anchor-or-delete) |
| 21 | literal | suggestion | smh dropped the constitution citation its NO-GO names | fixed — restored; pinned |
| 22 | literal | suggestion | smh sibling check lost its fetch guard | fixed — restored in smh; ported to cicd's sibling row; pinned |
| 23 | literal | nitpick | `drift.*` key paths do not exist in the tool's JSON | fixed — twins use the actual key names; dead spelling pinned out |
| 24 | acceptance | suggestion | planning-dir carve-out undocumented where reviewers read | fixed — carve-out bullet in both twins + SOP |
| 25 | edge | suggestion | fenced example bullets parse as entries | fixed — strip_fenced inherited (SCC-154); fixture |
| 26 | edge | suggestion | rename lanes yield config-dependent false unimplemented | fixed — `--no-renames` in the documented one-liner, both twins + SOP |
| 27 | literal | suggestion | comment omits the third outside-run state (unstarted) | fixed — comment names landed/foreign/unstarted and why unstarted stays free |
| 28 | edge | suggestion | self-referencing blocked_by wedges a lane behind itself | fixed — dropped loudly with a warning; fixture |
| 29 | edge | suggestion | second Declared Change Set block silently discarded | fixed — reported in `incomplete`; fixture |
| 30 | acceptance | suggestion | Part B mutations shipped weaker than promised | fixed — blocker sentence now in BOTH twins via the corroboration fence + CANON row; sort-order law CANON-pinned. The promised prose-sort fixtures are NOT buildable as real tests (prose law has no executable surface — the house's own prose-pinning scar); named here, stays |
| 31 | acceptance | suggestion | twins overstate what ANCHOR_RE machine-checks | fixed — claim reworded to shape-spot-check + applied law |
| 32 | blind | suggestion | review_level check token-presence; rule restated unpinned ×3 | fixed — ≤3-file threshold pinned across contract, both twins and the SOP; fence added |
| 33 | test-adequacy | suggestion | dispositions: line has no artifact-tier consumer | fixed — walkthrough_roster parses + GATES it (dispo-era lanes); fixtures both directions |
| 34 | test-adequacy | suggestion | SCC-231 disposition pin satisfied by the pre-existing sentence | fixed — unique bullet anchor + count>=2 |
| 35 | test-adequacy | suggestion | truncation/bare-path branches had no discriminating fixture | fixed — both fixtures + CLI subprocess tier |
| 36 | blind | suggestion | drift severity mapping pinned nowhere | fixed — per-bullet severity pins (a swap now reds) |
| 37 | acceptance | suggestion | Phase-0 lane check dropped beyond the enumerated deletion list | fixed — restored as Lens 1 check 4; pinned |
| 38 | acceptance | suggestion | Part I record says parent-keyed; work shipped SCC-226-keyed | fixed — record corrected (the work was right) |
| 39 | blind | nitpick | step-01 says unmeasured and cites the measurement | fixed — "unmeasured by that trial", SCC-232 result cited |
| 40 | acceptance | nitpick | lenses_run shape pin was presence-only for step-04 | fixed — step-04 block aligned to SKILL form + round-tripped through the parser |
| 41 | literal | nitpick | invalidated maximality comment in cmd_resolve | fixed — comment states the follower/fallback truth |
| 42 | test-adequacy | nitpick | tombstone regexes catch only exact old spellings | **dismissed — relevance leg 1**: variant-title re-accretion is speculative and partially netted by the ONE-section and defined-once checks |
| C1 | compound | important | diff verb strips the parser's only rejection signal | fixed — `incomplete` carried through; taught in both twins |
| C2 | compound | important | cicd drift dead at every layer; nargs fix alone removes the tripwire | fixed — `$PROJECT_ROOT` + nargs landed together; non-emitter pinned |
| C3 | compound | important | both new record obligations repeat the self-certification shape | fixed — walkthrough_roster gates `dispositions:`+`drift:` for 2026-08-20+ lanes |
| C4 | compound | important | SCC-233 chain unenforced at both ends | fixed — template pins (7) + machine consumer (33) + round-trip (40) |
| C5 | compound | important | asymmetric pinning steers maintainers toward the expensive routing | fixed — obsolete pins retired, current truth pinned both directions, quick membership pinned |
| C6 | compound | **critical** | twin-drift guards mutually defer over the self-audit pair; live divergence | fixed — shared law byte-aligned + four twin-law fences; FENCED_TODAY updated; constitution divergence healed; parity 57/57 now compares it |
| C7 | compound | important | wrong-door plans derive the lightest audit level | fixed — lane check restored + LEDGER deployable exclusion + heavier-default else-row |
| C8 | compound | important | promise-to-ship assertion downgrade is systemic (5 instances) | fixed — all five instances (13/14/15/30/40) + the assertion-drift law added to the drift contract. A mechanized assertion-level reconciler is over-engineering ledger: nothing requires it yet; the law + review practice cover it |
| C9 | compound | important | the rewrite's deletion list was falsified three times | fixed — all three drops restored (21/22/37) and pinned; the plan's amendment records the list was incomplete |

### Promised live regressions, executed (findings 13-15)

**Part B — the SCC-210 re-run (SCC-227's close-out regression).** The rebuilt three-lens
contract, applied to the frozen `SCC-210-implementation-plan.md`, surfaces BOTH known-good
findings, anchored and quoted, total 2 — not 44:

1. *The live test hard-naming the renamed files* — anchor `.agents/scripts/tests/test_command_surfaces.py:665`,
   literal text read: `"cicd-update-sprint-memory", "smh-update-maps-indexes"]` — a pinned door
   roster the plan's step-7 grep-and-re-point had to touch (Lens 2, the SCC-63 rename-scar row).
2. *The hand-authored skill doors* — anchor `.agents/skills/cicd-update-sprint-memory/SKILL.md:1-7`:
   no "GENERATED by sync-agents" header, prose launcher body; and the two renamed targets
   (`cicd-close-story-merge-tree`, `cicd-prune-worktree`) carry no skill door at all — the plan's
   "one sync run regenerates all of them" assumption fails exactly here (Lens 2, doors row).

**Part D — the SCC-124 fixture evidence.** The SCC-232 cost measurement executed the
post-consolidation step-01 assembly end-to-end on the SHA-verified fixture: the Literal-
Correctness lens, assembled per the consolidated contract, returned a real report — 2 important
findings including the vacuous-ARMED hole, a recorded true positive later independently fixed by
SCC-140 (`lc-cost-measurement.md` §Result). A full five-lens fixture re-run was NOT executed:
the per-scar mutations plus the step-04/SKILL round-trips cover the consolidation mechanically,
and the lenses whose prompts part D did not change buy no recall information from a ~30-minute
run. Named per the assertion-drift law: cut-or-name-why — named, stays.

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [ ] DECISION — the SCC-234 dead pointer (review deviation, recorded above): the parent ticket's
      index row I names SCC-234, a deleted key Jira cannot reissue, for the close-out-audit
      surface (surface 3) whose scope was deliberately left unspecified. Two clean resolutions —
      say which and the agent applies it as a board edit: **(a)** reword the parent's row to drop
      the dead key and mark surface 3 as future work with no number, or **(b)** keep surface 3
      live by rewording the row to "surface 3: unscheduled" and it gets planned as its own lane
      when you next call for it. (No new ticket is minted either way unless you say the word.)
