---
IsArtifact: true
ArtifactMetadata:
  title: SCC-95 — build /smh-merge-multiple-workingtrees
  type: implementation_plan
  date: 2026-08-11
---

# Plan — SCC-95 · `/smh-merge-multiple-workingtrees`

**Lane:** `chore/SCC-95-smh-merge-multi-lanes` in `.claude/worktrees/scc-95-merge-multi/` (own
worktree, cut from `main` @ `50e357b`).
**Subject repo:** the command centre itself.

## The acceptance list (authority: SCC-95's ACCEPTANCE block)

Every item is checkable by a command or an inspection. An item that is not, is not built here.

| # | Acceptance | The assertion that proves it |
|---|---|---|
| A1 | The command master exists and every `/`-reference to it resolves | `test_sops_prds_folder.py` T4 — RED before, green after |
| A2 | Toolkit lint stays clean | `workflow_lint.py --toolkit-only` → 0 errors, 0 warnings, exit 0 |
| A3 | It stops for a sign-off before **every** merge | grep the body: a STOP step between each lane's gate and its merge, plus the SCC-71 rationale stated inline |
| A4 | It refuses a deployable diff and names `/cicd-push-e2e` | grep the body for the `LANE: HANDOFF` branch and "no override" |
| A5 | `task_preflight.py --expect-key` runs per lane | grep the body for `--expect-key` inside the per-lane loop |
| A6 | Overlap map before any merge, with ledger / gate-or-script / command-or-rule classes, gate-changing lanes ordered LAST | inspection of the Step 3 table + a worked example |
| A7 | Stale-lane detection (behind main **and** references a path gone from main) | inspection; the SCC-77 case is the worked example |
| A8 | Prunes only `chore/*` it landed; unlink before remove; never a `claude/*` tree | grep the body for the unlink-first order + the `claude/*` refusal |
| A9 | One Dev Record **per ticket**, each moved to Done at its own merge | grep the body: `devrecord` inside the per-lane loop, not after it |
| A10 | SOP moves in the same commit; four doors exist after sync | `sop_currency.py` exit 0 with the SOP staged; door parity check |

## The load-bearing design decision, stated before any file is written

`/cicd-merge-epic-workingtrees` takes **one** operator invocation for the whole set. That is correct
**there** and would be a defect **here**, and the difference is not stylistic:

- the story command lands every lane on an **epic branch** — not production. The set reaches `main`
  later, through `/cicd-push-e2e`, which is its own separate sign-off.
- a Task lane lands on **`main` directly**. N lanes = **N production merges**.

SCC-71 is the written record of what happens when one invocation covers several merges: it was
invoked once and rode six, and the operator twice typed the command to authorise a merge that had
already happened. **So this command automates the analysis, the reconcile, the gate and the prune —
and never the authorisation.** It stops before every merge and hands back.

That is the one thing a reviewer should check hardest, because it is the one thing that makes this
command safe to exist at all.

## Steps

Each step names the assertion that proves it.

### Step 1 — RED first (nothing is written until something fails)

The tier for a **command** per `/smh-quick-dev`: the linter or the reference-resolver reporting the
specific missing thing, captured *before* the fix.

1. Add the `/smh-merge-multiple-workingtrees` reference to the SOP's command table **only**.
2. Run `python3 .agents/scripts/tests/test_sops_prds_folder.py` — **must FAIL T4** with
   `unresolved command: smh-merge-multiple-workingtrees` (no master answers to that name).
3. Paste the RED. Read *which* line raised — a check that dies in setup looks identical to one that
   fails its assertion.

⛔ If T4 does **not** go red, the assertion is fiction and the plan is wrong — stop and re-derive,
do not proceed to Step 2.

### Step 2 — GREEN: write the command master, minimally

`.agents/commands/smh-merge-multiple-workingtrees.md`, adapted from
`.agents/commands/cicd-merge-epic-workingtrees.md`. Structure, and what changes from the story lane:

| Step | Story lane (`cicd-`) | This command (`smh-`) |
|---|---|---|
| 0 | resolve the target **project** | resolve the **repo you are standing in**, from `git rev-parse`, never belief. Pin each lane's `EXPECTED_KEY` before any tool answers. |
| 1 | inventory trees → story → board row → verdict | inventory `chore/*` trees **and** branches (they disagree after prunes) → ticket key → `task.yaml` → the walkthrough's `Verdict:` line. No board row exists. |
| 2 | per-lane preflight, close-out eligibility | `task_preflight.py --fetch --repo --branch --expect-key` per lane. **Read the header line before the verdict.** A key mismatch is exit 2, not a warning. |
| 2.5 | *(none)* | ⭐ **NEW — staleness.** Per lane: `git rev-list --count <lane>..main`, plus re-resolve every path the lane's diff *references* against current `main`. Behind + a dead reference = **not eligible** until it absorbs `main` and re-gates. |
| 3 | overlap map: code / board / test | overlap map: **ledger** (`INDEX.md`, `MEMORY.md`, `CHANGELOG.md` → keep BOTH sides' rows, never pick a winner) · **gate-or-script** (`.githooks/`, `.agents/scripts/`) · **command-or-rule**. ⭐ **A lane that changes commit/push machinery is forced LAST**, because once it lands it changes the rules for every merge after it. |
| 4 | per lane: merge epic in → gate → close story → push to epic | per lane: absorb `origin/main` → command-centre gate → **STOP for the operator's sign-off** → merge `--no-ff` to `main` → Dev Record → ticket Done. **`main` moves after each landing, so the next lane re-absorbs.** |
| 5 | combined gate on the epic branch | combined gate on `main` after the last landing: `run_all.py`, `workflow_lint --toolkit-only`, link+anchor, `sop_currency`, door parity. |
| 6 | `/cicd-close-workingtree` per lane | prune inline per `/smh-close-task-merge-tree` Step 5: **unlink assets → remove tree → delete branch**, in that order. ⛔ Never a `claude/*` tree — that is `/cicd-close-workingtree`'s. |

Rule pointers the linter requires (it greps raw text): `git-policy.md` (this runs `git merge`,
`git push`, `git branch -d`) and `worktree-per-story.md` (it runs `git worktree`). Both go in the
header block. Also `jira.md` for the Dev Record calls.

Frontmatter: a real `description:`, and **no `platforms: []`** — omit the key so it publishes to all
four (an empty list syncs to NOWHERE while looking installed).

### Step 3 — the surfaces a new command must touch, or it is invisible

- `.agents/commands/INDEX.md` — a row, or `check_commands` warns and A2 fails.
- `docs/_scc_sops_prds/workflows_testing_SOP.md` — the §7 landing family table and the §17 reference
  table. **Written against SCC-90's restructured file, which is why SCC-90 lands first** (below).
- `/smh-sync-agents` — generates the four doors. **Run it, then verify the doors exist**; do not
  assume. Then start a new Codex chat / restart opencode, per the SOP.

### Step 4 — verify, then the review gate

Re-run every A-item assertion, paste real output, record `git rev-parse HEAD` beside it. Then
`/smh-code-review`, which re-derives the blast radius against current `main` before it rules.

## Landing-order dependencies — measured, not assumed

Derived with the same analysis this command will automate, which is the useful part:

- ⛔ **SCC-90 must land BEFORE this lane.** Both edit
  `docs/_scc_sops_prds/workflows_testing_SOP.md`, and SCC-90 rewrites it end to end. Writing this
  command's SOP rows against the *old* structure guarantees a conflict that a merge cannot resolve
  mechanically. **Mitigation: absorb `main` after SCC-90 lands, then write the SOP rows.**
- **SCC-77 must land AFTER this lane**, and after everything else. It adds `.githooks/pre-push`,
  `MAIN-PUSH-ENFORCE`, `mint-push-token.sh` and `pre-push-main-approval.sh` — once landed, every
  subsequent merge to `main` needs a token. It also edits
  `.agents/commands/smh-close-task-merge-tree.md`, the sibling of the command being built here (no
  file conflict; this lane does not edit that file).
- **SCC-83 / SCC-88 / SCC-89:** zero files in this lane's blast radius.

## Risks

| Risk | Mitigation |
|---|---|
| The command becomes a copy of the story version with words swapped, and quietly inherits one-invocation-for-the-set | A3 is a grep-checkable acceptance item, and the rationale is written into the body where the next agent reads it |
| Writing SOP rows against the pre-SCC-90 structure | absorb `main` after SCC-90 lands; do the SOP edit last |
| A green gate about the wrong lane | `--expect-key` per lane, header line read before the verdict; own worktree so `cwd` cannot drift into a sibling |
| Building it against today's five lanes and hard-coding their shape | the command is written to *derive* the set, and the SCC-77/83/88/89/90 case goes in as a worked example, never as data |

## Out of scope

Modifying `/cicd-merge-epic-workingtrees`. The story-lane command is correct for its lane; this is a
sibling, not a refactor. (Stated because the request that opened this ticket said "modify" — the
measured answer is that no change to it is needed.)

---

## Self-Audit (2026-08-11)

**Mode:** PRE-WORK. **Right-size:** FULL — it touches the naming law, the door law, four platform
surfaces, the SOP, and adds a command surface. **Repo/branch (from `rev-parse`):**
`scc-95-merge-multi` | `chore/SCC-95-smh-merge-multi-lanes`.

**Phase 0 — scope, list, traceability.** Change set: 1 new command master, 1 `commands/INDEX.md` row,
2 SOP sections, 4 generated doors, 1 walkthrough. Checkable list taken from SCC-95's ACCEPTANCE block
(A1–A10), all verifiable by command or inspection. Traceability walked **both** directions: every
A-item has a step, and no step traces to nothing — no scope creep found. **Lane check: LOCAL** — the
change set touches `.agents/` and `docs/` only, nothing deployable, so it closes through
`/smh-close-task-merge-tree`.

**Phase 1 — blast radius.** Door model verified against the live sibling: all four doors exist for
`smh-close-task-merge-tree` (`.claude/skills/`, `.agents/skills/`, `.opencode/commands/`,
`.agents/workflows/`), so the new command needs all four and only `/smh-sync-agents` may write them.
`_RULE_POINTERS` confirmed by reading `workflow_lint.py`: `git-policy` and `worktree-per-story` are
required; `smh-target-resolution` is **not**, and must stay not-required — its trigger is
`^#+\s*Step 0\b.*(?:target|project)`, so a Step 0 heading saying *"resolve the repo"* correctly
avoids it. Sibling lanes read live (5 worktrees): SCC-83/88/89 have **zero** files in this blast
radius; SCC-90 and SCC-77 do — carried into the findings below.

**Phase 2 — over-engineering gate.** Two tripwires fired. Both survive, and the justification is
recorded rather than assumed:

- *"A new command where an existing one should take a flag."* `/smh-close-task-merge-tree:37` states
  *"Invoking it IS the operator's per-merge sign-off for **this one** task"* and *"Approval is
  per-action and never carries forward."* A multi-lane mode inside that file would contradict the
  contract stated in that same file. The story lane sets the precedent with three separate commands
  rather than one flagged command. **Justified — keep it separate.**
- *"Clone-and-tweak."* This is a deliberate cross-family duplicate (`cicd-*` ⇄ `smh-*`), which the
  gate permits **only when stated with the divergence named** — the plan's Step 2 table is that
  statement. **Justified.** Standing obligation inherited: fix a shared idea in one, diff the twin.

No new rule file, no new script, no unrequested flag, and N is genuinely 5 today — not a
generalization for a hypothetical.

**Phase 3 — pre-mortem.** Walked; three rows produced findings (below). Cleared in one line each:
fresh clone N/A (ships no gate) · gate-fires-on-someone-else N/A · escape hatch N/A · rollback is a
doc revert, though the command *performs* irreversible `main` merges — mitigated by its own per-merge
STOP, which is the point of A3.

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | plan Step 2, the command body | **HIGH** | **Vacuous green on an empty set.** If no `chore/*` lane is eligible — none live, or all filtered out by staleness/HANDOFF — the command could report "all lanes landed" having done nothing. That is the *"gate that cannot fail"* tripwire, and it reads as success. | **BAKED IN** — the command must treat an empty eligible set as a **STOP with a named reason**, never a pass. Mirrors `/smh-code-review` §"an empty diff is a STOP, not a pass". |
| F2 | plan Step 3, `commands/INDEX.md` | MED | The plan says "a row". `commands/INDEX.md` is grouped **by lane**, not one row per command — `smh-close-task-merge-tree` sits under a **Task close-out** group row. A builder following "add a row" invents a shape the file does not use. | **BAKED IN** — extend the existing **Task close-out** group row to name both commands and say when each applies; do not mint a new group. |
| F3 | landing order | MED | **SCC-77 changes push mechanics mid-sequence.** It adds `.githooks/pre-push` + `MAIN-PUSH-ENFORCE` + `mint-push-token.sh`; today `.githooks/` holds only `commit-msg`, `post-commit`, `pre-commit`. Once it lands, every merge this command performs needs a minted push token — so a body written assuming unguarded `main` pushes silently breaks the first time it runs after SCC-77. | **BAKED IN** — the command's Step 4 must not assume an unguarded push: treat a push-approval prompt or token requirement as **expected, not an error**, exactly as `/cicd-push-e2e` and `/smh-close-task-merge-tree` already word it. And SCC-77 lands **last** in the order this lane recommends. |

### Four quick gates

- **Verification strategy present?** Yes — every A-item names the command that proves it, and Step 1
  is a genuine RED (T4 must fail before the master exists).
- **Anything irreversible?** The *built* command performs `main` merges and branch deletes. Gated by
  A3's per-merge STOP and by unlink-before-remove (A8). Building it is fully reversible.
- **Any step vague enough that the builder will guess?** One was — F2. Now specified.
- **Convention fit?** Naming law ✓ (`smh-` prefix, hyphens) · door law ✓ (generated, four) · artifacts
  in `_artifacts/_main/<date>_<slug>/` ✓ · no `platforms: []` ✓.

### Landing-order dependency (stated, per the rule)

⛔ **SCC-90 must land before this lane** — both edit `workflows_testing_SOP.md`, and SCC-90 rewrites it
end to end. Writing this command's SOP rows against the old structure produces a conflict no merge can
resolve mechanically. **If it does not land first**, this lane's SOP edit must be re-authored against
the new file, wasting the work. Mitigation: absorb `main` after SCC-90 lands, then edit the SOP last.

**SCC-77 lands after this lane** (F3). SCC-83, SCC-88, SCC-89: no overlap, order-independent.

```
Audit verdict: GO
```

*(GO with F1–F3 baked into the plan above. Re-audit is owed only if the change set widens beyond the
one command + INDEX + SOP.)*
