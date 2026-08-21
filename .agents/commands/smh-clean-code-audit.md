---
description: Audit a TASK diff against the command centre's own standard — the lobby machine floor (run_all, workflow_lint, sop_currency, py_compile, link+anchor) that can FAIL, plus a judgment pass over the toolkit conventions in the SOP and .agents/rules/ that caps at CONCERNS. The smh- counterpart of /cicd-clean-code-audit, for a repo that has no venv, no ruff and no tsc. Runs standalone, and is Step 3.5 of /smh-code-review.
platforms: [opencode, antigravity, claude, codex]
---

# /smh-clean-code-audit — Is this Task work clean, and can you prove it?

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push
>   `main`, never force-push
> - `.agents/rules/worktree-per-story.md` §"cwd is not intent" — the diff is resolved from command
>   output, because sibling `chore/*` lanes make cwd a bad witness
> - `.agents/rules/code-standards.md` — still the standard for real code (`.py`, `.ps1`, `.sh`): the
>   comment contract and the AI-drift bans below are **its** §1 and §2, and §6.5 is the **disposition**
>   test this command's fix step applies
> - `.agents/rules/tests-must-gate-for-real.md` §5 — a gate that cannot fail is a finding (the FAIL
>   ladder row below); §6 — run gates bare

Checks a **Task diff** against the two documents that define clean *here*:

| Document | Governs |
|---|---|
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | **the command centre's own standard** — the command menu, the two rules above every command, the safety net, the door model, the shipping roads. The SOP is the PRD for how this system is used, so a change that contradicts it is a defect even when every script passes. |
| `.agents/rules/code-standards.md` | the house definition of clean **code** — the comment contract (§1), the AI-drift bans (§2), severity (§7) |

**Load both now.** This command is the auditor; those files are the standard. Never audit from memory —
if a standard moved, the audit moves with it.

> **Why this is not `/cicd-clean-code-audit`.** That command's machine floor is
> the project venv's `ruff`, `npm run lint`, `pyrefly`, `tsc` — **none of which exist
> in the command centre.** There is no venv, no `backend/`, no `frontend/`, no `package.json`. Run it
> here and every check reports SKIPPED, which under its own rules is *"a check that did not run is not
> a check that passed"* — a floor made entirely of holes. The lobby has a real machine floor; it is
> just a different one, and it is Step 1 below. Both commands exist on purpose and are a **deliberate
> cross-family duplicate**: the standard, the floor and the severity ladder differ, the prefix carries
> a different permission. Fix a shared idea in one and diff the other.

> **Diff-scoped, always.** You judge what THIS task wrote. Legacy debt in untouched files is not the
> task's problem and must never red-wall it. A finding on an unchanged line is out of scope — note it
> as debt, do not gate on it.

---

## Step 0 — Resolve the repo and the diff (FIRST) — from command output, never from belief

The subject is **where you are standing**. If `$ARGUMENTS` names a folder under `Projects/` or a path,
use that; otherwise the current repo. Do **not** read `.agents/active-project.txt` — the command centre
is a legitimate subject here, and that pointer names a child project.

Task work runs in its own worktree (`.claude/worktrees/<slug>` off a `chore/<KEY>-<slug>` branch), and
the changed files commonly exist **only there**:

```bash
git worktree list                                    # find the tree for THIS task
REPO=$(cd "<the tree you resolved>" && git rev-parse --show-toplevel)
BRANCH=$(git -C "$REPO" rev-parse --abbrev-ref HEAD)
echo "Auditing: $(basename "$REPO") | Branch: $BRANCH"
```

Establish the changed-file set — the audit's entire universe. A Task branch forks from `origin/main`:

```bash
env -u GITHUB_TOKEN git -C "$REPO" fetch origin main # a bare `main` is this checkout's LAST PULL
git -C "$REPO" diff --name-only origin/main...HEAD   # committed on this branch
git -C "$REPO" diff --name-only                      # plus uncommitted
git -C "$REPO" diff --name-only --cached             # plus staged
```

If `$ARGUMENTS` names an explicit base ref, use it instead. **Echo the file count.**

⛔ **An empty set is a STOP, not a pass** — say so and stop. A vacuous green here is the exact failure
this gate exists to prevent (`tests-must-gate-for-real` §2).

<!-- twin-law: memory-sweep -->
⛔ **Never sweep another session's memory into this diff** (`artifacts-always-first` §"The memory
store"). Dirty files under `_artifacts/_memory/` belong to whatever wrote them — the store is shared
and two-tier since SCC-73, the lobby's index plus each project's own, so a sibling lane's uncommitted
entry shows up in a `git status` here. Report them as present and out of scope; they are parked or
left, never committed under this lane's key.
<!-- /twin-law -->

---

## Step 1 — The Machine Floor  *(objective — these can FAIL)*

The command centre's floor. Run every row the diff earns, **from the repo root, and paste actual
output** — a summarized result is not evidence.

| Check | Command | Runs when |
|---|---|---|
| **Enforcement suite** | `python3 .agents/scripts/tests/run_all.py` | **always.** Must be N/N files passed, exit 0 |
| **Toolkit self-consistency** | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | **always.** Naming law, frontmatter, `platforms: []`, INDEX coverage + dead links, rule pointers (incl. **disposition**), **both-machines** (a Windows-only venv path), encoding |
| **SOP currency** | `python3 .agents/scripts/sop_currency.py --paths <changed files> --message "<the commit message>"` | a usage surface changed — `.agents/commands/`, `.agents/rules/`, `.agents/scripts/*.py|.ps1`, git hooks, root `AGENTS.md` |
| **Python compiles** | `python3 -m py_compile <changed .py files>` | any `.py` in the diff |
| **Shell parses** | `bash -n <changed .sh files>` | any `.sh` in the diff |
| **PowerShell parses** | `pwsh -NoProfile -Command "[void][System.Management.Automation.Language.Parser]::ParseFile('<file>',[ref]$null,[ref]$null)"` | any `.ps1` in the diff |
| **Link + anchor** | resolve every Markdown link path and every `#L` anchor the diff touched | any `.md` in the diff |
| **Door parity** | `.claude/skills/<name>/`, `.agents/skills/<name>/`, `.opencode/commands/<name>.md`, `.agents/workflows/<name>.md` all agree with the command's `platforms:` | a command was added, renamed or deleted |

**⭐ `--toolkit-only` is not optional, and never swap in the bare form.** Without the flag,
`workflow_lint.py` resolves a project from `.agents/active-project.txt` and gates your Task on
whichever product project happens to be active — a gate about the wrong thing (SCC-64).

**Two things this floor does NOT have, said out loud:** there is no linter and no type checker here.
`ruff`, `pyrefly`, `eslint` and `tsc` are not installed in the command centre and there is no venv to
install them into. Do not report them as SKIPPED — that reads as a hole in the floor. Report them as
**not applicable to this repo**, and let `py_compile` plus the enforcement suite carry the objective
half. If the work adds a real Python package to this repo, that is the moment to add a linter, and it
is a finding worth raising.

**A tool that is missing when it should be there is a finding, not a skip.** `run_all.py` erroring out
means the floor is unrunnable and the repo breaks `tests-must-gate-for-real` §2. Report it and name
what fixes it.

**Also scan the changed lines for what no check catches:**
- a committed secret, key, or token
- leftover debug output (`print(`, `Write-Host` used as a debugger, `console.log`)
- commented-out code
- bare `except:` / `except Exception` with no re-raise and no logged reason (`code-standards` §2)
- a hardcoded absolute path or a `C:/` path where `Path(__file__).parent` belongs
- **A gate that cannot fail?** A report-only job, `|| true`, `continue-on-error`, or a check
  whose EMPTY input reads as a pass — `tests-must-gate-for-real` §5. Not a judgment call: it is
  the FAIL row below.
- **A `.venv/Scripts` path with no `.venv/bin` arm near it?** `workflow_lint` catches this one
  mechanically now (`both-machines`), so read its output rather than re-deriving it — but a
  bare `python`, a `;` path separator or `robocopy` is still yours to spot (`code-standards` §5).
- **bare `python`** in anything an operator will type or a script will run — the Mac has only `python3`

---

## Step 2 — The Judgment Pass  *(taste and convention — caps at CONCERNS)*

What no check can see. Read the changed hunks and answer each honestly.

**A. The comment contract** (`code-standards` §1 — for `.py` / `.ps1` / `.sh`)
- Does every non-obvious block carry provenance — **the ticket key and what it was for**? On the Task
  lane there is no `Story <E>.<S> (AC-n):` to write, so the equivalent is `SCC-<n>:` plus the reason.
- Did the change invalidate an existing `AIDEV-NOTE`? A stale anchor is **worse than none**, because
  it is trusted. Flag every one the diff should have updated and did not.
- Any comment that merely restates the code? Any `TODO`/`FIXME` with no owner and no tracked task?
- Does a genuine trap introduced here deserve a new `AIDEV-NOTE` that is missing?

**B. The AI-drift bans** (`code-standards` §2) — *inside `/smh-code-review` this half is satisfied by
importing Step 1's adversarial findings (source-labelled `review`); do not re-walk the hunks. The full
two-half pass is for standalone runs.*
- A new abstraction, script, rule or command with a single caller?
- Something re-implemented that already exists? **Search before you accept it as new** — the most
  common real finding.
- Defensive handling around states that cannot occur?
- Unused params, dead branches, a new file where an existing module was the home?
- Scope creep — changes outside what the ticket required?

**C. The command-centre conventions** *(the SOP's standard — this half is what makes the command
`smh-*`)*. Each row is a rule the SOP or `.agents/rules/` states, and each has been broken here before:

| Convention | The finding |
|---|---|
| **Naming law (SCC-63)** | a command not prefixed `cicd-` / `smh-` / `sentry-`; an underscore in a name; a surviving `/sudo-` reference anywhere — stale by definition |
| **The prefix is the permission** | a `cicd-*` command that acts on the lobby, or an `smh-*` command that binds `smh-target-resolution.md`. The prefix claims a permission; the body must match it |
| **One door per platform (SCC-66)** | a command with no launcher, or a door on a platform its `platforms:` does not claim. `.claude/commands/` and `/prompts:` are RETIRED doors — a new file in either is a FAIL |
| **Generated files are not edited** | a hand edit to `.agents/workflows/`, `.opencode/commands/`, or a `GENERATED by sync-agents` skill. Edit the command; re-run the sync |
| **The rule pointer** | a command that *does* the thing without pointing at the rule governing it — and, equally, a pointer that **replaced** the inline obligation. Agents follow the literal step list; a bare pointer gets skipped, so the obligation stays restated |
| **Both machines** | a documented command spelled only one way (`python` vs `python3`), a `\|` PATH join, a `robocopy`, a `chmod` that no-ops on the PC |
| **Gates ship armed** | a new gate landing warn-only. Hook output is invisible in VS Code, so warn-only reads as clean success — that is shipping nothing |
| **Every gate has an exit** | a new gate with no auditable escape hatch (`[sop-ok]`, an opt-out token). A gate with no legitimate way out gets `--no-verify`d permanently |
| **A gate must be able to fail** | a check whose empty input, missing tool, or piped exit code reads as PASS. Run gates bare — piping to `tail` returns TAIL's exit code |
| **Artifacts live in the tree** | a Task with no `_artifacts/_main/<date>_<slug>/walkthrough.md`. Absence means the step never ran |
| **Board narrative** | a note added to a finished row, or narrative landing on a board instead of in `history/` |
| **No personal name in directives** | a personal name in an `.agents/` body — use a generic referent |
| **Prose standard** | the SOP or a command written as a feature list rather than consequence-first. Every term gets explained; nothing is dumbed down |

---

## Step 3 — Findings

Emit findings in this exact shape so `/smh-code-review` can fold them into its verdict unchanged:

```
### Clean-Code Gate — <PASS | CONCERNS | FAIL>

**Machine floor**
- run_all.py       : <PASS/FAIL — n/n files, exit code>          [actual output pasted]
- workflow_lint    : <PASS/FAIL — n errors, n warnings>          [actual output pasted]
- sop_currency     : <PASS/FAIL/n-a — why>                       [actual output pasted]
- py_compile       : <PASS/FAIL/n-a — which files>
- link + anchor    : <PASS/FAIL — n links checked, n dead>
- door parity      : <PASS/FAIL/n-a — which commands>
- lint / types     : not applicable to this repo (no venv, no ruff, no tsc)

**Findings**
| # | file:line | Severity | Category | Finding | Disposition |
|---|-----------|----------|----------|---------|-------------|
| 1 | .agents/commands/smh-x.md:1 | FAIL | door-parity | claims codex, no .agents/skills door | applied |
| 2 | .agents/scripts/y.py:88 | CONCERNS | comment-contract | workaround has no SCC- provenance | applied |
```

**Verdict rules** — do not invent your own:

- **FAIL** — the enforcement suite is red · `workflow_lint --toolkit-only` reports an **error** · the
  SOP-currency check refuses · a changed `.py` does not compile · a dead link or anchor the diff
  introduced · a door-parity break · a committed secret · a §2 banned pattern shipped · a new gate
  that cannot fail.
- **CONCERNS** — `workflow_lint` **warnings** · comment-contract gaps · every judgment finding in
  Step 2B and 2C that is not listed above.
- **PASS** — floor green on the changed set, nothing above noise.

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
Audit and fix. Never merge to `main`, never transition a ticket, never prune a branch — that is
`/smh-close-task-merge-tree`'s job and invoking **it** is the operator's sign-off, not this. Commit
fixes inside the task worktree with explicit paths (`git add -A`/`.`/`-u` stay banned), and lead every
commit subject with the repo's Jira key or the armed `commit-msg` hook refuses it.

Optional additional input (a repo, a path, or a base ref): $ARGUMENTS
