# SCC-358 — the close-out ledger rides the PR

review-runtime: fan-out

Lane `chore/SCC-358-ledger-rides-the-pr` · 2026-08-31 · Plan: [implementation_plan.md](implementation_plan.md) · Manifest: [task.yaml](task.yaml)

## What this closes

`/cicd-push-e2e` was the last close-out door that wrote its bookkeeping **after** the merge, standing
on `main`, as a new direct push. That stopped being possible the day both repos went to an armed
server-side ruleset (lobby SCC-118 id 20756052; AviationChat AVCH-111 id 21963341, armed 2026-08-31):
a required check means a pull request is the only road in, so the post-merge write is a direct push
the gate refuses **by design**. It was found the hard way at the AVCH-111 close-out, where the ledger
commit needed its own operator approval and a hand-built `--no-ff` merge just to land.

**The law is not new — this was the last door without it.** `/smh-close-task-merge-tree` commits its
flight event pre-merge at Step 2.5 and carries an outright ban on post-merge commits, an instruction
that *"used to say the opposite, and that instruction was the whole of SCC-175"* — whose refusal
banner's `reset --hard` remedy then destroyed three other sessions' uncommitted work (SCC-180).
`/cicd-close-story-merge-tree` rides its board writes on the story branch. This ports the same law to
the third door.

## Task Checklist

| | Item |
|---|---|
| ✅ | `CS-21` in `test_command_surfaces.py` — eight checks (A, B, C1, C2, D, E, F1, F2, G, H) plus four controls, written RED first |
| ✅ | `cicd-push-e2e.md` — new **Step 3.5**, the bookkeeping committed on the epic branch before `gh pr create` |
| ✅ | `cicd-push-e2e.md` — Step 4's gated-tip sentence qualified for the one artifacts-only commit |
| ✅ | `cicd-push-e2e.md` — Step 3's `(Step 6)` cross-reference repointed to `(Step 3.5)` *(audit finding F2)* |
| ✅ | `cicd-push-e2e.md` — Step 5.5's PRD reconcile records to the ticket comment only, with the reason it cannot ride the PR |
| ✅ | `cicd-push-e2e.md` — Step 6 is prune + verify, carrying the ban and naming SCC-175 / SCC-358 |
| ✅ | `cicd-push-e2e.md` — Step 6.5's comment gains the slot for the Step 5.5 PRD line |
| ✅ | `commands/INDEX.md` — the routing index no longer describes a post-merge ledger *(audit finding F1)* |
| ✅ | `workflows_testing_SOP.md` — currency row, the command-atlas diagram (new `S35` node), and a §7 paragraph |
| ✅ | `workflows_testing_SOP_changelog.md` — one row, dated, ticket-keyed |
| ⚠ | `.opencode/commands/cicd-push-e2e.md` re-mirrored **in-lane, by byte copy, not by running the sync** — see `## Evidence`, "the correction the gate made" |

## Evidence

| AC | Assertion | Result |
|---|---|---|
| AC-1 | `CS-21 A` + `CS-21 B` — Step 3.5 writes both halves, and its offset precedes `gh pr create` | RED → GREEN |
| AC-2 | `CS-21 C1` + `CS-21 C2` — the `--after-merge` half instructs no `git commit`; Step 6 owns neither write | C1 standing green, C2 RED → GREEN |
| AC-3 | `CS-21 D` — Step 3.5's commit fence carries `<JIRA-KEY>` | RED → GREEN |
| AC-4 | `CS-21 E` — Step 6's ban names SCC-175 and SCC-358 | RED → GREEN |
| AC-5 | `CS-21 F1` + `CS-21 F2` — neither the door nor the SOP sends the reconcile to a ledger row | RED → GREEN |
| AC-6 | `CS-21 G` — Step 6 does not hand-append to the home-base INDEX | RED → GREEN |
| — | `CS-21 H` — the routing index does not describe a post-merge ledger *(added by the self-audit, F1)* | RED → GREEN |

**The RED, at `13ffe716` — nine real failures, four controls green, C1 the predicted standing guard:**

```
$ python3 .agents/scripts/tests/test_command_surfaces.py --case "CS-21"
[FAIL] CS-21 A Step 3.5 writes BOTH the ledger row and active-context: ... <no Step 3.5 section at all>
[FAIL] CS-21 B ORDER Step 3.5 -> gh pr create
[PASS] CS-21 C1 the --after-merge half instructs no `git commit`
[FAIL] CS-21 C2 Step 6 owns NEITHER the ledger row nor active-context: ... ## Step 6 — Prune the epic branch + update the ledger
[FAIL] CS-21 D Step 3.5 commits with the JIRA key in the subject
[FAIL] CS-21 E Step 6 carries the post-merge commit ban, with its scars named
[FAIL] CS-21 F1 the door's reconcile no longer records to the ledger row
[FAIL] CS-21 F2 ...and neither does the SOP's currency table
[FAIL] CS-21 G Step 6 no longer hand-appends to the home-base INDEX
[FAIL] CS-21 H commands/INDEX.md does not describe a post-merge ledger
[PASS] CS-21 CONTROL a door with no Step 3.5 fails A
[PASS] CS-21 CONTROL bookkeeping placed AFTER the PR fails B
[PASS] CS-21 CONTROL a commit with no <JIRA-KEY> fails D
[PASS] CS-21 CONTROL a ban with no scars named fails E
-- 5/14 passed --
```

⭐ **Each red names its own reason, which is the check that the red is real.** `A` reports *"no
Step 3.5 section at all"* and `C2` quotes the live Step 6 heading — neither is a setup failure
wearing a red's clothes (`red-test-can-die-before-its-assertion`).

**The GREEN, at `9b19b47d`:**

```
$ python3 .agents/scripts/tests/test_command_surfaces.py --case "CS-21"
-- 14/14 passed --
```

**The mutation sweep — 8/8 killed, each by its DECLARED case:**

```
$ python3 .agents/scripts/mutation_sweep.py --table _artifacts/_main/2026-08-31_ledger-rides-the-pr/sweep.json
-- sweep: 8 mutant(s) over 3 file(s) @ 9b19b47d --
KILLED    M1 the ledger write creeps back into Step 6 (the exact regression)   -> CS-21 C2
KILLED    M2 the lobby hand-append creeps back into Step 6                     -> CS-21 G
KILLED    M3 Step 5.5 records to the ledger row again                          -> CS-21 F1
KILLED    M4 the SOP's currency table says the ledger row again                -> CS-21 F2
KILLED    M5 the routing index describes a post-merge ledger again             -> CS-21 H
KILLED    M6 ORDER ONLY - Step 3.5 survives intact but the PR is named before it -> CS-21 B
KILLED    M7 the bookkeeping commit loses its JIRA key                         -> CS-21 D
KILLED    M8 a commit is instructed AFTER the merge again (the standing guard) -> CS-21 C1
-- restore verified: bytes match, nothing was committed, and `git diff --quiet 9b19b47d` is clean --
-- full file, unfiltered: python3 .agents/scripts/tests/test_command_surfaces.py -> exit 0 --
        | -- 260/260 passed --
-- sweep clean: 8/8 killed by their declared case --
```

⭐ **Every mutant is drawn from the shipped text, not from the cases** — each one re-plants the
retired instruction on the real surface (`M1` and `M2` put the two Step 6 writes back; `M5` restores
the routing index's stale tail). `M6` is the one that earns its keep: it leaves Step 3.5 completely
intact and only names the PR earlier, so a presence-only guard would sail past it. That is the
`source-grep-guards-cannot-see-order` failure mode, planted deliberately and killed.

### ⚠ The correction the gate made, recorded because the plan got it wrong

The plan's step S8 concluded that `sync-agents.ps1` was a **no-op** for this lane, reasoning that the
door's `description:` frontmatter was unchanged and the platform launchers are thin pointers carrying
only that description. That was right about the launchers and **wrong about opencode**: the
`.opencode/commands/` mirror is a **full byte copy of the brain**, so any body edit stales it. The
suite caught it — `every mirror door still says what its brain says: 1 drifted`.

It is re-mirrored here by byte copy rather than by running the sync, and that is a deliberate call
with a reason: `sync-agents.ps1 -WhatIf` showed the full run regenerates all ~70 doors **and writes
the machine-global caches** (`~/.config/opencode/commands`, `~/.gemini/antigravity/global_workflows`).
Run from an unmerged lane, that publishes unlanded work into every other project's menu. The mirror
was verified byte-identical to the brain at `origin/main` before the copy, so the result is exactly
what the sync would have produced for this file and nothing else. **The real `/smh-sync-agents`
belongs after the merge, run from `main`** — it is listed in `## Your Actions`.

### The full suite

```
$ python3 .agents/scripts/tests/run_all.py     (before the fixes)
65/67 files passed  FAILED: test_check_maps.py, test_command_surfaces.py
```

Both reds were this lane's own and both were legitimate: `test_command_surfaces.py` was the opencode
mirror above, and `test_check_maps.py` F2 was this session folder missing its ledger row in
`_artifacts/_main/INDEX.md` — which is a pleasing way for the ledger ticket to be caught. Both fixed;
the receipt below is the run of the code that actually lands.

## Your Actions

Everything in this lane's scope landed and is proven above. Two things are genuinely yours.

- [x] The merge itself — lands via this branch's PR
- [ ] Run `/smh-sync-agents` **after this lands, from `main`**, so the machine-global command caches
      (`~/.config/opencode/commands`, `~/.gemini/antigravity/global_workflows`) pick up the reworked
      door. It is deliberately not run from this lane: the sync writes machine-global caches, and
      doing that from an unmerged branch publishes unlanded work into every other project's menu.
      This is also the standing item you flagged this session.

**Raised once, with its remedy, and already filed — not left as a bill.**
[SCC-359](https://sudo-command.atlassian.net/browse/SCC-359) (Subtask of the rolling ticket SCC-318):
`/smh-quick-dev` Step 1.5 condition 3 can never pass for a lane that follows `/smh-plan-task` Step 5's
own convention. Step 5 requires the approval line to carry the sha of the commit that recorded it —
not knowable until that commit exists — so the planner writes `<pending>`, commits, then stamps the
real sha in a **second** commit. The last-touch sha is therefore always the stamp commit, never the
recorded one. Measured twice: SCC-347 (recorded `acb02585`, stamped `cf198990`) and this lane
(recorded `4fdedf2f`, stamped `13ffe716`), and in both the entire delta between the two shas is the
one placeholder line. It did not block this lane, because your approval was given live in this
session rather than read off disk.
