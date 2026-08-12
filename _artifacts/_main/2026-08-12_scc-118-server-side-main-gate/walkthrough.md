# SCC-118 — walkthrough: the main gate never ran on a GitHub-side merge

**Lane:** `chore/SCC-118-server-side-main-gate` · **Base:** `main` @ `8556e81` (SCC-122 absorbed)
**Status:** built, gated, and **proven live in both directions**. Merge-ready — handed back for
`/smh-close-task-merge-tree`.

---

## 1. What was broken, and the fact that decided the fix

A git hook lives on a machine and fires at `git push`. A merge performed on GitHub's servers — the
web *Merge pull request* button, or the REST API — never touches a machine, so the SCC-77 gate is
not bypassed there: it is **absent**. PR #2 (`dabb3c3`) landed on `main` that way from a web session.

The obvious fix is "restrict who may merge." Checking killed it:

```
PR #2:  merged_by = sudomadhatter (User)   committer = web-flow
```

**The agent merged as the operator.** Not a bot, not a separate app — the same GitHub identity. So
there is no *who* to restrict: any rule that lets the operator through lets an autonomous agent
through with it. The only server-side discriminator left is a **required status check**, keyed to
the commit. Every design decision below follows from that one finding.

## 2. What crossed to the server, and what could not

⛔ **This is not a port of the local hook**, and the code says so in three places on purpose.

| Half | What it proves | Can it live on a server? |
|---|---|---|
| **Authorisation** — token under `.git/`, 30-min TTL, one sign-off = one merge | *You said yes, once, for this merge* | **No.** The token by design never leaves the machine, and identity cannot stand in for it (§1). |
| **Enforcement** — real suite, toolkit lint, merge shape, source branch | *The change is fit to land* | **Yes.** This is what shipped. |

Neither half covers the other's ground. Claiming otherwise would be exactly the fiction
`tests-must-gate-for-real` exists to forbid, so the rule, the SOP and the script docstring all state
the limit rather than implying coverage.

## 3. What shipped

| File | Change |
|---|---|
| `.github/workflows/main-write-gate.yml` | **new — this repo's first CI.** Suite + lint + validator, no soft steps |
| `.agents/scripts/main_write_gate.py` | **new** — authorised source (`pr`) and merge shape (`gate`), plus SOP currency across the landing set |
| `.agents/scripts/tests/test_main_write_gate_ci.py` | **new** — 38 checks incl. a 6-mutant battery |
| `.agents/scripts/tests/test_door_preflight_order.py` | **new** — 12 checks, ordering isolated by relocation |
| `.agents/scripts/tests/test_main_ruleset_armed.py` | **new** — asks GitHub whether the gate is switched on |
| `.agents/commands/smh-close-task-merge-tree.md` (+ opencode mirror) | pre-flight step; **mint moved after the wait** |
| `.agents/rules/git-policy.md` | layer 3 of the write gate, with its scope limit |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | two safety-net rows, the merge-procedure change, the break-glass |
| `.agents/scripts/parallel_check.py` | machine dependency removed (§6) |
| `.agents/scripts/tests/test_sops_prds_folder.py` | T9 narrowed for runners only, with 4 controls (§6) |
| GitHub ruleset `20756052` | **armed**, `bypass_actors: []`, `current_user_can_bypass: never` |

## 4. Two corrections to the approved plan, both found by building

**① The plan said "both doors". That was wrong, and the wrong version was worse than nothing.**
`/cicd-push-e2e` is a `cicd-*` command, so it binds exactly one **project** and never the lobby: it
ships `epic/*` branches in project repos, which publish no `main-write-gate` check. A pre-flight
wait there would poll **forever** for a check that never appears — every AGY ship, a hang. The door
is untouched, and `test_door_preflight_order.py` now carries a standing guard that the pattern is
not copied into it by a later well-meaning edit. Giving a project the server-side half is its own
ticket in its own tracker.

**② Ordering between mint and wait is load-bearing.** The token's TTL is 30 minutes. The door has
always minted immediately before the push, which was correct when nothing sat between. Insert a CI
wait there and a slow run silently eats the token: everything else passes, the push dies on *"stale
token — it has been discarded"*, and a close-out that already did all its work has to be re-run. The
door mints **after** the wait, and the test asserts the index order with a reversed mutant.

## 5. Proof — both directions, on the real repo

`tests-must-gate-for-real`: one half is not a gate.

| Direction | Case | Result |
|---|---|---|
| **REJECTS** | PR #4 from `claude/scc-118-negative-control` — the same shape as PR #2 | `mergeable_state=` **`blocked`**, `0` check runs |
| **ALLOWS** | PR #3 from `chore/SCC-118-server-side-main-gate`, check green | `mergeable_state=` **`clean`**, `main-write-gate: success` |

⭐ **The reject is stronger than designed, and the reason is worth recording.** The negative-control
branch was built from `main`'s tree, so it does not *carry* the workflow — and for a `pull_request`,
GitHub runs the workflow from the **head**. That PR therefore dodged CI entirely: **zero** check
runs. It was still refused, because a required check that never reports is never satisfied. So a PR
cannot escape the gate by predating it or by deleting the workflow on its own branch.

**Gate mode was rehearsed live too**, because it had never run anywhere but a synthetic repo — and
this whole ticket exists because a gate was never exercised. A real merge commit
(`1b95bd5`, parents `8556e81` + `b308d8b`) was pushed to `gate/main-1b95bd5`:

```
20/20 files passed
[PASS] merge shape
-- main-write-gate: pass --
```

Run `31618946326`. The ref was deleted afterwards; `main` was never pushed.

## 6. Two machine dependencies the first CI run exposed

Running the suite off a laptop for the first time is what this ticket bought, and it immediately
found two places where the suite was testing **the operator's machine**, not the repo.

**`parallel_check.py` — a dry run required a binary it never calls.** `cmd_stamp` resolved the `acli`
binary unconditionally, then guarded every *use* of it behind `apply`. So a preview that writes
nothing died with "acli not found" anywhere without the Jira CLI. `test_parallel_check`'s docstring
already claimed *"offline by construction: nothing reaches acli or the network"* — true of the
network, false of the binary, and unnoticed because it had only ever run on two machines that both
have it. Verified the way the failure had to be reproduced, not just that it passes here:

```
python3 tests/test_parallel_check.py                    46/46
PATH=/usr/bin:/bin ACLI_BIN= python3 ...                46/46
```

**T9 — a doc-link gate that cannot be answered on a runner.** It resolves backticked paths against
what is on disk; most point into the `Projects/` submodules. On a runner it reported 8 paths as
"resolves nowhere", every one of them correct.

⛔ The round-3 ruling above `uncloned_note` — *"the check stays STRICT, and the failure carries its
own remedy"* — **is not reversed.** It rests on an assumption true of every checkout that existed
when it was written: the remedy is actionable. Tell a laptop `git submodule update --init` and it
complies. **4 of the 9 declared submodules are private**, and a runner holds no credential; supplying
one would mean parking a token with read access to every private repo inside a **public** repo's
Actions, to satisfy a doc-link check. There the remedy is *unavailable*, not unrun — and a gate
permanently red on a correct state is the disease that same ruling named, reached from the other
side. So T9 narrows only where all three hold: something found, projects genuinely missing, and the
platform declaring itself a runner. Keyed on the environment, never on the shape of the findings —
`unresolved_paths` says outright that no honest per-token classifier exists, and inventing one is how
that file has twice shipped a fix nothing could falsify.

Four controls, and **C-T9a is the one that matters** — it proves the gate is *unchanged* where it
counts. Asserting only the CI case would have proved the softening and not the strictness:

| Control | Expected |
|---|---|
| C-T9a developer checkout | still **HARD FAILS** |
| C-T9b runner, projects uncloned | inconclusive `[SIGNAL]` |
| C-T9c runner, **complete** checkout | still **HARD FAILS** |
| C-T9d nothing found | never "inconclusive" |

**Consequence, stated rather than left to be discovered:** doc links are gated by the local suite,
not by CI. A green check is not a claim about them. That sentence is in the SOP.

## 7. Gate evidence @ `b308d8b`

```
python3 .agents/scripts/tests/run_all.py            20/20 files passed   exit 0
python3 .agents/scripts/workflow_lint.py --toolkit-only
                                                   0 errors, 0 warnings  exit 0
CI (ubuntu-latest, run 31617587914)                20/20 files passed   success
CI gate-mode  (run 31618946326)                    [PASS] merge shape   success
test_main_ruleset_armed.py                         5/5 (armed, bypass list empty)
```

Both suite runs were bare, not piped — a pipe would have reported `tail`'s exit code, not the gate's.

## 8. ⚠ Your actions

1. **Close out this lane** — `/smh-close-task-merge-tree`. Invoking it is your merge sign-off; I have
   not merged and will not.
2. **⛔ `chore/SCC-123-evidence-extract` is live and must absorb `main` before its close-out.** The
   ruleset is armed *now*, but the door carrying the pre-flight only reaches that lane when this one
   lands. Until then its `git push origin main` will be **refused by GitHub** with a required-check
   error its door does not explain. The failure is loud and safe — a rejected push, never a bad
   merge — and `git merge origin/main` in that lane fixes it. Landing this lane first removes the
   trap entirely.
3. **Every ship now waits ~90s on CI.** That is the price of this ticket, and it is real.
4. If CI is ever down and `main` must move:
   `gh api -X PUT repos/{owner}/{repo}/rulesets/20756052 -f enforcement=disabled`, and re-arm with
   `-f enforcement=active`. `run_all` stays red while it is disabled, on purpose.

## 9. Still open, deliberately

- **Project repos have no server-side half.** AGY and the rest still take GitHub-side merges with no
  gate. That is the same bug, in four other trackers, and needs a ticket per repo — it is not in this
  one's scope and is not silently assumed done. `git-policy.md` says so in writing.
- **The authorisation half remains local-only and unportable.** Not a gap to be closed later; §2 is
  why.
