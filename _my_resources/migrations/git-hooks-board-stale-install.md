# Scrum-board stale-stamp hooks — per-machine install guide

**Why this document exists:** git hooks live in `.git/hooks/`, and `.git/` never travels through
GitHub — so the board stale-stamp automation must be installed **once per machine, per project**.
Cloning a repo does NOT bring the hooks with it. This is the checklist for every machine you work on
(desktop, laptop, new Mac).

## What the automation is (30 seconds)

A deterministic shell script — **no model, no cost, no network** — that git runs automatically after
every `commit` and every `merge`/`pull`:

1. It diffs `sprint-status.yaml` between the scrum board's last-reconcile commit and HEAD.
2. If any story/epic **status value** changed (comment-only edits are ignored), it stamps the board
   (`_my_resources/_quick_reference/sprint_scrum_board_map.md`):
   - a **banner** under the title listing every changed key: `old → new`;
   - an **inline flag next to every mention** of a changed story, e.g. `21.8b ⚠️`in-progress→done``.
3. Re-runs are self-updating: one banner, always reflecting the full drift — never duplicates.
4. **It never rebuilds the board and never runs a model.** The banner tells you to run
   `/sudo-update-scrum-board` — a full session with a smart model does the real reconcile, and that
   full rebuild clears every flag. Operator ruling 2026-08-02: no background model ever writes the
   board. The board may be stale, but never *silently* stale.

The tracked source lives in the project repo at `scripts/git-hooks/board-stale-stamp.sh`. The
installed hooks are two-line stubs that `exec` the tracked script — so script improvements arrive
via `git pull` with **no reinstall needed**. Reinstall is only ever needed on a brand-new clone.

## Install (per machine, per project — ~10 seconds)

```powershell
# from inside the project repo (currently: Projects/AGY_AVIATIONCHAT)
& scripts/git-hooks/install-hooks.ps1
```

Expected output:

```
installed: .git/hooks/post-commit -> scripts/git-hooks/board-stale-stamp.sh
installed: .git/hooks/post-merge  -> scripts/git-hooks/board-stale-stamp.sh
```

The installer **refuses to overwrite** a pre-existing hook that isn't ours — if it warns, open the
existing hook and chain the script manually (add the `exec` line from the stub).

**Which projects:** any project whose repo contains `scripts/git-hooks/board-stale-stamp.sh`.
As of 2026-08-02 that is **AGY_AVIATIONCHAT only**. If the kit gets copied to another project, the
same install step applies there.

## Verify it works (~30 seconds, safe — leaves no trace)

> ⚠️ **`sh` is NOT on PATH in PowerShell** — only inside Git Bash. Running these lines verbatim in a
> PowerShell window gets you `The term 'sh' is not recognized`, which looks like the hook is broken
> when nothing is wrong. This affects the **manual verify only**: git invokes its own bundled `sh`
> for hooks, so the installed hooks fire correctly regardless. Either run the block from **Git Bash**
> (where plain `sh` works), or derive git's bundled shell as below. Do not hardcode
> `C:\Program Files\Git` — installs vary (this machine's git is at `C:\Git`).

```powershell
# 0. Point $sh at git's own shell (works wherever git is installed):
$sh = Join-Path (Split-Path (Split-Path (Get-Command git).Source -Parent) -Parent) 'bin\sh.exe'

# 1. Fresh board -> must print NOTHING and exit 0:
& $sh scripts/git-hooks/board-stale-stamp.sh

# 2. Force a real drift view against an older commit -> banner + flags appear:
#    (any commit hash from `git log --oneline -- _bmad-output/implementation-artifacts/sprint-status.yaml`)
$env:BOARD_BASE = "<older-commit-hash>"; & $sh scripts/git-hooks/board-stale-stamp.sh; Remove-Item Env:BOARD_BASE

# 3. Inspect, then restore the test stamp (it is YOUR test edit — safe to discard):
git checkout -- _my_resources/_quick_reference/sprint_scrum_board_map.md
```

## Controls

| Need | How |
|---|---|
| Turn it off temporarily | create an empty file `scripts/git-hooks/DISABLE` (untracked) — delete it to re-enable |
| Uninstall from a machine | delete `.git/hooks/post-commit` and `.git/hooks/post-merge` |
| Update the behavior | edit the TRACKED `scripts/git-hooks/board-stale-stamp.sh`, commit — every machine gets it on pull; stubs never change |

## Troubleshooting

- **`\r: command not found` / hook errors on a new machine** — the `.sh` picked up CRLF line
  endings. `.gitattributes` pins `scripts/git-hooks/*.sh` to LF; if the file predates that rule run
  `git checkout -- scripts/git-hooks/board-stale-stamp.sh` after pulling, or re-clone.
- **Banner never appears** — confirm the hooks exist (`ls .git/hooks/post-*`), that
  `scripts/git-hooks/DISABLE` doesn't exist, and that you're in the MAIN checkout: the script
  deliberately does nothing inside story worktrees (it must never touch another lane's tree).
- **Banner appeared and you want it gone the right way** — run `/sudo-update-scrum-board`; the full
  rebuild is the only sanctioned way to clear the flags (hand-deleting them fakes freshness).

## Related

- Board + command design: memory `sudo-update-scrum-board-five-zones` · the command itself:
  `.agents/commands/sudo-update-scrum-board.md`
- Close-out keeps the board fresh in the normal path (Step 4.5 of `/sudo-update-sprint-memory`) —
  the hook is the tripwire for everything that leaks around it.
