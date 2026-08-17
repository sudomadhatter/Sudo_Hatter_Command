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

## ⚠ MID-REVIEW STATE (updated 2026-08-17, second compaction)

**Two of three lenses have REPORTED and their findings are FIXED IN THREAD:**

- **Acceptance auditor** — five gaps, all fixed at `4ae4cf5`: the SOP's own table row kept the
  retired wording; the S5 pin never globbed `.agents/scripts/tests/`; `main_write_gate.py` had zero
  declared mutation coverage (now `sweep-partSB.json`, 7 mutants); **the door never invoked
  `check-actions` at Step 3 although the SOP claims it does** (fixed — that claim was the sharpest
  find); the stale-door line was missing from the hand-authored `SKILL.md`.
- **Edge-case hunter** — 15 findings, every one executed rather than inferred. **Fixed so far
  (uncommitted at the time of writing, verified 48/48):** a `null` receipt passed the ENTIRE gate
  (`json.loads("null")` is `None`, and the guard skipped every assertion); any non-object JSON
  crashed it with `AttributeError`; the gate judged OTHER lanes' landed manifests (57 of them on
  `main` have no receipt — now skipped by branch, with the reason printed); `verdict_sha` was
  written and never read, so a stale receipt vouched for code it never saw; a quoted (non-ASCII)
  path silently skipped a lane — a BYPASS, now `-c core.quotepath=false`; `subtask.yaml` matched
  as `task.yaml`; and an `UnboundLocalError` in the gate's own failure path.

**⛔ STILL TO FIX from the edge-case lens (all proven, none started):**
  - **#5** two agreeing manifests ⇒ no receipt written AND the preflight says nothing (VERDICT
    still reads "clear") ⇒ the PR then demands a receipt nothing will write. `check_manifest`
    must ERROR on ambiguity instead of reporting both as INFO.
  - **#6** the `MERGE_PHRASE` exemption is a WHOLE-ROW bypass: appending "the merge itself" to
    SCC-164's exact defect row clears it. Tighten to the ledger SHAPE, and **flip `B3b`** — that
    control currently asserts the bypass is correct.
  - **#7** `\bthen\s+(?:invoke|run|call)\b` refuses genuine operator decisions ("Rule the landing
    order, then run the campaign") with exit 2, armed. Bind it to a ceremony object.
  - **#8** `UnicodeDecodeError` escapes `except OSError` in `write_receipt` (a corrupt receipt
    kills the whole preflight).
  - **#9** the self-dirt exemption is not lane-scoped, contradicting its own comment.
  - **#14** a CRLF brain loses its `\r` on the description rewrite; **#15** `cmd_finish` returns on
    the first family so banned rows are never reported in the same run.
  - **#11/#13** latent/cosmetic: astral-character length divergence PS vs Python (0 divergences
    measured today); a stale `-> None` annotation.

**Blind Hunter has NOT reported.** Its findings are still owed before any verdict.

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
