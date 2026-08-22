# SCC-269 — walkthrough

**Lane:** `chore/SCC-269-workspace-standard-reconcile` · **Ticket:** SCC-269 (Subtask, Part A of SCC-262)
**Tree:** `.claude/worktrees/SCC-269-workspace-standard-reconcile` · **Lane type:** `/smh-quick-fix` (LIGHT, re-qualified LIGHT on the real diff)
**Verdict:** N/A — the lightweight lane carries no review verdict by design (SCC-162)

---

## The ask, and the answer

Operator: *make sure the folder-as-workspace idea we used to design the workflow and file structure is
being implemented, and that it is clear in `docs/workspace-standard.md`.*

**The idea is implemented. The standard describing it had drifted.** Every requirement in
`_my_resources/research_docs/implementation-plan_folder-as-workspace-routing-system.md` (R1–R8) was
ground-truthed against the live tree and found present — adapters → numbered `AGENTS.md` → `router.md`
(categories, route-up, ask-don't-guess) → 73 skills pulled per routing row → `active-context.md`
(`1 PRIME` · `5 PICK UP` · `6 HAND OFF`) → gates → portability. The plan's `_experiment/` is
`_routing-canary/`; its `_system/AGENTS.md` is `docs/system-builder.md`. None of that was written down
in one place, and eight statements in the standard contradicted the brain it describes.

## What changed

- **`docs/workspace-standard.md`**
  - frontmatter `sources:` — theory doc repointed to `_my_resources/research_docs/` (renamed in `6d2b630`);
    the rollout doc (`_my_resources/docs/master-implementation-plan.md`, deleted in `f43c7bf`) named as retired
    instead of linked dead
  - **new §0.5 Lineage** — table mapping plan R1–R8, `_experiment/`, `_system/`, the validation loop and the
    anti-patterns to their live locations, with the section of the standard that states each; plus the
    lobby (§1–§8) vs floor (§1–§9) numbering difference, which the standard never said
  - Layer 1 item 9, "Supporting files", Format checklist, PATH CONTRACT "Open tasks" row — `todo_list.md` is no
    longer named as a "pick up" / "what's next" source; all four now state the live-board rule and point at
    root `AGENTS.md` §7 / `jira.md` (the ruling of 2026-08-09 the standard had missed)
  - Format checklist — "vendored `docs/workspace-standard.md` present" inverted to "**no** vendored copy in a
    thin project" (it contradicted the thin model stated three lines above it)
  - Part 2 "Git — one policy" — now matches `git-policy.md`: agents commit and push; the
    hand-Daniel-the-command default is gone
  - `.agents/` tier paragraph — garbled "`bmad/` is / and `bmad/` is" sentence repaired
  - Routing canary section — all five of the plan's validation checks tabled (canary · cold route ·
    persistence · negative/route-up · token frugality); it named two
- **`router.md`** — the "What do we do next" row routed to the retired `todo_list.md`, against `AGENTS.md` §7;
  it now routes to the live board (`SCC` from the lobby, the project's key inside one) with the rank order

## Flagged, not fixed — needs a ruling

- **Root `GEMINI.md` is not a one-line adapter.** It carries three Gemini-specific hard rules (sync scope,
  worktree enforcement, explicit staging). Plan R8, the standard's Layer 1, and `AGENTS.md` §8 all say
  "nothing model-specific in shared files". Either those rules move into `AGENTS.md`/`.agents/rules/` and the
  adapter shrinks, or the exception is written down. Recorded in §0.5 as an open exception.
- `_routing-canary/Power.md` shows the placeholder — the canary has not been run since its last reset. This
  lane changed `router.md` (routing structure), which is a re-run trigger per the standard.
- `jira_feed.py index-row` reported the first row on SCC-262 as *"MISSING 1 line — data loss"*: the line it
  lost was the `(empty - this cycle has taken no work yet)` placeholder it is supposed to replace. Read-back
  confirmed the INDEX is intact. The guard false-alarms on the first row of a fresh rolling ticket.
- `jira_feed.py devrecord --append-new` posted a **second** Dev Record comment (footer says "one per ticket, updated
  in place") and dropped the Outcome line. Both partials were deleted and one complete record re-posted;
  SCC-269 carries exactly one.

## Evidence

```
lane_qualify --paths docs/workspace-standard.md router.md        → LIGHT (intent)
lane_qualify --paths $(git diff --name-only origin/main...HEAD)  → LIGHT (real diff: the same two files)
run_all.py                                                       → 48/48 files passed
workflow_lint.py --toolkit-only                                  → 0 error(s), 0 warning(s), 8 info
```

Commit: `47a51e7` on `chore/SCC-269-workspace-standard-reconcile`, pushed (`origin/...` tracking, 0 ahead
after push). Record commit follows.

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [x] The root `GEMINI.md` exception is **filed, not owed here** — SCC-279 (Part C of SCC-262) carries
  the ruling with both doors written out (fold the three rules into `AGENTS.md`/`.agents/rules/`, or
  codify the exception in the standard). It is recorded in §0.5's R8 row as an open exception in the
  meantime, so the standard is honest about it today.

**Context, nothing owed:** this lane changed `router.md`, which is a `_routing-canary/` re-run trigger
per the standard's own cadence. The canary's `Power.md` is sitting on its placeholder, so it has not
run since its last reset — worth a green run on the next session that touches routing structure.
