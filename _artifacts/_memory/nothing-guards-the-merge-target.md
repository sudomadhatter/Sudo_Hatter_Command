---
name: nothing-guards-the-merge-target
description: "Every git guard protects the branch you merge FROM; nothing checks the branch you merge ONTO. A bare `git merge` after a `cd` landed a production merge commit on a sibling lane's branch and reported success — pin every call with cd <abs> && git in ONE line and assert rev-parse before merging (the -C spelling is auto-denied by Zoo since SCC-351)."
metadata:
  node_type: memory
  type: feedback
---

**A `cd` in one tool call does not hold for the next one.** On 2026-08-11, during a seven-lane
landing, `cd <worktree> && git checkout main` ran in one step and a **bare `git merge <lane>`** ran
in a later one. The working directory had reset to the shared checkout, which was standing on
`chore/SCC-89-…`. The merge put a **production merge commit on that sibling lane's branch** and
reported success.

**Why nothing caught it — this is the part worth remembering.** Every existing mitigation guards the
**source**: `--expect-key`, the preflight header line, pinning `$REPO`, `worktree-per-story`'s *"cwd
is not intent"* (which is written about which tree you *review*). **Nothing looks at the
destination.** And the failure is invisible by construction — the merge output, the changed-file
list, and the commit message all read correctly, because you wrote `-> main` yourself. It surfaced
only by running `git rev-parse --abbrev-ref HEAD` afterwards and not recognising the answer.

**Why:** git resolves `merge` against whatever HEAD happens to be, and a merge onto the wrong branch
is a completely legal operation. There is no gate, hook, or preflight anywhere in this toolkit that
validates the target — so the only thing standing between you and it is whether you looked.

**How to apply:**
- Pin **every** `git` invocation in the SAME compound line — `cd "$REPO" && git <verb> …` — never a
  bare `git` that trusts an earlier call's `cd`. (Until SCC-351 this bullet said `git -C "$REPO"`;
  Zoo Code auto-denies that spelling because its per-piece prefix matcher can't see verbs through
  `-C`, so the doors and this idiom moved to `cd … && git …`, which both permission layers match.)
- **Assert the target immediately before merging**, so it stops you instead of informing you:
  `test "$(cd "$REPO" && git rev-parse --abbrev-ref HEAD)" = "main" || { echo "NOT ON main — STOP"; exit 1; }`
- **Recovery — never reset, never force.** The merge commit is usually correct in every way except
  which pointer moved. Verify its tree is clean of the wrong branch
  (`git diff --name-only <main-tip> <sha>`), confirm its first parent is `main`'s tip
  (`git log -1 --format='%p' <sha>`), then `git merge --ff-only <sha>` from the tree holding `main`.
  The sibling branch keeps its uncommitted work untouched — that is what makes this recoverable.
- Bound into `.agents/rules/git-policy.md` §Safe-commit mechanics and into
  `/smh-merge-multiple-workingtrees` Step 0 and Step 4d.

Related: [[preflight-resolves-repo-from-cwd]] (same disease, aimed at the *report* rather than the
merge — the preflight cleared another lane's branch) · [[one-shot-permission-persists-in-context]]
(the other way a merge goes wrong: right branch, unauthorised) ·
[[closeout-target-is-a-machine-contract]] · [[commit-and-push-are-one-action]]
