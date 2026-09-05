---
IsArtifact: true
ArtifactMetadata:
  title: SCC-412 — the agent's own scratch branches stopped asking
  type: walkthrough
  date: 2026-09-05
---

# SCC-412 — the agent's own scratch branches stopped asking

**Lane:** `chore/SCC-412-worktree-agent-allow` · worktree `.claude/worktrees/SCC-412-worktree-agent-allow`
**Ticket:** [SCC-412](https://sudo-command.atlassian.net/browse/SCC-412) (Task)
**Base:** `origin/main` @ `4a9f013a`
**Plan:** [implementation_plan.md](implementation_plan.md)

---

## What this means for you, Mr. Hatter

Every time a review fans out lenses, the harness cuts a throwaway git branch per subagent —
`worktree-agent-<hash>` — and the close-out deletes it again. You were being asked to approve each
of those deletes: **6 stops** across the 20 newest sessions, spent authorising the agent to clean up
after itself. One narrow allow prefix ends that, and it cannot reach anything you care about.

**What it is not.** It is not a widening of `git branch`. The prefix is
`git branch -d worktree-agent-`, and a branch has to be named `worktree-agent-…` to ride it. Proven
below against `main`, `chore/`, `claude/`, `epic/`, a bare name, and two near-miss spellings.

⭐ **You asked for read forms, and the honest answer was that they would buy you nothing.** Claude
already carries `git branch --list`, `-a` and `--show-current`. When I pulled the seven real stops
behind the report's 10m51s, not one was a read — they were `--unset-upstream`, the
`worktree-agent-` deletes, and a `git reset --keep`. So the pick moved to where the cost actually
was, on your word.

---

## What shipped

Three rendered rows, one existing family (`allow-git-branch`), no new family:

| platform | row | why this spelling |
|---|---|---|
| Zoo | `git branch -d worktree-agent-` | literal prefix, longer than the `git branch -d` deny, so it wins by length exactly as `chore/` does |
| Zoo | `git branch -d "worktree-agent-` | the quoted twin, matching the six that already exist for chore/claude/epic |
| Claude | `Bash(git branch -d worktree-agent-*)` | **bare star** — the prefix ends in `-`, and Claude reads `Bash(X:*)` as `Bash(X *)` (battery A2b) |

Antigravity gets nothing: the family is `only: ["zoo", "claude"]` and this lane does not widen it.
`.agents/permissions/antigravity.json` is byte-unchanged, which is acceptance A's other half.

---

## Evidence

### Acceptance

| # | Statement | Result |
|---|---|---|
| A | The three rows render, and only those; Antigravity untouched | ✅ diff below |
| B | `permission_render.py --check` in sync, all three platforms | ✅ `in sync (zoo, claude, antigravity)` |
| C | The prefix reaches no protected branch on either platform | ✅ matcher table below |
| D | `git branch -r` excluded on evidence, not caution | ✅ measured delete below |
| E | No other allow row added, widened or re-spelled | ✅ one family's arrays, +3 rows |
| F | `run_all.py` green at the tip | ✅ 76/76 |

### Acceptance C — the matchers, run against every protected target

```
command                                        zoo      claude    expectation
git branch -d worktree-agent-afd9e37c41e9aa8   allow    allow     THE PICK - must be allow
git branch -d main                             deny     ask       protected - must NOT be allow
git branch -D main                             deny     ask       protected - must NOT be allow
git branch -d worktree-agent                   deny     ask       no trailing hyphen - must NOT be allow
git branch -d worktreeagent-x                  deny     ask       near-miss spelling - must NOT be allow
git branch -D worktree-agent-x                 allow    ask       capital D on the picked prefix
git branch -d epic/AVCH-100-x                  allow    ask       epic - pre-existing re-allow
git branch -d chore/SCC-1-x                    allow    allow     chore - pre-existing re-allow
```

Both near-misses fall through to the `git branch -d` deny, which is the row working. The two rows
that matter — `main` in either spelling — stay denied on Zoo and asking on Claude.

⭐ **`git branch -D worktree-agent-x` reads allow on Zoo, and that is by design, not a leak.** Zoo
lowercases both sides, so `-D` ≡ `-d` for every re-allow in this family — the guide already records
that for `epic/`, where the epic-close door's forced delete rides the same row deliberately. A
forced delete of a throwaway subagent branch is the intended behaviour; a forced delete of anything
else is unreachable through this prefix.

### Acceptance D — why `git branch -r` was refused

It was the obvious second candidate and it does not survive a test. In a throwaway repo:

```
=== git branch --list -D victim ===      usage error, branch survives
=== git branch --merged -D victim ===    fatal: malformed object name -D, branch survives
=== git branch -aD victim ===            fatal: cannot use -a with -d, branch survives
=== git branch -rd origin/keepme ===     Deleted remote-tracking branch origin/keepme (was c98bd87).
```

`--list`, `-a` and `--merged` all refuse to combine with a delete. `-r` does not. Excluded on that
measurement rather than on caution.

### Acceptance A and E — the whole diff

```
families.json   +3 rows into allow-git-branch, + the family's `why`
.vscode/settings.json      + "git branch -d worktree-agent-"
                           + "git branch -d \"worktree-agent-"
.claude/settings.json      + "Bash(git branch -d worktree-agent-*)"
antigravity.json           (unchanged)
```

### Acceptance F — the gates

```
permission_render: in sync (zoo, claude, antigravity)
76/76 files passed
workflow_lint --toolkit-only: 0 error(s), 0 warning(s), 8 info
```

---

## Two things carried that the pick did not ask for, declared not hidden

**`docs/migrations/terminal-permissions-guide.md`** — the tracked count line moves 125 → 127 allow,
and the "Lane/epic prune re-allows" family row gains the new entries with their reasoning.
`test_zoo_permissions.py::test_guide_currency` **requires** this: it is a live assertion that the
guide's count matches the rendered file, and it went red the moment the Zoo rows landed.

**`docs/.maps-state.json`** — the maps baseline re-anchored at `4a9f013a`. Housekeeping from earlier
in the session that silenced a stale-journal nag; `check_maps.py --strict` was already clean, so the
anchor was simply behind. Unrelated to the pick and named here rather than slipped in.

---

## Why this took a lane, and the door defect behind it

`/smh-llm-approvals` Step 4 carries an exemption that skips the plan, the audit and the review for
harvest work — on the condition that the change set touches **exactly four** paths. This one touches
six, and the door is explicit: *"A fifth path … voids the exemption and the work takes the full
lane."*

⛔ **But the two extra paths are not avoidable, and that is a defect in the door.** Step 3's gate
*requires* the guide edit that Step 4's guard *forbids*, because any Zoo allow row moves the count
line. So the fast path can never be used for a harvest that adds a Zoo row — the exemption is only
reachable for a Claude-only or Antigravity-only pick. Filed on
[SCC-411](https://sudo-command.atlassian.net/browse/SCC-411) with the remedy: either add the guide
to the permitted set, or move the count line to a generated file the render writes.

---

## One pre-existing hole found while testing, filed not fixed

`git branch -rd origin/main` reads **allow** on Zoo. It deletes a remote-tracking ref, and Zoo
auto-approves it through the broad `git ` prefix because the deny row is `git branch -D` — which
lowercases to `git branch -d` and never matches `git branch -rd`.

**Measured on `origin/main` @ `4a9f013a` with none of this lane present: also `allow`.** It predates
this work and lives in a different family, so closing it here would be undeclared scope creep of
exactly the kind the change-set reconciliation exists to catch. Low severity — it cannot touch a
real branch or the remote, and `git fetch` restores it. On
[SCC-411](https://sudo-command.atlassian.net/browse/SCC-411) with the flag orders the existing deny
cannot reach, and the note that this is the getopt-clustering residual Zoo's grammar cannot express.

---

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [ ] Nothing else. The Zoo rows go live on your next `zoo_permissions_apply.py --apply`; until then
      the two deletes still ask, which costs a click and nothing else.
