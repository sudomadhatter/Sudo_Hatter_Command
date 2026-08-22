---
IsArtifact: true
ArtifactMetadata:
  title: SCC-240 — self-diagnosing readers (roster + declared-set)
  type: walkthrough
  date: 2026-08-20
---

review-runtime: fan-out

# SCC-240 — the machine-read blocks stop being taught in a form their own parser rejects

**Lane:** `chore/SCC-240-self-diagnosing-readers` · **Repo:** command centre · **Base:** `origin/main` @ `db253fc`
**Plan:** [`implementation_plan.md`](implementation_plan.md) — `Audit verdict: GO`, operator `approved` 2026-08-20; Part B amendment audited `GO`, operator *"yes fix it in this ticket then keep going."*

## What this fixes, in one line

A close-out is gated on markdown blocks written by hand; every place the `lenses_run:` roster was **taught** showed it inside a code fence, and `walkthrough_roster.strip_fenced` deletes fenced content before reading (SCC-154, deliberately) — so "paste VERBATIM" produced a roster the gate could not see, and the refusal said "no roster" while the roster sat visibly in the file. ~12 minutes per reviewed lane, measured on SCC-210.

## Task Checklist

- [x] **Give `walkthrough_roster.py` a CLI** — it was library-only; the only way to learn what it saw was to run a close-out and read the refusal.
  - Review: four independent lenses reached the same defect — the CLI the commands run at Step 4 judged the *full gate*, which is not answerable at Step 4 (no stamp, no record lines yet), so it exited **0 on a fenced roster** and refused on a missing `dispositions:` line while the doc said "it must be a fence". Fixed: bare = "can the roster be READ?"; `--gate` = the full judgement; `--verdict` supplies an unwritten stamp.
  - Review: stamps were read from RAW text while everything else reads fence-stripped — a fenced *quotation* of a verdict governed (the SCC-154 shape). Fixed.
  - Review: a directory was "no such walkthrough"; a latin-1 byte raised a traceback under exit 1 (= REFUSED). Fixed: exit 2 with the named cause for every unreadable path.
- [x] **Make the refusal diagnostic** — three causes, three answers, now ONE function (`roster_defect`) for `judge` and the CLI.
  - Review: the empty-header message closed with "no blank line between" for a state the flag also sets on contiguous-but-mistyped rows. Fixed: the imperative names both checks.
- [x] **Attach a reason to every `declared_change_set` `incomplete` row** — four rejection paths, declared precedence.
  - Review: a `*`/`+`/no-marker bullet was told to add an op it had already written — a *wrong* reason, not a bare one, surviving inside the fix for exactly that defect. Fixed: the list marker gets its own sentence (`R8`).
- [x] **Fix the teaching surfaces so the taught form parses** — commands unfenced, engine templates keep their fence and gain the instruction.
  - Review: the Step-4 line claimed "exit 1 names one of three things" (judge refuses on nine) and "a clean run here is the close-out's answer" (false pre-stamp, and false on a FAIL-then-PASS story lane — `closeout_preflight` reads the FIRST stamp). Both commands and the SOP rewritten to say what the bare run is, what `--gate` is, and when `--verdict` is required.
- [x] **Pin it with a test that cannot go stale** — `test_doc_examples_parse.py` extracts every taught example *from the documents* and runs it through the real parser.
  - Review: `D2` searched the whole file (one warning exempted every fence) — now a 25-line window with a control; block `C` had no template carve-out and a one-deletion-from-vacuous floor — both fixed; block `G` was blind to a comment-out and a claim reversal — `G5` control; the extractors had no tests of their own — block `X`.
- [x] **Resolve the engine's self-contradiction about the verify wave** — one grouping owner, named where the work happens, before the instruction it governs.
- [x] **Part B — the wrong-tree guard reaches single-file runs** (review-discovered; SCC-190 is the owning mechanism).
  - While fixing the review findings this lane ran `test_declared_change_set.py --case …` from a reset cwd and recorded **`47/47 passed` against `main`**. The SCC-190 guard lives in `run_all.py` only; every single-file run — the review loop, and the only way the mutation sweep runs a test — bypassed it. The body now lives once in `wf_common.tree_guard`; `_harness.Cases.__init__` asks it and refuses exit 2 with no `FAILED:` line; `--on-main` on the file or `WF_ON_MAIN` in the env allows it, and `run_all --on-main` exports the env var so its children do not refuse one by one.
  - I first added a *warn-tier* tree label on belief, without checking whether the repo already had a guard. It did. Reverted; the guard was extended instead of duplicated.
- [x] Suite receipt, mutation sweep (10/10), review gate, re-stamped at the shipping sha.

## Evidence

Every acceptance row → the assertion that proves it → RED before, GREEN after. All runs below were made from the worktree; since Part B every test file prints `-- tree: SCC-240-self-diagnosing-readers [chore/SCC-240-self-diagnosing-readers] - worktree --` as its second line.

### 1 · The roster reader is runnable

RED (`test_walkthrough_roster.py --case "F · the refusal"`, at `db253fc`):

    [FAIL] F1 · the module runs as a command at all: rc=0 out='' - a library-only reader can only be interrogated by writing a script against its internals
    [FAIL] F1b · on a good walkthrough it PRINTS what it parsed and exits 0: rc=0 stdout='' err=''
    [FAIL] F1c · on a REFUSED walkthrough it exits non-zero and prints the reason: rc=0 out=''
    [FAIL] F1d · a missing file is a loud exit 2, never a verdict about content: rc=0 out='' err=''

GREEN after the review round (the first GREEN proved a CLI that answered the wrong question; `F1c` was also vacuous — `"fence"` matched the JSON key `roster_header_fenced` in stdout — and is now asserted on stderr alone):

    [PASS] F1c · on a REFUSED walkthrough it exits 1 and stderr NAMES the cause
    [PASS] F1e · a DIRECTORY is exit 2, and the message does not claim it is missing
    [PASS] F1f · an undecodable file is exit 2 with a named cause, NOT a traceback
    [PASS] F1g · with NO stamp the bare run still reads the roster and says the stamp is normally absent here
    [PASS] F1h · `--gate` with no stamp REFUSES to guess - exit 2, not a verdict
    [PASS] F1i · `--verdict` supplies the missing stamp and IS the judged value
    [PASS] F1j · two stamps: `--gate` judges the LAST, and SAYS the story-lane gate reads the first
    [PASS] F1k · ...and `--verdict` overrides both stamps
    [PASS] F1l · the stamp reader is LENIENT - a blockquoted, bolded, WAIVED stamp still resolves

Reproduced before the fix, from the review: a fenced roster with no stamp → **exit 0**; a fenced `Verdict: FAIL` quotation after a real `CONCERNS` → judged `FAIL`. Both now refuse / read `CONCERNS`.

### 2 · A fenced roster is named as fenced · 3 · A non-contiguous roster is named as such

RED — both cases got the same sentence, describing the roster's *format* to an author whose roster was already in the file:

    [FAIL] F2 · a roster lost to a code FENCE is named as fenced: ["Verdict PASS with NO `lenses_run:` roster. ..."]
    [FAIL] F3 · a roster ended by a BLANK LINE after its header is named as non-contiguous: ["Verdict PASS with NO `lenses_run:` roster. ..."]

GREEN — and `F7`/`F7b` (added on review) pin the now-common document: a fenced *example* above a real empty header reports `empty` and sends the author to their own header, not to the example they copied.

### 4 · A genuinely absent roster reads as it does now

The control, green throughout: `F4` (message byte-identical to `db253fc`, verified by the Acceptance Auditor loading both modules side by side) and `F4b` (no fence/contiguity blame leaks into it).

### 5 · Every `incomplete` bullet carries a reason

RED: `R1 · 0/4 reasoned, 0 distinct`. GREEN — four rejected bullets, three distinct reasons, precedence held (`R5`), the row IS the bullet with the reason appended (`R6`, rewritten on review: its first form was satisfied by any path containing `/`), and the list marker is its own reason (`R8`, a code fix from the review):

    '* NEW `star.md` — a star marker → A'  ← the bullet must start with `- ` - a `*` or `+` marker, or a line with no list marker at all, is not read as a declaration (the op and the path here are fine; only the marker is wrong)

### 6 · No doc teaches an unparseable block

RED (`test_doc_examples_parse.py`): `D1 · 2 taught example(s) yield ZERO lenses when pasted verbatim: ['.agents/commands/cicd-code-review.md:380 [fenced]', '.agents/commands/smh-code-review.md:378 [fenced]']` and `D2 · 2 fenced template(s) with no such instruction`.

GREEN: `22/22` including the review additions — `D2` scoped to a 25-line window with `D2b` as its control, `C0` naming its source, `X1–X5` on the extractors, `T` pinning both twins' Step-4 self-check. The Acceptance Auditor re-fenced the taught example in a scratch copy: **`D1` went red, naming the file.**

### 7 · The verify wave's grouping owner is unambiguous

RED: `G1–G4`, `group@-1`. GREEN: `group@2670`, before `serialise`; `G5` (review) proves a comment-out or an owner reassignment goes red.

### B · A single test file refuses in the main checkout while a lane exists

RED (`test_suite_runner.py --case TREE`, before `tree_guard` existed):

    [FAIL] T-H1 · a single HARNESS-based file REFUSES in the main checkout while a lane exists - exit 2, REFUSING named, and NO `FAILED:` line: exit 0: == h ==

GREEN: `T-H1`–`T-H6` 12/12 — refuses exit 2; `--on-main` and `WF_ON_MAIN=1` both allow; the same file in the lane runs unflagged; `run_all --on-main` propagates to harness-based children (`2/2 files passed`); a bare dir with no git degrades to silence. Whole file `107/107`; `test_mutation_sweep.py` `22/22`.

⛔ **What this cannot prove pre-merge:** the exact command that fooled me invoked **main's** copy of the test file, and main's harness is unchanged until this lane lands. `T-H1` drives the shipping `_harness.py` inside a fixture main-checkout with a lane worktree, which is the same shape; the live proof arrives with the merge.

### The gates

| Gate | Result |
|---|---|
| `run_all.py` (via `gate_receipt.py`) | **PASS** exit 0, 137.3s @ `c1e2d41`, `dirty_tree: false` — `40/40 files passed` · receipt `gates/suite.json` |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, 8 info** (pre-existing BOM notices on `testarch-*`) |
| `check_maps.py --depth3-only --strict` | **exit 0** |
| `tests/test_sops_prds_folder.py` | **61/61** |
| `lane_qualify.py` on the real diff | `TASK` — correct for this lane; **no deployable path**, no eject |
| `declared_change_set.py diff` (declared vs working tree) | `undeclared=0 · unimplemented=0 · incomplete=0` after Amendment 2 |

⛔ Gates run **bare**. Two process lessons from this lane are recorded, not hidden: `${PIPESTATUS[0]}` is a bashism (blank in zsh); and a single-file test run from a reset cwd measured `main` — Part B is the fix.

### Mutation sweep — `sweep.json`, declared before mutating, drawn from the code

    -- sweep clean: 10/10 killed by their declared case --
    -- restore verified: bytes match, nothing was committed, and `git diff --quiet 2a859d90` is clean --

| # | Mutant | Killed by |
|---|---|---|
| M1 | the fenced-header flag forced `False` | `F2` |
| M2 | the two diagnostic branches swapped (re-aimed at the extracted `roster_defect`) | `F3` |
| M3 | the bare CLI returns 0 on a roster it could not read (re-aimed at the bare-run path) | `F1c` |
| M4 | the missing-arrow bullet told the left side failed instead | `R2` |
| M5 | the taught roster example put back inside a code fence | `D1` |
| M6 | the verify wave's grouping sentence removed | `G1` |
| M7 | `tree_guard` never refuses | `T-H1` |
| M8 | `run_all --on-main` stops exporting `WF_ON_MAIN` | `T-H5` |
| M9 | the harness refuses with exit 1 (a sweep would score it as a kill) | `T-H1` |
| M10 | the harness ignores the hand-typed `--on-main` | `T-H2` |

All four test files then re-run **full and unfiltered** — the run that catches a mutant riding in behind green scoped filters. The sweep's first run refused M2's anchor (it had moved with the extraction) rather than mutating a line I did not declare; that is the tool working.

**HEAD:** `c1e2d41` · branch pushed to `origin/chore/SCC-240-self-diagnosing-readers`.

## Step 0.7 — re-derivation (blast radius against current `main`)

1. **What moved:** nothing moved — `git log db253fc..origin/main` is empty after a fresh fetch; the lane's base is still `main`'s head.
2. **What that changes here:** nothing; no sibling landed, the declared set and the sibling-lane overlap (SCC-235: ∅) stand as measured at plan time.
3. **What was re-measured:** the declared-set diff against the working tree (`0/0/0`), the `TASK` qualification, and every plan anchor the Literal-Correctness lens checked (one drift found and corrected: `test_review_engine.py:1416` → `:1420`).

## Code Review (2026-08-20)

Verdict: PASS @ c1e2d41
Suite evidence measured at `c1e2d41` (receipt `gates/suite.json`, this lane's own run).

lenses_run:
- blind-hunter · ok
- edge-case-hunter · recovered-inline — fan-out stalled twice (machine sleep, watchdog), rerun inline via a reproduction script
- literal-correctness-hunter · ok — first launch stalled, retry succeeded
- acceptance-auditor · ok — first launch stalled, retry succeeded
- test-adequacy-auditor · ok — first launch stalled, retry succeeded
lenses_counted:  5/5
lenses_na:       none
findings:        31 fixed in thread · 0 patch · 0 defer   (5 dismissed · 2 relevance kills)
dispositions:    per-lens: blind-hunter=8/1/1 · edge-case-hunter=2/1/0 · literal-correctness-hunter=8/1/0 · acceptance-auditor=1/2/1 · test-adequacy-auditor=12/0/0 · compound-synthesis=1/0/0
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — reconciled at c1e2d41 after Amendment 2 declared Part B's four files inside the one block
severity_floor:  none
notes:           verify wave: Evidence Verifier rerun inline, COLD (no dossier) — every `important` finding and both vacuity claims reproduced by script before any fix (`verify_bh.py`, `verify_ta.py`, `edge_inline.py`); Compound Synthesis rerun inline, COLD — one compound finding below. Review ran against the pre-fix diff at `5d29e36`; the fixes were re-gated (suite, sweep, lint, maps, SOP test, qualify, drift) at `c1e2d41`. The first Step-4 instruction this lane shipped was itself the review's top finding — the tool built to remove SCC-210's round trip reproduced it — and that is recorded above rather than smoothed over.

### Compound finding (contributing: BH#3 `F1c`, BH#4 `R6`, BH#7/TA#14 `D2`)

Three new assertions in three files were each satisfied by a **sibling artifact the assertion did not mean to read**: a JSON key name in stdout, a `/` inside every fixture path, a sentence anywhere in a 2,000-line file. The systemic gap is "assert on a substring" without asking what *else* in the output always contains it. Fixed in all three; the house rule it sharpens is already `tests-must-gate-for-real.md`'s — name the negative control first.

### Findings — disposition per finding

| # | Lens | Finding | Severity | Disposition |
|---|---|---|---|---|
| 1 | BH · TA · AA · LC | Step-4 self-check exits 0 pre-stamp; `--verdict` untested and undocumented; `judge` refuses on nine conditions not three | important | **fixed** — bare = roster read; `--gate`/`--verdict`; F1g–F1l; both commands + SOP rewritten |
| 2 | BH | CLI reads stamps RAW while `judge` reads stripped — fenced quotation governs | suggestion | **fixed** — `strip_fenced` before the stamp read |
| 3 | BH · TA | `F1c` satisfied by the JSON key `roster_header_fenced` | suggestion / important | **fixed** — stderr-only, phrase-level |
| 4 | BH · LC | `R6`'s `or "/" in k` unconditional | suggestion | **fixed** — row reconstructed from its bullet |
| 5 | BH | `D1` green-lights a `lenses_na` template row the parser drops | suggestion | **relevance-killed** — the doc half is the ticket's DO NOT; acceptance row 6's own words are "≥1 lens", which is what `D1` asserts |
| 6 | BH | block `C` lacks the template carve-out `D` has | suggestion | **fixed** — `template` flag in `declared_examples`, `X5` |
| 7 | BH · TA · AA · LC | `D2` whole-file search | suggestion / nitpick | **fixed** — 25-line window + `D2b` control |
| 8 | BH · EC | empty-header refusal's imperative names only the blank line | suggestion / important | **fixed** — names the row grammar |
| 9 | BH | orphaned two-word line; `choices=[*(...)]` | nitpick | **dismissed** (the wrap is cosmetic; `G1` normalises whitespace) / the `choices` half **fixed** in the rewrite |
| 10 | BH | block `C` comment "is red today" goes stale on landing | nitpick | **fixed** |
| 11 | TA | `--verdict` / last-stamp / note / JSON keys — 4 mutants survived 65 cases | important | **fixed** — F1g–F1l |
| 12 | TA | `_CLI_VERDICT_RE` has no width certification | suggestion | **fixed** — `F1l` |
| 13 | TA | fenced-example + real empty header undocumented by any case | important | **fixed** — `F7`/`F7b` |
| 14 | TA | marker-shape bullets get the op-vocabulary reason | important | **fixed** — `_MARKER_WHY`, `R8`/`R8b` |
| 15 | TA | sweep case-derived in selection; zero mutants on `main()` | important | **fixed** — M7–M10, re-aimed M2/M3 |
| 16 | TA | no narrowing mutants | suggestion | **fixed** — `F1l`, `X1`/`X2` |
| 17 | TA | extractors untested; CommonMark/unclosed branches unreached | suggestion | **fixed** — block `X` |
| 18 | TA | block `C` one example, `bool(found)` floor | suggestion | **fixed** — `C0` by name |
| 19 | TA | block `G` blind to comment-out and claim reversal; no control | important | **fixed** — `G5` |
| 20 | TA | Step-4 self-check instruction pinned by nothing, outside twin-law | suggestion | **fixed** — block `T` |
| 21 | AA | Row 1 PARTIAL (same as #1) | important | **fixed** |
| 22 | AA | `TEACHING_GLOBS` excludes SOP/rules; no live hole | suggestion | **relevance-killed** — no copyable block exists there today; widening to 2,000-line prose would trade a real corpus for noise |
| 23 | AA | fourth verdict reader | nitpick | **dismissed** — declared decision; now reads stripped text and names its disagreement with `closeout_preflight` |
| 24 | AA | receipt sha ≠ HEAD (planning-dir commit after it) | nitpick | **dismissed** — correct as stated; re-stamped at `c1e2d41` regardless |
| 25 | LC | "exit 1 names one of three things" — judge refuses on nine; guaranteed `dispositions:` refusal at Step 4 | important | **fixed** |
| 26 | LC | "exits 0 if the close-out would accept it" false pre-stamp | important | **fixed** |
| 27 | LC | "same parser, same answer" false for FAIL-then-PASS story lanes (last vs first stamp) | important | **fixed** — commands + SOP say it; `--gate` prints it |
| 28 | LC | plan anchor `test_review_engine.py:1416` drifted to `:1420` | suggestion | **fixed** |
| 29 | LC | plan cites `R4` (ships `R5`); M4 row `R1` (ships `R2`); `head_stripped` (ships `head_kept`) | nitpick | **fixed** |
| 30 | LC | exit-2 message says "no such" for a directory that exists | nitpick | **fixed** |
| 31 | LC | `R6` name vs assertion (same as #4) | nitpick | **fixed** |
| 32 | LC | `D2` name asserts adjacency the assertion does not test (same as #7) | nitpick | **fixed** |
| 33 | LC | pre-existing `step-01-review.md:398` citation (context line, not in this diff) | nitpick | **dismissed** — outside the diff; noted, one token, for whichever lane next touches that comment |
| 34 | EC | undecodable file tracebacks under exit 1 | important | **fixed** — exit 2, named cause, `F1f` |
| 35 | EC | contiguous-but-mistyped rows sent to hunt a blank line (same as #8) | important | **fixed** |
| 36 | EC | "no `python` fallback" on three teaching sites | important | **dismissed — false positive of my own line-scoped probe**; the fallback sits on the wrapped next line in all three |
| 37 | CS | substring assertions satisfied by sibling artifacts (compound of #3, #4, #7) | suggestion | **fixed** via its parents |

## Your Actions

Nothing is owed. The lane is review-complete at `c1e2d41` and pushed; the close-out is yours to invoke when you want it.

- [x] Plan written, self-audited (`Audit verdict: GO`) and approved; Part B amendment audited and taken on your word.
- [x] Suite, lint, maps, SOP-folder and qualify gates green at the shipping sha, with a receipt.
- [x] Mutation sweep 10/10, restore verified.
- [x] Review: five lenses, every `important` finding reproduced before it was fixed, re-gated after.
- [x] The merge itself — lands via this branch's PR.
