# Implementation Plan — Make the auto-memory store portable (travel + survive renames)

- **Date:** 2026-08-04
- **Workspace:** home base (lobby) + `~/.claude` (outside the repo)
- **Owner:** Daniel (chair) · engineer: Claude
- **Status:** AWAITING APPROVAL

---

## 1. The problem is bigger than "it doesn't travel"

Claude Code stores auto-memory at `~/.claude/projects/<slug>/memory/`, where `<slug>` is **derived from
the absolute path** of the workspace: `:`, `\`, `/`, and `_` all become `-`. Verified against all five
directories on this machine — the algorithm reproduces every one exactly.

That makes the store fragile on **three** axes, and two have already fired:

| Slug on disk | Decodes to | Files | State |
|---|---|---|---|
| `c--Sudo-Hatter-Command` | `c:\Sudo_Hatter_Command` | **25** | live (this session) |
| `c--AGY-Projects-aviationChat-AGY` | `c:\AGY\Projects\aviationChat-AGY` | **13** | ⚠️ **STRANDED** — path gone (home-base rename) |
| `c--Sudo-Hatter-Command-Projects-aviationChat-AGY` | `c:\Sudo_Hatter_Command\Projects\aviationChat-AGY` | **2** | ⚠️ **STRANDED** — path gone (project rename) |
| `C--Sudo-Hatter-Command-Projects-AGY-AVIATIONCHAT` | current AGY | 0 | live, but note the **capital `C`** |
| `C--Sudo-Hatter-Command-Projects-RAG-Pipeline-AC` | current RAG pipeline | 0 | live, capital `C` |

1. **Machine.** `~/.claude` is a real directory — not a git repo, not a junction, not under OneDrive
   (verified). Nothing carries it between machines.
2. **Rename.** Renaming the home base or a project changes the slug, orphaning everything under the old
   one. **This is why 15 files are already dead** — `rename-fix.ps1` repairs `~/.claude/settings.json`
   paths on rename day but has no idea `projects/<slug>/memory/` exists.
3. **Drive-letter case.** `c--…` and `C--…` are different directories. A session started from a
   differently-cased cwd silently starts a fresh, empty memory.

## 2. The fix

**Canonical memory moves into the repo; the slug directory becomes a junction pointing at it.** Same
pattern as the opencode config junction already in use. Once linked, memory commits and travels with
every other tracked file, and a rename only requires re-pointing the junction — never a data migration.

### Location: `_artifacts/_memory/`

Rationale: `AGENTS.md`'s prime mission already calls `_artifacts/` "the shared memory," so this is where a
reader looks. It adds **no** new top-level folder (no `router.md` row, no repo-map entry, no `AGENTS.md`
tier decision). It is tool-neutral in location — the Claude-specific wiring is the junction, not the path.

Linter impact: none. `_artifacts` is in `DEPTH3_DIRS`, so check 2.5 skips it at level 1; check 7 only
requires an `INDEX.md` in buckets holding **≥2 session-shaped subfolders**, and `_memory/` holds flat `.md`
files with no subdirs. Verified against the current code — it is skipped.

### New scripts: `link-memory.ps1` **+ `link-memory.sh`** (twins, per house convention)

The MacBook Pro means this needs both. `_my_resources/migrations/INDEX.md` already establishes the pattern
and the contract: `Restore-EnvMaster.ps1` / `restore-env-master.sh` are *"twins by contract… verified
byte-identical output"*, with the standing rule **"if either changes, change both."** This pair follows it.

Platform differences, all confined to one step:

| | Windows | macOS |
|---|---|---|
| Link type | **junction** (`New-Item -ItemType Junction`) | **symlink** (`ln -s`) |
| Store root | `%USERPROFILE%\.claude\projects\` | `~/.claude/projects/` |
| Slug source | `C:\Sudo_Hatter_Command` → `C--Sudo-Hatter-Command` | POSIX path, e.g. `/Users/dlohn/Sudo_Hatter_Command` → `-Users-dlohn-Sudo-Hatter-Command` |
| Drive-letter case axis | applies (`c--` vs `C--`) | n/a — no drive letter |

⚠️ **The macOS slug shape is inferred, not verified** — I derived the rule from the five Windows dirs on
this machine and it reproduces all five, but I cannot confirm how a leading `/` renders without seeing a
Mac. **One command on the MacBook settles it before the script is trusted there:**
`ls ~/.claude/projects/`. The `.sh` will compute the slug the same way and *verify the directory it
computed actually exists* before linking, refusing rather than guessing wrong.

Idempotent, and derives everything at runtime so it needs no knowledge of any other machine's paths:

1. Compute the slug from the repo root exactly as Claude Code does (`:` `\` `/` `_` → `-`).
2. Ensure `<repo>/_artifacts/_memory/` exists.
3. If the slug dir is a **real directory with files**, move them into canonical first (never clobber).
4. Replace the slug dir with a junction → `<repo>/_artifacts/_memory/`.
5. `-Adopt <slug>` — fold a stranded slug's files into canonical (skips name collisions, reports them).
6. `-WhatIf` default-safe dry run, mirroring the house convention in `rename-fix.ps1`.

Both drive-letter casings get a junction, closing axis 3.

### Documentation

- **`_my_resources/migrations/INDEX.md`** — new row in §1 (new-machine path: run `link-memory.ps1` after
  cloning) and in §3 (old machine / ongoing: re-run it on rename day). Plus a line in Rules naming the
  slug convention, since that is the thing that keeps biting.
- **`_my_resources/migrations/new_machine-migration-guide.md`** — the actual step, in order.
- **`_my_resources/migrations/rename-fix.ps1`** — its header currently promises it repairs `~/.claude`
  paths. Add the memory-junction step (or, minimally, a pointer to `link-memory.ps1`) so rename day stops
  stranding memory. **This is the change that prevents a fourth stranding.**
- **`_my_resources/migrations/INDEX.md` §2 (macOS notes)** — a row for `link-memory.sh`, and the twin-sync
  rule extended to name this second pair alongside the restore scripts.
- **`docs/workspace-standard.md`** — a PATH CONTRACT row for `_artifacts/_memory/` (both modes) and a short
  note in Part 2 "Context hygiene" that the memory store is a junction/symlink, plus what to do on rename day.

## 3. Two decisions I need from you

**A. The 15 stranded files — adopt or discard?**
`c--AGY-Projects-aviationChat-AGY` (13) and `c--Sudo-Hatter-Command-Projects-aviationChat-AGY` (2) are both
AviationChat memory from before the renames. They may hold facts still true about AGY.
- *Recommend:* **adopt into AGY's canonical store** (`Projects/AGY_AVIATIONCHAT/_artifacts/_memory/`), not
  the lobby's — they were written about that project. I would read all 15 first and report before moving.
- Alternative: leave them; they cost nothing but are invisible.

**B. Does this roll out to the projects too, or just the lobby now?**
AGY and RAG_Pipeline_AC have live (currently empty) slug dirs. Same script serves them.
- *Recommend:* **lobby now, AGY next** — proves the pattern once before repeating it. RAG pipeline last.

## 4. Steps

1. Write `.agents/scripts/link-memory.ps1` (dry-run verified before any write).
2. Create `_artifacts/_memory/`, move the 25 live files in, junction the slug dir, verify a read/write
   round-trip through the junction.
3. Confirm `git status` sees the 25 files as tracked-and-new in the lobby repo.
4. Run `check_maps.py` — confirm `_artifacts/_memory/` triggers no new drift.
5. Update the four docs above.
6. Depending on decision A, read + report the 15 stranded files, then adopt.
7. Close: `walkthrough.md` + `_artifacts/INDEX.md` row + `_main/INDEX.md` row + `active-context.md`.

## 5. Files touched

| File | Change |
|---|---|
| `.agents/scripts/link-memory.ps1` | **new** (Windows) |
| `.agents/scripts/link-memory.sh` | **new** (macOS twin — same contract as the restore-env pair) |
| `_artifacts/_memory/` + 25 `.md` files | **new** (moved from `~/.claude`) |
| `~/.claude/projects/c--Sudo-Hatter-Command/memory` | becomes a junction — **outside the repo** |
| `_my_resources/migrations/INDEX.md` | 2 rows + 1 rule |
| `_my_resources/migrations/new_machine-migration-guide.md` | 1 ordered step |
| `_my_resources/migrations/rename-fix.ps1` | memory-junction step / pointer |
| `docs/workspace-standard.md` | PATH CONTRACT row + upkeep note |

**Risk note.** Step 2 moves real data. The script never deletes a source until the copy is verified, and
I will run `-WhatIf` and show you the output before applying. `_my_resources/` edits are authorized by its
own INDEX ("the operator pointing an agent at this folder IS the instruction") plus your explicit ask.

---

**STOP — awaiting "approved", plus your calls on A and B.**

---

## Audit append — 2026-08-04, seeding run (this machine)

**§1's slug rule was wrong, and it was wrong in the one way that loses data.** The set is
`: \ / _ .` → `-`. The dot was missing.

**How a "verified against all five directories" claim was still false.** Every path in §1's table lives
under `c:\Sudo_Hatter_Command\…` — *not one of them contains a dot*. The sample could not distinguish
"dot is in the set" from "dot is not," so the rule fit all five and was recorded as confirmed. This
machine's home base is `c:\Users\dlohn\.gemini\…`, and that dotted directory is the discriminating case
the other machine never had. The table in §1 is therefore evidence from a different box; it is left as
written for provenance, not as the current state of this one.

**What the bug did.** `c:\Users\dlohn\.gemini\…` slugs to `c--Users-dlohn--gemini-…` — a *double* dash,
one from the `\` and one from the `.`. `[:\\/_]` computes `-.gemini`, matching nothing on disk. The
linker read that as "no local store exists," and its first dry run proposed creating a **new empty slug
dir**, junctioning it, and reporting success — leaving all **126** memories stranded in the untouched
original. Failure and success were indistinguishable in the output: both print "create slug dir" +
"junction". Caught by reading the dry run's file count, which said nothing about 126 files.

**Fixed.**

| File | Change |
|---|---|
| `.agents/scripts/link-memory.ps1` | char class → `[:\\/_.]`; `Resolve-SlugDir` resolves by enumeration (on-disk casing, exact match before case-insensitive); rule comment carries the evidence |
| `.agents/scripts/link-memory.sh` | twin edits (`sed 's#[:\\/_.]#-#g'`, `-name` before `-iname`) |
| `_artifacts/_memory/README.md` | rule corrected + why the dot matters |
| `Projects/{AGY_AVIATIONCHAT,Fresh_Workspace_BMAD,NEXgen-VR-Director}/.agents/scripts/` | both scripts re-copied — each vendored copy carried the same bug and would have stranded its own project's memory |

**Seeded.** 126 files moved to `_artifacts/_memory/`; junction verified; all 126 confirmed identical to a
pre-move backup by name and byte length. Canonical was empty beforehand, so this took the SEED path — the
other machine was held back from seeding with its stale set, as intended.

**Secondary fix.** The resolver reported the slug as `C--…` while disk says `c--…` (PowerShell uppercases
the drive letter; the harness records the cwd's own casing). Harmless on NTFS, but it makes the operator's
one verification step — compare this output to `ls ~/.claude/projects` — look like a second store had been
created. It now reports the on-disk spelling and names the mismatch explicitly.

**Still open.** The three maintained projects are unlinked; AGY has **16** memories in its slug dir. Each
is its own repo, so linking them is a separate, per-repo decision — see the close-out note.
