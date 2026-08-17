# RESUME STATE — SCC-190 (written 2026-08-17, before a context compaction)

**Delete this file at close-out.** It exists only so a fresh context can pick this lane up without
re-deriving anything from chat.

## The lane

| | |
|---|---|
| branch | `chore/SCC-190-bugs-and-updates-2026-08` |
| worktree | `.claude/worktrees/SCC-190-bugs-and-updates` |
| HEAD at write time | `154d3e2` — pushed, tree clean, `origin/main` absorbed |
| parent | SCC-190 (In Progress, labelled `bugs-and-updates`) |
| riders | SCC-191 (R) · SCC-192 (S) · SCC-193 (T) · SCC-195 (U) — **full** landing, no `landing_mode` key |
| operator approval | `approved`, recorded in `implementation_plan.md` at `97f5a97`; S6 settled as *"i wording only"* |

## What is DONE (all committed, all on disk)

- **All four parts built and green.** Part S (preflight receipt + PR-gate demand), Part T (fetch
  default, freshness on the verdict line, `ceremony_rows`, stale-door line, SCC-175 pin, the
  sign-off wording everywhere), Part R (Rule 1's fourth rung + the cycle), Part U (the Antigravity
  menu budget in the generator; 13,883 → 4,590 chars).
- **Mutation sweeps: 22/22 killed** across three rounds — `sweep-part{S,R,T,U}.json` and their
  `-result.txt`. Ten findings, every one a weak assertion of this lane's own, all closed by cases.
- **Suite receipt**: `gates/suite.json` — `pass`, exit 0, 33/33 files, `dirty_tree: false`, 116.6s.
- **Lint + maps**: `workflow_lint.py --toolkit-only` 0 errors · `check_maps.py --depth3-only
  --strict` exit 0.
- **Blast radius re-derived** (review Step 0.7) against current `main`: SCC-186 landed 4 files
  (`.vscode/settings.json`, two `_artifacts/_memory/` files, `_my_resources/.../quick_push_git_main`).
  **Zero overlap, and none of them is a gate, script, command, rule or SOP surface** — so the
  gates-not-files hazard does not apply. `main` absorbed at `154d3e2`, merge clean.
- **Board**: SCC-190 labelled `bugs-and-updates`, read back through the rule's own jql.

## What was IN FLIGHT at compaction

Three review lenses were running in the background against the diff at `154d3e2`
(`review-runtime: fan-out`): **Blind Hunter**, **Edge-Case Hunter**, **Acceptance Auditor**.

⛔ **If their results did not survive the compaction, RE-RUN THEM.** Do not write a verdict without a
roster — `walkthrough_roster.py` blocks the close-out on a `Verdict:` with no `lenses_run:` block,
and correctly so.

## What REMAINS, in order

1. **Finish `/smh-code-review`** — lens findings fixed *in thread* (never a new ticket: operator
   ruling 2026-08-15), then the acceptance audit, then Step 3's floor, then
   `/smh-clean-code-audit`.
2. **Append to `walkthrough.md`**: `## Code Review (2026-08-17)` carrying the `lenses_run:` roster
   **verbatim** and the canonical `Verdict: PASS|CONCERNS|FAIL|WAIVED @ <sha>` line.
3. **Dev Record** — `jira_feed.py devrecord --key SCC-190 --stage quick-dev --walkthrough <this
   folder>/walkthrough.md ... --apply`. ⛔ Never pass `--story` (SCC-174: it forks the record).
4. **Delete this file**, commit, push.
5. **`/smh-close-task-merge-tree`** — invoked by the operator. It will exercise this lane's OWN new
   machinery: the preflight now writes `preflight-receipt.json` here, Step 2.5 commits it beside the
   flight event, and `main_write_gate --mode pr` will REFUSE the PR if either is missing. That is
   the intended dogfood; if the PR check goes red on receipts, the cause is a skipped ceremony step,
   not a bug to work around.
6. At `--after-merge`: riders SCC-191/192/193/195 flip to Done first, **then** SCC-190 — and per
   SCC-190's own description, **clone a fresh rolling ticket with no subtasks** and label it
   `bugs-and-updates`. That is the cycle Part R just wrote into the rule.

## Things a fresh context will otherwise get wrong

- **`## Your Actions` in this walkthrough is deliberately minimal** — one ticked ledger row. Do not
  add "click Merge" or "re-invoke the door" rows: `jira_feed.py` now **refuses** the close-out on
  exactly those (this lane built that check).
- **Memory files are LISTED, never edited** (SCC-193 S7). Four are named in the walkthrough for the
  operator to rule on. The `_artifacts/_memory/` changes in this branch's history came from the
  `origin/main` absorb (SCC-186's), not from this lane.
- **The `.opencode/` and `.agents/workflows/` mirrors are GENERATED.** If a door needs changing,
  edit `.agents/commands/` and re-run `pwsh .agents/scripts/sync-agents.ps1 -NoGlobals`
  (`-NoGlobals` deliberately: the machine caches keep `main`'s content until this lands).
