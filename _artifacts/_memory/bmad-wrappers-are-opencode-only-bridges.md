---
name: bmad-wrappers-are-opencode-only-bridges
description: "BMAD command wrappers (testarch-*, bmad personas) should be platforms:[opencode] — Claude/Antigravity get the bmad-* skill natively; opencode has no native skills so the wrapper is its only bridge."
metadata: 
  node_type: memory
  type: project
  originSessionId: 9bdcb3af-df06-4250-b3ba-1a751b5531ac
---

BMAD installs its own skills (`bmad-agent-dev`, `bmad-tea`, `bmad-testarch-*`, `bmad-help`, …) natively only to its `ides:` list = **claude-code + antigravity**. **opencode is NOT in that list** → opencode has no native BMAD skills (no `.opencode/skills` dir at all).

**Consequence for `.agents/commands/` skill-wrapper stubs** (the `Invoke the \`bmad-X\` skill` one-liners — the 8 `testarch-*` and the 11 personas `dev`/`qa`/`pm`/`analyst`/`architect`/`tea`/`sm`/`tech-writer`/`ux-designer`/`bmad-help`/`bmad-master`): they must be `platforms: [opencode]`.
- **Claude & Antigravity** already surface the real `bmad-*` skill directly → the wrapper is a pure DUPLICATE slash entry there. (Antigravity confirmed: it sees the `bmad-`-prefixed ones, ignores the non-bmad wrapper.)
- **opencode** has no native skill → the wrapper command is opencode's ONLY path to that BMAD capability. Never drop opencode.

So: reach these in Claude via the skill name (`/bmad-agent-dev`, `/bmad-testarch-automate`), not a short alias. Set 2026-07-03; `.agents/commands/` synced, purged the 19 dups from Claude (38→19) + Antigravity global (39→20), opencode unchanged (40).

**Exception — `sudo-*` wrappers stay `[opencode, antigravity]`:** those target CUSTOM (non-BMAD) skills that Antigravity does NOT get natively, so they need the sync's antigravity workflow-mirror path (`.agents/workflows/`). Only genuine BMAD-skill wrappers qualify for `[opencode]`.

The sync ([[toolkit-sync-covers-agents-not-docs]]) already honors `platforms:` frontmatter per-file (`.agents/scripts/sync-agents.ps1` `Get-CommandPlatforms`), so scoping is a one-line frontmatter edit + resync, not a code change. Absent line = universal (all three). Related: [[antigravity-uses-workflows-not-commands]], [[command-center-sudo-skills]], [[sudo-commands-have-ap-twins-that-drift]].
