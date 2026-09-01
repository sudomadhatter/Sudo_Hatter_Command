# SCC-304 — Give /cicd-live-testing-team its own eyes: a Node Playwright frontend-check skill

**Lane:** `chore/SCC-304-playwright-frontend-check` · **Repo:** Sudo_Hatter_Command (lobby)
**Date:** 2026-08-23 · **Lane type:** `/smh-quick-dev` (lane_qualify: TASK — toolkit paths)

---

## The problem, in one paragraph

`/cicd-live-testing-team` is the one command that flies a running app, and its Step 2 says flatly
**"You cannot see the browser."** Every frontend symptom therefore arrives as a relay: the agent
coaches the human for one Console line, then one Network row, then component state, and the evidence
that reaches the bug doc is whatever survived retyping. Playwright is already installed on this
machine, so that constraint is no longer true — it is just unwired. Nothing in `.agents/skills/`
teaches an agent to use it, and Anthropic's official `webapp-testing` skill (the one the research
found) is **Python**, which is not what is installed here.

## Ground truth — measured, not assumed

Everything below was run before this plan was written. `verified` = evidence in hand.

| Fact | Evidence | Status |
|---|---|---|
| Playwright is **Node**, not Python | `@playwright/test ^1.58.2` in `Projects/AGY_AVIATIONCHAT/frontend/package.json`; `node_modules/.bin/playwright` present; `pip3 list \| grep -i playwright` empty | verified |
| Browsers are already downloaded | `~/Library/Caches/ms-playwright/` holds `chromium-1208`, `chromium-1234`, `chromium_headless_shell-*`, `ffmpeg-1011` | verified |
| ⛔ chromium **cannot launch while the Bash sandbox is ON** | `chromium.launch()` → `FATAL:mach_port_rendezvous_mac.cc:155 Check failed: kr == KERN_SUCCESS. bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer.<pid>: Permission denied (1100)` | verified |
| ...and succeeds with the sandbox off | same script, `dangerouslyDisableSandbox: true` → `TITLE_TEXT: hello`, `CONSOLE: ["log: probe-console-ok"]`, 5717-byte PNG written. Re-probed after the operator turned the sandbox off session-wide: launches clean with **no override at all**. | verified |
| The script must resolve `node_modules` from the frontend that owns Playwright | same script run from the scratchpad → `ERR_MODULE_NOT_FOUND`; run with cwd in `AGY_AVIATIONCHAT/frontend` → resolves | verified |
| A bare `npx playwright test` in AGY runs the journeys suite WITHOUT the Firebase emulators and fails fast | `frontend/playwright.config.ts` header comment | docs-say |

The two ⛔ rows are the whole reason this cannot be a copy of the upstream skill. An agent that reads
Anthropic's `webapp-testing` and follows it verbatim on this machine gets a Python `ImportError`, and
an agent that fixes that by switching to Node still gets a fatal Mach-port abort with no hint that the
sandbox caused it. Both traps are invisible from inside the failure.

## Acceptance (each row is checked by a command)

| # | Acceptance | Check |
|---|---|---|
| A1 | The skill exists and is well-formed | `.agents/skills/playwright-frontend-check/SKILL.md` carries `name:` + `description:`; `run_all.py` exits 0 |
| A2 | Its documented recipe RUNS on this machine | the skill's own probe writes a PNG and captures a console
line, exit 0. ⚠️ **AUDIT F3:** recorded as a transcript in the walkthrough, NOT as a suite row — the suite must
stay runnable on a machine with no Playwright and no browser, and `run_all.py` is stdlib-only by contract. |
| A3 | `/cicd-live-testing-team` reaches for it before coaching the human | `test_live_testing_browser_instrument.py`: the command body names the skill AND that skill dir exists on disk |
| A4 | The skill is published to the platform doors | `.claude/skills/playwright-frontend-check/SKILL.md` exists; `workflow_lint.py --toolkit-only` exits 0 |
| A5 | The skills INDEX names it in the Frontend / UI family | grep `.agents/skills/INDEX.md` |
| A6 | The operator's SOP moved with the command | `sop_currency.py` accepts the commit with no `[sop-ok]` |
| A7 | The lane leaves its record | plan, ticket rider, walkthrough and `task.yaml` exist under
`_artifacts/_main/2026-08-23_playwright-frontend-check/`; the close-out preflight blocks without them |

## Steps, each naming the assertion that proves it

1. **RED first — `.agents/scripts/tests/test_live_testing_browser_instrument.py`.**
   Run it before any edit and record the failure. It asserts the **wiring**, not prose (this house
   has three memories about how source-grep guards go blind): the command body names a skill slug,
   that slug resolves to a real `SKILL.md` on disk, and that file's frontmatter `name:` equals the
   slug. Mutants it must kill: delete the skill dir → RED; rename the slug in the command → RED;
   rename `name:` in the frontmatter → RED. Prose-only pinning kills none of those. → A1, A3

2. **Author `.agents/skills/playwright-frontend-check/SKILL.md`.** Hand-authored (no `/` command, so
   no launcher), named for what it knows per the SCC-63 naming rule. Content: the decision tree and
   reconnaissance-then-action discipline adapted from Anthropic's `webapp-testing`, re-expressed in
   Node, plus THE TWO TRAPS above stated as the first thing an agent reads, plus the four recipes the
   co-pilot loop actually needs — console capture, network capture, screenshot, DOM/selector recon —
   and the boundary that it reads the browser and never writes product code. → A1, A2

3. **Wire `/cicd-live-testing-team`.** Step 2's "You cannot see the browser" becomes "you can see the
   browser, but only through this skill, and only with the sandbox off": the skill is the FIRST
   frontend instrument, ahead of coaching the human, and the human stays the fallback for anything
   auth-gated or hard to script. Step 2's instrument ladder gains the row; Step 3's bug-doc
   **Evidence** section says captured artifacts (PNG + console/network JSON) are attached. → A3

4. **`.agents/skills/INDEX.md`** — add to the Frontend / UI family row. → A5

5. **`docs/_scc_sops_prds/workflows_testing_SOP.md`** — the command's usage changed, so the SOP moves
   in the same commit or the armed `sop_currency` gate refuses it. → A6

6. **`/smh-sync-agents`** to publish the skill to `.claude/skills/` and the platform caches, then the
   gates. → A4

## Declared Change Set

⚠️ **AUDIT FINDING F1 (fixed here):** the first draft of this block wrote `path — OP → rows`.
`declared_change_set.py parse` returned `"entries": []` with 8 `incomplete` bullets — the grammar is
**op first**. An empty parse makes `/smh-code-review` Step 2 diff the real change set against nothing
and report no drift: a green that lies.

- NEW `.agents/scripts/tests/test_live_testing_browser_instrument.py` - the permanent wiring guard, seen RED first -> A1, A3
- NEW `.agents/skills/playwright-frontend-check/SKILL.md` - hand-authored, Node, no launcher -> A1, A2
- EDIT `.agents/commands/cicd-live-testing-team.md` - Step 2 instrument ladder + Step 3 Evidence row -> A3
- EDIT `.agents/skills/INDEX.md` - Frontend / UI family row -> A5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` - SOP currency, same commit -> A6
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` - one provenance row -> A6
- NEW `.claude/skills/playwright-frontend-check/SKILL.md` - published by sync, never hand-edited -> A4
- EDIT `.agents/.sync-manifest.json` - regenerated by sync, never hand-edited -> A4
- EDIT `.agents/skills/cicd-live-testing-team/SKILL.md` - launcher, regenerated by sync (the command's description changed) -> A4
- EDIT `.agents/workflows/cicd-live-testing-team.md` - Antigravity mirror, regenerated by sync -> A4
- EDIT `.claude/skills/cicd-live-testing-team/SKILL.md` - Claude cache, regenerated by sync -> A4
- EDIT `.opencode/commands/cicd-live-testing-team.md` - opencode mirror, regenerated by sync -> A4
- EDIT `.claude/skills/INDEX.md` - cache mirror of the skills INDEX, regenerated by sync -> A4
- EDIT `docs/doc-graph.json` - regenerated and STAGED by the pre-commit refresh-maps hook -> A7
- EDIT `docs/doc-graph.md` - regenerated and STAGED by the pre-commit refresh-maps hook -> A7
- NEW `_artifacts/_main/2026-08-23_playwright-frontend-check/implementation_plan.md` - this plan -> A7
- NEW `_artifacts/_main/2026-08-23_playwright-frontend-check/tickets/SCC-304.md` - the ticket rider -> A7
- NEW `_artifacts/_main/2026-08-23_playwright-frontend-check/walkthrough.md` - the close-out record -> A7
- NEW `_artifacts/_main/2026-08-23_playwright-frontend-check/task.yaml` - the close-out manifest -> A7


> **Post-sync amendment (build time, not a change of approach).** `/smh-sync-agents` regenerates
> every door whose SOURCE changed. Editing the command's `description:` therefore rewrites its four
> platform mirrors, and editing `.agents/skills/INDEX.md` rewrites its `.claude/skills/` copy - five
> generated files, none hand-edited, all mechanical consequences of masters already declared above.
> They are listed so `/smh-code-review` Step 2 sees no undeclared drift. **Nothing about the
> approved approach changed**; had they been left undeclared the review would have reported five
> phantom findings, which is the failure this record prevents.

## Out of scope, deliberately

- **No Python Playwright install.** Node is what is installed; adding a second runtime to serve a
  skill nobody has used yet is the over-engineering this lane exists to avoid.
- **No change to `/cicd-e2e` or the AGY journeys suite.** This skill is an *observation* instrument
  for the co-pilot loop; the E2E tier is a different job with a different gate.
- **No product-code writing.** `/cicd-live-testing-team` writes evidence, not patches, and this skill
  inherits that boundary.

## Landing-order dependency

`SCC-280-teaching-edition` (parked, `Blocking/Security Risk`) also edits `.agents/.sync-manifest.json`.
Zero other file overlap. Neither lane blocks the other; whichever lands second re-runs
`/smh-sync-agents` to regenerate that one file. Per the house memory, lane collision is **gates, not
files** — so the second lane also re-runs `run_all.py` and `workflow_lint.py` over the combined tree.

## Risks

| Risk | Mitigation |
|---|---|
| The sandbox trap gets written as prose and ignored | it is the FIRST section of the skill, stated as a symptom-to-cause table so an agent hitting the Mach-port abort can match on the error text |
| The skill is written against AGY's node_modules and breaks for a project without Playwright | the skill states the resolution rule and the one-line install fallback rather than hardcoding AGY's path |
| A `grep`-shaped test that passes on a comment | the assertion binds slug → file → frontmatter `name:`, so a comment mentioning the slug cannot satisfy it alone; mutants listed in Step 1 |

---

## Self-Audit (2026-08-23)

**Level: LEDGER+BLAST** — the Declared Change Set touches a command/door surface, a new script, a
skills cache and more than one platform. **Mode: PRE-WORK.** Repo: `Sudo_Hatter_Command` ·
Branch: `chore/SCC-304-playwright-frontend-check` · Ticket: SCC-304.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/script/door the plan names resolved on disk; Declared Change Set parsed
             with declared_change_set.py; sop_currency.py _SURFACES + _EXEMPT_PREFIXES read at
             source to confirm which of this lane's paths actually arm the gate; run_all.py
             discovery mechanism read at source (auto-discovery -> no registration edit to
             declare); lane-fit check for deployable paths; Scope Ledger over every NEW entry
read:        .agents/scripts/sop_currency.py:59-83 · .agents/scripts/declared_change_set.py (via
             `parse`) · .agents/scripts/tests/run_all.py:11 · .agents/scripts/tests/_harness.py:99-180 ·
             .agents/scripts/tests/test_command_surfaces.py:662-690 · .agents/commands/cicd-live-testing-team.md ·
             .agents/skills/INDEX.md:3 · docs/_scc_sops_prds/workflows_testing_SOP_changelog.md ·
             Projects/AGY_AVIATIONCHAT/frontend/{package.json,playwright.config.ts} · the plan itself
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  twin check (`ls .agents/commands/ | grep live-testing`) - NO smh- twin exists, so the
             twin-parity obligation is cleared, not skipped; four-door check for the new skill
             (hand-authored, no command -> CS-07's ghost rule is about workflows, and CS-06 requires
             only frontmatter, both confirmed at source); sop_currency surface classification per
             path; sibling worktrees fetched and diffed; risk_seam classify run for shape
read:        .agents/scripts/tests/test_command_surfaces.py:662-690 (CS-05/CS-06/CS-07) ·
             .claude/skills/{systematic-debugging,python-patterns} (hand-authored skills ARE
             published to the cache) · git worktree list + `git -C <tree> diff --name-only
             origin/main...HEAD` for SCC-280 · risk_seam.py classify -> {"status":"unclassified"}
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  attached failure narratives to F2 and F4 only; produced no finding of its own
read:        the two anchored findings above
verdict:     clean (attached, originated nothing)
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `implementation_plan.md` § Declared Change Set | `declared_change_set.py parse` returned `"entries": []` with **8** `incomplete` bullets — *"the left side is not `<OP> <path>`"* | **F1.** `/smh-code-review` Step 2 diffs the real diff against the declared set. An empty parse compares against nothing and reports no drift — a green that lies. Silent: nothing fails today. **FIXED in-plan; re-parse now reads 12 entries / 0 incomplete.** | important |
| `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` (last 4 rows, each `\| — \| SCC-NNN \| …`) | one provenance row per change, e.g. *"`— \| SCC-298 \| Close-out **reconciles** `## Your Actions` before `finish`…"* | **F2.** The plan declared the SOP but not its changelog, so this change would land with no history row. Not gate-enforced, which is exactly why it gets forgotten. **FIXED: declared.** *(Pre-Mortem: the silent one — six months on, the SOP says the skill exists and nothing says when or why.)* | suggestion |
| measured probe output, this session | sandbox ON → `FATAL:mach_port_rendezvous_mac.cc:155 … Permission denied (1100)`; sandbox OFF → `SANDBOX_NOW_OFF: chromium launched clean` | **F3.** A2 as written ("its recipe RUNS, exit 0") reads as a suite row. It cannot be one: `run_all.py` is stdlib-only and must pass on a machine with no Playwright and no browsers. A reviewer would hunt for a test that must not exist. **FIXED: A2 restated as recorded transcript evidence.** | important |
| `.agents/scripts/sop_currency.py:71-78` `_SURFACES` / `:82` `_EXEMPT_PREFIXES` | `(".agents/commands/", (".md",), "the / command menu")` · `_EXEMPT_PREFIXES = (".agents/scripts/tests/",)` · `_EXEMPT_NAMES = {"INDEX.md"}` | **F4.** Confirms A6 is armed by exactly ONE path in this lane — the command edit. The new test file and both `INDEX.md` edits are exempt, and `.agents/skills/` is not a surface at all. So the SOP edit is load-bearing and cannot be dropped as "the skill isn't a usage surface". *(Pre-Mortem: the fresh-clone one — `core.hooksPath` is per-machine, so on an unarmed clone the gate is silently off and the omission ships.)* | suggestion |

No finding breaks an acceptance row or a hard gate. **All four are baked into the plan inline.**

### Scope Ledger

| CREATES (op `NEW`) | acceptance row requiring it |
|---|---|
| `.agents/scripts/tests/test_live_testing_browser_instrument.py` | A1, A3 |
| `.agents/skills/playwright-frontend-check/SKILL.md` | A1, A2 |
| `.claude/skills/playwright-frontend-check/SKILL.md` | A4 |
| `…/implementation_plan.md` | A7 |
| `…/tickets/SCC-304.md` | A7 |
| `…/walkthrough.md` | A7 |
| `…/task.yaml` | A7 |

**No empty acceptance cell.** A7 was added by this audit — the ceremony artifacts were being created
by an unwritten rule. **Caller count** for the one artefact that could be orphaned: the new SKILL.md
gains a caller created by this same plan (`cicd-live-testing-team.md`) *and* a second, independent one
(`.agents/skills/INDEX.md` Frontend/UI row) — falsifiable by `grep -rn playwright-frontend-check
.agents/` after the edits, which must return ≥2 files that are not the skill itself.

### Lane fit

The Declared Change Set touches **no** deployable path (`backend/` `frontend/` `firebase/`
`functions/` `mobile/` `.github/`). `Projects/AGY_AVIATIONCHAT/frontend/` was **read** for ground
truth and is **not** in the change set. Correct door: `/smh-close-task-merge-tree`.

### Landing-order dependency

`SCC-280-teaching-edition` (parked, `Blocking/Security Risk`) — its committed diff includes
`.agents/.sync-manifest.json`, which this lane's sync also regenerates. **That is the only overlap**
(its other 30 paths — `smh-tour`, `smh-training`, `teaching-edition/`, `rules/INDEX.md`,
`commands/INDEX.md`, `scripts/INDEX.md` — are disjoint from this set; `skills/INDEX.md` is untouched
by it). Neither lane blocks the other. Whichever lands second re-runs `/smh-sync-agents` to
regenerate that one file, and — per the house rule that **lane collision is gates, not files** —
re-runs `run_all.py` and `workflow_lint.py --toolkit-only` over the combined tree.
*(Pre-Mortem: the sibling-lands-first one — a hand-merged manifest that nobody regenerates is a
manifest that disagrees with disk, and `test_command_surfaces.py` is what discovers it, on someone
else's commit.)*

### Observations (uncounted, no severity)

- `.agents/skills/INDEX.md:3` claims *"the **32** authored skills in `.agents/skills/`"*. Measured
  today: **72** directories, of which **49** are hand-authored and **23** carry the
  `GENERATED by sync-agents` marker. The number is stale under every reading, and was stale before
  this lane. **Not fixed here** — no acceptance row requires it and correcting a count in a file this
  lane happens to touch is scope drift. Worth a rolling-ticket line.
- `risk_seam.py classify` returns `{"status": "unclassified", "root": ".../Sudo_Hatter_Command"}` —
  expected and correct per SCC-289: the command centre carries no code graph because it is markdown.
  Every Lens 2 judgement above was taken from the diff, not the classifier.
- `playwright.config.ts` warns that a bare `npx playwright test` in AGY lacks the Firebase emulators
  and fails fast. That is a boundary the skill should state, and it is why this skill is an
  *observation* instrument rather than a second E2E door.

Audit verdict: GO
