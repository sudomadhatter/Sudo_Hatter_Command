# Walkthrough — SCC-350 · The Wonderland team: six Zoo Code seats over the built-in slugs

**Lane:** `chore/SCC-350-wonderland-team` (consolidated, no subtasks) · **Ticket:** [SCC-350](https://sudo-command.atlassian.net/browse/SCC-350) (parent SCC-33) · **Close door:** `/smh-close-task-merge-tree`

## What shipped

The Zoo Code mode picker is now the operator's org chart. Six seats replace Zoo's five hard-coded
built-in modes (a same-slug custom mode replaces a built-in wholesale — verified against the
v3.80.1 compiled bundle before the plan was written) plus one new `designer` slug:

🫖🐰 March Hare — TEAM LEAD (`orchestrator`) · ⏰🐇 White Rabbit — PM (`architect`) · 🔨🪚
Carpenter — ENGINEER (`code`) · 🦋 Caterpillar — DESIGNER (`designer`) · 😼 Cheshire Cat — TESTER
(`debug`) · ♥️👑 Queen of Hearts — QA (`ask`, **no `edit` group — the platform strips her pen**).

- **Part A — seat masters** (`.agents/commands/smh-team-*.md`, 6 files): identity, doors, refusals,
  routing law per seat. Frontmatter carries `mode-name` / `mode-slug` / `mode-groups` — the ONE
  source the generator and the tests both read. `platforms: [zoo]` → one `.roo/commands/` launcher
  each, nothing on other platforms. March Hare carries the delegation protocol (`new_task` per
  seat, chosen by `whenToUse`; `switch_mode` for handoffs; ceiling = merge-ready).
- **Part B — generator** (`sync-agents.ps1` Sync-ZooSurfaces §3): `$personas` → `$seats`; names,
  groups and whenToUse read from master frontmatter (UTF-8 markdown) so the ps1 stays pure ASCII
  (Windows PowerShell 5.1 mangles no-BOM UTF-8 source); quoted YAML names; per-seat groups; the
  marker-guarded prune retired the five old persona dirs automatically.
- **Part C — team rule** (`.agents/rules/zoo-team.md`): roster map, hand-off order, cicd-vs-smh
  routing law, manuals, Sudo_Hatter profile by NAME only, the two per-machine auto-approve tiles.
  Rides the `.roo/rules/` copy list (fourth copy, Zoo-wide, frontmatter-stripped) — deliberately
  NOT a `CLAUDE.md`/`GEMINI.md` `@` import (Zoo-team law, not house floor).
- **Part D — worktree visibility travels**: tracked [.vscode/settings.json](../../../.vscode/settings.json)
  now sets `git.detectWorktrees: true` (was user-settings-only on the Mac; the PC and any VS Code
  profile inherit it via git).
- **Part E — tests, RED first**: new [test_zoo_team.py](../../../.agents/scripts/tests/test_zoo_team.py)
  — 7 fixture cases proving the validator fires (QA-with-edit, lowercase role, missing emoji,
  ALL-CAPS name, wrong slug set, missing base groups) + 7 live-tree checks (team law, master
  currency, QA prose refusal, dir prune, team-rule currency, detectWorktrees). Seen RED before the
  build: `8/14 passed`, all six live checks failing for the right reasons (transcript below).
  `test_settings_allowlist.py` E2/E4/E10 rewritten from personas to seats (declared amendment).
- **Part F — sync run**: regenerated `.roomodes` (6 seats), 6 seat rule dirs, `.roo/rules/zoo-team.md`,
  6 zoo launchers, manifest. `39 launchers … .roomodes (6 team seats); floor + team rules`.

## Evidence

- RED first (pre-build): `test_zoo_team.py` → `-- 8/14 passed --` with B2–B7 failing
  (`slug set ['analyst','architect','dev','pm','tech-writer','ux-designer'] != law […]`, missing
  seat dirs, no team rule, `detectWorktrees value=None`).
- GREEN at tip: `test_zoo_team.py` → `-- 14/14 passed --`.
- Full armed suite **bare**: `python3 .agents/scripts/tests/run_all.py` → `64/64 files passed`,
  exit 0, at `c13e397`, clean tree.
- Sync output: `zoo surfaces -> 39 launchers in .roo/commands/; .roomodes (6 team seats); floor +
  team rules in .roo/rules/`.

## Recorded decisions (deviations from the approved plan, each forced by an armed gate)

1. **Seat masters are `smh-team-*`, not `team-*`.** `workflow_lint.py` (lines 288–317) enforces a
   CLOSED naming law — `cicd-`/`smh-`/`sentry-` or a listed vendor bridge; widening the vendor list
   is explicitly forbidden in its own comment. The seats are house commands, so they took the
   `smh-` family. Change-set paths updated in the plan (rename only, zero content change).
2. **`run_all.py` was declared EDIT and needed none** — it auto-discovers `test_*.py` (its
   docstring line 11). Declared-set bullet amended before approval #2.
3. **Three undeclared files edited, each demanded by an armed gate at build time:**
   `test_twin_parity.py` (A1 requires every `smh-*` command pinned or recorded `NOT_PAIRED` — six
   seat records added with reasons), `.agents/rules/INDEX.md` (`test_rule_frontmatter` requires a
   Load row for `zoo-team.md`), `_artifacts/_main/INDEX.md` (`check_maps` F2 requires the session
   row). Inventory/ledger churn, no design freedom; the suite named each one.
4. **Mode names live in master frontmatter, not the ps1 table** — the ps1 is deliberately pure
   ASCII (zero non-ASCII bytes before this lane; PS 5.1 reads no-BOM UTF-8 as ANSI and would mangle
   every emoji on the PC). The generator reads the masters with explicit `-Encoding UTF8`.
5. **The maps hook refused the first commit** until the SOP named the six `/smh-team-*` doors —
   the operator page now lists them beside the team paragraph.

## Task Checklist

- [x] 1 Master roster: six seat masters with identity/doors/refusals (A) — test B3/B4
- [x] 2 Generator emits the roster over the five built-in slugs + designer (B) — test B2/E2
- [x] 3 Team rule synced to .roo/rules/ (C) — test B6
- [x] 4 QA edit-stripped mechanically; March Hare delegation protocol (A/B) — test B2 + fixture A2
- [x] 5 Seat skill bundles (Caterpillar: emil-design-eng + apple-design; Cheshire Cat: TEA doors) — masters name them
- [x] 6 Tracked git.detectWorktrees (D) — test B7
- [x] 7 RED-first tests + SOP same commit (E) — transcripts above; sop gate satisfied at `c13e397`
- [x] 8 Sudo_Hatter profile referenced by name only — zoo-team.md; no key material anywhere in the diff
- [ ] The merge itself — lands via this branch's PR

## Your Actions

- [ ] **See your team:** reload VS Code (or restart Zoo Code) in this workspace after the merge —
  the mode picker shows the six seats in place of Zoo's five stock modes.
- [ ] **Arm the March Hare (per machine):** tick **Mode switching** and **Subtasks** in Zoo's
  Auto-Approve panel so `new_task` delegation runs unattended.
- [ ] **Pin the Sudo_Hatter profile (per machine):** in Zoo's settings, set the Sudo_Hatter
  configuration profile as the active/default profile for the modes (extension state — git cannot
  carry it).
- [ ] **PC pickup:** pull `main` after the merge; `.roomodes`, the rules and `git.detectWorktrees`
  all arrive via git — only the two per-machine toggles above need hands.
