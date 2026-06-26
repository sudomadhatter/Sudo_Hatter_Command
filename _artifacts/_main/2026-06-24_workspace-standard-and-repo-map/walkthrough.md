---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — Workspace Standard + Repo-Map Hybrid + Artifacts Parity
  type: walkthrough
  date: 2026-06-24
---

# Walkthrough

Executed the approved plan (rev 2): Parts **F, E, D, A, C** in full, plus the **home-base portion of B**.
Part B lab-proving and project propagation are **BLOCKED** — another team is working in
`Projects/clean-bmad-workspace`, so per Daniel's instruction it was not touched.

## Decision locked: git policy
**Never run `git commit`/`push` yourself — hand Daniel the exact command. Exception: only when Daniel
explicitly delegates a specific commit/push in the moment.** This is now the single canonical rule
(`.agents/rules/git-policy.md`), referenced from `constitution.md`, `artifacts-always-first.md`, and
`AGENTS.md` §6.

## Changes, file by file

**Part F — rename `_experiment/` → `_routing-canary/`** (git mv, history preserved)
- Renamed the folder + updated headings/run-paths in all 7 of its files; rewrote its `README.md` to add the
  "when to run" triggers + the "this proves the mechanism, not your real routing" caveat.
- Updated live references: root `AGENTS.md` §4 table; `_docs/master-implementation-plan.md` (all 7).
- Left as historical: the YouTube transcript and the other session's conversion-plan artifact.

**Part E — reconcile the rule set at the `.agents/` source**
- `git mv .agents/rules/git-closeout-commits.md → git-policy.md`, rewritten to the canonical policy (default:
  hand the command; safe-commit mechanics apply only when delegated). This file was itself the contradiction —
  it literally claimed to supersede the "never commit" hard stop.
- `constitution.md` + `artifacts-always-first.md`: git hard-stops rewritten to the canonical policy + repointed
  to `git-policy`.
- `prose-formatting.md`: dead `_claude_artifacts/*` → `_artifacts/<workspace>/*`.

**Part D — artifacts org scheme** (`artifacts-always-first.md` §2)
- Added the workspace-bucket rule (file under the workspace the work primarily changes; `_home` for
  cross-project) and the two folder forms: random task `…/<YYYY-MM-DD>_<slug>/`, story `…/<epic>/<story>/`.

**Part A — the standard** (new `_docs/workspace-standard.md`)
- Format half (required file set + each file's spec + a compliance checklist), Upkeep half (rules single-source,
  git, artifacts cadence, routing-canary cadence, router/repo-map drift, end-of-task checklist), the repo-map
  two-mode standard (code vs content), and a reconciliation appendix carrying the retire-list.

**Part C — home-base parity**
- `AGENTS.md`: added `artifacts-always-first` to §3 ALWAYS-LOAD; added the prominent **⛔ ARTIFACTS — MANDATORY
  FIRST ACTION** gate ("applies at the lobby too"); added the `workspace-standard.md` reference; added §1 item 6;
  aligned §6 RISK GATE to the git policy.
- New `.claude/settings.json` with a SessionStart hook that injects `_artifacts/_home/active-context.md` + the
  artifacts/git gate (UTF-8 pinned).

**Part B (home-base portion)** — new `.agents/scripts/generate_repo_map.py`
- Hybrid generator: Python AST + light TS/JS signatures; collapses any dir over `--threshold` (default 8) to one
  summary line; preserves the curated header between `REPO-MAP:CURATED` sentinels and only rewrites the
  `REPO-MAP:AUTO` block; `--mode content` for non-code workspaces; scaffolds a curated-header template if no file
  exists.

## Verification (real output)

**SessionStart hook** — ran the hook command; injects continuity cleanly after pinning `-Encoding UTF8`:
```
# Home-base continuity + gate (auto-injected at SessionStart)
# ACTIVE CONTEXT — _home  (you own this, not a vendor)
## 1. PRIME STATE
Current workspace: `_home` (lobby at `C:\Sudo_Hatter_Command`)   |   Last session: 202...
```

**Generator vs the home base** (read-only → scratchpad): produced the curated-header scaffold + a clean tree.

**Generator vs ingestion-Pipeline-AC** (read-only → scratchpad, real data) — the headline proof:
```
lines: 192          (the current committed ingestion map is 514)
[34 files: .mdx34 | e.g. PPL_PA_I_A_01_podcast.md]
[48 files: .jsonx48 | e.g. PPL_PA_III_A_01_quiz.json]
[48 files: .jsonx48 | e.g. PPL_PA_III_A_01_rkp.json]
[184 files: .mdx184 | e.g. lesson_pa_i_a_k1.md]
[17 files: .pdfx17 | e.g. 14 CFR Part 67 (2025).pdf]
```
514 → 192 lines; the eliminated lines were pure file enumeration. Code dirs still carry signatures.

## Deviations from plan
- **clean-bmad-workspace went off-limits mid-session** (another team). Part B's lab-prove + B5 sync deferred;
  the generator was instead proven read-only against ingestion. No clean-bmad files touched.
- `prose-formatting.md` received an external frontmatter edit (user/linter) during the session; my
  `_claude_artifacts` fix to its carve-out line is preserved.

## Retire-list (follow-up — NOT done, captured in the standard's appendix)
- `.agents/workflows/autopilot_bmad_dev_loop.md` + `.agents/commands/{autopilot, 1_ccps_update-active-context,
  1_check-for-tech-stack-updates, 1_run-all-tests-back_front, 1_make-workflow-from-chat}` still reference
  `_claude_artifacts/` (and some `@.agent/` singular paths). **Engine-coupled** — the autopilot `.ps1` must be
  checked before moving its artifact paths, or docs/behavior will diverge.
- Per-project rule copies (`_claude_artifacts/`, opposite git policy, `mandatory-session-artifacts.md`, dead
  gates) get reconciled during each project's conversion (separate propagation plan).

## Your Actions

1. **Review** `_docs/workspace-standard.md` — it's the new canonical doctrine.
2. **Clear clean-bmad** when ready (after you've reviewed the other team's work) so I can lab-prove the repo-map
   (generate its `docs/repo-map.md`, wire its SessionStart hook) and then seed the template + `/sync-agents`.
3. **Decide** the autopilot retire-list follow-up (reconcile its `_claude_artifacts/` paths — needs the engine checked).
4. **Git** (home-base repo only; `Projects/` is gitignored from it; I did NOT commit, per policy). The renames are
   already staged by `git mv`. To stage the rest with explicit paths and commit:
   ```
   git add AGENTS.md .claude/settings.json _docs/master-implementation-plan.md _docs/workspace-standard.md \
     .agents/rules/constitution.md .agents/rules/artifacts-always-first.md .agents/rules/prose-formatting.md \
     .agents/rules/git-policy.md .agents/scripts/generate_repo_map.py _routing-canary \
     _artifacts/_home/active-context.md _artifacts/INDEX.md \
     "_artifacts/_home/2026-06-24_workspace-standard-and-repo-map"
   git diff --cached --stat   # verify ONLY these are staged
   git commit -m "feat(home-base): workspace standard + repo-map hybrid + artifacts parity; rename _experiment -> _routing-canary; unify git policy"
   ```
   Then push if you want it on the remote: `git push`.
