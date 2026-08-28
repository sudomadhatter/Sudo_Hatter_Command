# Walkthrough — Adviser Board filter rework (SCC-340)

<!-- twin-law: review-runtime-probe -->
review-runtime: inline (no subagent tool)

**Ticket:** [SCC-340](https://sudo-command.atlassian.net/browse/SCC-340) — Rework /smh-adviser-board to
one-filter-one-mind board rounds · **Subtasks (riders):** SCC-341 (a) · SCC-342 (b) · SCC-343 (c) ·
SCC-344 (d) · SCC-345 (e) — all worked in this lane per `work-consolidation.md` rule 2 (one repo, one
lane class; none earned its own branch).
**Branch:** `chore/SCC-340-adviser-board-filter-rework` off `origin/main` · **Plan:**
[implementation_plan.md](implementation_plan.md) · **Self-audit:** [self-audit.md](self-audit.md) (GO)

## Task Checklist

- [x] Read `/smh-quick-dev` command + approved plan + self-audit + floor/protocol rules
- [x] Mint SCC-340 + five Subtasks SCC-341..345 (a–e) as riders (operator asked for subtasks explicitly)
- [x] Worktree `chore/SCC-340-adviser-board-filter-rework` off `origin/main`; assets linked; SCC-340 → In Progress
- [x] RED first — `verify_board_filter.sh` written and run before any source edit: exit 1, ~90
      retired-vocabulary hits + 9 caucus-sense `floor` hits over the three surfaces (real source, real
      assertions — the gate failed on the actual retired model text)
- [x] Build per the Declared Change Set — all 15 rows landed; `minds/` untouched; no memory files edited
  - Finding: three self-referential negations of the retired model survived the first pass ("no hidden
    caucus", "no triads, no teams") — reworded to eliminate the terms entirely rather than allowlisting,
    so the grep gate needs no exception list.
  - Build decision: with Steps 3 and 7 deleted, the remaining steps were renumbered 0–6 (Round-0 cast
    menu is Step 2, board rounds Step 3, render Step 4, traffic Step 5, close Step 6). The plan keyed
    sections by their current names for identification; renumbering is the mechanical consequence of the
    two deletions, not a design change.
- [x] Door sync — `sync-agents.ps1 -NoGlobals` in the worktree; `.agents/skills/` master + `.claude/skills/`
      + `.opencode/commands/` regenerated; AG launcher (hand-authored, F6) body rewritten by hand in the
      same pass
- [x] GREEN — all five assertions pass, exit 0 (evidence below)
- [x] Commit `ebe7966` (explicit paths, ticket key in subject; SOP + changelog in the same commit per F3 —
      the armed `sop_currency.py` gate satisfied by update, not `[sop-ok]`)
- [x] Enforcement suite — first receipt run RED on one real finding (below); fixed; re-stamped GREEN
- [x] Review gate — `/smh-code-review` ran 2026-08-28; verdict **CONCERNS** @ `1aae519` (rows a/b
      operator-pending); 4 review fixes applied and re-gated — see `## Code Review` below

### Suite finding that fought back

First `run_all` receipt (84.9s @ `ebe7966`): **FAIL — `_artifacts/_main/INDEX.md: missing row for
2026-08-27_adviser-board-filter-rework/`**. The artifacts-index test demands every folder under
`_artifacts/_main/` carry an INDEX row; this lane created the folder. Fixed by adding the row (with this
walkthrough linked), committed, suite re-stamped.

## Evidence

Instrument: [verify_board_filter.sh](verify_board_filter.sh) — vocabulary grep gate (plan §8.2 / row c),
floor adjudication, door parity (row d). Mutation sweep: N/A — no script or gate code changed; the
assertions are grep/cmp instruments over markdown, and the enforcement suite owns the machine floor.

**RED (before any source edit, worktree @ `007efd1`):** exit 1 —
`FAIL(vocab)` × ~90 across `.agents/commands/smh-adviser-board.md`, `adviser-board/{TEAMS,CARD,SPAWNS,ROSTER,DOCTRINE,THIRD-SIDE}.md`,
`.agents/workflows/smh-adviser-board.md` (default triads, caucus clause, stage rooms/change, three minds,
team vocabulary — all real source text) · `FAIL(floor)` × 9 (caucus-log senses in CARD/SPAWNS) ·
`PASS(door)` × 3 (doors still matched the unmodified brain — regression guards, expected green pre-edit).

**GREEN (after build + sync, worktree @ `ebe7966`):**

```
PASS(vocab): zero unjustified retired-vocabulary hits
PASS(floor): no caucus-log sense of 'floor'
PASS(door): opencode mirror byte-identical to brain
PASS(door): claude skill description matches brain description
PASS(door): AG launcher description 127 chars (budget 135)
verify-exit=0
```

**Enforcement suite (receipt [gates/suite.json](gates/suite.json)):** first run FAIL (INDEX row, above);
re-stamped **GREEN** on the fixed tree — includes `workflow_lint.py --toolkit-only` and `sop_currency.py`.
Re-stamped again after the review fixes: **PASS, exit 0, 81.8s @ `1aae5194`** (the review touched
`.agents/commands/` surfaces, which invalidates a receipt — only `_artifacts/` is exempt).

**Acceptance rows:**

- **(c) vocabulary grep gate** — GREEN above (machine-proven).
- **(d) door parity** — GREEN above (machine-proven).
- **(e) enforcement suite** — GREEN receipt (machine-proven).
- **(a) Round-0 cast menu** and **(b) four visible rounds** — these are live board sessions the chair
  flies; the command text that implements them is landed and grep-clean, but only a human can drive the
  dry-run/full session. Owed below.

## Code Review (2026-08-28)

Verdict: CONCERNS @ 1aae519
Suite evidence measured on the same sha: `1aae5194` (receipt `gates/suite.json`, PASS exit 0, 81.8s).

review-runtime: inline (no subagent tool)
lens_isolation: shared — inline ladder in one context; no subagent tool exists in this runtime (SCC-177 probe)
lenses_run:

- edge-case-hunter · recovered-inline
- literal-correctness-hunter · recovered-inline
- acceptance-auditor · recovered-inline
- test-adequacy-auditor · recovered-inline
lenses_counted:  4/4
lenses_na:
- blind-hunter · n/a — context contaminated (holds the plan §11/§12, the walkthrough, and the Step 0.7 radius; dropped rather than faked, SCC-203)

dispositions:    per-lens: edge-case-hunter=2/2/0 · literal-correctness-hunter=3/1/0 · acceptance-auditor=1/0/0 · test-adequacy-auditor=0/1/0
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — reconciled clean after the declared-set fix below (before it: 19 undeclared / 3 incomplete, because the plan's block was a table the `declared_change_set.py` grammar cannot parse)

**Scope:** the full `origin/main...HEAD` diff (32 files: command brain + 6 contracts + 3 doors + AG
launcher + SOP set + 2 INDEXes + lane artifacts). **Method:** inline ladder per the engine contract —
Edge-Case and Literal-Correctness hunted the diff with repo access, the Acceptance Auditor walked it
against the plan, Test-Adequacy walked the assertion instrument; verify wave ran inline (cold — no
dossier; `evidence_extract.py` is a subagent-side tool and this runtime has none); triage applied the
assessor's three-question rule.

### Step 0.7 — re-derivation

1. **Nothing this diff references moved on `main`.** Merge-base `007efd1` == current `origin/main` tip;
   zero files landed while the lane built (`/tmp/theirs.txt` empty), so no reference could have been
   moved out from under it. The only stale references found were the lane's own (finding 3 below).
2. **True overlap: none — no conflicts.** `grep -Fxf mine theirs` → ∅; `merge-tree --write-tree` clean.
   Nothing to absorb; the review sha equals the built sha plus the review-fix commits.
3. **No sibling lanes live** (`git worktree list`: `main` + this tree only) — no landing-order
   dependency. `risk_seam.py classify` → `unclassified`, the permanent correct answer for this
   markdown repo (SCC-289). Derived `review_level`: **standard** (contract surfaces in the radius,
   32 files > 3).

### Findings

| file:line | severity | failure scenario | disposition |
| --- | --- | --- | --- |
| `.agents/commands/smh-adviser-board.md:160` | important | brain Step 3 says "Full templates in `SPAWNS.md` §3–§4" — after the renumbering, §3 is the Round-0 menu and the round templates live in §4–§5; a live session follows the pointer and misses the R2–R4 template | applied @ a962750 (§4–§5) |
| `.agents/commands/adviser-board/ROSTER.md:15` | suggestion | `Best against` named as the sole `swap` ranking key, contradicting the Round-0 top-3 rule (Best against **+ situation index**) the brain's `swap` move cites — two ranking rules for one menu | applied @ a962750 (aligned to the top-3 rule) |
| `_artifacts/.../self-audit.md:44–57` | important | 9 link targets written `path:line` — `check_links.py` resolves `#L<n>` anchors only, so all 9 read as dead paths the diff introduced (FAIL-class per the verdict rules) | applied @ a962750 (`#L<n>` anchors; check_links → clean) |
| `_artifacts/.../implementation_plan.md` (Declared Change Set) | important | block was numbered (`## 11.`) and table-shaped — the drift parser's grammar is `^## Declared Change Set$` + `- OP \`path\` → rows` bullets, so it read `present: false` ("no declared set to reconcile against") and every file read as undeclared drift | applied @ a962750 + 1aae519 (unnumbered heading + machine rows beside the human table; reconciliation → 0/0/0) |
| `docs/_scc_sops_prds/INDEX.md` | suggestion | declared in the plan's F4 prose ("rides with the fix") but had no machine row — read as undeclared drift | applied @ 1aae519 (row added) |
| `.agents/.sync-manifest.json`, `docs/doc-graph.{json,md}`, `.agents/skills/smh-adviser-board/SKILL.md` | suggestion | present in the diff, absent from the declared table | dismissed — sync/map-generated files; now declared explicitly as `EDIT (generated)` rows in the machine block |
| `.agents/workflows/smh-adviser-board.md` exists while `platforms:` excludes antigravity | suggestion | door on a platform the frontmatter does not claim | dismissed — pre-existing hand-authored, prune-protected door the plan maintains by name (§5.2 / F6); not introduced here |
| `verify_board_filter.sh` reports the AG description as 127 chars; an independent count says 125 | nitpick | two counters disagree | dismissed — both under the 135 budget; the declared instrument's own count governs |
| SPAWNS §5 R2–R4 template omits R1's "Reaches for" instruments paragraph | nitpick | R2–R4 spawn not reminded its instruments are optional | dismissed — the persona card it re-reads carries the same line; no concrete failure |

Tail: 9 findings assessed; 5 real and applied, 4 dismissed under the 2026-08-17 ruling. No finding's
assessment disagreed with its lens label in either direction.

### Gates (all re-run on the review-fixed tree @ `1aae519`)

- **Enforcement suite** — receipt PASS, exit 0, 81.8s @ `1aae5194` (re-stamped after the review fixes;
  inherited `a882a1d6` receipt was invalidated by the `.agents/commands/` touches). 61/61 files.
- **Toolkit lint** — `workflow_lint.py --toolkit-only`: 0 errors, 0 warnings, 8 info (BOM infos on
  vendor `testarch-*` files — pre-existing, not this diff's).
- **Assertion evidence** — `verify_board_filter.sh`: PASS(vocab) · PASS(floor) · PASS(door) ×3, exit 0.
- **SOP currency** — `sop_currency.py` exit 0. Review-fix commits carry `[sop-ok]`: they alter no usage
  (a §-pointer, a ranking-rule alignment, plan/self-audit mechanics — the SOP already describes the
  filter model).
- **Link + anchor** — `check_links.py --base origin/main`: clean (27 files, 225 claims, 0 dead) after
  the anchor fix; was 9 dead before.
- **Door parity** — opencode mirror byte-identical to the brain (`cmp`), claude skill == master skill
  (`cmp`), AG launcher description 127 ≤ 135 budget.
- **Declared set** — `declared_change_set.py diff`: present, 0 undeclared / 0 unimplemented / 0 incomplete.
- **bash -n** on `verify_board_filter.sh`: PARSE OK · **py_compile**: n/a (no `.py` in the diff) ·
  **lint/types**: not applicable to this repo (no venv, no ruff, no tsc).

### Acceptance matrix (plan §12, as amended 2026-08-28 — opinion waves, not R1–R4)

| row | evidence |
| --- | --- |
| (a) Round-0 cast menu dry-run | **EVIDENCED** — live board session 2026-08-28; see `## Live Session Evidence` below |
| (b) Full session, parallel opinion waves | **EVIDENCED** — two full waves of real statements flown live 2026-08-28; see `## Live Session Evidence` (the wave's parallelism is a surface property of the command text — this harness spawns sequentially, so the one-message parallel spawn is specified, not machine-provable here) |
| (c) vocabulary grep gate | machine-proven — PASS(vocab) + PASS(floor), exit 0 @ `1aae519`; extended with the round-ladder + wave gates (below), exit 0 after the amendment |
| (d) door parity | machine-proven — cmp ×2 IDENTICAL + AG 127 ≤ 135 @ `1aae519`; re-proven after the amendment (AG 130 ≤ 135) |
| (e) enforcement suite | machine-proven — receipt PASS exit 0 @ `1aae5194`, incl. workflow_lint + sop_currency; re-stamped after the amendment |

### Clean-Code Gate — PASS

**Machine floor** (imported from Step 3 — no double run): run_all PASS 61/61 exit 0 @ `1aae5194` ·
workflow_lint 0 errors / 0 warnings · sop_currency exit 0 · link+anchor clean · door parity green.
**This step's own checks:** `bash -n verify_board_filter.sh` PARSE OK · py_compile n/a (no `.py`) ·
comment contract (§2A): the diff's only code is the verify script — its comments carry SCC-340
provenance and state the floor-adjudication rule, no stale AIDEV-NOTE, no TODO/FIXME · banned-pattern
scan over added lines: none · conventions (§2C): naming law clean (workflow_lint), one door per
platform holds, generated files hand-edited: none (the AG launcher is the sanctioned hand-owned
exception), artifacts in the tree: yes. No findings above noise.

**Changes applied:** the five fixes in the findings table (commits `a962750`, `1aae519`, both
explicit-path, `[sop-ok]` where the hook demanded a SOP call) — every gate re-run after the last one.
Nothing merged, nothing closed, no ticket transitioned.

**Verdict basis:** every machine gate is green on the changed set and every engine finding is applied
or dismissed with a reason — but acceptance rows (a) and (b) have no evidence a machine can produce:
they are live board sessions only the chair can fly. An acceptance item with no evidence caps the
verdict at CONCERNS per the verdict rules; it is operator-pending, not failed. When the chair has flown
the dry-run and a full session, this lane closes via `/smh-close-task-merge-tree`.

## Your Actions

Everything the lane could prove by machine is proven above, and the chair has now flown the board
himself — see `## Live Session Evidence`. His mid-session amendment (parallel opinion waves +
orchestrator-does-all-research + rich-text rendering) is applied and re-gated in this lane; nothing
merged, nothing closed, no memory touched.

Then review and close out with `/smh-close-task-merge-tree` when satisfied.

## Operator amendment — parallel opinion waves (2026-08-28, live session)

Mid-session, the chair amended the design with two verbatim lines (quoted in full in
`## Live Session Evidence`): replies must be **easier to read** (rich text, headings), and the fixed
R1→R4 ladder must become **parallel opinion waves** — every seated filter spawns at once, each reads
what the others said and what the chair replied, and he gets several independent takes to choose from
instead of a forced read→attack→balcony→settle sequence. In the same session he ruled the division of
labour: **the orchestrator does all the searching** — database, web, project files — "the personalitys
have access to that information… they dont individually search for it. then they run in parallel and
come back with feed back."

Applied (all in this lane, same commit set):

- **Brain** (`smh-adviser-board.md`): Step 3 is now *Opinion waves (parallel)* — one wave per round of
  the chair's attention, **all Agent calls in a single message**, no mandatory sequence; attack /
  balcony / settle are **chair-invocable deepening moves** in the traffic table (`settle it` /
  `balcony` / `X vs Y` duel). Step 1 gains the **research brief**: the orchestrator gathers web /
  database / file research before the first wave and every spawn carries it; filter spawns never
  search (the old per-filter read caps are retired). Step 4 renders statements in **rich text**.
  Frontmatter description, chair rules, standing rules and the failure playbook all moved to wave
  vocabulary.
- **CARD.md**: rendering rules restructured — each statement is a markdown section (`### {icon}
  {Filter} — {Mind}` heading, italic one-line stance note, prose as a blockquote, bold slot labels).
  The verbatim law now governs the **words, not the typography** — stated explicitly.
- **SPAWNS.md**: the four R1–R4 templates replaced by ONE opinion-wave template (§4) carrying mind
  card, blind spot, house discipline, ground brief, **research brief**, doctrine, running summary
  ≤400 words, every other filter's statements verbatim, and the chair's latest words; the call-out
  template (§5) and the ER/Sales scope clause survive; inline mode is now §6 — one pass, all takes in
  a wave written before any is revised, every called move intact.
- **Consistency sweep**: THIRD-SIDE.md (balcony = chair-invoked move), TEAMS.md, the hand-maintained
  AG launcher (description 130 ≤ 135), `smh-adviser-board-REFERENCE.md`, `.agents/commands/INDEX.md`,
  the SOP row + cast-gate passage, and a new changelog line. Doors re-synced via
  `sync-agents.ps1 -NoGlobals` in the worktree — opencode mirror byte-identical, claude skill
  description matching.
- **Assertion instrument**: `verify_board_filter.sh` extended with a round-ladder gate (R1 READ /
  R2 ATTACK / R3 BALCONY / R4 SETTLE / four visible rounds / round ladder = retired) and wave-vocabulary
  presence checks (`opinion wave`, one-message parallel spawns, `RESEARCH BRIEF`, `settle it`).

**RED → GREEN.** RED before any source edit (worktree @ `764b2b2`): exit 1 — `FAIL(rounds)` × 7
(brain description + Step 3, SPAWNS §4 heading, TEAMS, AG description + body) and `FAIL(wave)` × 4
(brain lacks 'opinion wave' + 'settle it'; SPAWNS lacks 'opinion wave' + 'RESEARCH BRIEF'). Two
self-inflicted hits ("no fixed round ladder" in the new text) were reworded rather than allowlisted,
per the lane's own precedent. GREEN after build + re-sync: exit 0 —

```
PASS(vocab): zero unjustified retired-vocabulary hits
PASS(rounds): zero retired R1–R4 ladder terms
PASS(wave): parallel-wave vocabulary present (brain + SPAWNS)
PASS(floor): no caucus-log sense of 'floor'
PASS(door): opencode mirror byte-identical to brain
PASS(door): claude skill description matches brain description
PASS(door): AG launcher description 130 chars (budget 135)
verify-exit=0
```

## Live Session Evidence (2026-08-28)

The chair flew the board live on a real topic before amending it. What the session showed, in order:

1. **Round-0 cast menu rendered verbatim** — four filters seated (🔬 First Principles · 🎯 Human
   Needs · 🌊 Ruin & Ripple · 🩺 Ground Truth cut last), each with its top-3 menu, and three cut
   lines for the refused filters. The chair picked **"your pick ×4"**, seating Feynman · Semmelweis ·
   Munger · Drucker — one mind per filter, exactly as row (a) specifies.
2. **Two full waves of real statements ran.** Wave 1: independent takes, one verbatim statement per
   filter. Wave 2: cross-filter attacks — including **Munger's concession to the record** and the
   **Feynman-vs-Semmelweis collision** (the same duel the traffic table now names as the `X vs Y`
   example). Statements arrived verbatim with the ⚖ collision line and ≤2 questions.
3. **The rich-text render demo was shown to the chair** — heading per mind, italic stance note,
   blockquoted prose, bold slot labels — which prompted amendment line 1.
4. **The chair then amended the design** (his words, verbatim):
   > "Lets make the replys easier to read. I would prefer then to be well designed for easy read
   > ability using rich text and headings"
   >
   > "Can we have them run in parallel instead of reading what each is saying as they go ? they just
   > read what was said by the others in the chat, and then what I reply to everyone. Then I get 5
   > different opinions to choose from and they can expand from there after I guide it to the track I
   > am looking for. This gives me more ideas to brain storm with it doesnt block any ideas out of
   > the gate. And it will speed things up alot. we can then run them in parallel."
5. **Division of labour ruling** (same session, paraphrase-close): the orchestrator does all the
   searching of databases and the web; the personalities receive that information and run in
   parallel, coming back with feedback — they do not individually search.

**Evidence scope, stated honestly:** rows (a) and (b) are evidenced by this session. Row (b)'s
**parallelism is a surface property of the command text** — this harness spawns subagents
sequentially, so the one-message parallel spawn is specified in the command (and asserted present by
the wave gate) but cannot be machine-proven from this runtime; the amendment's *content* — waves not
a ladder, transcript circulation, chair-guided deepening, orchestrator research — is what the session
actually exercised and what the landed text now implements.
