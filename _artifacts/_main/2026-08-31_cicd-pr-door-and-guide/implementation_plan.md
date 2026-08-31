# Implementation Plan — SCC-347 · the cicd flow gains a PR door and a project overview guide

**Parent:** [SCC-347](https://sudo-command.atlassian.net/browse/SCC-347) · **Riders:** SCC-356 (Part A) · SCC-357 (Part B)
**Lane:** `chore/SCC-347-cicd-pr-door-and-guide` (CONSOLIDATED — one tree, one plan, two parts; same repo, same lane class, B edits a file A rewrites, so they run in order A → B)
**Close:** `/smh-close-task-merge-tree --expect-key SCC-347` — riders flip first, parent last.
**Out of this lane (ticket per repo):** [AVCH-111](https://sudo-command.atlassian.net/browse/AVCH-111) ports the `main-write-gate` ruleset + CI into AGY; [AVCH-112](https://sudo-command.atlassian.net/browse/AVCH-112) writes AGY's first `docs/project_overview_guide.md`. Both run AFTER this lane lands: AVCH-111 ships through the reshaped door (its `.github/` edit is deployable), AVCH-112 fills the file Part B's check WARNs about.

## Goal

Two things the operator found in the smh (lobby) side that the cicd (project) side lacks:

1. **The lobby lands on `main` through a pull request the operator merges; projects still merge locally and push `main` with a token.** [`/cicd-push-e2e`](../../../.agents/commands/cicd-push-e2e.md) Step 4 merges `--no-ff`, mints, pushes. Measured today: AGY `main` has no ruleset (`gh api repos/{owner}/{repo}/branches/main/protection` → 404 *Branch not protected*), so a merge made on GitHub's servers — the web button — is entirely unguarded there, the exact PR #2 hole SCC-118 closed here. Part A gives the door the lobby's shape: gate locally, push the epic tip, open the PR, STOP; `--after-merge <KEY>` finishes.
2. **The lobby's SOP is kept honest by a currency gate; projects have no "what we built and how it flows" page at all.** AGY carries a repo-map, a 19 KB project-context, a 110 KB PRD, seven architecture files — zero diagrams, none written for a human reader. Part B defines `docs/project_overview_guide.md` (a centre template), keeps it current at the STORY close-out, and uses its per-epic diff as the index into the PRD at the EPIC ship — a mandatory reconcile that either runs `/bmad-correct-course` or records `PRD: unchanged`. **The PRD is requirements and is never rewritten from the guide** (operator ruling this session).

**Why story-level, not a commit gate:** the lobby's `sop_currency.py` fires on five narrow paths, so a fire means something. A project's surface is `backend/` + `frontend/`, which every commit touches; a commit gate there fires always, the opt-out becomes reflex, and (per `sop-currency.md` itself) a reflexively opted-out gate checks nothing. Stories are the project's unit of change; the check lives there.

## Ground truth (verified this session, all from command output)

- `cicd-push-e2e.md` Step 4: `git merge … --no-ff`, `mint-push-token.sh`, `git push origin main`; Step 6 prunes; Step 6.5 moves the epic ticket. No `--after-merge`. No PRD mention anywhere in the file.
- `smh-close-task-merge-tree.md` Step 3 (lines 395–497) is the shape to mirror: `gh pr create --base main --head "$BRANCH" --fill`, print URL, STOP; `--after-merge` verifies with `git merge-base --is-ancestor`, reads the PR number off `git log -1 --format=%s origin/main`.
- `main_write_gate.py --mode pr` (line 275) owes receipts ONLY when the manifest's `close_command` is `smh-close-task-merge-tree`; `test_main_write_gate_ci.py` A5c pins that a manifest naming `cicd-push-e2e` owes nothing. So Part A needs no flight event and no receipt; AVCH-111 decides what AGY's gate demands.
- Tests that pin the CURRENT shape and must move with it: `test_door_preflight_order.py:322-326` ("does NOT wait on CHECK_NAME" — stays true; "still mints + pushes main unchanged" — flips); `test_stale_base_refs.py:62` exempts the `main...origin/main # must be 0 0` line — the line is KEPT in `--after-merge` (after `git pull --ff-only origin main`), so the exemption stays and its "no rows ruling nothing" guard stays satisfied; `test_command_surfaces.py:664-680` door-parity regression control diffs the live door against the pre-`ea8fe97` bytes — a content diff, still `stale` after the rewrite (run to confirm).
- `test_twin_parity.py`: `cicd-push-e2e.md` is in the UNPAIRED list with its reason; untouched.
- `closeout_preflight.py`: checks are plain functions called in `main()` (line ~520), `integration_branch(project)` (line 29) resolves the epic branch, `wf.git([...], project)` runs git; `check_artifacts` (298) finds the story walkthrough by slug — the same finder Part B's check reuses. Test harness: `test_closeout_preflight.py` builds temp repos with `lane_repo(tmp)` and blocks via `c.block(...)`.
- `test_command_surfaces.py` CS-13 E bans INSTRUCTIONS (clause-scoped) in `cicd-update-sprint-memory.md` for `git push`, `workitem transition`, `jira_feed.py devrecord`, `/cicd-prune-worktree`, `worktree remove`. Part B's new step uses none.
- `mermaid-diagram-preferences.md`: never `sequenceDiagram`; `flowchart TD/LR` only. The template says so in its own header.
- SOP: §7 push-e2e narrative at 841–875; the "Where / How it lands" table row at 1256 (*"Project repos … `/cicd-push-e2e`, unchanged — they publish no `main-write-gate`"*); the aside at 1405–1407; the hold paragraph at 1341 (*"the two door commands … mint it"* — already stale: both smh doors open PRs); the gate table row at 1532; the atlas diagram at 3809–3843. **The atlas diagrams for `/smh-close-task-merge-tree` (3845–3873) and `/smh-merge-multiple-workingtrees` (3875–3900) still draw "mint the token · push main"** while both commands open PRs — same section, fixed in the same pass (operator-profile obligation 9: in-lane, so fixed, not listed).
- Launcher regen: `.agents/scripts/sync-agents.ps1` (pwsh present on this Mac: see the port section's proof block). Sandbox may refuse `.claude/skills` writes (SCC-300); the door-parity test is the arbiter.
- Changelog: `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md`, table row `| date | ticket | what changed for the operator |` under `## 2026-08`.

## Parts

### Part A — `/cicd-push-e2e` becomes a PR door (SCC-356)

**A1 · Rewrite `cicd-push-e2e.md` Steps 4–6.5.** Steps 0–3 unchanged (bind, pin the key, resolve the branch, `ship_preflight.py`, absorb `origin/main`, the gate). Then:

- **Step 4 — Push the gated tip and open the PR, then STOP.** `cd "$PROJECT_ROOT" && env -u GITHUB_TOKEN git push origin epic/<KEY>-<slug>` (the tip that went green, absorbed main included), then `gh pr create --base main --head epic/<KEY>-<slug> --title "<KEY> ship epic/<KEY>-<slug>" --body-file <file>` whose body carries the gate evidence: suite totals, build, `E2E GATE: GREEN N/N`, the report path. Print the URL, **STOP**. No-`gh` fallback: the `compare/main...<branch>?expand=1` URL from `git remote get-url origin`. The three-form sign-off text stays; the sentence *"the click on Merge pull request is how that decision reaches GitHub"* replaces the mint. No `mint-push-token.sh`, no `git push origin main`, no `gate/**` ref in any fence. MANDATORY RULE 3 becomes *"on a deploying repo, the click IS a production deploy — know the rollback path before you open the PR."*
- **`--after-merge <KEY>` — Resuming after the click.** Step 5 verify: `env -u GITHUB_TOKEN git fetch origin main`; `git merge-base --is-ancestor epic/<KEY>-<slug> origin/main || STOP`; PR number off `git log -1 --format=%s origin/main`; `git checkout main && git pull --ff-only origin main`; the `main...origin/main # must be 0 0` line kept verbatim. Then the old Step 5 (deploy watch, live verify) → **Step 5.5 is Part B's slot** → Step 6 prune epic branch + ledger + active-context → Step 6.5 Dev Record comment naming PR #N + merge sha, epic ticket → Done. Same BEHIND check as the smh door (*is the door you are reading the pre-merge copy?*).
- Description frontmatter rewritten to the PR shape. `platforms:` stays absent (all four).

**A2 · `ship_preflight.py` docstring** line 23: *"The merge, the mint and the push stay in the command"* → *"The push of the epic tip and the PR stay in the command, where a human is watching; the merge happens on GitHub."*

**A3 · `test_door_preflight_order.py`.** The standing guard on PROJECT_DOOR becomes: no `mint-push-token.sh`, no `git push origin main`, no `gate/**` ref in its fences; `gh pr create` present; still no CHECK_NAME wait (a project may not publish the check — AVCH-111 is per repo). Docstring's *"ONE DOOR, NOT TWO"* section rewritten: both doors take the PR road; the standing guard is now against the gate/**-wait pattern, not against the PR shape. `REQUIRED_ORDER` and the mutant fixtures stay as the ordering contract's control — ⚠️ AUDIT FINDING F6: its comment at `test_door_preflight_order.py:233` (*"kept ONLY for the fixtures below and for `/cicd-push-e2e`, which still takes it"*) is rewritten to *"kept ONLY for the fixtures below"*.

**A4 · `git-policy.md`.** Table row for `main` (line 100): *"a pull request the operator merges — in this repo via `/smh-close-task-merge-tree`, in a project via `/cicd-push-e2e`"*. Lines 116–118 and 246–250, 256–258: project epics also ship through a PR; the server-side check per project is that project's own ticket (AVCH-111 for AGY); the local token stays as the backstop `pre-push` applies to any direct push to `main` from a machine.

**A5 · SOP + changelog + commands index.** ⚠️ AUDIT FINDING F3: `.agents/commands/INDEX.md:56` describes `cicd-push-e2e` as *"`--no-ff` merge, epic branch deleted after"* and `:58` describes `smh-close-task-merge-tree` as *"`--no-ff` merge to `main` … Invoking it IS the merge sign-off"* — the first goes stale with A1, the second already is (that door opens a PR since SCC-183). Both rows rewritten here; Lens 2's command-file row demands the index move with the door. ⚠️ AUDIT FINDING F5: the atlas *italic blurbs* above the two smh diagrams (SOP 3845–3847 *"wait for GitHub's `main-write-gate` … mint the token with your words, push `main`"*, and 3875–3881) carry the stale road in prose as well as in the diagram — both blurbs corrected with their diagrams. §7 push-e2e section (841–875) rewritten to the PR shape; table row 1256; aside 1405–1407; hold paragraph 1341 (no door mints today — the token gates direct pushes); gate table row 1532 (*"End-to-end gate — local, via `/cicd-push-e2e`, before the PR is opened"*); the push-e2e atlas diagram; the two stale smh atlas diagrams corrected to the PR road. One changelog row.

**A6 · Launchers + suite.** `pwsh .agents/scripts/sync-agents.ps1` regenerates the launcher (description changed); `python3 .agents/scripts/tests/run_all.py` green (⚠️ AUDIT FINDING F1: the runner is under `tests/`, not `scripts/` — `find` proved `.agents/scripts/run_all.py` does not exist; a builder running the wrong path reads *No such file* as a skipped gate); `sop_currency` passes with the SOP staged (no `[sop-ok]`).

### Part B — the project overview guide: story-level currency, epic-level PRD reconcile (SCC-357)

**B1 · `.agents/templates/project_overview_guide.md`** — ⚠️ AUDIT FINDING F2: `.agents/templates/` does not exist on disk, and `.agents/INDEX.md:15` still reads *"`templates/` | `project-template/` — the scaffold `/smh-new-project` clones"* while `docs/workspace-standard.md:133` records that scaffold as retired 2026-08-07. B1 creates the directory and rewrites that INDEX row to the new truth (*"`templates/` | `project_overview_guide.md` — the skeleton a project copies to `docs/`"*) in the same commit; `check_maps` may regenerate the inventory beside it. The skeleton every project copies to `docs/project_overview_guide.md`. Header states what it is (what was BUILT and how it flows — for a human; the PRD says what was WANTED and is never rewritten from this page) and the currency law (edited at every story close-out that changes behaviour, or the walkthrough says why not). Sections: §1 What this is (one paragraph) · §2 How a request flows (`flowchart TD`, one per major entry point) · §3 The parts and their contracts (table: part · owns · talks to · lives at) · §4 Where things live (points at `repo-map.md`, never duplicates it) · §5 What changed, per epic (table: epic · what changed in the system · shipped) · §6 Glossary. HTML-comment guidance per section; the mermaid rule named in the header.

**B2 · `workspace-standard.md`**: a `docs/project_overview_guide.md` line under *Supporting files every workspace carries* (dev workspaces), a conversion-checklist row, and a table row beside `repo-map.md`.

**B3 · `cicd-update-sprint-memory.md` — new Step 3.5 "Keep the project overview guide current".** Read `PROJECT_ROOT/docs/project_overview_guide.md`. If this story changed a flow, a part, a contract or where something lives → edit the guide (flowcharts only) and add/extend the epic's row in §5; the edit rides the story branch. Otherwise write `Project overview guide: unchanged — <reason>` under the walkthrough's `## Evidence`. File absent → write `Project overview guide: absent — <project> has no guide yet` and carry on (AVCH-112 owns the first edition). Uses none of CS-13 E's banned instructions.

**B4 · `cicd-close-story-merge-tree.md` Step 2**: `docs/project_overview_guide.md` named in the explicit-path commit list.

**B5 · `closeout_preflight.py` `check_overview(project, key, rep, branch)`**, wired in `main()` after `check_artifacts`. Guide path absent → `warn("overview", "no docs/project_overview_guide.md yet — the save's guide step records `absent`")`. Present: `git diff --name-only <integration_branch(project)>...HEAD -- docs/project_overview_guide.md` non-empty → `info` (edited on this lane); else the story walkthrough (same finder as `check_artifacts`) matches `^\s*(?:[-*>]\s*)?\**Project overview guide:\**\s*(unchanged|absent)\b` → `info`; neither → `err("overview", "guide neither edited nor accounted for — /cicd-update-sprint-memory Step 3.5 never ran")`. ⚠️ AUDIT FINDING F4: this script is also run by `/cicd-prune-worktree` (`cicd-prune-worktree.md:43`) and `/cicd-merge-epic-workingtrees` (`cicd-merge-epic-workingtrees.md:71`), so once a project HAS a guide, an `err` here would block the prune or the set-landing of every story saved BEFORE Step 3.5 existed — a red with no remedy the operator can act on. Scope it the way `walkthrough_roster.py:40` scopes its roster demand: a literal `OVERVIEW_CUTOFF = "<the date this lane lands>"`; a walkthrough whose `## Code Review (<date>)` header predates the cutoff → `info("overview", "predates the guide law — exempt")`, never `err`. No `## Code Review` header at all → treat as pre-cutoff (legacy). The cutoff is a literal date, not "the day it lands" (F28's lesson in that file). Tests in `test_closeout_preflight.py`, block `OV · SCC-357`: absent→warn · edited→info · line→info · neither→err · regex positives/negatives · pre-cutoff walkthrough → info · a mutant control (a line reading *"Project overview guide: updated"* does NOT satisfy).

**B6 · `cicd-push-e2e.md --after-merge` Step 5.5 "Reconcile the PRD against what shipped".** `git diff <merge-sha>^1..<merge-sha> -- docs/project_overview_guide.md` is the epic's whole guide delta (first parent vs merge). Empty → write `PRD: unchanged — epic shipped as specified (guide delta empty)` into the ledger row and the epic ticket comment. Non-empty → open ONLY the PRD sections `epics.md` maps to this epic's FRs; each divergence (guide says X, PRD says Y) → invoke `/bmad-correct-course` on a `chore/<PROJECT-KEY>-<slug>-prd-reconcile` lane (sprint-change-proposal + PRD/architecture edit, landing through the PR door) — or, no divergence → the `PRD: unchanged` line. Never edit the PRD in place on `main`. A test pins the wiring: `test_command_surfaces.py` gains a block asserting the `--after-merge` section contains `PRD: unchanged` and `/bmad-correct-course` AFTER the `--is-ancestor` fence and BEFORE the `transition --key` fence, with a reordered-mutant control.

**B7 · SOP §7**: one paragraph on the three currency levels (commit → SOP, lobby only · story → overview guide · epic → PRD via correct-course); changelog row.

## Declared Change Set

- EDIT `.agents/commands/cicd-push-e2e.md` — Steps 4–6.5 to the PR shape + `--after-merge` → A1 · Step 5.5 PRD reconcile → B6
- EDIT `.agents/scripts/ship_preflight.py` — docstring only → A2
- EDIT `.agents/scripts/tests/test_door_preflight_order.py` — PROJECT_DOOR guard + docstring → A3
- EDIT `.agents/rules/git-policy.md` — `main` row, write-gate scope paragraphs → A4
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §7, tables, asides, three atlas diagrams → A5 · currency paragraph → B7
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — two rows → A5, B7
- EDIT `.agents/.sync-manifest.json` + generated launchers and mirrors as the generator emits: `.claude/skills/cicd-push-e2e/SKILL.md` · `.opencode/commands/{cicd-push-e2e,cicd-update-sprint-memory,cicd-close-story-merge-tree}.md` · `.agents/workflows/{cicd-push-e2e,cicd-update-sprint-memory,cicd-close-story-merge-tree}.md` (⚠️ AUDIT FINDING F7: all three edited commands have opencode + Antigravity mirrors; the hand-authored `.claude/skills/` launchers for the two story commands carry no steps and are left alone — CS-05) → A6
- EDIT `.agents/commands/INDEX.md` — rows 56 and 58 → A5 (F3)
- EDIT `.agents/INDEX.md` — the `templates/` row → B1 (F2)
- NEW `.agents/templates/project_overview_guide.md` → B1
- EDIT `docs/workspace-standard.md` — three rows → B2
- EDIT `.agents/commands/cicd-update-sprint-memory.md` — Step 3.5 → B3
- EDIT `.agents/commands/cicd-close-story-merge-tree.md` — Step 2 path list → B4
- EDIT `.agents/scripts/closeout_preflight.py` — `check_overview` + wiring → B5
- EDIT `.agents/scripts/tests/test_closeout_preflight.py` — block OV → B5
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — after-merge reconcile wiring block → B6
- EDIT `.agents/scripts/tests/test_stale_base_refs.py` — only if the `0 0` line moves out of a fence (expected: unchanged) → A1
- NEW `_artifacts/_main/2026-08-31_cicd-pr-door-and-guide/{implementation_plan.md,task.yaml,tickets/SCC-356.md,tickets/SCC-357.md,walkthrough.md,sweep.json,sweep-b.json,sweep-c.json}` — planning surfaces + the three sweep tables
- EDIT `_artifacts/_main/INDEX.md` — the lane's ledger row → A6 (added when `check_maps` F2 refused the receipt run; a real red, not a hypothetical)

### Amendment ledger (reconciled against the real diff before the review)

Four paths landed that the first cut did not declare, each with why:

- EDIT `.agents/skills/cicd-push-e2e/SKILL.md` and EDIT `.roo/commands/cicd-push-e2e.md` — the
  generator emits **five** mirror surfaces for a command whose description changed, not the three
  the plan listed (`.agents/skills/` is the launcher master and `.roo/` is Zoo, platform 5 since
  SCC-349). Nothing was hand-edited; both are `sync-agents.ps1` output.
- EDIT `.agents/INDEX.md` — audit finding F2, already written into B1: the `templates/` row named a
  scaffold retired 2026-08-07, and B1 creates that directory.
- EDIT `.agents/commands/INDEX.md` — audit finding F3, already written into A5.
- EDIT `docs/doc-graph.json` · `docs/doc-graph.md` — regenerated and staged by the `pre-commit`
  hook itself on every doc-touching commit. Machine-owned; never hand-edited.

⚠️ **One acceptance row was worded wrong and is corrected here, not quietly met.** Row 5 said the
template must contain no `sequenceDiagram`. It contains exactly one — inside the HTML comment that
**forbids** it, which is the `[[comment-literal]]` inversion this house has a memory about. The real
property is *no `sequenceDiagram` inside a mermaid fence*, and that is what was checked: **one**
mermaid fence, and it is a `flowchart TD`. (The amendment first said "4 fences" — a count written
from the plan's own §2 sentence, *"one per major entry point"*, rather than from the file. A
correction that carries an unmeasured number is the defect it is correcting, one layer up:
`grep -c '```mermaid'` returns `1`.)

## Port checklist (MANDATORY RULE 5)

Trigger test — does any file in SCOPE exist in more than one repo? Proof, run 2026-08-31 from the lobby:

```
AGY lacks .agents/scripts/closeout_preflight.py
AGY lacks docs/workspace-standard.md
AGY lacks .agents/commands/cicd-push-e2e.md
AGY lacks .agents/commands/cicd-update-sprint-memory.md
AGY lacks .agents/templates/project_overview_guide.md
ls: Projects/AGY_AVIATIONCHAT/docs/project_overview_guide.md: No such file or directory
```

AGY is a thin project (its `.agents/INDEX.md` §Not here); no SCOPE file has a twin, so the six checks do not fire. The two AVCH tickets are NEW files in AGY, not ports: AVCH-111 adapts `main-write-gate.yml` + `main_write_gate.py` (that plan carries its own port section — the lobby copy is the source and both will differ by design: repo name, check scope); AVCH-112 instantiates the template.

## Build order

A1 → A2 → A3 → A4 → A5 → A6 (suite green, launchers) → B1 → B2 → B3 → B4 → B5 → B6 → B7 → suite green again. Commits: `SCC-356 …` leads Part A commits, `SCC-357 …` Part B; the SOP rides each part's commit so `sop_currency` never needs `[sop-ok]`.

## Acceptance (the checkable list)

1. `grep -c "mint-push-token.sh\|git push origin main" <fences of cicd-push-e2e.md>` = 0; `gh pr create --base main` present; `--after-merge` section present with `merge-base --is-ancestor`. `test_door_preflight_order.py` green with the flipped guard.
2. `--after-merge` carries Step 5.5 with `PRD: unchanged` and `/bmad-correct-course` between the ancestor fence and the ticket transition; the new `test_command_surfaces.py` block green, its reordered mutant red.
3. `cicd-update-sprint-memory.md` has Step 3.5 teaching all three states — `Project overview guide: edited|unchanged|absent - <reason>` — with an **ASCII hyphen**, which is what `_OVERVIEW_LINE_RE` was written against and what the command emits. (The row first pinned an em dash; the regex ends at the state word and is indifferent to the dash, so the literal in this row was never the property under test. `test_closeout_preflight.py` OV3b pins both spellings.) CS-13 E still clean; `test_command_surfaces.py` block CS-20 pins the ALLOW half.
4. `closeout_preflight.py --story X` on a temp repo: absent→WARN, edited→INFO, line→INFO, neither→ERROR (block OV, 6+ checks green).
5. `.agents/templates/project_overview_guide.md` exists, contains no `sequenceDiagram`, ≥1 `flowchart`; `workspace-standard.md` names it three times.
6. `python3 .agents/scripts/tests/run_all.py` green; **every commit touching a usage surface stages the SOP**; door-parity green after sync; SOP changelog carries two rows. (The row first read *"without `[sop-ok]`"*, absolutely, and the lane used it twice — correctly. `sop-currency.md` names `_artifacts/` history and the gate's own tests as NOT usage changes, so an artifacts-only or test-only commit has no SOP edit to stage and the logged opt-out is the designed answer, not a bypass. An acceptance row that forbids the documented escape makes the honest commit look like a violation, which is how an opt-out stops being read at all.)

## Batch approval

**Batch approval (2026-08-31):** "approved" — the operator's verbatim word this turn, given at the `/smh-plan-task SCC-347` Step 5 stop. Covers the plans that stop listed, and only those: **SCC-356** (Part A) and **SCC-357** (Part B), this plan as it stood at `5738d7d2` (`Audit verdict: GO` recorded at that commit) — recorded at `acb02585`.

Planning scope only, per `000-PLAN-FIRST-GATE` § "One approval MAY cover several plans" clause 4: it is not merge approval and not a ticket transition. Edit either part's plan after this line and that part's gate re-arms at `/smh-quick-dev` Step 1.5.

## Self-Audit (2026-08-31)

**Level:** LEDGER+BLAST (commands, a rule, a script others import, a gate-adjacent test, the SOP) · **Mode:** PRE-WORK
**Subject:** `chore/SCC-347-cicd-pr-door-and-guide` @ 8a1b3cbf (= origin/main; no sibling worktree carries changes)

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every declared path exists (20 `ls` probes: 19 OK, 1 MISSING → F1) · NEW paths absent (template, guide) · declared_change_set.py parse → present, every bullet mapped · plan step refs A1–A6/B1–B7 exist · both machines: python3/python noted, pwsh present (/opt/homebrew/bin/pwsh) and native on the PC · lane fit: no deployable path in the set (generated launchers under .claude/ are toolkit, not product) · Scope Ledger: NEW template ← acceptance row 5; planning surfaces carved out · precondition: parent SCC-347 carries no ACCEPTANCE block, the riders' `## Plan` rows do (SCC-356: 8, SCC-357: 7, each an observable) — met via the subtasks
read:        .agents/commands/cicd-push-e2e.md (whole) · cicd-update-sprint-memory.md (whole) · cicd-close-story-merge-tree.md:125-220 · smh-close-task-merge-tree.md:280-330,395-520 · closeout_preflight.py:29-60,298-364,462-545 · ship_preflight.py header · main_write_gate.py header + :275 · test_door_preflight_order.py:1-70,226-240,300-340 · test_command_surfaces.py:655-685,715-730,2074-2125 · test_stale_base_refs.py:55-70 · test_twin_parity.py PAIRS/UNPAIRED · test_main_write_gate_ci.py:660-700 · git-policy.md:95-132,228-262 · SOP 841-875,1236-1262,1336-1350,1400-1412,1528-1536,3809-3900 · SOP changelog head · workspace-standard.md:140-208 · mermaid-diagram-preferences.md · .agents/INDEX.md:12-18 · .agents/commands/INDEX.md:56-58 · walkthrough_roster.py:14-40,104-114 · `find -name run_all.py` · `find -type d -name templates`
verdict:     findings below (F1, F2)
```

```
lens:        2 Parity + Blast
checks_run:  command files → four doors: .claude/skills/cicd-push-e2e (generated, carries the description), .opencode/commands + .agents/workflows mirrors exist for all three commands (F7); commands/INDEX.md rows 56/58 (F3) · rule change → workflow_lint _RULE_POINTERS ("git-policy","git-mutating") — push-e2e already cites git-policy; no new pointer needed · script change → closeout_preflight callers: cicd-merge-epic-workingtrees.md:71, cicd-prune-worktree.md:43, cicd-code-review, cicd-update-sprint-memory, cicd-close-story-merge-tree, scripts/INDEX.md; no .githooks caller; signature unchanged (new check reads existing args) → F4 on consequence · gate/hook: none armed or disarmed · path move/rename/delete: none · SOP + surfaces same commit: build order states it · memory store: untouched · >1 repo: port section proves no SCOPE file exists in AGY (6 probes) — checks do not fire · twins: cicd-update-sprint-memory / cicd-close-story-merge-tree / cicd-push-e2e all in test_twin_parity UNPAIRED with reasons — no port · siblings: fetched origin/main; `git worktree list` = main checkout + this lane; diff origin/main...HEAD empty in both; only this lane's untracked planning folder · risk_seam classify → unclassified, root = lobby (correct, SCC-289)
read:        .agents/commands/INDEX.md:56,58 · workflow_lint.py:71 · `grep -rln closeout_preflight` · test_twin_parity.py:138-162 · `git worktree list` + per-tree diff/status · risk_seam.py output · .claude/skills/cicd-update-sprint-memory/SKILL.md:1-20 · walkthrough_roster.py CUTOFF
verdict:     findings below (F3, F4, F5, F6, F7)
```

```
lens:        3 Pre-Mortem (bounded — attaches to F1 and F4 only)
checks_run:  the other-machine narrative on F4: a PC session runs /cicd-prune-worktree on an AGY story saved in July, after AVCH-112 lands the guide → `overview` ERROR, exit 2, prune refused, and the only "remedy" is to re-run a save on a story already Done — the dated cutoff removes that path · the wrong-path narrative on F1: `python3 .agents/scripts/run_all.py` → *No such file*, which the door's own Step 1.5 warns reads as "no gate here"; the builder ships a red suite as green
read:        the two findings above; cicd-prune-worktree.md:43
verdict:     no unattached output
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `closeout_preflight.py:462` + `cicd-prune-worktree.md:43` | `python3 .agents/scripts/closeout_preflight.py --story <id> --project <PROJECT>` | B5's `err` blocks prune / set-landing for every pre-law story once a guide exists (F4) | important — fixed in B5: dated `OVERVIEW_CUTOFF` |
| `implementation_plan.md` A6 + `find -name run_all.py` → `.agents/scripts/tests/run_all.py` | (plan) `python3 .agents/scripts/run_all.py` | the named gate does not exist; a builder reads *No such file* as skipped (F1) | medium — fixed in A6, acceptance 6 |
| `.agents/INDEX.md:15` | `templates/ \| project-template/ — the scaffold /smh-new-project clones` | B1 creates a directory the index describes as something retired 2026-08-07 (`workspace-standard.md:133`) (F2) | medium — fixed in B1 + change set |
| `.agents/commands/INDEX.md:56` | `--no-ff merge, epic branch deleted after` | index describes the road A1 removes; Lens 2 command-file row (F3) | medium — fixed in A5 + change set |
| SOP `3845-3847` | `wait for GitHub's main-write-gate on the exact merge commit, mint the token with your words, push main` | the blurb, not only the diagram, carries the stale road (F5) | low — fixed in A5 |
| `test_door_preflight_order.py:233` | `kept ONLY for the fixtures below and for /cicd-push-e2e, which still takes it` | comment contradicts A3 after the flip (F6) | low — fixed in A3 |
| `.agents/workflows/` + `.opencode/commands/` listings | `cicd-close-story-merge-tree.md cicd-push-e2e.md cicd-update-sprint-memory.md` (both dirs) | three commands' mirrors regenerate, not one (F7) | low — fixed in change set |

### Observations (uncounted)

- `test_command_surfaces.py:664-680` door-parity regression control diffs the live door against the pre-`ea8fe97` bytes and expects `stale`; the rewritten door still differs in content, so it should hold — confirm by running, and if the verdict function keys on `mint-push-token` presence rather than content, the control needs its own amendment (say so in the walkthrough).
- `~/.codex/skills` lists no `cicd-*` launchers on this Mac (count 0); whether that is by design (`platforms:` absent = all four) or a stale Codex cache is the sync's call at A6 — report the per-surface counts it prints.
- The operator's parent ticket is prose without an ACCEPTANCE block; the checkable list lives in this plan and in the two riders' `## Plan` rows. Acceptable per `/smh-plan-task` Step 1's authority order (ticket → intent this session → the plan's 2–6 statements).

**Sibling landing-order dependency:** none — no other lane is live in this repo.

Audit verdict: GO
