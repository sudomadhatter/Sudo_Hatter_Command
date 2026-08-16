# Implementation Plan — SCC-183 · Revision 3: the PR door

**R3 (2026-08-16), THIRD cut — rewritten against two NO-GO audits.** Supersedes R1 (a `--direct`
token push straight to `main` — built, reviewed **FAIL** @ `3e4d4f5`) and R2 (a prose-only PR lane
plus a second command — approved, then **PARKED**). R1's plan text survives at `bd549e6`, R2's at
`96be628`, the first cut of R3 at `9c5ac41`.
The ticket description is the canonical statement of R3; this file is its build sheet — ⛔ **except
for one sentence the ticket still gets wrong, which Part D corrects (audit N9).**

**Both audits are appended below in full, unedited, in order.** Cut 1 → `NO-GO`, 15 findings (F1–F15).
Cut 2 → `NO-GO`, 15 findings (N1–N15), of which 8 were first-audit findings only *partially* cleared.
Nothing is quietly amended; every change carries the finding number that forced it.

**The one defect both audits found, in three different disguises.** R1 shipped *"`docs/**` is not a
prose tree"* and was reviewed **FAIL**. Cut 1 reproduced it through `lane_qualify` — measured, that
predicate rates the agent's own permission hook `LIGHT` (**F1**). Cut 2's fix reproduced it *again*
through its own allowlist, which admitted the **nine** per-folder `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`
front doors — the files every LLM reads on entering a folder, on both machines (**N1**). Each time,
the shape is the same: *a rule about which files are safe to land unread, written from what the
author had in mind rather than from what `git ls-files` actually returns.* Hence the standing
requirement now baked into AC-4 and the mutation table: **refusal cases are enumerated from the repo,
and every one of them must kill a mutant.**

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
| R2 | branch is not `(epic\|chore)/<KEY>-<digits>-<slug>` | ⛔ **audit N13**: do **not** re-type the regex. `from main_write_gate import branch_pattern` and call it — it builds the pattern from `AUTHORISED_PREFIXES` **and this repo's `jira.conf` keys**, with a `[A-Z][A-Z0-9]+` fallback. A re-typed copy drifts from the gate it exists to anticipate. A test asserts R2 and the gate agree |
| R3 | `<KEY>` not in this repo's `jira.conf` `JIRA_KEYS` | a wrong-project key is a failure this system already rules on. Note `branch_pattern` already consumes the keys, so R3 is the *explicit message*, not a second derivation |
| R4 | working tree dirty | a PR must describe committed work; a dirty tree is the SCC-184 failure condition itself |
| **P** | **PR-exists probe — runs BEFORE R5, and BRANCHES ON STATE** | see the box below |
| R5 | zero commits vs `origin/main` **and no PR** → *"nothing to land"* | ⛔ an empty input must never read as a pass (`tests-must-gate-for-real` rule 1) |
| R6 | local branch **diverged** from its remote | force-push is banned. **Audit F6b**: after `--delete-branch` there is no upstream — that is *absence*, not divergence, and is handled as its own arm |
| R7 | `gh` absent or unauthenticated | name the prerequisite with an install/login hint, never assume |
| R8 | **`--merge` eligibility** — see the box below | the split, made mechanical |

### ⛔ Audit N2 (HIGH) — check P must branch on PR **state**, never bare-exit 0

The second cut wrote P as *"if a PR exists → print its URL and exit 0."* Measured: `gh pr list
--state all` on this repo returns **PR #7 CLOSED-unmerged** (also #3, #4). A bare existence probe
therefore has three holes, each of which **reports success while nothing landed** — the exact shape
`tests-must-gate-for-real` rule 1 bans. F6's fix over-corrected. P branches:

| PR state found for this branch | `land_pr.py` (no `--merge`) | `land_pr.py --merge` |
| --- | --- | --- |
| **none** | fall through to R5 → create | fall through to R5 → create → merge steps |
| **OPEN** | print URL, exit 0 (idempotent) | ⛔ **fall through to the merge steps** — do not exit 0, or a re-run after a pending gate never merges and still reports success |
| **MERGED**, `HEAD` is an ancestor of it | report `landed: PR #N · <sha>`, exit 0 | same — nothing left to do |
| **MERGED**, `HEAD` is **not** an ancestor (new commits since) | continue → open a **new** PR | same, then merge |
| **CLOSED**, unmerged | ⛔ **refuse by name** — *"PR #N was closed unmerged; reopen it or re-cut the branch"*. Never exit 0 | same refusal |

One AC row per state (AC-5).

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
authored against a product repo's layout is vacuous in a governance repo"*.

⛔ **Audit N1 (CRITICAL) — the second cut's allowlist reproduced F1 a third time.** Its arm 1 was
*"`*.md` under `docs/`, `_artifacts/`, `_my_resources/` (any depth)"* and its refusal named only the
**root** `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`. Measured: `git ls-files` returns **nine tracked
per-folder front doors** inside those prefixes — `docs/{AGENTS,CLAUDE,GEMINI}.md`,
`_artifacts/{…}`, `_my_resources/{…}` — and `lane_qualify.classify()` rates all nine **LIGHT**. Both
arms passed, so `--merge` would have auto-landed `_artifacts/CLAUDE.md`: the file every LLM reads on
entering that folder, on both machines, with no click and no review. **Refusal is by BASENAME at any
depth, never by root path.** Same defect, third appearance; this is the arm that kills it.

⛔ **Precedence is load-bearing and stated: refusals are evaluated FIRST and win.** (Audit N6: the
second cut's refusal list read as careful carving while doing no work — every path it named was
already unreachable under arm 1, so a `_is_prose` with *no refusals at all* would have scored 100% on
AC-4. That is `prose-pinning-guards-are-vacuous` in predicate form.)

**Refused first — these are what the allow arms would otherwise admit:**

- ⛔ basename `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` **at any depth** — nine tracked files today; law
  and routing, not prose (N1);
- ⛔ anything under `docs/migrations/` **wholesale** — not `docs/migrations/scripts/`. Measured: that
  directory holds **zero** `.md` files, so the second cut's bullet was unreachable while six real
  guides (`install_guides/machine_setup_card.md`, `new_machine-migration-guide.md`,
  `antigravity-ide-extension-migration.md`, `propagate-autopilot-glm-hybrid.md`,
  `python_vytest-updates-other-machines.md`, `gemini_extensions/gemini-extensions-sync-guide.md`)
  were allowed. It refused the scripts and admitted the instructions telling a human to run them —
  missed by one directory level (N7);
- ⛔ empty path set → **refused by name**, never a pass;
- ⛔ any path whose git mode is not a regular blob (symlink / gitlink). ⛔ **Audit N12 — name the
  mechanism**: `--name-only` carries **no mode**, so the classified set is read with
  `git diff --raw origin/main...HEAD` (or `ls-files -s`) and the mode column is the source. Measured:
  10 gitlinks exist (`Projects/*`) and `lane_qualify` rates a bare gitlink bump **`LIGHT`** — only the
  prefix is holding that door today.

**Then allowed:**

- `*.md` under `docs/`, `_artifacts/`, `_my_resources/` (any depth);
- the tracked generator output `docs/repo-map.md`, and any `_artifacts/**/INDEX.md`;
- `_artifacts/_memory/**.md`.

⛔ **N16 (CRITICAL) — root `router.md` is CUT from the allowlist.** Found by running the revised
predicate over `git ls-files` rather than reading it: both prior cuts listed `router.md` as an allow
arm **by name**. It is the **MASTER ROUTER** — *"You are in the LOBBY. This table is the directory:
pick the workspace, then read **its** `AGENTS.md`"* — the first file an agent reads to decide where
to go, and it carries the artifact-ownership exception registry. It is routing law in exactly the
sense the nine front doors are, and it would have auto-landed unread. **This is the same defect a
fourth time**, surviving the very audit that killed its third appearance, because that audit was
hunting the prefix arm and this one is an exact-path arm. It is why the enumerate-from-the-repo rule
is now the standing requirement and not a note.

**Measured, this cut — the revised predicate run over all 3,235 tracked files:** **484 eligible**
(15%). Zero at the repo root, zero non-`.md`, zero front doors, zero under `docs/migrations/`. The
eligible set is 454 `_artifacts/**` (session artifacts, `_memory/`, `INDEX.md`s), 19 `docs/**` and 11
`_my_resources/**`. Every one of the seven refusal mutants above dies. ⛔ This probe — predicate ×
`git ls-files`, not predicate × imagination — **is** the AC-4 test, and writing it is step one of
Part A.

⛔ **Audit N11 — `docs/.maps-state.json` is CUT from the allowlist.** It is `check_maps`' own
baseline (`check_maps.py:345` reads `reconciled_at`, `:380` writes it) and
`check_maps --depth3-only --strict` is one of *this lane's own* AC-13 gates. Auto-merging it lets a
lane move the baseline every future staleness check measures from, unread. It was also the single
non-`.md` file in an allowlist sold as prose-only. A maps lane that also touches `docs/repo-map.md`
now costs the operator one click — the right price.

⛔ **Audit N12 — the `..`-segment and absolute-path arms are CUT.** The classified set comes from
`git diff … origin/main...HEAD`, which emits repo-relative normalised paths: never absolute, never a
`..` segment. Both arms were error handling for states that cannot occur — a Phase 2 tripwire.

### ⛔ Audit N5 — this allowlist is NARROWER than the operator's ruling, and that is declared, not hidden

The ruling reads *"Doc / index / memory / maps lanes → the agent merges."* Measured against the three
lanes that actually landed: PR #5 (maps) ✅ allowed · PR #8 (memory) ✅ allowed · **PR #6 (SCC-184) —
the doc lane the operator merged an hour before giving the ruling, and cited in it — touches
`.agents/rules/git-policy.md`, which `lane_qualify` rates `TASK` and `_is_prose` refuses ⇒ REFUSED.**
The same goes for *index* lanes touching the tracked `INDEX.md` files under `.agents/` and `.claude/`.

So two of the four classes the ruling names sit **outside** this door. Narrower-than-the-ruling is
the safe direction and is the right call — but presenting it *as* the ruling is not:
`blocking-gates-need-a-quoted-ruling` holds that a derived corollary is a **proposal, never law**.
It is therefore surfaced to the operator as a proposal at approval time, in one line: *"`.agents/`
rule and toolkit-`INDEX.md` edits will still need your click, even though they are doc lanes."*

### Then

Push the branch if merely ahead → **freshness check (below)** → `gh pr create --base main`, body
assembled from the walkthrough's `Verdict:` line, the `gates/*.json` receipts and the change summary
→ **print the URL last**.

⛔ **Audit F9 + N3 — the freshness refusal is at PR-CREATE time, on BOTH paths.** Measured on the
live ruleset: `enforcement: active`, required check `main-write-gate`,
`strict_required_status_checks_policy` = **false** — so the check certifies the PR head *only*, and a
sibling landing in between is **not** re-gated. The second cut bolted this re-check to the `--merge`
path alone. But the operator's split routes **CODE** lanes — the riskier half — to the click, so the
window was narrowed on the safe half and left **fully open on the dangerous one**. Therefore:

> refuse unless `git merge-base --is-ancestor origin/main <head>` — if `main` moved, absorb and
> re-gate rather than open (or merge) stale. Enforced at create, and **re-enforced** immediately
> before `gh pr merge` on the `--merge` path, because `main` can move while the check runs.

**With `--merge` (eligible lanes only):**

1. poll `main-write-gate` on the PR head until completed;
2. re-run the ancestry refusal above (the create-time pass can be minutes stale);
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
⛔ **Audit N14**: when `gh` is unreachable or unauthenticated, `--dry-run` **degrades to argv-only**
rather than dying at R7 — offline is exactly when a preview is most useful, and R7's hard refusal
belongs to the acting paths, not the preview.

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
>   opencode no launcher exemption. Part B is not done until all four doors and both registries
>   agree — pinned by AC-14.
> - ⛔ **Audit N10a — the second cut called the two `SKILL.md` files hand-authored. Measured, they
>   are not.** `.claude/skills/smh-close-task-merge-tree/SKILL.md` and `.agents/skills/…` are
>   **1,022 bytes, byte-identical to each other**, and are *thin launchers* ("read
>   `.agents/commands/…` and follow it END TO END"). Two consequences the first framing hid:
>   (a) their frontmatter `description:` is a **verbatim copy of the command's**, and
>   `test_command_surfaces.is_launcher_for()` compares exactly that — so editing the command's
>   frontmatter alone flips **all four doors to `badlauncher`**; the frontmatter edit and the door
>   regeneration are one commit, not two.
>   (b) that copied description currently reads *"merge to main with --no-ff … **Invoking this skill
>   is the operator merge sign-off**"*, and the body repeats it. **Part B makes both sentences
>   false** — the merge moves to the PR and the sign-off becomes the operator's click. AC-14
>   (all doors agree) **cannot catch this**: four consistent copies of a false sentence agree
>   perfectly. So AC-14 gains a **semantic** row — no door may still describe the local `--no-ff`
>   merge as the sign-off — which is a wiring check on named strings, not a prose gate.

Same two-half edit to `/smh-merge-multiple-workingtrees`'s per-lane step, with the same door sweep.

## Part C — the operator's one-time acts

1. `gh repo edit --enable-squash-merge=false --enable-rebase-merge=false` — **both are ON today**
   (measured). Either would put a single-parent commit on `main`.
2. Allow-list lines in `.claude/settings.local.json`:
   `Bash(python3 .agents/scripts/land_pr.py *)`, plus the **narrow** `gh` reads:
   `Bash(gh pr create *)`, `Bash(gh pr view *)`, `Bash(gh pr list *)`.
   ⛔ **Audit N4 — NOT a bare `Bash(gh pr *)`.** That is a superset of `gh pr merge --merge` typed
   directly at the Bash layer: it would hand every future session an unconditional merge capability
   that **bypasses `merge_eligible` entirely**. The mechanical split only binds if `land_pr.py` is
   the *only* road to a merge; a bare wildcard makes it one road among two, which defeats the lane.
3. **Decide `strict_required_status_checks_policy`** (audit N3). Today it is `false`, so the required
   check certifies the PR head only and a sibling landing in between is not re-gated. Setting it
   `true` makes GitHub itself refuse a stale PR — closing the window on the **click** path, which
   `land_pr.py` cannot reach. Cost: a PR that falls behind must be updated before it can merge.
   **Recommended: yes.** ⚠ This is a gate that can block a shipping path, so per
   `blocking-gates-need-a-quoted-ruling` it needs the operator's own words — it is a **proposal**
   here, and ships only if they give them.
4. ✅ Already given — the split ruling (narrowed as declared in the N5 box, and re-surfaced at
   approval time).

## Part D — law and the SOP

`.agents/rules/git-policy.md` § *The write gate* → **three roads to `main`**: the PR door (a
`chore`/`epic` lane, the required check, and who merges by lane class); `/cicd-push-e2e` for epics in
project repos; break-glass local. State plainly that the PR door carries no token because **a GitHub
merge never touches a machine** — the token is *structurally absent* there, not bypassed (SCC-118's
own finding). `docs/_scc_sops_prds/workflows_testing_SOP.md` updated **in the same commit**.

⛔ **Audit N10b — five dependants the second cut never named.** A quoted-glob sweep for
`mint-push-token` / `git push origin main` (the *unquoted* form dies under zsh with "no matches
found" and prints nothing — a silently empty sweep) returns `.agents/scripts/hooks_armed.py`,
`.agents/scripts/task_preflight.py`, `.agents/scripts/tests/test_task_preflight.py`,
`.agents/scripts/tests/test_main_push_gate.py`, and — **a third doc describing the landing road** —
`docs/_scc_sops_prds/jira_manual.md`. That doc joins Part D's scope; AC-11's positive half
("the three roads and no fourth") has to hold across **all three** docs, not two.

⛔ **Audit N9 — F5 is not closed until the TICKET is corrected.** This file declares the SCC-183
description canonical, and that description still reads *"every `-C` git call is INSIDE the script
where the permission layer never sees it."* The withdrawal lives only here, so the canonical document
still asserts the mechanism the plan says it does not rest on — and both `/smh-quick-dev` and the
close-out read the ticket first. **Part D step: replace that sentence in the Jira description** with
the withdrawal's own reasoning (one stable command string, testable code, never touching the shared
checkout — and *designing around the agent's own permission layer is not a thing this lane does;
that layer is the operator's control over the agent, not an obstacle to route around*). ⛔ `acli
edit --description` **REPLACES** — read the description back after writing it.

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
| AC-4 | ⛔ **Refusal rows are re-derived from paths the ALLOW arms would otherwise admit** — the only set that can kill a mutant (audit N6). Namely: the **nine** tracked `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` under `docs/`, `_artifacts/`, `_my_resources/` (N1); the **six** `docs/migrations/**.md` guides (N7); `docs/.maps-state.json` (N11); a gitlink bump (N12); and the **empty set**. Allows: `docs/**.md` outside `migrations/`, `_artifacts/**/INDEX.md`, `_artifacts/_memory/**.md`, `docs/repo-map.md`, root `router.md` | table test, rows **enumerated from `git ls-files`**, not hand-written (audit F1). ⛔ The old row list is retired: every path it named was already unreachable under arm 1, so a `_is_prose` containing **no refusals at all** scored 100% on it |
| AC-4b | Refusals are evaluated **before** the allow arms | precedence case: a path matching both (e.g. `docs/CLAUDE.md`) refuses |
| AC-5 | One row **per PR state** — none / OPEN / MERGED-ancestor / MERGED-with-new-commits / CLOSED-unmerged — on both the plain and `--merge` paths (audit N2). CLOSED refuses **by name**; OPEN under `--merge` **falls through** rather than exiting 0 | table test against an injected `gh` recorder + the F6 ordering case |
| AC-6 | The **actionable identifier is the last line** on every path — the URL when handing back, `landed: PR #N · <sha>` on the merge path | stdout assertion, both paths (audit F8) |
| AC-7 | `--merge` emits `gh pr merge --merge`, never `--squash`/`--rebase` | argv assertion via the injected `gh` recorder |
| AC-8 | The ancestry refusal fires on **both** paths — at `pr create` time (so the click path is covered too) **and** again immediately before `gh pr merge` | two scratch-repo cases (audit F9 + N3) |
| AC-9 | The close-out's default path runs no `git checkout main`, no `git push origin main`, no mint outside `## Break-glass`; its pre-merge step hands back | wiring assertion on the command body — pins **wiring**, stated as a convention, not sold as a gate |
| AC-10 | `test_door_preflight_order.py` **learns the two-half shape** and is red before it is green — ⛔ **and its three negative-control fixtures (`PROSE_ONLY`, `COMMENT_ONLY_FENCE`, `MUTANT_WAIT_AFTER_MINT`), its `--delete gate/main-` assertion, its `flight_recorder.py`-before-gate-ref assertion and its separate `PROJECT_DOOR` case over `/cicd-push-e2e` all survive the rewrite unchanged** (audit N15) — Part B does not touch that door, and a rewrite that satisfies "red before green" while dropping the controls leaves a guard that cannot fail | run it against the un-edited body first (audit F3); diff the fixture set before/after |
| AC-11 | `git-policy.md` + the SOP + **`jira_manual.md`** (audit N10b) describe the three roads **and no fourth** — a positive check *and* a **scoped** negative one: `git grep -c -- '--direct\|direct-push-allowlist' -- .agents docs` = **0** | ⛔ **audit N8 — the scope is load-bearing.** Unscoped, the AC is unpassable: this lane's own `implementation_plan.md` (8), `walkthrough.md` (9) and `_artifacts/_main/INDEX.md` (1) legitimately name the retired flag, and deleting the lane's audit trail to go green is what `artifacts-always-first` forbids. Plus `sop_currency` passing **without** `[sop-ok]` (audit F2) |
| AC-12 | Live repo merge method = merge commits only | `@live`-guarded; **skips** without network — never a vacuous green |
| AC-13 | Suite green at the shipping sha, clean tree; lint 0/0; maps clean | `gate_receipt.py run … run_all.py` with `dirty_tree=false`; `workflow_lint --toolkit-only`; `check_maps --depth3-only --strict` |
| AC-14 | **All four doors** for both edited commands agree, plus `.sync-manifest.json` and `commands/INDEX.md`; `land_pr.py` has its `scripts/INDEX.md` row | `test_command_surfaces.py` + `workflow_lint --toolkit-only` (audit F4, F14). ⛔ The two `SKILL.md`s are **generated 1,022-byte launchers** whose `description:` is a verbatim copy of the command's, and `is_launcher_for()` compares exactly that — the frontmatter edit and the regeneration are **one commit** (audit N10a) |
| AC-14b | ⛔ **Semantic**: no door still calls the local `--no-ff` merge the operator's sign-off | named-string assertion across all four doors + both `SKILL.md` descriptions. AC-14 cannot catch this — four consistent copies of a false sentence agree perfectly (audit N10a) |
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
   survivors** found by an independent pass over the same file. ⛔ **The declared table must contain
   these widening mutants, and each must DIE** (audit N6 — the mutants that matter were the ones
   missing):
   - drop the basename refusal → `_artifacts/CLAUDE.md` becomes eligible (N1);
   - narrow `docs/migrations/` back to `docs/migrations/scripts/` → the six install guides become
     eligible (N7);
   - re-add `docs/.maps-state.json` to the allowlist (N11);
   - flip precedence so the allow arms are evaluated first (AC-4b);
   - drop the `lane_qualify` half, and separately drop the `_is_prose` half — **either alone must
     still refuse** `.claude/hooks/require-push-approval.py` (F1);
   - make P exit 0 on a CLOSED PR (N2), and delete the create-time ancestry check (N3).
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

---

## Re-Audit (2026-08-16) — Revision 3, second cut

**Mode:** PRE-WORK (Parts A–D unbuilt; Part E built and re-verified). **Right-size: FULL.** Adversarial
re-audit of the rewrite against the 15 findings above, plus a hunt for defects the rewrite introduced.
The first audit is untouched.

**Repo pinned from command output, not belief:** `git -C … rev-parse --abbrev-ref HEAD` →
`chore/SCC-183-direct-main-fastlane`, HEAD `9c5ac41`; `rev-parse --short origin/main` → **`b0fda44`**
(moved from `fdd6d75` since the plan was written); `git worktree list` → main checkout + this lane only.
Working tree clean.

**⛔ Standing note on method.** The first audit's proudest finding was reasoned rather than run and came
out inverted. Everything below marked **Measured** was executed this turn; everything unrun is marked
**⚠ UNVERIFIED** by name in § What could not be verified.

### Phases walked

- **Phase 0 — scope / right-size / traceability.** Change set unchanged from the first cut. Lane check
  re-run: still LOCAL, no deployable path. Traceability: `--json` is gone (F15 cleared), so no plan step
  now traces to nothing — but **AC-4's refusal half traces to nothing runnable** (N6) and **AC-11 as
  written cannot pass** (N8).
- **Phase 1 — blast radius, re-derived against `b0fda44`.** `origin/main` gained exactly one merge,
  PR #8 (SCC-186), touching three `_artifacts/_memory/` files. **Zero overlap** with this lane's change
  set — no landing-order dependency, but the lane must absorb `b0fda44` before it opens its PR, or its
  own two-dot diff shows three memory files as deletions (measured in `git diff --stat origin/main`).
  Re-ran the door sweep and the dependant sweep with **quoted** `--include` globs (the unquoted form
  dies under zsh with "no matches found" and prints nothing — a silent empty sweep). That sweep found
  five dependants the plan does not name (N10b).
- **Phase 2 — over-engineering / drift gate.** Two tripwires fire, both inside the F1 fix: **error
  handling for states that cannot occur** (the `..` / absolute-path arms, N12) and **a check whose
  input can never reach it** — every explicit-refusal bullet in `_is_prose` is unreachable (N6). One
  tripwire *cleared*: the `--json` flag is cut, and no new command or rule file appears.
- **Phase 3 — pre-mortem.** Other machine ✅ (stdlib `python3`, no new interpreter). Fresh clone ✅
  (nothing `core.hooksPath`-armed). Empty input ✅ at the `merge_eligible` layer (measured:
  `lane_qualify.classify(repo, [], False)` → `TASK`, "silence is never a pass") but ❌ at the
  **command** layer (N2: the P probe turns three real PR states into exit 0). Four platform caches
  ⚠ (N10a). Sibling lands first ⚠ (N3: only the `--merge` path is guarded; the click path is not).
  Rollback: the `main` write is still the irreversible act, and N1 widens what it can write.

### Findings

Severity is against *what reaches `main` unseen*. `R` = a first-audit finding not cleared.

| # | file:line | Sev | Failure scenario (measured unless marked) | Disposition |
|---|---|---|---|---|
| **N1** `R`(F1) | `implementation_plan.md:141-142` (`_is_prose` arm 1) | **CRITICAL** | **Measured.** Allow arm 1 is *"`*.md` under `docs/`, `_artifacts/`, `_my_resources/` (any depth)"*. `git ls-files` returns **nine tracked per-folder front doors** inside those prefixes: `docs/{AGENTS,CLAUDE,GEMINI}.md`, `_artifacts/{AGENTS,CLAUDE,GEMINI}.md`, `_my_resources/{AGENTS,CLAUDE,GEMINI}.md`. The refusal bullet names only the **root** three. Second arm measured: `lane_qualify.classify(repo, ['docs/CLAUDE.md','_artifacts/AGENTS.md','_my_resources/GEMINI.md'], False)` → **`('LIGHT', '3 path(s), none deployable and none in the toolkit')`**. **Both arms pass ⇒ `--merge` auto-lands them.** A lane rewrites `_artifacts/CLAUDE.md` — the file every LLM reads on entering that folder, on both machines — and it reaches `main` with no click, no token, no review. This is F1's own defect (a routing/permission surface auto-merged) reproduced *through the fix for F1*, exactly as F1 was R1's killed critical reproduced through a different predicate. | **NEEDS REVISION — blocking.** Refuse `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` **by basename at any depth**, not by root path. Add the nine to AC-4's refusal rows and to the mutation table as a mutant that must die. |
| **N2** | `implementation_plan.md:102` (check P) | **HIGH** | **Measured.** P is *"If a PR exists → print its URL (and its state) and **exit 0**"*, with no state discrimination. `gh pr list --state all` on this repo returns **PR #7 `chore/SCC-185-memory-housekeeping` CLOSED, unmerged** (also #3, #4 CLOSED). Three holes: (a) a **closed** PR ⇒ P exits 0 ⇒ no PR is opened, nothing lands, and the close-out reports success; (b) a **merged** PR plus new commits ⇒ same silent no-op; (c) on `--merge`, an existing **open** PR makes P exit 0 *before* steps 1–4, so any re-run after a pending gate never merges and still exits 0. F6's fix over-corrected into the exact thing `tests-must-gate-for-real` rule 1 bans. | **NEEDS REVISION.** P must branch on state: `OPEN` → report and (with `--merge`) **fall through** to the merge steps; `MERGED` → success report only if `HEAD` is an ancestor of it, else continue to open a new PR; `CLOSED` → **refuse by name**, never exit 0. One AC row per state. |
| **N3** `R`(F9) | `implementation_plan.md:158-162` · AC-8 | **HIGH** | **Measured on the live ruleset**: `enforcement: active`, checks `['main-write-gate']`, `strict_required_status_checks_policy` = **false** — the plan's claim verifies. But the ancestry re-check is bolted to the **`--merge`** path only. The operator's split routes **CODE** lanes — the riskier half — to the click, and neither R1–R8 nor Part B refuses a *stale* PR there. GitHub merges it un-re-gated. F9's fix therefore narrows the window on the safe half and leaves it fully open on the dangerous half. The first audit's optional Part C-4 (`strict_required_status_checks_policy: true`) was dropped rather than decided. | **NEEDS REVISION.** Make the ancestry refusal a check at **PR-create** time (both paths), *and* put `strict_required_status_checks_policy: true` back as a Part C operator act with a stated yes/no. |
| **N4** `R`(F5) | `implementation_plan.md:216-219` (Part C-2) | **HIGH** | The F5 box withdraws the invisibility claim but **the experiment F5's disposition ordered was never run**, so the plan keeps *both* allow-list lines. `Bash(gh pr *)` is a superset of `gh pr merge --merge` typed directly at the Bash layer — it hands every future session an unconditional merge capability that **bypasses `merge_eligible` entirely**. The mechanical split only binds if `land_pr.py` is the *only* road to a merge; this line makes it one road among two. ⚠ Whether the narrower line is even needed depends on the unrun experiment. | **NEEDS REVISION.** Either run the one-command experiment and record it, or narrow item 2 to `Bash(gh pr create *)`, `Bash(gh pr view *)`, `Bash(gh pr list *)` — never a bare `gh pr *`. |
| **N5** | `implementation_plan.md:127-148` vs the ticket's `OPERATOR RULING … SPLIT` | **HIGH** | **Measured.** The ruling: *"Doc / index / memory / maps lanes → the agent merges."* Against the three lanes that actually landed: PR #5 (maps) `docs/.maps-state.json` + `docs/repo-map.md` → **allowed** ✅; PR #8 (memory) → **allowed** ✅; **PR #6 (SCC-184) — the doc lane the operator merged an hour before giving the ruling, and cited in it — touches `.agents/rules/git-policy.md`, which `lane_qualify` rates `TASK` and `_is_prose` refuses ⇒ REFUSED.** Same for any *index* lane touching the ten tracked toolkit `INDEX.md` files under `.agents/` and `.claude/`. So two of the four classes the ruling names are silently outside the door, and the plan presents the allowlist as implementing the ruling. Narrower-than-the-ruling is defensible; **undeclared** narrowing of a quoted ruling is not (`blocking-gates-need-a-quoted-ruling`: a derived corollary is a proposal, never law). | **NEEDS REVISION (cheap).** State the narrowing in Part A in one paragraph, with the PR #6 example, and surface it to the operator as a proposal rather than shipping it as their ruling. |
| **N6** | `implementation_plan.md:143-148` · AC-4 | **MEDIUM** | **Measured.** Every path AC-4 lists as *must refuse* is already refused **by arm 1 alone** — `.claude/**`, `.opencode/**`, `.agents/**`, `.githooks/**`, `.github/**`, `tests/**`, `opencode.json`, `requirements.txt` and `docs/migrations/scripts/*.sh` can none of them match *"`.md` under docs/_artifacts/_my_resources"*; and the empty set is refused one layer earlier by `lane_qualify` (`[]` → `TASK`, measured). `docs/migrations/scripts/` holds **zero** `.md` files, so even that bullet is unreachable. **A `_is_prose` consisting of nothing but arm 1 plus the three exact paths scores 100% on AC-4's entire refusal half.** The refusals read as careful carving while doing no work, and the mutants that matter (N1, N7) are untested. This is `prose-pinning-guards-are-vacuous` in predicate form. | **NEEDS REVISION.** Delete the unreachable bullets or move them above the allow arms and say precedence is load-bearing; then re-derive AC-4's refusal rows from paths arm 1 **would otherwise admit** — which is the only set that can kill a mutant. |
| **N7** | `implementation_plan.md:141,145` | **MEDIUM** | **Measured.** `docs/migrations/install_guides/` holds five tracked `.md` files — `machine_setup_card.md`, `new_machine-migration-guide.md`, `antigravity-ide-extension-migration.md`, `propagate-autopilot-glm-hybrid.md`, `python_vytest-updates-other-machines.md` — plus `docs/migrations/gemini_extensions/gemini-extensions-sync-guide.md`. All are **allowed** (`lane_qualify` → `LIGHT`, measured). These are the copy-paste command sequences the operator runs on a fresh machine. The refusal reached for `docs/migrations/scripts/` and **missed by one directory level**: it excluded the scripts and admitted the instructions that tell a human to run them. | **NEEDS REVISION.** Refuse `docs/migrations/` wholesale, not `docs/migrations/scripts/`. |
| **N8** | `implementation_plan.md:260` (AC-11) | **MEDIUM** | **Measured.** AC-11's negative half is *"zero occurrences of `--direct` / `direct-push-allowlist`"* with **no scope**. `git grep -c` on this branch: `implementation_plan.md` **8**, `walkthrough.md` **9**, `_artifacts/_main/INDEX.md` **1** — all tracked files in this lane. As literally written the AC can only be satisfied by deleting the lane's own audit trail, which `artifacts-always-first` forbids. The first audit's disposition scoped it to `.agents/` + `docs/`, where it measures **0** today; the rewrite dropped the scope. A builder meets an unpassable AC by narrowing it silently — and then nobody knows what it checked. | **TIGHTEN.** Write the scope into AC-11: `git grep -c … -- .agents docs` must be 0. |
| **N9** `R`(F5) | `implementation_plan.md:6` vs `:70-73` | **MEDIUM** | **Measured.** The plan declares *"The ticket description is the canonical statement of R3; this file is its build sheet"* — and the live SCC-183 description still reads *"every `-C` git call is INSIDE the script where the permission layer never sees it."* The withdrawal exists **only in the build sheet**, so the canonical document still asserts the claim the plan says it does not rest on. Anyone who reads the ticket first — which is what `/smh-quick-dev` and the close-out both do — builds against the withdrawn mechanism. | **NEEDS REVISION.** F5 is not resolved until the ticket description's sentence is corrected. That is a Jira write for the operator's flow, not an audit act; name it as a Part C or Part D step. |
| **N10** `R`(F3/F4) | `implementation_plan.md:196-210` | **MEDIUM** | **(a) Measured**: `.claude/skills/smh-close-task-merge-tree/SKILL.md` and `.agents/skills/…` are **1,022 bytes, byte-identical to each other**, and are *thin launchers* ("read `.agents/commands/…` and follow it END TO END"), not the hand-authored bodies the plan calls them. Their frontmatter `description:` is a **verbatim copy of the command's**, and `test_command_surfaces.is_launcher_for()` compares exactly that — so changing the command's frontmatter alone flips all four doors to `badlauncher`. Worse, the launcher body asserts *"Invoking this skill is the operator's per-merge sign-off"*, a sentence **Part B makes false** and AC-14 (agreement between doors) cannot catch, because four consistent copies of a false sentence agree perfectly. **(b) Measured**, quoted-glob sweep for `mint-push-token` / `git push origin main`: five dependants the plan never names — `.agents/scripts/hooks_armed.py`, `.agents/scripts/task_preflight.py`, `.agents/scripts/tests/test_task_preflight.py`, `.agents/scripts/tests/test_main_push_gate.py`, and **`docs/_scc_sops_prds/jira_manual.md`**, a *third* doc describing the landing road that Part D does not update and AC-11's positive half ("the three roads and no fourth") would have to cover. | **NEEDS REVISION.** Correct the hand-authored claim, add a semantic check (the four doors must not still call the local merge the sign-off), and put `jira_manual.md` into Part D's scope. |
| **N11** | `implementation_plan.md:140-141` | **LOW** | **Measured.** `docs/.maps-state.json` is allowed by exact path and rated `LIGHT`. It is `check_maps`' own baseline: `check_maps.py:345` reads `reconciled_at`, `:380` writes `{"reconciled_at": <head>}` — and `check_maps --depth3-only --strict` is one of **this lane's own AC-13 gates**. Auto-merging it lets a lane move the baseline every future staleness check measures from, with no human reading the diff. It is also the one non-`.md` file in an allowlist sold as prose-only. | **CUT or JUSTIFY.** Simplest: drop `docs/.maps-state.json` from the allowlist — a maps lane that also touches `docs/repo-map.md` still needs one click. |
| **N12** | `implementation_plan.md:147-148` | **LOW** | Phase 2 tripwire — *error handling for states that cannot occur*. The classified set is `git diff --name-only origin/main...HEAD` (F12, correctly pinned), which emits **repo-relative, normalised** paths: never absolute, never a `..` segment. Both arms are unreachable. The mode arm has a different problem: `--name-only` **carries no mode**, so there is no stated mechanism to detect symlink/gitlink at all — the builder must switch to `--raw`/`ls-files -s` and the plan does not say. Measured: 10 gitlinks exist (`Projects/*`), all already refused by prefix, and `lane_qualify` rates a bare gitlink bump **`LIGHT`** — so the prefix is the only thing holding that door. | **TIGHTEN.** Cut the `..`/absolute arms; name `--raw` (or `ls-files -s`) as the source of the mode, or cut the mode arm and say the prefix carries it. |
| **N13** `R`(F13) | `implementation_plan.md:99` (R2) | **LOW** | F13 was half-taken. The plan corrected the *description* ("it is not chore-only") but still **re-types** the regex instead of pinning it. **Measured**: `main_write_gate.branch_pattern(keys)` builds `^(epic\|chore)/(<keyalt>)-\d+-.+` from `AUTHORISED_PREFIXES` **and this repo's `jira.conf` keys**, with a fallback `[A-Z][A-Z0-9]+` when keys are absent. A re-typed copy drifts from the gate it is meant to anticipate, and R3 (the key check) then duplicates work `branch_pattern` already does. | **TIGHTEN.** `from main_write_gate import branch_pattern` and call it; assert in the test that R2 and the gate agree. |
| **N14** `R`(F7) | `implementation_plan.md:170-174` | **LOW** | F7's fix redefines `--dry-run` as *"performs network READS … no writes"*. Correct and honest — but it makes the one flag an operator would use to preview a landing depend on `gh` auth and connectivity, so **offline it dies at R7 instead of printing the argv it would have run**, which is the moment a preview is most useful. | **NOTE + one line.** Say `--dry-run` degrades to argv-only when `gh` is unreachable, or accept it explicitly in the plan. |
| **N15** `R`(F3) | `implementation_plan.md:198-203` · `test_door_preflight_order.py` | **LOW** | **Measured.** The test the plan correctly adopts as part of the change carries more than the ordering assertion: `REQUIRED_ORDER = (GATE_REF, CHECK_NAME, "mint-push-token.sh", "git push origin main")`, a `--delete gate/main-` assertion, a `flight_recorder.py`-before-gate-ref assertion, **three negative-control fixtures** (`PROSE_ONLY`, `COMMENT_ONLY_FENCE`, `MUTANT_WAIT_AFTER_MINT`) and a **separate `PROJECT_DOOR` assertion** over `/cicd-push-e2e`, which Part B does not change. AC-10 pins only "red before green"; a rewrite that satisfies AC-10 while dropping the negative controls leaves a guard that cannot fail. | **TIGHTEN AC-10.** Require the three mutant fixtures and the `PROJECT_DOOR` case to survive the rewrite unchanged. |

### First-cut findings: confirmed cleared

| Cleared | Evidence measured this turn |
|---|---|
| **F2** ✅ | `git -C <lane> diff origin/main -- .agents/rules/git-policy.md docs/_scc_sops_prds/workflows_testing_SOP.md` → **0 lines**. Full `diff --stat origin/main` shows only artifacts + the three memory files the lane is behind on. `git grep` for `--direct` / `direct-push-allowlist` over `.agents/` + `docs/` → **0 hits**; the only survivors are the lane's own plan, walkthrough and INDEX narrative (which is N8, an AC-scoping defect, not a revert defect). |
| **F6b** ✅ | Missing upstream after `--delete-branch` is now its own arm in R6, stated as *absence, not divergence*. |
| **F7** ✅ | The `run_gh` seam is named in Part A and in the Verification plan; `--dry-run` is redefined honestly. (Residual N14.) |
| **F8** ✅ | AC-6's row names **two concrete strings**, one per path — the URL on hand-back, `landed: PR #N · <sha>` on merge. That is testable by stdout assertion. The abstract sentence *"the actionable identifier is the last line"* is unfalsifiable **prose** and must not be the assertion text; the row beneath it saves it. |
| **F10** ✅ | The tick is number-free (`- [x] The merge itself — lands via this branch's PR`) and rides the branch. Measured that the requirement is real: `.agents/commands/smh-close-task-merge-tree.md:471` — *"⛔ Before `finish`: tick the merge row."* |
| **F11** ✅ | `sop_currency.classify('.agents/scripts/land_pr.py')` → **`the safety-net scripts`**. The plan's build-order statement is correct and AC-11 forbids `[sop-ok]`. |
| **F12** ✅ | Three-dot `origin/main...HEAD` named with its reason. Confirmed load-bearing: the lane is 3 files behind `b0fda44`, and the two-dot form would classify those. |
| **F14** ✅ | `.agents/scripts/INDEX.md` exists (21 rows); AC-14 pins the new row. |
| **F15** ✅ | `--json` is gone from the usage line and from every AC. |
| **F1, F3, F4, F5, F6, F9, F13** | **Partially cleared only** — see N1/N5/N6/N7, N15, N10, N4/N9, N2, N3, N13. |
| Also re-verified | `lane_qualify.TOOLKIT_PREFIXES` = `('.agents/', '.githooks/', '.github/', '_bmad/', '_bmad-output/')`; `classify()` signature is `(repo: Path, paths: list[str], no_file_changes: bool)`, so the plan's call is valid. Live repo merge methods: `merge:true, rebase:true, squash:true` — **Part C-1 is still needed and its claim holds**. |

**Sibling-lane landing order:** none. `origin/main` advanced `fdd6d75` → **`b0fda44`** (PR #8, SCC-186, three `_artifacts/_memory/` files) with **zero** overlap against this change set. One mechanical consequence: absorb `b0fda44` before opening the PR, or the lane's own two-dot diff reads as deleting three memory files.

### The four gates

1. **Verification strategy present?** ⚠ **Improved but still short.** RED-first, the `gh` seam, the pinned diff range and a mutation table that must include a `_is_prose`-widening mutant are all named and all right. But **AC-4's refusal half is vacuous** (N6) — it would pass against a predicate with no refusals in it — and AC-11 cannot pass at all as written (N8). A widening mutant is required; the mutants that actually matter (N1's nine front doors, N7's install guides) are not in the table.
2. **Anything irreversible?** ⚠ **Yes, and N1 widens it.** The `--merge` write to `main` is still the core irreversible act, and the file set it now admits includes every folder-level `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` under three prefixes — the routing law every platform reads on both machines. N4 adds a second irreversible road (`Bash(gh pr *)`) that the split does not gate at all.
3. **Any step vague enough that the builder will guess?** ⚠ **Yes.** Allow-vs-refuse **precedence** in `_is_prose` is unstated (N6); the mode-detection mechanism is unstated (N12); P's behaviour per PR state is unstated (N2); whether the two SKILL.md files are generated or hand-authored is stated **wrongly** (N10a).
4. **Convention fit?** ✅ **Good, and better than the first cut.** Stdlib `python3`, artifacts in-tree, no new command and no new doors, `smh-*` prefix carrying the right permission, the `scripts/INDEX.md` row added, the door sweep named. The remaining misses are N10b's five unnamed dependants and `jira_manual.md`.

### Per-item

| Part | Verdict |
|---|---|
| **A** `land_pr.py` | **NEEDS REVISION** — N1 (blocking), N2, N3, N5, N6, N7, N11, N12, N13, N14 |
| **B** the two-half close-out | **NEEDS REVISION** — N10, N15 |
| **C** the operator's acts | **NEEDS REVISION** — N4 (the `gh pr *` bypass), N3 (the dropped strict-checks act) |
| **D** law + SOP | **NEEDS REVISION** — N8 (AC-11 unscoped), N9 (the ticket still asserts the withdrawn claim), N10b (`jira_manual.md`) |
| **E** retire R1 | **✅ SAFE — verified by measurement.** Both halves are 0-line diffs against `origin/main`; the negative grep is clean over `.agents/` + `docs/`. |

### What could not be verified

- **⚠ UNVERIFIED — whether subprocess `gh`/`git` calls are visible to the permission layer.** F5's disposition ordered a throwaway experiment; it was not run then and was not run now. Forcing a denial in a non-interactive session hits the `ask` → auto-deny path, which would answer a *different* question. N4's disposition stands on the plan's own text, not on this.
- **⚠ UNVERIFIED — whether `/smh-sync-agents` regenerates the two 1,022-byte `SKILL.md` launchers.** Running the sync is a mutation and out of an audit's lane. Measured facts only: they are launcher-shaped, byte-identical across both caches, and carry a verbatim copy of the command's `description:`.
- **⚠ UNVERIFIED — `_is_prose` against git's quoted / octal-escaped paths.** No tracked path contains a space or a non-ASCII byte (measured: zero). A quoted path would fail the prefix test and refuse, i.e. **fail closed** — but that is reasoning, not a run.
- **⚠ UNVERIFIED — macOS case-insensitivity** (`Docs/x.md` vs `docs/`). Reasoned fail-closed; not measured.
- **Everything in Parts A–D is unbuilt**, so no runtime behaviour was observed. Every finding above is a defect **in the plan text**, which is the only artifact that exists.

```
Audit verdict: NO-GO
```

**Why NO-GO and not "GO with notes".** N1 is the third appearance of one defect: R1 shipped *"`docs/**` is not a prose tree"* and was reviewed **FAIL**; the first cut of R3 reproduced it through `lane_qualify` and was audited **CRITICAL** (F1); the fix for F1 reproduces it again through its own allowlist, and this time it admits the files that tell every agent on both machines what to read. The fix is genuinely small — refuse those three basenames at any depth, refuse `docs/migrations/` wholesale, and re-derive AC-4's refusal rows from paths arm 1 *would otherwise admit* so the test can kill a mutant. N2 and N3 are each a path that reads as success while nothing landed or while something stale landed, and N4 leaves a road around the very split this lane exists to make mechanical. All of them are cheap in a plan and expensive in a diff. Fix them, then re-run **Phase 1 and Phase 2 only** — Phase 0's scoping is settled and Phase 3's rows are unaffected.
