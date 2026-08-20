---
IsArtifact: true
ArtifactMetadata:
  title: SCC-210 — rebalance the cicd close-out (door · memory · prune)
  type: implementation_plan
  date: 2026-08-20
---

# SCC-210 — Rebalance the cicd close-out

**Ticket:** [SCC-210](https://sudo-command.atlassian.net/browse/SCC-210) · **Lane:** `chore/SCC-210-close-out-rebalance`
(worktree `.claude/worktrees/SCC-210-close-out-rebalance`, cut from `origin/main` @ `fe0f211`) ·
**Close:** `/smh-close-task-merge-tree` · **review-runtime:** fan-out

**Source of truth:** the ticket description (= [SCC-210-implementation-plan.md](_artifacts/_main/2026-08-17_SCC-197-wave2-twin-parity/SCC-210-implementation-plan.md),
measured at `fd22097`). Every line number below was **re-measured at `fe0f211`** on 2026-08-20; where the
ticket's number drifted, this file carries the live one.

## 1. Goal — in one paragraph

Three commands, each doing the job its name says, in the same shape as the Task-lane close-out.
**`/cicd-close-story-merge-tree`** is the door you type to close a story: gate → run sprint-memory →
land on the epic branch → file the Dev Record → move the ticket → prune. **`/cicd-update-sprint-memory`**
keeps its name and shrinks to exactly what the name says (route learnings, update board / story /
active-context, hold the budget) and is still invocable on its own. **`/cicd-prune-worktree`** (was
`cicd-close-workingtree`) is the disk utility, called by the door and by `/cicd-merge-epic-workingtrees`.
The defect this removes: today the Jira `Done` write sits at
[cicd-update-sprint-memory.md:160-161](.agents/commands/cicd-update-sprint-memory.md#L160-L161), ~100 lines and
three STOPs (`:246` conflict, `:254` red gate, `:269` rejected push) **before** the landing push at
[:258](.agents/commands/cicd-update-sprint-memory.md#L258). A stopped landing leaves code on one disk under a
ticket that reads Done. After this, the ticket moves only after the push returns 0.

## 2. Decisions that need your eye (the Woz part)

1. **CO-01 contradicts §6 of the ticket, and §6 wins.** CO-01 says "replace the hand-written `acli …
   transition` with `jira_feed.py finish`". §6 DO-NOT says "Do not use `jira_feed.py finish` in the story
   door — its merge check hardcodes `origin/main`". **Re-measured: true** —
   [jira_feed.py:1789-1790](.agents/scripts/jira_feed.py#L1789-L1790) fetches `origin main` and asks
   `merge-base --is-ancestor tip origin/main`; a story tip is never an ancestor of `main` until the epic ships,
   so the door would hold every story forever. **Decision:** the door keeps `acli jira workitem transition
   … --status "Done" --yes`, relocated **after** the landing push (CO-03). What we lose until the follow-on:
   an open `- [ ]` in a story walkthrough cannot hold the ticket. What we keep from CO-01's intent: the
   `check-actions` refusal (CO-02) — it reads only the walkthrough, no merge check, so it is safe in the
   door. The follow-on (teach `finish` a `--landing-target`) is recorded in the Dev Record, **not minted**
   (review findings are not a work queue).
2. **Only ONE name retires: `cicd-close-workingtree`.** `cicd-update-sprint-memory` keeps its name. So
   "no file outside `_artifacts/` references a retired name" is a grep for one string. The 116 files that
   name `cicd-update-sprint-memory` are a **semantic re-point, hand-checked per hit**: every place that
   says "invoking it IS the sign-off / Step 7 lands / it moves the ticket / it prunes" now means the door;
   every place that says "routes learnings / prunes context / updates the board" still means sprint-memory.
3. **Platform doors.** `cicd-update-sprint-memory` and `cicd-merge-epic-workingtrees` declare
   `platforms: [opencode, antigravity]` and reach Claude/Codex through **hand-authored** launcher skills
   (pinned by `test_command_surfaces.py` CS-05 at
   [:664](.agents/scripts/tests/test_command_surfaces.py#L664)). **Decision:** the door and the utility
   get the same treatment — `git mv` the hand-authored skill dir for the utility, author one for the door
   (copy the shape), keep `platforms: [opencode, antigravity]` on both command files so the generator never
   competes with the hand door. CS-05's list gains the two new names and loses the old one.
4. **Twin parity: record, don't pair.** `cicd-close-story-merge-tree` and `smh-close-task-merge-tree` have
   different stems, so the deriver
   ([test_twin_parity.py:218-232](.agents/scripts/tests/test_twin_parity.py#L218-L232)) will not auto-pair
   them; they become **unpinned** and the completeness row goes RED unless recorded. **Decision:** enter
   both new names in `NOT_PAIRED` with the reason (landing target differs — epic branch vs `main`; the smh
   door's twin-law fences are PR-road specific). Promoting them to `PAIRS` would mean fence-by-fence law
   parity — a design of its own, out of scope here, and said so in the entry.
5. **Where the story `done` flip lives: sprint-memory (unchanged).** The ticket's §3 keeps Step 4
   (`story_status.py set <id> done`) in sprint-memory. It is a **file** write that rides the branch, so a
   stopped landing publishes nothing — the defect is only the remote ticket write, which moves. The door
   invokes sprint-memory as its Step 1, so the flip still happens only inside an operator-invoked close-out.
6. **Out of this repo, out of this lane:** one hit in
   `Projects/AGY_AVIATIONCHAT/.agents/scripts/git-hooks/pre-push-main-approval.sh:10` (a comment naming
   `/cicd-update-sprint-memory` as "the epic-branch key"). Other repo, comment only, name survives →
   an AVCH follow-on line in the Dev Record, not an edit here.

## 3. Acceptance → the assertion that proves it (RED first)

| # | Acceptance | Assertion — must fail against today's tree |
|---|---|---|
| **A** | Three command files exist under their final names; `cicd-close-workingtree.md` does not | `test_command_surfaces.py` CS-13: `ls .agents/commands/{cicd-close-story-merge-tree,cicd-update-sprint-memory,cicd-prune-worktree}.md` all exist, old file absent |
| **B** | The retired name cannot return | CS-13: sweep `.agents/ docs/ AGENTS.md .opencode/ .claude/ _bmad/custom/` for `cicd-close-workingtree` → zero hits (`_artifacts/` and `_my_resources/` excluded by law; ⚠️ AUDIT FINDING F2: **`.claude/worktrees/` excluded too** — sibling lanes' checkouts live there and still carry the old name); mutation: re-add one reference → RED |
| **C** | The board cannot lie | CS-13: in the door, line of `--status "Done"` **>** line of `git push origin HEAD:epic/` — RED today against `cicd-update-sprint-memory.md` (161 < 258) |
| **D** | Multi-lane still prunes | CS-13: `cicd-merge-epic-workingtrees.md` Step 6 names `/cicd-prune-worktree`; the utility contains no `git push origin HEAD:epic` |
| **E** | sprint-memory is genuinely slimmed | CS-13: `cicd-update-sprint-memory.md` contains none of: `git push`, `workitem transition`, `devrecord`, `/cicd-prune-worktree`, `worktree remove` |
| **F** | Every door resolves | CS-13: for each of the three names — `.agents/commands/<n>.md`, `.agents/skills/<n>/SKILL.md`, `.claude/skills/<n>/SKILL.md`, `.agents/workflows/<n>.md`, `.opencode/commands/<n>.md` all exist (Codex reads `.agents/skills` natively) |
| **G** | The SOP tells the truth | CS-13: SOP §7 altitude table names all three new roles; the sentence "You almost never type `/cicd-close-workingtree`" is gone; `docs/doc-graph.json` carries no `cicd-close-workingtree` |
| **H** | Callers pin the lane (CO-04/05) | `test_closeout_preflight.py`: `--expect-key SCC-1` against branch `claude/SCC-2-x` → exit 2; no key segment → warn; both callers pass it |
| **I** | Freshness on the verdict (CO-06) | `test_closeout_preflight.py`: default fetches; `--no-fetch` → verdict carries `STALE`, non-zero exit |
| **J** | Memory dirt named apart (CO-07) | `test_closeout_preflight.py`: a dirty `_artifacts/_memory/x.md` reports as its own `err` carrying the park-or-leave ruling, not in the generic count |
| **K** | The other findings landed (CO-02/08/09) | CS-13 greps: door has `check-actions` before the landing commit; door has an unscoped `jira_feed.py check --key <KEY> --project`; door's sign-off sentence carries the spend clause (`spent by it`) |

**RED-first order:** C first (the defect), then A/B/E/G greps, then H/I/J script tests. Paste each failing
output and read which line raised it. All assertions are stdlib Python run via `python3`/`python` —
interpreter-neutral by construction (`run_all.py` already runs on both machines).

## 4. The step-level split (re-measured)

| Today in `cicd-update-sprint-memory.md` | Lines @ fe0f211 | Goes to |
|---|---|---|
| Step 0 bind · 0.5 absorb epic · 0.6 preflight | 16–58 | **door** (0.6 gains CO-04/05) |
| Step 1 read · 2 verify on disk · 3 route · 4 apply + `done` flip + epic close · 5 prune-context · 6 artifacts/summary/memory | 60–224 | **sprint-memory** (stays) |
| Step 4.5a transition | 160–161 | **door**, after the push (CO-03) |
| Step 4.5b Dev Record · 4.5c check | 163–195 | **door**, after the push (mirrors smh Step 4 "after the merge, never before") + CO-08 unscoped check |
| Step 7 land | 226–271 | **door** (+ CO-02 `check-actions` before the close-out commit, CO-09 spend clause at 229) |
| Step 8 prune | 273–277 | **door**, delegating to `/cicd-prune-worktree` |

## 5. Execution order (one commit per step; every commit stages the SOP or carries `[sop-ok]`)

1. **RED** — write CS-13 in `test_command_surfaces.py` + the three new cases in `test_closeout_preflight.py`;
   run; paste red. `[sop-ok]` (tests only).
2. **Rename the utility** — `git mv cicd-close-workingtree.md cicd-prune-worktree.md`; retitle; Step 1.7's
   remedy text and Step 1's "land it first using …" re-point to the door; `git mv` its hand-authored skill dir
   and retitle. SOP staged.
3. **Create the door** — `git mv cicd-update-sprint-memory.md cicd-close-story-merge-tree.md` (history follows
   the landing logic), then cut Steps 1–6 out of it and write the door body: Step 0/0.5/0.6 (CO-04:
   unbracket `--branch`/`--worktree`, add `--expect-key`, echo-check) → Step 1 *invoke
   `/cicd-update-sprint-memory`* → Step 2 `check-actions` (CO-02) + close-out commit → Step 3 land (merge gate,
   push) → Step 4 Dev Record + **transition Done** + scoped + unscoped `check` (CO-03/08) → Step 5 invoke
   `/cicd-prune-worktree` → Step 6 verify + report. Sign-off sentence + spend clause (CO-09). Preserve the
   `JIRA-HOOK` comment. `platforms: [opencode, antigravity]`. Author its hand skill. SOP staged.
   ⚠️ AUDIT FINDING F3 — CO-02's precondition: the `check-actions` STOP is armed only after the sweep over the
   project's existing story walkthroughs is recorded. **Measured 2026-08-20 (audit):** 120 AGY story walkthroughs
   (`Projects/AGY_AVIATIONCHAT/_artifacts/epic_*/**/walkthrough.md`), **0 refused** — arming is safe. Record that
   line in the walkthrough `## Evidence` and as a comment on SCC-210 at build time.
4. **Recreate the slim `cicd-update-sprint-memory.md`** — Steps 0 (bind) + 1–6 verbatim from step 3's cut,
   header rewritten: standalone-invocable, performs no landing/ticket write/prune, "invoked by the door as its
   Step 1". Update its hand skill text. SOP staged.
5. **`closeout_preflight.py`** — CO-05 `--expect-key` (required=True in the same commit as both callers),
   CO-06 `--fetch` BooleanOptionalAction default-on + `fresh` flag + three-state verdict, CO-07 memory-dirt
   split. `scripts/INDEX.md` usage line. SOP staged.
6. **Re-point every caller** (hand-checked per hit): `cicd-merge-epic-workingtrees.md` (:2, :22, :102, :136),
   `cicd-quick-dev.md` (:66, :231, :245, :251, :265, :267), `cicd-boot-sprint-memory.md` (:85, :88, :130),
   `cicd-autopilot-claude.md` (:196, :224, :226, :242, :257-258), `cicd-autopilot-opencode.md` (:176, :233),
   `cicd-write-story-tests.md` (:12, :84, :138), `cicd-dev-story-tests.md` (:184-185), `cicd-code-review.md`
   (:373), `cicd-code-review-AP.md` — ⛔ **frozen by SCC-209, not edited; recorded as an accepted stale
   mention inside an abandoned twin**, `cicd-park.md` (:19), `cicd-push-e2e.md` (:144),
   `cicd-create-epic-sprint.md` (:13), `cicd-prune-context.md` (:14, :59), `smh-close-task-merge-tree.md`
   (:2, :20, :648), `smh-merge-multiple-workingtrees.md` (:363), `commands/INDEX.md` (:47, :49, :55, :58, :86);
   rules: `constitution.md` (:17-18), `git-policy.md` (:3, :68, :256), `worktree-per-story.md` (7 hits),
   `artifacts-always-first.md` (:266, :345), `jira.md` (:165, :211, :561), `project-law.md` (:68);
   `AGENTS.md` (3 hits); `opencode-agents/bmad-sm.md`, `opus-reviewer.md`; `hooks/session-start-context.sh`
   (:26, :33); `scripts/INDEX.md`; `task_preflight.py` (:4, :86 — the `claude/` lane label string),
   `jira_feed.py` (:32, :577 docstrings), `link-worktree-assets.py` (:33, :201), `pre-push-main-approval.sh`
   (:10); tests that pin the names (`test_task_preflight.py:127,148`, `test_main_push_gate.py:308`,
   `test_twin_parity.py` NOT_PAIRED, `test_command_surfaces.py:664`, `test_jira_feed.py:793`,
   `test_workflow_lint.py:287`); `_bmad/custom/bmad-quick-dev.toml:75`; docs: `jira_manual.md` (:64, :130,
   :581), `jira_integration_guide.md` (:249), `autopilot_bmad_dev_loop.md` (:34, :89, :559, :563, :579),
   `tea_testing_guide.md` (:80, :690, :751, :783), `tea_deep_reference.md` (9 hits). SOP staged.
7. **SOP** — §7: altitude table (three rows change), "Two facts" (#2 replaced), both diagrams ("Which
   close-out do I run?" + "What calls what"), the three `###` subsections (651/672/691), the atlas entries
   (2892/2931/2970 — three diagrams redrawn to the new step lists), the system map (:265-297), the hooks
   diagram (:1661-1718 — `M`/`W` nodes), the one-typing rule (:990), and the ~20 prose rows (:81, :352,
   :1176, :1919, :1987-1994, :2194, …). Same commit as step 6 or its own — SOP is the staged doc either way.
8. **Generated surfaces** — `pwsh -File .agents/scripts/sync-agents.ps1` once (regenerates `.agents/workflows/`,
   `.opencode/commands/`, `.claude/skills/` tree copy, `.claude/hooks/`, the sync manifest, machine caches);
   `python3 .agents/scripts/generate_doc_graph.py` (doc-graph). Verify F. `[sop-ok]` if the SOP was already
   staged in 7.
9. **GREEN** — re-run CS-13 + `test_closeout_preflight.py` + `test_twin_parity.py` + `workflow_lint.py
   --toolkit-only`; then the full suite once through `gate_receipt.py run --task SCC-210 --gate suite`;
   mutation sweep (table drawn from the code: swap the Done/push order back, re-add the retired name in a
   workflow, drop `--expect-key` from one caller, make `--no-fetch` exit 0, fold memory dirt back into the
   count) via `mutation_sweep.py`.
10. `/smh-code-review` → walkthrough → Dev Record → STOP for `/smh-close-task-merge-tree`.

## 6. DO NOT (carried from the ticket, each re-checked)

- No `jira_feed.py finish` in the door (§2.1). · Never fold the utility into the door — merge-epic needs
  it per lane. · `_artifacts/` untouched (incl. the SCC-197 copy of this plan). · No hand edits to
  `.agents/workflows/`, `.opencode/commands/`, `.claude/skills/`, `.claude/hooks/`, `.sync-manifest.json`,
  `docs/doc-graph.*`. · Neither story close-out touches `main`. · The four production-door findings stay on
  their own ticket. · `cicd-code-review-AP.md` is frozen (SCC-209) — not edited. · `_my_resources/` ignored
  by law.

## 7. Blast radius + siblings

- **Sibling lanes:** `chore/SCC-235-dual-surface-blast-radius` touches only its own `_artifacts/` folder +
  memory files — zero overlap, no landing-order dependency. `chore/SCC-225-review-surface` is merged
  (PR #31); its tree awaits `--after-merge` pruning, not this lane's concern.
- **Scripts others import:** `closeout_preflight.py` is called only by the two commands being rewritten
  (+ SOP prose + its own test) — `--expect-key required=True` breaks no third caller.
  `wf_common.py`/`walkthrough_roster.py` untouched.
- **Hooks/gates:** `sop_currency.py` fires on every step above (commands, rules, scripts, AGENTS.md) — SOP
  rides every commit. `workflow_lint --toolkit-only` naming law: both new names carry the `cicd-` prefix,
  hyphens only. Twin-parity completeness row: covered by decision §2.4.
- **Other repos:** AGY's `pre-push-main-approval.sh:10` comment (§2.6) — follow-on under an AVCH key.
- **Both machines:** nothing here calls bare `python`; the PS sweep in the utility is unchanged; the sync
  runs under `pwsh` on the Mac and `powershell`/`pwsh` on the PC as today.

## Declared Change Set

- EDIT `.agents/scripts/tests/test_command_surfaces.py` — CS-13 block (A–G, K) + CS-05 hand list → A, B, C, D, E, F, G, K
- EDIT `.agents/scripts/tests/test_closeout_preflight.py` — expect-key / freshness / memory-dirt cases → H, I, J
- EDIT `.agents/scripts/tests/test_twin_parity.py` — NOT_PAIRED names → A
- EDIT `.agents/scripts/tests/test_task_preflight.py` — lane-label string re-point → A
- EDIT `.agents/scripts/tests/test_main_push_gate.py` — negative-control string re-point → A
- EDIT `.agents/scripts/tests/test_jira_feed.py` — comment re-point → A
- EDIT `.agents/scripts/tests/test_workflow_lint.py` — comment re-point → B
- DELETE `.agents/commands/cicd-close-workingtree.md` → A
- NEW `.agents/commands/cicd-prune-worktree.md` — the utility, renamed (git mv) → A, D
- NEW `.agents/commands/cicd-close-story-merge-tree.md` — the door (git mv of today's body, Steps 1–6 cut out) → A, C, K
- EDIT (wholesale rewrite) `.agents/commands/cicd-update-sprint-memory.md` — Steps 0 + 1–6 only → E
- DELETE `.agents/skills/cicd-close-workingtree/SKILL.md` → A
- NEW `.agents/skills/cicd-prune-worktree/SKILL.md` — hand door, renamed → F
- NEW `.agents/skills/cicd-close-story-merge-tree/SKILL.md` — hand door → F
- EDIT `.agents/skills/cicd-update-sprint-memory/SKILL.md` — slimmed description → F
- EDIT `.agents/scripts/closeout_preflight.py` — CO-05, CO-06, CO-07 → H, I, J
- EDIT `.agents/scripts/INDEX.md` — usage line + prose → H
- EDIT `.agents/scripts/task_preflight.py` — lane label string → A
- EDIT `.agents/scripts/jira_feed.py` — two docstring mentions → A
- EDIT `.agents/scripts/link-worktree-assets.py` — two docstring mentions → B
- EDIT `.agents/scripts/git-hooks/pre-push-main-approval.sh` — one comment → A
- EDIT `.agents/hooks/session-start-context.sh` — two lines → A
- EDIT `.agents/commands/cicd-merge-epic-workingtrees.md` — calls the utility + invoked-by text → D
- EDIT `.agents/commands/cicd-quick-dev.md` → A
- EDIT `.agents/commands/cicd-boot-sprint-memory.md` → A
- EDIT `.agents/commands/cicd-autopilot-claude.md` → A
- EDIT `.agents/commands/cicd-autopilot-opencode.md` → A
- EDIT `.agents/commands/cicd-write-story-tests.md` → A
- EDIT `.agents/commands/cicd-dev-story-tests.md` → A
- EDIT `.agents/commands/cicd-code-review.md` → A
- EDIT `.agents/commands/cicd-park.md` → A
- EDIT `.agents/commands/cicd-push-e2e.md` → A
- EDIT `.agents/commands/cicd-create-epic-sprint.md` → A
- EDIT `.agents/commands/cicd-prune-context.md` → A
- EDIT `.agents/commands/smh-close-task-merge-tree.md` → A, B
- EDIT `.agents/commands/smh-merge-multiple-workingtrees.md` → B
- EDIT `.agents/commands/INDEX.md` → A, B
- EDIT `.agents/rules/constitution.md` → A
- EDIT `.agents/rules/git-policy.md` → A
- EDIT `.agents/rules/worktree-per-story.md` → A, B
- EDIT `.agents/rules/artifacts-always-first.md` → A
- EDIT `.agents/rules/jira.md` → A
- EDIT `.agents/rules/project-law.md` → A
- EDIT `.agents/opencode-agents/bmad-sm.md` → A
- EDIT `.agents/opencode-agents/opus-reviewer.md` → A
- EDIT `AGENTS.md` → A, B
- EDIT `_bmad/custom/bmad-quick-dev.toml` → A
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §7 + atlas + diagrams + prose → G
- EDIT `docs/_scc_sops_prds/jira_manual.md` → A
- EDIT `docs/_scc_sops_prds/jira_integration_guide.md` → A
- EDIT `docs/_scc_sops_prds/autopilot_bmad_dev_loop.md` → A
- EDIT `docs/_scc_sops_prds/tea_testing_guide.md` → A
- EDIT `docs/_scc_sops_prds/tea_deep_reference.md` → A
- EDIT `docs/doc-graph.json` — regenerated, never hand-edited → G
- EDIT `docs/doc-graph.md` — regenerated → G
- EDIT `.agents/.sync-manifest.json` — regenerated by the sync → F
- EDIT `.agents/workflows/cicd-update-sprint-memory.md` — regenerated → F
- DELETE `.agents/workflows/cicd-close-workingtree.md` — purged by the sync → B
- NEW `.agents/workflows/cicd-close-story-merge-tree.md` — generated → F
- NEW `.agents/workflows/cicd-prune-worktree.md` — generated → F
- EDIT `.opencode/commands/cicd-update-sprint-memory.md` — regenerated → F
- DELETE `.opencode/commands/cicd-close-workingtree.md` — purged by the sync → B
- NEW `.opencode/commands/cicd-close-story-merge-tree.md` — generated → F
- NEW `.opencode/commands/cicd-prune-worktree.md` — generated → F
- EDIT `.claude/skills/cicd-update-sprint-memory/SKILL.md` — tree copy → F
- DELETE `.claude/skills/cicd-close-workingtree/SKILL.md` — purged by the sync → B
- NEW `.claude/skills/cicd-close-story-merge-tree/SKILL.md` — tree copy → F
- NEW `.claude/skills/cicd-prune-worktree/SKILL.md` — tree copy → F
- EDIT `.claude/hooks/session-start-context.sh` — redeployed by the sync → A
- EDIT `.opencode/commands/cicd-merge-epic-workingtrees.md` — regenerated mirror → D
- EDIT `.agents/workflows/cicd-merge-epic-workingtrees.md` — regenerated mirror → D
- EDIT `.opencode/commands/cicd-quick-dev.md` — regenerated mirror → A
- EDIT `.agents/workflows/cicd-quick-dev.md` — regenerated mirror → A
- EDIT `.opencode/commands/cicd-boot-sprint-memory.md` — regenerated mirror → A
- EDIT `.agents/workflows/cicd-boot-sprint-memory.md` — regenerated mirror → A
- EDIT `.opencode/commands/cicd-autopilot-opencode.md` — regenerated mirror → A
- EDIT `.opencode/commands/cicd-write-story-tests.md` — regenerated mirror → A
- EDIT `.agents/workflows/cicd-write-story-tests.md` — regenerated mirror → A
- EDIT `.opencode/commands/cicd-dev-story-tests.md` — regenerated mirror → A
- EDIT `.agents/workflows/cicd-dev-story-tests.md` — regenerated mirror → A
- EDIT `.opencode/commands/cicd-code-review.md` — regenerated mirror → A
- EDIT `.agents/workflows/cicd-code-review.md` — regenerated mirror → A
- EDIT `.opencode/commands/cicd-park.md` — regenerated mirror → A
- EDIT `.agents/workflows/cicd-park.md` — regenerated mirror → A
- EDIT `.opencode/commands/cicd-push-e2e.md` — regenerated mirror → A
- EDIT `.agents/workflows/cicd-push-e2e.md` — regenerated mirror → A
- EDIT `.opencode/commands/cicd-create-epic-sprint.md` — regenerated mirror → A
- EDIT `.agents/workflows/cicd-create-epic-sprint.md` — regenerated mirror → A
- EDIT `.opencode/commands/cicd-prune-context.md` — regenerated mirror → A
- EDIT `.agents/workflows/cicd-prune-context.md` — regenerated mirror → A
- EDIT `.opencode/commands/smh-close-task-merge-tree.md` — regenerated mirror → A, B
- EDIT `.agents/workflows/smh-close-task-merge-tree.md` — regenerated mirror → A, B
- EDIT `.opencode/commands/smh-merge-multiple-workingtrees.md` — regenerated mirror → B
- EDIT `.agents/workflows/smh-merge-multiple-workingtrees.md` — regenerated mirror → B
- EDIT `.opencode/agent/bmad-sm.md` — regenerated mirror → A
- EDIT `.opencode/agent/opus-reviewer.md` — regenerated mirror → A
- EDIT `_artifacts/_main/INDEX.md` — ⚠️ AMENDMENT (2026-08-20, during build): this lane's own session row. `test_check_maps.py`
  F2 fails without it (`missing row for 2026-08-20_scc-210-close-out-rebalance/ - add the INDEX row before closing out`),
  so the batch-reconcile note in `artifacts-always-first` does not cover a lane's own folder — the gate is the authority → A
- NEW `_artifacts/_main/2026-08-20_scc-210-close-out-rebalance/walkthrough.md` — the closing doc → A
- NEW `_artifacts/_main/2026-08-20_scc-210-close-out-rebalance/sweep-preflight.json` — ⚠️ AMENDMENT: the mutant
  table is TWO files, not one — `mutation_sweep.py` takes a single `test` per table, and this ticket has two
  test files. 7 mutants against `closeout_preflight.py` → H, I, J
- NEW `_artifacts/_main/2026-08-20_scc-210-close-out-rebalance/sweep-doors.json` — ⚠️ AMENDMENT: 8 mutants against
  the three command bodies and the preflight's argparse → A, B, C, E, K

> ⚠️ AUDIT FINDING F1 (applied): every regenerated mirror is declared **by path** — `declared_change_set.py diff`
> is per-file (`undeclared = changed − declared`, [:135](.agents/scripts/declared_change_set.py#L135)), so a
> "row class" covers nothing and 28 sync outputs would have read as undeclared drift at review. None is hand-edited.

## Self-Audit (2026-08-20)

**Level:** LEDGER+BLAST (command/door surfaces, a script others call, rules, a DELETE) · **Mode:** PRE-WORK ·
**Repo:** `SCC-210-close-out-rebalance` worktree, branch `chore/SCC-210-close-out-rebalance` @ `fe0f211` ·
**Plan:** this file · **Ticket:** SCC-210 (`In Progress` since this lane opened).

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every EDIT/DELETE path in the Declared Change Set exists on disk (54 EDIT + 5 DELETE → 0 missing);
             no NEW path pre-exists (12 NEW → 0 collisions); block parses (`declared_change_set.py parse` →
             present, 0 incomplete); six quoted line anchors re-read at fe0f211 (sprint-memory :160-161 / :229 /
             :258, jira_feed.py :1789-1790, test_command_surfaces.py :664, SOP :601) — all match; both-machines:
             the plan's commands are python3/pwsh, no bare `python`, no `.venv/Scripts`; lane fit:
             `lane_qualify.py` → TASK (full lane, correct door = /smh-close-task-merge-tree, no deployable path);
             Scope Ledger: 12 NEW × acceptance rows → every row filled (A/C/D/F/K for the commands + doors,
             A for the walkthrough, C for sweep.json); ticket carries 7 acceptance rows, plan 11, each with an
             observable → precondition holds.
read:        _artifacts/_main/2026-08-20_scc-210-close-out-rebalance/implementation_plan.md ·
             .agents/commands/cicd-update-sprint-memory.md · .agents/commands/cicd-close-workingtree.md ·
             .agents/scripts/jira_feed.py · .agents/scripts/declared_change_set.py · .agents/scripts/lane_qualify.py ·
             .agents/scripts/tests/test_command_surfaces.py · docs/_scc_sops_prds/workflows_testing_SOP.md
verdict:     findings below (F1, F3)
```

```
lens:        2 Parity + Blast
checks_run:  command file → four doors + commands/INDEX.md enumerated for all three names (today: opencode +
             workflow mirrors + HAND skills for the two platforms-restricted commands; generator marker
             `GENERATED by sync-agents` absent = hand-authored = never overwritten, sync-agents.ps1:644);
             command NAME → reference sweep at fe0f211: `cicd-update-sprint-memory` 116 files (32 _artifacts),
             `cicd-close-workingtree` 40 files (14 _artifacts) — every non-artifact hit is in the Declared
             Change Set; rule → `_RULE_POINTERS` (workflow_lint.py:70-100, :139): the utility keeps its
             `worktree-per-story.md` + `git-policy.md` mentions, the door keeps its header block, the slim
             sprint-memory keeps `smh-target-resolution.md` in Step 0 — lint runs RED/GREEN in step 9;
             script → callers of closeout_preflight.py: the two commands + SOP prose + its own test + INDEX
             (no hook, no third caller) so `--expect-key required=True` breaks nothing outside the diff;
             gate/hook → all four ENFORCE flags present, core.hooksPath=.githooks armed on this machine;
             SOP → staged in every commit that touches a usage surface (plan §5); `_artifacts/_memory/` →
             not touched; >1 repo → AGY carries NO copy of closeout_preflight.py or of the commands (thin
             project) — port rule clears; one AGY comment hit recorded as follow-on (plan §2.6);
             twins → deriver is identical-stem only (test_twin_parity.py:218-232), so the door never
             auto-pairs with smh-close-task-merge-tree; neither file carries a twin-law fence today (0/0/0),
             NOT_PAIRED entries are the recorded decision; siblings → fetched origin/main; SCC-235 touches only
             its own _artifacts folder + memory files (no overlap); chore/SCC-186-standing-push has an EMPTY
             diff against origin/main; risk_seam.py → `unclassified` (placeholder; informs nothing, gates
             nothing, by contract); doc-graph → generator scans `.agents/` only, excludes `_artifacts`, is run by
             nothing automatic → step 8 runs it by hand; CO-02 corpus → 120 AGY story walkthroughs, 0 refused.
read:        .agents/scripts/sync-agents.ps1 · .agents/scripts/workflow_lint.py · .agents/scripts/tests/test_twin_parity.py
             · .agents/scripts/generate_doc_graph.py · .agents/scripts/risk_seam.py · .agents/scripts/git-hooks/ ·
             Projects/AGY_AVIATIONCHAT/.agents/ · git worktree list + per-tree diff/status
verdict:     findings below (F2)
```

```
lens:        3 Pre-Mortem (attached only)
checks_run:  silent-failure narrative attached to F1 and F2; other-machine / fresh-clone / sibling-first rows
             checked for every finding — no unattached output
read:        the two lenses above
verdict:     attachments below
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `.agents/scripts/declared_change_set.py:135` | `return {"undeclared": sorted(chg - dec), "unimplemented": sorted(dec - chg)}` | the drift check is per-file; the plan's "row class" note covered 28 regenerated mirrors with no row, so `/smh-code-review` Step 2 would raise 28 *important* undeclared-drift findings. **Pre-mortem:** the reviewer dispositions them as noise in bulk and a genuinely hand-edited mirror hides among them. **Applied:** every mirror declared by path. | important |
| plan step B + `git worktree list` → `.claude/worktrees/SCC-235-dual-surface-blast-radius` | `sweep .agents/ docs/ AGENTS.md .opencode/ .claude/ _bmad/custom/` | `.claude/` contains `worktrees/`, where sibling lanes' full checkouts still carry `cicd-close-workingtree`; CS-13 would go RED on another lane's files — or GREEN on the day no sibling is open, and RED the next. **Pre-mortem:** the first failure is on the PC, where a parked tree lives. **Applied:** `.claude/worktrees/` excluded from the sweep. | important |
| ticket §9 CO-02 — `Run it once over the project's existing story walkthroughs and record the hit count in the ticket before arming the STOP` | plan §5 step 3 (before amendment) armed `check-actions` with no corpus step | an un-measured STOP on a 120-walkthrough corpus. **Measured now:** 0/120 refused. **Applied:** step 3 records the count in `## Evidence` and on the ticket. | minor |

### Observations (uncounted)

- The shared checkout's HEAD moved between two consecutive commands in this session (`main` →
  `chore/SCC-186-standing-push` → `main`): another session is live in the lobby checkout. Every command in
  this lane already pins `-C "$T"`; nothing here reads the shared tree.
- `risk_seam.py classify` returns `unclassified` for every input today — the SCC-228 placeholder; no depth
  signal was available to this audit.
- Promoting the door + `smh-close-task-merge-tree` to `PAIRS` would today be trivially green (no twin-law
  fences on either side). Left as `NOT_PAIRED` with the reason; a fence-by-fence pairing is its own design.
- `_bmad/custom/bmad-quick-dev.toml` sits under a `PLANNING` dir for the drift check, so its edit never
  reads as drift either way; it is still declared because it is a real hand edit.

**Sibling landing-order dependency:** none (zero file overlap with SCC-235; SCC-186 has an empty diff).

Audit verdict: GO
