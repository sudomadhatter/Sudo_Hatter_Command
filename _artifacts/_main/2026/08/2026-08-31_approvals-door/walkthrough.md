# SCC-354 — `/smh-llm-approvals`, the approvals audit door (Part A of SCC-352)

review-runtime: fan-out

**Lane:** `chore/SCC-354-approvals-door`, cut from `origin/main` at `8af1f134`
**Plan:** [implementation_plan.md](implementation_plan.md) — two self-audit passes, verdict **GO**
**Approved:** the operator's literal `approved`, 2026-08-31
**Scope cut:** the operator's ruling, 2026-08-31, after the review — see *What got cut* below

## What this is, in one paragraph

The operator types `/smh-llm-approvals`. The agent reads his recent Claude Code sessions and Zoo
Code threads, finds every terminal command that stopped and waited for his approval, and shows them
in chat as one list. He names the ones he wants allowed. The agent adds those rows to
`.claude/settings.json` and `.vscode/settings.json` and runs the Zoo apply so Zoo actually sees
them. He never opens a terminal, never edits a settings file, and is asked exactly one question.

## What got cut, and why — the lane's actual lesson

This first shipped as a 368-line Python script the operator ran in a terminal, whose job was to
**compute** the minimal allow-list row for each blocked command: a token-boundary breadth floor, a
replay through the real Zoo matcher, a merge into one row per family, and a paste-ready hand-off
block for Claude. 2,274 lines across 29 files, with a 406-line test file and a 13-mutant sweep.

Five review lenses and one live run against the operator's real lists found the same disease from
four directions:

| What it did | Reproduced |
| --- | --- |
| Proposed rows that beat the deny fence | `sudo rm -f /etc/x` → row `sudo rm` → `sudo rm -rf /` becomes `auto_approve`. Longest-prefix-wins means a row built from the whole command outranks the short deny row that caught it. |
| Lost the fence entirely on a fresh machine | Denies never seed into `globalState`, so `live_lists()` returned `deny=[]` and the door proposed bare `rm` and `sudo`. |
| Widened a careful list | Emitted `Bash(git *)` into a `.claude/settings.json` whose 41 git rules are subcommand-scoped on purpose and which omits `git reset`, `git clean` and `git push --force`. |
| Dropped the house's own idiom | `cd <abs> && <tool>` got no proposal at all and vanished silently, because candidate rows were prefixes of the whole string while the matcher evaluates per piece. |

Two more defects were found only by RUNNING it, not reading it: a rule built from a shell variable
assignment (`Bash(W=/Users/…; *)`), and `Bash(1 *)` from the `1` in `2>&1`. And a lens proved
`test_the_door_writes_nothing` vacuous by making `render()` write to the real tracked settings file
while the suite still printed 22/22.

**Every one of those lived in the computing, and the operator never asked for the computing.** His
words: *"all i asked for is a / command that gives me the terminal commands I had to approve."*

So the proposer, its test file, the extracted matcher, the JSONL fixture and the mutation sweep were
deleted, and `zoo_notify.py` / `test_zoo_permissions.py` / `test_zoo_notify.py` / `scripts/INDEX.md`
were restored to `origin/main`. What ships is **one command file** the agent follows, plus the five
generated launchers that put it in each platform's menu.

The guard that replaced the breadth floor is a sentence, not an algorithm: **a row is only ever as
wide as the command it came from.** `git fetch origin main` earns `Bash(git fetch *)`, never
`Bash(git *)`. The operator reads real commands and picks; nothing computes breadth on his behalf.

## Task Checklist

- [x] **The door** — [.agents/commands/smh-llm-approvals.md](../../../.agents/commands/smh-llm-approvals.md),
      four steps: read both stores, show the list, stop for his word, write both files and apply.
- [x] **Five launchers regenerated** by `sync-agents.ps1 -NoGlobals` from the new body — never
      hand-written. `.claude/skills/`, `.agents/skills/`, `.opencode/commands/`, `.roo/commands/`,
      `.agents/workflows/`.
- [x] **The proposer deleted** — `llm_approvals.py`, `zoo_matcher.py`, `test_llm_approvals.py`,
      `claude_session_sample.jsonl`, `sweep.json`.
- [x] **Four files restored to `origin/main`** — `zoo_notify.py`, `test_zoo_permissions.py`,
      `test_zoo_notify.py`, `.agents/scripts/INDEX.md`.
- [x] **Docs rewritten to match** — SOP start-here row, SOP `#### /smh-llm-approvals` section, SOP
      family table, changelog, both migration guides, `commands/INDEX.md`, `_main/INDEX.md`.
- [x] **`test_twin_parity.py` NOT_PAIRED row** kept — the command still exists and is still
      per-machine, so it still has no `cicd-*` twin.

## What is verified, and what is not

The reading half was proved live before the cut, and the shapes it reads are unchanged — the
command file carries the same two record shapes the script parsed. Run against the operator's real
machine it found 11 refused Claude commands by pairing each `tool_result` refusal back to its
`tool_use` by id, and found the Zoo store root correctly (`…/zoocodeorganization.zoo-code/tasks`,
genuinely empty on this Mac — Zoo has no thread history here).

**Not verified:** the door has not been run end-to-end as a command since the rewrite, because
running it means editing the operator's live settings files, which needs his word per Step 2. That
is the next thing to do and it is his call to trigger.

## Your Actions

- [x] **DECISION — run `/smh-llm-approvals` once, live. DONE 2026-09-01** — the acceptance test
      passed. Operator, verbatim: **"This check off the last of my task the / command works"**.
      The run read 18 Claude sessions and 5 Zoo threads, listed what had been approved, and stopped
      for his word before touching a file, exactly as designed. He answered "all of them", then
      narrowed it mid-run — verbatim: "only for claude though I a fixed zoo" — so Zoo's lists were
      left untouched and five rows were added to `.claude/settings.json` at `af84a549`. Three
      commands were deliberately NOT added despite "all of them", each named in the commit body:
      `git restore .` (discards the working tree), `git -C <path> merge` (the first mutation through
      `-C`, which is what `nothing-guards-the-merge-target` exists to stop), and `python - <<'PY'`
      (arbitrary code from a heredoc — no prefix narrower than "run any python").
- [x] The merge itself — lands via this branch's PR.

**What the live run exposed about the door itself, and its fix.** Step 1's Claude scan pairs only
the operator-refusal phrase (`doesn't want to proceed with this tool use`) and therefore misses
auto-mode classifier denials entirely — **9 refusals versus 35 classifier denials in the same 20
sessions**, worth 8 additional unique commands. Three of the five rows actually added came from that
missed set, so the gap is not cosmetic: the door under-reports its own subject by roughly four to
one. The fix is one more phrase in the Step 1 pairing. The scan was widened by hand for this run and
the gap recorded in the sweep's walkthrough
([SCC-338](../../../2026-09-01_SCC-338-pc-pickup/walkthrough.md)).
