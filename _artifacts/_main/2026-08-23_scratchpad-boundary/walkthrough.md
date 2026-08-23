# SCC-299 — the escape guard's scratchpad rule matched three levels too shallow

**Lane:** `chore/SCC-299-scratchpad-boundary` · **Repo:** Sudo_Hatter_Command · **Date:** 2026-08-23

## What was broken

`main` was **red**. `4e5e09f` (SCC-299's first landing, merged as PR #66 at 09:59) shipped a new
`is_scratchpad()` in the cwd-escape guard so that a session's scratchpad would stop raising false
permission prompts. The intent was right; the match was not.

The function has two branches. Branch 1 reads a configured `.claude/scratchpad-root` and matches it
correctly — exact equality **or** a `/`-terminated prefix. Branch 2, the built-in POSIX fallback,
did neither:

```python
prefix = f"claude-{getuid()}"
if norm.startswith(f"/private/tmp/{prefix}") or norm.startswith(f"/tmp/{prefix}"):
    return True
```

`/tmp/claude-<uid>` is not a scratchpad. It is the **parent of every session's scratchpad** on this
machine, and it is also where the shell's `TMPDIR` points, so it is where the test harness builds its
fixture repos. Everything underneath it therefore read as *inside the workspace*, and the guard
stopped refusing the escapes it exists to catch — including `cd /tmp/claude-501/other-repo`, a
different git checkout.

Two defects in one line:

1. **Too shallow.** The real scratchpad is `…/claude-<uid>/<project>/<session>/scratchpad`. SCC-299's
   own new positive cases spell it that way; the implementation matched at `claude-<uid>`.
2. **No boundary.** A bare `startswith` makes `/tmp/claude-5011-anything` a hit on `claude-501`.

## Evidence — it was red, and this is not a vacuous green

`test_cwd_escape_hook.py` on `main` @ `391a838`: **46/51**, five failures, all of them controls that
existed before SCC-299 and that SCC-299 broke:

- `M3 control: a tilde path OUTSIDE the workspace is still refused`
- `M3 control: the SAME `cd ..` from the ROOT leaves and is refused`
- `M4 refused: 'cd ..'`
- `M4 refused: 'cd /tmp/claude-501/other-repo && git status'`
- `M4 refused: 'cd /tmp/claude-501/<ws>-sibling && ls'`

⭐ **The first green run was measured and then thrown away.** It ran with the OS sandbox disabled,
which moves `TMPDIR` to `/var/folders/…` — so the fixture paths never sat under `/tmp/claude-<uid>`
and the bug's trigger was absent. That green proved nothing. The recorded result below is the
**sandboxed** run, `TMPDIR=/tmp/claude-501`, the exact condition that produced the red.

## The fix

Branch 2 now requires a `scratchpad` path component under the `claude-<uid>` root and matches on a
`/` boundary — the same two things branch 1 always did.

## Gates

| Gate | Result |
|---|---|
| `tests/test_cwd_escape_hook.py` (sandboxed, `TMPDIR=/tmp/claude-501`) | **51/51, exit 0** — was 46/51 on `main` @ `391a838` |
| `tests/run_all.py` | **59/59 files, exit 0** |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info — exit 0 |
| `check_maps.py --depth3-only --strict` | exit 0 |
| `check_links.py --base origin/main` | clean, exit 0 |

The first suite run was **58/59** — `test_check_maps.py` `F2` caught this lane's own new artifacts
folder with no `_artifacts/_main/INDEX.md` row. The row is in this commit; the check that found it is
the one that now passes.

## No review verdict — said plainly

This lane carries **no `Verdict:` line**, because the multi-lens review never ran: the session
directive in force bars spawning subagents unless the operator asked, and they did not. The
deterministic gates above certify this diff and no second pair of eyes did. `task_preflight.py`
records the same thing (*"no review Verdict line in this task's own walkthrough - the full gate
runs"*) and the full gate ran — nothing was skipped on a verdict's authority. Same shape as SCC-287.

## Decisions

- **The deployed `.claude/hooks/` copy is committed too.** `M7` compares it byte-for-byte against
  `.agents/hooks/`, and the hook that actually runs is the deployed one — a canonical-only fix would
  pass review and change nothing at runtime.
- **Fixed on its own lane, not folded into SCC-298.** SCC-298 was mid-close-out and its review verdict
  is already stamped at a sha; carrying an unrelated regression into it would invalidate that stamp
  and mis-attribute the commit. `main` being red also outranks one lane's landing — anything branching
  off `main` right now inherits it.

## Pitfalls

- **A green measured under different conditions than the red is not a fix.** Disabling the sandbox to
  get a write through also moved `TMPDIR`, which silently removed the bug's precondition. Re-measure
  under the failing condition, always.
- **The OS sandbox denies every write under `.claude/hooks/` and `.claude/skills/`, at any depth.**
  That is Claude Code protecting its own hooks and skills from the agent, and it is not configurable
  from `sandbox.filesystem.allowWrite`. Two consequences the system should know about: any
  `git merge`/`checkout`/`pull` that touches those paths fails with `Operation not permitted`, and
  `/smh-sync-agents` can never write `.claude/skills/` from inside a session.

## Follow-on — filed, not handed over

The `.claude/hooks` + `.claude/skills` sandbox denial is **SCC-300**, under SCC-33, with the probe
results and both observed consequences in its description. It is not this lane's work: nothing in
this repo can lift a platform-level write ban, and this fix does not depend on it.

## Your Actions

- [x] The merge itself — lands via this branch's PR

Nothing else is owed. The follow-on above is filed as SCC-300 and needs no decision from you here.
