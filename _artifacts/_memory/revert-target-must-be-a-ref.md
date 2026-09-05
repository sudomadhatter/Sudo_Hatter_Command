---
name: revert-target-must-be-a-ref
description: "Undoing work in a lane is a READ from a ref. `git checkout origin/main -- <path>` is safe under any later merge; `git checkout <sha> -- <path>` after absorbing main silently deletes whatever landed in between — no conflict, nothing red, and it rides onto main."
metadata:
  probe: "test -e .agents/rules/git-policy.md"
  node_type: memory
  type: feedback
---

**Reverting a file is a read, and which ref you read from decides whether a sibling lane's landed
work survives.** Measured 2026-08-16 (SCC-184) with two synthetic three-way merges — a lane and a
`main` both editing one file:

| Form | Result when the lanes meet |
| --- | --- |
| `git checkout origin/main -- <path>` | **SAFE.** The lane's net diff against the merge-base is empty, so git resolves in the sibling's favour. Their fix survives whichever lane lands first. |
| `git checkout <sha> -- <path>` after absorbing `main` | **DESTROYS the sibling's fix.** Clean merge, no conflict, nothing red — and it lands on `main` inside an otherwise correct lane. |

**Why nothing catches it:** git cannot tell a deliberate revert from a stale read. Both are a legal
write of older content, so there is no conflict to raise and no gate anywhere that looks. Same
disease as [[nothing-guards-the-merge-target]] (wrong destination) and
[[preflight-resolves-repo-from-cwd]] (wrong subject) — an operation acting on the wrong ref and
**reporting success**.

**⭐ The part that generalises past git.** The audit that found this asserted the hazard ran the
*other* way and rated it CRITICAL, driving a conditional GO on a plan. It had been **reasoned about,
not run.** Two scratch repos and four minutes inverted it. A claim about merge semantics is worth
exactly as much as the merge you actually ran — and this applies to audit findings precisely as it
applies to tests ([[prose-pinning-guards-are-vacuous]]: same-context authoring confirms, never
falsifies).

**How to apply:**
- **The only form worth memorising:**
  `git -C "$REPO" fetch origin && git -C "$REPO" checkout origin/main -- <paths>`
- **`main` is not a synonym for `origin/main`.** A local `main` is a cached pointer, stale from the
  moment a sibling pushes — which is exactly when this matters.
- **Re-assert before the close-out, not once at the start.** `main` moves while you build. If a
  revert is meant to be a no-op, prove it still is: `git -C "$REPO" diff origin/main -- <paths>`
  must be empty.
- **This is prose law with nothing checking it**, which is the [[review-findings-are-not-a-work-queue]]
  /SCC-164 thesis applied to itself. A mechanical form exists — before a close-out, assert the lane's
  diff removes no content `origin/main` gained since the merge-base — and is filed on SCC-184 as a
  proposal, unbuilt: it would be a new refusal on a shipping path, so it needs the operator's own
  words ([[blocking-gates-need-a-quoted-ruling]]).

Bound into `.agents/rules/git-policy.md` § Safe-commit mechanics, directly after
*"Pin the merge TARGET"* — they are twins and should be read together.

Related: [[git-branch-model-standard]] · [[commit-and-push-are-one-action]] ·
[[closeout-target-is-a-machine-contract]]
