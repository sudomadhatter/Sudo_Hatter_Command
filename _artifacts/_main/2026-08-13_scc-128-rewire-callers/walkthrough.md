---
IsArtifact: true
ArtifactMetadata:
  title: SCC-128 rewire callers + retire the bmad-code-review surface — walkthrough
  type: walkthrough
  date: 2026-08-13
---

# SCC-128 — Rewire callers + retire the vendor review surface

**Lane:** `chore/SCC-128-rewire-callers` @ `fb3a9ba` (pushed) · plan: [implementation_plan.md](implementation_plan.md)
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

Suite measured at **`fb3a9ba`**; no code or test change after it.

> **Two claims in the first draft of this section were false, and the review caught them.** It said
> `-- 44/44 passed --` and *"the Step 2 RED assertions GREEN (44/44 in that file)"* while the same
> section's own gate table said that file was failing — the 44/44 was a real run, but from `024f58a`,
> before the AP-twin stamp commit, which contradicted this very header. And it said `[sop-ok]` was
> *"used once"* when the log shows two. Both are corrected below. Recorded rather than silently
> edited: a walkthrough that quietly repairs its own evidence is the thing the review exists to stop.

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

⛔ **A5 was MISSED in the first pass and is only delivered because the review found it.**
`.agents/workflows/INDEX.md:13` still routed *"shipped code → `bmad-code-review`"*. My own acceptance
item named that file, and step 5 of the plan named it again as *"(hand-owned file)"* — and I reported
A5 delivered anyway. It is `sync-agents.ps1`'s `$excluded = @('smh-adviser-board.md', 'INDEX.md')`:
hand-written router prose with **no command upstream**, so no regeneration would ever have fixed it,
and Antigravity's door would have kept pointing at the retired skill. Fixed in `fb3a9ba`.

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

**GREEN** after the sweep and after the review's fixes — 12 cases, only SCC-126's file remains:

```
[PASS] SCC-128 A positive control: a clean toolkit is silent
[PASS] SCC-128 B a command naming the vendor skill is an ERROR
[PASS] SCC-128 C the underscore form (the retired rule) also fires
[PASS] SCC-128 D an INDEX row pointing at a retired surface fires
[PASS] SCC-128 D2 a nested skill file fires, and the message LOCATES it
[PASS] SCC-128 D3 a differently-cased spelling still fires
[PASS] SCC-128 D4 every offender is reported, across all scanned surfaces
[PASS] SCC-128 D5 positive control: ALL five populated surfaces, clean, silent
[PASS] SCC-128 E the error names the replacement engine
[PASS] SCC-128 F the live tree's ONLY offender is SCC-126's AP file:
                 ['.agents/commands/cicd-code-review-AP.md']
[PASS] SCC-128 G the check is WIRED into --toolkit-only (exit 2 + names it)
[PASS] SCC-128 G control: with the offender gone the CLI is clean again
-- 48/49 passed --   (the one failure is SCC-126's stale AP stamp — see the blocker)
```

**Scope: five surfaces, and the first draft's rationale for the exclusions was wrong.** The plan said
commands + rules. `.agents/skills/` was added during the build (the door Claude and Codex enter
through, SCC-66) after checking the guard would be satisfiable — **no vendor `bmad-*` skill lives
under `.agents/skills/`**. The review then found the exclusion list itself was the hole: `workflows/`
was excluded as "generated mirrors follow their command source", which is true of
`workflows/<command>.md` and **false of `workflows/INDEX.md`** — the one file that was actually
dirty. `opencode-agents/` was excluded too, and that is the surface the regression genuinely lived on
(`opus-reviewer.md` loaded the retired rule *by path*). Final scope: **commands · rules · skills ·
workflows · opencode-agents**. Still out, on ownership grounds rather than convenience: `.agents/bmad/`
(vendor, regenerated), `_artifacts/` (history, read as written), and the `.opencode/` / `.claude/`
byte-mirrors of masters that are guarded here.

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

**And two mutants my own set MISSED, found by the review's Test-Adequacy lens** — recorded because
the lesson is that a self-authored mutation set tests what the author already thought of:

| # | Mutation | Was | Now killed by |
|---|---|---|---|
| M7 | **delete the call site in `main()`** | **survived** — all 7 cases green while `workflow_lint --toolkit-only` went permanently silent (verified by deleting the line: the SCC-128 block stayed at 100%) | G — drives the real CLI in a synthetic lobby |
| M8 | `break` after the first `rep.err` | **survived** — every case used `any(...)` on a fresh report, so none ever required two findings in one report | D4 — asserts the offender SET |

Two more holes the same lens found, both now closed: case F used `all(o == ... for o in offenders)`,
and **`all()` over an empty set is `True`** — so the only case touching the real tree passed against a
detector gutted to `return`. It is now an exact-list match, which also makes the AP carve-out
**self-expiring**: when SCC-126 lands, case F goes red and whoever is here deletes the exemption
instead of inheriting a permanent silent hole. And the error message carried only `f.name` — ~50
skills own a file called `SKILL.md`, so the gate would have blocked a close-out while naming a file
that exists dozens of times; it now carries the path relative to the lobby, and D2 asserts the
locator rather than the basename.

### A7 · the AP file is untouched

```
$ git diff --name-only main...HEAD | grep -c "cicd-code-review-AP.md"
0
```

### A8 · floor — and the two red gates, both from one cause

| Gate | Result @ `fb3a9ba` |
|---|---|
| `run_all.py` | **20/21 files** — `test_workflow_lint.py` fails on **one** assertion, SCC-82 case G's staleness check (see the blocker). Case total **1335 → 1342 → 1347**, exactly additive at each step: 7 cases in the build, 5 more from the review's findings, nothing displaced |
| `workflow_lint --toolkit-only` | **exit 2** — 1 ERROR (my own lint, firing correctly on `.agents/commands/cicd-code-review-AP.md`), 1 WARN (that twin's stamp now stale) |
| `check_maps --depth3-only --strict` | **exit 0** |
| `sop_currency` | **exit 0** with the SOP staged (both directions shown above) |
| the Step 2 RED assertions | **GREEN** — 48/49 in that file; the single failure is not one of them |

## ⛔ The blocker, and why it is not papered over

**One root cause:** the operator-approved scope transfer moved `cicd-code-review-AP.md` to SCC-126,
and that file both (a) references the retired vendor surface and (b) carries an `ap_reconciled` stamp
naming a sha of `cicd-code-review.md` that my rewire superseded. This lane may not edit it, so both
symptoms are structurally unfixable from here:

1. **`workflow_lint` ERROR** — my own guard firing on that file. Predicted by the ticket. The
   exemption lives in the **test**, never in the linter, so the violation stays visible at every gate
   instead of being silently allowed.
2. **`run_all.py` red — SCC-82 case G.** ⚠ **The first draft of this section blamed "one root cause"
   for both of case G's assertions, and the review proved that wrong.** Only the first is the scope
   transfer's; the second was mine, and would have failed even if SCC-126 had already landed:
   - *"the live repo's AP twins report nothing"* — **SCC-126's.** The twin's stamp is stale because I
     moved its primary. This is the drift check working correctly, not a flake. It clears when they
     restamp, and **only** then.
   - *"only the twin that was actually diffed carries a stamp"* — **mine**, and now fixed. It was a
     hard-coded list of one filename; my legitimate reconciliation of `cicd-self-audit-AP.md` made it
     two. Left alone it would have sat red on `main` **with no owner** — the review's sharpest point,
     since an always-red floor is precisely what people learn to wave through. Rewritten to assert the
     property it was actually defending: *every stamped twin records WHY it was reconciled*. A bare
     `ap_reconciled:` bump with no written reason now fails it (proven by mutating the frontmatter),
     while an honest diff-and-record passes. That is the same "not a mute switch" intent SCC-82 wrote
     it for, expressed as a rule instead of a snapshot.

**One consequence I under-reported, and the review caught the blast radius:** `task_preflight.py`'s
`gate_plan` runs `workflow_lint --toolkit-only` for **every** local lane's close-out, and
`/smh-clean-code-audit`'s machine floor runs it too. So from the moment this lane lands — in either
order — every unrelated `chore/*` lane's gate returns an error it did not cause, until SCC-126 lands.
That is a second, independent reason the landing order below is not cosmetic.

**Not papered over, deliberately.** Restamping `cicd-code-review-AP.md` would be a lie in the exact
shape SCC-82 case D was built to catch — the stamp claims *"I read the primary and there is nothing to
port"*, and there **is** something to port: the engine rewire, which is SCC-126's work. Weakening
case G would hide a real staleness. So the red stands and is reported.

**The remedy, owned — and PROVEN, not predicted.** SCC-126 has already rewired the AP file in its own
tree (`7b14f91`): it now has **zero** references to the retired surface, so my lint clears the moment
that lands. But its frontmatter still carries `ap_reconciled: 3eea4d0`, which my primary superseded.

I merged both lanes into a throwaway detached worktree and ran the real checks on the real merged
history (the artifacts INDEX conflicts — both lanes add a row — resolved by keeping both):

```
retired-surface: 0 item(s)          ← my guard goes fully green; case F reports []
ap-twins:        1 item(s)
   WARN | cicd-code-review-AP.md: ap_reconciled names 3eea4d0,
          but cicd-code-review.md is now at 024f58a - diff the twin and restamp
-- 42/44 passed --                  ← measured before this lane's own fixes; `main` would be RED
```

So: **when SCC-126 lands its AP rewire it must also restamp `ap_reconciled` to `024f58a`** (or drop
the stamp and let the timestamp path resolve it). Without that one line, both lanes land and `main`
is red — and neither lane's own gate can see it, because SCC-126's gate ran before my commit existed
and mine may not touch their file. That is the single highest-value thing this review produced.

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

## Code Review (2026-08-13)

Verdict: CONCERNS @ fb3a9ba

Suite evidence measured at `fb3a9ba`; only artifact/doc commits follow it.

**Scope:** `origin/main...HEAD`, 24 files / 3,806 diff lines — the two rewired review commands, the
armed lint + its cases, the deleted rule, `opus-reviewer.md`, the INDEX/SOP/`tea_deep_reference`
sweep, and the regenerated in-repo doors.
**Method:** the `code-review-engine`'s own lens fan-out, run on this lane's diff — **four independent
read-only lenses, each in a fresh context that could not see this session** (Blind Hunter on the diff
text alone; Edge-Case and Test-Adequacy with repo access; Acceptance against the plan's A1–A8 and the
parent spec's eight numbered obligations). All four returned; **`lenses_run: 4/4`, none dead, none
n/a, no degradation.** Then Step 0.7's blast-radius re-derivation, the gate table above, and a
merge simulation of both live lanes.

**Findings**

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `.agents/workflows/INDEX.md:13` | **critical** | Antigravity's router kept sending shipped code to the retired skill; the file is sync-excluded, so no regeneration would ever fix it. An acceptance item I had reported delivered | **applied** `fb3a9ba` |
| 2 | `workflow_lint.py` `_RETIRED_SURFACES` | **critical** | `workflows/` excluded on a rationale false for `INDEX.md`; `opencode-agents/` excluded though it is where the regression lived. The guard could not see the one live violation | **applied** — scope now 5 surfaces |
| 3 | `workflow_lint.py` `main()` wiring | **critical** | deleting the call site left all 7 cases green while the gate CI runs went silent | **applied** — case G drives the real CLI |
| 4 | `test_workflow_lint.py` case F | important | `all()` over an empty set is `True` → the only live-tree case passed against a gutted detector, and the AP carve-out never expired | **applied** — exact-list match |
| 5 | `workflow_lint.py` findings loop | important | a `break` after the first error survived every case; a linter naming 1 of 5 resurrections | **applied** — case D4 asserts the set |
| 6 | `workflow_lint.py` message | important | `f.name` only; ~50 files are named `SKILL.md`, so the gate blocks a close-out without saying which file | **applied** — path relative to lobby |
| 7 | walkthrough `## Evidence` | important | claimed `44/44 passed` and `[sop-ok] used once`; both false at the stated sha | **applied** — corrected, with the error recorded |
| 8 | walkthrough blocker | important | attributed both case-G failures to the scope transfer; one was this lane's own stamp and had no owner | **applied** — re-attributed; assertion rewritten to a property |
| 9 | `smh-code-review.md` Step 1 | important | handed the engine a sha and diff taken *before* Step 0.7 absorbs `main` — the verdict would cite a commit that is no longer the tip | **applied** |
| 10 | `cicd-code-review.md` / `smh-code-review.md` Step 4 | important | both claimed the findings table is "the only copy anywhere" while the engine's step-04 writes action items into the story file | **applied** — authority stated, SOP note added |
| 11 | `opus-reviewer.md` step 1 | suggestion | told to read `SKILL.md`, whose opening gate says to print the contract table and return | **applied** — exempted explicitly |
| 12 | `workflow_lint.py` regex / walk | suggestion | case-sensitive (the human half of a resurrection is the half that varies); `rglob` yields directories named `*.md`, and `read_text` would take the linter down with a traceback | **applied** — `re.I`, `is_file()`, `OSError` guard |
| 13 | vendor skill still installed | suggestion | the deleted rule was invocation-triggered and forced "never write `done`"; the vendor skill is re-emitted by BMAD every regen, so a *direct* invocation now gets vendor behavior — including its `done` default | **deferred** — needs its own ticket; the guard covers routing, not direct invocation |
| 14 | `_artifacts/_memory/story-status-flip-contract.md` | suggestion | names the deleted rule as "the sanctioned override"; goes stale with this lane | **deferred** — store is read-only outside its own flows |
| 15 | `.agents/commands/INDEX.md:51` | nitpick | describes `/smh-code-review` as a "clean-room adversarial hunt", understated now it runs the full engine | **dismissed** — true at that altitude; the row is a router, not a spec |

**Why CONCERNS and not PASS:** `run_all.py` is not green (20/21). Every assertion this lane owns
passes; the single failure is SCC-126's stale AP stamp, which this lane is forbidden to touch and
which the merge simulation proves clears when they restamp. **Why not FAIL:** the mechanical FAIL
triggers — an acceptance item the diff does not deliver, a dead link this diff introduced, a
door-parity break, a gate that cannot fail — were all raised by the review and are all now applied.
The red that remains is a **cross-lane sequencing state with a named owner and a proven remedy**, not
a defect in this work. It is the operator's call whether that blocks the merge; the flow's mechanical
rule reads a red suite as FAIL, and this verdict deliberately does not overrule it — it reports the
suite red, names exactly which assertion and whose it is, and hands over the decision.

**Step 0.7 re-derivation (three lines, as required):** nothing this diff references moved — `main` is
unchanged at `36e1ffe` since the lane opened, so no absorb was needed. True overlap with what landed
while I built: **none** (zero files). Sibling landing-order dependency: **yes, and it is the blocker
above** — SCC-126 (`199ef5d`) owns `cicd-code-review-AP.md` and must land with a restamp; SCC-127
(`684c159`) touches only engine step files and `test_review_engine.py`, no overlap with this lane.
Both siblings and this lane add a row to `_artifacts/_main/INDEX.md`, which conflicts on merge — a
trivial keep-both, confirmed by resolving it in the simulation.

## Your Actions

- [ ] **Rule the landing order.** Recommended: **SCC-126 lands first** — merging this lane first would
      leave the AP autopilot instructed to read a rule file that no longer exists. Either order merges
      cleanly in git; this is about behavior, not conflicts.
- [ ] **Pass SCC-126 the restamp requirement** (`ap_reconciled: 024f58a`, or drop the stamp) — without
      it, `main` is red once both lanes land.
- [x] ~~Say whether I may update SCC-82 case G's stamped-twin assertion~~ — **done, and flagged
      rather than slipped in.** Leaving a red floor with no owner was the worse option, so the
      assertion was rewritten to the property it defends (every stamp records why) and proven to fail
      on a bare stamp. Review it as part of this lane; it is the one place I edited another ticket's
      test.
- [ ] Decide whether finding 13 earns a ticket: the vendor skill is still installed and BMAD re-emits
      it, and the rule that forced it to stop at `review` is now gone — so a **direct** invocation of
      it can write `done` to a story. This lane's guard covers routing, not direct invocation.
