---
IsArtifact: true
ArtifactMetadata:
  title: SCC-82 walkthrough - workflow_lint to zero, and the check that could never be satisfied
  type: walkthrough
  date: 2026-08-11
---

# SCC-82 — Walkthrough: two warnings, two completely different diseases

**Date:** 2026-08-11 · **Repo:** Sudo_Hatter_Command (lobby) · **Lane:** Task (LOCAL)
**Branch:** `chore/SCC-82-workflow-lint-zero-warnings`

> **⛔ NOT merged.** Pushed, gated and handed back for the operator to invoke
> `/smh-close-task-merge-tree`. One invocation authorises one merge; SCC-80's does not carry.

## Why this was worth a ticket

*"Look at and fix the 2 lint warnings, I don't want skeletons."*

They had stood on `main` for weeks, and **every close-out report had to carry the phrase "2
pre-existing warnings" as an excuse.** That is the actual cost, and it is not cosmetic: a gate whose
clean state is non-zero cannot tell you anything about your change, because the reader must first
hold a list of accepted noise in their head to interpret the output. The next real warning arrives
into a report that already says warnings are normal.

`workflow_lint.py --toolkit-only` now exits **0**, and a warning from here on is **yours**.

## W1 — a real omission, in the worst possible command

`cicd-merge-epic-workingtrees.md` is git-mutating (`git merge`, `git push origin HEAD:epic/…`) and
its **Rules in force** block cited only `worktree-per-story.md`. Every peer that touches git cites
`git-policy.md` — the rule carrying *explicit paths only, never `git add -A`*, *never force-push*,
and *every branch and commit carries the repo's Jira key*.

Of all the commands to be missing that pointer, this is the one that **merges every live story lane
and pushes to a shared epic branch.** It is precisely where a single `git add -A` sweeps a sibling
lane's in-flight work into your commit. Pointer added, with that consequence stated rather than
left implied. The linter's own docstring says the invariant is *"the pointer exists"*, never *"the
prose is deleted"* — so the inline restatements are untouched. Propagated to both its doors
(antigravity workflow + opencode) by `sync-agents -NoGlobals`; the dry-run showed exactly those two
files and **zero purges**.

## ⭐ W2 — the check was right to fire, and there was nothing to port

I diffed the pair, which is what the warning asks for. The one commit that made the primary newer —
`3eea4d0`, SCC-63 — restored the historic artifact filename `sudo-code-review-<story>.md` after the
rename sweep had over-renamed it to a name that **cannot exist on disk**. The twin does not contain
that line and does not need it: it is a headless single-pass reviewer that writes its verdict into
`walkthrough.md`, forbids a standalone file outright, and never globs for a pre-2026-08-02 verdict.
A contract-token diff of the whole pair confirmed no missing substantive element.

**So the pair was correctly synced and the check warned anyway — forever.** `check_ap_twins` was a
pure timestamp comparison (`pr_ts > ap_ts`) with **no way to record "diffed, nothing to port."** The
only way to clear it was to *touch the twin*, which resets the clock while asserting nothing. That
is a false claim encoded in a timestamp, and it is exactly the skeleton the ticket was about.

**Fix: give the twin something falsifiable to say.** `ap_reconciled: <primary-sha>` in its
frontmatter — *I read the primary at this sha and there is nothing to port.*

| State | Behaviour |
|---|---|
| stamp present, current | silent — and the twin's own commit date is now irrelevant |
| stamp present, **stale** | **WARN, even when the twin is the newer file** |
| no stamp at all | the original timestamp signal, unchanged |

The middle row is the whole point. The old check called "touch the twin without diffing" clean; the
new one names it. **The check gained teeth rather than losing them** — silence now costs you a
written statement of which version you read.

## The RED caught two bugs in my own fixtures

Both would have produced a green that proved nothing.

1. **Git timestamps have 1-second resolution.** Fixture commits made back-to-back land on the same
   second, so `pr_ts > ap_ts` was false: case B *did not fire*, and case C then "passed" while the
   feature was unbuilt — silent for a reason that had nothing to do with the stamp. Commit dates are
   now pinned via `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`, one day apart.
2. **`thing` is a substring of `thing-AP`.** The case asserting *"a twin that stopped naming its
   primary still warns"* used a twin that still said its own name, so `primary.stem in text` was
   trivially true and the case could never fail.

After the fix, case C is asserted with the twin **deliberately uncommitted** — committing it would
make the twin newer and let the timestamp path silence it, which is how the first draft passed
vacuously. And case D is built so the **old** check would call it clean: primary moves, then the
twin is committed *after* it still carrying the old sha. The setup itself is asserted
(`twin=1780432000 primary=1780345600`) so the case can never quietly stop testing what it claims.

## Gates

| Gate | Result |
|---|---|
| `tests/run_all.py` | **12/12 files, exit 0** — 10 new SCC-82 cases |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings — exit 0** (was 0/2) |
| `sop_currency.py` | **exit 0** — the SOP moved in the same commit, no `[sop-ok]` |
| `sync-agents -NoGlobals` | 2 doors updated, **0 purges** |

## Also fixed in passing

`workflows_testing_SOP.md` still described the SOP folder as a **13-doc manifest**. SCC-80 took it
to 11 and did not update this row — the same class of drift SCC-74 built that test to prevent,
sitting in the page that documents the test. Corrected.

## ⚠ Open

1. **`.opencode/node_modules`** shows as untracked in this tree. It is the known `.gitignore`
   symlink gap — `**/node_modules/` with a trailing slash matches directories, and the asset linker
   creates a **symlink**. `chore/SCC-77-main-write-gate` already carries the fix, so it is
   deliberately not fixed here and deliberately not committed.
2. **The other two twins** (`cicd-dev-story-tests-AP`, `cicd-self-audit-AP`) are unstamped **on
   purpose** — they were never stale, and stamping them to be tidy would be the same hollow claim in
   the other direction. A test asserts only the diffed twin carries a stamp.
