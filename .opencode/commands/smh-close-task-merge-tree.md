---
description: Close out TASK work — a `chore/<JIRA-KEY>-<slug>` branch that never got an epic and a story, so BMAD's `/cicd-update-sprint-memory` cannot close it. Preflights mechanically (branch shape, clean+pushed, main absorbed, and THE LANE — did anything deployable change?), runs the gate the lane selects, then OPENS A PULL REQUEST AND STOPS: it never merges. The operator's DECISION to proceed is the sign-off (the word approved, or invoking this command or /cicd-push-e2e); their click on Merge pull request is how that decision reaches GitHub, gated by the main-write-gate check. Re-invoked as `--after-merge <KEY>` it verifies the merge with plain git, files the Jira Dev Record, moves the Task to Done, and prunes the worktree AND the branch (SCC-62 — unlink assets before removing the tree; a recursive delete through a junction eats the shared targets). Refuses the moment a deployable path is in the diff and hands the work to `/cicd-push-e2e`.
platforms: [opencode, antigravity]
---

# /smh-close-task-merge-tree — Close a Task, Merge It, Prune the Tree

> **Rules in force for this command:**
> - `.agents/rules/worktree-per-story.md` §"cwd is not intent" — why every repo/branch below is
>   pinned from command output; with sibling lanes (and their worktrees) live, where you stand is
>   not evidence of what you mean
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never
>   force-push; every branch and every commit carries the repo's Jira key (armed 2026-08-07)
> - `.agents/rules/jira.md` — the `acli` reference, and the work-item type model this lane sits in
> - `.agents/rules/work-consolidation.md` — the `riders:` / `landing_mode: partial` contract this Step 4
>   settles: one lane may carry a whole Task's subtasks, and they flip here, parent last (SCC-170)
> - `.agents/rules/artifacts-always-first.md` — the plan is skippable on this lane; the closing
>   `walkthrough.md` is **not**, and the preflight blocks without it

**The Task lane's close-out.** The story lane ends at `/cicd-update-sprint-memory`, which reads a
sprint board, flips a story status and lands on an epic branch. **Task** work has none of those —
no epic, no story file, no board row, often no board at all — so that command has nothing to
operate on. This is the missing half: the same close-out obligations (record what was learned,
move the ticket, land the code, prune the branch) for work organised as a Task.

> **Story or Task?** One rule, one implementation — `jira_feed.py work_type()`, documented in
> `.agents/rules/jira.md` §Work-item types. **Story** = BMAD sprint work (a dotted number, a
> `debug-` marker, or a story file). **Task** = workflow / IDE / rules / skills work, filed under
> a grouping epic. If the work has a story, it does **not** come here.

**Why this command is `smh-*` and not `cicd-*`.** Every `/cicd-*` command binds
`smh-target-resolution.md` — *"operates on exactly ONE target — never the lobby."* Task work is
mostly toolkit work, and toolkit work lives **in** the command centre. So this belongs to the
`smh-*` family (`/smh-sync-agents`, `/smh-update-maps-indexes`, `/smh-new-project`) — the one that
is allowed to act on the repo you are standing in. The prefix is the permission; it is not cosmetic.

## 🛑 MANDATORY RULES (before you start)

1. **⛔ THIS COMMAND DOES NOT MERGE TO `main`. It opens a pull request and stops.**

   **⭐ THE SIGN-OFF IS THE OPERATOR'S DECISION TO PROCEED, and it is given in exactly one of three
   ways: the word `approved`, or invoking `/smh-close-task-merge-tree`, or invoking
   `/cicd-push-e2e`** (operator ruling, 2026-08-17, verbatim: *"its my decisiton to move forward
   with the push, is the wording that will stop causing confusion. the way I approve you to push or
   close is by saying approved or one of the 2 / commands."*). **From that word on, every step is
   the ceremony's and the agent runs it** — this command, the click's paperwork, `--after-merge`,
   the Dev Record, the transitions, the prune. ⛔ **The merge is never a task the operator owes, and
   never an open box in `## Your Actions`.**

   **The mechanism is unchanged, and that is also the operator's word** (asked which of two
   readings, 2026-08-17: *"i wording only"*). The **click** on *Merge pull request* stays a
   physical operator act — it is **how the decision reaches GitHub**, not work assigned to them.
   An agent still cannot press it, on any machine or platform, because the button is on GitHub.

   That physical step is *stronger* than a sentence in a file, which is why it stays. A **document**
   saying the sign-off happened sits in an agent's context and still reads as valid on task six —
   exactly how one invocation rode six merges (SCC-71), and how "you can move it to done" was once
   read as merge permission (SCC-37; ticket-status permission is **never** merge permission).
   **One decision, one merge.**

   So: if you reach Step 3 and the PR is not merged yet, the correct state is **waiting** — report
   the link and stop. ⛔ Never offer a way to land it without going through that PR.
2. **The preflight is not advisory.** Exit 2 STOPS the command. Report what failed; never "merge
   anyway", and never re-run it with the failing check worked around.
3. **The lane is not yours to choose.** `LANE: HANDOFF` means a deployable path is in the diff.
   That is not a task, whatever the ticket says — STOP and hand it to `/cicd-push-e2e`. There is no
   override flag, deliberately.
4. **Clear GITHUB_TOKEN on push/pull**: prefix with `$env:GITHUB_TOKEN = ""` (PowerShell) or
   `env -u GITHUB_TOKEN` (Bash) to prevent stale-session auth failures.

## Step 0 — Resolve the repo (FIRST) — from command output, never from belief

The repo is **where you are standing**, not a project pointer. If `$ARGUMENTS` names a folder under
`Projects/` or a path, use that; otherwise the current repo. Do **not** read
`.agents/active-project.txt` — this command's whole point is that the command centre is a
legitimate target.

**Resolve it mechanically and pin it in a variable.** `cwd` is not intent: it resets to the shared
checkout at slash-command boundaries, and the preflight finds its repo by walking *up from cwd*
looking for `.git`. Run these and read the answers:

```bash
REPO=$(cd "<the path you resolved>" && git rev-parse --show-toplevel)
BRANCH=$(git -C "$REPO" rev-parse --abbrev-ref HEAD)
echo "Repo: $(basename "$REPO") | Branch: $BRANCH"
```

Then pin **the Jira key you intend to close** — the one from the ticket, not the one you read off
the branch. Keep both; Step 1 makes the script compare them:

```bash
EXPECTED_KEY="SCC-00"    # the ticket you MEAN, stated before any tool has answered anything
```

**Author the task manifest if the task never got one.** `task.yaml` sits in the task's
`_artifacts/_main/<date>_<slug>/` folder and is intent written down where no cwd drift can reach
it — the preflight cross-checks it and warns when it is missing:

```yaml
task_key: SCC-00
primary_repo: <repo folder name>
branch: chore/SCC-00-<slug>
close_command: smh-close-task-merge-tree
secondary_repos: []        # single-repo task — the common case
```

**Cross-repo?** Then `secondary_repos` takes the block form instead — **replace** the `[]` line, never
leave it above a second one:

```yaml
secondary_repos:
  - repo: Projects/<name>
    landing: independent-task      # or retain-on-epic
    ticket: KEY-00
```

Cross-repo work: each `secondary_repos` row is **its own ticket in its own repo** closed through
its own lane — `landing: retain-on-epic` records the exception where a commit stays on a live epic
branch and must never be presented as merged to production.

⛔ **Since SCC-94 these rows are ENFORCED, not just recorded.** For every row, the preflight blocks
unless that repo is reachable, its declared ticket key is one that repo's own `jira.conf` answers
to, it is clean and `0/0` with its origin, and its memory store passes the same integrity contract
the lobby's does. Two consequences worth knowing before you write the row:

- **The lobby cannot see a dirty project half.** Submodules are `ignore = all`, so this repo's
  `git status` is clean no matter what state the project is in. This check is the only thing that
  looks.
- **A wrong key is caught here, not at the commit.** A project answering only to `AVCH` rejects an
  `SCC`-keyed commit at its hook; declaring the wrong one used to surface after the work was done.
- The inline `[{…}]` form is **not read** — it warns and verifies nothing rather than failing open.
  Use the block form.

⛔ **Echoing `Repo | Branch` from memory defeats the only guard here.** The line exists to catch a
wrong belief about where you are standing; a self-reported echo can only ever confirm the belief.
It must come from the commands above.

## Step 1 — Preflight (mechanical — one call answers every precondition)

**`--expect-key` is required — the script refuses to run without it (SCC-64).** This is the
machine half of Step 0: the preflight now blocks, mechanically, when the resolved branch does not
carry the key you pinned — a cwd that drifted into a sibling's lane fails the key match instead of
returning a clean verdict about the wrong branch. Still pass `--repo` and `--branch`: they are
written as optional because the script can guess, and the guess is exactly what fails when a
sibling lane has moved the shared checkout.

```bash
python3 .agents/scripts/task_preflight.py --fetch --repo "$REPO" --branch "$BRANCH" --expect-key "$EXPECTED_KEY"
```

**⭐ It FETCHES by default now (SCC-193), and it LEAVES A RECEIPT (SCC-192).** Two things follow,
and both are mechanical:

- **`--fetch` is the default.** `--no-fetch` is the offline opt-out and the VERDICT line then says
  the comparison is **stale**, with a non-zero exit — because on 2026-08-16 this ran without a
  fetch, the note saying so was an `INFO` under a verdict reading *clear to close out and merge*,
  and that verdict is the only line an agent acts on. A `stale` verdict is not a clear one.
- **It writes `preflight-receipt.json`** beside this lane's `task.yaml` — the key, the branch, the
  flags it actually ran with, the verdict and its exit, keyed on the walkthrough's verdict sha.
  **Commit it with the flight event at Step 2.5** (the block there stages it). ⛔ **`main-write-gate
  --mode pr` REFUSES the PR without it** — that receipt, plus the flight event, is the only way the
  system can tell this ceremony was RUN rather than narrated. Do not pass `--no-receipt`; it exists
  for probes and harnesses.

🛑 **Read the header line before you read the verdict.** It echoes the branch the script actually
resolved:

```
== task preflight - chore/<JIRA-KEY>-<slug> ==
```

If that key is not the key you named in Step 0, **STOP** — you are pointed at another lane. Say
which branch it resolved and which you meant; do not re-run it hoping for a different answer, and
never merge on a verdict whose header you did not check. (2026-08-09: this resolved a sibling's
`chore/*` branch mid-close-out and returned a clean verdict; merging it would have put another
lane's in-flight work on `main` under the wrong ticket. The script cannot catch this — it has no way
to know which ticket you meant.)

It answers, from the repo rather than from your memory of it:

| Check | What a failure means |
|---|---|
| **branch** | `chore/<JIRA-KEY>-<slug>`, key immediately after the prefix, key matches `.agents/jira.conf`. An `epic/`, `claude/incident-` or `claude/` branch is refused **by name, with the command that IS right** — scanned in that order, the specific incident prefix before the generic story one (SCC-148: a bare `incident/` entry no command creates once shadowed the real shape, and a live incident branch was routed to the story close-out). An unclassifiable shape falls to the generic `chore/…` refusal. |
| **intent** | the branch's key equals `--expect-key`. A mismatch means the preflight is aimed at **another lane's branch** — the 2026-08-09 failure, now a mechanical exit 2 instead of a prose warning. |
| **manifest** | a `task.yaml` declaring this `task_key` agrees on the branch. Missing manifest = warning (author it, Step 0); a manifest naming a **different branch** = error — one of them is lying. |
| **sync** | clean tree, `0/0` with origin. Merging an unpushed branch puts commits on production that exist on one disk. Dirty files under `_artifacts/_memory/` are named separately: another session's memory is **parked or left, never swept, deleted, or committed under this task**. |
| **base** | `origin/main` fully absorbed, and ≥1 commit ahead. Conflicts must surface **here**, never on `main`. |
| **scope** | ⭐ **THE LANE.** See below. |
| **artifacts** | a `walkthrough.md` mentioning the key exists. Without it the Dev Record cites nothing. |
| **worktree** | the worktree checked out on this branch — **expected** since SCC-62, and Step 5 prunes it. It blocks the branch delete until removed, so the order in Step 5 is not optional. |

**⭐ The lane, and why the E2E answer is mechanical.** The one thing that makes this command
cheaper than `/cicd-push-e2e` is skipping the end-to-end suite, and the only honest justification is
*nothing that deploys changed*. That is precisely the claim an agent is worst at auditing about its
own work, so the script derives it and prints it as `LANE:`:

- **`LOCAL`** — either the repo has **no deployable surface at all** (no `backend/`, `frontend/`,
  `firebase/`, `functions/`, `mobile/`, `.github/` — the command centre's case, and exactly what
  `git-policy.md` means by *"it has no E2E suite and never will"*), or the repo deploys but this
  diff touches none of those paths. **There is no E2E gate to skip.** Proceed.
- **`HANDOFF`** — a deployable path is in the diff. **STOP.** Print which one, and say: *this is a
  product change, and the product has one road to `main` — `/cicd-push-e2e`.* Leave the branch
  exactly as it is; nothing here is undone.

Exit 2 → stop and report. Exit 1 (warnings) → read them; a "never pushed" warning in particular
means Step 3 would merge something no other machine has.

⭐ **A `landing:` STALLED LANDING error is about `main`, not about your lane (SCC-159).** Local
`main` is ahead of `origin/main`, so an earlier close-out merged and never pushed — and every lane
behind it, this one included, queues invisibly. Nothing else catches it: Step 3's
`git pull --ff-only origin main` **succeeds silently when local is merely ahead**, and the `0 0`
check runs only after the push. Land or inspect that commit first. Offline — the operator pushes
from planes, where reads succeed while pushes die mid-upload — `--accept-unpushed-main` is the
auditable way through: it downgrades this one check to a warning and prints itself back into the
output, so the record shows it was used.

## Step 2 — Run the gate the lane selected

The preflight prints the exact commands under `gate:`. Run them and **paste the real output** — a
gate reported from intent is the failure this whole toolkit exists to remove.

**⭐ The preflight is also the ONLY thing that may skip this gate (SCC-146).** When the review
verdict is `PASS`/`CONCERNS` at a code-fresh sha, the tree is clean, and the lane's receipts
(`<task-artifacts>/gates/*.json`) all validate, it replaces the **suite entry only** with one line:

```
gate: SKIP - verdict PASS @ <sha>, receipts valid (suite, ...)
gate: python3 .agents/scripts/workflow_lint.py --toolkit-only
gate: python3 .agents/scripts/check_maps.py --depth3-only --strict
```

**A SKIP spares the SUITE only (SCC-154).** The artifact-scoped checks still print and still run:
every SKIPping lane structurally carries at least one post-verdict `_artifacts/` commit the suite
receipt never inspected (the stamp cannot cite the commit it rides in), and map/INDEX drift is
exactly `_artifacts/`-borne. Paste the SKIP line for the suite, then run the remaining printed
commands as normal. Three hard edges: **you never decide a skip by reading the walkthrough
yourself** — commands printed means commands run, all of them; **only the walkthrough beside this
task's own `task.yaml` can grant it** — foreign or substring-matched walkthroughs neither grant nor
block (SCC-154); and **a FAIL verdict is a preflight exit 2**, which Step 1 already stopped on — a
lane whose review said FAIL does not reach this step, let alone the merge.

When the commands do print, in the command centre that is:

```bash
python3 .agents/scripts/tests/run_all.py        # the enforcement suite — must be N/N files passed
python3 .agents/scripts/workflow_lint.py        # lint — the preflight prints the exact flags
```

**Run the lint with exactly the flags the preflight printed.** In the lobby that is
`--toolkit-only` (SCC-64); in a repo with a deployable surface it prints the bare, full-scope run.
Where the flags differ from the review's `--toolkit-only` run, that is a **different scope, not
duplication** — keep both runs and do not "clean up" the wider one into the narrower.

Plus, because task work is almost always **docs and rules**, the two checks `/cicd-quick-dev` Step 3
runs on a docs-only diff:

- **Link + anchor check** on every path and `#L` anchor the diff touched.
- **SOP currency** — a usage-surface change (`.agents/commands/`, `.agents/rules/`,
  `.agents/scripts/`, git hooks, root `AGENTS.md`) must have moved
  `docs/_scc_sops_prds/workflows_testing_SOP.md`. The armed commit-msg gate already
  enforced this per commit, so a surprise here means a commit was made with `--no-verify` or
  `[sop-ok]` — say which.

⭐ **When the verdict is code-fresh, CITE those two instead of re-walking them (SCC-156).**
`/smh-code-review` Step 3 ran both against this same diff, and if nothing outside `_artifacts/` has
changed since the verdict sha — the condition the preflight already computed for the SKIP — then the
diff they walked *is* the diff landing. Print which review run they came from and move on. This is
the same fail-toward-running rule the suite receipt follows: **cite only under code-fresh; if any
non-artifact file moved, walk them again.** Two live nets remain either way — the armed `commit-msg`
gate refused any SOP-less usage-surface commit as it was made, and CI re-checks at the landing sha.

Any failure → **STOP**. Fix it on the branch and re-run; do not carry a red gate into a merge.

⛔ **This gate is MECHANICAL only — never re-run the LLM review here.** The lane's review already
happened and stamped `Verdict: … @ <sha>` in the walkthrough; that verdict STANDS for that sha, and
this step's job is only to prove the deterministic gates are green at the landing sha. The review
engine is recall-first with no noise filter **by design**, so re-running it on anything — including
its own fixes — will always surface new findings, and "review until zero findings" is a loop that
never terminates (SCC-147, observed live: a re-review at close-out produced five fresh findings on
a lane already at PASS). If new findings somehow exist anyway, triage them by severity instead of
looping: `suggestion`/`nitpick` → record and proceed (a `defer` here still names its structural
blocker, or it is a patch); only a `critical`/`important` in `decision_needed` or `patch` stops the
merge — and it is fixed in this lane before the merge, never carried out of it.

## Step 2.5 — Record the flight event (pre-merge, artifacts-only) — SCC-133

The lane's evidence is about to be merged and forgotten. Record it **now, in the worktree, before
the merge** — the recorder writes one small file keyed on the walkthrough's `Verdict: … @ <sha>`
sha, and that file rides the merge like a receipt does:

```bash
python3 "<worktree>/.agents/scripts/flight_recorder.py" record --task <JIRA-KEY> \
        --root <task-artifacts folder> --repo "<worktree>" --apply      # PC: `python`
# Commit ONLY when it wrote something: on "already recorded" (a resumed close-out) or a
# refusal there is nothing staged, and a bare `git commit` would exit 1 for no reason.
# The preflight receipt (SCC-192) rides the SAME commit - it is the other half of the
# evidence main-write-gate --mode pr requires, and a second artifacts-only commit buys nothing.
# ⛔ THE GUARD AND THE ADD MUST SEE THE SAME PATHS. `git status` tolerates a pathspec that
# matches nothing (exit 0, empty); `git add` does NOT - it exits 128 and stages NOTHING, so the
# flight event never gets committed either and the PR gate then refuses for a MISSING EVENT.
# That is reachable whenever the receipt was not written: no live manifest, two manifests
# (the preflight now errors on that), `--no-receipt`, or an unwritable tree. Build the list
# from what exists, then guard and stage the SAME list.
PATHS=()
[ -d "<worktree>/_artifacts/_main/workflow-events" ] && PATHS+=(_artifacts/_main/workflow-events/)
if [ -f "<worktree>/<task-artifacts folder>/preflight-receipt.json" ]; then
  PATHS+=("<task-artifacts folder>/preflight-receipt.json")
fi
# ⛔ `[ -f … ] && PATHS+=(…)` returns 1 when the file is absent, which ABORTS the snippet under
# `set -e` - so the guard meant to survive a missing path became the thing that killed the step.
# The events dir is conditional too: it is tracked in this repo, but on first adoption of this
# door (or a lightweight lane that recorded none) it does not exist, and `git add` 128s on a
# pathspec that matches nothing - staging NOTHING, so the flight event is lost with it.
if [ ${#PATHS[@]} -gt 0 ] && git -C "<worktree>" status --porcelain -- "${PATHS[@]}" | grep -q .; then
  git -C "<worktree>" add -- "${PATHS[@]}"
  git -C "<worktree>" commit -F <msg>   # "<KEY> chore(recorder): flight event @ <sha7> [sop-ok]"
  git -C "<worktree>" push
fi
```

The script path is anchored on **`<worktree>`**, not the cwd — the door's cwd is the shared
checkout, and the lane that ships a recorder change (this one included) does not have that
change on `main` yet.

**Why here and not after the merge:** after Step 3 the only tree that has the merge is `main`'s,
and a file written there is either left untracked or committed straight onto `main` outside the
token you just spent — the exact write the gate refuses. Pre-merge, it is one more artifacts-only
commit, which the SKIP machinery already ignores (freshness is content-based). **Idempotent:** a
resumed close-out prints "already recorded" and writes nothing — the key is the verdict sha, not
HEAD, precisely so this commit does not create a second event on re-run.

**What it records and what it does NOT do (SCC-160):** the verdict sha, the lane's changed files,
the receipts by gate, and the walkthrough's decisions / pitfalls / follow-ons — the same buckets
the Dev Record posts — plus four mechanical fingerprints (a rules file rewritten · a red receipt ·
a non-PASS verdict · a script or command named in a pitfall). Recurrence across lanes climbs a
ladder (1 evidence · 2 candidate · 3+ action-required) that SessionStart and `/cicd-boot-sprint-memory`
**surface as proposals** — never as owed work, never as a minted ticket. `flight_recorder.py
candidates` prints the whole ladder any time. **A `record` failure never blocks the merge** — report
it like a failed receipt and carry on; nothing downstream depends on it.

## Step 3 — Hand back the link

### ⛔ Everything Step 4 will demand of `walkthrough.md` must be committed ON THIS BRANCH, NOW

Step 4 runs **after** the merge, so anything it finds missing forces a **post-merge commit** — which
is precisely what the gate refuses, and what SCC-175 is. Both of these are cheap here and expensive
five minutes later. Check both **before** opening the PR:

| Required | Why here, not later |
|---|---|
| `- [x] The merge itself — lands via this branch's PR` | **Number-free on purpose** — the PR number is assigned when the PR is opened, which is *after* this commit is pushed. The number and merge sha go on the ticket in Step 4, where both are known |
| a `## Your Actions` section, **even if it says nothing is owed** | `jira_feed.py finish` **refuses to close without it**: an absent section is not evidence that nothing is owed, so the answer must be recorded rather than assumed |

```bash
grep -q "The merge itself" <walkthrough> && grep -q "^## Your Actions" <walkthrough> \
  || { echo "walkthrough incomplete — fix it BEFORE the PR"; exit 1; }

# ⭐ SCC-193 · the CONTENT of that section, not just its presence. Refuses a row handing the
# operator ticket work (SCC-163) or the ceremony's own steps (SCC-193) - "click Merge",
# "re-invoke the door", "run --after-merge". HERE, before the PR, is the only place fixing
# either costs nothing: the same refusal fires again at Step 4's `finish`, which runs AFTER
# the merge, when the walkthrough is on `main` and the fix is a commit the gate refuses.
python3 .agents/scripts/jira_feed.py check-actions --walkthrough <walkthrough> \
  || { echo 'fix `## Your Actions` BEFORE the PR - it will refuse the close-out otherwise'; exit 1; }
```

⭐ **Both of these are measured failures, not hypotheticals.** On 2026-08-16 `jira_feed.py finish`
held SCC-184 at `Review Required` over the unticked merge box on a merge that had already happened —
and then held **SCC-183 itself**, at this very step, over a missing `## Your Actions`. The second one
was found by this lane landing through its own door, which is the only reason it is written down
here instead of being rediscovered by the next task.

The branch is already on `origin` — Step 1's preflight requires clean **and** pushed. So:

```bash
gh pr create --base main --head "$BRANCH" --fill
```

`--fill` builds the title and body from the commits, so nothing has to be re-typed. **The last line
it prints is the PR URL.** Print it and **STOP.**

**No `gh` on this machine?** Nothing is blocked — the branch is pushed, so the PR can be opened in
the browser. Build the URL from command output, never from memory:

```bash
git -C "$REPO" remote get-url origin      # -> the owner/repo
# https://github.com/<owner>/<repo>/compare/main...<BRANCH>?expand=1
```

Print that instead. One extra click for the operator, and this door needs no tool the machine does
not have.

⛔ **STOP means stop.** Do not merge it another way, do not mint a token, do not offer to. **The
operator's decision to proceed is the sign-off, and the click on *Merge pull request* is how it
reaches GitHub.** A link nobody has merged is not a merge running late — it is a merge that has not
been authorised. Waiting is correct behaviour, on every platform, on either machine.

**What guards the merge is on GitHub, not here.** `main` requires a green **`main-write-gate`**
check on the PR — the same enforcement suite, plus a check that the source is an `epic/*` or
`chore/*` branch carrying a real ticket key. GitHub refuses the merge button until it passes,
whoever opened the PR, from whatever machine, through whatever agent. That is the whole reason this
door needs no local token: **a merge performed on GitHub never touches a machine here**, so there is
no local push for a hook to gate — the token is *structurally absent, not bypassed* (SCC-118's own
finding). If the check is red, **STOP** — never disable the ruleset to get past it.

> ⓘ **Why this replaced ~15 hand-typed git/gh commands (SCC-183).** SCC-184 — docs only, every gate
> green, suite 32/32 — could not reach `main` in a full session. No gate stopped it. The *landing*
> did: each of those strings was judged separately by the agent's permission layer, several were
> denied, and the state was left stranded halfway. Measured, same op and same target:
> `git merge X --no-ff` **allowed**, `git -C <path> merge X --no-ff` **denied** — and `-C` is what
> `.agents/rules/nothing-guards-the-merge-target.md` *mandates*. Obeying the safety law guaranteed
> the permission miss. `gh pr create` has none of that: it is one command, it needs no checkout on
> `main`, it writes nothing on this machine, and it is what actually landed PR #5, #6 and #8.

### Resuming after the operator's click

When Step 3 handed back a link, the close-out is **paused, not finished**. Once the operator has
merged, re-invoke it to run Steps 4–6 only:

```bash
/smh-close-task-merge-tree --after-merge <JIRA-KEY>
```

It verifies the merge with plain git — no `gh` required, so this half works on any machine:

```bash
env -u GITHUB_TOKEN git -C "$REPO" fetch origin main
git -C "$REPO" merge-base --is-ancestor "$BRANCH" origin/main || { echo "NOT merged yet — STOP"; exit 1; }
git -C "$REPO" log -1 --format=%s origin/main        # -> "Merge pull request #N from ..."
```

The PR number comes off that merge subject; the merge sha is `git -C "$REPO" rev-parse --short
origin/main`. Both go in the Dev Record at Step 4.

**⛔ AND CHECK THAT THE DOOR YOU ARE READING IS THE CURRENT ONE (SCC-193 C).** This is the one
command most likely to be reading a file its own lane just changed — on 2026-08-16 an agent
followed an instruction its lane had **deleted**, because `git fetch` had been run and the working
tree never pulled:

```bash
BEHIND=$(git -C "$REPO" rev-list --count HEAD..origin/main)
```

If `BEHIND` is not `0`: ⛔ **this checkout is behind origin/main by N; the door text you are
following may be the PRE-merge copy.** Read the current one before Step 4 —
`git show origin/main:.agents/commands/smh-close-task-merge-tree.md` — and follow that.

⛔ If the ancestor check fails, **STOP** — the ticket does not move and no Dev Record is filed. A
close-out that reports `Done` on an unmerged PR is the same lie as one that reports it on a failed
merge. ⛔ The `--is-ancestor` check is also why `/smh-close-task-merge-tree` needs squash and rebase
merges **disabled** on the repo: either rewrites the commit, so the branch tip would not be an
ancestor of `main` and a real landing would read as a failure.

## Step 4 — File the Dev Record, then move the ticket

**After the merge, never before.** A ticket that reads `Done` while the merge failed is a lie on the
board; a merge that landed while the record lags is one command away from correct. Take the
recoverable failure.

> ⭐ **Before you write `Done`, settle the children (SCC-119 · riders SCC-156).** If this ticket is a
> **parent**, it closes **LAST** — the whole job closes together at the end, so a parent going `Done`
> over open subtasks is exactly the lie above, one level up.
>
> ```bash
> acli jira workitem search --jql "parent = <JIRA-KEY>" --fields "key,summary,status"
> ```
>
> **Riders close first, and YOU close them.** A subtask listed under `riders:` in this lane's
> `task.yaml` did its work IN this lane — the merge that just landed is its work too. For each
> declared rider that is still open **and appears in the search above**:
>
> ```bash
> acli jira workitem transition --key <RIDER-KEY> --status "Done" --yes
> ```
>
> This is an **agent step inside the ceremony the operator's word invoked** — the operator acts in
> words, never in board edits. A declared rider that is *not* a subtask of this parent is a
> declaration error: flip nothing, report it. Never transition a ticket whose work did not actually
> land here.
>
> After the riders: any **undeclared** child still not `Done` or `Deferred` → **STOP.** Finish it, or
> descope it properly (`Deferred` + the `descoped` label — that is the auditable escape, and the reason
> there is no `--force` flag). That exit is for children **nothing declared**; a declared rider is the
> designed state, not an unfinished job.
>
> ⭐ **PARTIAL LANDING — the lane ships before every part is built (SCC-170).** A consolidated lane
> carrying N subtasks may have to land early. That is legal, and it is **declared, never improvised**:
>
> 1. **Trim `riders:` in `task.yaml` to the subset whose work is actually on this branch** — and
>    commit that trim on the lane, before the preflight. `task_preflight.py` checks every declared
>    rider against the lane's commits and refuses one that leads no commit here. *Never declare a
>    ticket whose work is not real.*
> 2. **Add `landing_mode: partial`** to the same `task.yaml`. Without it an open undeclared child blocks,
>    exactly as it always has — the mode is a thing you say, and an unrecognised value fails CLOSED.
> 3. **The trimmed riders flip** as above. **The PARENT STAYS OPEN** — do not transition it, and do
>    not treat the preflight's partial-landing warning as noise.
> 4. **The remainder becomes the next lane**: name every left-behind child in this walkthrough's
>    `## Your Actions` and in the next lane's `task.yaml` `riders:`. The parent closes at *that*
>    lane's ceremony, when the last child does.
>
> ⛔ **If this command ever leaves the operator a Jira edit to do by hand, the flow is broken —
> stop and say so.** Not "please move SCC-00 to Done and re-run": the agent performs every board
> write, always inside this ceremony. A hand-back that assigns the operator data entry is a bug in
> the flow, never an instruction to relay.
>
> **This is a second layer, not a duplicate.** `task_preflight.py check_children()` already ran at
> Step 1 — it blocks on open undeclared children and WARNS each declared rider with the exact
> transition above — but it **warns rather than blocks when the board is unreachable**, and a
> sandboxed shell cannot reach the credential store at all. This step runs where the board is
> provably reachable, because the very next command transitions the ticket. Neither layer is
> load-bearing alone — the same shape as the two `start` seams (SCC-113).
>
> ⛔ A **`Subtask`** closes here exactly like a `Task` — its own branch, its own gate, its own
> `Done` — **whenever it ran as its own lane.** When it rode a consolidated lane instead (the
> default when able, per `work-consolidation.md` rule 2), it is a `riders:` entry in that lane's
> `task.yaml` and closes in the rider step above, right before its parent. Both are normal; the
> manifest says which happened, and it is the only thing that does. Either way it is never labelled `Bug` — if it turns out broken, the flag goes
> on its **parent**.

```bash
python3 .agents/scripts/jira_feed.py devrecord --key <JIRA-KEY> --project "$REPO" \
       --stage close-out --walkthrough <the walkthrough> \
       --outcome "merged to main at <merge-sha> via /smh-close-task-merge-tree" \
       --verdict "<gate result>" \
       --decision "<a ruling made while doing it>" \
       --pitfall "<what nearly bit>" \
       --followon "<anything still owed>" --closing --apply

python3 .agents/scripts/jira_feed.py finish --key <JIRA-KEY> \
       --walkthrough <the walkthrough> --apply
python3 .agents/scripts/jira_feed.py check --key <JIRA-KEY> --project "$REPO"   # must exit 0
```

⛔ **`--project "$REPO"` is REQUIRED on both.** Both subcommands resolve their repo by walking up
from **cwd**, and cwd is not intent — it resets to the shared checkout at slash-command boundaries,
and that checkout is on whatever branch the operator left it on. `devrecord`'s slug default reads
the branch you are standing on; land on a branch with no `/` (like `main`) and the lane slug comes
back empty, so the command dies with *"devrecord needs --story"* **after the merge has already
landed**, and the recovery it prints is the free-text `--story` this part exists to eliminate.
`$REPO` is the lane worktree Step 0 pinned; it is still on the lane branch until Step 5 prunes it,
so it is the one tree that can answer. ⛔ **Never `checkout` anything to make this work** — no
command here may change which branch a checkout is on. The operator uses those checkouts.
The same applies to `check`: without it, a FORK verdict is computed against whichever repo cwd
happened to be in, and the message never names the repo it read (`preflight-resolves-repo-from-cwd`).

⛔ **No `--story` here, and that is the fix (SCC-174).** `devrecord` picks update-vs-create off the
**slug**, never off `--key`, so the same lane spelled two ways posts a **second** Dev Record — and
this ceremony asking for `<branch-slug>` while `/smh-quick-dev` filed under something shorter is
exactly how AVCH-59 ended up with two. The slug now comes from **one** place, the lane's `task.yaml`
`branch:`, and the script reads it. Pass `--story` only to file under a lane you are **not** standing
on. If `check` reports a **FORKED Dev Record**, an id on the ticket is claimed by no manifest and no
branch: delete that record and re-run this block — never `--append-new` your way past it.

⛔ **Do NOT tick the merge row here, and do not commit anything after the merge.** This step used to
say the opposite, and that instruction was the whole of SCC-175: it produced a non-merge commit on
`main` that the write gate correctly refused, and the refusal banner's `reset --hard` remedy then
destroyed three other sessions' uncommitted work (SCC-180). **Two changes removed the need entirely:**

| Since | What handles it |
|---|---|
| **SCC-183** | Step 3 requires `- [x] The merge itself — lands via this branch's PR` committed **on the lane, before the PR opens**. By the time you are here it is already ticked, already on `main` |
| **SCC-175** | `finish` no longer reads that box as prose. It **computes** the answer: is the lane's tip an ancestor of `origin/main`? A row naming a merge door (`/smh-close-task-merge-tree`, `/cicd-push-e2e`) or carrying the canonical phrase is satisfied **only** by that check |

⭐ **So a tick can no longer close a ticket on its own** — which is the point, not a side effect. A
`- [x]` is a claim, and `finish --apply` writes `Done` to Jira on the strength of it; unverified, that
is the agent certifying its own merge. It now reads the row from **`HEAD`**, not the working tree, so
an uncommitted tick satisfies nothing (SCC-169's tick was left uncommitted and later wiped by a
reset). If the lane genuinely has not landed, `finish` re-opens the row and says so. **Every other
open box stays exactly as it is — those are the operator's to DECIDE.** ⛔ And since SCC-193 an open
box that hands over *the ceremony's own steps* — "click Merge", "re-invoke the door",
"run `--after-merge`" — is **refused** by `finish` and by `check-actions`: from the operator's word
on, those are yours to run, not theirs to do.

⭐ **`finish` writes the `Done`, and it may refuse to (SCC-155).** It reads `## Your Actions` in the
walkthrough you just filed and answers with its exit code — **read it, it is the report:**

| Exit | Means | What you report |
|---|---|---|
| `0` | the section had nothing open → the ticket is **`Done`** | closed |
| `3` | **HELD** — open `- [ ]` items were posted to the ticket as a "User tasks" comment, the `user-tasks` label added, and the review-status ladder tried | **"merged and awaiting you"**, listing the items. Not a failure — the merge landed |
| `2` | **refused** — no walkthrough, or no `## Your Actions` section. Nothing was written | fix the artifact and re-run; never transition by hand instead |
| `4` | the board was unreachable — transport, not a verdict | the merge stands; retry the ticket move |

**Why the ticket can be held:** a walkthrough that hands the operator work ("install the board
column", "run the memory audit") used to close as `Done`, and the record of what was still owed
died with the lane. **The auditable exit is the checkbox** — when the operator finishes an item they
flip it to `- [x]`, commit that (an artifacts-only commit), and re-run `finish`. There is no force
flag, deliberately: a gate with no legitimate exit gets worked around, and this one's exit leaves a
trail.

⛔ **Do NOT fall back to a hand-written `acli … transition` to `Done` when `finish` exits 3.**
That is the exact behaviour it replaces, and it writes a lie onto the board.

⛔ **`--yes` or acli stops on an interactive confirm no agent shell can answer.** This shipped
without it until SCC-113; `Done` was landing on luck. `finish` passes it on every transition, and
`tests/test_jira_feed.py` fails if any `workitem transition` under `.agents/` omits it.

**Exactly one Dev Record per ticket.** If `/cicd-quick-dev` already filed one at Step 4.5, this
**updates it in place** — **never pass `--append-new`.** `devrecord --apply` reads the ticket back
and exits 2 if the comment is not there, so a non-zero exit means the record did **not** land:
report that, do not report success.

**`--closing` clears a `Bug` flag, and this lane needs it.** A ticket arrives here typed `Bug` when
something found it broken and pulled it back out of `Done` — an audit that traced a live bug to it,
or the operator by hand. The fix you just merged IS that bug, so the type goes back to **`Task`**,
which is what the rule says this ticket is. It restores whatever `work_type()` computes, never
always `Story` — the first cut did that, and it stranded every flagged Task as a permanent `Bug`
because nothing else in the system can clear one. On a non-`Bug` ticket the flag is a silent no-op,
so it is always safe to pass.

No ticket key at all → say so in the report and skip both calls. **Never invent a key.**

## Step 5 — Prune the worktree, THEN the branch

Since SCC-62 every commit-producing lane runs in a worktree, so a Task lane owns one by default — and
**this command prunes it.** That is what lets ad-hoc work isolate at all: the old ban on chore worktrees
existed only because nothing cleaned them up. The lane that opened the tree is the lane that closes it.

**Order matters, and getting it wrong is destructive.**

```bash
# 1. UNLINK the gitignored assets FIRST — before anything is deleted.  (PC: `python`, not `python3`)
python3 .agents/scripts/link-worktree-assets.py --unlink .claude/worktrees/<slug>

# 2. Now remove the tree.
git worktree remove .claude/worktrees/<slug>
git worktree list                                       # the tree must be gone

# 3. Only then the branch.
git branch -d chore/<JIRA-KEY>-<slug>
env -u GITHUB_TOKEN git push origin --delete chore/<JIRA-KEY>-<slug>
git rev-list --left-right --count main...origin/main    # must be 0 0
git status --short                                      # must be empty
```

⛔ **Unlink before you remove.** A recursive delete **through a junction** destroys the shared
`.venv` / `node_modules` **targets**, not just the links — it walks into the real directory and deletes
the contents. `git worktree remove` does a recursive delete. Unlink first, every time.

`-d` (never `-D`): it refuses if the branch did not merge, which is the check working. A refusal here
after a successful Step 3 means the merge did not land — go look, do not force. `-d` also fails while a
worktree still holds the branch, which is why the tree goes first.

**PC:** a pruned worktree can leave an empty shell directory behind that blocks a later
`git worktree add` at the same path; only a PowerShell delete clears it.

If the tree belongs to a **story** lane (`claude/*`) rather than this Task, it is not yours to prune —
`/cicd-close-workingtree` owns that one. Leave it and say so.

## Step 6 — Verify, THEN report

Every ✅ below must come from a command you actually ran in this step, not from intent:

```bash
git rev-parse --abbrev-ref HEAD        # main
git log --oneline -1                   # the merge commit
git branch --list 'chore/<JIRA-KEY>-*' # empty
git ls-remote --heads origin 'chore/<JIRA-KEY>-*'  # empty
```

Print:

`✅ Task <JIRA-KEY> closed:`
- `Lane: LOCAL — <why the E2E gate did not apply, in the preflight's words>`
- `Gate: <the commands run + their real totals>`
- `Merged: <merge-sha> (--no-ff)` · `main 0 0, clean`
- `Jira: Dev Record filed (one record) · ticket → Done · check exit 0`
- `Pruned: chore/<JIRA-KEY>-<slug> local + remote` *(or why it was retained)*
- `Still owed: <the --followon items, or "nothing">`

Optional additional input (repo · branch): $ARGUMENTS
