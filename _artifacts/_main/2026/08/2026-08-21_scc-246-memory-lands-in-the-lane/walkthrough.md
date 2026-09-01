---
IsArtifact: true
ArtifactMetadata:
  title: SCC-246 — memory lands on the lane
  type: walkthrough
  date: 2026-08-21
---

# SCC-246 — a memory written during a lane lands ON THE LANE

**Lane:** `chore/SCC-246-memory-lands-in-the-lane`, cut from `origin/main` @ `2a20019`.

## The mechanism

`~/.claude/projects/<slug>/memory` is a per-machine symlink to `<repo>/_artifacts/_memory` in the
**main** working tree — hardcoded. An agent working in `.claude/worktrees/<lane>/` therefore writes
its memory into `main`'s tree. The memory never rides that lane's PR; it sits uncommitted in the
shared checkout until a later session finds it and cleans it up as a separate chore.

**Measured 2026-08-21:** after SCC-201 closed, `main` carried three untracked memory files and a
modified `MEMORY.md` from two different sessions.

## Why existing law did not cover it

`AGENTS.md` §7 and the close-out door both say another session's memory is *"parked or left, never
swept, deleted, or committed under this task."* That is correct for **someone else's** memory — and
it left **your own** homeless. No sentence told a lane agent where to put the memory it had just
written, so the default was "leave it", forever, in `main`.

## What changed

`AGENTS.md` §7 carries the four-step lane write path: write it → copy it into the worktree's own
`_artifacts/_memory/` → restore the shared checkout (**only** the files you wrote; `cmp` first,
never `git clean`) → commit on the lane. The close-out door's `sync` row now splits dirty memory by
**authorship**, not tidiness.

⛔ **The other-session protection is unchanged** and restated in both places.

## Evidence

| Gate | Result |
|---|---|
| `run_all.py` (bare) | **40/40, exit 0** |
| mirror regenerated | `/smh-sync-agents`, no hand edits |

## Your Actions

- [ ] **The merge itself** — lands via this branch's PR
