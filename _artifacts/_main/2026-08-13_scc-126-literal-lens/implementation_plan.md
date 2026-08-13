---
IsArtifact: true
ArtifactMetadata:
  title: SCC-126 — 5th lens (literal-correctness) + capped mode + the AP rewire
  type: implementation_plan
  date: 2026-08-13
---

# SCC-126 — Literal-correctness lens, capped in the autopilot

Parent spec: `_artifacts/_main/2026-08-12_scc-116-house-review-engine/implementation_plan.md` §SCC-126.
Research: `_my_resources/open_tasks/pr-af-dev-system-upgrade.md` Item 2 (`deepen_findings`,
harnesses.py:1524). Lane: `chore/SCC-126-literal-lens` off main @ `36e1ffe`.

**Scope transfer (2026-08-13, operator-approved, recorded on both tickets):** this lane also owns
`.agents/commands/cicd-code-review-AP.md` ENTIRELY — the capped-mode cost governance it always had
AND that command's rewire onto the engine, transferred in from SCC-128 so the three parallel lanes
(126/127/128) touch disjoint files. SCC-128 no longer touches the AP file.

## Why this lens

pr-af's own confession, and it is ours too: a multi-agent architectural review reliably surfaces
high-level findings and **systematically glides over the line-level check** — is the code, as
literally written, correct against the actual definitions of the symbols it depends on? All four
current lenses are high-altitude. Almost every golden a deep review misses is a symbol-level
assumption violation: a called method that does not exist, a wrong-variable argument, a type that
is not the assumed subclass, a nil deref, an invariant that does not hold.

## The work, step by step (each step names the assertion that proves it)

### Step A — RED: pin the lens before it exists
Append cases to `.agents/scripts/tests/test_review_engine.py`, in that file's own discipline
(relationship-binding checks, each shipping a counter-example proven to go red, prohibitions
asserted positively — see its module docstring; a keyword grep is the documented failure mode):
1. step-01 lens table has a **Literal-Correctness Hunter** row whose `How` cell names the hunter
   contract (the cell is the wiring — this is what binds Gates 1–3 to it).
2. The lens spec carries, adjacent and bound: **diff-scoped** (changed lines are the subject;
   repo access is for opening real definitions) · **early-exit on an empty patch set** ·
   **20-file cap** · **context-file spill above ~9,000 chars**.
3. The discipline sentence is present as prompt text (blockquoted): for each changed line,
   identify every external thing the code depends on, open the actual definition, verify the
   assumption holds; exhaustive, not selective; a reasoning discipline, not a bug checklist.
4. **Full vs capped mode is defined in the lens spec, once**: full = interactive callers; capped =
   the caps are mandatory (autopilot). A caller names the mode; it never re-defines the caps.
5. Lens arithmetic: `SKILL.md` and step-01 §skipped-by-mode say a spec-less review reports
   **`4/4`, never `4/5`** (Acceptance Auditor is the only mode-skipped lens; the new lens always
   runs). ⚠️ AUDIT NOTE: the natural red here is the EXISTING case at
   `test_review_engine.py:161` — flip it to pin `4/4` and it fails against the unedited files.
6. Evidence-pack row: the new lens is a repo-access lens → primed **yes** (SCC-125 rule), with the
   pack-is-a-starting-point instruction.
7. ⚠️ AUDIT FINDING (F6): the empty-patch early-exit is recorded as **`ok` with zero findings**,
   never `dead` and never `n/a` — otherwise every empty diff raises `severity_floor` to CONCERNS
   or reads as degraded. A case pins this with its counter-example.
Run `run_all.py` → paste the RED, and read WHICH line raised (a case dying in setup is not a red).

### Step B — GREEN: the lens lands
Edit `.agents/skills/code-review-engine/steps/step-01-review.md`:
- table row + a `## The literal-correctness lens` section: the ported discipline as blockquoted
  prompt text, the four scoping rules, the full/capped mode definition.
- The lens gets: `DIFF` + read access to `REPO` + pack (marked *yes*). Runs `always` (both
  review modes).
Edit `SKILL.md`: the `3/3` sentence becomes `4/4`; nothing else moves.
Re-run the Step A cases green.

### Step C — AP rewire (the transferred scope), one commit with the SOP
Rewrite `cicd-code-review-AP.md` §"The work" onto the engine:
- The AP command becomes a **caller**: it resolves the contract (`REPO`, `WORKTREE`, `DIFF`,
  `HEAD_SHA`, `review_mode`, `STORY_FILE`, `EVIDENCE_PACK` when available) and invokes
  `code-review-engine` with **capped mode named** for the literal lens. Its two-ingest read-budget
  law survives as caller-side input preparation (the diff is Ingest 1; the grounding pull primes
  the pack) — the cost contract is kept, the inline three-lens run is replaced by the engine's
  five.
- ⚠️ AUDIT FINDING (F1): the engine's "subagents unavailable" branch writes prompt files and
  RETURNS — in a headless pipeline that is a review that silently never ran. The AP rewire must
  therefore instruct, caller-side: *if subagents are unavailable in this runtime, run every lens
  inline, sequentially, yourself — never return unrun prompts* (the engine's own dead-lens inline
  path, generalized; "a lens is a prompt, not a privileged tool"). The AP file stops instructing
  a solo three-lens review of its own.
- References to `bmad_code_review_sudo_fix.md` / the vendor skill go to zero **in this file**.
- Everything downstream of the review (TEA gate, walkthrough sections, handoff blocks, verdict
  line) is untouched — the engine returns findings + severity floor; the AP command still owns its
  verdict.
- `docs/_scc_sops_prds/workflows_testing_SOP.md` staged in the SAME commit (sop_currency fires;
  `[sop-ok]` is wrong here — usage genuinely changes).
Assertions: grep for the two vendor spellings over the AP file = 0 hits · `workflow_lint.py
--toolkit-only` exit 0 · `run_all.py` green.

### Step D — sync + full gate
`/smh-sync-agents` (the `.claude/skills/` engine cache and any generated launchers regenerate from
source — never hand-edited). Then the full suite bare (no pipes): `run_all.py`, `workflow_lint.py
--toolkit-only`.

### Step E — stopwatch, on THIS branch, before any SCC-127 content arrives
Re-run the SCC-124 measurement (same SCC-110 diff, same best-of-N protocol from
`_artifacts/_main/2026-08-12_scc-124-baseline-trial/`) with the 5-lens engine. Record wall-clock in
the walkthrough. Bar (ticket text): ≤ the SCC-124 baseline; a miss is a regression to fix **here**,
where it is still attributable to this lens. Ordering is load-bearing: SCC-127's verify wave adds
its own wall-clock, so measuring after a merge from that lane destroys attribution.

## Landing order + cross-lane facts (carried from Step 0.5 sibling scan)
- All three lanes append to `test_review_engine.py` — trivial textual merges, later lanes rebase.
- **SCC-128's resurrection lint needs this lane's Step C landed first**, or its lint goes red on a
  file it may not edit (recorded on SCC-128's ticket).
- `cicd-code-review-AP.md:9` carries `ap_reconciled: <sha>` pinned to `cicd-code-review.md`, which
  SCC-128 rewrites. Whichever lane lands second owes the re-diff + restamp of that frontmatter
  line; for SCC-128 that is the ONE permitted touch of the AP file (frontmatter stamp only, never
  the body). Flagged for the operator at close-out.

## Boundaries
- No noise/worthiness filter anywhere (step-01 §no-noise-filter is the standing answer).
- `_bmad/`-installed and generated files never hand-edited.
- `/cicd-quick-dev` and `/smh-quick-dev` untouched (operator ruling in the parent spec).
- SCC-127's verify wave and SCC-128's caller rewires are NOT this lane's scope — step-02,
  step-03, `cicd-code-review.md`, `smh-code-review.md` are not edited here.

## Self-Audit (2026-08-13)

Mode: PRE-WORK · Right-size: **Full** (a command surface + skill step files + a gated test file).
Repo pinned from command output: `Repo: scc-126-literal-lens | Branch: chore/SCC-126-literal-lens`.

- **Phase 0** — change set named (step-01, SKILL.md, cicd-code-review-AP.md, test_review_engine.py,
  SOP doc, synced caches); checkable list = the 6 statements echoed in-session; traceability holds
  both ways (every statement → a step, every step → a statement); no deployable path in the set.
- **Phase 1** — doors: `cicd-code-review-AP` has NO skill/workflow/opencode door (verified by `ls`,
  all four absent — it is invoked by name from the three `cicd-autopilot-*` command bodies), so the
  only cache work is the engine skill's `.claude/skills/` copy via sync-agents. `ap-twins` lint
  read at `workflow_lint.py:140-169`: staleness is a **WARN**, restamp owed by whichever lane lands
  second (landing-order section). Test discovery is automatic (`run_all.py:20` glob). Sibling
  trees scanned: both empty at audit time; overlap facts recorded in the landing-order section.
- **Phase 2** — no new command, rule, script, or flag; capped mode traces to the ticket text;
  keeping AP's two-ingest read-budget law as caller-side input prep is a documented adaptation,
  not a clone. No tripwire fires.
- **Phase 3** — other machine: no new scripts, suite runs per-machine as today · fresh clone: no
  new hooks · empty input: F6 pins the empty-patch early-exit as `ok`, never `dead` · sibling
  lands first: no file overlap with 127/128 except test appends; plan still applies · rollback:
  revert the lane merge; nothing irreversible in-lane.

| # | Sev | Finding | Disposition |
|---|---|---|---|
| F1 | MED | Engine's no-subagent branch returns unrun prompts — silent no-review in a headless run of the AP command | baked into Step C: caller-side inline-sequential instruction |
| F2 | LOW | `test_review_engine.py:161` pins `3/3` — would go red unflipped | baked into Step A item 5: flipping it IS the natural red |
| F3 | LOW | `ap_reconciled` stamp goes stale-WARN when SCC-128 lands `cicd-code-review.md` | landing-order section; second-lander restamps (frontmatter line only) |
| F6 | LOW | Empty-patch early-exit could be mis-scored as `dead` → CONCERNS on every clean diff | baked into Step A item 7 with counter-example |

Four gates: verification strategy present per step (named command + expected output) · nothing
irreversible in-lane (Jira `start` already ran; devrecord is update-in-place) · vaguest step was
the AP headless behavior — tightened by F1 · conventions anchored (hand-authored skill law, door
model checked, artifacts in `_artifacts/_main/`, SOP-same-commit).

Audit verdict: GO
