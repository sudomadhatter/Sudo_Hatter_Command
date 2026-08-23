<!-- SCC-297 · chore/SCC-297-memory-symlink-sandbox-note · Sudo_Hatter_Command -->

# SCC-297 — the memory symlink wrote into `main` again, four hours after SCC-296 closed that exact trap

**Bottom line: I hit the failure whose walkthrough I had just read.** SCC-296 landed at 01:44 for
one reason — `~/.claude/projects/<slug>/memory` is a per-machine **symlink into the MAIN working
tree**, so a memory written from anywhere lands dirty in the shared checkout where no PR can reach
it. At 01:55 I wrote a memory, and it landed in exactly that place.

This is a **lightweight lane**: ticket → edit → push. No worktree, no plan, no review fan-out.

## What is being landed

| File | |
|---|---|
| `_artifacts/_memory/sandbox-is-the-approval-fatigue-fix.md` | new |
| `_artifacts/_memory/MEMORY.md` | one index line |

**Both are this session's own work**, which is what decides their treatment: AGENTS.md §7 splits
by **AUTHORSHIP**, not tidiness. Another session's memory is parked or left. Mine rides a lane.

## Why the content could not simply be dropped

`.claude/settings.local.json` is **gitignored**, so the sandbox configuration and every lesson
learned against it are recorded **nowhere in the repo**. The memory store is the only place that
survives, and it is read by every platform on both machines.

What it records, from SCC-287's measurement:

| | auto-approved of 929 Bash calls |
|---|---|
| settings rules + `allow-scratchpad.py` | 150 (16%) |
| **+ the best hook that can be written** | 340 (36%) |
| **still prompting** | **588** |
| **under `sandbox.enabled`** | **all of them** |

⭐ **No hook can do better, and the reason is structural:** `Bash(...)` rules match by **prefix over
the whole command string**, so no rule can ever match a command containing a pipe. Plus the four
things that break under the sandbox, every one hit live during the SCC-285 and SCC-287 close-outs:
`gh` fails TLS as a Go CLI · a sandboxed parent **cages its children** · writes into `.claude/` and
`.git/` are refused while `filesystem.allowWrite` does not appear to take effect · and a **refused
redirect makes a green gate report a failing exit code**.

## The ordering lesson — the part actually worth keeping

⛔ **Write the memory BEFORE close-out, on the lane, so it rides that lane's PR.** Writing it
afterwards is what mints tickets like this one. SCC-296's remedy — AGENTS.md §7's four steps —
assumes the lane is still **open**; SCC-287 was merged, Done, and its branch deleted, so there was
no lane left to put it on.

⚠ **Nothing mechanical will catch this.** `task_preflight.py`'s `sync` check reads the **worktree**,
and the dirty file is one directory up in a tree the preflight never looks at. On this lane there is
no worktree at all, so the check happens to see it — that is luck, not coverage.

## Gates

| Gate | Result |
|---|---|
| `workflow_lint.py --toolkit-only` | see `gates/lint.json` |
| `check_links.py --base origin/main` | see `gates/links.json` |
| `run_all.py` | see `gates/suite.json` |

Doc-only diff — two markdown files under `_artifacts/_memory/` plus this lane's own artifacts.
No code path changes. Gates run **bare**.

⛔ **No review verdict.** A lightweight lane does not run one, so the full gate runs and the PR
passes on the **preflight receipt** (`main_write_gate.py:213`).

## Your Actions

Nothing is owed. The merge click is the ceremony's.
