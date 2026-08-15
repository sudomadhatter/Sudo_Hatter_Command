---
IsArtifact: true
ArtifactMetadata:
  title: SCC-38 lane walkthrough — flight recorder (SCC-133) + autopilot done-means-green (SCC-134) + folded SCC-130
  type: walkthrough
  date: 2026-08-15
---

# SCC-38 lane — walkthrough

**Branch:** `chore/SCC-38-flight-recorder-autopilot-spec` · **Riders:** SCC-133, SCC-134 (operator
ruling: *"we will run them both in one branch. one then the other"*) · **Plan:**
[implementation_plan.md](implementation_plan.md) (`Audit verdict: GO`, `approved` received verbatim).

## Task Checklist

- [x] C1 — first commit: master plan `## Delta (2026-08-15)` + `open_tasks` proposal → 12-line pointer (`193d8ba`)
- [x] A1 — `flight_recorder.py record`: one event file, verdict-sha keyed, idempotent (`93dacb2`)
- [x] A2 — `candidates`: distinct-task ladder, `--json`
- [x] A3 — `surface`: silent-empty / one proposal per action-required rung / real hook run against a seeded repo
  - hook resolves the script beside itself (`$HERE/../scripts/…`) so the test can point `CLAUDE_PROJECT_DIR` at a temp repo and still exercise the real hook; `python3 || python`
- [x] A4 — door bound: `/smh-close-task-merge-tree` **Step 2.5** (pre-merge, artifacts-only commit); `/cicd-boot-sprint-memory` Step 3 line; SOP node + paragraph; scripts INDEX row; doors regenerated
- [x] A5 — manual-learnings question conditional in `cicd-update-sprint-memory` + `cicd-merge-epic-workingtrees`
- [x] B1 — `autopilot_bmad_dev_loop.md` §6a Done-means-green (five principles + "red gates stay human-in-the-loop, dropped not deferred") (`41f0ba2`)
- [x] `task.yaml` with `riders: [SCC-133, SCC-134]` (`aa5a8d3`); receipts chained clean (`828f95b` suite · `d5a2f8f` lint · `7f32ed2` maps)
- [x] Mutant sweep 13/13 killed pre-review; one test gap it exposed (rules-prefix) pinned first (`5fe9393`)
- [x] Review findings FIXED IN-LANE (`f6cd430`, `6a0541d`, `abbf875`) — operator ruling this session: *fix the relevant findings, ticket nothing*
  - the verifier's surviving mutant (`is_file → is_dir`) now killed; the post-review sweep is 18/18
- [x] Suite re-stamped ONCE after the last code-touching change (`abbf875`); receipts chained clean → `9530dd4`

## Evidence

Each acceptance item → the assertion → RED then GREEN. Suite file: `.agents/scripts/tests/test_flight_recorder.py`
(three `--case` blocks A1/A2/A3).

| Item | Assertion | RED (before) | GREEN (after) |
|---|---|---|---|
| A1 record | `--case A1`: one `workflow-events/2026-08/SCC-901_<sha7>.json`; `sha` = verdict sha ≠ `tip`; `changes` = lane files only after `main` moved on; fingerprints `rule-edited:.agents/rules/r.md`, `gate-red:lint` (not suite), `mention:gate_receipt.py` + `mention:/smh-code-review`, no `verdict:` on PASS; replay (and replay after an artifacts commit moved HEAD) writes nothing + says "already recorded"; no walkthrough → exit 2; no Verdict → exit 2 | `27/31` FAIL — `can't open file '…/flight_recorder.py'` (script absent; the 4 passes were the negative-shaped checks, vacuous on empty data) | `32/32 passed` |
| A2 candidates | `--case A2`: 3 distinct tasks → `action-required` (3 tasks, 3 shas, "commission the script"); same task twice → counts ONCE (2 distinct → `candidate`); 1 → `evidence`; `fingerprints: []` → no rung; `--json` parses | same RED run | same GREEN run |
| A3 surface + hook | `--case A3`: empty → no stdout, exit 0; malformed file → exit 0; seeded → exactly one PROPOSAL line naming SCC-11/12/13; **the real `session-start-context.sh` run with `CLAUDE_PROJECT_DIR=<temp repo>` emits it and exits 0**, and still prints its standing gate text | RED: 29/31 after the script existed but before the hook was wired — `A3 SessionStart hook emits …` FAIL | GREEN after the hook edit |
| A4 door | `smh-close-task-merge-tree.md` Step 2.5 present; `workflow_lint --toolkit-only` → `0 error(s), 0 warning(s)`; `check_maps --depth3-only --strict` exit 0; sync-agents regenerated 4 opencode mirrors + 2 workflows + `.claude/hooks/` copy; SOP-currency gate accepted the commit with the SOP staged | Step 2.5 absent | present @ `93dacb2` |
| A5 conditional question | `grep -n "manual learnings" .agents/commands/cicd-update-sprint-memory.md cicd-merge-epic-workingtrees.md` | `ask Daniel (always, …)` / `ask … once:` — unconditional | `CONDITIONALLY (SCC-133) … only when Step 3 routed ZERO learnings` / `once, and only if the set routed ZERO learnings` |
| B1 spec | `grep -c "Done-means-green" docs/_scc_sops_prds/autopilot_bmad_dev_loop.md`; `test_sops_prds_folder.py` | `0` | `1` (§6a, lines 313–362); folder test `61/61 passed` |
| C1 folded | `grep -c "Delta (2026-08-15)"` master plan; `wc -l` proposal | `0` · `135` | `1` · `12`, both pointer links resolve |

**Suite (through the receipt writer, clean tree) — FINAL, after the review fixes:** `28/28 files passed`,
exit 0, 87.9 s @ **`abbf875`** → `gates/suite.json` (committed `7fd697c`); lint `0 error(s), 0 warning(s)` @
`7fd697c` → `gates/lint.json` (`27736c3`); maps exit 0 @ `27736c3` → `gates/maps.json` (`9530dd4`).
(Pre-review stamps at `aa5a8d3` were superseded — the review's patches were code-touching.)
Assertion evidence, case-scoped: `test_flight_recorder.py` `--case A1` / `A2` / `A3` → `44/44 passed`;
`test_door_preflight_order.py` → `13/13`; `test_command_surfaces.py` → `57/57` after `sync-agents`.

**Mutant sweep — post-review, re-drawn from the PATCHED code (declared before mutating; every mutant an
edit to a real line; one run; sha256-verified restore; `git status` clean after):**

| Mutant | Edit | Killer | Verdict | Evidence |
|---|---|---|---|---|
| N1 | event keyed on HEAD instead of the verdict sha | A1 | KILLED | `A1 file name = <KEY>_<verdict sha7>.json` |
| N2 | FIRST stamp instead of LATEST | A1 | KILLED | `A1 file name …` (older CONCERNS stamp would win) |
| N3 | fences not stripped (decoy wins) | A1 | KILLED | `A1 dry-run …: [ERR] verdict sha deadbee is not a commit` |
| N4 | `--base` = local `main` | A1 | KILLED | `A1 changes = the lane's own files, three-dot from ORIGIN/main` |
| N5 | two-dot changes | A1 | KILLED | same case (origin/main advanced after the fork) |
| N6 | `warn` counted as red | A1 | KILLED | `A1 fingerprint gate-red only for the FAIL receipt` |
| N7 | no basename normalisation | A1 | KILLED | `A1 mention: path-form names normalise to their basename` |
| N8 | mention existence filter removed | A1 | KILLED | `A1 mention: NEG - doc names, unknown scripts … NOT fingerprints` |
| N9 | `RULES_PREFIX` widened | A1 | KILLED | `A1 rule-edited fires ONLY under .agents/rules/` |
| N10 | idempotency by dir-exists (the verifier's surviving mutant) | A1 | KILLED | `A1 a NEW latest verdict sha writes a SECOND file` |
| N11 | ladder floor 4 | A2 | KILLED | `A2 3 distinct tasks -> action-required` |
| N12 | raw count | A2 | KILLED | `A2 same task twice counts ONCE` |
| N13 | `surface` dies → `[ERR]` on stdout | A3 | KILLED | `A3 non-git --repo -> exit 0 and NOTHING on stdout` |
| N14 | `surface` exits 1 | A3 | KILLED | `A3 empty ledger -> no output, exit 0` |
| N15 | hook prints nothing | A3 | KILLED | `A3 SessionStart hook emits the proposal line` |
| N16 | hook: no beside-hook fallback | A3 | KILLED | same case (the temp repo has no script) |
| N17 | door: `record` moved AFTER the gate ref | door-order test (whole file) | KILLED | `ORDER flight_recorder.py record → pre-flight ref` |
| N18 | dry run writes | A1 | KILLED | `A1 dry-run writes nothing, exits 0` |

18/18 killed. Two first-draft survivors (N3, N5) were the FIXTURE's fault, not the code's — the decoy fence
sat before the real stamps (latest-governs rescued it) and origin/main never moved after the fork (two-dot ==
three-dot) — fixed in `6a0541d`, both then killed. Closing green: `test_flight_recorder.py` bare → `44/44 passed`.
The pre-review 13/13 table (M1–M13) is superseded; M8's verdict-family mutant no longer exists because the family
was removed.

## Decisions

- Keyed on the walkthrough's verdict sha, not HEAD — HEAD moves the moment the event is committed; a resumed close-out must not double-write (audit F1).
- One file per event, no materialised candidates view — sibling lanes never conflict; the ladder is recomputed on read (F2, F3).
- Bound PRE-merge as Step 2.5 — a post-merge write is a `main` write outside the token (F1).
- Renamed from the master plan's `command_center_closeout.py` to `flight_recorder.py` — a "closeout" name beside `closeout_preflight.py` that only records is a trap.
- The red-gate auto-fix loop for autopilot is DROPPED, not deferred — v2 is human-in-the-loop on TESTS RED by design; recorded in §6a and the master plan Delta.
- Cross-link from the autopilot commands to §6a CUT (F4) — a command-surface touch the ticket did not ask for.
- **Operator ruling, this session (verbatim): *"why dont we just fix the relivant findings? This exponetial ticket creation makes no sense … the agent will always find something during review, its the agents task."*** Applied here: every finding the review confirmed as real and worth doing was FIXED IN THIS LANE; the rest are dismissed by name in the review table; nothing is deferred, proposed, minted or owed. The 160 team receives the same ruling for SCC-160's open A/B rows.
- The `verdict:` fingerprint family was REMOVED on measurement (compound synthesis over the 83 landed walkthroughs: CONCERNS in 10 lanes — merges, unactionable; FAIL never reaches Step 2.5). Three families remain.
- Mentions must RESOLVE to a real file (`.agents/{rules,commands,scripts,hooks}`, `.githooks`, or a real `/smh-*` `/cicd-*` command) — a name that resolves to nothing is not a fingerprint. Kills the `walkthrough.md`/`MEMORY.md` noise and the truncated `policy.md` class at once.
- The verdict is read by the SAME reader the preflight trusts (`task_preflight.strip_fenced` + `VERDICT_RE`, latest stamp) — the first cut would have recorded FAIL on the landed SCC-83 walkthrough.
- `--base` defaults to `origin/main` when present — the door only fast-forwards LOCAL `main` after the merge, and the second machine routinely lags.

## Pitfalls

- `run_script` merges stderr into stdout, so a `[warn]` line for a malformed event file counted as "output" in the A3 line-count check — the test filters `[warn]` lines; the warning itself is correct behaviour.
- Lint/maps receipts stamped over an uncommitted suite receipt read `DIRTY` — chain them (commit each receipt, then stamp the next), exactly as SCC-160's log shows.
- A mutant that widens `RULES_PREFIX` survived the first table on paper — the original A1 check only asserted the rules file was present, not that the script was absent; pinned before the sweep ran.
- The single-repo fixture could not express "local `main` ≠ `origin/main`" — the exact state the recorder misbehaved in. `git update-ref refs/remotes/origin/main <sha>` models a remote-tracking ref without a remote; the fixture now forks the lane from an origin/main that is AHEAD of local main.
- A fenced decoy stamp placed BEFORE the real stamps proves nothing under latest-governs; walkthroughs paste fenced evidence AFTER the verdict, and that is where the fixture puts it now.

## Your Actions

Everything above landed on the branch. Nothing is owed to you by this lane except the merge word — no
tickets, no follow-ons, no residue (operator ruling this session).

- The first real event will be **this lane's own close-out** (Step 2.5, `"<worktree>/.agents/scripts/flight_recorder.py" record --task SCC-38 …`) — the ledger is born empty on purpose. It will carry `rule-edited:` for nothing (no rule changed), `gate-red:` for nothing (all receipts pass), and whichever real-file mentions this walkthrough's Pitfalls name.
- Dismissed by judgment, recorded so the reasoning is findable: a `dismiss` sub-command for proposals (not asked; the ledger has zero events; add it in the lane where a ruled-on proposal actually nags) · a mechanical guard refusing a merge when Step 2.5 was skipped (new law needing your quoted words; the numbered step + the Evidence row are today's net).

## Code Review (2026-08-15)

Verdict: PASS @ abbf875d3690cd255d33422262f81c393996bb57
Suite evidence measured @ `abbf875` (the last code-touching commit; `28/28 files passed`, exit 0, receipt `gates/suite.json` committed `7fd697c`).

**Scope:** `main...HEAD` — 27 files at review start (`c99ba0b`), 30 after the fixes: 1 new script, 1 new suite file + 1 pinned suite, 1 hook (+ mirror), 5 command bodies (+ opencode/workflow mirrors), 2 docs, the SOP, the master plan Delta, a proposal pointer, this folder.
**Method:** `/smh-code-review` → `code-review-engine` (5 lenses in parallel clean contexts, `lens_budget: standard`, `review_mode: full` with the lane plan as spec) → verify wave (Evidence Verifier + Compound Synthesis, one wave, dossier built by both) → triage under SCC-160's relevance gate **and the operator's ruling this session: fix the relevant findings in the lane, ticket nothing** → fixes applied → re-sweep → one re-stamp.

**Engine summary (as returned):**
```
lenses_run:      5/5  (blind ok · edge ok · literal ok · acceptance ok · test-adequacy ok)
lenses_na:       none
findings:        38 raw -> 28 grouped claims + 5 compound (33 triaged):
                 0 decision · 27 patch (ALL applied in-lane) · 0 defer   (2 noise-dismissed · 4 relevance kills)
severity_floor:  none  (every important was FIXED in f6cd430/6a0541d/abbf875, none carried; no lens or role dead)
notes:           verify wave ran (28/28 verified TRUE; verifier re-graded G3/G9/G11/G17 down); dossier built by
                 both roles (extractor exit 0); literal lens received 11/27 files by design (generated mirrors +
                 _artifacts withheld, all named), no top-up used; Blind Hunter starved (diff file only, outside
                 the repo); review-context prompt files deleted after the run (not evidence). No FINDINGS_SINK /
                 DEFERRED_WORK writes: nothing deferred.
```

**Step 0.7 — re-derivation against current `main`:** nothing this diff references moved — 0 files landed on
`main` since the fork (`main` = `origin/main` = merge-base `0b46c62`); overlap ∅, `merge-tree` clean; no
sibling lanes live. Absorb was a no-op.

### Findings table (authoritative)

| # | Where | Sev (verified) | Failure scenario | Disposition |
|---|---|---|---|---|
| G1 | `flight_recorder.py:58` `_MENTION_RE` (blind · edge · literal · acceptance · test-adequacy — all five) | important | lookbehind restarted after a hyphen: `.agents/rules/git-policy.md` → `mention:policy.md`; `.agents/scripts/gate_receipt.py` → nothing; a LIVE pitfall bullet → `task-merge-tree.md`; the ladder splits/undercounts the recurrences it exists to find | **applied** — whole path token consumed → basename; must resolve to a real file (`f6cd430`); pinned N7/N8 |
| G2/C1 | `:305` `--base` default = local `main` (blind · edge; compound: second machine needs no absorb) | important | preflight measures vs `origin/main` and only fast-forwards local `main` AFTER the merge; a lagging machine attributes every sibling rules edit to this lane → false action-required | **applied** — `resolve_base`: `origin/main` if present, else `main`; fixture models it (`f6cd430`); N4/N5 |
| G4/C2 | `build_event` verdict read (test-adequacy; compound proven on landed SCC-83: FAIL→PASS→PASS records FAIL) | important | first-match on raw text; fenced decoy wins; recorded verdict contradicts the reader the merge trusts | **applied** — `task_preflight.strip_fenced` + `VERDICT_RE`, latest stamp (`f6cd430`); N2/N3 |
| C4 | `verdict:` fingerprint family (compound; measured: CONCERNS in 10/47 lanes, FAIL unreachable) | suggestion | first proposal the operator sees would be "review verdict CONCERNS in 3 lanes" — unactionable | **applied** — family removed; verdict stays in `outcome` |
| G3 | `:125` gate-red for `!= pass` (edge · literal · test-adequacy) | suggestion (verifier: no `warn` receipts exist today) | `warn` (advisory, adopted by review) and `unrunnable` read as "went red" | **applied** — `== "fail"` only; fixture adds a `warn` receipt; N6 |
| G7 | `_MENTION_RE` accepts any bare `*.md` (blind · edge) | suggestion | `walkthrough.md`/`MEMORY.md` climb to a nonsense rung | **applied** — resolved with G1 (existence filter) |
| G6 | `/smh-merge-multiple-workingtrees` has no record step (blind) | suggestion | lanes landed by the set door leave no event | **applied** — 4b½ added |
| G9/G10 | door Step 2.5 block: cwd-relative script path; unconditional add/commit/push (blind · edge · acceptance) | nitpick / suggestion | first event never writes from a lobby cwd; replay commit exits 1 | **applied** — `<worktree>`-anchored path; commit only when something staged |
| G13 | `ladder` shas outnumber tasks (acceptance) | nitpick | evidence pairs unreadable on the surface line | **applied** — one sha per distinct task |
| G17/G18/G23 | `resolve_repo` traceback on a non-dir; `surface` leaks `[ERR]` to stdout (literal · test-adequacy) | nitpick | boot context pollution in a non-git ROOT (near-nil reach) | **applied** — `try_repo`; pinned N13 |
| G12/G19/C5 | hook: unconditional blank line; `$HERE/../scripts` dead in the `.claude/hooks` mirror (acceptance · literal · compound) | nitpick | empty line every boot; a settings change to the mirror would silently drop `surface` | **applied** — resolve from `$ROOT` first, capture output; hook-empty pinned |
| G20/G21/G22/G24/G25/G26 | test pins (test-adequacy) | suggestion | idempotency-by-dir mutant survived; refusals/absorb/order/mention-e2e/month-dir unpinned | **applied** — all pinned (`f6cd430`, `6a0541d`); door order in `test_door_preflight_order.py`; N10/N17 |
| G8 | `cicd-update-sprint-memory.md:224` two predicates (blind) | nitpick | agent reads the parenthetical, asks wrongly | **applied** — one predicate |
| G14/G16 | §6a splitting the runner diagram; plan A4 row said "Step 4" (acceptance) | nitpick | reading-order / spec-vs-built mismatch | **applied** |
| clean-code §2A | `read_receipts` silent `except Exception` | nitpick | a malformed receipt vanishes with no reason | **applied** (`abbf875`) |
| G5 | no `dismiss` path for proposals (blind) | suggestion | a ruled-on proposal reprints at every boot | **dismissed** — relevance leg 3 fails (not asked) and leg 1 (ledger has zero events; nothing can nag yet); recompute-on-read means it stops when the evidence changes; add it in the lane where a real proposal nags |
| C3 | ledger is fail-open with no completeness reader (compound of G6/G9/G10/G17) | important (compound, unverified) | a skipped Step 2.5 is indistinguishable from "nothing recurred" | **dismissed** — deliberate, audit-approved design (recorder never blocks a merge); a completeness gate on the merge is NEW LAW needing the operator's quoted words; the four contributing defects were each fixed above, which is what shrinks the miss surface |
| G11 | A3 can't tell `--repo "$ROOT"` from cwd; PC arm unexercised (acceptance · test-adequacy) | nitpick | none — the hook `cd`s to ROOT first, so the guard is redundant; the `python` arm is machine-bound | **dismissed** — no realistic path; the hook-empty case now runs from a foreign cwd anyway |
| G15 | 6a's "returns as an opt-in flag" sentence under "dropped, not deferred" (acceptance) | nitpick | tone only | **dismissed** — accurate: stating a revival condition is not deferring |
| G27 | prose edits unpinned (test-adequacy, informational) | nitpick | — | noise (correct per SCC-125) |
| G28 | "no visible mutation table" (test-adequacy) | nitpick | — | noise (the auditor could not read the walkthrough; the table exists) |

Changes applied: **all `applied` rows above** — `f6cd430` (fixes + pins), `6a0541d` (fixture), `abbf875` (clean-code 2A);
doors regenerated via `sync-agents`; SOP updated to three families + both doors. Nothing deferred, nothing proposed,
nothing minted.

### Gates (Step 3) — actual output

| Gate | Result |
|---|---|
| Enforcement suite (receipt writer, clean tree) | `28/28 files passed` · exit 0 · 87.9 s @ `abbf875` → `gates/suite.json` |
| Toolkit lint | `-- 0 error(s), 0 warning(s), 8 info --` @ `7fd697c` → `gates/lint.json` |
| check_maps `--depth3-only --strict` | exit 0 @ `27736c3` → `gates/maps.json` |
| Assertion evidence | `test_flight_recorder.py` (`--case A1/A2/A3`) `44/44` · `test_door_preflight_order.py` `13/13` · `test_command_surfaces.py` `57/57` |
| SOP currency | armed commit-msg gate accepted every usage-surface commit with the SOP staged (`93dacb2`, `f6cd430`); `[sop-ok]` on the four commits that changed nothing an operator types (receipts, a test fixture, an except-clause reason); `sop_currency.py --paths <all usage paths> … workflows_testing_SOP.md` exit 0 |
| Link + anchor | 20 md files in the diff, 36 relative links, **0 unresolved** |
| Door parity | no command added/renamed/deleted; mirrors regenerated; `test_command_surfaces` `57/57` |

### Acceptance matrix (Step 2 — items → proving assertion; the engine's Acceptance Auditor found A1/A3–A5/B1/C1 SATISFIED, A2 PARTIAL on G1, now fixed)

| Item | Where | Assertion |
|---|---|---|
| A1 record | `flight_recorder.py cmd_record/build_event` | A1 block: one file, latest-verdict-sha keyed, three-dot from origin/main, idempotent + second file on a new sha, four refusals |
| A2 candidates | `ladder/proposal/cmd_candidates` | A2 block: 3→action-required, 2→candidate (distinct), 1→evidence, `[]`→no rung, `--json`, mention e2e |
| A3 surface + hook | `cmd_surface`, `session-start-context.sh` | A3 block: silent-empty, non-git silent, malformed skipped, one proposal line, real hook run (seeded + empty, foreign cwd) |
| A4 door | `smh-close-task-merge-tree.md` Step 2.5 (+ 4b½ in the set door), boot Step 3, INDEX, SOP | lint 0/0; `test_door_preflight_order` pins record→gate-ref order; parity 57/57 |
| A5 conditional question | two command bodies | inspection: `CONDITIONALLY … only when Step 3 routed ZERO learnings` / `once, and only if …` |
| B1 §6a | `autopilot_bmad_dev_loop.md` (now below the runner diagram) | `grep -c Done-means-green` = 1; `test_sops_prds_folder` 61/61; links clean |
| C1 folded | master plan Delta; proposal pointer 12 lines | grep 1; wc 12; both links resolve |

Beyond-the-list drift: none — every hunk traces to an item or to a review fix recorded above.

### Clean-Code Gate — PASS

Nested run: imported Step 3's receipts + pasted runs (suite, lint, SOP, link/anchor); ran only what Step 3 did not.

| Check | Result |
|---|---|
| `py_compile` (3 changed .py) | ok |
| `bash -n` / `sh -n` hook | ok / ok |
| ruff / pyrefly / eslint / tsc | not applicable to this repo (no venv, no node) — `py_compile` + the suite carry the objective half |
| Scan: secrets · debug prints · commented-out code · bare except · abs paths · bare `python` | none — the two `print(` hits are the `say()` channel; `except Exception` ×3 all log a reason to stderr (the third was the one fix, `abbf875`); every operator-typed `python3` carries the `# PC: python` note; hook uses `command -v python3 \|\| command -v python` |
| §2A comment contract | every non-obvious block carries `SCC-133`/review provenance + why; no `AIDEV-NOTE` invalidated (0 touched); no unowned TODO |
| §2B drift bans | imported from Step 1 (`review`): no single-caller abstraction (the two scrape helpers are imported, not cloned; `task_preflight` reader reused, not re-implemented); no scope creep beyond the recorded review fixes |
| §2C conventions | naming law ✓ (no new command) · prefix-is-permission ✓ · one door per platform ✓ (regenerated) · generated files not hand-edited ✓ · rule pointers restated ✓ · both machines ✓ · gates armed n/a (no gate added; `surface` is a boot surface, not a gate — its positive control lives in the test) · every gate has an exit n/a · a gate must be able to fail ✓ (44/44 with negatives) · artifacts in the tree ✓ · board narrative n/a · no personal name ✓ (the edited sentence now says "the operator") · prose standard ✓ |
