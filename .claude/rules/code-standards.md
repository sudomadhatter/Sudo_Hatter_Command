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
| **Both machines** | This system is driven from a Mac **and** a PC. `python3` exists on one and `python` on the other, so **never hardcode either** — carry `sys.executable` down, or probe `python3 → python → py`. A `C:/…` path, a `;` separator, `robocopy`, or a bare `python` in a committed script is a finding, not a portability nicety: it works where it was written and dies on the other machine. |

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
> These commands read `Scripts/…exe` until 2026-08-18, so **every Mac run of the most-used audit found
> its own machine floor unrunnable** — and under the audit's own rule a missing tool "is a finding, not
> a skip", so the objective half did nothing while reporting normally. Resolve it once:
>
> ```bash
> VENV=backend/.venv/bin; [ -d "$VENV" ] || VENV=backend/.venv/Scripts   # POSIX first, then Windows
> ```
>
> **Use the venv's own executables.** Bare `python` / bare `ruff` is the drifted global install and
> produces false missing-dependency findings — and bare `python` does not exist on the Mac at all
> (§5, Both machines).
>
> **And pyrefly needs the interpreter PINNED even when invoked from the venv** (SCC-312, measured
> 2026-08-24 on the Mac): `<VENV>/pyrefly check` bare resolves its site-packages from the SYSTEM
> python — 949 errors, 669 of them fabricated `missing-import`, burying the real findings — while
> the same run with `--python-interpreter-path <VENV>/python` reported 0 missing-import. The pin
> belongs at the CALL SITE, never in a project's `pyrefly.toml` (AGY's states why: an absolute
> path or interpreter pin in config would split CI and local onto different interpreters).

A project whose stack differs declares its own commands in its `AGENTS.md`; these are the defaults for
the FastAPI + Next.js house shape.

---

## 6.5 Disposition — the ASSESSOR decides what is REAL, not the lens

> Hoisted here by SCC-205 because it is **disposition law, not review-engine law**: it governs every
> command that produces findings — both clean-code audits, both code reviews, both self-audits — and
> it lived in exactly one place, `code-review-engine/steps/step-01-review.md`, owned by no rule.
> This rule already owns the FAIL-vs-CONCERNS split (§7), so it is the one place all four audits bind.

**The ruling, in the operator's words (2026-08-17): *"the agent's job is to find things so it always
will — this is how we end up in this loop. The agent who assesses the finds has to decide what's real
and what's just the agent finding something to report. We fix actual issues."***

⛔ **A lens's severity label is an INPUT, not a verdict.** Every hunter is told to be exhaustive and is
measured by what it returns, so it will always return something, and it grades its own work. Treating
`critical` as an instruction to fix is how a four-lens review becomes an unbounded queue: each pass
finds more, each fix is a new unreviewed edit, and the lane never closes. **The orchestrator running
the audit is the assessor. Nobody else is.**

**Assess every finding against three questions, in order. All three must be YES to fix.**

1. **Is it REAL?** Can you state the concrete failure — *this input, this state, this wrong output*? A
   finding phrased as *"may be"*, *"could lead to"*, *"consider"* or *"is not covered"* has not
   established that anything is broken. **Reproduce it, or drop it.**
2. **Does it change BEHAVIOUR?** A gate that fails open, a wrong answer, a crash, a refusal of
   something legitimate, lost data. Naming, structure, wording, a missing test for a branch that is
   already correct — these do not.
3. **Is it in THIS lane's diff?** Pre-existing debt in an untouched file is not this task's work.

**Fix what passes all three. Dismiss the rest — including anything a lens called `critical`.** The
label neither promotes nor protects a finding; the assessment does.

⛔ **"It's cheap" is not a reason.** Twenty cheap fixes is not cheap — it is the audit that never ends,
and every one of them lands *after* the checks ran, unreviewed.

⛔ **Record the tail in ONE line**: how many findings came back, how many were assessed real and fixed,
and that the rest were dismissed under this ruling. Not one line each. Name individually only a finding
whose ASSESSMENT disagreed with its label, in either direction — that is the calibration signal.

---

## 7. Severity — what actually blocks

| Verdict | Trigger |
|---|---|
| **FAIL** | A §6 machine check errors on **changed lines**. A §2 banned pattern (bare `except:`, `any`, dead abstraction shipped). A committed secret. |
| **CONCERNS** | §1 comment-contract gaps (missing story provenance, a comment restating code, an unowned TODO). §2 judgment calls — bloat, duplication, unnecessary structure. |
| **PASS** | Machine floor green on changed lines, no judgment findings above noise. |

Objective things block. Taste does not — it gets recorded, argued, and fixed on its merits.
