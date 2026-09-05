# Walkthrough — Antigravity approvals harvest (SCC-405)

**Date:** 2026-09-04 · **Branch:** `chore/SCC-405-antigravity-approvals-harvest` (cut from `origin/main` @ `6cf4d37e`)
**Ticket:** [SCC-405](https://sudo-command.atlassian.net/browse/SCC-405) · **Door:** `/smh-llm-approvals` (exempt under `artifacts-always-first.md` § When to Skip)

## The operator's words, verbatim

> We need to do all of it what is the best way for you so we have the lowest chance of mistakes and failures ?

and, at the Step 2 gate:

> approved

The pick he approved: **the two widened families (`find`, `git worktree` reaching Antigravity) plus
the three new ones (`uname`, `lane_qualify.py`, `link-worktree-assets.py`), nothing from Claude's
stopped list, and the ~30 unpicked store rows dropped on apply.**

## What the harvest actually found

The Antigravity store carried **35** rows the tracked fence did not. The surprise was that almost
none of the underlying commands were missing from the source — nine already existed as families
(`find`, `git worktree`, `wc`, `pwsh`, `git fetch`, `git merge-base`, `git diff`, `git rev-parse`,
`acli jira`). Two of them were scoped `"only": ["claude"]`, so they rendered to
`.claude/settings.json` and never reached Antigravity at all. The harvest was therefore mostly a
**scoping** correction, not a set of new grants.

## What landed

| Row | Change | Renders to |
|---|---|---|
| `allow-git-worktree` | `only` widened `["claude"]` → `["claude", "antigravity"]` | `command(git worktree)` · `unsandboxed(git worktree)` |
| `allow-uname` | **new** family, `cmd: "uname"` | `Bash(uname:*)` · `command(uname)` · `unsandboxed(uname)` |

Net: **4 rows added to `.agents/permissions/antigravity.json`, 1 to `.claude/settings.json`.**
`.vscode/settings.json` is unchanged — see below.

## Two approved picks did NOT land, and neither is a fence refusal

**`find` → Antigravity: backed out.** It was written, rendered, and the suite refused it:

```
[FAIL] A5 every unknown tool ASKS on all three:
       {'antigravity': ['find . -delete', 'find . -exec rm {} ;']}
[FAIL] B8 Antigravity render keeps every baseline DECISION:
       regress=[('find . -delete', 'ask', 'allow'), ('find . -exec rm {} ;', 'ask', 'allow')]
```

Antigravity's grammar is a per-token anchored regex with no way to exclude a flag, so a bare `find`
token there grants `find . -delete` and `find . -exec rm {} ;`. There is no deny row that refused
it — like `npx` before it, this is a **battery case** (`test_permission_parity.py` A5/B8), and the
refusal is correct. `find` stays Claude-only; the reason is recorded in the family's own `why`.

**`lane_qualify.py` and `link-worktree-assets.py`: not written, because they were already covered.**
`allow-python3` (`cmd: "python3"`) is already scoped `["zoo", "claude", "antigravity"]` and already
renders `command(python3)` / `unsandboxed(python3)`. Adding a narrower row underneath an existing
broader family is drift, not a grant. This is **less** than the approved pick, and deliberately so.

## The honest limit on what this buys

Closing the drift is measured and real: the store went from 35 store-only rows to `in sync with
tracked file`. Whether it means **fewer prompts** is not proven here, and one measurement argues
against assuming it. `command(wc)` was already tracked and already in the live store, yet the store
still accumulated `wc -c /home/dlohn/.../{...}` as a separate click — a strict token-extension of a
grant that was already in force. Two readings fit: either the vendor's matcher requires the pattern
to cover every token of the command (so prefix families never help), or those clicks simply predate
the grant being applied. Nothing on disk distinguishes them. The next Antigravity session is the
evidence, and it is worth watching rather than assuming.

## Zoo was deliberately not touched

The harvest found **zero** Zoo threads. No row here is scoped to `zoo`, `.vscode/settings.json` is
byte-unchanged, `zoo_permissions_apply.py` never ran, and VS Code never had to be closed.

## Evidence

```
python3 .agents/scripts/permission_render.py --check        in sync (zoo, claude, antigravity)
python3 .agents/scripts/tests/test_permission_parity.py     99/99   (97/99 before the find backout)
python3 .agents/scripts/tests/run_all.py --on-main          72/73 files
python3 .agents/scripts/antigravity_permissions_apply.py    in sync with tracked file (allow=123 deny=384)
git diff --name-only origin/main...HEAD                     scope guard: 4 paths, all permitted
```

**The one red is pre-existing and was measured as such**, not assumed: with this lane's three files
stashed, `test_command_surfaces.py` fails identically at **329/330** on untouched `main`. `CS-22 B`
names three *sibling worktrees* carrying a stale copy of the test file
(`SCC-394-ag-skills-door` and two `agent-*` scratch trees) — no file in this diff. It will pass on
the PR, where the runner has no `.claude/worktrees/` to scan.

The backup of the pre-apply Antigravity store is kept at
`~/.gemini/config/config.json.scc-backup`.

## Why there is no `Verdict:` stamp here

This lane is a named exemption in `artifacts-always-first.md` § When to Skip (SCC-393): no plan, no
self-audit, no RED-first assertion and **no review verdict** for a permission harvest. It is what
`main_write_gate.py` calls a *lightweight lane* — a walkthrough carrying no `Verdict:` stamp, which
is why the flight-event requirement does not apply to it.

The first cut of this record carried one anyway, because `flight_recorder.py` refuses to stamp a
walkthrough without it. That was the wrong direction: the recorder's requirement is evidence that
this lane is not the kind of lane it records, not a reason to manufacture a verdict. The stamp and
its flight event were both removed.

What stands in for the review is the four guards, each of which was RUN rather than judged:

| Guard | Result |
|---|---|
| the operator's live pick at Step 2 | given: "approved" |
| `permission_render.py --check` | in sync (zoo, claude, antigravity) |
| the WHOLE `run_all.py` suite | ran before any commit; refused `find`, which was backed out |
| the scope guard | 3 paths outside `_artifacts/`, all among the four permitted |

## Your Actions

1. **Reload the VS Code window.** The Antigravity extension writes its in-memory settings back on
   every click, so without a reload the apply is silently undone.
2. **Merge the PR** when `main-write-gate` is green. This door opens the PR and stops.
3. **Watch one thing next session:** whether Antigravity still stops for `git worktree` and `uname`.
   If it does, the vendor's matcher needs every token covered and the family model buys less here
   than it does on Claude — worth knowing before the next harvest.
