# Walkthrough — Portable auto-memory store (junction into the repo, Windows + macOS twins)

- **Date:** 2026-08-04
- **Workspace:** home base (lobby)
- **Plan:** [`implementation_plan.md`](implementation_plan.md) — approved, then **revised mid-flight** (see §2)

---

## 1. What this was

"Does memory travel between machines?" It does not — and checking turned up that **15 memory files were
already dead** on this machine from renames done months ago.

Claude Code stores auto-memory at `~/.claude/projects/<slug>/memory/`, where `<slug>` is **derived from the
workspace's absolute path** (`:` `\` `/` `_` → `-`; the rule reproduces all five directories on this box
exactly). Three failure modes, two already fired:

| Slug | Decodes to | Files | State |
|---|---|---|---|
| `c--Sudo-Hatter-Command` | `c:\Sudo_Hatter_Command` | 25 | live |
| `c--AGY-Projects-aviationChat-AGY` | `c:\AGY\Projects\aviationChat-AGY` | **13** | ⚠️ stranded (home-base rename) |
| `c--Sudo-Hatter-Command-Projects-aviationChat-AGY` | `…\Projects\aviationChat-AGY` | **2** | ⚠️ stranded (project rename) |

`rename-fix.ps1` repairs `~/.claude/settings.json` on rename day but knows nothing about
`projects/<slug>/memory/`. **That gap is what killed the 15.**

## 2. The mid-flight revision that changed the whole approach

The plan originally called for seeding the repo store from this machine and adopting the 15 stranded files.
Daniel then established: **this desktop holds the OLDEST memories; the laptop has the current ones.**

That inverts the safe order. Seeding canonical from here and committing would push *stale* memory to git,
and the laptop's newer files would collide with it on arrival. So:

- **Nothing was applied on this machine.** No junction, no seeding, no adoption. The 25 local files and the
  15 stranded ones sit exactly where they were.
- Shipped instead: the **tooling + docs + an empty canonical store**, so the laptop can seed from the good
  side. That is precisely what "fix the rules so they're on git" asked for.

## 3. What shipped

### `.agents/scripts/link-memory.ps1` + `link-memory.sh` — twins by contract

Junction on Windows, symlink on macOS; identical otherwise. They follow the pair convention already
established for `Restore-EnvMaster.ps1` / `restore-env-master.sh`, and `_my_resources/migrations/INDEX.md`
now names **both** pairs under the standing "if either changes, change both" rule.

Behaviour: dry-run by default (`-Apply` / `--apply` to write), `-All` / `--all` reads
`.agents/maintained-projects.txt` rather than hand-looping `Projects/*`.

**Safety — the script never deletes or merges memory.** Three cases:
| Canonical | Local slug dir | Action |
|---|---|---|
| empty | has files | **SEED** — move them in (nothing to overwrite) |
| has files | has files | **BACK UP** to `memory.local-backup-<timestamp>`, warn, junction anyway. Never merged. |
| anything | already junctioned to canonical | no-op |

### Two bugs the dry run caught before anything was written

1. **Case double-processing.** The first draft linked both `C--…` and `c--…` spellings to defend against a
   "drive-letter case" axis. NTFS is case-**insensitive**, so those are one directory — the script processed
   it twice and the second pass invented a canonical-vs-local conflict against itself, complete with a
   spurious backup. Replaced with `Resolve-SlugDir`: compute one slug, reuse any case-insensitive match,
   create only if truly absent. Correct on both case-insensitive and case-sensitive volumes.
2. **Scaffolding counted as memory.** `README.md` in the store would have made a fresh canonical look
   populated, sending the *first* machine down the backup path — stranding the very memories the tool
   exists to rescue. `Get-MemoryFiles` / `count_memory_files` now exclude `README.md` and `.gitkeep`.

### `_artifacts/_memory/` + `README.md`

Canonical location. Chosen because `AGENTS.md` already calls `_artifacts/` "the shared memory", so it adds
**no** new top-level folder — no `router.md` row, no repo-map entry, no tier decision. Verified against the
linter: `_artifacts` is in `DEPTH3_DIRS`, and check 7 only wants an `INDEX.md` in buckets with ≥2
session-shaped subdirs, so a flat store is skipped. **Zero new drift.**

### Documentation

- `_my_resources/migrations/INDEX.md` — §1 **step 8** (new machine, both platforms) with the cross-machine
  ORDER warning; §2 macOS row for the `.sh`; §3 **rename-day step 2** with the 15-file evidence; the
  twin-sync rule extended to name this second pair.
- `_my_resources/migrations/new_machine-migration-guide.md` — §5 bullet, beside GitNexus and worktrees (the
  other two things that don't travel).
- `_my_resources/migrations/rename-fix.ps1` — header now states it is **step 2 of 3** and names the memory
  gap plus the follow-up command. This is the change that prevents a fourth stranding.
- `docs/workspace-standard.md` — PATH CONTRACT row + a Part 2 upkeep section.

### One rule tightened, unrelated but earned

`.agents/rules/artifacts-always-first.md:165` already said to present plans "inline in the chat", and I had
been linking instead. One of the **stranded** files — `present-plans-inline-full.md` — said it harder:
plans pasted FULLY inline, not summarized. Since it was stranded it never reached this session, which is a
tidy demonstration of the cost. The rule now says *fully inline*, names a link-only plan as a **gate
violation** (approval requires having been shown the thing), and allows only one exception: a plan past the
8 KB budget may link its exhaustive appendix, never the reasoning.

## 4. Verification — real output

Both scripts parse (`PSParser.Tokenize` / `bash -n`) and exit 0. Final dry run, after both fixes:

```
CLAUDE MEMORY LINK  (DRY RUN - re-run with -Apply to write)
store: C:\Users\dlohn\.claude\projects

=== C:\Sudo_Hatter_Command
  canonical : C:\Sudo_Hatter_Command\_artifacts\_memory  (0 file(s))
  slug      : C--Sudo-Hatter-Command
  WHATIF: would SEED canonical with 25 local file(s)
  WHATIF: would junction ...\memory -> C:\Sudo_Hatter_Command\_artifacts\_memory
```
One directory per workspace (no double pass), `0 file(s)` proving README is excluded from the count.

The `.sh` was exercised under Git Bash — **not** a valid macOS test (it sees `/c/Sudo_Hatter_Command` and
computes `-c-Sudo-Hatter-Command`), but it proved the guard: it found no matching slug dir, listed the real
entries, and **told the operator to stop before `--apply`** instead of creating a wrong directory.

`check_maps.py`: `level-2 INDEX`, `structure conformance` **clean**; the only depth-3 hit is this session's
own folder, resolved by the INDEX row below.

## 5. Task Checklist

- [x] `link-memory.ps1` + `link-memory.sh` written as twins; both parse, both dry-run clean
- [x] case double-processing bug found by dry run and fixed
- [x] scaffolding-counted-as-memory bug found and fixed
- [x] `_artifacts/_memory/` + `README.md` created (empty of memories, deliberately)
- [x] migrations INDEX §1/§2/§3 + twin rule; new-machine guide §5; `rename-fix.ps1` header
- [x] `docs/workspace-standard.md` PATH CONTRACT row + upkeep section
- [x] `artifacts-always-first.md` inline-plan rule tightened
- [x] `check_maps.py` — zero new drift
- [x] **nothing applied on this machine** (stale-memory constraint honoured)

## 6. Your Actions

**Order matters. The laptop goes first** — it holds the newest memories, and the first machine to link
seeds the shared store.

**1 — here (desktop), commit the tooling only:**
```powershell
git add .agents/scripts/link-memory.ps1 .agents/scripts/link-memory.sh .agents/rules/artifacts-always-first.md .agents/scripts/check_maps.py .agents/skills/v3-prompt-architecture/SKILL.md .agents/skills/5_adk_skills .claude/skills docs/workspace-standard.md _my_resources/migrations _artifacts/_memory _artifacts/INDEX.md _artifacts/_main/INDEX.md _artifacts/_main/active-context.md _artifacts/_main/2026-08-04_index-depth-exception-list _artifacts/_main/2026-08-04_portable-memory-store
git commit -m "feat(memory): junction Claude auto-memory into the repo so it travels

The harness stores memory under a slug DERIVED FROM THE WORKSPACE PATH, so it
never leaves the machine and a rename orphans it - 15 files were already dead
under two stale slugs. Canonical store is now _artifacts/_memory/, linked by
link-memory.ps1 / link-memory.sh (twins, dry-run by default, never merge or
delete). rename-fix.ps1 now names the follow-up step that was the actual gap."
git push
```

**2 — on the laptop:** pull, then
```powershell
powershell -File .agents\scripts\link-memory.ps1 -All          # READ THIS FIRST
powershell -File .agents\scripts\link-memory.ps1 -All -Apply
```
It will report `SEED canonical with N local file(s)`. Then commit `_artifacts/_memory/` and push. Those
become the shared memories.

**3 — back here (desktop):** pull, then run the same two commands. Canonical will be populated, so this
machine's 25 stale files get moved to `memory.local-backup-<timestamp>` — kept, not deleted, in case you
want to mine them later.

**4 — MacBook Pro:** run `ls ~/.claude/projects/` **first** and send me the output. The macOS slug shape is
inferred from Windows paths; the script refuses rather than guessing, but one look settles it permanently.
Then `bash .agents/scripts/link-memory.sh --all` (dry run) → `--apply`.

⚠️ Still outstanding from the earlier session: the three project repos have staged `adk-prompting`
deletions awaiting commit, and **B-L-WorldWide is on `main`** (owner-only).
