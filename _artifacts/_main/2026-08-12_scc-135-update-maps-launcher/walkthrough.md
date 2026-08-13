# SCC-135 — Un-invert `/smh-update-maps-indexes` so Antigravity gets a thin launcher

**Branch:** `chore/SCC-135-update-maps-launcher` · **Date:** 2026-08-12
**Trigger:** the operator ran `/smh-update-maps-indexes` in the Antigravity IDE and reported it
"ran, but output was thin/wrong."

---

## 1. What was actually wrong

Antigravity reads its `/` menu from `.agents/workflows/`, where a file over **12,000 characters** is
**truncated at the cap, not rejected**. The prior write-up in `sync-agents.ps1` said "silently
drops" — that word is what kept this invisible, because a dropped file fails obviously and a
truncated one runs and looks fine.

`/smh-update-maps-indexes` was the **only** command in the toolkit whose body lived in
`.agents/workflows/` while `.agents/commands/` held a 4,167-char wrapper. That inversion put it on
the mirror's `$excluded` list, which permanently exempted it from the thin-launcher rule that
protects the other twelve oversized commands.

At 39,594 characters, **70% never reached the agent.** Measured cut point:

| Reached the agent (0–12,000) | Never reached it (12,000–39,594) |
|---|---|
| Header, "What this maintains" (target list), Step 0 (preflight + linter), half of Step 0.5 — cut mid-sentence | Steps 1, 2, 3, 3.5–3.9, **Step 4 (findings report + STOP approval gate)**, Step 5, Step 6, Guardrails |

So the agent knew *what* to reconcile and *how to run the linter*, then improvised with no approval
gate. That is precisely the reported symptom.

### Damage from the ungated run (found in the working tree, carried on this branch)

- `_artifacts/_main/INDEX.md` gained 9 rows but **missed `2026-08-12_scc-117-branch-prune/`**, which
  exists on disk — the row the SessionStart hook flags.
- `2026-08-10_scc-77-main-write-gate/` was inserted **between two `2026-08-11` rows** (date order broken).
- `docs/.maps-state.json` anchored to `af821b0` while HEAD was `2151568`.
- No Step 4 findings report was ever presented.

The context-hygiene move (`active-context.md` → `active-context-archive.md`) and the `todo_list.md`
command-name fix were both done **correctly** — move-never-delete was honoured, content verbatim.

---

## 2. What shipped

1. **Body moved** `.agents/workflows/smh-update-maps-indexes.md` → `.agents/commands/smh-update-maps-indexes.md`
   (40,414 chars). Frontmatter now matches sibling commands: `description:` only, **no `platforms:` key**
   (= all four platforms), no `name:` key.
2. **Two folds** — the only wrapper instructions with no counterpart in the body, verified by grep:
   - the two-machine `python3` / `python` caveat (Mac vs python.org PC)
   - ⛔ do not pass `--dry-run` through to `check_maps.py` — it is not a supported flag there
   The other seven wrapper notes were already covered by the body and were dropped as duplication.
3. **`$excluded` shrunk** to `@('smh-adviser-board.md', 'INDEX.md')` with a comment recording why
   `smh-update-maps-indexes.md` must never be re-added.
4. **Failure-mode text corrected** in the generator and its header comment: "silently dropped" →
   truncated-at-the-cap. All 13 generated launchers regenerated with the accurate wording.
5. **SOP updated** — a new callout under the door table plus a warning on the command's own row,
   including "if you ran it in Antigravity before 2026-08-12, re-check what it edited."

Hop count collapsed from three to one on every platform:

```
before:  skill/workflow -> commands/<name>.md (4.2k wrapper w/ its own notes) -> workflows/<name>.md (39.6k body)
after:   skill/launcher -> commands/<name>.md (the body)
```

---

## 3. Acceptance evidence

| # | Acceptance | Result |
|---|---|---|
| 1 | Workflow is a generated thin launcher, standard shape | **1,082 chars**, `THIN LAUNCHER` marker present |
| 2 | No workflow file over 12,000 chars | **NONE** (was 1: this file at 39,594) |
| 3 | Command carries the full body; each fold present exactly once | Step 4 / Step 6 / Guardrails ×1 each; both folds ×1; old wrapper text ×0 |
| 4 | Removed from `$excluded`, comment updated | done |
| 5 | Sync is idempotent | second run — `git status` hash identical |
| 6 | Lane gate green | see below |

**Gates, all run bare (never piped — a pipe reports the exit code of the last stage):**

```
run_all.py                 21/21 files passed        exit 0
workflow_lint --toolkit-only  0 errors, 0 warnings   exit 0   (8 pre-existing BOM infos, bmad testarch)
test_command_surfaces.py   43/43 passed              exit 0
sop_currency.py            23 paths                  exit 0
```

`sop_currency` positive control: `--paths .agents/commands/smh-code-review.md` alone → **exit 1**,
so the gate demonstrably has teeth on this change set rather than passing vacuously.

Launcher bodies verified **ASCII-only**, preserving the PS 5.1 no-BOM constraint the generator
documents (a BOM-less `.ps1` parses as ANSI and would mojibake any non-ASCII literal).

---

## 4. Two traps worth recording

**A gate can report a false PASS from shell quoting alone.** `sop_currency --paths $PATHS` returned
**exit 0** on a change set it should have rejected — zsh does *not* word-split unquoted variables, so
argparse received a single argument containing 11 space-joined paths, matched no surface, and passed.
`${=PATHS}` (or `$(git diff --name-only)`, which does split) returns the correct **exit 1**. This is
the same family as the piped-gate trap: the gate ran, printed nothing alarming, and exited clean.

**`grep -E` does not accept `\|` as alternation.** An initial uniqueness check used patterns like
`'MASTER\|master'` under `-E`, where `\|` is a *literal pipe*. Three notes were reported as absent
from the body when they were present 7, 4 and 12 times. Re-run with real alternation before
concluding anything is missing.

---

## 5. Deliberately out of scope

- **Splitting the body into sub-commands.** Now unnecessary for the cap — the launcher handles any
  size. Still worth doing for agent attention (~11k of the 40k is preamble, a report template used
  only at Step 4, and a guardrails recap). ⛔ Do **not** split detect-vs-apply into separate `/`
  commands: Step 4's STOP is the safety property, and a separately invokable apply half routes
  around it.
- **Repairing the bad run's output** beyond carrying it forward — the missing `scc-117` INDEX row,
  the out-of-order `scc-77` row, and the non-HEAD anchor are all still present on this branch.
- `_artifacts/_main/2026-08-12_scc-119-subtask-rule/` was left **untracked**: the SCC-119 worktree
  holds its own newer copy (30,191 b vs 29,554 b), so the copy on main is a stray duplicate.
