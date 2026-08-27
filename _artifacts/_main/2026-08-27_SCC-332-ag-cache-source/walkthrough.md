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

---

review-runtime: fan-out
lens_isolation: worktree — every repo-reading lens got its own disposable checkout of THIS repo at the sha under review (git worktree add --detach into the scratchpad); the Blind Hunter got no tree at all, by design

## Code Review (2026-08-27)

Verdict: CONCERNS @ 20febc425830d259a66b1758d01a903344224d87
Suite evidence measured on: 20febc42 (gate receipt `gates/suite.json`, clean tree, exit 0, 85.7s)

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=5/0/0 · edge-case-hunter=6/0/0 · literal-correctness-hunter=10/0/0 · acceptance-auditor=8/0/0 · test-adequacy-auditor=10/0/0
drift:           undeclared=0 · unimplemented=0 · incomplete=1 — no `## Declared Change Set` block exists to reconcile against: this ran as an operator-directed lightweight lane with no `implementation_plan.md`, so `declared_change_set.py diff` has no left-hand side. Recorded as one finding at **important** per the declared-drift contract, not silently skipped. Scope was instead reconciled against the ticket's own FIX/TESTS block, recorded as `acceptance-source-SCC-332.md`; the Acceptance Auditor found **no out-of-scope change**.

**Scope.** 15 files, `origin/main...HEAD`: the two-line mechanism fix, its test block, 4 regenerated twins, 7 hand-authored doc surfaces, the sync manifest, and this lane's artifacts.

**Method.** Five lenses in parallel, each in a clean context; the four repo-reading lenses each in their own disposable worktree of this repo at the sha under review; the Blind Hunter starved of repo access by design. Every finding below was **re-verified by the assessor before being acted on** — the two comment-inversion mutants and the cache measurement were reproduced independently.

### Findings

| file:line | sev | failure scenario | disposition |
|---|---|---|---|
| `tests/test_command_surfaces.py` CS-18 B | **critical** | The ticket demanded a cap test on the **cache**; the block globbed `.agents/workflows/` — the source surface, which was never broken and stayed green through the defect's entire life. Zero test files referenced the cache path. The claim "40 doors, 0 over cap" was a `-WhatIf` projection; the real cache still held 23 over-cap bodies | applied @ b2189f7 — `CS-18 L` reads `~/.gemini/antigravity/global_workflows` directly; went RED, a real `-GlobalsOnly` run took it to 39 files / 0 over cap |
| `tests/test_command_surfaces.py` CS-18 | **important** | The ticket's second test ("every workflows door claiming antigravity has a cache twin") never landed in any form | applied @ b2189f7 — `CS-18 M2`, with `M` as its anti-vacuity control |
| `tests/test_command_surfaces.py` CS-18 H | **important** | Raw-text grep reads comments. Revert the call, leave the deleted literal in a `#` line → **10/10 green over the restored defect.** Reproduced | applied @ b2189f7 — `ps_code_only()`, quote-aware; mutant now dies |
| `tests/test_command_surfaces.py` CS-18 I | **important** | Same class: move the regen below the globals block, leave a mention above → green. `str.find` cannot tell a call from a mention | applied @ b2189f7 — anchored to a code-only line via `(?m)^` |
| `sync-agents.ps1:1013` → `.agents/workflows/INDEX.md` | **important** | Moving the cache's source to `workflows/` removed the `$excluded` protection on the router. No frontmatter → `Get-CommandPlatforms` returns UNIVERSAL → it publishes as a description-less `/INDEX` in the global menu. The old source actively **purged** it; the new source installs it | applied @ b2189f7 — `platforms: []` like its `commands/` twin; `CS-18 K`; verified absent from the cache after the real sync |
| `walkthrough.md`, `INDEX.md`, SOP | **important** | "38 files, **20** over the cap" — the real count is **23**. A `head -20` cap read as the count, then shipped to three files and a commit message | applied @ b2189f7 / 20febc4 |
| `docs/workspace-standard.md:283` | **important** | Newly added: "a command's full body is reachable from either." False — 24 of 40 doors are launchers pointing at `.agents/commands/`, which projects do not carry. A global-menu command inside a project now STOPS | applied @ b2189f7 — the reach change is stated, with why it is still the right trade |
| `tests/test_command_surfaces.py` CS-18 J | suggestion | Pin on one 21-character literal. Reword to "are never published to any command cache" → green over the restored defect | applied @ b2189f7 — matches the claim across five live rule sites |
| `tests/test_command_surfaces.py` CS-18 D/E | suggestion | Cardinality asserted where the comment claimed a relation: a legitimate third cache red-fails E while printing "one source feeding both platforms" — the opposite of the truth | applied @ b2189f7 — subset + inequality; benign-refactor controls added |
| `tests/test_command_surfaces.py` CS-18 D/H/I | suggestion | Red-failed three benign refactors: a row split across lines, `$c`→`$cache`, one extra space before `=` | applied @ b2189f7 — `re.S`, `$\w+`, regex not literal `find`; both controls now in the sweep |
| `sync-agents.ps1:563` | suggestion | The `$excluded` comment still called `smh-adviser-board` "~52k" (real 19,804 B) — in the same file this lane edited to retire that exact stale figure, 2.6× off | applied @ b2189f7 |
| `tests/test_command_surfaces.py` CS-18 A/B comment | suggestion | Claimed A/B "would have caught the defect on either surface." It would not have — B's surface was never broken | applied @ b2189f7 — comment now states B is a proxy and L is the real check |
| `.agents/workflows/INDEX.md` | suggestion | "The few hand-authored entries below" sits above a table of **generated** mirrors, and omits the one genuinely hand-authored door — the same doc-inverts-reality failure one paragraph from the retrospective about it | applied @ b2189f7 |
| `walkthrough.md` | nitpick | Cited `sync-agents.ps1:796` in the present tense; the call is at 801 after this diff's inserted comment lines | applied @ 20febc4 — citation removed in favour of the property |
| `walkthrough.md` | nitpick | "40 thin launchers" — measured: 24 generated launchers, 1 hand-authored, 14 full mirrors, 1 router | applied @ 20febc4 |
| `sync-agents.ps1` globals block | suggestion | `-WhatIf` fidelity for this cache is now only as good as the last real sync: the mirror writes nothing under `-WhatIf`, so a dry run enumerates the previous run's doors | applied @ b2189f7 — stated in the code, not silently accepted |
| `_artifacts/_memory/antigravity-uses-workflows-not-commands.md` | suggestion | Still says the global cache is "harmless legacy (the IDE wasn't reading it)" — now false, we deliberately publish launchers there | **deferred — blocked by an open decision:** the operator stood down the folder-identity question this session. The memory's *folder* claim is out of scope; its *legacy* claim is stale. One-line memory edit, not this lane's diff |

**Changes applied: 16 of 17 findings, in-lane. One deferred against a named open decision.** No finding produced a ticket.

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `61/61 files passed`, exit 0 — receipt `gates/suite.json` @ 20febc42, clean tree, 85.7s |
| Toolkit lint | `0 error(s), 0 warning(s), 8 info` (pre-existing BOMs on 8 `testarch-*` bridges), exit 0 |
| Assertion evidence | `--case "CS-18"` → `15/15 passed`, exit 0 |
| SOP currency | exit 0 — `workflows_testing_SOP.md` staged in the same commit |
| Link + anchor | `7 unresolved path(s), 0 bad anchor(s)`, exit 1. **All 7 verified pre-existing on `origin/main`** (same targets, same count, measured by running the checker against those files as they stand on main). **Zero introduced by this diff** |
| Door parity | N/A — no command added, renamed or deleted; all `.agents/commands/` changes are modifications |
| `py_compile` / PowerShell parse | both clean |

### Clean-Code Gate

Machine floor imported from Gates above (SCC-146); ran only what Step 3 did not.

| Check | Result |
|---|---|
| `py_compile` on changed Python | OK |
| PowerShell AST parse of `sync-agents.ps1` | OK, 0 parse errors |
| Comment contract (§2A) | The two new helpers and the CS-18 block carry *why*, with the measured failure that motivated each. `ps_code_only` states the mutant that defeated the old version; `CS-18 L` states why a source-side proxy is not the cache |
| Convention table (§2C) | Matches the file's house style: `c.block`/`c.check`, anti-vacuity controls (A for B, M for M2), details written as data |
| Diff-scoped | Legacy debt in untouched files noted, not gated on — the 7 pre-existing dead links and the 8 BOMs are left alone |

**Findings:** none beyond those in the table above.

### Step 0.7 — re-derivation

1. **Nothing this diff references moved, was renamed, or was deleted on `main`.** `git diff --name-only $BASE..origin/main` returned **0 files** — `origin/main` is still `96935095`, the merge-base. Every repo path and anchor the diff names re-resolves; `check_links` reports 0 bad anchors.
2. **True overlap: none.** `grep -Fxf mine theirs` → empty. `git merge-tree --write-tree --messages HEAD origin/main` returned a bare tree sha (`cd3a9a71`) with no conflict messages — clean.
3. **No sibling lane needs to land first.** `git worktree list` shows only `main` and this lane. Five remote `chore/*` branches exist (SCC-186, SCC-330, SCC-326, SCC-325, SCC-323); none has landed since the merge-base, so none can have moved anything under this diff. No landing-order dependency.

**`review_level: standard`** — derived, not chosen: the radius contains a gate surface (`test_command_surfaces.py`), a rule surface (`workspace-standard.md`), the sync engine itself, and 15 files. Only "nothing moved" came back contained.

### Why CONCERNS and not PASS

Every gate is green and every acceptance item is now evidenced. The verdict is capped at CONCERNS by one
item the repo cannot close by itself: **`CS-18 L`/`M2` assert machine state, and the PC has not been
synced.** They will go red there on the next run, correctly, until `/smh-sync-agents` is run on it. That is
an open operator action, and a lane whose gate is knowingly red on another machine is not a PASS.

### Why not FAIL

The critical finding was found, reproduced, fixed, and re-measured inside this lane before any verdict was
issued — the review did its job. The mechanism itself was independently confirmed correct by all five
lenses, and the source-split relation is killed by three separate mutants. No acceptance item is
undelivered, no dead link was introduced, no gate is red here.

## Your Actions

- [ ] **Run the sync on the PC — tracked as SCC-337, which carries the full runbook.** The Antigravity cache lives in the user profile, outside every repo, so git carries the fixed script and the fixed doors but never the cache; that machine still serves 23 truncated command bodies. ⛔ And the machine-global stage is gated on `$IsLobby -or $GlobalsOnly`, where `$IsLobby` is a path comparison against the repo root — so a sync run from a worktree updates the local surfaces, prints a normal summary, exits 0, and never touches the cache. That is exactly how this lane's own "after" figures were briefly a `-WhatIf` projection. `CS-18 L`/`M2` read the real directory and are red on the PC until the sync lands.
- [x] The merge itself — lands via this branch's PR
