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
| 9 · G | SCC-175 | **YES — both halves, and one is now a live contradiction** | Step 3 of the door now *requires* `- [x] The merge itself` committed on the branch **before** the PR. But Step 4 still carries the old instruction to tick it *after* the merge ([`smh-close-task-merge-tree.md:493-498`](../../../.agents/commands/smh-close-task-merge-tree.md)). The door contradicts itself today. G-ii (`finish` **computes** the merge row instead of trusting a tick) is still worth building: a `- [x]` can be written without merging, and `finish --apply` is what flips Jira to `Done`. **Three of G's own steps also moved** — see § Part 9 corrections |
| 10 · D | SCC-172 | **YES — unchanged** | Same reason as C. Additionally D3's fail-open is reachable in the lobby: the server ruleset refuses the *push*, but only because a sha with no green check cannot land — the local gate is the layer that says *why*, in the tree, before the network |
| 11 · E+I | SCC-173, SCC-177 | **YES — untouched by SCC-183** | The review surface. No overlap |
| 12 · L | SCC-180 | **YES — banner untouched, but two anchors moved** | [`pre-push-merge-backstop.sh:95`](../../../.agents/scripts/git-hooks/pre-push-merge-backstop.sh) still prints `reset --hard origin/$1` exactly where the plan says — verified. But L's *pass*-fixture and its `git-policy.md` edit both moved under SCC-183. **"No overlap" was wrong** — see § Stale anchors |

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

## ⛔ Stale anchors — three line references in the approved plan now point at the wrong text

Each of these is an address in the 2026-08-15 plan that SCC-183 moved. They are listed because a
builder working from that plan would chase each one and find something *plausible* sitting there.

| Approved plan says | Where it actually is now | Consequence if not corrected |
|---|---|---|
| **L step (1):** `workflows_testing_SOP.md:862` is the prose fixture that must **PASS** the imperative-vs-prose check | SCC-183 added 66 SOP lines; that prose is at **`:934`**. `:862` is now SCC-183's own heading — *"The road to `main` is a pull request, and you merge it"* | The text now at `:862` contains no `reset` at all, so the fixture asserts **nothing** and the comment-literal blindness case is vacuous. Pin by content, not by line |
| **L step (4):** edit `git-policy.md`'s recovery paragraph to name `--keep` / `--soft` | The paragraph survives at **`:324`** but reads *"do not reset and do not force"* and names neither. SCC-183 rewrote 58 lines of this file — its new road-to-main section at `:67-126` | Different sections, so no merge conflict — but the anchor must be found by text, and L does touch a file SCC-183 rewrote |
| **G:** *"Step 4's tick instruction (`smh-close-task-merge-tree.md:434-438`) is deleted"* | That instruction is at **`:493-498`** (the row above). `:434-438` is now partial-landing prose, from the same file's 196-line churn to 597 lines | A builder deletes the wrong block — and the block now at `:434-438` is live law about partial landings |

⭐ **The rule this lane adopts: no step in Parts 8–12 may cite a line number in a file SCC-183
touched.** Cite the text and `grep` for it. Seven files moved under this lane's feet in one landing,
and the lane after this one will move them again.

## ⭐ Part 9 corrections — three of G's steps, beyond the contradiction

The table above records G's *new* defect. These are corrections to G's **existing** steps.

**1. Step (5)'s acceptance is now vacuous.** It reads *"grep the ceremony for any commit after the
push → none."* That is already true: after Step 3 the only `git push` left in the door is the branch
delete at [`:557`](../../../.agents/commands/smh-close-task-merge-tree.md). It passes today, with
nothing built. Replace it with the assertion that actually fails — **Step 3 and Step 4 must not both
demand the tick.**

**2. F27's recogniser premise inverted.** F27 argues the literal `"The merge itself"` is *not* what
the corpus says, and pins SCC-163's `- [ ] **Merge and close out**` as the fixture. SCC-183 now
**mandates** `- [x] The merge itself — lands via this branch's PR` at Step 3. Measured across the 92
walkthroughs in `_artifacts/_main/` on 2026-08-16:

| Era | Row text | Walkthroughs |
|---|---|---|
| mandated forward (SCC-183) | `**The merge itself**` | **7** |
| legacy | `**Merge and close out**` · `**Land it**` · `**Merge sign-off**` · `**Merge**` | **5** |

F27's *design* survives untouched — an open row is the merge row only if it names a merge **door**
or reads merge/land + main/close-out, never by literal match. What changes is the **fixture set**:
pin one row from *each* era plus F27's negative control, or the parser goes green on its tests and
holds a real lane.

**3. Step (6)'s close-out call is a two-invocation ceremony now.** It schedules SCC-163's `finish
--apply` for *"the operator-invoked `/smh-close-task-merge-tree --expect-key SCC-164`, immediately
after the merge lands."* That door now opens a PR and **stops**; the Jira write happens on
re-invocation as **`--after-merge SCC-164`**, after the operator's click. Same ceremony, second call
— and this lane's own close-out is subject to it.

## Stale anchors — the approved plan's line numbers, re-measured 2026-08-16

The plan was written on 2026-08-15. SCC-183 rewrote the door, `git-policy.md` and the SOP the next
day. Every line anchor the remaining parts depend on was re-resolved before building; **three moved,
and one of them silently changes what a part can prove.**

| Plan says | Actually | Consequence |
|---|---|---|
| L's FAIL fixture: `pre-push-merge-backstop.sh:95` prints `reset --hard origin/$1` | **`:95`, verbatim** | none — L builds as written |
| L's PASS fixture: `workflows_testing_SOP.md:862` | **moved to `:934`** — *"why `reset --hard` would be the expensive move"* | the text survived SCC-183's rewrite, so the imperative-vs-prose distinction still has both fixtures. Had it not, L's check could only be proved in the direction that fails |
| L step (4): `git-policy.md`'s recovery paragraph | **`:324`**, and it says *"do not reset and do not force"* — it names **neither `--keep` nor `--soft`** | still to write, as planned |
| G: delete Step 4's tick instruction at `smh-close-task-merge-tree.md:434-438` | **moved to `:493-498`** | the instruction survived SCC-183 and now **contradicts** Step 3, which requires the same tick *before* the PR |
| G's recogniser fixture: SCC-163's row at `walkthrough.md:250` | **`:250`, verbatim** | fixture is good |
| G's fallback shas `eb9030b` (SCC-163) / `31ce965` (SCC-162) | **both still ancestors of `origin/main`** | the Verdict-sha fallback is provable |
| G's `open_actions` at `jira_feed.py:1306-1340`, `cmd_check` at `:1795` | **`:1440` and `:2017`** | code moved, contract unchanged |

⛔ **The first pass of this document called L "no overlap — untouched by SCC-183". That was wrong.**
The *banner* is untouched; both of L's fixtures live in files SCC-183 rewrote. Recorded rather than
corrected silently, because "no overlap" is exactly the claim that stops anyone re-checking.

**Sweep result for L-iii, measured now:** `reset --hard` appears **twice** in the whole toolkit —
the backstop banner (`:95`, the imperative L fixes) and the SOP prose (`:934`, which must keep
passing). L's sweep is therefore a two-fixture check, not a hunt.

## Part 9 corrections — the merge-row recogniser, measured against the live corpus

F27 ruled that a literal `"The merge itself"` match is not enough, because the corpus does not say
that. **Measured across 145 tracked walkthroughs, F27 is confirmed, not inverted:**

| Class | Count | Examples |
|---|---|---|
| Open rows naming a merge **door** | **12** | `**Merge and close out** — /smh-close-task-merge-tree --expect-key SCC-163` · `**Close out and merge**` · `**Merge sign-off** — run /smh-close-task-merge-tree` · `Approve merge and close-out of **SCC-39** via …` |
| Rows carrying the phrase `The merge itself` | **7** | including SCC-183's canonical `- [x] The merge itself — lands via this branch's PR` |
| ⛔ Open rows that say *merge* or *land* and name **no door** | **5** | `**Rule the landing order.**` · `**Decide whether the CONCERNS is worth clearing before the merge.**` · `**Follow-on ticket decision**` — **all real operator decisions the recogniser must never clear** |

⇒ **The recogniser is: an open row is the merge row iff it names `/smh-close-task-merge-tree` or
`/cicd-push-e2e`, OR carries the canonical `The merge itself` phrase.** Satisfied only when that
fires **and** `git merge-base --is-ancestor <lane-tip> origin/main` passes. Every other open row
still holds. The 5 no-door rows are pinned as negative fixtures; SCC-163's `:250` row is the
positive one.

⭐ **And G's door half is now the smaller, sharper half.** SCC-183 already made Step 3 demand the
tick *before* the PR and stopped the ceremony committing after the push — so G's step (5) is
**already satisfied on `main`**, and what remains is deleting the Step 4 instruction that still
tells the agent to do it again afterwards. G-ii keeps its full value: a `- [x]` is a claim, and
`finish --apply` is what writes `Done` to Jira on the strength of it.

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
