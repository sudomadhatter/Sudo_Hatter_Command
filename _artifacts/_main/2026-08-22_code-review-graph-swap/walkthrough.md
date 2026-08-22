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
- [ ] Part G · AVCH-73 — AviationChat, its own repo and lane

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
| `run_all.py` | after D, E, F, H | **51/51 files** (was 49; E and F each add one) |
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

## Your Actions

1. **Nothing yet.** GitNexus stays installed and registered until the lane lands — Part A only added
   the new CLI beside it.
2. **After the lane lands**, on **each** machine: `npm rm -g gitnexus`, delete `~/.gitnexus/` and each
   repo's `.gitnexus/`, and remove the `gitnexus` entries from `~/.claude.json`'s per-project
   `mcpServers`. The Windows PC also needs `pipx install code-review-graph`, `PYTHONUTF8=1`, and its
   own `~/.claude.json` override — `docs/code-review-graph.md` (Part C) will carry both recipes.
