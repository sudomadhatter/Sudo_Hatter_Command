# Walkthrough — SCC-350 · The Wonderland team: five Zoo Code seats over the built-in slugs

**Lane:** `chore/SCC-350-wonderland-team` (consolidated, no subtasks) · **Ticket:** [SCC-350](https://sudo-command.atlassian.net/browse/SCC-350) (parent SCC-33) · **Close door:** `/smh-close-task-merge-tree`

## What shipped

The Zoo Code mode picker is now the operator's org chart. Five seats replace four of Zoo's
hard-coded built-in modes (a same-slug custom mode replaces a built-in wholesale — verified
against the v3.80.1 compiled bundle before the plan was written) plus one new `designer` slug;
the `ask` slug is deliberately unclaimed, so stock Zoo Ask stays in the picker for plain Q&A:

🫖🐰 March Hare — TEAM LEAD (`orchestrator`) · ⏰🐇 White Rabbit — PM (`architect`) · 🔨🪚
Carpenter — ENGINEER (`code`) · 🦋 Caterpillar — DESIGNER (`designer`) · ♥️👑 Queen of Hearts —
TESTER & QA (`debug`, the quality seat at both ends: she writes the failing tests before a build,
judges the finished work through the review and audit doors, and fixes what the review finds in
the same lane — full pen, chartered group ceiling).

**Amendment 3 — the quality merge (operator, same day, post-first-PASS):** *"the tester and the QA
need to really be one"*, still named the Queen of Hearts — *"the self audit and the code review
are the QA and the testing."* The build initially shipped SIX seats (a separate 😼 Cheshire Cat —
TESTER on `debug`, the Queen edit-scoped on `ask`); the merge retired the Cat into the Queen,
moved her to `debug` (suppressing Zoo's law-free stock Debug), removed the scoped-pen machinery
end to end, and replaced it with a group CEILING (`mcp` is the TEAM LEAD's alone; nothing
unchartered) plus a live charter-name pin. Everything below the Evidence line that speaks of six
seats or the scoped pen is the accurate history of the first pass, superseded by this amendment
and re-reviewed in the second `## Code Review` section.

- **Part A — seat masters** (`.agents/commands/smh-team-*.md`, 6 files): identity, doors, refusals,
  routing law per seat. Frontmatter carries `mode-name` / `mode-slug` / `mode-groups` — the ONE
  source the generator and the tests both read. `platforms: [zoo]` → one `.roo/commands/` launcher
  each, nothing on other platforms. March Hare carries the delegation protocol (`new_task` per
  seat, chosen by `whenToUse`; `switch_mode` for handoffs; ceiling = merge-ready). At review, the
  12 flow doors the seats route to (`smh-plan-task`, `smh-quick-dev`, `smh-code-review`,
  `smh-self-audit`, `smh-close-task-merge-tree`, `cicd-write-story-tests`, `cicd-bdd-tests`,
  `cicd-dev-story-tests`, `cicd-quick-dev`, `cicd-code-review`, `cicd-create-epic-sprint`,
  `cicd-close-story-merge-tree`) gained `zoo` eligibility — a seat must be able to type its own
  doors.
- **Part B — generator** (`sync-agents.ps1` Sync-ZooSurfaces §3): `$personas` → `$seats`; names,
  groups and whenToUse read from master frontmatter (UTF-8 markdown) so the ps1 stays pure ASCII
  (Windows PowerShell 5.1 mangles no-BOM UTF-8 source); quoted YAML names; per-seat groups; the
  marker-guarded prune retired the five old persona dirs automatically.
- **Part C — team rule** (`.agents/rules/zoo-team.md`): roster map, hand-off order, cicd-vs-smh
  routing law, manuals, Sudo_Hatter profile by NAME only, the two per-machine auto-approve tiles.
  Rides the `.roo/rules/` copy list (fourth copy, Zoo-wide, frontmatter-stripped) — deliberately
  NOT a `CLAUDE.md`/`GEMINI.md` `@` import (Zoo-team law, not house floor).
- **Part D — worktree visibility travels**: tracked [.vscode/settings.json](../../../.vscode/settings.json)
  now sets `git.detectWorktrees: true` (was user-settings-only on the Mac; the PC and any VS Code
  profile inherit it via git).
- **Part E — tests, RED first**: new [test_zoo_team.py](../../../.agents/scripts/tests/test_zoo_team.py)
  — grown to **25 checks** after the review: 12 fixture cases proving every validator branch fires
  (bare-edit QA, lost scoped pen, lowercase role, bare name, ASCII prefix, ALL-CAPS name, dup
  slug, wrong slug set, missing base groups, YAML-breaking char) + 7 live-tree checks (team law,
  master currency incl. full whenToUse, QA prose refusal, seat-rule content currency, team-rule
  currency, detectWorktrees) + the C-block: 6 generator-SOURCE currency checks (the ps1's own
  stricter frontmatter regexes mirrored with a rejecting mutant, the $seats table ↔ .roomodes ↔
  masters three-way join, the $floor pin). Seen RED before the build: `8/14 passed`, all six live
  checks failing for the right reasons (transcript below). `test_settings_allowlist.py`
  E2/E4/E10 rewritten from personas to seats (declared amendment).
- **Part F — sync run**: regenerated `.roomodes` (6 seats), 6 seat rule dirs, `.roo/rules/zoo-team.md`,
  the zoo launchers, manifest. Final run: `51 launchers … .roomodes (6 team seats)` — the count in
  that summary is now MEASURED from emitted seats, never asserted.

## Evidence

- RED first (pre-build): `test_zoo_team.py` → `-- 8/14 passed --` with B2–B7 failing
  (`slug set ['analyst','architect','dev','pm','tech-writer','ux-designer'] != law […]`, missing
  seat dirs, no team rule, `detectWorktrees value=None`).
- GREEN at build tip `c13e397`: `test_zoo_team.py` `-- 14/14 passed --`; suite `64/64`.
- GREEN at FINAL tip `9590e5e` (post-review-fixes): `test_zoo_team.py` `-- 25/25 passed --`; full
  armed suite **bare** `64/64 files passed`, exit 0, receipt `gates/suite.json` PASS @ `9590e5e0`
  on a clean tree; `workflow_lint --toolkit-only` 0/0; `check_links --base origin/main` clean.
- Final sync output: `zoo surfaces -> 51 launchers in .roo/commands/; .roomodes (6 team seats);
  floor + team rules in .roo/rules/`.

## Recorded decisions (deviations from the approved plan, each forced by an armed gate)

1. **Seat masters are `smh-team-*`, not `team-*`.** `workflow_lint.py` (lines 288–317) enforces a
   CLOSED naming law — `cicd-`/`smh-`/`sentry-` or a listed vendor bridge; widening the vendor list
   is explicitly forbidden in its own comment. The seats are house commands, so they took the
   `smh-` family. Change-set paths updated in the plan (rename only, zero content change).
2. **`run_all.py` was declared EDIT and needed none** — it auto-discovers `test_*.py` (its
   docstring line 11). Declared-set bullet amended before approval #2.
3. **Three undeclared files edited, each demanded by an armed gate at build time:**
   `test_twin_parity.py` (A1 requires every `smh-*` command pinned or recorded `NOT_PAIRED` — six
   seat records added with reasons), `.agents/rules/INDEX.md` (`test_rule_frontmatter` requires a
   Load row for `zoo-team.md`), `_artifacts/_main/INDEX.md` (`check_maps` F2 requires the session
   row). Inventory/ledger churn, no design freedom; the suite named each one.
4. **Mode names live in master frontmatter, not the ps1 table** — the ps1 is deliberately pure
   ASCII (zero non-ASCII bytes before this lane; PS 5.1 reads no-BOM UTF-8 as ANSI and would mangle
   every emoji on the PC). The generator reads the masters with explicit `-Encoding UTF8`.
5. **The maps hook refused the first commit** until the SOP named the six `/smh-team-*` doors —
   the operator page now lists them beside the team paragraph.
6. **Review-driven design upgrades (all in-lane, recorded in `## Code Review`):** the QA pen
   became a fileRegex-SCOPED edit group rather than a bare strip (her own doors must write the
   review record — a full strip either broke the seat or pushed writes through the shell); the
   12 flow doors the seats name became zoo-eligible; `whenToUse` ships the full description
   (the 135-char Antigravity menu cut does not apply to Zoo and was amputating the delegation
   signal).

## Task Checklist

- [x] 1 Master roster: five seat masters with identity/doors/refusals (A, amendment 3) — test B3/B4
- [x] 2 Generator emits the roster over four built-in slugs + designer; ask stays stock (B) — test B2/E2
- [x] 3 Team rule synced to .roo/rules/ (C) — test B6
- [x] 4 Full-pen seats under a chartered group ceiling; charter-name pin; March Hare delegation protocol (A/B, amendment 3) — tests B2/B2b + ceiling fixtures
- [x] 5 Seat skill bundles (Caterpillar: emil-design-eng + apple-design; Queen of Hearts: TEA/testarch + review doors) — masters name them
- [x] 6 Tracked git.detectWorktrees (D) — test B7
- [x] 7 RED-first tests + SOP same commit (E) — transcripts above; sop gate satisfied at `c13e397`
- [x] 8 Sudo_Hatter profile referenced by name only — zoo-team.md; no key material anywhere in the diff
- [x] The merge itself — lands via this branch's PR

## Your Actions

- [ ] **See your team:** reload VS Code (or restart Zoo Code) in this workspace after the merge —
  the mode picker shows your five seats plus Zoo's stock Ask (kept on purpose for plain Q&A).
- [ ] **Arm the March Hare (per machine):** tick **Mode switching** and **Subtasks** in Zoo's
  Auto-Approve panel so `new_task` delegation runs unattended.
- [ ] **Pin the Sudo_Hatter profile (per machine):** in Zoo's settings, set the Sudo_Hatter
  configuration profile as the active/default profile for the modes (extension state — git cannot
  carry it).
- [ ] **PC pickup:** pull `main` after the merge; `.roomodes`, the rules and `git.detectWorktrees`
  all arrive via git — only the two per-machine toggles above need hands.

review-runtime: fan-out

## Code Review (2026-08-29)

Verdict: PASS @ 9590e5e
Suite evidence measured at the same sha: `9590e5e` (receipt `gates/suite.json`, PASS, clean tree).

lens_isolation: worktree — four detached copies at c13e397 under the session scratchpad (the lobby IS the repo under review, SCC-313's good case); the Blind Hunter got no tree at all. All five lenses ran as read-only Explore agents (no Write/Edit tools — the SCC-301 write hazard is closed mechanically), and the builder tree showed zero lens-authored changes after the wave.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok — 20-file cap honored, one earned top-up (.roomodes, named with its symbol), withheld files disclosed first line
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

Verify wave: Evidence Verifier + Compound Synthesis ran concurrently (grouped claims file in place of the evidence_extract dossier — the roles had full repo access in their own frozen trees; recorded here rather than silently). Verifier returned 20 grouped verdicts: 16 true, 4 partial, 0 refuted outright; Compound Synthesis emitted 6 compound findings, all with named parents.

Scope: the SCC-350 diff `origin/main...HEAD` (42 files at review start, 84 at tip after fixes), review_level standard (rule + gate + command surfaces in the radius).
Method: 5-lens fan-out → verify wave → assessor triage per code-standards §6.5 → all surviving patches applied in this lane before this verdict.

findings:        0 decision · 25 patch · 0 defer   (1 noise-dismissed · 4 relevance kills)
dispositions:    per-lens: blind-hunter=7/0/0 · edge-case-hunter=6/1/0 · literal-correctness=6/0/0 · acceptance-auditor=8/1/0 · test-adequacy-auditor=9/1/1 · compound=6/0/0 (a multi-lens finding counts once per contributing lens)
drift:           undeclared=41 · unimplemented=0 · incomplete=0 — all 41 accounted: 3 build-forced by armed gates (rules/INDEX row, twin-parity records, artifacts INDEX row — walkthrough §Recorded decisions 3), 12 door masters + 24 generated mirrors from the review's own door-eligibility patch (finding G6/C2 below), 2 machine-generated doc-graph files staged by the pre-commit hook

### Findings table (unique claims; 41 raw instances → 30 unique)

| # | anchor | severity (verified) | failure scenario | disposition |
|---|---|---|---|---|
| G1 | sync-agents.ps1 whenToUse emission | important 0.97 | Get-AgDescription's 135-char ANTIGRAVITY menu cut amputated every seat's distinguishing tail — the exact string March Hare delegates on | applied @ 9590e5e — full description emitted; B3 row pins whenToUse == master description |
| G2 | smh-team-queen-of-hearts mode-groups | important 0.92 | QA's own doors REQUIRE walkthrough/plan appends her `[read, command]` mode could not make — either the seat breaks or she writes through auto-approved shell prefixes, defeating the advertised strip | applied @ 9590e5e — fileRegex-scoped edit group `^_artifacts/.*\.md$` (Zoo tuple form, verified in the v3.80.1 schema); bare `edit` still banned by law + fixture; shell-path refusal written into the master |
| G6/C2 | six masters' doors × .roo/commands | important 0.93 | 12 flow doors the seats route to were not zoo-eligible — both QA doors and both PM planning doors untypeable in the seats' own picker | applied @ 9590e5e — the 12 doors gain `zoo`; launchers generated; E8/E9 door parity green |
| G3 | rules-architect vs /architect launcher | important 0.85 | `/architect` typed inside the White Rabbit seat = two unconditional identity contracts in one context | applied @ 9590e5e — zoo-team.md tiebreak paragraph (invocation wins for its task; seat refusals bind underneath); launcher deliberately kept (operator's BMAD-coexistence ruling) |
| G5 | test_zoo_team fixtures | important 0.98 | two validator branches unreachable — deletable with 14/14 green | applied — emoji-branch, working-seat-strip, dup-slug, YAML-char and lost-pen fixtures; weak assertions tightened to named messages |
| G11 | B5/E4 existence-only checks | important 0.93 | a stale seat rule naming a retired master passed the suite (the exact defect this diff repaired by hand at rules-architect) | applied — B5 now checks GENERATED marker + master join + mode-name |
| G15 | ps1 vs test frontmatter parsers | important 0.95 | unquoted mode-name keeps the suite green while the next sync silently skips the seat | applied — C0–C2 mirror the ps1's stricter regexes with a rejecting mutant |
| G7 | generator degrade paths | suggestion 0.9 | skipped seat still wrote .roomodes; WhatIf and the run summary both asserted "6" unconditionally | applied — emitted counter, loud short-emit warning, measured counts in both messages; C3 ties mode count to the table |
| G16 | $floor source | suggestion 0.9 | dropping zoo-team.md from the list stays green until the next sync/edit | applied — C5 pins the four-name list in source |
| G27 | utf-8 vs utf-8-sig reads | suggestion 0.93 | a PS 5.1 BOM makes frontmatter vanish with four misleading messages | applied — utf-8-sig everywhere in the suite's new readers |
| G29 | set-based slug compare | suggestion 0.95 | duplicate slug invisible to the file claiming the set is closed | applied — dup detection + fixture |
| G23 | B3 substring / B4 grep | suggestion 0.92 | `zookeeper` satisfies "zoo"; prose grep order-blind | applied — B3 equality `== ['zoo']`; B4 detail corrected (grep stays as the prose belt over the mechanical B2 law) |
| G4 | plan acceptance rows 1/3 | nitpick 0.96 | rows still demanded the pre-amendment shapes | applied — rows updated, marked as review-time corrections |
| G12/G13 | masters vs plan promises | suggestion 0.95 | switch_mode and the routing law missing from named masters | applied — March Hare switch_mode clause; routing law in Caterpillar + Cheshire Cat |
| G14 | plan rename traceability | suggestion 0.95 | team-*→smh-team-* rename rode the implementation commit unnoted | applied — amendment note in the plan body |
| G20 | ps1 ASCII comment | nitpick 0.97 | stated invariant false as written (260 comment bytes) | applied — restated as the true invariant (no non-ASCII in EMITTED literals) |
| G24/G25 | plan link · lint warning | suggestion 0.98 | dead link; the one toolkit lint warning | applied (pre-verdict, found independently by the gates too) |
| G26 | B4 detail filename | nitpick 0.95 | failure message names a nonexistent file, printed on PASS | applied |
| G30 | seat loop dequote | nitpick 0.9 | dropped the launcher loop's load-bearing dequote | applied (dequote+Trim); first-match guard dismissed — verifier confirmed unreachable on 7-line frontmatter with a 12-line window |
| C4 | .roomodes YAML integrity | medium 0.65 | a quote/backslash in a mode-name breaks the consumer while regex parsing stays green | applied — YAML-breaking-character law + fixture (stdlib bars a real yaml parse; the two breaking characters are pinned) |
| G17 | name-law narrowings | suggestion | hyphen/ampersand/trailing-space shapes unpinned | dismissed — relevance leg 1: no seat today carries those shapes; coverage-for-symmetry class |
| G22 | NOT_PAIRED existence sweep | nitpick | a stale record could pre-excuse a future name | dismissed — the ledger mechanism predates this lane; its own-suite contract, raised here once with the remedy named (an A0c row) |
| G28 | JSONC inline comments | suggestion 0.8 | trailing `//` breaks B7's parse with a misleading value=None | partially applied (parse error now named in the detail); inline-strip dismissed — fail-safe direction correct |
| G9 | RED evidence channel | suggestion 0.95 | RED-first proof lives in the walkthrough, unverifiable from git alone | dismissed with the reason recorded — the plan routed the proof to the walkthrough (committed with this lane); future lanes: commit the RED state first |
| G6-blind | /cicd-bdd-tests "resolves nowhere" | noise | contested with the literal lens | resolved by the verifier: both right about different surfaces; the actionable half is G6/C2 above (counted once there); blind's phrasing dismissed as the noise half |

### Acceptance matrix

| Acceptance row | Proving assertion |
|---|---|
| 1 — six modes on the closed slug set, name law | test_zoo_team B2 (25/25) + E2; `--case "A ·" 12/12` proves the detectors fire |
| 2 — QA pen scoped, no bare edit | B2 law (bare-edit ban + scoped-pen requirement) + fixtures; generated `ask` entry carries the fileRegex tuple |
| 3 — six masters, platforms [zoo], doors + refusals | B3 (`== ['zoo']`) + B4 + workflow_lint 0/0 |
| 4 — team rule current, persona dirs pruned | B5 (content currency) + B6 (byte-equal) + C5 (source pin) |
| 5 — tracked detectWorktrees | B7 (value=True) |
| 6 — armed suite green at tip; SOP same commit | run_all 64/64 @ 9590e5e (receipt PASS, clean); sop-currency gate passed both commits; changelog row present |

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `64/64 files passed`, exit 0, receipt `gates/suite.json` PASS @ 9590e5e0, DIRTY=no |
| Toolkit lint | `0 error(s), 0 warning(s), 8 info` (infos = pre-existing testarch BOMs), exit 0 |
| Assertion evidence | `test_zoo_team --case "A ·"` 12/12 · `--case "C ·"` 6/6 (named blocks, exit 0) |
| SOP currency | SOP + changelog staged in both usage-surface commits (armed commit-msg gate passed; maps hook additionally forced the six door names into the page) |
| Link + anchor | `check_links.py --base origin/main` → clean, exit 0 |
| Door parity | suite E8/E9 green over the widened zoo set (51 launchers) |

### Clean-Code Gate

py_compile clean on the three touched test files; comment contract satisfied (each non-obvious guard carries its why — the scoped-pen, ASCII-invariant, dup-slug and utf-8-sig comments state their incidents); no banned pattern in the diff (no bare except swallowing without a named reason — B7's records its parse error in the detail); drift/bloat findings imported from the fan-out above rather than re-hunted (source `review`).

### Step 0.7 — re-derivation

1. Nothing this diff references moved on `main`: 0 files landed on origin/main since the merge-base; every path the diff names re-resolved at review time.
2. True overlap: empty; `merge-tree` clean (lane is a fast-forward candidate).
3. Sibling lanes: none live (`git worktree list` = main + this lane); no landing-order dependency.

## Code Review (2026-08-29 — second pass: the quality-merge amendment)

Verdict: PASS @ fe4679d2
Suite evidence measured at the same sha: `fe4679d2` (receipt `gates/suite.json` re-stamped PASS, clean tree; the @ 9590e5e receipt was VOIDED by the amendment's code changes per certification-at-shipping-sha and is superseded, not deleted — its output_tail describing the six-seat table is the historical record of the first pass).

lens_isolation: worktree — one detached copy at 6950d2c7 under the session scratchpad shared by the four tree-reading lenses (all read-only Explore agents, no Write/Edit tools); the Blind Hunter got the diff blob only, no tree. Builder tree showed zero lens-authored changes after the wave; the lens worktree was pruned after triage.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok — 18-file scope inside the 20-file cap, all read in full
- acceptance-auditor · ok
- test-adequacy-auditor · ok — ran the suite live in the frozen tree (23/23 pre-fix tally pasted in its report) and simulated 5 declared mutants: 3 killed by named case, 1 survivor, 1 split — both non-kills fixed below (B2b, C7)
lenses_counted:  5/5
lenses_na:       none

Verify wave: folded into the lenses this pass — the test-adequacy lens executed the suite and its mutants in the frozen tree, the edge lens re-ran the ps1 regexes and NAME_RE over the live strings, and the literal lens hexdumped all seven name occurrences; the assessor cross-checked every fixed finding against a green named case before this verdict. No claim below rests on a lens's say-so alone.

Scope: the amendment delta `c2b13d5..fe4679d2` reviewed against the FULL branch diff `origin/main...HEAD` (78 files at review start), review_level standard (rule + gate + generator surfaces in the radius). The first pass's PASS @ 9590e5e covers the unamended remainder and stands as history.
Method: 5-lens fan-out → assessor triage per code-standards §6.5 → all surviving patches applied in this lane before this verdict.

findings:        0 decision · 21 patch · 0 defer   (6 dismissed with recorded reasons; 42 raw instances → 27 unique claims)
dispositions:    per-lens: blind-hunter=11/0/0 · edge-case-hunter=7/3/0 · literal-correctness=7/0/0 · acceptance-auditor=4/0/0 · test-adequacy-auditor=7/3/0 (a multi-lens finding counts once per contributing lens)
drift:           undeclared=0 after the amendment ledger fix (Q4/Q21) — the plan's Declared Change Set now carries every amendment path incl. the hook-staged doc-graph pair; unimplemented=0 (3 phantom NEW bullets for born-and-retired paths removed); incomplete=0

### Findings table (unique claims)

| # | anchor | severity (verified) | failure scenario | disposition |
|---|---|---|---|---|
| Q1 | gates/suite.json + walkthrough verdict | HIGH (all 5 lenses) | the only receipt on file certified the VOIDED six-seat sha — close-out would clear on code that no longer exists | applied — suite 64/64 re-run bare at `fe4679d2`, receipt re-stamped (pass, clean), this verdict line is the new machine-read record |
| Q2 | test_zoo_team charter name | HIGH 0.95 (adequacy F1) | a consistent revert of the merged seat to "— QA" survived every check — the ticket's whole point un-nameable silently | applied — `QUEEN_NAME` law literal + B2b pins the live .roomodes name AND its presence in the team rule master |
| Q3 | mode_problems group ceiling | MED 0.9 (edge F2) | with the scoped pen gone, any master could self-grant `mcp`/`browser` and stay green — `mcp` is the TEAM LEAD's delegation privilege | applied — `ALLOWED_GROUPS`/`MCP_SLUGS` ceiling + two REJECT fixtures |
| Q4 | plan Declared Change Set | MED (blind #4, literal L3) | 3 phantom NEW bullets for paths the final diff never contains; the amendment's own edits undeclared — drift reconciliation reads a fiction ledger | applied — phantoms removed, 24 amendment bullets added |
| Q5 | plan Acceptance rows 1–3 | HIGH (blind #3) | rows demanded six modes / an edit-stripped ask seat — the correct tree scores FAIL on its own contract | applied — rows rewritten to the amended law, marked amendment 3 |
| Q6 | walkthrough body | MED (blind #2, literal L6) | the shipped record asserted the retired design as delivered (title, roster, checklist, Your Actions) | applied — body updated to five seats + an explicit amendment narrative; first-pass sections kept as marked history |
| Q7 | tickets/SCC-350.md outline | MED (acceptance, blind #9, literal L5) | acceptance boxes pinned the deleted design (Cheshire on debug, Queen on ask, edit-strip) — unsatisfiable forever | applied — boxes updated, amendment note in the Why |
| Q8 | _artifacts/_main/INDEX.md row | MED (acceptance, blind #7, literal L4) | the durable ledger row described six seats, the dead Cat, the dead edit-strip and a stale check count | applied — row rewritten |
| Q9 | SOP upkeep line (§sync-agents) | MED (acceptance, blind #6) | second SOP location still said "six Wonderland team seats" — the operator's manual stated both numbers | applied — five |
| Q10 | allowlist docstring | MED (blind #5, edge F6) | same-file six-vs-five contradiction 20 lines above `SEATS` | applied |
| Q11 | changelog rows 145/146 | MED (literal L1, blind #10, edge F7) | two contradictory same-day "what shipped" rows for one ticket, both unlanded — the first naming a seat that does not exist | applied — folded into one accurate row (both rows were this lane's, so no history rewritten) |
| Q12 | B5 retired-dir denylist | MED (edge F3, adequacy F6) | an enumerated list is blind to any stray GENERATED rules-* dir it did not predict | applied — complement-of-LAW_SLUGS scan, marker-guarded like the generator's own prune |
| Q13 | B3 `if desc and` skip | MED (adequacy F3) | a master with no description emits a BLANK whenToUse — the delegation signal — with B3 green | applied — missing description is now a named defect |
| Q14 | C-block mirror currency | MED (adequacy F7) | nothing proved the mirrored regexes still equal the ps1's literals — a tightened reader would skip seats the mirror passes | applied — C6 asserts both patterns verbatim in the ps1 source |
| Q15 | full-desc emission unpinned at source | MED (adequacy F5, mutant e) | a generator-only regression to the 135-char cut ships green until the next sync | applied — C7 pins `+ $desc)` and bans Get-AgDescription inside the seat loop window |
| Q16 | ps1 reader takes LAST match in 12 lines | LOW→fixed (edge F8) | body prose matching `^mode-name:` overrides the real frontmatter silently | applied — reader stops at the closing `---` |
| Q17 | YAML backslash branch unmutated | LOW (blind #11, adequacy F10) | `or "\\" in name` deletable with the file green — the emoji-branch defect class recurring | applied — backslash fixture added |
| Q18 | Queen verdict literal | MED (literal L2) | seat brain taught a binary verdict — `PASS\|FAIL` where the doors emit `PASS\|CONCERNS\|FAIL\|WAIVED @ <HEAD-sha>` | applied |
| Q19 | bare testarch door names | LOW (literal L7) | bare `testarch-*` reads as skill names (the skills are `bmad-testarch-*`) — ambiguous both directions | applied — slash-led like every other door in the master |
| Q20 | Queen red phase cicd-only | MED (edge F5) | picked in the command centre, her only red-phase doors presume a BMAD story lane | applied — smh-lane route stated (red phase rides /smh-quick-dev's tests-first step) |
| Q21 | amendment ledger under-stated radius | MED (literal L3) | the "What changes" list omitted the three artifacts that then shipped stale | applied — ledger completed (see Q4) |
| D1 | sync warns, exit 0 on skipped seat | dismissed (edge F4) | designed shape: the first pass deliberately chose the loud warning + measured counts, with the armed suite as the hard gate; a throwing generator would break -WhatIf and partial syncs |
| D2 | zoo launcher description 135-cut | dismissed (edge F9) | menu blurb under the shared launcher contract, predating this lane; delegation reads whenToUse, which ships full — raised once with the remedy named (lift the cut for zoo launchers in a sync-agents lane) |
| D3 | role-class widening unmutated | dismissed (edge F10) | `[A-Z][A-Z &]*` predates the amendment (TEAM LEAD-era); no live shape it wrongly admits — coverage-for-symmetry class |
| D4 | B-block builders lack negative fixtures | dismissed (adequacy F2) | pre-existing suite architecture (B3/B5 shipped this shape in the first pass and its review weighed it); C0 remains the model for new checks |
| D5 | B4 pins vocabulary not content | dismissed (adequacy F4) | speculative — no concrete input gutting the master while preserving the four door names + the refusal phrase |
| D6 | dead parse fallback + unused role group | dismissed (adequacy F9) | pre-existing lines untouched by the amendment; noted for a future test-hygiene lane |

### Acceptance matrix (plan rows as amended)

| Acceptance row | Proving assertion |
|---|---|
| 1 — five modes on the closed slug set (ask deliberately unclaimed), name law | B2 + E2 (`--case "A ·"` 13/13 proves the detectors fire) |
| 2 — full pens under the chartered ceiling; mcp = TEAM LEAD only; charter-name pin | B2 (ceiling law) + B2b + the UNCHARTERED and mcp fixtures |
| 3 — five masters, platforms [zoo], Queen carries BOTH halves | B3 (`== ['zoo']`) + B4 + workflow_lint 0/0 |
| 4 — team rule current, stray GENERATED persona dirs impossible | B5 (complement scan) + B6 + C5 |
| 5 — tracked detectWorktrees | B7 (value=True) |
| 6 — armed suite green at tip; SOP same commit | run_all 64/64 @ fe4679d2 (receipt PASS, clean); sop gate green on `83a3220b` (SOP+changelog staged) and `fe4679d2` |

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `64/64 files passed`, exit 0, receipt `gates/suite.json` PASS @ fe4679d2, DIRTY=no |
| Toolkit lint | `0 error(s), 0 warning(s), 8 info` (infos = pre-existing testarch BOMs), exit 0 |
| Assertion evidence | `test_zoo_team --case "A ·"` 13/13 · `--case "C ·"` 8/8 (named blocks, exit 0) |
| SOP currency | SOP + changelog staged with the usage-surface commits (`83a3220b`, `fe4679d2`); `[sop-ok]` only on the two artifact/deletion-staging commits |
| Link + anchor | `check_links.py --base origin/main` → clean, exit 0 (retired-path mentions de-ticked — they never existed on main) |
| Door parity | suite E8/E9 green over the 50-launcher zoo set (one launcher retired with its master) |

### Clean-Code Gate

py_compile clean on the touched test files; comment contract satisfied — every new guard states its incident (the ceiling, the charter pin, the complement scan, the closing-`---` reader each carry their review-finding why; the C7 window comment explains the launcher-half exemption); no banned pattern in the diff; drift/bloat imported from the fan-out above rather than re-hunted (source `review`).

### Step 0.7 — re-derivation (amendment pass)

1. Nothing this diff references moved on `main`: 0 files landed on origin/main since the merge-base; every path re-resolved at review time.
2. True overlap: empty; `merge-tree` clean (fast-forward candidate).
3. Sibling lanes: none live (`git worktree list` = main + this lane); no landing-order dependency.
