---
IsArtifact: true
ArtifactMetadata:
  title: AviationChat navigation path-rot cleanup (rename + relocation)
  type: implementation_plan
  date: 2026-06-27
---

# Implementation Plan — AviationChat nav path-rot cleanup

## Goal
Eliminate two layers of stale absolute-path rot in the AGY workspace so agents/tools never hit dead
paths:
1. **Stale name** — old `aviationChat-AGY` (folder is now `AGY_AVIATIONCHAT`).
2. **Stale base path** — `c:\Sudo_Hatter_Command\…` (the project was relocated; that root does NOT exist —
   verified. Real root: `c:\Users\dlohn\.gemini\antigravity\scratch\Sudo_Hatter_Command\…`).

Scope (Daniel approved): **Everything — local + master re-sync**, pyrefly via the **`python_inter_venv_fix`**
skill. **Exclude frozen history** (`_artifacts/**` dated session records — never rewritten). Each repo
commits separately (git-policy: I hand the commands, never commit).

## Ownership map (decides WHERE each fix lands)
- **AGY-repo-owned** (fix in `Projects/AGY_AVIATIONCHAT/`): `AGENTS.md`, `CLAUDE.md`, `_artifacts/INDEX.md`,
  `.agents/rules/constitution.project.md`, `.agents/bmad/*` configs, `pyrefly.toml`, `docs/*`, `backend/*`,
  `scripts/*`, `scratch/*`.
- **Lobby-master-owned** (fix in lobby `.agents/`, then `/sync-agents` propagates to all projects + `.claude`/
  `.opencode`/global caches): the 11 skill files' footer links, `sync-agents.ps1`, `artifacts-always-first.md`.
  ⚠️ Fixing these inside the AGY repo would be **clobbered on next sync** — must fix at master.

## Files & edits

### A. AGY — nav identity (name)
1. `AGENTS.md:1` — title `aviationChat-AGY` → `AGY_AVIATIONCHAT`.
2. `CLAUDE.md:1` — `# Entry — aviationChat-AGY` → `AGY_AVIATIONCHAT`.
3. `_artifacts/INDEX.md` — fix `Projects/aviationChat-AGY/` → `Projects/AGY_AVIATIONCHAT/` (line ~4).
   **KEEP** the home-base bucket ref `_artifacts/aviationChat-AGY/` (line ~5) — that bucket really kept the
   old name; it's a correct path, not drift.
4. `.agents/rules/constitution.project.md` — project name ×3 (project-local `.project.md`, not synced).

### B. AGY — BMAD identity
5. `.agents/bmad/config.toml` + `.agents/bmad/{bmm,core,tea}/config.yaml` — `project_name` → `AGY_AVIATIONCHAT`.
   (`sync-agents.ps1` does NOT manage bmad module config → safe, per-workspace local edit.)

### C. AGY — broken base path (live code/config/scripts/docs)
6. `backend/check_db.py` — credential path → real base+name (real `service-account.json` confirmed present
   at new location). **Code change** — will spot-check it imports/points correctly.
7. `scripts/deploy_media.py`, `scripts/upload-faa-library.ps1`.
8. `scratch/upload_about_assets.py`, `scratch/check_foldin_targets.ps1`, `scratch/count_rkps.ps1`
   (scratch = throwaway, but cheap to correct).
9. `docs/workspace-standard.md`, `docs/file_structure_rules/{README.md, master-implementation-plan.md,
   workspace-standard.md}`.
10. `pyrefly.toml` + `.agents/rules/pyrefly-paths.md` → **via `python_inter_venv_fix` skill** (repoints the
    interpreter/type-check config to the real `.venv`).

### D. Lobby master toolkit (fix at master → `/sync-agents`)
11. 11 skill files in lobby `.agents/skills/` — footer `file:///C:/Sudo_Hatter_Command/Projects/aviationChat-AGY/…`
    links → correct base+name: `skills_explained.md`, `specialist_agents_team`, `regulatory-verification-protocol`,
    `rag-implementation`, `python_inter_venv_fix`, `hr-agent-schema-guide`, `gcp-cloud-run`,
    `6_dual-store-rag-patterns`, `agent-handoff-patterns`, `4_sse-streaming-patterns`,
    `5_adk_skills/adk-testing-patterns`.
12. `.agents/scripts/sync-agents.ps1`, `.agents/rules/artifacts-always-first.md` — base-path refs (verify at
    master, fix if present).
13. Run **`/sync-agents`** to push master fixes to all projects + `.claude`/`.opencode`/global caches.

## ✅ Decisions (resolved with Daniel, 2026-06-27)
- **D1 — Lobby master BMAD `project_name`:** set to **`Sudo_Hatter_Command`** (lobby `.agents/bmad/config.toml`
  + `bmm/core/tea config.yaml`).
- **D2 — Fresh_Workspace_BMAD BMAD `project_name`:** **fix to `Fresh_Workspace_BMAD`** this pass (separate repo
  → separate commit).
- **D3 — Skill footer links:** **convert to RELATIVE** (`../other-skill/SKILL.md`) at the lobby master so they
  never rot again (~11 files), then `/sync-agents`.

> Net: BMAD `project_name` becomes correct **per workspace** — lobby=`Sudo_Hatter_Command`,
> AGY=`AGY_AVIATIONCHAT`, Fresh=`Fresh_Workspace_BMAD` (3 separate repos, 3 separate commits).

## Execution order
1. Apply `python_inter_venv_fix` skill (pyrefly) → item 10.
2. AGY-local edits (A,B,C) via Edit.
3. Lobby-master edits (D items 11–12) via Edit.
4. `/sync-agents`.
5. Verify (below).

## Verification
- `grep -rn "aviationChat-AGY"` and `grep -rn "c:[\\/]Sudo_Hatter_Command[\\/]Projects"` across AGY + lobby,
  **excluding** `_artifacts/**`, `node_modules`, `.venv`, `_bmad/`, `_archived/` → expect **0 live hits**.
- Confirm `backend/check_db.py` points at the real `auth_keys/service-account.json` (exists).
- Confirm pyrefly/interpreter resolves (skill's own check).
- Re-run `/sync-agents` clean; spot-check one `.claude/skills/*/SKILL.md` got the corrected link.

## NOT touched
- Frozen history under `_artifacts/**` (dated walkthroughs, `_RUN-STATUS.md`, plans).
- The home-base bucket name `_artifacts/aviationChat-AGY/` (correct as-is).
- `_my_resources/**` (protected).
- Any code logic — base-path string corrections only.

## Git (per repo, at close — I hand commands, never run)
- AGY repo: its A/B/C files.
- Lobby repo: master `.agents/` + synced `.claude`/`.opencode` mirrors.
- Fresh repo (if Q2 = yes): its bmad config.
