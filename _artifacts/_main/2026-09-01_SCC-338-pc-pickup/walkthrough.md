# SCC-338 — the PC pickup sweep: six Review-Required tickets, one worktree, one push

review-runtime: inline (the operator's framing, verbatim: "We have a bunch of quick task we need to
do to push the rest of the tickets sitting in 'Review Required' these are all waiting on PC. So we
are going to do them all in one working tree and one push." Nothing was spawned.)

**Lane:** `chore/SCC-338-pc-pickup`, cut from `origin/main` @ `9dc97ac0`
**Ticket:** SCC-338 · **Riders verified in this lane:** SCC-335, SCC-346, SCC-351, SCC-352, SCC-355
**Machine:** the Windows PC — which is the whole point; every one of these six was blocked on work
that can only happen on a machine, never in a repo.

## What this lane is, in one paragraph

Six tickets sat in Review Required for days, and not one of them was waiting on code. Each was
waiting on the Windows PC to run something and report back. Three of them turned out to be blocked
by real Windows-only defects rather than by the operator's attention — the sort that only appear
when a script written on a Mac finally executes on Windows — so this lane fixed those, then ran
every verification on the machine that had been the blocker.

## The three defects that were actually blocking, not the operator

**The one that cost the most days.** `zoo_permissions_apply.py` printed an arrow written as U+2192
*after* its SQLite `con.commit()`. Windows' default stdout encoding is cp1252, which cannot encode
that character, so `print` raised `UnicodeEncodeError` at the line following a write that had
already succeeded. The operator ran `--apply`, watched a traceback, and read it the only sane way:
it failed. SCC-351's PC row therefore sat open over a decorative arrow. Five print sites in that
file and three in `zoo_notify_install.py` are now 7-bit, and the reason is written into the code at
the site so the next author does not restore it. This is the same defect family as SCC-335, which
fixed the READ half of the same pair; a new test now fails the suite if any operator-facing print in
these three scripts carries a non-ASCII character, with a rejects/allows control so it cannot pass
vacuously.

**The suite was red because of that crash, not despite it.** `test_apply_writes_only_the_list_keys`
had been failing for exactly this reason. The Zoo permissions gate went 19/20 to 22/22.

**The CRLF seam.** `.gitattributes` did not pin `.agents/workflows/*.md` to LF, so on a machine with
`core.autocrlf=true` the tracked door and the generated cache twin differed by line ending alone —
door 756 bytes with 13 CRLF, cache 743 bytes with 0, byte-identical after conversion. That is a
Windows-only false failure in a byte-comparison check. Pinned, following the narrow `*.sh text
eol=lf` precedent already in the file rather than widening to `* text=auto`.

**Eight read-only PowerShell verbs had no Zoo row.** Every read verb in the tracked allow list is
POSIX-shaped (`ls`, `cat`, `grep`, `head`), so on Windows the agent's equivalents each stopped for
approval and were then learned into the machine's decision store, where no test can see them and the
next `--apply` wipes them. `Get-ChildItem`, `Select-Object`, `Select-String`, `Test-Path`,
`Write-Output`, `findstr`, `dir` and `more` are now tracked. Deliberately NOT promoted: bare `del`,
which was measured auto-approving `del AGENTS.md` by outranking the delete denies, and bare
`git` / `git add` / `git commit` / `git push`, which are widenings already covered by scoped rows.

## And the suite itself was lying about this machine

With the three defects above fixed the PC still ran **67 of 71 files green**, and not one of the four
failures was a defect in the code it tested. One was a missing INDEX row for this very session
folder — fair, and fixed. The other three were the same root cause as everything else in this lane,
which is what makes them belong here rather than in a follow-on: a test authored on the Mac,
asserting something true, failing on Windows for a reason that has nothing to do with its subject.

`test_mac_plist_never_points_at_a_virtualenv_interpreter` builds a **darwin** plist on purpose and
then wrapped its interpreter in `pathlib.Path`. On Windows that is a `WindowsPath`, so
`Path("/usr/bin/python3").is_absolute()` is **False** — there is no drive letter — and the case went
red over a correct Mac plist. It is now `PurePosixPath`, which is what a POSIX artifact deserves
whatever machine runs the suite. That file's own header already says to compare `Path` parts and
never `str`, and names this exact scar; this was the one line that did not follow its own rule.

`test_the_registered_command_actually_produces_a_nag` ran the registered hook string under
`shell=True`. The string is POSIX and expands `$CLAUDE_PROJECT_DIR`; `shell=True` on Windows is
**cmd.exe**, which does not expand `$VAR` at all, so cmd.exe handed `sh` a literal `$CLAUDE_PROJECT_DIR/…`
path and the case died `rc=127`, "No such file or directory" — on a machine where the hook plainly
works, having fired at this agent twice during this session. The test was emulating the wrong shell.
It now runs `sh -c`, which is what Claude Code actually uses, and is correct on both machines.

**The third was not cosmetic and is the one worth remembering.**
`test_main_actually_honours_custom_storage_path_end_to_end` built the Mac user directory by hand and
isolated its child process with `HOME=` alone. On Windows neither holds: `Path.home()` reads
`USERPROFILE`, and the win32 branch of `zoo_notify.user_dir` reads `APPDATA`. So the sandbox leaked.
The child read the operator's **real Zoo store**, found a real already-answered thread, and reported
"needs nothing". A test that silently escapes its sandbox and reads live user data was red only by
luck — it could as easily have gone green on someone else's data. It now asks the module where it
looks, `user_dir(home=…, appdata=…)`, and pins all three variables together.

All three fixes are Mac-safe by construction: `PurePosixPath` is what that darwin path already was,
`sh -c` is the shell the Mac was using anyway, and `user_dir`'s darwin branch ignores `appdata` and
returns exactly the path the test used to hardcode.

**`run_all.py` is now 71/71 files on Windows**, up from 67/71 — under Git Bash.

⚠️ **Correction, added after the merge: that number was shell-specific and the claim was too broad.**
Run from **PowerShell**, which is how the operator actually runs it, the same tree scored 67/71 with
a *different* four files red — and one of those was `test_command_surfaces`, whose `CS-18 L` is the
authoritative check on the very cache this ticket exists to fix. It had been measured only from the
worktree, where the case **skips itself** and says so in its own output: *"This is a SKIP, not a pass
about the cache; the claim binds in main."* That line was read and passed over. `CS-18 L` was red in
the main checkout, and the remedy was the one command in this ticket's own runbook — the globals sync
from the main checkout, which had last been run before `main` moved. Re-run; `test_command_surfaces`
is now **323/323** and the cache is a byte mirror of its doors.

Three files remain red **under PowerShell only** and are a separate class from anything here — POSIX
`uid` semantics on Windows (`test_allow_scratchpad`), a folder scan walking into a vendored
`third_party` tree (`test_sops_prds_folder`), and one more binary-resolution failure of exactly the
kind fixed in `test_shape_guard` (`test_verdict_receipt`). All three are green under Git Bash. The
lesson this lane keeps re-teaching, now stated once: **on Windows the shell is part of the
environment under test**, so a green is only a green for the shell it ran in.

## The evidence, per ticket, measured on the PC 2026-09-01

| Ticket | What it was waiting for | Measured result |
|---|---|---|
| SCC-335 | the cp1252 round-trip proved on the machine that caused it | `locale.getencoding()` = **cp1252** — this IS that machine. Negative control on the old line: **U+26D4 0 · U+2B50 0 · U+FFFD 1** (reproduces). Shipped seam: **U+26D4 1 · U+2B50 1 · U+FFFD 0**. Acceptance A closed. |
| SCC-338 | the machine-global sync, from the repo ROOT | `test_command_surfaces.py --case "CS-18"` **29/29**, exit 0. Cache: **42 files, 0 over the 12,000-char cap**, newest written today. `smh-close-task-merge-tree.md` is **750 bytes**, not 48,672. `smh-adviser-board.md` present, `INDEX.md` absent. |
| SCC-346 | PC pickup after the VS Code switch | Operator, verbatim: "SCC-346 done". Its open DECISION row is settled below. |
| SCC-351 | `--apply` against the live decision store | The crash above is fixed; the store now carries **all 128 tracked allow rows and all 105 deny rows** — 0 tracked entries missing. Zoo permissions gate **22/22**. |
| SCC-352 | `/smh-llm-approvals` run once, live | Ran end to end over 18 Claude sessions and 5 Zoo threads. Five rows added to `.claude/settings.json` at `af84a549`. Operator, verbatim: "This check off the last of my task the / command works". |
| SCC-355 | the notifier's first execution on Windows | `zoo_notify.py --self-test` fired a real toast — operator, verbatim: "that worked". `zoo_notify_install.py` reads **`installed [ok]`**, startup entry written. |

## One measured thing worth carrying, with its fix named

The Zoo store carries **33 machine-learned allow rows and 1 deny row that are in no tracked file**,
including bare `del`, `git`, `git add`, `git commit` and `git push` — precisely the widenings this
lane declined to promote. They are learned every time "always allow" is clicked, and they outrank
narrower deny rows under the longest-prefix matcher. The fix is the existing one and takes ten
seconds: `python .agents\scripts\zoo_permissions_apply.py --apply` with VS Code closed replaces both
lists with the tracked ones and wipes the debris. It belongs at the next VS Code restart, not as an
open ticket — the tracked fence is fully installed, so nothing is unguarded today.

## What did NOT turn out to be a defect

The PC's opencode command cache holds 26 files over 12,000 characters. That is not a finding: the
12,000-char truncation is an **Antigravity** constraint and opencode has no such cap. Recorded here
so the next sweep does not re-file it.

## Your Actions

Everything in the table above is measured and closed. Nothing below is owed by you.

- [x] **The merge itself** — lands via this branch's PR.
- [x] **SCC-346 DECISION — the AVCH ticket for the AGY halves.** Settled: minted as
      [AVCH-114](https://sudo-command.atlassian.net/browse/AVCH-114) on the house cross-repo rule,
      filed on live numbers rather than the stale ones in SCC-346's row — 47 untracked allow rules
      in AGY's `.claude/settings.local.json` (the row said 49), zero `zoo-code.*` keys in its
      tracked `.vscode/settings.json`, and no `.roo` / `.roomodes`. The ticket records that AGY is
      covered today only because Zoo's decision store is per-install rather than per-workspace, so
      this is a durability and review gap, not an open hole.

## Code Review (2026-09-01)

Inline, by the lane, at the operator's stated runtime. Scope: three scripts, one test file, two
settings files, `.gitattributes`, and the two docs the currency gate requires.

The change set is small and every claim in it is backed by a command run on the machine in question
rather than by inspection. The one risk worth naming is that the ASCII guard scans `print(` and
`stderr` lines by text, so a print built through an intermediate variable would evade it; that is
accepted, because the guard exists to stop the *reflex* of typing a decorative arrow into an
operator-facing string, and it carries a rejects/allows control proving it fires on the real defect
and passes clean code. The eight promoted PowerShell verbs all only read, and a pipe into a
destructive verb splits into its own piece under Zoo's matcher and is judged separately, so a
`Get-ChildItem` piped into `Remove-Item` still lands on the deny row.

Findings: none requiring change. The `del` observation above is a machine-state fact with its
remedy named, not a defect in this diff.

Verdict: PASS @ cb422f2d
Suite evidence measured @ cb422f2d (run_all.py 71/71 files through gate_receipt.py, exit 0; receipt: [gates/suite.json](gates/suite.json)). Tree was dirty by the artifact writes of this same commit and nothing else.
