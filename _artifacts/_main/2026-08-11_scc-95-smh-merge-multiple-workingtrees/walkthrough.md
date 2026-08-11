---
IsArtifact: true
ArtifactMetadata:
  title: SCC-95 — build /smh-merge-multiple-workingtrees
  type: walkthrough
  date: 2026-08-11
---

# Walkthrough — SCC-95

**Branch:** `chore/SCC-95-smh-merge-multi-lanes` · **Lane:** LOCAL
**Plan + pre-work self-audit:** `implementation_plan.md` in this folder (`Audit verdict: GO`, F1–F3).

## ⭐ This command was written while running it by hand, and that changed it

The plan was authored before the landing. The command was written **during** a live six-lane
landing (SCC-90 → SCC-89 → SCC-94 → AVCH-53 → SCC-88 → SCC-83, then SCC-96), and every worked
example in its body is **measured from that run**. What follows is the delta between what the plan
imagined and what actually happened — which is the part worth reading.

### ⛔ The finding that reshaped the command: the merge landed on the wrong branch

The procedure ran `cd <worktree> && git checkout main`, and then — in a **separate tool call** — a
bare `git merge <lane>`. The working directory had reset between them to the shared checkout, which
was sitting on **a sibling lane's branch**. The merge succeeded and put a production merge commit
onto `chore/SCC-89-migrations-to-docs` instead of `main`.

**Nothing caught it.** The merge output is identical, the file list is right, and the commit message
says `-> main` because that is what you typed. It was found only by running `git rev-parse
--abbrev-ref HEAD` afterwards and not recognising the answer.

This is `worktree-per-story`'s *"cwd is not intent"* — but aimed at the **merge step itself**, not
at which tree you review in. The rule as written protects the diff; nothing protected the target.

**Baked in:** every git call in the command now carries `-C "$REPO"`, Step 0 carries a ⛔ block
explaining why with this incident, and Step 4d **asserts** `rev-parse --abbrev-ref HEAD` equals
`main` and aborts otherwise. The recovery is documented too: the merge commit was correct in every
way except which pointer moved, so `git merge --ff-only <sha>` from the tree holding `main` put it
where it belonged — after verifying its tree carried nothing from the wrong branch.

### The other seven deltas, all from the live run

| # | What the plan assumed | What happened | Where it landed in the command |
|---|---|---|---|
| 1 | lanes reported "ready" are committed | one lane had **0 commits** — its work sat uncommitted in the shared checkout | Step 1 now measures `rev-list --count main..<branch>` and calls 0-commits-plus-dirty *not built yet* |
| 2 | the overlap map is built from `git diff` | **`git diff` cannot see untracked files.** One lane was absent from the ledger-collision list until it committed an untracked artifact folder — becoming the **5th** lane on a file four were already fighting over | Step 3 folds `status --porcelain` untracked entries in *as if committed* |
| 3 | ledger conflicts are "keep both rows" | true, but **same-day rows do not order themselves** — needed 4 times | Step 3 states the tie-break: later-landing goes on top, re-derivable from `git log` |
| 4 | conflicts are ledger / gate / command-or-rule | two classes were missing and neither is mechanical: **rewrite-vs-edit** (SCC-94's paragraph no longer existed in SCC-90's rewritten file) and **modify/delete** (SCC-88 deleted a file SCC-89 had just fixed) | Step 3's table now has four classes, each with its own law |
| 5 | a modify/delete is resolved by ordering | **false, and it was checked** — both orders end with the file deleted. It is a *decision* | Step 3: rule it, and **prove the survivor exists at its destination BEFORE accepting the deletion** |
| 6 | a verdict at the tip is valid | three lanes' verdicts described a `main` that no longer existed. One went **FAIL** on re-review | Step 1 + 4b: re-measure after absorb; **record the old verdict, never overwrite it**; a mid-set FAIL is fixed in place, not dropped |
| 7 | the combined gate is a formality | it caught **SCC-96**, a real gate defect no lane could have found — the offending ledger row and the misreading checker lived in *different lanes* | Step 5 is now marked *do not skip*, with that incident as its ⓘ |

Also folded in: the **permission layer** refused `git merge` into `main` in auto mode. That is
SCC-71 enforced by something that cannot be talked out of it, so Step 4c names the refusal as the
contract working rather than a malfunction, and says to hand the rule over rather than route around
it. And the `LANE: HANDOFF` rule proved its worth on a **comment** — fixing one stale path in
`backend/requirements.txt` would have sent 33 memory files through the full E2E suite, so it was
left and written down.

## The plan's own audit findings — all three landed

| # | From the pre-work audit | Where it is |
|---|---|---|
| F1 | an empty eligible set must be a **STOP with a named reason**, never a pass | Step 1, ⛔ block |
| F2 | `commands/INDEX.md` is grouped **by lane**, not one row per command — extend the *Task close-out* group, do not mint a new one | done: the group row now names both commands and opens with **which one to use** |
| F3 | a lane that changes push machinery breaks later merges — treat a token prompt as expected | Step 4d, and the "gate-changing lanes land LAST" rule in Step 3 |

## Evidence

| Acceptance (SCC-95) | Evidence |
|---|---|
| A1 command master exists, `/`-refs resolve | `.agents/commands/smh-merge-multiple-workingtrees.md`; `test_sops_prds_folder.py` exit 0 |
| A2 `workflow_lint --toolkit-only` clean | **exit 0, 0 errors 0 warnings** — the pre-fix RED was `[WARN] not mentioned in commands/INDEX.md` |
| A3 stops before EVERY merge, and says why | Step 4c + the header's SCC-71 paragraph |
| A4 refuses a deployable diff, names `/cicd-push-e2e`, no override | Step 2, with the `backend/requirements.txt` worked example |
| A5 `--expect-key` per lane | Step 2 |
| A6 overlap map with classes; gate-changers LAST | Step 3 (four classes + the cross-repo rule) |
| A7 stale-lane detection | Step 2.5, with the 31-commits-behind example |
| A8 prunes only `chore/*` it landed; unlink first; never `claude/*` | Step 4f |
| A9 one Dev Record **per ticket**, at its own merge | Step 4e |
| A10 SOP moves in the same commit; four doors exist | SOP §7 altitude table + §17 reference row, same commit; doors verified below |

### Gates (bare — a piped gate returns the pipe's exit code)

```
python3 .agents/scripts/workflow_lint.py --toolkit-only   -> exit 0   0 errors, 0 warnings, 8 info
python3 .agents/scripts/tests/run_all.py                  -> exit 0   13/13 files passed
python3 .agents/scripts/tests/test_sops_prds_folder.py    -> exit 0
python3 .agents/scripts/tests/test_command_surfaces.py    -> exit 0

four doors, verified by existence not assumption (pwsh sync-agents.ps1):
  .claude/skills/smh-merge-multiple-workingtrees/SKILL.md      ✓
  .agents/skills/smh-merge-multiple-workingtrees/SKILL.md      ✓
  .opencode/commands/smh-merge-multiple-workingtrees.md        ✓
  .agents/workflows/smh-merge-multiple-workingtrees.md         ✓
```

Frontmatter carries a real `description:` and **no `platforms:` key** — omitting it publishes to all
four, whereas `platforms: []` syncs to NOWHERE while looking installed.

## Your Actions

- **Restart opencode / start a fresh Codex chat** to pick up the new door (the global caches were
  written by `sync-agents`, but a running client holds the old menu).

Verdict: PASS @ (this commit)
