---
description: Audit a diff against the house code standard — machine checks (ruff/eslint/types) that can FAIL, plus a judgment pass for the comment contract and AI-drift bans that caps at CONCERNS. Runs standalone or as /cicd-code-review Step 3.5.
platforms: [opencode, antigravity]
---

# /cicd-clean-code-audit — Is this code clean, and can you prove it?

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/smh-target-resolution.md` — bind ONE target, never operate on the lobby
> - `.agents/rules/code-standards.md` §6.5 — **disposition**: the assessor decides what is real, not
>   the lens; §5 — both machines; §6 — the machine floor, resolved per machine
> - `.agents/rules/tests-must-gate-for-real.md` §5 — a gate that cannot fail is a finding; §6 — run
>   gates bare, because a pipe returns the pipe's exit code

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
Every bare path and every command below resolves **under `PROJECT_ROOT`** (per
`.agents/rules/smh-target-resolution.md` §STD + §BIND); a needed path missing under `PROJECT_ROOT` →
STOP, never fall back to the lobby.

## Step 0.5 — Resolve the diff (worktree-aware)

Story work lives in its own worktree (`worktree-per-story`), and the code under audit commonly exists
**only there**. Run `git worktree list` under `PROJECT_ROOT`; if a `claude/<JIRA-KEY>-<story-slug>` tree matches the
story, `cd` into it and bind every path and command below to that tree. Echo `Auditing in <path>`.

Establish the changed-file set — this is the audit's entire universe. Resolve the base dynamically:
on a `claude/*` story branch the base is its EPIC branch (exactly one live `epic/*` is the normal
case); otherwise fall back to `main`:

```bash
# bare on purpose — this WHOLE fence runs inside the tree the prose above bound (the story
# worktree when one matched); a `cd` here would move the audit off that tree, and every diff
# below would measure the shared checkout instead (SCC-351 review). Fetch works from any
# tree of the repo — refs are shared.
env -u GITHUB_TOKEN git fetch origin
# origin/ FIRST: a local epic head is only as fresh as the last pull, and a story lane's real
# base is what the epic branch looks like NOW - sibling stories land there while you audit.
BASE=$(git for-each-ref --format='%(refname:short)' \
         'refs/remotes/origin/epic/*' 'refs/heads/epic/*' | head -1); BASE=${BASE:-origin/main}
git diff --name-only "${BASE}...HEAD"           # story branch vs the branch it forked from
git diff --name-only                            # STANDALONE ONLY - saved edits nobody staged yet
git diff --name-only --cached                   # STANDALONE ONLY - staged, if mid-work
```

⛔ **Those last two lines are for a STANDALONE run only. Embedded as `/cicd-code-review` Step 3.5,
drop them and audit the committed diff alone.** That command's Step 0.6 resolves *committed work
only* and reports uncommitted files as present-and-not-reviewed. Sweeping them in here re-scopes the
review from underneath itself: an `any` in a file the reviewer never saw becomes a FAIL on this
lane, and the lane cannot fix what it did not write. Whether the two commands review the same set is
not a detail — it is the difference between one verdict and two.

If `$ARGUMENTS` names an explicit base ref, use it instead. Echo the file count. **An empty set is a
STOP, not a pass** — say so and stop; a vacuous green here is the exact failure this gate exists to
prevent (`tests-must-gate-for-real` §2).

<!-- twin-law: memory-sweep -->
⛔ **Never sweep another session's memory into this diff** (`artifacts-always-first` §"The memory
store"). Dirty files under `_artifacts/_memory/` belong to whatever wrote them — the store is shared
and two-tier since SCC-73, the lobby's index plus each project's own, so a sibling lane's uncommitted
entry shows up in a `git status` here. Report them as present and out of scope; they are parked or
left, never committed under this lane's key.
<!-- /twin-law -->

---

## Step 1 — The Machine Floor  *(objective — these can FAIL)*

Run the §6 commands from `code-standards.md`, scoped to the changed set. Use the venv's own
executables, never a bare global tool. **Paste actual output** — a summarized result is not evidence.

⛔ **Resolve the venv bin dir FIRST — this system runs on both machines** (`code-standards` §5). A venv
puts its executables in `bin/` on POSIX and `Scripts/` on Windows, and this table named `Scripts/…exe`
outright until SCC-205: on the Mac every one of these commands missed, the floor reported itself
unrunnable, and the objective half of the most-used audit did nothing while the run looked normal.

```bash
ls backend/.venv/bin/ruff 2>/dev/null || ls backend/.venv/Scripts/ruff.exe   # which layout is this machine?
```

⛔ **`<VENV>` below is a placeholder you SUBSTITUTE, not a shell variable.** An earlier cut wrote
`"$VENV"` and assigned it in a separate block — but shell state does not survive between tool calls,
so each row run on its own expanded to `/ruff check`, exit 127, and the floor reported itself
unrunnable. That is the very failure this section exists to fix, reintroduced by its own fix.

| Check | Scoping |
|---|---|
| `<VENV>/ruff check <changed .py files>` | pass the changed paths directly |
| `npm run lint -- <changed .ts/.tsx files>` (in `frontend/`) | pass the changed paths directly |
| `<VENV>/pyrefly check` | whole-program — **count only errors whose file is in the changed set** |
| `npx tsc --noEmit` (in `frontend/`) | whole-program — **count only errors whose file is in the changed set** |

⛔ **Run each one BARE** (`tests-must-gate-for-real` §6): `<check> | tail -5` exits 0 whenever `tail`
succeeds, however red the check was. Redirect if you need to trim — `<check> > out.txt 2>&1; echo "EXIT=$?"`.

Skip a check whose language the diff never touched, and **say which you skipped and why**. A check that
did not run is not a check that passed.

If a tool is missing (e.g. `No module named ruff`), that is a **finding, not a skip** — the floor is
unrunnable and the project violates `tests-must-gate-for-real` §2. Report it and say what installs it.

**Also scan the changed lines for what no linter catches:**
- bare `except:` / `except Exception` with no re-raise and no logged reason
- `any` in TypeScript
- a committed secret, key, or token
- leftover debug prints / `console.log`
- commented-out code
- **Does it run on both machines?** (`code-standards` §5) A hardcoded absolute or `C:/…` path where
  `Path(__file__).parent` belongs, a `;` path separator, `robocopy`, `chmod` assumed present, or a
  bare `python`/`python3` hardcoded in a committed script — each works where it was written and dies
  on the other machine. This is a finding, not a nitpick.
- **A gate that cannot fail?** A report-only job, `|| true`, `continue-on-error`, or a check whose
  EMPTY input reads as a pass. See the FAIL ladder below — this one is not a judgment call.

⛔ **These two rows live HERE, in the always-run floor, and not in Step 2's judgment pass** — Step 2B
is skipped wholesale when this audit runs embedded as `/cicd-code-review` Step 3.5, and a
both-machines break or a vacuous gate is exactly as real on an embedded run as on a standalone one
(SCC-212).

## Step 2 — The Judgment Pass  *(taste — caps at CONCERNS)*

What no linter can see. Read the changed hunks and answer each honestly:

**A. The comment contract (`code-standards` §1)**
- Does every non-obvious block carry its `Story <E>.<S> (AC-n):` provenance — the workarounds, the
  fallbacks, the ordering constraints, the magic constants?
- Did the change invalidate an existing `AIDEV-NOTE`? A stale anchor is **worse than none** because it
  is trusted — flag every one the diff should have updated and did not.
- Any comment that merely restates the code? Any `TODO`/`FIXME` without an owner and a tracked task?
- Does a genuine trap introduced here deserve a new `AIDEV-NOTE` that is missing?

**B. The AI-drift bans (`code-standards` §2)** — *standalone runs only: as `/cicd-code-review`
Step 3.5 this part is satisfied by importing the Step-1 adversarial review's drift findings
(source-labelled `review`); do not re-walk the hunks.*
- New abstraction with a single caller?
- Something re-implemented that already exists? **Search before you accept it as new** — this is the
  most common real finding. Grep the obvious neighbours; use `code-review-graph query callers_of <name>` if the repo is
  indexed.
- Defensive `try`/`except` around code that cannot fail?
- Unused params, dead branches, a new file where an existing module was the home?
- Scope creep — changes outside what the story required?

---

## Step 3 — Findings

Emit findings in this exact shape so `/cicd-code-review` can fold them into its verdict unchanged:

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
- **FAIL** — a machine check errors on a changed line, or a §2 banned pattern shipped, or a secret, or
  **a new gate that cannot fail** shipped in this diff (`tests-must-gate-for-real` §5 — a green that
  verified nothing is worse than no gate, because it is read as evidence).
- **CONCERNS** — comment-contract gaps and judgment findings only.
- **PASS** — floor green on changed lines, nothing above noise.

<!-- twin-law: disposition -->
⛔ **Decide what is REAL before you fix anything** (`code-standards` §6.5 — the operator's ruling,
2026-08-17: *"the agent's job is to find things so it always will ... we fix actual issues"*). You are
the assessor; a lens's severity label is an INPUT, not a verdict. Three questions, all three YES to fix:
**is it REAL** (state the concrete failure — *this input, this wrong output* — or drop it) · **does it
change BEHAVIOUR** (naming, structure and wording do not) · **is it in THIS diff** (pre-existing debt in
an untouched file is not this lane's work). ⛔ **"It's cheap" is not a reason** — twenty cheap fixes is
the audit that never ends, each one landing after the checks ran, unreviewed. Record the tail in ONE
line: how many came back, how many were real and fixed, the rest dismissed under this ruling.
<!-- /twin-law -->

Apply the fixes you can make safely, then **re-run the affected check and paste the new output**. Mark
each finding `applied` / `deferred` / `dismissed` — a dismissal needs a reason, and a deferral
names its structural blocker (another live lane · another repo · an open decision); with no blocker it
is applied here (operator rulings 2026-08-15).

## Stay in lane
Audit and fix; never flip a story status, never edit `sprint-status.yaml`, never land on the epic branch.
Commit fixes inside the story worktree with explicit paths (`git add -A`/`.`/`-u` stay banned).

Optional additional input: $ARGUMENTS
