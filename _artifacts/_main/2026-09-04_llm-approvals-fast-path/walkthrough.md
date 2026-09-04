# Walkthrough — /smh-llm-approvals carries its own road (SCC-393)

**Date:** 2026-09-04 · **Branch:** `chore/SCC-393-approvals-fast-path` (cut from `origin/main` @ `70154040`)
**Plan:** [implementation_plan.md](implementation_plan.md) · **Ticket:** [SCC-393](tickets/SCC-393.md)

## What was wrong

`/smh-llm-approvals` was 281 lines describing four steps, and its fourth was
`Report what changed … Then stop.` — it named no road to `main`. Steps 1-3 modify four tracked
files (`.agents/permissions/families.json` and its three renders), so the door handed the next
agent a working tree it had no procedure for, next to the one branch nothing may touch casually.
The result was predictable: reach for the heaviest thing available.

Measured on the run that produced this ticket: writing twelve allow rows took minutes; a plan, a
worktree, an assert-first cycle, a review, a PR, a CI round-trip and a protected-branch detour took
the rest of the day.

Three more gaps compounded it, each a sentence the door did not carry:

| Gap | Measured cost |
|---|---|
| Never names the enforcement suite | All 17 picks written, THEN the gates went red. Six picks backed out by hand, one at a time |
| Never says the applies need the sandbox off | `antigravity_permissions_apply.py --apply` died `OSError: [Errno 30] Read-only file system` on `~/.gemini/` |
| Never names any road | The protected-branch rejection sent the road to be re-derived live |

## What changed

**Step 3** now runs `run_all.py` straight after the render, before anything is reported — and the
whole suite, not the permission battery alone, because a picked row can break a law the battery
does not run. It also distinguishes the two kinds of red: a pick the fence refuses (back it out,
name the deny row — or the battery case, for `npx`, which no deny row refuses), and a pick so good
it *resolved* a known disagreement, where backing out would throw away a correct pick.

**Step 4** is new: run the scope guard, write a lean walkthrough carrying the operator's words
verbatim, stamp it with `flight_recorder.py`, commit by explicit path, push the branch,
`gh pr create`, **stop**.

**The rule** gains `/smh-llm-approvals` as a third named exemption in
`artifacts-always-first.md` § When to Skip, conditional on four guards.

### The design decision worth stating

⛔ **The exemption keys on the COMMAND, and `lane_qualify.py` was deliberately left alone.** The
obvious fix — teach the qualifier that `.agents/permissions/*.json` is data — would hand the same
pass to a hand edit that has no operator pick, no forced `--check` and no forced suite run. Both
existing exemptions are command-named for the same reason.

**Why the change class earns an exemption, stated accurately.** There is no design to review and no
assertion to write; the gates already exist. The evidence is the SCC-392 harvest — and the honest
version of it is *not* "the ceremony passed five bad rows and the battery caught them". That run
carried **no plan, no walkthrough and no review at all** (its branch touched zero `_artifacts/`
files). It wrote seventeen picks and the **suite** caught every bad one: four by deny rows, one by
a battery case, one by the one-interpreter law. The claim that survives is the one that matters —
the machine, not the ceremony, is what protects this file.

## Evidence

```
python3 .agents/scripts/tests/run_all.py                 73/73 files
python3 .agents/scripts/tests/test_permission_parity.py  99/99
python3 .agents/scripts/tests/test_door_preflight_order.py  62/62
python3 .agents/scripts/permission_render.py --check     in sync (zoo, claude, antigravity)
python3 .agents/scripts/workflow_lint.py --toolkit-only  0 errors, 0 warnings
python3 .agents/scripts/check_links.py --base origin/main  clean
python3 .agents/scripts/declared_change_set.py           incomplete=[] undeclared=[] unimplemented=[]
python3 .agents/scripts/lane_qualify.py (this lane)      TASK - so THIS change took the full review
```

`sop_currency.py` passes, and was proven non-vacuous by a control run without the SOP staged, which
rejects loudly.

**Mutants run against the final assertions, both killed:**

```
M1  restore the banned road (checkout main / merge --no-ff / mint token / push origin main)
    -> H1 red, plus 4 rows of test_door_preflight_order red
M2  replace the exemption with its literal inverse ("is NOT exempt ... takes the FULL lane")
    -> H5 red  (bullet=342ch)
```

review-runtime: fan-out

## Code Review (2026-09-04)

lenses_run:
- blind-hunter · ok
- gate-integrity · ok
- acceptance-auditor · ok
lenses_counted: 3/3
lenses_na: none
findings: 3 FAIL · 12 patch · 0 defer
dispositions: per-lens: blind-hunter=12/0/0 · gate-integrity=8/0/0 · acceptance-auditor=6/0/0
severity_floor: FAIL (at review time; every finding fixed in-lane before this verdict)

**The three FAILs, all fixed:**

1. **Step 4 built a road `git-policy.md` bans.** `git checkout main && git merge --no-ff`,
   `mint-push-token.sh`, `git push origin main` — against *"No agent merges to `main` in this repo.
   There is no eligibility test, no 'small enough' class, no self-merge"* and *"No command may
   change which branch a checkout is on."* It also laundered a permission pick into merge
   permission, the SCC-37 substitution that rule names by title. **Fixed:** Step 4 ends at
   `gh pr create`. **And the suite could not have caught it** —
   `test_door_preflight_order.py` asserts *"no live door takes that road"* over a hardcoded `DOORS`
   dict of one, so the sentence was false while it said so. This door is now in that dict.
2. **The battery was blind to `read_file` grants.** A row `{"cmd": "/home/dlohn", "grant":
   "read_file"}` renders to a recursive read of the home directory — `~/.ssh`, cloud credentials,
   every `.env` — while `--check` prints *in sync* and the whole battery stays green, because its
   corpus is commands. **Fixed:** A16 + its control A16b.
3. **The exemption's guard 3 did not cover the change class.** It named
   `test_permission_parity.py`; the one-interpreter law that refused SCC-392's harvested `python`
   lives in `test_settings_allowlist.py`, which the battery does not run. **Fixed:** guard 3 is
   `run_all.py`.

**Five of seven H assertions were vacuous on first writing**, each proven by an executed mutant:
the fence-battery block was moved into Step 5 under *"afterwards, if you feel like it"* and the
ordering check stayed green; the apply paragraph was deleted and the sandbox check stayed green on
an unrelated match in Step 4; the exemption was replaced with its inverse and the rule check stayed
green. Every row is now scoped to the section whose property it names; H0 fails if a heading is
renamed; H6 **runs** `lane_qualify` instead of grepping it; the duplicate of E4 is deleted.

**Three false claims in the record, all corrected:** "a widened `find`" was fabricated (`find` was
a deliberate scoping call, never a battery red); "five could not land" was six (`python`); and the
claim that the ceremony had reviewed those rows was false.

Verdict: CONCERNS @ 042852b7

Every finding is fixed and every gate is green, and the two assertions guarding the safety
properties are mutation-proven. CONCERNS rather than PASS is deliberate and is about this lane's
history, not its final state: the first cut shipped a rule violation that only the review caught,
and five of seven new assertions did not test what they claimed. A full mutation sweep across all
thirteen assertions was not run — two were, plus four seen red-then-green.

## Your Actions

1. **One product decision is yours, and it is the point of this change.** You are approving a
   standing exemption that lets `/smh-llm-approvals` skip the plan, the self-audit, the RED-first
   assertion and the review verdict for a permission harvest. What it does **not** skip: the Jira
   key, the `chore/` branch, the record, the full suite, or your click on *Merge pull request*.
   The road to `main` is unchanged — this door opens a PR and stops, like every other door.
2. **Nothing to run.** This lane lands as a PR you merge.
3. **Next time you run `/smh-llm-approvals`** it will check the fence before reporting and take
   itself to a PR. If it ever asks you to approve a plan for a straight harvest, that is a
   regression in this ticket.
