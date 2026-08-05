---
name: agy-ruff-changed-files-is-a-hard-gate
description: "AGY's pr-check.yml lints CHANGED backend .py files as a hard gate with I001 (isort) selected and NOT ignored for tests — so a new test file with unsorted imports fails CI; run ruff before every ③"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2007a161-79d4-4c7d-9f5b-330e3df9b16b
  modified: 2026-07-30T16:57:59.388Z
---

**2026-07-30 (story 21.7 ③).** Story 21.7 shipped through ① and ② and reached ③ with a **CI-failing
lint error** in its contract file. Three facts combine, and each is individually easy to miss:

1. **`pr-check.yml:52-69` lints only the CHANGED backend `.py` files — and it is a HARD gate.** The step
   carries no `continue-on-error` and its comment says it must never gain one. (The *full-repo* ruff step
   right below it IS report-only, which is what makes people assume ruff is soft here. It is not.)
2. **`I` (isort) is in `[tool.ruff.lint] select`** (`pyproject.toml:70-76`).
3. **`backend/tests/**` per-file-ignores cover only `F401`, `F811`, `E501`** (`:88-90`) — **not `I001`**.

So an unsorted import block in a brand-new **test** file is a red CI run, even though tests are otherwise
leniently linted and `src = ["backend"]` reads like tests are excluded (they are not — the CLI is passed
explicit paths).

**Also found:** `backend/.venv` was running **ruff 0.15.21** while `backend/requirements.txt:56` pins
**`ruff==0.16.0`** — and the `AIDEV-NOTE` at `:52-55` says that pin exists *precisely* so "CI and
`backend/.venv` run the identical linter version." The venv had drifted off the thing that guarantees the
local check matches CI.

**Why it matters:** ② never ran the machine floor at all. The story's *reasoning* was excellent — its
self-audit caught a finding that would have red-walled an unrelated P0 gate — which is exactly how a diff
gets to ③ with a trivial mechanical failure nobody looked for. Good judgment does not substitute for
running the command.

**How to apply:**
- Run `backend\.venv\Scripts\python.exe -m ruff check <the story's changed .py files>` in **②**, not just
  at ③. Pass explicit paths — that is what CI does.
- Include **test** files in that command. They are changed files too.
- `ruff check --fix` for `I001` can **detach an explanatory comment** from the import block it documents
  (it hoists the sorted import above the comment). Read the diff after auto-fixing; re-author the comment
  rather than leaving it dangling above an unrelated line.
- If ruff output looks unexpected, check the venv version against the pin before believing it:
  `pip install -r backend/requirements.txt`.

**Update, same session:** the venv drift was fixed (`ruff==0.16.0` installed), and **pyrefly now sits
beside ruff in exactly this shape** — a `Types (pyrefly) — changed files` HARD gate plus a report-only
full-repo step. So the rule below is now two commands, not one: run **both** `ruff check` and
`pyrefly check` over the story's changed `.py` files at ②.

**And a `tests-must-gate-for-real` §3 trap worth generalising:** the ruff report-only step has cited
`_my_resources/open_tasks/todo_list.md → "clear backend ruff debt"` as its tracked EXPIRY since it was
written, and **that task did not exist**. The soft gate satisfied §3 on paper only. When a workflow
comment names an owner and a tracked task, **open the task file and confirm the line is there** — a
citation is not a tracking system. Both expiries (ruff + pyrefly) are real lines there now.

**The other half, from 21.4 ③ (same day, parallel lane): it lints WHOLE changed FILES, so lint debt you
did not write becomes your PR's blocker.** `FILES=$(git diff --name-only …); ruff check $FILES` — the
whole file, not your hunks. Story 21.4 touched 37 `.py` files and inherited **14 pre-existing I001/F841
errors**; a ③ gate scoped to changed *lines* (which is how `/sudo-code-review` Step 3.5 phrases it) reports
PASS while CI fails the PR. So:
- Run ruff on the **changed FILE list**, then run the SAME list against `main_debug` (the sibling shared
  checkout has the same `pyproject.toml`) to split NEW from INHERITED. Fix both — inherited debt in a file
  you touched is genuinely yours now — and say which was which in the verdict.
- **Re-run the suite after `--fix`.** isort reorders imports, and files like
  `test_hr_profile_single_writer.py` carry deliberate `import backend.main`-before-router ordering
  workarounds that a reorder can break. (In 21.4 the invariant survived — verify, don't assume.)
- **pyrefly was the opposite case on `main_debug` — until it landed the same day.** The 21.4 lane correctly
  observed it was not pinned and not in CI *on the trunk*, because the gate was still riding the 21.7
  branch. **It landed at `9358974a` on 2026-07-30**, so `main_debug` now DOES carry the pin
  (`pyrefly==1.1.1`) and both CI steps. Two lanes reading the trunk hours apart got opposite true answers —
  which is the actual lesson: **check the trunk, never assume, in either direction.** Gating on
  *regression vs a `main_debug` baseline* rather than an absolute count (21.4: 482 vs 489 repo-wide, net
  −7) stays the right instinct for the full-repo number, since the report-only step is soft by design; the
  **changed-files** step is the hard one and expects zero.

**⚠️ WHEN these gates actually fire — established at the 21.4 landing:** `pr-check.yml` is
`on: pull_request` → `branches: [main]`. A **direct push to `main_debug` — which is how every story
lands (`/sudo-update-sprint-memory` Step 7) — triggers NOTHING.** Both hard gates bite only at PROMOTE
(`main_debug → main`, via `/sudo-push-e2e`), where the "changed files" set is the whole promote diff and
inherits every story's accumulated debt. So: a red ruff/pyrefly result never blocks a story landing, but
it is not free either — it queues up for the promote. Say which of the two you mean; "it would fail CI"
is wrong for a landing and right for a promote.

Related: [[agy-typecheck-is-enforced-nowhere]] (the type half — as of 2026-07-30 it is wired the same
way), [[agy-database-import-is-an-init-step]], [[e2e-gate-fiction-test-guardrails]],
[[agy-canonical-test-venv]], [[governance-gate-scans-venv]].
