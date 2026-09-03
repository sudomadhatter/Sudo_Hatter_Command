# Walkthrough — SCC-383: the story lane checks the epic branch against main

**Ticket:** SCC-383 · **Branch:** `chore/SCC-383-epic-sync-check` · **Date:** 2026-09-03
**Plan:** [implementation_plan.md](implementation_plan.md) · **Ticket outline:** [SCC-383.md](tickets/SCC-383.md)

## Task Checklist

- [x] Add the epic-vs-`main` count as item 1 of Step 0.6 in `/cicd-dev-story-tests`; renumber 1→2, 2→3, 3→4
- [x] Make it a **STOP**, not a silent sync — the merge lands on the epic branch and takes the operator's sign-off
- [x] Update the step heading to name the new check
- [x] SOP updated in the SAME commit (`sop-currency`): new paragraph opening the ② section + the command-atlas Step 0.6 node
- [x] Mirror door re-synced — `.opencode/commands/cicd-dev-story-tests.md` (the gate caught it; `sync-agents.ps1` is PowerShell and this box has none, so the copy was made by hand and verified byte-equal)
- [x] `_artifacts/_main/INDEX.md` row added (the gate caught that too)
- [x] Lobby gate green apart from one pre-existing failure, attributed below

## Evidence

### What changed

| File | Change |
|---|---|
| `.agents/commands/cicd-dev-story-tests.md` | Step 0.6 gains item 1 — the epic-vs-`main` count and its STOP; list renumbered; heading updated |
| `.opencode/commands/cicd-dev-story-tests.md` | mirror door, byte-equal to the master |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | ② section gains the Step 0.6 stop paragraph; atlas node gains `STOP if the epic is behind main` |
| `_artifacts/_main/INDEX.md` | session row |

The check itself:

```bash
cd "$PROJECT_ROOT" && git fetch origin && git rev-list --count origin/epic/<JIRA-KEY>-<slug>..origin/main
```

`0` → carry on. Anything else → stop, report the count, name what landed on `main` since, and ask.

### Gate — `python3 .agents/scripts/tests/run_all.py`

| Run | Result |
|---|---|
| First | `68/71 files passed` — FAILED: `test_check_maps.py`, `test_command_surfaces.py`, `test_sops_prds_folder.py` |
| After fixing both of mine | `70/71 files passed` — only `test_sops_prds_folder.py` remains |
| After provisioning the gitignored journal | **`71/71 files passed`** |

**The two that were mine, both fixed in lane:**

- `test_command_surfaces.py` — `.opencode/commands/cicd-dev-story-tests.md [stale]`. Editing the master drifted its mirror door. Copied and verified byte-equal; the file now reports 0 failures.
- `test_check_maps.py` — `_artifacts/_main/INDEX.md: missing row for '2026-09-03_epic-sync-before-story/'`. Row added.

**The third was NOT my diff — it is a worktree provisioning gap, and it is now closed:**

`test_sops_prds_folder.py` → `T9 every prose path reference resolves:
file_folder_structure+maintaining.md -> docs/.maps-journal.jsonl (resolves nowhere)`.

Attribution, measured rather than assumed. The same test **passes in the main lobby checkout** and
fails only in this worktree. The cause is that `docs/.maps-journal.jsonl` is **gitignored**
(`.gitignore:23` — `**/docs/.maps-journal*.jsonl`) and **a git worktree does not inherit gitignored
files**. It is present in the main checkout (generated 2026-09-02) and absent here. The doc that
references it is untouched by this lane — `git diff --stat 23c9f911 ab68505e -- docs/_scc_sops_prds/`
is empty, and `git status --short docs/` shows only `workflows_testing_SOP.md`.

Closed by provisioning the journal into the tree — the same class of gap that
`link-worktree-assets.py` already closes for `.env`, `.venv` and `node_modules`. The file is
gitignored, so it is local state and is not in the commit. `test_sops_prds_folder.py` then reports
**0 failures** and the gate is **71/71**.

**The standing gap this exposes, named once with its remedy:** `link-worktree-assets.py` links
`.env`, `backend/.venv`, `auth_keys/` and `node_modules` but not `docs/.maps-journal.jsonl`, so
**every** lobby Task lane that runs the full gate in a worktree hits this same red. The remedy is one
entry added to that script's link list. Not folded in here — it is a change to a different script and
belongs in its own lane rather than inside a procedure commit.

## Your Actions

1. **Merge the PR** for `chore/SCC-383-epic-sync-check` — the road to `main` is a PR you click.
