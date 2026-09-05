---
IsArtifact: true
ArtifactMetadata:
  title: SCC-394 — Antigravity's door becomes the launcher skill
  type: implementation_plan
  date: 2026-09-04
---

# SCC-394 — Antigravity's door becomes the launcher skill

**Lane:** `chore/SCC-394-ag-skills-door` · worktree `.claude/worktrees/SCC-394-ag-skills-door`
**Base:** `origin/main` @ `eee79727` (re-based twice during the audit: `70154040` -> `ccc4c70c` when
SCC-393 landed, then -> `eee79727` when SCC-388 landed. `/smh-code-review` Step 0.7 re-derives the
blast radius against this line, so it is kept current rather than recording the original cut.)
**Ticket:** [SCC-394](https://sudo-command.atlassian.net/browse/SCC-394)
**review-runtime:** fan-out

---

## What changes for you, Mr. Hatter

**Scope, after your ruling of 2026-09-04: this ticket is the retirement half only.** It deletes the
Antigravity workflow surface and makes the launcher skill — the same generated `SKILL.md` Claude and
Codex already read — Antigravity's one door. It writes **no** new machine-global cache. The cache half
(mirroring our launchers into Google's documented `~/.gemini/config/skills/` so a *project* workspace can
see the lobby's commands) is a follow-on, gated on one measurement this ticket's Step 0 takes: whether
the old cache at the undocumented path was ever read at all. Four audit passes found nothing of
consequence in the retirement half and everything of consequence in the cache half; the cut is what the
fourth pass recommended and what you approved.

**What the ticket does.** Antigravity has deprecated workflows and retires them on **2026-11-01**. Any
`.agents/skills/<name>/SKILL.md` is now invoked as `/<name>`, exactly like a workflow, with no size cap.
Every one of the 39 antigravity-eligible commands already has a launcher `SKILL.md` in `.agents/skills/`,
so today Antigravity offers each command **twice** — the double door SCC-66 retired on every other
platform — and on 1 November one of the two goes dark. This ticket deletes `.agents/workflows/` (41
files), tells the sync engine that Antigravity reads the launcher skill, re-aims every test and law site
that called the workflow mirror the Antigravity door, and purges the retired machine cache once.

**The one tradeoff that survives the cut.** Codex and Antigravity both read `.agents/skills/` natively,
so a launcher there reaches both and `platforms:` can no longer give a command to one without the other.
That split was already fiction: the 15 commands declared `[opencode, antigravity]` all carry hand-authored
skills that Codex has been reading all along. This plan writes that truth into the law rather than
building a per-platform cache to preserve a distinction nobody uses. Google's `skills.json` declared
paths exist if a real case ever appears.

**The description budget, after the cut.** Antigravity injects every skill's `description:` each turn.
In the lobby nothing changes: the 74 workspace skills it reads today (27,026 chars) are the same 74 it
reads after, and the 40-file workflow menu (5,051 chars) goes away. A project workspace carries nothing
of ours after this ticket — which, if Step 0's second number is "no", is what it carried before.

**Worked example.** You type `/smh-quick-dev` in Antigravity inside the lobby. The menu entry comes from
`.agents/skills/smh-quick-dev/SKILL.md`, the same file Claude and Codex use. Its body says "read
`.agents/commands/smh-quick-dev.md` and follow it end to end", so the command body stays the one brain.
In a project workspace the entry does not appear, because no global cache exists yet; the follow-on
decides whether it should.

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

## What is on disk today (measured on `70154040`; unchanged at `eee79727`)

| Surface | Count | Note |
|---|---|---|
| commands claiming `antigravity` (not `-AP`) | **39** | `Get-CommandPlatforms` semantics; **40 after Step 3** adds `smh-adviser-board` |
| … with a `.agents/skills/<name>/SKILL.md` | **39** — 24 generated + 15 hand-authored | zero missing — the skill door already covers the whole set |
| `.agents/workflows/*.md` | **41** — 39 generated + `INDEX.md` + hand-owned `smh-adviser-board.md` | the surface this ticket deletes |
| `~/.gemini/antigravity/global_workflows/*.md` on this machine | 40 | a path no vendor doc names; purged once by this ticket |
| `~/.gemini/config/skills/` on this machine | absent | the vendor's global skills path — **not written by this ticket** |
| `.agent/skills/` (BMAD's install for Antigravity, tracked) | 56 `bmad-*` | untouched |
| workspace skill descriptions (`.agents/skills/*/SKILL.md`) | 74 skills · 27,026 chars | unchanged |
| workflow-menu descriptions (capped at 135 by SCC-195) | 40 files · 5,051 chars | retired |

`smh-adviser-board` is the one command that declares `[claude, opencode, codex]` and carries a hand-owned
Antigravity workflow door, because that door holds an INLINE-mode paragraph. The brain already carries
that law itself — `## Running without subagents — inline mode` in `.agents/commands/smh-adviser-board.md`,
a capability self-test rather than a platform branch — so the generated launcher is sufficient and the
hand-owned door retires with the rest.

## The model after this ticket

| Platform | Door | Surface it reads |
|---|---|---|
| Claude | generated launcher `SKILL.md` (hand-authored wins) | `.claude/skills/` (tree-copied cache) |
| Codex | the **same** launcher | `.agents/skills/` (native) |
| **Antigravity** | the **same** launcher | `.agents/skills/` (native) — global cache is the follow-on |
| opencode | full-body command mirror | `.opencode/commands/` + global `~/.config/opencode/commands` |
| Zoo | generated launcher | `.roo/commands/` |

**`platforms:` for the skill door:** `claude` → the launcher goes to the `.claude/skills` cache; `codex`
**or** `antigravity` → the launcher goes to the master `.agents/skills/` (read by both). A command claiming
only `claude` never enters the master (unchanged). A **hand-authored** skill is tree-copied to Claude's
cache regardless of the command's `platforms:` — the SCC-59 shape, unchanged, and the reason the **11**
hand-authored `[opencode, antigravity]` commands (ten `cicd-*` plus `smh-close-task-merge-tree`) keep
their Claude entries (post-cut audit: the candidate set is 13; two are generated and are exactly the
`$masterOnly` pair).

## Acceptance — checkable, each with the assertion that proves it

| Row | Statement | Proven by |
|---|---|---|
| **A** | `.agents/workflows/` does not exist; `.gitattributes` no longer pins it and **does pin `.agents/skills/**/SKILL.md` and `.claude/skills/**/SKILL.md` LF**; the comment-stripped engine contains no `Sync-AntigravityWorkflowMirror`, no `$excluded`, no `$GlobalWfSrc`, no antigravity row in `$caches`, no `Join-Path … "workflows"`, no write to `global_workflows` other than the retirement purge, and **exactly one call to `Get-AgDescription`, inside `Sync-ZooSurfaces`** (it is Zoo's launcher truncator at `sync-agents.ps1:795`, not dead code) | `CS-18 A`/`N` (re-aimed) |
| **B** | every command claiming `antigravity` (not `-AP`) has a `.agents/skills/<name>/SKILL.md` that is a current generated launcher for its own brain OR hand-authored; a generated launcher sits in the master iff the command claims `codex` or `antigravity`, and in `.claude/skills` iff it claims `claude` | `CS-02` extended (`missing_ag`/`ag_here` retired) |
| **C** | the engine writes **no** Antigravity global cache — nothing under `~/.gemini/config/skills/`, nothing under `global_workflows` — and the one-time retirement purge of `~/.gemini/antigravity/global_workflows/` exists as CODE, removes only our non-`bmad-*` `*.md`, prints a RETIRED line and leaves the directory | `CS-18 C` (comment-stripped engine: the purge exists, no other Antigravity global write does) + `R` (retired cache holds none of our files; main checkout only, SKIP when absent) |
| **D** | the launcher stub names Claude, Codex **and** Antigravity, and every committed generated `SKILL.md` is byte-identical to a fresh `pwsh` emit of `Sync-LauncherSkills` | `CS-18 Q` re-aimed (`Q1` ran, `Q4` covered every committed GEN dir, `Q2` balanced quotes, `Q3` no BOM) |
| **E** | dead code and dead tests gone on both sides: the Antigravity call site of `Get-AgDescription` (the function survives for Zoo), `ag_description`, the SCC-195 `U1–U6`/`U8`/`U9` block (`U7` survives re-labelled as the Zoo truncation check, `AG_DESC_MAX` with it), `wf_hand_owned`, `ag_eligible`, `door_verdict`'s `launcher_ok`, the size-branch guards `N2`/`O`/`O2`/`O3`, the cache-twin checks `L`/`M`, `I`/`I2` and `M2`, `U6c` (their subject retires); `ag_description` and `AG_LIVE_DESCS` **survive** for `U7`; the 12,000 number leaves live law entirely (`CS-18 P` allow-list empty, `P3` retired) | `CS-18 N` + `P` |
| **F** | no live law, doc, door or memory says Antigravity reads `.agents/workflows/` or `global_workflows` — `RULE_SITES` widened, anti-fossil `J0` kept; SOP + changelog moved in the same commit; `repo-map.md` and `doc-graph.{md,json}` regenerated; `_artifacts/_main/INDEX.md` row present | `CS-18 J` widened · `sop_currency` gate · `check_maps --depth3-only --strict` |
| **G** | `smh-adviser-board` declares `antigravity`; its hand-owned workflow door is gone; the brain's inline-mode section is the only inline law | `test_adviser_board_filter_gates` F re-aimed |
| **H** | floor green — `run_all.py` (73 files), `workflow_lint.py --toolkit-only`, `check_maps.py --depth3-only --strict`, `check_links.py`; the lane ran `sync-agents.ps1 -NoGlobals` and committed every regenerated file; **Step 0's two baseline numbers are in the walkthrough before Step 1 starts**; Step 9's hands checks and the four decision rows are in `## Your Actions` | gate receipts + walkthrough |

## Steps — assert-first, in this order

**Step 0 · baseline (hands, REQUIRED, before any code).** In Antigravity, open the Customizations panel
and record two numbers in the walkthrough: (a) how many **Skills** it lists in the lobby, and (b) in a
**project workspace** (any `Projects/<name>`), whether the 40 workflows from
`~/.gemini/antigravity/global_workflows/` appear under Global at all. **(b) is the follow-on's gate**: it
is the only check anywhere that can say whether the old cache was ever read, and therefore whether a new
one is worth building. Without it a later "project workspaces show nothing" cannot be told from a
condition that predates this ticket.

**Step 1 · write the RED assertions.** Every new or re-aimed check in `test_command_surfaces.py` and the
sibling tests is written against the unmodified tree and seen red before Step 2 starts. Paste the red run
into the walkthrough. `CS-18 Q` needs `pwsh` (`/usr/bin/pwsh` on this box).

**Step 2 · the engine** (`sync-agents.ps1`) — design in the next section. ⛔ Same commit as Steps 3, 5, 6.

**Step 3 · delete the surface — ⛔ in the SAME commit as Steps 2, 5 and 6.** `git rm -r
.agents/workflows/` (41 files); `smh-adviser-board.md` frontmatter
`platforms: [claude, opencode, antigravity, codex]` (a `.agents/commands/` edit, so a `sop_currency`
surface). In `.gitattributes`, **replace** the pin rather than dropping it — the byte-mirror contract
moves onto `SKILL.md` (row D's `CS-18 Q` byte-compares on both machines), and on the PC
`core.autocrlf=true` would otherwise hand every `SKILL.md` CRLF on checkout, the SCC-338 defect one
surface over:

```gitattributes
.agents/skills/**/SKILL.md text eol=lf
.claude/skills/**/SKILL.md text eol=lf
```

Rewrite the 14-line comment block above the old pin (`.gitattributes:20-33`) in the same edit: it still
says the sync writes `global_workflows` and explains `CS-18 L` in terms of `.agents/workflows/*.md`. Keep
the SCC-338 measurement as the `ⓘ` reason the pin exists. The `**` glob was proved with
`git check-attr -a` in a scratch repo: it matches `.agents/skills/foo/SKILL.md`, a nested `steps/SKILL.md`,
and nothing else.

⛔ **Landing order.** `claude/teaching-edition` at `0d76f72c` **adds three files into `.agents/workflows/`**
(`smh-tour.md`, `smh-training.md`, `smh-new-project.md`), pins five distinct `.agents/workflows/` paths
across ten sites in `validate_teaching_edition.py`, and its working tree carries **44 dirty rows** under
that directory. **SCC-394 lands first.** That lane then repoints its three doors to `.agents/skills/`,
re-aims its validator, and resolves its dirty tree against a directory that no longer exists — under its
own key, and it must **not** resolve those conflicts by keeping its side. Step 9 owes a `## Your Actions`
row saying so.

**Step 4 · tests** — re-aim list in the section below.

**Step 5 · scripts — same commit.** `workflow_lint.py` `_RETIRED_SURFACES` drops `"workflows"` and its
three comment sites; `record_map_changes.py` `TOOLKIT_FAMILIES` drops `"workflows"`; `sop_currency.py`
docstring line 28 and `.agents/scripts/INDEX.md` line 67 drop `workflows/` from the exempt list;
`generate_doc_graph.py` prose — **two** sites: line 575 `"… Rebuild after editing rules/workflows."` and
line 21 `prose toolkit (rules / workflows / skills / commands)`. `check_maps.py` `vendor_markers` **keeps**
`.agents/workflows` on purpose — a project carrying it is stale vendoring. ⛔ These four `.py` edits fire
the armed `sop_currency` gate (`_SURFACES` includes `.agents/scripts/` `*.py`/`*.ps1`; `tests/` and every
`INDEX.md` are exempt).

**Step 6 · law and docs — same commit** (the gate fires on `.agents/commands/` `.md`, `.agents/rules/`
`.md`, `.agents/scripts/` `.py`/`.ps1`, `.githooks/`, and root `AGENTS.md`):
- `AGENTS.md` §4 "Master toolkit" row (drop `workflows`), "Lobby tool dirs" row (Antigravity enters
  through the launcher skill in `.agents/skills/`), §8 portability paragraph.
- `.agents/AGENTS.md` §1, §3 routing row, §4; `.agents/INDEX.md` workflows row deleted.
- `.agents/commands/INDEX.md` lines 20–41 (the door model paragraph, the SCC-56 paragraph, the
  `smh-adviser-board` row).
- `.agents/skills/INDEX.md`: state that this surface is Antigravity's `/` menu too. `.claude/skills/INDEX.md`
  is its byte tree-copy (`sync-agents.ps1:1115`, no `INDEX.md` exclusion) and regenerates in Step 8.
- `.agents/commands/smh-sync-agents.md`: "What it touches", the machine-global caches bullet (Antigravity's
  is retired; the vendor's global skills path is a follow-on), the whole `-GlobalsOnly` section (the
  12,000 paragraph goes), the per-surface count list, **and line 51** — the `-Status` sentence lists
  `.agents/{commands,workflows}` as an invocable surface; Step 2 drops it from `Get-SurfaceState`.
- `.agents/commands/smh-clean-code-audit.md:98` (the **Door parity** row lists `.agents/workflows/<name>.md`
  as a fourth door) and `:161` (generated-surfaces row) — the machine floor `/smh-code-review` Step 3.5
  runs on this very lane.
- `.agents/commands/smh-quick-dev.md:365` — "Generated surfaces are never hand-edited. `.agents/workflows/`…".
- `.agents/commands/smh-update-maps-indexes.md:48` and `:263` — `{rules,workflows,skills,commands}/INDEX.md`
  as MASTER family maps; drop `workflows` from both brace lists. This is the command that regenerates
  `docs/repo-map.md` and `docs/doc-graph.{md,json}`, which row F requires.
- `.agents/opencode-agents/opus-auditor.md:37` — "Read `.agents/workflows/cicd-self-audit.md` and follow it
  exactly", two lines below its own "If any of these are missing, HALT" (`:33`). Repoint to
  `.agents/commands/cicd-self-audit.md`. Its `.opencode/agent/` twin is a generated mirror
  (`sync-agents.ps1:1202`) — edit the source only.
- `.agents/rules/sop-currency.md:42` exempt list; `.agents/rules/project-law.md:20` tier-1 inventory.
- `docs/workspace-standard.md` §"Command sync & platform reach" (the surfaces bullet, the `commands/` vs
  `workflows/` bullet, the "Gemini reads two workflow surfaces" bullet → Antigravity reads the skill
  surface natively; the launcher STOPs outside the lobby) **and line 159** in §"Supporting files".
- `docs/_scc_sops_prds/workflows_testing_SOP.md`: the `/smh-sync-agents` row at **line 4442** (inside
  §19's invocation table, not §3) — drop its 135-char paragraph; the `-GlobalsOnly` paragraph and the
  mermaid `CACHE` node; §19's footnote; the "Antigravity's size cap is retired" box rewritten as
  "Antigravity enters through the same skill door" with the SCC-135/332/370 history compressed to one `ⓘ`
  paragraph. One line in `workflows_testing_SOP_changelog.md`.
- `docs/_scc_sops_prds/INDEX.md:119`; `docs/_scc_sops_prds/file_folder_structure+maintaining.md` lines 13,
  43 (a mermaid node) and 382; `docs/_scc_sops_prds/tdad_stack_install_guide.md:319`;
  `docs/migrations/install_guides/new_machine-migration-guide.md:423` ("refreshes the Antigravity
  workflows"); `docs/migrations/install_guides/vscode-ide-extension-migration.md:235`;
  `_my_resources/open_tasks/plan_adviser-board-rework.md`.
- Regenerate `docs/repo-map.md` (`generate_repo_map.py`) and `docs/doc-graph.{md,json}`
  (`generate_doc_graph.py`).
- `test_settings_allowlist.py` B4 comment: the extension is live again (SCC-378); the recommendation stays
  absent by the operator's choice. Comment only.

**Step 7 · memory** (content edits; approval of this plan is the per-item yes, the SCC-370 precedent;
filenames stay stable because other memories `[[link]]` them). **Thirteen files** (post-cut audit
corrected the count; the change set carries thirteen `_artifacts/_memory/` rows):
`antigravity-uses-workflows-not-commands.md` (body rewritten: Antigravity's `/` menu is skills, workflows
retire 2026-11-01, the door is the launcher skill; history compressed to two lines),
`one-door-per-platform-per-command.md` (table row), `codex-is-fourth-platform.md` (one line: Codex and
Antigravity share `.agents/skills/`), `MEMORY.md` line 91 hook text,
`bmad-wrappers-are-opencode-only-bridges.md:18` (the `sudo-*` wrapper exception's premise is retired),
`sandbox-denies-writes-under-dot-claude-hooks-skills.md:30`, `grep-skips-gitignored-projects.md` (a tense
change, not a repoint — it names the surface inside a true anecdote),
`thin-projects-center-owns-workflow-law.md:11`, `sop-doc-currency-gate.md:20`,
`e2e-gate-fiction-test-guardrails.md:34`, `toolkit-sync-covers-agents-not-docs.md:31`,
`doc-graph-unc-hang-and-scope.md:10,17`, `git-branch-model-standard.md:90`. Narrated in chat in one line
each when written. **Guard:** `git status --short _artifacts/_memory/` immediately before staging — the
store is shared across every lane on the machine. **Sweep:** before this step closes, re-run the widest
sweep (`.agents/workflows`, `global_workflows`, `{rules,workflows`, `{commands,workflows`,
`workflows/INDEX`, `Antigravity workflows`, `workflow mirror`, bare `workflows` in `_artifacts/_memory/`)
once more — every pass found "a few more" of this class.

**Step 8 · sync and gates, inside the lane.** Run `pwsh .agents/scripts/sync-agents.ps1 -NoGlobals` with
the sandbox off (`.claude/skills` is write-denied under the OS sandbox in-session). ⛔ `-NoGlobals` is
not optional: `$IsLobby` compares a worktree equal to itself (`sync-agents.ps1:114`), so a bare sync from
this lane would write **this machine's** global caches. Then commit **whatever `git status --short` shows
under `.agents/skills/`, `.claude/skills/`, `.opencode/` and `.agents/.sync-manifest.json`**, checking
each against the change set — the six `.opencode/` mirrors and `.claude/skills/INDEX.md` are among them.
Then the floor: `run_all.py` · `workflow_lint.py --toolkit-only` · `check_maps.py --depth3-only --strict`
· `check_links.py`, through the receipt writer into `gates/`.

**Step 9 · after landing.** The ceremony (`/smh-close-task-merge-tree`) runs no sync. On this machine
the operator's ordinary post-pull `/smh-sync-agents` from the lobby runs the retirement purge; the
walkthrough's `## Your Actions` carries the hands checks and four decision rows:

1. In the lobby, type `/smh-sync-agents` in Antigravity → it launches from the skill and reads the
   command body (the launcher's "Execute now" line is what you should see it do first). Then a window
   reload.
2. Customizations → Skills: the 74 house + 56 BMAD workspace skills are listed; spot-check the alphabetical
   tail (`workspace-structure`, `write-swift`).
3. Customizations → Workflows: no house entries, no deprecation banner.
4. Open a project workspace: `/smh-quick-dev` is either absent (no global cache) or, if the old entries
   linger until the purge has run there, STOPs with "that file does not exist in this workspace". Record
   what Global shows — with Step 0 (b), that is the follow-on's whole input.

`## Your Actions` rows, each worded as a **decision** because `jira_feed.py banned_action_rows` refuses a
row that asks the operator to create ticket work (measured: "mint a follow-on ticket …" REFUSED; these
are accepted):
- *Decide whether the Antigravity global cache follow-on is worth building, from Step 0 (b) and item 4:
  if project workspaces never showed the 40 old entries, nothing was lost; if they did, the follow-on is
  `Copy-Tree -Mirror` of the 40 launcher dirs into `~/.gemini/config/skills/` — no manifest, no purge, a
  retired launcher STOPs cleanly — the Codex and opencode shape.*
- *Decide whether `Projects/sudo-command-center` and `Projects/Fresh_Workspace_BMAD` get the
  workflows-to-skills port before 2026-11-01 — both carry `.agents/workflows/`, both are their own repos,
  and `Fresh_Workspace_BMAD` is a frozen template whose disposal is already yours.*
- *On the other machine: pull and run `/smh-sync-agents` so its retired cache is purged too.*
- *`claude/teaching-edition`: repoint its three workflow doors to `.agents/skills/` and re-aim
  `validate_teaching_edition.py` before resuming it; do not resolve its 44 dirty `.agents/workflows/` rows
  by keeping them.*

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
skills: widening the exclusion to them would pull the 11 hand-authored entries (ten `cicd-*` plus
`smh-close-task-merge-tree`) out of Claude's menu.

**Retirement purge, once per machine** — the `~/.codex/prompts` shape at `sync-agents.ps1:1300-1306`,
inside the globals block (`(-not $NoGlobals) -and ($IsLobby -or $GlobalsOnly)`): if
`~/.gemini/antigravity/global_workflows/` exists, remove our non-`bmad-*` `*.md` from it and print a
`RETIRED` line naming the count; leave the directory. `Test-Path` before `Remove-Item` — it throws under
`$ErrorActionPreference = "Stop"` on a missing path. `-WhatIf` prints `would purge …` and removes nothing.

**Deletions:** `Sync-AntigravityWorkflowMirror`; the **Antigravity call site** of `Get-AgDescription` at
`:622` — **not the function**, which `Sync-ZooSurfaces:795` calls and whose header comment is retitled as
Zoo's truncator (`test_zoo_team.py` C7 pins only that the Zoo *seat* loop avoids it — a different
emitter); the SCC-195 comment block; the regen call and its `Write-Host`; `$GlobalWfSrc` and the
antigravity row of `$caches` (the table keeps the opencode row); `$excluded` (all four uses sit in the
retired region); `.agents\workflows` in `Get-SurfaceState`; the "commands/workflows" wording in the
`-Reconcile` keep-list header; the header `.DESCRIPTION` / door-model comments.

**Reported counts** after a sync: generated launcher skills · `.claude/skills` · `.opencode/commands` ·
opencode global · codex bmad skills. No Antigravity global line.

**Not in this ticket:** `Sync-AntigravitySkills` and `~/.gemini/config/skills/`. Four audit passes
designed and re-designed a claim-manifest mirror for that path; the fourth pass's recommendation, and
the operator's ruling, is that it is a follow-on gated on Step 0 (b), and that if it is built it is the
dumb `Copy-Tree -Mirror` shape every other cache in this engine already uses.

## Tests — the exact re-aim list

`test_command_surfaces.py` (63 references to the surface today):
- helpers: delete `wf_hand_owned`, `ag_eligible`; `is_launcher_for` loses `budgeted`; `door_verdict`
  loses `launcher_ok`. **`ag_description`, `AG_DESC_MAX` and the `AG_LIVE_DESCS` setup survive for `U7`**
  — post-cut audit: `U7`'s assertion is "the real PowerShell generator and this file's emulation agree",
  and the emulation *is* `ag_description` (`test_command_surfaces.py:1539`), reading `AG_LIVE_DESCS`
  from the `U1–U6` setup region; deleting either strands the surviving case with a `NameError` on the
  first run. Move the setup `U7` needs into `U7`'s own block when `U1–U6` go.
- `CS-01`: keep ".claude/commands is retired"; delete the hand-owned checks and the three "declaration"
  controls that only served them.
- `CS-02`: eligibility for the skill door = claude|codex|antigravity; placement asserted both ways per row
  B; `missing_ag`, `ag_here`, `hand_ag` and the antigravity `mirror_place_error` calls go; the four
  door-place controls keep only the opencode pair.
- `CS-03`: `MIRRORS = (".opencode/commands",)`; the `WF` controls go; keep "a launcher on an OPENCODE door
  is NOT exempt" and the `ea8fe97^` regression control.
- `CS-07`: workflow ghosts and the "≥20 workflows" count go; the opencode ghost sweep stays.
- `CS-13 F`: four doors, not five.
- `CS-15`: `seam_sites` sweeps `.agents/commands` only.
- SCC-195 block: delete `U1–U6` (including `U6c`, which consumes their totals), `U8`, `U9`. **`U7`
  survives** — its pwsh extraction of `Get-AgDescription` is the only test of a 135 cut that Zoo's
  launchers still carry; re-label it as the Zoo truncation check and carry its setup with it.
- `CS-18`: rewritten as "the Antigravity door is the skill door" — `A` (no workflows dir, no mirror
  function, `Get-AgDescription` called from exactly one site inside `Sync-ZooSurfaces`, no cap number
  outside that function, comment-stripped, **and `.gitattributes` carries no `.agents/workflows` pin while
  it does carry LF pins matching `.agents/skills/**/SKILL.md` and `.claude/skills/**/SKILL.md`** — no test
  in the repo reads that file today, which is why the SCC-338 pin could be dropped silently), `C` (the
  comment-stripped engine contains the retirement purge and **no other write under `.gemini/`**; opencode
  still `commands`), `J` (`RULE_SITES` = `docs/workspace-standard.md`, `.agents/commands/INDEX.md`,
  `.agents/skills/INDEX.md`, `.agents/commands/smh-sync-agents.md`; the inverted-claim regex widened to
  "Antigravity … reads/mirrors … workflows"), `R` (retired cache holds none of our files; main checkout
  only, SKIP when absent), `P` (allow-list empty; `P0` teeth control kept; `P3` retired), `Q` (round-trip
  `Sync-LauncherSkills` + `New-LauncherSkillStub` + `Get-CommandPlatforms` + `$AllPlatforms` under `pwsh`
  into a temp master; compare only committed GEN dirs; `Q4` = every committed GEN dir was emitted).
  `D–H`, **`I`** (it asserts the mirror call is *present* — `^\s*\$\w+\s*=\s*Sync-AntigravityWorkflowMirror`
  — so it goes RED, not stale), `I2`, `K`, `L`, `M`, **`M2`** (calls the deleted `ag_eligible` over
  `WFDIR`), `N2`, `O`, `O0`, **`O2`** (the door-count control for `O`, reads the deleted directory), `O3`
  retire with their subject (post-cut audit added `I`, `M2`, `O2`).
- module docstring line 14.

Sibling tests: `test_zoo_notify.py` (the `ag` door → `.agents/skills/smh-llm-approvals/SKILL.md`, same
pointer + "END TO END" assertion); `test_live_testing_browser_instrument.py` (`WORKFLOW` → the skill
launcher; `A1b` re-aimed); `test_adviser_board_filter_gates.py` (`AG` removed from the file list; block F
keeps opencode byte-identity + Claude skill description, drops the 135-char budget, adds "the brain
carries `## Running without subagents`"); `test_door_preflight_order.py` line **507** glob removed (499 is
the commands glob); `test_doc_examples_parse.py` line 55 comment; `test_workflow_lint.py` lines 583/592
fixture (no `workflows/INDEX.md`).

**Mutation sweep** (`/smh-quick-dev` Step 3): the mutant table is drawn from the engine's code — the
eligibility set, the `$masterOnly` predicate, the purge filter, the stub literal — never from the cases.

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
- EDIT `.gitattributes` — swap the `.agents/workflows/*.md` LF pin for `.agents/skills/**/SKILL.md` and `.claude/skills/**/SKILL.md`; the `*.sh` pin stays → A
- EDIT `.agents/opencode-agents/opus-auditor.md` — its step 1 reads a workflow file this ticket deletes; repoint to `.agents/commands/cicd-self-audit.md` → F
- EDIT `.opencode/agent/opus-auditor.md` — the generated mirror of the above, regenerated by the Step 8 sync → F
- EDIT `.agents/commands/smh-clean-code-audit.md` — the Door parity row and the generated-surfaces row drop the retired door → F
- EDIT `.opencode/commands/smh-clean-code-audit.md` — byte mirror, regenerated by the Step 8 sync → F
- EDIT `.agents/commands/smh-quick-dev.md` — the generated-surfaces bullet drops the retired door → F
- EDIT `.opencode/commands/smh-quick-dev.md` — byte mirror, regenerated by the Step 8 sync → F
- EDIT `docs/_scc_sops_prds/tdad_stack_install_guide.md` — repoint the install target to `.agents/commands/` → F
- EDIT `_my_resources/open_tasks/plan_adviser-board-rework.md` — one line, so a plan resumed later does not build against a door that is gone → F
- EDIT `_artifacts/_memory/bmad-wrappers-are-opencode-only-bridges.md` — the workflow-mirror premise for `sudo-*` wrappers is retired → F
- EDIT `_artifacts/_memory/sandbox-denies-writes-under-dot-claude-hooks-skills.md` — drop the retired surface from the maintained list → F
- EDIT `_artifacts/_memory/grep-skips-gitignored-projects.md` — a tense change, not a repoint: it names the surface inside a true anecdote about a past investigation → F
- EDIT `.agents/commands/smh-update-maps-indexes.md` — drop `workflows` from the `{rules,workflows,skills,commands}` master-map brace lists at lines 48 and 263 → F
- EDIT `.opencode/commands/smh-update-maps-indexes.md` — byte mirror, regenerated by the Step 8 sync → F
- EDIT `.agents/rules/project-law.md` — the tier-1 inventory at line 20 drops `workflows` → F
- EDIT `.claude/skills/INDEX.md` — byte tree-copy of the master skills INDEX, regenerated by the Step 8 sync → F
- EDIT `docs/migrations/install_guides/new_machine-migration-guide.md` — line 423 says the sync "refreshes the Antigravity workflows"; it refreshes the Antigravity skills → F
- EDIT `_artifacts/_memory/thin-projects-center-owns-workflow-law.md` — line 11's toolkit inventory drops `workflows` → F
- EDIT `_artifacts/_memory/sop-doc-currency-gate.md` — line 20, the fourth copy of the `sop_currency` exempt list → F
- EDIT `_artifacts/_memory/e2e-gate-fiction-test-guardrails.md` — line 34 names "the antigravity workflow mirror" as a live surface → F
- EDIT `_artifacts/_memory/toolkit-sync-covers-agents-not-docs.md` — line 31 quotes the "Rebuild after editing rules/workflows" sentence Step 5 removes → F
- EDIT `_artifacts/_memory/doc-graph-unc-hang-and-scope.md` — lines 10 and 17, the same sentence → F
- EDIT `_artifacts/_memory/git-branch-model-standard.md` — line 90's toolkit inventory drops `workflows` → F
- EDIT `docs/migrations/install_guides/vscode-ide-extension-migration.md` — line 235 lists "workflows" among the toolkit's surfaces → F
- EDIT `.agents/scripts/sync-agents.ps1` — launcher eligibility, master placement, retired-cache purge, deletions, header → A, B, C, D
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
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — the `/smh-sync-agents` row at line 4442 (inside §19, not §3), `-GlobalsOnly`, mermaid, §19 box → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line → F
- EDIT `docs/_scc_sops_prds/INDEX.md` — line 119 note → F
- EDIT `docs/_scc_sops_prds/file_folder_structure+maintaining.md` — three stale sites (lines 13, 43, 382) → F
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

`run_all.py` (73 test files) · `workflow_lint.py --toolkit-only` · `check_maps.py --depth3-only --strict`
· `check_links.py` · the armed `sop_currency` and Jira commit-msg gates · `CS-18 Q` under `pwsh`. Then
`/smh-code-review`. `CS-18 R` binds only in the main checkout after a real sync has run the purge, so a
lane run reports it as SKIP with the stated reason; the purge code itself is asserted by `CS-18 C`, and
the standing suite on `main` proves `R` after the operator's first post-landing sync.

## Out of scope, named

- **The Antigravity global cache** (`~/.gemini/config/skills/`) — the follow-on, gated on Step 0 (b).
- BMAD's `.agent/skills/` install and its manifest `ides: [claude-code, antigravity]` — untouched.
- Rule frontmatter (`trigger:` / `globs:` — Antigravity's rule loader is not changing).
- The permission fence (`.agents/permissions/`, `antigravity_permissions_apply.py`) — SCC-378's.
- The two project copies of the sync engine — see **Port** below; a `## Your Actions` decision.
- Whether the `.vscode/extensions.json` recommendation for the extension comes back — the operator's.

## Port — `sync-agents.ps1` exists in three repos (`port-checklist.md`)

**⚠️ AUDIT FINDING (2026-09-04): this section did not exist, and its absence was a mechanical NO-GO.**
`port-checklist.md` fires when the scope names a file that exists in more than one repo, and
`/smh-self-audit`'s rules-in-force line makes a missing section a NO-GO rather than a note (SCC-176).
The plan previously dismissed this in one line that named `Projects/sudo-command-center` **and the
skeleton** — and the skeleton carries no engine copy at all, while `Projects/Fresh_Workspace_BMAD`,
which does carry a copy and 24 workflow files, was named nowhere.

Measured from the main checkout, where the submodules are populated:

| Repo | Engine copy | Diff vs the lobby's | `.agents/workflows/` | Own git repo |
|---|---|---|---|---|
| the lobby (this ticket) | `.agents/scripts/sync-agents.ps1` | — | 41 files | yes |
| `Projects/sudo-command-center` | present | **differs** (+95 / −412 lines) | **41 files** | yes, own board |
| `Projects/Fresh_Workspace_BMAD` | present | **differs** (+240 / −706 lines) | **24 files** | yes, own board |
| `Projects/sudo-project-skeleton` | **absent** — it has `.agents/scripts/`, but no `sync-agents.ps1` in it | n/a | none | yes |

**The decision: this ticket does not port, and the reason is the rule's own, not convenience.** Both
copies differ from the lobby's by hundreds of lines, both are separate git repos with their own boards,
and a lobby ticket editing files inside them produces a commit no ticket of theirs accounts for — the
same constraint `sop-currency.md` §"Known drift" already records for the AGY copy. The six checks are
answered for **that decision**:

1. **A path git gave you is used exactly as git gave it** — n/a to this ticket's diff; no path in the
   158-row change set is consumed from git output. Due at the port, where the target's own engine
   handles its own paths.
2. **Operator-facing text goes through `printf`, never `echo`** — n/a: this ticket adds no shell
   script. The engine is PowerShell and uses `Write-Host`, matching every existing cache routine.
3. **On a write, verify the FILE — not `$?`** — **due and answered here**, because the engine writes:
   this ticket's only machine-cache write is the one-time retirement purge, and `CS-18 R` verifies it by
   reading the directory back; `CS-18 Q` byte-compares every committed launcher against a fresh emit.
   Neither reads an exit code.
4. **No `.agents/rules/` path the target repo does not carry** — this ticket edits
   `.agents/rules/sop-currency.md`, which is lobby-only law; neither project repo carries it
   (each project's `.agents/` holds `INDEX.md`, `rules/`, `scripts/`, `skills/`). Nothing in the change
   set points a project at a lobby rule path.
5. **It runs on BOTH machines** — the engine is `pwsh`, present on both. The plan names every gate by
   bare script name and contains no bare `python `. The `.gitattributes` fix in Step 3 exists
   *because* of the PC, and is the one place where the two machines genuinely disagreed.
6. **Hooks stay repo-local, and the port needs the target's OWN key** — both project repos carry their
   own `.githooks/` (4 and 2 files) and their own boards. **The port is therefore a follow-on ticket in
   each repo under that repo's key, and it is not optional there either**: both carry
   `.agents/workflows/` and both go dark on 2026-11-01.

   > **⚠️ AUDIT FINDING, third pass: the detector this check leaned on is switched off for both
   > repos.** `check_maps.py` does keep `.agents/workflows` in `vendor_markers` — it is there today,
   > so nothing changes at landing — but `fan_out_targets` (`check_maps.py:245`) lints only the names
   > in `.agents/maintained-projects.txt`, which are `AGY_AVIATIONCHAT` and `NEXgen-VR-Director`,
   > neither of which carries the engine; `Fresh_Workspace_BMAD` is de-listed there by design and
   > `sudo-command-center` was never listed. And the gate this ticket runs, `--depth3-only`, exits
   > before conformance is reached at all. A signal nobody receives is memory with extra steps.
   >
   > So the follow-on goes into `## Your Actions` as a **decision**, worded as one: *"Decide whether
   > `Projects/sudo-command-center` and `Projects/Fresh_Workspace_BMAD` get the workflows-to-skills port
   > before 2026-11-01"*. ⛔ Fourth pass: **not** "mint the follow-on tickets" — `jira_feed.py`
   > `banned_action_rows` refuses a row that asks the operator to create ticket work (SCC-163), and the
   > natural per-repo spelling was measured REFUSED. A decision row passes; the row itself is in Step 9.
   > `Fresh_Workspace_BMAD` is a frozen template whose disposal `maintained-projects.txt` already
   > records as the operator's call.

## Open questions

None blocking. The `claude/teaching-edition` landing order is stated in Step 3 and owed as a
`## Your Actions` row. Parent epic placement on the board is the operator's (guardrail 2); the ticket is
minted bare like its five sibling sync-agents tickets.

---

## Scope ruling (2026-09-04)

After the fourth self-audit pass returned NO-GO, the auditor reported that every finding of consequence
across four passes sat in the machine-global-cache half of the ticket — a claim manifest, a refusal test,
atomic writes and eight test cases designed to protect a directory that does not exist on this machine —
and recommended splitting the ticket: ship the retirement half, defer the cache to a follow-on gated on
one measurement. The operator's word: **"Approved"** (2026-09-04, on that recommendation). This body is
the retirement half. The four audit records below are kept as history; their findings on the retirement
half are all folded in, and their findings on the cache half are the reason it is not here. Editing the
plan re-armed the plan-first gate; the cut plan waits for the word again.

---

## Self-Audit (2026-09-04)

**Level: LEDGER+BLAST** (41 `DELETE` rows, a script others import, four door surfaces, two gates,
a rule, and a file that exists in more than one repo). **Mode: PRE-WORK.** Three lenses, run blind
to each other, merged under the anchor rule. Corroboration set the sort order only; severity is by
consequence alone.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  existence sweep of all 12 named PowerShell symbols, 15 test helpers, 34 CS-18 sub-blocks,
             8 sibling-test line anchors and 9 script/doc line anchors named by Steps 5-6
             Declared Change Set completeness - re-parsed (135 entries, EDIT 90 / DELETE 41 / NEW 4,
             incomplete: []) then swept the live tree for surface mentions absent from the block
             the plan's measured counts re-derived from disk (39 ag-eligible, 24 gen + 15 hand,
             41 workflow files, 74 house skills, 56 bmad, the $cxOnly pair, 25/26 launcher EDIT rows)
             both-machines: every command the plan tells the builder to run; grep for a bare `python `
             lane fit: deploy-surface scan of the change set
             test strategy against tests-must-gate-for-real.md
             Scope Ledger: acceptance precondition, every CREATE x its row, caller counts
read:        the plan (433 lines) - sync-agents.ps1 - test_command_surfaces.py - the 8 sibling tests -
             workflow_lint.py - record_map_changes.py - sop_currency.py - generate_doc_graph.py -
             check_maps.py - check_links.py - run_all.py - tests-must-gate-for-real.md -
             sop-currency.md - AGENTS.md - .agents/AGENTS.md - the four INDEX files - the SOP -
             file_folder_structure+maintaining.md - tdad_stack_install_guide.md - workspace-standard.md -
             smh-adviser-board.md - smh-clean-code-audit.md - smh-quick-dev.md - opus-auditor.md -
             .gitattributes - three _artifacts/_memory files
verdict:     findings below

lens:        2 Parity + Blast
checks_run:  path delete sweep - all repo-wide references to the surface, live sites separated from
             archived _artifacts history; markdown links and #L anchors
             command file: four platform doors + commands/INDEX.md for both edited commands
             command name change: none in the change set - cleared
             rule: sop-currency.md citers + workflow_lint _RULE_POINTERS - cleared
             scripts: .githooks/ callers, own tests, scripts/INDEX.md - cleared
             gate/hook armed: no new gate ships; SOP-ENFORCE present - cleared
             SOP / usage surface same-commit against the real _SURFACES list in sop_currency.py
             _artifacts/_memory legality and the SCC-370 precedent
             a file existing in >1 repo against port-checklist.md
             twins: cicd-* siblings carry no reference to the surface - cleared
             sibling worktrees after a fetch
read:        the plan - .gitattributes - sop_currency.py - workflow_lint.py - check_links.py -
             record_map_changes.py - check_maps.py - port-checklist.md -
             agent-memory-is-long-term-only.md - smh-clean-code-audit.md - smh-quick-dev.md -
             opus-auditor.md (both copies) - tdad_stack_install_guide.md - the SCC-370 plan -
             the SCC-388 worktree diff - a cross-repo find for sync-agents.ps1
verdict:     findings below

lens:        3 Pre-Mortem
checks_run:  the new mirror and its purge on a machine with no cache dir, an unmarked dir, a
             name-colliding operator-authored skill, and an interrupted run
             the one-time retirement purge against the ~/.codex/prompts purge it copies
             the 41-file delete against every live citing site, and which gate would see each
             check_maps vendor_markers keeping the surface on purpose - walked, home base exempt,
             a project clone reports STALE-VENDOR as intended - defused
             the armed sop_currency gate against Step 6's same-commit law edits - defused
             .claude/skills under the OS sandbox - Step 8's parenthetical is correct - defused
             the platforms: collapse and smh-adviser-board's inline law - the brain's section is a
             capability self-test, not a platform branch, so the deletion is safe - defused
             the description-budget arithmetic against a live measurement of all 39 launchers
             what the Customizations panel shows the morning after
             CS-18 L/M/R SKIP semantics in a worktree versus the main checkout
             the SCC-388 overlap - a merge conflict, loud not silent - defused
read:        the plan - sync-agents.ps1 (header, Copy-Tree 157-206, the globals block 1255-1367) -
             check_maps.py - sop_currency.py - check_links.py - workflow_lint.py -
             test_command_surfaces.py CS-18 L/M - smh-adviser-board.md and its workflow door -
             smh-clean-code-audit.md - smh-quick-dev.md - opus-auditor.md (both copies) -
             tdad_stack_install_guide.md - four memory files - a live measurement of every
             ag-eligible launcher description and of the current workflow menu - core.hooksPath
verdict:     narratives below, all attached to anchored findings
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| plan:426 · `port-checklist.md` | "`Projects/sudo-command-center` and the skeleton carry their own copies of the sync engine and their own key space (as SCC-367 recorded) — a follow-on there when this lands, under their keys." | **The plan names the wrong second repo and carries no port section.** Measured from the main checkout where the submodules are populated: `sync-agents.ps1` exists in **three** repos — the lobby, `Projects/sudo-command-center` (which carries 41 `.agents/workflows/` files) and `Projects/Fresh_Workspace_BMAD` (24 files, named nowhere in the plan). `Projects/sudo-project-skeleton` carries no engine copy, so the copy the plan does name does not exist. `port-checklist.md` requires the six checks answered with command output for a file that differs across repos, and this command's rules-in-force line makes a missing port section a **NO-GO, not a note** (SCC-176). | **blocker** `x2` |
| `.gitattributes:34`, under the comment at `:22-23` | `.agents/workflows/*.md text eol=lf` — beneath "`sync-agents.ps1` writes `~/.gemini/antigravity/global_workflows/*.md` with LF, but this box runs `core.autocrlf=true`, so git hands the working copy of `.agents/workflows/*.md` CRLF" | The plan drops this pin (change-set row: "drop the `.agents/workflows/*.md` LF pin; the `*.sh` pin stays") and moves the byte-mirror contract onto `.agents/skills/<name>/SKILL.md` (row C, `L`/`M` re-aimed) — but `grep -c 'skills' .gitattributes` is **0**, so nothing replaces it. On the PC, `core.autocrlf=true` hands every `SKILL.md` CRLF on checkout while the cache is LF, and `CS-18 L`/`M` go red after every pull. That is the SCC-338 defect reproduced one surface over, on the machine where `L`/`M` bind. Acceptance rows **C and D** fail on the PC. | **blocker** |
| `.agents/opencode-agents/opus-auditor.md:37` and its byte twin `.opencode/agent/opus-auditor.md:37` | "1. **Load the audit workflow:** Read `.agents/workflows/cicd-self-audit.md` and follow it exactly." | Step 3's `git rm -r .agents/workflows/` deletes that file, and neither copy is in the Declared Change Set (the plan contains zero occurrences of `opus-auditor` or `opencode-agents`). The opencode audit subagent's step 1 becomes a read of a file that does not exist, directly under its own line "If any of these are missing, HALT and report which." No gate sees it: `check_links.py` is diff-scoped and these files are not in the diff, `CS-18 J`'s `RULE_SITES` names four other files, and `workflow_lint.check_both_machines` excludes the surface. Acceptance row **F** is false at close. | **blocker** `x2` |
| `.agents/commands/smh-clean-code-audit.md:98` and `:161`, both with byte-identical `.opencode/commands/` twins | `\| **Door parity** \| ` + "`.claude/skills/<name>/`, `.agents/skills/<name>/`, `.opencode/commands/<name>.md`, `.agents/workflows/<name>.md` all agree with the command's `platforms:`" | This is the machine floor of `/smh-clean-code-audit`, which `/smh-code-review` Step 3.5 runs **on this very lane** — the gate that closes this ticket instructs the auditor to verify a fourth door that will exist for none of the 39 commands. Neither copy is in the change set. Both are `.agents/commands/*.md`, a `sop_currency` surface, so deferring the fix to a later commit is blocked by the armed gate unless the SOP rides along. Acceptance row **F** is false at close. | **blocker** `x2` |
| plan:213-216 against `.agents/scripts/sync-agents.ps1:179-202` | plan: "`Copy-Tree … -Mirror` per dir, then write a marker file `.sync-agents-mirror` into the dir … purge = every cache dir carrying the marker whose name is not in the source set. Never `bmad-*`, never an unmarked dir (the operator's own global skills)." · engine: `$kept` is built from the **source** tree, then `if (-not $kept.Contains($rel)) { Remove-Item -LiteralPath $item.FullName -Recurse -Force }` | **The marker lives inside the directory the mirror rebuilds, so every sync deletes it and the next statement writes it back.** Two consequences. (1) The marker gates the *purge* only — nothing gates the *mirror*. If the operator hand-writes `~/.gemini/config/skills/<one-of-our-names>/` under the vendor's documented path, the mirror runs on his directory, deletes everything in it that is not ours, overwrites his `SKILL.md` and then stamps our marker on it. Row C's "unmarked dirs are never touched" reads as blanket protection and is purge-only protection: **a data-loss path**. (2) Any interruption between the delete and the rewrite leaves a fully-mirrored, permanently unmarked directory that the purge can never reclaim and that `L`/`M` do not report (they report *marked* orphans) — a retired command keeps serving its old body from the Global menu with every gate green. | **blocker** |
| plan:43-50, against plan:75 and plan:77 | "the payload Antigravity carries after this ticket is the same 35,577 characters it carries now, minus the 4,921 the workflow menu spent" | **Measured on this tree, the claim is wrong in direction for a project workspace.** The 39 ag-eligible launcher descriptions total **16,832 characters**; the current workflow menu totals **5,051** across 40 files, because SCC-195 capped each at 135. In the lobby the global copies share names with the workspace ones and the vendor's "workspace beats global" precedence probably absorbs them — probably, since that is a rule about which body runs, not a documented statement that the injected description list is deduped. In a **project** workspace there are no workspace copies, so the payload goes from 5,051 to 16,832: it roughly **triples**, on exactly the surface SCC-195 was written for, in the same ticket that retires the SCC-195 budget machinery. The only detector anywhere in the plan is a hands-only alphabetical spot-check the morning after. | **blocker** |
| `_artifacts/_memory/bmad-wrappers-are-opencode-only-bridges.md:18` · `sandbox-denies-writes-under-dot-claude-hooks-skills.md:30` · `grep-skips-gitignored-projects.md` | "those target CUSTOM (non-BMAD) skills that Antigravity does NOT get natively, so they need the sync's antigravity workflow-mirror path (`.agents/workflows/`)" | Acceptance row **F** names **memory** explicitly, and Step 7 declares four files. Measured, **five** live memory files name the surface and three of them are undeclared. No test can catch it — `RULE_SITES` holds no memory path. This is SCC-370's own recorded miss repeating: its plan noted "the **SEVENTH** memory file; Step 5 named six." | major `x2` |
| plan:155 against `docs/_scc_sops_prds/workflows_testing_SOP.md:4442` | plan: "§3 `/smh-sync-agents` row (drop the 135-char paragraph)" · SOP §3 begins at line **255** (`## 3. The two laws above every command`) and lines 255-320 contain no occurrence of `smh-sync-agents`, `135` or `description`. The paragraph is line **4442**, inside §19's invocation table. | The builder is sent to a section that holds nothing of the kind. If §3 is edited and "§19's invocation table footnote" is read as the separate `ⓘ` block that follows the table, line 4442 survives and acceptance row **F** is false at close. | major |
| plan:269 against `.agents/scripts/tests/test_door_preflight_order.py:499` and `:507` | plan: "`test_door_preflight_order.py` line 499 glob removed" · line 499 is `+ sorted(REPO.glob(".agents/commands/*.md"))`; the workflows glob is line **507** | A builder following the cited number deletes the **commands** glob from the SCC-193 "sign-off wording, pinned both directions" block, gutting that check's main surface while leaving the workflows glob to resolve to an empty set. Two checks silently weakened, both still green. | major |
| plan:107, plan:417-418, `step 9`, against `test_command_surfaces.py` CS-18 `L`/`M` | Gates: "the door-parity check and `CS-18 L`/`M`/`R` bind only in the main checkout after the ceremony's sync, so a lane run reports them as SKIP with the stated reason." The block reads `_is_main = wf.tree_tag(ROOT)[2]` and registers `True` when false. | The three assertions that are the *only* proof of the cache half of row C report success while asserting nothing everywhere the plan runs them, and the plan never schedules the run that would bind them — Step 9 is four hands checks in the UI, and the ceremony before it is a sync, not a suite run. Row C closes green, proven by nobody; the first evidence of a mis-written cache is a hands step failing with no test to say which of the three ways it failed. | major |
| `.agents/commands/smh-quick-dev.md:365` + byte twin · `docs/_scc_sops_prds/tdad_stack_install_guide.md:319` · `_my_resources/open_tasks/plan_adviser-board-rework.md` | "**Generated surfaces are never hand-edited.** `.agents/workflows/`, `.opencode/commands/`, and" | Three further live sites naming a directory that will not exist, none in the change set. The first pair is a `sop_currency` surface, so it cannot be cleaned up in a later commit for free. | minor |
| plan:136 against `.agents/scripts/generate_doc_graph.py:575` and `:21` | plan: "prose `rules/workflows` → `rules/commands` (3 sites)" · the literal string appears **once** (line 575); the only other surface-naming prose is line 21, spelled `prose toolkit (rules / workflows / skills / commands)` | The builder hunts three sites and finds one — either two lines get edited that were never in scope, or line 21's differently-spelled site is missed. | minor |
| plan:414 (Gates) against `.agents/scripts/tests/run_all.py:53` | "`run_all.py` (72 files today)" · `FILES = sorted(p.name for p in HERE.glob("test_*.py"))` discovers **73** on disk | A stale baseline in the line the close-out reads for its expected count. No behaviour attached. | minor |

### Observations (uncounted, non-blocking)

- `sop_currency.py`'s real `_SURFACES` is narrower than the plan's Step 6 parenthetical claims: it is
  `.agents/commands/` (`.md`), `.agents/rules/` (`.md`), `.agents/scripts/git-hooks/`, `.githooks/`,
  `.agents/scripts/` (`.py`, `.ps1`) and the exact match `AGENTS.md`, with `_EXEMPT_NAMES = {"INDEX.md"}`
  and `_EXEMPT_PREFIXES = (".agents/scripts/tests/",)`. The declared `.agents/scripts/INDEX.md` edit and
  all eight test-file edits are exempt and fire nothing. The direction that matters: Step 5's four `.py`
  edits **do** fire the gate and are not bound by Step 6's "same commit as Step 2" instruction.
- SCC-370's staging guard is not carried forward — it required `git status --short _artifacts/_memory/`
  immediately before staging, because the store is shared across every lane on the machine. SCC-388 is
  live right now and touches no memory file, so today's exposure is nil, but the guard costs one line.
- `check_links.py` is diff-scoped and skips deleted files, so the archived `_artifacts/` mentions of the
  surface will not turn the gate red. Archive history is legitimately exempt from row F.
- The plan's structural checks are almost entirely source-contains asserts. `tests-must-gate-for-real.md`
  says "the only way to prove a structural test non-vacuous is a mutation", and the plan contains no
  occurrence of `mutation`. `/smh-quick-dev` Step 3 requires the sweep regardless, so this is a note.
- `docs/_scc_sops_prds/file_folder_structure+maintaining.md:43` carries a third stale mention inside a
  mermaid node; the plan names only lines 13 and 382. The file is in the change set, so this is
  completeness inside a listed file rather than an unlisted edit.
- Step 0's baseline is marked "optional", and it is the only check that can ever answer whether the old
  global cache was read at all. Without it, a Step 9 item 3 failure cannot be told from a pre-existing
  condition.

### Landing-order dependency

**SCC-388 lands first.** The lanes overlap on two files. `_artifacts/_main/INDEX.md` is a guaranteed
textual conflict — both insert a new row immediately under the separator — and this lane has already
resolved that conflict once, at `63ce167c`, when it absorbed `origin/main`. `AGENTS.md` overlaps by file
but not by hunk: SCC-388 rewrites the §3 protocol-size figure near line 44, while this lane rewrites the
§4 "Master toolkit" and "Lobby tool dirs" rows and §8, so git auto-merges. SCC-388's third file,
`.agents/scripts/check_maps.py`, is untouched here on purpose. Order it that way because SCC-388 is the
smaller, already-green lane, and because if this lane lands first SCC-388 inherits a hand merge in the
largest law file in the repo, resolved by whoever holds the smaller ticket. The cost is asymmetric.

```
Audit verdict: NO-GO
```

**The grounds, both named by the rule.** The port rule fires mechanically — `sync-agents.ps1` exists in
three repos, all three carrying the surface this ticket deletes, and the plan has no port section
answering `port-checklist.md`'s six checks; `.agents/rules/port-checklist.md` makes that a NO-GO rather
than a note. And five anchored findings break an acceptance row outright: rows **C** and **D** on the PC
(the LF pin), row **F** three times over (the opencode auditor, the clean-code-audit floor, three
undeclared memory files), row **C**'s data-loss path in the marker design, and the budget paragraph that
reassures with a number measured against the wrong roster.

None of it is a re-scope. Every finding closes inside this lane's own subject, and the fixes are folded
into the sections below.


---

## Self-Audit — second pass, after the amendments (2026-09-04)

**Level: LEDGER+BLAST. Mode: PRE-WORK re-audit.** Two lenses (Repo Reality + Scope Ledger, and
Parity + Blast aimed at the amendments themselves), run blind to each other. Pre-Mortem was not re-run:
its five narratives all attached to first-pass findings, every one of which is now closed, and the
amendment rule forbids adding lenses rather than deleting them.

```
lens:        1 Repo Reality + Scope Ledger (re-audit)
checks_run:  each of the 13 first-pass findings verified closed against the tree, not against the
             plan's claim that it was fixed
             the completeness sweep re-run WIDER - not just the literal `.agents/workflows` path but
             the brace-expansion form `{rules,workflows,skills,commands}` and a bare `workflows` word
             sweep over every live law, command, script and doc surface, subtracted against the
             change set
             `**` gitattributes semantics proved empirically with `git check-attr -a` in a scratch
             repo rather than reasoned from memory
             the budget re-measured independently three ways until the counting method reproduced
             `--case` verified to exist in `_harness.py` and `CS-18` verified to be a real block label
             declared_change_set parse; every EDIT/DELETE path existence-checked; the 41 DELETE rows
             proved set-equal to `.agents/workflows/*.md` on disk
             Scope Ledger over every artefact the amendments introduced
             cross-section agreement: acceptance rows vs Engine design vs Tests re-aim vs change set
read:        the amended plan - port-checklist.md - .gitattributes - sync-agents.ps1 - _harness.py -
             test_command_surfaces.py CS-18 - test_door_preflight_order.py - run_all.py -
             sop_currency.py - workflow_lint.py - check_links.py - check_maps.py -
             generate_doc_graph.py - project-law.md - smh-update-maps-indexes.md and its twin -
             opus-auditor.md (both) - smh-clean-code-audit.md - the SOP - five memory files -
             the three Projects repos from the main checkout
verdict:     13 of 13 first-pass findings closed; 5 new (2 major, 3 minor)

lens:        2 Parity + Blast (re-audit)
checks_run:  all eleven new change-set rows: path exists, cited line read literally, implied edit safe
             the generated-mirror claims verified against sync-agents.ps1:1202 and Sync-CommandDir
             sop_currency classify() walked for every new row and every command file the plan edits
             `**` glob proved empirically with git check-attr against three candidate patterns
             the manifest redesign attacked on: operator-dir clobber, -WhatIf, corrupt/empty/
             hand-edited manifest, concurrency across worktrees, Windows /MIR versus the PS branch
             landing order re-derived after a fetch
             twins: every `.agents/commands/` and `.opencode/commands/` file naming the surface
             cross-section agreement on the manifest, CS-18 S and .gitattributes
read:        the amended plan - .gitattributes - sop_currency.py - sync-agents.ps1 (Copy-Tree both
             branches, Sync-CodexSkills, the globals block, $IsLobby) - test_command_surfaces.py
             CS-18 L/M - the four command files and their twins - cicd-* siblings - git check-attr in
             a scratch repo - git fetch/worktree/log/diff against origin/main
verdict:     findings below
```

### Disposition of the first pass — 13 of 13 closed

Every first-pass finding was verified against the tree rather than against the plan's claim to have
fixed it. The Port section now exists and its six checks reproduce when run independently; the
`.gitattributes` swap is correct and its `**` globs were proved with `git check-attr` rather than
assumed; both `opus-auditor` copies and both `smh-clean-code-audit` sites are declared; the memory
sweep now finds exactly five live files and all five are declared; the manifest redesign genuinely
removes the delete-then-rewrite defect, because `Copy-Tree` enumerates `$dstRoot` and the root-level
manifest sits one level above every enumeration; the three budget numbers (27,026 · 16,832 · 5,051)
each reproduced exactly; and the SOP line, the test-glob line, the `--case` invocation, the
`sop_currency` surface list, the two `generate_doc_graph` sites and the 73-file count all verify.

### New findings, second pass

| anchor | literal text read | consequence | severity | now |
|---|---|---|---|---|
| `.agents/commands/smh-update-maps-indexes.md:48` and `:263`, with byte-identical `.opencode/commands/` twins | "`` `.agents/{rules,workflows,skills,commands}/INDEX.md` `` \| **MASTER** family maps (this repo is the source) \| **Editable here** — fix drift" | The first amendment's sweep matched the literal path and missed the brace-expansion form. This is the command that regenerates `docs/repo-map.md` and `docs/doc-graph.{md,json}` — the two artefacts row **F** requires — so after Step 3 it sends the operator to reconcile a MASTER map at a path that does not exist. A `sop_currency` surface, so a later cleanup commit is not free. | major `x2` | **fixed** — Step 6 + two change-set rows |
| plan row **A** against the `CS-18 A` description in the Tests section | row A: "`.gitattributes` … **does pin `.agents/skills/**/SKILL.md` and `.claude/skills/**/SKILL.md` LF**" · `CS-18 A`: "no workflows dir, no mirror function, no `Get-AgDescription`, no cap number, comment-stripped" | **The first amendment added a clause to an acceptance row and no assertion for it.** `grep -rn gitattributes .agents/scripts/` finds no test in the repo that reads the file — which is precisely why the SCC-338 pin it replaces could be dropped silently in the first place. Row A would close green on a clause proven by nobody, and the failure would surface as `L`/`M` red on the *other* machine after the next pull: the same self-certification the first pass called a blocker for row F, reintroduced by the fix for it. | major `x2` | **fixed** — `CS-18 A` now reads `.gitattributes` both ways |
| plan Engine design: "**order: claim, then mirror.** Write the name into the manifest *before* mirroring that dir" against "the mirror refuses to clobber. Destination dir exists and is **not** in the manifest → skip it" | both, as written | **Read in the stated order the two rules cancel.** Claim first and the name is in the manifest by the time the refusal test runs, so the test passes and `Copy-Tree -Mirror` clobbers the operator's directory — reinstating the exact data-loss path the redesign exists to close. | major | **fixed** — the pass is now five numbered steps, refusal tested against the OLD manifest before any claim |
| plan's `-WhatIf` clause against `sync-agents.ps1:976-984` | plan: "`-WhatIf` prints `would mirror …`" · engine: `if (-not $WhatIf) { New-Item …; Copy-Tree … -Mirror } else { Write-Host … }` | The shape the design copies guards only the *copy*. Implemented literally, a dry run writes the claim manifest — claiming all 39 names on a machine where the cache is measured absent — and a name the operator later hand-writes there is then found *claimed*, the refusal is skipped, and his directory is emptied. The data-loss path reached through the one mode that writes nothing. | major | **fixed** — `-WhatIf` writes nothing at all; `CS-18 S` case (c) |
| plan's manifest clause against `sync-agents.ps1:234-238` | engine: `Write-Warning ("sync-agents: unreadable {0} ({1}) - purging nothing this run" …); return $empty` | No stated behaviour for a corrupt, empty or hand-edited manifest — and the house pattern fails safe against *deletion*, which inverts on a claim manifest: unreadable would read as "nothing is ours", the mirror would refuse all 39, and the Global menu would freeze at the last good run while `L`/`M` iterated zero claimed dirs and passed. Cache dead, every gate green. | major | **fixed** — unreadable manifest means the whole pass is inert; `CS-18 S` case (d) |
| plan Step 3 against `sop_currency.py:72` | Step 3 edits `.agents/commands/smh-adviser-board.md`; `_SURFACES` row 1 is `(".agents/commands/", (".md",), "the / command menu")` | The first amendment bound Step 5's `.py` edits to the SOP commit and left Step 3 out. A builder committing Step 3 alone is rejected by the armed hook, and the shortest way past is `[sop-ok]` on a `platforms:` change — a false attestation, permanent in the log. | major | **fixed** — Step 3 header now says "in the SAME commit as Steps 2, 5 and 6" |
| plan Step 8's staging list against the five new `.opencode/` change-set rows | Step 8: "commit the regenerated `.agents/skills/*/SKILL.md`, `.claude/skills/*/SKILL.md` and `.agents/.sync-manifest.json`" | The amendments added five generated-mirror rows and this list was not touched, so a builder following it literally leaves five declared EDITs dirty and the close-out preflight refuses the tree. Loud, not silent — but a re-run of the sync plus a second commit at the worst moment. | minor | **fixed** — the five mirrors named in Step 8 |
| `.agents/rules/project-law.md:20` | "\| **Tier 1 — workflow law** \| the command center's `.agents/` \| rules · commands · skills · **workflows** · scripts · templates \|" | Live tier-1 law naming a master-toolkit directory that will not exist — the identical construction to `AGENTS.md:107`, which Step 6 already edits. A `sop_currency` surface. | minor | **fixed** — Step 6 + change-set row |
| `.gitattributes:20-33` | "`sync-agents.ps1` writes `~/.gemini/antigravity/global_workflows/*.md` with LF … `test_command_surfaces.py --case CS-18` case L byte-compares door against cache" | The change-set row swapped only the pin line; the 14-line comment above it survives, still asserting the sync writes `global_workflows` and still describing `CS-18 L` in terms of `.agents/workflows/*.md`. Row **F** forbids exactly that, and the plan already treats a test *comment* as a row-F item. | minor | **fixed** — Step 3 rewrites the block, keeping the SCC-338 measurement as the `ⓘ` reason |
| plan:12 and the landing-order paragraph against `git log origin/main` | plan: "**Base:** `origin/main` @ `70154040`" · "**SCC-388 lands first.**" · `origin/main` is now `eee79727 Merge pull request #151 from … chore/SCC-388-resync-shells-gate`, and `git merge-base --is-ancestor origin/main HEAD` said **no** | SCC-388 landed **during this audit**, so the guidance had become a description of the past, the stale `Base:` fed `/smh-code-review` Step 0.7's blast re-derivation, and the `_artifacts/_main/INDEX.md` conflict the paragraph called resolved was not — `63ce167c` resolved it against `70154040`, which predates the merge. | minor | **fixed** — `origin/main` absorbed at `ef1bbd31`, `Base:` updated, landing-order restated below |
| plan Step 0 against acceptance row **H** | Step 0 is REQUIRED and sits before Step 1, outside `## Your Actions`; row H's closest clause was "the hands check in `## Your Actions` is recorded" | Scope-Ledger row with an empty acceptance cell: the ticket could close with H green having never taken the baseline — the precise outcome the amendment making Step 0 required exists to prevent. | minor | **fixed** — row H now requires both baseline numbers in the walkthrough before Step 1 |

### Observations (uncounted)

- **One residual clobber path the manifest cannot close, and it is the accepted shape.** Once a name is
  claimed it stays claimed while its source lives, so if the operator deletes a claimed dir and authors
  his own skill under a name we already own, the next sync mirrors over it. Row C's wording ("refuses
  to write into an existing **unclaimed** dir") is literally true, and every other cache in this engine
  uses the same ownership model. One line in the walkthrough, not a design change.
- **The retirement purge of `~/.gemini/antigravity/global_workflows/` deletes by exclusion, not by
  claim** — it copies the `~/.codex/prompts` shape, `Where-Object { $_.Name -notmatch '^bmad-' }` then
  `Remove-Item`. That shape already shipped once and the directory is ours by construction, so it
  stands; it is simply the one write in the ticket that is not claim-gated.
- `.agents/workflows/INDEX.md` carries its own 87-char `description:`, so today's real injected menu is
  5,138 chars over 41 files rather than 5,051 over 40. The budget table's direction and magnitude are
  unaffected (16,832 / 5,138 = 3.28x).
- **Concurrency is smaller than it looks but not zero.** Two syncs racing would read-modify-write the
  root manifest and lose one run's claims. The single write per run in the rewritten pass reduces the
  window to one file operation; `-NoGlobals` in Step 8 is what keeps this lane out of the machine
  caches entirely, and the amendment now says so explicitly.
- `grep-skips-gitignored-projects.md` names the surface inside a true anecdote about a past
  investigation. Its change-set row says "a tense change, not a repoint" — rewriting the history would
  be worse than leaving it.
- The Port section answers all six checks but carries its measurements as a table rather than verbatim
  command output. Every number reproduced when re-run independently, so this is form, not substance.

### Landing-order dependency — settled by events

**SCC-388 landed at `eee79727` during this audit, and this lane absorbed it at `ef1bbd31`.** The
`_artifacts/_main/INDEX.md` conflict resolved as predicted — both lanes insert a row under the
separator — and `AGENTS.md` auto-merged, because SCC-388's whole diff there is the line-44 protocol-size
figure while this ticket rewrites §4 and §8. Overlap with the fifteen files the amendments added is
**nil**. **Third pass corrected the next sentence, which said no third lane was in flight.**
`git worktree list` shows `claude/teaching-edition` at `0d76f72c`, which **adds three files into
`.agents/workflows/`** (`smh-tour.md`, `smh-training.md`, `smh-new-project.md`) and pins six paths there
inside `validate_teaching_edition.py` — a `.agents/scripts/*.py` file, so a `sop_currency` surface.
**SCC-394 lands first.** Every count in this plan is drawn against `eee79727` and reproduces there; if
that lane landed first the delete would be 44 files and its validator would have to ride this ticket's
one commit. The price of going first is that lane's own — repoint three doors to `.agents/skills/` and
re-aim six validator paths, under its own key — the same shape the Port section chose for the two
project repos. It is recorded in `## Your Actions` so it is a decision, not a surprise.

```
Audit verdict: GO
```

**Why GO and not another round.** Both NO-GO grounds are gone: the Port section exists and its six
checks reproduce independently, and every finding that broke an acceptance row is closed with an
assertion attached rather than a promise — `CS-18 A` now reads `.gitattributes`, `CS-18 S` binds the
mirror's refusal in four ways during the build, and Step 9 item 0 is what makes `L`/`M`/`R` actually
run. The second pass found five new defects and every one of them was inside the first pass's own
amendments, which is the shape of a converging audit rather than a widening one: the plan's original
subject survived both passes unchanged. What remains open is recorded above as observations, none of
which changes a file.


---

## Self-Audit — third pass, on the plan as amended (2026-09-04)

**Level: LEDGER+BLAST. Mode: PRE-WORK.** Requested by the operator because the second pass's five
fixes were issued a GO without any blind lens reading them. All three lenses, blind, on the plan body as
it stood at `85e56a9c`. Every consequential claim below was re-measured by the auditor before it was
written down; three of the largest came from the Pre-Mortem lens and were promoted only after the
Repo-Reality check they implied was run by hand (the ceremony file, the `maintained-projects.txt`
allowlist, the post-Step-3 count).

```
lens:        1 Repo Reality + Scope Ledger (third pass)
checks_run:  all 32 cited path/line/name references resolved against the tree - all correct
             the five second-pass fixes, each verified against the tree - four hold, one does not
             declared_change_set parse (149, incomplete: []) + a WIDER completeness sweep (brace
             forms, bare `workflows`, install guides, .claude/skills, memory) - 6 undeclared sites
             both machines - no bare `python `; pwsh named 11 times
             lane fit - no deployable path
             internal consistency after two amendments - hunted `marker`, `optional`, `72 files`,
             `3 sites`, `line 499`, `skeleton`, `§3`, the Base: sha, every disk-table count
             Scope Ledger - every created artefact x its acceptance row; none empty
read:        the plan body (1-739) - .gitattributes - sync-agents.ps1 (nine regions) - sop_currency.py
             - check_maps.py - run_all.py - _harness.py - test_command_surfaces.py -
             test_door_preflight_order.py - the five edited commands - opus-auditor.md -
             project-law.md - sop-currency.md - .agents/AGENTS.md - AGENTS.md - workspace-standard.md
             - the SOP - four docs/_scc_sops_prds files - two install guides - seven memory files -
             .agents/skills/INDEX.md vs .claude/skills/INDEX.md (diff -q)
verdict:     findings below

lens:        2 Parity + Blast (third pass)
checks_run:  five edited command files - all doors, INDEX lines, Zoo cleared
             command name change - none
             rules - neither in _RULE_POINTERS; citers verified
             scripts - only .githooks/post-commit:20 calls any; no test pins TOOLKIT_FAMILIES
             gates/hooks - nothing armed or disarmed; SOP-ENFORCE present
             the 41-file delete - git grep over tracked files; one live hit outside the change set
             SOP / usage surface - _SURFACES walked against all 149 rows; the one commit is achievable;
             Step 8's later commit fires nothing
             memory - six declared, no seventh found by the narrow sweep
             files in >1 repo - Port trigger re-run from the main checkout; every figure reproduces
             the manifest design attacked on nine concrete sequences, THREE OF THEM MEASURED ON PWSH
             twins - no cicd-* sibling carries the sentence
             sibling worktrees - a FOURTH tree the plan says does not exist
read:        the plan body - sync-agents.ps1 (Copy-Tree both branches, Get-SyncManifest,
             New-LauncherSkillStub, Sync-CodexSkills, :81, :114, :332) - sop_currency.py -
             workflow_lint.py - check_maps.py - record_map_changes.py - generate_doc_graph.py -
             generate_repo_map.py - test_command_surfaces.py CS-18 - the five commands and twins -
             .roo/commands/smh-quick-dev.md - the teaching-edition worktree - four pwsh probes
verdict:     findings below

lens:        3 Pre-Mortem (third pass)
checks_run:  the "ceremony's sync" traced through /smh-close-task-merge-tree Steps 0-6 and
             --after-merge, every command, rule, hook and settings.json - IT DOES NOT EXIST
             Step 9 item 0 EXECUTED on the main checkout - tree_guard refused, exit 2
             CS-18 L's absent-cache branch against the measured state - SKIP registers True
             the ag-eligible set recounted before AND after Step 3 - 39 then 40
             the STALE-VENDOR handoff against fan_out_targets and maintained-projects.txt - OFF
             the retirement purge on a Mac that has not pulled - defused (it is code)
             $UserHome on native Windows - defused (USERPROFILE first)
             the .gitattributes swap under autocrlf - defused (no tracked SKILL.md blob has CRLF)
             _artifacts/_memory in this worktree and main - defused (a plain tracked dir in both)
             the "additive robocopy" claim for opus-auditor's twin - defused (overwrites in place)
             the -NoGlobals window - the old cache keeps serving, and its launchers still work
read:        the plan (all 1003 lines) - smh-close-task-merge-tree.md - wf_common.py tree_guard -
             test_command_surfaces.py CS-18 L/M - check_maps.py fan_out_targets - maintained-projects.txt
             - sync-agents.ps1 (Get-CommandPlatforms, Copy-Tree, the globals block) - .gitattributes -
             smh-adviser-board.md and its launcher - SOP:4442 - live: ~/.gemini, a real --case CS-18
             run on main, a CRLF sweep of every tracked SKILL.md
verdict:     narratives below - four, three promoted after the auditor re-ran their Lens-1 check
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| plan Step 9 preamble + item 0, row H, against `.agents/commands/smh-close-task-merge-tree.md` (the word `sync-agents` appears once, at `:35`, in the naming paragraph) and `.agents/scripts/wf_common.py:569` | plan: "the ceremony's plain `/smh-sync-agents` from the main checkout runs first" · "Immediately after the ceremony's sync, from the **main checkout**, run `python3 … --case CS-18`" · `wf_common.py`: `REFUSING - this is the MAIN checkout on `main`, but N lane worktree(s) are checked out … Or say you meant this tree: --on-main` | **The ceremony runs no sync, so the only proof of the cache half of row C was scheduled after a step nobody performs.** Both earlier passes built on the sentence and neither opened the ceremony file. Then the item-0 command itself refuses from the main checkout while any lane worktree exists (measured: exit 2 today, with `SCC-392` and `teaching-edition` on disk), and if the cache root is absent — measured absent — `CS-18 L` prints "SKIPPED: this machine has no Antigravity global cache" and registers `True`. Three green SKIPs close row C. The morning after, project workspaces still show the 40 old workflow entries, which still work because their launchers point at command files that still exist; the failure is invisible until 2026-11-01. Rows **C** and **H** false at close. | **blocker** |
| plan Engine step 1, against a pwsh probe | plan: "Unreadable, corrupt, or **truncated** → `Write-Warning` and **do nothing this run**" · measured: `Get-Content -Raw <zero-byte file> \| ConvertFrom-Json` → `$null`, **no throw** | A zero-byte manifest — the canonical "truncated" — never reaches a `catch`. It parses to an empty claim set, step 2 refuses all 39 existing dirs as unclaimed, the Global menu freezes at the last good run, and `L`/`M` iterate zero claimed dirs and pass. This is verbatim the "cache dead, every gate green" outcome step 1 was rewritten to prevent, reached through the one input it names. `CS-18 S` had no zero-byte case. Row **C** false. | **blocker** |
| plan Engine step 2 predicate + `CS-18 S` case (b), against a pwsh probe | plan: "`-PathType Container` falls through to `New-Item -ItemType Directory` on an occupied path, **which throws**" · S(b): "a bare *file* at one of our names is **refused, not thrown on**" · measured: `New-Item -ItemType Directory -Force` over an existing file → **no throw**, file's bytes intact | The stated reason is false on Mac/WSL. Two consequences: the un-fixed build does not throw either, so S(b) as worded passes on the clobbering build and **can never be seen RED** — a violation of Step 1's own red-first rule and of `tests-must-gate-for-real`; and the real behaviour splits by machine (Linux walks a file with `Get-ChildItem -Recurse`; Windows robocopy rc 16 → `throw` at `sync-agents.ps1:167`). | **major** |
| plan `:53-54`, `:94`, Step 9 item 3 "Expect **39**", against Step 3 and `.agents/commands/smh-adviser-board.md:3` | Step 3: "`smh-adviser-board.md` frontmatter `platforms: [claude, opencode, antigravity, codex]`" · today: `[claude, opencode, codex]` · measured: 39 ag-eligible today, `smh-adviser-board` not among them; **40 after Step 3**; its launcher description is **792** chars → **17,624** | Every count the ticket checks itself against was measured on `70154040`, before the plan's own `platforms:` edit, and both earlier passes confirmed the figures reproduced — which they do, for today's tree. The engine's source set is "the same set the retired cache carried", and that cache holds 40 files. Step 9 item 3's instrument was calibrated one short: a real single-entry truncation would count 39 and match the expectation exactly. Row **H**'s expected value wrong. | **major** |
| plan Port check 6, against `.agents/scripts/check_maps.py:245,663` and `.agents/maintained-projects.txt` | plan: "after this lands each project clone reports STALE-VENDOR — which is the detector that will surface the follow-on rather than leaving it to memory" · `check_maps.py:245`: `elif allow is not None and child.name not in allow: skipped.append(…"not in .agents/maintained-projects.txt")` · the list: `AGY_AVIATIONCHAT`, `NEXgen-VR-Director`; "De-listed 2026-08-07: Fresh_Workspace_BMAD" | The marker is already in `vendor_markers` today, so nothing changes at landing; and `fan_out_targets` skips both engine-carrying repos by name while the two it does lint carry no marker. The gate this ticket runs, `--depth3-only`, exits before conformance. The follow-on the Port section hands to a detector is handed to nothing — the exact "left to memory" it promised to avoid, until both project menus go dark on 2026-11-01. | **major** |
| plan Engine step 5, against a pwsh probe and `sync-agents.ps1:81` | plan: "5. **Purge** every old claim not in the source set, dropping its manifest entry" · `:81`: `$ErrorActionPreference = "Stop"` · measured: `Remove-Item -LiteralPath <missing> -Recurse -Force` → `ItemNotFoundException` | This purge iterates a manifest list, unlike `Sync-CodexSkills`'s which iterates `Get-ChildItem` and can only delete what it just saw. One hand-deleted claimed dir → terminating error → everything after `Sync-AntigravitySkills` in the globals block (codex mirror, reported counts) never runs. The second pass's `try/catch` was scoped to the mirror loop only. | **major** |
| plan landing-order paragraph, against `git worktree list` and `.claude/worktrees/teaching-edition` @ `0d76f72c` | plan: "`git worktree list` now shows no third lane in flight, so this lane lands next with nothing to order against" · that lane's diff: `.agents/workflows/smh-new-project.md`, `smh-tour.md`, `smh-training.md`, `.agents/scripts/validate_teaching_edition.py` (six hard-coded `.agents/workflows/` paths) | A live lane **adds three files into the directory this ticket deletes** and pins six paths there in a `sop_currency` surface. SCC-394 first → that lane's validator opens six paths that no longer exist. Teaching-edition first → the delete is 44 files and the validator joins this ticket's one commit. Unordered either way. | **major** |
| plan Step 8 staging list, against change-set rows for `.opencode/commands/smh-adviser-board.md`, `.opencode/commands/smh-sync-agents.md`, and `sync-agents.ps1:1115` | plan: "the **five** generated mirrors … `.opencode/agent/opus-auditor.md` plus `.opencode/commands/{smh-clean-code-audit,smh-quick-dev,smh-update-maps-indexes}.md`" (a brace of **four**) · `:1115`: `Sync-Dir $skillSrcDir $claudeSkDst (@('bmad-*') + $cxOnly)` — no `INDEX.md` exclusion; `diff -q` → `.claude/skills/INDEX.md` identical to the master | The second pass's own logged defect recurring at the sentence it fixed: says five, names four, omits two declared `.opencode/` EDITs, and `.claude/skills/INDEX.md` — a tree copy of a file Step 6 edits — is in neither the change set nor the list. A builder following it leaves three declared or undeclared EDITs dirty; the close-out preflight refuses the tree. | major `x2` |
| `.agents/commands/smh-sync-agents.md:51` (+ `.opencode/` twin) | "invocable surfaces (`.agents/{commands,workflows}`, `.claude/commands`, `.opencode/commands`):" | The file is in the change set; this site is not in Step 6's bullet for it. After Step 2 drops `.agents\workflows` from `Get-SurfaceState`, the command's own doc tells the operator `-Status` reads a directory the engine no longer scans. The `{commands,workflows}` spelling escaped both the literal-path sweep and the `{rules,workflows` sweep. | minor |
| `docs/migrations/install_guides/new_machine-migration-guide.md:423` | "`/smh-sync-agents -GlobalsOnly` used on Windows; it also refreshes the Antigravity workflows, the Codex prompts and the 56 bmad-* Codex skills" | The document a new machine is built from says the sync maintains an Antigravity workflow cache. Not in the change set; no gate sees it. Row **F** false. | minor |
| `_artifacts/_memory/thin-projects-center-owns-workflow-law.md:11` · `_artifacts/_memory/sop-doc-currency-gate.md:20` | "rules, `/` commands, skills, workflows, scripts, sync — lives once in the lobby" · "Exempt by design: `INDEX.md` churn, `reference/`, `templates/`, `skills/`, `workflows/`, `_artifacts/`, its own tests" | Two more live memories naming the retired surface — the `AGENTS.md:107` construction and the fourth copy of the exempt list. Seven memory files in all now; Step 7 named five. Row **F** names memory. | minor |
| plan change-set row for the SOP · plan Port check 1 · plan Engine step 3 | "— §3 row, `-GlobalsOnly`, mermaid, §19 box → F" · "no path in the 135-row change set" · "a single write also **closes** the read-modify-write race" (its own audit history at the time said "reduces") | Three stale sentences the amendments left behind: the machine-parsed change-set row still sends the builder to §3 after Step 6 was corrected to line 4442; the Port section's count is two amendment rounds old; the body overstates what the single manifest write buys. | minor |

### Observations (uncounted)

- **The panel count in Step 9 item 3 measures the wrong population** (Pre-Mortem, not promoted: an
  instrument-validity judgment, not a fact about the tree). The Customizations panel lists what the
  extension found on disk; SCC-195's recorded symptom (SOP line 4442, "workflows get dropped from the
  agent's list outright") was in what is *injected*. Adopted anyway, because it costs thirty seconds:
  item 3 now also asks the agent in the project workspace to list its `/` commands.
- **Sequence (ix) — a claimed name is reserved.** If the operator deletes a claimed dir and later creates
  his own under that name, the next sync mirrors over it. Every other cache in the engine has the same
  shape; it is now stated in the Engine design so it is known rather than discovered.
- **Absent vs unreadable manifest.** The house helper guards `Test-Path` before its `try`
  (`sync-agents.ps1:227`), which is what keeps a fresh machine out of the inert arm. The first draft of
  step 1 never distinguished the two; the rewrite does.
- **Windows `robocopy /MIR` throws where the PowerShell branch does not** (`:167`, rc ≥ 8). The
  `try/catch` around the loop body, already in the design, is what makes a locked destination on the PC
  recoverable rather than fatal.
- `.agents/workflows/INDEX.md` declares `platforms: []` and carries its own 87-char description, so
  "40 files · 5,051" is the injected menu and "41 · 5,138" is the directory. The plan's figure is the
  right one.
- Step 9 item 0b hard-codes `python3`; the `(PC: python)` gloss is now beside it.
- `record_map_changes.py` has no test file, so `TOOLKIT_FAMILIES` dropping `"workflows"` carries no
  assertion. Behaviourally inert (a family with no directory yields nothing).

### Landing-order dependency

**SCC-394 first; `claude/teaching-edition` after, under its own key.** This lane is current with
`origin/main` at `eee79727`; `SCC-392` is spent. The teaching-edition lane is the only other tree that
writes *into* `.agents/workflows/`, and every count in this plan reproduces exactly on `eee79727`. The
price of going first is that lane's: three doors repointed to `.agents/skills/`, six validator paths
re-aimed. Recorded in the plan body and, at close, in `## Your Actions`.

```
Audit verdict: NO-GO
```

**The grounds.** Row **C** is broken twice — its only binding proof was scheduled after a ceremony
step that does not exist, and its fail-safe never fires on the input it names — and row **H** carries an
expected count that is one short of the plan's own edit. `CS-18 S` case (b), as worded, could never be
seen RED, which breaks the red-first rule this lane runs on.

**Every finding is closed in the body above** — the Engine design's steps 1, 2, 3 and 5 rewritten
against the measured behaviours; `CS-18 S` at six cases; Step 9 rebuilt so the closing session performs
the sync and the `--on-main` run itself; the counts moved to 40 / 17,624; the Port section's handoff
moved from a dead detector to a `## Your Actions` decision; the teaching-edition order stated; Step 8's
list replaced by a rule; six more sites declared. The change set is now 153 rows.

**What changed between passes, stated plainly.** The first two passes found *missed sites* — files the
sweep did not open. This pass found *measured runtime behaviour* — three PowerShell semantics that read
the opposite way on this box from how the prose assumed, and one house ceremony that does not do what
the plan said it does. Prose audits are the wrong instrument for the first class; the `CS-18 S` cases
written RED against a real `pwsh` will settle them in minutes. A fourth blind pass follows because the
rule says so; if it returns only observations, the plan is ready for the word.


---

## Self-Audit — fourth pass, on the plan as amended (2026-09-04)

**Level: LEDGER+BLAST. Mode: PRE-WORK.** Three lenses, blind, on the plan body at `0ca86dd2`, briefed
to verify the third pass's fixes against the tree and to **measure** every claim about runtime
behaviour rather than read it. Lens 2 wrote a 56-line `pwsh` scratch implementation of the five-step
pass and drove nine sequences through it; Lens 1 probed seven manifest inputs, `New-Item` with and
without `-Force`, `Test-Path` on symlinks, and `Remove-Item` under `Stop`; Lens 3 ran the item-0b
command on the main checkout and five wordings through `jira_feed.banned_action_rows`. The auditor
re-ran the four load-bearing checks by hand before writing them down.

```
lens:        1 Repo Reality + Scope Ledger (fourth pass)
checks_run:  the eleven third-pass fixes, each against the tree - eight hold, three do not
             four pwsh probes on /usr/bin/pwsh 7.6.5 (seven manifest inputs; New-Item over a file
               with/without -Force; Test-Path on broken and good symlinks; Remove-Item under Stop)
             counts re-derived: 39 -> 40 after Step 3, 16,832 -> 17,624, 27,026, 5,051 - all exact
             declared_change_set parse - 153, incomplete [], every path on disk
             completeness sweep, widest form - 5 undeclared live sites (4 memory, 1 install guide)
             every path:line anchor in the body (27) opened - all correct
             generated-launcher census - 25 + 26, all declared, none undeclared
             both machines - one python3, glossed; pwsh x12
             lane fit - clean
             internal consistency after three rounds - 12 stale phrases hunted, 2 live
             Scope Ledger - one cell empty (the Port ## Your Actions row)
read:        the plan body and the third-pass record - sync-agents.ps1 (sixteen regions) -
             smh-close-task-merge-tree.md (all 790 lines) - smh-quick-dev.md - wf_common.py -
             _harness.py - run_all.py - jira_feed.py (SCC-163 Part B, SCC-193 Part B) -
             check_maps.py - maintained-projects.txt - .gitattributes - git-policy.md -
             test_command_surfaces.py - every cited site - seven memory files
             RAN: `--case CS-18 --on-main` from main (34/34, rc 0); `banned_action_rows` on the
               Port row (REFUSED); the four pwsh probes with output
verdict:     findings below

lens:        2 Parity + Blast (fourth pass)
checks_run:  Step 9 items 0a/0b adversarially - the closing session DOES stand on main with the
               lane pruned; --on-main IS accepted (measured 34/34); 0a says sandbox off; nothing in
               the house does a post-merge sync (hooks run only memory_store_check.py)
             the five-step pass MEASURED - 56-line scratch implementation, nine sequences plus one
               (a caught purge failure) - ONE DESIGN DEFECT
             sop_currency - all 153 rows through classify(): 13 fire, 13/13 bound; Step 8's later
               commit fires nothing
             the new rows and bullets - every path, every line verbatim, generated ones say
               edit-the-source
             Port trigger re-run from main - the table reproduces; maintained-projects.txt confirmed
             sibling worktrees - SCC-392 spent; teaching-edition confirmed, validator count
               corrected to 5 paths / 10 sites
             twins - cleared
             cross-section - one acceptance row still carries the retired premise; one fix claimed
               as made and not made
read:        the plan body and the third-pass record - smh-close-task-merge-tree.md - git-policy.md -
             worktree-per-story.md - _harness.py - wf_common.py - sync-agents.ps1 (Save-SyncManifest,
             $excluded, :1006-1020, :1055, :1066, :1115, :1202, :1212, :1261) - sop_currency.py -
             generate_doc_graph.py - test_command_surfaces.py - check_maps.py - the SOP - three
             undeclared memory files - validate_teaching_edition.py
             RAN: $TMPDIR/scc394/{pass,drive,purge_throw}.ps1; `git show 63a40b90 --
               .agents/.sync-manifest.json` (a two-line, timestamp-only diff)
verdict:     findings below

lens:        3 Pre-Mortem (fourth pass)
checks_run:  Step 9 0a/0b traced through the ceremony's Steps 3-6: where the receipts land
             the walkthrough-write window - Step 3's "committed ON THIS BRANCH, NOW" vs Step 4's
               post-merge ban
             item 0a's side effect on main - Save-SyncManifest's tracked timestamp, measured; an
               ff-pull over a dirty file reproduced in a scratch repo (refuses, exit 1)
             the ## Your Actions port row through banned_action_rows, five wordings - two REFUSED
             the manifest write path - WriteAllText in place, no temp+rename; nothing un-inerts it
             the second machine - nothing tells it it owes a sync
             the teaching-edition tree's REAL exposure - 44 dirty rows, not 3 committed files
             DEFUSED: CS-18 S without pwsh (pwsh on both machines; Q already runs this shape) -
               the eol=lf pins churning PC status (checkout-only) - cwd after the prune - the Mac
               retirement purge - post-merge/post-commit hooks
read:        the plan and all three prior records - smh-close-task-merge-tree.md (Steps 1, 3, 4, 5)
             - jira_feed.py - sync-agents.ps1 - .agents/.sync-manifest.json - smh-sync-agents.md -
             _harness.py check() - test_command_surfaces.py L/Q, U7 - .githooks/{post-merge,
             post-commit} - .github/workflows/ - the teaching-edition tree's status - a scratch
             ff-merge-over-dirty-file probe
verdict:     narratives below - six, all attached
```

### Findings

| anchor | literal text read | consequence | severity | now |
|---|---|---|---|---|
| plan Deletions + rows **A**/**E**, against `.agents/scripts/sync-agents.ps1:795` inside `Sync-ZooSurfaces` (`:768`) | plan: "**Deletions:** `Sync-AntigravityWorkflowMirror`, `Get-AgDescription`, …" · engine `:795`: `('description: ' + (Get-AgDescription $desc)),` · `:906` (codex): "FULL description, never Get-AgDescription: that helper's 135-char cut is the ANTIGRAVITY…" | **`Get-AgDescription` is not dead code — it is the Zoo launcher emitter's truncator too**, on a surface this ticket does not retire. Two live call sites: `:622` (Antigravity, retired here) and `:795` (Zoo, untouched). Delete it and the sync throws at the Zoo stage under `Stop`, including Step 8's own `-NoGlobals` run — the lane cannot reach its gates. Keep it and rows A/E are false as written. `.roo/commands/*.md` are cut to 135 today; whether Zoo needs that is out of scope and must not change. `test_zoo_team.py` C7 pins only that the *seat* loop avoids it — a different emitter. | **blocker** | **fixed** — delete the call site, keep the function retitled; rows A/E assert "exactly one call, inside `Sync-ZooSurfaces`"; `U7` survives as the Zoo truncation check |
| plan Engine steps 3 and 5, measured with a scratch implementation | step 3: "**Write the new manifest once** …" · step 5: "**Purge** … dropping its manifest entry … This loop gets the same `try/catch`" · measured: after a caught purge failure, the manifest already read `{"dirs":["smh-quick-dev"]}` and `smh-retired/` survived a second, clean run | **The write-once-before-purge ordering strips a claim before the purge deletes the dir, so any purge that does not complete orphans it permanently** — verbatim the failure the manifest redesign was justified by. The `try/catch` the third pass added converts an ordinary Windows file lock into a silent permanent orphan: a retired command keeps serving from the Global menu, unclaimed, invisible to `L`/`M` (which report claimed orphans), every gate green. And the mirror-side reorder alone reopens the other orphan (a dir we wrote, unclaimed, refused as not ours). | **blocker** | **fixed** — two atomic writes: claim before mirror, drop after purge; a failed purge keeps its claim; `S`(g)/(h) added |
| plan row **C** `:124`, against row **H**, Step 9 and Gates | row C: "`L`/`M` byte-compare + new `R` in the main checkout, **run from main after the ceremony sync** per Step 9 item 0" | **The acceptance row still carried the exact premise the third pass called a blocker.** Row H, Step 9 and Gates were rewritten; row C was not, and "Step 9 item 0" no longer existed. A closer reading the acceptance table as the contract is sent straight back to a sync nobody runs. | major `x2` | **fixed** — row C's proof cell now names `S`(g) as the lane-time proof and 0a/0b as the real-machine confirmation |
| plan Step 9 item 0a, against `sync-agents.ps1:263`, `:1066`, `:1212`, and `git show 63a40b90 -- .agents/.sync-manifest.json` | plan: "0a. **Run the full sync from the main checkout, sandbox off:** `pwsh .agents/scripts/sync-agents.ps1` (no `-NoGlobals` …)" · `:263`: `"generated": ' + (ConvertTo-ManifestString ((Get-Date).ToString('s')))` · that file's last diff: two lines, the timestamp alone | `Save-SyncManifest` sits inside `if (-not $GlobalsOnly)` and stamps wall-clock time on every run, so item 0a **guarantees** the closing session ends by dirtying a tracked file on `main` — the checkout the constitution says is never an agent's. It can neither commit it nor leave it honestly; the operator's next lobby `git pull` refuses on it (reproduced). | major `x2` | **fixed** — 0a is `-GlobalsOnly`: the globals block at `:1261` runs under `($IsLobby -or $GlobalsOnly)`, the manifest write is skipped, nothing tracked moves |
| plan row **H** and Step 9 0a/0b "pasted into the walkthrough", against `smh-close-task-merge-tree.md:352-354` and `:639` | ceremony Step 3: "Everything Step 4 will demand of `walkthrough.md` must be committed ON THIS BRANCH, NOW … anything it finds missing forces a **post-merge commit** — which is precisely what the gate refuses" | **The third pass fixed WHO runs 0a/0b and left WHERE the evidence goes.** By the time the closing session stands on `main` with the lane pruned, the walkthrough has landed and the branch is gone; pasting into it is a post-merge write to `main`, banned by the door's own rule. The three lines of `L`/`M`/`R` had no legal destination, and the cache half of row C would have been proven in chat only. | major `x2` | **fixed** — 0a/0b output goes to the Dev Record and the close-out report; `S`(g) is the walkthrough's lane-time proof |
| plan Port §check 6 "mint the two follow-on tickets", against `jira_feed.py:2137-2140` and the SCC-163 comment at `:2093-2101` | regex: `\b(?:mint\|file\|create\|raise\|log)\s+(?:a\|an\|its\s+own\|the\|one)?\s*…(?:ticket\|task\|subtask\|issue\|key)\b` → "asks the operator to CREATE ticket work" · measured: "Mint a follow-on ticket in `Projects/sudo-command-center`…" **REFUSED**; "Decide whether … get the workflows-to-skills port …" accepted | The third pass moved the follow-on from a dead detector into the one walkthrough section whose armed gate refuses exactly that shape. The plan's own plural spelling slips the regex by accident of the article group; the builder's natural per-repo spelling blocks the close-out at Step 3 and again at `finish`. | major `x2` | **fixed** — the row is a decision ("Decide whether…"), measured accepted, and named in Step 9 |
| plan body lines 1–822 (`grep -i teaching` → none), against the third-pass record's "the teaching-edition order stated" and `.claude/worktrees/teaching-edition` @ `0d76f72c` | body: nothing · that lane: `A .agents/workflows/smh-tour.md`, `A smh-training.md`, `M smh-new-project.md`; `validate_teaching_edition.py` 5 paths / 10 sites; **44 dirty rows** under `.agents/workflows/` in its working tree | A fix asserted as applied was not — the order existed only in the audit record, the half the builder is told not to treat as subject. And the price was measured against that lane's committed diff, not its working tree: whoever resumes it pulls `main`, meets forty-odd conflicts in a directory they believe they own, and the obvious resolution — keep ours — resurrects `.agents/workflows/` on `main`. | major `x3` | **fixed** — the order and the 44-row warning are in Step 3; a `## Your Actions` row names it |
| plan Engine step 1 + step 3, against `sync-agents.ps1:296` `[IO.File]::WriteAllText` | step 1: inert on `$null` · step 3: one write · engine: in-place write, no temp-then-rename · step 2 prints a remedy, step 1 does not | The inert arm fixes the *state* and says nothing about how it is reached or left. `WriteAllText` truncates first; a kill mid-call produces the zero-byte file step 1 names, and from then on every sync warns and does nothing, forever, with a bare `Write-Warning` in a fifteen-line sync nobody reads. `S`(e) then certifies the freeze as correct. | major | **fixed** — both writes are temp-then-rename; the inert warning prints `delete … .sync-agents-mirror.json and re-sync` |
| plan Port check 5, against what the ticket actually introduces | "It runs on BOTH machines — the engine is `pwsh`, present on both …" | Answered about the engine's *portability*; the ticket introduces a per-machine *action* (`~/.gemini/config/skills/` is written by a sync on that machine) and nothing in the tree tells the second machine it owes one. Harmless today (a stale cache still serves working doors); after 2026-11-01 the second machine goes dark silently. | major | **fixed** — a `## Your Actions` row: "On the other machine: pull, run `-GlobalsOnly`, report the count" (measured accepted) |
| `_artifacts/_memory/e2e-gate-fiction-test-guardrails.md:34` · `toolkit-sync-covers-agents-not-docs.md:31` · `doc-graph-unc-hang-and-scope.md:10,17` · `git-branch-model-standard.md:90` · `docs/migrations/install_guides/vscode-ide-extension-migration.md:235` | "**the antigravity workflow mirror**" as a surface the sync guards · "Rebuild after editing rules/workflows" ×2 (byte-for-byte the sentence Step 5 removes) · "all rules, commands and workflows" · "Agent rules, workflows, skills, and MCP configuration" | Four more memory files and one more install guide, undeclared — the same class every pass has found "a few more" of. Eleven memory files now. | minor | **fixed** — Step 7 and five change-set rows |
| plan change-set row for `file_folder_structure+maintaining.md` "two stale pointers" against Step 6's three sites | `:13`, `:43`, `:382` all carry the retired path | The machine-parsed row undercounts what Step 6 names — the "says five, names four" shape one sentence over. | minor | **fixed** — "three stale sites (lines 13, 43, 382)" |
| Scope Ledger: the Port `## Your Actions` row | created by Port §check 6; rows A–G never mention the section; row H binds it only to the hands checks | The one artefact the Port remedy consisted of was required by no row — and, per the finding above, refused by the gate that reads the section. | minor | **fixed** — the row is a decision named in Step 9, which row H binds |

### Observations (uncounted)

- `--on-main` prints no tree line (`_harness.py:60` returns before it); `L`/`M`/`R` announce their own
  SKIP reason, so real numbers are themselves proof of the main checkout. Pre-existing harness
  behaviour, not this plan's.
- `S`(d) and (e) discriminate only if "the cache unchanged" includes the manifest's own bytes — a
  "refuse everything" arm would still rewrite it to `{"dirs":[]}`. Both cases now say so explicitly.
- `.agents/rules/tests-must-gate-for-real.md:24` and `completion-not-illusion.md:17` read "manual /
  Antigravity workflows" — the generic word, correctly out of the change set; named because a literal
  `grep` hits them and both are `sop_currency` surfaces.
- `[[antigravity-uses-workflows-not-commands]]` wiki-links survive by design — Step 7's "filenames stay
  stable" is doing real work.
- Row D says "every committed generated `SKILL.md`"; `CS-18 Q` compares the master surface, and
  `test_command_surfaces.py:1698-1713` already byte-compares master against the `.claude/skills` copy.
  Not a gap.
- `$excluded` is safe to delete — all four uses sit inside the retired mirror region.
- Three stale `__pycache__/*.pyc` carry the retired strings; gitignored, sources declared.
- `_my_resources/open_tasks/plan_optimize-sudo-dev-story-tests.md:200` names the memory by filename in
  a historical sentence; `CS-18 P` passes over it today. Left alone.

### Landing-order dependency

**SCC-394 first; `claude/teaching-edition` after, under its own key** — now in the body (Step 3) and
owed as a `## Your Actions` row. `SCC-392` is spent. Within the engine, the order is now: read → refuse
→ claim-write → mirror → purge → drop-write.

```
Audit verdict: NO-GO
```

**The grounds.** Rows **A** and **E** were unsatisfiable as written — the function they retire has a
live caller on a surface this ticket does not touch — and row **C**'s cache proof had, for the fourth
time, no path by which it could bind: its acceptance cell still named the ceremony sync, its evidence
had no legal home, and the mirror design it was proving orphaned retired directories on the first
failed purge.

**Every finding is closed in the body above**, and the change set is now 158 rows.

**What this pass says about the next one, for the operator to rule on.** Four passes, four NO-GOs.
The first two found files a sweep had not opened. The third found PowerShell semantics that read the
opposite way from the prose. This one found a live caller a grep would have shown in a second, a
purge ordering a 56-line scratch script exposed in a minute, and a walkthrough write the ceremony's own
text bans. Every finding this round was found by *running* something, not by reading — and every one
would have surfaced in the first hour of a red-first build, at `CS-18 S` or at the first `-NoGlobals`
sync. Prose has found what prose can find. The recommendation is that the plan is ready for the
operator's word and that the remaining truth lives in the RED tests; a fifth blind pass is his call, not
the auditor's, and the rule's own text — *"do not re-run it hoping for a different answer"* — is the
reason it is not scheduled here.


---

## Self-Audit — post-cut, on the retirement half (2026-09-04)

**Level: LEDGER+BLAST. Mode: PRE-WORK. One lens** — Repo Reality + Scope Ledger — because the surviving
half carries four full passes of history and what is new is the cut itself. Run blind on the body as
written after the operator's scope ruling.

```
lens:        1 Repo Reality + Scope Ledger (post-cut)
checks_run:  dangling references to the removed half - 16 tokens swept over the body; every hit is
               framed as follow-on, history, or a different legitimate subject; zero live references
             internal consistency - rows A-H vs Steps vs Engine vs Tests vs change set vs Gates vs
               Port vs Out of scope; row C / CS-18 C+R / the purge paragraph agree; row H reconciles
               with Steps 0, 8, 9; Port check 3 traces to row C; Port check 6's row is byte-identical
               to Step 9's; row E vs the Tests list - two real breaks
             anchors - 22 of 22 line anchors land on the literal text claimed; the 41 DELETE rows are
               set-identical to .agents/workflows/*.md on disk
             change set - 158 entries, incomplete [], every path on disk; no row serves only the
               removed half; the widened rule creates zero new launcher dirs and prunes zero
             both machines / lane fit - clean
             the retirement purge - sync-agents.ps1:1300-1306 read; the plan's four-part description
               of the copied shape is accurate (Test-Path, the bmad filter, -WhatIf, the RETIRED line)
             Scope Ledger - precondition met; ten created artefacts, every cell filled
read:        the plan body (1-614) - task.yaml - sync-agents.ps1 (fourteen regions) -
             test_command_surfaces.py (:14 :75 :151 :210-250 :589-712 :1419-1585 :2145 :2482
             :2669-3200) - six sibling tests - five scripts - .gitattributes - six command files -
             opus-auditor.md - project-law.md - workspace-standard.md:159 - the SOP:4442 -
             .agents/workflows/INDEX.md - maintained-projects.txt - the three Projects repos
verdict:     findings below
```

### Findings

| anchor | literal text read | consequence | severity | now |
|---|---|---|---|---|
| plan Tests re-aim "helpers" line, against `test_command_surfaces.py:1457`, `:1539-1540` | plan: "delete `wf_hand_owned`, `ag_eligible`, `ag_description`" while "`U7` survives" · test `:1539`: `want = [ag_description(d) for d in probes]` · `:1540`: "U7 the REAL PowerShell generator and this file's emulation agree" · `:1457`: `AG_LIVE_DESCS = [d for d in …]` inside the `U1–U6` region | **`U7` *is* the test of `ag_description`** — the emulation it compares the real generator against — and it reads `AG_LIVE_DESCS` from the setup the plan deletes. Delete the helper and keep `U7`, and the SCC-195 block raises `NameError` on first run; `run_all.py`, row H's floor, cannot go green and the lane never reaches its gates. Residue of the fourth pass's own "U7 survives" fix: written into row E and the U-block line, never into the helper delete list. | **blocker** | **fixed** — `ag_description`, `AG_DESC_MAX` and the `AG_LIVE_DESCS` setup survive for `U7`; the setup moves into `U7`'s block |
| plan "retire with their subject" line, against `test_command_surfaces.py:2747`, `:2868`, `:3117`, `:1568` | `:2747`: `gen = re.search(r"^\s*\$\w+\s*=\s*Sync-AntigravityWorkflowMirror\b", sync, re.M)` (`CS-18 I` asserts the call is **present**) · `:2868`: `CS-18 M2 every antigravity door in workflows/ has a cache twin` (calls the deleted `ag_eligible`) · `:3117`: `CS-18 O2 …and the sweep read a real number of doors` (reads the deleted directory) · `:1568`: `U6c …the whole menu payload stays under the budget` (consumes `U1–U6` totals) | The enumeration is presented as exhaustive and omits four live cases whose subject this plan deletes. `I` goes RED, not stale; `M2` raises on a deleted helper; `O2` and `U6c` read what is gone. A builder working the list as written leaves four broken cases behind row H. | medium | **fixed** — `I`, `M2`, `O2`, `U6c` added to the retire list and to row E |
| plan Step 7 "**Eleven files:**" against the thirteen names that follow and the thirteen `_artifacts/_memory/` change-set rows | the count and the list disagree | A builder who trusts the count leaves two memory files asserting the retired surface; row F fails late, at the sweep. | low | **fixed** — "Thirteen files" |
| plan `:107` and `:286` "13 `cicd-*`", against a measurement | the `$masterOnly` candidate set is 13; two are generated and are exactly the pair the guard excludes; the hand-authored set the guard protects is **11** — ten `cicd-*` plus `smh-close-task-merge-tree`, which the wording dropped | The engine rule is right and yields the right two; only the stated blast radius was wrong, and a builder sanity-checking "13 cicd-*" measures 10 and cannot tell a stale number from a wrong build. | low | **fixed** — both sentences say 11, and name the eleventh |

### Observations (uncounted)

- `opus-auditor.md:37`'s HALT sentence is at `:33`, *above* the target — the plan's positional gloss was
  inverted; corrected in Step 6. Anchor, text and repoint were right.
- `.agents/workflows/INDEX.md` carries an 87-char `description:` despite `sync-agents.ps1:574` claiming it
  has none; the budget actually released is 41 files / 5,138 chars, not 40 / 5,051. Direction and
  magnitude unaffected; the two figures the argument leans on (74 / 27,026 and 56) reproduce exactly.
- The `.gitattributes` comment block's mention of `CS-18 L` is not a dangling reference — the plan is
  describing text it is about to rewrite.

### Scope Ledger

Ten created artefacts — the widened eligibility, `$masterOnly`, the stub sentence, the retirement purge,
`CS-18 C`, `R`, `Q`, the `.gitattributes` pins, Step 0's two numbers, the four `## Your Actions` rows —
each against the row that requires it (B, B, D, C, C, C, D, A, H, H). No empty cell.

```
Audit verdict: GO
```

The cut removed every subject the four NO-GOs were about, and the one blocker this pass found was
residue of the cut itself — a surviving test whose Python twin was still on the delete list — closed by
a two-line correction. Nothing in the retirement half has been found wanting across five passes beyond
missed sites and list hygiene, all folded in. The plan-first gate is armed on this body; it waits for the
word.

