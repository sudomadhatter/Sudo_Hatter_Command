---
name: code-standards
description: "Activates when writing, reviewing, or gating code — backend (Python/FastAPI) or frontend (React/TypeScript). The house definition of 'clean': the comment contract (Story provenance + AIDEV-NOTE anchors), the AI-drift bans, style/organization, and the machine-checkable floor. The `cicd-clean-code-audit` skill and `/cicd-code-review` Step 3.5 both enforce THIS file — edit the standard here and the gate follows."
trigger: glob
globs: ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
# Path-scoped. `globs:` is Antigravity's field; `paths:` is Claude Code's, and Claude
# loads this file ONLY when it reads a file matching one of them. Both lists are the
# same set on purpose — one classification, two readers (test_rule_frontmatter.py).

---

# Code Standards — the house definition of "clean"

This file is the standard. The **`cicd-clean-code-audit`** skill is the auditor that checks a diff against
it, and **`/cicd-code-review` Step 3.5** is the gate that can fail a story on it. There is one
definition of clean and it lives here — change it here and every enforcement point follows.

> **Scope of enforcement: the diff, not the repo.** The gate judges the code THIS story wrote. Legacy
> debt in untouched files is not the story's problem — same grandfathering discipline the test gate
> already uses. Ratchet debt down deliberately; never red-wall a story with it.

---

## 1. The Comment Contract

Two markers, two different jobs. Both are for the agent who arrives next — including you, six weeks
from now, with none of today's context.

| Marker | Answers | Required when |
|---|---|---|
| `Story <E>.<S> (AC-n):` | **Why does this code exist?** | any non-obvious block a story produced — a workaround, a fallback, an ordering constraint, a defensive branch, a magic constant, a deliberate omission |
| `AIDEV-NOTE:` | **What will bite the next agent who touches this?** | a trap that is invisible from the code alone and would otherwise be re-broken |
| `AIDEV-TODO:` | **What was deliberately deferred?** | only with a **named owner + a tracked task**. Without both it is banned (see §2). |

```python
# Story 14.6 (FR40): additive + best-effort — a grading failure must never
# break the chat stream.
await _emit_grading_event(...)

# AIDEV-NOTE: single-writer chokepoint — every profile write routes HERE.
# A cache belongs in profile_service (set_field-invalidated), never on chat_sessions.
def set_field(...):
```

```typescript
// Story 17.5 — email is the primary row identifier (E17-FR7); uid is NOT
// stable across re-invites.
email: string;
```

**Rules for anchor notes**

1. **Never delete or rewrite an `AIDEV-*` note without instruction.** If your change invalidates one,
   **update** it — a stale anchor is worse than none, because it is trusted. (This is the specific
   case of `karpathy-guidelines` → *"When your changes make a comment wrong, fix it."*)
2. **Grep `AIDEV-` before editing an unfamiliar or complex file.** The notes exist to be read first.
3. **Keep them short** — ≤2 lines, ~120 chars per line. An anchor is a warning, not documentation.
4. **Reserve them for genuine traps.** Spraying anchors over obvious code is its own failure mode: it
   trains the next agent to skip them, which defeats the whole mechanism.

**Banned**

- **Commented-out code.** Git has it. Delete it.
- **`TODO` / `FIXME` without an owner and a tracked task.** An unowned TODO is a wish.
- **Comments that restate the code.** `# increment i` earns nothing. Comments carry the *why*.
- **Stale comments left behind by a change.** If you changed the code, the comment is now your problem.

---

## 2. AI-Drift Bans

What "clean" means beyond formatting. These are the recurring failure modes of agent-written code, and
they are what the judgment half of the audit hunts for.

| Ban | Why |
|---|---|
| **No new abstraction with a single caller.** | A base class / factory / wrapper serving one call site is speculative structure. Inline it; abstract on the second caller, not the first. |
| **No re-implementing what already exists.** | Search before you write. This is the single most common review finding — a helper written twenty feet from the one it duplicates. |
| **No defensive `try`/`except` around code that cannot fail.** | It hides real errors and reads as diligence. Catch what can actually throw. |
| **No bare `except:` / `except Exception` without re-raise or a logged reason.** | Swallowing everything turns a crash into silent corruption. |
| **No `any` in TypeScript.** | Type it, or `unknown` + a narrow. `any` disables the checker you are paying for. |
| **No unused params, dead branches, or leftover debug prints.** | Dead code is a lie about intent. |
| **No new file where an existing module is the home.** | New files fragment the mental map. Extend the module that owns the concern. |
| **No scope creep beyond the story.** | Adjacent code, comments, and formatting are out of bounds unless your change breaks them (`karpathy-guidelines` → Surgical Changes). |

---

## 3. Style — Backend (Python)

| Standard | Rule |
|---|---|
| **Type Safety** | Type hints on ALL function signatures. Pydantic for data validation. |
| **Style** | PEP 8. Max 120 chars/line (matches `ruff` `line-length`). f-strings only. |
| **Docs** | Docstrings on public functions/classes. Comments carry the *why* (§1). |
| **Imports** | Absolute imports only (`from backend.agents.specialist...`). |
| **Tests** | ALL tests in `backend/tests/`. Standard Pytest. `unittest.mock` to isolate from live APIs. |
| **Dependencies** | Listed in `requirements.txt`. Always use `.venv` — never bare `python`. |
| **Temp files** | Debug scripts in `_test_scripts/` (not committed). |

## 4. Style — Frontend (React/TypeScript)

| Standard | Rule |
|---|---|
| **Components** | Functional + hooks only. TypeScript interfaces, never `any`. |
| **Organization** | Reusable: `components/common/`. Feature: `components/features/`. |
| **Styling** | Module CSS or styled-components. Mobile-first responsive. |

## 5. General

| Standard | Rule |
|---|---|
| **API** | RESTful. JSON bodies/responses. |
| **Git** | Present tense commits. Explicit paths only — `git add -A`/`.`/`-u` are banned (`git-policy`). Never commit secrets. |
| **Paths** | `Path(__file__).parent` — never hardcoded CWD paths. |
| **Both sides** | This system runs on ONE PC with two sides: Windows (PowerShell, `python`) and Ubuntu inside WSL2 (bash, `python3`). `python3` exists on one and `python` on the other, so **never hardcode either** — carry `sys.executable` down, or probe `python3 → python → py`. A `C:/…` path, a `;` separator, `robocopy`, or a bare `python` in a committed script is a finding, not a portability nicety: it works where it was written and dies on the other side. |

---

## 6. The Machine Floor

"Clean" has to be checkable, not arguable. These are the commands — the **same ones CI runs**, per
`tests-must-gate-for-real` §2. If a check cannot be run locally, it is not a gate.

| Check | Command (from the project root) |
|---|---|
| Backend lint | `<VENV>/ruff check backend/` |
| Backend types | `<VENV>/pyrefly check --python-interpreter-path <VENV>/python` |
| Frontend lint | `npm run lint` (in `frontend/`) |
| Frontend types | `npx tsc --noEmit` (in `frontend/`) |

> **`<VENV>` IS PER-MACHINE — resolve it, never hardcode it** (SCC-205, measured 2026-08-18). A venv
> puts its executables in `backend/.venv/Scripts/` on Windows and `backend/.venv/bin/` on POSIX.
> These commands read `Scripts/…exe` until 2026-08-18, so **every POSIX-side run of the most-used audit
> found its own machine floor unrunnable** — and under the audit's own rule a missing tool "is a finding, not
> a skip", so the objective half did nothing while reporting normally. Resolve it once:
>
> ```bash
> VENV=backend/.venv/bin; [ -d "$VENV" ] || VENV=backend/.venv/Scripts   # POSIX first, then Windows
> ```
>
> **Use the venv's own executables.** Bare `python` / bare `ruff` is the drifted global install and
> produces false missing-dependency findings — and bare `python` does not exist on the Ubuntu side at
> all (§5, Both sides).
>
> **And pyrefly needs the interpreter PINNED even when invoked from the venv** (SCC-312, measured
> 2026-08-24 on the POSIX side): `<VENV>/pyrefly check` bare resolves its site-packages from the SYSTEM
> python — 949 errors, 669 of them fabricated `missing-import`, burying the real findings — while
> the same run with `--python-interpreter-path <VENV>/python` reported 0 missing-import. The pin
> belongs at the CALL SITE, never in a project's `pyrefly.toml` (AGY's states why: an absolute
> path or interpreter pin in config would split CI and local onto different interpreters).

A project whose stack differs declares its own commands in its `AGENTS.md`; these are the defaults for
the FastAPI + Next.js house shape.

---

## 6.5 Disposition — reproduce or drop, fix or escalate

> Hoisted here by SCC-205 because it is **disposition law, not review-engine law**: it governs every
> command that produces findings — both clean-code audits, both code reviews, both self-audits — and
> it lived in exactly one place, `code-review-engine/steps/step-01-review.md`, owned by no rule.
> This rule already owns the FAIL-vs-CONCERNS split (§7), so it is the one place all four audits bind.
>
> **Rewritten by SCC-447 (2026-09-11).** The 2026-08-17 ruling below still stands. What changed is
> that "real" stopped being a judgment call and became a receipt on disk, and that a finding the
> lane is not fixing now has somewhere to go other than back into the queue.

**The ruling, in the operator's words (2026-08-17): *"the agent's job is to find things so it always
will — this is how we end up in this loop. The agent who assesses the finds has to decide what's real
and what's just the agent finding something to report. We fix actual issues."***

⛔ **A lens's severity label is an INPUT, not a verdict.** Every hunter is told to be exhaustive and is
measured by what it returns, so it will always return something, and it grades its own work. Treating
`critical` as an instruction to fix is how a four-lens review becomes an unbounded queue: each pass
finds more, each fix is a new unreviewed edit, and the lane never closes. **The orchestrator running
the audit is the assessor. Nobody else is.**

### Gate 0 — the reproduction gate, which runs before the three questions

⛔ **A `critical` or `important` that did not reproduce does not exist.** Not "is downgraded", not
"is worth a note in the record" — it is dropped, and only its count survives. Gate 0 runs first
because the three questions below it are judgment, and this one is not.

**Reproduction is three layers, and each layer is cheaper than the one after it.**

| Layer | Who | What it does |
|---|---|---|
| 1 | the **lens** that found it | writes `reproduce:` and `expected_wrong_output:`, **runs that command in its own copy**, and deletes the finding if it does not fail the way it predicted |
| 2 | the **engine** | checks that both fields and `reproduced: yes` are present. It cannot execute anything — the skill grants it no Bash, by design — so the floor it returns is **provisional** |
| 3 | the **caller** (the door that ran the review) | runs the command again on the REAL tree and writes the receipt. **That receipt is what binds** |

Layer 1 is where the cost deliberately lands. A lens that must run its own command discovers it has
nothing while the file is still open and the reasoning is still in context, which is the cheapest
place in the whole system to find out. The tax is also severity-gated: a `suggestion` costs nothing
and can never block, so the only move this prices out is inflating a nitpick to be heard.

Layer 3 is not optional, because a lens works in its own worktree copy. SCC-295 measured three of
five lenses editing that copy mid-review, and one reporting a RED result no version of the real code
could produce. A lens proves a defect exists **in the lens's tree**. Only the caller proves it exists
in shipping code.

The caller's receipt is written by one script, once per finding id:

```bash
python3 .agents/scripts/repro_receipt.py run --root <artifacts> --id <finding-id> -- <command>
```

There is no `--result` flag — a receipt implies execution. The script runs the command, records the
true exit code and the tail of its output, and notes whether the tree was dirty. A finding whose
command does not fail when it is run, is **dropped and counted**.

### The three questions, on what survives Gate 0

1. **Is it REAL?** The receipt answers this now. What is left for judgment is whether the failure the
   command produced is the failure the finding described.
2. **Does it change BEHAVIOUR?** A gate that fails open, a wrong answer, a crash, a refusal of
   something legitimate, lost data. Naming, structure, wording, a missing test for a branch that is
   already correct — these do not.
3. **Is it in THIS lane's diff?** Pre-existing debt in an untouched file is not this task's work.

### The action policy — what the agent does, and what it records

| The finding | What the agent does | The disposition it records |
|---|---|---|
| reproduced `critical` | fixes it, in this lane, with a pin seen red then green | `fixed @<sha> · pin <test>[:<case>] · repro <id>` |
| reproduced `important` | does **not** fix it — it escalates to the operator, in the same thread | `escalated · repro <id> · default: ships as recorded` |
| `critical` or `important` that did not reproduce | dropped, counted, and never written up on its own | `dropped — no reproduction` |
| `suggestion` or `nitpick` | nothing at all; a count | `recorded` |
| reproduced, and this lane structurally cannot hold the fix | `defer` against ONE named blocker | `deferred — <blocker>` |

**The agent fixes a reproduced `critical` and nothing else.** An `important` is real and it is not
urgent, and fixing it is a new unreviewed edit at the end of a lane, which is the loop this section
exists to end — one turn later, with a fresh finding attached. Escalation is not a soft refusal: the
operator sees it, with its receipt and a one-line recommendation, and the default is that it ships as
recorded.

⛔ **"It's cheap" is not a reason.** Twenty cheap fixes is not cheap — it is the audit that never ends,
and every one of them lands *after* the checks ran, unreviewed.

⛔ **Record the tail in ONE line**: how many were fixed, escalated and deferred, and how many were
dropped for want of a reproduction. Not one line each. Name individually only a finding whose
reproduction disagreed with its label, in either direction — that is the calibration signal, and it
is the only thing in the tail worth a sentence.

---

## 7. Severity — what actually blocks

| Verdict | Trigger |
|---|---|
| **FAIL** | An **open reproduced** `critical`, with its receipt on disk. Or: a §6 machine check errors on **changed lines**; a §2 banned pattern (bare `except:`, `any`, dead abstraction shipped); a committed secret. |
| **CONCERNS** | An **open reproduced** `important` — escalated to the operator, or deferred behind a named blocker. Also a dead lens, §1 comment-contract gaps, and §2 judgment calls (bloat, duplication, unnecessary structure). |
| **PASS** | Machine floor green on changed lines, no judgment findings above noise, and no open reproduced finding. |

Objective things block. Taste does not — it gets recorded, argued, and fixed on its merits.

**The floor is computed AT THE STAMP, on the rows that are still OPEN (SCC-447)** — never at triage,
from whatever the lenses first returned. That is the one change that gives the floor a way down, and
is why the loop ended: the floor moves as the work closes rows. A row closed by a
fix and a green pin is not a reason to hold a lane; it is the lane working as designed. There are
exactly two ways down and both are evidence: a receipt showing the command does **not** fail, or a
fix with a pin seen red then green. Any other downgrade is the caller overruling the review.

**CONCERNS is a shippable verdict, and the go/no-go is the operator's word.** It means the review
found something real that this lane is not fixing — an escalated `important`, or a defer behind a
named blocker — and the operator decides. FAIL is the blocker; CONCERNS is information, and
no command, door or agent may treat it as a blocker on its own authority.

**One review per lane.** The lenses run ONCE. When the fixes land, the retest is the pins
named in the `fixed` rows plus the enforcement suite once through the receipt writer — never a second
fan-out over the same diff. Measured over 138 reviews on disk, a re-review converted a non-PASS to
PASS one time in seven and cost a full roster every time.
A second full roster needs the operator's written word, and `walkthrough_roster.py` refuses a
walkthrough carrying two roster headers without it.
