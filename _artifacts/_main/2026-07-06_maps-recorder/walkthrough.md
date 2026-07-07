# Map-drift Recorder — upkeep walkthrough

## What it is
A commit-time **recorder** that keeps the repo-map / INDEX upkeep loop pre-scoped. A `post-commit`
git hook classifies each commit's changes into the `/1_update-maps` judgment categories and appends
one line to a machine-local journal. The SessionStart nag and `/1_update-maps` then read a ready-made
worklist instead of re-deriving "what changed."

## The pieces (per repo)
- `.githooks/post-commit` — fires after every commit (non-blocking; can't break a commit).
- `.agents/scripts/record_map_changes.py` — the classifier. Modes: `--commit HEAD` (hook), `--nag`
  (print classified tail), `--consume <sha>` (archive reconciled lines).
- `docs/.maps-journal.jsonl` — the journal. **Gitignored / machine-local** (like `.gitnexus/`).
- SessionStart hook (`.claude/settings.json`) runs `record_map_changes.py --nag`.
- `check_maps.py --set-anchor` now also **consumes** the journal (rolls reconciled lines to
  `docs/.maps-journal-archive.jsonl` — a move, not a delete).

## The rule that matters
The journal is a **cache, never the truth.** Every reader runs a freshness guard (journal's last
sha == HEAD?). If a commit bypassed the hook (another machine, `--no-verify`, rebase), the nag prints
"behind HEAD" and you fall back to `check_maps.py`'s `git diff <anchor>..HEAD`, which stays ground truth.

## Enabling it in a repo (one time)
```bash
git config core.hooksPath .githooks
```
Already set for the lobby, AGY_AVIATIONCHAT, Fresh_Workspace_BMAD.

## Day-to-day
Nothing manual. Commit as usual → the hook records. At session start the nag tells you what needs a
purpose line / INDEX row / sync. Run `/1_update-maps` to apply the prose fixes; its close-out
`--set-anchor` clears the journal.

## Scope
Live in 3 repos. Other `Projects/<name>` need the same 4 steps (vendor the script, add the hook,
gitignore the journal, add the SessionStart nag, `git config core.hooksPath .githooks`).
Byproduct: fixed a pre-existing Windows cp1252 crash in `check_maps.py`'s depth-3 nag.
