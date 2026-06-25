# Walkthrough — Home-base maps refresh · GitNexus on the lobby · open_tasks as "what's next"

**Workspace:** `_home` (Sudo_Hatter_Command) · **Date:** 2026-06-25 · **Status:** done (handoff)
**Plan:** `implementation_plan.md` (this folder) — approved with: scope exclusions confirmed, Approach **A** (marker-file), alias **`SUDO_HATTER_COMMAND`**, agent runs `analyze`. Guide-update in `_my_resources/` approved separately.

## TL;DR
All asks done. **FINAL GitNexus state: ONE lobby index `SUDO_COMMAND` = the command center** — all of `.agents/` (rules · workflows · commands · skills · scripts, ~17k nodes), rooted directly at `.agents/` (`--skip-git`) to beat the dot-folder skip. (Got there via revisions: thin portfolio map → two indexes → collapsed to a single `SUDO_COMMAND` per Daniel — "replace the old with the new, name it SUDO_COMMAND.") `_my_resources/open_tasks/` is wired as the read-only "what's next" source. Maps have no drift. Also fixed the self-audit `_AP` `.agent/`→`.agents/` ref and **surfaced ~50+ more dangling `.agent/` refs** across the toolkit (flagged for a dedicated pass). **One surprise:** commit `8a40c0f` landed on `origin/main` mid-session bundling my first-pass repo edits with the prior self-audit work — I did not run git (see §Git).

## Task 1 — Maps up to date
- Verified **no drift**: `_docs/repo-map.md` AUTO body regenerates byte-identical; the SessionStart drift checker prints nothing; `router.md` lists all 7 `Projects/`.
- The real map edits were the ones Tasks 2 & 3 introduced (below). Regenerated the AUTO body after those edits (curated header preserved) → drift check exit 0, no nags.

## Task 2 — GitNexus on the lobby (infra in, project files out)
- **NEW `c:\Sudo_Hatter_Command\.gitnexusignore`** — scopes the lobby graph. Excludes `_artifacts/`, `_my_resources/`, `.claude/`, `.opencode/`, `.vscode/`, build junk. For `Projects/`: `Projects/*/**` excluded, with `!Projects/*/{AGENTS,CLAUDE,GEMINI,README}.md` re-included so each project surfaces as ONE node.
- **`.gitignore`** — added `**/.gitnexus/` (index folder is disposable, never committed). Verified ignored.
- **Indexed** (I ran it): `$env:GITNEXUS_NO_GITIGNORE="1"; gitnexus analyze "c:\Sudo_Hatter_Command" --index-only --name SUDO_HATTER_COMMAND -f`
  - `GITNEXUS_NO_GITIGNORE=1` so the lobby `.gitignore`'s `/Projects/` rule doesn't pre-exclude the tree (scope lives in `.gitnexusignore`).
  - `--index-only` so it did **not** inject a GitNexus section into the curated AGENTS.md/CLAUDE.md or the synced `.claude/` mirror (deliberately unlike the per-project indexes).
- **Verified via cypher** (`repo: SUDO_HATTER_COMMAND`):
  - All **7 projects present** — aviationChat-AGY, clean-bmad-workspace, ingestion-Pipeline-AC, jetChat-AGY (markers); B&L WorldWide, NEXGen Films, openCode (README). **Zero project source files.**
  - Lobby infra docs indexed (`_docs/`, `_routing-canary/`, `_system/`, root contract files).
- **`.agents/` dot-folder skip — first hit, then RESOLVED (see Task 2b).** GitNexus hard-skips dot-folders, so `.agents/` could not ride in the `SUDO_HATTER_COMMAND` portfolio index (verified: 0 files; `!.agents/` negation does not override the skip). Daniel then clarified the toolkit IS the point → solved with a second index rooted directly at `.agents/`.

## Task 2b — Map the command center (Daniel: "all the rules and workflows… the one they all point to… it's the command center")
- **NEW index `SUDO_HATTER_TOOLKIT`**, rooted directly at `.agents/` (which bypasses the dot-folder skip):
  `$env:GITNEXUS_NO_GITIGNORE="1"; gitnexus analyze "c:\Sudo_Hatter_Command\.agents" --skip-git --index-only --name SUDO_HATTER_TOOLKIT -f`
  → **17,153 nodes / 17,405 edges / 15 clusters / 21 flows**. Cypher-verified coverage: rules(61) · workflows(7) · commands(32) · skills(935) · scripts(4). This is the master toolkit, NOT the pointer/mirror copies (`.claude/`/`.opencode/` stay excluded).
- `.agents/.gitnexus/` is covered by the `**/.gitnexus/` ignore (verified).
- **Caveat:** `--skip-git` disables commit-staleness tracking → re-index manually after editing any rule/workflow.
- So the home base briefly had two Tier-2 graphs (portfolio + command center). Docs/memory/guide updated to match.

## Task 2c — Collapse to ONE index named `SUDO_COMMAND` (Daniel: "replace the old with the new… name it SUDO_COMMAND, that's cleaner")
- **Dropped the thin portfolio index entirely** and made the command-center index the canonical lobby index. Sequence: `gitnexus remove SUDO_HATTER_TOOLKIT --force` + `gitnexus remove SUDO_HATTER_COMMAND --force`, then re-analyze `.agents` as `--name SUDO_COMMAND`. (First attempt without `--force` only previewed; and a name collision until the old `SUDO_HATTER_COMMAND` was removed.)
- **Registry is now exactly 3:** `AGY_AVIATIONCHAT`, `RAG_Pipeline_AC`, **`SUDO_COMMAND`** (= `.agents/`, 17,153 nodes; MCP-verified 14 rules + 3 workflows at top level).
- **Deleted the now-dead root `.gitnexusignore`** (it only scoped the removed portfolio index; the active index is `.agents/`-rooted). The orphaned root `.gitnexus/` was removed by `gitnexus remove`.
- **MCP note:** querying the old `SUDO_HATTER_COMMAND` name failed (the running MCP server cached its old root path); the fresh name `SUDO_COMMAND` resolves cleanly. If you rename an index, prefer a new name or restart the MCP server.

## Task 2d — `.agent/` (singular) dangling refs
- Fixed inline: `commands/1_self-audit-stress-test_AP.md` `@.agent/` → `@.agents/` (its sibling already used `.agents/`).
- **Surfaced, NOT mass-edited:** grep `[^s]\.agent/` over `.agents/` = ~50+ refs in `commands/` adapters, `opencode-agents/`, and `skills/`. Nuanced (some are intentional Antigravity-`.agent/` convention docs; some are aviationChat project file:/// links). Needs a deliberate scoped pass — flagged in memory + below.

## Task 3 — `_my_resources/open_tasks/` as the "what's next" source
A standing **read-only** carve-out from the `_my_resources/` do-not-reference rule, scoped to `open_tasks/` only.
- **`router.md`** — new routing row: "What do we do next / open tasks / Daniel's plans & PRPs" → `_my_resources/open_tasks/` (read `todo_list.md` + plans/PRPs; never edit; cross-check vs live files).
- **`_docs/repo-map.md`** — amended the `_my_resources/` PROTECTED row to note the `open_tasks/` exception; added a "To find X" row + a Knowledge-map row.
- **Memory** — updated `my-resources-personal-area-protected.md` with the standing carve-out; updated `tooling-gitnexus-shannon-tracks.md` with the new lobby index; updated both `MEMORY.md` pointer lines.
- Did **not** edit `_my_resources/README.md` (it already frames `open_tasks` as work-context).

## Guide update (approved)
- **`_my_resources/diagrams_guides/system/gitnexus-usage-guide.md`** — added `SUDO_HATTER_COMMAND` to the indexed-repos status, a paragraph on the thin lobby scope + the `.agents/` limitation, and the lobby re-index command in the re-index block.

## Git — READ THIS
- I ran **no** git commands. A commit **`8a40c0f`** ("feat(toolkit): restore self-audit body in master with conditional GitNexus Phase-1; repoint home-base adapter") landed on `main` **and `origin/main`** during the session. It bundled the *previous* session's pending self-audit body work (`.agents/.../1_self-audit-stress-test.md`, the on-hold `gitnexus-audit-integration` artifacts) **with my Task 1/2/3 repo edits** (`router.md`, `_docs/repo-map.md`, `.gitignore`, `.gitnexusignore`) — all in final form. Almost certainly you (or your automation) committed+pushed your backlog plus my work together. **Confirm that was intentional.**
- **Still uncommitted:** the guide (`_my_resources/.../gitnexus-usage-guide.md`) + this session's `_artifacts/_home/2026-06-25_home-base-maps-gitnexus-opentasks/` files + the `_artifacts/INDEX.md` row + `_artifacts/_home/active-context.md`.
- Memory files live under `C:\Users\dlohn\.claude\...` (auto-persisted, outside this repo).

## Your Actions (commit the remainder, when ready)
> Note: `router.md`/`.gitignore`/`_docs/repo-map.md` (+ the now-deleted `.gitnexusignore`) were already in commit
> `8a40c0f`. The later revisions re-modified `_docs/repo-map.md`, **deleted** `.gitnexusignore`, and edited the `_AP`
> adapter — all included below. (`git add` stages the deletion of a tracked file.)
```powershell
cd c:\Sudo_Hatter_Command
git add .gitnexusignore .agents/commands/1_self-audit-stress-test_AP.md _docs/repo-map.md `
        _my_resources/diagrams_guides/system/gitnexus-usage-guide.md `
        _artifacts/_home/2026-06-25_home-base-maps-gitnexus-opentasks/ `
        _artifacts/_home/active-context.md _artifacts/INDEX.md
git commit -m "feat(home): GitNexus lobby index = command center (SUDO_COMMAND); open_tasks 'what's next'; maps; fix self-audit _AP path"
git push
```

## Verify it works (optional, after re-index)
- `gitnexus list` → `SUDO_HATTER_COMMAND` present.
- Ask me "show all my projects" / "what's the lobby graph" → I query `repo: SUDO_HATTER_COMMAND` and return the 7 project nodes.
- Ask me "what do we do next" → I read `_my_resources/open_tasks/todo_list.md` (read-only) and cross-check live files.

## Follow-ups (not done)
- **Dedicated `.agent/` (singular) cleanup pass** across the master `.agents/` toolkit (~50+ refs in `commands/`, `opencode-agents/`, `skills/`). Triage each: broken adapter path → `.agents/`; intentional Antigravity-convention doc → leave; aviationChat project file:/// link → verify/repoint. Use `grep [^s]\.agent/` + GitNexus to sweep; then `/sync-agents` to propagate.
- `SUDO_COMMAND` has no commit-staleness tracking (`--skip-git`) — re-index manually after editing rules/workflows. Could add a SessionStart hook later if churn warrants.
- Re-index `AGY_AVIATIONCHAT` (4 behind) / `RAG_Pipeline_AC` (1 behind) when convenient.
