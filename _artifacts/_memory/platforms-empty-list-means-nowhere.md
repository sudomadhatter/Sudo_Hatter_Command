---
name: platforms-empty-list-means-nowhere
description: "`platforms: []` in a .agents/commands/*.md frontmatter syncs the command to ZERO platforms — it is the one value that means \"never surface this\", and omitting the key entirely is what means \"all four\"; a command written this way exists on disk, is INDEXed, and is silently untypeable everywhere."
metadata: 
  probe: "test -e .agents/scripts/sync-agents.ps1"
  node_type: memory
  type: project
  originSessionId: 27c1ed6c-690d-4f25-91b4-b537755e900d
  modified: 2026-07-25T17:27:33.710Z
---

In `.agents/commands/*.md`, the `platforms:` frontmatter controls sync reach. The trap:

| Frontmatter | Reach |
|---|---|
| key **absent** | **universal — all four** (claude, opencode, antigravity, codex) |
| `platforms: [claude, opencode]` | just those |
| **`platforms: []`** | **NOWHERE** — "documentation, not an invocable command" |

`Get-CommandPlatforms` in `.agents/scripts/sync-agents.ps1` returns the matched empty array, so the
`-contains $Platform` test fails for every platform and the file is copied to zero invocable dirs.

**Why it fools you:** an author who doesn't know the valid values writes the empty list as a
placeholder — it looks like "unset". It is the exact opposite of unset. Observed 2026-07-25: a
`/update-personal-sprint-map` command authored in Antigravity had `platforms: []`. It reached
`.agents/commands/` in the lobby *and* both maintained projects (the vendor step is a whole-tree
robocopy that ignores `platforms:`), and it was registered in **both** INDEX.md files — so it looked
completely installed. It was typeable on **zero** platforms, including the one that wrote it.

**Tell:** `grep -c '<command-name>' .agents/.sync-manifest.json`. The manifest records what the sync
actually wrote. Zero hits = it has never landed anywhere, regardless of what's in `.agents/commands/`.
Presence in `.agents/commands/` and INDEX.md proves nothing.

**Fix:** set a real list (or delete the key), then `/sync-agents -Maintained` — a lobby-only sync
updates the lobby + machine-globals but leaves the projects on their stale vendored copy.

**⚠️ WhatIf hides the project half.** In `-WhatIf` the vendor robocopy doesn't run, so each project's
`Sync-CommandDir` still reads its *old* vendored file and the dry-run shows no project destinations.
Absence of project copies in a dry-run is an artifact, not a finding — verify on disk after the real run.

Related: [[bmad-wrappers-are-opencode-only-bridges]] (legit narrow `platforms:` pins),
[[one-door-per-platform-per-command]] (manifest-driven purge), [[antigravity-uses-workflows-not-commands]].
