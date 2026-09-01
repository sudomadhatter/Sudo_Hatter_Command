# Implementation Plan — SCC-146: gate receipts for the Task lane (close-out reads the verdict)

**Ticket:** [SCC-146](https://sudo-command.atlassian.net/browse/SCC-146) (Bug) · **Branch:** `chore/SCC-146-gate-receipts` · **Worktree:** `.claude/worktrees/gate-receipts` off `main` @ `44a12c1`

## The defect, reproduced in the source (reproduce-before-you-fix, doc/flow tier)

Two findings, one root:

1. **Redundancy.** The Task flow runs `run_all.py` up to 4× with no code change between runs:
   quick-dev Step 3 (`smh-quick-dev.md:234`), review Step 3 (`smh-code-review.md:188`), the
   clean-code audit's machine floor (Step 3.5), and close-out Step 2
   (`smh-close-task-merge-tree.md:180`). `smh-code-review.md:195` states the limit outright:
   *"No receipts on this lane, and that is a stated limit, not an oversight."*
2. **Correctness hole.** `task_preflight.py:729 check_artifacts()` only globs for a
   `walkthrough.md` mentioning the key — it never reads the canonical
   `Verdict: PASS|CONCERNS|FAIL|WAIVED @ <sha>` line that `/smh-code-review` Step 4 writes
   (`smh-code-review.md:239-243`). **A FAIL verdict does not block the merge today**; if
   close-out's own gate run happens to pass, the work lands.

The one-line blocker: `wf_common.py:23` `BOARD_REL = "_bmad-output/implementation-artifacts/sprint-status.yaml"`,
and `resolve_project_root()` (`wf_common.py:79`) dies without that file. `gate_receipt.py:261`
calls it unconditionally in `main()` before any subcommand dispatch, so the receipt machinery —
which otherwise already does everything needed (`--cwd`, `check --sha`, tree-identity staleness
via `wf.same_tree`) — cannot run in the lobby, which has no board by definition.

**Verified in-source before planning:** line numbers above are re-derived against this worktree
(ticket's cached 552/653 had drifted to 729/856 — same lesson SCC-149 logged).

## Sibling-lane dependency (read at Step 0.5, binding on this plan)

`chore/SCC-149-incident-taxonomy` is at its review gate now and touches
`docs/_scc_sops_prds/workflows_testing_SOP.md` (row ~1311), `.agents/.sync-manifest.json`, and
`_artifacts/_main/INDEX.md`. This lane touches the same three files (different SOP sections —
§9's smh command walkthroughs, ~740-1200). **Landing order: SCC-149 first.** At this lane's
close-out, absorb `main` and reconcile: SOP sections are disjoint (auto-merge expected),
`.sync-manifest.json` is regenerated (never hand-merged), INDEX ledger keeps both rows
(SCC-147's precedent). If SCC-149 somehow does not land first, nothing here depends on its
content — only on merge mechanics.

## Acceptance (from the ticket's ACCEPTANCE block, all checkable)

| # | Item | Proving assertion |
|---|---|---|
| A1 | `gate_receipt.py run --root <dir> …` writes `<dir>/gates/<gate>.json` with **no board file present anywhere above it** | new case in `test_gate_receipt.py`: repo in a temp dir with no `_bmad-output/`, `run --root` succeeds, receipt lands at `<root>/gates/<gate>.json` |
| A2 | Without `--root`, behaviour is **byte-identical** to today | regression case: existing board-backed fixture, receipt path + JSON fields + exit codes unchanged (the 15 existing cases are themselves the regression net; add one explicit no-`--root` path assertion) |
| A3 | `check --sha <X>` rejects a receipt stamped at a different sha | **already pinned** — existing cases 8, 13–15 (`test_gate_receipt.py:109-161`); extend with one `--root` variant so the rejection is proven in root mode too |
| A4 | preflight prints `gate: SKIP — verdict <V> @ <sha>, receipts valid` when verdict is PASS, sha == HEAD, receipts valid, tree clean | new case in `test_task_preflight.py` (the ALLOW half) |
| A5 | preflight prints the gate commands when (a) sha moved, (b) tree dirty, (c) no receipt — **three separate assertions** | three new cases in `test_task_preflight.py` |
| A6 | preflight **exits 2** when the walkthrough verdict is FAIL | new case (the REJECT half) |
| A7 | A full Task lane run executes `run_all.py` exactly ONCE end to end | procedural: **this lane exercises itself** — count invocations across this lane's own quick-dev→review→close-out and record the count in the walkthrough |
| A8 | `run_all.py` stays N/N on a properly-armed machine | the closing bare run |
| A9 | `workflows_testing_SOP.md` updated in the **same commit** as the command changes — three commands change, so `sop_currency` fires; `[sop-ok]` is NOT appropriate | `git show --stat` of the commit |

## Steps (each maps to acceptance items; assertion named per step)

### S1 — `gate_receipt.py`: `--root` + `--task` (A1, A2, A3)

- Add `--root <path>` to the `run`, `check`, and `list` subparsers. In `main()` (line ~261):
  when `--root` is given, `project = Path(args.root).resolve()` and **`resolve_project_root()`
  is never called**; when absent, the current line runs unchanged.
- Receipt location in root mode: `<root>/gates/<gate>.json` — flat, no `norm_id(story)` segment
  (the root is already task-specific: `_artifacts/_main/<date>_<slug>/`). Implemented as a
  parameter on `receipt_dir()` (or a sibling helper) so `cmd_run`, `cmd_check` via
  `load_receipt`, and `cmd_list` all resolve the SAME way — one resolver, mirrored nowhere.
- Add `--task` as an argparse **alias for `--story`** (same dest, same receipt field — no
  schema churn). `run/check/list` each get it.
- `cmd_run`'s `path.relative_to(project)` print is safe in root mode (receipts are under root);
  guarded by the A1 test asserting the printed receipt path.
- **DO NOT touch** `resolve_project_root()`, `BOARD_REL`, or `GATES_REL` — shared by
  `check_maps`, `closeout_preflight`, `jira_feed`, `split_sprint_status`, `story_status`.

### S2 — `task_preflight.py`: the `gate` check (A4, A5, A6)

- `check_artifacts()` (line 729) currently returns `None`; make it **return its `hits` list**
  (behaviour otherwise unchanged) so the new check reuses the same walkthrough resolution —
  the ticket's "do not write a second one".
- New `check_gate(repo, branch, hits, rep) -> str | None` run from `main()` after
  `check_base`/`check_scope` (it needs their inputs' semantics, not their objects):
  - Parse the **canonical first line** `Verdict: (PASS|CONCERNS|FAIL|WAIVED) @ <sha>` from the
    hit walkthrough(s). Multiple hits with verdicts → use the one whose sha resolves; conflicting
    verdicts → no SKIP (fall through to full plan, say why).
  - **FAIL → `rep.err` → exit 2** (the merge is refused; A6).
  - **WAIVED → treated as CONCERNS, receipt check skipped** (WAIVED already means no suite
    exists) — eligible for SKIP only in the no-suite sense: it prints the plan as today (the
    plan for a WAIVED repo is already "(no enforcement suite…)").
  - **PASS/CONCERNS**: SKIP requires ALL of — verdict sha == HEAD (tree-identity via
    `wf.same_tree` is acceptable, matching `check_receipt`'s own staleness rule) · receipts
    under `<walkthrough-dir>/gates/` valid (reuse `gate_receipt.check_receipt` by import — the
    module is already imported nowhere in preflight, so import it the way `hooks_armed` is;
    receipts must be result `pass`/`warn`, not dirty, sha-fresh) · working tree clean ·
    `origin/main` absorbed (the same facts `check_sync`/`check_base` derive — recomputed
    cheaply or read from `rep`, whichever keeps the checks independent; decided at RED time by
    what the test can pin).
  - Any miss → return `None` and the existing `gate_plan()` prints commands exactly as today
    (A5's three cases).
- `main()`: when `check_gate` returns a SKIP line, print `gate: SKIP — verdict <V> @ <sha>,
  receipts valid` at the existing print site (line ~856) instead of the plan rows. JSON mode
  carries the same decision (`"gate": ["SKIP — …"]`).

### S3 — `/smh-quick-dev` Step 3: stamp the suite receipt (A7)

Wrap the ONE full-suite run in the receipt writer:

```bash
python3 .agents/scripts/gate_receipt.py run --task <KEY> --gate suite \
    --root <task-artifacts-dir> --cwd <worktree> \
    -- python3 .agents/scripts/tests/run_all.py
```

Real output still pasted, as today. One paragraph, in Step 3's existing bullet — no new step.

### S4 — `/smh-code-review` Steps 3 + 3.5: inherit, else re-stamp (A7)

- Step 3: **replace** the `smh-code-review.md:195-199` "No receipts on this lane" paragraph
  with inheritance mirroring `/cicd-code-review`'s certification logic: receipt sha == HEAD
  **and** result pass (failed:0) **and** clean tree → **adopt, cite the receipt, do not
  re-run**; anything else → run and re-stamp (same `gate_receipt.py run --root` form). Port
  verbatim: **"Fail toward running, never toward trusting."** Call out that Step 0.7 absorbs
  `main` and moves HEAD, so the sha check invalidates the inherited receipt automatically —
  correct, and needs no special case.
- Step 3.5: extend the existing "No double drift-hunt" carve-out (line ~219) to the machine
  floor: when nested, `/smh-clean-code-audit` **imports Step 3's receipts** instead of
  re-running run_all / workflow_lint / sop_currency / link+anchor, and runs only what Step 3
  did not (py_compile, comment contract §2A, convention table §2C). **Standalone
  `/smh-clean-code-audit` is unchanged** (its own body already carries the import-when-nested
  convention at `smh-clean-code-audit.md:129`; verify no contradicting sentence remains).

### S5 — `/smh-close-task-merge-tree` Step 2: honour the preflight (A7)

- State that Step 2 runs what the preflight printed: a `gate: SKIP` line from the preflight is
  the ONLY skip — **the agent never decides to skip on its own reading**; gate commands printed
  → run them all, as today.
- Keep and state the scope difference: close-out runs `workflow_lint.py` **without**
  `--toolkit-only` while review runs it **with** — different scopes, NOT duplication; written
  down so it is not "cleaned up" later.

### S6 — SOP + mirrors + ledger (A9)

- `docs/_scc_sops_prds/workflows_testing_SOP.md`: update §9's three command walkthroughs
  (~740, ~1087, ~1178) + the gate-receipt mention at ~466 if it claims story-lane-only.
  **Staged in the same commit as the command/script changes** — `sop_currency` fires; no `[sop-ok]`.
- Mirrors regenerated via `/smh-sync-agents` (never hand-edited): skills + opencode + workflows
  for the three commands.
- `_artifacts/_main/INDEX.md` ledger row for this session dir.

## RED strategy (Step 2 of the lane — written and run FIRST)

All in the two existing suites (extend, never fork — `red-file-hosts-expansion-tests`):

- `test_gate_receipt.py`: A1 (boardless `--root` run), A2 (no-`--root` regression pin),
  A3-root variant, `--task` alias case.
- `test_task_preflight.py`: A4 SKIP · A5 sha-moved / dirty / no-receipt (3 cases) · A6 FAIL→exit 2.
  Fixture: extend `make_repo()`'s walkthrough fixture with a parameterised `Verdict:` line +
  a real receipt written by actually invoking `gate_receipt.py run --root` (never a hand-written
  JSON — a hand-faked receipt is the exact fabrication the tool exists to prevent).

Expected RED: A1/A4/A5/A6 cases fail against current source (gate_receipt dies in
`resolve_project_root`; preflight has no `gate:` SKIP/FAIL logic). A2/A3 pass green-first and
are declared as characterization.

## Mutation sweep (declared here in shape; the table itself is drawn FROM the final code at Step 3, per tests-must-gate-for-real §Mutation Testing)

Candidate classes, from the code being changed: (a) `--root` resolution falls back to
`resolve_project_root` anyway (the blocker resurrected); (b) `check_gate` treats FAIL as
CONCERNS (the correctness hole resurrected); (c) SKIP printed without the receipt-validity
conjunct; (d) SKIP printed on a dirty tree; (e) verdict regex loosened to match a
non-first-line mention (prose-pinning class). Sweep runs as ONE pass, restore from COPIES
(SCC-147's trap), closing green run.

## Out of scope

The cicd- story lane (already has receipts + certification inheritance), `/cicd-quick-dev`,
any change to `resolve_project_root()` / `BOARD_REL` / `GATES_REL`, and the per-machine
receipt caveat (documented in the walkthrough as a stated limit: receipts are per-machine
evidence; a fresh machine re-runs — the SKIP conditions fail safe toward running).

---

## Self-Audit (2026-08-14)

**Mode: PRE-WORK · Right-size: Full** (a gate, a script other scripts import, three command
surfaces, the SOP). Plan: this file · Ticket: SCC-146 · Repo/branch echoed from command output:
`Sudo_Hatter_Command | chore/SCC-146-gate-receipts` (worktree `.claude/worktrees/gate-receipts`).

**Phase 0 — scope + checkable list.** Change set named in the plan header and S1–S6. Acceptance
list A1–A9 comes verbatim from the ticket's ACCEPTANCE block; traceability holds both ways
(every A has an S; every S traces to an A or to house law — mirrors/ledger to the door law and
the INDEX lint). No deployable path in the change set → Task lane confirmed.

**Phase 1 — blast radius.** Walked with grep, not belief:
- `gate_receipt.py` is **imported by `closeout_preflight.py:24`**, which calls
  `gr.receipt_dir(project, story)` (line 307), `gr.load_receipt(...)` (312) and
  `gr.check_receipt(...)` (314) → **finding F1 below**.
- `task_preflight.py` callers: `/smh-close-task-merge-tree` Step 1 (the command body),
  `tests/test_task_preflight.py`, `scripts/INDEX.md` row. All in the change set already.
- Three command files → four platform doors each, regenerated by sync-agents (S6).
- SOP + usage surface in the same commit (S6, A9). `_artifacts/_memory/` untouched.
- **Sibling lanes:** `chore/SCC-149-incident-taxonomy` live at its review gate; overlap =
  `workflows_testing_SOP.md` (disjoint sections), `.sync-manifest.json` (regenerated, never
  hand-merged), `_artifacts/_main/INDEX.md` (keep-both-rows). **SCC-149 lands first**; if it
  does not, nothing here depends on its content — merge mechanics only.

**Phase 2 — over-engineering gate.** `--root` and `--task` trace to A1/ticket fix direction;
`check_gate` to A4–A6; no new command, no new rule, no new script, no new test file (both
suites extended). One deliberate near-tripwire: importing `gate_receipt` into `task_preflight`
mirrors `closeout_preflight`'s existing pattern — reuse, not clone-and-tweak. Cleared.

**Phase 3 — pre-mortem.** Both machines: command bodies keep the `PC: python` convention;
scripts are stdlib-only. Fresh clone / other machine: receipts are per-machine → every SKIP
conjunct fails → gate runs in full (fail toward running — the silent-failure row is closed by
design). Empty input: no verdict line → no SKIP → today's behaviour. Four caches: sync-agents
(S6). Sibling lands first: handled above. Rollback: pure git revert; no delete, no history
rewrite, no ticket transition inside the work. Gate that cannot fail: A5/A6 pin both halves
(reject AND allow) per tests-must-gate-for-real.

**Findings**

| # | file:line | Severity | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | `gate_receipt.py:88` (`receipt_dir`) | important | changing `receipt_dir`/`load_receipt` signatures breaks `closeout_preflight.py:307-314` at story close-out — a crash in the OTHER lane's preflight | **baked into S1**: signature changes are default-preserving keyword params; `test_closeout_preflight.py` runs in the closing suite as the regression net |
| F2 | plan §S2 | minor | `check_gate` reading "main absorbed" by re-deriving it could disagree with `check_base`'s own answer | baked into S2: decided at RED time by what the test pins; the two must share the derivation or the SKIP conjunct drops to the stricter one |
| F3 | plan §RED | minor | hand-written receipt JSON in fixtures would fabricate the very evidence the tool exists to prevent | already in the plan: fixtures invoke `gate_receipt.py run --root` for real |

**Four quick gates:** verification strategy present per item (A-table names the proving case) ·
irreversible: none inside the lane (merge/transition live in close-out, outside this command) ·
vague steps: S2's absorbed-check ambiguity is named and bounded (F2) · convention fit: extends
existing suites, reuses the import pattern, door law via sync-agents.

Audit verdict: GO

