# The Sudo Dev System — changelog

**One line per change: date · ticket · what changed for the operator.** Newest first.

This file is where the change story lives, so that
[`workflows_testing_SOP.md`](workflows_testing_SOP.md) can state the *current* system in present
tense with no "since SCC-x" narration — the writing contract is
[`sop-currency.md`](../../.agents/rules/sop-currency.md) §Writing the update, habit 4. When the
SOP-currency gate makes you update the SOP, the delta description goes **here**, as one line, in
the same commit. Deeper history: `git log --follow` on the SOP, and the per-ticket session folders
under `_artifacts/_main/`.

The entries below were harvested from the SOP's own body during the 2026-08-21 de-clutter. A date
of `—` means the page recorded the ticket but not the day; the ticket's session folder under
`_artifacts/_main/` or the Jira board has the full record.

## 2026-08

| Date | Ticket | What changed for the operator |
|---|---|---|
| 2026-08-21 | SCC-246 | A memory written during a lane is copied into the lane's worktree and rides its PR; the shared checkout is restored (authorship still protects other sessions' memory). |
| 2026-08-21 | SCC-245 | Ninth speaking obligation (FLOOR): close the loop — a reply never ends on a new problem; a finding without a fix is a bill. |
| 2026-08-21 | SCC-211 | `/cicd-push-e2e` pre-flights (`ship_preflight.py` at Step 1.5, ticket pinned at Step 0.6); all three close-out doors derive which tree gets gated (`wf_common.trees_to_measure`); a `chore/*` branch is admitted only when its diff reaches deployable code. |
| 2026-08-20 | SCC-242 | `finish` resolves the landing target (flag → `task.yaml` `landing_ref:` → `origin/main`); the story door transitions via `finish`, not raw `acli`; `index-row` files inside the `INDEX` section; the rolling-ticket clone names the three edits it leaves owed. |
| 2026-08-20 | SCC-243 | Every `lane_qualify.py` caller lists every verdict it can return (test discovers callers by invocation); `/cicd-non-crit-pr-push` gains its own deployable-path check. |
| 2026-08-20 | SCC-240 | The lens roster is taught unfenced (the parser strips code fences); `walkthrough_roster.py` gains a CLI self-check run right after pasting; `declared_change_set.py` names why each `incomplete` bullet was rejected; the wrong-tree guard covers single-file test runs. |
| 2026-08-20 | SCC-231 | Step 1.5 reconciles the plan's `## Declared Change Set` block against the real diff (`undeclared` / `unimplemented` / `incomplete`; no block is itself a finding). |
| 2026-08-20 | SCC-232 | Step 0.7's measured blast radius resolves the review level (`quick` vs `standard`) — derived, never chosen; excluded lenses report `skipped-by-mode`. |
| 2026-08-20 | law | The `## Code Review` section is machine-read: `dispositions:` + `drift:` lines required; `walkthrough_roster.py` blocks lanes dated ≥ 2026-08-20 missing either. |
| 2026-08-20 | SCC-210 | Close-out rebalanced: `/cicd-close-story-merge-tree` is THE door (the Jira `Done` write moves AFTER the landing push); `/cicd-update-sprint-memory` slims to the save; the janitor is `/cicd-prune-worktree` (renamed so it stops reading like a close-out). |
| 2026-08-20 | SCC-206 | The Your-Actions reader's ride-along window closes on any list item; HTML comments are invisible to it. |
| 2026-08-19 | SCC-238 | The two non-crit push twins restore the checkout to `main` and pull after the GitHub merge. |
| 2026-08-19 | SCC-215 | *A decision* is banned as a `## Your Actions` row type — an agent asks in-session instead of parking questions on the board. |
| 2026-08-18 | SCC-222 | `/smh-non-crit-pr-push` created: routine docs/notes under standing ticket SCC-186 and branch `chore/SCC-186-standing-push`, straight to PR (`/cicd-non-crit-pr-push` is the child-project twin). |
| 2026-08-18 | SCC-209 | The `*-AP` autopilot twins are marked UNMAINTAINED pending a rewrite; `workflow_lint`'s `ap_reconciled` stamp retired. |
| 2026-08-17 | SCC-205 | Twin-parity guard: shared law fenced `twin-law` in both `/cicd-*`/`/smh-*` twins, symmetry + identity asserted; `check_both_machines` lint (`.venv/Scripts` vs `bin`). |
| 2026-08-17 | SCC-198 | `jira_feed.py start` clones the rolling ticket's successor the moment it moves to In Progress; `running-bug-list` is the one-ticket baton label. |
| 2026-08-17 | SCC-193 | Your-Actions content rule: the ceremony's own steps are refused as operator rows; decision-to-proceed IS the sign-off; `--after-merge` warns on stale door text; the preflight fetch is the default and staleness rides the verdict line. |
| 2026-08-17 | SCC-195 | `/smh-sync-agents` shortens workflow descriptions to 135 chars so Antigravity's menu keeps every workflow. |
| 2026-08-17 | SCC-175 | `finish` computes the merge row from ancestry at `HEAD` — a tick never closes a ticket on its own; the tick is committed on the lane before the PR opens. |
| 2026-08-17 | SCC-190/191/192 | Rolling "Bugs and Updates" ticket is rung 3 of look-before-mint; the close-out preflight leaves a receipt and `main-write-gate --mode pr` requires it; four honesty rules in the preflight and `finish`. |
| 2026-08-16 | SCC-183 | The road to `main` is a PR: the close-out opens it and prints the URL; your click on *Merge pull request* is how your decision reaches GitHub; the local landing ceremony is deleted. |
| 2026-08-16 | SCC-163 | Banned action rows (mint / file / rule-on-ticket) refused at close-out (armed after a measured zero-false-positive count); the merge backstop learns the epic-in-chore fast-forward case. |
| 2026-08-16 | SCC-171/172 | The main-push token gate fixed on the PC (git-dir path) and its three fail-open arms closed (plain commit, remote with no `main`, pre-gate worktree). |
| 2026-08-16 | SCC-187 | `evidence_extract.py` ranks caller snippets (`[importer]` / `[name-match]` / `[unranked]`), with a reserved slot for the weaker class. |
| 2026-08-15 | SCC-162 | Lightweight lane `/smh-quick-fix` created: command-centre work that cannot break the dev system — no plan, no `approved`, no review; qualification is `lane_qualify.py`, never judgement. |
| 2026-08-15 | SCC-164/170 | Consolidated Task mode: one lane for a whole Task with `riders:`; `work-consolidation.md` (six judgment rules). |
| 2026-08-15 | SCC-160 | Review triage relevance gate: a true finding must matter or die with a reason; a review never produces a ticket; survivors are fixed in the lane; `defer` only on a named structural blocker. |
| 2026-08-15 | SCC-165 | Stale-base-ref sweep: commands may not diff/cut against a local `main` nobody refreshed (21 fixed, 4 ruled correct-as-local). |
| 2026-08-15 | SCC-166 | Step 0.7 blast-radius re-derivation + Step 1.5 acceptance audit ported into `/cicd-code-review`, re-deriving against `origin/$EPIC`; `/cicd-push-e2e` addresses "the operator". |
| 2026-08-15 | SCC-174 | The Dev Record slug is read from the lane's `task.yaml` `branch:`, never typed; forked Dev Records detected by proof. |
| 2026-08-15 | SCC-176 | `port-checklist.md`: six mechanical checks answered at plan time for any centre↔project port, both directions. |
| 2026-08-15 | SCC-179 | `mutation_sweep.py` mechanizes the sweep rules; a hand-run sweep is the defect. |
| 2026-08-15 | SCC-180 | Suite fails any instruction line printing `git reset --hard`; `--keep`/`--soft` are the sanctioned rewinds. |
| 2026-08-15 | SCC-173/177 | `walkthrough_roster.py` blocks close-outs whose review left no lens roster (scope: lanes dated ≥ 2026-08-15); the engine returns the roster verbatim and runtime is probed at Step 0. |
| 2026-08-14 | SCC-155 | `/cicd-parallel-check` renamed `/cicd-label-tasks` (Task twin `/smh-label-tasks`); `finish` HOLDS a merged ticket with open Your-Actions rows (`user-tasks` label) instead of writing `Done`. |
| 2026-08-14 | SCC-156 | You act in words; the agent does every board write. Case-scoped mutation runs; rider subtasks on your order. |
| 2026-08-14 | SCC-37 | The merge-token mint refuses without your verbatim this-turn merge words (`--operator-approval`) or a terminal-typed key. |
| 2026-08-14 | SCC-144 | `commit-msg` merge-target guard armed (a merge onto a branch that is not a legal destination for its source is refused); the Jira/SOP gates' merge carve-out fixed inside worktrees. |
| 2026-08-14 | SCC-147 | The close-out never re-runs the LLM review — one review per lane, severity triage at close; Stage-4 `lens_budget` caps. |
| 2026-08-14 | SCC-149 | `claude/incident-*` positively classified: a STOP at story close-out; it lands only via `/cicd-mobile-error-team`. |
| 2026-08-14 | SCC-154 | Incident branch pairings with story/chore lanes positively refused; roster-in-code-fence failure identified. |
| 2026-08-14 | SCC-145 | Mutation doctrine surfaced as a Step 3 obligation (declared table, one sweep, code-derived mutants). |
| 2026-08-13 | SCC-128 | The shared review engine (`code-review-engine`) runs every review; the walkthrough's Code Review table is the authoritative record. |
| 2026-08-13 | SCC-133 | Close-outs record a flight event per lane (`flight_recorder.py`); a fingerprint seen in 3 lanes prints a proposal at session start; the save asks for learnings only when it routed none. |
| 2026-08-13 | SCC-138 | The Task close-out runs `check_maps.py --depth3-only --strict` as a blocking gate. |
| 2026-08-12 | SCC-118 | Server-side `main-write-gate` required check added — the half that covers merges made on GitHub itself; `.github/` counts as deployable only where something ships. |
| 2026-08-12 | SCC-119 | Subtask law: broken-out work goes UNDER its ticket; a subtask earns its own branch + worktree or stays a checklist. |
| 2026-08-13 | SCC-113 | The board moves itself at both ends: `post-commit` hook + command start-seams write `In Progress`; close-outs write `Done`; door-content parity checks added. |
| 2026-08-11 | SCC-94 | `secondary_repos` in `task.yaml` is checked mechanically by the preflight (reachable, keyed, clean, 0/0, memory integrity), with a landing-order warning. |
| 2026-08-11 | SCC-97 | Merge-target discipline after a merge landed on a sibling lane: `-C "$REPO"` on every git call, assert the target before merging. |
| 2026-08-10 | SCC-77 | `/cicd-push-e2e` sign-off became mechanical: single-use approval token, spent per push; `pre-push` refuses `main` landings without one. |
| 2026-08-10 | SCC-78 | Task lane created (`/smh-quick-dev` → `/smh-code-review` → close): a defined way to BUILD system work, not just land it. |
| 2026-08-10 | SCC-74 | Every procedural doc consolidated into `docs/_scc_sops_prds/` (this folder); the page renamed `workflows_testing_SOP.md`. |
| 2026-08-09 | SCC-56 | Parallel-safety ruling moved out of ① into its own command (a fact about a group at a moment). |
| 2026-08-09 | SCC-62 | The worktree trigger is concurrency, not work type: every committing lane gets its own worktree. |
| 2026-08-09 | SCC-63 | Command naming law: `cicd-*` / `smh-*` / `sentry-*` families, hyphens only, `sudo-` prefix retired. |
| 2026-08-09 | SCC-64 | Close-outs must be told the ticket (`--expect-key`); `task.yaml` written at task start; gates run unpiped. |
| 2026-08-09 | SCC-66 | One door per command per platform (Claude/Codex launcher skills; `.claude/commands/` and Codex prompts retired). |
| 2026-08-09 | SCC-71 | Incident recorded: one invocation rode six merges — permission-as-document does not expire; led to the token gate. |
| 2026-08-09 | ruling | Plan-approval gate hardened: "approved" may not appear in an agent-authored button label; `_my_resources/open_tasks/todo_list.md` retired as an agent source. |
| 2026-08-08 | SCC-51 | Plan/walkthrough byte caps removed — dense, not short; length is never a reason to drop a finding. |
| 2026-08-07 | SCC-31/AVCH-23 | Toolkit centralized: shared rules/commands/skills/BMAD live only in the command centre; a project carries only its own law. |
| 2026-08-07 | SCC-13/AVCH-10 | The scrum-board map and its command retired; the live Jira board is the view. |
| 2026-08-07 | AVCH-41 | AGY's twin copy of this page last synced; it has drifted since, and re-syncing is an AVCH ticket of its own. |

## Earlier

| Date | Ticket | What changed for the operator |
|---|---|---|
| 2026-07-14 | — | The quick reference carved out of `tea_deep_reference.md` as its own page. |
| — | SCC-123 | `evidence_extract.py`: the review engine's fact-fetcher (dossier before reasoning). |
| — | SCC-126 | Autopilot Stage 4 runs the house review engine via `/cicd-code-review-AP`. |
| — | SCC-134 | Autopilot "done means green": stage gates are script exit codes, never agent say-so. |
| — | SCC-203 | The runtime probe asks capability, never policy; a contaminated Blind Hunter is dropped (`n/a` + reason), not faked. |
