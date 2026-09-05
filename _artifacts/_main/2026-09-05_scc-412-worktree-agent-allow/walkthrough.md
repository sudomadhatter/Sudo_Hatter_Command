---
IsArtifact: true
ArtifactMetadata:
  title: SCC-412 — the allow row that could not have worked
  type: walkthrough
  date: 2026-09-05
---

# SCC-412 — the allow row that could not have worked

**Lane:** `chore/SCC-412-worktree-agent-allow` · **Outcome: BACKED OUT.** No permission row ships.
**Ticket:** [SCC-412](https://sudo-command.atlassian.net/browse/SCC-412) (Task)
**Base:** `origin/main` @ `4a9f013a`
**Plan:** [implementation_plan.md](implementation_plan.md)

---

## What this means for you, Mr. Hatter

You approved one narrow allow row so the agent could delete its own throwaway
`worktree-agent-<hash>` branches without asking you. **It was built, it was green, and the review
proved it would have bought you nothing.** It is reverted. What the lane actually produced is four
measured defects in the permission fence, all of which predate it.

**Why it could not work.** Every one of those six stops was run with the sandbox off, because the
delete is always paired with `git worktree remove`, and worktree removal needs escalation. The
approvals reader classifies an escalated call as `escalation` *before* it ever asks about coverage:

```python
elif escalated:
    stops.append((t1 - t0, "escalation", cmd))
elif not covered(cmd, prefixes):
    stops.append((t1 - t0, "waited", cmd))
```

An allow row cannot touch that branch of the tree. The repo already knew this — the scar test
`test_L_an_ALLOWED_command_run_with_the_sandbox_off_is_still_a_stop` exists to say so — and the
door's own report prints escalation stops under a separate heading reading *"a second, independent
gate"*. I read the six out of the wrong bucket. Measured at the tip: of 19 calls in the window
containing that command, **6 escalated and 0 coverage-fixable**; the other 13 were this session's
own analysis commands that merely contain the string.

**The real remedy for those stops is the sandbox, not the fence** — `/sandbox`, or leaving the
worktree teardown escalated and accepting the prompt. A permission row was never the instrument.

⛔ **And the safety claim was wrong too, which is the more serious half.** The record asserted three
times that the prefix "cannot reach anything you care about." Two independent lenses falsified it
and real git confirmed it:

```
$ git branch -d worktree-agent-x main
Deleted branch worktree-agent-x (was 9dd7d8f).
Deleted branch main (was 9dd7d8f).
```

`git branch -d` takes a **list**. The allow prefix is satisfied by the first argument and every
argument after it rides free, with no shell metacharacter for a splitter to catch. I had tested
eight single-argument commands and generalised from the shape of the `chore/` row instead of
testing a two-argument one.

---

## What the lane leaves behind

**Reverted** — `families.json`, `.claude/settings.json`, `.vscode/settings.json` and
`terminal-permissions-guide.md` are byte-identical to `origin/main`. `permission_render --check`
prints *in sync*. Zoo stays at 125 allow / 115 deny; nothing was widened anywhere.

**Kept** — `docs/.maps-state.json`, the maps baseline re-anchored at `4a9f013a`. Housekeeping from
earlier in the session; `check_maps.py --strict` was already clean and the anchor was simply behind.

**Filed on [SCC-411](https://sudo-command.atlassian.net/browse/SCC-411)** — five rows, each with its
remedy. Every one is pre-existing and none was introduced by this lane:

| # | Defect | Measured |
|---|---|---|
| 1 | `git branch -d <allowed> <victim>` deletes both; the prefix only guards the first argument | `allow` on zoo, claude **and** antigravity for `git branch -d chore/SCC-1-x main`; real git exits 0 deleting both |
| 2 | `git branch --delete main` — the long form is in neither deny grammar | `allow` on zoo and antigravity |
| 3 | `git branch -f -d main` — the deny expects `-d` in first flag position | `allow` on zoo and antigravity |
| 4 | `git branch -rd origin/<ref>` deletes a remote-tracking ref | `allow` on zoo; reproduced end to end |
| 5 | `zoo_pieces()` splits `$(…)` but not backticks | `` git branch -d chore/x `echo main` `` → `allow` on all three |

Rows 2, 3 and 4 are expressible as deny rows and the remedy names them. **Row 1 is not** — neither
Zoo's literal-prefix grammar nor Antigravity's per-token regex can say *"exactly one argument"*, so
closing it needs a `PreToolUse` hook that parses the branch list. That is the one worth your
attention, and it is why this lane's own row would have been a new door into an old hole.

Also filed: the `/smh-llm-approvals` fast path is **unreachable for any Zoo-side harvest**, because
Step 3's gate requires a guide count-line edit that Step 4's four-path scope guard forbids. That
contradiction is why this ran as a full lane at all.

---

## Evidence

| # | Original acceptance row | Result |
|---|---|---|
| A | Three rows render, and only those | **void** — reverted, nothing renders |
| B | `--check` in sync | ✅ `in sync (zoo, claude, antigravity)` after the revert |
| C | The prefix reaches no protected branch | ❌ **FALSIFIED** — `git branch -d worktree-agent-x main` is allow/allow |
| D | `git branch -r` excluded on evidence | ✅ still true, and now filed as SCC-411 row 4 |
| E | No other allow row added, widened or re-spelled | ✅ and now stronger: **no** allow row at all |
| F | `run_all.py` green at the tip | ✅ 76/76 |

Row C is the one that mattered and it did not hold. Under the house rule that an acceptance row
without a passing assertion is not satisfied, the lane fails its own contract — which is the correct
outcome, and the reason the row is not shipping.

### Review

review-runtime: fan-out

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- acceptance-auditor · ok
- literal-correctness-hunter · dead — still running when the operator's back-out decision made its
  verdict moot; no findings collected
- test-adequacy-auditor · dead — same
lenses_counted:  3/5
lenses_na:       none

The two dead lenses are recorded as dead rather than dropped. Three lenses independently found the
multi-argument escape and the missing test coverage, and the acceptance auditor found the escalation
misclassification that ended the lane — the finding no gate in this repo would have caught.

---

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [ ] Nothing. The fence is exactly as you left it, and your six stops still stop — they always
      would have. If you want them gone, that is a `/sandbox` conversation, not a fence one.
