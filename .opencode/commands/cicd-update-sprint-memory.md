---
description: The story SAVE — read the session's artifacts, code-verify the claimed work, route every learning to its home, apply the board / story / active-context updates, flip the closed story to done, and prune the context budget. It performs NO landing, NO ticket write and NO prune of a worktree — that is the door, /cicd-close-story-merge-tree, which invokes this as its Step 1. Runnable standalone any time a session needs saving.
platforms: [opencode, antigravity]
---

# /cicd-update-sprint-memory — the Session / Story SAVE

> **Rules in force for this command:**
> - `.agents/rules/worktree-per-story.md` — one worktree per story, resolve-or-STOP; the save is authored INSIDE
>   the story's tree so its edits ride the story branch
> - `.agents/rules/artifacts-always-first.md` — the walkthrough is the closing doc; learnings route to their homes
> - `.agents/rules/git-policy.md` — the standalone path absorbs the epic branch with a merge; explicit paths only,
>   never force, and ⛔ **no push lives in this command at all** — the landing is the door's

Self-contained, project-scoped — targets THIS repo's `_bmad-output/`. Run it as the save at the end of a story
(or any dev / brainstorm / research session). **Active-context holds STATE, not history** — narratives go to
the walkthrough + git, durable cross-session facts to the memory store; this keeps `active-context.md`
small so `/cicd-boot-sprint-memory` stays cheap.

⭐ **This command does exactly what its name says, and since SCC-210 nothing more.** It used to be the whole
story close-out: it landed the branch on the epic branch, moved the Jira ticket, filed the Dev Record and called
the prune — so the command an operator typed to close a story was named after a side effect of doing it. Those
four steps live in **`/cicd-close-story-merge-tree`**, the door, which invokes this command as its Step 1. The
split is not cosmetic: the ticket write is a **remote** write that rides no branch, and it used to happen ~100
lines and three STOPs before the landing push, so a stopped landing left the code on one disk under a ticket that
read `Done`.

⛔ **Everything this command writes is a FILE write, and that is what makes it safe to run before the landing.**
The board, the story frontmatter, `active-context.md` and the memory files all ride the story branch. If the
landing stops, none of them is published. Nothing here reaches a remote — deliberately.

**Two ways in, and they differ only in what has already been done for you:**

| Invoked by | What is already true | What you do |
|---|---|---|
| **`/cicd-close-story-merge-tree`** (the normal path) | the target is bound, the epic branch is absorbed, and the preflight has run — its block is your evidence | skip Step 0.5/0.6's work, read the block it hands you, start at Step 1 |
| **you, directly** | nothing | run Step 0.5 and Step 0.6 yourself, then Step 1. The save is complete on its own; the landing is simply not part of it |

⛔ **On the standalone path, Step 4's `done` flip leaves THREE things owed, and you must say so.** The flip
writes two files; it does not land the branch, file the Dev Record, or move the Jira ticket — and since
SCC-210 no step in this command does. So a story saved this way reads `done` on the board and in its
frontmatter while its ticket still reads `In Review` and its code sits on one disk. That is the same
two-surface divergence the rebalance exists to remove, pointing the other way, and the honest answer is not to
withhold the flip — the operator's invocation IS the sign-off for it — but to **print what is still owed and
name the door that settles it**:

```
Session save applied · <story> review → done (files only)
STILL OWED: the landing on epic/<EPIC-KEY>-<slug> · the Dev Record · the ticket move
→ run /cicd-close-story-merge-tree <story> to settle all three (it re-runs this save first; idempotent)
```

Print those two lines whenever this command was **not** invoked by the door. Invoked by the door, they are
its Steps 3–4 and it will do them, so say nothing.

**Your invocation — of this command, or of the door — IS the sign-off for the story flip in Step 4.** Only an
objectively-red `FAIL` verdict blocks it.

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** *"Which project are we closing out?"* —
never guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>`
before any work; every bare path below resolves under `PROJECT_ROOT`, and a needed project path missing
there → STOP and say so. ONE exception to §BIND: Step 6's Claude auto-memory write always targets Daniel's
global memory dir.

## Step 0.5 / 0.6 — Sync and preflight: the door has already done these

**Invoked by `/cicd-close-story-merge-tree`?** It absorbed the story's epic branch at its Step 0.5 (echoing
`Base: current with origin/epic/<JIRA-KEY>-<slug> @ <sha>`) and ran the preflight at its Step 0.6. **Do not re-run
either** — read the preflight block it hands you; it is the evidence for Steps 1, 2 and 4, and re-running it
costs a fetch and answers nothing new.

**Standalone?** Do both yourself before you read or edit anything, because Steps 1–4 rewrite the two hottest
files in the repo and authoring those edits on a stale base is discovered at merge time, not now:

```bash
git fetch origin epic/<JIRA-KEY>-<slug>
git rev-list --count HEAD..origin/epic/<JIRA-KEY>-<slug>    # >0 → behind
git merge origin/epic/<JIRA-KEY>-<slug>                     # CONFLICT → STOP and report, never force

python3 .agents/scripts/closeout_preflight.py --story <id> --project <PROJECT> \
       --expect-key <JIRA-KEY> --branch <name> --worktree <path>
```

⛔ **`--expect-key`, `--branch` and `--worktree` are not optional.** `cwd` is not intent: the script walks up from
`cwd` and guesses branches, so a sibling lane that moved the shared checkout becomes the target and every check is
reported honestly about the **wrong** branch. **Check the target it echoes before you read its verdict.**
**Exit 2 = BLOCKED — with ONE expected exception.** The `landed` check asks whether the story branch is already
an ancestor of its epic branch, and this command runs **before** any landing (its own or the door's), so a
healthy lane reports `[ERROR] landed: … has N commit(s) NOT on epic/…` and exits 2. That row is expected here;
every other error is not. **Read the rows, never the exit code alone** — an `intent` error means the wrong
lane, and that one always blocks. A verdict carrying **STALE** was computed against the last fetch, not the
remote; the line names which remedy applies (a failed fetch is an uplink to fix, `--no-fetch` a flag to drop).

## Step 1 — Read current state & this session's artifacts (scoped — no needless whole-file reads)
1. `_bmad-output/active-context/active-context.md` — full (about to prune it).
2. `_bmad-output/implementation-artifacts/sprint-status.yaml` — **Grep THIS story's id; read only its epic block + line**, never all 400+ lines.
3. `_bmad-output/component-specs/` — names only; open one only when routing a learning into it (Step 3).
4. `_bmad-output/project-context.md` — ONLY if a learning looks app-wide (check for an existing rule first); else skip, its rules loaded at boot.
5. This session's `_artifacts/<YYYY-MM-DD>_<slug>/` — the TWO living docs: `implementation_plan.md` (carries `## Self-Audit`) + `walkthrough.md` (carries the `## Task Checklist` outline, `## Evidence`, `## Suite Ledger`, `## Code Review` with the verdict, and `## Your Actions` — everything close-out needs is in this ONE doc). **Skip anything already read THIS session.** **If `walkthrough.md` ends with a `## Close-Out Handoff` block** (autopilot Stage 4 writes one), that is the AUTHORITATIVE pre-routed learnings — Step 3 lifts it, no re-deriving.
6. **Cross-reference plan vs walkthrough** for plan-vs-built deltas — unless already surfaced this session.

Report: sprint objective, story status, plan-vs-walkthrough deltas, # known pitfalls.

## Step 2 — Verify the claimed work exists on disk (grep-check — NOT a code review)
**Step 0.6 already did the file-level half**: its `file-list` lines check every path the story CLAIMED
it changed against the tree — tracked ✅ / untracked-never-committed ⚠️ / absent ❌. Do not redo it by
hand; an `ERROR: claimed but ABSENT` there means the work was renamed or never landed, and it blocks.
What remains for you is the *semantic* half — that the named fix is actually present in those files.
Code-verify the story/task you just closed: grep its fix/feature in the files it touched, mark
`✅ Code-Verified` / `❌ Not Found` / `⚠️ Partial`. After an /autopilot run it's already tests-green +
QA-approved — a confirming grep is enough; don't re-run the suites. Only RE-verify a pre-existing
`## Active Tasks` entry if THIS session changed its files. Human-gated carryovers (pending live-QA / deploy)
can't be grep-advanced — leave as-is. Queue every `✅` to move to `## Completed Tasks`.

## Step 3 — Route each learning to the RIGHT home (the 4 homes)
**If `walkthrough.md` has a `## Close-Out Handoff` block, LIFT it:** its four sub-sections map 1:1 to the
four homes below — route each item to its tagged home. Pre-sorted by the doer, so
do NOT re-derive. **Only if there is NO such block** (a manual, non-autopilot session) categorize every
learning yourself:
- **New architecture rule / invariant (app-wide)** → `_bmad-output/project-context.md` (`## Critical Architecture Rules`)
- **New component pitfall / gotcha / failure mode** → `_bmad-output/component-specs/<spec>.md`
- **New bug discovered (still open)** → `active-context.md` (`## Active Tasks`)
- **Cross-session fact / recurring pitfall / Daniel preference (NOT component-scoped)** → a Claude
  auto-memory file **+ a one-line `MEMORY.md` pointer. Collect here; validated + written automatically in
  Step 6, no approval gate** (frontmatter spec there).

Append format for specs/rules: `- **YYYY-MM-DD**: [description]. (Source: session artifacts)`.

## Step 4 — Apply updates (specs / rules / active-context now; memory waits for Step 6)
- **Every active-context entry is BORN as a pointer — ≤3 lines: outcome · STILL-OWED · pointer** to where
  the record actually lives (the map in `/cicd-prune-context`). The narrative goes in `sprint-status.yaml`'s
  story line + the walkthrough, NEVER here — active-context POINTS at information, it does not restate it.
- **Completed tasks**: move `✅` items to `## Completed Tasks` with `- **Resolved:** YYYY-MM-DD` (pointer form).
- **Story-status → `done` (this command's PRIMARY purpose).** The operator invoking this — or invoking
  **`/cicd-close-story-merge-tree`**, which invokes this — **IS the
  sign-off** — **flip the just-closed story to `done` by default, without asking.** ⛔ The flip writes two
  FILES and nothing else; it publishes nothing until a landing does, which is why it is safe here and why the
  ticket write that is *not* safe here lives in the door instead (SCC-210). Do it with the
  script, never by hand-editing two files:

  ```bash
  python3 .agents/scripts/story_status.py set <id> done --project <PROJECT>
  ```

  It writes the story frontmatter **and** the board key in one operation **or neither** — the two
  surfaces drifted apart repeatedly when this was two manual edits (six stories were found drifted on
  2026-08-03 alone). It refuses a downgrade, refuses an unknown status, and refuses outright if the two
  surfaces already disagree — that case needs `--reconcile`, which is a decision, not a default.
  It prints `board X -> Y, frontmatter X -> Y`; echo that as `Closing <story>: review → done`.
  Idempotent: only `ready-for-dev`/`in-progress`/`review` advance; never downgrade.
  - **Gate evidence (advisory this sprint, hard after):** if the story recorded gate receipts, confirm
    them before the flip — `python3 .agents/scripts/gate_receipt.py check --story <id> --require
    <gates> --advisory`. A receipt proves the gate RAN, at which commit; prose cannot.
    ⏳ Remove `--advisory` at the close of the first full sprint after this landed (ruling 2026-08-02).
  - **ONLY objectively-red tests block the flip.** Read the **`Verdict: … @ <sha>`** line in the story
    walkthrough's `## Code Review` section (stories closed before 2026-08-02 keep the old standalone
    verdict — fall back to `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md` when the
    walkthrough has no such section). **FAIL** (a NEW regression or missing
    required tier — actually red) → do NOT flip; tell Daniel to fix via `/cicd-code-review`, then re-run.
    **Every other verdict closes it:** **PASS** → flip; **CONCERNS** → flip + record them; **WAIVED /
    missing / stale** (verdict on an old HEAD) → flip. Fail-open: a gate-read error never blocks close-out.
  - **No "leave it at review and ask" branch — never punt the flip back to Daniel.** A pending
    **live-test / live-verify / live-QA / live-checkride** or "stays review until X" note is NOT a blocker:
    his invocation resolves it. Flip and NOTE it (`note: pending live-test — closed on your invocation`).
    The red-tests **FAIL** is the only refusal.
  - **"commit owed" is NOT a blocker** — the agent commits its own work in the story worktree, and the
    door's Step 3 lands it. Nothing about git blocks the status flip.
- **Epic closure — do it in the SAME pass, never leave it to be noticed later.** An umbrella cannot
  close itself: when every child of this story's epic is terminal (`done`/`descoped`), the epic key is
  the only thing still holding it open, and a stale-open epic keeps recommending finished work.
  Step 0.6's `epic` line already answers this — `epic-N is 'X' but ALL n children are terminal - it can
  close now`. When it says that:
  1. diff `_bmad-output/planning-artifacts/epics.md` against the board keys 1:1 — a child that exists in
     one and not the other is the real finding, and it is NOT closeable yet;
  2. flip the epic key with `story_status.py set epic-N done --project <PROJECT>`;
  3. update the epic's status line in `epics.md` in the same edit — the two rot independently.
  **A pending live-verify / live-QA debt does NOT hold an epic open** — same rule as the story flip
  above. A `deferred` or `deferred-v3` child DOES: park it under a *deferred epic*, never as a parked
  row under a finished one, or the epic can never close.
- **Last Updated**: set to today's date at the top of `active-context.md`.
- **CHANGE LOG — `_bmad-output/history/CHANGELOG.md`, one entry per line, newest first** (Wave 4
  split, 2026-08-03: the log no longer lives in `sprint-status.yaml` — the pointer there says so).
  Add your entry as its own `#   YYYY-MM-DD (<story> <stage>): …` line directly under the CHANGE-LOG
  header block in THAT file. The board's real `last_updated:` key refreshes automatically when
  `story_status.py set` flips the story. ⛔ **Never re-join the log into one ` | `-separated line** —
  it was 29k characters on a single line, which made every concurrent close-out an unresolvable
  conflict. Distinct lines let two lanes merge. Keep your entry to what the board needs; the narrative
  belongs in the story's walkthrough. ⛔ **Never add a narrative note to the board row itself** — a
  non-terminal row may carry ≤120 chars; a terminal row carries NOTHING (`workflow_lint` errors on
  both, and the flip drops the old note automatically).
## Step 5 — Prune & budget → run `/cicd-prune-context` (AUTOMATIC, never ask)
Invoke **`/cicd-prune-context`** against the same `PROJECT_ROOT` (it inherits the binding — no
re-resolution). It applies unconditionally — the ONLY gate in THIS command stays Step 4's red-tests
check; everything else, incl. Step 6's memory write, just applies. Carry its report line
(`active-context: ~X / 5,000 tokens`) into Step 6's summary EVERY save — and the door carries it into its own.

## Step 6 — §5 artifacts, summary & manual catch
- Ensure this session's `_artifacts/<date>_<slug>/` has the single **`walkthrough.md`** with its
  sections per `artifacts-always-first` §5 — **`## Task Checklist`** (the outline), **`## Evidence`**,
  and **`## Your Actions`** (what landed — branch + commit range, which the door's Step 3 fills in after the
  landing returns 0 — plus anything still on
  Daniel); story work also carries `## Suite Ledger` + the review's `## Code Review`. (Sections of the
  walkthrough, not separate files. Dense, not short — no byte cap; never cut a finding to shorten it.)
- Print a **`Session save applied:`** summary — ✅ tasks moved to Completed, 🧠 learnings routed (→ file),
  🧹 stale pitfalls / old completed pruned.
- **Memory (AUTOMATIC — validate, cross-check, write; no approval gate):** for each candidate (Close-Out
  Handoff `→ Claude memory` bucket, or from Step 3), self-validate + write WITHOUT asking:
  1. **Valid to store?** A durable cross-session fact (recurring pitfall, architecture invariant, Daniel
     preference) — NOT a one-off, NOT already captured in Steps 3–4. Fails → drop it.
  2. **Cross-check existing memory.** Read `MEMORY.md` + any same-topic file. Already covered → UPDATE that
     file in place (no duplicate); CONTRADICTED → new learning wins, rewrite the stale file. NEW file only
     when nothing covers it.
  3. **Write it.** One fact per file (`name`/`description`/`metadata.type` frontmatter) + a one-line
     `MEMORY.md` pointer.
  - Report outcome: `🧠 Memory: wrote [name] (new) · updated [name]`, or `🧠 Memory: nothing cross-session
    — unchanged` (most sessions).
- **Then ask the operator — CONDITIONALLY (SCC-133):** ask *"Saved the session updates. Any manual learnings, new bugs, or sprint-objective changes to add?"* **only when Step 3 routed ZERO learnings automatically** (nothing went to a spec, a rule, the pitfalls file, or the memory queue in Step 3). When Step 3 routed at least one, print the routed list instead and do not ask — the operator's don't-slow-me-down mandate, without deleting the one guaranteed human-input hook for the sessions that produced nothing. Apply any additions.

---

## Done — the save is complete; the landing is somebody else's step

Print the `Session save applied:` summary and stop. ⛔ **Do NOT land the branch, do NOT move the Jira ticket, do
NOT file a Dev Record, and do NOT prune a tree.** Those four are `/cicd-close-story-merge-tree`'s, and it runs
them **land → Dev Record → ticket → prune** — that order being the safety property: everything written here
rides the story branch, so a landing that stops publishes nothing, and the ticket moves only after the push
returned 0, because a remote board write cannot be taken back.

**Invoked BY the door?** Hand your summary lines back to it: the routed learnings, the story flip line
(`Closing <story>: review → done`), and `active-context: ~X / 5,000 tokens`. It prints them in its own report.

**Invoked standalone and the story is genuinely ready to land?** Say so in one line and hand the operator
`/cicd-close-story-merge-tree` — typing it IS the sign-off for that landing, and it re-runs this save first, which
is idempotent.

Optional additional input: $ARGUMENTS
