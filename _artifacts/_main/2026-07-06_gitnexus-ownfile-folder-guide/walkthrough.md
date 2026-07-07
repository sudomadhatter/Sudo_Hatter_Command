---
IsArtifact: true
ArtifactMetadata:
  title: GitNexus → own file + pointer (×3) + living-template rule + Fresh audit — walkthrough
  type: walkthrough
  date: 2026-07-06
---

# Walkthrough — GitNexus out of the front door (×3), living-template rule, Fresh clone-audit

## What changed & why
Per Daniel's preference ("GitNexus → its own file + a pointer, never cluttering AGENTS.md"), moved the inline
GitNexus block out of the front door in **all three** repos, added a **rule** that keeps Fresh (the living
template) current, and **audited Fresh for clone-readiness**.

### GitNexus → `docs/gitnexus.md` + one-line pointer (lobby · AGY · Fresh)
- **Lobby**: created `docs/gitnexus.md` (block + scope note); replaced the ~50-line block in `AGENTS.md` with a
  2-line pointer. **AGENTS.md 16,034 → 9,610 B** over the session (−40%).
- **AGY**: created `Projects/AGY_AVIATIONCHAT/docs/gitnexus.md`; replaced its block with a pointer + fixed the
  §3 "see the GitNexus section" reference to point at the new file. **AGENTS.md 13,554 → 10,125 B.**
- **Fresh (ready scaffold)**: Fresh has no code to index, but it's the clone-me skeleton, so it's pre-wired —
  created a **ready-template** `docs/gitnexus.md` (a "not indexed yet; when this becomes a real project run
  analyze + add `.gitnexusrc skipAgentsMd`" note + `<PROJECT>` placeholders) and added the pointer to its
  `AGENTS.md`. Safe because we already set `skipAgentsMd` on lobby/AGY so the generator won't re-inject.

### `living-template-sync` rule (so Fresh-propagation is automatic)
`.agents/rules/living-template-sync.md` + INDEX row + a `fresh-workspace-living-template` memory. It fires on
any shared-rule / front-door-pattern / folder-convention change at the home base: `.agents/**` rides
`/sync-agents`; front-door + structure changes (NOT synced) must be hand-mirrored into Fresh. Kept generic (no
"Daniel" in the rule body, per `no-personal-name-in-directives`).

## Verification (actual output)
- `gitnexus:start` markers in the 3 `AGENTS.md`: **0 / 0 / 0** (block gone everywhere).
- `docs/gitnexus.md` pointer present in all 3; `docs/gitnexus.md` file present in all 3 (lobby 4,234 B / AGY
  3,804 B / Fresh 3,389 B).
- `living-template-sync.md` rule present + 1 INDEX row.
- No AGY product terms (AviationChat/Sully/Igor) in Fresh AGENTS.md: **0**.

## Fresh clone-readiness audit — 2 findings
**GOOD:** front-door files present (AGENTS/CLAUDE/GEMINI + docs/repo-map + docs/workspace-standard +
docs/gitnexus scaffold); generic (no product leak); root `INDEX.md` absent is correct (workspace roots use
`AGENTS.md`, not a root INDEX).

- **FINDING 1 — Fresh's vendored `.agents/` is stale (BLOCKER for "up to speed").** It's missing the new
  toolkit floor law (`.agents/AGENTS.md`, `.agents/INDEX.md`) and the `living-template-sync` rule. **Fix: run
  `/sync-agents`** — it additively vendors master `.agents/` into Fresh (and AGY). Until then, Fresh's toolkit
  is behind.
- **FINDING 2 — stale name "clean-bmad-workspace" in 13 files** (incl. both adapters' titles, `AGENTS.md`
  title + an `_artifacts/clean-bmad-workspace/` path, `docs/repo-map.md`). The folder is `Fresh_Workspace_BMAD`
  but the content still says the old name. For a clone-me skeleton this is a wart — a cloner has to hunt-replace
  it. **Recommend:** convert the identity to a clear placeholder (e.g. `<PROJECT_NAME>`) so clone+rename is a
  single mechanical find-replace. (Pre-existing; not introduced here — surfaced by the audit.)

## Task Checklist
- [x] Lobby / AGY / Fresh: GitNexus block → `docs/gitnexus.md` + pointer
- [x] AGY §3 "GitNexus section" reference repointed to `docs/gitnexus.md`
- [x] `living-template-sync` rule + INDEX row + memory
- [x] Verify changes landed (block gone ×3, pointers in, byte wins)
- [x] Audit Fresh for clone-readiness → 2 findings
- [ ] **Run `/sync-agents`** to vendor the new `.agents/` law into Fresh + AGY (Finding 1)
- [ ] Decide Finding 2 (placeholder-ise Fresh's stale name) — awaiting Daniel
- [ ] Follow-ups: `workspace-structure` skill + `master-implementation-plan.md` folder-org section

## Update — follow-ups completed (same session)
- **Fresh renamed** `clean-bmad-workspace` → `<PROJECT_NAME>` across front-door + docs + `pyrefly.toml` +
  `_artifacts/` + `_my_resources/` (Daniel: "reset them all"). Clone = one find-replace. (`pyrefly.toml` still
  has a stale *root* path `c:\Sudo_Hatter_Command\…` — `python_inter_venv_fix` territory, fixed on clone.)
- **`workspace-structure` skill** created (`.agents/skills/workspace-structure/SKILL.md` + skills INDEX row) —
  thin decision guide over `docs/workspace-standard.md`, auto-surfaces on reorg tasks.
- **`/sync-agents` drift-check** added: on a lobby sync it flags when Fresh's front-door pattern lags (deterministic
  detection replaces "remember to update Fresh"). **`living-template-sync` rule slimmed** to the reconcile-judgment.
- **master-implementation-plan.md** §9 "Files & folders organization strategy" added.
- **`/sync-agents` RAN** (lobby + AGY + Fresh) — Finding 1 CLOSED: `.agents/AGENTS.md`/`INDEX.md`,
  `living-template-sync`, and `workspace-structure` now vendored into AGY + Fresh (verified present ×3). Drift-check
  reported **`Fresh living-template check OK`**. Globals refreshed (opencode 43 / antigravity 23) — restart opencode.

## Your Actions
**1. Run `/sync-agents`** — closes Finding 1 (propagates `.agents/AGENTS.md`, `.agents/INDEX.md`,
`living-template-sync.md` into every project incl. Fresh).

**2. Commit (explicit paths, all `main_debug`):**
```bash
# lobby
git add AGENTS.md docs/gitnexus.md .agents/rules/living-template-sync.md .agents/rules/INDEX.md _artifacts/_main/2026-07-06_gitnexus-ownfile-folder-guide/ _artifacts/INDEX.md
git commit -m "refactor(front-door): GitNexus block -> docs/gitnexus.md + pointer; add living-template-sync rule"
# AGY
cd Projects/AGY_AVIATIONCHAT && git add AGENTS.md docs/gitnexus.md && git commit -m "refactor(front-door): GitNexus block -> docs/gitnexus.md + pointer" && cd ../..
# Fresh
cd Projects/Fresh_Workspace_BMAD && git add AGENTS.md docs/gitnexus.md && git commit -m "chore(front-door): pre-wire GitNexus docs/gitnexus.md scaffold + pointer" && cd ../..
```
I ran no git.
