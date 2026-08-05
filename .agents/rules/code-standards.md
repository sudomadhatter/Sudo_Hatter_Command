---
name: code-standards
description: "Activates when writing, reviewing, or gating code — backend (Python/FastAPI) or frontend (React/TypeScript). The house definition of 'clean': the comment contract (Story provenance + AIDEV-NOTE anchors), the AI-drift bans, style/organization, and the machine-checkable floor. The `clean-code-audit` skill and `/sudo-code-review` Step 3.5 both enforce THIS file — edit the standard here and the gate follows."
since: 2026-06-24
---

# Code Standards — the house definition of "clean"

This file is the standard. The **`clean-code-audit`** skill is the auditor that checks a diff against
it, and **`/sudo-code-review` Step 3.5** is the gate that can fail a story on it. There is one
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

---

## 6. The Machine Floor

"Clean" has to be checkable, not arguable. These are the commands — the **same ones CI runs**, per
`tests-must-gate-for-real` §2. If a check cannot be run locally, it is not a gate.

| Check | Command (from the project root) |
|---|---|
| Backend lint | `backend/.venv/Scripts/python.exe -m ruff check backend/` |
| Backend types | `backend/.venv/Scripts/pyrefly.exe check` |
| Frontend lint | `npm run lint` (in `frontend/`) |
| Frontend types | `npx tsc --noEmit` (in `frontend/`) |

> **Use the venv interpreter.** Bare `python` is the drifted global install and produces false
> missing-dependency findings. Always `backend/.venv/Scripts/python.exe -m <tool>`.

A project whose stack differs declares its own commands in its `AGENTS.md`; these are the defaults for
the FastAPI + Next.js house shape.

---

## 7. Severity — what actually blocks

| Verdict | Trigger |
|---|---|
| **FAIL** | A §6 machine check errors on **changed lines**. A §2 banned pattern (bare `except:`, `any`, dead abstraction shipped). A committed secret. |
| **CONCERNS** | §1 comment-contract gaps (missing story provenance, a comment restating code, an unowned TODO). §2 judgment calls — bloat, duplication, unnecessary structure. |
| **PASS** | Machine floor green on changed lines, no judgment findings above noise. |

Objective things block. Taste does not — it gets recorded, argued, and fixed on its merits.
