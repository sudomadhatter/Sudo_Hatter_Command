# SCC-58 — Verifying workflow components · walkthrough

**Verdict: PASS @ `0c232d8` (center) · `91baad8` (skeleton)**
**Date:** 2026-08-09 · **Lane:** `chore/SCC-58-verify-workflow-components` (worktree)

---

## What was asked, and what the answer turned out to be

| Ticket question | Answer |
|---|---|
| Is `/self-assess` actually using GitNexus for edges? | **No.** The gate could never fire. Fixed. |
| Audit its effectiveness | The graph is worth using; the *instructions around it* had three gaps. All closed. |
| Does the skeleton have the file/folder guide, set up and used? | **Yes** on both — but its content contradicted the project's own law in six places. Fixed. |

---

## 1. The GitNexus gate was dead — and would have stayed dead

`/self-assess` is `/sudo-self-audit`. Phase 1 *does* instruct graph-first edge analysis, gated on:

> the repo's `AGENTS.md`/`CLAUDE.md` carries a "GitNexus — Code Intelligence" section

The heading is real. **The file is wrong.** `# GitNexus — Code Intelligence` is the H1 of
`docs/gitnexus.md` in all three repos, and never a section of `AGENTS.md` — which carries only a
lowercase one-line pointer (`**GitNexus** — code-intelligence (…)`, AGY `AGENTS.md:177`). An agent
checking the literal condition finds nothing and falls through to grep, every time.

**Matching the heading instead would have failed the other way.** The skeleton ships
`docs/gitnexus.md` titled `# GitNexus — Code Intelligence (project skeleton — NOT indexed yet)` — a
title match returns a **false positive** on a repo with no index at all. Prose is the wrong predicate
in both directions, so detection now calls `list_repos`, which is ground truth.

## 2. What the graph is actually worth (measured, not assumed)

`impact(get_db, upstream, summaryOnly)` against AGY:

```
impactedCount: 286   direct: 141   processes: 72   modules: 12
epistemic: "exact"   risk: CRITICAL
```

Grep on the same symbol returns a flat file list — no depth, no execution flows, no risk. The tool
earns its place; only the wiring was broken.

## 3. Three effectiveness gaps, each an observed failure mode

| Gap | Why it bites | Fix |
|---|---|---|
| Called the graph "authoritative" with **no freshness check** | The index is a machine-local cache that does not travel with git. `Sudo_Hatter_Command`'s was **4 commits behind HEAD** during this very audit; AGY's is pinned to `epic/AVCH-18`. A stale index describes code that no longer exists — and reads exactly like a clean audit. | Compare `lastCommit`/`branch` vs `git rev-parse HEAD` before trusting it; stale ⇒ lead, not authority. |
| `repo:` was **conditional** | Three repos are indexed. An unscoped call silently answers about the wrong one. | Unconditional. |
| Grep cross-check named dynamic/string refs, **not attribute dispatch** | `impact()` returns 0/LOW for `self.<attr>.<method>()`. "Nothing breaks" is the answer it is most likely to get wrong — and the most dangerous to be wrong about. | A 0/LOW verdict must be grep-verified. Non-zero results are trustworthy; it is the *absence* of edges that is unreliable. |

All three mirrors kept byte-identical: `.agents/commands/`, `.agents/workflows/`, `.opencode/commands/`.
`sudo-self-audit_AP.md` delegates by `@`-reference and inherits the fix — verified, no edit needed.
`SKILL.md` is a 15-line launcher — no change.

## 4. The skeleton guide argued with its own AGENTS.md

Present and routed (`AGENTS.md` §6), so the ticket's question answers yes. Its content had drifted:

| Claim | Ground truth |
|---|---|
| `.agents/` is "the **vendored master toolkit** — `rules/ skills/ commands/ workflows/ scripts/ templates/`" | On disk: only `rules/`, `skills/`, `scripts/`, all index-only. Contradicted `AGENTS.md` §3 **and** its own §5. |
| "Git — **never** commit/push yourself" | `AGENTS.md` §8: commits **and pushes** on `claude/*` are FREE. A gate conflict. |
| `task-list.md` mandated 3× | `AGENTS.md` §5: "no separate `task-list.md`". |
| `_system/` at the center | Does not exist. |
| `../../router.md` | Resolves to the skeleton root, which has no `router.md`. |
| `AGENTS.md` §5 listed `self-audit-stress-test.md` | Retired 2026-08-02. |

## 5. What was deliberately NOT done here

The operator asked mid-session to extend the parallel-work rules. Split to **SCC-62** because it
touches six files that SCC-61's lane had open and uncommitted at the time. Split by operator decision.

**This session was its own evidence for that ticket:** the lane opened onto a shared checkout sitting
on *another* lane's branch with 11 dirty files, while SCC-61 was itself a ticket about a preflight
resolving the wrong branch. Same root cause, twice, in one afternoon.

---

## Task Checklist

- [x] Locate `/self-assess`; confirm whether it calls GitNexus for edges — **it could not**
- [x] Audit effectiveness empirically (`impact()` on AGY, not doc-reading alone)
- [x] Fix detection + add repo/freshness/0-LOW guards across all 3 mirrors
- [x] Verify skeleton ships the file/folder guide and routes to it — **it does**
- [x] Fix the 6 contradictions in the skeleton guide (separate repo, separate commit)
- [x] File SCC-62 for the parallel-worktree change
- [x] Gates: `run_all` 10/10 exit 0 · `sop_currency` exit 0 (re-run after merging main)

## Your Actions

Nothing manual. Both lanes landed by this close-out.

**Scope honesty:** the fixed gate was proven by reading the condition against every repo's files and by
calling `impact()` directly. `/sudo-self-audit` was **not** run end-to-end to watch the new gate fire —
that needs a real plan to audit, which this Task never produced. First story that runs ② exercises it.
