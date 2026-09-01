# SCC-369 — Nag the agent, don't rewrite the rule

**Lane:** `chore/SCC-369-shape-nag` · worktree `.claude/worktrees/scc369-shape-nag`
**Plan:** [implementation_plan.md](implementation_plan.md) · **Ticket:** SCC-369 (Task, one consolidated lane)
**Base:** `origin/main` @ `645ea5e7`, absorbed to `e54e0c37` mid-lane

---

## What this lane actually did

`command-shape.md` was a rule that reached every platform and changed nobody's behaviour. It is
summarized in `AGENTS.md` §6, restated in `zoo-team.md` for every Zoo seat, keyworded into
`rule-trigger.py`, and it fired twice as a prompt injection during the very session that measured
it — while that session broke it repeatedly. The measurement is the whole argument: over 25 Claude
sessions and 7,858 Bash calls, **1,933 violations of that one rule, 98.9% of every detectable
violation in the transcripts.** Five copies of the law, and near-total non-compliance.

So this lane stopped writing the rule down and started **nagging** — injecting the correction at
the instant of the mistake, citing the rule file by name so the agent is sent back to the law
rather than handed a sixth restatement of it. That is the operator's ruling of 2026-09-01, and it
is now written into the rule itself as §Nag, with its own limits attached so a future editor
cannot quietly turn a nag into a gate.

**The channel was established by probe, not by assumption.** Only one of four candidate channels
reaches the model: `PostToolUse` → `hookSpecificOutput.additionalContext`, verbatim. A hook's
`systemMessage`, its stderr, and a `PreToolUse` `allow` carrying a reason all go nowhere the model
can read. `PostToolUse` is also the right *safety* answer rather than a compromise — it runs after
the command, so it cannot block, wedge, or slow a headless run, and `permissionDecision: "ask"`
would have been worse than useless because it becomes an **auto-DENY in auto mode**.

**The front door was manufacturing the problem it complained about.** `AGENTS.md` §6 still carried
the pre-SCC-351 text telling agents to *"use `git -C`"* — the exact spelling Zoo's permission layer
auto-denies — and so did five places in the operator's SOP, including the row whose entire subject
is agents working on the wrong tree, which named `git -C` as its remedy. An agent obeying the front
door faithfully generated the approval stops. Of 1,247 `git -C` invocations measured, **521 named a
verb the allow list cannot pre-approve**; every one of those was a stop that would have been silent
in the `cd <abs> && git <verb>` shape the rule already mandated.

**What the nag is deliberately not.** It never blocks — asserted by test, because a mutant that
returns `ask` must fail the suite. It is not applied to destructive commands: a `PostToolUse` nag
speaks *after* the damage, so `git add -A` and `git worktree remove --force` stay `PreToolUse`
concerns and are named out of scope rather than silently skipped. And Zoo Code gets **no nag at
all**, because Zoo has no hook surface of any kind — that is why `zoo_notify.py` has to poll the
thread store. Zoo gets measurement and a correct fence instead, and the rule says so in the
negative so the next reader does not spend a day trying to write one.

## What closed, item by item

**1 · `AGENTS.md` §6 reconciled.** The gate now states the per-piece law — permission layers judge
a compound command **piece by piece**, so `cd <abs> && git status` is two matchable pieces while
`git -C <path> status` is one piece no verb rule can see — and pins the `cd <abs> && git` spelling.

**2 · The scan that should have caught it, widened.** `test_zoo_permissions.py`'s `git -C` sweep
reached `.agents/{commands,rules,skills}` only, so no test could see the root entry files where the
bad text actually lived. It now covers them. Both halves are proved: a live line rejects, and a
blockquoted teaching line still passes, so prose that *explains* the anti-pattern is not swept up.
The mutant confirms the scan is not pinned to one filename — re-inserting `git -C` into `CLAUDE.md`
goes red too.

**3 · `shape-guard.py`, the nag.** Registered through `run-hook.sh`, never a bare interpreter —
naming one platform's binary reproduces SCC-77, where the PC has `python` and no `python3` and the
hook exits **127 in silence**, which is indistinguishable from a hook with nothing to say. It fires
exactly one nag per broken rule, names the rule and the remedy, stays silent on a clean command, on
a `grep` *for* the string, and on a heredoc body, and fails open on malformed input.

**4 · `shape_scan.py`, the measurement.** Its load-bearing design decision is that it does **not
re-implement the three rules** — it calls the hook's own `violations()` and reads the rule number
out of the nag text. The measurement therefore cannot drift from what the nag actually catches, and
`test_shape_scan.py` fails if a private copy of the detector ever creeps back in. The negative
battery is the point of the tests, not decoration: the first cut of this scanner counted a `grep`
*for* `"git -C"` as a use of it, and counted heredoc bodies as commands.

**5 · The ruling promoted to law.** `command-shape.md` now carries §Nag with the operator's words,
the measurement that justifies it, the mechanism, and three numbered limits — a nag may never
block, a nag cannot protect against a destructive command, and only `PostToolUse`
`additionalContext` reaches the model. Six new checks in `test_rule_frontmatter.py` went red first.

**6 · The Zoo fence corrected.** Eight commands that repeatedly stopped and waited for approval,
and that no deny row protects, were promoted: `npx vitest`, `npm run`, `test -`, `sleep`, `ps aux`,
`ln -s`, and the two-machine venv twin (`backend/.venv/bin/` and `backend/.venv/Scripts/`, because
the same repo resolves to a different directory on the Mac than on the PC). All eight were checked
against the deny list first; none collides. The tracked file reads **120 allow / 105 deny**.

The store itself is being **reset rather than merged**, and the guide now records why. 143 entries
exist only in one Mac's globalState and never existed on the PC; `zoo_permissions_apply.py` has no
surgical remove, so keeping them would mean committing debris like `do`, `done` and `giast` into
repo policy. Of the 143, **101 are already covered by tracked prefixes and only 42 newly prompt** —
every one of those debris, a typo, or a bare-token superset whose trailing-space form is already
tracked. The reset also closes the `rm -f` hole with no deny-list change at all.

## Evidence

Whole gate, run bare, after absorbing `origin/main`:

python3 .agents/scripts/tests/run_all.py — EXIT_CODE_WAS=0 — 70/70 files passed

Controls:

python3 .agents/scripts/shape_scan.py --self-test — NEGATIVE CONTROLS: PASS (all six score zero) · POSITIVE CONTROLS: PASS (all five fire with the right rule)

Live measurement, 2026-09-01, rules 3 / 2 / 1:

- **Claude Code** — 9.44 % piped gate · 9.35 % exit-echo tail · 5.71 % `git -C`, over 8,234 commands in 25 sessions. Recorded baseline was 9.49 / 9.36 / 5.79 over 8,122; the window grows every session, so this is the same population re-counted, not a change in behaviour.
- **Zoo Code** — 19.03 / 4.45 / 3.64 % over 247 commands in 19 threads, reproduced exactly to two decimals when taken. ⛔ **It is no longer re-derivable from the live store:** Zoo's task directory came back **empty** after the VS Code restart on 2026-09-01, and no `ui_messages.json` survives anywhere under `globalStorage`. The scan reports *"no commands found — nothing to measure"* rather than a fabricated 0 %, which is the correct behaviour and is why the figure above is quoted from its recorded capture rather than re-run. Nothing in this lane touched Zoo's task store.

## Acceptance

| | Statement | Result |
|---|---|---|
| A | `AGENTS.md` §6 states the per-piece law and the `cd <abs> &&` pin; no `git -C` outside a blockquote in any root entry file | **MET** — `test_zoo_permissions.py` + its `CLAUDE.md` mutant |
| B | A piped gate, an exit-echo tail and a `git -C` each produce exactly one nag naming their rule | **MET** — `test_shape_guard.py` |
| C | A clean command, a `grep` for the string, and a heredoc body produce no nag | **MET** — the negative battery, six controls |
| D | The hook returns `allow` on every path, and a mutant returning `ask` fails the suite | **MET** — `test_shape_guard.py` |
| E | `shape_scan.py` reproduces the baselines | **MET** — Zoo exact to 2 dp at capture; Claude within 0.2 pp on a grown window. See the ⛔ note above: the Zoo store has since been emptied, so this row is proved by its capture, not by a re-run |
| F | `command-shape.md` carries §Nag and `rules/INDEX.md` its row | **MET** — `test_rule_frontmatter.py`, 10/17 red → 17/17 green |
| G | `zoo_permissions_apply.py --status` reads *in sync* on both lists | **PENDING the operator's hands** — see Your Actions |
| H | Whole gate green | **MET** — 70/70, exit 0 |

## Your Actions

| # | What | Why it is yours and not mine |
|---|---|---|
| 1 | **Quit VS Code fully (Cmd+Q, not just close the window)**, then in **Terminal.app** — not VS Code's integrated terminal — paste: `python3 .agents/scripts/zoo_permissions_apply.py --apply && python3 .agents/scripts/zoo_permissions_apply.py --status` | The apply writes into VS Code's globalState SQLite, and VS Code flushes its own in-memory copy on exit — so a write made while it runs is silently undone. `zoo_permissions_apply.py` refuses while it detects VS Code running, by design. This agent session lives *inside* VS Code, so it cannot be the thing that waits for VS Code to be gone. |
| 2 | Read the closing `--status`: both lists must say **in sync with tracked file** | That line IS acceptance row G. Before the apply it reads `allowedCommands: 255 (DRIFT: 7 tracked entries missing, 142 store-only)`. |
| 3 | Merge the pull request when `/smh-close-task-merge-tree` hands you the link | `main` is never an agent's. |

## Out of scope, named not dropped

- **A nag for `git add -A` and `worktree remove --force`.** Destructive — a `PostToolUse` nag speaks after the damage. At 4 and 18 hits in 7,858 calls they are a risk problem, not a time problem, and they belong in a `PreToolUse` guard.
- **Any nag for Zoo seats.** Zoo has no hook surface. Measurement and a correct fence are what it can have.
