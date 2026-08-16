# Implementation Plan — SCC-183: Prose Fast Lane to `main`

**Revision 2 (2026-08-16) — route (b): a one-commit pull request.**
Revision 1 designed a *direct push* to `main`. It was built, reviewed **FAIL @ `3e4d4f5`**, and is
superseded by this document. R1's plan text and its eleven acceptance items are preserved in git
history at `bd549e6`; the review that killed it is in `walkthrough.md`, which stays as written.

Goal, unchanged: let a change that is **only prose** — docs, resources, artifacts — reach `main`
without the plan → audit → review → close-out ceremony that a code change rightly pays for.

---

## Operator ruling (verbatim)

The lane itself, 2026-08-16:

> "yes delete then you take on this task. I do want it, the little changes to documents and updating
> things that dont touch any code are frustrating."

The safety boundary, chosen from three options the same turn — **"Prose only, law excluded"**:

> `docs/**` · `_my_resources/**` · `_artifacts/**` · `*.md` at repo root — everything else refused,
> with `.agents/**`, `.githooks/**` and `tests/**` named as explicit hard refusals.

The route, after R1 was reviewed FAIL and two routes were put to the operator:

> "b it is then"

Route (b) as it was described to them when they chose it: *"Make the fast lane a one-commit
auto-merged PR. The check already runs on `pull_request`, so nothing server-side changes and most of
the `--direct` token work becomes unnecessary. Least new law — but it stops being a 'direct push.'"*

---

## Why R1 could not work, in one paragraph

`main` carries an **active** ruleset, `main write gate (SCC-118)`, requiring the `main-write-gate`
status check with an **empty bypass list** (0 actors — verified this turn against the live API). That
check is published only by `.github/workflows/main-write-gate.yml`, which triggers on `pull_request`
into `main` or a push to `gate/**`. On the `gate/**` road the check runs `main_write_gate.py --mode
gate`, whose first assertion is `main_write_gate.py:145`:

> `is not a merge commit — it has {len(shas)} parent(s). main advances by exactly one merge commit.`

A single-parent prose commit therefore **can never earn the check that `main` requires**. R1's 103
green tests never saw this because its fixtures build remotes with `git init --bare` — a remote with
no ruleset and no CI. The design was refuted by the server, not by a bug.

---

## What route (b) is

The prose lane stops trying to push to `main`. It pushes an ordinarily-named branch, opens a pull
request, and lets the road that **already exists and is already required** carry it:

```text
chore/<KEY>-<n>-<slug>  ──push──▶  origin
        │
        ├── PR into main  ──▶  main-write-gate runs on `pull_request`:
        │                        · run_all.py (the full enforcement suite)
        │                        · workflow_lint.py --toolkit-only
        │                        · main_write_gate.py --mode pr
        │                            – authorised_branch(): the source branch name must match
        │                              ^(epic|chore)/(SCC)-\d+-.+
        │                            – sop_currency across every landing commit
        │
        └── merge (a merge commit, never squash/rebase) ──▶ main
```

`chore/SCC-183-direct-main-fastlane` — this very branch — already matches that pattern. The route
needs nothing invented.

### Four consequences, stated bluntly

1. **No new *technical* capability is granted — but likelihood is a different axis, and the first
   draft of this line overclaimed** (audit finding F4). Anyone who can push a `chore/*` branch and
   merge a PR can do this today, unchanged: PR #2 (`dabb3c3`, 2026-08-12) is the proof, and it is the
   incident SCC-118 was written about. The local `gh` token carries `repo` + `workflow` already.
   R1 minted a genuinely new privilege — a single-parent push to `main` — and the whole
   fail-closed-allowlist-as-security-boundary argument existed to contain it; route (b) mints none,
   so that threat model evaporates with it. **What (b) does change is normalisation:** a road
   previously travelled by accident becomes documented, tooled and routine, with an entry in the
   menu. The risk argument survives that correction; the sentence "no new capability" does not, and
   this plan will not lean on it.
2. **Zero server-side change.** No ruleset edit, no workflow edit, no `main_write_gate.py` edit. The
   ruleset (verified live) carries `required_status_checks` + `deletion` + `non_fast_forward` and
   **no pull-request rule**, so a PR needs no new permission to exist.
3. **Zero change to the approval token, the minter, or `pre-push-main-approval.sh`.** Those gate
   pushes **to `main`**. This lane never pushes to `main`.
4. **What it does relax, and this is the only new law here:** a local merge through
   `/smh-close-task-merge-tree` requires the operator's **verbatim words** (SCC-37). A merge
   performed on GitHub never touches a machine, so that token is not bypassed — it is *structurally
   absent*, exactly the gap SCC-118 was written about. Route (b) therefore needs a deliberate answer
   to "what replaces the operator's yes," which is the next section.

---

## The decision that matters: who clicks merge

> [!IMPORTANT]
> **(b1) — RECOMMENDED, and what this plan implements. The agent opens the PR and stops. The
> operator merges.**
> This keeps SCC-37's *substance* — one deliberate human act per landing — while deleting the
> ceremony that the operator called frustrating: no plan, no self-audit, no code review, no
> close-out, no token, no verbatim-quote transcription. It is **less** work than today, not more:
> tapping a green PR is cheaper than dictating approval words, and it works from a phone.
>
> **(b2) — the command polls for the green check and merges itself.**
> This removes the operator from prose landings entirely. That is the SCC-71 / SCC-37 failure mode in
> a new coat — an agent landing on `main` on standing context rather than a this-turn yes. It is one
> flag away if the operator rules for it, but this plan will not take it silently.

`allow_auto_merge` is `false` on this repo (verified). Under (b1) that is irrelevant — nothing is
auto-merged — so **no repository setting changes either**.

**Two things about (b1) that must be said out loud (audit finding F5):**

- **It is stronger than SCC-37's token in the way that matters.** SCC-37 exists because an agent
  *claimed* an approval it had not been given — ticket-status permission read as merge permission.
  Under (b1) the operator performs the merge themselves, so there is no claim for an agent to
  fabricate and nothing to falsify. The token converts a silent inference into a visible one; (b1)
  removes the inference.
- **It is a convention, not a gate.** Nothing mechanically stops an agent holding `gh` from merging
  the PR it just opened. AC-7 pins the command's *wiring* — its terminal step hands back — and a
  source-grep assertion is exactly the guard this repo's own memory says is blind to order and
  invertible by a comment. It raises the cost of drift; it does not prevent it. That is the same
  standing every "the agent must stop here" rule in this system has, and it is stated rather than
  dressed up.

---

## What survives from R1's code

### DELETE — revert to the pre-SCC-183 state

| File | What goes |
| --- | --- |
| `.agents/scripts/git-hooks/mint-push-token.sh` | the whole `--direct` / `MODE=direct` mode, its mandatory-`--key` block, its merge-commit refusal, its allowlist sourcing, `mode=` in the token |
| `.agents/scripts/git-hooks/pre-push-main-approval.sh` | the whole direct block and the `mode)` token-parser arm |
| `.agents/scripts/tests/test_main_push_gate.py` | the 21 direct-mode cases, their five helpers, **and the `c.block` wiring** — the whole file reverts |

> ⚠️ **AUDIT FINDING F2 — do not hand-unpick these. Check them out.**
> R1's change was **not** purely additive, contrary to the first draft of this section. Measured:
> it removed **25** pre-existing lines from `pre-push-main-approval.sh` and **5** from
> `mint-push-token.sh` — the merge path's *content* survived byte-identical but its *lines* were
> reindented into an `else` branch, and `CMD=""; BRANCH=""; KEY=""; APPROVAL=""` was rewritten to add
> `MODE=""`. A builder who trusts "additive" will unpick by hand and leave residue.
>
> The revert is therefore a checkout, not an edit, and it is correct by construction:
>
> ```sh
> git checkout main -- .agents/scripts/git-hooks/mint-push-token.sh \
>                      .agents/scripts/git-hooks/pre-push-main-approval.sh \
>                      .agents/scripts/tests/test_main_push_gate.py
> ```
>
> **Run it AFTER absorbing `main`, not before** — see Landing order. If SCC-164's Parts C and D have
> landed by then, `main` is the correct revert target and this picks them up for free; if this runs
> against a stale `main` it silently reverts their fixes too.

### KEEP, RENAMED, AND TIGHTENED

`direct-push-allowlist.sh` → **`.agents/scripts/prose-scope.sh`**, predicate `prose_path_allowed()`.

Two honest changes of character:

- **It is a scope guard, not a security boundary,** and the file will say so in its header. Under (b)
  nothing is protected *by* it — an agent that ignores it and opens an ordinary PR has done nothing it
  could not do before. Its job is "am I in the right lane," which is a correctness question, not a
  containment one. Describing it as security when it is not is precisely what
  `.agents/rules/tests-must-gate-for-real.md` forbids.
- **Tightened to `*.md` only**, per review findings #2 and #13. R1 allowed whole prefixes, and a
  census run this turn finds **147 tracked non-`.md` files** under them — including **3 `.sh`, 4
  `.ps1`, 2 `.py`**, among them `install-git-hooks.sh` (the script that arms every gate in the repo)
  and `restore-env-master.sh` (the secrets kit). None of those is prose. `.md` under the three
  prefixes, and nothing else.

```sh
prose_path_allowed() {
  case "$1" in
    "")                                                    return 1 ;;   # F6 — see below
    AGENTS.md|CLAUDE.md|GEMINI.md)                         return 1 ;;   # law, not prose — see below
    docs/*.md|docs/*/*.md)                                 return 0 ;;
    _my_resources/*.md|_my_resources/*/*.md)               return 0 ;;
    _artifacts/*.md|_artifacts/*/*.md)                     return 0 ;;
    */*)                                                   return 1 ;;
    *.md)                                                  return 0 ;;
    *)                                                     return 1 ;;
  esac
}
```

(The real predicate matches `.md` at any depth; the shape above is illustrative. Depth handling and
the leading-refusal ordering are AC-4's job to pin, since R1 proved ordering is where this class of
predicate fails.)

> ⚠️ **AUDIT FINDING F6 — the empty set must not read as a pass.**
> The predicate is applied per path across a diff, and the caller's verdict is "no offending path was
> found." With an **empty** diff the loop runs zero times, finds nothing, and the command sails on to
> open an empty PR — a check whose missing input reads as a pass, which is Rule 1 of
> `.agents/rules/tests-must-gate-for-real.md` and the tripwire this audit is required to fire on.
> Two arms close it: `""` refuses inside the predicate (above), and the **caller** refuses a zero-path
> diff by name — *"nothing to land"* — rather than treating it as clean. AC-10 pins the caller half;
> the predicate half is one row of AC-4's table.

> [!NOTE]
> **One narrowing of what you approved, flagged rather than smuggled.** You approved root `*.md`,
> which is exactly four files: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `router.md`. The first three are
> the system's brain and its two front doors — law, not prose. R1's review also found that
> `sop_currency.classify()` special-cases **only `AGENTS.md`**, so `CLAUDE.md` and `GEMINI.md` have
> **no backstop at all**, contrary to what I told you when you chose the boundary. This plan excludes
> all three, which leaves `router.md` as the only root file in the lane.
>
> **Second narrowing, same callout (audit finding F10):** you approved whole prefixes — `docs/**`,
> `_my_resources/**`, `_artifacts/**`. This plan allows only `*.md` inside them, which removes 147
> tracked files from the lane, including every `.sh`, `.ps1`, `.py`, `.yaml` and `.json` under those
> roots. `_artifacts/**/task.yaml` is the one you might actually miss.
>
> Narrowing is the safe direction to guess in and both are reversible with one word. Say it and I
> restore either or both.

### CUT — the `c.block` wiring goes back too  *(audit finding F7)*

R1 wrapped the 73 pre-existing checks in `test_main_push_gate.py` under `c.block` guards. It was
introduced to satisfy the ORPHAN rule for the 21 direct cases; those cases are deleted, so the wiring
now traces to **no acceptance item in this plan** — Phase 2 scope creep by its own definition. Worse,
it maximises the conflict surface with **SCC-172**, which is scoped to that exact file and has not
been built yet.

It is a genuine improvement and should not be lost: fold it into SCC-164 Part D, where that file is
already open. Recorded on SCC-172 rather than carried here.

### ADD — the lane itself

| File | What |
| --- | --- |
| `.agents/commands/smh-prose-push.md` | the command body: ticket → branch → commit → push → PR → **stop**, with the scope check as its first step and a hard refusal that names the offending paths |
| **all four platform doors** — `.claude/skills/smh-prose-push/`, `.agents/skills/smh-prose-push/`, `.opencode/commands/smh-prose-push.md`, `.agents/workflows/smh-prose-push.md` | generated launchers, emitted by `sync-agents`, never hand-authored. **F9:** the first draft named two of four. One door per platform per command (SCC-66); three of four is the failure mode that rule exists for |
| `.agents/commands/INDEX.md` · `.agents/.sync-manifest.json` | the command surface's own registries — a new entry that misses these is invisible to the lint |
| `.agents/scripts/prose-scope.sh` | the predicate above, plus a `--check <path>...` CLI so the tests and the command drive **one** definition |
| `.agents/scripts/tests/test_prose_scope.py` | the predicate's table, the empty-input refusal, the refusal wiring, the mutants |

---

## Checkable Acceptance Criteria

| # | Criterion | How it is checked |
| --- | --- | --- |
| AC-1 | `mint-push-token.sh`, `pre-push-main-approval.sh` **and `test_main_push_gate.py`** are byte-identical to the `main` this lane absorbed | `git diff main -- <all three>` is empty — achieved by checkout, not by hand-unpicking (F2) |
| AC-2 | The full enforcement suite is green at the shipping sha, clean tree | `run_all.py` + a `gate_receipt.py` stamp with `dirty_tree=false` |
| AC-3 | `prose_path_allowed` refuses every one of the 147 tracked non-`.md` files under the three prefixes | a test that enumerates them from `git ls-files`, not a hand-written list |
| AC-4 | It refuses `.agents/**`, `.githooks/**`, `tests/**`, root `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`, case variants (`.Agents/x.sh`), `..` segments, paths with spaces, and symlink/gitlink modes | table test, one row per class |
| AC-5 | An **independent** mutation sweep drawn from the shipped predicate — not from the cases — kills every mutant | sweep run by a fresh agent that has not seen the test file (R1's 13/13 was confirmatory; an independent sweep of the same code found **8 survivors**) |
| AC-6 | The command refuses, loudly and by name, when the diff contains a non-prose path | a test that drives the command's check step over a mixed diff |
| AC-7 | The command **stops** at "PR opened" and performs no merge | assertion on the command body: no `gh pr merge`, no `--auto`, no `git push origin main`, and its terminal step hands back. Pins wiring, not prose — and does not pretend to be a gate (F5) |
| AC-8 | The lane's documented route matches the live gate | `main_write_gate.py --mode pr --branch chore/SCC-999-x` exits 0; `--branch claude/foo` exits non-zero |
| AC-9 | `.agents/rules/git-policy.md` and `docs/_scc_sops_prds/workflows_testing_SOP.md` describe **three** roads to main and state plainly that the prose road carries no token | doc diff + the armed `sop_currency` gate |
| AC-10 | An **empty** path set is refused by name, not treated as clean | drive the command's check step over a zero-path diff; it must exit non-zero saying "nothing to land" (F6) |
| AC-11 | The command reaches **all four** platform doors plus `commands/INDEX.md` and `.sync-manifest.json` | `workflow_lint.py --toolkit-only` and the existing `test_command_surfaces.py` (F9) |
| AC-12 | The lane depends on no tool absent from the other machine, or says so | `gh` is required by this command and by nothing else in `.agents/scripts/`; AC-12 is satisfied by the command naming that prerequisite and failing with an install hint, not by assuming it (F9) |

---

## Verification plan

1. **Assert-first.** AC-3 through AC-6 are written RED against the current tree and must fail before
   the predicate exists. R1's two proven exploits (H1 keyless, H3 gate-rewrites-itself) are retired
   with the direct mode they attacked, but their *generalisation* — "a path rule that fails open is
   vacuous in a governance repo" — is what AC-3/AC-4 carry forward.
2. **The mutation sweep is run by a separate agent** that reads only `prose-scope.sh`, never the
   tests. R1's sweep is the cautionary case: 13/13 killed, and an independent pass over the same file
   found 8 survivors, because the mutants were drawn from branches the cases already covered.
3. **The road IS rehearsed end-to-end — the first draft excused a gap that is trivially closable
   (audit finding F8).** It remains true that this lane edits `.agents/**` and `tests/**`, so it is
   not prose and must land the ordinary way through `/smh-close-task-merge-tree`. But that is an
   argument about *this diff*, not about the road. Rehearse the road with a throwaway:

   ```sh
   # a scratch branch whose NAME matches what main_write_gate.py --mode pr requires
   git switch -c chore/SCC-183-prose-rehearsal
   #  ... one added line in a docs/**.md file, committed with an SCC key ...
   git push -u origin chore/SCC-183-prose-rehearsal
   gh pr create --base main --title "SCC-183 rehearsal — DO NOT MERGE" --body "..."
   gh pr checks --watch          # main-write-gate must go GREEN on pull_request
   gh pr close --delete-branch   # closed, never merged; main does not move
   ```

   This proves the claim the whole plan rests on — that a prose PR earns the required check — against
   the **live** ruleset and the **live** workflow, which is precisely the layer R1's 103 green tests
   could not see. It lands nothing. Its output goes in the walkthrough as evidence, with the PR
   number and the check's conclusion.
4. **What still is not covered, stated rather than glossed:** nobody merges a prose PR during this
   lane, so the merge half of the road is exercised for the first time on the next genuine doc-only
   change. The walkthrough says that in those words.

---

## Deliberately NOT in this lane

- **Finding #3 — the merge-arm hole in the local hook. → route it to SCC-172, do not mint a key**
  (audit finding F3). Pre-existing on `main`, and the server gate catches that shape today. The first
  draft said "its own ticket"; **SCC-172** (Part D of SCC-164) already exists, is `To Do`, is scoped
  to `pre-push-main-approval.sh` + `.githooks/pre-push` + `test_main_push_gate.py`, and its D1 is the
  same defect class in the same rung — *"the branch-binding rung fails OPEN when the token's branch
  does not resolve."* The operator has ruled on this pattern in writing: *"we are not developing 3
  tasks for every 1 we try to fix."* Comment it onto SCC-172.
- **Enabling `allow_auto_merge`** on the repository. Not needed under (b1).
- **Route (b2)**, the self-merging variant. Named above; not built.
- **AVCH-63**, the port to `Projects/AGY_AVIATIONCHAT`. Its own ticket, its own repo, after this lands.

---

## Landing order

> ⚠️ **F1 CORRECTED AFTER MEASUREMENT (2026-08-16, post-approval, pre-build).**
> The audit asserted this ordering was *not negotiable*. Two synthetic three-way merges were then run
> to prove it, and they proved the opposite — the hazard is real but runs in the **reverse** direction,
> and the ordering constraint dissolves. Corrected below; the original claim is struck rather than
> quietly edited, because it drove a conditional GO.
>
> **What was measured** (scratch repos, a lane and a `main` both editing one file):
>
> | Order | Result |
> | --- | --- |
> | lane reverts the file to **current `main`'s content**, then absorbs `main` later | **SAFE.** The lane's net diff against the merge-base is empty, so git takes `main`'s side. A sibling's fix lands intact. |
> | lane absorbs `main` **first**, then reverts the file to a **stale sha** | **DESTROYS the fix.** Clean merge, no conflict, nothing red — and it rides onto `main`. |
>
> So the risk is not *"revert before SCC-164 lands"*. It is *"revert to anything other than the ref
> `main` as it stands at the moment of the checkout."* The plan's remedy was already right as written
> — `git checkout main -- …`, the ref, never a sha — but its stated reason was inverted and its
> sequencing requirement was unnecessary.

**Corrected rule: SCC-164 does not have to land first. The revert must target the ref `main`, always.**
Reverting today is safe; SCC-164's Parts C and D will overwrite this lane's (empty) side of those
files when either lane absorbs the other. What follows is the overlap that remains real.

SCC-164 is not a doc lane. It is a live 90-file family lane at `13906ec` with an uncommitted working
tree, and its overlap with this plan is structural on three axes:

| Axis | SCC-164 | This lane |
| --- | --- | --- |
| The two hook scripts | **Part C (SCC-171)** — `--git-common-dir` mis-normalised in `mint-push-token.sh` **and** `pre-push-main-approval.sh`. **Part D (SCC-172)** — three measured fail-opens in `pre-push-main-approval.sh` + `.githooks/pre-push`. **Both still `To Do` — not yet built.** | AC-1 reverts those exact files to `main` |
| The gate's test file | Part D is scoped to `test_main_push_gate.py` | AC-1 reverts that exact file, and F7 hands the `c.block` wiring to Part D |
| The command surface | it is *the command-surface correctness family* — `.sync-manifest.json`, `.opencode/commands/`, `.agents/workflows/`, `commands/INDEX.md`, 17 command bodies | this lane **adds a command**, which writes to every one of those registries |

**The rule that replaces the sequencing requirement — one line, and it is the whole of it:**

> **AC-1's revert targets the ref `main`, never a sha, and never a stale local `main`.**
> `git fetch origin && git checkout origin/main -- <paths>` is the form that cannot be got wrong. A
> revert to *current* `main` is a no-op against the merge-base, so git resolves in the sibling's
> favour whichever lane lands first. A revert to a **sha** — including a `main` from before an absorb
> — silently deletes whatever landed in between, with no conflict and nothing red. That is the same
> shape as the `check_maps` and `preflight` failures in this system's memory: an operation reporting
> success while acting on the wrong tree.

**What genuinely remains, and it is ordinary conflict, not silent loss:** both lanes edit
`docs/_scc_sops_prds/workflows_testing_SOP.md` and `_artifacts/_main/INDEX.md` for real, and both
write to the command-surface registries (`.agents/.sync-manifest.json`, `commands/INDEX.md`). Those
will conflict loudly if they collide, which is the failure mode you want. Whichever lane lands second
re-diffs and resolves.

**Build order for this lane, therefore:** build it all now, revert with `origin/main` as the target,
and re-check `git diff origin/main -- <the three files>` is empty immediately before the close-out —
because `main` may have moved during the build.

---

## Status

**APPROVED — operator replied `approved`, 2026-08-16.** Build proceeding under this revision.
One post-approval correction was made before any code: F1's mechanism was measured and found
inverted, which removed the conditional on the GO. See § Landing order.

---

## Self-Audit (2026-08-16) — Revision 2, PRE-WORK

Repo resolved from command output, not belief:
`Repo: SCC-183-direct-main-fastlane | Branch: chore/SCC-183-direct-main-fastlane`
(worktree `/Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees/SCC-183-direct-main-fastlane`,
repo root `/Users/sudohatter/Sudo_Hatter_Command`). Plan under audit: this file. Ticket: **SCC-183**.

**Right-size: FULL.** It touches a gate/hook pair, a script other scripts source, the door law, four
platform surfaces, and it *deletes* shipped code.

### Phases walked

- **Phase 0 — scope + checkable list.** Change set enumerated: 3 files reverted, 1 renamed and
  tightened, 6 added (command + 4 doors + predicate + test) + 2 registries. Acceptance list rewritten
  from 9 items to **12**; three new items (AC-10/11/12) came from findings, and every plan step now
  traces to one. **Lane check: clear** — no `backend/`, `frontend/`, `firebase/`, `functions/`,
  `mobile/` path; `.github/` is *read* to verify the workflow's triggers and not modified, so this
  stays Task work closing through `/smh-close-task-merge-tree`.
- **Phase 1 — blast radius.** The sibling sweep is where this audit earned its keep: `git worktree
  list` + `git -C … status` + `git -C … diff --name-only main...HEAD` found SCC-164 live at `13906ec`
  with 90 committed files and 11 uncommitted, and `acli jira workitem view SCC-172` showed Parts C
  and D still `To Do` and scoped to the same two hook scripts and the same test file this plan
  reverts. That is **F1**, and it changed the plan's landing-order section from one sentence to a
  sequencing contract. Cleared in one line each: no command *rename* (so no orphaned caches); the
  predicate has exactly two callers today and both are being deleted; no file this plan moves is the
  target of a Markdown link; nothing under `_artifacts/_memory/` is touched.
- **Phase 2 — over-engineering gate.** One tripwire fired: *a plan step tracing to no acceptance
  item*. The `c.block` wiring survived from R1 with no item behind it → **CUT (F7)**, and handed to
  SCC-172 where the file is already open. The *new command* tripwire was considered and cleared: no
  existing command can take this as a flag — `/smh-quick-dev` and `/smh-close-task-merge-tree` are
  the ceremony this lane exists to skip, so bolting a "skip yourself" flag onto them is worse than a
  separate door. A second near-miss: minting a new ticket for finding #3 → **routed to SCC-172 (F3)**
  under the operator's own consolidation ruling.
- **Phase 3 — pre-mortem.** *The other machine:* the lane now depends on `gh`, which nothing else in
  `.agents/scripts/` needs — the only genuinely new portability debt here, pinned as **AC-12 (F9)**.
  *Fresh clone:* nothing ships a gate that is silently off — this lane adds no hook. *Empty input:*
  **fired — F6**, the zero-path diff read as clean. *The four platform caches:* **fired — F9**, two of
  four named. *A sibling lane lands first:* **fired — F1**, and the failure is silent (a revert-to-a-
  stale-main undoes Parts C/D with a clean merge and no red). *Rollback:* a merged prose PR is undone
  by a revert commit through the ordinary door; nothing here is irreversible. *Escape hatch:* the
  ordinary ladder is always available and is stricter, so the prose lane needs no `--force` of its own.
- **Phase 4 — verdict**, below.

### Findings

| # | Where | Severity | Failure scenario | Disposition |
| --- | --- | --- | --- | --- |
| F1 | § Landing order | **HIGH** *(was CRITICAL)* | A revert that targets a **sha** rather than the ref `main` silently deletes whatever a sibling landed in between — clean merge, no red, nobody notices | **FIXED IN PLAN, then CORRECTED** — measured post-approval: the hazard runs the opposite way from the audit's claim, and the sequencing requirement was unnecessary. Remedy is now one rule (revert to `origin/main`, never a sha), not a 4-step contract |
| F2 | § DELETE (AC-1) | HIGH | "Purely additive" is false — R1 removed 25 pre-existing lines from `pre-push-main-approval.sh` and 5 from `mint-push-token.sh`; a builder trusting it hand-unpicks and leaves residue | **FIXED IN PLAN** — revert is now a `git checkout main -- …`, correct by construction; measured numbers recorded |
| F3 | § Deliberately NOT | HIGH | Minting a new key for finding #3 duplicates SCC-172 (`To Do`, same files, same defect class) against a standing operator ruling | **FIXED IN PLAN** — routed to SCC-172 |
| F4 | § Four consequences | MEDIUM | "No new capability" is true technically and false in effect; the whole risk argument leans on a sentence that cannot carry it | **FIXED IN PLAN** — restated as capability-unchanged / normalisation-changed, with PR #2 as the evidence |
| F5 | § who clicks merge | MEDIUM | (b1) presented as if it were a gate; AC-7 is a source-grep guard, which this repo's memory says is invertible by a comment | **FIXED IN PLAN** — both halves stated: stronger than the token in substance, a convention in enforcement |
| F6 | § predicate | MEDIUM | An empty diff yields zero iterations → no offending path → **pass**, and the command opens an empty PR. `tests-must-gate-for-real` Rule 1 | **FIXED IN PLAN** — `""` arm in the predicate + AC-10 on the caller |
| F7 | § `c.block` wiring | MEDIUM | Kept with no acceptance item behind it, on the one file SCC-172 is scoped to — pure conflict surface | **CUT** — reverts with the rest; folded into SCC-164 Part D |
| F8 | § Verification plan | LOW | A closable coverage gap was being excused; the live ruleset + live workflow are exactly the layer R1's tests could not see | **FIXED IN PLAN** — throwaway rehearsal PR added, opened and closed without merging |
| F9 | § ADD, § Phase 3 | LOW | Two of four platform doors named; `gh` dependency unstated on a two-machine system | **FIXED IN PLAN** — all four doors + both registries listed; AC-11 and AC-12 added |
| F10 | § narrowing callout | LOW | The prefix→`*.md` narrowing sat in a bullet while the root-law narrowing got a callout; both narrow what the operator approved | **FIXED IN PLAN** — both in one callout, both reversible with one word |

Ten findings, ten dispositions, none deferred. F1 is the one that would have cost real work.

### Landing-order dependency

**SCC-164 must land before this lane's AC-1 revert runs.** Stated in full in § Landing order, with a
split-build fallback if SCC-164 sits. Naming it here too because a landing-order dependency that
lives only in a prose section is one nobody re-reads at close-out time.

### Four gates

- **Verification strategy present?** ✅ Each of AC-1…AC-12 names the command that proves it. AC-5 is
  the one that needs a *person* to enforce: the sweep must be run by an agent that has not read the
  test file, because R1's confirmatory 13/13 is the cautionary case.
- **Anything irreversible?** ⚠️ One deletion — R1's direct-mode code and its 21 tests. It is
  recoverable from git (`3499861`, `2219968`, `e6e6290`) and the plan says so. The rehearsal PR is
  opened and closed, never merged. Nothing else.
- **Any step vague enough to be guessed?** One was: *"the real predicate matches `.md` at any
  depth"* left depth handling to the builder. AC-4's table now owns it, and R1 proved this is exactly
  where the class fails.
- **Convention fit?** ✅ One door per platform per command; artifacts in
  `_artifacts/_main/<date>_<slug>/`; POSIX `sh` for the predicate, matching every other hook-adjacent
  script; the audit appended into the plan rather than a standalone file.

```text
Audit verdict: GO
```

**GO — unconditional as of the F1 correction.** The ten findings were baked into the plan before this
verdict was written, and Phases 0–3 were re-walked against the amended text. The verdict originally
read *"GO, conditional on the sequencing in § Landing order"*; that condition was retired when F1 was
measured and its mechanism found inverted. The remaining obligation is a one-line rule, not a
sequencing contract: **revert to the ref `origin/main`, never to a sha.**

A note worth keeping for the next audit: **F1 was the finding this audit was proudest of, and it was
half wrong.** It was written from reasoning about three-way merges rather than from running one. The
severity survived; the mechanism and the remedy did not. The lesson is the one already in this
system's memory under a different name — *same-context authoring confirms, never falsifies* — and it
applies to audit findings exactly as it applies to tests.
