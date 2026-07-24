---
description: Audit a diff against the house code standard — machine checks (ruff/eslint/types) that can FAIL, plus a judgment pass for the comment contract and AI-drift bans that caps at CONCERNS. Runs standalone or as /sudo-code-review Step 3.5.
platforms: [opencode, antigravity]
---

# /clean-code-audit — Is this code clean, and can you prove it?

Checks a **diff** against `.agents/rules/code-standards.md` — the one house definition of clean. Two
halves: the **machine floor** (objective, can FAIL) and the **judgment pass** (taste, caps at CONCERNS).

**Load `.agents/rules/code-standards.md` now.** This command is the auditor; that file is the standard.
Never audit from memory — if the standard moved, the audit moves with it.

> **Diff-scoped, always.** You judge the code THIS story wrote. Legacy debt in untouched files is not
> the story's problem and must never red-wall it. A finding on an unchanged line is out of scope —
> note it as debt, do not gate on it.

---

## Step 0 — Resolve the target project (FIRST — before any other step)
Run from the **command center** (the lobby), this command operates on exactly ONE child project under
`Projects/`, never the lobby itself. Resolve the target now:
0. **Self (sub-project fast path — check this FIRST, and STOP here if it matches)** — if this repo has
   **no** `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip straight to the
   binding rule. Do NOT read `active-project.txt` or parse `$ARGUMENTS` for a project name.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is
   the target; consume that first token (the remainder is the real argument — a story id or a base ref).
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under `Projects/`, use it.
3. **Ask** — else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"*.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.
Every bare path and every command below resolves **under `PROJECT_ROOT`**.

## Step 0.5 — Resolve the diff (worktree-aware)

Story work lives in its own worktree (`worktree-per-story`), and the code under audit commonly exists
**only there**. Run `git worktree list` under `PROJECT_ROOT`; if a `claude/<story-slug>` tree matches the
story, `cd` into it and bind every path and command below to that tree. Echo `Auditing in <path>`.

Establish the changed-file set — this is the audit's entire universe:

```bash
git diff --name-only main_debug...HEAD          # story branch vs the trunk it forked from
git diff --name-only --cached                   # plus staged, if mid-work
```

If `$ARGUMENTS` names an explicit base ref, use it instead. Echo the file count. **An empty set is a
STOP, not a pass** — say so and stop; a vacuous green here is the exact failure this gate exists to
prevent (`tests-must-gate-for-real` §2).

---

## Step 1 — The Machine Floor  *(objective — these can FAIL)*

Run the §6 commands from `code-standards.md`, scoped to the changed set. Use the venv interpreter, never
bare `python`. **Paste actual output** — a summarized result is not evidence.

| Check | Scoping |
|---|---|
| `backend/.venv/Scripts/python.exe -m ruff check <changed .py files>` | pass the changed paths directly |
| `npm run lint -- <changed .ts/.tsx files>` (in `frontend/`) | pass the changed paths directly |
| `backend/.venv/Scripts/pyrefly.exe check` | whole-program — **count only errors whose file is in the changed set** |
| `npx tsc --noEmit` (in `frontend/`) | whole-program — **count only errors whose file is in the changed set** |

Skip a check whose language the diff never touched, and **say which you skipped and why**. A check that
did not run is not a check that passed.

If a tool is missing (e.g. `No module named ruff`), that is a **finding, not a skip** — the floor is
unrunnable and the project violates `tests-must-gate-for-real` §2. Report it and say what installs it.

**Also scan the changed lines for the §2 banned patterns that linters miss:**
- bare `except:` / `except Exception` with no re-raise and no logged reason
- `any` in TypeScript
- a committed secret, key, or token
- leftover debug prints / `console.log`
- commented-out code

## Step 2 — The Judgment Pass  *(taste — caps at CONCERNS)*

What no linter can see. Read the changed hunks and answer each honestly:

**A. The comment contract (`code-standards` §1)**
- Does every non-obvious block carry its `Story <E>.<S> (AC-n):` provenance — the workarounds, the
  fallbacks, the ordering constraints, the magic constants?
- Did the change invalidate an existing `AIDEV-NOTE`? A stale anchor is **worse than none** because it
  is trusted — flag every one the diff should have updated and did not.
- Any comment that merely restates the code? Any `TODO`/`FIXME` without an owner and a tracked task?
- Does a genuine trap introduced here deserve a new `AIDEV-NOTE` that is missing?

**B. The AI-drift bans (`code-standards` §2)**
- New abstraction with a single caller?
- Something re-implemented that already exists? **Search before you accept it as new** — this is the
  most common real finding. Grep the obvious neighbours; use GitNexus `context({name})` if the repo is
  indexed.
- Defensive `try`/`except` around code that cannot fail?
- Unused params, dead branches, a new file where an existing module was the home?
- Scope creep — changes outside what the story required?

---

## Step 3 — Findings

Emit findings in this exact shape so `/sudo-code-review` can fold them into its verdict unchanged:

```
### Clean-Code Gate — <PASS | CONCERNS | FAIL>

**Machine floor**
- ruff        : <PASS/FAIL — n errors on changed lines>   [actual output pasted]
- eslint      : <PASS/FAIL — n errors on changed lines>   [actual output pasted]
- pyrefly     : <PASS/FAIL/SKIPPED — why>
- tsc         : <PASS/FAIL/SKIPPED — why>

**Findings**
| # | file:line | Severity | Category | Finding | Disposition |
|---|-----------|----------|----------|---------|-------------|
| 1 | backend/services/x.py:88 | FAIL | banned-pattern | bare `except:` swallows the write error | applied |
| 2 | frontend/src/a.tsx:12 | CONCERNS | comment-contract | fallback has no Story provenance | applied |
```

**Verdict rules** (from `code-standards` §7 — do not invent your own):
- **FAIL** — a machine check errors on a changed line, or a §2 banned pattern shipped, or a secret.
- **CONCERNS** — comment-contract gaps and judgment findings only.
- **PASS** — floor green on changed lines, nothing above noise.

Apply the fixes you can make safely, then **re-run the affected check and paste the new output**. Mark
each finding `applied` / `deferred` / `dismissed` — a dismissal needs a reason.

## Stay in lane
Audit and fix; never flip a story status, never edit `sprint-status.yaml`, never land on `main_debug`.
Commit fixes inside the story worktree with explicit paths (`git add -A`/`.`/`-u` stay banned).

Optional additional input: $ARGUMENTS
