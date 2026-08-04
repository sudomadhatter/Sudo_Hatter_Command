---
IsArtifact: true
ArtifactMetadata:
  title: Propagate the verdict-reading contract across commands + maintained projects
  type: walkthrough
  date: 2026-08-03
---

# Walkthrough — verdict-contract propagation

Plan: [implementation_plan.md](implementation_plan.md) · Branch `main_debug` · **uncommitted by choice**
(see Your Actions — a concurrent session is writing these repos).

## Task Checklist

- [x] **Sweep — 7 verdict-readers checked against [`artifacts-always-first.md:210-212`](../../../.agents/rules/artifacts-always-first.md#L210-L212)**
  - 1 real gap (boot), 1 minor (resume), 5 already correct — **3 of those correct *by design***
    (`sudo-update-sprint-memory` fails open on purpose; `sudo-quick-dev` has no review; autopilot keys on
    *section presence*, flips only to `review`, never `done`). Recorded in the plan so they don't get
    "fixed" into blockers later. I had assumed autopilot was a gap when I raised this — it isn't.
- [x] **WS-A — [`sudo-boot-sprint-memory.md`](../../../.agents/commands/sudo-boot-sprint-memory.md) Step 2b** (5,209 → 6,761 B)
  - `review` status no longer implies close-out: read `## Code Review` → `Verdict:` from the lane's
    `walkthrough.md`; pre-08-02 legacy fallback (read-only); SHA≠HEAD → `/sudo-code-review`, never
    close-out; N lanes of one epic collapse to `/sudo-merge-epic-workingtrees`.
  - Added the two board hard-rules boot lacked: **live worktree outranks the YAML**, and **never
    recommend a `descoped`/`deferred` story**.
  - Wording lifted verbatim from the board's ⛔ block so the two cannot drift.
- [x] **WS-B — [`sudo-resume.md`](../../../.agents/commands/sudo-resume.md) Step 3** — report the YAML
  status as *the YAML's claim*, not truth; boot owns resolution; never recommend close-out from resume.
- [x] **WS-D — propagate** — `/sync-agents` + `-Maintained`, 4 platform surfaces × 4 projects.
- [x] **WS-C — landed in all four repos** (operator reaffirmed scope: lobby + the maintained three)
  - lobby `b72e0f1` (10 files) · Fresh `861448b` (3) · NEXgen `bcc940d` (3) · AGY already carried it
  - all four pushed, `0 0` vs `origin/main_debug`, 0 dirty
  - Fresh's lobby gitlink is configured `ignore=all` — left alone rather than `--force`d

## Evidence

| Plan check | Result |
|---|---|
| 1 · boot names verdict source, staleness, legacy fallback, worktree-wins, no-deferred | ✅ 5/5 markers |
| 2 · boot's wording matches the board's (no drift) | ✅ ⛔ block lifted verbatim |
| 3 · boot still read-only / discovery-only | ✅ `Read-only — … never edit anything.` intact; 0 write verbs added |
| 4 · workflow-enforcement gate | ✅ **64 checks, 4/4 files** (`closeout_preflight` 24 · `gate_receipt` 18 · `story_status` 10 · `encoding` 12) |
| 5 · byte-identity across projects × platforms | ✅ **32/32 MATCH** (SHA-256 vs master, all 3 edited commands) |
| 6 · Fresh + NEXgen clean 3-file commit | ✅ 3 files each; the concurrent session committed its own 60 first, so nothing of mine swept it |
| 7 · post-push: fix present in **HEAD** of all 4 repos, 0 dirty, `0 0` vs origin | ✅ 4/4 — boot + resume + board all YES |

Launcher threshold: boot 6,761 B and resume 5,761 B are both under 11,500 B → full bodies, no thin
launcher. Board unchanged at 16,979 B (still a launcher). No code changed → no test suite in scope.

**The 8 KB budget question.** It is real but narrower than I was applying it:
[`artifacts-always-first.md:40`](../../../.agents/rules/artifacts-always-first.md#L40) caps the two
*living story* docs. The enforcement gate's own case `F7 _main/ initiative plans are out of scope`
confirms `_artifacts/_main/` is excluded. I had also invented a size gate for an AGY quick-reference doc
last session — that was over-application, not a rule.

## Suite Ledger

| Scope | Command | Result | Why this run |
|---|---|---|---|
| workflow-enforcement gate | `python .agents/scripts/tests/run_all.py` | **pass — 64 checks, 4/4 files** | command-file edits |
| toolkit propagation | `sync-agents.ps1`, then `-Maintained` | pass — 4 projects × 4 surfaces | WS-D |
| byte-identity | SHA-256 master vs 32 synced copies | pass — 32/32 | verification 5 |

## Your Actions

**⚠️ Three other `claude` processes are live on this machine and one is committing to these repos.**

| Evidence | |
|---|---|
| Lobby HEAD moved mid-session | `c103e00` *"feat(workflow): Wave 3 + Wave 5"* committed **21:49:20**, ~5 min before I checked |
| It vendored my **uncommitted** work downstream | Fresh HEAD `7c7a06f` *"vendor Wave 3 + Wave 5 from the lobby master"* **already contains my `sudo-resume` edit**, which is still uncommitted in the lobby |
| NEXgen has a foreign index | **60 files staged** by that process (incl. new `A .agents/scripts/git-hooks/*`); only my 3 board files are unstaged |
| Processes | 4 × `claude` running (21:42–21:46) |

So the toolkit fix is **done, synced, and gate-green everywhere** — but the git state is being written by
someone other than me, and `git commit` in NEXgen would sweep 60 files I did not author.

**Resolved** — the concurrent session committed its own work; my four commits then landed cleanly on top
with explicit paths only, sweeping nothing of theirs.

| # | Pri | Action | Closes |
|---|---|---|---|
| 1 | 🟡 | **`B-L-WorldWide` (12 sudo cmds) and `BRKN_Tattoos` (13) have the toolkit installed but are NOT on `maintained-projects.txt`.** Frozen at July copies — including the old `sudo-boot-sprint-memory` with exactly this defect. Either add them to the maintained list or accept they drift | toolkit coverage |
| 2 | 🟢 | Restart opencode to pick up the refreshed global cache (47 cmds) | sync propagation |
| 3 | 🟢 | GitNexus index stale after the concurrent commits — `gitnexus analyze` | index freshness |
| 4 | 🟢 | `BRKN_Tattoos` has a gitlink with **no `.gitmodules` mapping** (`git submodule status` errors on it) | lobby submodule hygiene |
