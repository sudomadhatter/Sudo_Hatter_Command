# Walkthrough — SCC-449: the close-out deletes the branch it merged

**Ticket:** SCC-449 (Task)
**Branch:** `chore/SCC-449-closeout-branch-delete` — cut from `origin/main` at `7d71c9a8`
**Worktree:** `.claude/worktrees/scc-449-closeout-branch-delete`
**Commits:** `9f2b2838` (one commit)
**Plan:** [implementation_plan.md](implementation_plan.md) — approved 2026-09-11, *"Approved fix it"*
**Status:** built and certified (`gates/suite.json` — 91/91 @ `9f2b2838`, clean tree), pushed. Not landed.
**Date:** 2026-09-11

---

## Task Checklist

- [x] **Found the real cause, with evidence.** `git branch -d` refused a branch that was fully merged. It checks merged-into-**upstream** when an upstream exists and merged-into-**HEAD** when one does not; lanes here push without `-u` because the sandbox cannot write the lobby's `.git/config`, so there was no upstream and the HEAD it used was the shared lobby on a `main` 20 commits stale.
- [x] **Named what made it permanent**, which is the actual subject of the lane.
  - The door asserted a false diagnosis — *"a refusal means the merge did not land"* — sending every agent to look for a failed merge that had in fact landed.
  - Step 6's report template offered *(or why it was retained)*, so the verify step accepted its own failure and could never go red.
  - `/cicd-prune-worktree` has documented the correct mechanism since 2026-08-01 and it never crossed over. A half-port, in the door that closes SCC-447's own lane.
- [x] **Measured the recurrence before touching anything:** 7 local and 10 remote lane branches left behind, **5 of the 7 local ones with no upstream at all**. 14 were fully merged (each proven with `rev-list` first) and were removed; 2 hold genuine unmerged work and were kept — `chore/SCC-431-zoo-remote` and `claude/teaching-edition`.
- [x] **Fixed the door.** Remote deleted first, with the reason; the mechanism sentence carried verbatim from the sibling door; the false diagnosis replaced by the real cause and a ladder that keeps the safety check intact instead of bypassing it. `-D` stays banned and the shared lobby is never pulled.
- [x] **Removed the escape.** Both branch lists must come back empty. A branch proven merged and still present is a close-out that did not finish. The one legal retention is a branch that did not land, which has its own proof.
- [x] **Deleted the note that licensed it**, after porting its two pieces of real knowledge into the door: the upstream-vs-HEAD mechanism, and a second measured refusal (SCC-430, 2026-09-07) where `push origin --delete` is blocked by stale generated maps.
  - The note justified retaining by citing the door's escape clause while the door offered the escape. Each authorised the other, and one of them lived outside the repo where no test could reach it. This is the general case **SCC-448** is parked on; this lane fixes only the close-out instance.
- [x] **Fixed the same defect in the test machinery.** `check_rows`'s counter-example was a plain literal while its pattern was wrap-tolerant, so re-flowing a paragraph made the counter-example read as "not present" and the check reported *itself* vacuous. SCC-447 learned this for the pattern side and left the mutation side literal. Both sides are wrap-tolerant now.
- [ ] **Land via PR** — the close-out door opens it; the merge is the operator's click.

---

## Evidence

### Acceptance → evidence

| Row | Statement | Proved by |
|---|---|---|
| **A** | Step 5 deletes the remote first and says why the order is mechanical | `test_closeout_branch_delete.py` block A, counter-example rejected |
| **B** | The false diagnosis is gone; the real cause is named and the ladder given (`rev-list` proof → `--set-upstream-to=origin/main` → `-d`); `-D` and pulling the lobby stay banned; the stale-maps refusal on the remote delete is named with its remedy | block B |
| **C** | Step 6's blanket escape is gone; both retired sentences are banned outright | block C, both bans seen RED on the unfixed door |
| **D** | Both doors carry the mechanism in the **same** sentence, so the next half-port fails | block D, cross-door equality |
| **E** | The `.opencode/` mirror is byte-identical | block E |

### The runs

```
python3 .agents/scripts/tests/test_closeout_branch_delete.py
RED  (unfixed door):  7/41 passed  — 34 failures, incl. both bans firing on the live sentences
GREEN (fixed door):  44/44 passed
```

```
python3 .agents/scripts/gate_receipt.py run --task SCC-449 --gate suite --root _artifacts/_main/2026-09-11_scc-449-closeout-branch-delete --cwd . -- python3 .agents/scripts/tests/run_all.py
[PASS] suite exit=0 30.3s @ 9f2b2838
91/91 files passed
```

`git rev-parse HEAD` → `9f2b2838aba14c1b8b41be12b7df163d56786856`

Static checks: `workflow_lint.py --toolkit-only` 0 errors, 0 warnings, 8 info · `check_links.py --base origin/main` clean · `check_maps.py` via `test_check_maps` 37/37 · SOP staged in the same commit as the door (the currency gate).

### The cleanup, as performed

Fourteen merged branches removed, each proven with `git rev-list --count origin/main..<branch>` returning `0` before deletion. Six local: `SCC-186-live-testing-bug-list`, `SCC-430-autopilot-claude`, `SCC-437-llm-approvals`, `SCC-439-retire-bmad-token-gate`, `SCC-440-closeout-tick`, `SCC-440-tea-docs-ci-gate`. Eight remote: those six, plus `SCC-186-standing-push`, `SCC-435-r3f-drei-suite`, `SCC-436-r3f-repo-link`. Retained, correctly: `chore/SCC-431-zoo-remote` (2 commits off `main`) and `claude/teaching-edition` (37 commits off `main`).

Four asset symlinks were released before every worktree removal, two of them pointing at live credential files (`.env`, and the AviationChat and migrations `auth_keys`). All targets verified intact afterwards.

---

## Suite Ledger

| Scope | Command | Result | Why this run |
|---|---|---|---|
| the new pins, RED | `test_closeout_branch_delete.py` | 7/41 | proof the checks can fail, on the unfixed door |
| the new pins, GREEN | `test_closeout_branch_delete.py` | 44/44 | the fix |
| maps | `test_check_maps.py` | 36/37 → 37/37 | the lane's depth-3 INDEX row |
| lint | `workflow_lint.py --toolkit-only` | 0 errors | the door and SOP are usage surfaces |
| links | `check_links.py --base origin/main` | clean | markdown in the diff |
| **certification** | `gate_receipt.py run --task SCC-449 --gate suite … -- run_all.py` | **PASS 91/91** @ `9f2b2838`, clean tree | the certifying run; `gates/suite.json` |

---

## Your Actions

Landed: `chore/SCC-449-closeout-branch-delete` is pushed to origin at `9f2b2838`. Nothing has reached `main`; the PR is the close-out door's.

- [ ] **The merge itself** — lands via this branch's PR
