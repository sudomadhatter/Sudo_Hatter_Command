---
description: After a Task's subtasks are PLANNED, answer "which of these can I run side by side, and which are small enough for one light lane?" — one snapshot over ONE parent Task's Subtasks. Reads every lane's plan, extracts what each will actually modify, computes the largest set with no file overlap, and stamps `parallel-ok` + `quick-dev` on the winners. Stamps the set it was computed against so it can detect its own staleness. States, never starts.
platforms: [opencode, antigravity, claude, codex]
---

# /smh-label-tasks — Which of this Task's subtasks can run in parallel? (SCC-155)

> **Rules in force for this command:**
> - `.agents/rules/jira.md` — the `acli` reference, the label vocabulary, and guardrail 4
>   (this command writes labels and one comment; it transitions nothing)
> - `.agents/rules/smh-target-resolution.md` — the Step-0 ladder. **This command varies from
>   it**: see Step 0, which derives the target from the key instead of asking.
> - `.agents/rules/artifacts-always-first.md` — read-and-report; no plan, no walkthrough

**Run it when a Task's subtasks are planned, before you start any of them.** That timing is the
whole point: `parallel-ok` is a property of a **set at a moment**, never of one subtask, so it
cannot be ruled when each subtask is minted — the siblings do not exist yet. This command is the
moment the comparison is possible.

**The operator's lever, stated plainly: to develop a Task in parallel, plan all its subtasks
first.** `/smh-plan-task` does that in one shot and ends by invoking this command. Grounded lanes
unlock approval; nothing else does.

**The `smh-` twin of `/cicd-label-tasks`, and the prefix is the permission.** Same engine
(`label_tasks.py`), same set math, same stamp. What differs is the unit: that command assesses
**BMAD stories under a BMAD epic**, this one assesses **Subtasks under one Task** — work with no
story file, no sprint board and no epic branch. Point either at the other's parent and it refuses
by name and hands you across.

## 🛑 MANDATORY RULES

1. **It STATES, it never STARTS.** It prints the commands to act on the answer. It writes labels
   and one comment to Jira. It **never** touches the working tree, cuts a branch, creates a
   worktree, or transitions a ticket. Guardrail 2 stands: placement is the operator's.
2. **No plan, no verdict.** The answer is *"plan the subtask first"* — never a guess. A board
   once called a story with no story file parallel-safe; the very next step found both lanes
   editing one function at the same line.
3. **Fail toward 🔒.** A false 🟢 puts two lanes on one file; a false 🔒 costs only
   serialisation. When a plan is ambiguous about whether it will edit something, **count it as an
   edit.**
4. **Every ticket gets exactly ONE verdict.** ⛔ "Not yet checked" is not a verdict.
5. **Show the ANSWER, never the math.** ⛔ Pairwise notation ("✅ vs C+D"), lane letters, and
   cross-references the reader has to join are **banned**.
6. **The verdict is a SNAPSHOT and says so.** It carries the set it was computed against. Never
   present a stamped verdict whose child set no longer matches the board.

## Step 0 — Resolve the target (FIRST)

**Derived from the key, not asked and not guessed.** Each repo declares its Jira project in its own
`.agents/jira.conf` (`JIRA_KEYS="SCC"` in the lobby, `"AVCH"` in `Projects/AGY_AVIATIONCHAT`), so
the script resolves the repo itself. **This is a deliberate variance from
`smh-target-resolution.md` §STD**: the command follows the ticket.

Echo exactly `Target: <repo name> | Task: <PARENT-KEY>` before any work.

## Step 1 — Enumerate and ground

```bash
python3 .agents/scripts/label_tasks.py plan --parent <TASK-KEY> --out /tmp/lt-plan.json
```

It refuses first and enumerates second. An **Epic** parent is refused by name and handed to
`/cicd-label-tasks` — an epic's children are Stories, or Tasks that each own their own Subtasks,
and assessing them as one flat set answers a question nobody asked. **Done children are excluded**
automatically.

Then, per child, the **grounding ladder** — first available wins. Fetch before rung 1:
`env -u GITHUB_TOKEN git -C "$REPO" fetch origin main` — a bare `main` is this checkout's last pull,
and grounding a label on a stale diff reads a lane as touching files it does not.

| Authority | Source | Why it outranks the next |
|---|---|---|
| 1. `branch-diff` | `git diff --name-only origin/main...chore/<KEY>-<slug>` | code written beats every declaration |
| 2. `plan` | the `implementation_plan.md` whose sibling `task.yaml` declares `task_key: <KEY>` | a declaration beats an intention |
| 3. `ticket` | the Subtask's own description | the intention is all there is — **weakest rung**, and rule 3 governs its ambiguity |

<!-- twin-law: tests-only-diff-is-not-rung-1 -->
⛔ **A TESTS-ONLY DIFF IS NOT RUNG 1 (SCC-259).** An assert-first lane commits its RED tests
before a line of implementation exists, so `branch-diff` there is the test files and nothing
else — a real touch-set that badly understates where the code is about to land. The script keeps
those paths as a source, flags it `tests_only`, and ranks it **below** the rungs that can see
further. A diff that is entirely planning artifacts was already excluded for the same reason
(SCC-155 #16). A diff carrying any real source file stays rung 1.
<!-- /twin-law -->

⭐ **The plan is joined by DECLARATION, never by slug.** A Task lane's artifacts folder is
`<date>_<slug>` with no key in it, so the join is the `task.yaml` manifest every lane already
writes — the same declaration `check_gate` governs on. The match is exact: `SCC-146`'s manifest
never grounds `SCC-14`.

## Step 2 — ⭐ Extract the touch-sets (THIS is the judgment, and it is yours)

The packet names the exact files to read. For each **grounded** child, read them and decide **what
it will actually modify**. No parser wins this: a plan names paths it reads, paths it writes, and
paths it explicitly hands to a sibling.

⛔ **A source carrying a `ref` is NOT in your checkout — open it with `git show`.** The packet
emits `{"kind": …, "path": …, "ref": "<branch>"}` when it found the file on the lane's own branch
rather than in the working tree, which is the normal state for a plan `/smh-plan-task` has left in
flight. Opening `<path>` there is an ENOENT on the rung the packet just called authoritative, and
an agent that reads the miss as "no source" downgrades a grounded child:

```bash
git -C "$REPO" show "<ref>:<path>"     # ref present  → read it from the branch
cat "<path>"                            # ref null     → it is in the checkout
```

| Signal | Read it as |
|---|---|
| a `**Files changed:**` / step table / files-to-modify list | **modify** |
| `[Source: .agents/scripts/x.py#L42]` | **reference** — that marker means "here is where I read this" |
| a path inside a venv / `site-packages` / `node_modules` | **reference** — you cannot edit a dependency |
| *"NO `jira_feed.py` changes — that is the C lane entirely"* | ⭐ **negative declaration** — the strongest free signal. Exclude the path, note the named sibling |
| a file described only in "what already exists" prose | **reference** |
| the same file called "no change expected" in one section and listed as an edit in another | **modify** — rule 3, fail toward 🔒 |

Write one JSON object keyed by ticket:

```json
{
  "SCC-160": {
    "paths":      [".agents/scripts/label_tasks.py"],
    "creates":    [".agents/commands/smh-label-tasks.md"],
    "imports":    [],
    "blocked_by": [],
    "quick_dev":  {"eligible": true, "evidence": "one script + its test; acceptance is one assertion"},
    "evidence":   "plan step table names label_tasks.py and one new command doc"
  }
}
```

- **`creates`** — files this lane ADDS. Also counted as touched; add/add on a new file has no merge
  base, so two lanes creating one file collide even though neither "modifies" it.
- **`imports`** — a module or symbol this lane consumes that **another lane creates**. A 🔒 with
  zero file overlap today, and the edge a pure file-diff cannot see.
- **`blocked_by`** — a declared dependency locks regardless of files.
- **⭐ `quick_dev`** — see Step 2.5. **Omit the key entirely if you did not assess it**; an absent
  key leaves the label exactly as it is, while `false` actively strips it.
- **`evidence`** — one line, quoting the plan. It goes on the board; a verdict without its evidence
  is an assertion.

⛔ **Every grounded child needs an entry.** The script refuses the whole run if one is missing — an
absent touch-set would silently read as "touches nothing", a manufactured 🟢.

## Step 2.5 — Rule `quick-dev` in the same pass

**`quick-dev` means: small enough for ONE light `/smh-quick-dev` lane.** Judge each grounded child:

| Eligible when… | Not eligible when… |
|---|---|
| its acceptance reduces to 1–3 checkable statements | it needs its own breakdown to be checkable |
| its touch-set is small (≲3 source files, no new subsystem) | it adds a subsystem, a rule, or a gate |
| no deployable path (`backend/`, `frontend/`, `firebase/`, `functions/`, `mobile/`, `.github/`) | a deployable path is in the touch-set — that is `/cicd-push-e2e` work, whatever the ticket says |
| nothing about it is still an open question | the plan itself says "decide X during the work" |

It is **advisory** — a batching aid for the operator, never permission to skip a gate. Every
eligible call carries an evidence line, the same as a touch-set.

## Step 3 — The set math (mechanical)

```bash
python3 .agents/scripts/label_tasks.py resolve \
        --plan /tmp/lt-plan.json --touchsets /tmp/lt-touch.json --out /tmp/lt-verdicts.json
```

It computes the **largest set in which every pair is disjoint**, deterministically. Planning
directories (`_bmad-output/`, `_bmad/`, `_artifacts/`, `_my_resources/`) never count as overlap —
only source paths decide. An **in-flight child with no landed plan approves nothing**: its surfaces
are unknown, nothing can be proved disjoint from unknown ground, and rule 3 says which way that
falls.

## Step 4 — Print the answer

Print the table the script renders, unedited — approved list first, then one verdict per ticket:

| Verdict | Meaning |
|---|---|
| 🟢 approved | safe to run beside **every other** 🟢 |
| 🔒 after `<ticket>`, `<ticket>` | shares ground with EVERY ticket named — run after all of them land |
| ⏳ waiting on `<ticket>` | an in-flight lane's surfaces are unknown; clears when its plan lands |
| 📝 no plan | ungrounded — `/smh-plan-task <PARENT-KEY>` unlocks it |
| ⚡ quick-dev | small enough for one light lane (a separate column, not a verdict) |

## Step 5 — Stamp the board

```bash
python3 .agents/scripts/label_tasks.py stamp \
        --plan /tmp/lt-plan.json --verdicts /tmp/lt-verdicts.json --apply
```

Adds `parallel-ok` to the 🟢 set **and strips it from everyone else** — that rewrite is what makes
this self-correcting where a per-ticket writer rotted. `quick-dev` rides the same pass with the
same rewrite, **except where you left it unassessed**, which is left untouched. Every other label
is preserved. Posts one comment on the **parent Task** carrying the table, the evidence, and the
stamp: `verified <date> against N children: <keys>`.

⛔ **Labels and one comment only.** It does not transition anything (`jira.md` guardrail 4).

## Re-checking later — is yesterday's answer still good?

```bash
python3 .agents/scripts/label_tasks.py check --parent <TASK-KEY>
```

`[FRESH]` (exit 0) or `[STALE]` (exit 1) with the children added or removed since. **A stamped set
that no longer matches the parent's children is not a verdict** — it reads *"re-run me"*.

## Report

`✅ Label check — <PARENT-KEY> (Task) in <repo>:`
- `Approved (<n>): <keys>` *(or why nothing was)*
- `Locked: <key> after <key>, <key> — <the shared path per blocker>` per row — ⛔ **every** declared blocker, not the first. A row naming one of three reads as a single dependency, and the operator schedules against it.
- `Quick-dev (<n>): <keys>`
- `Ungrounded: <keys> → /smh-plan-task <PARENT-KEY>`
- `Board: <n> labels added, <n> stripped · comment on <PARENT-KEY>`
- `Stamp: verified <date> against <n> children`

⛔ Never end by starting one of them. The next move is the operator's.

Optional additional input (a parent Task key): $ARGUMENTS
