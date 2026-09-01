# SCC-184 — A revert reads from a REF, never a sha

**Task:** SCC-184 · **Branch:** `chore/SCC-184-revert-target-is-a-ref` · **Lane:** LOCAL (doc/law only)
**Date:** 2026-08-16 · **Lane style:** lightweight (operator-directed, doc-only — ticket → edit → push)

---

## What this is, in one line

Undoing work in a lane is a **read from a ref**, and which ref you read from silently decides whether
a sibling lane's landed work survives your merge. This lane writes that down as law and as memory.

## Why it exists — the honest origin

This rule is a **correction of my own audit**, not a discovery.

Auditing the SCC-183 plan, I filed a finding (F1) claiming a revert-then-absorb sequence would destroy
a sibling's fix. I rated it **CRITICAL**, and it drove a conditional GO on that plan. Then I actually
ran it. Two scratch repos, two synthetic three-way merges, about four minutes:

| Form | Measured result when the lanes meet |
|---|---|
| `git checkout origin/main -- <path>`, then absorb main | **SAFE.** The lane's net diff against the merge-base is empty, so git resolves in the sibling's favour. `PART-C FIX` survived. |
| Absorb main first, then `git checkout <sha> -- <path>` | **DESTROYS the sibling's fix.** `main` after landing showed only the original two lines. Clean merge, **no conflict**, nothing red. |

The hazard is real. **My finding had it pointing the wrong way.** The claim was reasoned about, not run.

So the deliverable is not "F1 was right" — it is the inverted, measured rule, plus the meta-lesson that
outlived it: *a claim about merge semantics is worth exactly as much as the merge you actually ran.*

## What landed

Three files, **84 insertions, zero deletions**:

| File | What |
|---|---|
| [.agents/rules/git-policy.md](../../../.agents/rules/git-policy.md) | New `###` under § Safe-commit mechanics, placed **directly after** *"Pin the merge TARGET"* — they are twins and read together. The measured two-row table, the safe form, and why nothing catches it. |
| [_artifacts/_memory/revert-target-must-be-a-ref.md](../../_memory/revert-target-must-be-a-ref.md) | New memory, `type: feedback`. Carries the table, the "reasoned about, not run" lesson, and the how-to-apply bullets. |
| [_artifacts/_memory/MEMORY.md](../../_memory/MEMORY.md) | One index line, directly under its twin `nothing-guards-the-merge-target`. |

**The safe form, which is the whole rule:**

```bash
git -C "$REPO" fetch origin
git -C "$REPO" checkout origin/main -- <paths>
```

`main` is **not** a synonym for `origin/main`. A local `main` is a cached pointer, stale from the moment
a sibling pushes — which is exactly the moment this matters.

## The third instance of one disease

| Rule | Wrong thing |
|---|---|
| `preflight-resolves-repo-from-cwd` | wrong **subject** — cleared another lane's branch |
| `nothing-guards-the-merge-target` | wrong **destination** — merged onto a sibling's branch |
| **this one** | wrong **source ref** — read old content over a sibling's fix |

All three are an operation acting on the wrong ref and **reporting success**. Git cannot tell a
deliberate revert from a stale read: both are a legal write of older content, so there is no conflict to
raise and no gate anywhere that looks.

## Evidence

Gates re-run **at the post-absorb tip** (`dcc2b0a`), after `origin/main` `a30c94a` — SCC-164's partial
landing — was merged in. Run bare, never piped (a pipe hides the exit code; zsh has no `PIPESTATUS`):

| Gate | Result |
|---|---|
| `python3 .agents/scripts/tests/run_all.py` | **32/32 files passed, exit 0** |
| `python3 .agents/scripts/workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info — exit 0 |
| `python3 .agents/scripts/check_maps.py --depth3-only --strict` | silent, exit 0 |

The suite grew 29 → 32 when SCC-164 landed; all three of its new files pass against this change.

**This lane's own rule, applied to itself.** The absorb of `origin/main` merged with zero conflicts —
which is precisely the condition under which the hazard is invisible. So it was checked rather than
assumed:

```
$ git diff --numstat origin/main...HEAD
34      0       .agents/rules/git-policy.md
1       0       _artifacts/_memory/MEMORY.md
49      0       _artifacts/_memory/revert-target-must-be-a-ref.md
```

Zero deletions in every row: the lane removes nothing `origin/main` gained. Both anchors also survived
SCC-164 intact — the new `###` still sits between *"Pin the merge TARGET"* (line 250) and `## Sync-first`
(line 316), and the index line still sits under its twin.

## Decisions

- **Prose now, mechanical check as a proposal.** The operator chose this shape explicitly. A pre-close-out
  assertion — *the lane's diff removes no content `origin/main` gained since the merge-base* — would add a
  new refusal to a shipping path. That is new law and needs the operator's own words before it is built
  (`blocking-gates-need-a-quoted-ruling`), so it is recorded on the ticket and deliberately unbuilt.
- **A new SCC key rather than a rider on SCC-183.** Also the operator's call. SCC-183 is parked; this rule
  is independent of it and had no reason to wait.
- **`[sop-ok]` on the rule commit.** `sop_currency` classifies `.agents/rules/**` categorically as "the
  rules commands cite". This adds no command, changes no flow, and alters no usage surface — and staging
  the SOP doc would have raced SCC-164's then-open edit of that same file. The opt-out is logged, which is
  what makes it auditable.
- **Manifest authored at close-out, not at task start.** The lightweight lane skips the plan folder, so
  `task.yaml` did not exist until the ceremony needed it. Recorded as-is rather than backdated; the
  preflight's warning about it is correct.

## Pitfalls — what nearly bit

- **A clean merge is not evidence of a correct one.** This lane absorbed 44 commits of SCC-164 with zero
  conflicts, and that is exactly the state in which a stale-ref revert lands unnoticed. The `--numstat`
  check above exists because "it merged fine" proves nothing about content.
- **The headline finding of my own audit was inverted** — see above. It had already driven a verdict
  before it was measured.
- **A false `MEMORY AUDIT DUE`.** Earlier in this session I reported `MEMORY.md` at 99.4% of budget and
  called an audit mandatory. The cap moved 20 KB → 25 KB on 2026-08-09 and I was quoting the stale figure.
  Real state at landing: **21,319 / 25,600 bytes = 83.3%**, under the 90% trigger. The operator had already
  said yes on that false number and retracted it; no audit was run, correctly.
- **Piping a gate hides its exit code.** `PIPESTATUS` is bash-only and this shell is zsh, so an earlier
  `| tail` returned the exit of `tail`. Every gate above was run bare.
- **A new session folder needs an `INDEX.md` row in the same commit**, or `check_maps` F2 fails on it.

## Your Actions

- [ ] **The merge itself** — signed off by your invocation of `/smh-close-task-merge-tree` this turn.

## Follow-ons

- **The mechanical form of this rule** is recorded on SCC-184 and deliberately unbuilt — it needs your
  words first, because it would add a refusal to a shipping path.
- **SCC-183** stays parked. Its plan's AC-1 already carries the corrected `checkout origin/main --` form,
  so it inherits this rule when it resumes.
