---
IsArtifact: true
ArtifactMetadata:
  type: walkthrough
  task: SCC-305
  branch: chore/SCC-305-bugs-cycle-8
  date: 2026-08-24
---

review-runtime: fan-out

# SCC-305 — Bugs cycle 8, consolidated lane (Parts A–I) — walkthrough

Nine riders on one branch: SCC-309 (A), SCC-310 (B), SCC-311 (C), SCC-312 (D), SCC-313 (E),
SCC-314 (F), SCC-315 (G), SCC-317 (H), SCC-319 (I — operator-added mid-lane).

## Task Checklist

- [x] Startup step: `jira_feed.py start --key SCC-305 --apply` — cycle 9 minted as SCC-318,
      baton handed, read back as exactly two rows (SCC-318 `running-bug-list` / SCC-305
      `bugs-and-updates`); SCC-305 → In Progress by hand (start leaves Rolling Tickets alone).
- [x] Worktree `chore/SCC-305-bugs-cycle-8` cut at e4ec815 from origin/main; no sibling lanes.
- [x] Plan + self-audit (GO, 2 findings baked in) + operator `approved`.
- [x] Part A — bare `pytest -q` totals pattern (RED Q1/Q2 seen: totals=None; GREEN 7/7).
- [x] Part B — managed exclude block in the COMMON info/exclude (RED X1/X3 seen; GREEN 4/4).
    - Finding while building: a per-worktree `info/exclude` is IGNORED by git — measured with a
      probe before designing; the ticket's assumed mechanism does not exist, so the block lives
      in the shared file and unlink keeps it while any sibling lane remains.
- [x] Part C — grammar op-first + literal example in cicd-dev-story-tests, smh-quick-dev,
      artifacts-always-first (+ parse-your-own-block proof step). smh-plan-task:196 verified
      already op-first.
    - The maps commit gate read the example path `path/to/file.md` as a broken doc link —
      examples now use a `.py` path, same grammar.
- [x] Part D — pyrefly row pins the venv interpreter. Measured on the Mac against AGY's venv:
      bare = 949 errors / 669 missing-import; pinned = 405 / **0** missing-import. PC owed.
- [x] Part E — step-01 lens-tree contract: lobby `isolation: "worktree"` delivers neither half
      for a submodule project; per-lens `git -C <project> worktree add --detach` recipe written,
      probe recorded as the verification method.
- [x] Part F — cicd-code-review Step 3.1 inherits by TREE comparison (`wf.same_tree`), names the
      implementing code, carries the smh `docs/`-invalidates clarification; sha-equality gone.
- [x] Part G — Step 5 sixth MANDATORY checkbox: story file `Status: review` AND Dev Agent Record
      filled, placeholder grep (`\{\{|\(2 fills:`) that must return nothing; "may advance" → MUST.
- [x] Part H — gate_receipt worktree resolution (RED W1/W4 seen: receipt in main, silent foreign
      write; GREEN) + jira.md two-label row + three prose sites + cross-board note.
- [x] Part I (SCC-319) — `memory_store_check.py` promoted from the test file (one
      implementation, two callers), per-worktree baseline delta, three advisory post-move hooks
      (RED: module absent; GREEN 19/19).
- [x] Suite failures diagnosed and fixed, not waived: check_maps F2 wanted this lane's INDEX row
      (added); test_install_git_hooks live check failed because the machine's local
      `core.hooksPath` had drifted to an ABSOLUTE path — reset to the installer's own relative
      `.githooks`, 30/30.
- [x] Mutation sweeps (declared before mutating, code-derived): 3/3, 3/3, 2/2 killed by their
      declared cases; trees restored and verified by the sweep script.
- [x] Full suite through the receipt writer: PASS @ 046294b2 (first stamp was a real RED that
      caught the two failures above — the mechanism working).
- [x] Five-lens code review: 49 raw findings triaged under code-standards §6.5 → one fix wave
      (commit d3e006e, every code fix RED-first), re-certified PASS 61/61 @ d3e006e4. Details
      in `## Code Review` below; raw lens returns in [review-lens-results.md](review-lens-results.md).

## Evidence

| Acceptance | Proof (RED → GREEN) |
|---|---|
| A1–A4 (-q totals) | `test_gate_receipt.py` block `SCC-309/317…`: RED `Q1/Q2 totals=None` → GREEN `Q1 totals='3043 passed, 35 skipped, 547 warnings in 9.14s'`, `Q2 totals='3 failed, 275 passed in 12.0s'`; Q3 pins absence-still-null (born green, characterization) |
| B1–B5 (clean lanes) | `test_link_worktree_assets.py` block `SCC-310…`: RED `X1 ?? .venv ?? auth_keys`, `X3 no managed block` → GREEN 4/4; X2 real-dirt-still-dirty is the allow half |
| C1–C3 (grammar) | op-first + literal example in all three sites; this lane's own plan block parses 18(+7) entries, 0 incomplete via `declared_change_set.py parse` |
| D1–D3 (pyrefly) | pasted Mac runs: bare 949 errors (669 missing-import) vs pinned 405 (0 missing-import); `pyrefly.toml` untouched; PC paste-run → Your Actions |
| E1–E3 (lens trees) | step-01 launch contract rewritten with the measured probe + per-lens project-worktree recipe; bare `worktree` record now requires copies OF THE REPO UNDER REVIEW |
| F1–F3 (tree inherit) | `grep -c same_tree .agents/commands/cicd-code-review.md` 0 → 3 (measured after the review fix restated Step 3.1 as the two-layer test); sha-equality adopt bullet gone; "fail toward running" retained verbatim |
| G1–G3 (story file) | sixth MANDATORY checkbox with machine grep; may→MUST at the Done section; sibling commands checked: cicd-code-review, cicd-close-story-merge-tree, cicd-update-sprint-memory carry no Dev Agent Record mention (gap was chain-wide, now gated at ② close-out) |
| H1a–H1e (lane receipts) | RED `W1 in_main=True`, `W4 silent foreign write exit 0` → GREEN `W1 in_lane=True in_main=False`, `W2 check exit 0`, `W3 unchanged at project root`, `W4 exit 2 naming both trees` |
| H2a–H2c (labels) | jira.md row teaches both labels + dual-label JQL + AVCH-80 cross-board note; `grep -rn "bugs-and-updates" .agents/` post-fix: every hit states the two-label design (work-consolidation.md, jira_feed.py, tests, fixed prose). Deliberate deviation from SCC-317 acceptance 3 recorded: post-handoff the single-label query returns the successor, so the rule prescribes the dual-label search that cannot lie between or during cycles |
| I-1..I-5 (memory store) | `test_memory_store_check.py` RED (module absent) → GREEN 19/19: I1 dead-row exit non-zero naming the file; I2 `tms.check_store is msc.check_store`; I3 incident repro (`reset --keep`) SHOUTS all three names; I4 store-untouched move silent; I5 three hooks exist, probe `python3 → python → py`, `exit 0` advisory. `test_memory_store.py` passes unchanged with the import |

Suite: `run_all.py` **61/61 files** via `gate_receipt.py` receipt `gates/suite.json` — final
certification **PASS @ d3e006e4** (exit 0, 85.5s), stamped after the review-fix wave, the last
code-touching change; commits after it are `_artifacts/`-only → code-fresh. The development
certification was PASS 61/61 @ 046294b2. Both first attempts were real REDs on environment
defects (check_maps INDEX row; `core.hooksPath` drift, twice) — fixed, not waived (Suite Ledger).

Mutation sweeps (tables in [sweep-gate-receipt.json](sweep-gate-receipt.json),
[sweep-link-assets.json](sweep-link-assets.json), [sweep-memory-check.json](sweep-memory-check.json)):
M1 -q pattern width narrowing → killed by Q2 · M2 same-repo comparison inverted → killed by W1 ·
M3 main() wiring dropped → killed by W1 · M4 exclude write dropped → killed by X1 · M5 sibling
guard dropped → killed by X3 · M6 removal disabled → killed by X4 · M7 delta gutted → killed by
I3c · M8 dead-row check dropped → killed by I1b. **8/8 killed by their declared case**; each sweep
ended with the full file unfiltered green (50/50, 51/51, 19/19) and byte-identical restores.

## Suite Ledger

| scope | command | duration | result | why this run |
|---|---|---|---|---|
| full | `gate_receipt.py run --task SCC-305 --gate suite --root … -- run_all.py` | 84.8s | FAIL 58/60 @ e116644f | first certification attempt — caught check_maps F2 (INDEX row) + hooksPath drift |
| scoped | `test_check_maps.py`, `test_install_git_hooks.py` | ~40s | diagnostic | read the two failures |
| full | same receipt command, re-stamp | 84.6s | PASS 61/61 @ 046294b2 | certification after the fixes + Part I |
| full | same receipt command, post-review | 79.9s | FAIL 59/61 @ d3e006e4 | first post-review-fix stamp — caught the machine's `core.hooksPath` drifted back to ABSOLUTE (second occurrence today) |
| scoped | `test_hooks_armed.py`, `test_install_git_hooks.py` | ~35s | diagnostic → green | after resetting `core.hooksPath` to relative `.githooks` |
| full | same receipt command, re-stamp | 85.5s | **PASS 61/61 @ d3e006e4** | certification at the shipping SHA, after the last code change |

## Your Actions

What landed: branch `chore/SCC-305-bugs-cycle-8` — commits e116644 (Parts A–H), the Part I
commit, d3e006e (review-fix wave), and the receipt/artifact commits — pushed, `0 0` vs origin.

Agent-taken decisions, for ratification: (1) Part B writes the shared COMMON `info/exclude`
(measured: git ignores a per-worktree one) with removal gated on last-lane unlink; (2) Part H2
deviates from SCC-317's literal acceptance 3 — jira.md prescribes the dual-label search;
(3) machine config `core.hooksPath` reset from absolute to relative `.githooks` (the installer's
own designed value) to unbreak the live-repo check — **it drifted back to absolute within hours
and was reset a second time during review; no script in this repo writes an absolute value, so
something machine-local (IDE or another session) rewrites it — worth watching**; (4) sync-agents
was run mid-lane, so the machine caches carry this lane's doc text ahead of the merge — a
post-merge sync re-converges them; (5) the memory-store delta baseline only advances on a clean
run — after a deliberate retirement the shout repeats until `--delta --rebaseline` acknowledges it.

- [x] The merge itself — lands via this branch's PR
- [ ] DECISION — PC half of Part D: paste `<VENV>/pyrefly check --python-interpreter-path <VENV>/python`
      into a PC shell from an AGY checkout and confirm 0 fabricated missing-import (SCC-312
      acceptance 2/4; this Mac session cannot run it).
- [ ] DECISION — the three memory-store hooks guard the LOBBY only. Project repos
      (AGY_AVIATIONCHAT first) get the same guard when their own `.githooks/` carry the shims —
      cross-repo work needs a ticket per repo, so say the word and it becomes an AVCH ticket.

## Code Review (2026-08-24)

Verdict: PASS @ d3e006e4070830b110423f61be8a82969ef2ff9b

lenses_run:
- acceptance-auditor · ok
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- test-adequacy-auditor · ok

lenses_counted: 5
lenses_na: none

dispositions: per-lens: acceptance-auditor 4 drift rows → recorded in drift line · blind-hunter 17 → 6 fixed · test-adequacy-auditor 11 → 4 folded into the fix wave · edge-case-hunter 12 → 4 fixed (2 VERIFIED promotions) · literal-correctness-hunter 5 → 4 fixed — 49 raw findings, ~20 deduped anchors, 13 distinct fixes (8 code+test in commit d3e006e, 5 doc), remainder dismissed under §6.5
drift: undeclared=9 (doc-graph regen ×2 + sync-cache mirrors ×7 — all byte-products of declared steps, kept) · unimplemented=3 (`.agents/workflows/*` thin-launcher EDIT rows — sync never rewrites launchers for content edits; permanently unimplementable, recorded here so the rows read as a declaration error, not a failed sync) · incomplete=0 — dispositions in the findings table

### Findings — fixed (all three §6.5 answers YES)

| Anchor | Corroboration | Defect → fix |
|---|---|---|
| `gate_receipt.py` -q totals | edge-case ×2, VERIFIED | pattern matched retry prose (`2 failed, retrying in 30s`) and `_totals` took the FIRST match (inner suite beat the final summary) → clause-grammar pattern + LAST match; RED Q4/Q5 seen, now green |
| `gate_receipt.py lane_receipts_root` | blind + test-adequacy | `--cwd` outside any git repo silently fell back to `--project` (the SCC-317 shape mirrored); non-git `--project` blamed the wrong flag → both refuse, naming the path; RED W5 seen |
| `memory_store_check.py check_delta` | blind + TA + edge-case (×3 important) | the DETECTING run advanced the baseline — a confirming re-run answered "all fine" and the evidence was gone → baseline holds until recovery; `--delta --rebaseline` is the acknowledgment for deliberate removals; corrupt/unwritable baselines say so on stderr; RED I3d/I6b seen |
| `memory_store_check.py main` | test-adequacy | explicit `--store <typo>` exited 0 silent → exit 2 naming the path; hook's no-flag default stays silent; RED I7a seen |
| `link-worktree-assets.py _split_managed_block` | blind + edge-case, VERIFIED | missing END sentinel absorbed USER exclude patterns into the managed block (deleted on last-lane unlink) → truncated block = sentinel line only; RED X5a/X5b seen |
| `cicd-code-review.md` Step 3.1 | blind + literal-correctness (×2 important) | my new prose claimed `same_tree` exempts `_artifacts/` commits — it has no carve-outs; the "cannot disagree" guarantee was false on first use → restated as the honest two-layer test (`same_tree`, then `git diff --name-only` filtered to `_artifacts//_bmad-output/`) |
| `jira.md` labels row | blind | handoff window: dual-label JQL returns TWO open rows with no tiebreak → one sentence (file into `bugs-and-updates`; the baton row only holds the baton) + a real `### Labels` heading so the `§labels` pointers resolve |
| SOP + changelog claim | blind + TA + plan row | "memory store is guarded now" overclaimed — hooks ship lobby-only → claim scoped, per-repo install owed as a Your Actions DECISION |
| `cicd-dev-story-tests.md` Step 5 grep | literal-correctness | `(2 fills:` exists nowhere in tree, packs, or the incident story → dropped; the gate is the attested `{{` grep |
| walkthrough F1 evidence | literal-correctness | pasted `grep -c` figure did not reproduce (0→2 vs actual 3) → re-measured and corrected |
| `test_gate_receipt.py` W3b/W4 | test-adequacy + blind | dead `subdir` fixture now exercised; W4's name-substring assert was half-vacuous → asserts path segments |

Dismissed (one line, per §6.5): the remaining ~7 deduped anchors — names-only delta (the ticket's own acceptance definition; content-revert out of scope), conservative keep of the exclude block under stale worktrees, lens-recipe caveats, I5 grep-strength and INDEX_CAP identity suggestions, no-summary `no tests ran` form, orphaned pre-fix receipts (one transition), shared-file locking — dismissed as not-REAL, not-BEHAVIOUR, or not-this-diff. Calibration disagreements worth naming: edge-case #10 ("older-branch checkout is a FALSE alarm") was dismissed *against* its important label — for the symlinked lobby store that checkout genuinely empties the live store, so the shout is a true positive; edge-case #6 was promoted *by verification* from blind #12's suggestion to a fixed data-loss defect; blind #16 (importer path) was verified dismissable — receipts are committed in-tree and travel with the merge.

### Gates

| Gate | Result |
|---|---|
| Full suite (receipt) | `gates/suite.json` — **PASS 61/61, exit 0, 85.5s @ d3e006e4**, after the last code change; the FAIL 59/61 before it was the machine's `core.hooksPath` drift (Suite Ledger), not this diff |
| Scoped assertions | `test_gate_receipt.py` 54/54 · `test_link_worktree_assets.py` 53/53 · `test_memory_store_check.py` 26/26 · `test_memory_store.py` green unchanged |
| workflow_lint | `--toolkit-only`: 0 error(s), 0 warning(s), 8 info (pre-existing BOM/info rows) |
| check_links | clean (walkthrough swept in while untracked) |
| sop_currency | armed commit-msg gate passed d3e006e with the SOP + changelog staged in the same commit |
| py_compile | gate_receipt.py, memory_store_check.py, link-worktree-assets.py — OK |

### Acceptance matrix

A through I: DELIVERED (evidence table above). G3 — the one PARTIAL from the acceptance lens —
closed when this walkthrough landed with the sibling-commands line in the G row. H2 carries the
recorded deliberate deviation (dual-label search over SCC-317's literal acceptance 3).

### Clean-Code Gate

Machine floor: this is the scripts-only lobby (no `backend/`/`frontend/` stacks), so the floor is
`py_compile` over the three touched scripts (OK) plus the suite's own lint files — green. Judgment
pass: comment contract holds (review-fix comments state the constraint, not the changelog);
no banned patterns introduced; the two stderr prints in `check_delta` are the advisory-loudness
design, not debug residue.

### Step 0.7 — re-derivation

1. What moved on main since the branch cut: nothing — zero commits, zero files (re-checked at review).
2. What that changes for this lane: nothing — no rebase, no overlap, merge-tree still clean.
3. What was re-derived: no sibling lanes live; review_level=standard held for the whole review.
