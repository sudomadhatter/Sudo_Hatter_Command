---
IsArtifact: true
ArtifactMetadata:
  title: Replace GitNexus with code-review-graph and wire rules/skills activation — walkthrough
  type: walkthrough
  date: 2026-08-22
  ticket: SCC-270
  twin: AVCH-73
---

# SCC-270 — walkthrough

Lane: `chore/SCC-270-code-review-graph-swap` (consolidated; riders SCC-272 … SCC-278).
Plan: [implementation_plan.md](implementation_plan.md). Approval recorded at `4d5a07e`, covering the
plan as it stood at `60b6868`.

## Task Checklist

- [x] **Part A · SCC-272** — bake-off + both-machine install recipe. **PASS; tripwire did not fire.**
- [x] **Part B · SCC-273** — lobby MCP, ignore and scope files. Index scoped 300→126 files; mirrors excluded.
- [x] **Part C · SCC-274** — `docs/code-review-graph.md`, every pointer re-aimed, 12 skill docs → 1 house skill.
- [x] **Part D · SCC-275** — check 9 reads the graph DB via stdlib `sqlite3`; commands re-cited; **acceptance row 2 met**.
- [x] **Part E · SCC-276** — activation frontmatter on all 25 rules; `.claude/rules/` emitted by the sync.
- [x] **Part F · SCC-277** — prompt-trigger hook + `InstructionsLoaded` probe; canary § "Probe 2".
- [x] **Part H · SCC-278** — `risk_seam.classify` answers from the graph; both reviews print the tiers.
- [x] **Part G · AVCH-73** — AviationChat, its own repo and lane. Committed and pushed on
  `chore/AVCH-73-code-review-graph-swap`; its own walkthrough carries the AGY bake-off.
  - ⛔ Found there: GitNexus is **live code** in `backend/tia/`, outside AVCH-73's scope. Ported by
    **AVCH-77** (under AGY's CI/CD epic AVCH-43), which also adds the macOS entry point that gate has
    never had. AVCH-73's acceptance 1 was amended to name its carve-outs rather than read as passed.
- [x] **Review** — `/smh-code-review`, this file's `## Code Review (2026-08-22)` section. Three
  findings applied in thread, three dismissed with reasons. **CONCERNS** — every gate green, floor
  raised because the Blind Hunter was dropped (this context built the lane).

## Evidence

### Part A — the bake-off (acceptance row 1)

**Install (Mac, 2026-08-22).** `brew install pipx` (1.16.7) → `pipx install code-review-graph` →
**code-review-graph 2.3.8 on Python 3.14.7**. Console script:
`~/.local/bin/code-review-graph` → `~/Library/Application Support/pipx/venvs/code-review-graph/bin/code-review-graph`.
⚠️ That real path is what the Mac's local-scope `~/.claude.json` override must name: a GUI-launched
editor gets a stripped `PATH` that does not contain `~/.local/bin` — the identical scar that left this
machine with zero GitNexus tools for weeks.

**Build — three graphs, all cold, all under 8 seconds.**

| Graph | Files | Nodes | Edges | Wall | Built-at commit |
|---|---|---|---|---|---|
| Lobby (this lane's worktree) | 300 (166 with nodes) | 1,637 | 29,400 | **4.0 s** | `4d5a07e` |
| AGY_AVIATIONCHAT (`main`) | 839 (798) | 8,869 | 76,429 | **5.9 s** | `f2f04c85` |
| AGY story worktree AVCH-34 | 825 | 8,871 | 75,698 | **7.1 s** | lane HEAD |

`status --json` carries `built_at_commit` **and** `current_sha`, and the SQLite `metadata` table holds
`git_head_sha` — **check 9's mechanism is confirmed real** (acceptance row 4 is buildable exactly as
planned, with stdlib `sqlite3` and no CLI on `PATH`). A per-worktree graph works, which the lane model
needs. `frontend/.next` was auto-excluded as build output without being asked.

**⭐ The finding that matters most for the command centre: `.agents/` is indexed.**

```
nodes by top-level dir:  .agents 1073 · .claude 257 · .agent 193 · _artifacts 42 · _bmad 32 · docs 24 · .githooks 4
check_maps.py 35 nodes · jira_feed.py 110 · task_preflight.py 37 · workflow_lint.py 22 · sop_currency.py 8
```

GitNexus's lobby index was **86 symbols across 18 files** and was *structurally* blind to `.agents/`
(its walker hardcoded `dot: false`, so the whole master toolkit was invisible and the `!/.agents/`
line in `.gitnexusignore` was inert). The toolkit this repo exists to maintain is now graph-visible for
the first time. The same table also proves Part B's necessity: `.claude` (257) and `.agent` (193) are
sync **mirrors** re-indexing the same symbols — `.code-review-graphignore` must exclude them.

**Blast radius — `calculate_cognitive_zone`, checked against grep rather than against GitNexus's claim.**

`query callers_of` → **5**: `SpecialistOrchestrator.handle_socratic` + 4 tests.
Ground truth (`grep`): the function is called at `backend/agents/specialist/agent.py` lines 2459, 2537,
2663, 2684, 2722 — **all five inside `handle_socratic`** (1838–2812) — plus the test file. So one
caller function and its tests is **exact**, and `tests_for` independently returned those 4 tests.

Walking up one level, `query callers_of handle_socratic` → 19, including **`event_stream`
(`backend/routers/specialist.py`)** and `run_terminal` (`backend/scripts/socratic_terminal.py`), plus
17 tests. Grep confirms the only two non-test callers of `handle_socratic` are exactly those two sites
(`specialist.py:360`, `socratic_terminal.py:74`).

GitNexus's recorded answer was *"HIGH risk, 7 upstream into event_stream / specialist_chat /
quiz_tutor / socratic_chat."* Measured against grep, the true chain is
`socratic_chat` → `event_stream` (defined line 358) → `handle_socratic` → `calculate_cognitive_zone`.
**`specialist_chat` and `quiz_tutor_chat` do not reach it at all** — GitNexus over-reported, because
`specialist.py` defines **three** nested closures named `event_stream` (lines 143, 358, 429) and it
collapsed them. code-review-graph has the same same-name-closure imprecision in the other direction:
it names the right file and the right function name but attributes the call to the copy at line 429
(`quiz_tutor_chat`'s) rather than 358 (`socratic_chat`'s).

**Verdict on the tripwire: it does not fire.** code-review-graph did not miss a caller GitNexus found —
it found the true chain, and GitNexus's extra two were false. Both tools share one precision limit on
same-named nested closures; neither is safe as a *sole* authority, which is why the house contract
keeps "read the source the graph points you at" rather than trusting the node list.

**Change detection — the capability GitNexus had no equivalent of.** From the AVCH-34 story worktree:

```
detect-changes --base $(git merge-base HEAD main)   →  12 changed files
  38 changed function(s)/class(es) · 0 affected flow(s) · 20 test gap(s)
  Overall risk score: 0.60
  Untested: _assert_off_loop, _Snapshot, exists, to_dict, _DocRef
  Token savings: 81,512 → ~9.9k
```

⚠️ **Semantic to bake into the house contract (Part C):** `--base main` is **two-dot** — it reported
104 files because it counted everything that landed on `main` since the branch diverged. The
lane-only question needs **`--base $(git merge-base HEAD main)`**, which returns exactly the 12 files
`git diff --name-only main...HEAD` lists. Writing `--base main` in the contract would have shipped a
review that silently reviews other lanes' work.

**MCP server — 30 tools (acceptance row 4).** macOS has no `timeout` binary, so the probe is
`perl -e 'alarm(60); exec "code-review-graph","serve"'`. ⚠️ A bare `initialize` + `tools/list` returns
**only** the initialize result (542 bytes, zero tools) — the handshake needs
`{"jsonrpc":"2.0","method":"notifications/initialized"}` between them. Recording that here because the
first probe looked exactly like a dead server. With it: 37,529 bytes and all 30 tools, including the
seven this lane exists for — `detect_changes_tool`, `get_review_context_tool`, `get_impact_radius_tool`,
`get_affected_flows_tool`, `get_knowledge_gaps_tool`, `get_hub_nodes_tool`, `get_suggested_questions_tool`.
`serverInfo` reports the MCP layer as `3.4.7` while the package is `2.3.8` — cosmetic, noted so nobody
chases it later.

## Suite Ledger

| Gate | When | Result |
|---|---|---|
| `declared_change_set.py parse` | plan, after audit amendments | present, 113 entries, 0 incomplete |
| `run_all.py` | after D, E, F, H, and again at the shipping sha `1133ebb` | **52/52 files, exit 0** (was 49; E and F each add one, SCC-279 adds `test_entry_adapters.py` on the absorb) |
| `workflow_lint.py --toolkit-only` | after D, E, F, H | **0 errors, 0 warnings** |
| `test_check_maps_graph_fresh.py` | Part D, RED→GREEN + 3 mutants | 5/5; mutants all killed |
| `test_rule_frontmatter.py` | Part E, RED→GREEN + 2 mutants | 9/9; mutants all killed |
| `test_rule_trigger.py` | Part F, RED→GREEN + 4 mutants | 18/18; mutants all killed |
| `test_risk_seam.py` | Part H, RED→GREEN + 6 mutants | 24/24; mutants all killed |
| `check_maps.py` | Part D | ledger row added; depth-3 clean |
| `gate_receipt.py` | at the tip, once | not yet run |

### Parts B–E — what landed

**B (SCC-273).** `.mcp.json` and `.antigravity/mcp.json` now run `code-review-graph serve`;
`.gitnexusignore`/`.gitnexusrc` deleted; `.code-review-graphignore` written. ⚠️ **SCC-186 landed on
`main` mid-lane touching all four MCP configs** (it added Playwright). The merge kept *both* facts —
verified per file: `code-review-graph` + `md-feedback` + `playwright`, no `gitnexus`. Scoping the
index dropped it from 300 files/1637 nodes to **126/1111**, of which **1073 are `.agents/`**; the
`.claude`/`.agent` mirror duplicates the plan predicted are gone.

**C (SCC-274).** `docs/code-review-graph.md` is the house contract. Twelve GitNexus skill docs
deleted — six masters *and* six tracked copies under `.claude/skills/` that the sync manifest never
owned and could not have purged (audit finding F1/F6, caught at plan time). The repo-map's two-index
workaround was deleted rather than reworded: it existed only because the old walker could not read
`.agents/`.

**D (SCC-275).** Check 9 rewritten. Its test is new (the check had **none** before), and because the
red died at import rather than at an assertion, three mutants were run to prove the green: going
blind, inverting the comparison, and dropping the fix command from the message all fail. **Acceptance
row 2 is met** — `gitnexus` appears in no tracked file outside `_artifacts/` history.

**E (SCC-276).** All 25 rules carry activation frontmatter mirroring `rules/INDEX.md`. The one thing
worth stating plainly: **a rule without `paths:` loads at launch, unconditionally**, so path-scoping
is not decoration — it is the difference between a gate that binds and a gate that waits for someone
to open the right file. Floor and protocol tiers are therefore left unscoped, and the test asserts
they never gain `paths:`. `.claude/rules/` holds six generated copies, never symlinks (Windows
without Developer Mode turns a symlink into a text file containing a path).

**F (SCC-277).** Two hooks, one for each way a rule activates. `rule-trigger.py`
(`UserPromptSubmit`) reads the `triggers:` lists that twelve rules carried and **nothing had ever
read** — Antigravity judges a rule's `description:` itself, Claude Code had no equivalent, so a
request-shaped rule could not activate at all. It prints pointers, never bodies, three at most.
Matching is **word-set, not substring**: `reproduce-before-you-fix` lists `red suite` and an operator
writes "the suite is red". `log-rule-load.sh` (`InstructionsLoaded`) is the receipt for the other
half — `_routing-canary/README.md` § "Probe 2" is the end-to-end check, and the probe command was run
verbatim before it was written down.

Two things the tests earned rather than assumed:

- The RED was taken against a **stub that parsed the prompt and said nothing**, so it failed at five
  assertions rather than on a missing file. It then caught a real bug: with `CLAUDE_PROJECT_DIR`
  naming a tree that has no `.agents/rules/`, the hook fell through to its own ancestors and answered
  out of the lane it was installed in — a cross-tree read.
- Mutant 3 **survived the first cut of case D**, and that mattered. Deleting the no-closing-fence
  guard changed nothing, because that fixture's trigger list was mangled too and stayed silent either
  way — a vacuous pin. A second fixture (a good `triggers:` list, no closing fence) makes it bite.

**H (SCC-278).** `risk_seam.classify` had returned `unclassified` for every input since SCC-228 built
the seam; SCC-224 was to fill it and left it empty, so the Parity + Blast lens ran on nothing while
reading as though it had context. It now answers from the graph, and **both** code-review commands
print the tiers beside the overlap list.

The measured facts that shaped it:

- **`~/.local/bin` is not on `PATH`** in the shell this runs from — measured here, this session. The
  CLI is probed (`which` → pipx's dir), never named.
- Two fixture defects surfaced by cases that **failed against correct code**, each of which would
  have left a green test proving nothing: an `/usr/bin/env` shebang cannot resolve once the case
  under test empties `PATH`; and emptying `PATH` removes **git** too, so the "no CLI" case was
  passing because `git rev-parse` failed. It would have survived deleting the probe outright. Both
  now run on a git-only `PATH`.
- ⚠ **Test links are call-graph links.** `detect-changes` called all eight functions of
  `rule-trigger.py` untested while `test_rule_trigger.py` was exercising every one of them through
  `subprocess.run`. That is most of `.agents/scripts/tests/`, and "no test found" reads identically
  to "no test exists" — recorded in the contract doc, both review commands, and the SOP.

**Live, against the real installed tool:** `classify` prints `classified` on the fresh graph and
`unclassified` with the graph's own stamp rewritten. Nothing in git history was touched to prove it.

### The merge that absorbed SCC-269 / SCC-271 / SCC-279 turned my own gate red

Worth recording, because the defect was in the **test**, not the code, and the failure mode is
general. Case L is the live arm — it runs `classify` against the real installed tool so that a canned
fixture which has drifted from the tool's real output cannot hide. It skipped when the CLI or the
graph db was missing. It did **not** skip when the graph was merely **stale**.

A merge moves `HEAD`. `_graph_is_fresh` then reports `False`, `classify` correctly returns
`unclassified` — which is the behaviour cases E and F exist to pin — and case L called that a
failure. So `git merge origin/main` produced a red suite that said nothing true about the code, and
`code-review-graph update` made it green without a line changing.

Fixed by making the precondition what it should always have been: not *"is the tool installed"* but
*"can the tool answer"* — CLI present, db present, **and db at `HEAD`**. A stale graph now states
`L SKIPPED` with the reason and the command that clears it.

Proven both ways rather than asserted: **fresh → 24/24** with the live arm running;
**stale → 23/23** with the live arm skipping. Mutant **M1** (delete the `and fresh` guard) **dies** —
it fires the live arm against a stale graph and fails, which is exactly the bug. The graph's stamp
was rewritten in place and restored, so no lane history was touched to prove it.

review-runtime: inline (blocked: standing session directive — "Do not call the AgentTool unless the user requested it". The operator approved the SCC-270 plan, which names this command as the next step; they did not separately authorise a subagent fan-out, and the directive names that tool specifically. Recorded here rather than laundered into a clean-looking `inline`.)

## Code Review (2026-08-22)

Verdict: CONCERNS @ 1133ebbc3a4acb5fe07374cd05001fdf26aed3ad
Suite evidence measured at the same sha: 1133ebbc3a4acb5fe07374cd05001fdf26aed3ad

lenses_run:
- edge-case-hunter · recovered-inline — inline runtime; ran sequentially in this context
- literal-correctness-hunter · recovered-inline — inline runtime; ran sequentially in this context
- acceptance-auditor · recovered-inline — inline runtime; ran sequentially in this context
- test-adequacy-auditor · recovered-inline — inline runtime; ran sequentially in this context
lenses_counted:  4/4
lenses_na:
- blind-hunter · n/a — context contaminated (this context built the lane and holds the plan, the walkthrough and every part's reasoning). DROPPED rather than faked, per the engine's § When the order CANNOT protect it.

dispositions:    per-lens: edge-case-hunter=1/2/0 · literal-correctness-hunter=1/8/0 · acceptance-auditor=1/0/0 · test-adequacy-auditor=1/2/0
drift:           undeclared=7 · unimplemented=1 · incomplete=0 — dispositions in the findings table below; every row named, none cut

**Scope.** 120 files, `origin/main...HEAD`, re-taken after Step 0.7 absorbed `origin/main` at `db75f19`.
**Method.** Four lenses inline over the diff; every path and `#L` anchor in the 79 changed markdown
files resolved mechanically; the declared change set reconciled with `declared_change_set.py`; the
acceptance list recovered from `acli jira workitem view SCC-270` and matched item-by-item to a
command that proves it.

**Why CONCERNS and not PASS.** Every gate is green and every acceptance item is evidenced. The floor
is raised by **one review layer that never ran**: the Blind Hunter was dropped, and this whole review
ran in the context that built the lane. That is the honest severity for a self-review — the findings
below are real and were caught, but nobody independent looked.

### Findings

| # | file:line | Severity | Failure scenario | Disposition |
|---|---|---|---|---|
| 1 | `.agents/scripts/risk_seam.py` — the `untested` field | **important** | `classify` reported 11 untested functions for `risk_seam.py`, 8 for `rule-trigger.py`, 3 for `check_maps.py` — **all of them thoroughly tested**. The graph holds 24 `TESTED_BY` edges and not one names a subject under test (21 point at builtins like `str`/`Path`/`mkdir`, 3 at a test class's own `assertEqual`). A reviewer trusting the column opens a dozen files for nothing, or worse, files "no test" findings against tested code. | **applied @ `b7659a2`** — `classify` now publishes `test_links`; all four consuming commands, the contract doc, the scripts INDEX and the SOP tell the reader to check it first. RED first (4 assertions), 4/4 mutants dead. |
| 2 | `.claude/rules/sop-currency.md:91` | **important** | This lane **creates** `.claude/rules/` — six generated copies, and the copy is what Claude Code loads. `.agents/rules/` holds all 25 rules; the mirror holds only the 6 path-scoped ones, so `[project-law.md](project-law.md)` resolved beside the master and pointed at nothing beside the copy. An agent following the pointer opens nothing and is told nothing. | **applied @ `1133ebb`** — master link is now `../../.agents/rules/project-law.md`, which resolves from both folders (both sit two levels below the root). `test_rule_frontmatter.py` pins it; the re-introduction mutant dies. |
| 3 | `.agents/commands/sentry-security-team-avch.md:45` | suggestion | Read "code-graph enrichment when available" — the tool is un-named, so an agent knows to reach for something but not what to call. Acceptance 5 asks these surfaces to **cite** the tool. | **applied @ `1133ebb`** |
| 4 | `.agents/scripts/generate_doc_graph.py:38` · `record_map_changes.py:43` | dismissed | Suspected the same replace-don't-add bug as the `.gitignore` one: `.gitnexus` was **replaced** by `.code-review-graph` in both skip lists rather than added beside it, so a still-present `.gitnexus/` would be walked. | **dismissed — verified, not assumed.** Both auto-skip every dot-directory anyway (`generate_doc_graph.py:78` `not d.startswith(".")`, `record_map_changes.py:99` `or head.startswith(".")`), and the latter is fed by `git diff --name-status`, which never reports gitignored paths. Triple-covered; the entries are decorative in both. |
| 5 | `docs/_scc_sops_prds/tea_deep_reference.md:786-791` + 2 others | dismissed (relevance) | Six links into `Projects/AGY_AVIATIONCHAT/backend/tests/…` did not resolve, plus two `relative/path` placeholders. | **dismissed** — worktree false positive: `Projects/` is gitignored and absent from a worktree; all six resolve in the shared checkout, verified. None on a line this diff added. The placeholders are prose examples. |
| 6 | `.agents/hooks/log-rule-load.sh` | suggestion | New in this lane, no `test_log_rule_load.py`. | **dismissed** — a six-line diagnostic logger, not a gate. It was exercised live and verified by reading the log **file** rather than `$?`, and `_routing-canary/README.md` § Probe 2 carries the command. A test asserting a logger logs would restate the code. |

**Also caught during the review, in this lane's own earlier commits** (fixed, and each recorded in
its own commit): `.claude/mcp.json` is a third tracked MCP config in **both** repos and Part B
updated only `.mcp.json`; and in the AGY twin, `.gitignore` **replaced** `.gitnexus/` instead of
adding beside it, which would have surfaced the still-live TIA index as untracked.

⚠ **A process finding worth more than any of the above.** The first attempt at finding 3 edited
`.agents/workflows/sentry-security-team-avch.md` — a **generated** mirror of `.agents/commands/`.
`sync-agents` silently reverted it on the next run and the edit vanished with no error. Re-reading
the file after the sync is the only reason it was caught. The sync banner says "edit the master,
never the copies"; this is what ignoring it looks like from the inside.

### Step 0.7 — re-derivation

1. **Did anything this diff references move, rename or get deleted on `main`?** No. `main` advanced
   14 commits during this lane (SCC-186, SCC-269, SCC-271, SCC-279); all were absorbed at `db75f19`,
   after which `merge-base HEAD origin/main` **equals** `origin/main` and `theirs` is empty. Every
   path and `#L` anchor in the 79 changed markdown files was re-resolved mechanically: 9 unresolved,
   **0** of them on a line this diff added, and all 9 explained in findings 5.
2. **True overlap and merge result.** Overlap is **zero files**. `git merge-tree --write-tree
   --messages HEAD origin/main` returns a bare tree sha (`e2df6ce`) with no conflict messages.
   ⚠ The absorb was not free: it turned `test_risk_seam.py` red, because case L treated a stale
   graph — the normal state right after any merge — as a failure rather than a precondition. Fixed
   at `68c3c7f`, proven both ways (fresh 24/24 with the live arm running, stale 23/23 with it
   skipping), mutant dead.
3. **Sibling lanes and landing order.** One other live worktree: `SCC-280-teaching-edition` on
   `claude/teaching-edition` @ `3cdb130`. **No landing-order dependency either way** — zero file
   overlap, and this lane touches no surface that lane is building on. The AGY twin **AVCH-73** is a
   different repo with its own key and gate; it is already committed and pushed on its own lane and
   neither blocks the other.

### Acceptance matrix

| # | Item | Proving assertion | Result |
|---|---|---|---|
| 1 | Bake-off evidence, both repos | lobby walkthrough § Part A; AGY walkthrough § Bake-off — `callers_of calculate_cognitive_zone` = 5 (1 production, 4 tests); `detect-changes` 1918 files on a bad base vs 18 on the merge-base | **met** |
| 2 | `gitnexus` in no tracked lobby file outside history | `git grep -Iln -i gitnexus` minus `_artifacts`/`_my_resources`/`_bmad*` → **2 hits**, both *historical narrative* (`risk_seam.py:6` "SCC-224 was meant to fill it with GitNexus", `docs/code-review-graph.md:58` naming the engine it replaced) | **met in intent, not literally** — no live dependency remains; the two survivors describe the past. Named here rather than claimed clean. |
| 3 | MCP + ignore files | all three configs list `code-review-graph`; `git check-ignore .code-review-graph/` exit 0; `.gitnexusignore`/`.gitnexusrc` absent; `.code-review-graphignore` present | **met** (acceptance named two configs; three were updated) |
| 4 | check 9 reads SQLite, no CLI dep | `check_maps.py:569-573` `sqlite3.connect(...mode=ro)` reading `metadata.git_head_sha`; `test_check_maps_graph_fresh.py` **5/5**; `run_all` **52/52** | **met** |
| 5 | Five surfaces re-cited, one house skill, lint green, SOP same commit | `cicd-code-review` · `cicd-self-audit` · `cicd-clean-code-audit` · `smh-update-maps-indexes` · `sentry-security-team-avch` all cite `code-review-graph`, all zero `gitnexus`; `.agents/skills/code-review-graph/SKILL.md` is the single door, no `gitnexus*` skill remains; `workflow_lint` **0 errors**; SOP staged in every usage-surface commit (the gate rejected one attempt and was satisfied, never `[sop-ok]`'d) | **met** |
| 6 | Rule frontmatter mirrors INDEX, test asserts it, `.claude/rules/` emitted | `test_rule_frontmatter.py` **10/10**, including the new dangling-link guard; `.claude/rules/` = 6 files = exactly the path-scoped masters | **met** |
| 7 | `rule-trigger.py` hook registered + RED→GREEN test + canary probe | `.claude/settings.json` carries `UserPromptSubmit` → `run-hook.sh .claude/hooks/rule-trigger.py` and `InstructionsLoaded` → `log-rule-load.sh`; `test_rule_trigger.py` **18/18**, taken RED against a stub (5 failures) first; `_routing-canary/README.md` § Probe 2 present, both commands run before being written down | **met** |
| 8 | `risk_seam` classified/unclassified, `gates_audit` False, both Step 0.7 twins print tiers | `test_risk_seam.py` **27/27** (28 when the graph is fresh; case L skips when stale, by design); both `smh-` and `cicd-code-review` carry the `risk_seam.py classify` line | **met** — ⚠ the acceptance text says `detect-changes --json`; **there is no such flag**. The full JSON is the default output and `--brief` replaces it. Implementation is correct; the acceptance wording is stale. |

**Declared-set reconciliation.** `undeclared=7 · unimplemented=1 · incomplete=0`, block present. Every
row named, none cut:

- `.agents/.sync-manifest.json`, `.claude/hooks/INDEX.md`, `.claude/skills/INDEX.md`,
  `.opencode/commands/smh-self-audit.md` — **stay**: generated output of declared actions.
- `.agents/commands/smh-self-audit.md` — **stays**: a `risk_seam` consumer, and Part H's contract is
  that consumers cite the new engine. Should have been declared; the plan named its three siblings.
- `.claude/mcp.json` — **stays**: found *by* this review. A file the plan could not have declared
  because the gap is what the review discovered.
- `.agents/scripts/tests/test_check_maps_graph_fresh.py` (undeclared) pairs with
  `.agents/scripts/tests/test_check_maps.py` (unimplemented) — the plan declared the check-9 test
  would extend the existing file; it landed as a dedicated new one instead. **Stays**: the behaviour
  is tested either way, and a 5-case file for one check reads better than a graft. Plan overreach on
  the filename, not dropped scope.

### Gates

| Gate | Command | Result |
|---|---|---|
| Enforcement suite | `python3 .agents/scripts/tests/run_all.py` | **52/52 files passed**, exit **0** — run bare |
| Toolkit lint | `python3 .agents/scripts/workflow_lint.py --toolkit-only` | `-- 0 error(s), 0 warning(s), 8 info --`, exit **0** (the 8 are pre-existing UTF-8 BOMs on vendor `testarch-*` files) |
| Assertion evidence | `test_risk_seam.py` · `test_rule_trigger.py` · `test_rule_frontmatter.py` · `test_check_maps_graph_fresh.py` | 27/27 · 18/18 · 10/10 · 5/5 — all GREEN now, each taken RED at an assertion first |
| SOP currency | `sop_currency.py --paths <changed> --message …` | exit **0**. It **rejected** one commit this session and was satisfied by updating the SOP — never `[sop-ok]`'d |
| Link + anchor | every markdown link in the 79 changed `.md` files, resolved relative to its own file | 9 unresolved, **0** introduced by this diff — see finding 5 |
| Door parity | `git diff --name-status … -- .agents/commands/` | no command added or renamed — parity not at risk |
| Map drift | `check_maps.py --depth3-only --strict` | exit **0** |
| Compile | `py_compile` on every changed `.py` | clean |

### Clean-Code Gate

Machine floor imported from the table above (SCC-146: nested, the audit does not re-run what Step 3
already ran). Ran only what Step 3 did not:

| Check | Result |
|---|---|
| `py_compile`, all changed `.py` | clean |
| Comment contract (§2A) — every ⛔ block names the scar it prevents | **pass**; the two new ones (`_test_link_count`, case M) both carry the measured numbers that caused them |
| Convention table (§2C) — probe the binary, never name it; explicit-path commits; stdlib only | **pass**; `_test_link_count` opens the db read-only via stdlib `sqlite3` and returns 0 on any failure, matching `_graph_is_fresh` beside it |
| Drift / bloat | imported from Step 1 — findings 1–3 applied, 4–6 dismissed with reasons |
| Legacy debt in untouched files | the 8 BOM infos on vendor `testarch-*` files: noted, not gated on, not this diff's |

**Changes applied during review:** findings 1, 2 and 3, at `b7659a2` and `1133ebb`.

## Your Actions

- [x] **The merge itself — lands via this branch's PR.** Number-free on purpose: the PR number is
  assigned after this commit is pushed, so the number and the merge sha go on the ticket at Step 4.

- [ ] **Set up both machines.** Until this is done the swap is landed in git but not live for you —
  the repo points at a tool neither machine has. On **each** machine: `pipx install code-review-graph`,
  then add the absolute-path override in `~/.claude.json` under `projects["<repo path>"].mcpServers`.
  The tracked `.mcp.json` names the command portably, which is right for a terminal and **not** enough
  for a Dock-launched editor — `launchctl getenv PATH` is unset, so the editor hands its children a
  stripped `PATH` with no `~/.local/bin`, the server never starts, and the session simply has no graph
  tools with no error. The Windows PC also needs `PYTHONUTF8=1` and `fastmcp >= 3.2.4`. Then retire the
  old engine: `npm rm -g gitnexus`, delete `~/.gitnexus/` and each repo's `.gitnexus/`, and drop the
  `gitnexus` entries from `~/.claude.json`'s per-project `mcpServers`. Recipes: `docs/code-review-graph.md`.

**⛔ ONE EXCEPTION to the uninstall — the machine that runs the AviationChat TIA gate.** Found by the
AGY twin (AVCH-73) while doing the same swap there: GitNexus is **live code** in that repo, not a stale
doc reference. `Projects/AGY_AVIATIONCHAT/backend/tia/gate.py:68` shells out to
`node .gitnexus/run.cjs status` and parses its output; `select.py:64` refuses to select tests when that
index is not at `HEAD`; `scripts/tia_gate.ps1` drives both. Removing GitNexus does not degrade that gate
— a missing index reads as `STALE_INDEX`, trips the `RUN_ALL` fail-safe, and the "fast" pre-push gate
silently becomes a full-suite run every time, with nothing saying why. AVCH-73's scope excluded
`backend/`, so the port is **AVCH-77** under the AGY CI/CD epic AVCH-43, which also adds the macOS entry
point that gate has never had — `tia_gate.ps1:27` and `gate.py:132,141` all hardcode
`backend/.venv/Scripts/python.exe`, so on a Mac it cannot dispatch a single test today. Everywhere else,
GitNexus can go.

### Rulings made at close-out (2026-08-22) — nothing owed here, recorded so the record is true

**The independent-review question is answered, and the answer was that the question was wrong.** This
lane's review ran `inline` because the agent read the session directive *"do not call the Agent tool
unless the user requested it"* as forbidding the Blind Hunter fan-out. The operator's ruling, verbatim:
*"we already fixed this with explicite instruction that the /command is the user calling for the sub
agents."* **Invoking `/smh-code-review` IS the operator asking for its lenses** — the directive governs
unprompted fan-outs, never the ones a command body specifies. The verdict stays **CONCERNS** because
that is the honest record of what actually ran; it is not re-run, and the lane lands on the operator's
word.

**Follow-on, deliberately NOT ticketed here.** The operator's call was *"we are coming back to this…
that is a huge bug we have to brain storm and fix"* — a brainstorm, not a defined fix, so minting a key
now would invent scope. The defect is durable regardless: it is carried as a `--followon` on this
ticket's Dev Record and as a flight-event fingerprint (non-PASS verdict), both of which outlive this
lane. The shape worth fixing: a session-level directive silently outranked a command body, and the only
symptom was a verdict one floor lower than it should have been.

**The manifest keeps `secondary_repos: []`, and that is a decision rather than an omission.** AVCH-73 is
this task's second-repo half and closes through its own lane. Declaring it here would have verified the
wrong tree: `task_preflight.py` resolves a secondary to the **submodule root** and reads *its* `HEAD`
(`main`), so it structurally cannot see `chore/AVCH-73-code-review-graph-swap`, which lives in a
worktree of that submodule — and it would have hard-errored on another session's untracked
`_artifacts/epic_23/` sitting in AGY's shared checkout. AVCH-73's own preflight reads its lane directly
and is the stronger check. Worth knowing generally: since SCC-62 every commit-producing lane runs in a
worktree, so this blind spot applies to **any** cross-repo secondary half.
