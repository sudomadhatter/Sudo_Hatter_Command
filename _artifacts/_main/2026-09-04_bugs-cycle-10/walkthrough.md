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

Two things that watch your permission fence were lying to you, in opposite directions, and both
are fixed. A five-lens review then found a third lie in the same instrument and two real holes in
the fence, all of which are also now closed.

The first was a **measurement** error. The approvals door — `/smh-llm-approvals`, the thing that
tells you which trivial commands keep stopping and waiting for your click — reads your rendered
Claude allow list to work out what is already covered. It was throwing away a third of that list.
Fifty-four of your 153 Claude `Bash(...)` rows end in a bare star, like
`Bash(python3 .agents/scripts/*)`, and the reader stripped only the other two spellings. Every
bare-star row came back with its `*` still glued on, matched nothing, and the door billed you for
stops an existing rule already approves.

The second was a real **hole**, and it is the kind that ships green. `env -C <dir> <command>` is
GNU `env`'s "change directory first" flag. It runs whatever follows it somewhere else entirely, and
nothing downstream ever sees the `-C` — so a fence written to deny `rm -rf /` did not deny
`env -C /tmp rm -rf /`. The battery meant to catch this carried `env -u GITHUB_TOKEN` twins and no
`env -C` twin, so it was blind to the whole class. PR #165 shipped a single `Bash(env -C:*)` allow
row that auto-approved `env -C <dir> rm -rf /` through a **fully green** battery run.

⭐ **And the ticket understated it.** Scoping measured that the wrapper was not denied *anywhere* —
it read *ask* on Zoo, Claude and Antigravity alike. So adding the tripwire alone turns the battery
red rather than arming it. Closing it properly needed a deny family as well, which is the
difference between installing a smoke alarm and putting out the fire.

**What the review changed.** Five independent lenses hunted this lane and between them found that
the fix I shipped had opened a new way for the door to go permanently silent, that half the deny
rows had no test behind them, that a legal `env -iC` flag cluster walked straight through, and that
the same door was *under*-reporting in a second way I had not looked for — the prefix `ls` was
matching `lsof` and `lsblk`, so real stops were being dropped. All of it is fixed in this lane, with
a mutant proving each new assertion can fail. The full account is in **Code Review** at the bottom.

⚠️ **One thing is tracked-green and not yet live on this machine, and it needs you.** Zoo Code does
not decide from `.vscode/settings.json` — it decides from VS Code's own globalState database, and
its **denied** list never seeds from the tracked file at all. So the new deny rows are correct in
git and absent from the tool until an apply runs, and Zoo's apply refuses while VS Code is open.
Your two commands are in **Your Actions** at the bottom.

---

## What shipped

### Part B — SCC-409 · the approvals door's coverage reader

`approval_stops.py` turns each rendered row `Bash(<body>)` into a coverage prefix by stripping the
trailing wildcard, then asks whether a command starts with any of those prefixes. Three defects, one
filed and two found by the review, all in that three-line path.

**1. The bare star was never stripped** (the filed bug). The tuple handled `:*` and ` *` and not a
bare `*`. That spelling is not sloppiness — it is the **working** one: SCC-375's check A2b, in
`tests/test_settings_allowlist.py`, established that Claude reads `Bash(X:*)` as `Bash(X *)`, so any
prefix ending in `/`, `=`, `-` or `:` must be written `Bash(X/*)`. That is why every
`Bash(<VAR>=*)` door variable and `Bash(python3 .agents/scripts/*)` are spelled that way.
**54 of 153** rendered rows are bare-star; at the tip, **0** prefixes carry a stray `*`.

The tuple's **order is load-bearing** and now says so: put the bare `*` first and
`Bash(git status:*)` strips to `git status:`. So is the **`break`** — without it `Bash(X* *)`
strips twice and returns a prefix *wider* than the row that produced it. Both are held by
assertions, not by comments.

**2. A row that strips to nothing silenced the whole door** (review, my regression). Adding the
bare-star strip created a new input: `Bash(*)` came back as `""`, and `"rm -rf /".startswith("")` is
True. One such row makes `covered()` answer True for every command and the door reports zero stops
forever — indistinguishable from "nothing to harvest", which is the SCC-407 failure this script
exists to end. Rows that strip to nothing are now dropped, so the door over-reports rather than
going quiet.

**3. A prefix matched inside a word** (review, pre-existing and the mirror of the filed bug).
`Bash(ls *)` yields the prefix `ls`, and a bare `startswith` marked `lsof -i :3000`, `lsblk` and
`git statuses` as already-approved — dropping their stops from the report. A prefix now covers a
segment only at a **boundary**: the segment is the prefix, or continues it after a space, or the
prefix already ends on a separator. Those separators are exactly the endings A2b requires the
bare-star spelling for, so the two rules meet rather than fight.

### Part C — SCC-410 · the `env -C` / `env --chdir` laundering wrapper

**The tripwire** (as filed): `env -C` twins added to the battery's `DESTRUCTIVE` list, so an
`env -C` allow row can never again ship green.

**The deny family** (found while scoping): one new family `deny-env-chdir` in `families.json`. After
the review widened it, it denies **eight spellings** and renders **10 Zoo deny rows** (105 → 115)
and **40 Antigravity deny rows** (384 → 424: 20 written plus 20 `cd <abs> && ` house twins the render
pass adds). It renders **nothing** to Claude, and `.claude/settings.json` is byte-unchanged: Claude
carries no deny list at all, and battery A3 is its guard — which is exactly why the tripwire and the
deny row belong in the same lane.

**Deny side only.** This family can never grant anything, and no allow row is added, widened or
re-spelled anywhere in this lane. Both allow arrays are byte-identical to `origin/main`.

**What is closed, and what honestly is not:**

```
CLOSED - the eight spellings the fence now denies
  command                                      zoo    claude  antigravity
  env -C /tmp rm -rf /                         deny   ask     deny
  env -C/tmp rm -rf /                          deny   ask     deny
  env --chdir /tmp rm -rf /                    deny   ask     deny
  env --chdir=/tmp rm -rf /                    deny   ask     deny
  env -u GITHUB_TOKEN env -C /tmp rm -rf /     deny   ask     deny
  env -u GITHUB_TOKEN -C /tmp rm -rf /         deny   ask     deny
  /usr/bin/env -C /tmp rm -rf /                deny   ask     deny
  cd /abs && env -C /tmp rm -rf /              deny   ask     deny

RESIDUAL 2 - getopt cluster: Antigravity denies, Zoo cannot express it
  env -iC /tmp rm -rf /                        ask    ask     deny
  env -vC /tmp rm -rf /                        ask    ask     deny
  env -iC/tmp rm -rf /                         ask    ask     deny

RESIDUAL 1 - an option ORDERED before the flag: ask on all three
  env -i -C /tmp rm -rf /                      ask    ask     ask
  env FOO=1 -C /tmp rm -rf /                   ask    ask     ask
  env -u FOO -u BAR -C /tmp rm -rf /           ask    ask     ask
```

Both residuals are **grammar limits, not oversights**, and both land on *ask* — you still decide,
nothing auto-runs. Zoo matches a literal prefix and Antigravity matches per token by position, so
"any option before the flag" is not expressible as a finite row set on either. The cluster is
expressible on Antigravity (the token regex is the renderer's own cluster class `-[a-zA-Z]*C.*`) and
not on Zoo, so it is deliberately **absent** from the destructive set: that check demands both
platforms deny, and listing it would red the battery over a limit rather than a defect. Both are
written into the family's own `why` and into the guide, beside the arbitrary-quoting residual the
guide already records for `git push origin "main`.

---

## Evidence

Measured at `HEAD` — the sha is on the `Verdict:` line in **Code Review** below.

### Acceptance

| # | Statement | Result |
|---|---|---|
| A | `allow_prefixes()` returns `python3 .agents/scripts/` for a bare-star row | ✅ `test_D_b`, seen red first |
| B | A slow call a bare-star row covers reports **zero** stops | ✅ `test_D_c`, seen red first, and now carries its own control |
| C | `DESTRUCTIVE` carries the `env -C` twins, A3 still green on this base | ✅ 10 twins, one per claimed spelling; A3 green |
| D | Injecting `Bash(env -C:*)` turns A3 **red** naming the env -C rows; removing it returns green | ✅ output below |
| E-tracked | `env -C` and `env --chdir` denied in the rendered Zoo and Antigravity lists | ✅ A2 and A12 green; per-spelling table above |
| E-live | live stores measured and recorded, applies handed over with their commands | ✅ numbers below, **applies not run** |
| F | `--check` in sync, `run_all.py` green at the tip | ✅ `in sync`, **75/75** |
| G | No allow row added, widened or re-spelled | ✅ machine-checked: both allow arrays byte-identical to `origin/main` |

### Part B — red first, then green, then mutants

The two filed cases, seen red against the unfixed script for the right reason — the returned prefix
still carrying its `*`:

```
RED     test_D_b_a_BARE_STAR_row_is_stripped_to_its_prefix -> ['python3 .agents/scripts/*', 'git status', 'ls']
RED     test_D_c_a_slow_call_a_BARE_STAR_row_covers_is_not_a_stop -> a command a bare-star allow row already covers was billed as a stop
```

Every mutant, including the three that survived the first cut and were closed during the review:

```
M1  revert the bare-star strip     -- 19/24 --  D_b, D_c, D_d, D_f
M2  bare star FIRST in the tuple   -- 23/24 --  D_b   ['python3 .agents/scripts/', 'git status:', 'ls ']
M3  break removed                  -- 23/24 --  D_e   (survived the first cut)
M4  `suffix in body`               -- 23/24 --  D_b   (survived the first cut)
M7  `body.rstrip(":* ")`           -- 23/24 --  D_e   (survived the first cut)
MA  empty-prefix guard removed     -- 23/24 --  D_d   ['', '', 'git status']
MB  boundary rule -> bare startswith -- 23/24 -- D_g   'lsof -i :3000' was marked covered
```

M1's failure is the best evidence in the lane, because it does not report a count — it prints all
54 rows by name: `['python3 .agents/scripts/*', 'env -u GITHUB_TOKEN python3 .agents/scripts/*',
'backend/.venv/bin/*', 'MSG=*', 'REPO=*', …]`.

Real effect at the tip:

```
rendered Claude Bash allow rows : 153
bare-star rows                  : 54
prefixes still carrying a `*`   : 0 []
```

### Part C — the hole reproduced before it was closed

Step 4, twins added and nothing else. Two checks red, not one — A12 shows the house `cd <abs> && `
shape was equally open. (A2's and A12's detail strings truncate at four entries by design, so the
fifth twin was in the red set and simply not printed.)

```
[FAIL] A2 every destructive command is DENIED on Zoo and Antigravity (known disagreements pinned below): zoo=['env -C /tmp rm -rf /', 'env -C /tmp git push --force origin main', 'env -C /tmp git add .', 'env -C /tmp gh pr merge 3'] ag=['env -C /tmp rm -rf /', 'env -C /tmp git push --force origin main', 'env -C /tmp git add .', 'env -C /tmp gh pr merge 3']
[PASS] A3 Claude never auto-APPROVES a destructive command its list does not deliberately allow: leak=[]
[FAIL] A12 every destructive command is still DENIED on Zoo and Antigravity behind the house `cd <abs> && ` shape: zoo=['env -C /tmp rm -rf /', 'env -C /tmp git push --force origin main', 'env -C /tmp git add .'] ag=['env -C /tmp rm -rf /', 'env -C /tmp git push --force origin main', 'env -C /tmp git add .']
-- 97/99 passed --
```

Step 5, deny family added and rendered:

```
[PASS] A2 every destructive command is DENIED on Zoo and Antigravity (known disagreements pinned below): zoo=[] ag=[]
[PASS] A3 Claude never auto-APPROVES a destructive command its list does not deliberately allow: leak=[]
[PASS] A12 every destructive command is still DENIED on Zoo and Antigravity behind the house `cd <abs> && ` shape: zoo=[] ag=[]
-- 99/99 passed --
```

**Every deny spelling is load-bearing** — dropping any group from the family reds the battery, so no
row shipped as decoration:

```
drop rows containing '/usr/bin/env'      -- 97/99 passed --
drop rows containing 'GITHUB_TOKEN env -C' -- 96/99 passed --
drop rows containing 'GITHUB_TOKEN -C'   -- 96/99 passed --
drop rows containing '--chdir'           -- 97/99 passed --
```

### Acceptance D — the tripwire actually fires

`Bash(env -C:*)` injected into the rendered Claude allow list — the PR #165 row, verbatim:

```
[FAIL] A3 Claude never auto-APPROVES a destructive command its list does not deliberately allow: leak=['env -C /tmp rm -rf /', 'env -C /tmp git push --force origin main', 'env -C /tmp git add .', 'env -C /tmp gh pr merge 3']
-- 94/99 passed --
FAILED: A3 ..., A6 parity: identical decisions across the three (Claude's deny reads as ask), B4 --check is CLEAN on the tracked tree, B5 --check is clean on an exact copy (all four files present), D3 the renderer runs standalone under this interpreter and reads the tracked tree as in sync (exit 0)
```

The other four reds are A6 (a parity row) and three drift rows correctly noticing a hand-injected
row that no source renders. Injection reverted; `git status` on `.claude/settings.json` is empty,
and the battery returns to `99/99`.

### The gates

```
$ python3 .agents/scripts/permission_render.py --check
permission_render: in sync (zoo, claude, antigravity)

$ python3 .agents/scripts/tests/run_all.py
75/75 files passed

$ python3 .agents/scripts/workflow_lint.py --toolkit-only
-- 0 error(s), 0 warning(s), 8 info --

$ python3 .agents/scripts/check_links.py --base origin/main
  clean

$ git diff --name-only origin/main...HEAD
.agents/permissions/antigravity.json
.agents/permissions/families.json
.agents/scripts/approval_stops.py
.agents/scripts/tests/test_approval_stops.py
.agents/scripts/tests/test_permission_parity.py
.vscode/settings.json
_artifacts/_main/2026-09-04_bugs-cycle-10/implementation_plan.md
_artifacts/_main/2026-09-04_bugs-cycle-10/task.yaml
_artifacts/_main/2026-09-04_bugs-cycle-10/walkthrough.md
_artifacts/_main/INDEX.md
docs/_scc_sops_prds/tdad_stack_install_guide.md
docs/migrations/terminal-permissions-guide.md
```

### Step 7.5 — the live stores, measured read-only

```
$ python3 .agents/scripts/zoo_permissions_apply.py --status
tracked file: .vscode/settings.json  (125 allow / 115 deny)

/mnt/c/Users/dlohn/AppData/Roaming/Code/User/globalStorage/state.vscdb
  allowedCommands: 124  (DRIFT: 1 tracked entries missing from store, 0 store-only entries)
  deniedCommands:  105  (DRIFT: 10 tracked entries missing from store, 0 store-only entries)
  destructiveCommandGuardEnabled: False

/mnt/c/Users/dlohn/vscode-isolated/User/globalStorage/state.vscdb
  allowedCommands: 124  (DRIFT: 1 tracked entries missing from store, 0 store-only entries)
  deniedCommands:  105  (DRIFT: 10 tracked entries missing from store, 0 store-only entries)
  destructiveCommandGuardEnabled: False

$ python3 .agents/scripts/antigravity_permissions_apply.py --status
status  : DRIFT allow: store-only=58 tracked-missing=3 | deny: store-only=0 tracked-missing=40
```

The 10 Zoo and 40 Antigravity `tracked missing` deny rows **are this lane's new rows** — that is the
fence being tracked-green and not yet live. The pre-existing `1 allow` drift on both Zoo stores is
unrelated and untouched. One `--apply` covers **both** Zoo stores; the script enumerates every
candidate database rather than taking one path.

⚠️ **Neither `--apply` was run from this lane, deliberately.** Zoo's refuses while VS Code is open,
and quitting it is your call. Antigravity's store carries store-only allow rows that its apply would
*replace* rather than merge — read `--status` for today's figure; it was 43 when the plan was
audited and 58 when this was written, so it moves. Deleting somebody's un-harvested grants inside a
bug-fix lane is exactly the rogue widening this cycle exists to clean up after.

---

## Three reds the batch surfaced, closed here rather than handed to you

**`test_zoo_permissions.py::test_guide_currency`** — the terminal-permissions guide carries a live
count line that must match the rendered file, and the new deny rows moved it from 105 to 115. The
guide's "Launder shapes" family row now documents `env -C` / `env --chdir` beside `git -C` — same
class, same reasoning — and names both residuals rather than claiming the wrapper is closed. 25/25.

**`test_sops_prds_folder.py::T9`** — `tdad_stack_install_guide.md` had a "Files Modified by This
Setup" row naming a requirements file under the retired Fresh_Workspace_BMAD project, a path that
resolves nowhere. Not this lane's doing: SCC-403 removed that submodule from git in `0ea1339b` on
2026-09-04, *before* this lane was cut — `git ls-tree origin/main Projects/` lists nine gitlinks,
not ten — and the row is a historical ledger of what that install changed, not a live instruction.
The test's own source comment names this exact case. The row now records the repo as retired without
claiming a workspace path. 61/61.

**`check_links.py`** — my own doing, and the neatest illustration of the problem: the first draft of
the paragraph above quoted the dead path verbatim in backticks, so the document *describing* the fix
became the repo's only unresolved path. Re-worded; clean.

---

## What this lane does NOT do

- **No allow row is added, widened or re-spelled.** Machine-checked, not eyeballed: `families.json`'s
  allow array is byte-identical (85 → 85), deny goes 33 → 34 with exactly one new entry and no
  existing entry modified, and both rendered allow arrays are byte-identical to `origin/main`.
- **`.claude/settings.json` is untouched**, by design: Claude has no deny list, so the new family
  renders nothing there. If that file ever moves in this diff, the change was not what was planned.
- **`allow-find` is not re-widened to Antigravity.** SCC-405 backed it out because a bare `find`
  token there grants `find . -delete`.
- **The sibling wrappers are not swept.** Measured at the tip, `env -i`, `env FOO=1`, `nice`,
  `xargs` and `command` in front of `rm -rf /` all read *ask* on all three platforms — safe today,
  and the same class as this defect. `nice`, `xargs` and `command` are general-purpose and denying
  them wholesale could bite real work, so they go to the open rolling ticket
  [SCC-411](https://sudo-command.atlassian.net/browse/SCC-411) as one row.
- **`deny-git-c` is not widened.** A first pass at the cluster fix caught that pre-existing family
  too; it was reverted. Git's `-C` is a non-clusterable top-level option, so the change would have
  been inert at best and is out of this lane's scope either way.

---

## Your Actions

Two commands, both on this one box, both after the merge:

```bash
# 1. Zoo Code - QUIT VS CODE FULLY FIRST (all windows). The apply refuses while it runs.
#    One run covers both stores.
python3 .agents/scripts/zoo_permissions_apply.py --apply

# 2. Antigravity - READ THIS FIRST. Its apply REPLACES both grant arrays rather than merging,
#    so every store-only allow row not yet harvested into families.json is deleted.
python3 .agents/scripts/antigravity_permissions_apply.py --status
```

For #2 my recommendation is to harvest before applying: run `/smh-llm-approvals`, which is the door
built to turn those store-only clicks into tracked families, and apply after. Applying first loses
them.

Until #1 runs, `env -C /tmp rm -rf /` still reads *ask* on this box rather than *deny*. Ask is safe
— nothing auto-runs — it is simply weaker than the repo now claims.

---

review-runtime: fan-out

## Code Review (2026-09-04)

Verdict: PASS @ c6f1232f
Suite evidence measured on: c6f1232f — `run_all.py` 75/75 through `gate_receipt.py`, clean tree, receipt at [gates/suite.json](gates/suite.json); `permission_render --check` in sync. The last code-bearing commit is `0326278c`; everything after it is record.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
dispositions:    per-lens: blind-hunter=14/3/0 · edge-case-hunter=4/1/0 · literal-correctness-hunter=5/0/0 · acceptance-auditor=7/0/0 · test-adequacy-auditor=5/0/0
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — the plan's Declared Change Set was AMENDED during this review with the two forced doc edits; the reconciler now returns all four arrays empty

**Scope:** the full `origin/main...HEAD` diff, 12 files, re-taken after Step 0.7.
**Method:** five lenses in parallel, each in its own clean context; the four repo-reading lenses each
in their own isolated worktree copy of the lobby (`lens_isolation: worktree`), the Blind Hunter with
the diff alone and no repo access. Every finding was re-measured by me before it was acted on — the
Blind Hunter has no repo access, so its claims are inferences until run.

**Changes applied: substantial.** 31 findings survived triage and every one was fixed in this lane;
4 were dismissed with reasons; nothing was deferred and no ticket was produced.

### Findings

| # | file:line | severity | failure scenario | disposition |
|---|---|---|---|---|
| 1 | `approval_stops.py:83` | blocking | `Bash(*)` strips to `""`; `"rm -rf /".startswith("")` is True, so `covered()` returns True for every command and the door reports zero stops forever — the SCC-407 silence, re-introduced by this lane's own one-liner. Measured: `allow_prefixes -> ['']`, `covered('rm -rf /') -> True`. | applied @ `df521a6a` — rows that strip to nothing are dropped; `test_D_d` + mutant MA |
| 2 | `approval_stops.py:covered/report_head` | important | `Bash(ls *)` yields prefix `ls`; a bare `startswith` marked `lsof -i :3000`, `lsblk` and `git statuses` as already-approved and dropped their stops. Pre-existing, and the mirror of the filed bug. | applied @ `df521a6a` — new `_matches()` boundary rule; `test_D_g` + mutant MB |
| 3 | `families.json` `deny-env-chdir` | important | `env -u GITHUB_TOKEN -C /tmp rm -rf /` — one `env`, `-u` before `-C` — read `ask` on all three. The house wraps nearly every git/gh call in that prefix, so it is the likeliest spelling here. Verified runnable on coreutils 9.4. | applied @ `0326278c` — denied on Zoo and Antigravity, twin added to `DESTRUCTIVE` |
| 4 | `families.json` `deny-env-chdir` | important | `env -iC /tmp rm -rf /` — a legal getopt cluster — walked through. `_ag_token` has carried a cluster rule since the SCC-378 review, but an explicit `render:` bypasses derivation, so it never ran. | applied @ `0326278c` — Antigravity token regex is now the renderer's own cluster class; Zoo's limit documented as a residual |
| 5 | `families.json`, `test_permission_parity.py` | important | Six shipped deny rows had no twin in `DESTRUCTIVE`. Deleting all of them and re-rendering left the battery at **99/99** — half the fence this lane adds was unfalsifiable by its own battery. | applied @ `0326278c` — 10 twins, one per claimed spelling; each group proven load-bearing by deletion |
| 6 | `test_approval_stops.py` | important | Three mutants survived the whole suite: `break` removed, `if suffix in body`, `body.rstrip(":* ")`. M4 chops a character off any row with an interior star — a wrong-short prefix over-covers, the exact error this lane exists to fix. | applied @ `df521a6a` — interior-star row in `D_b` and the new `D_e`; all three now red |
| 7 | `walkthrough.md:261` | blocking | The walkthrough quoted the retired `Projects/Fresh_Workspace_BMAD/...` path in backticks while narrating its removal, so `check_links.py` exited 1 on the repo's only dead path — the document describing the fix became the defect. | applied @ this commit — re-worded; `check_links` clean |
| 8 | `approval_stops.py:80` + 4 sites | important | "battery A2b" — A2b is in `test_settings_allowlist.py`, not the parity battery (`grep A2b test_permission_parity.py` → no match). A load-bearing comment sending the next maintainer to a file where the check does not exist. | applied @ `df521a6a` — corrected in the script, the test docstring, the plan and the INDEX row |
| 9 | `implementation_plan.md` Declared Change Set | important | Two files edited and never declared, so `declared_change_set.py` returns two `undeclared` rows on every later run of the gate, close-out included. | applied @ this commit — plan amended with both bullets and a note saying why; reconciler now empty |
| 10 | `walkthrough.md` Step 7 / Step 4 blocks | suggestion | Three fenced blocks presented as terminal output were hand-composed: a glob `git diff --name-only` never prints, `ag=[same four]`, and dropped check titles. In a lane whose thesis is "the instruments were lying", synthesised instrument output is the wrong artifact. | applied @ this commit — real output pasted, and A2/A12's four-entry truncation is now stated |
| 11 | `walkthrough.md` mutant 2 | suggestion | "the `break` is unreachable as a behaviour change because `*` is last" — false. `Bash(X* *)` double-strips without it; what the break stops is a second strip on the same body, not a fourth suffix. | applied @ `df521a6a` — reasoning corrected, and the behaviour is now held by `test_D_e` |
| 12 | `implementation_plan.md` pre-mortem | suggestion | "the applies are per-machine (Mac *and* PC)" — the machine model SCC-398 retired. An operator reading it would defer the apply believing a second seat exists. | applied @ this commit — corrected to ONE PC, with the correction marked |
| 13 | `families.json` `why`, guide | important | Both claimed the wrapper was closed while four spellings of an open-ended grammar were denied. | applied @ `0326278c` — eight spellings enumerated, two residuals named, both landing on `ask` |
| 14 | `walkthrough.md` Step 7.5 | nit | "52 store-only allow rows **will be DELETED**" written as a hard fact inside an operator instruction; it read 58 two hours later. | applied @ this commit — phrased as "read `--status` for today's figure" |
| 15 | `tdad_stack_install_guide.md:165` | important | The T9 fix moved the path out of the shape the test matches rather than removing the stale claim. | applied @ this commit — the row records the repo as retired and carries no path token |
| 16 | `walkthrough.md` Step 6 | nit | A6 described as a drift check; it is a parity row. | applied @ this commit |
| 17 | `test_approval_stops.py` `D_c` | suggestion | `assert not r["stops"]` passes identically when the fixture is broken and the transcript is never read — the vacuous green the file's own docstring refuses. | applied @ `df521a6a` — control added: same fixture, allow list emptied, must find exactly one stop |
| — | `test_approval_stops.py` glob stub | dismissed | "monkeypatches the stdlib `glob` process-wide" — true, and it is the pattern `_scan()` has used since SCC-407; the `finally` restores it. Matching the file's existing harness beats a local deviation. | dismissed |
| — | `_artifacts/_main/INDEX.md` | dismissed | "undeclared by the plan" — `_artifacts/` is carved out of the reconciliation on both sides by design; the tool confirms it, returning exactly two undeclared rows and not three. | dismissed |
| — | `families.json` schema | dismissed | "`DENY-side only` rests on array position, not a `side` key" — true of all 34 families; the schema has no such key by design, and A2/A3 would catch a relocation. Inventing one here would be a lane-local schema fork. | dismissed |
| — | AG `--chdir.*` over-reach | dismissed | `--chdir-foo` is denied and is not a real `env` flag. Deny-side, so the worst case is refusing a command that would have failed anyway. | dismissed |

### The gates

| Gate | Result |
|---|---|
| Enforcement suite | `75/75 files passed`, exit 0 |
| Toolkit lint | `-- 0 error(s), 0 warning(s), 8 info --` |
| Assertion evidence | `test_approval_stops.py` 24/24 · `test_permission_parity.py` 99/99 · `test_zoo_permissions.py` 25/25 · `test_sops_prds_folder.py` 61/61 · `test_check_maps.py` 35/35 |
| SOP currency | accepted (`[sop-ok]` on each commit, with its reason in the body) |
| Link + anchor | `clean` |
| Door parity | n/a — no command added, renamed or deleted |
| Declared set | `undeclared=0 · unimplemented=0 · incomplete=0` |

One honest note on the suite: an intermediate run read `74/75  FAILED: test_verdict_receipt.py`
while a mutation sweep was rewriting files underneath it. Run alone it is 51/51, and the clean
re-run is 75/75. The number of record is the clean one.

### Step 0.7 — re-derivation

1. **Nothing this diff references moved.** `git merge-base HEAD origin/main` == `origin/main` ==
   `5c444d22`, and `git diff --name-only $BASE..origin/main` returned **0 files** — no lane landed
   while this one was built, so every path, script and rule pointer the diff names still resolves.
2. **True overlap is EMPTY and the merge is clean.** `grep -Fxf mine.txt theirs.txt` returned
   nothing, and `git merge-tree --write-tree --messages HEAD origin/main` returned a bare tree sha
   (`71ae3022`) with no conflict messages.
3. **One sibling lane is live and there is no landing-order dependency.**
   `chore/SCC-380-agent-human-sop` @ `c2a30594`, 9 files, zero overlap with this lane's 12. Worth one
   sentence though: it edits `test_sops_prds_folder.py`, whose T9 check this lane satisfies by a doc
   correction. No textual conflict either way, and if SCC-380 lands first this lane's T9 fix stays
   valid — it removes a stale path, which no version of that test wants.

### Clean-Code Gate

`/smh-clean-code-audit` bound to this worktree, nested — Step 1's drift findings imported rather than
re-hunted, and Step 3's runs imported rather than re-run, per the audit's own no-double-floor rule.

| Check | Result |
|---|---|
| `py_compile` on the two changed scripts | clean |
| Comment contract (§2A) | every new comment states a measured consequence and names its source (SCC-409, SCC-375 A2b, SCC-378, the 2026-09-04 review); the four `⛔` blocks each carry the failure they prevent |
| Convention table (§2C) | matches the file's existing idiom — same `⛔` heading style, same synthetic-fixture harness, same `_leading_underscore` helper naming |
| Machine floor | imported from the gate table above |
| Diff-scoped legacy debt | `.agents/scripts/INDEX.md` still carries no row for `approval_stops.py` (it shipped without one in SCC-407). Noted, untouched, not gated on — `check_maps.py` passes, so the INDEX is curated rather than exhaustive |

**Bloat check on my own fixes:** `_matches()` is 5 lines and replaces two call sites; the empty
guard is 2 lines. No abstraction was introduced for a single use, and no adjacent code was improved.
