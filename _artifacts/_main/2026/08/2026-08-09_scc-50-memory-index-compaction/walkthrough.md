# SCC-50 — Memory index compaction

**Branch:** `chore/SCC-50-memory-index-compaction` · **Lane:** LOCAL (lobby has no deployable surface)

## What this changed

Three files:

| File | Change |
|---|---|
| `_artifacts/_memory/MEMORY.md` | The index rewritten — related memories share a line instead of each taking one, so every file stays linked while the row count drops. |
| `_artifacts/_memory/agy-epic-19-deferred-pin-cascade.md` | Records the Epic 19 reopen; the memory previously read as permanently deferred. |
| `_artifacts/_memory/sprint-dependency-map-recommends-stale-work.md` | Hook tightened. |

`MEMORY.md` loads into context on **every** session, before any rule file. Individual memories are
read only when a row looks relevant. That asymmetry is the whole reason the index has a size
standard and the 139 memory files do not — the index is a standing tax on every conversation.

## The result, and the honest number

**The byte target was not met, and it is not reachable by compaction.**

The branch's original commit claimed 20.0 → 17.7 KB. That number was measured against a `main` that
has since moved twice. After absorbing `origin/main` the index is **18,418 bytes (18.0 KB)** — the
compaction is real, but `main` added memories faster than rewording removed bytes.

The arithmetic behind this: ~139 entries each carrying a useful one-line hook has a floor around
17.5 KB. Going below it means **deleting memories**, not compressing them further. Five carry hooks
that already say CLOSED / FIXED / RESOLVED:

- `tea-retrofit-active-initiative`
- `governance-gate-scans-venv`
- `admin-credentials-drift-from-doc`
- `agy-school-identity-ghost-doc-window`
- `command-surface-restructure-2026-07-14`

Deleting those is an operator decision and was **not** taken here. This shipped as the compaction it
is, with the target dropped rather than faked.

## The two merges, and what the second one caught

The branch sat unmerged while `main` moved 182 files. It absorbed `origin/main` twice — never
rebased, per `git-policy.md`, which lists rebasing a pushed branch alongside force-push under
**Never**.

**First absorb** (`16f5525`) — one conflict, on the Jira row. The compacted line had quietly
**dropped "gate ARMED"**, a fact `main` still carried. Compaction that loses a fact is loss, not
compaction, so the resolved row carries all three: `acli` authed · gate ARMED · wrong-project key
rejected.

**Second absorb** (`f330aef`) — needed because SCC-51 landed on `main` in between and edited the same
file. The declared conflict was trivial, but it hid a real defect that the conflict markers did not
point at:

> SCC-51 **deleted** `artifact-budgets-are-scoped-not-universal.md` and replaced it with
> `limits-relocate-content-never-truncate.md`. This branch's compaction had folded that row into a
> combined **"Story artifacts"** line somewhere else in the file. Git merged both sides cleanly —
> the combined line was outside the conflict region — leaving an index that **pointed at a deleted
> file** *and* **still taught the 8/10 KB cap SCC-51 had just removed**, while the replacement
> memory sat on disk with no row at all.

A clean auto-merge is not evidence of a correct one. What caught it was not reading the diff but
asserting the invariant: **every memory file has exactly one index row, and every row resolves to a
file that exists.**

## Verification

```
files on disk = 139   rows = 139
STRANDED (file with no row)   : none
DANGLING (row pointing at nothing): none
conflict markers left: 0
```

- `run_all.py` — **8/8 files passed**
- `task_preflight.py` — 0 errors, LANE LOCAL, `origin/main` fully absorbed

## Pitfall worth keeping

Grepping one memory name to confirm a merge is not a check — the first absorb looked broken for
exactly that reason (`artifact-budgets-are-scoped-not-universal` had vanished, which was *correct*).
The stranded/dangling assertion answers the real question in one pass and does not care what
anything is named.
