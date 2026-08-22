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
- [ ] Part B · SCC-273 — lobby MCP, ignore and scope files
- [ ] Part C · SCC-274 — docs + the one house skill
- [ ] Part D · SCC-275 — commands, scripts, check 9, tests, SOP
- [ ] Part E · SCC-276 — rules activation frontmatter + generated `.claude/rules/`
- [ ] Part F · SCC-277 — rule-trigger hook + routing-canary probe
- [ ] Part H · SCC-278 — risk_seam classifier so the review loop reads the graph by default
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
| `run_all.py` | Part D and at the tip | not yet run |
| `workflow_lint.py --toolkit-only` | Part D and at the tip | not yet run |
| `check_maps.py` | Part D | not yet run |
| `gate_receipt.py` | at the tip, once | not yet run |

## Your Actions

1. **Nothing yet.** GitNexus stays installed and registered until the lane lands — Part A only added
   the new CLI beside it.
2. **After the lane lands**, on **each** machine: `npm rm -g gitnexus`, delete `~/.gitnexus/` and each
   repo's `.gitnexus/`, and remove the `gitnexus` entries from `~/.claude.json`'s per-project
   `mcpServers`. The Windows PC also needs `pipx install code-review-graph`, `PYTHONUTF8=1`, and its
   own `~/.claude.json` override — `docs/code-review-graph.md` (Part C) will carry both recipes.
