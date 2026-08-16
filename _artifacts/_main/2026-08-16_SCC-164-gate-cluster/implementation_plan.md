# SCC-164, second half — the gate cluster (Parts 8–12)

**This is not a new plan.** The plan is
[`2026-08-15_SCC-164-command-surface-family/implementation_plan.md`](../2026-08-15_SCC-164-command-surface-family/implementation_plan.md),
approved by the operator on 2026-08-15, with its § ARMING ruling quoted verbatim. Parts 1–7 landed;
that lane's `task.yaml` declared `landing_mode: partial` and named the remainder — **C, G, D, E, I, L
— as the next lane**. This document is the **delta only**: what SCC-183 changed underneath the
remaining parts, and the build order that follows from it. Everything not restated here is unchanged
and still binding, including the § ARMING ruling, the eight Rules of the lane, and each part's
declared mutants.

**Operator's word opening this lane (2026-08-16):** *"ok lets finish those then i want this done"* —
the parent closes at this lane's ceremony.

---

## What SCC-183 changed, part by part

SCC-183 landed between the two halves (PR #11 `819f981`, PR #12 `bc3a851`). It deleted the local
merge-to-main road in the lobby and replaced it with a pull request the operator clicks. Every
remaining part touches that surface, so each one is re-derived against it before it is built.

| Part | Key | Still real? | What changed |
|---|---|---|---|
| 8 · C | SCC-171 | **YES — unchanged** | The token path is spent by `/cicd-push-e2e`, which SCC-183 deliberately left alone: it ships **project** epics, and project repos have no `main-write-gate` check to gate a PR ([`test_door_preflight_order.py:284-290`](../../../.agents/scripts/tests/test_door_preflight_order.py) pins that carve-out). The PC path bug is live in every project worktree |
| 9 · G | SCC-175 | **YES — both halves, and one is now a live contradiction** | Step 3 of the door now *requires* `- [x] The merge itself` committed on the branch **before** the PR. But Step 4 still carries the old instruction to tick it *after* the merge ([`smh-close-task-merge-tree.md:493-498`](../../../.agents/commands/smh-close-task-merge-tree.md)). The door contradicts itself today. G-ii (`finish` **computes** the merge row instead of trusting a tick) is still worth building: a `- [x]` can be written without merging, and `finish --apply` is what flips Jira to `Done` |
| 10 · D | SCC-172 | **YES — unchanged** | Same reason as C. Additionally D3's fail-open is reachable in the lobby: the server ruleset refuses the *push*, but only because a sha with no green check cannot land — the local gate is the layer that says *why*, in the tree, before the network |
| 11 · E+I | SCC-173, SCC-177 | **YES — untouched by SCC-183** | The review surface. No overlap |
| 12 · L | SCC-180 | **YES — untouched by SCC-183** | The backstop banner. No overlap |

**Nothing dissolved.** The one thing that did change is the *stakes* on C and D: in the lobby they
now guard a road no lobby command takes, and their live blast radius is the project repos and the PC.
They are back-ports, not inventions — see below.

## C and D are a BACK-PORT, and the source is measured

`Projects/AGY_AVIATIONCHAT` already carries all five fixes (AVCH-59), each with its reproduction
recorded in the file. The plan said so ("AGY is AHEAD on C/D and stays so"); this lane closes the
divergence in the direction the plan set. Diffed 2026-08-16, lobby vs AGY:

| Fix | Where | AGY's measured reproduction |
|---|---|---|
| **C1** delete the `case "$GIT_COMMON" in /*)` normalisation | `mint-push-token.sh`, `pre-push-main-approval.sh` | `C:/…/modules/…` does not match `/*` → repo root prepended to an already-absolute path → token written nowhere, **every push to main refused** |
| **C3** verify the token WROTE | `mint-push-token.sh` | ⭐ AGY's first cut used `if ! { … } > "$TOKEN"` — **fires on dash, does nothing on bash or macOS `/bin/sh`**. The remedy contained the defect. `[ -s "$TOKEN" ]` asks the filesystem instead |
| **D1** unresolvable branch = REFUSAL; `^2` unconditional | `pre-push-main-approval.sh` | plain non-merge commit + token naming a never-existed branch → ✅ APPROVED |
| **D2** zero remote sha = REFUSAL | `pre-push-main-approval.sh` | bare remote, 3 stacked merges, 1 token → ✅ APPROVED, remote `rev-list --count --merges` = 3 |
| **D3** narrow the allow-on-missing to non-`main` refs | `.githooks/pre-push` | main checkout: REFUSED · stale worktree: `main -> main` **LANDED**. Same repo, same refs, same missing token |

Ported with the lobby's own referents (the lobby *does* have `.agents/rules/git-policy.md`; AGY's copy
rewrites that path because it is a thin project). AGY also carries an `echo` → `printf` fix on the
approval line — arbitrary operator prose through `echo` re-expands backslashes on dash/ash/BusyBox
(`echo-truncates-at-backslash-c`). It rides along; it is the same claim-verbatim-words mechanism.

## ⛔ The lobby's own fixtures sit INSIDE fail-open D2

`test_main_push_gate.py`'s `gate()` helper defaults `remote_sha=ZERO`
([`:79-82`](../../../.agents/scripts/tests/test_main_push_gate.py)). Every behaviour case in the file
is therefore driven through the `remote_sha != ZERO` arm's **else** — the arm D2 says falls straight
through to approved. The suite's happy path ("main WITH a valid token is allowed") is green *because
of* the hole. Closing D2 turns those cases red, and that is the correct signal: the fixtures must be
rebuilt on a real remote tip and a real merge commit, as AGY's `stage_one_merge` already does.

This is recorded here rather than discovered mid-build because it changes the shape of Part 10: it is
not "add three cases", it is "rebuild the fixture, then add three cases and their controls".

## Build order

Unchanged from the approved plan's rows 8–11, with F22's ordering constraint intact.

| # | Part | Key | Note |
|---|---|---|---|
| 1 | **C** | SCC-171 | the token path, both scripts |
| 2 | **G + L** | SCC-175 + SCC-180 | two halves of one incident: G removes the reason the banner gets read, L makes the banner safe |
| 3 | **D1 + D2** | SCC-172 | the gate script; fixture rebuild lands here |
| 4 | **E + I** | SCC-173 + SCC-177 | the review surface — the largest part |
| 5 | **D3** | SCC-172 | ⛔ **LAST edit of the lane (F22).** `core.hooksPath=.githooks` is RELATIVE, so this worktree's own `.githooks/pre-push` goes LIVE for this lane's pushes the moment it is saved. Prove it in a scratch repo, then commit and push once |

⭐ **F22 is materially safer than when it was written.** This lane never pushes `main` — it pushes
`chore/SCC-164-gate-cluster` and opens a PR. D3 narrows the fail-open to `main` refs *only*, so it
cannot touch this lane's own pushes even while live. The order is kept anyway; the reasoning is
recorded so the next lane knows which part of the constraint was load-bearing.

## Review runtime — probed at Step 0, per Rule 3

**`review-runtime: inline`.** Probed, not assumed: this session carries a standing directive that the
subagent tool is not to be used, so fan-out is unavailable. Under Part I's own contract that makes
`recovered-inline` the only legal per-lens state for this lane, and the roster this lane writes is the
first one the parser it builds will read. The lane is the parser's first live fixture.

## What this lane does NOT do

- **No AGY/AVCH file is touched.** Hooks are repo-local (`repo-local-enforcement-never-centralizes`).
- **The local token gate is not retired.** SCC-183 recorded that as a follow-on; it stays a follow-on.
  Retiring it would strand `/cicd-push-e2e`, which is the *only* road for project epics until AVCH-63
  ports the PR door there. Fixing it and retiring it are not in tension — a gate that is wrong on one
  of two machines gets fixed before anyone argues about whether to keep it.
- **`/cicd-push-e2e` is not converted to a PR door.** That is AVCH-63, and it is per-project work.
