# SCC-332 — the Antigravity global cache was fed command bodies, not thin launchers

## The defect, in one line

`.agents/scripts/sync-agents.ps1` set **one** source for **both** machine-global caches:

```powershell
$GlobalCmdSrc = Join-Path $Master "commands"   # fed to opencode AND antigravity
```

That is correct for opencode — it reads full command bodies and has no size limit. It is wrong for
Antigravity, which **truncates a workflow over 12,000 characters instead of rejecting it** (SCC-135,
measured). A dropped workflow fails visibly; a truncated one runs and looks fine.

## What it cost, measured before the fix

| | files in `~/.gemini/antigravity/global_workflows` | over the 12,000-char cap |
|---|---|---|
| before | 38 raw command bodies | **20** |
| after | 40 thin launchers from `.agents/workflows/` | **0** |

Worst case was `/smh-close-task-merge-tree` at **48,672 chars** — the door that gates merges to `main`.
Its cached copy stopped mid-sentence inside its own safety table, with **32 later headings gone**.

The per-project surface `.agents/workflows/` was never affected. It has honoured the launcher rule since
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
simply being bypassed. `Sync-CommandDir` already filters by each file's `platforms:` frontmatter, and the
generated doors carry it, so no exclusion list was needed and none was added.

Ordering already held: the mirror regenerates at `sync-agents.ps1:796`, above the globals block, so the
cache is always built from a fresh door set. `CS-18 I` now pins that.

## ⭐ The doc came first, and the code followed it

`docs/workspace-standard.md` stated the **inverse** of how the system works:

> `.agents/workflows/` are **in-repo reference process-docs** … they are NOT pushed to any command cache.
> *(Antigravity confusingly calls its invocable units "workflows," but our source is always `commands/` —
> name-matching that to `.agents/workflows/` is the exact bug this rule prevents.)*

`workflows/` **is** Antigravity's menu, on both surfaces. Anyone wiring the global cache from that
paragraph would wire it exactly as it was wired. Corrected in place; `CS-18 J` fails if it returns.

**Lesson: when a doc and a mechanism disagree, measure the mechanism.** An authoritative-sounding rule is
the most expensive kind of wrong, because the next person implements it faithfully.

## Docs corrected (8 edits, 6 hand-authored files)

| File | Was |
|---|---|
| `docs/workspace-standard.md` | the inverted `commands/` vs `workflows/` rule; the surfaces list; "Gemini is global-only" |
| `.agents/commands/smh-sync-agents.md:27` | both caches described as receiving "commands" |
| `.agents/commands/smh-slash-command-updating.md:7-15` | "the canonical `.agents/commands/` set is mirror-synced into" both caches |
| `.agents/commands/INDEX.md:20-23` | AG published from `commands/`; `:31` cited a stale "25k" for `smh-adviser-board` (real: 19,804 B) |
| `.agents/scripts/sync-agents.ps1:8, :795` | header claimed `commands/` mirrors to all four; `:795` said the global cache mirrors `commands/` "unchanged" |
| `.agents/workflows/INDEX.md:3` | called this folder "longer-form reference docs", not Antigravity's menu |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | SCC-135's cap section knew one escape route; the second is now recorded beside it |

`description:` frontmatter was deliberately **not** edited — it drives four doors per command through
`is_launcher_for`/CS-02. Body-only edits regenerate exactly two twins per command. Confirmed: the sync
rewrote 4 twins and zero skill doors.

## Tests

`CS-18` in `.agents/scripts/tests/test_command_surfaces.py`, 10 checks. It reads the script as **text** and
never dot-sources it — `sync-agents.ps1` runs top-to-bottom, so importing it fires a real sync and
republishes the machine caches once per mutant, and a dot-sourced `exit 0` does not stop the caller in
pwsh 7, so that failure is silent and green.

Sources are pinned as a **relation** (the two caches must differ, and each must resolve to its own dir),
so renaming a variable keeps it true while collapsing them back to one source fails it.

**Mutation sweep — 4 mutants, 4 killed, each by a different check:**

| mutant | killed by |
|---|---|
| revert the source split (the original defect) | `CS-18 E`, `CS-18 F` |
| wire the copy call back to the shared variable | `CS-18 H` |
| an over-cap file reaches `.agents/workflows/` | `CS-18 B` |
| restore the inverted doc rule | `CS-18 J` |

`test_command_surfaces.py` 226/226 · `run_all.py` 61/61.

## Recorded, not fixed

- **The PC has not run this.** `core.hooksPath` and the machine caches are per-machine; the Antigravity
  cache there still holds the old bodies until `/smh-sync-agents` runs on it. Held open as an unchecked
  operator action on the ticket.
- **`pwsh` vs `powershell.exe`.** The dry-run verification above used `pwsh` 7. The PC ships Windows
  PowerShell 5.1 under a different name; the sync itself is run there routinely, but this lane's
  before/after measurement is Mac-only.
- **An earlier memory note doubted the destination folder** (`~/.gemini/antigravity` vs the live
  `~/.gemini/antigravity-ide`). Out of scope and stood down by the operator: the source split is correct
  regardless of which folder the IDE reads, and Antigravity is the least-used surface here.
