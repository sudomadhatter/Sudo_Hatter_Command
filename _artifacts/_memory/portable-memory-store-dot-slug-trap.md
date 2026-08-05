---
name: portable-memory-store-dot-slug-trap
description: Auto-memory lives in the repo at _artifacts/_memory/ via a junction; the slug rule turns '.' into '-' too, and omitting that silently strands every memory.
metadata:
  type: project
---

Claude Code auto-memory is no longer machine-local. The canonical store is **`_artifacts/_memory/` inside
the repo**, and `~/.claude/projects/<slug>/memory/` is a junction (Windows) / symlink (macOS) pointing at
it. Memory therefore commits and travels with every other tracked file. Linked with
`.agents/scripts/link-memory.ps1` / `.sh` — dry-run by default, `-Apply` / `--apply` to write.

The lobby was seeded from this machine on **2026-08-04** (126 files). The other machine was told to hold
its stale set back rather than seed, so the lobby's canonical store is authoritative from that date.

**The `<slug>` rule is `: \ / _ .` → `-` — the dot is in the set.** This home base sits under `.gemini`,
so the true slug carries a *double* dash there:

    c:\Users\dlohn\.gemini\...  ->  c--Users-dlohn--gemini-...
                    ^ '\' then '.'        ^^ both dashes

**Why:** the first cut of both scripts used `[:\\/_]`, without the dot. That computes `-.gemini`, which
matches no directory on disk. The linker then concluded there was no local store, created a brand-new
empty slug dir, junctioned *that*, and printed a success message — while all 126 real memories sat
stranded in the untouched original. A data-loss bug wearing a green check, in the very tool built to
prevent data loss. Caught on the seeding run before `-Apply`.

**How to apply:**
- Write memories to `_artifacts/_memory/` (or through the junction — same thing). Never hand-copy into
  `~/.claude/...`.
- Before trusting any linker run, read its `slug :` line against `ls ~/.claude/projects/`. If the file
  count under `SEED`/`canonical` is not the count you expect, **stop** — a wrong slug reports as a clean
  first-time link, identical to a real one.
- Dry-run always; back the store up before an `-Apply` that moves files.
- The two scripts are **twins by contract** — fix one, fix the other, and re-copy to the vendored
  `.agents/scripts/` in every maintained project ([[maintained-projects-allowlist]]), each of which is
  its own repo.
- Never merge two machines' stores automatically. Second machine in gets its local set moved aside to
  `memory.local-backup-<timestamp>`; a human reconciles.
- On rename day the slug changes — re-run the linker to re-point. Nothing moves, because the data was
  never in the slug dir. See [[env-migration-kit]].

Related: [[artifact-budgets-are-scoped-not-universal]] for what belongs in memory vs. an artifact.
