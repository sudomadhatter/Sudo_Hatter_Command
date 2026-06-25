---
IsArtifact: true
ArtifactMetadata:
  title: "WS7 home-base drift hook + aviationChat Phase 2 — walkthrough"
  type: walkthrough
  date: 2026-06-25
---

# Walkthrough — WS7 (home base) + aviationChat Phase 2

Two workstreams, one approved plan. Everything below is **done**. Two repos are left **uncommitted** for
Daniel (commands in "Your Actions"). GitNexus confirmed **zero code behaviour changed**.

## Part A — WS7: the home base got its own repo-map + drift hook

- **A1.** Added optional `-Root` and `-MapPath` params to the master
  `.agents/scripts/check-repo-map-drift.ps1` (backward-compatible — projects calling their vendored copy with
  no args are unchanged). Re-vendored the identical script into `Projects/aviationChat-AGY/scripts/` (hash-matched).
- **A2.** Generated `_docs/repo-map.md` (curated header naming every top-level area incl. a `Projects/` pointer,
  + an auto body). `Projects/`, `_my_resources/` ignored from the scan; `_artifacts/` ignored by default.
- **A3.** Wired the home-base `.claude/settings.json` SessionStart hook to (1) inject `_docs/repo-map.md` into
  continuity and (2) run the drift script with `-Root $env:CLAUDE_PROJECT_DIR -MapPath '_docs/repo-map.md'`.
  **The direct edit went through this time** — no `settings.json.proposed` needed for the home base.
- **A4.** Added a `_docs/repo-map.md` row to AGENTS.md §4.

**Test output (Part A):**
```
JSON parse check ............ VALID JSON
block 1 (continuity + map) .. active-context present; repo-map present
block 2 (drift) ............. drift exit: 0   (silent = clean)
```

## Mid-session: artifact-location rule revised (Daniel)

New rule: **artifacts go where you WORK FROM.** From the home base → `_artifacts/<project>/` bucket (project
work) or `_artifacts/_home/` (home-base work); from inside a project → that project's local `_artifacts/`.
- Moved this session's folder `_artifacts/_home/2026-06-25_ws7-and-aviationchat-phase2/` →
  `_artifacts/aviationChat-AGY/2026-06-25_ws7-and-phase2/`.
- Codified in AGENTS.md §5/§7, `_docs/workspace-standard.md`, `_artifacts/INDEX.md` placement rules, and the
  `artifacts-live-with-the-work` memory (+ MEMORY.md pointer).

## Part B — aviationChat Phase 2: one toolkit, no stale forks

What fought back: the approved plan called this "a few live refs." Reality — **`.agent/` was referenced ~120
times across 100+ files** baked *inside* the new `.agents/` toolkit (Phase 1 vendored the files without
repointing their internal `.agent/` mentions), the two engine mirrors, README, `.gemini`, the deploy ignores,
**and a no-touch BMAD zone**: `_bmad/custom/{bmad-dev-story,bmad-quick-dev}.toml` *load* the plan-gate from
`.agent/rules/000-PLAN-FIRST-GATE.md` at runtime. I stopped and got Daniel's call → **Option A: repoint the 2
BMAD TOMLs** (their headers say "Lives in `_bmad/custom/` — survives BMAD skill updates," i.e. the customization
layer, so editing a path is legitimate).

- **B1 preserve-sweep.** `.agent/skills/` had **0** unique files (all 1,025 already in `.agents/skills/`); the
  14 `.agent/workflows/` were already reclassified as `.agents/commands/1_*`; `gemini.md`'s roster/models/DB are
  in AGENTS.md §1/§6 + `_bmad-output/project-context.md`. Only `000-PLAN-FIRST-GATE.md` needed preserving.
- **Gate preserved** → `.agents/rules/000-PLAN-FIRST-GATE.md` (its `_opencode_artifacts/` ref consolidated to `_artifacts/`).
- **Repoint** `.agent/` → `.agents/` across live wiring: **96 files** (`.agents/`, `.opencode/`, `.claude/commands/`,
  `.claude/skills/python_inter_venv_fix`, README, `.gemini/GEMINI.md`, `.gcloudignore`, `.dockerignore`, `docs/workspace-standard.md`).
- **Consolidate** `_claude_artifacts/` + `_opencode_artifacts/` → `_artifacts/`: **25 files** (command/agent/workflow writers).
- **B (BMAD, Option A):** repointed the gate path in `_bmad/custom/bmad-dev-story.toml` + `bmad-quick-dev.toml` (2 refs each, 0 residual). *Nothing else in `_bmad/` touched.*
- **B3.** Removed the forked `.claude/rules/` (18 files) — it still shipped `git-closeout-commits.md` (contradicts
  never-commit) + dead `_claude_artifacts/` refs. Canonical rules now load only from `.agents/rules/` (matches the
  home base, which has no `.claude/rules/`).
- **B5.** Fixed `pyrefly-paths.md` (`...\aviationChat-AGY\...` → `...\Projects\aviationChat-AGY\...`) and the `adk`
  rule's dead external `v2-prompt-architecture` path → the in-repo `.agents/skills/v3-prompt-architecture/SKILL.md`
  (v2 never existed; v3 is the doctrine of record).
- **3 backend comment pointers** (`study_context.py`, `context_cache.py`, `sully_spike_websocket.py`) had
  `# See: .agent/...` docstrings — fixed the prefix to `.agents/` (comments only, no logic). Note: their
  `agent-context-protocol.md` target is missing from BOTH toolkits — a **pre-existing dead reference**, not caused here.
- **Deleted `.agent/`** — 1,059 files; only `.agents/` remains.
- **B7.** Regenerated `docs/repo-map.md`; drift check **exit 0 (clean)**.

**Verification (Part B):**
```
grep .agent[/\] in .agents / .opencode / .claude  ....... 0 occurrences
grep _claude_artifacts|_opencode_artifacts in live wiring  0 occurrences
aviationChat drift check ................................ exit 0 (silent)
GitNexus detect_changes(scope: all, AGY_AVIATIONCHAT):
  changed_count 31 · affected_count 0 · affected_processes [] · risk_level LOW
  (only "code" symbol = _build_live_config, whose comment was edited — zero call-graph impact)
```

## Files changed (summary)
- **Home base:** `.agents/scripts/check-repo-map-drift.ps1` · `_docs/repo-map.md` (new) ·
  `_docs/workspace-standard.md` · `AGENTS.md` · `.claude/settings.json` · `_artifacts/INDEX.md` ·
  `_artifacts/_home/active-context.md` · `_artifacts/aviationChat-AGY/2026-06-25_ws7-and-phase2/` (this folder).
- **aviationChat:** 96 repointed + 25 consolidated + 2 BMAD TOMLs + 3 backend comments + `pyrefly`/`adk`/gate +
  removed `.claude/rules/` (18) + deleted `.agent/` (1,059) + regenerated `docs/repo-map.md`. (This repo also
  still carries Phase 1's uncommitted conversion.)

## Your Actions

**1. Commit the home base** (branch `main`, c:\Sudo_Hatter_Command) — explicit paths (your prior-session work
on `router.md`/`_my_resources/` is left untouched; review `git status` if unsure):
```powershell
git -C c:/Sudo_Hatter_Command add `
  .agents/scripts/check-repo-map-drift.ps1 `
  _docs/repo-map.md _docs/workspace-standard.md AGENTS.md `
  .claude/settings.json `
  _artifacts/INDEX.md _artifacts/_home/active-context.md _artifacts/aviationChat-AGY/
git -C c:/Sudo_Hatter_Command commit -m "feat(home): WS7 lobby repo-map + drift hook; artifacts go where you work from"
```

**2. Commit aviationChat** (branch `main_debug`, Projects/aviationChat-AGY) — this repo's uncommitted state is the
**entire conversion (Phase 1 + Phase 2)** and is all our work (GitNexus = zero code behaviour change). Eyeball
`git status` first; if it's only the conversion, this repo's own `-A` is fine here:
```powershell
git -C c:/Sudo_Hatter_Command/Projects/aviationChat-AGY status            # confirm it's all conversion work
git -C c:/Sudo_Hatter_Command/Projects/aviationChat-AGY add -A
git -C c:/Sudo_Hatter_Command/Projects/aviationChat-AGY commit -m "refactor(agents): collapse .agent/ -> .agents/; reconcile forked config; project-local _artifacts (Phase 1+2)"
```

**3. Apply the aviationChat hook** — `Projects/aviationChat-AGY/.claude/settings.json` still has the old inline
drift + a stale `_claude_artifacts` Bash rule. Copy the project-local
`Projects/aviationChat-AGY/_artifacts/2026-06-25_workspace-standard-conversion/settings.json.proposed` over
`Projects/aviationChat-AGY/.claude/settings.json` (drop `.proposed`). *(The home base did NOT need this — its direct edit worked.)*
