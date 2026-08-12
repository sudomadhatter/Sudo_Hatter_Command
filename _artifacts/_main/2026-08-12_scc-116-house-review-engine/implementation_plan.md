---
IsArtifact: true
ArtifactMetadata:
  title: SCC-116 house review engine - port pr-af discipline, retire bmad-code-review
  type: implementation_plan
  date: 2026-08-12
---

# SCC-116 — House review engine (pr-af discipline, our runtime)

## Goal and evidence

Replace the vendor `bmad-code-review` skill with a house-owned review engine and port four pr-af
mechanisms: programmatic evidence extraction, a literal-correctness lens, an evidence-verify wave,
and compound synthesis. Research: `_my_resources/open_tasks/pr-af-dev-system-upgrade.md`
(all load-bearing claims re-verified against pr-af source @ `8593130`, 2026-08-12 session).

Why now, verified 2026-08-12:
- `cicd-code-review.md:32` still invokes `bmad-code-review`, whose step-04 flips stories to `done`
  and syncs `sprint-status.yaml` — violating the command's own "stay in lane" law AND the
  status-flip contract (only human close-out sets `done`).
- Containment today is `.agents/rules/bmad_code_review_sudo_fix.md` — an adapter rule that must win
  an attention contest against the vendor skill on every run. The engine deletes the contest.
- The vendor skill cannot be fixed in place: BMAD-regenerated, and `customize.toml` only appends.

**Operator mandate (2026-08-12): speed is an acceptance criterion.** Quick lanes
(`/cicd-quick-dev`, `/smh-quick-dev`) are OUT of scope. The engine runs only at the story/task
review gate. A clean diff must cost the same or less wall-clock than today; the verify wave runs
only when findings exist.

## Target architecture

```text
.agents/skills/code-review-engine/          # hand-authored house skill (no prefix, naming law §8)
├── SKILL.md                                # contract: caller has already resolved everything
└── steps/
    ├── step-01-review.md                   # 5 lenses in parallel, primed with the evidence pack
    ├── step-02-verify.md                   # Verifier ‖ Compound (both self-gating)
    ├── step-03-triage.md                   # 4-bucket model ported verbatim
    └── step-04-record.md                   # findings -> walkthrough; NO status flip, NO HALTs

.agents/scripts/evidence_extract.py         # pure code, zero LLM, --pack + --findings modes
```

Caller contract (engine never resolves these): `REPO` · `WORKTREE` · `DIFF` · `STORY_FILE` or task
acceptance list (optional) · `HEAD_SHA` · `review_mode` (`full` | `no-spec`).

Wave math (wall-clock = slowest member of a parallel batch, not the sum):
clean diff = 1 wave (same as today, now pack-primed, so same or faster);
diff with findings = 1 wave + ONE new verify wave. There is no other new wall-clock anywhere.

## Subtasks (sequential; each = `chore/<KEY>-<slug>` off main, landed via /smh-close-task-merge-tree)

### SCC-122 — Engine scaffold
Port from `bmad-code-review`: step-02 fan-out shape, step-03 4-bucket triage
(`decision_needed`/`patch`/`defer`/`dismiss`) verbatim, deferred-work routing. Port NOTHING from
step-01 (caller resolves everything) and only the findings-writing ~20 lines of step-04.
New in the spec:
- **Severity→verdict mapping table** (one vocabulary bridge, defined once): confirmed `critical`
  → FAIL; `important` → CONCERNS floor; `suggestion`/`nitpick` → never gate. Verifier-revised
  severity wins over hunter-asserted severity.
- **NA-vs-died semantics:** a lens skipped because `review_mode=no-spec` (Acceptance lens) records
  `n/a (mode)` and does NOT cap the verdict; only a lens that DIED after retry+inline caps at
  CONCERNS. Failure contract otherwise inherited unchanged from the callers.
- pr-af severity alias normalization map (cheap robustness, research doc §A.3).

### SCC-123 — evidence_extract.py
Port of pr-af `evidence.py` mechanics. **Pure-Python search — no `grep` subprocess** (pr-af shells
out at `evidence.py:260,402`; the system runs on multiple machines incl. Windows, so subprocess
grep is banned). Same walk/skip-dirs/caps semantics implemented with `re` + `os.walk`.
- Two modes: `--pack <files>` (pre-lens dossier: content + import context; max_files=6,
  400 lines/file, 16k chars) and `--findings <json>` (per-finding EvidencePackage: primary_code,
  caller_snippets, cross_refs, diff_hunk, import_context, related_code).
- Caps re-read from pr-af `config.py` AT THE PORT SHA (post-#68 caps moved; do not copy the
  research doc's Appendix A blindly). Keep: semaphore 10, ≤8 identifiers/finding, 10s per search,
  byte-bounded cache, stop-word list.
- `_path_to_module` needs a TS/JS branch (relative imports + `@/` aliases) or the frontend gets
  silently empty `IMPORTED BY`. Port their direct-join-first path-normalization fix, not the naive
  version.
- **Record the GitNexus decision in the module docstring:** grep-fresh beats the GitNexus index
  here on purpose (index is machine-local, stale after pull, misses attr-dispatch). Do not
  "deduplicate" this script into GitNexus calls; do not grow it into a blast-radius tool.

### SCC-124 — Baseline trial + stopwatch gate (go/no-go)
Run the scaffolded engine head-to-head against the current review on one real, already-landed
story diff. Measure: wall-clock, finding count, finding overlap, anything the 4 current lenses
missed. **Acceptance: clean-diff wall-clock ≤ current review.** If the bar fails, SCC-128 (rewire)
does not proceed until the regression is fixed. This subtask produces the timing evidence the
operator conditioned adoption on.

### SCC-125 — Prompt transplant (recall-first)
pr-af three FP gates + severity rubric + evidence-chain format + "what's NOT in the diff" +
author-intent engagement rule (research doc Appendix B) onto the **hunter lenses only**
(Blind Hunter, Edge Case Hunter, + the new literal lens).
- **Auditor lenses (Acceptance, Test-Adequacy) are EXEMPT from Gate 1/Gate 3** — a reachability
  proof is unwritable for a missing-test finding; they get adapted rubrics instead.
- **No noise filter, ever:** pr-af's own measurement (config.py:160) — worthiness gating trades
  recall 0.69→0.52. Our reviewer applies fixes, so noise is cheap and misses are expensive.
- Every lens prompt states: the evidence pack is a starting point, NOT the search space; live-file
  verification beats the pack (anti shared-anchor bias).

### SCC-126 — 5th lens: literal-correctness
Port `deepen_findings` discipline (harnesses.py:1524): resolve every symbol the changed code leans
on to its real definition and verify the assumption holds. Diff-scoped only; early-exit on empty
patches; 20-file cap; context-file spill above ~9k chars.
**Cost governance:** full mode in interactive reviews; in `cicd-code-review-AP` (autopilot) it runs
capped (file cap + spill mandatory) — the one real token cost of this epic, and it multiplies
overnight.

### SCC-127 — Verify wave
`step-02-verify.md`: Evidence Verifier (harnesses.py:1272 role framing — "neither reviewer nor
adversary; independent investigator") ‖ Compound synthesis (harnesses.py:1072 — NEW findings only,
`contributing_findings` required, confidence ≥0.6, empty list valid). Both consume
`evidence_extract.py --findings` output; both self-gate (0 findings → no wave; <2 → no compound).
- Severity becomes evidence-forced: verifier's `revised_severity` feeds the SCC-122 mapping table.
- **Extractor failure semantics:** extractor is code, not a lens — if it dies, the verifier runs
  cold (repo access only) with a note; it does NOT cap the verdict.

### SCC-128 — Rewire callers + retire the vendor surface
The full blast radius (bigger than the research doc listed):
1. `cicd-code-review.md` Step 1 → engine. 2. `smh-code-review.md` Step 1 → engine (gains the
lenses). 3. `cicd-code-review-AP.md` → engine, capped mode. 4. **RETIRE
`.agents/rules/bmad_code_review_sudo_fix.md`** (its whole job was patching the vendor skill).
5. **Rewrite `.agents/opencode-agents/opus-reviewer.md`** (references the fix rule — opencode
autopilot QA lane). 6. INDEX files. 7. `docs/_scc_sops_prds/workflows_testing_SOP.md` in the SAME
commit — sop_currency fires and `[sop-ok]` is not appropriate; usage genuinely changes.
8. **Resurrection lint:** armed check (workflow_lint or test_command_surfaces) — no command/rule
may reference `bmad-code-review`; BMAD regen re-emits the skill forever, so the guard is permanent.

### SCC-129 — Gate the gate
Seeded bad-diff fixture lands as a PERMANENT negative control in the test suite: the engine must
REJECT the seeded diff and PASS a clean one (a check that cannot fail is a finding). Then run
`/smh-code-review` — the new engine — on its own final diff as the cheapest real integration test.

## Verification

```bash
python3 .agents/scripts/tests/run_all.py            # incl. new engine fixtures + resurrection lint
python3 .agents/scripts/workflow_lint.py --toolkit-only
grep -rn "bmad-code-review" .agents/commands/ .agents/rules/   # empty after SCC-128
```
Plus: SCC-124 timing evidence recorded in its walkthrough; SCC-129 fixture red/green both proven.

## Boundaries

- `/cicd-quick-dev` and `/smh-quick-dev` untouched (operator ruling).
- No pr-af runtime, service, or dependency is vendored; prompts and mechanics only.
- No noise/worthiness filter is added at any layer (recorded so nobody adds one "for free" later).
- `_bmad/`-installed skill files are never hand-edited; the vendor skill is routed around, and its
  `.claude/skills/` copy is left for the regenerator to manage.
- Sequential with SCC-38 (shared files: workflow_lint, tests, SOP, INDEXes) — this epic lands first.
