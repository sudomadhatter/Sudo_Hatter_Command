---
IsArtifact: true
ArtifactMetadata:
  title: SCC-214 — template-clone fixtures for the two git-repo-per-scenario suites
  type: walkthrough
  date: 2026-08-21
---

review-runtime: fan-out

# SCC-214 — Rebuild the two git-repo-per-scenario test files from a template clone

**Lane:** `chore/SCC-214-template-clone-tests` · **Ticket:** SCC-214 (Task, standalone)
**Plan:** [implementation_plan.md](implementation_plan.md) (with its Self-Audit, `Audit verdict: GO`)
**Ran in parallel with** SCC-213, which landed on `main` mid-lane and was absorbed at `ff35df9`.

---

## What this changed, and what the measurement changed about it

The ticket's premise was that the two slowest test files are slow because each scenario builds a real git repo from scratch, and that rebuilding them from a template clone gets the suite to ~50 s. **Measuring first moved the target.** Repo construction is **19 %** of `test_task_preflight.py` and **14 %** of `test_git_hooks.py`. The larger cost is that macOS **assesses every newly created executable on its first launch** — 0.19–0.28 s idle, **1.6–2.8 s under this suite's own parallel load**, because the assessor serialises — and the assessment is keyed by **inode**: a hard link to an assessed file costs 0.006 s, while a byte copy, an APFS clone and a byte-identical new file each pay in full. Between them the two files create 88 fresh `acli` stubs and 72 fresh hook sets: **~58 s of their 191 s.**

So the change does both. `_repo_template.py` builds each fixture repo once per shape and hands every scenario its own copy, and executables are **hard-linked to a read-only template inode** so the assessment is paid once per shape instead of once per scenario.

**Part A left the target missed at 94.8 s and said so; the operator then ruled the fix into this ticket rather than a new one, and Part B closed it.** The suite is now **135.6 s → 62.0 s** — a 54 % cut — because `test_task_preflight.py` was split at a measured seam. See **§ Part B**.

## Task Checklist

- [x] Measure BEFORE properly — discard the first attempt (the system clock stepped backwards mid-run, making every wall number from it fiction) and re-measure on a monotonic clock
- [x] Write the plan, run `/smh-self-audit` (LEDGER+BLAST, 3 lenses) → `Audit verdict: GO`, one anchored finding baked in
- [x] RED first — `test_repo_template.py` against today's builders: 3 rows red for the right reasons, 9 characterization rows green
- [x] GREEN — `_repo_template.py`, then both builder sets converted; **no block in either target file touched**
- [x] Mutation sweep, declared before mutating
  - the 11-mutant table came back clean; the **22-mutant** table did not, and found six of my own checks wrong
- [x] `/smh-code-review` — 5 lenses, fan-out
  - two `critical` findings were checks **that could not fail**, both mine, both reproduced by the lens
- [x] Absorb `main` (SCC-213 landed mid-lane) and resolve the ledger conflict
- [x] Suite receipt PASS at the shipping sha

## Evidence

Machine: this Mac, `cpu_count` 10, monotonic clock, same command both sides (`python3 .agents/scripts/tests/run_all.py`, default parallel width). Scripts and both reports ride the branch in [`measure/`](measure/).

| # | Acceptance (ticket, verbatim) | The assertion that proves it | Result |
|---|---|---|---|
| 1 | Full `run_all.py` wall clock posted BEFORE and AFTER, same machine, same run mode. Target ~50 s | `measure/before/report.txt` vs the receipt at the shipping sha | **135.6 s → 62.0 s** (Part A 94.8 s, Part B 62.0 s). Within ~12 s of the target, and the remaining gap is the packing limit, not a slow file — see § Part B |
| 2 | Every scenario in both files starts from a fresh clone — proven by a test that FAILS if state leaks, not by inspection | `test_repo_template.py` T1–T5, 46 cases; mutant **M1** (clone from the previous scenario) seen killing it | **PASS** |
| 3 | Case count unchanged in both files | `test_git_hooks.py` **151/151**; `test_task_preflight.py`'s 186 became **106 + 80 = 186** across its two halves after the Part B split — same cases, redistributed | **PASS** |
| 4 | Full enforcement suite green | `gates/suite.json` — `pass`, exit 0, **62.0 s @ `0a4d4a27`**, 43/43 files, clean tree | **PASS** |

**RED → GREEN, the assertions that changed state.** RED, against the pre-change builders:

```
[FAIL] the module imports: ModuleNotFoundError("No module named '_repo_template'")
[FAIL] one launcher per process: 3 distinct acli launchers for 3 board() calls
[FAIL] a hook shares the template inode: the hook was copied, not linked — the assessment is paid twice
-- 9/12 passed --
```

GREEN, at `8a5bf3b4` (`python3 .agents/scripts/tests/test_repo_template.py`): `-- 46/46 passed --`.

The nine rows green in the RED run are **characterization** checks — the isolation properties that had to survive the change — and they are labelled as such rather than presented as reds. Independently confirmed by the Test-Adequacy lens, which ran the new file against the `f25d7cb` fixtures and measured exactly `9/12`.

**Per-file wall clock.** Part A's column was profiled solo at load ~4–13 (the SCC-213 lane was running its own suite), so it is conservative; Part B's is the contended in-pool figure from `measure/floor.py`, which is the number that actually sets the suite.

| File | Before | After Part A | After Part B |
|---|---|---|---|
| `test_task_preflight.py` | 113.8 s | 79.8 s | **49.5 s** (+ 46.1 s in its new contract half) |
| `test_git_hooks.py` | 77.8 s | 44.9 s | 44.1 s |
| `test_task_preflight_receipts.py` | 49.0 s | 39.7 s | 41.1 s |
| **`run_all.py` (whole suite)** | **135.6 s** | 94.8 s | **62.0 s** |

**Gates, run bare. Part A at `8a5bf3b4`, all re-run after the Part B split at `0a4d4a27`:**

| Gate | Result |
|---|---|
| Enforcement suite | `43/43 files passed`, exit 0 — receipt `pass`, **62.0 s @ `0a4d4a27`**, clean tree (42/42 at 94.8 s before the split) |
| `workflow_lint.py --toolkit-only` | exit 0, **0 errors** |
| `sop_currency.py --paths <changed>` | exit 0 — `.agents/scripts/tests/` is exempt; `INDEX.md` is not a usage surface, so no `[sop-ok]` is needed |
| `check_maps.py --depth3-only --strict` | exit 0 (it caught a real miss first: this artifact folder had no `_artifacts/_main/INDEX.md` row) |
| Declared-set drift | `undeclared=0 · unimplemented=0 · incomplete=0` |
| `py_compile` (4 changed `.py`) | exit 0 |
| Mutation sweep | **22/22 killed by their declared case**, restore verified byte-identical, closing unfiltered run green — re-run at `0a4d4a27` after the split, which is what proves the split touched no swept decision |

## Mutant table (declared BEFORE mutating; every mutant drawn from a decision in the code)

M1 destination-cached clone · M2 no freeze · M3 link every file · M4 copy instead of link · M5 stale origin URL · M6 launcher memo gone · M7 cache before build · M8 no occupied refusal · M9 key ignores `ci` *(narrowing)* · M10 key ignores `arm` *(narrowing)* · M11 FETCH_HEAD kept · M12 chmod escape unwatched · M13 `.git/config` unscrubbed · M14 launcher writable · M15 occupied scan first-entry-only *(narrowing)* · M16 `os.link` fallback raises · M17 symlink branch neutered · M18 `shared_root` memo gone · M19 failed build left on disk · M20 unknown-keyword raise gone · M21 `_key()` first-path-only *(narrowing)* · M22 `leaks()` follows symlinks.

⭐ **The 22-mutant sweep did not come back clean, and that is the record worth keeping.** Six were not killed:

- **Three CRASHED the file** (M2, M6, M16). A file that dies prints no `FAILED:` line, and `mutation_sweep.judge()` refuses to score that shape — so a crash was being recorded as indistinguishable from a survivor. That was the Test-Adequacy lens's exception-safety finding, which I had not yet fixed. `main()` now converts an escape into a named, attributable row.
- **Three genuinely SURVIVED**, each passing for the wrong reason. The sharpest: **M5 survived because my own review fix weakened its case** — once `_seal` neutralised the template's URL, dropping `set-url` left `origin` merely *broken*, so "the predecessor's commit is invisible" passed for free. It now asserts the positive: origin points at this scenario's own bare.

## Code Review (2026-08-21)

Verdict: PASS @ 0a4d4a27
Suite evidence measured on: 0a4d4a27 (the receipt's sha). The lens fan-out ran on the Part A diff at 8a5bf3b4; Part B is a file SPLIT that changed no assertion and no decision in any reviewed file, re-gated and re-swept at 0a4d4a27 — recorded in § Part B rather than re-running five lenses over a redistribution.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=3/2/0 · edge-case-hunter=2/0/0 · literal-correctness-hunter=1/2/0 · acceptance-auditor=4/3/0 · test-adequacy-auditor=9/4/0 (a multi-lens finding counts once per contributing lens)
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — the declared set matched the shipping diff exactly, re-run after the absorb

**Scope:** the committed `origin/main...HEAD` diff, code only (5 files, 691 lines) — `review-code.diff` in this folder is the exact text the lenses were handed.
**Method:** `review_level: standard` (derived at Step 0.7: >3 source files, and the radius includes the fixtures that guard the merge gate), `lens_budget: standard`, `review_runtime: fan-out`. Five lenses in parallel, each in its own clean context.

**The tail, in one line (per the disposition ruling):** 30 findings came back across five lenses; **19 were assessed real and fixed**, and 11 were dismissed — pre-existing debt, hazards with no reachable trigger, or observations without a concrete failure. Two findings disagreed with their label in a direction worth recording: the Blind Hunter's `ACLI_BIN` lifetime finding was rated `important` and is **dismissed** (reproduced: `preflight()` is the only door in all three consumer files — 97 + 34 + 0 calls — and its file-existence guard re-boards, a guard that exists because this exact failure already happened once); and the Literal-Correctness lens's `_REPO_DEFAULTS` finding was rated `nitpick` but was **fixed**, because my comment named a silent failure the code cannot produce, which misleads the next maintainer.

### Findings

| file:line | severity | failure scenario | disposition |
|---|---|---|---|
| `test_repo_template.py` (T3 merge row) | **critical** | The row asserted only `rc == 0 and moved` — exactly what a repo running **no hook at all** produces. Reproduced: delete `core.hooksPath` from the fixture and it still passed, 24/24. This is the row that speaks for the ticket's non-negotiable ("`test_git_hooks.py` guards the merge gate") | applied @ 71e99a2 — both halves; `chore -> chore` must still be REFUSED through the hard link |
| `test_repo_template.py` (T3 inode row) | **critical** | The row read `HARD_LINKS` from the module under test, so the module could switch its own check off. Reproduced: disable hard-linking entirely — the whole ~58 s mechanism — and the suite stays 24/24 green with the row printing "SKIPPED" | applied @ 71e99a2 — the expectation is probed independently and the module must agree with it |
| `_repo_template.py` `_seal`/`_copy_entry` | important | `0o555` stops a write, but a scenario that `chmod`s first writes **through** the shared inode. Reproduced: clone A `chmod(0o755)` then `write_text` changes clone B's mode *and* bytes | applied @ 71e99a2 — `_verify_sealed` re-checks every cached template on every reuse and raises `TemplateCorrupted` |
| `test_repo_template.py` `leaks()` | important | The leak needle is self-referential with no positive control. Reproduced: rename the two `mkdtemp` prefixes and `leaks()` returns `[]` with a real `FETCH_HEAD` leak sitting in the clone, 24/24 green | applied @ 71e99a2 — a planted real `shared_root()` path must be seen |
| `_repo_template.py` `_seal` | important | `_seal` scrubbed `FETCH_HEAD` while its comment claimed that was "the one file" — `git remote add origin <abs>` also writes the template path into `.git/config`, closed only by caller discipline | applied @ 71e99a2 — scrubbed at source to an unresolvable placeholder, so a caller that forgets gets a loud error, not quiet shared state |
| `test_repo_template.py:44-52` **x4** | important | The guarded import was defeated two lines below itself: both consumer modules import `_repo_template` at module scope, so the guarded failure re-raised unguarded. Found independently by Blind, Acceptance, Edge and Literal-Correctness | applied @ 71e99a2 — one guard covering all three imports |
| `_pf_fixtures.py` `_launcher()` | important | The most-shared object the change adds — one file, fixed path, `ACLI_BIN` for ~88 blocks, outliving every `TempDir` — was left at `0o754`, owner-writable, while the module's own stated rule is that shared executables are frozen | applied @ 71e99a2 — launcher and stub frozen `0o555` |
| `test_repo_template.py` (whole file) | important | A defect escaping a block killed the file with no `FAILED:` line, which `mutation_sweep.judge()` refuses to score — so a crash read as a survivor. Reproduced four ways by the lens, then again by my own sweep (M2, M6, M16) | applied @ aaca3f6 + 7610d34 — `main()` reports the escape as a named row, under a block so `--case` governs it |
| `test_repo_template.py` (M5/M15/M20 cases) | important | Three new checks passed for the wrong reason — found by the sweep, not by a lens | applied @ aaca3f6 |
| `test_git_hooks.py` `_key()` | suggestion | Keyed on basenames, discarding half the identity its own docstring demands; `return ()` survived the whole suite | applied @ 71e99a2 — keys on full paths, plus a case that varies `scripts=` |
| `_repo_template.py` (6 decisions) | suggestion | `os.link` fallback, both symlink branches, the `shared_root` memo and the failed-build cleanup each survived being neutered — no mutant aimed at any of them | applied @ 71e99a2 — block T5, and mutants M16–M19 |
| `_pf_fixtures.py:73` | nitpick→fixed | The comment warned of a **silent** wrong-template bug the code cannot produce (the `unknown` check raises) — misleading the next maintainer | applied @ 71e99a2 |
| `test_repo_template.py` `leaks()` | nitpick | Evaluated twice per assertion, on the passing path too, in the one file whose subject is wall-clock | applied @ 71e99a2 — bound once |
| `_pf_fixtures.py` `board()` / `ACLI_BIN` | important (lens) | Claimed a stray caller would now hit a live stub with a deleted state file | **dismissed** — reproduced the opposite: `preflight()` is the only door and re-boards on a missing state file |
| `_repo_template.py` `_force` | suggestion (lens) | Never fires on POSIX | **dismissed** — it is the Windows path, and correct there |

### Step 0.7 — re-derivation

1. **Did anything this diff references move on `main`?** No. At review time `origin/main` was `f25d7cb`, identical to this lane's merge base, so the landed-diff set was empty. SCC-213 landed **during** the review (`1220847`) and was absorbed at `ff35df9`; its set is `_artifacts/_memory/**` plus its own artifact folder, and this diff references none of it. Every path and anchor this diff names re-resolved after the absorb — `check_maps --depth3-only --strict` exit 0.
2. **True overlap and `merge-tree`.** The landed-diff intersection was empty, but the *live sibling* comparison found the real one: **`_artifacts/_main/INDEX.md`**, where both lanes add a row at the top of the same table. It conflicted on the absorb exactly as predicted. It is a **ledger** conflict — both rows are additions and both belong — resolved by keeping both, SCC-213 above SCC-214. No other file overlapped; `merge-tree` was otherwise clean.
3. **Sibling landing order.** SCC-213 was the only live sibling and it landed first, which is why the conflict was mine to resolve rather than the operator's. Nothing else is live. Had the order reversed, the same one-line ledger merge would have fallen to SCC-213.

### Clean-Code Gate — PASS

Nested under Step 3.5, so the machine floor is **imported** from Step 3 (suite receipt, `workflow_lint` exit 0, `sop_currency` exit 0, link/anchor exit 0) and the §2B ban-hunt is imported from the lens findings above. Run here: `py_compile`, the comment contract (§2A), the convention table (§2C).

| Check | Result |
|---|---|
| `py_compile` (4 changed `.py`) | exit 0 |
| Committed secret / token | none |
| Debug output | 30 `print(` calls, **all** in `measure/*.py` — measurement scripts whose job is to print. **Zero** in shipped code |
| Commented-out code | none |
| Broad `except` | 3 sites, all deliberate: `_repo_template.py:167` re-raises after cleaning up a half-built template (a `KeyboardInterrupt` mid-build must still clean up, then propagate); two `except Exception: pass` sites in T4/T5 where the raise **is** the case. One lacked a stated reason → fixed @ 7610d34 |
| Hardcoded absolute / `C:/` paths | none |
| A gate that cannot fail | **This was the review's main finding, and it is closed** — every check added here has a mutant that kills it |
| Both machines | `HARD_LINKS` is False on `nt` by design (`_harness.TempDir`'s rmtree handler chmods read-only files, which through a link would unfreeze the template); no bare `python`, no `;` PATH join, no `robocopy` in shipped code |
| §2A provenance | `SCC-214` + the reason on every non-obvious block (3 refs in `_repo_template.py`, 8 in `test_repo_template.py`); no `AIDEV-NOTE` in the touched files to stale |
| §2C generated surfaces | none in the diff — no `.agents/workflows/`, `.opencode/`, or generated skill touched |
| §2C naming law / door parity | n/a — no command added, renamed or deleted |
| §2C no personal name in `.agents/` | 0 |
| §2C artifacts live in the tree | plan, walkthrough, manifest, sweep table, receipts and both measurement reports all ride this branch |

One row considered and dismissed: **"every gate has an exit."** `_verify_sealed` raises with no escape hatch. That row governs operator-facing gates (`[sop-ok]`); this is an internal fixture invariant, and an escape hatch would defeat the property it exists to hold.

---

## Part B — the split, and why the 45 seconds was worth taking

**How this got here.** Part A closed with one open decision: the suite was at 94.8 s against a ~50 s target, and the remaining lever was a third file split. The operator's ruling: *"We are not opening a new ticket it's add it to this one or we scrape it"*, then *"Nope fix that here, test it then we will close this ticket out"*, then **`Approved`**. So it is scope on SCC-214.

**The value, measured before committing to it.** `run_all.py` is concurrent, so the suite's wall IS its slowest file. One file at **81.8 s** was holding a **94.0 s** suite whose runner-up was 45.1 s — 41 files finishing and waiting on one.

**The seam was measured, not chosen by eye.** All 25 blocks timed in one process (73.9 s of block time, `measure/blocktime.py`); the balance point put **38.8 s / 35.1 s** either side, and it landed on a real boundary. `test_task_preflight.py` keeps the **refusals** (does the preflight stop deployable code, the wrong lane, a bad branch shape, an unpushed tree, open subtasks?). The new `test_task_preflight_contract.py` takes the **contract** (the manifest it reads, the secondary repos that manifest declares, the plan it prints, the receipts it leaves, the end-to-end pass).

**The risk I named before starting was real, and did not matter.** `_repo_template` caches per process and `run_all` gives each file its own, so splitting **duplicates** that file's template builds. It did: sum-of-files rose **370.3 → 390.3 s**. The wall fell anyway, because the wall was floor-bound.

| `measure/floor.py`, same instrument, minutes apart | Before split | After split |
|---|---|---|
| **suite wall** | 94.0 s | **61.7 s** |
| slowest file | `test_task_preflight.py` 81.8 s | `test_task_preflight.py` 49.5 s |
| runner-up | `test_jira_feed.py` 45.1 s | `test_task_preflight_contract.py` 46.1 s |
| sum of files | 370.3 s | 390.3 s |
| perfect-packing floor (work ÷ 10) | 37.0 s | 39.0 s |

**Gate receipt agrees within 0.5 %:** `run_all.py` through the receipt writer = **62.0 s**, exit 0, 43/43 files, clean tree @ `0a4d4a27`.

⛔ **And the honest stopping point: splitting again buys almost nothing.** Five files now sit between 41 s and 50 s against a 39.0 s packing limit — the suite is work-bound, not floor-bound. The next real lever is reducing total work, and the biggest single file left is `test_jira_feed.py` at 46.1 s, which SCC-214 never touched. That is a statement of where the next gain is, **not** a ticket and not a request.

**Part B evidence**

| # | Acceptance | Result |
|---|---|---|
| B1 | The wall drops materially, measured not projected | 94.0 → 61.7 s (`floor.py`), receipt 62.0 s @ `0a4d4a27` |
| B2 | **Case count unchanged — the split loses nothing** | **106 + 80 = 186**, exactly the single file's count |
| B3 | Every other `_pf_fixtures` consumer still green | receipts 39/39 · ship 102/102 · repo_template 46/46 · git_hooks 151/151 |
| — | Gates re-run after the split | `run_all` 43/43 exit 0 · `workflow_lint --toolkit-only` exit 0, 0 errors · `check_maps --depth3-only --strict` exit 0 · `sop_currency` exit 0 · `py_compile` exit 0 · drift `undeclared=0 · unimplemented=0 · incomplete=0` |
| — | Mutation sweep re-run at the shipping sha | **22/22 killed by their declared case**, restore verified — a split changes no decision in any swept file, and this is what proves it rather than asserting it |

**One process note worth keeping.** The split script asserted its seam offset against the file's real text and **failed twice** before cutting — once on the block line, once on the import block. Both were my off-by-ones, and both failed loudly instead of silently cutting in the wrong place. A split that guesses its offsets is how a file loses cases without anyone noticing; the 186 arithmetic is the second guard behind it.

---

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [x] Plan, walkthrough, manifest, mutant table, both measurement reports and the review diff are linked above and ride the branch
- [x] SCC-213's ledger-row conflict in `_artifacts/_main/INDEX.md` resolved by keeping both rows
- [x] The third conversion — **you ruled it into this ticket rather than a new one, and it is done.** 135.6 s → 62.0 s. Nothing is owed.
