---
description: Epic kickoff — write the epic + its stories, generate the sprint board, then interactively risk-score every story P0–P3 (test levels). Phase A of the sudo flow, before the per-story dev loop.
platforms: [opencode, antigravity]
---

# /cicd-create-epic-sprint — Epic Kickoff: Stories + Sprint + Risk-Score (Phase A)

> **Rules in force for this command:**
> - `.agents/rules/000-PLAN-FIRST-GATE.md` — `epics.md` and `sprint-status.yaml` are project files.
>   The Step 2 checkpoint is this command's gate: it opens on the operator's word alone, and a
>   correction restarts the wait
> - `.agents/rules/artifacts-always-first.md` § Hard Stops — no project file is edited for a
>   commit-producing lane before its lane is open; that is why the branch is cut in Step 1, before
>   the epic is written
> - `.agents/rules/git-policy.md` — the epic branch is cut from `origin/main` at kickoff; explicit
>   paths only, never `git add -A`; `git status --short` empty + `0 0` before the work is called
>   finished; backticks in `-m "…"` EXECUTE, so commit with `-F <file>`
> - `.agents/rules/worktree-per-story.md` § "cwd is not intent" — every git call below is bound with
>   `-C "$PROJECT_ROOT"`, and the branch is echoed from command output, never from belief
> - `.agents/rules/jira.md` — the acli reference: the Epic is created bare, with an outline (SCC-49),
>   and its key is read from output, never invented
> - `.agents/rules/work-consolidation.md` rule 1 — look for a home before you mint: the Epic dedupe
>   search in Step 1 and the one-line "what I looked at" sentence
> - `.agents/rules/smh-target-resolution.md` §STD + §BIND — Step 0 binds `PROJECT_ROOT`

Thin orchestrator — calls three existing BMAD/TEA skills back-to-back so a batch of requirements arrives as
an epic, a populated sprint board, AND a Daniel-confirmed P0–P3 risk map in ONE pass. Runs BEFORE the
per-story dev loop. Project-scoped (targets THIS repo).

> Flow position: `cicd-boot-sprint-memory` → **`cicd-create-epic-sprint`** →
> `cicd-write-story-tests` → `cicd-dev-story-tests` → `cicd-code-review` → `cicd-close-story-merge-tree`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override (remainder = the real argument — requirements source, focus, …) → `.agents/active-project.txt` →
else **STOP and ask** — never guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly**
`Target: Projects/<name>` before any work. Every bare path below resolves under `PROJECT_ROOT` (nested
`bmad-*` skills bind their `{project-root}` to it); a needed path missing under `PROJECT_ROOT` → STOP and
say so, never fall back to the lobby.

## Step 1 — Key the epic and cut its branch (BEFORE any project file is written)
<!-- JIRA-HOOK: epic/story tickets mint here when the branch is cut (epic + stories → Jira, ids recorded on the sprint board). Separate story; not built yet. -->
Per `git-policy.md`, every epic integrates on its own short-lived branch; per
`artifacts-always-first.md` § Hard Stops, no project file is edited for a commit-producing lane before
its lane is open. So the branch comes FIRST, and **every artifact from here on — `epics.md`, the board,
the test design — is authored on that branch, inside `$PROJECT_ROOT`.**

**1a. The key — look before you mint.** `<JIRA-KEY>` is the EPIC's Jira ticket (one of the repo's keys
in `.agents/jira.conf` — the armed commit-msg hook rejects the wrong project's key). A re-run (this
command has two human stops, so a stall and restart is the normal case) or a backfilled board already
has the row, and a second Epic for the same BMAD epic is two rows, one of which nothing will ever move
again. `jira_feed.py mint` does this search for stories; the Epic mint has no script, so the look is
written here (`work-consolidation.md` rule 1):

```bash
acli jira workitem search --jql "project = <PROJ> AND type = Epic AND statusCategory != Done" \
     --fields key,summary --limit 50
```

**Say in ONE line what you looked at and why no open Epic covers this one** — or which key does, in
which case reuse it and skip the mint. That sentence is the whole enforcement mechanism. If no ticket
exists, **mint it now** (operator ruling 2026-08-07 — the human is already in the room at kickoff, no
separate ask), bare (no `--assignee`), carrying the requirements source as its description:

```bash
acli jira workitem create --project <PROJ> --type Epic --summary "Epic <N> — <title>" \
     --description "Epic <N> — <title>. Source: <requirements path from \$ARGUMENTS>. Outline follows at Step 2."
```

Read the key from the create output — **never invent a key, never cut the branch unkeyed.** The full
outline is backfilled in Step 2, once `epics.md` carries the Epic (SCC-49 — a summary-only ticket is a
title, not a ticket; it is complete by the end of Step 2, never left that way). Story tickets are NOT
minted here: ① `/cicd-write-story-tests` mints each story's ticket at pickup (its Step 1.6, through
`jira_feed.py mint`), so the board fills as work actually starts. Full acli reference: `.agents/rules/jira.md`.

**1b. The branch.** Cut it from up-to-date `origin/main` and push it so it lives on origin. Every call
is bound to the repo Step 0 resolved — a bare `git checkout -b` acts on whatever tree the shell is
standing in, which is the lobby checkout (`worktree-per-story.md` § "cwd is not intent"):

```bash
git -C "$PROJECT_ROOT" fetch origin
git -C "$PROJECT_ROOT" checkout -b epic/<JIRA-KEY>-<slug> origin/main   # re-run and origin/epic/<JIRA-KEY>-<slug> exists? `checkout epic/<JIRA-KEY>-<slug>` instead — never a second cut
git -C "$PROJECT_ROOT" push -u origin epic/<JIRA-KEY>-<slug>
BRANCH=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD); echo "Epic branch: $BRANCH"
```

The echoed line must read `Epic branch: epic/<JIRA-KEY>-<slug>` — anything else → STOP. Story worktrees
(`/cicd-write-story-tests` ①) branch FROM this branch — it must exist, with the kickoff's output pushed
onto it, before the first one opens. The epic reaches `main` only via `/cicd-push-e2e`, which deletes
the branch after the merge.

## Step 2 — Create the epic and its stories — then STOP
Invoke the **`bmad-create-epics-and-stories`** skill for the requirements in `$ARGUMENTS` (a PRD, a
fix-list path, or a described scope — e.g. `_my_resources/open_tasks/fix_list_admin_sudoadmin.md`). It
writes the epic + its user stories with acceptance criteria into
`_bmad-output/planning-artifacts/epics.md` (stories live in that file; **no per-story files are written
here** — ① creates those). Confirm the new `## Epic <N>` section and its stories are in `epics.md`
before continuing. If the skill stops for input (missing requirements source, ambiguous scope), surface
it and STOP — never guess.

**FLOW CONTRACT (how this orchestration runs):** the nested BMAD skill
is a 4-step workflow whose step files each end in their own `[C]`-continue menu. Those menus exist for
STANDALONE greenfield use — do **NOT** surface them one-by-one during this orchestration; that turns one
kickoff into five stalls. When `$ARGUMENTS` names an already-approved requirements source (a signed-off
plan / fix-list), drive the skill's internal steps straight through (auto-continue its menus), appending per
the brownfield precedent (namespaced `E<N>-FR*` requirements; Epic 17/18 section format in `epics.md`).
This command has exactly **TWO human checkpoints**:
  1. ONE consolidated review after the epic is written — epic definition + full story list + AC digest
     in a single message — then **STOP and wait.** The operator's word opens Step 3; nothing else
     does. Per `000-PLAN-FIRST-GATE`, these are **not** approval: "ok" · "looks good" · "continue" ·
     clicking an option you wrote · being told to do the work · answering your clarifying question ·
     the operator **correcting** the epic + story set (a correction narrows it — edit `epics.md`,
     re-present the set, and stop again). Do not write the board on any of them;
  2. the Step 4 per-story risk-scoring (the designed hard stop).
A nested skill stopping on a REAL gap (missing source, contradictory scope) still surfaces + STOPs — this
contract removes ceremony, never judgment.
**On the operator's word — backfill the outline, then commit and push** (explicit paths, the Jira key
leads the subject, `-F` never `-m` — backticks in `-m "…"` EXECUTE):

```bash
python3 .agents/scripts/jira_feed.py outline --epic <N> --project <PROJECT> --out epic-outline.txt   # PC: `python`
acli jira workitem edit --key <JIRA-KEY> --yes --description-file epic-outline.txt
rm epic-outline.txt
printf '%s\n' "<JIRA-KEY> docs(epic): Epic <N> — <title>: epic + stories" > epic-commit-msg.txt
git -C "$PROJECT_ROOT" add _bmad-output/planning-artifacts/epics.md
git -C "$PROJECT_ROOT" diff --cached --stat                       # ONLY epics.md; anything else → unstage it
git -C "$PROJECT_ROOT" commit -F epic-commit-msg.txt
git -C "$PROJECT_ROOT" push origin HEAD:epic/<JIRA-KEY>-<slug>
```

`outline --epic` renders the goal and the story list straight out of `epics.md` — nothing invented, and
it **requires the `## Epic <N>` heading to exist**, which is why the mint at Step 1a is bare and the
outline lands here. ⛔ Never `git add -A` / `.` / `-u` — the shared checkout may carry the operator's
own uncommitted work.

## Step 3 — Generate the sprint board — then commit and push it
Land the new epic + story keys in `_bmad-output/implementation-artifacts/sprint-status.yaml` as **`backlog`**
— NOT `ready-for-dev` (the board's state machine: a story flips to `ready-for-dev` only when
`/cicd-write-story-tests` ① creates its story file). Follow house style: the epic's
comment block (STATUS · Source · order/deps), one commented line per story key (P-levels appended after
Step 4), `epic-<N>-retrospective: optional`, and a dated entry PREPENDED to the `# last_updated:` journal
line. For a single-epic append, edit the YAML directly per house style — invoking the full
`bmad-sprint-planning` skill is only warranted when regenerating the whole board. Confirm the keys appear,
then:

```bash
printf '%s\n' "<JIRA-KEY> chore(board): Epic <N> rows on sprint-status.yaml (backlog)" > epic-commit-msg.txt
git -C "$PROJECT_ROOT" add _bmad-output/implementation-artifacts/sprint-status.yaml
git -C "$PROJECT_ROOT" diff --cached --stat                       # ONLY the board
git -C "$PROJECT_ROOT" commit -F epic-commit-msg.txt
git -C "$PROJECT_ROOT" push origin HEAD:epic/<JIRA-KEY>-<slug>
```

## Step 4 — Risk-score the backlog (test levels) — INTERACTIVE HARD STOP
This is the final step and a **hard stop** — you WORK WITH Daniel to label every story, one at a time.

1. Invoke the **`bmad-testarch-test-design`** skill to risk-analyze the epic's stories (Risk = Probability ×
   Impact, per the TEA Test Priorities Matrix).
2. Assume the **Test Architect (Murat)** persona and walk Daniel through the P-level decision **ONE STORY AT
   A TIME**. For EACH story present:
   - **Your recommended P-level** (P0 / P1 / P2 / P3) — your opinion, stated first.
   - **Why** — the Probability × Impact reasoning in a line or two (what breaks, and how much it hurts).
   - **What it is** — one line of plain-language context on the feature/decision being scored.
   - **Levels it earns** — P0 = Unit+Integration+E2E+Manual (100%) · P1 = Unit+Integration+E2E (80%) ·
     P2 = Integration+Manual (50%) · P3 = Manual/skip (20%).
3. Give Daniel a way to **confirm or override each label individually** (the tap-to-answer question UI; the
   recommended P-level is the default first choice). ONE tap-screen carrying every story as its OWN question
   (recommendation + why + levels on each) satisfies "one at a time" — each story gets an individual
   decision (Epic 17/19 precedent: "interactive chips"). What is forbidden is deciding on the human's
   behalf: never record a P-level that wasn't explicitly confirmed. **STOP and wait** for the decisions.
   This is the hard stop.
4. Record the confirmed P-levels + test-level allocation into the test-design artifact
   (`_bmad-output/test-artifacts/test-design-epic-<N>.md` — the skill's epic-level output) and reflect
   the P-level onto each story in `epics.md` and onto its board line. Then commit and push all three:

   ```bash
   printf '%s\n' "<JIRA-KEY> docs(tea): Epic <N> risk-scored - P-levels on test design, epics and board" > epic-commit-msg.txt
   git -C "$PROJECT_ROOT" add _bmad-output/test-artifacts/test-design-epic-<N>.md \
                             _bmad-output/planning-artifacts/epics.md \
                             _bmad-output/implementation-artifacts/sprint-status.yaml
   git -C "$PROJECT_ROOT" diff --cached --stat                    # ONLY those three
   git -C "$PROJECT_ROOT" commit -F epic-commit-msg.txt
   git -C "$PROJECT_ROOT" push origin HEAD:epic/<JIRA-KEY>-<slug>
   rm epic-commit-msg.txt
   ```

## Done
Report: the epic id + title, the epic branch + commit range pushed, the stories created (ids + titles), sprint-status counts, and the confirmed
**P-level map** (story → P0–P3 + levels earned). Point to the next step:
> "Backlog risk-scored and sprint-ready. Next: `/cicd-write-story-tests <story>` for the top P0 (e.g. `<id>`)."
Leave it there — **do NOT start writing tests or code** (that's `/cicd-write-story-tests`).

Before the report, prove the kickoff is on origin (`git-policy.md` — `0 0` + clean, or the work is not
finished; an unverified "pushed" is how this hides):

```bash
git -C "$PROJECT_ROOT" status --short                                              # must be empty
git -C "$PROJECT_ROOT" rev-list --left-right --count epic/<JIRA-KEY>-<slug>...origin/epic/<JIRA-KEY>-<slug>   # must be "0 0"
```

State both results in the report, with `Epic branch: <from rev-parse>` and the commit range landed.

Optional additional input: $ARGUMENTS
