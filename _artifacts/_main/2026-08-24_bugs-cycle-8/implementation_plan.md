---
IsArtifact: true
ArtifactMetadata:
  type: implementation_plan
  task: SCC-305
  branch: chore/SCC-305-bugs-cycle-8
  date: 2026-08-24
---

# SCC-305 — Bugs cycle 8, consolidated lane (Parts A–H)

One branch (`chore/SCC-305-bugs-cycle-8`), one worktree, eight riders:
SCC-309 (A), SCC-310 (B), SCC-311 (C), SCC-312 (D), SCC-313 (E), SCC-314 (F), SCC-315 (G), SCC-317 (H).
Three script fixes with red-first tests (A, B, H-defect-1); five doc/rule fixes with
machine-verifiable assertions (C, D, E, F, G, H-defect-2).

## Acceptance list (checkable — Step 1)

Each row is proved by the named command or inspection; Step 2 turns every row into an
assertion seen RED first (or an honest `characterization` where the check is born green).

- **A** `gate_receipt.py` totals: (A1) a receipt over `pytest -q` output records non-null
  `totals` equal to pytest's own bare summary line; (A2) the `=`-banner form still parses
  (regression); (A3) output with no recognisable summary still records null; (A4) a test in
  `test_gate_receipt.py` pins A1–A3 and FAILS against today's single pattern.
- **B** linked worktrees stamp clean: (B1) a freshly linked worktree reports clean
  `git status --short`; (B2) a receipt stamped there records `dirty_tree: false`; (B3)
  `--unlink` leaves no stale `info/exclude` entries; (B4) real uncommitted edits STILL read
  dirty; (B5) a test pins B1/B3/B4 and fails against today's script.
- **C** Declared Change Set grammar: (C1) `cicd-dev-story-tests.md` Step 1 states
  op-marker-FIRST and carries one literal example bullet; (C2) every sibling statement agrees
  (`smh-quick-dev.md:191`, `artifacts-always-first.md:181`; `smh-plan-task.md:196` is already
  op-first — verified and listed); (C3) a block written from the doc's stated order parses to
  N entries, 0 incomplete via `declared_change_set.py`.
- **D** pyrefly row: (D1) the §6 command in `code-standards.md`, pasted on the Mac from a
  project root, reports only real type errors — zero missing-import for deps present in the
  venv (verified live against AGY's `backend/.venv`); (D2) form is machine-neutral
  (`<VENV>/pyrefly check --python-interpreter-path <VENV>/python` — same `<VENV>` note §6
  already carries for bin/ vs Scripts/); PC paste-run is OWED and recorded in Your Actions;
  (D3) AGY `pyrefly.toml` untouched.
- **E** lens isolation for submodules: (E1) `step-01-review.md` launch contract names what a
  repo-reading lens receives when the reviewed repo is a git submodule under `Projects/`, with
  the per-lens `git -C <project> worktree add --detach` recipe runnable as written; (E2) a
  bare `lens_isolation: worktree` is forbidden unless lenses got isolated copies OF THAT
  PROJECT; (E3) the measured probe is written down as the verification method.
- **F** cicd Step 3.1 inherit: (F1) `cicd-code-review.md` Step 3.1 states a TREE comparison,
  names `gate_receipt.check_receipt` / `wf.same_tree`, and contains no bare sha-equality adopt
  test (`grep -c same_tree .agents/commands/cicd-code-review.md` goes 0 → ≥1); (F2) carries
  the smh clarification that `docs/` invalidates and only `_artifacts/`(+`_bmad-output/`
  planning surfaces) are exempt; (F3) "fail toward running" retained verbatim.
- **G** Step 5 story-file check: (G1) the MANDATORY checklist carries a sixth item — story
  file `Status: review` AND `## Dev Agent Record` filled (no placeholder), with the fixed
  placeholder literal stated as a grep that must return nothing; (G2) ":326-328" prose changes
  "may advance" to a requirement, `never flip to done` clause kept verbatim; (G3) the
  walkthrough states which sibling commands were checked for the same gap and what each said.
- **H1** `gate_receipt.py` worktree resolution: (H1a) `run --project <P> --cwd <worktree>`
  writes the receipt INSIDE the worktree, main checkout left clean; (H1b) `check` with the
  same flags FINDS it (exit 0); (H1c) non-worktree invocation byte-identical to today;
  (H1d) genuine ambiguity REFUSES and names both trees; (H1e) a test pins H1a+H1b red-first.
- **H2** rolling-ticket label: (H2a) `jira.md` §labels teaches the live two-label vocabulary
  (`running-bug-list` = baton on the un-started successor; `bugs-and-updates` = family label a
  started cycle wears) and the dual-label lookup from `work-consolidation.md:77`; (H2b)
  `grep -rn "bugs-and-updates" .agents/` afterwards hits only sites that state the two-label
  vocabulary correctly (work-consolidation.md, jira_feed.py, tests, and the fixed prose) —
  no site presents it as THE lookup label alone, and stale `SCC-190 today` pointers go;
  (H2c) the rule states the label pair is cross-board (AVCH-80).
  NOTE a deliberate deviation from SCC-317's literal acceptance 3: post-handoff (SCC-318
  minted today) the single-label query returns the SUCCESSOR, not SCC-305 — the dual-label
  search is the form that can never lie between or during cycles, so that is what jira.md
  prescribes.

## Steps

1. **RED tests (A, B, H1)** — add failing cases to
   `.agents/scripts/tests/test_gate_receipt.py` (bare `-q` summary → totals; worktree
   `--project`+`--cwd` write/read) and `.agents/scripts/tests/test_link_worktree_assets.py`
   (clean status via info/exclude; unlink cleanup; real-dirt still dirty). Paste RED, read
   which line raised.
2. **GREEN scripts** — `gate_receipt.py`: add a second anchored pytest pattern for the bare
   summary line (alongside, not replacing, the `=` one); resolve the receipts root inside the
   `--cwd` worktree when `--cwd` names a path inside a different worktree of the resolved
   project (both `run` and `check`/`list`), refusing loudly when ambiguous.
   ⚠️ AUDIT FINDING: `closeout_preflight.py:25` and `task_preflight.py:59` `import gate_receipt
   as gr` (and `main_write_gate.py` pulls it into the main gate) — the H1 change stays inside
   `main()`'s flag resolution; `receipt_dir()`, `check_receipt()`, `receipt_defect()`
   signatures untouched, and `test_task_preflight.py` + `test_task_preflight_receipts.py` +
   `test_task_preflight_contract.py` run green in the suite before commit.
   `link-worktree-assets.py`: on link, append the linked asset paths to the worktree's
   `.git` info/exclude (worktree-local); on `--unlink`, remove exactly the lines it wrote.
3. **Doc fixes (C, D, E, F, G, H2)** — edit the seven doc/rule/skill files per the acceptance
   rows above. D is verified by paste-running the new command on the Mac against AGY's venv
   before committing.
4. **Generated mirrors** — regenerate via `/smh-sync-agents` (workflows + platform caches);
   if the sandbox blocks `.claude/skills` writes (SCC-300), record it and leave the sync to
   the operator as a Your Actions row.
5. **SOP currency** — operator-visible changes (D's pyrefly command; H2's label lookup) →
   update `docs/_scc_sops_prds/workflows_testing_SOP.md` if it names either surface, plus a
   one-line changelog row; otherwise `[sop-ok]` per commit with the reason logged.
   ⚠️ AUDIT FINDING: the SOP already teaches the two-label vocabulary (SOP:1779-1785) and
   tree-not-sha staleness (SOP:40); its pyrefly mentions (:2183, :3347) are about the centre
   having no such tools, not the §6 command form. Expect the SOP body to need no edit —
   `[sop-ok]` with the reason is then the honest path, and the two `docs/` rows in the
   Declared Change Set go unused (declared-but-untouched is the visible, correct record).
6. **Suite via receipt writer** — commit, then
   `gate_receipt.py run --task SCC-305 --gate suite --root _artifacts/_main/2026-08-24_bugs-cycle-8 --cwd <worktree> -- python3 .agents/scripts/tests/run_all.py`.
7. **Mutation sweep** — table drawn FROM the code for the two changed scripts
   (`mutation_sweep.py`, one sweep).
8. **Review gate** — `/smh-code-review`, then walkthrough + `task.yaml` + Dev Record.

## Declared Change Set

- EDIT `.agents/scripts/gate_receipt.py` — bare -q pytest totals pattern; worktree-aware receipts-root resolution for run/check/list → A, H1
- EDIT `.agents/scripts/tests/test_gate_receipt.py` — pins both totals forms + worktree write/read resolution → A, H1
- EDIT `.agents/scripts/link-worktree-assets.py` — write worktree info/exclude on link, clean on unlink → B
- EDIT `.agents/scripts/tests/test_link_worktree_assets.py` — clean-status, unlink-cleanup, real-dirt cases → B
- EDIT `.agents/commands/cicd-dev-story-tests.md` — Step 1 grammar op-first + literal example; Step 5 sixth MANDATORY story-file item + placeholder grep; may→must advance to review → C, G
- EDIT `.agents/commands/smh-quick-dev.md` — grammar op-first at :191; rolling-label prose at :238 → C, H2
- EDIT `.agents/rules/artifacts-always-first.md` — §2 grammar sentence op-first + literal example → C
- EDIT `.agents/rules/code-standards.md` — §6 pyrefly row: interpreter-resolving form → D
- EDIT `.agents/skills/code-review-engine/steps/step-01-review.md` — submodule lens-tree contract + recipe; rolling-label prose at :651 → E, H2
- EDIT `.agents/commands/cicd-code-review.md` — Step 3.1 sha-equality → tree comparison naming same_tree; docs/-invalidates clarification → F
- EDIT `.agents/rules/jira.md` — label row: two-label vocabulary, dual-label lookup, cross-board note → H2
- EDIT `.agents/commands/smh-quick-fix.md` — rolling-label prose at :68 → H2
- EDIT `.agents/workflows/smh-quick-fix.md` — regenerated mirror (sync, not hand-edit) → H2
- EDIT `.agents/workflows/smh-quick-dev.md` — regenerated mirror (sync, not hand-edit) → C, H2
- EDIT `.agents/workflows/cicd-dev-story-tests.md` — regenerated mirror (sync, not hand-edit) → C, G
- EDIT `.agents/workflows/cicd-code-review.md` — regenerated mirror (sync, not hand-edit) → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — only if it names the pyrefly command or the rolling-ticket lookup → D, H2
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line per operator-visible change → D, H2

## Landing-order dependencies

None — `git worktree list` shows no sibling lanes; only the main checkout exists.

## Risks

- Sandbox denial on `.claude/skills` writes may block `/smh-sync-agents` in-session
  (SCC-300) — mitigated in step 4.
- G's "demonstrated, not asserted" acceptance (a story failing the new checklist) is a doc
  checklist, not a script — demonstrated by quoting the 19.5 placeholder case against the
  new grep line, not by running a BMAD lane here.
- D's PC half cannot run from this Mac session — recorded as an operator action, per
  two-machines-mac-and-pc.

## Self-Audit (2026-08-24)

Level: **LEDGER+BLAST** (rules + gate scripts + command surfaces + multi-platform mirrors in
the change set). Mode: PRE-WORK.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  all 18 declared paths exist on disk (ls loop, all OK)
             declared_change_set.py parse -> present: true, 18 entries, 0 incomplete
             both-machines: plan writes python3 and notes PC `python`; stdlib only
             lane fit: no deployable path in the set (.agents/, docs/, workflows only) -> smh door correct
             Scope Ledger: zero op-NEW rows -> no created artefact to justify; acceptance
             list has 8 lettered groups, each with concrete observables (precondition met)
read:        implementation_plan.md; .agents/scripts/tests/ listing; declared_change_set.py parse output
verdict:     clean
```

```
lens:        2 Parity + Blast
checks_run:  script callers: grep .githooks + .agents/scripts for gate_receipt / link-worktree-assets
             SOP co-occurrence: grep SOP for pyrefly + rolling labels
             twins: C fixes cicd+smh+rule sites together; F ports smh->cicd; G names the smh task.yaml check
             sibling worktrees: git worktree list -> only main checkout; no landing-order deps
             risk_seam.py classify -> status unclassified, root "." (correct in the centre, SCC-289)
read:        closeout_preflight.py:25, task_preflight.py:59, main_write_gate.py:81, jira_feed.py:2197
             workflows_testing_SOP.md:40,1763-1785,2183,3347
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  attach-only pass over Lens 2 survivors
read:        (attaches to anchored findings only)
verdict:     findings below (attachments)
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/closeout_preflight.py:25` | `import gate_receipt as gr` | H1's resolution change ripples into close-out, task preflight and the main gate; an API drift here dies on someone else's close-out. Pre-mortem: the NEXT lane's `/smh-close-task-merge-tree` is where it would surface, silently reading the wrong tree. Fix baked into step 2: change confined to `main()` flag resolution, importer-facing functions unchanged, preflight suites green before commit. | medium |
| `docs/_scc_sops_prds/workflows_testing_SOP.md:1779` | `\| running-bug-list \| next cycle, not yet started — this is the trigger \|` | The SOP already teaches H2's vocabulary and (at :40) F's tree-not-sha rule — the two declared docs/ rows are likely no-ops; committing "SOP updates" that change nothing would be noise, `[sop-ok]` with reason is the honest record. Baked into step 5. | low |

### Observations
- `smh-plan-task.md:196` already states the grammar op-first — C2's "every sibling agrees" is
  two fixes plus one verification, not three fixes.
- G's acceptance 2 ("demonstrated, not asserted") is satisfiable by quoting the 19.5
  placeholder against the new grep line — no BMAD lane needs to run here.

Audit verdict: GO
