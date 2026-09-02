# SCC-375 — Claude Code stops on the PC, and why no allow rule was going to fix it

Lane: `chore/SCC-375-claude-msys-path` · PR [#137](https://github.com/sudomadhatter/Sudo_Hatter_Command/pull/137)
Ticket: [SCC-375](https://sudo-command.atlassian.net/browse/SCC-375), Part B under the SCC-373 rolling ticket.

## What this lane actually did

The operator's complaint was that Claude Code interrupts him constantly on the PC while Zoo Code
sits at roughly 10%, and that the cause is "the working tree and the compound requests." Both halves
of that turned out to be right, and the reason they are right is a platform fact rather than a
missing rule.

**Claude Code has two independent ways not to interrupt you.** One is the allow list, which is
string rules matched against commands and works everywhere. The other is the **sandbox**, where the
operating system fences what a command may touch so the prompt is skipped entirely, whatever shape
the command has. The sandbox is built on macOS Seatbelt and Linux seccomp, and the vendor documents
it plainly: *"The sandbox is built into Claude Code and runs on macOS, Linux, and WSL2. Native
Windows is not supported."* The operator's `settings.local.json` sets
`sandbox.enabled: true` and `autoAllowBashIfSandboxed: true` — on the Mac that carries the load, and
on this PC it does nothing at all. So on Windows the allow list is the only thing between the
operator and a prompt, which is why the same config feels fine on one machine and hostile on the
other.

That reframes the work: the allow list has to be actually correct on Windows, and it was not.

## What closed, item by item

**1 · The chain hook could not read Git Bash's own path spelling.**
`allow-readonly-chain.py` knew `C:\ws` and `C:/ws` and not `/c/ws` — the spelling Git Bash produces
and hands back from `pwd`, and therefore the one agents type. `_is_abs` accepted it (it starts with
`/`), so it reached the containment test unrewritten and was compared against a root of `c:/ws`.
Never equal, so **every `cd /c/<repo> && …` chain fell through to a prompt** — 114 calls, 7.0% of
every stop. Fourth instance of this bug in the house after SCC-321 and SCC-171/172. It fails safe,
which is why it survived: every fixture spells the root `C:/…`.

**2 · Twenty allow rules could never match anything.**
Claude Code documents `Bash(X:*)` as equivalent to `Bash(X *)` — *"the space before a trailing `*`
is part of the rule"* — so a prefix ending in punctuation demands a space the real command never
has. Measured against 22,385 subcommands drawn from 18 transcripts:

| rule | matched | respelled `X*` |
|---|---|---|
| `Bash(python .agents/scripts/:*)` | **0** | 199 |
| `Bash(git push -u origin chore/:*)` | **0** | 18 |
| `Bash(backend/.venv/Scripts/:*)` | **0** | 12 |
| `Bash(git push origin claude/:*)` | **0** | 3 |
| `Bash(git push -u origin claude/:*)` | **0** | 2 |
| `Bash(git push origin chore/:*)` | **0** | 1 |

13 rules respelled plus their Mac/POSIX twins, and 7 assignment rules un-anchored: `Bash(REPO=/*)`
and six siblings required the value to begin with `/`, true on the Mac and false on Windows where
the doors print `REPO=c:/…`. This is why the untracked `settings.local.json` had accumulated broad
hand-approved `Bash(python:*)` and `Bash(git:*)` for verbs the tracked file already believed it
covered — the narrow rule never fired, so the operator approved the broad one.

**3 · The `VAR=` vocabulary was half of Zoo's.**
Zoo allowlists 35 bare assignment names; Claude's tracked settings allowlisted 14. The doors print
`TREE=<path>` and `WT=<path>` as their **own subcommand** — that is the worktree pin the operator
named — and neither had a rule. 918 prompting subcommands (7.7%) were a bare `VAR=` with no rule,
led by `TREE=` (111) and `WT=` (59). Added `TREE=`, `WT=` and the 21 names Zoo carried and Claude
did not, so the two platforms now read the same.

**4 · Six scripts crashed instead of printing, which is what created the `PYTHONIOENCODING=` habit.**
Windows consoles default to cp1252 and cannot encode the house's own output markers.
`memory_store_check.py` was measured dying mid-run on a `post-checkout` hook, so its regression
warning could never reach the operator. That crash is why agents learned to prefix calls with
`PYTHONIOENCODING=utf-8`, and that prefix became the largest remaining family of stops (136) with no
allow rule. **The prefix must not be allowlisted** — a rule for it would match
`PYTHONIOENCODING=utf-8 <anything>` as one subcommand and launder past every verb rule, the same
call already made against Zoo's `if exist ` and `ForEach-Object` in SCC-374. So the fix went into
the scripts: the guard is the first statement of `main()` in `label_tasks`,
`link-worktree-assets`, `main_write_gate`, `memory_store_check`, `shape_scan` and `vscode_sync`.

**5 · The suite was pinning the broken spelling.**
`test_settings_allowlist` A2 named `Bash(python3 .agents/scripts/:*)` as a sentinel, so the gate was
green while that rule approved nothing — the class `tests-must-gate-for-real` §5 calls worse than no
gate, because the green is read as evidence. Corrected, and a new case **A2b** fails on any rule
using `X:*` after a path separator so the bug cannot return.

## Evidence

- `test_allow_readonly_chain.py` — new block R **red first** (3 of 7 failing, the three ALLOW cases),
  full file **156/156** after.
- `test_settings_allowlist.py` — **28/28** including the new A2b.
- Re-measured with the hook as its own oracle over 18 transcripts: prompting subcommands
  **11,883 → 11,675**; assignment stops **918 → 705**; the `/c/` fix moved 75.2% → 72.4% on the
  earlier (over-stated) model.
- Encoding proof on this console: `python -c "print('⛔ …')"` raises `UnicodeEncodeError`; the same
  print after `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` succeeds.
- CI `main-write-gate` **success on the PR head `b043ea69`**; PR `MERGEABLE / CLEAN`, 0 behind main.

## Corrections made in-flight, recorded because they changed the operator's picture

Two of my own claims did not survive measurement and were withdrawn rather than quietly dropped.
I first reported a **75% prompt rate**, built on this hook's docstring claim that a settings rule
prefix-matches the whole command string so nothing containing a pipe can match. The vendor docs say
the opposite — *"A rule must match each subcommand independently"* — and there is a built-in
read-only set (`ls`, `cat`, `grep`, `find`, `git` reads, `cd`) that never prompts in any mode. The
docstring is stale and the number was inflated. I also theorised that project work fails because
paths take "a different route"; measurement showed routed subcommands are **better** covered
(69.7%) than average (46.9%), because the work is driven from the lobby. Both are recorded here
because the first version of each was told to the operator.

## Acceptance

- [x] `cd /c/<repo> && <read>` chains auto-allow; `/c/Windows`, `/d/…` and a bare drive root still refuse.
- [x] No tracked rule uses the dead `X:*` spelling, enforced by A2b.
- [x] Claude's `VAR=` vocabulary is a superset of Zoo's (39 vs 35; "in Zoo but not Claude" is empty).
- [x] The six scripts run bare with no `PYTHONIOENCODING=` prefix.
- [x] Full enforcement suite: the only file I broke (`test_settings_allowlist`) is fixed; the three
      still red are pre-existing and unrelated — `test_allow_scratchpad` (uid test),
      `test_mutation_sweep` (passes standalone 40/40), `test_sops_prds_folder` (Windows long path
      inside torch site-packages, the known `rglob-sweeps-must-prune-the-walk` issue).

## Your Actions

- [ ] **Merge PR [#137](https://github.com/sudomadhatter/Sudo_Hatter_Command/pull/137)**, then switch to `main` and pull — the rules are read from disk, so
      an unpulled merge changes nothing locally. AGY hit exactly this: #60 was merged while the old
      13-rule file was still on disk.
- [ ] **Decide on the two untracked files this lane did not create** —
      `.vscode/settings.json.bak-llm-approvals` (the backup the approvals skill wrote; safe to delete
      now that SCC-374 is merged) and `scratch/mutation_sweep_24_7.py`. The close-out preflight
      counts them as uncommitted and will keep saying so.
- [ ] **Decide on the 8 dirty files under `_artifacts/_memory/`** — 5 deletions and MEMORY.md edits
      that were already in the tree when this session started. They belong to another session, so
      this lane must not sweep, delete or commit them; the preflight blocks until they are committed
      under their own key or parked.
- [ ] **The WSL question, if you ever want the sandbox on the PC.** Ubuntu/WSL2 is already installed
      and the repo is reachable at `/mnt/c/Sudo_Hatter_Command`, but `node` is not installed there
      and `claude` resolves to the Windows binary leaking through `PATH`. My recommendation is
      **don't** — the toolkit is Windows-shaped (`acli` in the Windows credential store,
      `.venv/Scripts/*.exe`, the git hooks) and `/mnt/c` is slow. Recorded so the option is not lost.

## Out of scope, named not dropped

- `PYTHONIOENCODING=` / `PYTHONUTF8=` as **allow rules** — refused on purpose (item 4). The script
  guard removes the need; any script still printing markers without the guard should get one.
- AGY's own permission vocabulary shipped separately as
  [AVCH-115](https://sudo-command.atlassian.net/browse/AVCH-115) / PR #60 (merged): 13 allow rules → 171, plus a 24-row deny floor it did not have.

## Code Review (2026-09-01)

Reviewed against the diff on `b043ea69`. The one finding that mattered was self-inflicted and is
fixed in-lane: the respell in commit `4dfd5448` broke `test_settings_allowlist` A2, CI went red at
03:00 and 03:12 with `70/71 files passed FAILED: test_settings_allowlist.py`, and commit `8f9440f5`
corrected the sentinel and added A2b so the dead spelling cannot return. No finding was deferred and
none was carried out of the lane.

The suite receipt for this lane records **`fail` (exit 1, 174.4s @ b043ea69)**, and the verdict below
says CONCERNS rather than PASS because of it. The red is **not this lane's diff** — it is three files
that were already red before the first commit here, verified by re-running them with this lane's
script edits stashed:

| file | why it is red | this lane's diff |
|---|---|---|
| `test_allow_scratchpad.py` | `E · uid is read from the PROCESS` — a uid-grant fixture | untouched |
| `test_mutation_sweep.py` | `K3c SIGKILL leaves residue` — passes **40/40 standalone**, red only under full-suite contention | untouched |
| `test_sops_prds_folder.py` | `WinError 3` on a 260-char path inside `torch-2.13.0.dist-info` in an AGY worktree's `.venv` — the known `rglob-sweeps-must-prune-the-walk` defect | untouched |

The one file this lane *did* break, `test_settings_allowlist.py`, is fixed and green at 28/28. I am
not claiming a green suite, and I did not fix the three above: each is a separate subject with its
own cause, and `rglob-sweeps-must-prune-the-walk` in particular needs the walk pruned with `os.walk`
rather than filtered after the fact. They are named here so the red is attributable rather than
ambient.

**No `Verdict:` stamp is written here on purpose.** The SCC-363 gate is right that a verdict cannot
stand on a suite that did not pass, and the suite receipt records `fail`. Stamping one behind
`[verdict-ok]` would log a bypass for reds this lane did not cause, so the stamp is simply withheld
until the suite is green. The PR itself is unaffected: `main-write-gate` is green on `b043ea69`.
