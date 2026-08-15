---
description: Land a SET of finished Task lanes — multiple `chore/<JIRA-KEY>-<slug>` branches — on `main`, one merge at a time, in an order derived from measurement rather than belief. Inventories every lane (branch, key, commits, `task.yaml`, walkthrough `Verdict:`), preflights each with `--expect-key`, filters stale lanes, and builds an overlap map that classifies every shared file (ledger / rewrite-vs-edit / modify-delete / gate-or-script) and forces lanes that change commit or push machinery to the END. Then, per lane — absorb `main`, reconcile, re-gate, STOP for the operator's sign-off, merge `--no-ff`, Dev Record, ticket to Done, prune — and finishes with a combined gate on `main`, which is the only run that sees the whole set together. The `smh-` counterpart of `/cicd-merge-epic-workingtrees`. Use when several Task lanes are review-complete at once.
---

# /smh-merge-multiple-workingtrees — Land a Set of Task Lanes, One Sign-off Per Merge

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never
>   force-push; every branch and every commit carries the repo's Jira key; conflicts surface on
>   the branch, never on `main`
> - `.agents/rules/worktree-per-story.md` §"cwd is not intent" — every repo and branch below is
>   pinned from command output. With N lanes live, where you are standing is the wrong tree N−1
>   times out of N — **and see the ⛔ in Step 0, which is not a warning about worktrees but about
>   this command's own merge step**
> - `.agents/rules/jira.md` — the `acli` reference and the Dev Record contract
> - `.agents/rules/artifacts-always-first.md` — the walkthrough's `Verdict:` line is the flip gate

**Why this exists.** Closing N finished lanes one at a time through `/smh-close-task-merge-tree` is
correct but blind: each close-out sees one lane. **The set ships what no single lane ever saw.** On
2026-08-11 six lanes landed this way and the combined gate at the end caught a real defect
(SCC-96) that *every individual lane had been green against*, because the offending ledger row and
the checker that misread it lived in two different lanes. That is the whole argument for this
command in one sentence.

**Why one invocation is NOT one sign-off for the set.** `/cicd-merge-epic-workingtrees` lands its
lanes on an **epic branch** — not production — and reaches `main` later through `/cicd-push-e2e`, a
separate sign-off. A Task lane lands on **`main` directly**: N lanes = **N production merges**.
SCC-71 is the written record of one invocation riding six merges. So this command **stops before
every merge and hands back**. It automates the analysis, the reconcile, the gate and the prune —
never the authorisation.

> Flow position: N × (`/smh-quick-dev` → `/smh-code-review`) → **`/smh-merge-multiple-workingtrees`**.
> One finished lane does not need this — that is `/smh-close-task-merge-tree`.

---

## Step 0 — Resolve the repo and pin every key (FIRST) — from command output, never belief

```bash
REPO=$(git rev-parse --show-toplevel)
echo "Landing repo: $(basename "$REPO")"
git -C "$REPO" worktree list
git -C "$REPO" branch --list 'chore/*' --format='%(refname:short) %(objectname:short)'
```

Trees and branches **disagree after prunes** — inventory BOTH. A branch with no tree is still
landable; a tree on an already-merged branch is a leftover to report, not to land.

### ⛔ Use `git -C "$REPO"` on EVERY git call in this command. Never a bare `git` after a `cd`.

**This is the one that actually bit, and it bit the merge itself.** On 2026-08-11 this procedure ran
`cd <worktree> && git checkout main`, then — in a later call — a bare `git merge <lane>`. The working
directory had reset to the shared checkout between the two, which was sitting on a **sibling lane's
branch**. The merge succeeded, reported success, and landed a production merge commit **onto
`chore/SCC-89-migrations-to-docs` instead of `main`**.

Nothing caught it. The merge output looks identical, the file list is right, and the commit message
says `-> main` because you wrote it that way. It was found only by running `git rev-parse
--abbrev-ref HEAD` afterwards and not recognising the answer.

So, mechanically:

- **Every** `git` invocation takes `-C "$REPO"` or `-C "$TREE"`. A `cd` is not a lock.
- **Immediately before the merge**, echo the branch from `rev-parse` and compare it to `main` by
  name. If it is not `main`, STOP.
- Recovery, if it happens anyway: the merge commit is usually *correct in every way except which
  pointer moved* — check `git log -1 --format='%p'`, and if its first parent is `main`'s tip, you
  can `git -C <tree-holding-main> merge --ff-only <that-sha>` to put it where it belonged. Verify
  the tree carries nothing from the wrong branch first: `git diff --name-only <main-tip> <sha>`.

Then pin, **before any tool has answered anything**, the Jira keys you intend to land. A lane whose
key you cannot name is not in the set.

## Step 1 — Inventory every lane (the eligibility table)

Per `chore/*` lane, from ITS tree (or a `--detach` throwaway if the branch has none):

| Column | Source — command output, never memory |
|---|---|
| branch · tip | `git -C <tree> rev-parse --abbrev-ref HEAD` · `rev-parse --short HEAD` |
| **commits ahead** | `git -C "$REPO" rev-list --count main..<branch>` — **see below** |
| key | the segment after `chore/` — must match a Step 0 key |
| `task.yaml` | the lane's `_artifacts/_main/<date>_<slug>/task.yaml` |
| **verdict** | the LAST `Verdict:` line in that folder's `walkthrough.md` |
| dirty · untracked | `git -C <tree> status --porcelain` — **both halves matter, see Step 3** |

**⚠ "Ready" does not mean committed.** A lane reported finished can have **zero commits**, its work
sitting uncommitted in a shared checkout. That happened on 2026-08-11 to a lane whose team had
reported it done. `rev-list --count main..<branch> == 0` with a dirty tree means the lane has not
been built yet in any sense git can see — it needs commit, artifacts and review before it is in the
set at all.

**Verdict rules — the flip gate, held here:**
- Grep the lane's **own** artifact folder only. A recursive grep hits historical verdicts in
  `_artifacts/_main/INDEX.md` and other lanes' walkthroughs — that exact mistake produced a wrong
  eligibility call on 2026-08-11.
- `PASS`/`CONCERNS` at the lane's tip → eligible. A verdict at an older sha is valid **only** if
  every commit after it is artifact-stamp or doc-only (`git log --oneline <verdict-sha>..<tip>`).
- **A verdict measured before a sibling landed is stale even though nothing on the branch changed.**
  It described a `main` that no longer exists. Step 4b re-measures; the old verdict is **recorded,
  never overwritten** — on 2026-08-11 one lane's pre-absorb verdict was `FAIL` and the record of
  that failure was the most useful line in its walkthrough.
- `FAIL`, no verdict, or a voided verdict → **not eligible**. Name what is missing and the command
  that produces it (`/smh-code-review`).

⛔ **An empty eligible set is a STOP with a named reason, never a pass.** "All lanes landed" after
zero merges is the gate that cannot fail.

## Step 2 — Preflight each eligible lane

```bash
python3 .agents/scripts/task_preflight.py --fetch --repo "$REPO" --branch "chore/<KEY>-<slug>" --expect-key "<KEY>"
```

⭐ **A `landing:` STALLED LANDING error here is the whole set's problem, not one lane's
(SCC-159).** This command merges lane after lane onto local `main`; if `main` was already ahead of
`origin/main` when you started, every lane in the loop lands on the stuck one and the run reports
success N times over. The preflight now refuses at the first lane instead. `--accept-unpushed-main`
is the auditable offline exit, and it is stated in the output when used.

🛑 **Read the header line before the verdict** — it echoes the branch the script actually resolved.
A key mismatch is a mechanical exit 2. Pass `--repo` and `--branch` explicitly: the script can
guess, and the guess is exactly what fails when a sibling lane has moved the shared checkout.

**⭐ THE LANE decides eligibility, not the ticket.** `LANE: HANDOFF` — a deployable path
(`backend/ frontend/ firebase/ functions/ mobile/ .github/`) in the diff — removes that lane from
this set: *the product has one road to `main`, `/cicd-push-e2e`.* No override flag, deliberately.
The rest of the set continues without it.

> ⓘ **This rule is worth obeying even when it costs you a one-line fix.** On 2026-08-11 a lane
> carried a stale path in a `backend/requirements.txt` **comment**. Fixing it would have flipped
> that lane from `LOCAL` to `HANDOFF` and sent 33 memory files plus one comment through the full
> end-to-end suite. The comment was left, and the debt written down. Trading a real deploy gate for
> a comment is the trade the lane rule exists to prevent.

## Step 2.5 — Staleness against **current** `main`

```bash
git -C "$REPO" rev-list --count "chore/<KEY>-<slug>..main"     # commits behind
git -C "$REPO" diff --name-only main..."chore/<KEY>-<slug>"    # then re-resolve every path it REFERENCES
```

Behind `main` **and** referencing a path that no longer exists there = **not eligible until it
absorbs and re-gates.** Every gate on that branch can be green: a green suite proves the lane runs
against the `main` it was written for, not that its references still resolve. Worked example — a
lane 31 commits behind, all gates green, editing a file a landed sibling had **deleted**.

## Step 3 — The overlap map (before ANY merge)

Pairwise-intersect every eligible lane's `git diff --name-only main...<branch>` and classify each
shared file. **Four classes, and only the first is mechanical:**

| Class | Looks like | Resolution law |
|---|---|---|
| **ledger** | `_artifacts/_main/INDEX.md` · `MEMORY.md` · `CHANGELOG.md` | **Keep BOTH sides' rows, never pick a winner.** Every lane appends at the same table head, so it conflicts every time and resolves the same way every time. |
| **rewrite vs edit** | one lane rewrote a doc another lane edited a paragraph of | ⚠ **NOT mechanical, and git cannot tell you.** The paragraph the edit changed no longer exists, so *both* automatic resolutions are wrong. **Re-author** the edit into the new structure. |
| **modify / delete** | one lane deletes a file another lane edited | ⚠ **A decision, not a strategy.** Ordering does not rescue it — both orders end with the file deleted. Rule which side wins, and **prove the surviving content exists at its destination BEFORE accepting the deletion**. |
| **gate or script** | `.githooks/` · `.agents/scripts/` · anything a gate imports | ORDER MATTERS. State which version must win before merging, and re-run the gate that file feeds after each landing that touches it. |
| **generated** | sync manifests, mirrors, tool-written INDEXes | Resolved by **REGENERATING**, never by hand-merge. |

**⚠ `git diff` cannot see untracked files, so this map UNDERCOUNTS.** On 2026-08-11 one lane was
absent from the ledger-collision list until it committed an untracked artifact folder — at which
point it became the **fifth** lane on a file four lanes were already fighting over. Run
`git -C <tree> status --porcelain` per lane and fold anything untracked into the map **as if it were
already committed**, because at merge time it will be.

**The ledger tie-break, stated once so it is reproducible.** Same-day rows do not order themselves.
**The lane that lands later goes on top** — that keeps the file's newest-first semantics true
against merge history, and anyone can re-derive it from `git log` afterwards.

**⭐ A lane that changes commit or push machinery lands LAST.** Once it lands it changes the rules
for every merge after it — a pre-push approval hook landed mid-sequence turns the rest of the
session into a different procedure.

**Cross-repo dependencies are part of the order.** A lane whose deletion's destination is an
**unmerged branch in another repo** lands AFTER that branch merges there. Get this wrong and the
content exists on no merged branch in either repo, and nothing says so.

State the full landing order and every dependency in writing. **Dump the eligibility table, the
landing order and every conflict decision to a scratch file** (`_artifacts/_main/<date>_<slug>/`, or
the session scratchpad) — a landing runs long enough to be compacted, and re-reading four lines
costs less than re-deriving them. It is a convenience, not a durable-state mechanism: a session
*was* compacted mid-landing on 2026-08-13 and lost nothing, because the set is cheap to re-derive
and the real decisions were already in the merge commits. Then proceed to Step 4 with the FIRST
lane only.

## Step 4 — The landing loop (per lane, in the derived order)

**4a — absorb.** `env -u GITHUB_TOKEN git -C <tree> merge origin/main --no-edit`. `main` moves after
every landing, so **every lane re-absorbs at its turn**. Conflicts are resolved HERE, never on
`main`, using the Step 3 table. A conflict **outside** the map is a finding: stop and re-derive.

**4b — re-gate on the post-absorb tree, BARE.** Piping to `tail` returns the *pipe's* exit code.

```bash
python3 .agents/scripts/tests/run_all.py
python3 .agents/scripts/workflow_lint.py --toolkit-only
```

Plus whatever this lane's own assertions are — **run the lane's own tests against the reconciled
tree**, because that is the real question. A suite that only passes against the text it was written
for goes red here, and that is the check working.

An **artifacts-only** absorb keeps the lane's `Verdict:` valid. A code, script **or doc** change
during 4a voids it — only `_artifacts/` is exempt, and a `docs/` commit invalidates (SCC-154
corrected the old "doc-only" wording after a docs commit staled a receipt mid-review; the same
correction applies here).
**Append the re-measurement to the walkthrough; never edit the old verdict away.**

⭐ **The LAST lane's 4b and Step 5's combined gate can be the same run — skip one, mechanically
(SCC-156).** After the final lane's absorb-and-merge, `main`'s tree and the tree 4b just gated are
frequently byte-identical, and running the 25-file suite twice over identical content buys nothing.
Ask git, never your memory of what happened:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, ".agents/scripts")
import wf_common as wf
from pathlib import Path
print("identical" if wf.same_tree(Path("."), "<4b-sha>", "main") else "DIFFERENT — run both")
PY
```

Identical ⇒ run the combined gate once and say in the summary which run covered both. Different, or
either sha unknown (`same_tree` returns `None`) ⇒ **run both.** Fail toward running.

**⚠ A review can fail at this stage, and that is not a reason to drop the lane.** Fix on the branch,
re-review, re-stamp, continue. On 2026-08-11 a lane went `FAIL` here (two dead links the move
introduced), was fixed in place, and landed `PASS` — with the `FAIL` left in the record.

**⚠ The fixes you make here are ORDINARY COMMITS, and the armed SOP gate applies to them.** The
absorb-merge itself is exempt — git writes merge messages, and the two `commit-msg` gates carve
merges out (since SCC-144 they do so inside a worktree too; the probe used to be blind there, so
this step could refuse an absorb on a condition no author could satisfy). A hand fix is not a merge:
touch a usage surface (`.agents/commands/` · `.agents/rules/` · `.agents/scripts/*.py|.ps1` ·
`.githooks/` · root `AGENTS.md`) while fixing, and the commit is **rejected** unless
`docs/_scc_sops_prds/workflows_testing_SOP.md` moves with it. Stage the doc, or say `[sop-ok]` when
the fix genuinely changes nothing an operator types — that token stays in the log as the record of
the call.

**The re-measurement stamp — append it, never edit the old verdict away.** The shape, from the
2026-08-13 landing (`_artifacts/_main/2026-08-13_scc-127-verify-wave/walkthrough.md`):

```markdown
## Post-absorb re-measurement (<date>, landing set <keys in order>)

**Verdict: <PASS|CONCERNS> @ <post-absorb sha>** — re-measured after absorbing `main` at <sha>
(<what landed there>). The pre-absorb `Verdict: … @ <sha>` above is **left standing on purpose**:
it described a `main` that no longer exists.

<Doc-only absorb? say so and stop here. Otherwise, one bullet per conflicted file naming the
resolution and WHY — the judgement calls are the part nobody can re-derive later.>

    python3 .agents/scripts/tests/run_all.py                     -> 21/21 files, N/N cases, exit 0
    python3 .agents/scripts/workflow_lint.py --toolkit-only      -> 0 errors, 0 warnings, exit 0
    python3 .agents/scripts/check_maps.py --depth3-only --strict -> exit 0

**Case total additive: <main> + <lane A> + <lane B> = <total>.** <Or say which lane displaced
which, and why that was correct.>
```

The case-total line is the cheapest real check in the whole step: if the totals are not additive,
one lane's tests displaced another's and the merge ate coverage neither review would ever see.

**4c — 🛑 STOP. Hand back for THIS lane's sign-off.** Print the lane's key, tip, verdict line, gate
totals, and what the merge changes on `main`. **One invocation of this command is not N
authorisations** (SCC-71). Wait for the operator's word for THIS lane.

> ⓘ **The permission layer may enforce this for you.** In auto mode the classifier can refuse
> `git merge` into `main` outright. That refusal is the contract working, not a malfunction — it is
> SCC-71 held by something that cannot be talked out of it. Retry once; if it refuses again, hand
> the rule to the operator rather than routing around it.

**4d — merge, with the target re-checked out loud:**

```bash
git -C "$REPO" checkout main
test "$(git -C "$REPO" rev-parse --abbrev-ref HEAD)" = "main" || { echo "NOT ON main — STOP"; exit 1; }
env -u GITHUB_TOKEN git -C "$REPO" pull --ff-only origin main
git -C "$REPO" merge "chore/<KEY>-<slug>" --no-ff -m "merge: chore/<KEY>-<slug> -> main (task: <gate summary>; review <verdict>)"
env -u GITHUB_TOKEN git -C "$REPO" push origin main
git -C "$REPO" rev-list --left-right --count main...origin/main    # must be 0 0
```

A push-approval prompt or token requirement is **expected, not an error** — satisfy it, never bypass
it. Rejected push (remote moved) → STOP and report; never force.

⭐ **Since SCC-144 the `test … = "main"` line above has a machine behind it.** The `commit-msg` hook
refuses a merge whose target is not a legal destination for its source and names the SCC-97
signature — a lane landing on a sibling lane — when it sees one. Keep the assertion anyway: it stops
you one step earlier, and it is the half that still works under `--no-verify`.

**4e — Dev Record, then the ticket — per lane, at ITS merge, never batched.**
`jira_feed.py devrecord --key <KEY> … --closing --apply` (updates in place — never `--append-new`),
then `acli jira workitem transition --key <KEY> --status "Done" --yes` (**`--yes` or acli stops on a
confirm prompt no agent shell can answer** — SCC-113), then `jira_feed.py check --key
<KEY>` exit 0. **One Dev Record per ticket.** Close a parent ticket only once every sub-task and
linked ticket has landed.

**4f — prune what you landed — unlink FIRST, tree second, branch last.**

```bash
python3 .agents/scripts/link-worktree-assets.py --unlink .claude/worktrees/<slug>
git -C "$REPO" worktree remove .claude/worktrees/<slug>
git -C "$REPO" branch -d "chore/<KEY>-<slug>"        # -d never -D; a refusal means the merge did not land
env -u GITHUB_TOKEN git -C "$REPO" push origin --delete "chore/<KEY>-<slug>"
```

⛔ A recursive delete through a junction eats the shared `.venv`/`node_modules` **targets** — unlink
before remove, every time. ⛔ **Never a `claude/*` tree** — those are `/cicd-close-workingtree`'s.

Then return to 4a with the NEXT lane, against the `main` that now exists.

## Step 5 — The combined gate on `main` (after the LAST landing) — ⭐ do not skip this

```bash
git -C "$REPO" checkout main
python3 .agents/scripts/tests/run_all.py                    # bare
python3 .agents/scripts/workflow_lint.py --toolkit-only     # bare
python3 .agents/scripts/check_maps.py                       # bare — and only meaningful HERE
python3 .agents/scripts/sop_currency.py                     # bare
```

Every lane was green alone, and green again after absorbing its predecessors. **This is the only run
that sees all of them together.**

> ⓘ **It earns its place.** On 2026-08-11 this step caught a gate defect no lane could have: one
> lane's ledger row cited a memory by name, and *another* lane owned the checker that misread the
> citation as a folder that had gone missing. Neither lane was wrong; the pair was. It became its
> own ticket, fixed test-first, and the set closed green.

**`check_maps.py` is meaningful only on `main`.** Inside a worktree it labels the tree by the **CWD
basename** and reports a false AUTO-block stale, and the repo-map's curated block can name
**gitignored** paths that do not travel to worktrees. Both read as drift and are not.

Red here = **fix forward** on a new `chore/*` lane with its own ticket, named in the report. Never
rewritten history, and never merged-and-hoped.

## Step 6 — Verify, THEN report

```bash
git -C "$REPO" rev-list --left-right --count main...origin/main    # 0 0
git -C "$REPO" status --short                                      # empty
git -C "$REPO" worktree list                                       # only expected trees
git -C "$REPO" branch --list 'chore/*'                             # only deliberately-retained lanes
```

Print per lane: `✅ <KEY> landed @ <merge-sha>` or `⏸ <KEY> held — <reason>`, then the combined gate
totals, what remains live and why, and every follow-on owed.

Optional additional input (repo · a subset of lane keys): $ARGUMENTS
