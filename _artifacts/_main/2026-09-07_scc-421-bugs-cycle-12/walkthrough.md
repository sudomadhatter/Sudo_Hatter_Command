# Walkthrough — SCC-421 (Bugs and Updates Cycle 12) & Riders SCC-425, SCC-427

Parent ticket: [SCC-421](https://sudo-command.atlassian.net/browse/SCC-421)  
Successor rolling ticket: [SCC-428](https://sudo-command.atlassian.net/browse/SCC-428)  
Rider subtasks: [SCC-425](https://sudo-command.atlassian.net/browse/SCC-425), [SCC-427](https://sudo-command.atlassian.net/browse/SCC-427)  
Branch: `chore/SCC-421-bugs-cycle-12`  
Worktree: `.claude/worktrees/scc-421-bugs-cycle-12`  

---

## 1. Overview & Rolling Ticket Baton Swap

Per the rolling ticket protocol and consolidation rules:
1. **Clone & Baton Pass**: Cloned [SCC-421](https://sudo-command.atlassian.net/browse/SCC-421) to [SCC-428](https://sudo-command.atlassian.net/browse/SCC-428).
   - Removed `running-bug-list` label from SCC-421; added `bugs-and-updates`.
   - Transitioned [SCC-428](https://sudo-command.atlassian.net/browse/SCC-428) to `Rolling Tickets` status carrying the `running-bug-list` label.
   - Bumped SCC-428 summary to `Bugs and Updates - 2026-09 rolling ticket (cycle 13)`.
   - Updated SCC-428 description with `PREDECESSOR: https://sudo-command.atlassian.net/browse/SCC-421`.
2. **Consolidated Lane Execution**: Single isolated worktree and branch for the parent Task and rider subtasks (`chore/SCC-421-bugs-cycle-12`).

---

## 2. Changes Made

### SCC-425: Playwright in Worktree Linker & Turbopack Refusal
- [`.agents/scripts/link-worktree-assets.py`](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/.agents/scripts/link-worktree-assets.py):
  - Moved helper `is_link()` above `find_assets()`.
  - Raised search depth in `find_assets()` to 2 (discovers `firebase/tests/node_modules` while strictly preserving skip rules for `.git`, `.venv`, and `node_modules` directories).
  - Updated shared `node_modules` warning banner to explicitly state:
    `Next.js Turbopack refuses symlinked node_modules pointing outside the filesystem root (HTTP 500). The E2E tier must run its own npm ci in this tree.`
- [`.agents/scripts/tests/test_link_worktree_assets.py`](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/.agents/scripts/tests/test_link_worktree_assets.py):
  - Added test block `B5` asserting depth-2 discovery for `firebase/tests/node_modules`.
  - Verified that scanner does not descend into discovered asset directories.
  - Verified warning message for Turbopack symlink refusal.
  - Verified `--unlink` cleanly removes depth-2 links while preserving targets in the source repo.

### SCC-427: Mobile-First Invariant in `/smh-designer` & Frontend UI Guide
- [`.agents/commands/smh-designer.md`](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/.agents/commands/smh-designer.md):
  - In Step 3 ("Load Persistent Rules"), added:
    - **Mobile First, Always**: Design, build, and review the phone render before desktop. Base styles target mobile; `min-width` / Tailwind `sm:` `md:` `lg:` enhance outward. Never `max-width` that subtracts from desktop. Heavy visual effects take lower budgets on base rule. Screenshot mobile first.
    - **Dual-Viewport Layout Verification**: Mandate layout suites test both phone (e.g. 375x667) and desktop viewports.
- [`docs/_scc_sops_prds/frontend_UI_design_guide.md`](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/docs/_scc_sops_prds/frontend_UI_design_guide.md):
  - Added Section 2: "Mobile First, Always (The House Foundation)" featuring the operator quote, core principles, and the AVCH-133 case study (chip wrapping, text clamp overflow, GPU blur overloading).
  - Added "Responsive & Mobile-First Quality" subsection to Section 8 Pre-Delivery UI Quality Checklist (zero horizontal overflow, adaptive wrap & stacking, touch target geometry $\ge 44 \times 44\text{px}$, performance budget on mobile, and dual-viewport verification).
- [`.agents/scripts/tests/test_command_surfaces.py`](file:///home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-421-bugs-cycle-12/.agents/scripts/tests/test_command_surfaces.py):
  - Added block `CS-25` asserting `smh-designer.md` Step 3 carries Mobile-First and Dual-Viewport invariants, `frontend_UI_design_guide.md` carries Section 2 and Section 8 checklist, with anti-vacuity controls.
- Synchronized mirrors via `pwsh .agents/scripts/sync-agents.ps1 -NoGlobals`.

---

## 3. Task Checklist

- [x] Clone SCC-421 to successor SCC-428 and update summary to Cycle 13
- [x] Transition SCC-428 to `Rolling Tickets` and assign label `running-bug-list`
- [x] Transition SCC-421 to `In Progress` with label `bugs-and-updates`
- [x] Set up worktree `.claude/worktrees/scc-421-bugs-cycle-12` and link assets
- [x] Author and approve `implementation_plan.md`
- [x] Implement SCC-425 depth-2 asset linking and Turbopack symlink refusal warning
- [x] Implement SCC-427 `/smh-designer.md` Step 3 invariants and frontend guide sections
- [x] Synchronize agent mirrors and launcher skills
- [x] Add automated unit tests (`test_link_worktree_assets.py` B5, `test_command_surfaces.py` CS-25)
- [x] Verify full test suites (`test_link_worktree_assets.py`, `test_command_surfaces.py`, `test_rule_frontmatter.py`, `test_check_maps.py`, `test_git_hooks.py`)
- [x] Explicit-path commits for SCC-425 and SCC-427
- [x] Update `_artifacts/_main/INDEX.md` with session row

---

## 4. Evidence & Commits

- **SCC-425 Commit**: `386bf5f0` (`SCC-425 fix(linker): raise find_assets to depth 2 and name Turbopack symlink refusal [sop-ok]`)
- **SCC-427 Commit**: `9556025a` (`SCC-427 docs(designer): add persistent mobile-first invariant and guide [sop-ok]`)

---

## 5. Suite Ledger

| Suite / Test | Result | Notes |
|---|---|---|
| `test_link_worktree_assets.py` | 58/58 PASS | Includes B5 depth-2 linking and Turbopack refusal warnings |
| `test_command_surfaces.py` | 329/329 PASS | Includes CS-25 mobile-first invariants and dual-viewport assertions |
| `test_rule_frontmatter.py` | 30/30 PASS | Frontmatter and tier-1/tier-2 integrity clean |
| `test_check_maps.py` | 37/37 PASS | Depth-3 _artifacts INDEX clean with session row |
| `test_git_hooks.py` | 163/163 PASS | Git hooks and commit-msg enforcement clean |
| `run_all.py` | 81/81 PASS | Measured at `9556025a` via `gate_receipt.py` (`gates/suite.json`) |

---

## Code Review

Verdict: PASS @ 9556025a

review_level: standard
lens_isolation: worktree
review-runtime: fan-out
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted: 5/5
lenses_na: none
findings: 0 decision · 0 patch · 0 defer
dispositions: per-lens: blind-hunter=0/0/0 · edge-case-hunter=0/0/0 · literal-correctness-hunter=0/0/0 · acceptance-auditor=0/0/0 · test-adequacy-auditor=0/0/0
drift: undeclared=0 · unimplemented=0 · incomplete=0

- **Review Summary**:
  - `link-worktree-assets.py`: Reordering `is_link` above `find_assets` prevents `NameError`. Depth-2 search properly skips recursion into gitignored assets while allowing submodules and test directories (like `firebase/tests/node_modules`).
  - `smh-designer.md` and `frontend_UI_design_guide.md`: Follow house markdown conventions and cleanly encode the operator's mobile-first directives without breaking existing command shapes or workflows.
  - Tests include strong anti-vacuity assertions and negative controls.

### Step 0.7 — re-derivation
1. What moved: `origin/main` is level with this lane; no concurrent landings.
2. What it changes here: no conflicting changes to `link-worktree-assets.py` or `/smh-designer.md`.
3. What was re-measured: full test suite re-verified clean via `gate_receipt.py` @ `9556025a`.

---

## Your Actions

None required. All changes are verified and ready for task close-out.
