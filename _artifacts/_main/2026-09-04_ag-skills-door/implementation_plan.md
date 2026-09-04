---
IsArtifact: true
ArtifactMetadata:
  title: SCC-394 — Antigravity's door becomes the launcher skill
  type: implementation_plan
  date: 2026-09-04
---

# SCC-394 — Antigravity's door becomes the launcher skill

**Lane:** `chore/SCC-394-ag-skills-door` · worktree `.claude/worktrees/SCC-394-ag-skills-door`
**Base:** `origin/main` @ `70154040`
**Ticket:** [SCC-394](https://sudo-command.atlassian.net/browse/SCC-394)
**review-runtime:** fan-out

---

## What changes for you, Mr. Hatter

Nothing you type changes. `/smh-quick-dev` in Antigravity still runs the same command body; it will
launch from the **skill** instead of the **workflow**, the way it already does in Claude and Codex.
Three things get better:

1. **Antigravity stops offering every house command twice.** Today each of the 39 antigravity-eligible
   commands is in its `/` menu once as a workflow and once as a skill, because every one already has a
   launcher `SKILL.md` in `.agents/skills/` and Antigravity now reads that folder as a `/` menu. That is
   the SCC-66 double door, back on one platform.
2. **The machine-global Antigravity menu moves to the path the vendor actually names.** The sync
   writes `~/.gemini/antigravity/global_workflows/`; the vendor's own shipped `migrate-workflows` skill
   scans `~/.gemini/config/` and never looks there. The new cache is `~/.gemini/config/skills/`.
3. **The deadline is met with room to spare.** Antigravity retires workflows on **2026-11-01**. After that
   date the current door is dark; after this ticket there is nothing left to go dark.

**The one tradeoff worth your attention: Codex and Antigravity now share one surface and one door.**
Both read `.agents/skills/` natively, so a launcher placed there reaches both, whatever `platforms:`
says. You can no longer give a command to Codex and withhold it from Antigravity, or the reverse. In
practice that line was already fiction: the 15 commands declared `[opencode, antigravity]` all carry a
hand-authored skill, which Codex has been reading all along. **My recommendation is to write the truth
into `platforms:` law rather than build a per-platform skill cache to preserve a split nobody uses** —
the vendor offers `skills.json` declared paths for that, and it would cost a second generated surface
to keep one command out of one menu. If a real case ever appears, that lever exists.

**The thing I measured so you do not have to worry about it:** Antigravity injects every skill's
`description:` into its context each turn. SCC-195 hit a budget on the workflow menu and cut those
descriptions to 135 characters. The skill launchers carry full descriptions. But the skill roster does
**not grow** with this ticket — all 74 house skills and BMAD's 56 are already in `.agents/skills/` and
`.agent/skills/` today — so the payload Antigravity carries after this ticket is the same 35,577
characters it carries now, minus the 4,921 the workflow menu spent. Whether Antigravity already drops
entries at that size is a **pre-existing** question; the hands step at the end measures it, and if
it does, the fix is a follow-on with a number in hand, not a guess here.

## The vendor's word (first-party, all read 2026-09-04)

| Fact | Source |
|---|---|
| "Workflows are deprecated and will be retired on **November 1, 2026**." Existing workflows keep working until then. | antigravity.google/docs/migration/workflows-to-skills |
| "Any skill located in `.agents/skills/<name>/` or `~/.gemini/config/skills/<name>/` can be invoked via `/<name>`." | same page |
| Skills are an "unrestricted bundle"; workflows have the "12,000 character limit". Skills take precedence when both exist. | same page |
| Skill = `SKILL.md` with `name` (optional, defaults to the folder) and `description` (required). Workspace path `.agents/skills/` (`.agent/` accepted as legacy), global `~/.gemini/config/skills/`. | antigravity.google/docs/skills · the extension's own `agy-customizations` skill (`~/.gemini/antigravity/builtin/skills/agy-customizations/docs/skills.md`) |
| Progressive disclosure: only names + descriptions are injected; the body loads on invocation. Workspace beats global on a name conflict. | the extension's `agy-customizations` skill |
| The shipped `/migrate-workflows` skill scans `~/.gemini/config/global_workflows/`, `~/.gemini/config/workflows/` and `<workspace>/.agents/workflows/`; it never overwrites an existing `SKILL.md` and renames the workflow to `.md.bak`. | `~/.gemini/antigravity/builtin/skills/migrate-workflows/SKILL.md` |

⛔ **Do not run the vendor's `/migrate-workflows`.** Every target `SKILL.md` already exists, so it would
change nothing except littering a generated directory with 41 `.md.bak` files. The sync engine is the
migration.

## What is on disk today (measured on `70154040`)

| Surface | Count | Note |
|---|---|---|
| commands claiming `antigravity` (not `-AP`) | **39** | `Get-CommandPlatforms` semantics |
| … with a `.agents/skills/<name>/SKILL.md` | **39** — 24 generated + 15 hand-authored | **zero missing** — the skill door already covers the whole set |
| `.agents/workflows/*.md` | **41** — 39 generated + `INDEX.md` + hand-owned `smh-adviser-board.md` | the surface this ticket deletes |
| `~/.gemini/antigravity/global_workflows/*.md` on this machine | 40 | a path no vendor doc names |
| `~/.gemini/config/skills/` on this machine | absent | the vendor's global skills path |
| `.agent/skills/` (BMAD's install for Antigravity, tracked) | 56 `bmad-*` | untouched by this ticket |
| skill descriptions Antigravity injects today | 130 skills · 35,577 chars | unchanged after; the workflow menu's 4,921 go away |

`smh-adviser-board` is the one command that declares `[claude, opencode, codex]` and carries a hand-owned
Antigravity workflow door instead of a generated one, because that door holds an INLINE-mode paragraph.
The brain already carries that law itself — `## Running without subagents — inline mode` in
`.agents/commands/smh-adviser-board.md` (the "can you spawn? if not, say so before Step 0" self-test,
`SPAWNS.md` §6) — so the generated launcher is sufficient and the hand-owned door retires with the rest.

## The model after this ticket

| Platform | Door | Surface it reads |
|---|---|---|
| Claude | generated launcher `SKILL.md` (hand-authored wins) | `.claude/skills/` (tree-copied cache) |
| Codex | the **same** launcher | `.agents/skills/` (native) |
| **Antigravity** | the **same** launcher | `.agents/skills/` (native) + global `~/.gemini/config/skills/` |
| opencode | full-body command mirror | `.opencode/commands/` + global `~/.config/opencode/commands` |
| Zoo | generated launcher | `.roo/commands/` |

**`platforms:` after this ticket, for the skill door:** `claude` → the launcher goes to the
`.claude/skills` cache; `codex` **or** `antigravity` → the launcher goes to the master `.agents/skills/`
(read by both). A command claiming only `claude` never enters the master (unchanged). A **hand-authored**
skill is tree-copied to Claude's cache regardless of the command's `platforms:` — the SCC-59 shape,
unchanged, and the reason the 13 `[opencode, antigravity]` `cicd-*` commands keep their Claude entries.

## Acceptance — checkable, each with the assertion that proves it

| Row | Statement | Proven by |
|---|---|---|
| **A** | `.agents/workflows/` does not exist; `.gitattributes` no longer pins it; the comment-stripped engine contains no `Sync-AntigravityWorkflowMirror`, `Get-AgDescription`, `$excluded`, `Join-Path … "workflows"`, or a write to `global_workflows` other than the retirement purge | new `CS-18 A`/`N` (re-aimed) |
| **B** | every command claiming `antigravity` (not `-AP`) has a `.agents/skills/<name>/SKILL.md` that is a current generated launcher for its own brain OR hand-authored; a generated launcher sits in the master iff the command claims `codex` or `antigravity`, and in `.claude/skills` iff it claims `claude` | `CS-02` extended (`missing_ag`/`ag_here` retired) |
| **C** | the Antigravity machine cache is `~/.gemini/config/skills/`, a per-dir mirror of exactly the antigravity-eligible launcher dirs, each stamped with a marker file; purge touches only marked dirs whose source retired; `bmad-*` and unmarked dirs are never touched; the retired `~/.gemini/antigravity/global_workflows/` purge exists as CODE and leaves nothing of ours there | `CS-18 C–H` re-aimed to the skills mirror; `L`/`M` byte-compare in the main checkout only; new `R` (retired cache empty of our files, main checkout, SKIP when absent) |
| **D** | the launcher stub names Claude, Codex **and** Antigravity, and every committed generated `SKILL.md` is byte-identical to a fresh `pwsh` emit of `Sync-LauncherSkills` | `CS-18 Q` re-aimed to the skill emitter (`Q1` ran, `Q4` covered every committed GEN dir, `Q2` balanced quotes, `Q3` no BOM) |
| **E** | dead code and dead tests gone on both sides: `Get-AgDescription`, `ag_description`, `AG_DESC_MAX`, the SCC-195 `U1–U9` block, `wf_hand_owned`, `ag_eligible`, `door_verdict`'s `launcher_ok`, the size-branch guards `N2`/`O`/`O3`; the 12,000 number leaves live law entirely (`CS-18 P` allow-list empty, `P3` retired) | `CS-18 N` + `P` |
| **F** | no live law, doc, door or memory says Antigravity reads `.agents/workflows/` or `global_workflows` — `RULE_SITES` widened, anti-fossil `J0` kept; SOP + changelog moved in the same commit; `repo-map.md` and `doc-graph.{md,json}` regenerated; `_artifacts/_main/INDEX.md` row present | `CS-18 J` widened · `sop_currency` gate · `check_maps --depth3-only --strict` |
| **G** | `smh-adviser-board` declares `antigravity`; its hand-owned workflow door is gone; the brain's inline-mode section is the only inline law | `test_adviser_board_filter_gates` F re-aimed (AG budget check retired; brain carries `## Running without subagents`) |
| **H** | floor green — `run_all.py`, `workflow_lint.py --toolkit-only`, `check_maps.py --depth3-only --strict`, `check_links.py`; the lane ran `sync-agents.ps1 -NoGlobals` and committed the regenerated tree copies; after landing the ceremony runs plain `/smh-sync-agents` from the **main** checkout; the hands check in `## Your Actions` is recorded with what the operator saw | gate receipts + walkthrough |

## Steps — assert-first, in this order

**Step 0 · baseline (hands, optional, before any code).** In Antigravity, open the Customizations
panel and note two numbers: how many **Skills** it lists, and whether the 40 **Workflows** in
`~/.gemini/antigravity/global_workflows/` appear under Global at all. The second answers a question the
repo cannot: whether that cache was ever read.

**Step 1 · write the RED assertions.** Every new or re-aimed check in `test_command_surfaces.py` and the
four sibling tests is written against the unmodified tree and seen red before Step 2 starts. Paste the
red run into the walkthrough. `CS-18 Q` needs `pwsh` (`/usr/bin/pwsh` on this box).

**Step 2 · the engine** (`sync-agents.ps1`) — design in the next section.

**Step 3 · delete the surface.** `git rm -r .agents/workflows/` (41 files); drop the
`.agents/workflows/*.md text eol=lf` block from `.gitattributes`; `smh-adviser-board.md` frontmatter
`platforms: [claude, opencode, antigravity, codex]`.

**Step 4 · tests** — re-aim list in the section below.

**Step 5 · scripts.** `workflow_lint.py` `_RETIRED_SURFACES` drops `"workflows"` and its three comment
sites; `record_map_changes.py` `TOOLKIT_FAMILIES` drops `"workflows"`; `sop_currency.py` docstring line
28 and `.agents/scripts/INDEX.md` line 67 drop `workflows/` from the exempt list; `generate_doc_graph.py`
prose "rules/workflows" → "rules/commands" (3 sites). `check_maps.py` `vendor_markers` **keeps**
`.agents/workflows` on purpose — a project carrying it is stale vendoring, and that is exactly what the
marker detects.

**Step 6 · law and docs, same commit as Step 2** (the armed `sop_currency` gate fires on
`.agents/commands/**`, `.agents/scripts/**`, `.agents/rules/**` and root `AGENTS.md`):
- `AGENTS.md` §4 "Master toolkit" row (drop `workflows`), "Lobby tool dirs" row (Antigravity enters
  through the launcher skill in `.agents/skills/`), §8 portability paragraph.
- `.agents/AGENTS.md` §1, §3 routing row, §4; `.agents/INDEX.md` workflows row deleted.
- `.agents/commands/INDEX.md` lines 20–41 (the door model paragraph, the SCC-56 paragraph, the
  `smh-adviser-board` row).
- `.agents/skills/INDEX.md`: state that this surface is Antigravity's `/` menu too.
- `.agents/commands/smh-sync-agents.md`: "What it touches", the machine-global caches bullet, the whole
  `-GlobalsOnly` section (the 12,000 paragraph goes — its reason no longer exists on any surface we
  publish), the per-surface count list. The `.opencode/commands/` mirror follows byte-for-byte.
- `.agents/rules/sop-currency.md` line 42 exempt list.
- `docs/workspace-standard.md` §"Command sync & platform reach": the surfaces bullet, the
  `commands/` vs `workflows/` bullet (retire), the "Gemini reads two workflow surfaces" bullet
  (Antigravity reads two **skill** surfaces; the launcher still STOPs outside the lobby).
- `docs/_scc_sops_prds/workflows_testing_SOP.md`: §3 `/smh-sync-agents` row (drop the 135-char
  paragraph), the `-GlobalsOnly` paragraph and the mermaid `CACHE` node, §19's invocation table footnote,
  and the "Antigravity's size cap is retired" box rewritten as "Antigravity enters through the same
  skill door" with the SCC-135/332/370 history compressed to one `ⓘ` paragraph (sop-currency habit 4).
  One line in `workflows_testing_SOP_changelog.md`.
- `docs/_scc_sops_prds/INDEX.md` line 119 (the "anything dropped in `.agents/workflows/` becomes a `/`"
  note — now "in `.agents/skills/`"); `docs/_scc_sops_prds/file_folder_structure+maintaining.md` lines 13
  and 382 point at `.agents/workflows/smh-update-maps-indexes.md`, a launcher since SCC-135 — repoint to
  `.agents/commands/smh-update-maps-indexes.md`.
- Regenerate `docs/repo-map.md` (`generate_repo_map.py`) and `docs/doc-graph.{md,json}`
  (`generate_doc_graph.py`).
- `test_settings_allowlist.py` B4 comment: the extension is live again (SCC-378); the recommendation
  stays absent by the operator's choice, not because the platform is retired. Comment only.

**Step 7 · memory** (content edits, declared here; the SCC-370 precedent — approval of this plan is the
per-item yes; filenames stay stable because other memories link them):
`antigravity-uses-workflows-not-commands.md` (body rewritten: Antigravity's `/` menu is skills,
workflows retire 2026-11-01, the door is the launcher skill, the global path is
`~/.gemini/config/skills/`; history compressed to two lines), `one-door-per-platform-per-command.md`
(table row), `codex-is-fourth-platform.md` (one line: Codex and Antigravity share `.agents/skills/`),
`MEMORY.md` line 91 hook text. Narrated in chat in one line each when written.

**Step 8 · sync and gates, inside the lane.** Run `pwsh .agents/scripts/sync-agents.ps1 -NoGlobals`
with the sandbox off (`.claude/skills` is write-denied under the OS sandbox in-session), commit the
regenerated `.agents/skills/*/SKILL.md`, `.claude/skills/*/SKILL.md` and `.agents/.sync-manifest.json`.
Then the floor: `run_all.py` · `workflow_lint.py --toolkit-only` · `check_maps.py --depth3-only --strict`
· `check_links.py`. Receipts into `gates/`.

**Step 9 · hands, after landing** (goes into the walkthrough's `## Your Actions`; the ceremony's
plain `/smh-sync-agents` from the main checkout runs first, then a window reload):
1. In the lobby, type `/smh-sync-agents` in Antigravity → it launches from the skill and reads the
   command body (the launcher's "Execute now" line is what you should see it do first).
2. Customizations → Skills: the 74 house + 56 BMAD workspace skills are listed; spot-check the
   alphabetical tail (`workspace-structure`, `write-swift`) — a dropped tail is the SCC-195 shape.
3. Open a project workspace (any `Projects/<name>`): the 39 global launchers appear under Global, and
   `/smh-quick-dev` STOPs with "that file does not exist in this workspace" rather than improvising.
4. Customizations → Workflows: no house entries, no deprecation banner.

## Engine design — the specifics

**`Sync-LauncherSkills`** (master `.agents/skills/`):
- eligible = `-AP` skipped; `platforms` ∩ {`claude`,`codex`,`antigravity`} ≠ ∅.
- emitted into the master iff `platforms` ∩ {`codex`,`antigravity`} ≠ ∅ (claude-only stays cache-only,
  emitted at the local stage exactly as today).
- hand-authored `SKILL.md` (no marker) always wins; stale generated launchers pruned. Unchanged.
- `New-LauncherSkillStub` sentence: "this skill exists so the same / works in Claude, Codex and
  Antigravity, whose menus read skills, not commands." — one literal, regenerates every launcher.

**Local stage** (`.claude/skills` copy): `$cxOnly` becomes `$masterOnly` = commands whose master
`SKILL.md` is **generated** and whose `platforms` claim `codex` or `antigravity` but not `claude`. Today
that is `cicd-bdd-tests` and `sentry-security-team-avch` — the same two as now. ⛔ Not hand-authored
skills: widening the exclusion to them would pull 13 `cicd-*` entries out of Claude's menu.

**`Sync-AntigravitySkills`** (new; shape of `Sync-CodexSkills`):
- source set = every `.agents/skills/<name>/` where `<name>` is an antigravity-eligible command (not
  `-AP`), generated or hand-authored — the same set the retired cache carried. Knowledge skills
  (`python-patterns`, …) stay workspace-only, as they are for every other global cache.
- destination `~/.gemini/config/skills/<name>/`, `Copy-Tree … -Mirror` per dir, then write a marker
  file `.sync-agents-mirror` into the dir (`GENERATED by sync-agents - mirror of
  .agents/skills/<name>; do not edit; purged when the source retires`).
- purge = every cache dir carrying the marker whose name is not in the source set. Never `bmad-*`,
  never an unmarked dir (the operator's own global skills).
- `-WhatIf` prints `would mirror antigravity skill '<name>'` / `would purge …`; the same fidelity caveat
  as today (a brand-new command's launcher is emitted by `Sync-LauncherSkills`, which writes nothing
  under `-WhatIf`, so the cache preview is a floor).
- guarded like the other caches (missing/broken path → warning, never a crash); runs only when
  `(-not $NoGlobals) -and ($IsLobby -or $GlobalsOnly)`; `Sync-LauncherSkills` already runs before the
  globals block, which is the ordering `CS-18 I2` pins.
- retired-cache purge, once per machine, same shape as the `~/.codex/prompts` purge: remove our
  non-`bmad-*` `*.md` from `~/.gemini/antigravity/global_workflows/` and print a RETIRED line; leave
  the directory.

**Deletions:** `Sync-AntigravityWorkflowMirror`, `Get-AgDescription`, the SCC-195 comment block, the
regen call and its `Write-Host`, `$GlobalWfSrc` and the antigravity row of `$caches` (the table keeps
the opencode row; the skills mirror is its own call), `.agents\workflows` in `Get-SurfaceState`, the
"commands/workflows" wording in the `-Reconcile` keep-list header, and the header `.DESCRIPTION` /
door-model comments (Antigravity enters through the launcher skill).

**Reported counts** after a sync: generated launcher skills · `.claude/skills` · `.opencode/commands` ·
opencode global · **antigravity global (skills)** · codex bmad skills.

## Tests — the exact re-aim list

`test_command_surfaces.py` (63 references to the surface today):
- helpers: delete `wf_hand_owned`, `ag_eligible`, `ag_description`, `AG_DESC_MAX`; `is_launcher_for` loses
  `budgeted`; `door_verdict` loses `launcher_ok`.
- `CS-01`: keep ".claude/commands is retired"; delete the hand-owned checks and the three
  "declaration" controls that only served them.
- `CS-02`: eligibility for the skill door = claude|codex|antigravity; placement asserted both ways per
  row B; `missing_ag`, `ag_here`, `hand_ag` and the antigravity `mirror_place_error` calls go; the four
  door-place controls keep only the opencode pair.
- `CS-03`: `MIRRORS = (".opencode/commands",)`; the `WF` controls go; keep "a launcher on an OPENCODE
  door is NOT exempt" and the `ea8fe97^` regression control.
- `CS-07`: workflow ghosts and the "≥20 workflows" count go; the opencode ghost sweep stays.
- `CS-13 F`: four doors, not five.
- `CS-15`: `seam_sites` sweeps `.agents/commands` only.
- SCC-195 block: delete `U1–U9` (including the `U7` pwsh extraction of `Get-AgDescription`).
- `CS-18`: rewritten as "the Antigravity door is the skill door" — `A` (no workflows dir, no mirror
  function, no `Get-AgDescription`, no cap number, comment-stripped), `C–H` (the skills-mirror call reads
  `$Master/skills` and targets `.gemini/config/skills`; opencode still `commands`), `I2` (launcher regen
  precedes the globals block), `J` (`RULE_SITES` = `docs/workspace-standard.md`,
  `.agents/commands/INDEX.md`, `.agents/skills/INDEX.md`, `.agents/commands/smh-sync-agents.md`; the
  inverted-claim regex widened to "Antigravity … reads/mirrors … workflows"), `L`/`M` (cache twin
  byte-compare per eligible launcher dir, main checkout only, marked orphans reported), new `R` (retired
  cache holds none of our files, main checkout only, SKIP when absent), `P` (allow-list empty; `P0`
  teeth control kept; `P3` retired), `Q` (round-trip `Sync-LauncherSkills` + `New-LauncherSkillStub` +
  `Get-CommandPlatforms` + `$AllPlatforms` under `pwsh` into a temp master; compare only committed GEN
  dirs; `Q4` = every committed GEN dir was emitted). `K`, `N2`, `O`, `O0`, `O3` retire with their subject.
- module docstring line 14.

Sibling tests: `test_zoo_notify.py` (the `ag` door → `.agents/skills/smh-llm-approvals/SKILL.md`, same
pointer + "END TO END" assertion); `test_live_testing_browser_instrument.py` (`WORKFLOW` → the skill
launcher; `A1b` re-aimed); `test_adviser_board_filter_gates.py` (`AG` removed from the file list; block F
keeps opencode byte-identity + Claude skill description, drops the 135-char budget, adds "the brain
carries `## Running without subagents`"); `test_door_preflight_order.py` line 499 glob removed;
`test_doc_examples_parse.py` line 55 comment; `test_workflow_lint.py` lines 583/592 fixture (no
`workflows/INDEX.md`).

## Declared Change Set

Rows A–H are the acceptance table above.

- DELETE `.agents/workflows/INDEX.md` → A
- DELETE `.agents/workflows/cicd-bdd-tests.md` → A
- DELETE `.agents/workflows/cicd-boot-sprint-memory.md` → A
- DELETE `.agents/workflows/cicd-clean-code-audit.md` → A
- DELETE `.agents/workflows/cicd-close-story-merge-tree.md` → A
- DELETE `.agents/workflows/cicd-code-review.md` → A
- DELETE `.agents/workflows/cicd-create-epic-sprint.md` → A
- DELETE `.agents/workflows/cicd-dev-story-tests.md` → A
- DELETE `.agents/workflows/cicd-e2e.md` → A
- DELETE `.agents/workflows/cicd-label-tasks.md` → A
- DELETE `.agents/workflows/cicd-live-testing-team.md` → A
- DELETE `.agents/workflows/cicd-merge-epic-workingtrees.md` → A
- DELETE `.agents/workflows/cicd-non-crit-pr-push.md` → A
- DELETE `.agents/workflows/cicd-park.md` → A
- DELETE `.agents/workflows/cicd-prune-context.md` → A
- DELETE `.agents/workflows/cicd-prune-worktree.md` → A
- DELETE `.agents/workflows/cicd-push-e2e.md` → A
- DELETE `.agents/workflows/cicd-quick-dev.md` → A
- DELETE `.agents/workflows/cicd-resume.md` → A
- DELETE `.agents/workflows/cicd-self-audit.md` → A
- DELETE `.agents/workflows/cicd-update-sprint-memory.md` → A
- DELETE `.agents/workflows/cicd-write-story-tests.md` → A
- DELETE `.agents/workflows/sentry-security-team-avch.md` → A
- DELETE `.agents/workflows/smh-adviser-board.md` → A
- DELETE `.agents/workflows/smh-clean-code-audit.md` → A
- DELETE `.agents/workflows/smh-close-task-merge-tree.md` → A
- DELETE `.agents/workflows/smh-code-review.md` → A
- DELETE `.agents/workflows/smh-label-tasks.md` → A
- DELETE `.agents/workflows/smh-llm-approvals.md` → A
- DELETE `.agents/workflows/smh-memory-audit.md` → A
- DELETE `.agents/workflows/smh-merge-multiple-workingtrees.md` → A
- DELETE `.agents/workflows/smh-new-project.md` → A
- DELETE `.agents/workflows/smh-non-crit-pr-push.md` → A
- DELETE `.agents/workflows/smh-plan-task.md` → A
- DELETE `.agents/workflows/smh-quick-dev.md` → A
- DELETE `.agents/workflows/smh-quick-fix.md` → A
- DELETE `.agents/workflows/smh-review.md` → A
- DELETE `.agents/workflows/smh-self-audit.md` → A
- DELETE `.agents/workflows/smh-sync-agents.md` → A
- DELETE `.agents/workflows/smh-sync-vscode.md` → A
- DELETE `.agents/workflows/smh-update-maps-indexes.md` → A
- DELETE `.gitattributes` block pinning `.agents/workflows/*.md` (EDIT to the file: the block goes, the `*.sh` pin stays) → A
- EDIT `.agents/scripts/sync-agents.ps1` — launcher eligibility, master placement, `Sync-AntigravitySkills`, retired-cache purge, deletions, header → A, B, C, D
- EDIT `.agents/commands/smh-adviser-board.md` — `platforms:` adds `antigravity` → G
- EDIT `.opencode/commands/smh-adviser-board.md` — byte mirror of the brain → G
- EDIT `.agents/commands/smh-sync-agents.md` — door model, caches, `-GlobalsOnly`, counts → F
- EDIT `.opencode/commands/smh-sync-agents.md` — byte mirror of the brain → F
- EDIT `.agents/skills/cicd-bdd-tests/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/cicd-e2e/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/cicd-label-tasks/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/cicd-live-testing-team/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/cicd-non-crit-pr-push/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/cicd-prune-context/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/cicd-push-e2e/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/cicd-quick-dev/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/sentry-security-team-avch/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-adviser-board/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-clean-code-audit/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-code-review/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-label-tasks/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-llm-approvals/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-memory-audit/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-merge-multiple-workingtrees/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-new-project/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-non-crit-pr-push/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-plan-task/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-quick-dev/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-quick-fix/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-review/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-self-audit/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-sync-agents/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.agents/skills/smh-sync-vscode/SKILL.md` — regenerated launcher (stub names all three readers) → D
- EDIT `.claude/skills/cicd-autopilot-claude/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/cicd-autopilot-deepseek4/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/cicd-e2e/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/cicd-label-tasks/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/cicd-live-testing-team/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/cicd-mobile-error-team/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/cicd-non-crit-pr-push/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/cicd-prune-context/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/cicd-push-e2e/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/cicd-quick-dev/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-adviser-board/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-clean-code-audit/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-code-review/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-label-tasks/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-llm-approvals/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-memory-audit/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-merge-multiple-workingtrees/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-new-project/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-non-crit-pr-push/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-plan-task/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-quick-dev/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-quick-fix/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-review/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-self-audit/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-sync-agents/SKILL.md` — regenerated launcher copy → D
- EDIT `.claude/skills/smh-sync-vscode/SKILL.md` — regenerated launcher copy → D
- EDIT `.agents/.sync-manifest.json` — regenerated by the lane sync → H
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — the re-aim list → A, B, C, D, E, F
- EDIT `.agents/scripts/tests/test_zoo_notify.py` — AG door → skill launcher → B
- EDIT `.agents/scripts/tests/test_live_testing_browser_instrument.py` — `WORKFLOW` → skill launcher → B
- EDIT `.agents/scripts/tests/test_adviser_board_filter_gates.py` — block F re-aimed → G
- EDIT `.agents/scripts/tests/test_door_preflight_order.py` — surface glob removed → A
- EDIT `.agents/scripts/tests/test_doc_examples_parse.py` — comment → F
- EDIT `.agents/scripts/tests/test_workflow_lint.py` — fixture without a workflows router → A
- EDIT `.agents/scripts/tests/test_settings_allowlist.py` — B4 comment states the platform is live → F
- EDIT `.agents/scripts/workflow_lint.py` — `_RETIRED_SURFACES` and comments → A
- EDIT `.agents/scripts/record_map_changes.py` — `TOOLKIT_FAMILIES` → A
- EDIT `.agents/scripts/sop_currency.py` — docstring exempt list → F
- EDIT `.agents/scripts/generate_doc_graph.py` — prose → F
- EDIT `.agents/scripts/INDEX.md` — line 67 exempt list → F
- EDIT `AGENTS.md` — §4 rows, §8 paragraph → F
- EDIT `.agents/AGENTS.md` — §1, §3, §4 → F
- EDIT `.agents/INDEX.md` — workflows row deleted → F
- EDIT `.agents/commands/INDEX.md` — door model, SCC-56 paragraph, adviser row → F
- EDIT `.agents/skills/INDEX.md` — this surface is Antigravity's menu too → F
- EDIT `.agents/rules/sop-currency.md` — exempt list → F
- EDIT `docs/workspace-standard.md` — §Command sync bullets → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §3 row, `-GlobalsOnly`, mermaid, §19 box → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line → F
- EDIT `docs/_scc_sops_prds/INDEX.md` — line 119 note → F
- EDIT `docs/_scc_sops_prds/file_folder_structure+maintaining.md` — two stale pointers → F
- EDIT `docs/repo-map.md` — regenerated → F
- EDIT `docs/doc-graph.md` — regenerated → F
- EDIT `docs/doc-graph.json` — regenerated → F
- EDIT `_artifacts/_memory/antigravity-uses-workflows-not-commands.md` — body rewritten → F
- EDIT `_artifacts/_memory/one-door-per-platform-per-command.md` — table row → F
- EDIT `_artifacts/_memory/codex-is-fourth-platform.md` — one line → F
- EDIT `_artifacts/_memory/MEMORY.md` — line 91 hook → F
- NEW `_artifacts/_main/2026-09-04_ag-skills-door/implementation_plan.md` — this file → H
- NEW `_artifacts/_main/2026-09-04_ag-skills-door/task.yaml` — grounds the lane → H
- NEW `_artifacts/_main/2026-09-04_ag-skills-door/tickets/SCC-394.md` — the ticket outline → H
- NEW `_artifacts/_main/2026-09-04_ag-skills-door/walkthrough.md` — at close → H
- EDIT `_artifacts/_main/INDEX.md` — session row → F

## Gates

`run_all.py` (72 files today) · `workflow_lint.py --toolkit-only` · `check_maps.py --depth3-only --strict`
· `check_links.py` · the armed `sop_currency` and Jira commit-msg gates · `CS-18 Q` under `pwsh`. Then
`/smh-code-review` (the door-parity check and `CS-18 L`/`M`/`R` bind only in the main checkout after the
ceremony's sync, so a lane run reports them as SKIP with the stated reason).

## Out of scope, named

- BMAD's `.agent/skills/` install and its manifest `ides: [claude-code, antigravity]` — untouched.
- Rule frontmatter (`trigger:` / `globs:` — Antigravity's rule loader is not changing).
- The permission fence (`.agents/permissions/`, `antigravity_permissions_apply.py`) — a different
  Antigravity surface, SCC-378's.
- `Projects/sudo-command-center` and the skeleton carry their own copies of the sync engine and their
  own key space (as SCC-367 recorded) — a follow-on there when this lands, under their keys.
- Whether the `.vscode/extensions.json` recommendation for the extension comes back — the operator's.

## Open questions

None blocking. Parent epic placement on the board is the operator's (guardrail 2); the ticket is minted
bare like its five sibling sync-agents tickets.
