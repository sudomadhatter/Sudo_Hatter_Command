# SCC-332 — the Antigravity global cache was fed command bodies, not thin launchers

## The defect, in one line

`.agents/scripts/sync-agents.ps1` set **one** source for **both** machine-global caches:

```powershell
$GlobalCmdSrc = Join-Path $Master "commands"   # fed to opencode AND antigravity
```

Correct for opencode — it reads full command bodies and has no size limit. Wrong for Antigravity, which
**truncates a workflow over 12,000 characters instead of rejecting it** (SCC-135, measured). A dropped
workflow fails visibly; a truncated one runs and looks fine.

## What it cost, measured

| | files in `~/.gemini/antigravity/global_workflows` | over the 12,000-char cap |
|---|---|---|
| before | 38 raw command bodies | **23** |
| after (measured on this Mac after a real `-GlobalsOnly` run) | 39 doors | **0** |

Worst case was `/smh-close-task-merge-tree` at **48,672 chars** — the door that gates merges to `main`.
Its cached copy stopped mid-sentence inside its own safety table, with **32 later headings gone**.

The per-project surface `.agents/workflows/` was never affected; it has honoured the launcher rule since
2026-07-25. Only the machine-global cache bypassed it, which is why this sat unnoticed: Antigravity is the
least-used platform here, and in-repo work uses the door that was already correct.

## The fix

Each cache names its own source; the copy loop reads that field instead of one shared variable.

```powershell
$GlobalCmdSrc = Join-Path $Master "commands"
$GlobalWfSrc  = Join-Path $Master "workflows"
$caches = @(
  @{ Name = 'opencode';    Platform = 'opencode';    Src = $GlobalCmdSrc; Path = … },
  @{ Name = 'antigravity'; Platform = 'antigravity'; Src = $GlobalWfSrc;  Path = … }
)
…
$names = Sync-CommandDir $c.Src $c.Path $c.Platform -Mirror -SkipAP -WhatIf:$WhatIf
```

`Sync-AntigravityWorkflowMirror` was **not touched**. The launcher mechanism was already right — it was
being bypassed. `Sync-CommandDir` already filters by each file's `platforms:` frontmatter.

Ordering already held: the regen call is unconditional top-level code above both the `-GlobalsOnly` guard
and the globals block, so `/smh-slash-command-updating` refreshes the doors before mirroring them.
`CS-18 I2` pins it.

**One guard WAS needed, and the review found it.** Promoting `workflows/` from a sync *destination* to a
sync *source* removed the protection `$excluded` used to give `.agents/workflows/INDEX.md`. That router
has no `commands/` twin and carried no frontmatter, which `Get-CommandPlatforms` reads as **universal** —
so it would have published as a description-less `/INDEX` entry in the global slash menu SCC-195 exists to
protect. Its `commands/` sibling declares `platforms: []`; the workflows router now does too. `CS-18 K`.

## ⭐ The doc came first, and the code followed it

`docs/workspace-standard.md` stated the **inverse** of how the system works:

> `.agents/workflows/` are **in-repo reference process-docs** … they are NOT pushed to any command cache.
> *(Antigravity confusingly calls its invocable units "workflows," but our source is always `commands/` —
> name-matching that to `.agents/workflows/` is the exact bug this rule prevents.)*

`workflows/` **is** Antigravity's menu, on both surfaces. Anyone wiring the global cache from that
paragraph would wire it exactly as it was wired. Corrected in place; `CS-18 J` matches the *claim* rather
than one literal string, so a reword cannot bring it back.

**Lesson: when a doc and a mechanism disagree, measure the mechanism.**

## ⚠ What changed for the worse, stated plainly

24 of the 40 doors are thin launchers reading *"read `.agents/commands/<name>.md` relative to the repo root
of the workspace you are in… if that file does not exist, STOP."* Under the thin model a project carries no
`.agents/commands/`. So a big command invoked from the **global** menu inside a project now **stops** where
it previously delivered the first 12,000 characters and improvised the rest.

That is the right direction — it is SCC-135's own lesson applied — but it is a real reach change and it is
recorded here rather than discovered later. In-repo Antigravity work is unaffected: it reads
`.agents/workflows/` directly.

## Docs corrected

| File | Was |
|---|---|
| `docs/workspace-standard.md` | the inverted `commands/` vs `workflows/` rule; the surfaces list; a false "full body is reachable from either" claim |
| `.agents/commands/smh-sync-agents.md` | both caches described as receiving "commands" |
| `.agents/commands/smh-slash-command-updating.md` | "the canonical `.agents/commands/` set is mirror-synced into" both caches |
| `.agents/commands/INDEX.md` | AG published from `commands/`; a stale "25k" for `smh-adviser-board` (real: 19,804 B) |
| `.agents/scripts/sync-agents.ps1` | header claimed `commands/` mirrors to all four; the ordering comment said the cache mirrors `commands/` "unchanged"; `$excluded`'s comment still said adviser-board was "~52k" |
| `.agents/workflows/INDEX.md` | called this folder "longer-form reference docs"; called generated twins "hand-authored" |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | SCC-135's cap section knew one escape route; the second is recorded beside it |

`description:` frontmatter was deliberately **not** edited on any command — it drives four doors each
through `is_launcher_for`/CS-02. Body-only edits regenerated exactly 4 twins and 0 skill doors.

## Tests

`CS-18` in `.agents/scripts/tests/test_command_surfaces.py`, 15 checks. It reads the script as **text** and
never dot-sources it — `sync-agents.ps1` runs top to bottom, so importing it fires a real sync and
republishes the machine caches once per mutant, and a dot-sourced `exit 0` does not stop the caller in
pwsh 7, so that failure is silent and green.

**It reads the script with its comments STRIPPED** (`ps_code_only`). The first version did not, and two of
its checks were invertible by a `#` line — see the review below.

**`CS-18 L`/`M2` read the real cache directory**, not a source-side proxy. That distinction is the whole
finding of this lane's review: a code fix does not move a `$HOME` cache, and `$IsLobby` is false in a
worktree, so the first sync wrote 4 local twins and left the cache untouched with every source check green.

**Mutation sweep — 7 mutants killed, 2 benign refactors correctly pass:**

| mutant | killed by |
|---|---|
| revert the source split (the original defect) | `CS-18 E`, `F` |
| wire the copy call back to the shared variable | `CS-18 H` |
| …and hide the deleted literal in a comment | `CS-18 H` |
| move the regen below the globals block, mention left above | `CS-18 I2` |
| restore the inverted doc rule **with different wording** | `CS-18 J` |
| strip the router's `platforms: []` | `CS-18 K`, `M2` |
| an over-cap file reaches `.agents/workflows/` | `CS-18 B` |
| *control:* rename the loop variable `$c` → `$cache` | **passes**, correctly |
| *control:* split a cache row across physical lines | **passes**, correctly |

## Recorded, not fixed

- **The PC has not run this.** The cache lives in `$HOME`; git carries the script and the doors but not the
  cache. `/smh-sync-agents` once on that machine. `CS-18 L`/`M2` go red there until it does.
- **`-WhatIf` fidelity for this cache is now only as good as the last real sync** — the mirror writes
  nothing under `-WhatIf`, so a dry run enumerates the previous run's doors. Noted in the code.
- **Nothing observes the machine caches except `CS-18 L`/`M2`.** `Get-SurfaceState`/`-Status` cover only
  repo-local dirs. That blind spot is why SCC-332 lived undetected.
- **An earlier memory note doubted the destination folder.** Out of scope, stood down by the operator: the
  source split is correct regardless of which folder the IDE reads.
