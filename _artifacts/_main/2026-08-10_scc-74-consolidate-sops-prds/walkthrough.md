---
IsArtifact: true
ArtifactMetadata:
  title: SCC-74 walkthrough - every SOP/PRD consolidated into docs/_scc_sops_prds and put under a gate
  type: walkthrough
  date: 2026-08-10
---

# SCC-74 — Walkthrough: the SOPs and PRDs get a home that can notice when they rot

**Date:** 2026-08-10 · **Repo:** Sudo_Hatter_Command (lobby) · **Lane:** Task (LOCAL)
**Branch:** `chore/SCC-74-consolidate-sops-prds` · **Commits:** `4fad953` (red) → `8020873`
(consolidation) → `53677fb` (references + content + law)

> **⛔ This branch is NOT merged.** It is pushed, gated and preflight-clear, and it is handed back
> for the operator to invoke `/smh-close-task-merge-tree`. Merging it on the authority of an earlier
> invocation is the exact failure `one-shot-permission-persists-in-context` records.

## What changed, in one line

Thirteen procedural documents moved out of the one folder every drift-checker in this system is
**forbidden** to look at, into `docs/_scc_sops_prds/` — where a test in `run_all` and `check_maps.py`
both watch them.

## The finding that drove it

The docs did not rot from neglect. `_my_resources/` is named in `SCAN_IGNORES` (`check_maps.py`), in
`DEFAULT_REGEN_IGNORE` for the repo-map, and in the GitNexus ignore list — and its own local law said
*"excluded from repo-map regen + linter scans … do not fix that."* Ten of the thirteen lived inside
it. **No automation could reach them, so nothing was able to notice when they went wrong.**

It showed. The index they lived under listed **2 files that did not exist** and omitted **4 that
did** — and that index had been wrong long enough that nobody could say when it broke.

The operator's ruling mid-session turned this from a cleanup into a law: `_my_resources/` is his
**thinking and brainstorming space** — agents ignore it unless he links a specific document, and
staleness there is *fine by design*; `docs/` is the **maintained** surface and must never go stale.
Those two folders now get opposite treatment on purpose, which makes "a procedural doc in
`_my_resources/`" a defect by definition rather than a matter of taste.

## Developed test-first (operator ruling)

Every item in the definition of done was written as an executable assertion **before** the work that
satisfied it, in `.agents/scripts/tests/test_sops_prds_folder.py`. All of them failed at `4fad953`.

**Running the red caught three bugs in the tests themselves** — which is the entire argument for
running it rather than assuming it:

| Bug | Why it mattered |
|---|---|
| T3/T4 passed **vacuously** on an absent folder | no folder → empty file set → nothing to complain about. **Deleting the folder would have made the suite healthier.** |
| T7 filtered **absolute** path parts | this repo is checked out under `.claude/worktrees/<lane>/`, so `"worktrees"` matched every file and it found **0 of 2** duplicate copies |
| T6 used a top-level glob | `diagrams_guides/` nests its docs one level down, so it saw **3 of 13** and reported a nearly-clean folder |

## ⭐ A silent fail-open, found only by writing the test

`sop-currency.sh` guards `[ -f <SOP doc> ] || exit 0`, so the gate degrades gracefully in a project
clone that has no SOP page. **Move the doc without moving that literal and the lobby starts looking
like a project clone:** the hook exits 0 before it ever reaches the Python, and the gate **disarms
itself** — no output, no error, and under VS Code (which renders hook output nowhere the operator
looks) indistinguishable from a clean pass.

T5 could not see it: it only reads the Python constant, and the two drifting apart *is* the bug. T8
now pins them together, and it was proven the honest way — repoint one, watch it go red, fix the
other, watch it go green.

## The autopilot duplicate — resolved on evidence, not preference

Two copies, **508 differing lines**. The plan said this needed the operator's eyes; the evidence made
it unambiguous instead:

| | `.agents/reference/` | `_my_resources/diagrams_guides/system/` |
|---|---|---|
| last substantive commit | **2026-08-09** (SCC-41, twice) | 2026-06-28 |
| worktree concurrency model | documented throughout | **zero mentions** |
| language | current | *"the v2 idea"* |

The older copy's unique §7 was the **superseded pre-worktree** concurrency model, so nothing was
grafted. `.agents/reference/` held only that doc and is retired; the constraint it existed for
(keep reference docs off Antigravity's command surface) is now better served — a doc under `docs/`
is off every surface *by construction*.

## ⛔ Corrections to this ticket's own research

**1. The "26 retired `sudo-` hits" figure was wrong in both directions.** Ground truth: **3**
unresolved command references; **9** pointing at a deleted `_bmad-output/sudo-tests` directory (real
staleness, but a dead *path*); and **3** on `sudo-command.atlassian.net` — the **live Jira site
slug**, which a blanket prefix rename would have broken. So T4 resolves references against
`.agents/commands/` instead of pattern-matching a prefix: a command reference is dead when no master
answers to that name. Self-maintaining, and it catches the *next* rename with no edit.

**2. I overstated `check_maps.py` coverage in the first draft of the new INDEX.** `check_paths`
inspects **backticked, multi-segment paths inside table rows** — a dead markdown link sails straight
past it. My first control "passed" because I appended a plain line, which proved nothing. Redone
inside a table row, the controls are decisive. The INDEX now states the real boundary: `check_maps`
reads table cells, T2/T3 read links, neither substitutes for the other.

## check_maps: the narrative-ledger rule generalised

`_artifacts/_main/INDEX.md` was **already permanently red on `main`** — dead paths
`.claude/commands` and `docs/file_structure_rules/README.md`, both correctly recorded as removed. The
exemption existed but named only `_artifacts/INDEX.md`, while the depth-3 bucket ledgers are where
the detailed narrative actually lives, and a row describing work that *retired* a path has to name
it. Now any `_artifacts/**/INDEX.md` is exempt. **A lint that is red for reasons nobody may fix
trains people to skip its output** — that was the real cost.

Proven with controls both ways: an identical dead row **fails** in a live index and is **exempt** in
the ledger.

## F5 earned its place

The plan required confirming both vacated folders were empty **against disk, never against an
index**. That caught `diagrams_guides/INDEX.md` still sitting there — the very index that listed 2
phantom files. Verifying against it would have deleted a folder on the word of a document already
proven wrong.

## Gates

| Gate | Result |
|---|---|
| `run_all.py` | **12/12 files** (11 before; the new suite auto-joined) |
| `test_sops_prds_folder.py` | **16/16** — 5 of them fixture controls proving the detector fires *and* stays quiet |
| `check_maps.py` | **clean** — including the `_artifacts/_main` drift that was red on `main` |
| `workflow_lint.py --toolkit-only` | 0 errors, 2 warnings (both pre-existing, unrelated) |
| `sop_currency.py` | correct in all 3 directions: no doc → reject · new path → accept · old path → reject |

Two self-inflicted failures were caught by the new gate before commit: a literal markdown-link
example in the INDEX, and retired command names inside an explanatory note. Both were the gate
working on its author.

## Handed back — open items for the operator

1. **⚠ SCC-77 overlaps this lane — and should land FIRST.** `chore/SCC-77-main-write-gate` is live
   and edits `_my_resources/_quick_reference/sudo_workflows_testing.md` (53 lines) and
   `.agents/commands/smh-close-task-merge-tree.md` (17) — files this branch **moves and renames**.
   Git handles rename-vs-edit, but landing SCC-77 first makes the question disappear; landing SCC-74
   first means SCC-77's merge needs a real review. No hook-file collision: SCC-77 adds
   `pre-push-main-approval.sh` / `mint-push-token.sh`, this touches `sop-currency.sh` only.

   **A second, independent reason to sequence it that way:** this lane's first preflight came back
   `BLOCKED — 1 uncommitted change`, on `.opencode/node_modules`. The cause is a genuine repo bug —
   `.gitignore` line 24 read `**/node_modules/` **with a trailing slash**, which matches directories
   only, while `link-worktree-assets.py` puts a **symlink** at that path. Git treats a symlink as a
   file, so it was ignored in the shared checkout and *not* ignored in any worktree, and
   `task_preflight.py` counted it as uncommitted — blocking the close-out of a lane that was clean.
   **SCC-77 already carries the exact fix** (drop the trailing slash, with a comment recording why),
   so it was deliberately NOT fixed here — a duplicate edit to the same three lines would collide
   head-on. This lane instead ran `link-worktree-assets.py --unlink`, which the worktree rule
   requires before removal anyway; the preflight then came back **clear**. Until SCC-77 lands, every
   lane hits this, and the workaround is the unlink.
2. **Memory will be stale after the merge.** `sop-doc-currency-gate.md` and
   `relocated-doc-links-are-mispathed-not-dead.md` name the old SOP path. The store is read-only
   outside the sanctioned flows, so nothing was edited — **your call at close-out.**
3. **AGY's second copy needs an AVCH ticket.** `Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_workflows_testing.md`
   was already behind; it now differs in *location* too. Cross-repo work takes a ticket per repo, so
   it is recorded as open drift in `sop-currency.md` with the two options, not fixed here.
4. **An empty `docs/_scc_sops_prds/` exists in the main checkout** from when the location was being
   settled — harmless, superseded by this merge.
5. **SCC-78 minted** (under epic SCC-33): `/smh-self-audit` + `/smh-quick-dev`, the Task-lane
   equivalents of the story-loop commands. This session is the evidence — `/cicd-self-audit` had to
   be run against the lobby it explicitly refuses.
