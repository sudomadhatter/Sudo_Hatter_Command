# Implementation Plan — Code Standards: define it, document it, gate it

**Date:** 2026-07-23
**Scope:** lobby master `.agents/` → 4 LLM surfaces (Claude · opencode · Antigravity/Gemini · Codex) → `AGY_AVIATIONCHAT` + `Fresh_Workspace_BMAD`
**Status:** awaiting Daniel's approval

---

## 1. Context — why this is being done

Daniel asked for a verified code standard: best practices written down, an agent-comment convention
captured as a skill/rule, and a gate inside `/sudo-code-review` that proves new code is clean.

Investigation found the standard exists on paper and is enforced **nowhere**:

| Layer | Current state | Evidence |
|---|---|---|
| The rule | 36 lines, three thin tables. Frontmatter says `activation: Always On`; `rules/INDEX.md:27` lists it **on-demand**. Ambiguous whether it loads at all. | `.agents/rules/code-standards.md` |
| The comment convention | **Undocumented.** 852 `# Story 21.12:` / `// Story 17.5 —` provenance comments across 178 AviationChat files — pure emergent habit, no rule mentions it. | grep across `Projects/AGY_AVIATIONCHAT` |
| The review | `/sudo-code-review` has an adversarial pass (Step 1) and a **test** gate (Steps 2–3). No standards gate exists. | `.agents/commands/sudo-code-review.md` |
| The machine floor | Backend `Lint (ruff)` and frontend `Lint (ESLint)` are **both `continue-on-error: true`** — report-only, no named owner, no tracked expiry. | `pr-check.yml:47`, `pr-check.yml:82` |
| Local runnability | `ruff` is **not installed** in `backend/.venv` and absent from `requirements.txt`. CI does `pip install ruff` inline. **No local lint entrypoint exists.** | `backend/.venv/Scripts/` listing |
| ESLint severity | 5 rules downgraded to `warn` with a bare `TODO: Ratchet these back` — no owner, no expiry. | `frontend/eslint.config.mjs` |

The last four rows are a direct violation of the project's own
`tests-must-gate-for-real.md` — §3 ("a soft gate is a ONE-RUN window with a named owner + a tracked
expiry — never open-ended") and §2 ("CI must run the REAL suite entrypoint... the *same* one the local
gate runs"). The lint gate today is the exact "reads as protection, protects nothing" shape that rule
was written to kill.

**Intended outcome:** one written standard, one auditor skill, one gate in `/sudo-code-review` that can
actually fail, and a machine floor that is runnable locally and blocking on new code.

### Decisions taken (Daniel, 2026-07-23)
1. **Comment convention** — Daniel deferred ("I was told this is common practice"). Confirmed: it is
   **anchor comments**. Taking **both** markers, they do different jobs:
   - `Story X.Y (AC-n):` → *why does this code exist* (852 instances already — codifying reality)
   - `AIDEV-NOTE:` → *what will bite the next agent who touches this* (new)
2. **CI lint** — **ratchet**: hard gate on changed files only; full-repo pass stays report-only but
   gains a named owner + tracked expiry.
3. **Gate teeth** — machine checks can **FAIL**; judgment calls cap at **CONCERNS**.

---

## 2. What gets built

### A. Rewrite the standard — `.agents/rules/code-standards.md`

Keep the existing backend/frontend/general tables (they're correct, just thin). Add four sections and
fix the activation ambiguity.

**A1. Frontmatter fix.** Drop `activation: Always On`; the INDEX is right that this is on-demand
(loading full style tables into every session burns context for no gain). Rewrite `description:` so its
trigger is explicit, matching the INDEX row convention.

**A2. New — The Comment Contract.** The part Daniel remembered.

```
# Story 14.6 (FR40): additive + best-effort — a grading failure
# must never break the chat stream.
await _emit_grading_event(...)

# AIDEV-NOTE: single-writer chokepoint. Any profile write routes HERE.
# A cache belongs in profile_service (set_field-invalidated), never on chat_sessions.
def set_field(...):
```

| Marker | Required when | Rules |
|---|---|---|
| `Story <E>.<S> (AC-n):` | any non-obvious block a story produced — workaround, fallback, ordering constraint, defensive branch, magic constant | states the *why*, not the *what*; one line where possible |
| `AIDEV-NOTE:` | a trap the next agent would otherwise re-break | ≤2 lines, ~120 chars/line; **never delete or rewrite one without instruction** — if your change invalidates it, *update* it; grep `AIDEV-` before editing a complex file |
| `AIDEV-TODO:` | deferred work | must carry **owner + tracked task**, else it is banned |

Bans: commented-out code (git has it) · `TODO`/`FIXME` without owner+ticket · comments that restate the
code · stale comments left behind by a change (already covered by `karpathy-guidelines` "Surgical
Changes" — cross-linked, not duplicated). Anchor notes are for non-obvious traps only — spraying them
is its own failure mode.

**A3. New — AI-drift bans.** What "clean" means beyond style; this is what the judgment half of the
gate hunts:
- No new abstraction with a single caller.
- No re-implementing what exists — search first (this is the review's most common finding).
- No `any` in TS. No bare `except:` in Python.
- No defensive try/except wrapping code that cannot fail.
- No unused params, dead branches, leftover debug prints.
- No new file where an existing module is the home.

**A4. New — The machine floor.** Exact runnable commands, so "clean" is checkable not arguable:

| Check | Command |
|---|---|
| Backend lint | `backend/.venv/Scripts/python.exe -m ruff check backend/` |
| Backend types | `backend/.venv/Scripts/pyrefly.exe check` |
| Frontend lint | `npm run lint` (in `frontend/`) |
| Frontend types | `npx tsc --noEmit` (in `frontend/`) |

Uses the venv interpreter per the `agy-venv-interpreter-discipline` memory — bare `python` is the
drifted global 3.14 and produces false findings.

### B. New skill — `.agents/skills/clean-code-audit/SKILL.md`

The auditor. Diff-scoped (new code only — legacy debt is not this story's problem, same grandfathering
discipline the test gate already uses). Two halves:

1. **Machine half** — run the four A4 commands, scoped to changed files. Objective. Can FAIL.
2. **Judgment half** — an LLM pass for what linters cannot see: comment contract compliance (A2),
   AI-drift bans (A3), naming, dead abstractions. Caps at CONCERNS.

Emits findings as `file:line` + severity + category, so `/sudo-code-review` can fold them into its
verdict file without reformatting.

Standalone-runnable too (`/clean-code-audit`), not only via the review — useful mid-story.

### C. Gate it — `.agents/commands/sudo-code-review.md`

Insert **Step 3.5 — Clean-Code Gate** between the test gate (Step 3) and the verdict (Step 4). It
invokes the skill against the story diff, in the story worktree that Step 0.5 already resolved.

Extend the Step 4 verdict rules:
- **FAIL** — existing triggers, **plus** a ruff/eslint/tsc error on changed lines, or a banned pattern
  (bare `except:`, `any`, committed secret).
- **CONCERNS** — existing triggers, **plus** comment-contract gaps, AI-drift findings, missing story
  provenance.
- Verdict file gains a `## Clean-Code Gate` section with the actual command output pasted — same
  evidence discipline the test gate already demands.

### D. Wire the machine floor for real — `AGY_AVIATIONCHAT`

The "fix the code if needed" part. Three edits, no product-code changes:

1. **`backend/requirements.txt`** — add `ruff==<pin matching CI>`. Dev tooling already lives here by
   house convention (`pytest`, `pytest-cov` are in this file). This is what makes the local command in
   A4 exist at all, closing the `tests-must-gate-for-real` §2 hole.
2. **`.github/workflows/pr-check.yml`** — the ratchet:
   - `actions/checkout@v4` needs `fetch-depth: 0` (default depth-1 cannot diff against the base).
   - New **hard** step: lint only files changed vs `origin/${{ github.base_ref }}`. No
     `continue-on-error`.
   - Existing full-repo step **stays** `continue-on-error: true` but gains an owner + expiry comment
     pointing at a tracked task, satisfying `tests-must-gate-for-real` §3.
   - Same shape for both backend (ruff) and frontend (ESLint).
3. **`frontend/eslint.config.mjs`** — put an owner + tracked task on the 5 `warn` downgrades. The
   bare `TODO: Ratchet these back` is the "report-only forever" trap in miniature.

> **Note (not in scope, flagged):** `pr-check.yml` triggers only on `pull_request: branches: [main]`.
> Work landing on `main_debug` never runs this gate. Worth a decision later; not changed here.

### E. Propagate — 4 platforms, 3 repos

Authorship stays single-source in the lobby `.agents/`, then:

| Step | Command | Reach |
|---|---|---|
| 1 | `/sync-agents` (no arg) | lobby `.claude/` + `.opencode/` **and** the opencode / Antigravity / Codex machine-global caches |
| 2 | `/sync-agents Projects/AGY_AVIATIONCHAT` | vendors master `.agents/` (rules + skills + commands) into the project |
| 3 | `/sync-agents Projects/Fresh_Workspace_BMAD` | same — keeps the living template current per `living-template-sync` |

Codex needs no adapter (reads `AGENTS.md` + `.agents/skills/` natively). `_bmad/` is excluded from the
vendor by design — untouched. Run `-WhatIf` first on each.

Index updates: a revised `code-standards` row in `.agents/rules/INDEX.md`, a new
`clean-code-audit` row in `.agents/skills/INDEX.md`.

**D applies to AviationChat only.** `Fresh_Workspace_BMAD` has its own `pr-check.yml` and a
`pyrefly.toml`; whether the template gets the same ratchet is a separate call — flagged, not assumed.

---

## 3. Files touched

**Lobby master (authoring):**
- `.agents/rules/code-standards.md` — rewrite
- `.agents/skills/clean-code-audit/SKILL.md` — new
- `.agents/commands/sudo-code-review.md` — Step 3.5 + Step 4 verdict rules
- `.agents/rules/INDEX.md`, `.agents/skills/INDEX.md` — rows

**AviationChat (the code fix):**
- `backend/requirements.txt`, `.github/workflows/pr-check.yml`, `frontend/eslint.config.mjs`

**Generated by sync (never hand-edited):** `.claude/`, `.opencode/`, global caches, both projects'
vendored `.agents/`.

---

## 4. Verification

1. **Standard loads** — `/sudo-code-review` on a real story; confirm it reads `code-standards.md` and
   echoes the Step 3.5 header.
2. **Machine floor runs locally** — after D1, `backend/.venv/Scripts/python.exe -m ruff check backend/`
   returns a real result instead of `No module named ruff`. Paste actual output.
3. **The gate can actually fail** — the honesty check this whole plan exists to enforce. Introduce a
   deliberate violation on a scratch branch (a bare `except:` plus an `any`), run the gate, confirm
   **FAIL** with correct `file:line`. Then remove it and confirm PASS. A gate never seen red is an
   unproven gate.
4. **CI ratchet is real** — `-WhatIf`-equivalent check that the changed-files lint step has no
   `continue-on-error`, and that `fetch-depth: 0` is set (without it the diff silently returns nothing
   and the hard gate passes vacuously — the exact failure mode `tests-must-gate-for-real` describes).
5. **Judgment half works** — run the audit against a diff with a `Story X.Y`-less non-obvious block;
   confirm CONCERNS, not FAIL.
6. **All 4 surfaces resolve** — `& ".agents/scripts/sync-agents.ps1" -Maintained -Status` clean; spot-check
   the command appears in the opencode + Antigravity + Codex caches and both projects' `.agents/`.

---

## 5. Open questions for Daniel

1. **Ruff pin** — CI currently does bare `pip install ruff` (unpinned, so CI can drift). Pin to the
   current release in `requirements.txt` and make CI install from it?
2. **`Fresh_Workspace_BMAD` CI** — apply the same D2/D3 ratchet to the template, or lobby-rule-only for now?
3. **`main_debug` coverage** — `pr-check.yml` only fires on PRs into `main`. Out of scope here; worth its own task.
