# SCC-77 — Enforce the main-branch write gate

**Branch:** `chore/SCC-77-main-write-gate` (Task lane → `/smh-close-task-merge-tree`)
**Base:** `main` @ `9a6a026`
**Lane:** LOCAL (command centre has no deployable surface)

---

## The problem, in one line

`git-policy.md` documents a write gate that has never executed on this machine.

| Layer | Claimed | Actual |
|---|---|---|
| `pre-push` git hook | — | **does not exist** in either repo |
| `require-push-approval.py` PreToolUse | "forces the approval prompt on any `git push` targeting `main`" | wired to `powershell -Command "python …"`; this Mac has **neither** (only `pwsh`, `python3`) → exit 127, silent |
| 4× SessionStart hooks | continuity + drift checks | same defect, all dead |
| AGY `.claude/hooks/` | — | directory does not exist |

Six merges rode one sign-off on 2026-08-09 because nothing was there to stop them.

Extra find: SCC's `core.hooksPath` is the **absolute** `/Users/sudohatter/Sudo_Hatter_Command/.githooks`.
AGY's is the relative `.githooks`. AGY's is correct — an absolute path cannot survive a clone to the PC.

---

## The door set (operator ruling 2026-08-10)

Two doors, plus the operator. This is what `git-policy.md:70`, the command bodies, and the SCC-77
ticket already say — **no rule doc changes.**

| Destination | Key |
|---|---|
| `main` | `/cicd-push-e2e` (epic, full gate + e2e) · `/smh-close-task-merge-tree` (task, preflight + lane gate) · operator's direct "approved" |
| epic branch | `/cicd-update-sprint-memory` — **never main** |

The SOP's SCC-71 block reads as if `/cicd-update-sprint-memory` were a third main door. It is making
the one-typing-one-merge point about both close-outs, but the sentence that follows turns it into a
door list. That sentence is the only surface carrying the wrong model; it gets fixed here.

---

## Architecture — two layers, one authoritative

**Layer A — git `pre-push` hook. THIS IS THE GATE.** Plain `sh`; Git-for-Windows bundles `sh`, so it
runs identically on both machines, under every agent platform, and in the operator's own terminal.
Per the ticket: *"Git hooks are the only enforcement layer both machines and all platforms share."*

**Layer B — Claude `PreToolUse` hook. UX only.** Prompts earlier with a better message. Repaired, but
nothing depends on it. If it dies again the gate still holds.

---

## The token contract

**Path** `$(git rev-parse --git-common-dir)/main-push-approval`

`--git-common-dir` (not `--git-dir`) so every worktree shares one token. Under `.git/`, so it never
travels with a clone and never lands in a commit.

**Content**

```
branch=chore/SCC-77-main-write-gate
tip=<sha of the branch at mint time>
command=/smh-close-task-merge-tree
key=SCC-77
minted=<epoch seconds>
```

**Gate order** — each step its own refusal message, so a failure says which rule fired:

1. `DISABLE` present, or `MAIN-PUSH-ENFORCE` absent → pass through (unarmed).
2. Ref is not `refs/heads/main` → **exit 0 immediately.** `main` is the only protected destination;
   whole-token match so `epic/main-fix` never trips it.
3. No token → **REFUSE**, printing the two doors by name.
4. `minted` older than 30 min → **REFUSE** (stale sign-off).
5. `tip` ≠ the sha actually being pushed → **REFUSE.** The branch moved after the sign-off, so commits
   exist that no gate ever saw. This is the check that matters most.
6. Consume — delete the token, **then** allow.

**Deliberate: the token is consumed before the push, so a rejected push needs a fresh sign-off.**
There is no `post-push` hook, so this is the only available order — and it fails in the safe
direction. A rejected push means the remote moved, which means re-running the door command to
re-preflight anyway. That is SCC-71's rule working, not friction.

**Escape hatches** — all three loud and documented, none silent:
`git push --no-verify` · delete `MAIN-PUSH-ENFORCE` · `.agents/scripts/git-hooks/DISABLE`.

---

## Files

### New

| # | Path | What |
|---|---|---|
| 1 | `.githooks/pre-push` | Thin dispatcher. Copies the `commit-msg`/`pre-commit` house pattern **including the SCC-32 worktree guard** — a tree cut before the script existed must warn and allow, never die on `exec` |
| 2 | `.agents/scripts/git-hooks/pre-push-main-approval.sh` | The gate. `main` only |
| 3 | `.agents/scripts/git-hooks/MAIN-PUSH-ENFORCE` | Tracked arm flag, same prose shape as `JIRA-ENFORCE` — tracked on purpose, or it arms one machine and is silent on the other |
| 4 | `.agents/scripts/mint_push_token.py` | Writes the token. **One** implementation, called by both doors |
| 5 | `.agents/scripts/tests/test_main_push_gate.py` | Registered in `run_all.py` → 12/12 |
| 6 | `.agents/hooks/run-hook.sh` + deployed `.claude/hooks/run-hook.sh` | Interpreter shim: `python3` else `python` |

### Modified

| # | Path | Change |
|---|---|---|
| 7 | `.claude/settings.json` | All 5 hook commands off `powershell`/`python` |
| 8 | `.agents/commands/cicd-push-e2e.md` | Mint step immediately before Step 4's `git push origin main` |
| 9 | `.agents/commands/smh-close-task-merge-tree.md` | Mint step immediately before Step 3's `git push origin main` |
| 10 | `_my_resources/_quick_reference/sudo_workflows_testing.md` | Fix the SCC-71 door sentence; document the gate (SOP currency requires this anyway) |
| 11 | `.agents/rules/git-policy.md` | Rewrite the `Enforcement:` paragraph to describe what actually enforces; **fix `:67`'s false "AGY keeps its own identical copy"** (ruled defect 6) |
| 12 | *(config, not a file)* | `git config core.hooksPath .githooks` — relative, matching AGY |

---

## Tests (`test_main_push_gate.py`)

1. `.githooks/pre-push` exists and is executable.
2. `core.hooksPath` resolves to a directory containing it.
3. Push to a non-`main` ref → allowed with no token.
4. Push to `main`, no token → **refused**, exit non-zero.
5. Push to `main`, valid token → allowed.
6. Push to `main`, same token again → **refused** (consumed).
7. Token whose `tip` ≠ pushed sha → **refused**.
8. Token older than 30 min → **refused**.
9. Arm flag absent → allowed (unarmed passes through).
10. **No hook command in `.claude/settings.json` names a single-platform binary** — the regression
    test for the actual bug. Bans bare `powershell`, bare `python`, `C:\`, `.ps1` as the entry point.

---

## Stated limitations — not defects, and they go in the docs

1. **An agent can write files, so an agent can forge a token.** This is not a security boundary
   against a determined agent. It converts a *silent* violation into a *deliberate, traceable* one,
   and it stops the real SCC-71 failure mode — a command body sitting in context that still reads
   valid on task six. That is the correct target.
2. **`gh pr merge` and the GitHub web UI never reach a local hook.** Structurally out of reach.
   Already routed to the SCC-75 child.

---

## Scope

**This repo only.** SCC-77 is an SCC ticket. AGY needs the same two files plus `core.hooksPath` —
that is a separate AVCH ticket, per the cross-repo rule (a ticket per repo).

---

## Also riding along (operator-confirmed)

- The exit-127 hook repair (items 6, 7) — it is the same root cause and the ticket already lists it as
  point 3.
- Defect 6: `git-policy.md:67`'s false AGY claim (item 11).
- The parked memory correction for `git-branch-model-standard.md` — its description states the epic
  model as universal, which is what misleads every session reading it in the lobby.

## Routed elsewhere — not built here

- Defect 2 (stale `git_walkthrough_settings.md:299`) → **SCC-74**.
- Defects 3/4/5 (incident prefix mismatch; incident lands via PR; `gh pr merge` ungated) → one new
  child of **SCC-75**.
- Neither minted — placement is the operator's (`jira.md` guardrail 2).

---

## Order of work

1. Cut `chore/SCC-77-main-write-gate` + worktree off `main`, author `task.yaml`.
2. Rewrite the SCC-77 Jira description (it still names `/close-task-merge-tree` and `/sudo-push-e2e`).
3. Gate script + dispatcher + arm flag (1, 2, 3).
4. Minter (4), then wire both doors (8, 9).
5. Hook-wiring repair (6, 7) + `core.hooksPath` (12).
6. Tests (5) → `run_all.py` 12/12.
7. Docs (10, 11) + memory correction.
8. **Live proof on the branch:** push to main with no token → refused · mint → allowed · retry →
   refused. Paste the real terminal output into the walkthrough; a gate reported from intent is the
   exact failure this toolkit exists to remove.
9. `/smh-close-task-merge-tree` — and this branch's own merge is the gate's first real customer.
