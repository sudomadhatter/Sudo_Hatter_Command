# SCC-419 — cycle 12 opens: track the BLUF output style

**Ticket:** SCC-419 (the 2026-09 rolling ticket, cycle 12)
**Lane:** `chore/SCC-419-bugs-cycle-12`, cut from `origin/main` at `22b2eb6a`
**Date:** 2026-09-06

## What this is

The operator's custom output style, `BLUF.md`, was sitting **untracked** in `.claude/output-styles/`.
It is active in his sessions — the system prompt loads it — but git had never seen it, so one
`git clean` would have deleted it with no way back.

That is not hypothetical. The same file was lost once already: the Mac's copy was never found on
disk and had to be **recovered by asking that Claude to quote its own system prompt's output-style
section**. Tracking it here means the next machine gets it from the repo instead of from a
reconstruction.

Found while clearing the lobby's dirty working tree after the AVCH-128 hosting retirement. The
operator's call, in his words: *"yes commit it"*.

## What landed

| File | Change |
|---|---|
| `.claude/output-styles/BLUF.md` | tracked as-is, byte-identical to the working copy — frontmatter (`name`, `description`, `keep-coding-instructions: true`) plus the seven rules |
| `_artifacts/_main/INDEX.md` | one row for this session folder — required, and the enforcement suite caught its absence (below) |
| `_artifacts/_main/2026-09-06_scc-419-bugs-cycle-12/` | this walkthrough and the lane manifest |

No rule text was edited, and the style's content is exactly what his sessions already load.

## Why it belongs in the repo rather than his personal area

`.claude/` is already a **tracked** directory here — `.claude/mcp.json` and the whole of
`.claude/rules/` live in git. An output style is machine configuration for this command centre, not
a personal document, so it sits with the rest of that configuration. `_my_resources/` is his
personal area and stays untouched.

## Task Checklist

- [x] Confirm the file is genuinely untracked and not ignored
  - `git check-ignore -v .claude/output-styles/BLUF.md` returns nothing, and it showed as `??` in
    `git status`. It is a real file, 1386 bytes — not one of the `?? .claude/*` sandbox bind mounts
    that are `/dev/null` character devices.
- [x] Read the whole file before committing it
- [x] Copy it into the lane byte-identically (`diff -q` clean) rather than retyping it
- [x] Run the enforcement suite so a new file under `.claude/` cannot break a gate

## Evidence

| Row | Acceptance | Evidence |
|---|---|---|
| A1 | The tracked copy is the working copy | `diff -q` between the lobby's file and the lane's is silent; `git show` of the committed blob matches |
| A2 | The lane changes exactly one file | `git show --stat` — one file, one addition, no deletions anywhere |
| A3 | Nothing in the repo's own gates regresses | the enforcement suite below |

## Suite Ledger

| Scope | Command | Result | Why this run |
|---|---|---|---|
| enforcement suite, first run | `python3 .agents/scripts/tests/run_all.py` | **79/80 — `test_check_maps.py` FAILED** | The lobby's machine floor. It caught a real omission of mine, not a flake: `F2 the live _artifacts tree reports no MISSING rows`, because this session folder had no row in `_artifacts/_main/INDEX.md` |
| the drift itself | `python3 .agents/scripts/check_maps.py` | exactly one row named: `_artifacts/_main/INDEX.md: missing row for 2026-09-06_scc-419-bugs-cycle-12/` | Confirming the failure was mine and bounded, rather than the known maps-journal cache drift the session banner warns about |
| enforcement suite, after the row | `python3 .agents/scripts/tests/run_all.py` | **80/80 files passed** (`33/33` in the final group) | Certification at the shipping state |

## Your Actions

- [ ] The merge itself — lands via this branch's PR
