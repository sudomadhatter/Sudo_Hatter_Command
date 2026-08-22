# SCC-244 — Bugs and Updates, cycle 4 (one consolidated lane)

**Ticket:** SCC-244 (Task, `In Progress`) · **Branch:** `chore/SCC-244-bugs-updates-cycle-4`
**Worktree:** `.claude/worktrees/scc-244-bugs-updates-cycle-4` · **Base:** `origin/main` @ `038c0f1`
**Riders:** SCC-254 (A) · SCC-255 (B) · SCC-256 (C) · SCC-257 (D) · SCC-258 (E) · SCC-259 (F) · SCC-260 (G)
**Successor minted:** SCC-262 (cycle 5) — baton `running-bug-list` handed at `jira_feed.py start`.

The seven riders were all measured on 2026-08-21 while running the real `/cicd-*` doors against
AVCH Epic 19. Each carries a file anchor; every anchor was re-verified against this worktree
before this plan was written (see *Recon* per part).

---

## Scope decision — what lands here, and the one part that cannot

Six riders (A–F) are entirely inside this repo and land on this lane. **Rider G splits**, and the
split is a *structural* blocker, not a preference:

| G half | Repo | Disposition |
|---|---|---|
| `cicd-write-story-tests.md` Step 1 names the story path | **this repo** | **lands here** |
| `_bmad/custom/bmad-create-story.toml` in AGY | `AGY_AVIATIONCHAT` (submodule, `JIRA_KEYS="AVCH"`) | **AVCH ticket** — a commit there carries an AVCH key and its own PR |
| same file in the project template | `Projects/sudo-project-skeleton` | **filed on SCC-262** — the submodule is **not initialized** (`git submodule status` shows `-de8dbf29`, the directory is empty) and the repo has no `.agents/jira.conf`, so there is no key to commit under from here |

⚠️ The empty-directory state is itself a reading trap worth recording: `cd Projects/sudo-project-skeleton
&& git log` **succeeds and prints the LOBBY's log**, because git walks up out of the empty dir. Anyone
"verifying the template" that way reads the wrong repo and sees a pass.

---

## Acceptance list — from each rider's own ACCEPTANCE block

Authority order per `/smh-quick-dev` Step 1: the ticket's `ACCEPTANCE` block first. Every row below
is checkable by a command.

| # | Rider | Acceptance statement | The check |
|---|---|---|---|
| A1 | SCC-254 | Boot Step 2b names the epic-branch read **and** the disagreement report | `test_boot_epic_branch_read.py` scans the Step 2b section for a `git show <epic-ref>:…sprint-status.yaml` fence + the disagreement sentence |
| A2 | SCC-254 | SOP page updated | armed `commit-msg` `sop_currency.py` |
| B1 | SCC-255 | Without `--repo`, inside a **submodule** checkout, the script links the same assets `--repo` links | `test_link_worktree_assets.py` — fixture repo whose `.git` is a **gitdir file** |
| B2 | SCC-255 | An **unverified resolution** exits non-zero with the resolved path in the message; a *verified* repo with zero assets exits 0 and says so (⚠️ AUDIT FINDING 2 — amended from SCC-255's literal wording) | `test_link_worktree_assets.py --case unverified-resolution-refuses` |
| B3 | SCC-255 | `tests/` covers the submodule case | the file above exists and runs in `run_all.py` |
| C1 | SCC-256 | Step 0.5 item 2 no longer requires HEAD on the epic branch; no command contradicts `worktree-per-story.md:221` | `test_shared_checkout_stays_on_main.py` — pattern-scan across **all** `.agents/commands/*.md` |
| C2 | SCC-256 | SOP page updated | `sop_currency.py` |
| D1 | SCC-257 | `outline` on a `## Acceptance Criteria` → `### Theme` → `- **AC-n**` story renders every AC | `test_jira_feed.py --case ac-theme-subheadings` |
| D2 | SCC-257 | A story with flat `1.` ACs still renders as before | same file, regression case |
| E1 | SCC-258 | `mint` on a ticket whose description is a **hand note** replaces it with the outline and preserves the note under `PREVIOUS NOTE` | `test_jira_feed.py --case mint-reuse-stale-description` |
| E2 | SCC-258 | `outline` and `mint` accept the same flags | `test_jira_feed.py --case outline-accepts-jira-project` |
| F1 | SCC-259 | `plan` lists a `story` source for a child whose story file exists **only on the lane branch**; a tests-only branch-diff carries `tests_only: true` and ranks **after** `story` | `test_label_tasks.py --case branch-only-story-source` |
| F2 | SCC-259 | `resolve`'s lock `detail` names **every** declared blocker, not the first | `test_label_tasks.py --case resolve-lists-all-blockers` |
| G1 | SCC-260 | `cicd-write-story-tests.md` Step 1 names `_bmad/bmm/stories/` next to the skill invocation | `test_story_path_is_pinned.py` |
| G2 | SCC-260 | The two out-of-repo halves are **filed**, not silently dropped | the ticket keys appear in `## Your Actions` and on the board |
| Z1 | all | Enforcement suite green at the shipping sha, through the receipt writer | `gate_receipt.py run … run_all.py` → `gates/suite.json` |
| Z2 | riders | The two memory files written during the discovery session ride **this** PR, and `main` is clean | `git -C <main> status --short` empty; both paths in this branch's diff |

---

## Recon — every anchor re-verified in this worktree (2026-08-21)

- **A** `.agents/commands/cicd-boot-sprint-memory.md:58` — *"Read `_bmad-output/implementation-artifacts/sprint-status.yaml`"*, no branch named. **Confirmed.**
- **B** `.agents/scripts/link-worktree-assets.py:58-67` — `repo_root()` returns `Path(--git-common-dir).parent`. In a submodule the common dir is `<super>/.git/modules/<path>`, so the parent is a **gitdir**. **Confirmed.**
- **C** `.agents/commands/cicd-write-story-tests.md:27` — *"and HEAD is on it (**never** `main`)"* vs `.agents/rules/worktree-per-story.md:221` *"it stands on `main`"*. **Confirmed contradiction.**
- **D** `.agents/scripts/jira_feed.py:193` — `_NEXT_HEAD_RE = re.compile(r"^#{1,4}\s+\S")` cuts at **any** level; `section_body` (`:198-204`) uses it. **Confirmed.**
- **E** `.agents/scripts/jira_feed.py:839,880` — reuse branch says *"carries its outline (N chars)"* off a length test. **Confirmed.**
- **F** `.agents/scripts/label_tasks.py:497-499` — `branch-diff` source, *"An empty diff is the same story"*. **Confirmed.**
- **G** `.claude/skills/bmad-create-story/SKILL.md:76` — `default_output_file = {implementation_artifacts}/{{story_key}}.md`; AGY `_bmad/custom/` holds 5 tomls, **none** for `bmad-create-story`. **Confirmed.**

---

## Steps — each names the assertion that proves it

Order is **scripts first, docs second**: A/C/G are prose changes whose only honest guard is a
pattern scan, and a scan written after the scripts can reuse the same harness idiom.

### Step 1 — B: `link-worktree-assets.py` resolves a submodule (B1–B3)
RED: `test_link_worktree_assets.py`, two blocks. `submodule-resolves` builds a fixture where the
worktree's `.git` is a **file** containing `gitdir: …`; asserts the resolved repo is a working tree
and the assets link. `empty-repo-refuses` asserts a non-zero exit whose message carries the
resolved path.
GREEN: resolve through `git worktree list --porcelain` line 1 (the main working tree), verify the
result with `git -C <resolved> rev-parse --show-toplevel` and require it to equal `<resolved>`.

> ⚠️ **AUDIT FINDING 2 — the refusal keys on RESOLUTION, not on asset count.** SCC-255's
> ACCEPTANCE B2 says *"a resolved repo with zero assets exits non-zero"*. Measured across the nine
> local checkouts, **six have zero assets** — `B-L-WorldWide`, `BRKN_Tattoos`, `NEXGen-Films`,
> `OpenChat-Openrouter`, `RAG_Pipeline_AC`, `sudo-command-center` — and **ten command bodies** call
> this script at worktree-open time (`cicd-write-story-tests`, `cicd-dev-story-tests`,
> `cicd-quick-dev`, `cicd-prune-worktree`, `smh-quick-dev`, `smh-quick-fix`, `smh-plan-task`,
> `smh-close-task-merge-tree`, `smh-merge-multiple-workingtrees`, + `worktree-per-story.md`). Taken
> literally, B2 makes every lane in those six repos un-openable — breaking a hard gate in six repos
> to fix a bug in one. The ticket's own reasoning is *"'nothing to link' on a repo that **has** a
> `backend/.venv` is a defect"* — that is a **resolution** failure, and that is what is refused:
> - resolved path is not a working-tree root (the measured submodule `.git/modules/<x>` case) → **exit 1**, message carries the resolved path;
> - resolution verified, zero assets → **exit 0** printing `resolution verified: <path>`, so an empty result can never be mistaken for a failed one;
> - `--require-assets` is the opt-in for a caller that knows assets must exist.
>
> This deviates from B2's literal text. It is the operator's to overrule at the approval stop.

### Step 2 — D: `section_body` respects heading depth (D1–D2)
RED: two cases in `test_jira_feed.py` — the 19.x `### Theme` shape (expect every AC), and a flat
`1.` story (expect the pre-change list, byte for byte).
GREEN: `section_body` reads the matched heading's level from `head_match.group(0)` and cuts at the
next heading of **that level or shallower**.

> ⚠️ **AUDIT FINDING 3 — `story_statement` shares `section_body`** (`jira_feed.py:216-220`,
> `body = section_body(text, _STORY_HEAD_RE.search(text))`). Depth-awareness grows every `## Story`
> block that has `###` children, silently changing ticket descriptions the fix was never aimed at.
> The regression case is therefore **required, not optional**, and it must include a story whose
> `## Story` section carries a `###` sub-heading — a flat story cannot detect this.

### Step 3 — E: `mint` refreshes a stale description (E1–E2)
RED: `mint-reuse-stale-description` (a ticket carrying a hand note; expect outline + `PREVIOUS NOTE`)
and `outline-accepts-jira-project` (expect exit 0, not `unrecognized arguments`).
GREEN: test the description for the `Rendered by jira_feed.py` trailer instead of its length; add
`--jira-project` to the `outline` subparser.

> ⚠️ **AUDIT FINDING 4 — the argparse surface is reached by an ARMED HOOK.**
> `.agents/scripts/git-hooks/post-commit-jira-start.sh:119` runs
> `"$PY" .agents/scripts/jira_feed.py start --key "$KEY" --timeout 10 --apply` on the first commit of
> every `chore/ · claude/ · epic/` branch, in every repo. A subparser edit that disturbs `start`
> fires there — and **VS Code hides hook output**, so it reads as a clean commit. A case pinning
> `start`'s accepted flags is added alongside E2.

### Step 4 — F: `label_tasks.py` grounding (F1–F2)
RED: `branch-only-story-source` (story file only on the lane branch; expect a `story` source and
`tests_only: true` ranked below it) and `resolve-lists-all-blockers` (a child declaring four; expect
four in `detail`).
GREEN: `git show <branch>:<path>` fallback for the story read; classify a branch-diff whose
`source_paths` are all under `tests/` or `_bmad*`; join all blockers in `detail`.

> ⚠️ **AUDIT FINDING 1 — the change lands in a script BOTH twins read, and both their doors
> publish the ranking as law.** `.agents/commands/cicd-label-tasks.md:79` and
> `.agents/commands/smh-label-tasks.md:73` each carry the same authority row —
> `| 1. \`branch-diff\` | … | code written beats every declaration |`. Demoting a tests-only
> branch-diff in the script without editing both bodies ships a door that contradicts its own
> engine, which is precisely the measured `cicd`/`smh` drift pattern. **Both bodies join the
> Declared Change Set**, each gaining the tests-only exception under rung 1.

### Step 5 — A, C, G1: the three prose changes, each with a scan
RED: three scan tests, each written to fail **now** and to keep failing on a future regression —
they scan the whole `.agents/commands/` glob with a `MIN_FILES` floor (`test_stale_base_refs.py`
idiom), never a pinned line number.
GREEN: edit the three command bodies; run `/smh-sync-agents` and commit the regenerated mirrors.

### Step 6 — riders, SOP, receipt, mutants
The two memory files are already staged on this lane. SOP page updated for every usage-surface
change. Mutation sweep declared as JSON and run through `mutation_sweep.py`, drawn **from the code**.
Suite run once, on the shipping sha, through `gate_receipt.py`.

### Step 7 — file the two out-of-repo halves (G2)
One AVCH subtask for the AGY toml; one SCC-262 subtask for the skeleton toml. Both get the measured
defect, an anchor, SCOPE and ACCEPTANCE, per `audit-findings-need-a-file-anchor`.

---

## Declared Change Set

**Reconciled against `git diff --name-status 038c0f1..HEAD` after every part landed.** Rows the
sync did not actually touch are **struck**, not left as phantom scope; rows the work turned up that
plan time did not foresee are marked **+**. Three rows are still owed at the time of writing.

### Scripts and their tests

- EDIT `.agents/scripts/link-worktree-assets.py` — `repo_root()` resolves the main WORKING TREE; refuse an UNVERIFIED resolution → B1, B2
- NEW `.agents/scripts/tests/test_link_worktree_assets.py` — submodule (gitdir-file) fixture + the unverified-resolution refusal + a plain-repo characterization block → B1, B2, B3
- EDIT `.agents/scripts/jira_feed.py` — `section_body` depth-aware (opt-in per caller); `mint` reuse tests for the outline trailer; `outline` gains `--jira-project` → D1, D2, E1, E2
- EDIT `.agents/scripts/tests/test_jira_feed.py` — the `### Theme` AC shape, the flat-AC regression, the `story_statement` non-regression, the stale-description reuse, the flag parity, the armed hook's exact line → D1, D2, E1, E2
- EDIT `.agents/scripts/label_tasks.py` — story read via `ls-tree` on the lane branch; `tests_only` demotion; all blockers in `detail` → F1, F2
- EDIT `.agents/scripts/tests/test_label_tasks.py` — branch-only story source, tests-only ranking, multi-blocker detail → F1, F2
- **+** EDIT `.agents/scripts/tests/test_twin_parity.py` — `FENCED_TODAY` gains the label-tasks pair, so the shared rule is held by a FENCE rather than by matching text today → F1
- NEW `.agents/scripts/tests/test_boot_epic_branch_read.py` — the anchored Step 2b scan, one mutant per requirement → A1
- NEW `.agents/scripts/tests/test_shared_checkout_stays_on_main.py` — paragraph scan across all `.agents/commands/*.md` **and** `.agents/rules/*.md` → C1
- NEW `.agents/scripts/tests/test_story_path_is_pinned.py` — the story-dir pin in the same section as the skill invocation → G1

### Command and rule bodies

- EDIT `.agents/commands/cicd-label-tasks.md` — the tests-only rule, FENCED as `twin-law`, plus an unfenced cicd-only note on reading rung 3 from the lane branch → F1
- EDIT `.agents/commands/smh-label-tasks.md` — the same fenced rule; ⛔ the story-branch note is **deliberately not mirrored** (operator ruling: stories are app work, the command centre has none) → F1
- EDIT `.agents/commands/cicd-boot-sprint-memory.md` — Step 2b reads the epic branch's YAML, reports the disagreement, falls back when the project is between epics → A1
- EDIT `.agents/commands/cicd-write-story-tests.md` — Step 0.5 item 2 cuts the tree with the epic ref as an OPERAND; the HEAD precondition is scoped to `EnterWorktree` and names the trip back to `main` → C1
- **+** EDIT `.agents/rules/worktree-per-story.md` — the authority the command was following says the same thing at `:70`; scoping only the command would leave it disagreeing with its own rule → C1
- **+** EDIT `.agents/commands/sm.md` — the create-story route names `_bmad/bmm/stories/` → G1
- ~~EDIT `.agents/commands/cicd-write-story-tests.md` Step 1 names the story dir~~ — **already true at `:45`** before this lane; G1's live defect was `/sm`, found by re-reading the surface rather than trusting the rider text

### Regenerated mirrors — reconciled after `/smh-sync-agents -NoGlobals`

- EDIT `.agents/workflows/smh-label-tasks.md` · `cicd-boot-sprint-memory.md` · `cicd-write-story-tests.md` — all three **flipped from verbatim copy to generated thin launcher**: the edits pushed each body past `sync-agents.ps1`'s 11,500-byte ceiling
- EDIT `.opencode/commands/cicd-label-tasks.md` · `smh-label-tasks.md` · `cicd-boot-sprint-memory.md` · `cicd-write-story-tests.md` · **+** `sm.md`
- **+** EDIT `.agents/.sync-manifest.json` — the sync's own record; changes on every run and was not foreseen
- ~~EDIT `.claude/skills/{cicd-label-tasks,smh-label-tasks,cicd-boot-sprint-memory,cicd-write-story-tests}/SKILL.md`~~ — **unchanged, all four.** A skill is a thin launcher naming the command; a command *body* edit never reaches it

### Docs, board and artifacts

- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the usage changes in A, B, C, D, E, F and G1 → A2, C2
- **+** EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one row per rider. ⛔ Owed, not optional: `sop-currency.md` habit 4 puts the change story here and keeps the page in timeless present tense, and B/D/E/F had put ticket refs and dates in the spine instead. Those three passages are rewritten and one unresolvable prose path (`.git/modules/`) that had been failing `test_sops_prds_folder` T9 since `7b2ac12` is now written as the placeholder it always was
- **+** EDIT `_artifacts/_main/INDEX.md` — the session row; `check_maps.py` F2 fails without it
- EDIT `_artifacts/_memory/MEMORY.md` + NEW `_artifacts/_memory/exercise-the-real-cicd-doors.md` — the two riders that were sitting uncommitted on `main` → Z2
- NEW `…/implementation_plan.md` (this file) · `…/task.yaml` → Z1
- **owed** `…/walkthrough.md` · `…/sweep.json` · `…/gates/suite.json` → Z1

## Out of scope, and named

- `.claude/skills/bmad-create-story/SKILL.md` is **vendored BMAD**, not ours, and stays untouched.
  ⭐ **Operator ruling 2026-08-21 — BMAD is not edited AND not overridden**, so the two
  `_bmad/custom/bmad-create-story.toml` subtasks this plan originally carried are **dropped, not
  deferred**. Ground truth agrees the override was never needed: 139 story files sit under
  `_bmad/bmm/stories/` on AGY and **zero** under `_bmad-output/implementation-artifacts/`, because
  our own commands name the path at the call site. G1 makes that convention complete rather than
  patching the vendor — which is why what remains of G is one sentence in `/sm`.
- The rolling ticket's own start-up block prescribes four hand-run `acli` commands that
  `jira_feed.py start` already does better. **Fixed forward in SCC-262's description**, not here —
  SCC-244's description is the closing record of this cycle and should not be rewritten under it.

---

## Self-Audit (2026-08-21)

**Level: LEDGER+BLAST** — the Declared Change Set touches scripts other files import
(`jira_feed.py`, `label_tasks.py`, `link-worktree-assets.py`), two command/door surfaces, an armed
gate's input (`sop_currency.py`), four platform caches, and a `cicd`/`smh` twin pair. Mode:
**PRE-WORK**.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/script/command/door the plan names exists (12/12 OK, listed)
             `declared_change_set.py parse <plan>` — after one repair, 32 entries / 0 incomplete
             lane fit: zero deployable paths (backend|frontend|firebase|functions|mobile|.github) in the block
             both-machines: every command is stdlib python3 + git + acli; no venv, no bare `python`
             Scope Ledger: 11 NEW artefacts x acceptance row — every one mapped (B1-B3, A1, C1, G1, Z1, Z2)
             Ledger precondition: 16 acceptance rows, each with a named command — PASS
read:        implementation_plan.md · .agents/scripts/{link-worktree-assets,jira_feed,label_tasks,
             declared_change_set,mutation_sweep,gate_receipt}.py · .agents/scripts/INDEX.md ·
             .agents/commands/{cicd-boot-sprint-memory,cicd-write-story-tests,cicd-label-tasks,
             smh-label-tasks}.md · .agents/rules/{worktree-per-story,port-checklist}.md ·
             docs/_scc_sops_prds/workflows_testing_SOP.md · .agents/scripts/tests/test_stale_base_refs.py
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  four platform doors for both edited commands — all present (workflows / opencode / claude skill)
             twins: `label_tasks.py` backs BOTH /cicd-label-tasks and /smh-label-tasks (INDEX.md:33) — PORT REQUIRED
             callers of `link-worktree-assets.py`: 10 command bodies + worktree-per-story.md (grep -rl, listed)
             hook callers: post-commit-jira-start.sh:119 runs `jira_feed.py start` — argparse is a hook surface
             SOP: both halves in the same commit, per the armed commit-msg gate
             _artifacts/_memory/: the two riders are the AGENTS.md §7 lane write path (a sanctioned flow),
               not an edit to another session's memory — copy + cmp + restore already done, `main` is clean
             port-checklist (file in >1 repo): the two `bmad-create-story.toml` copies are FILED, not built
               here, so the six checks belong to those tickets — stated, not skipped
             sibling worktrees: `git worktree list` shows ONE tree (this lane). No landing-order dependency.
             risk_seam.py classify → {"status":"unclassified"} (placeholder; informs, never gates)
             ASSET CENSUS across all 9 local checkouts — 6 have zero linkable assets
read:        .agents/scripts/INDEX.md · .agents/commands/{cicd,smh}-label-tasks.md authority tables ·
             .agents/scripts/git-hooks/post-commit-jira-start.sh · .gitmodules · git submodule status ·
             git worktree list · the census loop's own output
verdict:     findings below
```

```
lens:        3 Pre-Mortem (bounded — attaches only, never originates)
checks_run:  the silent one, the other-machine one, the fresh-clone one, the sibling-lands-first one
read:        the surviving anchored findings from lenses 1 and 2
verdict:     three narratives attached (see the table's Consequence column); zero unattached output
```

### Findings

| # | anchor | literal text read | consequence | severity |
|---|---|---|---|---|
| 2 | `.agents/scripts/link-worktree-assets.py:44-49` + the 9-repo census | `("node_modules","dir"), ("auth_keys","dir"), (".venv","dir"), (".env","file"), (".env.local","file")` | **Was a NO-GO.** ACCEPTANCE B2 read literally refuses on zero assets; **6 of 9** local checkouts have zero, and **10 command bodies** call this at worktree-open. Every lane in those six repos becomes un-openable — a hard `worktree-per-story` gate broken in six repos to fix a bug in one. *Pre-mortem (fresh clone):* even an asset-bearing repo has none before `npm install`, so a lane opened on a freshly cloned PC refuses too. **Cleared by the Step 1 amendment** — the refusal now keys on resolution, not count. | **HIGH** |
| 1 | `.agents/commands/cicd-label-tasks.md:79` · `.agents/commands/smh-label-tasks.md:73` | `\| 1. `branch-diff` \| … \| code written beats every declaration \|` | Part F demotes a tests-only branch-diff in the shared script; both doors publish the old ranking as law. Ships an engine that contradicts its own doors — the measured `cicd`/`smh` drift. *Pre-mortem (other session):* the next agent follows the door, not the script, which is this whole ticket's origin story. **Cleared** — both bodies + their five caches added to the change set. | **HIGH** |
| 3 | `.agents/scripts/jira_feed.py:216-220` | `body = section_body(text, _STORY_HEAD_RE.search(text))` | `story_statement` shares the function Part D changes; depth-awareness silently grows every `## Story` block that has `###` children. **Cleared** — the regression case is now required to carry a `###` under `## Story`; a flat story cannot detect it. | **MED** |
| 4 | `.agents/scripts/git-hooks/post-commit-jira-start.sh:119` | `if "$PY" .agents/scripts/jira_feed.py start --key "$KEY" --timeout 10 --apply` | Part E edits the argparse surface an **armed hook** reaches on the first commit of every `chore/ · claude/ · epic/` branch, in every repo. *Pre-mortem (the silent one):* VS Code hides hook output, so a broken `start` reads as a clean commit. **Cleared** — a case pinning `start`'s flags rides with E2. | **MED** |

### Observations (uncounted — belief, not check)

- The lobby carries `.env` + `node_modules`, so **B1 and B2 cannot be proved by running the script
  here**. The gitdir-file fixture is load-bearing, not decoration.
- `Projects/sudo-project-skeleton` is an **uninitialized** submodule (empty dir). `cd` into it and
  `git` walks up to the lobby and answers about the wrong repo — the reason G's template half is
  filed rather than "just done".
- Seven riders in one lane is the largest consolidated cycle so far (cycle 3 ran three). The
  mitigation is ordering — scripts with real tests first, prose scans last — not fewer parts.

### Landing-order dependencies

None. `git worktree list` shows exactly one tree (this lane), and `origin/main` is at `038c0f1`
with nothing ahead.

```
Audit verdict: GO
```

**Read that verdict precisely:** the plan **as first written was a NO-GO on finding 2** — its
consequence broke a hard gate. The GO is against the **amended** plan above, where Step 1's refusal
keys on resolution instead of asset count. The deviation from SCC-255's literal ACCEPTANCE B2 is the
one thing here the operator may want to overrule.
