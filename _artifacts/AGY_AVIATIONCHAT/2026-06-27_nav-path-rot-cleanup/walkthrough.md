---
IsArtifact: true
ArtifactMetadata:
  title: AviationChat navigation path-rot cleanup — walkthrough
  type: walkthrough
  date: 2026-06-27
---

# Walkthrough — AviationChat nav path-rot cleanup

## What this was
A deep-dive audit of AGY's navigation found the project had been **renamed**
(`aviationChat-AGY → AGY_AVIATIONCHAT`) and **relocated** (`c:\Sudo_Hatter_Command\` →
`c:\Users\dlohn\.gemini\antigravity\scratch\Sudo_Hatter_Command\` — verified the old root does NOT exist), and
the stale absolute paths never followed. Broken pointers were scattered across nav identity, BMAD config, live
code, type-check config, and the lobby master toolkit. The nav *architecture* was healthy; the rot was the issue.

## What changed & why (step by step)

### 1. Pyrefly / interpreter config (via the `python_inter_venv_fix` skill)
The skill flagged **four** interpreter-config files. Three (`​.vscode/settings.json`, root + `backend/`
`pyrightconfig.json`) were **already portable** (`${workspaceFolder}`/relative) — no change. Only `pyrefly.toml`
held the dead absolute path → repointed to the real `backend/.venv` (kept absolute + `\\` per the project's own
`pyrefly-paths.md` rule, which I also corrected). **Verified the interpreter resolves:**
```
$ backend/.venv/Scripts/python.exe -c "import sys, fastapi, google.adk, pydantic; print(sys.executable); ..."
C:\Users\dlohn\.gemini\antigravity\scratch\Sudo_Hatter_Command\Projects\AGY_AVIATIONCHAT\backend\.venv\Scripts\python.exe
fastapi 0.129.0
deps OK
```

### 2. AGY nav identity (the old name)
`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` titles; `_artifacts/INDEX.md` (`Projects/AGY_AVIATIONCHAT/…`, **kept** the
correct home-base bucket ref `_artifacts/aviationChat-AGY/`); `constitution.project.md` (×3).

### 3. Broken base-path in live code/scripts/docs
`backend/check_db.py` (credential path — **verified the real `auth_keys/service-account.json` exists** at the new
location), `scripts/deploy_media.py` + `upload-faa-library.ps1`, `scratch/{upload_about_assets.py,
check_foldin_targets.ps1, count_rkps.ps1}`, `docs/file_structure_rules/{README.md, master-implementation-plan.md}`.
Left the **bare home-base name** `Sudo_Hatter_Command` (correct) and the historical "reference donor" narrative.

### 4. Lobby master toolkit → relative links (durable fix) + re-sync
Converted the 8 skill files' footer `file:///C:/…/aviationChat-AGY/.agents/skills/<x>/SKILL.md` links to
**relative** `../<x>/SKILL.md` (20 links) so they never rot on a move. Fixed 3 prose/command refs
(`adk-testing-patterns` cd example; `python_inter_venv_fix` — fixed only the *current*-path side, kept the
illustrative "moved-from" old path; `skills_explained.md` → portable relative path). `sync-agents.ps1` /
`artifacts-always-first.md` had **no** stale markers (only the correct name) — no change.

### 5. BMAD project_name — and a design discovery
Reading `sync-agents.ps1` before running it surfaced that a project sync **robocopies the whole master
`.agents/` (incl. `bmad/`) into each project** — so `/sync-agents` would have **overwritten** the per-project
BMAD `project_name` with the master's value (that's *why* all three workspaces wrongly read `aviationChat-AGY` —
the master propagated one value to all). Per your call ("make bmad/ project-owned"), I **excluded `.agents/bmad/`
from the vendor** (new `-ExcludeDirs` param on `Sync-Dir`, + doc-comment + `sync-agents.md` update). Now each
workspace owns its BMAD identity. **Verified post-sync — 3 distinct names, none clobbered:**
```
LOBBY: project_name = "Sudo_Hatter_Command"
AGY  : project_name = "AGY_AVIATIONCHAT"
FRESH: project_name = "Fresh_Workspace_BMAD"
```

### 6. Ran `/sync-agents` (lobby + both projects)
```
RUN 1 LOBBY : .claude 35 · .opencode 31 · opencode-global 31 · antigravity-global 30
RUN 2 AGY   : .claude 35 · .opencode 31   (vendored .agents refreshed, bmad/ untouched)
RUN 3 FRESH : .claude 35 · .opencode 31   (same)
```
Propagated the relative skill links to every project's vendored `.agents/` + `.claude`/`.opencode` mirrors.
**Verified** AGY's vendored link is now `[multi-agent-orchestration.md](../multi-agent-orchestration/SKILL.md)`.

### 7. Fixed two more on the final sweep
`GEMINI.md` (missed nav adapter) and `.opencode/agent/autopilot-auditor.md` (a **project-local orphan** — master
now uses `opus-auditor`/`opus-reviewer`; sync's additive copy left it, so I corrected its example path directly).
Regenerated the lobby `docs/doc-graph.{md,json}` (generated artifact, was stale after the skill-link edits) →
**0** `aviationChat-AGY` refs remain in it.

### Verification (final)
- Key nav/brain/adapters (`AGENTS/CLAUDE/GEMINI/constitution.project`): **CLEAN**.
- Interpreter resolves; `check_db.py` credential path exists; BMAD names = 3 distinct; skill links relative; doc-graph 0 refs.
- Remaining `aviationChat-AGY` hits are all **intentional/legit**: the home-base bucket name `_artifacts/aviationChat-AGY/`
  (kept by design), the `python_inter_venv_fix` "moved-from" example, frozen `_artifacts/**` history, and **37
  `_bmad-output/**` files** (BMAD-generated work products — out of scope; future BMAD output now uses the corrected name).

## Deviations from plan
- Plan listed `sync-agents.ps1`/`artifacts-always-first.md` as base-path fixes — turned out they had no stale
  markers (no change needed).
- Added (not in original plan, surfaced mid-run): the `bmad/`-exclusion change to `sync-agents.ps1` (your
  approval), `GEMINI.md`, the orphan `autopilot-auditor.md`, and the doc-graph regen.

## Task Checklist
- [x] Pyrefly/interpreter config repointed (via skill) + verified resolving
- [x] AGY nav identity (AGENTS/CLAUDE/GEMINI/INDEX/constitution) → AGY_AVIATIONCHAT
- [x] AGY BMAD project_name → AGY_AVIATIONCHAT (4 files)
- [x] AGY broken base-paths in code/scripts/docs corrected (credential verified)
- [x] Lobby master skill links → relative (8 files, 20 links) + 3 prose refs
- [x] Lobby master sync-agents.ps1/artifacts-always-first.md — verified no stale, no change
- [x] Lobby BMAD project_name → Sudo_Hatter_Command (4 files)
- [x] Fresh BMAD project_name → Fresh_Workspace_BMAD (4 files)
- [x] sync-agents.ps1: exclude bmad/ from vendor (your approval) + docs
- [x] /sync-agents ran (lobby + both projects); links propagated; bmad NOT clobbered (3 distinct names verified)
- [x] GEMINI.md + orphan autopilot-auditor.md fixed; doc-graph regenerated
- [ ] **Deferred (out of scope):** 37 `_bmad-output/**` files still say `aviationChat-AGY` in prose — BMAD-generated content, your call whether to bulk-rename

## Your Actions
Three separate repos — commit each on `main_debug` (never `main`). The `/sync-agents` legitimately touched
`.agents/.claude/.opencode` broadly, so `git add -A` per repo is the practical call (your commit, your tree):

```bash
cd "c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command"

# LOBBY (master toolkit + re-sync + doc-graph + this session's artifacts)
git add -A && git commit -m "fix(nav): relative skill links + exclude bmad from sync vendor; lobby bmad=Sudo_Hatter_Command; regen doc-graph"

# AGY (separate repo): nav identity + base-paths + bmad name + pyrefly + propagated toolkit
git -C Projects/AGY_AVIATIONCHAT add -A && \
  git -C Projects/AGY_AVIATIONCHAT commit -m "fix(nav): repoint stale name+path after rename/relocation (pyrefly, code, docs, bmad=AGY_AVIATIONCHAT)"

# FRESH (separate repo): bmad name + propagated toolkit
git -C Projects/Fresh_Workspace_BMAD add -A && \
  git -C Projects/Fresh_Workspace_BMAD commit -m "fix(nav): bmad project_name=Fresh_Workspace_BMAD + propagated toolkit (relative skill links)"
```

Then:
- **Reload VS Code** (`Ctrl+Shift+P → Developer: Reload Window`) so pyrefly picks up the new interpreter path (it does not hot-reload).
- **Restart opencode** so the refreshed global command cache is picked up.
- Decide on the deferred `_bmad-output/**` bulk-rename (37 files, prose only).
