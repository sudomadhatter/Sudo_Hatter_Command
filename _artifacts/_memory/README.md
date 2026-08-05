# `_artifacts/_memory/` — the portable auto-memory store

This directory is the **canonical** home of Claude Code's auto-memory for this workspace. The harness
writes memory to `~/.claude/projects/<slug>/memory/`, which is **not** a repo and never leaves the machine
that wrote it. A junction (Windows) / symlink (macOS) points that path here, so memory lives in git and
travels with every other tracked file.

Link it with **`.agents/scripts/link-memory.ps1`** (Windows) or **`link-memory.sh`** (macOS). Both are
dry-run by default; add `-Apply` / `--apply` to write. `-All` / `--all` does the lobby plus every project
in `.agents/maintained-projects.txt`.

## Why this exists

`<slug>` is **derived from the absolute path** of the workspace — `:` `\` `/` and `_` all become `-`. That
makes the harness's own store fragile in three ways, two of which had already cost real data before this
was set up:

| Axis | What breaks | Evidence |
|---|---|---|
| **Machine** | `~/.claude` isn't a repo, isn't a link, isn't cloud-synced — memory simply never leaves the box | verified 2026-08-04 |
| **Rename** | renaming the home base or a project changes the slug, orphaning everything under the old one | **15 files stranded** under two dead slugs from past renames |
| **Case** | on a case-insensitive volume the two spellings collide rather than fragment | handled by reusing the existing dir, never creating a second |

`rename-fix.ps1` repairs `~/.claude/settings.json` paths on rename day but knows nothing about
`projects/<slug>/memory/`. That gap is what stranded the 15.

## The rules

- **Memory files live here; the harness path is only a link.** Never hand-copy memories into
  `~/.claude/...` — write them here (or through the link, which is the same thing).
- **Never merge two machines' stores automatically.** If canonical already holds memories and a machine's
  local store holds its own, the script moves the local set aside to
  `memory.local-backup-<timestamp>` and reports it. It deletes nothing and guesses nothing — a human
  reconciles.
- **First machine seeds.** Whichever machine links first moves its memories in. Every later machine finds
  canonical populated and takes the backup path. **So link the machine with the *newest* memories first.**
- **`README.md` and `.gitkeep` are scaffolding, not memories.** The scripts exclude them when counting, so
  their presence never makes an empty store look populated (which would send the first machine down the
  backup path and strand the very files it was meant to rescue).
- **On rename day, re-run the linker.** The slug changes; the junction must be re-pointed. Nothing needs
  to move, because the data was never in the slug directory to begin with — that is the whole point.

## Related

- `docs/workspace-standard.md` — PATH CONTRACT row + the upkeep note
- `_my_resources/migrations/INDEX.md` — new-machine setup (§1) and rename day (§3)
- `.agents/rules/artifacts-always-first.md` — what belongs in memory vs. an artifact
