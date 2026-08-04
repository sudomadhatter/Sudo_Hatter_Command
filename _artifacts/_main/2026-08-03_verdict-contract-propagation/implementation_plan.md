---
IsArtifact: true
ArtifactMetadata:
  title: Propagate the verdict-reading contract across commands + maintained projects
  type: implementation_plan
  date: 2026-08-03
---

# Plan — verdict-contract propagation

Follow-on to [the board/doc refresh](../2026-08-03_scrum-board-workflow-doc-refresh/implementation_plan.md).
Ad-hoc infra: `main_debug`, no worktree, no story key, explicit paths only.

**Problem.** The board now reads a verdict from the one place it lives and checks it isn't stale. The
question was whether every other agent/command/project needs the same. I swept them. **One real gap,
one one-liner, everything else already correct** — three of those correct *by design*, recorded here so
nobody "fixes" them later.

## The sweep — what actually reads a verdict

Authority: [`artifacts-always-first.md:210-212`](../../../.agents/rules/artifacts-always-first.md#L210-L212)
— *"`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <reviewed-sha>` … any code/test diff between that SHA and HEAD
invalidates the verdict."* Every reader below was checked against that line.

| Reader | State | Why |
|---|---|---|
| [`sudo-boot-sprint-memory.md:41`](../../../.agents/commands/sudo-boot-sprint-memory.md#L41) | ⛔ **GAP** | Classifies `reviewed → /sudo-update-sprint-memory` from `sprint-status.yaml` **alone**. Zero mentions of `Verdict:`, `## Code Review`, or `walkthrough.md` in the file. Same defect as the board — in the command that runs at the **start of every session**. |
| [`sudo-resume.md:57`](../../../.agents/commands/sudo-resume.md#L57) | ⚠️ minor | Same YAML-only inference when reporting a branch's "step", but it defers to boot (`:84`) and its real job is the git surface. One-line fix. |
| [`sudo-merge-epic-workingtrees.md:34`](../../../.agents/commands/sudo-merge-epic-workingtrees.md#L34) | ✅ correct | Already reads `Verdict: … @ <sha>` from `## Code Review` **with** the pre-08-02 fallback. No own staleness check, but hands to `closeout_preflight.py`, which has one. |
| [`closeout_preflight.py:194-211`](../../../.agents/scripts/closeout_preflight.py#L194-L211) | ✅ correct | Strongest link — parses `verdict, sha`; warns on a missing `@ <sha>` (*"staleness CANNOT be checked"*); diffs `{sha}..HEAD`; warns when the SHA isn't in the repo. |
| [`sudo-update-sprint-memory.md:82`](../../../.agents/commands/sudo-update-sprint-memory.md#L82) | ✅ **by design** | Fails **open** on a stale verdict — *"ONLY objectively-red tests block the flip."* Close-out is the human's sign-off: the board *recommends* re-review, close-out must not *forbid* landing. |
| [`sudo-quick-dev.md:12`](../../../.agents/commands/sudo-quick-dev.md#L12) | ✅ **by design** | Runs **no** adversarial review — human review is the gate. There is no verdict to read. |
| autopilot (4 launchers / 3 engines) | ✅ **by design** | Resume keys on *section presence* — "did Stage 4 run?" — not landability, and already carries the legacy fallback ([`ref:343-346`](../../../.agents/reference/autopilot_bmad_dev_loop.md#L343-L346)). Flips only to `review`, **never** `done` ([`autopilot_claude.md:182-187`](../../../.agents/commands/autopilot_claude.md#L182-L187)); SHA is fresh by construction since Stage 4 just ran. |

No `_AP` twin exists for boot or resume (only code-review / dev-story-tests / self-audit have twins).

## WS-A — teach `/sudo-boot-sprint-memory` where a verdict lives

Modify [`.agents/commands/sudo-boot-sprint-memory.md`](../../../.agents/commands/sudo-boot-sprint-memory.md)
— Step 2b only. Boot stays **discovery-only and read-only**: this changes what it *recommends*, never
what it writes.

1. **Replace the "Next command" bullet** (`:41-42`). The `review` case stops being a YAML lookup:
   - not-started → `/sudo-write-story-tests` · mid-dev → `/sudo-dev-story-tests` (unchanged)
   - status `review` → **open that lane's `_artifacts/epic_*/story-*/walkthrough.md` and read the first
     line of `## Code Review`.** No section and no legacy `sudo-code-review-<story>.md` = the review
     never ran → `/sudo-code-review`, whatever the YAML says. `FAIL`/`CONCERNS` → `/sudo-code-review`.
     `PASS`/`WAIVED` whose `@ <sha>` **is** that branch's HEAD → `/sudo-update-sprint-memory`. `@ <sha>`
     that is **not** HEAD → code landed after the review → `/sudo-code-review`, never close-out.
2. **Legacy fallback** — pre-08-02 lanes keep a standalone `sudo-code-review-<story>.md` /
   `code-review.md`: **read-only history**, fall back to it, never write a new one. (Board's wording
   verbatim, so the two can't drift.)
3. **⛔ A live worktree wins over the YAML.** Boot already runs `git worktree list` two bullets down but
   never says the tree outranks `sprint-status.yaml`. Board hard-rule parity.
4. **⛔ Never recommend a `descoped` / `deferred` story.** Board hard-rule parity; both rules were paid
   for by incidents.

~14 lines into a 74-line file; stays well under the 11,500 B Antigravity launcher threshold either way
(verify after sync regardless).

## WS-B — `/sudo-resume` one-liner

Modify [`.agents/commands/sudo-resume.md:57`](../../../.agents/commands/sudo-resume.md#L57) — after
"report the whole set", add that a `review` status is **not** proof the story is landable and that boot
resolves it from the walkthrough. Resume must not grow boot's logic; it points.

## WS-C — commit the already-synced board command in the maintained projects

[Fresh_Workspace_BMAD](../../../Projects/Fresh_Workspace_BMAD/) and
[NEXgen-VR-Director](../../../Projects/NEXgen-VR-Director/) already hold the **byte-identical** master
(`cmp`-verified last session) but have it **uncommitted**. Both are on `main_debug` at `0 0` vs
`origin/main_debug`, dirty in exactly the `.agents/` + `.claude/` + `.opencode/` copies of
`sudo-update-scrum-board.md` — so each is a clean 3-file commit.

⚠️ **Needs its own in-the-moment "approved"** — two more repos on `main_debug`, and approval does not
carry across repos. NEXgen is a bare gitlink from the lobby, so its pointer moves too; that lobby-side
bump is **not** in scope (already dirty from prior work).

## WS-D — propagate

`/sync-agents` then `-Maintained`. Do WS-C's commits **after** the sync, so the boot/resume edits land in
the same commit as the board command instead of leaving a third dirty state behind.

## Not in scope — decided, not skipped

- **The AGY quick-reference docs need no edit.** `sudo_workflows_testing.md:83` describes boot as
  *"tells you the next story and which command to run"* — true before and after; its other four mentions
  are nav rows (grep-verified).
- **`sudo_artifacts_and_gates.md` does not get copied into Fresh/NEXgen.** It is thick with AGY specifics
  (278 s suite, Cloud Run, Sentry, SERIAL pinning), and the contracts it *describes* live in
  `.agents/rules/`, which all three projects already get via sync. Three copies = three bodies to drift —
  the exact failure my last audit flagged. Say the word if you want it anyway.
- **`/sudo-update-sprint-memory`'s fail-open stays.** Correct as written; recorded so it doesn't get
  "fixed" into a blocker later.

## Verification

| # | Check | How |
|---|---|---|
| 1 | Boot names the verdict source, the staleness rule, the legacy fallback, worktree-wins, and no-deferred | grep the 5 markers in the file |
| 2 | Boot's wording matches the board's (no drift between the two) | diff the two ⛔ blocks side by side |
| 3 | Boot is still read-only / discovery-only | grep for any write verb added — must be 0 |
| 4 | Every path and `/command` the new text names resolves | scripted, same checker shape as last session |
| 5 | Sync clean; AGY/Fresh/NEXgen `.agents` + `.claude` + `.opencode` copies byte-match master | `cmp` per copy |
| 6 | Fresh + NEXgen commit is exactly 3 files each, `0 0` after push | `git status --porcelain` + `rev-list --count` |

No code changes → no test suite in scope; these are directive Markdown files.

## Risk

Low: two Markdown command files, plus two 3-file commits in repos already clean and in sync. The one
real hazard is **wording drift** between boot and the board — verification #2 exists for that.
