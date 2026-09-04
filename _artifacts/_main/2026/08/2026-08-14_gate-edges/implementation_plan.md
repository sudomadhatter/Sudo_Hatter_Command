# SCC-154 — Gate follow-ons: check_gate verdict resolution + receipt edges (SCC-146) and the incident class in the merge gates (SCC-149)

**Lane:** `chore/SCC-154-gate-edges` (worktree `.claude/worktrees/gate-edges`, cut from `main` @ `21da58b`)
**Ticket:** SCC-154 — ONE combined ticket by the operator's explicit ruling ("lets do one ticket with both of them").
**Sources of record:** the SCC-146 review (`_artifacts/_main/2026-08-14_gate-receipts/walkthrough.md`, Verdict: CONCERNS @ 732f0726, findings 1–17 + compounds C1–C6) and the SCC-149 review (`_artifacts/_main/2026-08-14_incident-taxonomy/walkthrough.md`, Verdict: PASS @ 4fa5596, findings 2/3/5/12/13 + compounds C1/C3 + the dev session's concurrent-wave items).

Both reviews ordered their fixes and both orders are LOAD-BEARING. This plan preserves them: within each
cluster, the pinning tests land (and are committed) BEFORE the behavior change they protect.

## Sibling lanes

`git worktree list` at lane-open: main checkout only. No sibling lanes, no file-overlap dependencies.
(SCC-38 may open in parallel per the operator — assessment-phase, disjoint file set; whichever lands
second absorbs main first.)

## Acceptance (checkable)

1. **B-refuse:** a real `git merge` of `claude/incident-x` into a `claude/SCC-*` or `chore/*` target (and the reverse) is REFUSED by the armed guard; `main <- claude/incident-x` and `claude/incident-x <- main` stay allowed-with-note. Proven by new cases in `test_git_hooks.py` driving real git — the four refuse pairs seen RED first (today they fall to `unknown` → allow).
2. **B-note:** the incident allow-note no longer prints "outside the branch model" — new case asserts the note names the pipeline AND that string is ABSENT. RED first.
3. **B-backstop:** a pushed `refs/heads/claude/incident-*` ref through the real pre-push dispatcher is never refused and never receives story-lane instructions; a story/chore push carrying an unlanded incident branch names `main` + the pipeline in its remedy, never "its epic/* branch". RED first (today: epic-remedy misroute). Existing G2 pin ("its epic/* branch" for story lanes) must stay green.
4. **B-pins (land FIRST, before 1–3):** target-side INC absorb (`claude/incident-x <- main` allowed + note), case N gains `"/cicd-mobile-error-team" not in out`, a positive pin on the story-destination wording, `claude/incident-` (empty suffix) classifies incident, `claude/INCIDENT-x` classifies story, one sha carrying incident + story names vs `main` REFUSES (unknown ≠ allow). Characterization-green where today's behavior is already correct — declared as such.
5. **B-boot:** `cicd-boot-sprint-memory.md` closing condition reads "empty after setting aside `claude/incident-*` matches"; mirrors regenerated via sync-agents.
6. **A-killers (land FIRST):** conjunct-killer cases in `test_task_preflight.py` pinning today's CORRECT behavior: bad-existing-receipt (result=fail · dirty-with-non-artifacts-dirt · unreadable JSON), verdict-fresh/receipt-STALE, unknown-verdict-sha (warn + full plan), CONCERNS allow-half, WAIVED branch, `--json` gate field. NO pin of today's `any(FAIL)` multi-stamp semantics (review verifier id 33: pinning it would cement defect #1). Characterization-green, declared.
7. **A-resolution:** verdicts pool ONLY from governing walkthroughs — hits whose sibling `task.yaml` declares `task_key: <expect-key>`. Foreign/substring hits (SCC-14 ⊂ SCC-146; content-mention walkthroughs) can neither grant a SKIP nor block. >1 stamped governing walkthrough → no SKIP (info). Within the one governing walkthrough the LATEST stamp governs: FAIL-then-PASS is SKIP-eligible, PASS-then-FAIL exits 2. All four directions RED/GREEN-proven (FAIL-then-PASS and foreign-pool RED first — today any(FAIL) wedges and foreign stamps pool).
8. **A-skip-scope:** on SKIP, ONLY the `run_all.py` entry is replaced by the SKIP line; `workflow_lint` and `check_maps` entries still print. RED first (fixture with all three plan files: today SKIP replaces the whole plan).
9. **A-root-mode:** `gate_receipt.py run --root` without `--cwd` dies with a message naming the requirement (RED: today it runs the gate inside the artifacts dir and records `fail` for a suite that never ran); a relative `--root` resolves against `--cwd` when given (RED: today against invoker cwd); `--project` + `--root` together die (mutually exclusive, finding 13).
10. **A-nearmiss+fence:** a verdict-looking line at line start that fails the canonical regex (e.g. `**Verdict: FAIL @ sha**`) in a GOVERNING walkthrough → `rep.err`, exit 2 (RED: today demotes to info + full gate). A canonical stamp inside a ``` fence is ignored for both scans (RED: today a fenced col-0 FAIL blocks). The indented-decoy line and table/bullet prose still never match (existing pins stay green).
11. **A-unify+dirt:** `check_gate` reads receipt result-validity through a shared `gate_receipt` helper (landed strictly AFTER acceptance 6's tests — C3); the receipt records `dirty_paths` (additive field, recorder stays strict) and `check_gate` exempts `_artifacts/`-only dirt while non-artifacts dirt still refuses (RED for the exemption; killer pin for the non-artifacts half).
12. **A-docs:** `smh-code-review.md` Step 3 inherit bar reads pass-or-warn (finding 11) and drops "doc-only" (finding 12, both texts — the `nonartifact_moved` docstring too); close-out command + SOP flowchart state the new SKIP shape (suite spared, artifact-scoped checks still run); finding 15's per-machine question recorded as a DECISION (traveled receipts stand; the unarmed-clone case blocks via `hooks_armed` errors feeding the errs-guard).
13. **Gate:** `run_all.py` green bare (exit 0), `workflow_lint.py --toolkit-only` 0/0, `check_maps.py --depth3-only --strict` exit 0; both mutation sweeps (one pass each, mutants drawn FROM the shipped code, restore-from-copies, application verified) all KILLED by their NAMED cases.

## Steps

### Phase B (SCC-149 cluster) — order binding per C3
- **B0 (tests first):** acceptance 4's pins + de-literalize the `:47` comment in the INC block. Commit.
- **B1:** judge-arm narrowing in `merge-target-guard.sh`: `story:incident|chore:incident|incident:story|incident:chore) refuse` ABOVE the `incident:*|*:incident) unknown` wildcard (first-match order is load-bearing — same lesson as the classify arm); `destination()` gains an incident row; RED cases from acceptance 1 first, then the edit.
- **B2:** note replacement (acceptance 2): in the named-unjudged branch, INCIDENT_SEEN prints the pipeline note INSTEAD of the generic line; the no-name branch keeps its wording.
- **B3:** backstop (acceptance 3): `refs/heads/claude/incident-*` case arm ABOVE `refs/heads/claude/*` — note + `continue`, never judged; `integration_of()` gains `claude/incident-*` → "main (via the incident pipeline — /cicd-mobile-error-team)" ABOVE `claude/*`.
- **B4:** boot text (acceptance 5).
- **B-sweep:** declared mutants drawn from the changed sh: (M-B1) delete the four-pair refuse arm; (M-B2) reorder it BELOW the wildcard (dead code); (M-B3) revert the note replacement (generic prints alongside); (M-B4) widen the backstop incident arm to `refs/heads/claude/*`; (M-B5) delete `integration_of`'s incident row; (M-B6) widen classify's incident arm to `*incident*`. Each row names its killing case before the sweep runs.

### Phase A (SCC-146 cluster) — order binding per C2/C3
- **A0 (killers first):** acceptance 6's cases. Commit BEFORE any source change.
- **A1:** resolution (acceptance 7): `check_gate` gains `expect`; governing filter via the sibling `task.yaml`'s `task_key` (`manifest_field`, already in this file); fence-strip helper applied before all verdict scans; near-miss detector on governing texts only (acceptance 10); latest-stamp-governs replaces `any(FAIL)`. RED cases first, one commit for tests, one for the change.
- **A2:** SKIP scope (acceptance 8): `main()` swaps only the `run_all.py` plan entry.
- **A3:** root-mode hardening (acceptance 9) in `gate_receipt.py` argparse/main.
- **A4:** shared validity helper + `dirty_paths` recording + reader-side exemption (acceptance 11) — strictly after A0.
- **A5:** doc alignments (acceptance 12) — command docs + SOP in the same commits as their surfaces.
- **A-sweep:** declared mutants drawn from the changed python: (M-A1) governing filter removed (pool = all hits); (M-A2) latest-stamp reverted to any(FAIL); (M-A3) >1-governing guard deleted; (M-A4) fence-strip removed; (M-A5) near-miss detector deleted; (M-A6) SKIP-plan swap reverted to `[skip]`; (M-A7) `--cwd` requirement removed; (M-A8) dirt exemption widened to ANY dirt. Each row names its killer.

### Close
- SOP flowchart + scripts/INDEX.md rows in the same commits as their surfaces; `_artifacts/_main/INDEX.md` ledger row; walkthrough + task.yaml; sync-agents regeneration; suite receipt stamped through the receipt writer on a clean tree; `/smh-code-review`; `/smh-close-task-merge-tree` (the operator's "we need this finished" is this ONE merge's sign-off, recorded in the walkthrough).

## Risks / pre-mortem
- **The A1 semantics change flips a live behavior:** a foreign-walkthrough FAIL no longer blocks. Deliberate (finding 2's whole point — foreign verdicts must not gate this lane) and the real flow always has a governing task.yaml (quick-dev Step 5 mandates it), where FAIL still exits 2. Pinned both ways.
- **Existing fixtures must keep passing through A1:** `make_repo` already writes `task.yaml` (`task_key: SCC-11`, correct branch) beside ADIR — verified before planning; the governing filter binds to it unchanged.
- **G2's epic-remedy pin vs B3:** `integration_of` keeps the `claude/*` story arm intact below the new incident arm; G2 stays green or the sweep's M-B5 aim is wrong.
- **sh `case` first-match:** both new arms sit above the globs that would swallow them; M-B2 exists precisely to prove the order is asserted, not assumed.
- **Fence-strip could eat legitimate stamps** if a walkthrough has an UNCLOSED fence: the tail is dropped → no verdict → full gate runs. Fail-toward-running; documented in the helper.

## Self-Audit (2026-08-14)

Mode: PRE-WORK. Repo: Sudo_Hatter_Command | Branch: chore/SCC-154-gate-edges (from rev-parse).
Plan: this file. Ticket: SCC-154. Right-size: **FULL** (gates + hooks + scripts other scripts import).

**Phase 0 — traceability:** every plan step traces to an acceptance item (1–13) and every acceptance
item has a step; no deployable path in the change set (`.agents/`, `docs/`, `_artifacts/` only) — the
lane is LOCAL. The ticket's ACCEPTANCE block and this plan's list agree (the ticket block is the
source; the plan expands it into steps).

**Phase 1 — blast radius:** command files changed (smh-code-review, smh-close-task-merge-tree,
cicd-boot-sprint-memory) → all four platform doors regenerate via sync-agents, never hand-edited.
`task_preflight.py` / `gate_receipt.py` are imported by `closeout_preflight.py` (`gr.receipt_dir` /
`load_receipt` / `check_receipt`) — every signature change stays default-preserving keywords, same as
SCC-146. `scripts/INDEX.md` + SOP land in the same commits as their surfaces (armed sop_currency).
Sibling lanes: none live at lane-open (worktree list = main only). Memory store untouched.

**Phase 2 — over-engineering tripwires:** no new command, no new rule, no new script — every change
extends an existing surface; the one new helper (`receipt_defect` in gate_receipt) is finding 10's
explicit ask and lands only after A0's tests (C3). No flag any acceptance item does not require
(`--cwd` requirement IS finding 5's remedy). Gates-that-cannot-fail: both sweeps exist to prove the
new checks non-vacuous; every mutant row names its killer before the sweep runs.

**Findings (plan corrected in place before approval):**
- **F1 — near-miss detector needs an `@` requirement.** Line-start + markdown-prefix + a status word
  alone would err on legit prose headings ("## Verdict rationale: why FAIL was wrong"). All three
  shapes finding 6 names carry an `@`; the detector requires verdict-at-line-start + status word +
  `@` on the line, canonical-unmatched. A typo'd stamp with NO `@` is missed — and harmless: it can
  never grant a SKIP, and the governing latest-stamp rule means it cannot demote a real one.
- **F2 — acceptance-8's fixture must write its `workflow_lint.py` / `check_maps.py` stubs ON THE
  BRANCH BEFORE the verdict stamp** — they are non-artifacts paths, so writing them after the stamp
  trips the code-fresh check and the case would prove staleness, not SKIP scope.
- **F3 — acceptance-6's dirty-receipt pin must use NON-artifacts dirt** (`docs/…`), or A4's
  reader-side exemption would legitimately flip the pin later and the killer would die with it.

**Audit verdict: GO**
