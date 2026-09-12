# Walkthrough — SCC-447: a review finding arrives with a command that reproduces it, or it does not arrive

**Ticket:** SCC-447 (Task)
**Branch:** `chore/SCC-447-review-disposition` — cut from `main` at `03778605`; `origin/main` absorbed at `8bf95733` (SCC-186's records only, conflict-free)
**Worktree:** `.claude/worktrees/scc-447-review-disposition`
**Commits:** `05a7e5ba..c34edf5f` — three plan commits, six parts in six commits (`9b127e09` + `3964e196` doctrine · `27aa4248` scope · `3233f2e8` gates · `72f2735c` doors · `ccef6674` lanes · `455a2124` records), one absorb, one tip fix (`c34edf5f`)
**Plan:** [implementation_plan.md](implementation_plan.md) — v3, ruled 2026-09-11 (no `escalate` bucket, no `defer` bucket)
**Status:** built, **reviewed under the finished doors — two `--range` reviews, both `PASS` @ `63399ba3`** (24 reproduced findings fixed with pins, 0 dropped, 0 held), certified (`gates/suite.json` — 90/90 @ `63399ba3`), pushed. **Not landed** — the close-out door opens the PR. This lane is D10's stated exception: the doors that would review each part were its subject, so it was reviewed at the tip as Parts 1–3 (`114deb3a..3233f2e8`) and Parts 4–6 (`3233f2e8..3f482b30`).
**Date:** 2026-09-11 (reviewed 2026-09-12)

review-runtime: fan-out

---

## Task Checklist

- [x] **Part 1 — doctrine** (rows A, B): `code-standards` §6.5 Gate 0 + §7's two grounds and the byte twin; `artifacts-always-first` §6 vocabulary; `jira.md`'s review-findings paragraph; the engine's four steps — three lenses, the hunter contract (`reproduce:` + `expected_wrong_output:`, run in the lens's own copy first), step-02 a pass-through, the presence gate, two buckets, a PROVISIONAL floor; the negative-control fixture re-attributed.
  - Landed at `9b127e09` under v2's policy (`escalate` and `defer` beside `fix`). The operator struck both the same day: *nothing reproduced is handed to him to read, nothing is deferred anywhere.* Corrected at `3964e196` — 20 rewritten content checks and 4 identifier bans, RED first.
  - `test_review_engine.py` (about 130 of 264 rows) and four sibling tests pinned the engine being retired; retired in the same commit, sized honestly under RED.
- [x] **Part 2 — scope** (row D): `review_scope.py` — one part, masters only, no byte cap; withholds mirrors, generated launchers and records and PRINTS every path it withheld; groups commits by rider key; refuses a two-key range naming both; `--audit` keeps every mirror and still strips records.
- [x] **Part 3 — gates** (rows D, E): `repro_receipt.py` (no `--result` flag; three results with their own exit codes; `--cwd` required); `walkthrough_roster.py` reads the findings table for lanes dated 2026-09-12+ and refuses a stamp the rows do not support; `task_preflight.py`'s FAIL message; `workflow_lint.py`'s fourth alternation; the 19-mutant sweep.
  - The plan's `NA4` label already existed → the mode-skip case is `NA7` with `NA8` as its control. The §6.5 command line lacked the `--cwd` the script requires — corrected, twin byte-copied.
- [x] **Part 4 — doors** (row C): nine `twin-law:` fences byte-identical across `/smh-code-review` and `/cicd-code-review`; Step 1 cuts the diff through `review_scope.py`; a new Step 1.4 reproduces on the real tree; the floor resolves at the stamp on the rows still open; Step 6 ends the turn with one screen and the two words.
  - **The lane's own enforcement floor was RED and had been since Part 1**: `test_suite_runner.py`'s ORPHAN walker rejected `test_review_disposition.py`'s module-level `run_checks` helper. Fixed here (`check_rows()` returns rows; every block checks under its own guard).
  - `test_review_engine.py` was protecting the Blind Hunter's drop clause — the enforcement suite holding retired doctrine in place. Same class again in Part 5 (`test_command_surfaces` AP1 pinned `second non-PASS`) and Part 6 (the pictures).
- [x] **Part 5 — lanes** (rows E, F, H): the autopilot stops at a non-PASS verdict (a story run is four children, a quick fix two); `work-consolidation` Rule 2 reviews one part at a time with the suite as the cross-part check; both planners warn at 40 master files; both self-audits resolve POST-DEV through `review_scope.py --audit`, and Lens 2 states the asymmetry in the same words.
  - The plan declared two autopilot rows; the real surface was seven (both seat tables, the manual's §4/§5 tables + diagrams + headings, its §6 charter, the SOP's §15 line, the §18 atlas chain). A charter saying "escalate" beside a table saying "one fix cycle" is a lane that reads whichever half the agent reaches first.
  - Three line-wrap mismatches in Part 4's checks → `one_line()`: words are the law, where the line ends is not.
- [x] **Part 6 — records** (row G): the quickref's three review diagrams and their hand-drawn SOP twins redrawn from ONE data table; block I holds every node to its appendix row, label for label (green on the old tables before any edit — proof the twins were exact folds — and on the new); the atlas node says three lenses; the autopilot's picture stops at a non-PASS verdict (in the declared file, not in the plan's list); the SOP's gates-table engine row no longer drops a Blind Hunter under inline; changelog row six.
  - **The first full suite at the tip was 88/90**, and both reds were this lane's: `$L` used unbound in the two fences Part 4 added to the story door (`test_boot_epic_branch_read` A6 — a fence is its own shell, SCC-441's exact shape), and two subprocess seams in `review_scope.py` decoding with the machine locale (`test_jira_feed` SCC-335 E1). Neither is visible to any per-part targeted run — D10's claim, made on the lane that wrote it. Fixed at `c34edf5f`, mirrored, sweep re-run, suite re-stamped 90/90.
- [x] **The two `--range` reviews of D10** — run under the doors this lane changed, on the operator's word ("yes lets close this out"). Six lenses in six isolated worktrees, 24 `important` findings reproduced on this tree through `repro_receipt.py`, every one fixed with a pin seen red, both verdicts PASS. The record is the two `## Code Review` sections below.
  - **The doors caught their own author.** The scope cut found `review_scope.py` withholding ITSELF (`s1`, fixed before any lens ran); the lenses then found the auditor rubric naming a green suite as a reproduction — exit 0, which the writer reads as not reproduced, so no auditor finding could ever have survived (`x1`); the receipt writer certifying a typo'd `--case` label (`e2`) and splitting a piped command (`x3`); the roster gate refusing the second part's first review as a re-review (`x6`); the story close-out reading the FIRST stamp while the doors say the LAST governs (`e3`); three CONCERNS grounds §7 does not have, in the doors themselves (`b1`, `b2`); and eleven law sentences that could be inverted with every pin green.
- [ ] **Land via PR** — `/smh-close-task-merge-tree` opens it; the merge is the operator's click.

---

## Evidence

### Acceptance → evidence (the plan's rows, in its order)

| Row | Statement (short) | Proved by |
|---|---|---|
| **A** | §6.5 Gate 0 · action policy (reproduced → fixed; `held` / `out-of-lane` the caller's only other dispositions) · §7's two CONCERNS grounds · "CONCERNS ships on the operator's word" · one review per lane · the floor on what is still OPEN · twin byte-equal · `artifacts-always-first` + `jira.md` say the same words | `test_review_disposition` block A — every content check with a counter-example applied in memory and rejected; 261/322 → 322/322 at `3964e196`; **703/703 whole file at the tip** |
| **B** | three lens rows, no levels · hunter contract requires `reproduce:` + `expected_wrong_output:` and the lens's own run · step-02 pass-through · presence gate (the engine cannot execute) · `fix` / `drop` · floor provisional, two evidence-backed ways down · `.claude/skills/` cache byte-identical · fixture re-attributed | block B; `test_review_engine` 414/423 → 423/423 (Part 1), 413/423 → 417/417 (Part 4); `test_finding_record` 8/10 → 10/10; `test_lens_roster_contract` 39/39; `test_review_fixture` 69/69; `test_doc_examples_parse` 22/22 |
| **C** | both doors: `review_scope.py` in Step 1 with its output as `DIFF` · Step 1.4 through `repro_receipt.py` on the real tree · D2 in the fix paragraph · machine floor only in the nested 3.5 · floor at the stamp · D4 re-stamp · D5 screen · no `lens_budget` · no `re-run the review` sentence · `.opencode/` mirrors byte-equal | block C 28/209 → 209/209; `test_twin_parity` 68 → 76/76 (nine fences); `test_command_surfaces` 343/345 → 345/345 |
| **D** | `review_scope.py` and `repro_receipt.py`, each seen red first | `test_review_scope` 43/43 on a temp git repo (RED first, 8 behaviours incl. `--audit` proved by the same fixture); `test_repro_receipt` 2/19 → 19/19; **mutation sweep 19/19 killed by their declared case**, at `8bf95733` and again at `c34edf5f` after the seam pin |
| **E** | the roster gate's refusals (fixed row without pin / receipt; held row without patch; fixed nitpick; PASS over an open row; `important` neither fixed nor held = no verdict; second roster needs the operator's quoted word); `NA7` mode-skip exempt; `task_preflight` FAIL sends to the pins and the suite; the autopilot's row | `test_walkthrough_roster_dispositions` 14/48 → 48/48; `test_walkthrough_roster` NA block 7/8 → 85/85; `test_task_preflight` 0/2 → 141/141; `test_command_surfaces` CS-12 28/29; block E (autopilot) 15/54 → 54/54 |
| **F** | Rule 2: reviewed on its own commits, `--range` for parts without rider keys, the suite is the integration check; both planners warn at 40 masters | block F 4/25 → 25/25 |
| **G** | SOP (§③, §`/smh-code-review`, §10, §11, §15, the atlas rows), the quickref diagrams and the changelog moved in the same commits as the surfaces; lint 0 errors; `run_all.py` N/N through the receipt writer on a clean tree | block I 27/69 → 69/69 (the parity check green on the old tables and the new; all four diagrams valid under the Mermaid validator); six SCC-447 changelog rows; `workflow_lint --toolkit-only` 0 errors; **`gates/suite.json`: `pass`, 90/90 files, 30.8s, `dirty_tree: false` @ `c34edf5f`** |
| **H** | both self-audits resolve POST-DEV through `review_scope.py … --range <first>..<HEAD> --audit`; Lens 2 carries the asymmetry sentence, identical in both twins | block H 4/24 → 24/24 (with an explicit twin-equality check on the sentence, which sits outside every `twin-law` fence) |

### The certifying run — pasted (the review's re-stamp, after the last code change at `bcd1ba09`)

```
python3 .agents/scripts/gate_receipt.py run --task SCC-447 --gate suite --root _artifacts/_main/2026-09-11_scc-447-review-disposition --cwd . -- python3 .agents/scripts/tests/run_all.py
[PASS] suite exit=0 30.0s @ 63399ba3
        receipt: gates/suite.json
90/90 files passed
```

`git rev-parse HEAD` → `63399ba3fa4dd8bcd432500cb5524b73944d499d`

Earlier certifying runs, superseded: 90/90 @ `c34edf5f` (before the reviews); 88/90 @ `8bf95733` (the two tip defects).

Static checks at the tip: `workflow_lint.py --toolkit-only` 0 errors, 0 warnings, 8 info · `check_links.py --base origin/main` clean · `check_maps.py --depth3-only --strict` clean · `sop_currency.py` satisfied on every commit (the SOP staged with every usage surface; `[sop-ok]` on the tip fix only, which changes no usage).

### The run before it — pasted, because a red receipt is the mechanism working

```
[FAIL] suite exit=1 29.6s @ 8bf95733
88/90 files passed  FAILED: test_boot_epic_branch_read.py, test_jira_feed.py
```

`test_boot_epic_branch_read` A6: `cicd-code-review.md: no fence uses $L before binding it — line 247, line 333` · `test_jira_feed` SCC-335 E1: `unpinned seams: ['review_scope.py:65', 'review_scope.py:73']`. Fixed in `c34edf5f`: 50/51 → 51/51 and 20/21 → 21/21, then the re-stamp above.

---

## Suite Ledger

| Scope | Command | Duration | Result | Why this run |
|---|---|---|---|---|
| Part 1 targeted | `test_review_disposition --case "A ·"/"B ·"`, `test_review_engine`, `test_lens_roster_contract`, `test_finding_record`, `test_review_fixture`, `test_doc_examples_parse` | — | RED then GREEN (totals in the plan's Part 1 as-built) | the part's own pins, on the operator's approval of the plan |
| Part 2 targeted | `test_review_scope` | — | RED then 43/43 | the script's behaviours on a temp repo |
| Part 3 targeted | `test_repro_receipt`, `test_walkthrough_roster_dispositions`, `test_walkthrough_roster`, `test_task_preflight`, `test_command_surfaces`, `test_workflow_lint` | — | RED then GREEN | the gates' refusals |
| Part 4 targeted | `test_review_disposition --case "C ·"`, `test_review_engine`, `test_command_surfaces`, `test_twin_parity`, `test_suite_runner`, `workflow_lint --toolkit-only`, `check_links` | — | RED then GREEN | the doors; the ORPHAN floor found and fixed |
| Part 5 targeted | `test_review_disposition --case "E ·"/"F ·"/"H ·"`, `test_command_surfaces`, `test_check_maps`, 15 sibling files | — | RED then GREEN | the lanes; AP1's retired needle |
| Part 6 targeted | `test_review_disposition --case "I ·"` then whole file, `test_sops_prds_folder`, `test_command_surfaces`, `workflow_lint --toolkit-only`, `check_links`, `check_maps --depth3-only --strict`, `sop_currency` | — | 27/69 → 69/69 · 703/703 · 61/61 · 345/345 · 0 errors · clean · clean · satisfied | the records |
| mutation sweep | `mutation_sweep.py --table sweep.json --repo .` | ~2 min | 19/19 killed, restore verified, closing files green | Part 3's table, run at `8bf95733` |
| **full suite #1** | `gate_receipt.py run --task SCC-447 --gate suite … -- run_all.py` | 29.6s | **FAIL 88/90** @ `8bf95733` | the first full run at the tip; both reds this lane's |
| tip-fix targeted | `test_boot_epic_branch_read`, `test_jira_feed --case SCC-335`, `test_review_scope`, `test_review_disposition --case "C ·"`, `test_twin_parity`, `test_command_surfaces` | — | 51/51 · 21/21 · 43/43 · 209/209 · 76/76 · 345/345 | the two fixes, seen red first by the suite |
| mutation sweep | `mutation_sweep.py --table sweep.json --repo .` | ~2 min | 19/19 killed | `review_scope.py` changed, so the sweep over it re-ran, at `c34edf5f` |
| full suite #2 | `gate_receipt.py run --task SCC-447 --gate suite … -- run_all.py` | 30.8s | **PASS 90/90** @ `c34edf5f`, clean tree | certified the tip before the reviews (superseded) |
| review, scope cut | `review_scope.py --range 114deb3a..3233f2e8` / `--range 3233f2e8..3f482b30` | — | 33 files / 509 KB · 23 files / 157 KB (re-cut after `s1`) | the two parts D10 owes; the first cut found `s1` |
| review, pins RED | `test_review_scope`, `test_repro_receipt`, `test_walkthrough_roster_dispositions`, `test_closeout_preflight --case "RS ·"`, `test_review_disposition` | — | 5, 4, 2, 3 and 65 rows red on the unfixed tree | every new pin seen red before its fix |
| review, GREEN | the same five, plus `test_walkthrough_roster`, `test_task_preflight`, `test_twin_parity`, `test_command_surfaces`, `test_boot_epic_branch_read`, `test_sops_prds_folder`, `workflow_lint --toolkit-only` | — | 58/58 · 28/28 · 139/139 · 139/139 · 793/793 · 85/85 · 141/141 · 76/76 · 345/345 · 52/52 · 61/61 · 0 errors | the fixes |
| mutation sweep | `mutation_sweep.py --table sweep.json --repo .` | ~6 min | **34/34 killed** by their declared case (M20–M34 new) | the review's fixes, each with a mutant |
| **full suite #3 — certification** | `gate_receipt.py run --task SCC-447 --gate suite … -- run_all.py` | 30.0s | **PASS 90/90** @ `63399ba3`, clean tree | the certifying run after the review's last code change; `gates/suite.json` |

---

## Code Review (2026-09-12, Parts 1–3: 114deb3a..3233f2e8)

Verdict: PASS @ 63399ba3
suite evidence: run_all 90/90 @ 63399ba3 (gates/suite.json) — this review's own re-stamp after the fixes below; the last code-touching commit is `bcd1ba09`.

lenses_run:
- edge-case-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  3/3
lenses_na:       none
lens_isolation:  worktree
dispositions:    per-lens: edge=7/0/5 · acceptance=1/0/2 · test-adequacy=3/0/3
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — reconciled at Step 2 after the plan's declared block was corrected (five generated or mirrored outputs and one test declared, one overreach row struck; a record edit)

scope: the doctrine (`code-standards` §6.5/§7 + twin, `artifacts-always-first` §6, `jira.md`), the engine skill's four steps, the negative-control fixture, `review_scope.py`, `repro_receipt.py`, `walkthrough_roster.py`'s findings gate, `task_preflight.py`, `workflow_lint.py`, the retired `evidence_extract.py`, and their tests — 33 masters, 509 KB, cut by `review_scope.py --range 114deb3a..3233f2e8` after `s1`.
method: three lenses fanned out in isolated worktrees (`isolation: "worktree"`, cut from `3f482b30`), each bound to the hunter contract or the auditor rubric plus the shared rubric, each running its own reproduction; every `critical`/`important` re-run on this tree through `repro_receipt.py` (receipts in `gates/repro/`); reproduced → fixed here with a pin seen red; the floor resolved at this stamp on the rows still open.

| # | file:line | sev | lens | failure scenario | repro | disposition |
|---|---|---|---|---|---|---|
| 0 | .agents/scripts/review_scope.py:139 | important | door (Step 1 scope cut, before any lens) | the bare marker substring classified the script ITSELF, its test, `test_command_surfaces.py`, the scripts INDEX and two command masters as "generated" and withheld them from every review | s1 | fixed @3f482b30 · pin test_review_scope.py:"1 ·" · repro s1 |
| 1 | .agents/scripts/review_scope.py:223 | important | test-adequacy | the all-withheld guard removed: an empty kept list gives `git diff` an empty pathspec, the patch carries the record and the mirror just withheld, and the suite stays green | t1 | fixed @bcd1ba09 · pin test_review_scope.py:"9 ·" · repro t1 |
| 2 | .agents/scripts/repro_receipt.py:72 | important | test-adequacy | the id validation removed: `--id ../../escape` writes the receipt outside `gates/repro/` and prints REPRODUCED; the suite stays green | t2 | fixed @bcd1ba09 · pin test_repro_receipt.py:"7 ·" · repro t2 |
| 3 | .agents/scripts/repro_receipt.py:76 | important | test-adequacy | the non-git `--cwd` refusal removed: the receipt is written with `sha: null` and the run dies exit 1, which a door reads as NOT reproduced while a `reproduced` receipt sits on disk | t3 | fixed @bcd1ba09 · pin test_repro_receipt.py:"6 ·" · repro t3 |
| 4 | .agents/scripts/review_scope.py:84 | important | acceptance+edge | a keyless tree (detached HEAD, an agent worktree): `lane_key()` is `""`, every commit files under the first key in its subject, a two-part range reads as ONE part and the exit-2 refusal never fires — D6's "never a guess" | a1 | fixed @bcd1ba09 · pin test_review_scope.py:"10 ·" · repro a1 |
| 5 | .agents/skills/code-review-engine/steps/step-01-review.md:199 | important | edge | the auditor rubric names "a suite that comes back green over the gap" as a reproduction; exit 0 is what the receipt writer reads as NOT reproduced, so no auditor `critical`/`important` written to its own rubric could survive to a fix | x1 | fixed @bcd1ba09 · pin test_review_disposition.py:"B ·" · repro x1 |
| 6 | .agents/scripts/repro_receipt.py:59 | important | edge | a house test whose `--case` label matches no block exits 3 and prints `NO CASES RAN`; none of the unrunnable signatures match, so a command that ran zero checks is certified `reproduced` | e2 | fixed @bcd1ba09 · pin test_repro_receipt.py:"3 ·" · repro e2 |
| 7 | .agents/scripts/repro_receipt.py:87 | important | edge | `-- python3 -c "…" \| grep -q X`: the door's shell splits the line before the writer starts; only the left stage runs, the receipt records a command the lens never wrote | x3 | fixed @bcd1ba09 · pin test_repro_receipt.py:"8 ·" · repro x3 |
| 8 | .agents/scripts/review_scope.py:95 | important | edge | `KEY_RE` makes `UTF-8`, `H-1`, `CS-18` in real subjects into phantom parts: no selector dies naming a part that does not exist, `--key` silently drops that commit's files from the patch | x4 | fixed @bcd1ba09 · pin test_review_scope.py:"2 ·" · repro x4 |
| 9 | .agents/scripts/review_scope.py:156 | important | edge | a mirror by PREFIX: `.claude/settings.json` (the branch-delete guard hook, the deny rows) has no master and was withheld from every review that touched it | x5 | fixed @bcd1ba09 · pin test_review_scope.py:"1 ·" · repro x5 |
| 10 | .agents/scripts/walkthrough_roster.py:280 | important | edge | rosters counted per FILE: a consolidated lane's second PART review — the flow Rule 2 mandates — is refused as a re-review from 2026-09-12 unless a fabricated `re-review:` quote is added | x6 | fixed @bcd1ba09 · pin test_walkthrough_roster_dispositions.py:"R ·" · repro x6 |

dropped — no reproduction: 0
recorded: 10 — suggestions 9 (unreadable-receipt arm uncased; three selection refusals uncased; `--key` diffs `base..HEAD` on the part's files, so a shared file carries another part's hunk; the gate is blind to a walkthrough with `dispositions:` counts and no table; `_PIN_TOKEN_RE` accepts `pin —`; `ruled` closes a held critical with no quoted word; a decorated severity cell exempts a row; `--out` resolves against the shell's cwd) · nitpicks 1 (the SCC-441 measurement is 84 files / 647 KB at HEAD, not 82 / 618).
calibration: the keyless tree was graded `important` by the Acceptance lens and `suggestion` by the Edge lens for the same defect (row 4, merged); the assessor read `ruled`-without-a-quote and the decorated severity cell as gate bypasses graded below their failure — recorded at the lens's label, named here as the signal.

gates: enforcement suite — `gates/suite.json` pass 90/90 @ 63399ba3 (30.0s, clean tree) · toolkit lint — 0 errors, 0 warnings, 8 info · assertion evidence — the pins named above, each seen red on the unfixed tree (5 · 4 · 2 · 3 · 65 red rows) then green · SOP currency — satisfied on every commit, the SOP staged · link + anchor — `check_links --base origin/main` clean · door parity — no command added, renamed or deleted.

### Acceptance (Parts 1–3)

| Row | Result | Proving assertion |
|---|---|---|
| A | MET | `test_review_disposition --case "A ·"` (relationship regexes with in-memory counter-examples); `cmp` twin identical |
| B | MET | `--case "B ·"` incl. the two new auditor-rubric pins; `test_review_engine` 417/417; `test_lens_roster_contract` 39/39; `test_finding_record` 10/10; `test_review_fixture` 69/69; cache `cmp` identical ×5 |
| C | not in this part (Parts 4–6) — the `workflow_lint.py` fifth arm filed under C is here: CS-12 19/19 |
| D | MET, with rows 0–10 fixed — `test_review_scope` 58/58; `test_repro_receipt` 28/28; `test_walkthrough_roster_dispositions` 139/139; `test_walkthrough_roster` 85/85; `test_task_preflight --case SCC-447` 2/2; sweep 34/34 |
| E | not in this part |
| F | not in this part |
| G | not in this part (records withheld) |
| H | the Part 2 half MET — `test_review_scope` block 8 (`--audit` keeps mirrors, strips records) |

### Clean-Code Gate — PASS

Machine floor only (nested): enforcement suite inherited from Step 3's receipt (pass 90/90 @ 63399ba3) · `workflow_lint --toolkit-only` 0 errors · `sop_currency` satisfied at each commit · `py_compile` on all 20 changed `.py` files clean · `check_links --base origin/main` clean · door parity n/a. Changed-line scan: no secret, no debug print, no commented-out code, no bare `except`, no hardcoded path, no gate that cannot fail. Judgment pass: not run nested (§7). Imported drift findings from Step 1: none.

### Step 0.7 — re-derivation

1. What moved on `main` under this diff: nothing this diff references — `main` gained SCC-186's records twice (PRs #211 and #212: two artifact folders, the `_main` INDEX row, `docs/.maps-state.json`, `docs/migrations/*`); both absorbed (`8bf95733`, `497ea77a`) before the verdict.
2. The true overlap and `merge-tree`: zero overlapping paths both times; `git merge-tree --write-tree` clean both times.
3. Sibling lanes: none live (`git worktree list`: `main` and this lane); no landing-order dependency.

Changes applied: rows 0–10 above (fixes committed at `3f482b30` and `bcd1ba09`, sweep table at `63399ba3`).

## Code Review (2026-09-12, Parts 4–6: 3233f2e8..3f482b30)

Verdict: PASS @ 63399ba3
suite evidence: run_all 90/90 @ 63399ba3 (gates/suite.json) — the same re-stamp; the last code-touching commit is `bcd1ba09`.

lenses_run:
- edge-case-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  3/3
lenses_na:       none
lens_isolation:  worktree
dispositions:    per-lens: edge=6/0/4 · acceptance=4/0/2 · test-adequacy=8/0/10
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — the same lane-wide reconciliation as Parts 1–3

scope: both review doors, the nested paragraph in both clean-code audits, the close-task door's triage sentence, the autopilot command and `autopilot_run.py`, both self-audits, both planners, `work-consolidation` Rule 2, `test_review_disposition.py` blocks C–I, `test_review_engine.py`, `test_command_surfaces.py`, and the tip fixes — 23 masters, 157 KB, cut by `review_scope.py --range 3233f2e8..3f482b30` (the range also carries `docs/migrations/*` and `docs/.maps-state.json` from the two absorbs; skipped as main's).
method: as above — three lenses, isolated worktrees, own reproductions, the door's re-run through `repro_receipt.py`, fixed with pins, floor at the stamp.

| # | file:line | sev | lens | failure scenario | repro | disposition |
|---|---|---|---|---|---|---|
| 1 | .agents/commands/cicd-code-review.md:435 | important | acceptance+test-adequacy | both doors mint a CONCERNS from "no acceptance list" / "no evidence" — the story door in the retired words (`cap the verdict at **CONCERNS**`, `CONCERNS floor`), the task door relabelling it the "coverage ground" — a third ground §7 does not have, ten lines from a fence that says "exactly two" | b1 | fixed @bcd1ba09 · pin test_review_disposition.py:"C ·" · repro b1 |
| 2 | .agents/commands/smh-code-review.md:395 | important | acceptance | a lint warning, a soft CI step and missing automate evidence each mint a CONCERNS in the doors' gate tables and the audit legend — none with a receipt or a patch behind it | b2 | fixed @bcd1ba09 · pin test_review_disposition.py:"C ·" · repro b2 |
| 3 | .agents/commands/smh-code-review.md:175 | important | acceptance | "blind lens first on the diff alone" — a live ordering instruction for a retired lens, ten lines below the sentence saying the blind lens is gone; the seventh site the six-site fix missed | b3 | fixed @bcd1ba09 · pin test_review_disposition.py:"C ·" · repro b3 |
| 4 | .agents/commands/cicd-self-audit.md:221 | important | acceptance+test-adequacy+edge | the POST-DEV fence `cd`s into the project, runs a project-relative `.agents/scripts/` path (no thin project has one) and points `--repo` at the shared checkout — against its own footnote two lines down | b4 | fixed @bcd1ba09 · pin test_review_disposition.py:"H ·" · repro b4 |
| 5 | .agents/commands/cicd-autopilot-claude.md:157 | important | test-adequacy | a fifth stage re-grown under the story seat table passes every pin — the table is what the lead executes, one child per row | b5 | fixed @bcd1ba09 · pin test_review_disposition.py:"E ·" · repro b5 |
| 6 | .agents/commands/smh-code-review.md:242 | important | test-adequacy | "you fix nothing yet" inverted to "fix in thread — act on what it hands back, here, now" in both doors and their mirrors with 703/703 green | b6 | fixed @bcd1ba09 · pin test_review_disposition.py:"C ·" · repro b6 |
| 7 | .agents/scripts/review_scope.py:65 | important | test-adequacy | the UTF-8 pin reverted with the suite green; on a real byte outside UTF-8 the whole scope cut aborts with a traceback, no patch, nothing withheld printed | b7 | fixed @bcd1ba09 · pin test_review_scope.py:"1 ·" · repro b7 |
| 8 | .agents/scripts/tests/test_review_disposition.py:1181 | important | test-adequacy | block I's "the parity check can fail" row asserted an always-true predicate; the label-for-label comparison could be replaced with `missing = []` and all six rows stayed green | b8 | fixed @bcd1ba09 · pin test_review_disposition.py:"I ·" · repro b8 |
| 9 | .agents/commands/smh-code-review.md:588 | important | test-adequacy | "CONCERNS is shippable" inverted to "CONCERNS never ships by itself — a fix batch and a second pass are owed" in both doors with no pin firing | b9 | fixed @bcd1ba09 · pin test_review_disposition.py:"C ·" · repro b9 |
| 10 | .agents/commands/cicd-code-review.md:650 | important | test-adequacy | "report it and name the fix, never stamp over it" can revert to "caps the verdict at CONCERNS" unseen — a third ground re-admitted in the door | b10 | fixed @bcd1ba09 · pin test_review_disposition.py:"C ·" · repro b10 |
| 11 | .agents/commands/cicd-code-review.md:333 | important | edge | the Step 1 and Step 1.4 fences use `$WORKTREE` and `$ARTIFACT_DIR` that no fence binds; as their own shells, `--cwd ""` runs the lens's command in the lobby and `--root ""` lands the receipt where the roster gate never looks | e1 | fixed @bcd1ba09 · pin test_review_disposition.py:"C ·" · repro e1 |
| 12 | .agents/scripts/repro_receipt.py:59 | important | edge | the `NO CASES RAN` certification — found independently from this range; the file is Parts 1–3's (row 6 there) | e2 | fixed @bcd1ba09 · pin test_repro_receipt.py:"3 ·" · repro e2 |
| 13 | .agents/scripts/closeout_preflight.py:375 | important | edge | the story close-out reads the FIRST `Verdict:` while the doors say the LAST governs and `task_preflight` reads `found[-1]`; a story lane re-stamped FAIL→PASS after `apply <ids>` could never close without rewriting the first stamp, which the door forbids | e3 | fixed @bcd1ba09 · pin test_closeout_preflight.py:"RS ·" · repro e3 |
| 14 | .agents/commands/cicd-self-audit.md:221 | important | edge | `--range <first>..<HEAD>` in both self-audits and Rule 2: git's `A..B` excludes A, so the part's first commit never enters the selection and — only withheld paths print — nothing says so | e4 | fixed @bcd1ba09 · pin test_review_disposition.py:"H ·" · repro e4 |

dropped — no reproduction: 0
recorded: 16 — suggestions 9 (five block-C pins bind the line wrap `one_line()` exists to end; the whole `review-scope` fence deletable with pins green; `held is never a question` and the exit-code table and the nested-3.5 bullet and `lenses_na` sentence unpinned; `--out` relative to the shell's cwd; `--key` diffs `base..HEAD` on the part's files; the audit table's `applied/deferred` vocabulary is parsed by the roster gate) · nitpicks 7 (`autopilot_SOP.md:275` "six children"; `test_twin_parity.py:189` names the retired fence; `work-consolidation.md:181` unpinned; `is_generated()`'s `lstrip()` untested; the parity row printed its failure text on PASS — fixed incidentally with row 8; `test_autopilot_run.py:216` "six children"; `wf.die` refusals share exit 2 with `unrunnable`).
calibration: row 8 was graded `important` by the lens with a note the assessor might read it as `critical` (a gate that cannot fail); kept at the lens's label. Row 4 was reached by all three lenses independently.

gates: as Parts 1–3 — one certifying run covers both sections (`gates/suite.json` pass 90/90 @ 63399ba3).

### Acceptance (Parts 4–6)

| Row | Result | Proving assertion |
|---|---|---|
| A | not in this part |
| B | the `test_review_engine.py` slice MET — 417/417 |
| C | MET, with rows 1–3, 6, 9–11 fixed — `--case "C ·"` (now with the CLAIM, CONCERNS-shippable, no-spec, FAIL-reason, operator, range and fence pins); `test_twin_parity` 76/76; `test_command_surfaces` 345/345; `.opencode/` mirrors byte-identical |
| D | the tip slice MET — `test_review_scope` 58/58 (`is_generated`, the UTF-8 fixture, the rider key, the byte-copy mirror rule, the keyless refusal) |
| E | MET, with row 5 fixed — `--case "E ·"` (charter row, retirement paragraph, the two seat tables counted 4 and 2) |
| F | MET, with row 14 fixed — `--case "F ·"` (Rule 2's three sentences with the corrected range wording; the 40-master paragraph identical in both planners) |
| G | MET — `--case "I ·"` (the parity check now through `drifted()`; the TEA node reads `else FAIL`); `workflow_lint --toolkit-only` 0 errors; `run_all` 90/90 @ 63399ba3 |
| H | MET, with rows 4 and 14 fixed — `--case "H ·"` (the story twin's fence binds the lobby and runs the LOBBY's script; `<first>^..<HEAD>` in both twins with the reason) |

### Clean-Code Gate — PASS

As Parts 1–3: the machine floor inherited from Step 3, `py_compile` clean on every changed `.py`, links clean, parity n/a, changed-line scan clean, judgment pass not run nested.

### Step 0.7 — re-derivation

1. What moved on `main` under this diff: nothing this diff references; SCC-186's records absorbed at `8bf95733` and `497ea77a`.
2. The true overlap and `merge-tree`: zero; clean.
3. Sibling lanes: none live; no landing-order dependency.

Changes applied: rows 1–14 above (committed at `bcd1ba09`; sweep table at `63399ba3`).

## Your Actions

Landed: `chore/SCC-447-review-disposition` is pushed to origin; the review's fixes are at `bcd1ba09`, the sweep table at `63399ba3`, both verdicts PASS at that sha. Nothing has reached `main`; `/smh-close-task-merge-tree` opens the PR.

- [ ] **The merge itself** — lands via this branch's PR
