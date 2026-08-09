# SCC-62 — Worktree isolation on concurrency · walkthrough

**Verdict: PASS @ `8fb1ff5`**
**Date:** 2026-08-09 · **Lane:** `chore/SCC-62-worktree-on-concurrency` (worktree)
**Gates:** `run_all` 10/10 exit 0 · `sop_currency` exit 0 (both run **bare** — a pipe returns `tail`'s code)

---

## What changed, and why it was backwards before

`worktree-per-story.md` decided who got an isolated tree by asking **what kind of work this is**. Story
lanes got one; ad-hoc work was *forbidden* one and sent to the shared checkout. The hazard is
**concurrency**, not work type — a chore lane beside a story lane collides exactly as hard, and it was
the one told to sit where the collisions happen.

The old wording also made the agent **self-classify** ("am I in a sudo story lane?") and ended with
*"unsure? you're not."* That sentence routed every ambiguous case into the shared checkout — the one
place it must not go. Removing the classification removes the failure mode.

**It went wrong twice in one afternoon (2026-08-09):** SCC-61 exists because a close-out preflight
resolved a *sibling lane's* branch and printed `VERDICT: clear to close out and merge`; SCC-58 then
opened onto a checkout still standing on SCC-61's branch with 11 dirty files.

## The two things that deliberately did NOT change

1. **Base branches are untouched.** A story still branches from its **epic branch**, never `main`;
   Task work still branches from `main`. Cutting a story from `main` would lose every sibling's work in
   the epic and break the landing sequence. The rule now states this as its own ⛔, because "everyone
   gets a tree" is exactly the change that invites someone to simplify the base too.
2. **Each close-out still prunes its own tree** — `/sudo-close-workingtree` for stories,
   `/close-task-merge-tree` Step 5 for Tasks.

## Step 5 is the unblocker, not a nicety

The old ban on chore worktrees was justified as preventing "an orphan tree that no close-out will ever
prune." That was never a principle — it was a workaround for a missing prune step. Step 5 now removes
the worktree **then** the branch, in that order (`-d` cannot delete a branch a worktree still holds).

## The finding the pre-dev audit caught

`worktree-per-story.md` is one of the **protocol four**, and its gate is **inlined** into each project's
`AGENTS.md` §8 — AGY at line 128, the skeleton at line 95, both saying *"one story, one worktree."*
Flipping the center rule alone would have **split the law**: two lanes in one repo obeying different
worktree rules, one isolating and one sitting in the shared checkout beside it, both editing
`sprint-status.yaml` — the #1 conflict surface. That became step **S1b**, tracked per repo because each
is a separate git repo:

| Repo | Ticket | Why separate |
|---|---|---|
| `Sudo_Hatter_Command` | SCC-62 | this change |
| `AGY_AVIATIONCHAT` | **AVCH-52** | armed `jira.conf` — an SCC key is **rejected** by its commit-msg hook |
| `sudo-project-skeleton` | SCC-62 (traceability only) | no armed `jira.conf` |

## The script, and the bug reading the old law prevented

`.agents/scripts/link-worktree-assets.py` links gitignored runtime assets into a fresh tree. Visibility
was never the problem — an agent can read `.env` by absolute path; **pytest, uvicorn, `next dev` and the
emulators resolve it relative to cwd**, so it is the *process* that breaks.

| Asset | Mac | PC | Why |
|---|---|---|---|
| `node_modules/`, `auth_keys/`, `.venv` | symlink | **junction** | directory; a junction needs no admin |
| `.env`, `.env.local` | symlink | **copy** | Windows file-symlinks need admin/Developer Mode |

**The bug I nearly shipped.** My first `--unlink` walked a fixed list of the assets it had linked.
`/sudo-close-workingtree` Step 3 already carries the hard-won rule against exactly that: *"never work
from a list of the junctions I created"* — lanes link more than the script knows about, and **Next.js /
Turbopack plants its own junctions** under `frontend/.next/` just by running the dev server (2026-07-27:
2 of 3 reparse points in a worktree were Next's). A missed link is not a cosmetic leak — the recursive
delete that follows walks **through** it and destroys the shared target. `--unlink` now **enumerates**
every reparse point, refuses to report success while any remain, and never descends through one.

**Verified, not assumed:** planted a rogue symlink outside the asset list → `--unlink` found and removed
it along with `.env`, reported `0 remaining`, and both targets (`docs/`, `.env`) survived intact.

## Known, expected, not a defect

The Antigravity workflow mirror of `close-task-merge-tree` stays a **thin launcher** — the body is ~13.9k
against a 12k cap. A grep against that mirror returns 0 and **looks like a failed sync**. It isn't.

---

## Task Checklist

- [x] S1 — trigger flipped to concurrency; base-branch table + ⛔ preserved; `⛔ Your tree is your world`; mechanical sibling check with its limits stated; frontmatter + G1 gate updated
- [x] S2 — `close-task-merge-tree` Step 5 prunes tree **then** branch, unlink-first
- [x] S3 — `link-worktree-assets.py`, enumerating unlink, destructive path verified safe
- [x] S4 — opencode mirror byte-identical; skills are thin launchers (no body); SOP page updated
- [x] AVCH-52 filed for AGY's inlined §8
- [ ] **S1b** — inlined §8 in AGY (AVCH-52) + skeleton, each in its own repo/commit

## Your Actions

None for the center repo. S1b lands in the two project repos immediately after this.
