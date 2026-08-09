---
IsArtifact: true
ArtifactMetadata:
  title: .agents/ toolkit floor law — walkthrough
  type: walkthrough
  date: 2026-07-06
---

# Walkthrough — Gave `.agents/` its correct floor law

## What changed & why
The other team deleted `.agents/AGENTS.md` + `.agents/CLAUDE.md`. Verification showed those files held
**only a GitNexus block** (0 lines of routing law, across every git version), so they were generator stubs,
not important instructions. But the workspace standard lists `.agents/` as a **Tier-1 Floor** that must have
a real `AGENTS.md` + adapters — a gap that never got filled. This authors the real thing so an agent entering
the master toolkit knows what it is, how to act, and where every tool lives.

Per Daniel's steer, `.agents/` gets **zero GitNexus content** — it's a markdown toolkit, navigated by its
indexes (and the doc-graph), not the code-graph.

## Files created (4)
- **`.agents/AGENTS.md`** (3,317 B) — Tier-1 floor law: §1 ROOT LAW (this is THE master toolkit, single
  source of authorship; mirrors are downstream; never edit a mirror, edit here then `/sync-agents`), §2
  reading-order, §3 ROUTING TABLE (task → subfolder → its `INDEX.md`: rules/commands/skills/workflows/bmad/
  scripts/templates/hooks/opencode-agents), §4 the authorship+sync law, §5 gates + go-back-up. No GitNexus
  block (a comment records that decision).
- **`.agents/INDEX.md`** (1,484 B) — the inventory: one row per subfolder → what it holds → its dispatch
  `INDEX.md`, linking the four existing sub-INDEXes rather than duplicating them.
- **`.agents/CLAUDE.md`** (248 B) + **`.agents/GEMINI.md`** (257 B) — bare one-line adapters, matching every
  other front door.

## Verification (actual output)
- 4 files present; sizes above.
- **Zero GitNexus**: `gitnexus:start` markers = 0; `indexed by GitNexus` lines = 0.
- Routing coverage: every real subfolder (rules, commands, skills, workflows, bmad, scripts, templates via
  `templates/project-template/`, hooks, opencode-agents) named in the routing table + inventory.
- Adapters both point to `AGENTS.md`.

## Notes
- **Propagation:** these live *inside* `.agents/`, so `/sync-agents` will additively vendor them into every
  `Projects/<name>/.agents/` on the next run — same toolkit law everywhere.
- **Why the stubs existed / how to avoid:** the GitNexus CLI's `upsertGitNexusSection()` auto-creates
  `AGENTS.md`/`CLAUDE.md` at any root it indexes. `.agents/` was once indexed as its own `SUDO_COMMAND`
  graph (via `analyze --skip-git`, to bypass GitNexus's dot-folder skip), which minted the stubs. Prevention
  = don't re-run that index against `.agents/`; if you ever do, pass `--skip-agents-md` (or drop a
  `.agents/.gitnexusrc` with `skipAgentsMd:true`). Guard not added yet — pending Daniel's call (keep the
  folder config-free vs. belt-and-suspenders).

## Task Checklist
- [x] Verify what the deleted files were (GitNexus stubs, 0 floor-law lines)
- [x] Confirm `.agents/` is a Tier-1 Floor per `workspace-standard.md:77`
- [x] Author `.agents/AGENTS.md` (floor law, no GitNexus)
- [x] Author `.agents/INDEX.md` (inventory linking sub-INDEXes)
- [x] Author `.agents/CLAUDE.md` + `.agents/GEMINI.md` adapters
- [x] Verify: files present, zero GitNexus, routing coverage, adapters
- [ ] `.agents/.gitnexusrc` guard — deferred to Daniel's decision
- [ ] Follow-ups: `workspace-structure` skill + master-implementation-plan.md update + lobby/AGY GitNexus→own-file

## Your Actions
Commit on the lobby repo (`main_debug`), explicit paths (the deletions are now replaced by real files):
```bash
git add .agents/AGENTS.md .agents/INDEX.md .agents/CLAUDE.md .agents/GEMINI.md _artifacts/_main/2026-07-06_agents-folder-floor-law/ _artifacts/INDEX.md
git commit -m "feat(.agents): author real Tier-1 toolkit floor law (AGENTS.md + INDEX.md + adapters), replacing deleted GitNexus stubs"
```
Then, to propagate the toolkit law into every project's vendored `.agents/`: run `/sync-agents`.
I ran no git.
