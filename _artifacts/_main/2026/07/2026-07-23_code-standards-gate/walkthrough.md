# Walkthrough — Code Standards: define it, document it, gate it

**Date:** 2026-07-23 → 2026-07-24 · **Plan:** `implementation_plan.md` (approved)
**Outcome:** shipped. One written standard, one auditor, one gate that can fail, and a machine floor
that is now locally runnable and blocking on new code.

---

## What was wrong

Daniel asked whether a code standard existed and whether it was being kept. It existed; nothing kept it.

- `code-standards.md` was 36 lines and self-contradictory — frontmatter `activation: Always On`, INDEX
  row said on-demand.
- The comment convention he half-remembered was real (852 `Story X.Y` comments across 178 AviationChat
  files) and documented nowhere. It survived by imitation alone.
- `/sudo-code-review` gated *tests* only. No standards gate existed.
- Both CI lint jobs were `continue-on-error: true`, "report-only," with no owner and no expiry —
  a direct violation of the repo's own `tests-must-gate-for-real` §3.
- `ruff` was **not installed** in `backend/.venv` and absent from `requirements.txt`; CI pip-installed it
  inline, unpinned. **No local lint entrypoint existed** — §2 of the same rule.

## What was built

| # | Change | File |
|---|---|---|
| 1 | Standard rewritten — comment contract, AI-drift bans, machine floor, FAIL-vs-CONCERNS split; activation ambiguity resolved to on-demand | `.agents/rules/code-standards.md` |
| 2 | New auditor — diff-scoped; machine half can FAIL, judgment half caps at CONCERNS | `.agents/commands/clean-code-audit.md` + `.agents/skills/clean-code-audit/SKILL.md` |
| 3 | Gate wired in as **Step 3.5**, independent of the `sudo-tests.yaml` opt-in; Step 4 verdict rules extended | `.agents/commands/sudo-code-review.md` |
| 4 | Index rows | `.agents/rules/INDEX.md` · `.agents/skills/INDEX.md` |
| 5 | `ruff==0.16.0` pinned so local == CI | `backend/requirements.txt` (AGY) |
| 6 | Lint ratchet: hard gate on changed files + report-only full pass **with owner + expiry**; `fetch-depth: 0` | `.github/workflows/pr-check.yml` (AGY) |
| 7 | Owner + expiry on the 5 `warn` downgrades | `frontend/eslint.config.mjs` (AGY) |

**The two comment markers.** `Story <E>.<S> (AC-n):` answers *why this code exists* — codifying the 852
that already existed, so zero migration. `AIDEV-NOTE:` is new and answers *what will bite the next agent*
— ≤2 lines, and **never deleted without instruction**; if a change invalidates one, it gets updated.

## Verification — actually run, not asserted

| Check | Result |
|---|---|
| ruff installed + runnable locally | `ruff 0.16.0` — was `No module named ruff` |
| **Gate can go RED** (the honesty check) | probe file → `E722 bare except` + `F401`, **exit 1** |
| CI logic (a) bogus base sha | `::error::Cannot resolve PR base` → **exit 1**, no vacuous pass |
| CI logic (b) valid base, no `.py` changed | "nothing to lint" → exit 0, honest |
| CI logic (c) valid base, bad `.py` in diff | file listed, ruff → **exit 1** |
| `pr-check.yml` parses; hard steps have no `continue-on-error`; `fetch-depth: 0` on both checkouts | confirmed via YAML parse |
| Existing tripwires not broken | `TestHarnessWiringTripwires` + `test_coverage_instrument` — **6 passed** |
| All 4 surfaces resolve the new command | Claude `.claude/skills/` · opencode global · Antigravity `global_workflows` · Codex `.agents/skills/` (native) — all present; `Step 3.5` in every `sudo-code-review` copy |

The probe commit was dropped (`git reset --hard HEAD~1`); worktree left clean.

## Where it landed

- **Lobby** (`main_debug`) — authored, synced to all 4 surfaces. **Uncommitted** — landing on `main_debug`
  needs per-action sign-off (`git-policy`), and the tree also holds another session's work
  (`sudo-switch-machine`, `sudo-mobile-error-team`, `.gitignore`).
- **AGY_AVIATIONCHAT** — worktree `.claude/worktrees/code-standards-gate`, branch
  `claude/code-standards-gate`, two commits: `985c2222` (CI ratchet) + `b304e5a9` (standards artifacts).
  Not landed.
- **Fresh_Workspace_BMAD** — 27 files synced into the working tree, **uncommitted**: its local trunk is
  `main`, which is owner-only.

## Flagged, not done

1. **`pr-check.yml` only fires on `pull_request: branches: [main]`.** Everything landing on `main_debug`
   — most of the work — never runs this gate. Bigger than this task; needs its own decision.
2. **Fresh's backend lint is still not wired.** `ruff==0.16.0` was added to
   `Fresh_Workspace_BMAD/backend/requirements.txt` (2026-07-24, on Daniel's go-ahead) so a cloned project
   is not born with an unrunnable machine floor. Two gaps remain there:
   - Fresh's `pyproject.toml` has **no `[tool.ruff]` section**, so `ruff check backend/` would run with
     library defaults (line-length 88, E4/E7/E9/F only) — contradicting `code-standards` §3, which states
     120 to match the ruff config. AGY's config can't be copied wholesale: its `per-file-ignores` name
     AGY-only paths (`scripts_legacy/**`, `agents/**/prompts.py`).
   - Fresh's `pr-check.yml` has **no backend lint step at all** (its frontend `npm run lint` is already a
     hard gate — better than AGY's was). The changed-files ratchet was scoped to AGY by the plan.
3. **The AGY sync swept in ~76 files of unrelated master drift** (gitnexus skills, INDEX files) into the
   worktree. Left uncommitted deliberately — committing it is a separate call.
4. **Neither report-only lint pass has a measured debt count yet.** The owner/expiry comments point at
   `_my_resources/open_tasks/todo_list.md`; the tasks still need writing there (that file is read-only to
   agents by standing rule).
