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

---

## Self-Audit (2026-08-12) — `retroactive`

**Mode: POST-DEV.** The work was already built and pushed at `0fef0c8` when this ran, and no
`implementation_plan.md` was ever written for SCC-135. Per `/smh-self-audit` Step 0 this is the
retroactive path: audited against the ticket's SCOPE + ACCEPTANCE block plus the actual change set,
**not** against an invented plan. ⚠ A retroactive audit cannot change a decision that is already
built — do not read this as a gate that ran in time.

**Right-size: FULL.** It changes a script other scripts import (`sync-agents.ps1`), the door law, and
more than one platform surface.

**Repo pinned from command output:** `Sudo_Hatter_Command` | `chore/SCC-135-update-maps-launcher` |
HEAD `0fef0c8` | `main` `2151568`. `merge-base == main tip`, so the lane is a clean descendant and
needs no absorb.

| Phase | Walked? | One line |
|---|---|---|
| 0 — scope / checkable list | **Skipped** | The decision is built; `/smh-code-review` Step 2 audits the diff against acceptance. Traceability was still checked (see F3). |
| 1 — blast radius | **⭐ Walked** | Re-derived against current `main`; all five doors verified; two sibling lanes read. |
| 2 — over-engineering | **Skipped** | Cutting an abstraction is cheap in a plan, expensive in a diff — that is `/smh-code-review` Step 1's job now. |
| 3 — pre-mortem | **Partly** | Only the external-state rows, per the command's own table. |

### Phase 1 — blast radius (re-derived, not trusted from earlier in the session)

Doors for `smh-update-maps-indexes`, all five present and correctly shaped:
`.claude/skills` 675 · `.agents/skills` 675 · `.agents/workflows` 1,173 (launcher) ·
`.opencode/commands` 40,414 · `.agents/commands` 40,414 (the body). `commands/INDEX.md` describes
behaviour, not doors — unaffected, cleared.

**Sibling lanes read live** (`git worktree list`): `chore/SCC-119-subtask-rule` @ `a2b102a` and
`chore/SCC-124-baseline-trial` @ `aa44d52`. SCC-124 has **zero** overlap. SCC-119 overlaps on two
files, both **committed** on its side — see F2.

### Phase 3 — external-state rows only

| Scenario | Handled? |
|---|---|
| **The other machine** | ✅ The fold added for exactly this: `python3` on the Mac, `python` on a python.org PC, retry the other name on *command not found*. |
| **A fresh clone** | ✅ No new gate ships here; the regenerated workflows are committed, so a clone gets them. |
| **The four platform caches** | ⚠️ Repo-local doors are committed, but the **global** caches this sync wrote (`~/.gemini/antigravity/global_workflows`, `~/.config/opencode/commands`) are machine-local. The PC needs its own `/smh-sync-agents` before the fix is live there. |
| **A sibling lane lands first** | ⚠️ See F2 — this lane should land first. |
| **Rollback** | ✅ Revert the commit and re-run the sync; the launchers are generated, so nothing is hand-authored to restore. Nothing irreversible: no delete, no history rewrite, no force-push. |

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | `_artifacts/_main/INDEX.md` (scc-117 row) | **HIGH** | I wrote `(see branch history)` in the Artifacts column, but the folder actually holds `task.yaml` + `walkthrough.md`. An INDEX row that lies about what is on disk — the same defect class as the truncated run's, committed by the fix for it. | **FIXED in this audit** → `task.yaml + walkthrough` |
| F2 | `.agents/.sync-manifest.json`, `docs/_scc_sops_prds/workflows_testing_SOP.md` | **MED** | Both are `changed in both` against `chore/SCC-119-subtask-rule`, committed on its side. SOP hunks are ~600 lines apart (mine 1706–1790, theirs 1080–1132) so the 3-way merge should resolve; the manifest is **generated** and will conflict textually. | **Land this lane first.** SCC-119 then absorbs `main`. ⛔ Resolve the manifest by **re-running the sync**, never by hand-merging JSON. |
| F3 | `.agents/scripts/check_maps.py` | **MED** | The `test-results` → `SCAN_IGNORES` change is the operator's, carried from the working tree, and traces to **no SCC-135 acceptance item** — textbook scope leakage. No test covers `SCAN_IGNORES` (only a prose mention in `test_sops_prds_folder.py`), so it ships unproven. | **Accept, disclosed.** Carried at the operator's explicit instruction; named here so it is not mistaken for audited work. |
| F4 | `.opencode/commands/smh-update-maps-indexes.md` | **LOW** | opencode now receives a 40,414-char command where it previously received a 4,167-char wrapper. No opencode size cap is known — **unverified assumption**. Strictly less indirection than before either way. | **Accept, flagged.** Re-check if opencode ever renders it truncated. |
| F5 | Antigravity runtime | **INFO** | The fix is proven structurally (launcher generated, nothing over cap) but **not** proven in the IDE — that cannot be verified from here. | Operator reloads Antigravity and re-runs to confirm the door. |

### Four quick gates

- **Verification strategy present?** ✅ Every acceptance item has a command and an expected output;
  all six were run bare, and the SOP gate carries a positive control at exit 1.
- **Anything irreversible?** ✅ No. No delete, no history rewrite, no force-push. The Jira transition
  to *In Progress* is reversible.
- **Any step vague enough that the builder will guess?** ✅ N/A — built.
- **Convention fit?** ✅ Frontmatter matches sibling commands (`description:` only, no `name:`, no
  `platforms:` = all four); artifacts in `_artifacts/_main/<date>_<slug>/`; launcher shape
  byte-consistent with the other twelve.

```
Audit verdict: GO
```

GO with F2 binding: **this lane lands before SCC-119**, and SCC-119 resolves `.sync-manifest.json`
by re-running the sync rather than hand-merging it.

---

## Close-out addendum (2026-08-12) — F6, found by the preflight

**The preflight blocked at exit 2 and it was right to.** `sync: 1 uncommitted change(s)` — the
untracked `_artifacts/_main/2026-08-12_scc-119-subtask-rule/` this walkthrough had already flagged as
a stray. Verified redundant first (SCC-119 has `implementation_plan.md` + `task.yaml` +
`walkthrough.md` all **committed** on its branch, and its copy is newer: 30,191 b vs 29,554 b), then
**parked** to scratch rather than deleted or committed — another lane's work is never swept under
this ticket.

**Parking it turned the gate RED, which is the gate working.** `run_all` went 20/21 with
`test_check_maps.py` failing, because `_artifacts/_main/INDEX.md` still carried a **row** for the
folder that was no longer on disk — `stale row 2026-08-12_scc-119-subtask-rule/ (folder not on disk)`.
That row came from the truncated Antigravity run, which had added an INDEX row for a stray duplicate
of another lane's folder. Removing the row corrects that run's ungated output; it does not touch
SCC-119's own work.

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F6 | `_artifacts/_main/INDEX.md` | **HIGH** | ⛔ **SCC-119 adds NO `_artifacts/_main/INDEX.md` row of its own** — verified, 0 hits in its committed diff vs `main`. It was relying on the row the truncated run happened to leave behind, which this lane has now removed. When SCC-119 lands its three files, `main` will have a session folder with **no INDEX row**, which `check_maps` reports as fatal drift. | **Handoff, binding.** SCC-119 must add its own INDEX row in the same commit as its folder. This lane ships internally consistent — no folder, no row — and cannot fix SCC-119's half without committing another lane's work. |

Gates re-run after the row removal: `check_maps` exit 0, `run_all` **21/21** exit 0.
