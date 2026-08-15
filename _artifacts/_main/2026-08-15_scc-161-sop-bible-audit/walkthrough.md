# Walkthrough — SCC-161 · the dev-system bible, audited and rebuilt

> **Lane:** `chore/SCC-161-sop-bible-audit` (worktree `.claude/worktrees/scc-161-sop-bible-audit`) · **Repo:** Sudo_Hatter_Command
> **Operator-directed, 2026-08-15:** *"audit this doc … make sure it's updated with all our changes … flows for easy reading … a section dedicated to all the commands with mermaid diagrams … not just the macro"*, then *"we are not running quick dev we are editing a doc thats all"*, then *"create a ticket, make the edits, push it."* No plan-first stop, no self-audit, no RED assertion — by that word. The lightweight lane this argues for is **SCC-162** (minted the same session on *"we will make a task for it"*).
> **Subject:** [`docs/_scc_sops_prds/workflows_testing_SOP.md`](../../../docs/_scc_sops_prds/workflows_testing_SOP.md) — 166 KB → 218 KB, 23 → 43 mermaid blocks, 6 → 7 Parts.

## Task Checklist

- [x] **Currency sweep** — every claim contradicted by the live toolkit fixed (ledger A below)
- [x] **Reading flow** — dense diagram nodes trimmed, the eight giant safety-net table cells relocated verbatim into a "history behind the checks" asides section, the main-gate material given its own heading, §19's reference tables moved ahead of their asides, pointers from each lane section to its atlas diagram
- [x] **The command atlas (Part VI)** — §17 *How the commands interact* (call graph · who writes the board · where each command stops for you) + §18 *Every command, one diagram*: 14 existing per-command diagrams moved and corrected, 19 new (ledger B)
- [x] Both labelling commands (`/cicd-label-tasks`, `/smh-label-tasks`) present in the lane sections, the reference tables, the §4 map, the Start-here table and the atlas — the operator's mid-turn check
- [x] Every mermaid block passes the house-subset linter (0 errors); two of the trickiest validated by the Mermaid renderer (`valid: true`); every `#anchor` link resolves (115 headings)
- [x] Gates green on the lane (Evidence)

## Evidence

| Gate | Result | Where |
|---|---|---|
| `python3 .agents/scripts/tests/run_all.py` (lane tree, after the rebuild) | **28/28 files passed · exit 0** | scratchpad `run_all_after.txt` |
| `test_sops_prds_folder.py` alone (links · T4 command refs · T9 prose paths · 12-doc manifest) | **61/61** — one T9 red on first run (a project-relative path in the AGY-twin sentence), fixed, re-run green | — |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, 8 info** | — |
| doc linter (`check_doc.py`, scratchpad): mermaid subset · anchors · node length | **43 blocks · 0 errors**; 16 nodes between 130–160 chars, none over 160 | — |
| Mermaid renderer spot-check (park/resume with two subgraphs + a cross edge; the review-engine fan-out) | `valid: true` both | MCP tool result |
| SOP-currency gate | this commit stages the SOP itself; no `[sop-ok]` needed | commit-msg hook |

Measured at 57297cc (the rebuild) and again at 1f5b6bf (after absorbing `main` = c9ca3ab, SCC-160's landing): `run_all` **28/28 exit 0**, folder test **61/61**, toolkit lint **0/0**, doc linter **43 blocks · 0 errors**.

## Findings ledger A — stale or wrong claims, fixed

| # | Was | Now | Ground truth |
|---|---|---|---|
| A1 | header "Current as of 2026-08-11" | 2026-08-15 | the page had moved on 2026-08-14/15 under SCC-133/155/156/159/160 without the date |
| A2 | "1861 checks across 23 files, measured 2026-08-13" | 28 files, ~2,270 checks, a minute and a half in parallel (SCC-156) | `run_all` on the lane |
| A3 | "Pins the 11-doc manifest" | 12-doc | `test_sops_prds_folder.py` T1/T6 (SCC-37 added `sharing_keys_secrets_secure.md`) |
| A4 | §12: SCC statuses `Blocking`; AVCH `In Review`; "Only SCC has `To Do Next`" | SCC live: `To Do · To Do Next · Blocking/Security Risk · In Progress · Done`; AVCH live: `To Do · To Do Next · In Progress · Review Required · Deferred · Done` | `acli` status counts on both boards, 2026-08-15 — **`jira.md` still says `Blocking`; a JQL on it returns nothing → open item O2** |
| A5 | §7: "Neither SCC nor AVCH currently has an `Awaiting Review` column" | AVCH has `Review Required`, the first rung of `finish`'s ladder; SCC has none | `jira.md` §finish ladder + the live board |
| A6 | §13: migrations kit "in `_my_resources/`"; arm hooks by hand only; secrets "from the hand-carried bundle" | kit is `docs/migrations/` (SCC-89); `install-git-hooks.sh` / `Install-GitHooks.ps1` arms + verifies (SCC-115); `env_master.py --restore` (SCC-39); Keyway for team keys (SCC-37/152) | `machine_setup_card.md`, the migrations INDEX |
| A7 | §15: "⚠️ Not yet run for real … Windows-only, no stage has executed" | proven end to end on Story 14.2 (spec header) | `autopilot_bmad_dev_loop.md` Status line |
| A8 | §15: "four separate sessions"; Stage 2 "different model"; "every launcher uses an underscore" | four stages in **three** sessions (Build resumes Dev); Stage 2 = fresh session, same model; launchers are hyphenated `cicd-autopilot-*` (SCC-63) | spec §4/§5b; `.agents/commands/` |
| A9 | §15 silent on the autopilot law | §6a *Done-means-green* stated (gate = exit code; bounded engine retries; park with receipt; auto-fix loop dropped, not deferred) | spec §6a (SCC-134) |
| A10 | "Where you are standing": AGY twin "body identical" | twin last synced 2026-08-07, a fifth the size, in AGY's un-scanned `_my_resources/`; this page canonical; re-sync = an AVCH ticket | `Projects/AGY_AVIATIONCHAT/_my_resources/_quick_reference/sudo_workflows_testing.md` @ 91d47613 |
| A11 | §6 story-lane overview: "STOP — you type 'approved'" for ② | "STOP — the plan is posted; you read it; your reply is the trigger", + ②'s BDD refusal | `cicd-dev-story-tests.md` Step 2 accepts `continue` / `changed` / a path — **open item O1** |
| A12 | §7 chooser: Task arm went straight to `/smh-close-task-merge-tree`; no incident arm | "how many Task lanes?" fork → `/smh-merge-multiple-workingtrees`; `claude/incident-*` → `/cicd-mobile-error-team` | the three close-outs' SCC-149 refusals; the altitudes table one screen above already named the multi door |
| A13 | §7 what-calls-what missing `/smh-merge-multiple-workingtrees` | added; both Task doors call neither janitor nor prune | the command bodies |
| A14 | §7 `/smh-close-task-merge-tree` prose silent on the CI wall | the `gate/main-<sha>` push, the `main-write-gate` wait, token minted **after** the wait (30-min TTL) | command Step 3 (SCC-118/156) |
| A15 | §7 `/cicd-update-sprint-memory` "three things" | + conditional learnings question (SCC-133), incident-branch STOP (SCC-149) | command Steps 6/7 |
| A16 | §8 fast lane: ad-hoc chore branch and "no story file" absent | stated | `cicd-quick-dev.md` Step 0.5 |
| A17 | §9 "Four commands" | seven; overview map gains `/smh-plan-task`, `/smh-label-tasks`, the eject, both close-out doors | §9's own subsections |
| A18 | §10 gates map: commit-side hooks only | + `merge-target-guard`, `post-commit-jira-start`, `pre-push-merge-backstop`, `pre-push-main-approval`, `flight_recorder`, `hooks_armed`, `label_tasks`, `evidence_extract`; `/smh-code-review`, `/smh-quick-dev`, both labelling commands added as callers | verifier agent's edge audit |
| A19 | §19 Task-lane table missing `/smh-plan-task`, `/smh-label-tasks`; Longer-reading missing 8 sibling docs | added | folder INDEX |
| A20 | Start-here table: no row for label-tasks / plan-task / merge-multiple / atlas | added | — |
| A21 | §3 Law 1 silent on ②'s wording | one ⓘ aside naming the unreconciled `continue` | O1 |
| A22 | §5 lane chooser: `.github/` listed as deployable unconditionally | ".github/ only in a repo that ships one of those" | `task_preflight.py` two-list rule (SCC-118) |

## Findings ledger B — the diagrams (four verifier agents, then rebuilt)

**Existing, moved to the atlas and corrected** (verdict before → what changed):

| Diagram | Before | Fixed |
|---|---|---|
| ① `/cicd-write-story-tests` | MINOR DRIFT | Step 1.6.4 board move (In Progress / Blocking), frontmatter stamp, "commit in worktree, do not push the epic", Step 1 may stop for input |
| ② `/cicd-dev-story-tests` | ACCURATE | Step 5's four items; Step 0.7 files-on-disk; Step 4 "Automate: skipped — why" |
| ③ `/cicd-code-review` | MINOR DRIFT | empty-diff STOP; `lens_budget: standard`; the engine's severity floor binds; receipts `unrunnable` = finding; Step 5 clears `## Your Actions`; "never lands, never flips" |
| `/cicd-quick-dev` | MINOR DRIFT | the ad-hoc chore lane; bug-fix eject + one pinning regression test; who resumes after the stop |
| `/cicd-update-sprint-memory` | MINOR DRIFT | conditional learnings question; incident STOP; Step 0.5 conflict STOP; receipt pre-check; Bug flag cleared at 4.5 |
| `/cicd-merge-epic-workingtrees` | MINOR DRIFT | incident lanes excluded from inventory; `done` lanes prune-only; conditional question; Step 6 `--repo/--branch` + echoed slug |
| `/cicd-close-workingtree` | MINOR DRIFT | **Step 1.7 drawn as its own gate BEFORE cleanup** (was buried in Step 5); remote delete only if on origin; 3c conditional |
| `/cicd-push-e2e` | MINOR DRIFT | chore-branch light-gate path; Step 4 pre-push summary STOP; token minted last; watch every run to success |
| `/smh-close-task-merge-tree` | STALE at Step 3 | the CI wall (gate ref → wait → mint → push); child STOP vs rider warn; refuses `epic/`, `claude/`, incident by name; a `claude/*` tree not its to prune |
| `/smh-quick-dev` | ACCURATE (nodes up to 658 chars) | trimmed to readable nodes; batch-approval bypass from `/smh-plan-task`; `## Your Actions` as a machine contract; absorb `main` at 0.5 |
| `/smh-code-review` | MINOR DRIFT | **removed the stale `check_maps` node** (it is the close-out's gate, not the review's); Step 5 clears `## Your Actions`; DIFF/HEAD re-taken after the absorb |
| §13 park/resume | MINOR DRIFT (one false claim) | resume no longer "checks out the epic branch"; dual scope; the gitlink guard; card rides a story branch; `--ff-only` divergence STOP |
| §15 autopilot | MINOR DRIFT | same-model audit; three sessions; the baseline-differential gate + `REVIEW INCOMPLETE`; the parking states; the worktree open |
| §16 incidents → `/cicd-mobile-error-team` | MINOR DRIFT | runbook STOP at Step 0; the two early exits; Step 9 close-the-loop |

**Lane-level maps kept in place and corrected:** §4 lifecycle (all commands incl. label-tasks, plan-task, merge-multiple, quick-dev); §6 story overview (A11); §7 chooser + what-calls-what (A12/A13); §7 branch model (chore-handoff light gate; incident lane; token wording); §9 Task-lane overview (A17); §10 gates (A18). §5, §11 unchanged.

**New in the atlas (19):** `/cicd-boot-sprint-memory` · `/cicd-create-epic-sprint` · `/cicd-label-tasks` + `/smh-label-tasks` (one engine, two entries) · `/smh-plan-task` · `/cicd-bdd-tests` · `/cicd-self-audit` · `code-review-engine` · `/cicd-clean-code-audit` + `/smh-clean-code-audit` (one shape, two floors) · `/smh-self-audit` (two modes) · `/cicd-e2e` · `/smh-merge-multiple-workingtrees` · `/cicd-prune-context` · `/cicd-live-testing-team` · `/smh-sync-agents` · `/smh-memory-audit` · `/smh-update-maps-indexes` — plus §17's three interaction views (call graph · who writes the board · where each command stops for you, a table).

**Not diagrammed, on purpose:** `/smh-adviser-board` (not part of the dev process; stays in the tables and the §4 map), the BMAD vendor bridges (`dev`, `pm`, `qa`, `sm`, `tea`, `analyst`, `architect`, `tech-writer`, `ux-designer`, `bmad-help`, `bmad-master`, `testarch-*`), the `-AP` twins (robot-only, covered by the autopilot entry), `/smh-review`, `/smh-new-project`, `/smh-slash-command-updating`, `/sentry-security-team-avch`.

## Decisions

- **The atlas is the single home for per-command diagrams.** Parts III/V keep prose, the WHY asides, and the lane-level maps; each command subsection carries a one-line `▶ Diagram:` pointer. No diagram appears twice — a duplicated diagram is one the SOP gate would let drift.
- **Relocate, never truncate.** The eight table cells over 900 chars were split at their first ⚠/⛔/⭐/ⓘ marker: the refusal stays in the row, the rest moves **verbatim** into "The incident history behind the checks". `task_preflight`'s "no override flag" sentence was moved back into its row by hand because the split had left the row too thin.
- **Describe what the command does, flag the law.** ②'s stop is written `continue`/`changed`; the page now says so and names the tension with Law 1 rather than pretending either away (O1).
- **Node budget:** ≤ ~130 chars, ≤ 4 lines, detail in prose. Sixteen nodes sit between 130 and 160 (dense close-out steps); none over 160.

## Pitfalls

- A Python heredoc with `\n` inside a non-raw triple-quoted string wrote **real newlines** into one mermaid block (the maps-indexes one) — caught by the linter's "unbalanced quotes" check, not by eye. Author mermaid replacement text as raw strings.
- `test_sops_prds_folder.py` T9 resolves **every backticked path in prose** against disk — a project-relative path (`_my_resources/_quick_reference/…`) written in the lobby's page reds it. Name the folder and the file separately.
- A background `Bash` call does **not** inherit a `cd` from a compound command in an earlier call reliably — the suite was launched three times before it ran in the lane tree. Put the `cd` in the same command line every time.

## Follow-ons (not tickets — evidence for the operator)

- **O1 — ②'s wording vs Law 1.** `cicd-dev-story-tests.md` Step 2 accepts `continue`/`changed`/a path; `000-PLAN-FIRST-GATE.md` lists `continue` as *not* approval. One of them should move; the page now describes the command and flags the gap.
- **O2 — `jira.md` names the SCC blocking status `Blocking`; the board says `Blocking/Security Risk`.** A JQL on `"Blocking"` returns nothing today (SCC-157 sits in the renamed status). Rule edit, its own ticket.
- **O3 — the AGY twin** (`sudo_workflows_testing.md`, 2026-08-07) is a fifth of this page. Re-sync or retire is an AVCH ticket.
- **SCC-162** — the lightweight lane, minted on the operator's word this session.

## Your Actions

- [x] **The merge itself** — signed off 2026-08-15: you invoked `/smh-close-task-merge-tree` (twice — the first run was stopped by the Claude Code auto-mode permission classifier at the merge step; nothing had landed). Branch pushed, `0 0` clean, `main` (c9ca3ab, SCC-160's landing) absorbed at 1f5b6bf; its three SOP hunks merged clean and its second ruling is reflected in the review diagrams. Preflight `clear to close out and merge` (LANE: LOCAL, GATES: ARMED); full gate green at the lane tip: `run_all` 28/28 exit 0 · `workflow_lint --toolkit-only` 0/0 · `check_maps --depth3-only --strict` exit 0 · folder test 61/61. Flight event not recorded — no `Verdict:` sha to key on (no review on this lane, by your word).
