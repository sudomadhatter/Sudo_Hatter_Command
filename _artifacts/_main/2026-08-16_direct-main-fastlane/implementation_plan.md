# Implementation Plan — SCC-183 · Revision 3: the PR door

**R3 (2026-08-16), second cut — rewritten against a NO-GO audit.** Supersedes R1 (a `--direct` token
push straight to `main` — built, reviewed **FAIL** @ `3e4d4f5`) and R2 (a prose-only PR lane plus a
second command — approved, then **PARKED**). R1's plan text survives at `bd549e6`, R2's at `96be628`.
The ticket description is the canonical statement of R3; this file is its build sheet.

**The first cut of this plan was audited `NO-GO` with 15 findings.** The audit is appended below in
full, unedited. Two of its findings changed the *design*, not the wording, and they are called out at
the top of the parts they hit. Nothing is quietly amended.

---

## The one-line thesis

**The gates are not what blocks us. The landing ceremony is.** Every gate passed on SCC-184 and it
still could not reach `main` from an agent session for an entire day.

## What was measured, not reasoned

| Evidence | Result |
| --- | --- |
| Controlled pair, same op, same target | `git merge X --no-ff` **allowed** · `git -C <path> merge X --no-ff` **denied** |
| Who mandates `-C` | `.agents/rules/nothing-guards-the-merge-target.md` — **every** git call |
| Who wrote the allow-list | bare `Bash(git merge *)`, no `-C` form |
| The shared checkout during SCC-184's landing | held dirty by another session; the stash was denied too |
| The documented workaround (a landing worktree at `origin/main`) | refused by our own minter: `HEAD is 'HEAD', not 'main'` |
| `gh pr merge` this session | **denied by the risk classifier**, not the allow-list |
| PR #5 (SCC-153) · PR #6 (SCC-184) · PR #8 (SCC-186) | all **merged**, `main-write-gate` green in ~45 s, zero denials |

So: **obeying the safety law guarantees the permission miss**, and the road that works already exists
and has now carried work three times. R3 invents no privilege — it builds a door onto that road.

## Operator rulings this lane runs under (verbatim)

> "we need to make sure the agent gives me the link like this everytime. if its this straight forward
> I am ok with it."
>
> "I dont want another ticket at all, this is never ending." → the standing key **SCC-186**.

And the split, chosen from three options presented this turn:

> **Doc / index / memory / maps lanes → the agent merges.** Code lanes → the agent stops at the PR
> and the operator clicks.

---

## Build state on this branch

| Commit | Part | What |
| --- | --- | --- |
| `e923302` | — | absorb `origin/main` `fdd6d75`; one conflict (`_artifacts/_main/INDEX.md`, both sides added rows) resolved keeping all three |
| `7858710` | **E** (code) | R1's three files reverted via `git checkout origin/main --`; `direct-push-allowlist.sh` removed. Suite **32/32** after |
| `a280117` | **E** (docs) | **audit F2** — the first pass missed `git-policy.md` (+27) and `workflows_testing_SOP.md` (+41), which still described the `--direct` lane and named the deleted allowlist. Reverted the same way |

`git diff origin/main` over all five R1 files is now **0 lines**. Part E is complete.

> **Flagged rather than smuggled:** Part E ran before this plan was approved. It is a *revert to
> `origin/main`* — it removes this lane's own prior work and adds nothing — and it had to precede the
> plan, which is written against a tree with R1 gone. Trivially reversible (`git revert`).
> **Everything in Parts A–D waits for `approved`.**

---

## Part A — `land_pr.py`, the one command

`.agents/scripts/land_pr.py`, stdlib Python (both machines; `.sh` needs a POSIX shell the PC lacks
outside Git Bash).

> ### ⛔ Audit F5 changed this part's stated mechanism. Read this before the design.
>
> The first cut sold the script as *"every `-C` git call lives inside the script where the permission
> layer never sees it."* **That claim is withdrawn and the plan does not rest on it.** It was
> unverified, it contradicted Part C item 2 in the same document, and — the deciding reason — *designing
> around the agent's own permission layer is not a thing this lane will do.* That layer is the
> operator's control over the agent, not an obstacle to route around.
>
> **What the script is actually worth, and it is enough:**
> 1. **One stable command string**, so *one* allow-list entry covers every landing instead of a dozen
>    improvised ones that each get judged separately. That is the real fix for the denial storm.
> 2. **The landing becomes testable code** instead of prose each agent re-improvises differently.
> 3. **It never touches the shared checkout** — the SCC-184 blocker — because it only ever pushes a
>    branch and talks to GitHub.
>
> Part C item 2 is therefore a **hard prerequisite**, not a convenience, and the plan says so once,
> consistently.

```text
python3 .agents/scripts/land_pr.py [--repo PATH] [--merge] [--dry-run]
```

*(`--json` is **CUT** — audit F15: no acceptance item required it.)*

### The ordered checks — order is load-bearing (audit F6)

| # | Check | Note |
| --- | --- | --- |
| R1 | not a git repo / cannot resolve | never act on belief; `git rev-parse` is the only source |
| R2 | branch is not `(epic\|chore)/<KEY>-<digits>-<slug>` | the **real** `main_write_gate.py` pattern, corrected per audit F13 — it is not chore-only |
| R3 | `<KEY>` not in this repo's `jira.conf` `JIRA_KEYS` | a wrong-project key is a failure this system already rules on |
| R4 | working tree dirty | a PR must describe committed work; a dirty tree is the SCC-184 failure condition itself |
| **P** | **PR-exists probe — runs BEFORE R5** | **audit F6**: after a merge, commits-ahead is 0, so an empty-diff refusal placed first would report failure on every re-run and on `--after-merge`. If a PR exists → print its URL (and its state) and **exit 0**. Idempotent |
| R5 | zero commits vs `origin/main` **and no PR** → *"nothing to land"* | ⛔ an empty input must never read as a pass (`tests-must-gate-for-real` rule 1) |
| R6 | local branch **diverged** from its remote | force-push is banned. **Audit F6b**: after `--delete-branch` there is no upstream — that is *absence*, not divergence, and is handled as its own arm |
| R7 | `gh` absent or unauthenticated | name the prerequisite with an install/login hint, never assume |
| R8 | **`--merge` eligibility** — see the box below | the split, made mechanical |

### ⛔ Audit F1 (CRITICAL) — `lane_qualify` alone is the WRONG predicate for `--merge`

Measured: `lane_qualify.classify()` rates **`.claude/hooks/require-push-approval.py`** — the agent's
own PreToolUse push gate — and `.claude/settings.json` as **LIGHT**, along with ~1,100 other
`.claude/**` files, 69 `.opencode/**` files, `docs/migrations/scripts/*.sh`, `opencode.json` and
`requirements.txt`. `TOOLKIT_PREFIXES` covers only `.agents/ .githooks/ .github/ _bmad*`.

**Failure scenario:** a lane edits the agent's own permission hook, R8 passes, `--merge` lands it on
`main` with no click, no token, no review. That is R1's own killed CRITICAL ("`docs/**` is not a prose
tree") reproduced through a different predicate.

**The cut that caused it, named:** the first cut dropped R2's `prose_scope` predicate arguing
*"`lane_qualify` already answers this."* It does not. `lane_qualify` answers **"which dev lane does
this work belong in"**; `--merge` asks **"may this land with no human looking at it"**. Different
questions, and the measurement settles it. R2's instinct was right; only its *packaging* (a separate
script plus a whole new command and four platform doors) was over-built.

**Resolution — both, fail-closed, and inside `land_pr.py`:**

```python
def merge_eligible(repo, paths):     # BOTH must hold; ANY failure => operator clicks
    verdict, why = lane_qualify.classify(repo, paths, no_file_changes=False)
    if verdict != "LIGHT":            # LIGHT-VCS is unreachable from a real PR (audit: verified)
        return False, why
    bad = [p for p in paths if not _is_prose(p)]
    return (not bad), (f"not prose: {', '.join(bad[:3])}" if bad else "prose only")
```

`_is_prose(p)` is an **allowlist**, never a denylist — the generalisation R1 died on is *"a denylist
authored against a product repo's layout is vacuous in a governance repo"*:

- `*.md` under `docs/`, `_artifacts/`, `_my_resources/` (any depth), and `router.md` at the root;
- the three tracked generator outputs by exact path: `docs/repo-map.md`, `docs/.maps-state.json`,
  and any `_artifacts/**/INDEX.md`;
- `_artifacts/_memory/**.md`;
- ⛔ **refused explicitly** even though they are `.md`: root `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
  (the system's brain and its front doors — law, not prose), and anything under `.claude/`,
  `.opencode/`, `.agents/`, `.githooks/`, `.github/`, `tests/`, `docs/migrations/scripts/`;
- ⛔ empty path set → **refused by name**, never a pass;
- ⛔ any path with a `..` segment, an absolute prefix, or a non-file mode (symlink / gitlink) →
  refused.

### Then

Push the branch if merely ahead → `gh pr create --base main`, body assembled from the walkthrough's
`Verdict:` line, the `gates/*.json` receipts and the change summary → **print the URL last**.

**With `--merge` (eligible lanes only):**

1. poll `main-write-gate` on the PR head until completed;
2. ⛔ **audit F9 — re-check freshness before merging.** Measured on the live ruleset:
   `strict_required_status_checks_policy` is **false**, so the check certifies the PR head *only*,
   and a sibling landing in between is not re-gated. Auto-merge removes the human latency that used
   to catch that. So: refuse unless `git merge-base --is-ancestor origin/main <pr head>` — if `main`
   moved, absorb and re-gate rather than merge stale;
3. `gh pr merge --merge --delete-branch`. ⛔ **Never `--squash`, never `--rebase`** — either puts a
   single-parent commit on `main` and breaks the one-merge-per-landing shape every gate here assumes;
4. report `landed: PR #N · merge commit <sha>` — **audit F8**: this, not a URL, is the last line on
   the merge path, because that is what the operator's own ruling asks for. AC-6 is corrected to
   *"the actionable identifier is the last line"*, which is the URL on the hand-back path and the
   landed-line on the merge path.

**Testability (audit F7).** `--dry-run` is redefined honestly: it performs **network READS**
(`gh pr list`, `gh pr view`, `gh api …/check-runs`) and performs **no writes** — no push, no
`pr create`, no `pr merge` — printing the exact argv it would have run. The `gh` layer is one
injectable seam (`run_gh=subprocess...`) so tests substitute a recorder and **no test calls GitHub**.

## Part B — the close-out becomes two halves around the merge

`/smh-close-task-merge-tree`:

- **Steps 0 – 2.5 unchanged** — preflight `--expect-key`, the lane's gate, the flight event.
- **The merge box is ticked on the LAST COMMIT ON THE BRANCH.** ⛔ **Audit F10**: it cannot say
  *"lands via PR #N"* — `N` is assigned by `gh pr create`, which runs *after* that commit is pushed.
  It ticks as **`- [x] The merge itself — lands via this branch's PR`**, and the PR number and merge
  sha go into the **Dev Record** at `--after-merge`, where both are known. **This still closes
  SCC-175** — the defect is that a *post-merge commit on `main`* is refused by the gate; ticking on
  the branch removes the commit, which is the whole fix.
  Live evidence it is real, measured an hour ago: `jira_feed.py finish` **held SCC-184 at
  `Review Required`** over an unticked box in a walkthrough whose merge had already happened.
- **New Step 3** — invoke Part A. Eligible lane: it merges and reports. Otherwise: it prints the
  link and the command **STOPS**.
- **New Step 3b — `--after-merge <KEY>`, a separate invocation** — verify merged
  (`gh pr view --json mergedAt,mergeCommit`), `git fetch`, Dev Record with the real PR number and
  merge sha, ticket → `Done`, prune worktree + branch.
- **The local token door moves to a `## Break-glass` section** — kept, documented, never the default.
  `pre-push-main-approval.sh` is **unchanged** and still gates any direct push to `main`.

> ### ⛔ Audit F3 + F4 — Part B has a blast radius the first cut did not name
>
> - **`test_door_preflight_order.py`** hard-pins the presence *and index order* of `gate/main-` →
>   `main-write-gate` → `mint-push-token.sh` → `git push origin main` inside the close-out's fences,
>   and it is **section-blind**. Moving those lines into `## Break-glass` either reds `run_all.py` or
>   — worse — stays green while certifying a road the door no longer takes. **This test is part of
>   the change**: it must learn the two-half shape (assert the PR path is the default and the token
>   path is under the break-glass heading), and that update is itself RED-first.
> - **Four platform doors.** `.opencode/commands/smh-close-task-merge-tree.md` is a byte-identical
>   **37,819-byte** mirror (23,941 for the multi-worktree one), and `test_command_surfaces.py` gives
>   opencode no launcher exemption. The `.claude/skills/…` and `.agents/skills/…` entries for that
>   command are **hand-authored**, so `/smh-sync-agents` will not fix them. Part B is not done until
>   all four doors and both registries agree — pinned by AC-14.

Same two-half edit to `/smh-merge-multiple-workingtrees`'s per-lane step, with the same door sweep.

## Part C — the operator's three one-time acts

1. `gh repo edit --enable-squash-merge=false --enable-rebase-merge=false` — **both are ON today**
   (measured). Either would put a single-parent commit on `main`.
2. Two allow-list lines in `.claude/settings.local.json`:
   `Bash(python3 .agents/scripts/land_pr.py *)` and `Bash(gh pr *)`.
   **A hard prerequisite** (see the F5 box): without it `--merge` cannot run at all, and the split
   degrades to "the operator clicks everything" — which is safe, but is not what was asked for.
3. ✅ Already given — the split ruling.

## Part D — law and the SOP

`.agents/rules/git-policy.md` § *The write gate* → **three roads to `main`**: the PR door (a
`chore`/`epic` lane, the required check, and who merges by lane class); `/cicd-push-e2e` for epics in
project repos; break-glass local. State plainly that the PR door carries no token because **a GitHub
merge never touches a machine** — the token is *structurally absent* there, not bypassed (SCC-118's
own finding). `docs/_scc_sops_prds/workflows_testing_SOP.md` updated **in the same commit**.

⛔ **Audit F11 — build order, not a preference.** `sop_currency.classify('.agents/scripts/land_pr.py')`
returns *"the safety-net scripts"*, so **the first Part A commit is REJECTED unless the SOP doc is
staged with it**, and AC-11 forbids `[sop-ok]` here. Therefore the SOP's new § is written **with**
Part A's first commit, not after it.

## Part E — retire R1 ✅ **complete** (`7858710` code · `a280117` docs)

## Deliberately NOT in this lane

- **No separate `prose_scope` script, and no `/smh-prose-push` command with four new doors.** The
  *predicate* is reinstated (audit F1) as a function inside `land_pr.py`; the *packaging* stays cut.
- **Deleting the local token door.** It stays as break-glass.
- **AVCH-63**, the port to project repos — its own ticket, its own repo, after this lands.

---

## Checkable acceptance

| # | Criterion | The assertion that proves it |
| --- | --- | --- |
| AC-1 ✅ | All five R1 files byte-identical to `origin/main`; `direct-push-allowlist.sh` gone | `git diff origin/main -- <the five>` = 0 lines (**verified**, `7858710` + `a280117`) |
| AC-2 | Every check R1–R8 + P fires, by name, each **RED first** | `test_land_pr.py`, one case per row |
| AC-3 | Empty diff refused by name — *"nothing to land"* | R5 case over a scratch repo with no commits ahead |
| AC-4 | `merge_eligible` **refuses** `.claude/hooks/require-push-approval.py`, `.claude/settings.json`, `.opencode/**`, `docs/migrations/scripts/*.sh`, `AGENTS.md`, `opencode.json`, `requirements.txt`, `..` segments, symlink/gitlink modes, and the **empty set** — and **allows** `docs/**.md`, `_artifacts/**/INDEX.md`, `_artifacts/_memory/**.md`, `docs/repo-map.md`, `docs/.maps-state.json` | table test, one row per class, enumerated from `git ls-files` — **not** a hand-written list (audit F1) |
| AC-5 | Re-run on a branch that already has a PR prints its URL and exits 0; no second PR; works when commits-ahead is 0 | idempotence case + the F6 ordering case |
| AC-6 | The **actionable identifier is the last line** on every path — the URL when handing back, `landed: PR #N · <sha>` on the merge path | stdout assertion, both paths (audit F8) |
| AC-7 | `--merge` emits `gh pr merge --merge`, never `--squash`/`--rebase` | argv assertion via the injected `gh` recorder |
| AC-8 | `--merge` refuses when `origin/main` is **not** an ancestor of the PR head | scratch-repo case (audit F9) |
| AC-9 | The close-out's default path runs no `git checkout main`, no `git push origin main`, no mint outside `## Break-glass`; its pre-merge step hands back | wiring assertion on the command body — pins **wiring**, stated as a convention, not sold as a gate |
| AC-10 | `test_door_preflight_order.py` **learns the two-half shape** and is red before it is green | run it against the un-edited body first (audit F3) |
| AC-11 | `git-policy.md` + the SOP describe the three roads **and no fourth** — a positive check *and* a negative one: zero occurrences of `--direct` / `direct-push-allowlist` | doc grep both ways + `sop_currency` passing **without** `[sop-ok]` (audit F2) |
| AC-12 | Live repo merge method = merge commits only | `@live`-guarded; **skips** without network — never a vacuous green |
| AC-13 | Suite green at the shipping sha, clean tree; lint 0/0; maps clean | `gate_receipt.py run … run_all.py` with `dirty_tree=false`; `workflow_lint --toolkit-only`; `check_maps --depth3-only --strict` |
| AC-14 | **All four doors** for both edited commands agree, plus `.sync-manifest.json` and `commands/INDEX.md`; `land_pr.py` has its `scripts/INDEX.md` row | `test_command_surfaces.py` + `workflow_lint --toolkit-only` (audit F4, F14) |
| AC-15 | Two machines: no new interpreter; `gh` named as a prerequisite and refused-for with a hint | R7 case + the command body's prerequisite line |

## Verification plan

1. **RED first.** `test_land_pr.py` runs before `land_pr.py` exists — the import failing *is* a real
   red for a script that is not there. Each check is then seen red against the stub before its branch
   is written. `test_door_preflight_order.py`'s new assertions run red against the un-edited command
   body (AC-10).
2. **No test calls GitHub.** Scratch repos via `git init` for the git-shaped checks; an injected `gh`
   recorder for argv. The one live item (AC-12) is `@live`-guarded and skips offline.
3. **Mutation sweep drawn from `land_pr.py`**, not from the cases, run through `mutation_sweep.py`
   with a declared table. R1's sweep is the cautionary case: 13/13 killed by its author, **8
   survivors** found by an independent pass over the same file. **The sweep must include a mutant
   that widens `_is_prose`** — F1's failure must be a case that dies.
4. **The diff range is pinned** (audit F12): `merge_eligible` classifies
   `git diff --name-only origin/main...HEAD` (three-dot, merge-base) — the set the PR actually adds,
   not everything `main` gained.
5. **The road is proven by use, three times already** — PRs #5, #6, #8. This lane lands as the fourth.
6. **What is NOT covered, stated rather than glossed:** the `--merge` path cannot run end to end
   until Part C item 2 is in the allow-list; until then it is proven only by recorded argv. The
   walkthrough says so in those words.

## Landing

`lane_qualify` rates this diff **TASK** (it touches `.agents/**` and `tests/**`), and `merge_eligible`
refuses it twice over — so **the operator clicks the merge**, by their own split. The lane eats its
own dog food: `land_pr.py` opens the PR and refuses to merge itself.

---

*The `NO-GO` audit that produced this revision follows, unedited. A re-audit of this text is required
before `approved` (a NO-GO stops the lane; the plan is fixed and re-audited, never re-run hoping for a
different answer).*

## Self-Audit (2026-08-16) — Revision 3, PRE-WORK

**Mode:** PRE-WORK. **Right-size: FULL.** The plan touches a rule (`git-policy.md`), the SOP, two
command bodies that are doors to `main`, a new script that imports another script, and the
`--merge` privilege itself. Every phase was walked.

**Repo pinned from command output, not belief:**
`git -C … rev-parse --show-toplevel` → `/Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees/SCC-183-direct-main-fastlane`
· `rev-parse --abbrev-ref HEAD` → `chore/SCC-183-direct-main-fastlane` · HEAD `7858710`.
Checkable list taken from **authority 1**, the ticket's `CHECKABLE ACCEPTANCE` block, plus the
binding `OPERATOR RULING 2026-08-16 — SPLIT` comment (id 10160).

### Phases walked

- **Phase 0 — scope / right-size / traceability.** Change set: `+.agents/scripts/land_pr.py`,
  `+.agents/scripts/tests/test_land_pr.py`, `~.agents/commands/smh-close-task-merge-tree.md`,
  `~.agents/commands/smh-merge-multiple-workingtrees.md`, `~.agents/rules/git-policy.md`,
  `~docs/_scc_sops_prds/workflows_testing_SOP.md`, plus artifacts. **Lane check: LOCAL confirmed** —
  no `backend/ frontend/ firebase/ functions/ mobile/ .github/` path in the set, so
  `/smh-close-task-merge-tree` is the right door. Traceability: every ticket AC has a plan step;
  **one plan step traces to no AC** — the `--json` flag (F15).
- **Phase 1 — blast radius.** Ran the reference sweeps and read every consumer. Cleared: no sibling
  lane (`git worktree list` → main + this lane only, no landing-order dependency); `task_preflight.py`
  and `closeout_preflight.py` carry no post-merge-shape assumption; `workflow_lint._RULE_POINTERS`
  still satisfied (the edited bodies keep their `git-policy` citation); `commands/INDEX.md` needs no
  row (no new command). **Not cleared:** the two edited command bodies have live byte-identical
  opencode mirrors and generated Antigravity launchers (F4), and one existing test hard-pins the
  step order this plan rewrites (F3). Part E's own sweep found R1's law text still on the branch (F2).
- **Phase 2 — over-engineering gate.** No new command, no new rule file, no clone-and-tweak; the
  `cicd-*`/`smh-*` duplication question does not arise. `land_pr.py` is genuinely new capability, not
  a rebuild — nothing in `.agents/scripts/` opens a PR today. One tripwire fires: a config flag no
  acceptance item requires (F15). One tripwire fires in its subtler form — not *a gate that cannot
  fail*, but **a gate wired to the wrong predicate** (F1) and **three ACs with no runnable proof** (F7).
- **Phase 3 — pre-mortem.** The other machine: ✅ no new interpreter, `python3` matches the five
  existing invocations in the same command body. Fresh clone: ✅ nothing here is `core.hooksPath`-armed.
  Gate fires on someone else's commit: ✅ named refusals, all with hints. Escape hatch: ✅ break-glass,
  auditable. Empty input: ✅ R5 refuses by name — but see F6, it also masks AC-5. Four platform caches:
  ❌ F4. Sibling lands first: ❌ F9 — the merged result is never re-gated. Rollback: Part C-1 and Part E
  are reversible; **the `--merge` write to `main` is not**, which is why F1 is critical rather than high.

### Findings

| # | file:line | Severity | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | `implementation_plan.md:84` (R8) · `.agents/scripts/lane_qualify.py:80` | **CRITICAL** | **Measured**: `classify()` rates as `LIGHT` — 1,102 tracked `.claude/**` files (incl. `.claude/hooks/require-push-approval.py`, the deployed PreToolUse push gate, and `.claude/settings.json`), 69 `.opencode/**` files, `docs/migrations/scripts/{install-git-hooks.sh,install_git_hooks.py,restore-env-master.sh,env_master.py}`, `opencode.json`, `requirements.txt`. `TOOLKIT_PREFIXES` is `.agents/ .githooks/ .github/ _bmad*` only. So a lane touching only those paths passes R8, and `--merge` auto-lands it on `main` with **no operator click, no local token, no PreToolUse ask (the hook reads `git` commands, never `gh`), and no review**. An agent can auto-merge a neutered copy of its own permission hook. **This is R1's own killed critical (walkthrough finding #2, `docs/**` is not a prose tree) reproduced through a different predicate.** | **NEEDS REVISION — blocking.** Either gate `--merge` on a purpose-built allowlist for *this* question, or extend `lane_qualify` (`.claude/`, `.opencode/`, `docs/migrations/scripts/`) as a **named part of this plan with its own RED case**. `lane_qualify`'s own docstring warns against reusing a predicate authored for a different question (`sop_currency.classify`); R3 does exactly that for a third question. |
| F2 | `implementation_plan.md:53,146,162` (Part E / AC-1) | **HIGH** | **Measured**: `git diff --stat origin/main` → `.agents/rules/git-policy.md +27`, `docs/_scc_sops_prds/workflows_testing_SOP.md +41`. Both still describe the `--direct` prose lane: `git-policy.md:114` points at `.agents/scripts/git-hooks/direct-push-allowlist.sh` (deleted by `7858710`), and the SOP ships a copy-paste recipe `mint-push-token.sh --direct …` for a flag `mint-push-token.sh` no longer has. AC-1 only asserts the three `.sh`/`.py` files; AC-11 is a *positive* assertion ("describe the three roads") that a document describing **four** roads, one of them dead, passes cleanly. | **NEEDS REVISION.** Part E is not done. Add the two doc reverts to Part E, and give AC-11 a negative half: `grep -c -- '--direct'` and `grep -c 'direct-push-allowlist'` over `.agents/` + `docs/` must be **0**. |
| F3 | `implementation_plan.md:104-120` (Part B) · `.agents/scripts/tests/test_door_preflight_order.py:154` | **HIGH** | **Measured**: that test reads `.agents/commands/smh-close-task-merge-tree.md` and hard-requires, inside ``` fences, the presence **and index order** of `gate/main-` → `main-write-gate` → `mint-push-token.sh` → `git push origin main`, plus `--delete gate/main-`, plus `flight_recorder.py` before `gate/main-`. `code_lines()` is document-wide and **section-blind**. Part B moves exactly those steps under `## Break-glass`. Two outcomes, both bad: drop or reorder any of them and `run_all.py` goes RED (failing AC-12 *and* the PR's own `main-write-gate`); keep them and the suite stays green while certifying an ordering contract for a road the door no longer takes. The plan names this test nowhere. | **NEEDS REVISION.** Decide and write it down: either the break-glass block preserves the exact order (and the test is re-scoped + re-commented to say it now pins the break-glass path), or the test is rewritten as part of Part B. |
| F4 | `implementation_plan.md:104,122` (Part B) | **HIGH** | **Measured**: `.opencode/commands/smh-close-task-merge-tree.md` is a **byte-identical 37,819-byte** mirror; `.opencode/commands/smh-merge-multiple-workingtrees.md` a 23,941-byte one. `test_command_surfaces.py`'s `door_verdict()` gives opencode **no launcher exemption** — any drift is `stale` and the sweep fails ("run /smh-sync-agents"). `.agents/workflows/*.md` are generated launchers that go `badlauncher` the moment the command's frontmatter `description:` changes. And `.claude/skills/smh-close-task-merge-tree/SKILL.md` + `.agents/skills/…` are **hand-authored** (pinned by CS-05 as never generator-written), so a sync will not touch them. The plan mentions doors nowhere. | **NEEDS REVISION.** Add an explicit Part B step: re-sync the doors, and hand-check the two hand-authored skills. Otherwise the commit that implements Part B reds `run_all.py`, and the PR that carries this lane cannot pass the gate it needs to land. |
| F5 | `implementation_plan.md:66-67` vs `:132-134` | **HIGH** | The plan asserts both *"every `-C` git call lives inside the script where the permission layer never sees it"* (Part A's whole mechanism) and *"`Bash(gh pr *)` is a hard prerequisite for the doc-lane auto-merge… without it `--merge` dies at the tool layer"* (Part C-2). **Both cannot be true.** If subprocesses are invisible, C-2 is unnecessary **and** it hands the session a bare `gh pr merge` at the Bash layer that bypasses F1's mechanical split entirely. If they are visible, Part A does not solve the ticket's stated problem at all. ⚠ **UNVERIFIED**: I did not force a permission denial to measure which limb holds — the *contradiction* is measured, the *resolution* is not. | **NEEDS REVISION.** Resolve by experiment before building: run one throwaway `python3 -c` that shells to a mutation the allow-list does not cover, and record the result in the walkthrough. If invisible (expected), **cut C-2's `Bash(gh pr *)` line** and keep only `Bash(python3 .agents/scripts/land_pr.py *)` — one door, not two. |
| F6 | `implementation_plan.md:81,82,166` (R5/R6 vs AC-5) | **MEDIUM** | Refusal order masks an AC. Once the PR merges, `origin/main` contains the branch, so commits-ahead is 0 and **R5 fires first** — a re-run says *"nothing to land"* and exits non-zero, where AC-5 promises "prints the URL and exits 0". On the `--merge` path `--delete-branch` also removes the remote branch, so R6's divergence check has no upstream left and the plan does not say what it does with a missing `@{u}`. An `--after-merge` turn or any retry then reads as a failed landing. | **NEEDS REVISION.** Probe for an existing PR **before** R5/R6, and specify the missing-upstream branch: an already-merged PR is a **success** report (`PR #N merged as <sha>`), never a refusal. |
| F7 | `implementation_plan.md:96-98,166,168,181-182` | **MEDIUM** | `--dry-run` is defined as "prints the exact `gh` argv it *would* run **without touching the network**" and "no test calls GitHub" — but *detecting an existing PR* (AC-5), *polling `main-write-gate`* and *the allowed-on-LIGHT half of AC-4* (AC-7) are all network reads. The plan names **no injectable `gh` runner or seam**. The builder will either monkeypatch an internal that was never designed to be one, or quietly drop the cases — and three ACs read green with nothing behind them. | **NEEDS REVISION.** Name the seam in Part A: a single `run_gh(argv)` indirection the test replaces with a scripted fake, and say so in the Verification plan. |
| F8 | `implementation_plan.md:167` (AC-6) vs `:92` | **MEDIUM** | AC-6 says the URL is the last line **"every path"**; Part A says the merge path's last line is `landed: PR #N, merge commit <sha>` — which is what the operator's ruling comment actually specifies for the doc lane. Written literally, the assertion fails the intended behaviour; the tempting "fix" is to bolt a URL onto the merge path nobody asked for. | **REVISE THE AC**, not the code: *"the code-lane path ends with the PR URL; the merge path ends with `landed: PR #N, merge commit <sha>`"* — one assertion per path. |
| F9 | `implementation_plan.md:91` (the `--merge` poll) | **MEDIUM** | **Measured** on the live ruleset (`gh api repos/sudomadhatter/Sudo_Hatter_Command/rulesets/20756052`): `enforcement: active`, `bypass_actors: []`, `current_user_can_bypass: never` — **but `strict_required_status_checks_policy: false`**. The required check therefore runs on the PR *head* sha only. If `main` advances between green and merge, the merged tree was never run through `run_all.py`. Pre-existing for the manual door; `--merge` removes the human latency that used to catch it, and R1–R8 contain no "branch contains `origin/main`" refusal. | **NEEDS REVISION (cheap).** Add R9: refuse `--merge` unless `git merge-base --is-ancestor origin/main HEAD`, re-checked immediately before the merge call. Optionally raise `strict_required_status_checks_policy: true` as a fourth Part C operator act. |
| F10 | `implementation_plan.md:109-111` (Part B) | **MEDIUM** | The merge tick is to ride the **last commit on the branch**, worded *"lands via PR #N"* — but `N` is assigned by `gh pr create`, which runs **after** that commit is pushed. Writing the number needs a further commit, which moves the PR head, re-triggers `main-write-gate`, and on the code lane may arrive after the operator has already clicked Merge. As written, SCC-175 does not close: `jira_feed.py finish` holds the ticket again, or the walkthrough on `main` names the wrong PR. | **NEEDS REVISION.** Tick the box with a **number-free** wording (*"landed via the PR door — signed off by the operator's merge"*), or have `land_pr.py` create the PR first and then commit+push the tick, re-polling the new head. Pick one and write it into Part B. |
| F11 | `implementation_plan.md:62,137-144` (build order A→B→D) | **MEDIUM** | **Measured**: `sop_currency.classify('.agents/scripts/land_pr.py')` → `"the safety-net scripts"` — a usage surface. The armed commit-msg gate therefore **rejects the first Part A commit** unless `docs/_scc_sops_prds/workflows_testing_SOP.md` is staged in the same commit, and AC-11 forbids `[sop-ok]`. | **REVISE THE ORDER.** State that every commit in this lane touching `.agents/scripts/` or `.agents/commands/` carries its SOP hunk, or land Part D first. |
| F12 | `implementation_plan.md:96` | **LOW** | The diff range fed to `classify()` is unspecified. `git diff --name-only origin/main HEAD` and `origin/main...HEAD` give different file sets once `main` has moved — the first can pull sibling-lane files into the classification and flip a LIGHT lane to TASK, or (after a bad absorb) the reverse. Ambiguity the builder will fill in by guess. | **TIGHTEN** — name `git diff --name-only origin/main...HEAD` explicitly, with the reason. |
| F13 | `implementation_plan.md:78` (R2's justification) | **LOW** | **Measured**: `main_write_gate.branch_pattern()` is `^(epic\|chore)/<KEY>-\d+-.+`. It accepts `epic/*` too, and it requires the `-<number>-` segment. R2's stated reason ("the gate requires that shape") is half right, and a looser R2 regex would refuse branches the gate accepts — or worse, accept ones it refuses. | **TIGHTEN** — say the reason is *the Task lane*, and pin R2's regex against `main_write_gate.branch_pattern` rather than re-typing it. |
| F14 | `implementation_plan.md:62` | **LOW** | `.agents/scripts/INDEX.md` gets no row for `land_pr.py`. **Measured**: nothing enforces it (`workflow_lint` indexes `commands/INDEX.md` only), and R1's own review already logged `direct-push-allowlist.sh` as undocumented with "nothing enforces it" — so this is convention, not a gate. It is nonetheless the convention this repo keeps. | **ADD THE ROW** — one line, no gate change. |
| F15 | `implementation_plan.md:70` | **LOW** | Phase 2 tripwire: `--json` is a flag **no acceptance item requires**. Nothing in AC-1…AC-13 or the ticket reads machine output from this script. | **CUT IT.** Default disposition for an unjustified tripwire. Saves a code path, a test case, and an output contract nobody has asked for. |

**Sibling-lane landing order:** none. `git worktree list` reports the main checkout at `fdd6d75` and
this lane only; no other `chore/*` tree is live and no file in this change set is held by another
lane. Nothing has to land first.

**Cleared and worth stating:** Part E's core claim **verifies** — `git diff origin/main --` over
`mint-push-token.sh`, `pre-push-main-approval.sh`, `test_main_push_gate.py` is **0 lines**, and
`direct-push-allowlist.sh` is gone from `.agents/scripts/git-hooks/`. `lane_qualify.classify()`
**imports cleanly** from the worktree and returns `(verdict, reason)` as the plan assumes. The
enforcement suite is **32/32 green** at `7858710` — every RED below would be this plan's own.
`LIGHT-VCS` is not a `--merge` hole in practice: it is returned **only** for
`--no-file-changes` with zero paths, which a real PR can never be — it is dead weight in R8's
condition, not an opening.

### The four gates

1. **Verification strategy present?** ⚠ **Partly.** RED-first, a mutation sweep drawn from the
   source, and `--dry-run` argv assertions are all named and all correct in principle — but F7
   shows three ACs (4, 5, 7) have no runnable proof because no `gh` seam is designed, and AC-8's
   own text honestly concedes it is "a convention, not a gate".
2. **Anything irreversible?** ⚠ **Yes, and it is the plan's core.** `--merge` writes `main` with no
   human in the loop; under F1 the file set it permits includes the agent's own permission hook.
   Part C-1 (`gh repo edit`) and Part E (`git revert 7858710`) are both reversible; the `main` write
   is not. Gate it on F1's fix before it ships.
3. **Any step vague enough that the builder will guess?** ⚠ **Yes** — the `gh` seam (F7), the diff
   range (F12), the missing-upstream case (F6), and the exact shape of the break-glass block (F3).
4. **Convention fit?** ⚠ **Mostly.** Stdlib `python3` matching five existing invocations in the same
   body, artifacts in-tree, no new command so no new door, `smh-*` prefix carrying the right
   permission — all correct. It misses the door model for the two command bodies it edits (F4) and
   the `scripts/INDEX.md` convention (F14).

### Per-item

| Part | Verdict |
|---|---|
| **A** `land_pr.py` | **NEEDS REVISION** — F1 (blocking), F5, F6, F7, F9, F12, F13, F15 |
| **B** the two-half close-out | **NEEDS REVISION** — F3, F4, F10 |
| **C** the operator's three acts | **NEEDS REVISION** — F5 (cut item 2's `Bash(gh pr *)` line) |
| **D** law + SOP | **NEEDS REVISION** — F2 (the negative half of AC-11), F11 (ordering) |
| **E** retire R1 | **NEEDS REVISION** — the code half is **SAFE and verified**; the doc half (F2) never ran |

```
Audit verdict: NO-GO
```

**Why NO-GO and not "GO with notes".** F1 is not a rough edge — it is the same defect class that
reviewed R1 **FAIL**, arriving through a different predicate, on a path that writes `main` with no
review, no token, no hook and no click. F2, F3 and F4 each independently red the very gate this lane
must pass to land through its own door. All five are cheap to fix **in the plan**; none is cheap to
fix in a diff. Fix them, then re-run Phases 1 and 2 only — Phase 0's scoping and Phase 3's
pre-mortem rows are unaffected by the fixes.
