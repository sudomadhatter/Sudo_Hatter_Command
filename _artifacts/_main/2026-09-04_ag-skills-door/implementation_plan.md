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

**⚠️ AUDIT FINDING (2026-09-04) — this paragraph was wrong, and the corrected version is the second
tradeoff you should see.** Antigravity injects every skill's `description:` into its context each turn.
SCC-195 hit a budget on the workflow menu and cut those descriptions to 135 characters; skill launchers
carry full descriptions. The original claim here was that the payload does not change. Re-measured on
this tree, that is true in the **lobby** and false in a **project workspace**:

| Where | Carries today | Carries after | Why |
|---|---|---|---|
| the lobby | 74 workspace skills (27,026 chars) + the 40-file workflow menu (5,051) | the same 74 workspace skills (27,026) | the 39 global launchers share names with the workspace ones, and the vendor's "workspace beats global" precedence resolves the conflict — **down** by 5,051 |
| a project workspace | the 40 global workflows (**5,051** chars, each capped at 135 by SCC-195) | the 39 global launchers (**16,832** chars, uncapped) | no workspace copies exist there to win the name conflict — **up 3.3×** |

So this ticket **triples** the injected description payload on exactly the surface SCC-195 was written
for, in the same change that retires SCC-195's budget machinery. Two things keep that from being a
reason to stop. The vendor calls skills an "unrestricted bundle" against workflows' stated 12,000-char
cap, and describes progressive disclosure as injecting names and descriptions only — so the cap that
forced the 135-char cut is documented as *not applying* to the surface we are moving to. And 16,832
characters is small against any plausible budget. **What is not acceptable is closing this ticket
without the number**, which is what the original paragraph would have done. Step 9 item 3 therefore
counts the entries in a project workspace rather than eyeballing the tail, and the count goes into the
walkthrough. If it comes back short, the follow-on has its figure in hand — and the lever is a cap on
the **global mirror only**, not a return of the workspace cut.

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
| workspace skill descriptions (`.agents/skills/*/SKILL.md`) | 74 skills · **27,026** chars | unchanged by this ticket |
| workflow-menu descriptions (`.agents/workflows/*.md`, capped at 135 by SCC-195) | 40 files · **5,051** chars | retired by this ticket |
| the 39 ag-eligible launcher descriptions (what the new global cache carries) | **16,832** chars | ⚠️ **new** cost in a project workspace — see the corrected budget table above |

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
| **A** | `.agents/workflows/` does not exist; `.gitattributes` no longer pins it **and does pin `.agents/skills/**/SKILL.md` and `.claude/skills/**/SKILL.md` LF** (audit — the byte-mirror contract moves with the surface); the comment-stripped engine contains no `Sync-AntigravityWorkflowMirror`, `Get-AgDescription`, `$excluded`, `Join-Path … "workflows"`, or a write to `global_workflows` other than the retirement purge | new `CS-18 A`/`N` (re-aimed) |
| **B** | every command claiming `antigravity` (not `-AP`) has a `.agents/skills/<name>/SKILL.md` that is a current generated launcher for its own brain OR hand-authored; a generated launcher sits in the master iff the command claims `codex` or `antigravity`, and in `.claude/skills` iff it claims `claude` | `CS-02` extended (`missing_ag`/`ag_here` retired) |
| **C** | the Antigravity machine cache is `~/.gemini/config/skills/`, a per-dir mirror of exactly the antigravity-eligible launcher dirs, claimed by a **manifest at the cache root** (never a marker inside the mirrored dir — see the audit); the mirror **refuses** to write into an existing unclaimed dir and the purge removes only claimed dirs whose source retired; `bmad-*` and unclaimed dirs are never written or removed; the retired `~/.gemini/antigravity/global_workflows/` purge exists as CODE and leaves nothing of ours there | `CS-18 C–H` re-aimed to the skills mirror; new `S` (refuse-to-clobber, runs anywhere against a temp cache root under `pwsh`, so it does **not** SKIP in the lane); `L`/`M` byte-compare + new `R` in the main checkout, **run from main after the ceremony sync** per Step 9 item 0 |
| **D** | the launcher stub names Claude, Codex **and** Antigravity, and every committed generated `SKILL.md` is byte-identical to a fresh `pwsh` emit of `Sync-LauncherSkills` | `CS-18 Q` re-aimed to the skill emitter (`Q1` ran, `Q4` covered every committed GEN dir, `Q2` balanced quotes, `Q3` no BOM) |
| **E** | dead code and dead tests gone on both sides: `Get-AgDescription`, `ag_description`, `AG_DESC_MAX`, the SCC-195 `U1–U9` block, `wf_hand_owned`, `ag_eligible`, `door_verdict`'s `launcher_ok`, the size-branch guards `N2`/`O`/`O3`; the 12,000 number leaves live law entirely (`CS-18 P` allow-list empty, `P3` retired) | `CS-18 N` + `P` |
| **F** | no live law, doc, door or memory says Antigravity reads `.agents/workflows/` or `global_workflows` — `RULE_SITES` widened, anti-fossil `J0` kept; SOP + changelog moved in the same commit; `repo-map.md` and `doc-graph.{md,json}` regenerated; `_artifacts/_main/INDEX.md` row present | `CS-18 J` widened · `sop_currency` gate · `check_maps --depth3-only --strict` |
| **G** | `smh-adviser-board` declares `antigravity`; its hand-owned workflow door is gone; the brain's inline-mode section is the only inline law | `test_adviser_board_filter_gates` F re-aimed (AG budget check retired; brain carries `## Running without subagents`) |
| **H** | floor green — `run_all.py`, `workflow_lint.py --toolkit-only`, `check_maps.py --depth3-only --strict`, `check_links.py`; the lane ran `sync-agents.ps1 -NoGlobals` and committed the regenerated tree copies; after landing the ceremony runs plain `/smh-sync-agents` from the **main** checkout; **Step 0's two baseline numbers are in the walkthrough before Step 1 starts**; the Step 9 hands checks are recorded in `## Your Actions` with what the operator saw, including the counted number of Global launchers in a project workspace | gate receipts + walkthrough |

## Steps — assert-first, in this order

**Step 0 · baseline (hands, REQUIRED, before any code).** In Antigravity, open the Customizations
panel and note two numbers: how many **Skills** it lists, and whether the 40 **Workflows** in
`~/.gemini/antigravity/global_workflows/` appear under Global at all. The second answers a question the
repo cannot: whether that cache was ever read.

> **⚠️ AUDIT FINDING (2026-09-04): this step was marked "optional" and cannot be.** It is the only
> check anywhere in the ticket that can tell a Step 9 failure apart from a condition that predates it.
> If the global launchers do not show up in a project workspace afterwards and no baseline was taken,
> there is no way to know whether this ticket broke the global path or whether the global path was
> never read — and the follow-up is spent debugging a regression that may not be one. Both numbers go
> into the walkthrough before Step 1 starts.

**Step 1 · write the RED assertions.** Every new or re-aimed check in `test_command_surfaces.py` and the
four sibling tests is written against the unmodified tree and seen red before Step 2 starts. Paste the
red run into the walkthrough. `CS-18 Q` needs `pwsh` (`/usr/bin/pwsh` on this box).

**Step 2 · the engine** (`sync-agents.ps1`) — design in the next section.

**Step 3 · delete the surface — ⛔ in the SAME commit as Steps 2, 5 and 6.** `git rm -r
.agents/workflows/` (41 files); `smh-adviser-board.md` frontmatter
`platforms: [claude, opencode, antigravity, codex]`.

> **⚠️ AUDIT FINDING, second pass (2026-09-04): this step edits a `sop_currency` surface and was bound
> to no SOP commit.** `.agents/commands/smh-adviser-board.md` is `.agents/commands/` `.md` —
> `sop_currency.py:72`'s first surface row. The first amendment bound Step 5's `.py` edits and left
> Step 3 out, so a builder committing Step 3 as written is rejected by the armed hook, and the
> shortest way past it is `[sop-ok]` on a `platforms:` change — a false attestation that stays in the
> log forever. The whole law-and-surface set lands as one commit.

And in `.gitattributes`, **replace** the pin rather than dropping it:

```gitattributes
.agents/skills/**/SKILL.md text eol=lf
.claude/skills/**/SKILL.md text eol=lf
```

> **⚠️ AUDIT FINDING (2026-09-04): dropping the LF pin without replacing it reproduces SCC-338 one
> surface over.** `.gitattributes:34` pins `.agents/workflows/*.md text eol=lf`, and the comment above
> it at `:22-23` says why: the sync writes the machine cache with LF while the PC runs
> `core.autocrlf=true`, so git hands the working copy CRLF and the byte-compare goes red after every
> pull. This ticket **moves that same byte-mirror contract onto `SKILL.md`** (row C, `L`/`M` re-aimed) —
> and `grep -c 'skills' .gitattributes` is `0`, so nothing was replacing it. On the PC, which is exactly
> where `L`/`M` bind, rows **C and D** would have failed on every pull. `.claude/skills` is pinned too
> because `CS-18 Q` byte-compares committed launchers against a fresh `pwsh` emit on both machines.
>
> **Second pass:** rewrite the 14-line comment block at `.gitattributes:20-33` in the same edit. It
> still says the sync "writes `~/.gemini/antigravity/global_workflows/*.md`" and still explains
> `CS-18 L` in terms of `.agents/workflows/*.md` — a live statement that Antigravity reads the retired
> surfaces, which is exactly what acceptance row **F** forbids, in a file no gate reads. Keep the
> SCC-338 measurement as the `ⓘ` reason the pin exists; repoint the surfaces to
> `~/.gemini/config/skills/` and `SKILL.md`.
>
> The `**` glob was verified against git itself rather than reasoned about: in a scratch repo,
> `git check-attr -a` returns `text: set · eol: lf` for `.agents/skills/foo/SKILL.md`,
> `.claude/skills/bar/SKILL.md` and a nested `bar/steps/SKILL.md`, and nothing for a sibling
> `other.md`. The narrow pin is deliberate — `.gitattributes:16-17` says the file is "Deliberately
> NARROW" — and only `SKILL.md` carries the byte-mirror contract.

**Step 4 · tests** — re-aim list in the section below.

**Step 5 · scripts.** `workflow_lint.py` `_RETIRED_SURFACES` drops `"workflows"` and its three comment
sites; `record_map_changes.py` `TOOLKIT_FAMILIES` drops `"workflows"`; `sop_currency.py` docstring line
28 and `.agents/scripts/INDEX.md` line 67 drop `workflows/` from the exempt list; `generate_doc_graph.py`
prose — **two** sites, not three (audit): line 575 `"… Rebuild after editing rules/workflows."` and line
21 `prose toolkit (rules / workflows / skills / commands)`, which is spelled differently and would have
been missed by a grep for the first. `check_maps.py` `vendor_markers` **keeps** `.agents/workflows` on
purpose — a project carrying it is stale vendoring, and that is exactly what the marker detects.

⛔ **These four `.py` edits fire the armed `sop_currency` gate** (`_SURFACES` includes `.agents/scripts/`
`*.py`/`*.ps1`; `.agents/scripts/tests/` and every `INDEX.md` are exempt). They must ride in the **same
commit** as Step 6's SOP edit, exactly like Step 2 — the original plan bound only Step 2 to that commit.

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

> **⚠️ AUDIT FINDING (2026-09-04): four live doors still cite the surface and none of them were in this
> list.** A repo-wide sweep (live tree, `_artifacts/` history excluded) found them; no gate in this
> plan's Gates section can see any of them, because `check_links.py` is diff-scoped, `sop_currency` is
> a co-occurrence gate on files already in the commit, and `CS-18 J` opens four named files. Acceptance
> row **F** would have closed green and false. All four are added to the Declared Change Set.

- `.agents/opencode-agents/opus-auditor.md:37` — **the sharpest one.** It reads
  "**Load the audit workflow:** Read `.agents/workflows/cicd-self-audit.md` and follow it exactly",
  directly above its own line "If any of these are missing, HALT and report which." Step 3 deletes that
  file, so the opencode audit subagent's step 1 becomes a read of nothing. Repoint to
  `.agents/commands/cicd-self-audit.md`. Its `.opencode/agent/opus-auditor.md` twin is a generated
  mirror (`sync-agents.ps1:1202`, additive robocopy) and follows from the sync in Step 8 — edit the
  source, never the mirror.
- `.agents/commands/smh-clean-code-audit.md:98` and `:161` — the machine floor that
  `/smh-code-review` Step 3.5 runs **on this very lane**. Line 98's **Door parity** row lists
  `.agents/workflows/<name>.md` as a fourth door that must agree with `platforms:`; line 161 names
  `.agents/workflows/` as a generated surface nobody may hand-edit. Drop the retired door from both;
  the `.opencode/commands/` twin regenerates in Step 8. `sop_currency` surface — same commit.
- `.agents/commands/smh-quick-dev.md:365` — "**Generated surfaces are never hand-edited.**
  `.agents/workflows/`, `.opencode/commands/`, and …". Same treatment, same commit.
- `docs/_scc_sops_prds/tdad_stack_install_guide.md:319` — "to `.agents/workflows/`; guide updates in
  this folder same day." Repoint to `.agents/commands/`.
- `_my_resources/open_tasks/plan_adviser-board-rework.md` — an open planning note naming the surface as
  live. One line, so a plan picked up later does not rebuild against a door that is gone.

> **⚠️ AUDIT FINDING, second pass (2026-09-04): two more live doors, and one of them is load-bearing
> for row F itself.** The first amendment's sweep matched the literal path `.agents/workflows`; a wider
> sweep on the brace-expansion form found these.

- `.agents/commands/smh-update-maps-indexes.md:48` and `:263` — both write
  `` `.agents/{rules,workflows,skills,commands}/INDEX.md` `` and call it a **MASTER** family map the
  operator should "fix drift" in directly. This is the command that regenerates `docs/repo-map.md` and
  `docs/doc-graph.{md,json}` — the two artefacts acceptance row **F** requires — so after Step 3 it
  sends the operator to reconcile a master map at a path that does not exist. Drop `workflows` from
  both brace lists; the `.opencode/commands/` twin regenerates in Step 8. `sop_currency` surface —
  same commit.
- `.agents/rules/project-law.md:20` — the tier-1 row reads "rules · commands · skills · **workflows** ·
  scripts · templates", the identical construction to `AGENTS.md:107`, which Step 6 already edits. Line
  23 ("No vendored commands, workflows, scripts…") describes what a project must *not* carry and stays
  correct as prose about the retired surface, so line 20 is the edit. `.agents/rules/` is a
  `sop_currency` surface — same commit.
- `docs/workspace-standard.md:159` — "the MASTER toolkit (rules, commands, skills, workflows, scripts,"
  sits in §"Supporting files every workspace carries", *outside* the §"Command sync & platform reach"
  this step already names. The file is in the change set; this is completeness inside a listed file.
- `docs/workspace-standard.md` §"Command sync & platform reach": the surfaces bullet, the
  `commands/` vs `workflows/` bullet (retire), the "Gemini reads two workflow surfaces" bullet
  (Antigravity reads two **skill** surfaces; the launcher still STOPs outside the lobby).
- `docs/_scc_sops_prds/workflows_testing_SOP.md`: the `/smh-sync-agents` row at **line 4442**, inside
  §19's invocation table — drop its 135-char paragraph. ⚠️ **Audit: the plan said "§3" and §3 is line
  255 (`## 3. The two laws above every command`), which contains no occurrence of `smh-sync-agents`,
  `135` or `description`.** A builder sent to §3 edits nothing and line 4442 survives, leaving row F
  false. Also: the `-GlobalsOnly` paragraph and the mermaid `CACHE` node,
  and the "Antigravity's size cap is retired" box rewritten as "Antigravity enters through the same
  skill door" with the SCC-135/332/370 history compressed to one `ⓘ` paragraph (sop-currency habit 4).
  One line in `workflows_testing_SOP_changelog.md`.
- `docs/_scc_sops_prds/INDEX.md` line 119 (the "anything dropped in `.agents/workflows/` becomes a `/`"
  note — now "in `.agents/skills/`"); `docs/_scc_sops_prds/file_folder_structure+maintaining.md` lines 13
  and 382 point at `.agents/workflows/smh-update-maps-indexes.md`, a launcher since SCC-135 — repoint to
  `.agents/commands/smh-update-maps-indexes.md`, **and line 43**, a third mention inside a mermaid node
  (`CMDS["commands/ + workflows/…"]`) that the audit found in the same file.
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

> **⚠️ AUDIT FINDING (2026-09-04): five live memory files name the surface, and this step declared
> three of them.** Acceptance row **F** names memory explicitly and no test can catch a miss — the
> `RULE_SITES` list holds no memory path — so the row was self-certifying. This is SCC-370's own
> recorded miss repeating; its plan noted "the **SEVENTH** memory file; Step 5 named six." The three
> additions:
>
> - `bmad-wrappers-are-opencode-only-bridges.md:18` — "those target CUSTOM (non-BMAD) skills that
>   Antigravity does NOT get natively, so they need the sync's antigravity workflow-mirror path
>   (`.agents/workflows/`)." The whole premise is retired: Antigravity now reads `.agents/skills/`
>   natively, which is what makes the `sudo-*` wrapper exception unnecessary.
> - `sandbox-denies-writes-under-dot-claude-hooks-skills.md:30` — names `.agents/workflows` in the list
>   of surfaces the sync maintains. One-word edit.
> - `grep-skips-gitignored-projects.md` — same, in passing.
>
> **Guard, carried forward from SCC-370:** run `git status --short _artifacts/_memory/` immediately
> before staging. The store is shared across every lane on the machine, so a sibling's in-flight memory
> edit is stageable by accident. SCC-388 is live right now and touches no memory file, so today's
> exposure is nil — the guard costs one line and does not depend on that staying true.

**Step 8 · sync and gates, inside the lane.** Run `pwsh .agents/scripts/sync-agents.ps1 -NoGlobals`
with the sandbox off (`.claude/skills` is write-denied under the OS sandbox in-session), commit the
regenerated `.agents/skills/*/SKILL.md`, `.claude/skills/*/SKILL.md`, `.agents/.sync-manifest.json`
**and the five generated mirrors the amendments added — `.opencode/agent/opus-auditor.md` plus
`.opencode/commands/{smh-clean-code-audit,smh-quick-dev,smh-update-maps-indexes}.md`** (⚠️ second-pass
audit: those rows entered the change set while this staging list stayed byte-identical, so a builder
following it literally leaves five declared EDITs dirty and the close-out preflight refuses the tree).
⛔ `-NoGlobals` is not optional here: `$IsLobby` compares a worktree equal to itself
(`sync-agents.ps1:114`), so a bare sync from this lane would write **this machine's** global caches.
Then the floor: `run_all.py` · `workflow_lint.py --toolkit-only` · `check_maps.py --depth3-only --strict`
· `check_links.py`. Receipts into `gates/`.

**Step 9 · hands, after landing** (goes into the walkthrough's `## Your Actions`; the ceremony's
plain `/smh-sync-agents` from the main checkout runs first, then a window reload):

0. **⚠️ AUDIT FINDING (2026-09-04) — not a hands step, and the reason this item exists.** Immediately
   after the ceremony's sync, from the **main checkout**, run
   `python3 .agents/scripts/tests/test_command_surfaces.py --case CS-18` and paste `L`, `M` and `R`
   into the walkthrough. Those three are the *only* proof of the cache half of row C, and they are
   written to SKIP outside the main checkout — the block reads `_is_main = wf.tree_tag(ROOT)[2]` and
   registers `True` when that is false. So every place the plan ran them, they reported success while
   asserting nothing, and the plan never scheduled the one run that binds them. Without this item row C
   closes green, proven by nobody, and the first evidence of a mis-written cache is item 3 failing with
   no test to say which of the three ways it failed.
1. In the lobby, type `/smh-sync-agents` in Antigravity → it launches from the skill and reads the
   command body (the launcher's "Execute now" line is what you should see it do first).
2. Customizations → Skills: the 74 house + 56 BMAD workspace skills are listed; spot-check the
   alphabetical tail (`workspace-structure`, `write-swift`) — a dropped tail is the SCC-195 shape.
3. Open a project workspace (any `Projects/<name>`): **count** the launchers listed under Global — the
   number goes in the walkthrough, because this is the surface whose injected payload triples (5,051 →
   16,832 chars) and a count is the only thing that distinguishes "fine" from "silently truncated".
   Expect **39**. Then confirm `/smh-quick-dev` STOPs with "that file does not exist in this workspace"
   rather than improvising.
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

> **⚠️ AUDIT FINDING (2026-09-04) — the marker design below replaces a per-dir marker file, which was
> a data-loss path.** The original design wrote `.sync-agents-mirror` *inside* each mirrored dir. But
> `Copy-Tree -Mirror` builds `$kept` from the **source** tree and then runs
> `if (-not $kept.Contains($rel)) { Remove-Item -LiteralPath $item.FullName -Recurse -Force }`
> (`sync-agents.ps1:179-202`), so the marker is deleted on every run and rewritten by the next
> statement. Two failures follow. The marker gated only the *purge*, never the *mirror*: an operator
> who hand-writes `~/.gemini/config/skills/<one-of-our-names>/` under the vendor's own documented path
> would have his directory emptied, overwritten and then claimed. And any interruption between the
> delete and the rewrite leaves a fully-mirrored, permanently unclaimable directory that the purge can
> never reclaim and that `L`/`M` never report, because they report *claimed* orphans.

- **claim manifest, at the cache ROOT, outside everything the mirror rebuilds:**
  `~/.gemini/config/skills/.sync-agents-mirror.json` — `{"generator":"sync-agents","dirs":[…]}`,
  one entry per dir we own. It is the single source of truth for what is ours.

**The pass, in this exact order — ⚠️ second-pass audit rewrote it, because "claim, then mirror" as
first written cancelled the refusal it was paired with:**

1. **Read the old manifest.** Unreadable, corrupt, or truncated → `Write-Warning` and **do nothing this
   run**: no mirror, no purge, no manifest write. Fail-safe has to mean *inert*, not *unclaimed*. The
   first draft left this unstated, and the house pattern at `sync-agents.ps1:234-238` ("unreadable …
   purging nothing this run") only fails safe against deletion — inverted onto a claim manifest, an
   unreadable file would read as "nothing is ours", the mirror would refuse all 39 dirs, and the global
   menu would silently freeze at whatever the last good run wrote while `L`/`M` iterated zero claimed
   dirs and passed. Cache dead, every gate green.
2. **Test for refusal, against the OLD manifest.** For each name in the source set: destination exists
   and is **not** in the old manifest → refuse it, print
   `SKIP unclaimed '<name>' (not written by sync-agents)`, drop it from this run's set. ⛔ The refusal
   test must read the **old** manifest and must run **before** any claim is written. The first draft
   said "write the name into the manifest *before* mirroring that dir" and then tested against that
   same manifest — so the name was always present by the time the test ran, the test always passed,
   and `Copy-Tree -Mirror` clobbered the operator's directory. The two rules cancelled.
   Use bare `Test-Path` for "destination exists", **not** `-PathType Container`: a *file* or symlink
   sitting at one of our names must be refused too, and `-PathType Container` falls through to
   `New-Item -ItemType Directory` on an occupied path, which throws.
3. **Write the new manifest once** — `(old claims ∩ still-sourced) ∪ (the names step 2 left)`. One
   write per run, not one per dir. An interruption after this point leaves claimed dirs that are
   partially written, which the next run simply completes; a single write also closes the
   read-modify-write race between two syncs in different worktrees.
4. **Mirror** each claimed dir: `Copy-Tree … -Mirror` into `~/.gemini/config/skills/<name>/`.
5. **Purge** every old claim not in the source set, dropping its manifest entry. Never `bmad-*`, never
   an unclaimed dir (the operator's own global skills).

⛔ **`-WhatIf` writes nothing at all** — not the manifest, not a dir, not a purge. It prints
`would mirror antigravity skill '<name>'` / `would purge …` / `would SKIP unclaimed …`. The shape this
copies (`Sync-CodexSkills`, `sync-agents.ps1:976-984`) guards only the *copy* with `if (-not $WhatIf)`,
so a literal implementation would have a **dry run write the claim manifest** — claiming all 39 names
on a machine where the cache does not exist yet (measured absent). If the operator then hand-wrote one
of those names under the vendor's documented path, the next real sync would find it *claimed*, skip the
refusal, and empty his directory: the data-loss path reached through the one mode that writes nothing.

⛔ **Wrap the per-dir loop body in `try/catch`, not just the initial `New-Item`.** On Windows
`Copy-Tree` is `robocopy /MIR` and **throws** on `rc >= 8` (`sync-agents.ps1:167`); the PowerShell
branch never throws. `Sync-CodexSkills` guards only the root create, so one locked destination would
abort the whole sync mid-loop. The claim-then-mirror ordering makes that state recoverable — but only
if the loop survives to finish the other dirs.

**`CS-18 S` proves the refusal**, and unlike `L`/`M`/`R` it does not need the main checkout: it points
the function at a temp cache root under `pwsh` and asserts four things, each written RED first against
a build that still clobbers — (a) an unclaimed dir holding a sentinel byte survives untouched and the
manifest did not grow; (b) a bare *file* at one of our names is refused, not thrown on; (c) a
`-WhatIf` run against an absent cache root leaves **no manifest on disk**; (d) an unreadable manifest
leaves the cache entirely unchanged rather than refusing everything.

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
  function, no `Get-AgDescription`, no cap number, comment-stripped, **and `.gitattributes` carries no
  `.agents/workflows` pin while it does carry LF pins matching `.agents/skills/**/SKILL.md` and
  `.claude/skills/**/SKILL.md`** — ⚠️ second-pass audit: the first amendment added that clause to
  acceptance row A and added no assertion for it. `grep -rn gitattributes .agents/scripts/` finds no
  test anywhere in the repo that reads the file, which is precisely why the SCC-338 pin it replaces
  could be dropped silently in the first place. Without this check a builder who mistypes the pin
  closes row A green and the failure surfaces as `L`/`M` going red on the *other* machine after the
  next pull), `C–H` (the skills-mirror call reads
  `$Master/skills` and targets `.gemini/config/skills`; opencode still `commands`), `I2` (launcher regen
  precedes the globals block), `J` (`RULE_SITES` = `docs/workspace-standard.md`,
  `.agents/commands/INDEX.md`, `.agents/skills/INDEX.md`, `.agents/commands/smh-sync-agents.md`; the
  inverted-claim regex widened to "Antigravity … reads/mirrors … workflows"), `L`/`M` (cache twin
  byte-compare per **manifest-claimed** launcher dir, main checkout only, claimed orphans reported),
  new `R` (retired cache holds none of our files, main checkout only, SKIP when absent), **new `S` —
  the refuse-to-clobber proof** (⚠️ audit: `L`/`M`/`R` all SKIP outside the main checkout, so the
  cache half of row C had no assertion that ever binds during the build. `S` runs anywhere: it points
  `Sync-AntigravitySkills` at a temp cache root under `pwsh` and asserts the **four** cases the Engine
  design names — an unclaimed dir's sentinel byte survives and the manifest does not grow; a bare
  **file** at one of our names is refused rather than thrown on; a `-WhatIf` run against an absent
  cache root leaves **no manifest on disk**; an unreadable manifest leaves the cache unchanged rather
  than refusing every dir. Each written RED first against a build that still clobbers),
  `P` (allow-list empty; `P0`
  teeth control kept; `P3` retired), `Q` (round-trip `Sync-LauncherSkills` + `New-LauncherSkillStub` +
  `Get-CommandPlatforms` + `$AllPlatforms` under `pwsh` into a temp master; compare only committed GEN
  dirs; `Q4` = every committed GEN dir was emitted). `K`, `N2`, `O`, `O0`, `O3` retire with their subject.
- module docstring line 14.

Sibling tests: `test_zoo_notify.py` (the `ag` door → `.agents/skills/smh-llm-approvals/SKILL.md`, same
pointer + "END TO END" assertion); `test_live_testing_browser_instrument.py` (`WORKFLOW` → the skill
launcher; `A1b` re-aimed); `test_adviser_board_filter_gates.py` (`AG` removed from the file list; block F
keeps opencode byte-identity + Claude skill description, drops the 135-char budget, adds "the brain
carries `## Running without subagents`"); `test_door_preflight_order.py` line **507** glob removed — ⚠️ **audit: the plan said 499, which is
`+ sorted(REPO.glob(".agents/commands/*.md"))`.** Following the wrong number guts the SCC-193
"sign-off wording, pinned both directions" block of its main surface while leaving the workflows glob
to resolve to an empty set: two checks silently weakened, both still green;
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

`run_all.py` (**73** test files on disk today — audit; `run_all.py:53` discovers them with
`HERE.glob("test_*.py")`) · `workflow_lint.py --toolkit-only` · `check_maps.py --depth3-only --strict`
· `check_links.py` · the armed `sop_currency` and Jira commit-msg gates · `CS-18 Q` and the new
`CS-18 S` under `pwsh`. Then `/smh-code-review`.

`CS-18 L`/`M`/`R` bind only in the main checkout after the ceremony's sync, so a lane run reports them
as SKIP with the stated reason — **and Step 9 item 0 is what makes them actually run**, because a
permanent SKIP is not evidence. `CS-18 S` was added precisely so the mirror's refuse-to-clobber
guarantee has a check that binds *during* the build.

⚠️ **Audit note on non-vacuity.** Almost every check this ticket writes is a source-contains assert,
and `tests-must-gate-for-real.md` says the only way to prove a structural test non-vacuous is a
mutation. `/smh-quick-dev` Step 3 requires the sweep regardless; it is named here so the mutant table
is drawn **from the engine's own code** (the eligibility set, the `$masterOnly` predicate, the
manifest claim/refuse branches, the purge filter) rather than from the cases, which SCC-144 measured
as the difference between 14 case-derived mutants all killed and 24 of 25 code-derived ones surviving.

## Out of scope, named

- BMAD's `.agent/skills/` install and its manifest `ides: [claude-code, antigravity]` — untouched.
- Rule frontmatter (`trigger:` / `globs:` — Antigravity's rule loader is not changing).
- The permission fence (`.agents/permissions/`, `antigravity_permissions_apply.py`) — a different
  Antigravity surface, SCC-378's.
- The two project copies of the sync engine — see the **Port** section below, which replaces the
  one-line dismissal that used to sit here and named the wrong repo.
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
   135-row change set is consumed from git output. Due at the port, where the target's own engine
   handles its own paths.
2. **Operator-facing text goes through `printf`, never `echo`** — n/a: this ticket adds no shell
   script. The engine is PowerShell and uses `Write-Host`, matching every existing cache routine.
3. **On a write, verify the FILE — not `$?`** — **due and answered here**, because the new mirror
   writes. `CS-18 L`/`M` byte-compare the written cache against the source dir, and `S` asserts the
   sentinel file survives; neither reads an exit code. The manifest is verified by reading it back,
   which is what makes the claim-then-mirror order safe.
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
   `.agents/workflows/` and both go dark on 2026-11-01. `check_maps.py` `vendor_markers` keeps
   `.agents/workflows` on purpose, so after this lands each project clone reports STALE-VENDOR — which
   is the detector that will surface the follow-on rather than leaving it to memory.

## Open questions

None blocking. Parent epic placement on the board is the operator's (guardrail 2); the ticket is minted
bare like its five sibling sync-agents tickets.

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
**nil**. `git worktree list` now shows no third lane in flight, so this lane lands next with nothing to
order against.

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

