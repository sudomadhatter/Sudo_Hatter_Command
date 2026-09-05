---
IsArtifact: true
ArtifactMetadata:
  title: SCC-373 — cycle 10, the two instruments that watch the permission fence
  type: walkthrough
  date: 2026-09-04
---

# SCC-373 — cycle 10: the two instruments that watch the permission fence

**Lane:** `chore/SCC-373-bugs-cycle-10` · worktree `.claude/worktrees/bugs-cycle-10`
**Ticket:** [SCC-373](https://sudo-command.atlassian.net/browse/SCC-373) (Bugs and Updates — 2026-09)
**Riders:** [SCC-409](https://sudo-command.atlassian.net/browse/SCC-409) (Part B) · [SCC-410](https://sudo-command.atlassian.net/browse/SCC-410) (Part C)
**Base:** `origin/main` @ `5c444d22`
**Plan:** [implementation_plan.md](implementation_plan.md)

---

## What this means for you, Mr. Hatter

Two things that watch your permission fence were lying to you, in opposite directions,
and both are fixed.

The first is a **measurement** error. The approvals door — `/smh-llm-approvals`, the thing that
tells you which trivial commands keep stopping and waiting for your click — reads your rendered
Claude allow list to work out what is *already* covered. It was throwing away a third of that list.
Fifty-four of your 153 Claude `Bash(...)` rows are written with a bare star at the end, like
`Bash(python3 .agents/scripts/*)`, and the reader stripped only the other two spellings (`:*` and
` *`). Every bare-star row came back with its `*` still glued on, so it matched nothing, so the door
believed those commands were uncovered and billed you for stops that an existing rule already
approves. That is the instrument error that inflated SCC-406's claimed savings. One line fixes it.

The second is a real **hole**, and it is worth a paragraph because it is the kind that ships green.
`env -C <dir> <command>` is GNU `env`'s "change directory first" flag. It runs whatever follows it
somewhere else entirely, and nothing downstream ever sees the `-C` — so a fence written to deny
`rm -rf /` does not deny `env -C /tmp rm -rf /`. The battery that is supposed to catch exactly this
carried `env -u GITHUB_TOKEN` twins and no `env -C` twin, so it could not see the wrapper at all.
That is not theoretical: PR #165 shipped a single `Bash(env -C:*)` allow row that auto-approved
`env -C <dir> rm -rf /` through a **fully green** battery run, and it was closed unmerged.

⭐ **And the ticket understated it.** Scoping measured that the wrapper is not denied *anywhere* —
`env -C /tmp rm -rf /` read *ask* on Zoo, Claude and Antigravity alike. So adding the tripwire twins
on their own turns the battery red rather than arming it, because the hole is real on the deny side
too. Closing it properly needed one new deny family as well as the twins. That is the difference
between installing a smoke alarm and putting out the fire.

⚠️ **One thing is tracked-green and not yet live on this machine, and it needs you.** Zoo Code does
not decide from `.vscode/settings.json` — it decides from VS Code's own globalState database, and
its **denied** list never seeds from the tracked file at all. So the new deny rows are correct in
git and absent from the tool until an apply runs, and Zoo's apply refuses while VS Code is open.
Your two commands are in **Your Actions** at the bottom.

---

## What shipped

### Part B — SCC-409 · `allow_prefixes()` stripped two spellings out of three

`approval_stops.py` turns each rendered row `Bash(<body>)` into a prefix by stripping the trailing
wildcard. It handled `:*` and ` *` and not a bare `*`.

The bare star is not sloppiness — it is the **working** spelling. Battery A2b established that
Claude reads `Bash(X:*)` as `Bash(X *)`, so any prefix ending in `/`, `=`, `-` or `:` must be
written `Bash(X/*)` or it silently means something else. That is why every `Bash(<VAR>=*)` door
variable and `Bash(python3 .agents/scripts/*)` are spelled that way.

Measured on this lane's base: **54 of 153** rendered Claude `Bash(...)` allow rows are bare-star.
Measured at the tip after the fix: **0** prefixes still carry a `*`.

The suffix tuple's **order is load-bearing** and now says so in a comment. Put the bare `*` first
and `Bash(git status:*)` strips to `git status:`, which matches nothing — the same bug with a
different victim. Proven, not asserted: that reorder is mutant 1 below and it turns a case red.

### Part C — SCC-410 · the `env -C` / `env --chdir` laundering wrapper

Two changes, and only one of them is the ticket as filed.

**The tripwire** (as filed): five `env -C` twins added to the battery's `DESTRUCTIVE` list, mirroring
the `env -u GITHUB_TOKEN` block that was already there. Four `env -C` spellings and one
`env --chdir=` spelling, so both flag forms are covered.

**The deny row** (found while scoping): one new family `deny-env-chdir` in `families.json`, covering
both spellings and both flag shapes — `-C /tmp`, `-C/tmp`, `--chdir /tmp`, `--chdir=/tmp` — plus the
`env -u GITHUB_TOKEN` twin. It renders **4 Zoo deny rows** and **16 Antigravity deny rows** (8
written plus 8 `cd <abs> && ` house twins the render pass adds automatically).

It renders **nothing** to Claude, and `.claude/settings.json` is byte-unchanged in this lane. Claude
carries no deny list at all; battery A3 is its guard, which is precisely why the tripwire and the
deny row belong in the same lane.

**Deny side only.** This family can never grant anything. No allow row is added, widened or
re-spelled anywhere in this lane — acceptance G, checked below.

---

## Evidence

### Acceptance

| # | Statement | Result |
|---|---|---|
| A | `allow_prefixes()` returns `python3 .agents/scripts/` for a bare-star row | ✅ `test_D_b`, seen red first |
| B | A slow call a bare-star row covers reports **zero** stops | ✅ `test_D_c`, seen red first |
| C | `DESTRUCTIVE` carries the five `env -C` twins, A3 still green on this base | ✅ A3 green with twins present, no deny row yet |
| D | Injecting `Bash(env -C:*)` turns A3 **red** naming the env -C rows; removing it returns green | ✅ output below |
| E-tracked | `env -C` and `env --chdir` denied in the rendered Zoo and Antigravity lists | ✅ A2 and A12 green |
| E-live | live stores measured and recorded, applies handed over with their commands | ✅ numbers below, **applies not run** |
| F | `--check` in sync, `run_all.py` green at the tip | ✅ 75/75 |
| G | No allow row added, widened or re-spelled | ✅ `families.json` diff is one new `deny` entry |

### Part B — red first, then green, then mutants

```
RED     test_D_b_a_BARE_STAR_row_is_stripped_to_its_prefix -> ['python3 .agents/scripts/*', 'git status', 'ls']
RED     test_D_c_a_slow_call_a_BARE_STAR_row_covers_is_not_a_stop -> a command a bare-star allow row already covers was billed as a stop
```

Both red for the right reason: the returned prefix still carrying its `*`. After the one-line fix:

```
-- 20/20 passed --
```

Mutants:

```
=== MUTANT 1: bare star FIRST (ordering must be load-bearing) ===
AssertionError: ['python3 .agents/scripts/', 'git status:', 'ls ']
-- 19/20 passed --  FAILED: test_D_b_a_BARE_STAR_row_is_stripped_to_its_prefix

=== MUTANT 2: break removed ===
-- 20/20 passed --
```

Mutant 1 kills the case and the failure names exactly what breaks — `git status:` and `ls `, both
trailing junk that matches nothing. **Mutant 2 does not kill**, and that is the honest result: with
this three-entry tuple the `break` is unreachable as a behaviour change, because `"*"` is last and
nothing follows it. It is defensive, not load-bearing. Left in place — it becomes load-bearing the
moment a fourth suffix is added, and removing it would be an orthogonal edit.

Real effect at the tip:

```
rendered Claude Bash allow rows : 153
bare-star rows                  : 54
prefixes still carrying a `*`   : 0 []

sample, before -> after:
  env -u GITHUB_TOKEN git push origin --delete chore/* -> env -u GITHUB_TOKEN git push origin --delete chore/
  env -u GITHUB_TOKEN git pull --ff-only origin main*  -> env -u GITHUB_TOKEN git pull --ff-only origin main
  env -u GITHUB_TOKEN git push -u origin chore/*       -> env -u GITHUB_TOKEN git push -u origin chore/
  env -u GITHUB_TOKEN python3 .agents/scripts/*        -> env -u GITHUB_TOKEN python3 .agents/scripts/
  env -u GITHUB_TOKEN git push origin chore/*          -> env -u GITHUB_TOKEN git push origin chore/
```

### Part C — the hole reproduced before it was closed

Step 4, twins added and nothing else:

```
[FAIL] A2 every destructive command is DENIED on Zoo and Antigravity: zoo=['env -C /tmp rm -rf /', 'env -C /tmp git push --force origin main', 'env -C /tmp git add .', 'env -C /tmp gh pr merge 3'] ag=[same four]
[PASS] A3 Claude never auto-APPROVES a destructive command its list does not deliberately allow: leak=[]
[FAIL] A12 every destructive command is still DENIED behind the house `cd <abs> && ` shape: zoo=[...] ag=[...]
-- 97/99 passed --
```

Two reds, not one — A12 shows the house `cd <abs> && ` shape was equally open. Step 5, deny family
added and rendered:

```
[PASS] A2 ... zoo=[] ag=[]
[PASS] A3 ... leak=[]
[PASS] A12 ... zoo=[] ag=[]
-- 99/99 passed --
```

### Acceptance D — the tripwire actually fires

`Bash(env -C:*)` injected into the rendered Claude allow list — the PR #165 row, verbatim:

```
[FAIL] A3 Claude never auto-APPROVES a destructive command its list does not deliberately allow:
       leak=['env -C /tmp rm -rf /', 'env -C /tmp git push --force origin main',
             'env -C /tmp git add .', 'env -C /tmp gh pr merge 3']
-- 94/99 passed --
```

The other four reds in that run are the drift checks correctly noticing a hand-injected row that no
source renders. Injection reverted; `git status` on `.claude/settings.json` is empty, and:

```
[PASS] A3 ... leak=[]
-- 99/99 passed --
```

### Step 7 — the batch

```
=== 1. permission_render.py --check ===
permission_render: in sync (zoo, claude, antigravity)

=== 2. tests/run_all.py ===
75/75 files passed

=== 3. scope guard: git diff --name-only origin/main...HEAD ===
.agents/permissions/antigravity.json
.agents/permissions/families.json
.agents/scripts/approval_stops.py
.agents/scripts/tests/test_approval_stops.py
.agents/scripts/tests/test_permission_parity.py
.vscode/settings.json
_artifacts/_main/2026-09-04_bugs-cycle-10/*
docs/_scc_sops_prds/tdad_stack_install_guide.md
docs/migrations/terminal-permissions-guide.md
_artifacts/_main/INDEX.md
```

### Step 7.5 — the live stores, measured read-only

```
ZOO  tracked file: .vscode/settings.json  (125 allow / 109 deny)

/mnt/c/Users/dlohn/AppData/Roaming/Code/User/globalStorage/state.vscdb
  allowedCommands: 124  (DRIFT: 1 tracked missing, 0 store-only)
  deniedCommands:  105  (DRIFT: 4 tracked missing, 0 store-only)
  destructiveCommandGuardEnabled: False

/mnt/c/Users/dlohn/vscode-isolated/User/globalStorage/state.vscdb
  allowedCommands: 124  (DRIFT: 1 tracked missing, 0 store-only)
  deniedCommands:  105  (DRIFT: 4 tracked missing, 0 store-only)
  destructiveCommandGuardEnabled: False

ANTIGRAVITY  store: ~/.gemini/config/config.json
  status: DRIFT  allow: store-only=52 tracked-missing=3 | deny: store-only=0 tracked-missing=16
```

The four Zoo `tracked missing` deny rows and the sixteen Antigravity ones **are this lane's new
rows** — that is the fence being tracked-green and not yet live. The pre-existing `1 allow` drift on
both Zoo stores is unrelated and untouched.

⚠️ **Neither `--apply` was run from this lane, deliberately.** Zoo's refuses while VS Code is open,
and it is your call when to quit it. Antigravity's store is adrift by **52 store-only allow rows**
(up from 43 when the plan was audited — nine more clicks since), and its apply *replaces* both
arrays rather than merging, so running it blind would silently delete all 52. Deleting somebody's
un-harvested grants inside a bug-fix lane is exactly the rogue widening this cycle exists to clean
up after.

---

## Two reds fixed that the declared change set did not predict

Both surfaced in the Step 7 batch, both closed here rather than handed to you as a bill.

**`test_zoo_permissions.py::test_guide_currency`** — the terminal-permissions guide carries a live
count line (`125 allow / 105 deny`) that must match the rendered file. The new deny family moved
that to 109, so the guide went stale the moment the fence changed. Updated, and the guide's
"Launder shapes" family row now documents `env -C` / `env --chdir` beside `git -C` — the same class,
the same reasoning, one paragraph. 25/25.

**`test_sops_prds_folder.py::T9`** — `tdad_stack_install_guide.md` had a table row naming
`Projects/Fresh_Workspace_BMAD/backend/requirements.txt`, a path that resolves nowhere. Not this
lane's doing: SCC-403 removed that submodule from git on 2026-09-04, before this lane was cut, and
the guide row is a historical ledger of what that install changed. The test's own source comment
names this exact case. The row now reads *"Fresh_Workspace_BMAD, `backend/requirements.txt` — repo
retired from this workspace (SCC-403, 2026-09-04; it lives on GitHub only)"*, which keeps the
history and stops claiming a live workspace path. 61/61.

Both files are outside the plan's declared change set and are declared here instead.

---

## What this lane does NOT do

- **No allow row is added, widened or re-spelled.** The `families.json` diff is one new `deny` entry.
- **`.claude/settings.json` is untouched**, by design: Claude has no deny list, so the new family
  renders nothing there. If that file ever moves in this diff, the change was not what was planned.
- **`allow-find` is not re-widened to Antigravity.** SCC-405 backed it out because a bare `find`
  token there grants `find . -delete`.
- **The sibling wrappers are not swept.** Measured on this base, `env -i`, `env FOO=1`, `nice`,
  `xargs` and `command` in front of `rm -rf /` all read *ask* on all three platforms — safe today,
  and the same class as this defect. `nice`, `xargs` and `command` are general-purpose and denying
  them wholesale could bite real work, so they go to the open rolling ticket
  [SCC-411](https://sudo-command.atlassian.net/browse/SCC-411) as one row.

---

## Your Actions

Two commands, both on this machine, both after the merge:

```bash
# 1. Zoo Code — QUIT VS CODE FULLY FIRST (all windows). The apply refuses while it runs.
python3 .agents/scripts/zoo_permissions_apply.py --apply

# 2. Antigravity — READ THIS FIRST. 52 store-only allow rows will be DELETED by an apply.
python3 .agents/scripts/antigravity_permissions_apply.py --status
```

For #2 my recommendation is to harvest before applying: run `/smh-llm-approvals`, which is the door
built to turn those 52 store-only clicks into tracked families, and apply after. Applying first
loses them.

Until #1 runs, `env -C /tmp rm -rf /` still reads *ask* on this box rather than *deny*. Ask is safe
— nothing auto-runs — it is simply weaker than the repo now claims.
