---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — clean-bmad .agents conversion + model-agnostic autopilot
  type: walkthrough
  date: 2026-06-24
---

# Walkthrough — clean-bmad-workspace → `.agents` format

## What this did
Converted `Projects/clean-bmad-workspace/` from the old format (`.agent/` singular source +
`.claude/rules/` mirror + fat placeholder `CLAUDE.md`/`AGENTS.md` + dead `/dev /pm /sm` commands) to the
home-base **new format**: `.agents/` (plural) is the single vendored toolkit, `AGENTS.md` is the brain,
`CLAUDE.md`/`GEMINI.md` are one-line adapters. Also made the autopilot loop **doc** model-agnostic and
moved it into the shared toolkit, and captured the whole procedure as a reusable playbook.

## What changed, file by file

**Home-base master (`.agents/`) — additive:**
- `+ .agents/workflows/autopilot_bmad_dev_loop.md` — the rich loop doc, made model-agnostic: new §5a
  "Engine vs harness" (the orchestrator spawns its own `claude` workers, so it's harness-independent and
  stays on Opus 4.8) + an **Engine Adapter** table (Claude proven; opencode = optional seam, *Anthropic
  not OpenRouter*, not built; Antigravity IDE-bound) + §5b the **effort-over-model-downgrade** lesson.

**clean-bmad-workspace:**
- `AGENTS.md` — rewritten as a generic Layer-2 map (MAP/MISSION/SUPPORT, ALWAYS-LOAD, ROUTING TABLE,
  PERSISTENCE). Carries the authoritative **GIT = never commit/push** hard-rule.
- `CLAUDE.md`, `GEMINI.md` — collapsed to thin "Read AGENTS.md" adapters (GEMINI.md now at root).
- `opencode.json` — repointed to `.agents/` with a least-context `instructions` list; project
  `permission` block preserved.
- `.agents/` — fully vendored from master (rules · skills(106) · commands · workflows · bmad · scripts ·
  templates · opencode-agents). `.agents/rules/` = 11 master rules + 6 project rules; `git-closeout-commits.md` dropped.
- `.claude/` — `commands/`(32) + `skills/`(106) refreshed by sync; `.claude/rules/` **deleted**.
- `.opencode/` — `commands/`(31) + `agent/`(13) created by sync.
- `.agent/` (singular) **deleted**; `.gemini/GEMINI.md` **deleted** (notes.md kept); `.antigravity/mcp.json` kept.
- `_01_My/Agentic_Loops/autopilot_bmad_dev_loop.md` — replaced with a pointer to the shared master copy.

## What fought back (the discoveries)
1. **The autopilot script can't move.** `autopilot-dev-story.ps1` resolves repo root as
   `$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path` — hard-bound to `<project>/scripts/`. Moving it
   into `.agents/scripts/` would silently break every path. → Left it project-local; "shared placement"
   delivered via the **doc** (master `.agents/workflows/`) + the `_AP`/`autopilot` commands (already in
   master). Promoting the script is a flagged follow-up (needs a location-independent `$RepoRoot` + a test run).
2. **`.agent/` was NOT fully superseded.** Its `workflows/` held 3 docs not in the master
   (`1_live-user-QA-bugs.md`, `1_looping-dev-cycle.md`, `update_workflow_template_match.md`) — and
   `1_looping-dev-cycle.md` was git-**untracked** (deleting blind = permanent loss). → Preserved all 3 to
   `_preserved-from-old-.agent/` in this folder before deleting. **Your call:** promote any to the master
   toolkit, or leave archived.
3. **The git contradiction.** Removing `git-closeout-commits.md` leaves the vendored `constitution.md:19`
   + `artifacts-always-first.md:137` still saying "you MAY commit at close-out." Resolved for clean-bmad
   via the authoritative `AGENTS.md` override (clean base-rule + project-override precedence). The global
   fix is the flagged follow-up below.

## Deviation from the approved plan
- Plan B1 said "move the script to master `.agents/scripts/`." Changed to "keep project-local" for the
  `$RepoRoot` reason above — a safer call that doesn't risk the fragile CLAUDE-ONLY engine for a routing test.
- Added a "preserve unique files" step (A5b) that the plan didn't anticipate, after finding the 3 unique workflows.

## Verification (actual results)
```
[1] singular .agent/ refs in root files .... none ✓
[2] {{PLACEHOLDER}} in root files .......... none ✓
[3] tool dirs: .claude/commands 32 · .claude/skills 106 · .opencode/commands 31 · .opencode/agent 13 ✓
[4] all 7 AGENTS.md-referenced paths resolve ✓
[5] model-agnostic edits vendored into clean-bmad copy ✓
[6] git-closeout-commits.md absent from vendored rules ✓
```
> Not yet run: the live **opencode routing test** (yours) and the optional `_experiment` cold-agent canary.

## Your Actions
1. **Run the opencode routing test** (the real proof): open an opencode session in
   `Projects/clean-bmad-workspace/` and confirm it boots `AGENTS.md` + `.agents/rules/constitution.md` +
   `karpathy`, sees `.opencode/commands`, and resolves a `.agents/skills` skill.
2. **Decide the 3 preserved workflows** — promote any to master `.agents/`, or leave archived in this folder.
3. **Decide the global git follow-up** — make never-commit the master default (and close-out-commit an
   aviationChat-only override)? This is a 2-line master edit I'll do on your go-ahead.
4. **Commit (you push — agents don't).** Two repos changed:
   ```bash
   # clean-bmad-workspace (its own repo)
   cd "c:/Sudo_Hatter_Command/Projects/clean-bmad-workspace"
   git add AGENTS.md CLAUDE.md GEMINI.md opencode.json .agents .claude .opencode .gemini _01_My
   git add -u .agent   # stage the deletions
   git commit -m "refactor: convert to home-base .agents format (single-source toolkit, thin adapters, never-commit git rule)"
   git push

   # home base (shared master toolkit + artifacts)
   cd "c:/Sudo_Hatter_Command"
   git add .agents/rules .agents/commands/INDEX.md .agents/workflows .agents/skills/INDEX.md _artifacts
   git commit -m "feat(agents): rule frontmatter + INDEX routers; model-agnostic autopilot doc; clean-bmad conversion"
   git push
   ```

## Addendum — rules-structure follow-on pass (same day)
After the conversion, Daniel refactored the master git rule (`git-closeout-commits.md` → `git-policy.md`,
never-commit by default) and began adding `description:` frontmatter to rules. Built on that:
- Added `description:` frontmatter to the remaining 5 master rules — **all 12 now self-route**.
- Added **`INDEX.md` routers** to `.agents/{rules,commands,workflows,skills}/` — "when to use which," scan to
  dispatch (INDEX = router, vs README = explainer).
- **Re-synced clean-bmad** onto the new master: it now carries `git-policy.md` + the INDEXes; its `AGENTS.md`
  git line was simplified to defer to `.agents/rules/git-policy.md`. The earlier override is gone — the git
  contradiction is resolved at the source, not papered over.
