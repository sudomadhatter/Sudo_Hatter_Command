---
IsArtifact: true
ArtifactMetadata:
  title: Project → .agents format conversion playbook (reusable; → /convert-project)
  type: reference
  date: 2026-06-24
---

# Conversion Playbook — old format → home-base `.agents/` format

Proven on `clean-bmad-workspace` (2026-06-24). This is the reusable procedure for the 6 queued
projects in `router.md`; it is structured to graduate into a `/convert-project <name>` command.
**Order matters** — master-side changes happen before the sync so they get vendored.

## What "converted" means (target end-state)
- Root: thin `CLAUDE.md` + `GEMINI.md` ("Read AGENTS.md") + a generic Layer-2 `AGENTS.md` map.
- `.agents/` (plural) = the single vendored toolkit (rules · skills · commands · workflows · bmad · scripts · templates · opencode-agents).
- `.claude/` = `commands/` + `skills/` (+ project `settings*.json`). `.opencode/` = `commands/` + `agent/`.
- `opencode.json` points at `.agents/` with a least-context `instructions` list.
- No `.agent/` (singular), no `.claude/rules/`. Rules load by path from `.agents/rules/` via `AGENTS.md`.

## Ordered steps

| # | Step | How |
|---|---|---|
| 0 | **Master-side first** (if the change is shared) | Author any new shared doc/command in the home-base master `.agents/` BEFORE syncing (e.g. `.agents/workflows/autopilot_bmad_dev_loop.md`). |
| 1 | **Sync the toolkit** | `& .agents/scripts/sync-agents.ps1 -Target <project>` → vendors the whole master `.agents/` (additive `robocopy /E`) + populates `.claude/{commands,skills}` and `.opencode/{commands,agent}`. |
| 2 | **Add project-specific rules** | Copy the project's own rules (those NOT in the master) into `<project>/.agents/rules/`. They survive the additive sync. |
| 3 | **Drop conflicting master rules** | Remove `<project>/.agents/rules/git-closeout-commits.md` (see Git policy below). |
| 4 | **Rewrite the 3 root files** | Generic Layer-2 `AGENTS.md` (no domain values, no `{{PLACEHOLDERS}}`) + thin `CLAUDE.md`/`GEMINI.md`. Put the **git hard-rule** in `AGENTS.md` ALWAYS-LOAD. |
| 5 | **Rewrite `opencode.json`** | `instructions: ["AGENTS.md", ".agents/rules/constitution.md", ".agents/rules/karpathy-guidelines.md"]`, `skills.paths: [".agents/skills"]`. **Preserve** the project's `permission` block; only the paths change. |
| 6 | **Preserve, then retire old format** | FIRST copy any unique non-vendored files out (see Gotcha 2), THEN delete `.agent/` (singular), `.claude/rules/`, and the redundant `.gemini/GEMINI.md`. Keep `.gemini/notes.md` and `.antigravity/mcp.json`. |
| 7 | **Point personal copies at the master** | Replace `_01_My/Agentic_Loops/autopilot_bmad_dev_loop.md` with a pointer to `.agents/workflows/...`. |
| 8 | **Verify** | See the checklist; then run the opencode/cold-agent routing test. |

## Rule reconciliation (clean-bmad instance)
- **Keep (project-specific, copied to `.agents/rules/`):** `adk_file_formating`, `credential-resolution`,
  `prompt-tdd`, `pyrefly-paths`, `useEffect-dep-array-stability`, `voice-agent-architecture`.
- **From master (vendored):** `constitution`, `karpathy-guidelines`, `artifacts-always-first`,
  `code-standards`, `collaborative-debug-first`, `completion-not-illusion`, `dependency-awareness`,
  `mermaid-diagram-preferences`, `powershell-encoding-safety`, `prose-formatting`, `bmad_code_review_fast_path`.
- **Retire (stale/superseded):** `mandatory-session-artifacts` (dead Antigravity flow), `000-PLAN-FIRST-GATE`
  (folded into constitution + artifacts-always-first).
- **Drop (policy conflict):** `git-closeout-commits` (permits close-out commits — see below).

## Git policy (DECIDED)
**Agents NEVER `git commit`/`git push`.** They print the exact command in the walkthrough's "Your
Actions"; Daniel pushes himself. Implementation: the authoritative rule lives as a line in `AGENTS.md`
ALWAYS-LOAD (loaded first, our file, BMAD-update-proof), and `git-closeout-commits.md` is not vendored.
> KNOWN RESIDUE: the vendored master `constitution.md:19` + `artifacts-always-first.md:137` still carry a
> "you MAY commit at close-out — see git-closeout-commits" clause. The `AGENTS.md` line explicitly
> supersedes it. The clean global fix (make never-commit the master default; close-out-commit becomes an
> aviationChat-only override) is a flagged FOLLOW-UP, not done here.

## BMAD-owned vs ours (the user's constraint: BMAD updates regenerate its files)
- **BMAD-owned — never hand-edit, re-sync from source:** `_bmad/`, `.agents/bmad/`, the `bmad-*` skills
  and commands. Old BMAD skill versions in a project's `.agent/skills/` are SUPERSEDED by the newer
  vendored `.agents/skills/` — the new set wins; don't preserve the old ones.
- **Ours — safe to author:** `AGENTS.md`, `CLAUDE.md`/`GEMINI.md`, `opencode.json`, our non-bmad rules in
  `.agents/rules/`. **Put every customization here**, never in a BMAD-owned file.

## Gotchas discovered (bake these into /convert-project)
1. **Don't move the autopilot script.** `autopilot-dev-story.ps1` resolves repo root as
   `$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path` — it hard-assumes it lives at `<project>/scripts/`.
   Moving it into `.agents/scripts/` silently breaks every path. Leave it project-local. (Promoting it to
   master needs a location-independent `$RepoRoot` + a real test run — a future enhancement.)
2. **Check for unique content before deleting `.agent/`.** clean-bmad's `.agent/workflows/` held 3 docs
   NOT in the master (`1_live-user-QA-bugs.md`, `1_looping-dev-cycle.md`, `update_workflow_template_match.md`)
   — one was git-UNTRACKED (permanent loss if deleted blind). Always `git ls-files` + diff against the
   vendored set, and copy unique files to the artifact folder first.
3. **opencode.json paths break on conversion.** The old file points at `.agent/...` — rewrite it (step 5)
   or the very first opencode session fails to boot.

## Verification checklist (all ✓ on clean-bmad 2026-06-24)
- `grep '\.agent/' AGENTS.md CLAUDE.md GEMINI.md opencode.json` → none.
- `grep '{{' AGENTS.md CLAUDE.md GEMINI.md opencode.json` → none.
- `.claude/commands` (32) · `.claude/skills` (106) · `.opencode/commands` (31) · `.opencode/agent` (13) populated.
- Every path referenced in `AGENTS.md` resolves on disk.
- `.agents/rules/git-closeout-commits.md` absent.
- Final: a cold opencode/Claude/Antigravity session boots `AGENTS.md` → `.agents/` and routes.
