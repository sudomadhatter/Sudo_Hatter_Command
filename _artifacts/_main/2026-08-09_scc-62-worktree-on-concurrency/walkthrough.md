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

---

## Follow-on sweep (2026-08-09, post-landing — `chore/SCC-62-stale-copies`)

The operator asked for a fresh-eyes pass before the AVCH-52 merge: silly errors here waste every future
lane's time. The pass found six, all fixed on this branch:

1. **Center `AGENTS.md` §8 still carried the full OLD gate** — "Ad-hoc non-story work never opens a
   worktree." S1b aligned AGY and the skeleton but missed the center's own front door — the repo where
   Task lanes actually run. Replaced with the aligned concurrency-triggered text.
2. **`worktree-per-story.md`'s own Hard stops contradicted its Trigger** — "NEVER open a worktree
   outside a sudo story lane" survived 170 lines below the section that abolished it. Rewritten.
3. **`.agents/rules/INDEX.md` row** still described the old trigger ("Ad-hoc non-story work: NO
   worktree"). Rewritten.
4. **`artifacts-always-first.md` hard stop** — same stale sentence, rewritten.
5. **`link-worktree-assets.py` scanned the repo root only.** AGY keeps every runtime asset one level
   down (`backend/.env`, `backend/.venv`, `frontend/node_modules`), so on the repo that motivated the
   script it would have linked only root `auth_keys/` and printed success. Now scans root + depth-1
   (deliberately not deeper — an unbounded walk would descend into the node_modules being linked).
   Re-verified end-to-end on a fake nested-layout repo: 4 nested assets linked, idempotent re-run,
   rogue link found by `--unlink`, `0 remaining`, every shared target intact, tree removed cleanly.
6. **Two docs cited `/sudo-close-workingtree` "Step 8"** for the unlink — that command's unlink step is
   **3a**; its steps end at 6. Fixed in the rule and the script docstring, and 3a now leads with the
   cross-platform script call (it was PowerShell-only — a Mac story close-out had no runnable
   procedure), keeping the PowerShell block as the by-hand PC path. `.opencode` mirror re-synced
   byte-identical; the Antigravity mirror stays a thin launcher (869 B).

**State at this commit:** S1b skeleton half landed (`42802c0`); AVCH-52 pushed (`b2d3237a`), its merge
runs at the AGY close-out immediately after this lands.

**Reported, deliberately NOT changed:** the skeleton's §8 is written around the retired `main_debug`
branch model (6 mentions, all predating SCC-62) — template-wide drift beyond this ticket's scope; needs
its own small task.

---

## Third leg (2026-08-09 — `chore/SCC-62-retire-main-debug`)

The operator rolled the deferred `main_debug` drift into this ticket rather than filing a new one
("it's something missed by another task"). Landed in the skeleton at `d463613`.

**The 2026-08-07 epic-branch migration retired `main_debug` everywhere except the template.** Every
project cut from the skeleton was therefore born teaching a dead branch model. Two of the seven
references were **live enforcement**, not prose — which is why this was worth more than a find-replace:

- **`.github/workflows/pr-check.yml` gated PRs to `[main, main_debug]`.** Under the epic model, stories
  merge into their epic branch, so gating only `main` leaves the `claude/*` → `epic/*` flow CI-ungated —
  *verbatim the P0-1 lesson the file's own header says it exists to prevent.* Now `[main, 'epic/**']`.
- **`.claude/settings.json` injects a GIT gate into every SessionStart** telling the agent to branch off
  `main_debug`. It now states the SCC-62 concurrency trigger.

Docs fixed alongside: `AGENTS.md` §8 (both gates), `README.md` (the setup step ran `git checkout -b
main_debug` verbatim, plus the branch-model paragraph), `docs/file_structure_rules/README.md`.

**Found while rewriting the enforcement sentence — the promised hook did not exist.** `AGENTS.md` §8
claimed a `PreToolUse` hook at `.claude/hooks/require-push-approval.py` and `settings.json` invoked it,
but the file was never copied into the template. Every new project got a hook pointing at a missing
script and **no push-approval gate at all**. Shipped from the canonical `.agents/hooks/` source (byte-
identical to the center's deployed copy), genericized to "the operator" since a template must not carry
a personal name. It is already the post-migration version — `PROTECTED = ("main",)`, fails open, only
ever asks. Behavior-tested: push to `main` → `ask`; push to `chore/*` → silent pass.

### ⛔ Pitfall — backticks in a double-quoted `git commit -m` are COMMAND SUBSTITUTION

Committing this work, the message quoted the README line being fixed: `` `git checkout -b main_debug` ``
inside a double-quoted `-m "..."`. Bash executed it. It created the branch, switched to it, and the
commit landed on **`main_debug`** — the exact branch this ticket deletes — with the backticked text
replaced by the command's empty stdout, silently corrupting the message.

It failed loudly enough to catch (`Switched to a new branch 'main_debug'` in the output) and nothing was
pushed, so recovery was local: `git checkout <chore-branch>` → `git merge --ff-only main_debug` →
`git commit --amend -F <message-file>` → `git branch -D main_debug`. Verified after: 0 branches named
`main_debug` local **and** remote in all three repos.

**This repo is unusually exposed to it** — it is a git-workflow toolkit, so commit messages routinely
quote git commands. **Write any commit message containing backticks to a file and use `-F`**, never
`-m "..."`. Memory: [[commit-message-backticks-execute]].
