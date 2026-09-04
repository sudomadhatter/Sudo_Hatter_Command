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

- [ ] **Take Step 0's two baseline numbers in Antigravity — BEFORE your next `/smh-sync-agents`
      from the lobby, not merely before this lands.** (a) How many **Skills** does the
      Customizations panel list in the lobby? (b) Open any `Projects/<name>` workspace — do the 40
      old workflow entries appear under **Global** at all?
      ⛔ **(b) has a deadline this ticket creates.** The first lobby sync after this lands runs the
      retirement purge and empties `~/.gemini/antigravity/global_workflows`. Once it is empty the
      question is permanently unanswerable — a later "project workspaces show nothing" cannot be
      told from a condition that predates this ticket — and the follow-on decision below has no
      input at all. Two minutes now, or the measurement is gone.
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

**The four hands checks, after your first lobby sync.** Every other assertion in this ticket is
static file analysis; no test in this repo can reach Antigravity's menu, so these are the only
end-to-end evidence that the new door actually opens.

- [ ] In the lobby, type `/smh-sync-agents` in Antigravity → it should launch from the skill and
      say it is reading `.agents/commands/smh-sync-agents.md`. Then reload the window.
- [ ] Customizations → **Skills**: the 74 house + 56 BMAD workspace skills are listed. Spot-check
      the alphabetical tail (`workspace-structure`, `write-swift`).
- [ ] Customizations → **Workflows**: no house entries, and no deprecation banner.
- [ ] Open a project workspace: `/smh-quick-dev` is either absent, or STOPs with "that file does
      not exist in this workspace". Record what **Global** shows — with (b) above, that is the
      follow-on's whole input.

**What landed here, for context (nothing owed):** the workflow surface and every engine wire that
fed it; the retirement purge; the LF byte contract moved onto both `SKILL.md` surfaces; 20 law and
doc sites; 13 memory files; `docs/repo-map.md` and `docs/doc-graph.{md,json}` regenerated.

---

## Code Review (2026-09-04)

Verdict: CONCERNS @ e71cadef
Suite evidence measured on: e71cadef (re-stamped after the last code-touching change)

review_level: standard — the radius carries gate, hook, rule and contract surfaces and 160 files.
review_runtime: fan-out
lens_isolation: worktree — the four repo-reading lenses each got their own copy; the repo under
review IS the lobby, so `isolation: "worktree"` delivers the contract. The blind hunter got no
tree at all, by design.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:
- none · n/a — review_mode full and review_level standard, so every lens in the roster ran

### Step 0.7 — the blast radius, re-derived against current `main`

`origin/main` is still `eee79727`, this lane's base: **nothing landed while I built.** Overlap
with landed work is empty, `git merge-tree` returns a clean tree with no conflict messages, and
no absorb was needed. `risk_seam.py classify` returns `unclassified`, which is the permanent
correct answer here — the command centre carries no code graph.

Three sibling lanes exist. `SCC-392` is spent (empty diff against `main`). `claude/teaching-edition`
at `0d76f72c` is the landing-order dependency, unchanged since 2026-08-24, and the ordering is
already stated in the plan and owed as a `## Your Actions` row.

Nothing this diff references moved, was renamed, or was deleted on `main`.

### Disposition — the tail, in one line

**Twenty-six findings came back across five lenses. Fourteen were assessed real and fixed in this
lane; twelve were dismissed** under the assessor rule (not real, not behaviour-changing, or not in
this diff). Three assessments disagreed with the lens's own label and those are the calibration
signal worth carrying:

- The edge-case lens filed the unparseable-YAML frontmatter as `important` on this diff. **Verified
  it myself and downgraded it out of the lane**: both descriptions are byte-identical on
  `origin/main`, so it is pre-existing debt in lines this ticket does not touch. Recorded in
  [deferred-work.md](../deferred-work.md) with the remedy named.
- The blind lens filed the claude-only stub wording as `nitpick`. **Dismissed** — the plan's
  acceptance row D explicitly requires the stub to name all three platforms, and the operator
  approved that.
- The test-adequacy lens filed `$masterOnly`'s missing coverage as `suggestion`. **Promoted and
  fixed**: four mutants survived on the predicate this ticket rewrote, one of which is the exact
  hazard the engine's own comment names.

### What the review actually caught — the two that mattered

**Three of my own new guards could not fail.** `CS-18 C1` and `C1b` took a 900-character window
from the first `global_workflows` and asked whether `Remove-Item`, `bmad-` and `RETIRED` appeared
in it. They did — supplied by the `~/.codex/prompts` retirement twenty lines below, which has the
identical shape. Dropping the purge's `bmad-*` filter and replacing its `Test-Path` guard with
`if ($true)` each left the suite at 300/300, and both mutants wreck the operator's machine.
`CS-18 A`'s residue sweep matched double-quoted `Join-Path` only, while every surviving emitter
in this engine is single-quoted; a working workflow emitter written in the file's own house style
returned zero residue. All now scoped by name, quote-agnostic, and case-insensitive.

**Three edits landed on half a wrapped sentence.** The engine's `.DESCRIPTION`, its DOOR MODEL
comment, and `smh-sync-agents.md`'s own door paragraph each had the noun on the following line, so
the substitution left the other half still asserting the retired model — and `CS-18 J`, the guard
written for exactly that, could not see the last one because `workflow mirror` spanned a newline.
J now sweeps every tracked `.md` rather than four hand-listed files, which is what would have
caught the two further sites the acceptance lens found (`docs/repo-map.md`'s toolkit inventory and
the SOP's §19 blurb).

### Mutation sweep — 12 mutants, run through `mutation_sweep.py`

Every one of these SURVIVED before the fixes and is KILLED after. Restore verified against the
pinned pre-sweep sha and bytes; the full file ran unfiltered at the end of each sweep.

| # | Mutant | Killed by |
|---|---|---|
| M1 | purge deletes BMAD's own global install | `CS-18 S` |
| M2 | the `Test-Path` guard is gone | `CS-18 C1b` |
| M3 | `-WhatIf` polarity inverted — a DRY RUN performs the delete | `CS-18 S` |
| M4 | the `Remove-Item` arm is unreachable | `CS-18 S` |
| M5 | a workflow emitter restored in house style | `CS-18 A` |
| E5 | the hand-authored-SKILL-wins guard removed | `CS-18 Q7` |
| E7 | the GENERATED-marker test inverted | `CS-18 T` |
| E8 | `Sync-Dir` stops reading the exclusion | `CS-18 T` |
| E11 | the manifest set ignores the exclusion | `CS-18 T` |
| M3b | the antigravity eligibility arm reverted | `CS-18 Q6` |
| M10 | the length guard counts code points, not UTF-16 units | `U7` |
| T6b | Q's committed set built from a broken glob | `CS-18 Q4b` |

⛔ One mutant (`M2`) initially scored **NOT KILLED — SWEEP ERROR**: removing the `Test-Path` guard
made `CS-18 S`'s extraction raise, and a crash "kills" every mutant aimed anywhere in the file, so
the sweep correctly refuses to score it. `S` now degrades to a stated SKIP when its anchor is
absent, and `C1b` owns that red. That is the CS-19 lesson this file already records twice, met a
third time.

### Acceptance audit

Rows **A, B, C, D, E, G** are satisfied with the assertion that proves each — see the Evidence
matrix above; the acceptance lens re-ran every one independently in its own tree and reproduced
the builder's RED from `origin/main` before believing the GREEN.

**Row F was NOT satisfied at review time** — four live sites still carried the retired claim
(`smh-sync-agents.md`'s door paragraph and its frontmatter description, the SOP §19 blurb, and
`docs/repo-map.md`'s inventory). All four fixed in-thread, and `CS-18 J` widened so a hand list
cannot miss the next one. Row F is satisfied at this sha.

**Row H is NOT satisfied, and cannot be in this lane.** Two reasons, both stated rather than
papered over: the enforcement suite is 72/73 because `test_rule_frontmatter.py` fails on
`Projects/sudo-command-center`, identically on `origin/main` at `eee79727` with none of this
diff present; and Step 0's two baseline numbers are a hands measurement that is now an unchecked
`## Your Actions` row holding the ticket out of `Done`. **That is why this verdict is CONCERNS
rather than PASS.**

### Declared Change Set

`declared_change_set.py diff` → `present: true`, `incomplete: []`, `unimplemented: []`,
`undeclared: [".claude/rules/sop-currency.md"]` — one row, the generated tree copy of a declared
master edit, disclosed above and not added to the plan because editing an approved plan re-arms
the plan-first gate.

### Clean-code gate

Imported from Step 3 rather than re-run (SCC-146): `run_all.py`, `workflow_lint.py --toolkit-only`
(0 errors, 0 warnings, 8 info — all UTF-8 BOM notices on vendored `testarch-*` commands),
`sop_currency.py` (silent over all 160 changed paths), and the link+anchor sweep. `py_compile` is
clean on all twelve changed Python files; `pwsh` parses `sync-agents.ps1` with zero errors. The
comment contract holds: every comment this diff made wrong was rewritten in the same commit, which
is what the two wrapped-sentence findings were.
