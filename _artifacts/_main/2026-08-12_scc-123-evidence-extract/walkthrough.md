# Walkthrough — SCC-123 `evidence_extract.py` (2026-08-12)

**Ticket:** SCC-123 (Subtask of SCC-116, the house review engine) · **Branch:** `chore/SCC-123-evidence-extract`
**Plan:** [implementation_plan.md](implementation_plan.md) · **Lane HEAD at review close:** `3f5dc27`

## What shipped

`.agents/scripts/evidence_extract.py` — the review engine's fact-fetcher, ported from pr-af's
`evidence.py` @ `8593130` into a stdlib-only, two-machine-safe script. Zero LLM calls: `--pack`
primes a review lens with the changed files plus who imports them, `--findings` pulls ground truth
for an asserted finding (code at the line, call sites, diff hunk, cross-refs, blast radius). Search
is pure Python — a shelled-out `grep` is banned — and the guard proves that with process creation
blocked inside the interpreter, not with a source grep.

Shipped in four commits on this lane:

- `f338ff0` — the port itself + a 67-row guard (reviewed: FAIL, see below).
- `6d51047` — **all 19 review findings closed**; guard rebuilt to 98 rows and proven able to fail
  by a 12-mutant driver; suite counts re-measured.
- `3f5dc27` — two operator-authored docs rolled in at his direction (SCC-38 epic plan, GraphRAG
  proposal); not SCC-123 work, riding the push as asked.
- the round-2 closure (the commit carrying this walkthrough) — the clean-room re-verification's
  five residues closed, guard 103 rows, its surviving mutant killed, counts re-trued to 1091/21.

## Evidence

| Gate | Result | Where measured |
|---|---|---|
| `tests/test_evidence_extract.py` (bare) | **103/103, exit 0** | round-2 closure tree |
| `tests/run_all.py` (bare) | **21/21 files, 1091/1091 cases, exit 0, ~80 s** | round-2 closure tree |
| `workflow_lint.py --toolkit-only` (bare) | **0 errors, 0 warnings (8 pre-existing BOM infos), exit 0** | lane at `6d51047` |
| `py_compile` on the subject | **exit 0** | lane at `6d51047` |
| Mutation proof, both rounds | **15/15 caught, each by the row built for it** | 12 at `6d51047`'s tree, 3 at the round-2 tree |
| `sop_currency.py` (commit-msg hook) | **accepted every commit** (SOP staged with each usage change; operator-files commit exempt paths) | at commit time |

The mutation proof is the acceptance-item-10 evidence: round 1 killed the review's four hollow-row
mutants (always-last-hunk · line-fallback-41 · identifier-blind blast · cross-ref-everything) plus
a revert of every `6d51047` fix; round 2 killed the re-review's surviving mutant (the
`_under_skip_dir` pair clause) plus reverts of both round-2 behaviour fixes. Drivers: session
scratchpad `mutation_proof.py` / `mutation_proof_round2.py` (literal mutations, guard run per
mutant, source restored; deliberately not committed — they edit the subject in place and belong to
this review, not to the tree). The independent re-reviewer additionally ran its own 13-mutant
campaign from scratch and confirmed 12 kills plus the one survivor that round 2 closed.

## Task checklist

- [x] Port with the seven deviations D1–D7 (per-importer resolution, nested-tsconfig alias roots,
  direct-join-first normalization, caller-supplied diff, thread pool, degrade-not-die, GitNexus
  rationale in the docstring).
- [x] Guard, paired-fixture style, proven able to fail — **rebuilt under review**: the first proof
  (7 mutations) probed only known design decisions; the review's 4 perimeter mutants all survived
  it. The rebuilt 98-row guard kills all 12 of the combined set.
- [x] `INDEX.md` + SOP §10 rows; both suite counts corrected **twice** (988/18 at `f338ff0`,
  1086/21 at `6d51047` — SCC-118 landed 3 test files mid-review, then the rebuild grew the guard).
- [x] Review FAIL fixed and the gate re-run (this section + Code Review below).

## Code Review (2026-08-12)

Verdict: CONCERNS @ 3f5dc27
Suite evidence measured at the staged tree of `6d51047` (docs-only delta to `3f5dc27`); the
round-2 closure commit below re-measured at its own tree (21/21 files, 1091/1091 cases, exit 0).

**Scope:** the SCC-123 diff against `origin/main` @ `4274a96` — `evidence_extract.py` (905 lines),
its 910-line guard, INDEX/SOP/plan doc rows.
**Method:** clean-room adversarial subagent (no conversation context, findings confirmed by
execution in a sandbox), Step 2 acceptance audit, Step 3 centre gates bare, Step 3.5 clean-code
audit; then every finding fixed on the lane and a second clean-room pass run against the fixed sha.

**Round 1 — FAIL @ `f338ff0`.** Decisive finding: acceptance item 10 ("the guard can fail") was
false — four content checks could not fail, proven by four mutants that invert real behaviour and
still scored 67/67. The full 19-finding table with dispositions:

| # | Sev | Where (at `6d51047`) | Failure scenario | Disposition |
|---|---|---|---|---|
| H-1 | HIGH | [evidence_extract.py:763](../../../.agents/scripts/evidence_extract.py#L763), `_safe_extract` :796 | `line_start: 1e400` → `int(inf)` raises `OverflowError`, escapes `pool.map`, every finding's evidence destroyed | applied — caught + per-finding isolation; guard :746 |
| H-2 | HIGH | [evidence_extract.py:824](../../../.agents/scripts/evidence_extract.py#L824) | duplicate titles (expected for multi-lens fan-out) collapse onto one package with the wrong file's code | applied — output is a LIST in finding order; guard :538 |
| H-3 | HIGH | guard rows rebuilt at :474/:731/:480/:469 | four content checks pass inverted implementations (67/67 each) | applied — path:line + marker anchors, 3-hunk middle-target fixture, head-decoy blast fixture, never-named negative; 12/12 mutants killed |
| H-4 | HIGH | [evidence_extract.py:115](../../../.agents/scripts/evidence_extract.py#L115) | `.claude/worktrees/<lane>/` copies listed as importers/callers — another branch's code, unlabelled | applied — (parent,child) pair prune in walk + `_under_skip_dir`; guard :596 |
| H-5 | HIGH | [evidence_extract.py:855](../../../.agents/scripts/evidence_extract.py#L855) | `PYTHONIOENCODING=cp1252` → `UnicodeEncodeError`; could not pack its own source on the PC | applied — both streams UTF-8 `errors=replace`; guard :697 |
| M-6 | MED | [evidence_extract.py:704](../../../.agents/scripts/evidence_extract.py#L704) | 6 bad paths + 1 good → sliced before validation → empty pack, exit 0 | applied — cap counts files PACKED; guard row |
| M-7 | MED | [evidence_extract.py:585](../../../.agents/scripts/evidence_extract.py#L585) | added `++ x` source line renders `+++ x` → treated as header → patch truncated + bogus key | applied — positional header detection; guard 5b rows |
| M-8 | MED | [evidence_extract.py:252](../../../.agents/scripts/evidence_extract.py#L252) | `../../../../etc/hosts` read and printed as evidence | applied — every escaping candidate dropped, fallback included; guard :677 |
| M-9 | MED | `_note` :151 + call sites | silent-empty/partial: nothing on stderr for skips, blown deadlines, degraded findings | applied — stderr notes everywhere the contract promises one |
| M-10 | MED | guard §2b | four caps (callers 10 · cross-refs 10 · blast 5 · slice 1200) had no rows | applied — four rows, each with the cap proven to bite |
| M-11 | MED | docstring + INDEX.md | both named `_import_specifiers`, which does not exist | applied — real names (`_python_module_names`/`_python_importers`/`_ts_importers`) |
| M-12 | MED | docstring + guard header | both still claimed the discredited PATH-emptied proof | applied — sitecustomize wording with the `os.defpath` reason kept |
| L-13 | LOW | `_extract_diff_hunk` :643 | dead `line is None` branch (caller always coerces) | applied — removed |
| L-14 | LOW | `_extract_mentioned_file_paths` | space-check claimed dead | **dismissed** — live for the backtick regex, its other source; not dead code |
| L-15 | LOW | guard :898 | third-party tripwire checked 2 names; `import numpy` passed | applied — every import vs `sys.stdlib_module_names` |
| L-16 | LOW | guard §7 | docstring tripwires inflate the row count | **dismissed** — disclosed as tripwires in place; disclosure, not deception |
| L-17 | LOW | `main()` | `--pack` silently ignored `--diff`/`--blast-radius` | applied — usage error, exit 2 |
| L-18 | LOW | plan D5 | determinism claimed unqualified; 10s deadlines make big-repo output load-dependent | applied — claim scoped to inside-deadline runs, partials now carry a note |
| L-19 | LOW | `_alias_roots` :491 | tsconfig without `paths` got an invented `@/ → src` root → confident wrong resolutions | applied — default only when NO config exists; guard :648 |

**Gates (Step 3, all bare, at the staged tree of `6d51047`):** `run_all.py` 21/21 files, 1086/1086
cases, exit 0 · `workflow_lint --toolkit-only` 0 errors 0 warnings, exit 0 · guard 98/98, exit 0 ·
`py_compile` exit 0.

**Round 2 — clean-room re-verification @ `3f5dc27` → CONCERNS.** An independent clean-room pass
(no conversation context) confirmed **every round-1 finding closed or dismissed-with-evidence by
execution** — including reproducing all four hollow-row mutants and watching the rebuilt guard
kill each — then ran its own 13-mutant campaign and 17 defect-repro scenarios. Its verdict line:
*"CONCERNS — all 19 prior findings are genuinely closed … but my own mutation campaign found one
surviving mutant … plus three MED/LOW residues in the new code; none hands wrong evidence to a
reviewer at HEAD."* All five residues closed on the lane in the round-2 commit:

| # | Sev | Where | Failure scenario | Disposition |
|---|---|---|---|---|
| NEW-1 | MED | guard coverage for `_under_skip_dir`'s pair clause | deleting only the pair clause (keeping the walk prune) scored 98/98, so a refactor collapsing it ships green while a DIRECT `--pack`/finding target inside `.claude/worktrees/` returns another branch's code | applied — two pinning rows (direct pack refused with a note; findings `file_path` yields empty `primary_code`); the surviving mutant now dies on both |
| NEW-2 | MED | `main()`'s `usable` pre-filter | titleless/non-dict findings silently dropped — 4 in → 2 out — while the docstring promises index joins; every package after a dropped entry would be misassigned | applied — filter removed, one package per input entry ALWAYS (junk degrades in place with a note); 4-in-4-out guard rows |
| NEW-3 | MED | `_alias_roots` JSONC handling | a real-world JSONC tsconfig fails `json.loads`, is skipped silently, AND suppresses the default — aliased imports read `IMPORTED BY: none` with no way to know why | applied — the skip is named on stderr; guard row with a JSONC fixture |
| NEW-4 | LOW | `_resolve_rel` docstring overclaim | containment is lexical (`abspath`, no `realpath`); an in-repo symlink to an outside file is read | applied as a docstring scope, behaviour kept BY DESIGN — this system plants junctions inside repos (portable memory store) and following them is the intended read; a repo linking outside has vouched for the target |
| NEW-5 | LOW | `split_unified_diff` docstring | the disclosed bare-concat cost described the wrong failure shape ("keeps only its first file" — actually the first file's patch absorbs later headers and hunks) | applied — sentence corrected to the verified shape |
| obs | — | guard §5b in-process call | a raise there crashed the guard (every later row unreported) rather than failing a row | applied — wrapped; a raise is now a red row, not a dead guard |

**Round-2 gates (all bare, at the closure tree):** guard 103/103 exit 0 · `run_all.py` 21/21
files, 1091/1091 cases, exit 0 · round-2 mutants 3/3 killed (driver output pasted in the commit).
Suite counts in the SOP and `INDEX.md` re-trued to **1091/21** in the same commit.

**Acceptance matrix (Step 2, plan items 1–12):**

| Item | Verdict | Proving assertion |
|---|---|---|
| 1 stdlib-only, UTF-8-forced streams | PASS | guard `tripwire: every import is stdlib` + cp1252 row :697 |
| 2 pack caps (6/400/16000/1200) | PASS | four cap rows + counter-examples; slice row :581 (exactly 1200) |
| 3 findings LIST + six fields + caps | PASS | list-shape row, six-fields row, §2b cap rows, dup-title rows :538 |
| 4 no grep subprocess, both modes | PASS | sitecustomize block rows + control shell-out dies; byte-identical both modes |
| 5 IMPORTED BY true positives + negatives | PASS | §3 rows: flat/package/parent-form/TS-relative/alias/index, each with counters |
| 6 caps, skips, stop-words discriminate | PASS | node_modules/worktrees counters, stop-word row, 8-of-12 identifier rows |
| 7 degrades instead of dying | PASS | §5: missing/binary/absent-line exit 0 **with stderr notes**; 1e400 + poisoned-finding isolation rows |
| 8 deterministic | PASS | byte-identical row (same-fixture double run); claim scoped per L-18 |
| 9 registered (INDEX + SOP + auto-discovery) | PASS | rows present; `run_all` discovered the guard (21st file) |
| 9b both suite counts true, measured | PASS | 1086/21 measured 2026-08-12 (~80 s); SOP callout records the double staleness |
| 10 the guard can fail | PASS | **15/15 mutants killed across both rounds** — the review's four, a revert per fix, and the re-review's survivor closed by NEW-1's rows |
| 11 repo-name recurrence resolves | PASS | recurrence row (`myrepo/core.py`) |
| 12 GitNexus decision in docstring | PASS | guard docstring rows |

### Clean-Code Gate

| Check | Result |
|---|---|
| Machine floor (`py_compile`, lint on changed set) | exit 0 / 0 errors 0 warnings |
| §2A comment contract | new comments state constraints, not narration: the OverflowError comment names the real input (`1e400`), the pair-prune comment names the false-evidence consequence, the splitter docstring names the accepted cost (bare concatenated diffs) |
| §2C conventions | matches siblings: module docstring with WHY sections, `_snake` helpers, `Cases`-style guard, no new dependencies |
| Naming | `_SKIP_DIR_PAIRS`, `_note`, `_safe_extract` follow the file's existing register |
| Dead code | L-13 branch removed; no new unreachable paths found |

**Step 0.7 re-derivation:** `main` moved `8556e81 → 4274a96` (SCC-118, 8 commits) mid-review and
was absorbed at merge `c4f69ff` before the verdict; true overlap was test-suite-count coupling only
(no file overlap — `merge-tree` clean, SOP auto-merged). Landing-order dependency confirmed real:
SCC-118's three test files moved the measured floor 18/988 → 21/1055 (→ 1086 after this rebuild),
which is why the counts were re-measured at the fixed sha rather than carried. Re-checked after the
fix push: `origin/main` still `4274a96`, lane 0 behind — nothing further moved under this verdict.

## Your Actions

- [ ] **Close out and merge** — `/smh-close-task-merge-tree` with `--expect-key SCC-123`. The lane
  is pushed, clean, 0 behind `origin/main`; nothing merges without your sign-off. ⚠ One heads-up
  for the merge in the shared checkout: your two rolled-in files still sit there UNTRACKED at the
  same paths; if git refuses the merge over them, the copies are byte-identical (`cmp`-verified) —
  remove the untracked pair and re-merge, nothing of yours is lost.
- [ ] **SOP-nag ticket (optional, your call from the plan's 9b):** the suite-count staleness now has
  three recorded instances in two days; a nagging check was scoped as its own ticket and none
  exists. Say the word and it gets minted; not minted unilaterally.
- [x] ~~`_artifacts/_main/INDEX.md` missing rows~~ — cross-session drift (8 folders, most not this
  lane's), deferred to `/update-maps-indexes` per the SessionStart hook's own remedy; not swept into
  this diff.
