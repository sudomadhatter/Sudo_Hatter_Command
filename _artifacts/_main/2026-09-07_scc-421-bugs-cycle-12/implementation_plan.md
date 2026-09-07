# Implementation Plan: SCC-421 Bugs and Updates (Cycle 12)

Execute the consolidated Task lane for **SCC-421** covering subtasks **SCC-425** and **SCC-427**.

## Summary of Startup Work Completed

- **Successor Ticket Cloned**: Cloned `SCC-421` to `SCC-428` (`Bugs and Updates - 2026-09 rolling ticket (cycle 13)`).
- **Baton Handed & Verified**: Verified via JQL search that `SCC-428` holds `running-bug-list` and `SCC-421` holds `bugs-and-updates`.
- **Successor Description & Summary Updated**: `SCC-428` summary bumped to cycle 13; `PREDECESSOR` updated with cycle 12 (`SCC-421`).
- **Ticket Started**: `SCC-421` transitioned from `Rolling Tickets` to `In Progress`.
- **Consolidated Worktree Opened**: Created `.claude/worktrees/scc-421-bugs-cycle-12` on branch `chore/SCC-421-bugs-cycle-12` from `origin/main`; runtime assets linked via `link-worktree-assets.py`.
- **Manifest Initialized**: `task.yaml` initialized with `riders: [SCC-425, SCC-427]`.

---

## User Review Required

> [!IMPORTANT]
> - Subtask **SCC-425** notes that `frontend/e2e/run-e2e.mjs` belongs to `Projects/AGY_AVIATIONCHAT` and lands via an AVCH lane. In this SCC lane, we implement the depth-2 linker fix in `link-worktree-assets.py`, the updated Turbopack warning note, the test suite coverage in `test_link_worktree_assets.py`, and the documentation update in `playwright-in-a-worktree.md`.
> - Subtask **SCC-427** updates `.agents/commands/smh-designer.md` and `docs/_scc_sops_prds/frontend_UI_design_guide.md`, backed by automated verification in `.agents/scripts/tests/test_command_surfaces.py`. The generated launcher skill `.claude/skills/smh-designer/SKILL.md` is synced via `sync-agents.ps1 -NoGlobals` (never hand-edited).

---

## Proposed Changes

### Component 1: Worktree Asset Linker & Playwright Guidance (SCC-425)

#### [MODIFY] [link-worktree-assets.py](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/.agents/scripts/link-worktree-assets.py)
- Raise `find_assets(repo)` search depth to 2 levels:
  - Keep repo root and depth 1 (`child`).
  - Scan depth 2 (`grandchild` inside `child` for non-asset directories).
  - Retain all skip guards: ignore directories named in `asset_names`, `.git`, symlinks, or junctions.
  - Discover `firebase/tests/node_modules` (and similar nested package assets) automatically.
- Update header docstring and comments to document bounded depth-2 walk.
- Update warning text for shared `node_modules`:
  - Name Next.js Turbopack's refusal of symlinks pointing outside the filesystem root (HTTP 500 on all routes).
  - Explicitly direct running `npm ci` in the worktree's `frontend/` for E2E suites.

#### [MODIFY] [test_link_worktree_assets.py](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/.agents/scripts/tests/test_link_worktree_assets.py)
- Add test case verifying depth-2 asset discovery (e.g. `firebase/tests/node_modules`).
- Verify that directory skipping still prevents descending into linked assets or symlinks.
- Verify that the updated warning message naming Turbopack / HTTP 500 fires when `node_modules` is linked.

#### [MODIFY] [playwright-in-a-worktree.md](file:///home/dlohn/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT/.agents/rules/playwright-in-a-worktree.md)
- Add numbered section detailing Next.js Turbopack symlink refusal:
  - Verbatim error messages (`Symlink node_modules is invalid, it points out of the filesystem root...`).
  - Why it lies about its cause (dev server compiles with HTTP 500 on every route, presenting as timeout/blank page rather than build failure).
  - The fix: run `npm ci` in `frontend/` within the worktree.

---

### Component 2: Mobile-First Invariant for Designer Lane (SCC-427)

#### [MODIFY] [smh-designer.md](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/.agents/commands/smh-designer.md)
- In Step 3 ("Load Persistent Rules"), add the two persistent invariants:
  - **Mobile First, Always**: Design, build, and REVIEW the phone render before desktop. Base CSS is phone; `min-width` / Tailwind `sm:`, `md:`, `lg:` enhance out. Never a `max-width` query subtracting from desktop baseline. Expensive effects (blur, mix-blend-mode, large animated layers) take reduced counts/values on mobile. Screenshot mobile first when handing back.
  - **Dual-Viewport Layout Verification**: Layout test suites that measure only one viewport have a blind spot. Any spec asserting geometry runs at both phone (e.g. 375x667) and desktop viewports.

#### [MODIFY] [frontend_UI_design_guide.md](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/docs/_scc_sops_prds/frontend_UI_design_guide.md)
- Add the Mobile-First invariant and dual-viewport testing principle into the house UI standards.
- Include the AVCH-133 real-world examples:
  - Double-line wrapping of confidential chip on phone header.
  - Text clamp overflow edge-to-edge at 375px.
  - Compounded blur + screen blend mode layers overloading mobile GPU.

#### [MODIFY] [test_command_surfaces.py](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/.agents/scripts/tests/test_command_surfaces.py)
- Add test block for SCC-427 asserting that `smh-designer.md` Step 3 carries the Mobile-First invariant.
- Add negative controls (verifying that stripping the invariant or relaxing checks fails).

#### [SYNC] Run Sync-Agents
- Run `pwsh .agents/scripts/sync-agents.ps1 -NoGlobals` to regenerate `.claude/skills/smh-designer/SKILL.md` from the command definition.

---

## Verification Plan

### Automated Tests
- `python3 .agents/scripts/tests/test_link_worktree_assets.py` — verify depth-2 linking and warning output.
- `python3 .agents/scripts/tests/test_command_surfaces.py` — verify `smh-designer.md` invariant check and negative controls.
- `python3 .agents/scripts/tests/test_rule_frontmatter.py` — verify rules inventory and frontmatter integrity.
- `python3 .agents/scripts/tests/run_all.py` — verify full test suite passes.
- `python3 .agents/scripts/task_preflight.py` — verify task preflight passes for `SCC-421` with riders `SCC-425` and `SCC-427`.

### Manual Verification
- Verify `git status` in the worktree is clean of untracked stray files before committing.
- Commit changes with explicit paths keyed to riders (`SCC-425 ... [sop-ok]` and `SCC-427 ... [sop-ok]`).
