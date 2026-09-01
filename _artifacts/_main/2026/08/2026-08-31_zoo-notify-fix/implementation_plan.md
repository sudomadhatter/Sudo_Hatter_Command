# SCC-355 — Zoo notifications actually reach the operator (follow-on fix)

**Lane:** `chore/SCC-355-zoo-notify-fix` · worktree `.claude/worktrees/zoo-notify-fix` · cut from `origin/main` @ `8a1b3cbf`
**Ticket:** SCC-355 (Subtask under SCC-352) — reopened from `Review Required` to `In Progress`; it was
parked awaiting the operator's confirmation, and his confirmation was *"the notifications are not
working"*. Follow-on inside the same key, no new ticket ([[followon-fixes-are-not-a-new-story]]).
**Diagnosis this plan acts on:** [diagnosis.md](diagnosis.md) — reproduction, measurements, the miss.

**Run mode:** INLINE. No subagents, no fan-out, per the operator's standing budget constraint
([[budget-is-a-live-constraint-announce-spend]]).

---

## What is already proven, so it is NOT in scope

| Claim | Evidence | Status |
|---|---|---|
| The ntfy push reaches the operator's phone | `--self-test` push read back off the public topic (`id=gX9zeFd5MG8P`, title `Zoo Code - needs you`), **and the operator confirmed he sees it** | ✅ works — no ntfy app setup is owed |
| `terminal-notifier` is installed and exits 0 | `/opt/homebrew/bin/terminal-notifier`; `--self-test` → `banner=sent` exit 0 | ✅ channel healthy |
| Zoo exposes no event hook to subscribe to | guide §6.1, SCC-355's own probe: 19 settings keys, 20 commands, none an event | ✅ settled — polling is the only design |

**The banner's on-screen appearance is still unconfirmed** and stays an operator checkbox: a Work
Focus swallows it while the run reports `sent` ([[claude-notifications-mac-and-phone]]).

---

## Acceptance — the checkable list

| # | Statement | Proved by |
|---|---|---|
| A1 | `classify()` returns `"ask"` for a tail Zoo actually writes when it needs the operator: `type=ask, partial=True, isAnswered=None, autoApprovalDecision=None` | new test, **seen RED against the shipped code**, GREEN after the fix |
| A2 | The fix changes **no** verdict that was already right: a `say` still streaming stays silent, an auto-approved ask stays silent, an answered ask stays silent, `completion_result` still means turn-end | the existing 38-test battery green, unchanged, plus one test asserting all four |
| A3 | Both thread fixtures are **real redacted captures** from the live store, not hand-built stubs — the ask fixture's tail carries `partial: True` and the file holds >50 messages | a test asserting both properties of the fixture files themselves |
| A4 | The watcher starts itself on login and is restarted if it dies — it is no longer something the operator must remember to run | `zoo_notify_install.py --status` reports the agent loaded; `launchctl list` names it |
| A5 | A launchd-started watcher resolves the right ntfy topic even though `launchd` never sources `~/.zshrc` | a test that the generated plist carries `NTFY_TOPIC` in `EnvironmentVariables` ([[zshrc-is-invisible-to-automation]]) |
| A6 | An ask **already pending** when the watcher starts still pages — the reboot case, which `KeepAlive` makes routine rather than exotic | a test that priming stays silent for a stale thread but pages for a fresh unanswered ask |
| A7 | The PC has a shipped, tracked install artifact and a documented step (it cannot be executed from this Mac) | the installer's `--status` renders the Windows branch under a forced platform; operator checkbox for the live run |
| A8 | The docs say "install the agent", not "run the command", everywhere the old step appears | `sop_currency.py` passes with the SOP staged (no `[sop-ok]`); `check_links` clean; `.agents/scripts/INDEX.md` names both scripts |

---

## Steps

### Step 1 — RED first (A1, A2, A3, A6)

1. **Capture the fixtures.** Copy two real threads out of
   `~/Library/Application Support/Code/User/globalStorage/zoocodeorganization.zoo-code/tasks/`,
   redacting file paths and prompt bodies but preserving **every** structural field
   (`type`/`ask`/`say`/`partial`/`isAnswered`/`autoApprovalDecision`/`ts`). One tail
   `ask/tool partial=True isAnswered=None`; one tail `say/completion_result`.
2. **Write the pinning test** `test_partial_ask_still_pages_because_zoo_never_clears_it()` and
   invert `test_partial_ask_never_fires` (which today pins the bug as intended behaviour).
   *Assertion:* run it against the **shipped** `classify()` and paste the red. Per
   [[reproduce-before-you-fix]] G2 the red must fail for the right reason — read which line raised.

### Step 2 — GREEN, minimal (A1, A2)

Move the `partial` guard so it applies to `say` messages only. An `ask` flagged `partial` **is** the
operator-facing ask; Zoo clears the flag when it auto-approves and leaves it standing when the
operator must answer (10 asks on disk carry `partial=True` **and** `isAnswered=True`).

Double-paging needs no new code: `thread_signature()` already keys on `(event, len(messages),
tail.ts)`, and a partial ask finalised in place keeps both, so the signature is identical and
`watch()` sends once. Verified before writing this plan.

### Step 3 — the priming exception (A6)

`watch()`'s first sweep primes silently so a restart does not page once per historical thread. With
`KeepAlive` the watcher restarts on every login and reboot, and asks measurably sit open for 17+
minutes — so "restarted while an ask is pending" is routine. During priming, still page for a thread
whose tail is an **unanswered ask** *and* whose mtime is within a freshness window (default 300 s).
Stale backlog stays silent. *Assertion:* two threads through one priming sweep, one fresh one stale,
exactly one page.

### Step 4 — the installer (A4, A5, A7)

`zoo_notify_install.py`, shaped like its sibling `zoo_permissions_apply.py`: `--status` (default,
read-only), `--apply`, `--remove`.

- **Mac:** writes `~/Library/LaunchAgents/com.sudohatter.zoo-notify.plist` with `RunAtLoad`,
  `KeepAlive`, `EnvironmentVariables` carrying `NTFY_TOPIC` and a `PATH` that includes
  `/opt/homebrew/bin` (launchd's default `PATH` does **not**, and `terminal-notifier` lives there —
  this is the same class of miss as the `.zshrc` one), and `StandardOutPath`/`StandardErrorPath`
  under `~/Library/Logs/` so a silent watcher can be diagnosed instead of guessed at.
- **PC:** writes a `zoo-notify.cmd` into the Startup folder, using `pythonw` so no console window
  opens. Authored here, **run by the operator** — [[mac-authored-code-hides-windows-bugs]] is why it
  is a checkbox and not a claim.

*Assertion:* tests over both branches with the platform forced, asserting the plist's keys and the
`.cmd`'s content into a tmp dir; nothing touches the real `~/Library/LaunchAgents` in a test.

### Step 5 — docs (A8)

SOP §13 row, the changelog, guide §6.1/§11, `.agents/scripts/INDEX.md`. The step becomes *install the
agent once per machine*, and the old *"start the watcher"* line goes — it is the instruction that
produced this bug report.

---

## Risk named up front

**The freshness window in Step 3 is a heuristic and it can page for a thread the operator already
abandoned.** That is the deliberate direction of the error: this notifier fails OPEN, per the
module's own deny-list doctrine. A spurious banner costs a glance; a missed one costs the feature.

**Landing-order dependency:** the live sibling lane `chore/SCC-347-cicd-pr-door-and-guide` also edits
`docs/_scc_sops_prds/workflows_testing_SOP.md`, `workflows_testing_SOP_changelog.md` and
`_artifacts/_main/INDEX.md`. All three are **ledgers** — append-shaped, conflicts resolvable by
keeping both rows. Whichever lands second absorbs `main` and re-runs its gate
([[lane-collision-is-gates-not-files]]).

---

## Port section (MANDATORY RULE 5 — the trigger is PROVEN, not asserted)

**Trigger:** this lane writes a per-machine OS integration and edits a script that already resolves
paths per platform.

| # | Check | Answer |
|---|---|---|
| 1 | A path git gave you is used exactly as git gave it | The installer takes **absolute** paths from `Path.home()`; the plist's `ProgramArguments` carries the repo's absolute path resolved at `--apply` time, never a git-relative one |
| 2 | Operator-facing text goes through `printf`, never `echo` | Python `print()` throughout; no shell `echo` ([[echo-truncates-at-backslash-c]]) |
| 3 | On a write, verify the FILE — not `$?` | `--apply` re-reads the plist it wrote and prints its resolved contents; `--status` parses it back |
| 4 | No `.agents/rules/` path the target repo does not carry | Nothing ships into a project repo; this is lobby-only |
| 5 | It runs on BOTH machines | Both branches written and unit-tested with the platform forced. The **live** PC run is A7's operator checkbox, not a claim ([[two-machines-mac-and-pc]]) |
| 6 | Hooks stay repo-local, and the port needs the target's OWN key | No git hook is touched. The LaunchAgent is a machine artifact outside the repo, installed by a tracked script — the same shape as `zoo_permissions_apply.py --apply` ([[repo-local-enforcement-never-centralizes]]) |

---

## Declared Change Set

- EDIT `.agents/scripts/zoo_notify.py` — the `partial` guard applies to `say` only; priming pages a fresh pending ask → A1, A2, A6
- EDIT `.agents/scripts/tests/test_zoo_notify.py` — invert the partial test, add the pinning regression, assert fixture shape, cover priming → A1, A2, A3, A6
- EDIT `.agents/scripts/tests/fixtures/zoo_ui_messages_ask.json` — replace the 5-message stub with a real redacted capture whose tail is `partial: True` → A3
- EDIT `.agents/scripts/tests/fixtures/zoo_ui_messages_turnend.json` — replace the stub with a real redacted capture → A3
- NEW `.agents/scripts/zoo_notify_install.py` — per-machine installer: launchd agent on the Mac, Startup `.cmd` on the PC → A4, A5, A7
- NEW `.agents/scripts/tests/test_zoo_notify_install.py` — both platform branches, env carriage, no real store touched → A4, A5, A7
- EDIT `.agents/scripts/INDEX.md` — a row for the installer, and the notifier's row corrected → A8
- EDIT `docs/migrations/zoo-code-permissions-guide.md` — §6.1/§11: install the agent, not run the command → A8
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the Zoo notification row rewritten → A8
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — the changelog row → A8
- EDIT `_artifacts/_main/INDEX.md` — the session row for this lane → A8
- NEW `_artifacts/_main/2026-08-31_zoo-notify-fix/implementation_plan.md` — this plan → all
- NEW `_artifacts/_main/2026-08-31_zoo-notify-fix/task.yaml` — the lane manifest → all
- NEW `_artifacts/_main/2026-08-31_zoo-notify-fix/walkthrough.md` — RED→GREEN evidence and the review → all
- NEW `_artifacts/_main/2026-08-31_zoo-notify-fix/diagnosis.md` — the investigation this plan acts on (already written) → all
- EDIT `.agents/commands/smh-llm-approvals.md` — drop the `partial is not true` filter; it hides 4 of 27 operator-stopped commands (audit F1) → A9
- EDIT `.opencode/commands/smh-llm-approvals.md` — regenerated mirror of the brain → A9
- EDIT `.agents/workflows/smh-llm-approvals.md` — regenerated mirror of the brain → A9

---

## Self-Audit (2026-08-31)

**Level:** LEDGER+BLAST (the set touches a script others import, a door surface, the SOP, and
creates two new files) · **Mode:** PRE-WORK · **Runtime:** inline, no subagents.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path the plan names resolved on disk (10 EXISTS, 2 correctly NEW)
             declared_change_set.py parse -> present: true, 15 entries
             stdlib-only import audit of zoo_notify.py (argparse/json/os/subprocess/sys/time/urllib/pathlib)
             lane fit: no deployable path in the declared set
             Scope Ledger: both NEW artefacts x their acceptance rows
             ticket precondition: 8 acceptance rows, each naming a concrete observable
read:        .agents/scripts/zoo_notify.py, .agents/scripts/tests/test_zoo_notify.py,
             both fixtures, .agents/scripts/INDEX.md, docs/migrations/zoo-code-permissions-guide.md,
             docs/_scc_sops_prds/workflows_testing_SOP.md:2787, _artifacts/_main/INDEX.md
verdict:     clean
```

Scope Ledger — every `NEW` artefact carries a requiring row, so no finding:

| Created | Required by | Caller count |
|---|---|---|
| `.agents/scripts/zoo_notify_install.py` | A4, A5, A7 | an entry point by design, like its sibling `zoo_permissions_apply.py`; callers are the operator and the docs |
| `.agents/scripts/tests/test_zoo_notify_install.py` | A4, A5, A7 | `run_all.py` |

```
lens:        2 Parity + Blast
checks_run:  script scar - callers in .githooks/ (none), its test (present), scripts/INDEX.md (present)
             usage-surface scar - .agents/scripts/*.py is a sop_currency surface; the SOP is declared
             twin check - no cicd-*/smh-* sibling of zoo_notify.py exists
             door scar - grep "zoo_notify" across every command, workflow and generated mirror
             sibling worktrees - env -u GITHUB_TOKEN git fetch origin main, then per-tree diff
             risk_seam.py classify --repo <this tree> -> unclassified (correct: SCC-289, no code graph)
read:        .agents/commands/smh-llm-approvals.md:42-56, .opencode/commands/smh-llm-approvals.md:54,
             .agents/workflows/smh-llm-approvals.md:54, .githooks/, chore/SCC-347 worktree diff
verdict:     findings below
```

```
lens:        3 Pre-Mortem (bounded - attaches narratives, originates nothing)
checks_run:  attached the silent-failure narrative to F1; the other-machine narrative to F2
read:        the two anchored findings above
verdict:     clean (no unattached output produced, so none discarded)
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/commands/smh-llm-approvals.md:54` (+ identical at `.opencode/commands/smh-llm-approvals.md:54`, `.agents/workflows/smh-llm-approvals.md:54`) | ``` `type` is `ask`, `ask` is `command`, `partial` is not `true`, and **`autoApprovalDecision` is `null`** ``` | **F1 — the same bug, in a second door.** `/smh-llm-approvals` exists to surface the commands that stopped for the operator so they can be allow-listed, and it applies the identical `partial is not true` filter. Measured against the live store: it would list **23** and silently drop **4**. Fixing `classify()` alone leaves this door under-reporting, and the operator's next read of it looks like the fix failed | **HIGH** |
| `chore/SCC-347-cicd-pr-door-and-guide` worktree diff | `docs/_scc_sops_prds/workflows_testing_SOP.md`, `workflows_testing_SOP_changelog.md`, `_artifacts/_main/INDEX.md` | **F2 — landing-order dependency.** All three are ledgers this lane also edits. Whichever lands second must absorb `main` and re-run its gate, keeping both rows rather than either | **MEDIUM** |

**Pre-mortem narrative attached to F1 (the silent one):** the fix ships, Zoo starts paging correctly,
and the operator runs `/smh-llm-approvals` to top up his allow-list — where four of his stopped
commands are still missing. Nothing errors. He concludes the notification fix did not work, because
the only surface he can *read* still under-reports.

**Pre-mortem narrative attached to F2 (the other-machine one):** SCC-347 lands first, this lane's
SOP row conflicts, and a rushed resolution keeps one row and drops the other — leaving the SOP
telling him to *start the watcher* after the watcher became a LaunchAgent.

### Observations (uncounted — no anchor, judgment only)

- The plist will embed this repo's absolute path in `ProgramArguments`. If the repo ever moves, the
  agent points at a dead path and fails silently. Baked into Step 4 below as a `--status` check
  rather than left as a hope.
- The ntfy topic `mac-sudo-command` is **public by name** — I read the operator's own notification
  history off it with an unauthenticated `curl` while investigating. Pre-existing since Claude's
  2026-08-14 wiring, not introduced here, and out of this lane's scope. Remedy if he wants it:
  an ntfy access token, or a random topic name. Raised once, not carried.

### Amendments baked into the plan (read them in context above)

- **A9 added** to the acceptance list, and three rows added to the Declared Change Set, for F1.
- **Step 4 amended:** `--status` must verify the installed plist's `ProgramArguments` path still
  exists on disk, not merely that the agent is loaded.

```
Audit verdict: GO
```

---

## ⚠️ AUDIT FINDING (Lens 2, F1) — the reach check, folded into scope

`reproduce-before-you-fix` §Contributing causes asks *what else shares this mechanism* — and then
says **go look**. Looking found `/smh-llm-approvals` carrying the same filter in prose. It is fixed
in this lane: same mechanism, same subject, one sentence plus its two generated mirrors.

| # | Statement | Proved by |
|---|---|---|
| A9 | No door tells an agent to skip a Zoo ask because it is flagged `partial` — the `/smh-llm-approvals` reader is corrected in the command brain and both generated mirrors | `grep -rn "partial\` is not" .agents/ .opencode/` returns **zero**; `test_command_surfaces.py` green (the mirrors stay byte-identical to the brain) |

### Declared Change Set — F1 additions

- EDIT `.agents/commands/smh-llm-approvals.md` — drop the `partial is not true` filter; it hides 4 of 27 operator-stopped commands → A9
- EDIT `.opencode/commands/smh-llm-approvals.md` — regenerated mirror of the brain → A9
- EDIT `.agents/workflows/smh-llm-approvals.md` — regenerated mirror of the brain → A9
