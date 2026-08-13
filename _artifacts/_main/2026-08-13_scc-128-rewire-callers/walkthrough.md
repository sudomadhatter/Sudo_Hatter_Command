---
IsArtifact: true
ArtifactMetadata:
  title: SCC-128 rewire callers + retire the bmad-code-review surface — walkthrough
  type: walkthrough
  date: 2026-08-13
---

# SCC-128 — Rewire callers + retire the vendor review surface

**Lane:** `chore/SCC-128-rewire-callers` @ `cd3e16d` (pushed) · plan: [implementation_plan.md](implementation_plan.md)
(carries the `## Self-Audit (2026-08-13)` section, verdict **GO**, operator `approved`).

## Task Checklist

- [x] Step 0/0.5 — repo + branch pinned from `rev-parse`; SCC-128 moved `To Do → In Progress`; sibling
      lanes read (SCC-126 holds `test_review_engine.py` uncommitted, SCC-127 clean — **zero file overlap**)
  - ⚠ **cwd is not intent, again.** The Bash tool's working directory was the **main checkout**, not
    this worktree, while an early `git rev-parse` echo had reported the lane. Edits were unaffected
    (all writes used absolute worktree paths) but two test runs executed `main`'s copy of the suite
    and were therefore evidence about the wrong tree. Caught by `grep -c SCC-128` returning `0` on the
    file I had just edited. `main`'s checkout was verified clean and unmodified before continuing.
- [x] Step 1 — acceptance list fixed (A1–A8 in the plan), every item checkable by a command
- [x] Step 1.5 — plan written, `/smh-self-audit` run (**GO**, 2 findings baked in), operator `approved`
- [x] Step 2 — **RED first**: 7 resurrection-lint cases written before the check existed
- [x] Step 3 — GREEN: lint armed, both callers rewired, adapter rule deleted, `opus-reviewer` rewritten,
      INDEX + SOP + `tea_deep_reference` updated, four in-repo doors regenerated, doc-graph rebuilt
- [x] Step 3f — **6 mutants, 6 killed** (table below)
- [x] AP-twin drift woken by my own edit: `cicd-self-audit-AP.md` diffed and reconciled
  - ⛔ `cicd-code-review-AP.md` is SCC-126's under the operator-approved scope transfer — **not touched**,
    and it is the single cause of both red gates below

## Evidence

Suite measured at **`cd3e16d`**; no code or test change after it.

### A1 · `/cicd-code-review` Step 1 invokes the engine

`.agents/commands/cicd-code-review.md` Step 1 now names `code-review-engine` and supplies the full
caller contract as a table (`REPO · WORKTREE · DIFF · HEAD_SHA · review_mode · STORY_FILE ·
ARTIFACT_DIR · DEFERRED_WORK`). The inline four-point subagent-failure contract collapses into the
engine's own per-lens contract, with the returned `severity_floor` stated as **binding** on Step 4
(floor or worse, never better). Proof: `grep bmad-code-review` on the file returns nothing, and the
armed lint (A6) would ERROR if it did.

### A2 · `/smh-code-review` Step 1 invokes the engine

Was `bmad-review-adversarial-general` — a single adversarial lens. Now the same engine, so the Task
lane gains the Edge-Case, Acceptance and Test-Adequacy lenses. `review_mode: full` binds the task's
`implementation_plan.md` as the spec, which is what makes the Acceptance lens meaningful here. Step 2
gained a **no-double-audit** clause mirroring the existing Step 3.5 convention: import the lens's
findings, keep the item→assertion matrix as the command's own.

### A3 · the adapter rule is deleted

`.agents/rules/bmad_code_review_sudo_fix.md` removed (`git rm`); its `rules/INDEX.md` row removed.
`grep bmad_code_review .agents/rules/INDEX.md` → no match.

### A4 · `opus-reviewer.md` rewritten onto the engine

Doctrine source is now `code-review-engine/SKILL.md` + `steps/step-01-review.md`, run solo-sequential.
It gains the **fourth pass (Test-Adequacy)** and the three finding gates, with the auditor exemption
stated (a reachability proof is unwritable for a finding whose subject is absent). Its autopilot
interface is unchanged: same story-file sections, same artifact mirror, same "never flip to done" —
now cited to the engine's own boundary section rather than to a deleted rule.

### A5 · SOP + INDEXes current, in the same commit

`workflows_testing_SOP.md` ③ diagram names the engine and the contract it is passed; its `smh-` diagram
names the engine too; "review layer" → "review lens" in the CONCERNS row. `tea_deep_reference.md` (3
places) updated because it documents this exact command chain and would otherwise be factually wrong.
Gate proof — the change set **without** the SOP is refused, **with** it passes:

```
$ python3 .agents/scripts/sop_currency.py --paths ".agents/commands/cicd-code-review.md" --message "..."
  x The SOP quick-reference was not updated with this change.   → exit 1
$ python3 .agents/scripts/sop_currency.py --paths ".agents/commands/cicd-code-review.md" \
      "docs/_scc_sops_prds/workflows_testing_SOP.md" --message "..."
  → exit 0
```

`tea_testing_guide.md` and `tdad_stack_install_guide.md` are **deliberately left** — closed-initiative
history, out of the guard's scope. Recorded so the choice reads as a decision, not an oversight.

### A6 · the resurrection lint — RED first, then GREEN

**RED** (the check did not exist; the run died at the call, and the traceback names why — not an
assertion failing for an unrelated reason):

```
File ".../test_workflow_lint.py", line 431, in res_report
    lint.check_retired_review_surface(root, r)
AttributeError: module 'workflow_lint' has no attribute 'check_retired_review_surface'
```

**RED on the live tree** once the check existed — case F listing every surface still to clean:

```
[FAIL] SCC-128 F no command or rule outside SCC-126's AP file resurrects it:
  ['INDEX.md', 'artifacts-always-first.md', 'bmad_code_review_sudo_fix.md',
   'cicd-code-review-AP.md', 'cicd-code-review.md', 'cicd-self-audit.md']
```

**GREEN** after the sweep — only SCC-126's file remains:

```
[PASS] SCC-128 A positive control: a clean toolkit is silent
[PASS] SCC-128 B a command naming the vendor skill is an ERROR
[PASS] SCC-128 C the underscore form (the retired rule) also fires
[PASS] SCC-128 D an INDEX row pointing at a retired surface fires
[PASS] SCC-128 D2 a nested skill file routing to the vendor skill fires
[PASS] SCC-128 E the error names the replacement engine
[PASS] SCC-128 F no command or rule outside SCC-126's AP file resurrects it: ['cicd-code-review-AP.md']
-- 44/44 passed --
```

**Scope widened by one surface, with evidence.** The plan said commands + rules; the guard also scans
`.agents/skills/` because that is the door Claude and Codex actually enter through (SCC-66), and the
skills router carried a live reference. Checked before widening: **no vendor `bmad-*` skill lives
under `.agents/skills/`**, so the guard is satisfiable rather than permanently red. Case D2 asserts it.

**Both spellings are caught on purpose.** `bmad-code-review` is the skill; `bmad_code_review_sudo_fix`
is the deleted rule — and the underscore form is the half that survives as a **dangling file path an
agent is told to open**, which is precisely the live break described under "Landing order".

### A6b · mutation check — 6 mutants, 6 killed

A check that has never failed proves nothing, so each mutant was required to be killed by the specific
case that owns that property. The positive control (A) stayed green in every run — it is a real
control, not a passenger.

| # | Mutation | Killed by |
|---|---|---|
| M1 | the check body returns immediately (no-op) | B, C, D, D2, E |
| M2 | regex narrowed to `bmad-code-review` (hyphen only) | C, D — the underscore/rule spelling |
| M3 | `skills` dropped from the scanned surfaces | D2 |
| M4 | `rglob` → `glob` (non-recursive) | D2 — the nested `SKILL.md` |
| M5 | `rep.err` → `rep.warn` (a gate that cannot block) | B, C, D, D2 |
| M6 | the remedy stripped from the message | E |

### A7 · the AP file is untouched

```
$ git diff --name-only main...HEAD | grep -c "cicd-code-review-AP.md"
0
```

### A8 · floor — and the two red gates, both from one cause

| Gate | Result @ `cd3e16d` |
|---|---|
| `run_all.py` | **20/21 files** — `test_workflow_lint.py` fails on SCC-82 case G (see below). Case total **1335 → 1342**, exactly additive: my 7 cases, nothing displaced |
| `workflow_lint --toolkit-only` | **exit 2** — 1 ERROR (my own lint, firing correctly on `cicd-code-review-AP.md`), 1 WARN (that twin's stamp now stale) |
| `check_maps --depth3-only --strict` | **exit 0** |
| `sop_currency` | **exit 0** with the SOP staged (both directions shown above) |
| the Step 2 RED assertions | **GREEN** (44/44 in that file) |

## ⛔ The blocker, and why it is not papered over

**One root cause:** the operator-approved scope transfer moved `cicd-code-review-AP.md` to SCC-126,
and that file both (a) references the retired vendor surface and (b) carries an `ap_reconciled` stamp
naming a sha of `cicd-code-review.md` that my rewire superseded. This lane may not edit it, so both
symptoms are structurally unfixable from here:

1. **`workflow_lint` ERROR** — my own guard firing on that file. Predicted by the ticket. The
   exemption lives in the **test**, never in the linter, so the violation stays visible at every gate
   instead of being silently allowed.
2. **`run_all.py` red — SCC-82 case G, two assertions:**
   - *"the live repo's AP twins report nothing"* — the twin's stamp is stale because I moved its
     primary. **This is the drift check working correctly**, not a flake.
   - *"only the twin that was actually diffed carries a stamp"* — a hard-coded list of exactly one
     filename. My legitimate reconciliation of `cicd-self-audit-AP.md` (diffed, nothing to port,
     reason written into its frontmatter) makes the list two. The assertion pins an **identity**, not
     the property it means to protect.

**Not papered over, deliberately.** Restamping `cicd-code-review-AP.md` would be a lie in the exact
shape SCC-82 case D was built to catch — the stamp claims *"I read the primary and there is nothing to
port"*, and there **is** something to port: the engine rewire, which is SCC-126's work. Weakening
case G would hide a real staleness. So the red stands and is reported.

**The remedy, owned:** when SCC-126 lands its AP rewire it must also **restamp `ap_reconciled` to
`024f58a`** (or drop the stamp) — otherwise both lanes land and `main` is red. Because their AP commit
will necessarily be dated after mine, the timestamp path then resolves on its own; it is the *stamp*
that needs the explicit action. Case G's second assertion needs one line updated to include
`cicd-self-audit-AP.md`; it is another ticket's test, so it is **not** changed here on my own judgment.

## Decisions taken while building

- **`-NoGlobals` on the sync.** The full sync writes the operator's machine-global opencode,
  Antigravity and Codex menus. Running it from an unmerged lane would install unreviewed command
  bodies system-wide, before review and before merge. The in-repo doors (which ride the branch and are
  what door-parity gates) were regenerated; the globals refresh when this lands and is synced from
  `main`.
- **`[sop-ok]` used once**, on the AP-twin reconciliation commit only — a frontmatter note on a
  headless autopilot command the operator never types. The rewire commit itself carries the SOP.
- **The memory store was not touched.** `_artifacts/_memory/story-status-flip-contract.md` names the
  deleted rule as "the sanctioned override" and goes stale with this lane, but the store is read-only
  outside its own flows. Logged as a follow-on.

## Your Actions

- [ ] **Rule the landing order.** Recommended: **SCC-126 lands first** — merging this lane first would
      leave the AP autopilot instructed to read a rule file that no longer exists. Either order merges
      cleanly in git; this is about behavior, not conflicts.
- [ ] **Pass SCC-126 the restamp requirement** (`ap_reconciled: 024f58a`, or drop the stamp) — without
      it, `main` is red once both lanes land.
- [ ] Say whether I may update SCC-82 case G's stamped-twin assertion (one line) or whether that goes
      to SCC-126 / a follow-on.
