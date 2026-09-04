# Walkthrough — /smh-llm-approvals carries its own landing road (SCC-393)

**Date:** 2026-09-04 · **Branch:** `chore/SCC-393-approvals-fast-path` (cut from `origin/main` @ `70154040`)
**Plan:** [implementation_plan.md](implementation_plan.md) · **Ticket:** [SCC-393](tickets/SCC-393.md)

## What was wrong

`/smh-llm-approvals` is 281 lines and describes four steps in detail. Its fourth step is
`Report what changed … Then stop.` — it names no road to `main`. Steps 1-3 modify four tracked
files (`.agents/permissions/families.json` and its three renders), so the door hands the next agent
a working tree it has no procedure for, next to the one branch nothing is allowed to touch
casually. The result is predictable: reach for the heaviest thing available.

Measured on the run that produced this ticket (SCC-392, 2026-09-04): writing twelve allow rows took
minutes. A plan, a worktree, an assert-first cycle, a five-lens review, a pull request, a CI
round-trip and a protected-branch detour took the rest of the day.

Four gaps compounded it, each a sentence the door did not carry:

| Gap | Measured cost |
|---|---|
| Never names `test_permission_parity.py` | All 17 picks written, THEN the battery reported A3/A5/A6/B8 red. Five picks backed out by hand, one at a time |
| Never says the applies need the sandbox off | `antigravity_permissions_apply.py --apply` died `OSError: [Errno 30] Read-only file system` on `~/.gemini/` |
| Never names Road 2 (`gate/**`) | The protected-branch rejection sent the road to be re-derived live, though `main_write_gate.py:216` already calls `gate/**` *the local door's road* |
| `lane_qualify.py` answers `TASK` for `.agents/permissions/` | Correct for a hand edit — but it is the machine signal an agent reads when deciding how much ceremony to spend |

## What changed

**The door, Step 3** — the fence check moves to where it belongs: straight after the render,
before anything is reported. A red row is not a test to fix, it is a pick that cannot land; back
that row out, re-render, and tell the operator which pick was refused and *which deny row of his
own refused it*.

**The door, Step 4 (new)** — the landing road, explicit end to end: the `chore/<KEY>-<slug>`
branch, the explicit-path commit, the local `--no-ff` merge, the Road 2 `gate/**` push that lets
the required check attach, the minted single-use token, the push. Plus the two operational facts
nothing stated: the applies need the Bash sandbox off, and `.git/config.lock` can appear as a
character device under the sandbox rather than a stale lock.

**The rule** — `/smh-llm-approvals` becomes a third named exemption in
`artifacts-always-first.md` § When to Skip, beside `/cicd-quick-dev` and `/smh-quick-fix`.
Invoking it IS the skip-the-plan instruction, conditional on four machine-checkable guards.

### The design decision worth stating

⛔ **The exemption keys on the COMMAND, and `lane_qualify.py` was deliberately left alone.**

The obvious fix was to teach the qualifier that `.agents/permissions/*.json` is data rather than
toolkit code. That would have been wrong. The qualifier classifies by path and cannot see this
door's guards, so widening it would hand the same pass to a hand edit that has no operator pick, no
forced `--check` and no forced battery run — i.e. to the exact case the full lane exists for. Both
existing exemptions in that list are command-named for the same reason. Cost of leaving it: the
machine still answers `TASK` for these paths, which is why the door says so explicitly and tells
the reader not to "fix" it.

**Why the change class earns an exemption at all:** there is no design to review — the door
dictates the row shape — and no assertion to write, because the battery already exists, already
guards the fence, and is auto-discovered by `run_all.py`. Empirically the ceremony did not catch
what mattered: on SCC-392 the plan and the five-lens review both passed five fence-tearing rows,
and the battery caught all five in seconds. The test is the gate here; the lane was only cost.

## Evidence

```
python3 .agents/scripts/tests/test_permission_parity.py --on-main    91/91
python3 .agents/scripts/tests/run_all.py                            73/73 files
python3 .agents/scripts/permission_render.py --check                 in sync (zoo, claude, antigravity)
python3 .agents/scripts/lane_qualify.py (this lane)                  TASK - so THIS change took the full lane
```

Block **H** (H1-H7) in `test_permission_parity.py`. H1/H2/H3/H5 were seen RED before the change:

```
[FAIL] H1 the door has a landing step that names Road 2 - not a `Then stop.` ending: gate/=False write_gate=False
[FAIL] H2 Step 3 names the fence battery, so damage is found BEFORE the report, not after
[FAIL] H3 the APPLY region - not Step 1's unrelated caveat - states the sandbox must be off: region=2539ch
[FAIL] H5 the rule's When-to-Skip names the door AND all four guards it is conditional on: named=False
```

⛔ **H3 shipped vacuous on first writing and was caught before commit.** `"sandbox off" in body`
passed on Step 1's caveat about `claude_permissions_status.py` — a different script and a different
failure — so the assertion was green while the gap it names was wide open. It is now pinned to the
apply region (`body[body.find("zoo_permissions_apply.py"):]`) and to the real error string. Same
defect class as G8a directly above it in the same file, found the same way: by asking which slice
the assertion actually reads.

## Your Actions

1. Nothing, for this change — it lands through the normal road with the gate green.
2. **Next time you run `/smh-llm-approvals`,** it will check the fence before reporting and land
   its own change. If it ever asks you to approve a plan for a straight harvest again, that is a
   regression in this ticket.
