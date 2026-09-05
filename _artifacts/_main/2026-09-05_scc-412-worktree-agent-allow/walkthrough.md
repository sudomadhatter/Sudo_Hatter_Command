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
proved it would have bought you effectively nothing** — one interruption worth zero seconds. It is reverted. What the lane actually produced is four
measured defects in the permission fence, all of which predate it.

**Why it could not work — and the count was inflated twice over.** The review measured that the
"6 stops" are **3 distinct calls, each recorded twice**: a context compaction replays the record, so
the same `tool_use` appears at two line offsets with an identical id, and `approval_stops.py` does
not dedupe. Two of the three are escalation stops — the delete is always paired with
`git worktree remove`, which needs the sandbox off — and one is a classifier refusal. So the row
would have removed **one** interruption worth **0.0 seconds**. The double-counting is itself a
defect in the door, now filed on SCC-411: it inflates every number that report prints. The
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

**Added at the operator's call** — two rows in `test_permission_parity.py`'s `DESTRUCTIVE` list:

```python
"git branch -d worktree-agent-x main", "git branch -D worktree-agent-x main",
```

They are the **tripwire for the escape that killed this lane**, and they are only addable *because*
the row was reverted: with the prefix present they read `allow` and A2 goes red; without it they
read `deny` on Zoo and Antigravity and `ask` on Claude, so the battery is green at 99/99. Re-add
that allow prefix in any future lane and this row fails by name.

⛔ **The `chore/`, `claude/` and `epic/` twins are deliberately absent.** They read `allow` on all
three platforms **today**, on a pre-existing hole that no permission row on either grammar can close
— it needs a `PreToolUse` hook that parses the branch list. Adding them here would red the battery
over a defect this file cannot fix. That is SCC-411's item, with the hook named.

**Kept** — `docs/.maps-state.json`, the maps baseline re-anchored at `4a9f013a`. Housekeeping from
earlier in the session; `check_maps.py --depth3-only --strict` was already clean and the anchor was
simply behind. (The bare `--strict` is not a runnable spelling; the script refuses it.)

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

---

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [ ] Nothing. The fence is exactly as you left it, and your six stops still stop — they always
      would have. If you want them gone, that is a `/sandbox` conversation, not a fence one.

---

## Code Review (2026-09-05)

Verdict: CONCERNS @ f7d2b54382ab8bbf66d90396156185e938c2fbc3
Suite evidence measured on f7d2b54382ab8bbf66d90396156185e938c2fbc3 — run_all.py 76/76, permission_render --check in sync.

review-runtime: fan-out

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- acceptance-auditor · ok
- literal-correctness-hunter · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind-hunter=12/5/0 · edge-case-hunter=8/0/0 · acceptance-auditor=5/0/0 · test-adequacy-auditor=6/0/0 · literal-correctness-hunter=11/0/0
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — reconciled clean after the back-out removed the four voided EDIT bullets

**Why CONCERNS and not PASS.** All five lenses reported, so the floor is not degradation. It is
that the review falsified the lane's own acceptance row C *and* its central measurement, and six
further factual errors in this record had to be corrected from lens evidence rather than caught
before it was written. What ships is sound — a revert, a tripwire and the record — but a review that
had to correct this much of its own subject does not read PASS.

**Why not FAIL.** The blocking findings were all against the permission row, and that row is
reverted. Nothing they describe is present in the diff being merged.

### Findings

| # | file:line | severity | failure scenario | disposition |
|---|---|---|---|---|
| 1 | `families.json:1201` (reverted) | blocking | `git branch -d worktree-agent-x main` reads allow on Zoo and Claude; real git deletes both branches. Acceptance C asserted the opposite. | **applied @ f7d2b54382ab8bbf66d90396156185e938c2fbc3** — row reverted; the pre-existing class filed on SCC-411 with a PreToolUse-hook remedy |
| 2 | `approval_stops.py:310` | blocking | All 6 stops the row was bought for are `escalation` kind; `elif escalated:` precedes `elif not covered(...)`, so no allow row reaches them. The lane's entire justification. | **applied @ f7d2b54382ab8bbf66d90396156185e938c2fbc3** — row reverted, measurement written into the record |
| 3 | `test_zoo_permissions.py:272` | important | `test_reallow_beats_its_deny` enumerates 14 pairs by hand; the new rows were not added, so the length invariant that made the row work was unasserted. | **dismissed** — moot, the rows no longer exist |
| 4 | `.vscode/settings.json` (pre-existing) | important | `git branch --delete main` and `git branch -f -d main` read allow on Zoo and Antigravity; the deny spells only `git branch -D`. | **deferred — SCC-411**, with the deny rows named; different family, not this lane's subject |
| 5 | `permission_matchers.py` `zoo_pieces` (pre-existing) | important | Backtick command substitution is never split into its own piece, so `` git branch -d chore/x `echo main` `` reads allow on all three. | **deferred — SCC-411**, remedy names the existing `$(…)` pass to extend |
| 5b | `test_zoo_permissions.py:142,274` (pre-existing) | important | **No assertion bounds ANY re-allow prefix in this family.** Measured: widening `worktree-agent-` all the way to the single letter `w` — so `git branch -d wip-x` auto-approves — leaves the suite at **76/76 green**. Only an empty prefix is caught, and only because `git branch -d main` happens to sit in two DESTRUCTIVE batteries. The same hole guards `chore/`, `claude/` and `epic/`. | **deferred — SCC-411**, with the three near-miss BATTERY rows and the `test_reallow_beats_its_deny` pair that kill the mutant |
| 6 | `implementation_plan.md:54-57` | low | Four Declared Change Set bullets lacked the `→ row` separator, so `docs/.maps-state.json` reconciled as `undeclared`. | **applied @ f7d2b54382ab8bbf66d90396156185e938c2fbc3** — separators added; reconciliation now clean |
| 7 | `walkthrough.md` (original) | low | `- [x] The merge itself` was ticked in a record shipping with an unmerged branch. | **dismissed** — that row is the door's own ledger line, checked against ancestry rather than its tick (SCC-175) |

One positive worth keeping: `test_settings_allowlist.py` A2b **does** guard the Claude bare-star
spelling — respelling the row as `Bash(...worktree-agent-:*)` turns it red naming the dead rule,
so that half of the lane's reasoning was covered by an existing assertion.

Five further lens findings were relevance-killed as restatements of 1 and 2 (mixed-case branch
names, `-D` folding, the `-rd` spelling, Antigravity denying the intended command, and the
"Lane/epic prune re-allows" heading being wrong for a non-lane branch) — all moot once the row was
reverted.

### Step 0.7 — re-derivation

- The landing ref moved nothing under this diff: `merge-base` == `origin/main` == `4a9f013a`, 0 files landed while the lane was built, and every path the diff references still resolves.
- True overlap is EMPTY and `git merge-tree --write-tree --messages HEAD origin/main` returned a bare tree sha with no conflict messages.
- Sibling lanes: the shared `main` checkout only — no landing-order dependency, and nothing else holds a branch this lane touches.
