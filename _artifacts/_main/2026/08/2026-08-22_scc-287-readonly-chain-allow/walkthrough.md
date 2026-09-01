<!-- SCC-287 · chore/SCC-287-readonly-chain-allow · Sudo_Hatter_Command -->

# SCC-287 — a second allow SHAPE for the approval-fatigue problem, and the day it stopped being the fix

**Bottom line: this hook works, is measured, and is NOT the answer to the ticket's actual
complaint.** It removes 190 approval prompts from a 929-call session. It leaves **588**. Mid-lane
the operator said so in plain words — *"you are not fixing the problem you are making patches"* —
and the search that followed found the real mechanism: **Claude Code's built-in OS sandbox**, which
auto-allows every one of those 588. The sandbox is on now. This lane ships anyway, for one honest
reason stated in full below: **the sandbox does not exist on native Windows, and half this system
is a PC.**

## What this was

`allow-scratchpad.py` refuses **any** shell metacharacter, and that strictness was bought with pain
— the SCC-263 review reproduced fourteen escapes in the deny-list version it replaced, and the
ruling was that *the parser is the security boundary, and a regex is not a shell parser*. The ask
was never to relax it. It was to add a **second allow-list of SHAPES** beside the first:

| | shape |
|---|---|
| **1 (existing)** | one simple command, no metacharacters, inside the session scratchpad — already permits **writes and deletes** |
| **2 (this lane)** | a pipeline or chain whose **every atom** is something the operator already allows on its own — read-only verbs only, no redirect, no heredoc, no subshell, no backtick, no `$`, no substitution of any kind |

⭐ **Shape 2 grants strictly LESS authority than shape 1.** It cannot write, cannot delete, and
cannot reach outside what `settings.local.json` already says yes to. It is an *unlocker*, not a
grant: an atom that is not already permitted refuses the **whole chain**.

## The pivot — and why it is in this document rather than a footnote

The lane was building the hook when the operator rejected the approach. That was correct, and the
count proves it rather than merely agreeing with it:

| | auto-approved | share of 929 |
|---|---|---|
| **BEFORE** — settings prefix rules + `allow-scratchpad.py` | 150 | 16% |
| **AFTER** — the above + `allow-readonly-chain.py` | 340 | **36%** |
| **prompts removed** | **190** | |
| **still prompting** | **588** | 64% |

Why the 588 still prompt, by first cause: **216 redirect · 149 heredoc · 115 other excluded
character (glob, brace, `~`, `!`) · 72 expansion or substitution · 36 a verb or flag not on the
list.** Every one of those is a *shape* nobody can safely allow-list, which is exactly the operator's
point: a longer list is a longer list, not an architecture.

⭐ **THE ROOT CAUSE IS ARCHITECTURAL AND NO HOOK CAN REACH IT.** `Bash(...)` rules match by **prefix
over the whole command string**, so no rule can ever match a string containing a pipe — the 81 rules
in `settings.local.json` never get a chance. The only other layer is a `PreToolUse` hook. That is
the entire permission surface; a hook is the ceiling, not a step toward one.

**The real fix — the OS sandbox.** `sandbox.enabled` + `autoAllowBashIfSandboxed` (which defaults
to true) runs Bash under macOS Seatbelt and auto-allows it, because the *cage*, not the *string*,
is now the boundary. It is live on this Mac. Its own frictions were found and fixed during SCC-285's
close-out and are recorded there — Go CLIs (`gh`) fail TLS under Seatbelt, a sandboxed parent cages
its children, and writes into `.claude/` and `.git/` are refused.

⛔ **What keeps this lane alive: the sandbox has NO native Windows implementation — WSL2 only.** On
the PC this hook is the only relief that exists. That is the whole case for landing it, and if the
PC stops mattering, this file is the argument for deleting the hook.

## Task Checklist

- [x] **RED-first** — the hook refuses each SCC-263 escape re-expressed as a pipeline (comment-hidden
      path, quoted redirect, fd-dup redirect, flag-glued path, backslash-escaped verb, one good `-C`
      licensing a bare `git`)
- [x] **Anti-vacuity** — block A proves the verb list is populated and that an unknown verb anywhere
      refuses the WHOLE chain
- [x] **Re-measure and record the before/after** — the table above; re-run at this HEAD over the
      session's own transcript, not a fixture
- [x] **Non-goal stated** — heredocs stay ineligible. That is an authoring habit, not a config gap:
      write the script to the scratchpad and run it by absolute path.
- [x] Operator's `todo_list.md` note rolled in (`ba59c75`) — where the sandbox settings live, and
      the PC half still owed

## Evidence

**`test_allow_readonly_chain.py` — 150/150, exit 0.** Fifteen blocks, and the ones that carry weight:

| Block | What it pins |
|---|---|
| **A** | anti-vacuity — the verb list is non-empty and an unknown verb kills the chain |
| **D** | separators hidden **inside quotes** are refused, not parsed |
| **F** | flags that turn a read-only verb into a **write** (`git -o`, `--output`) are absent from the allow-list by construction |
| **G4** | a pseudo-flag *scar* — see the second defect below |
| **H** | an interpreter (`python3`, `node`) is never a pipe **SINK** |
| **J / K** | both halves of the condition are load-bearing — remove either and tests fail |
| **L** | the two legal outputs only: `allow` or **SILENCE** |
| **M** | an existing `deny`/`ask` from another layer is honoured, never overridden |
| **P** | `compile_rule`'s separator guard — the first defect below |

**⭐ THE MEASUREMENT FOUND TWO REAL DEFECTS THAT THE TESTS DID NOT.** Both are recorded because both
are the same lesson: a test written from the author's model confirms the model.

1. **The first count said 82% was already covered** — absurd against an operator approving nine in
   ten. Cause: the open end of a compiled prefix rule was `.*`, **which crosses `&&`**, so
   `Bash(git status:*)` "matched" `git status && git checkout main`. The BEFORE model was
   over-crediting the old system and the hook itself carried the same bug. Fixed in both
   (`[^;|&]*`), pinned by block P.
2. **A naive `.split()` invented flags nobody typed** — `--jql 'project = SCC AND created >= -3d'`
   produced a token `-3d'`, and `grep "a -o b" f` read an `-o` flag out of a **search pattern**.
   Fixed with a quote-aware `tokenize()`, pinned by G4.

**Refusal is the default, everywhere.** `SAFE` is a frozenset of permitted characters, not a list of
banned ones; `$`, backtick and backslash are absent from it in every quoting context. Anything the
parser does not positively recognise produces **silence**, which is a no-decision, not an allow.

## Gates

| Gate | Result |
|---|---|
| `test_allow_readonly_chain.py` | **150/150, exit 0** — re-run after `origin/main` was absorbed |
| `run_all.py` | see `gates/suite.json` |
| `workflow_lint.py --toolkit-only` | see `gates/lint.json` |
| `check_links.py --base origin/main` | see `gates/links.json` |
| `check_maps.py --depth3-only --strict` | see below |

⛔ **All gates run bare — no pipe, and no redirect out of the workspace.** A `| tail` reports the
pipe's exit code, not the gate's; and under the sandbox a `> /tmp/…` redirect **fails**, and the
shell reports the redirect's failure as the gate's. SCC-285 hit the second one live.

⛔ **NO REVIEW VERDICT — stated, not implied.** This lane carries no `Verdict: … @ <sha>` line: the
fan-out never ran, because the approach was rejected mid-flight and the work that followed was
research, not review. Three mechanical consequences, all correct behaviour:

- `task_preflight` prints `gate: no review Verdict line…` and **the full gate runs** — nothing is skipped.
- `flight_recorder record` **REFUSES** — it keys its event on the verdict sha, and there is none.
- `main_write_gate --mode pr` passes on the **preflight receipt** instead (`main_write_gate.py:213`).

What is missing is an independent read of this diff. The gates certify it; no second pair of eyes did.

## Landing order

No collision. This lane's four code paths — `.agents/hooks/allow-readonly-chain.py`, its deployed
`.claude/` twin, `.agents/scripts/tests/test_allow_readonly_chain.py`, `.agents/hooks/INDEX.md` —
are touched by no other live lane. `.claude/settings.json` gains one PreToolUse entry; `SCC-288`
and `SCC-296` do not touch it. `origin/main` (`4bd2bd6`) is absorbed at `15560a9`, conflict-free.

## Your Actions

Nothing is owed — the merge click is the ceremony's, not yours.

- **One open question this lane cannot answer: how much do you work on the PC?** The hook's only
  remaining justification is that machine. If the PC moves to WSL2, the sandbox covers it too and
  this hook becomes dead weight worth deleting. Recorded, not decided.
- **`sandbox.filesystem.allowWrite` did not take effect live.** The entries for `.claude/worktrees`
  and `.git` were added during SCC-285's close-out and were still refused; `network.allowedDomains`
  was live immediately. It most likely needs a session restart — unverified.
- **Optional hardening, not started:** `sandbox.credentials` entries for `~/.aws` and `~/.ssh`.
