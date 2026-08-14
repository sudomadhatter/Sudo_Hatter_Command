# Walkthrough — SCC-149: incident branch-prefix taxonomy (guard carve-out + consumer step lists)

**Ticket:** [SCC-149](https://sudo-command.atlassian.net/browse/SCC-149) · **Branch:** `chore/SCC-149-incident-taxonomy` · **Plan:** `implementation_plan.md` (Self-Audit GO, operator `approved`)

## Task Checklist

- [x] Step 0/0.5 — worktree off main @ `44a12c1` (SCC-147's tip), assets linked, ticket → In Progress, sibling check (lens-budget fully landed, no dependency)
- [x] Step 1/1.5 — 6 acceptance items grounded in real lines; plan + self-audit GO; literal `approved`
  - finding while grounding: the SOP row drifted 1304 → 1311 after SCC-147; never trust a ticket's cached line number
  - finding while grounding: `test_git_hooks.py:489` (case N's comment) repeated the false taxonomy claim — a surface the ticket missed
- [x] Step 2 — RED: INC block, 3 assertions failing at their own checks (91/94)
- [x] Step 3 — GREEN: guard carve-out, 94/94; Commit 1 `f7f6961` (guard + tests + SOP row + INDEX clause, SOP staged with the guard — no `[sop-ok]`)
- [x] Step 3 — Cluster 2: three consumer carve-outs + mirrors; Commit 2 `fe225dc` (`[sop-ok]`, justification in message)
  - finding at the sweep: my own Commit-1 comment quoted the old false literal, re-tripping the acceptance-5 grep — reworded (the comment-literals-invert-source-grep-tests class, caught by running the sweep against HEAD instead of trusting the edit)
- [x] Step 3 — mutation sweep: 6 mutants (5 declared + 1 re-aim), 6 killed; restore from copies byte-identical; closing green run
  - finding in the sweep itself: M5's kill was a SYNTAX ERROR (empty `if` body), not a caught silent absence — every case crashed and the verdict line still said "killed by its named case". Re-aimed as M5b (note → `:`, script valid): killed by the note assertion ALONE. The red-dies-before-its-assertion class, inside the sweep built to catch it.
- [x] Full gate at `ec13bc7`, every command bare: run_all **23/23 files, 1911/1911 cases, exit 0** (exactly additive: 1907 main + 4 INC, predicted before measured) · workflow_lint --toolkit-only exit 0 · check_maps --depth3-only --strict exit 0
  - mid-lane hazard, caught before damage: one commit command ran in the SHARED CHECKOUT on main — the shell's cwd silently reverted between tool calls (the SCC-97 signature this very lane's gate exists for). The add was a no-op there and the commit refused empty; redone with `-C` pinned to the worktree, which every git call carries since
- [x] Step 4 — /smh-code-review: **Verdict: PASS @ `4fa5596`** — 5 lenses + verify wave over 17 findings; 3 applied (one doc fix: update-sprint-memory's incident arm gets an explicit STOP, `4fa5596`), 7 deferred to a named follow-on (backstop incident class + target-side/boundary tests, C3's test-first sequencing), 9 dismissed with measurement
  - finding at the stamp: HEAD advanced `fe225dc`→`2b96202` mid-review (this session sealing `ec13bc7`+`2b96202` as the review started); the delta was re-read and the verdict stamped deliberately past it (compound finding 4)

## Evidence

### Acceptance 1 — the guard positively classifies `claude/incident-*`, both arms proven on real git

The INC block in `test_git_hooks.py` drives real `git merge` through a real `core.hooksPath`
(the harness's charter: a source-grep cannot see whether git ever invoked the hook).

**RED — before the fix (guard at `44a12c1`'s state), the assertions fail where they assert:**

```
[FAIL] INC · a claude/incident-* hotfix merge into main is ALLOWED: edy:  git merge --abort   then re-check where you are standing:
[FAIL] INC · ...and it is never the story-lane refusal: edy:  git merge --abort   then re-check where you are standing:
[FAIL] INC · ...and the note names the pipeline that owns the lane: edy:  git merge --abort   then re-check where you are standing:
[PASS] INC · the ordinary story arm still refuses (the carve-out swallowed nothing): ...
-- 91/94 passed --
```

Which line raised: each `[FAIL]` is the case's own `c.check` — the captured evidence is the guard's
*refusal remedy text* (`git merge --abort …`), i.e. the story-lane refusal firing on the incident
merge, exactly the ticket's claim. Not a setup death. The fourth case passes green-first and is
declared as characterization: the story arm's refusal predates this lane (SCC-144's TBL loop).

**GREEN — after the fix, run bare (exit code read directly, no pipe):**

```
exit=0
[PASS] INC · a claude/incident-* hotfix merge into main is ALLOWED: SCC-149)
[PASS] INC · ...and it is never the story-lane refusal: SCC-149)
[PASS] INC · ...and the note names the pipeline that owns the lane: SCC-149)
[PASS] INC · the ordinary story arm still refuses (the carve-out swallowed nothing): ...
-- 94/94 passed --
```

The PASS evidence tail `SCC-149)` is the guard's new note actually printing in the captured merge
output — the allowed merge says who owns the lane.

### Acceptance 2 — the comment matches the code that now exists

`merge-target-guard.sh` lines 50–58 now describe the real shape (`claude/incident-<short-id-lower>`),
the real mechanism (carve-out ABOVE the story arm, first-match order called out as load-bearing at
the arm itself), and the real verdict (positively classified, deliberately unjudged). The old text
("`incident-*` is explicitly outside the branch model") described an arm that never existed.

### Acceptance 3 — each consumer carries the carve-out in its OWN step list

Commit `fe225dc`, one sentence each, at the exact step where the scan happens:

- `cicd-boot-sprint-memory.md` (the check-the-remote bullet): a `claude/incident-*` branch on origin
  is never "the step was already done on another machine" — report as incident, route nowhere.
- `cicd-merge-epic-workingtrees.md` Step 1.1 (the inventory): `claude/incident-*` matches are
  EXCLUDED — never fix, merge, land or PRUNE one there (the escalating arm).
- `cicd-update-sprint-memory.md` (the landing precondition): `claude/*` **and never
  `claude/incident-*`** — the branch satisfies the glob and must not satisfy the gate.

Mirrors regenerated by `sync-agents` (never hand-edited): `.opencode/commands/` ×3,
`.agents/workflows/` ×2 — update-sprint-memory's antigravity mirror exists but is a generated
14-line thin-launcher stub (the 12k-cap mechanism, SCC-135) carrying no step text, so it had
nothing to regenerate (measured by two review roles; this sentence originally claimed the mirror
did not exist, which failed against `ls`). Launcher skills likewise: thin doors, no step text,
nothing to propagate. Manifest updated.

### Acceptance 4 — SOP row corrected in the SAME commit as the guard

The four files landing together, output pasted (a review lens flagged this as the one narrated
claim among pasted ones; verified by two independent runs):

```
$ git show --stat --format='%h %s' f7f6961
f7f6961 SCC-149 fix(guard): claude/incident-* is positively classified, deliberately unjudged — the dead incident carve-out becomes a real one
 .agents/scripts/INDEX.md                        |  2 +-
 .agents/scripts/git-hooks/merge-target-guard.sh | 26 +++++++++++++++--
 .agents/scripts/tests/test_git_hooks.py         | 38 +++++++++++++++++++++++--
 docs/_scc_sops_prds/workflows_testing_SOP.md    |  2 +-
```

`sop_currency` was satisfied by staging the SOP with the usage surface, not by `[sop-ok]`.

Two-machine note (owed by the plan's self-audit): every command in this lane ran Mac-side
(`python3`, `pwsh`); on the PC the same gates run as `python` — the guard itself is POSIX sh with
no interpreter probe, per its own header, so the fix carries no per-machine surface.

### Acceptance 5 — the sweep, both patterns, including `.sh` and `docs/`

**Scope stated honestly (a review verifier measured this):** the pasted sweep below ran the
ticket's four enforcement dirs — `.agents/commands`, `.agents/rules`, `.agents/scripts`, `docs/` —
which is what acceptance 5 names. A literally repo-wide run at the same sha returns ~29 further
hits, **all inside `_artifacts/`**: prior lanes' plans and walkthroughs quoting the old literal as
history (this lane's own docs among them, unavoidably — they narrate the removal). That class is
the ledger doing its job, not a live surface; the enforcement dirs are the claim. Sweep B
(unbackticked) is zero even repo-wide.

Run against the committed tree (`git grep … HEAD`), noise filter documented:

```
=== sweep A: backticked `incident[-/] minus claude/incident ===
cicd-mobile-error-team.md:17,234   — `incident:<short-id>` is a GitHub ISSUE label; `incident-response.yml` is a WORKFLOW FILENAME
git-policy.md:212                  — the protected rule sentence itself (acceptance 6)
mobile-mode.md:48                  — workflow filename
test_git_hooks.py:491,529          — the bare `incident-42` FIXTURE name (case N's point, post-fix)
test_task_preflight.py:306,343     — historical comments about the OLD dead shape (accurate history)
sentry_error_response_team.md:176, tea_deep_reference.md:613 — artifact/command filenames
=== sweep B: unbackticked incident-\* ===
(zero hits after the comment reword)
```

Zero bare branch-prefix survivors. The one post-commit-1 hit was this lane's own comment quoting
the removed literal inside its removal story — the comment-literal class: a grep guard cannot tell
a claim from a mention of the claim. Reworded in `ec13bc7`; the sweep above is the final run at
that sha, and sweep B's zero includes `.sh` and `docs/` as the ticket demanded.

### Acceptance 6 — `git-policy.md:210-212` byte-identical

```
$ shasum -a 256 .agents/rules/git-policy.md      # captured BEFORE any edit
e1e165040d7a98350a5fed9ec4fdb94a6d37bf61f3eac0286de57a64208cbc90
$ git diff main...HEAD -- .agents/rules/git-policy.md
(empty)
$ shasum -a 256 .agents/rules/git-policy.md      # at the end
e1e165040d7a98350a5fed9ec4fdb94a6d37bf61f3eac0286de57a64208cbc90
```

### Mutation sweep — declared in the plan BEFORE running, all drawn from the code

Pre-declared in the plan; run as one sweep. Restore from COPIES (never `git checkout --`;
SCC-147's trap), application verified by an explicit unified-diff line count (SCC-129's lesson).

| # | Mutant | Named case | Result |
|---|---|---|---|
| M1 | incident arm moved BELOW `claude/*` (SCC-148's shadowing shape in a `case`) | INC allow | **KILLED** by its named case (exit 1) |
| M2 | pattern → `incident-*` (the old comment's fiction) | INC allow | **KILLED** by its named case (exit 1) |
| M3 | judge verdict `unknown` → `refuse` | INC allow | **KILLED** by its named case (exit 1) |
| M4 | pattern widened to `claude/*` (carve-out eats the story arm) | INC story-arm | **KILLED** by its named case AND the TBL loop (story→main, story→chore all flipped to allowed) |
| M5 | the pipeline-name note **deleted** | INC note | **killed dishonestly** — see below |
| M5b | the note replaced with `:` (script stays valid) | INC note | **KILLED** by its named case alone — the honest kill |

```
restored byte-identical: True
closing green confirmation: exit=0 ['-- 94/94 passed --']
```

**The M5 story — a finding against this lane's own sweep, caught by reading which line raised.**
M5 deleted both `echo` lines, which left an **empty `if` body — a syntax error in sh** — so every
case in the suite crashed and the sweep's verdict line still read "KILLED by its named case"
(the named case was indeed among the failures, along with everything else). That kill proves
deleting the lines breaks the script; it proves nothing about whether a *silently absent* note
would be noticed — the red-dies-before-its-assertion class, inside the sweep built to catch
exactly that class. M5b re-aims it: the note becomes a no-op (`:`), the script stays valid, and
the only case that can catch it is the note assertion — run separately, killed by that case alone.

## Code Review (2026-08-14)

Verdict: PASS @ 4fa5596

Suite evidence measured at `4fa5596` (bare re-run after the one review fix; byte-identical totals were
independently measured by the review on the `2b96202` tree first). **Stamped deliberately past the
lens-reviewed sha `fe225dc`** — the delta is `ec13bc7` (comment-only guard reword, reviewed by the
lenses as the then-uncommitted working-tree edit and flagged by the Acceptance lens in committed form),
`2b96202` (artifacts/docs only), and `4fa5596` (this review's own doc fix) — no code or test change
post-evidence.

- **Scope:** `main...HEAD`, 13 files at review time (guard carve-out + INC tests + 3 consumer commands
  + mirrors + SOP row + manifest + INDEX clause), re-derived against current `main` (Step 0.7).
- **Method:** `code-review-engine` (SCC-116) — 5 parallel clean-context lenses, evidence-verify +
  compound-synthesis wave over 17 serialized findings, triage per step-03; then acceptance audit,
  command-centre gate, `/smh-clean-code-audit`.

**Engine summary:**

```
lenses_run:      5/5   (blind ok · edge ok · literal ok · acceptance ok · test-adequacy ok)
lenses_na:       none  (review_mode: full, lens_budget: standard; 13 files ≤ cap, no truncation)
findings:        0 decision · 3 patch (applied) · 7 defer   (9 dismissed)
severity_floor:  none  (verify wave ran: verifier ok + compound ok, dossier built, extractor exit 0;
                        no unapplied decision/patch finding above suggestion; deferred never gates)
notes:           HEAD advanced fe225dc→2b96202 mid-review (dev session sealing ec13bc7+2b96202);
                 evidence re-based and re-measured at the new tree. Verifier: 16/17 findings true,
                 1 refuted. All three hunter-asserted importants revised down to suggestion with
                 traced reasoning; the three compound importants are the record's sharpest content.
```

### Findings (authoritative table)

| # | file:line | Severity | Finding | Disposition |
|---|-----------|----------|---------|-------------|
| 1 | merge-target-guard.sh:171 | suggestion | carve-out width: ALL incident topologies now unjudged (chore←incident, story←incident were refused-as-story pre-diff, now allow-with-note) | dismissed — documented-deliberate: the arm's own comment claims all incident merges for the pipeline, the plan's design decision argues it, and the ticket's "ALLOWED-with-note" wording permits it. Any future narrowing is bound by C3's sequencing |
| 2 | test_git_hooks.py:535 | suggestion | incident-as-TARGET untested (absorb `main` into the incident lane); the guard:206 note-line mutant survives 94/94 | deferred — follow-on test; verifier traced that no surviving mutant can flip an allow/refuse verdict on the absorb-main move (exposure is note-level) |
| 3 | merge-target-guard.sh:261 | nitpick | every incident merge prints "outside the branch model" and "positively classified" adjacently | deferred — cosmetic message branch; rides the follow-on |
| 4 | cicd-update-sprint-memory.md:237 | suggestion | the precondition's incident arm carried no stop verb; the next paragraph merges the epic unconditionally | **applied — `4fa5596`** (explicit STOP + handoff to `/cicd-mobile-error-team`; mirrors regenerated via sync-agents) |
| 5 | pre-push-merge-backstop.sh:67,100 | suggestion | backstop remedy tells an incident pusher to land on "its epic/* branch"; no incident-shaped ref is tested through it | deferred — pre-existing, outside SCC-149's ticket scope; see C1 follow-on |
| 6 | .agents/workflows/cicd-update-sprint-memory.md | — | "stale mirror not regenerated" | dismissed with measurement — a 1,086-byte generated thin launcher (12k-cap mechanism); carries no precondition text to go stale |
| 7 | merge-target-guard.sh:55 | nitpick | committed comment re-tripped the acceptance-5 sweep at fe225dc | dismissed — resolved in-lane by `ec13bc7`; review's own sweep at HEAD: zero survivors |
| 8 | workflows_testing_SOP.md:1311 | nitpick | acceptance-4 same-commit constraint invisible in a flattened diff | dismissed — verified: `git show --stat f7f6961` carries SOP + guard + tests + INDEX together |
| 9 | merge-target-guard.sh:264 | nitpick | note nested narrower than the whole no-refusal path | dismissed — traced: a pure incident merge always sets UNJUDGED, so the note always prints; silence occurs only on any-allow-wins, the guard's normal allow behavior |
| 10 | test_git_hooks.py:535 | nitpick | harness mechanics inherited, not re-proven by this diff | dismissed — shared fixtures already exercised by the file's 90 pre-existing checks; the RED run proves git invoked the hook |
| 11 | cicd-boot-sprint-memory.md:100 | nitpick | plan said "one sentence each"; carve-outs run 2–3 | dismissed — cosmetic deviation, substance delivered |
| 12 | merge-target-guard.sh (classify) | suggestion | boundary shapes unpinned: `claude/incident-` (empty suffix → incident) and `claude/INCIDENT-x` (case → story) | deferred — follow-on test; both current behaviors arguably correct, neither pinned |
| 13 | merge-target-guard.sh:212 | suggestion | a sha carrying incident + a refusable name REFUSES (unknown ≠ allow, so any-legal-name-wins does not extend to incident); semantics unpinned | deferred — intended-semantics question for the follow-on |
| 14 | the three carve-out sentences | suggestion | no doc-assertion test pins them, incl. merge-epic's prune-guard sentence | dismissed — SCC-147 convergence ruling: deliberately unguarded prose; prune-guard noted as the strongest candidate if ever revisited |
| 15 | merge-target-guard.sh:171 | nitpick | judge()'s incident row is behaviorally equivalent to the `*` default (its deletion mutant survives by equivalence) | dismissed — documentation + ordering insurance, deliberate; recorded so a future sweep reads the survivor correctly |
| C1 | backstop ← guard | important | compound: the widened unjudged set drains into a backstop whose refusal prescribes the SCC-148 misroute verbatim ("land it on its epic/* branch") — the enforcement machinery itself printing the taxonomy error, to a phone, mid-incident | deferred — named follow-on ticket: teach `pre-push-merge-backstop.sh` the incident class + drive an incident-shaped ref through it in test |
| C2 | update-sprint landing path | important | compound: on the incident-worktree → epic-landing path every mechanical layer prints allow (guard unknown×2, backstop exempt on epic pushes) and the only control was finding 4's verbless prose arm — with the guard's new note affirmatively reassuring "not a gap" at both merge points | **applied — `4fa5596`** closes the control-point half; the residual (guard note wording, backstop) rides C1 |
| C3 | walkthrough mutant table | important | compound: any future narrowing of the judge row is unauthorable red-first today — the width-mutants provably survive (by equivalence + the untested target side), so a botched narrowing ships at full green | deferred — sequencing constraint recorded: land finding 2's target-side test + width-killing mutants BEFORE any narrowing of finding 1 |
| C4 | verdict sha | suggestion | compound: no single sha carried both the verdict and the acceptance-5 evidence unless stamped deliberately | **applied** — stamped @ `4fa5596` with the fe225dc→HEAD delta enumerated above |

### Gates (each run bare; actual output)

- **Enforcement suite** — `python3 .agents/scripts/tests/run_all.py` → `23/23 files passed`, **1911/1911 cases**, `EXIT=0` (exactly additive: 1907 main + 4 INC)
- **Toolkit lint** — `workflow_lint.py --toolkit-only` → `-- 0 error(s), 0 warning(s), 8 info --`, `EXIT=0`
- **Assertion evidence** — the lane's own RED assertions re-run green: `test_git_hooks.py` → `-- 94/94 passed --`, `EXIT=0` (INC allow + no-story-refusal + pipeline-named note + story-arm control all PASS)
- **SOP currency** — `sop_currency.py --paths <17 changed> --message "SCC-149 …"` → `EXIT=0`
- **Link + anchor** — every path/`#L` anchor in the changed hunks resolved in-tree (mobile-error-team:17/:47, boot:96, update-sprint:237, SOP row, scripts/INDEX): 0 dead
- **Door parity** — n/a: no command added, renamed or deleted (three edited; mirrors regenerated, not hand-edited — verified by re-running sync-agents, which changed nothing beyond the review fix)
- **py_compile / bash -n / manifest JSON** — all OK on the changed `.py` / `.sh` / `.json`

### Acceptance matrix (ticket's 6 items → the assertion that proves each)

| # | Item | Verdict | Proving assertion |
|---|---|---|---|
| 1 | guard positively classifies `claude/incident-*`; both arms on real git | DELIVERED | INC block through a real `core.hooksPath`: RED 91/94 pre-fix (story refusal captured), GREEN 94/94 post-fix; story-arm control still refuses |
| 2 | line-51 comment matches the code that now exists | DELIVERED | guard lines 151–159 (arm + order comment) + 50–58 (header) read against the code; `ec13bc7` de-literalized the removal story |
| 3 | each Cluster-2 command carries the carve-out in its OWN step list; mirrors via sync | DELIVERED | boot:96–103 ("Except claude/incident-*… route nowhere"), merge-epic Step 1.1 (inventory EXCLUDES; never fix/merge/land/prune), update-sprint:237 (glob exclusion + explicit STOP since `4fa5596`); sync-agents regenerated all mirrors |
| 4 | SOP row corrected in the SAME commit as the guard fix | DELIVERED | `git show --stat f7f6961`: SOP + guard + tests + INDEX in one commit; row at 1311 (ticket's 1304 drifted with SCC-147 — documented) |
| 5 | repo-wide sweep zero bare branch-prefix survivors incl. `.sh` + `docs/` | DELIVERED | review's independent `git grep` at HEAD: zero outside the documented noise class (issue label, workflow filename, fixture names, historical comments, the protected git-policy sentence) |
| 6 | git-policy.md:210–212 byte-identical | DELIVERED | `git diff main...HEAD -- .agents/rules/git-policy.md` → empty (re-measured by the review) |

Nothing in the diff falls outside the acceptance list (no drift found beyond the findings above).

### Clean-Code Gate — PASS

**Machine floor**
- run_all.py       : PASS — 23/23 files, 1911/1911 cases, exit 0          [pasted above]
- workflow_lint    : PASS — 0 errors, 0 warnings (8 info: pre-existing BOMs), exit 0
- sop_currency     : PASS — exit 0 over the real changed set              [pasted above]
- py_compile       : PASS — test_git_hooks.py
- bash -n          : PASS — merge-target-guard.sh
- link + anchor    : PASS — all cited paths/anchors resolve, 0 dead
- door parity      : n/a — no command added/renamed/deleted
- lint / types     : not applicable to this repo (no venv, no ruff, no tsc)

**Judgment pass** — comment contract: every non-obvious changed block carries `SCC-149` provenance
(guard arm/header/judge comments, INC test comments); no stale AIDEV-NOTE touched; no unowned TODO.
Drift/bloat: imported from the engine table above (findings 1, 14, 15 — all dismissed with reasons);
conventions: naming law clean, generated files regenerated never hand-edited, both-machine spelling
(`python3`) respected, the new gate behavior ships armed and its tests prove both arms.

### Step 0.7 — blast radius vs current main (re-derived at review time)

- **Nothing this diff references moved on `main`:** merge-base = `main` = `origin/main` = `44a12c1`; the theirs-set is empty — nothing landed while this lane was built.
- **True overlap: none; `merge-tree --write-tree HEAD main` writes cleanly (no conflict entries).**
- **Sibling lanes:** `chore/SCC-146-gate-receipts` live at `44a12c1` (no commits) — no landing-order dependency in either direction.

**Changes applied by this review:** one — finding 4/C2 (`4fa5596`, doc + mirrors). Everything else:
implementation correct as-is.

### ⛔ Post-verdict note (2026-08-14 08:32, after the stamp)

Minutes after the Verdict was stamped and committed, an **uncommitted, untested behavioral edit to
`merge-target-guard.sh` appeared in this worktree from another session** (re-judges
`incident:story|incident:chore|story:incident|chore:incident` to refuse, adds a `destination()`
incident row, replaces the note lines — i.e. it implements this review's DEFERRED findings 1/3).
**It is NOT covered by `Verdict: PASS @ 4fa5596`**, which binds committed work only. It ships no
test and lands exactly inside compound finding C3's warning: the width-mutants provably survive
today, so this change is unauthorable red-first until finding 2's target-side test + width-killing
mutants land FIRST. Per the convergence rule (one review per lane) it must NOT be folded into this
lane's verdict — either move it to the C1/C3 follow-on ticket lane and restore the tree, or the
close-out preflight will (correctly) refuse the dirty tree.

**RESOLVED (same day, ~09:00):** the edit was the dev session's own concurrent review wave — two
reviews of one lane collided mid-flight (this section's review stamped first; the dev session's
23-finding verify wave was still open and had begun applying its patch bucket). Surfaced to the
operator with both options; **the operator ruled: honor the stamp.** The guard edit was reverted
(restore verified against HEAD; suite re-run bare: 94/94, exit 0), and the dev wave's surplus
findings are folded into the follow-on item below rather than looped on — the convergence rule
applied to the collision it was written for, one lane over from where it was written.

## Your Actions

- [x] **Resolve the post-verdict working-tree edit** — resolved on the operator's explicit ruling ("honor the stamp"): reverted, restore verified against HEAD, suite green bare (94/94, exit 0). See the RESOLVED note above.
- [ ] **Merge sign-off** — run `/smh-close-task-merge-tree` (mechanical close-out; the Verdict above is the review of record — one review per lane, per the SCC-147 convergence rule).
- [ ] **Follow-on ticket decision (C1/C3 + deferred tests)** — one Task: teach `pre-push-merge-backstop.sh` the incident class (its refusal currently prescribes the SCC-148 misroute for incident refs), landing the target-side INC test + width-killing mutants FIRST (C3's sequencing), then the judge-arm narrowing the reverted edit attempted (explicit refuse for `story/chore↔incident` — the four pairs fall to `*)`→unknown today, so narrowing the incident arm alone does NOT re-refuse them; the reverted draft had the arm shape), the note-replacement fix (finding 3: print the incident line INSTEAD OF "outside the branch model", which is runtime-assembled and grep-invisible), plus the deferred boundary/multi-name pins (findings 2, 3, 12, 13, 5). **From the dev session's concurrent wave, additionally:** boot's closing condition "Only when BOTH are empty" is unsatisfiable while an incident branch lingers on origin (amend to "empty after setting aside `claude/incident-*` matches"); the `:47` line-number pin in the INC test comment (de-literalize); case N gains `"/cicd-mobile-error-team" not in out` (kills the `*incident*`-widening mutant); a positive pin for the story-destination wording (INC (b)'s negative referent is otherwise unasserted anywhere).
