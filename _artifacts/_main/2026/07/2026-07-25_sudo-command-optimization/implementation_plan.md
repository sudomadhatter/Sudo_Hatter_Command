---
IsArtifact: true
ArtifactMetadata:
  title: Sudo command surface optimization — single-source slimming, zero safety loss
  type: implementation_plan
  date: 2026-07-25
---

# Sudo command optimization — implementation plan

**Goal.** The `/sudo-*` command set has grown context-heavy: the 20 masters in `.agents/commands/` total ~197 KB, and ~51% of the lobby's whole sudo surface (67 files, 402 KB across `.agents/commands` + `.agents/workflows` + `.claude/*`) is byte-identical mirror duplication, with a further layer of *hand-paraphrased* duplication inside the masters themselves. Slim every command to its executable steps + gates, single-source everything else, and lose **zero** safety obligations. Scope per Daniel: **sudo commands only**, plus non-BMAD sub-workflows they call. BMAD skills untouched (see §2).

## 1. What the audit found (baseline)

| Bloat class | Size | Where |
|---|---|---|
| Step 0 "resolve target project" preamble | **~20.2 KB / 242 lines**, paraphrased 16 different ways | 16 of 20 masters |
| Re-narration of existing rules (`git-policy`, `worktree-per-story`, `artifacts-always-first`, `tests-must-gate-for-real`, `constitution`) | ~6–8 KB | 12 masters |
| Inline explanations of *other* commands/skills (what `/sudo-e2e` does, what `bmad-testarch-*` do, clean-code-audit internals, GitNexus tool tour, run-e2e.mjs internals) | ~4–5 KB | ~25 catalogued sites |
| History/anecdote prose (31k-token close-out story, OIDC loss tale, d098dc63 incident, fix-history parentheticals) | ~2 KB | 5 masters |
| `sudo-adviser-board.md` internal duplication (spawn templates restate the caucus/card contract ~90%; 148-line roster with an existing REFERENCE doc) | ~20 KB potential | 1 file (Phase 2) |

Baseline safety inventory (≈259 gates/STOPs/obligations, per file, exhaustive): [safety-inventory.md](safety-inventory.md). **The optimization is only done when every line of it survives** — either verbatim in the slimmed file or in the rule section the file now points to.

Known bugs found (fixed by this plan): 6 of 11 `sudo-*` SKILL.md launchers point at `_my_resources/active-project.txt` — the real pointer is `.agents/active-project.txt` (only file that exists). `sudo-self-audit_AP.md:12` points at the `.agents/workflows/` *mirror* — works today, but that mirror auto-degrades to a stub if the master ever crosses 11.5 KB (it sits at 10.6 KB); repoint to the master in `.agents/commands/`.

## 2. BMAD constraint — verified

The BMAD customize layer **is installed and already in use**: `bmad-customize` skill at `.claude/skills/bmad-customize/`, resolver at `_bmad/scripts/resolve_customization.py` (lobby + AGY), and four live team overrides in `_bmad/custom/` (both repos, byte-identical): `bmad-dev-story.toml`, `bmad-quick-dev.toml`, `bmad-testarch-atdd.toml`, `bmad-testarch-automate.toml`. The dev-story override already injects the plan-first gate + artifact protocol via `activation_steps_prepend` + `persistent_facts` + `on_complete`.

**Consequence:** this optimization needs **no BMAD changes at all** — the bloat lives entirely in our wrapper layer, and the BMAD overrides are a second enforcement layer *underneath* the wrappers, which makes trimming wrapper re-narration of the artifact protocol extra safe. No new overrides proposed.

## 3. Design — one obligation, one home (4-layer law)

1. **Commands** = orchestration only: numbered steps, gates/STOPs, echo contracts, verdict semantics.
2. **Rules** (read in place on all 4 platforms, already single-sourced) = mechanics: `git-policy`, `worktree-per-story`, `artifacts-always-first`, `tests-must-gate-for-real`, `code-standards` + **one new rule** (below).
3. **Other commands/skills self-describe when invoked** — per Daniel: *point, don't explain*. "Run `/sudo-e2e` — GREEN required" replaces every embedded description of what the callee does.
4. **BMAD overrides** keep enforcing inside the black box (already live, untouched).

Hard constraints honored:
- **Obligations stay as explicit steps** (memory: `restate-alwayson-obligations-in-command-bodies`) — we compress the *how*, never delete the *what*. Every STOP/echo/never line stays in the command body as a one-liner; only the mechanics move behind a rule pointer.
- **Kept verbatim, untouchable:** ② Step 2 model-switch gate (memory says it's at-ceiling by design), ② Step 2.5 conditional gate, both BDD gates, epic-flow FLOW CONTRACT, quick-dev EJECT tripwire, push-e2e MANDATORY RULES + human gates, close-workingtree merge-ancestor gate, all verdict semantics (PASS/CONCERNS/FAIL/WAIVED), status-flip contract, `PIPELINE_BLOCKER` blocks (orchestrator contract), all `**Never:**` lists.
- Relative `.agents/...` pointers are the established cross-platform mechanism (the generated AG stubs and SKILL launchers already rely on it).

### 3a. New file: `.agents/rules/sudo-target-resolution.md` (~2.5 KB)

The canonical Step-0 ladder, written once, with its three deliberate variants:
- **§STD** — 0 self fast-path → 1 `$ARGUMENTS` inline override → 2 `.agents/active-project.txt` pointer → 3 STOP-and-ask. (14 commands)
- **§ASK** — boot variant: never silently reuse the pointer; always confirm. (`sudo-boot-sprint-memory`)
- **§DUAL** — park/resume variant: scope = lobby + project, both repos.
Plus the shared binding rule (all paths under `PROJECT_ROOT`; missing path → STOP; never the lobby) and the echo contract. Frontmatter `activation: Manual`. Add its row to `.agents/rules/INDEX.md`.

Each command's Step 0 shrinks to ~3 lines, e.g.:
> **Step 0 — Bind the target** per `.agents/rules/sudo-target-resolution.md` §STD. Unknown → STOP and ask; never guess, never the lobby. **Echo exactly** `Target: Projects/<name>` before any work; a needed path missing under `PROJECT_ROOT` → STOP.

### 3b. Per-file work table (Phase 1 — 15 masters, edit in `.agents/commands/` only; mirrors regenerate via sync)

| File | Now | Target | Cut (→ where) | Keep verbatim |
|---|---|---|---|---|
| sudo-update-sprint-memory | 14,219 | ~9.8K | Step0→rule; Step7 landing narration→`git-policy` §The landing (keep all STOP/precondition lines + command skeleton); Step5 anecdotes→one-liners; "map of other files' jobs"→cut | Step 4 flip semantics (sign-off, only-red-blocks, no-punt, idempotence), ≤20 KB budget report, Step 6 asks |
| sudo-dev-story-tests | 11,988 | ~8.9K | Step0→rule; Step0.5→`artifacts-always-first` §2 + echo; Step0.6→`worktree-per-story` "Resuming" + echo; Step0.7 BDD *explainer*→bare `/sudo-bdd-tests` pointer | Step 0.7 gate itself, **Step 2 + 2.5 whole**, Step 5 checklist, Done lane rules |
| sudo-code-review | 11,906 | ~9.2K | Step0→rule; Step0.5→rule pointer + echo; testarch sub-skill descriptions→bare invocations; clean-code-audit internals→skill pointer | Clean-Room framing, all Step 3.x gate obligations, Step 3.5's six hard rules, verdict semantics, stay-in-lane |
| sudo-self-audit | 10,626 | ~8.7K | Step0→rule; GitNexus tool tour→bare calls + `gitnexus-impact-analysis` pointer | All phases, 9 tripwires, Go/No-Go, right-size gate |
| sudo-create-epic-sprint | 7,314 | ~6.1K | Step0→rule; tighten fix-history parentheticals | **FLOW CONTRACT verbatim**, Step 3 interactive hard stop, `backlog` correction |
| sudo-write-story-tests | 7,083 | ~5.6K | Step0→rule; Step0.5 mechanics→worktree rule (keep ordering caveat + echo) | BDD Vision Lock, ground-every-red, Done/Git rules |
| sudo-boot-sprint-memory | 6,585 | ~5.3K | Step0→rule §ASK (ASK line stays inline); Step3 guardrails→one-liners + constitution pointer | Discovery-only header, Step 2b worktree/origin checks, "NOT the master pick-up" |
| sudo-push-e2e | 6,339 | ~5.4K | Step0→rule; token/credential mechanics→`git-policy` pointers (rules stay as one-liners) | MANDATORY RULES, path table, both 🛑 HUMAN GATEs, gate-is-not-optional |
| sudo-park | 6,232 | ~5.6K | Step0→rule §DUAL; d098dc63 tale→one-liner | Hard boundary, gitlink guard, count-out-loud, Never-list |
| sudo-bdd-tests | 5,990 | ~5.4K | Generic pass only (Step0→rule; pointer-ize ② mention) | everything else |
| sudo-quick-dev | 5,062 | ~4.5K | Step0→rule; intro bypass-prose→one line each | **EJECT tripwire**, scoped-verification rules, stop-at-end |
| sudo-resume | 4,657 | ~4.3K | Step0→rule §DUAL; trim why-prose to 3 lines (ls-remote rationale is load-bearing) | ff-only STOP, never-force rules, Never-list |
| sudo-live-testing-team | 4,622 | ~4.2K | Generic pass only | everything else |
| sudo-e2e | 3,744 | ~3.3K | Step0→rule; harness internals→"the harness owns env/seed/config — do NOT hand-roll" | journeys-config-only rule, GREEN/RED contract, env-failure-is-RED |
| sudo-close-workingtree | 3,405 | ~3.2K | Step0 compact | merge-ancestor gate, `-d` not `-D`, three ✅ report |

**Masters: ~111 KB → ~87 KB (−21%)**; ×3 mirrored surfaces ≈ −60 KB repo-wide. Bonus: ②, ③, and close-out drop under the 11.5 KB stub threshold → their three Antigravity launchers **revert to full verbatim workflows** (AG gets the real flow natively again).

Also in Phase 1: fix the 6 SKILL.md pointer paths (`.agents/skills/` masters; `.claude/skills/` copies follow via sync), repoint `sudo-self-audit_AP.md:12` at `.agents/commands/sudo-self-audit.md`, add the new rule + INDEX row.

### 3c. Phase 2 (optional, each needs its own go-ahead)

- **sudo-adviser-board (52.7K → ~30K):** move the 148-line roster + question bank + tone dial into the existing REFERENCE doc (`_my_resources/diagrams_guides/workflows_tea_testing/sudo-adviser-board-REFERENCE.md` — lobby-only is fine, the board is a lobby command; reconcile the stale `commands/INDEX.md` path citation while there); de-duplicate spawn templates by making them *assembly instructions* ("paste §contract verbatim into the spawn") instead of a second copy — spawned agents still receive fully self-contained prompts. All 34 chair/integrity gates stay in the command.
- **sudo-mobile-error-team (16.1K):** light generic pass only (Step0→rule + pointer-ization); incident-critical, gets its own diff review.
- **`_AP` convergence:** restructure `dev-story-tests_AP`/`code-review_AP` to the delta-over-manual pattern `self-audit_AP` already proves. Artifact names + `PIPELINE_BLOCKER` contract frozen (autopilot engines depend on them).

## 4. Execution order (Phase 1)

1. Open lobby worktree `claude/sudo-command-slim` (edits touch only `.agents/` — no gitignored assets needed).
2. Write the new rule; slim the 15 masters per §3b; fix the SKILL/AP pointers.
3. **Self-verify against [safety-inventory.md](safety-inventory.md)**: per file, tick every obligation as (a) still inline or (b) present in the pointed-to rule §. Any orphan = put it back. Record the checklist in the walkthrough.
4. Present per-file diffs + before/after size table → Daniel reviews.
5. On sign-off: land on `main_debug` (explicit paths), then from the **main lobby checkout** run `/sync-agents -Maintained` (regenerates `.agents/workflows/` + `.claude/*` + globals + vendors AGY/Fresh; the 3 AG stubs should disappear in favor of verbatim mirrors).
6. Post-sync checks: `-Status` clean; grep zero remaining `_my_resources/active-project.txt` under `.agents/`; mirrors byte-identical; read-only smoke `/sudo-boot-sprint-memory` against AGY to prove Step-0-via-rule resolves.

## 5. Risks & rollback

- **Risk: an agent skips a pointer and misses an obligation.** Mitigated by the restate-obligations pattern — every obligation stays a literal step; pointers carry only mechanics — plus the §4.3 audit. Same pattern already proven by `clean-code-audit` → `code-standards.md` and the SKILL launchers.
- **Risk: sync ghosts.** `.sync-manifest.json` purge handles retired paths automatically; nothing is renamed in Phase 1 (no ghosts possible).
- **Rollback:** single worktree branch; `git revert` of one landing commit restores everything; mirrors regenerate on the next sync.

## 6. Open questions for Daniel

1. Phase 2 adviser-board: in or out? (Biggest single win, most delicate file.)
2. `Co-Authored-By: Claude Opus 4.8` is hardcoded in ③ + ③_AP — genericize to `Claude <noreply@anthropic.com>`, or leave?
3. Anything you consider sacred text beyond the safety inventory (exact wording you want preserved even where I'd compress)?
