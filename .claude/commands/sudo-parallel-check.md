---
description: After an epic's stories are WRITTEN, answer "which of these can I run side by side?" — one snapshot over one BMAD epic's children. Reads every story file, extracts what each will actually modify, computes the largest set with no file overlap, and tags the winners `parallel-ok` on the board. Stamps the set it was computed against so it can detect its own staleness. States, never starts.
---

# /sudo-parallel-check — Which of this epic's stories can run in parallel? (SCC-56)

> **Rules in force for this command:**
> - `.agents/rules/sudo-target-resolution.md` — the Step-0 ladder. **This command varies from
>   it**: see Step 0, which derives the target from the key instead of asking.
> - `.agents/rules/jira.md` — the `acli` reference, the label vocabulary, and guardrail 4
> - `.agents/rules/artifacts-always-first.md` — read-and-report; no plan, no walkthrough

**Run it when an epic's stories are written, before you start any of them.** That timing is the
whole point: `parallel-ok` is a property of a **set at a moment**, never of one story, so it cannot
be ruled at story pickup — ① mints 19.1's ticket before 19.2's file exists, and there is nothing to
compare against. This command is the moment the comparison is possible.

**The operator's lever, stated plainly: to develop an epic in parallel, write all its stories first.**
Grounded stories unlock approval; nothing else does.

## 🛑 MANDATORY RULES

1. **It STATES, it never STARTS.** It prints the commands to act on the answer. It writes labels and
   one comment to Jira. It **never** touches the working tree, cuts a branch, creates a worktree, or
   transitions a ticket. Guardrail 2 stands: placement is the operator's.
2. **No story file, no verdict.** The answer is *"write the story first"* — never a guess. On
   2026-07-31 a board called a story with **no story file** parallel-safe; its ① then found both
   stories editing `check_cost_cap` at the same line.
3. **Fail toward 🔒.** A false 🟢 puts two lanes on the same file; a false 🔒 costs only
   serialisation. When the story file is ambiguous about whether it will edit something, **count it
   as an edit.**
4. **Every ticket gets exactly ONE verdict.** ⛔ "Not yet checked" is not a verdict.
5. **Show the ANSWER, never the math.** ⛔ Pairwise notation ("✅ vs C+D"), lane letters, and
   cross-references the reader has to join are **banned** — the lane-letter matrix was found
   confusing and that ruling stands.
6. **The verdict is a SNAPSHOT and says so.** It carries the set it was computed against. Never
   present a stamped verdict whose child set no longer matches the board.

## Step 0 — Resolve the target (FIRST)

**The target is derived from the key, not asked and not guessed.** Each repo declares its Jira
project in its own `.agents/jira.conf` (`JIRA_KEYS="SCC"` in the lobby, `"AVCH"` in
`Projects/AGY_AVIATIONCHAT`), so `AVCH-13` resolves to AGY and `SCC-99` resolves to the command
centre. `parallel_check.py` does this itself; you do not pick a project.

**This is a deliberate variance from `sudo-target-resolution.md` §STD, and it is why a `sudo-*`
command may reach the lobby here.** It does not roam the command centre — it **follows the epic**.
The lobby carries a full BMAD install (`_bmad/bmm/`), so the day an epic and its stories are written
there, this command answers for them exactly as it does for any project (operator ruling
2026-08-09). Adding a project is zero edits: give it a `jira.conf` and it resolves.

Echo exactly `Target: <repo name> | Epic: <PARENT-KEY>` before any work. Two repos claiming one
project key is a misconfiguration and the script says so rather than picking one.

## Step 1 — Enumerate and ground

```bash
python3 .agents/scripts/parallel_check.py plan --parent <PARENT-KEY> --out /tmp/pc-plan.json
```

It refuses first and enumerates second:

- **not a BMAD epic** → refused **by name**. A grouping epic (`CI/CD Improvment`, `Thin toolkit`)
  has `Task` children with no story files; this command assesses BMAD stories only.
- **no `_bmad/bmm/stories/` in that repo** → refused. That is the lobby's answer *today*, and it
  stops being so on its own.

Then, per child, it applies the **grounding gate** in authority order — first available wins:

| Authority | Source | Why it outranks the next |
|---|---|---|
| 1. `branch-diff` | `git diff --name-only <epic-branch-or-main>...<story-branch>` | code written beats every declaration |
| 2. `plan` | `implementation_plan.md` | a declaration beats an intention |
| 3. `story` | the story file's Dev Notes | the intention is all there is |

**Umbrella children are excluded automatically** — a child whose BMAD number prefixes a sibling's
(`12.3` over `12.3.4`, `12.3.7`) contains them rather than competing with them. It renders as a
context line, never a verdict row. **Done children are excluded.** Both are the script's job, not
yours.

## Step 2 — ⭐ Extract the touch-sets (THIS is the judgment, and it is yours)

The packet names the exact files to read. For each **grounded, non-umbrella** child, read them and
decide **what it will actually modify**. This is the step no parser wins: across 139 AGY story
files, 105 name source paths, 58 carry negative declarations, and only 29 have a `**Task**`
checklist — there is no field to grep.

**Telling "will modify" from "mentions":**

| Signal | Read it as |
|---|---|
| a `**Files changed:**` / `## Task` / files-to-modify list | **modify** |
| `[Source: backend/x.py#L42]` | **reference** — that marker means "here is where I read this" |
| a path inside a venv / `site-packages` / `node_modules` | **reference** — you cannot edit a dependency |
| *"NO `firestore_session.py` changes — that is 19.2 entirely"* | ⭐ **negative declaration** — the strongest free signal in the corpus. Exclude the path, and note the named sibling |
| a file described only in "what already exists" prose | **reference** |
| the same file called "no change expected" in one section and listed as an edit in another | **modify** — rule 3, fail toward 🔒 |

Write one JSON object keyed by ticket:

```json
{
  "AVCH-15": {
    "paths":      ["frontend/src/components/dashboard/AgentCards.tsx"],
    "creates":    ["frontend/src/components/__tests__/CheckrideStates.test.tsx"],
    "imports":    [],
    "blocked_by": [],
    "evidence":   "story L86 'Files changed:' names AgentCards.tsx (DpeLiveCard) + one new test file"
  }
}
```

- **`creates`** — files this story ADDS. Also counted as touched; add/add on a new file has no merge
  base, so two stories creating the same file collide even though neither "modifies" it.
- **`imports`** — a module or symbol this story consumes that **another story creates**. That is a
  🔒 with zero file overlap today, and it is the edge a pure file-diff cannot see.
- **`blocked_by`** — from the story's frontmatter. A declared dependency locks regardless of files.
- **`evidence`** — one line, quoting the story. It goes on the board; a verdict without its evidence
  is an assertion.

⛔ **Every grounded child needs an entry.** The script refuses the whole run if one is missing —
an absent touch-set would silently read as "touches nothing", which is a manufactured 🟢.

## Step 3 — The set math (mechanical)

```bash
python3 .agents/scripts/parallel_check.py resolve \
        --plan /tmp/pc-plan.json --touchsets /tmp/pc-touch.json --out /tmp/pc-verdicts.json
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
| 🔒 after `<ticket>` | shares ground with that ticket — run after it lands |
| ⏳ waiting on `<story>` | an in-flight story's surfaces are unknown; clears when its plan lands |
| 📝 no story | ungrounded — `/sudo-write-story-tests <id>` unlocks it |

## Step 5 — Stamp the board

```bash
python3 .agents/scripts/parallel_check.py stamp \
        --plan /tmp/pc-plan.json --verdicts /tmp/pc-verdicts.json --apply
```

Adds `parallel-ok` to the 🟢 set **and strips it from everyone else** — that rewrite is what makes
this self-correcting where the per-story writer rotted, and it preserves every other label. Posts
one comment on the **epic** carrying the table, the evidence, and the stamp:
`verified <date> against N children: <keys>`.

⛔ **Labels and one comment only.** It does not transition anything (`jira.md` guardrail 4).

## Re-checking later — is yesterday's answer still good?

```bash
python3 .agents/scripts/parallel_check.py check --parent <PARENT-KEY>
```

`[FRESH]` (exit 0) or `[STALE]` (exit 1) with the children added or removed since. **A stamped set
that no longer matches the parent's children is not a verdict** — it reads *"re-run me"*. An
undetectably stale snapshot is exactly how the sprint dependency map and the `Deferred` saved filter
both misled on 2026-08-09; this is the check that makes the same failure impossible here.

## Report

`✅ Parallel check — <PARENT-KEY> (Epic <n>) in <repo>:`
- `Approved (<n>): <keys>` *(or why nothing was)*
- `Locked: <key> after <key> — <the shared path>` per row
- `Ungrounded: <keys> → /sudo-write-story-tests <id>`
- `Board: <n> labels added, <n> stripped · comment on <PARENT-KEY>`
- `Stamp: verified <date> against <n> children`

⛔ Never end by starting one of them. The next move is the operator's.
