# SCC-352 — Agent approvals + notifications (CONSOLIDATED lane, 2 parts)

**Lane:** `chore/SCC-352-llm-approvals` (one worktree, one branch, keyed by the parent)
**Mode:** CONSOLIDATED — the operator ruled it: *"we can skip the label task and just do them both
on one working tree one at a time."* Part B is built first (it is smaller and it pays back
immediately), then Part A, both in this tree, each part's commits led by its own subtask key.

**Riders:** SCC-354 (Part A, the door) · SCC-355 (Part B, notifications)

---

## Parent acceptance — the checkable list

| # | Statement | Proved by | Part |
|---|---|---|---|
| A1 | `/smh-llm-approvals` exists as a command brain with a generated launcher for every platform in its `platforms:` list, and a run writes NO store | door-parity check in the enforcement suite + a dry run that leaves every store byte-identical | A |
| A2 | Every Zoo row the door proposes replays TRUE through the ONE matcher module, picked rows land in tracked `.vscode/settings.json`, battery + ceremony tests stay green | `.agents/scripts/tests/run_all.py` (existing `test_zoo_permissions.py` battery) + a new suggest test | A |
| A3 | Every Claude row it proposes is a valid `Bash(...)` rule derived from real session JSONL, and NAMES which of the six `.claude/settings.json` stores it targets | new test asserting each proposed row carries a resolved store path | A |
| A4 | opencode and Codex each have a working propose path OR a recorded reason in `terminal-global-permission.md` why the surface is not worth it | inspection of the guide + `check_links` | A |
| B1 | Zoo fires a desktop notification on an approval-ask and on turn-end, on Mac and PC | operator triggers one of each and confirms (he is the hands) | B |
| B2 | The same two events push to the existing ntfy topic `mac-sudo-command` | same trigger; phone receives | B |
| C1 | The loose working-tree files left over from the SCC-351 session land on `main` with this Task — operator's instruction this session: *"roll all the untracked files in the source control into this story when you push to main"* | `git diff --name-only origin/main...HEAD` names all five | both |
| A5/B3 | SOP, changelog, and `zoo-code-permissions-guide.md` §6/§11 name the new door and the notification wiring | `sop_currency.py` (armed commit-msg gate) + `check_links` | both |

---

## Part B — SCC-355, Zoo notification parity (built FIRST)

### What is actually true today (measured, not assumed)

Claude's pipeline is `~/.claude/settings.json` `Notification` + `Stop` hooks → `~/.claude/notify.sh`
→ terminal-notifier banner + ntfy push to topic `mac-sudo-command`. Two consequences the ticket
outline did not know:

- **`notify.sh` is per-machine and untracked.** It lives under `~/.claude/`, not in this repo, and
  per `[[claude-notifications-mac-and-phone]]` the PC has no copy yet. So "parity" cannot mean
  "commit a hook" — it means a tracked script plus a per-machine install step, the same shape as
  `zoo_permissions_apply.py --apply`.
- **The lobby's tracked `.vscode/settings.json` carries no notification key at all** (`grep -n
  "notif\|sound\|ntfy"` → 0 hits), so nothing exists to extend.

### The open question, and the fallback if the answer is no

**Step B0 is an investigation, and it may come back negative:** does Zoo Code expose an event hook
surface (a settings key, a command, anything that fires on approval-ask and on turn-end)? If it
does, wire it. If it does not, the fallback is already grounded by this session's recon — Zoo writes
every thread to
`~/Library/Application Support/Code/User/globalStorage/zoocodeorganization.zoo-code/tasks/<id>/ui_messages.json`
(confirmed present, 2 task dirs on this Mac), so a small watcher keyed on that file's mtime and its
last message type drives the SAME notify script. **Either answer is a pass for B1** — what is not
allowed is discovering the surface does not exist and stopping.

### Steps

1. **B0 — probe Zoo's notification surface.** Enumerate `zoo-code.*` settings keys and any
   extension-contributed commands. *Assertion:* a written finding in the guide naming the surface
   or naming its absence, with the command output that answered it.
2. **B1 — the notifier.** A tracked `.agents/scripts/zoo_notify.py` that takes an event name and a
   message and fires terminal-notifier (Mac) / the PC equivalent plus the ntfy push, reusing the
   topic from `NTFY_TOPIC` with `mac-sudo-command` as the default. *Assertion:* a unit test that a
   dry-run invocation composes the right banner text and the right ntfy URL for both machines, with
   NO network call.
3. **B2 — the trigger.** Whichever B0 returned: the hook wiring, or the mtime watcher. *Assertion:*
   a test that feeds a captured `ui_messages.json` with an approval-ask as its last message and
   asserts the notifier is called once with the ask event; and a second fixture ending in a
   completed turn asserting the turn-end event.
4. **B3 — the per-machine install step** documented beside Zoo's existing `--apply`, plus SOP,
   changelog and guide rows. *Assertion:* `sop_currency.py` passes without `[sop-ok]`, `check_links`
   clean.
5. **B4 — the live proof.** Operator triggers one ask and one turn-end and confirms banner + phone.
   Recorded under `## Your Actions`, because he is the hands and this cannot be self-certified.

### Risk named up front

The Focus-mode failure in `[[claude-notifications-mac-and-phone]]` bit this exact pipeline once: a
Work Focus swallows the banner while the script still exits 0 and the phone push still arrives. B4's
check must therefore distinguish *fired but suppressed* (visible in Notification Center history)
from *never fired*, or a green will be claimed on a silent Mac.

---

## Part A — SCC-354, the `/smh-llm-approvals` door

### The structural finding that shapes this part

The matcher mirror the ticket wants to reuse — `decide()`, `pieces()`, `_longest()` — lives **inside
the test file**, `.agents/scripts/tests/test_zoo_permissions.py` (lines 41–137). A production
`--suggest` path cannot import from a test without making the test a library, and copying it creates
a second copy of the exact thing whose whole purpose is to be the single mirror of Zoo's real
matcher. **So step A1 is an extraction, not a feature:** move the mirror into
`.agents/scripts/zoo_matcher.py`, have the existing test import it, and prove the extraction changed
no verdict before anything new is built on it.

### Steps

1. **A1 — extract the matcher.** Move `decide`/`pieces`/`_longest`/`_mask_quotes` into
   `.agents/scripts/zoo_matcher.py`; `test_zoo_permissions.py` imports them. *Assertion:* the full
   existing battery (battery / ceremony / residuals / re-allow / tie tests) passes unchanged — a
   verdict that moves is a failed extraction, not a new decision.
2. **A2 — the thread readers.** `zoo_threads()` over
   `globalStorage/zoocodeorganization.zoo-code/tasks/*/ui_messages.json` and `claude_sessions()`
   over `~/.claude/projects/*/*.jsonl`. Claude's approval-stop signal is present and greppable —
   this session's own JSONL carries `doesn't want to proceed with this tool use` twice, alongside
   `permissionMode` and `command_permissions`. *Assertion:* a test over committed fixture files
   (one Zoo thread, one Claude JSONL, both redacted) extracting a known list of commands.
3. **A3 — the proposer.** For each extracted command, replay through `zoo_matcher.decide()` and emit
   the SHORTEST prefix that flips it to allow without flipping any battery row. *Assertion:* a test
   that every proposed row (a) makes its own command allow, and (b) leaves
   `test_battery_never_auto_approves` green — the proposer must never propose a row that unlocks the
   deny battery.
4. **A4 — the door.** `.agents/commands/smh-llm-approvals.md` plus generated launchers; it PRINTS
   grouped rows per platform and writes nothing. ⚠️ **AUDIT FINDING (Lens 2, SCC-66 scar):** a new
   door also needs its row in `.agents/commands/INDEX.md`, and the new scripts need theirs in
   `.agents/scripts/INDEX.md` — a door on disk that no index names is how four platform caches
   drift apart. Both index rows are now in the Declared Change Set. *Assertion:* the suite's door-parity check, and a
   test that a full run over the fixtures leaves every store file byte-identical.
5. **A5 — the six Claude stores.** Every proposed Claude row names its target
   `.claude/settings.json`. *Assertion:* a test that no proposed row is emitted without a resolved
   store path.
6. **A6 — opencode + Codex.** Confirm each store and matcher shape, wire the propose flow or record
   why not in `terminal-global-permission.md` (which today says both are "to be pinned in the
   SCC-352 lane"). *Assertion:* those two rows no longer say "to be pinned"; `check_links` clean.
7. **A7 — SOP, changelog, guide §6/§11.** *Assertion:* `sop_currency.py` passes without `[sop-ok]`.

---

## Port section (MANDATORY RULE 5 — the trigger is PROVEN, not asserted)

**Trigger, with the command output that answered it:**

```
.vscode/settings.json    copies=8   every project differs from the lobby (differ=1 × 7)
.claude/settings.json    copies=6   every project differs from the lobby (differ=1 × 5)
grep -l "zoo-code\." Projects/*/.vscode/settings.json   →  no matches
grep -l "permissions"  Projects/*/.claude/settings.json →  all 5 projects carry their own block
```

| # | Check | Answer |
|---|---|---|
| 1 | A path git gave you is used exactly as git gave it | The readers take **absolute** paths from `Path.home()`, never a git-relative path; store paths are resolved per repo and printed verbatim |
| 2 | Operator-facing text goes through `printf`, never `echo` | Python `print()` throughout; no shell `echo` in either script ([[echo-truncates-at-backslash-c]]) |
| 3 | On a write, verify the FILE — not `$?` | Only `--apply` writes, and it already re-reads the store; the door itself writes nothing, which A4's byte-identical assertion proves |
| 4 | No `.agents/rules/` path the target repo does not carry | Nothing ships into a project repo. **The door READS six `.claude/settings.json` files but WRITES none of them** — a picked Claude row is applied by the operator in that repo's own lane, with that repo's own key |
| 5 | It runs on BOTH machines | Zoo globalStorage differs by OS (`Application Support` vs `%APPDATA%`); both roots resolved from a table, never hardcoded. Part B's PC branch is explicitly in scope ([[two-machines-mac-and-pc]], [[mac-authored-code-hides-windows-bugs]]) |
| 6 | Hooks stay repo-local, and the port needs the target's OWN key | No hook is installed into any project. Proposing a row for `Projects/AGY_AVIATIONCHAT/.claude/settings.json` is a **cross-repo change and needs an AVCH key** ([[cross-repo-work-needs-a-ticket-per-repo]]) — so the door PRINTS those rows and refuses to write them, and the guide says so |

---

## Declared Change Set

⚠️ **AUDIT FINDING (Lens 1, fixed here):** this block was first written as a markdown table and
`declared_change_set.py parse` returned `present: false` — the review's drift check would have read
the whole lane as undeclared. Rewritten as the grammar the parser actually accepts:
`- <OP> \`path\` — why → <rows>`.

**Already committed on this lane** (acceptance row C1) — declared so the drift check reconciles them:

- EDIT `.gitignore` — ignore the regenerated `firebase-debug.log` → C1
- EDIT `_artifacts/_main/2026-08-30_zoo-approvals/tickets/SCC-351.md` — close-out trim → C1
- EDIT `_artifacts/_memory/MEMORY.md` — index rows for the two new memories → C1
- NEW `_artifacts/_memory/budget-is-a-live-constraint-announce-spend.md` — session memory → C1
- NEW `_artifacts/_memory/worktree-remove-force-eats-untracked-memories.md` — session memory → C1

**Part B — SCC-355:**

- NEW `.agents/scripts/zoo_notify.py` — the notifier: banner + ntfy push → B1, B2
- NEW `.agents/scripts/tests/test_zoo_notify.py` — dry-run composition test, no network → B1, B2
- NEW `.agents/scripts/tests/fixtures/zoo_ui_messages_ask.json` — thread ending in an ask → B1
- NEW `.agents/scripts/tests/fixtures/zoo_ui_messages_turnend.json` — thread ending complete → B1
- EDIT `.vscode/settings.json` — notification wiring, only if B0 finds a settings surface → B1

**Part A — SCC-354:**

- NEW `.agents/scripts/zoo_matcher.py` — the matcher mirror, extracted from the test → A2
- EDIT `.agents/scripts/tests/test_zoo_permissions.py` — imports the extracted mirror → A2
- NEW `.agents/scripts/llm_approvals.py` — thread readers plus the row proposer → A1, A2, A3
- NEW `.agents/scripts/tests/test_llm_approvals.py` — reader and proposer tests → A1, A2, A3
- NEW `.agents/scripts/tests/fixtures/zoo_thread_sample.json` — redacted Zoo thread → A2
- NEW `.agents/scripts/tests/fixtures/claude_session_sample.jsonl` — redacted Claude session → A2
- NEW `.agents/commands/smh-llm-approvals.md` — the door brain → A1
- NEW `.claude/skills/smh-llm-approvals/SKILL.md` — generated Claude launcher → A1
- NEW `.opencode/commands/smh-llm-approvals.md` — generated opencode launcher → A1
- NEW `.roo/commands/smh-llm-approvals.md` — generated Zoo launcher → A1
- NEW `.agents/workflows/smh-llm-approvals.md` — generated Antigravity launcher → A1
- NEW `.agents/skills/smh-llm-approvals/SKILL.md` — generated skills-surface launcher → A1

⚠️ **AUDIT FINDING (Lens 3, pre-mortem attached to A4):** the sandbox DENIES writes under
`.claude/skills/` (SCC-300), so `/smh-sync-agents` cannot generate that launcher in-session — the
SCC-351 lane hit exactly this and hand-wrote its mirrors byte-matching the generator, proving
equivalence through the suite's currency checks. Plan for that, or the door ships with four of its
five launchers and the parity check fails at review.
- EDIT `.agents/scripts/zoo_permissions_apply.py` — the `--suggest` mode → A2

**Both parts — the index and doc surfaces:**

- EDIT `.agents/commands/INDEX.md` — the new door's row → A1
- EDIT `.agents/scripts/INDEX.md` — rows for every new script → A1, B1
- EDIT `docs/migrations/zoo-code-permissions-guide.md` — sections 6 and 11 → A4, A5/B3
- EDIT `docs/migrations/terminal-global-permission.md` — the opencode and Codex rows → A4
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the new door's usage → A5/B3
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — the changelog row → A5/B3

⚠️ **AUDIT FINDING (Lens 1, fixed here):** the changelog was declared with no path at all. The real
file is `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — and it matters more than a typo,
because `sop_currency.py` is an ARMED commit-msg gate: a builder who edits the SOP and cannot find
the changelog gets their commit rejected mid-flow.

**Not in the set, and deliberately so:** no file under `Projects/*/` is written. No deployable path
(`backend/`, `frontend/`, `firebase/`, `functions/`, `mobile/`, `.github/`) is touched — MANDATORY
RULE 4 checked and clear, so this stays Task work and closes via `/smh-close-task-merge-tree`.

## Build order

B0 → B1 → B2 → B3 (SCC-355 lands green in this tree) → A1 → A2 → A3 → A4 → A5 → A6 → A7.
B4's live proof is the operator's, recorded under `## Your Actions`, and does not block Part A.

---

## Self-Audit (2026-08-30)

**Level: LEDGER+BLAST** — the Declared Change Set touches scripts others import, a new command/door
surface, five platform launchers, an armed gate's doc pair, and files that exist in more than one
repo. **Mode: PRE-WORK.** Subject: `_artifacts/_main/2026-08-30_llm-approvals/implementation_plan.md`
on `chore/SCC-352-llm-approvals`; parent SCC-352, riders SCC-354 + SCC-355.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/script/rule/door the plan names exists (14 checked, 1 miss)
             declared_change_set.py parse (run 3x: table -> heading suffix -> clean)
             Scope Ledger: 17 NEW artefacts x the acceptance row requiring each
             caller count for the extracted matcher module
             both-machines: stdlib only, python3 vs python, no venv
             lane fit: no deployable path in the declared set
read:        .agents/scripts/zoo_permissions_apply.py (145 lines, argparse --status/--apply)
             .agents/scripts/tests/test_zoo_permissions.py (423 lines; decide/pieces/_longest L41-137)
             .agents/scripts/declared_change_set.py L1-80 (HEADING + LEFT grammar)
             .agents/scripts/tests/run_all.py, .agents/scripts/sop_currency.py, check_links.py
             docs/_scc_sops_prds/workflows_testing_SOP.md:2785, .agents/rules/zoo-team.md:63
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  env -u GITHUB_TOKEN git fetch origin main, then git worktree list + per-tree diff
             twins: any cicd-*/smh-* sibling for an approvals door
             new command -> all launcher surfaces + .agents/commands/INDEX.md
             edited script -> .githooks/ callers + its test + .agents/scripts/INDEX.md
             file in >1 repo -> the plan's port section answers all six checks with output
             _artifacts/_memory/ row: is this the memory flow?
             risk_seam.py classify --repo <lane>
read:        git worktree list -> 2 trees (main @632f7583, this lane @7d8345ff) — NO sibling lane,
             so there is no landing-order dependency to name
             ls .agents/commands | grep -i "approval|permission|notif" -> none; no twin exists
             launcher surfaces measured on smh-self-audit: .claude/skills/, .opencode/commands/,
             .roo/commands/, .agents/workflows/, .agents/skills/  (FIVE, not four)
             grep -rn zoo_permissions_apply .githooks -> empty; no hook calls it
             risk_seam -> {"status":"unclassified","root":".../SCC-352-llm-approvals"} — correct and
             permanent in the centre (SCC-289); every judgement here taken from the diff
verdict:     findings below
```

```
lens:        3 Pre-Mortem (attaches narratives only; cannot originate a finding)
checks_run:  the silent one / the other-machine one / the fresh-clone one / sibling-lands-first
read:        the four survivors from lenses 1-2
verdict:     4 narratives attached, 0 unattached (nothing discarded)
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `implementation_plan.md` (heading) | `## Declared Change Set (combined, SCC-226)` | `declared_change_set.py`'s `HEADING` is `^##\s+Declared Change Set\s*$` — the suffix made `parse` return `present: false`. **Pre-mortem (the silent one):** `/smh-code-review`'s drift check reads absence as "nothing declared", so all 29 files present as undeclared drift and any real drift is buried in the noise — while the plan LOOKS complete on the page. **FIXED inline** | blocker |
| `implementation_plan.md` §Declared Change Set | `\| Op \| Path \| → acceptance \| Part \|` | the block was a markdown table; the parser accepts only `- <OP> \`path\` — why → rows`, so it yielded 0 entries even once the heading matched. **FIXED inline** — now 29 entries, 0 incomplete, 17 NEW | blocker |
| `implementation_plan.md` acceptance row A2 | ``run_all.py`` | there is no `.agents/scripts/run_all.py`; the real gate is `.agents/scripts/tests/run_all.py`. **Pre-mortem (the other-machine one):** an agent on the PC runs the named path, gets "no such file", and reports a gate green that never executed — the [[suite-red-file-may-have-run-nothing]] failure exactly. **FIXED inline** | important |
| `implementation_plan.md` §Declared Change Set | `\| EDIT \| changelog \|` | declared with no path at all; the real file is `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md`. **Pre-mortem:** `sop_currency.py` is an ARMED commit-msg gate, so a builder who edits the SOP and cannot find the changelog has their commit rejected mid-flow and reaches for `[sop-ok]` — silently retiring the gate this Task depends on. **FIXED inline** | important |
| `implementation_plan.md` step A4 | `plus generated launchers` | no `.agents/commands/INDEX.md` or `.agents/scripts/INDEX.md` row was declared. SCC-66's scar: a door on disk that no index names is how the platform caches drift apart. **FIXED inline** — both index rows added | important |
| `implementation_plan.md` step A4 | `- NEW generated launchers for \`smh-llm-approvals\` — one per platform` | prose where the grammar needs ONE repo-relative path; reported as `incomplete: 1`. Measuring a real door showed **five** launcher surfaces, not the four the parity row assumes. **Pre-mortem (the fresh-clone one):** the sandbox denies writes under `.claude/skills/` (SCC-300), so the sync cannot generate that one in-session and the door ships with 4 of 5 — SCC-351 hit this and hand-wrote its mirrors. **FIXED inline**, all five declared and the sandbox limit noted in the step | minor |

**All six are fixed in the plan above.** Re-verified after the fixes:
`declared_change_set.py parse` → `present: True, entries: 29, incomplete: 0, NEW: 17`, and every
entry carries an acceptance row.

### Observations (uncounted, no check behind them)

- The lane's diff already writes three files under `_artifacts/_memory/`, and Lens 2's row says that
  store is read-only outside its own flows. This is an operator-directed exception, not a slip — his
  instruction this session was to roll the loose files into this Task. Rather than except it
  silently, the plan now carries acceptance row **C1** so the Scope Ledger passes honestly.
- `.agents/rules/zoo-team.md:63` and `workflows_testing_SOP.md:2785` both cite
  `zoo_permissions_apply.py --apply`. Neither enumerates the CLI exhaustively, so adding `--suggest`
  is additive and breaks no prose — but the SOP row is the operator's usage page and is already in
  the declared set.
- Only two Zoo task dirs exist on this Mac, so Part A's reader will be developed against a thin
  real-world sample. The committed fixtures are what make its tests non-vacuous, not the live store.

### Sibling landing-order dependencies

None. `git worktree list` shows only `main` and this lane; no other branch is in flight against
these paths.

Audit verdict: GO

**Batch approval (2026-08-30):** "approved" — the operator's exact word, this turn, at the
`/smh-quick-dev` Step 1.5 gate; covers the plans listed in `/smh-plan-task SCC-352` Step 5:
**SCC-354** and **SCC-355**, this plan as it stood at `cc0fa92a` — recorded at `237cf3fc`.
