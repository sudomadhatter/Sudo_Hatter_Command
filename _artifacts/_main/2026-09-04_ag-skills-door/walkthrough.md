---
IsArtifact: true
ArtifactMetadata:
  title: SCC-394 — Antigravity's door becomes the launcher skill
  type: walkthrough
  date: 2026-09-04
---

review-runtime: fan-out

# SCC-394 — walkthrough

**Lane:** `chore/SCC-394-ag-skills-door` · **Base:** `origin/main` @ `eee79727`
**Plan:** [implementation_plan.md](implementation_plan.md) · **Ticket:** [SCC-394](https://sudo-command.atlassian.net/browse/SCC-394)

## What shipped, in one paragraph

Antigravity deprecated workflows and retires them on **2026-11-01**. Every antigravity-eligible
command already had a launcher `SKILL.md` in `.agents/skills/`, and Antigravity invokes any skill
there as `/<name>` — so the platform was carrying **two** doors for the same command and one of them
goes dark in November. This deletes `.agents/workflows/` (41 files), tells the sync engine that
Antigravity reads the launcher skill Claude and Codex already share, purges the retired machine
cache once, and re-aims every test, law site, doc and memory that called the workflow mirror the
Antigravity door. **Nothing an operator types changes.** The scope was cut to this half on the
operator's ruling of 2026-09-04 — the machine-global cache (`~/.gemini/config/skills/`) is a
follow-on, gated on one measurement.

**The one tradeoff, stated rather than discovered.** `.agents/skills/` is Codex's native surface AND
Antigravity's, so `platforms:` can no longer give a command to one without the other. That split was
already fiction: every command declaring `[opencode, antigravity]` carries a hand-authored skill
Codex had been reading all along.

## Task Checklist

- [x] **Step 1 · RED** — 11 assertions written against the unmodified tree and seen fail.
- [x] **Step 2 · the engine** — `Sync-AntigravityWorkflowMirror` deleted; `Sync-LauncherSkills`
      widened to claude|codex|antigravity; the stub names Antigravity; `$cxOnly` → `$masterOnly`
      (generated launchers only); the retirement purge added to the globals block.
      - `Get-AgDescription` was on the delete list in an earlier draft and is **not** deleted — it is
        Zoo's launcher truncator (`Sync-ZooSurfaces`), and removing it would kill the sync at the Zoo
        stage, including this lane's own `-NoGlobals` run.
- [x] **Step 3 · the surface** — `git rm -r .agents/workflows` (41 files); `.gitattributes` LF pin
      moved onto both `SKILL.md` surfaces; `smh-adviser-board` now declares `antigravity`.
- [x] **Step 4 · tests** — `CS-18` rewritten; `CS-01/02/03/07/13/15/22` re-aimed; `U1–U6/U8/U9`
      retired and `U7` kept as Zoo's truncation check; five sibling test files repointed.
      - The suite's `sync-agents command doc names both retired doors` check hung on the single
        string `"RETIRED door"`, which survived on exactly one unwrapped line. Rewording that
        sentence dropped it to zero coverage while every retirement stayed documented — re-aimed to
        assert each retired door **by path**.
- [x] **Step 5 · scripts** — `workflow_lint.py`, `record_map_changes.py`, `sop_currency.py`,
      `generate_doc_graph.py`, `.agents/scripts/INDEX.md`. `check_maps.py` `vendor_markers` keeps
      `.agents/workflows` on purpose: a project carrying it is stale vendoring.
- [x] **Step 6 · law and docs** — 20 files, SOP + changelog in the same commit.
- [x] **Step 7 · memory** — 13 files in `_artifacts/_memory/`; the store was clean before staging.
- [x] **Step 8 · sync and gates** — `sync-agents.ps1 -NoGlobals`, maps regenerated, floor run.
- [ ] **Step 0 · the two baseline numbers** — OWED, see `## Your Actions`. Taken out of order and
      said so at the time: the RED assertions only edit test files and cannot perturb what
      Antigravity's Customizations panel shows, and nothing synced or landed before they were asked
      for.

## Evidence

**Acceptance rows → the assertion that proves each** (rows A–H are in the plan's acceptance table).

| Row | Proven by | State |
|---|---|---|
| **A** | `CS-18 A` / `A0` / `A2` / `A3` / `N` | green |
| **B** | `CS-02` (skill door = claude/codex/antigravity, placement both ways) | green |
| **C** | `CS-18 C` / `C1` / `C1b` (purge exists, `Test-Path`-guarded, only `.gemini` code) · `R` | green · `R` SKIPs in a worktree |
| **D** | `CS-18 Q` / `Q0` / `Q1` / `Q4` / `Q5` (round-trip the real emitter under `pwsh`) | green |
| **E** | `CS-18 N` · the retired-check ledger at the foot of the block | green |
| **F** | `CS-18 J` / `J0` / `J0b` · `sop_currency` gate · `check_maps --depth3-only --strict` | green |
| **G** | `test_adviser_board_filter_gates` block F | green |
| **H** | the floor below, through the receipt writer | see `gates/suite.json` |

### RED — the 11 assertions, against the unmodified tree

`python3 .agents/scripts/tests/test_command_surfaces.py` → **290/300**, the ten below failing:

```
FAIL  the sync engine states the door model and all THREE retirements
FAIL  CS-18 A   7 residue sites: workflows/ on disk · Sync-AntigravityWorkflowMirror ·
                $GlobalWfSrc · $excluded · the antigravity $caches row · Join-Path "workflows" ·
                .agents\workflows in Get-SurfaceState
FAIL  CS-18 A2  stale pin ['.agents/workflows/*.md text eol=lf']; missing
                ['.agents/skills/**/SKILL.md', '.claude/skills/**/SKILL.md']
FAIL  CS-18 A3  2 Get-AgDescription call sites, 1 of them outside Sync-ZooSurfaces
FAIL  CS-18 C1  no Test-Path-guarded removal under global_workflows that prints a RETIRED line
FAIL  CS-18 C1b (same subject — the guard)
FAIL  CS-18 C   1 .gemini site outside the purge: the antigravity $caches row
FAIL  CS-18 J   3 live rule docs still send Antigravity to workflows/
FAIL  CS-18 P   2 of 673 swept files still state the 12,000 cap as law
FAIL  CS-18 Q5  the generated stub says "Claude and Codex" — Antigravity reads this very file
```

`python3 .agents/scripts/tests/test_adviser_board_filter_gates.py` → **28/29**:

```
FAIL  F · the brain CLAIMS antigravity: platforms: ['claude', 'opencode', 'codex']
```

⛔ **One control failed on its first run and is recorded because it changes what the red means.**
`CS-18 J0` went red, which meant `J` was passing over four files that all still described the
workflow mirror — a detector matching nothing. The polarity is the hard part: every one of those
files must go on *naming* the retired surface ("workflows retire 2026-11-01"), so a noun-only
detector blocks the very edit this ticket makes. Rewritten as: a retired-surface noun near
"antigravity" is a live claim **unless** the same window marks it as history. `J0` green, `J` red
over three real files.

⭐ **Honest about what was green on arrival.** `CS-18 Q`'s byte-identity half and the five sibling
test repoints (`test_zoo_notify`, `test_live_testing_browser_instrument`, `test_door_preflight_order`,
`test_workflow_lint`, `test_doc_examples_parse`) were **characterization**, not red: they moved
assertions onto launcher skills that already existed. Only `Q5` — the stub naming Antigravity — was
a real red on that surface.

### GREEN — after the engine, the delete, the docs and the sync

```
python3 .agents/scripts/tests/test_command_surfaces.py        -- 300/300 passed --
python3 .agents/scripts/tests/test_adviser_board_filter_gates.py -- 29/29 passed --
python3 .agents/scripts/tests/test_settings_allowlist.py      -- 29/29 passed --
python3 .agents/scripts/tests/test_zoo_notify.py              -- 46/46 passed --
python3 .agents/scripts/tests/test_live_testing_browser_instrument.py -- 27/27 passed --
python3 .agents/scripts/tests/test_door_preflight_order.py    -- 62/62 passed --
python3 .agents/scripts/tests/test_workflow_lint.py           -- 59/59 passed --
python3 .agents/scripts/tests/test_doc_examples_parse.py      -- 22/22 passed --
```

`pwsh -NoProfile -File .agents/scripts/sync-agents.ps1 -NoGlobals`:

```
sync-agents: launcher skills -> 25 generated in .agents/skills/ (hand-authored skills untouched)
sync-agents: zoo surfaces -> 51 launchers in .roo/commands/; .roomodes (6 team seats)
sync-agents: .claude\commands   -> RETIRED (SCC-66; Claude's door is .claude\skills)
sync-agents: .claude\skills     -> 75 skill dirs (3 claude-only launcher(s))
sync-agents: .opencode\commands -> 60 cmds
```

⛔ `-NoGlobals` is not optional from a lane: `$IsLobby` compares a worktree equal to itself
(`sync-agents.ps1:114`), so a bare sync here would write **this machine's** global caches — and
would run the retirement purge — from an unlanded branch.

### The floor — and the one failure that is not this lane's

`gate_receipt.py run --task SCC-394 --gate suite … -- run_all.py` → `gates/suite.json`:

```
72/73 files passed  FAILED: test_rule_frontmatter.py
[FAIL] every project rule on disk has a Load row in that project's .agents/INDEX.md
[FAIL] no project carries a copy of a tier-1 lobby rule (project-law.md)
[FAIL] no project has zero rule rows in .agents/INDEX.md when rules exist on disk
        ['sudo-command-center (26 rules on disk, 0 in INDEX.md)']
```

**It is pre-existing and outside this repo.** Run from the MAIN checkout at this lane's base sha
`eee79727`, with none of this ticket's changes present, the same file fails with the same three
messages and the same 20/23. The subject is `Projects/sudo-command-center`, a separate git repo with
its own board, carrying 26 copies of tier-1 lobby rules that `project-law.md` forbids and listing
none of them in its `INDEX.md`. Nothing in this ticket's 158-row change set touches it, and a lobby
ticket editing files inside it produces a commit no ticket of theirs accounts for — the same
constraint the plan's Port section already records for that repo.

The receipt therefore records **FAIL**, which is the mechanism working rather than a claim about
this diff: it reports what the suite actually said. Every other file is green, including all eight
this lane edited. The remedy is one line on the port decision below — that repo needs a ticket of
its own before 2026-11-01 anyway, and the rule-copy drift belongs in the same one.

### The other three gates

```
python3 .agents/scripts/workflow_lint.py --toolkit-only   -- 0 error(s), 0 warning(s), 8 info --
python3 .agents/scripts/check_maps.py --depth3-only --strict   (silent, exit 0)
python3 .agents/scripts/check_links.py --base origin/main  8 unresolved path(s), 0 bad anchor(s)
```

The link check's 8 break down as **5 pre-existing** and **3 inside this lane's own plan document**:

- `.agents/INDEX.md:11 -> reference/INDEX.md` — `.agents/reference/` does not exist; SCC-74 retired
  that folder and left the row. It sat at line 12 of the same file on `main` and only surfaces now
  because the file entered this diff. **Left alone deliberately** — a fossil row in a file I happen
  to be editing is still orthogonal work. One line to delete, on the rolling ticket.
- `smh-update-maps-indexes.md:279` (and its opencode mirror) `-> _artifacts/active-context.md`, and
  `file_folder_structure+maintaining.md:11` / `:340` — all four present verbatim in the base
  versions of those files, all four pointing at paths that do not exist on `main` either.
- `implementation_plan.md:360 -> workflows/INDEX.md` is the `DELETE` row of the Declared Change Set.
  A delete ticket's change set names the paths it removes, so this link is dead *because the ticket
  worked*; `:154` and `:981` are prose mentions of a glob example and of a file that lives on the
  `claude/teaching-edition` branch. The plan is **not** edited to silence them — editing an approved
  plan re-arms the plan-first gate.

### Declared Change Set vs the real diff

158 declared. **One file in the diff is not in the plan:** `.claude/rules/sop-currency.md`, the
generated tree copy the sync writes for each of the six path-scoped rules. It is a mirror of the
declared `.agents/rules/sop-currency.md` edit, exactly like the `.opencode/` mirrors the plan does
declare — an omission in the change set, not scope drift. It is **not** added to the plan, because
editing an approved plan re-arms the plan-first gate; it is recorded here instead and left for the
review to rule on.

## Your Actions

Nothing here is a ceremony step — those are the close-out's and they run on your word. These are the
decisions and the one measurement only you can take.

- [ ] **Take Step 0's two baseline numbers in Antigravity, before this lands.** (a) How many
      **Skills** does the Customizations panel list in the lobby? (b) Open any `Projects/<name>`
      workspace — do the 40 old workflow entries appear under **Global** at all? **(b) is the whole
      gate for the follow-on:** if project workspaces never showed them, nothing was lost and the
      cache half replaces nothing. Without this number, a later "project workspaces show nothing"
      cannot be told from a condition that predates this ticket.
- [ ] **Decide whether the Antigravity global-cache follow-on is worth building**, from (b) above.
      If it is, it is the dumb shape every other cache in this engine already uses: `Copy-Tree
      -Mirror` the launcher dirs into `~/.gemini/config/skills/` — no manifest, no purge, a retired
      launcher simply STOPs. Four audit passes' worth of findings all sat in the version that was
      *not* dumb.
- [ ] **Decide whether `Projects/sudo-command-center` and `Projects/Fresh_Workspace_BMAD` get the
      workflows-to-skills port before 2026-11-01.** Both carry `.agents/workflows/` (41 and 24
      files), both are separate repos with their own boards, and both go dark on that date.
      `Fresh_Workspace_BMAD` is a frozen template whose disposal is already yours. **Fold the
      rule-copy drift into the same decision:** `sudo-command-center` also carries 26 copies of
      tier-1 lobby rules with zero rows in its `INDEX.md`, which fails `test_rule_frontmatter.py`
      today on `main` and did before this lane opened.
- [ ] **On the other machine: pull and run `/smh-sync-agents` from the lobby**, so its retired
      Antigravity cache is purged too. Caches are per machine; git cannot carry them.
- [ ] **`claude/teaching-edition` must land AFTER this** and must not resolve its conflicts by
      keeping its side. That lane adds `smh-tour.md`, `smh-training.md` and `smh-new-project.md`
      into `.agents/workflows/`, pins five paths across ten sites in `validate_teaching_edition.py`,
      and its working tree carries 44 dirty rows under that directory. After this lands it repoints
      those three doors to `.agents/skills/` and re-aims its validator, under its own key.

**What landed here, for context (nothing owed):** the workflow surface and every engine wire that
fed it; the retirement purge; the LF byte contract moved onto both `SKILL.md` surfaces; 20 law and
doc sites; 13 memory files; `docs/repo-map.md` and `docs/doc-graph.{md,json}` regenerated.
