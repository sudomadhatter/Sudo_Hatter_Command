---
IsArtifact: true
ArtifactMetadata:
  title: Replace GitNexus with code-review-graph and wire rules/skills activation into the routing system
  type: implementation_plan
  date: 2026-08-22
  ticket: SCC-270
  twin: AVCH-73
  lane: chore/SCC-270-code-review-graph-swap
---

# SCC-270 — code-review-graph swap + rules/skills activation layer

**Mode: CONSOLIDATED** — one lane (`chore/SCC-270-code-review-graph-swap`), one plan with six part
sections, every part a rider under SCC-270 keyed per commit. Why: same repo, same lane class (toolkit
config/docs/scripts/rules), and the parts share files (`AGENTS.md`, `.agents/rules/*`, the SOP), so
they are sequenced, not parallel. The AviationChat half cannot ride this lane — its commit gate
answers only to `AVCH` — so it is **AVCH-73**, a separate lane in that repo, planned here as Part G
and closed by its own `/smh-close-task-merge-tree --expect-key AVCH-73`.

## 1. Goal

Two things the operator asked for on 2026-08-22, in order of weight:

1. **The code-graph tool that helps most with code reviews and self-audits**, on a license a paid
   product can use. GitNexus is PolyForm-Noncommercial; `code-review-graph` (MIT, v2.3.8) is built for
   the review loop — `detect_changes_tool` (diff → risk-scored functions, affected flows, test gaps,
   review questions, with `base=<ref>`), `get_review_context_tool`, `get_impact_radius_tool`,
   `get_affected_flows_tool`, `get_knowledge_gaps_tool`, hub/bridge nodes — and indexes `git ls-files`,
   so the `.agents/` toolkit that GitNexus could not see becomes graph nodes.
2. **Something that makes the agent better at using the rules and skills, fitting the folder-as-
   workspace routing system.** No product does this without imposing its own schema (`base` was
   evaluated and rejected — same noncommercial license, hook-only, rewrites `~/.claude/CLAUDE.md`).
   The native mechanisms fit the three-layer plan exactly: Claude Code loads a `.claude/rules/*.md`
   file only when a file matching its `paths:` is read; Antigravity now reads **`.agents/rules/`** —
   the master dir — with per-file `trigger:` activation; intent-shaped triggers ("something is
   broken", "the board comes up") get one small `UserPromptSubmit` hook that reads the rule
   frontmatter and injects a one-line pointer.

Background: evaluation record in `_artifacts/_memory/base-is-not-a-gitnexus-replacement.md`
(written this session; moved onto this lane per AGENTS.md §7). GitNexus footprint measured at
39 tracked lobby files + 6 skill docs in AGY; every toolkit dependency on it is already soft
(`check_maps` check 9 is a non-fatal nag; the audit commands say "if indexed").

## 2. Decisions and trade-offs (read these; the file list below follows from them)

1. **We do not run `code-review-graph install` against the repos.** Its installer appends a
   `<!-- code-review-graph MCP tools -->` section to `CLAUDE.md`, `AGENTS.md` and `GEMINI.md`, writes
   hooks into `.claude/settings.json`, and generates four skills into `.claude/skills/`. The adapter
   law (one-line `CLAUDE.md`, `AGENTS.md` the single brain, one door per platform) forbids all three.
   We hand-write the MCP entries and author ONE house skill in `.agents/skills/code-review-graph/`
   that the sync carries to `.claude/skills/`. The CLI (`pipx install code-review-graph`) is the only
   thing installed, per machine.
2. **The tracked `.mcp.json` carries the portable form** `{"command":"code-review-graph","args":["serve"]}`.
   Machine quirks stay machine-local exactly as they did for GitNexus: a local-scope
   `~/.claude.json` override on the Mac (GUI-launched editors have a stripped `PATH`) and the `.exe`
   path + `PYTHONUTF8=1` on the PC, both documented in `docs/code-review-graph.md`.
3. **Freshness check 9 reads the graph's own metadata** — `.code-review-graph/graph.db`, table
   `metadata`, key `git_head_sha` — with stdlib `sqlite3`. No CLI on `PATH` is required for the lint,
   and the hint is still non-fatal. The per-worktree DB is gitignored (`.code-review-graph/`).
4. **Rule frontmatter is activation metadata that MIRRORS `rules/INDEX.md`'s Load column; the
   INDEX stays the classification.** AGENTS.md §3 says a rule's frontmatter does not declare its
   load class — that sentence becomes "…does not *decide* it: `trigger:`/`paths:` mirror the INDEX
   and `test_rule_frontmatter.py` fails when they disagree." Floor → `trigger: always_on`; protocol →
   `trigger: model_decision` (their law is inline in AGENTS.md; loading 44 KB on every read-only
   session is what the tier exists to avoid); path-shaped on-demand → `paths:` + `trigger: glob` /
   `globs:`; intent-shaped on-demand → `trigger: model_decision` + `triggers:` keyword list.
5. **`.claude/rules/` holds generated copies, not symlinks.** Claude Code accepts symlinks, but a
   Windows checkout without Developer Mode turns a symlink into a text file containing a path — the
   rule would load as one line of garbage. `/smh-sync-agents` emits the path-scoped rules the same
   way it already emits `.claude/skills/`.
6. **The trigger hook never blocks and prints at most three pointers.** It reads `triggers:` from
   the on-demand rules' frontmatter, matches whole words in the prompt (case-insensitive), prints
   `⛔ trigger fired → read .agents/rules/<name>.md (<why>)`, exits 0 on any error (fail-open, like
   every hook here). Reach this ticket: Claude Code on both machines (hook) + Antigravity (native
   triggers). Codex hooks are experimental, off by default and absent on Windows; opencode needs a
   JS plugin — neither is built here, and the SOP says so.
7. **Part A is a tripwire.** If `code-review-graph`'s blast radius on `calculate_cognitive_zone`
   misses callers GitNexus names, or `detect-changes` misses files on the same diff, the lane stops
   at Part A with the evidence, lands as `landing_mode: partial` (riders trimmed to A), and the
   remainder is re-planned — the fallback candidate is `codebase-memory-mcp` (memory file above).
8. **Every part's commit that touches a usage surface stages the SOP in that SAME commit** — ⚠️
   **AUDIT FINDING F2 baked.** `sop_currency.py` `_SURFACES` (armed) fires on `.agents/commands/`,
   `.agents/rules/`, `.agents/scripts/*.py|*.ps1`, `.githooks/` and root `AGENTS.md`. That is Part C
   (`AGENTS.md`), Part D, Part E (`.agents/rules/*` + `sync-agents.ps1`) and Part H (`risk_seam.py`):
   each of those commits also stages `docs/_scc_sops_prds/workflows_testing_SOP.md` + its changelog
   line. Part F's `.agents/hooks/` is not a gated surface, but hook reach is usage, so its SOP line
   rides Part F's commit too. `[sop-ok]` is not used anywhere in this lane.
9. **Out of scope, on purpose:** AGY's `.github/claude/incident-triage.md` (a `.github/` path —
   `/cicd-push-e2e` territory); any change to which rules exist or what they say; Gemini CLI /
   Codex / opencode wiring; uninstalling GitNexus from the machines before Part A passes (a
   `## Your Actions` item in the walkthrough).

## 3. The parts (each a rider; build order = this order)

### Part A — Bake-off + both-machine install recipe (acceptance 1)
1. `brew install pipx && pipx ensurepath && pipx install code-review-graph` on this Mac — ⚠️ **AUDIT
   FINDING F5 baked:** `pipx` is absent today (`command -v pipx` → nothing). The console script lands
   in `~/.local/bin`, which a GUI-launched editor's stripped `PATH` does not see, so the Mac's
   `~/.claude.json` local override names `/Users/<you>/.local/bin/code-review-graph` (decision 2).
   PC later: `python -m pip install --user pipx && python -m pipx ensurepath && pipx install
   code-review-graph`, `PYTHONUTF8=1`, fastmcp ≥ 3.2.4 per its README.
2. Build both graphs — lobby and `Projects/AGY_AVIATIONCHAT` — with `code-review-graph build`;
   record `code-review-graph status --json` for each (files, nodes, edges, `built_at_commit`, wall time).
3. Compare against GitNexus on the same questions, AGY: `impact calculate_cognitive_zone` vs
   `impact({target:"calculate_cognitive_zone",direction:"upstream",repo:"AGY_AVIATIONCHAT"})` (known
   HIGH, 7 upstream callers); `detect-changes --base main` on the most recent landed story diff vs
   `detect_changes({scope:"compare",base_ref:"main"})`. Lobby: `query` on `check_maps.py` callers.
4. MCP smoke without a session: `initialize` + `tools/list` piped into `code-review-graph serve` via
   `perl -e 'alarm(40); exec …'` (no `timeout` binary on macOS) — expect 30 tools.
**Assertion that proves it:** `walkthrough.md` `## Evidence` carries both tools' outputs side by side
and the pass/fail line from decision 7. This part commits only artifacts + the memory move.

### Part B — Lobby MCP, ignore and scope files (acceptance 2, 3)
`.mcp.json` and `.antigravity/mcp.json` replace the `gitnexus` entry with `code-review-graph serve`
(`md-feedback` untouched); `.gitignore` drops `**/.gitnexus/` and adds `.code-review-graph/`;
`.gitnexusignore` and `.gitnexusrc` are deleted; `.code-review-graphignore` scopes the lobby index
to the manager surface (excludes `_artifacts/`, `_my_resources/`, `_bmad/`, `_bmad-output/`,
`_routing-canary/`, and the sync mirrors `.claude/`, `.opencode/`, `.agent/`, `.antigravity/` —
indexing them would duplicate every toolkit symbol 3–4×; `Projects/` needs no line because
`git ls-files` lists submodules as gitlinks, not files).
**Assertion:** `python3 -c "import json;d=json.load(open('.mcp.json'));assert d['mcpServers']['code-review-graph']['args']==['serve']"`
and `code-review-graph status --json` after a rebuild shows `.agents/scripts/*.py` indexed and zero
`_artifacts/` paths.

### Part C — Docs + the house skill (acceptance 2, 5)
`docs/gitnexus.md` → `docs/code-review-graph.md`: the house contract (before editing a symbol:
`get_impact_radius_tool` + `get_review_context_tool`; before every commit: `detect_changes_tool` with
`base=<the branch you will land on>`; warn on HIGH risk; `query_graph_tool` pattern `tests_for`
before claiming coverage), the tool table, freshness (`status`, `update`, `watch`), the both-machine
install recipe and the local MCP override note from decision 2. `AGENTS.md` §8 pointer block,
`.agents/INDEX.md` line 19–20, `.agents/skills/workspace-structure/SKILL.md` 27–28,
`docs/repo-map.md` header 40–59 and `docs/workspace-standard.md` 175 are re-pointed. The six
`.agents/.claude/skills/gitnexus/*/SKILL.md` are deleted; ONE hand-authored
`.agents/skills/code-review-graph/SKILL.md` (explore · impact · review · refactor · debug, condensed
from upstream's seven, written against the house contract) is the single master, synced to
`.claude/skills/`. `.agents/skills/INDEX.md` gets it in the Code-quality-gates family.
⚠️ **AUDIT FINDING F1/F6 baked — acceptance 2 reaches further than the first draft declared.** The
six `.claude/skills/gitnexus/*/SKILL.md` copies are TRACKED and were never sync-managed (the manifest
purge cannot remove them) — they are `git rm`'d explicitly. The toolkit's own `.agents/AGENTS.md:43`
comment, `docs/AGENTS.md:31`, the four SOP/PRD docs that describe the graph (`docs/_scc_sops_prds/INDEX.md:11`,
`file_folder_structure+maintaining.md` 59/83/87/214/233/383/397 — the check-9 diagram, the MCP-servers
table and the "after committing" row — `tea_deep_reference.md:123`, `tea_testing_guide.md`
156/203/498/523, a TIA design that named GitNexus `impact()` as its engine: reworded to
`detect_changes_tool`, design unchanged), the new-machine guide (`docs/migrations/INDEX.md` 7/78 and
`install_guides/new_machine-migration-guide.md` §326–345 — the GitNexus install block becomes the home
of decision 2's both-machine recipe), `test_sops_prds_folder.py:9` (docstring), and the generated
`docs/doc-graph.md` + `doc-graph.json` (re-run `generate_doc_graph.py`) are all in the Declared Change
Set below. `/smh-sync-agents` runs INSIDE Part C so `test_command_surfaces.py`'s door-parity check sees
the new master's `.claude/skills/` copy.
⚠️ **AUDIT FINDING F3 baked — sibling lane:** `docs/workspace-standard.md` is also changed by the
in-flight SCC-269 lane (`chore/SCC-269-workspace-standard-reconcile`). **SCC-269 lands first**; Part C
absorbs `origin/main` before touching the file and re-greps `gitnexus` in it rather than trusting line
175. If SCC-269 has not landed, the edit is one line and the merge conflict is trivial — but it is
named here so nobody is surprised.
**Assertion:** acceptance 2's grep is empty; `ls .claude/skills/code-review-graph/SKILL.md` after
`/smh-sync-agents`.

### Part D — Commands, scripts, check 9, tests, SOP (acceptance 4, 5)
Commands: `cicd-self-audit.md` (lines 11, 143, 149: "GitNexus, gated on `list_repos`" → "code-review-
graph, gated on `code-review-graph status --json` exit 0"), `cicd-clean-code-audit.md` (156:
`context({name})` → `query_graph_tool` callers), `smh-update-maps-indexes.md` (14, 51, 106–107, 407,
481–484, 517: check 9 wording + the re-index hand-off becomes `code-review-graph update`),
`sentry-security-team-avch.md` + its Antigravity mirror in `.agents/workflows/` and the
`workflows/INDEX.md` row. Scripts: `check_maps.py` check 9 per decision 3 (+ `.code-review-graph` in
the dot-cache ignore list), `record_map_changes.py` ignore list, `generate_doc_graph.py` /
`evidence_extract.py` / `risk_seam.py` docstrings (the "do not deduplicate into the graph" reasoning
stays — it is about machine-local indexes, which is still true), `scripts/INDEX.md` line 31. Tests:
`test_check_maps.py` gains a fixture DB with a `metadata(git_head_sha)` row (RED before the script
change), `test_evidence_extract.py` 1404 asserts the new docstring, `test_command_surfaces.py` 1830
ignore set. SOP: §6 ③ and §9 name the review tools; §5's check-9 line; changelog one line.
Opencode mirrors regenerate via `/smh-sync-agents`.
**Assertion:** `run_all.py` green; `workflow_lint.py --toolkit-only` green; `check_maps.py` prints
`[code-review-graph index]` with the built-at commit.

### Part E — Rules activation frontmatter + generated `.claude/rules/` (acceptance 6)
All 25 masters in `.agents/rules/` get frontmatter per decision 4 (the three floor rules
`always_on`; the four protocol rules `model_decision`; path-shaped on-demand rules get `paths:` +
`trigger: glob` + `globs:`: `code-standards` → `**/*.py`, `**/*.{ts,tsx}`; `dependency-awareness` →
`**/package.json`, `**/requirements*.txt`, `**/pyproject.toml`; `powershell-encoding-safety` →
`**/*.ps1`; `tests-must-gate-for-real` → `**/tests/**`, `**/*.test.*`, `**/*.feature`;
`living-template-sync` → `AGENTS.md`, `.agents/templates/**`, `_bmad/custom/**`; `sop-currency` →
`.agents/commands/**`, `.agents/rules/**`, `.agents/scripts/**`, `.githooks/**`; the rest
`model_decision` + `triggers:`). `rules/INDEX.md` "How rules load" states the mirror contract;
`AGENTS.md` §3 sentence per decision 4. `sync-agents.ps1` emits `.claude/rules/<name>.md` for every
master carrying `paths:` (verbatim copy, stale ones pruned). NEW `test_rule_frontmatter.py`: every
rule's `trigger` agrees with the INDEX Load column, every `paths:` rule is on-demand, every intent
rule carries `triggers:` — seen RED before the frontmatter lands.
**Assertion:** the test; `pwsh .agents/scripts/sync-agents.ps1 -WhatIf` lists six `.claude/rules/`
emits; in a fresh session, reading any `.ps1` shows `powershell-encoding-safety` under `/context`
Memory files.

### Part F — Rule-trigger hook + routing-canary probe (acceptance 7)
NEW `.agents/hooks/rule-trigger.py` (stdlib, `python3 → python` via the existing `run-hook.sh`),
registered as `UserPromptSubmit` in `.claude/settings.json`; NEW `test_rule_trigger.py` (prompt
"the suite is red" → pointer to `reproduce-before-you-fix`; "what's in progress on jira" → `jira`;
"write me a poem" → nothing; a malformed rule file → exit 0 and nothing) seen RED first. NEW
`.agents/hooks/log-rule-load.sh`, an `InstructionsLoaded` hook (matcher `path_glob_match`) that
appends `file_path` to `${TMPDIR:-/tmp}/claude-rule-loads.log`; `_routing-canary/README.md` gains
the rule-activation probe: read a `.ps1`, then `cat` the log — the canary now proves routing AND
activation. `.agents/hooks/INDEX.md` lists both; `.claude/hooks/` mirrors come from the sync.
**Assertion:** the test; the probe's log line after one fresh session.

### Part H — Feed the graph into the review loop's risk seam (acceptance 8 — operator confirms at the stop)
**Why this part exists:** the operator asked for *the one that helps the most with code reviews and
self audits*. Today `/smh-code-review` Step 0.7 and `/smh-self-audit` Lens 2 take their blast radius
from `evidence_extract.py` and from `risk_seam.py classify`, which is a **placeholder** (returns
`unclassified` for every input — SCC-228 built the seam, SCC-224 was to fill it with GitNexus and left
it empty). Without this part, the new graph is an enrichment the agent may call — exactly GitNexus's
posture. With it, the review loop reads the graph by default.
1. `risk_seam.py classify(paths)` shells to `code-review-graph detect-changes --json` (stdlib
   `subprocess`, never imports the package) when `.code-review-graph/graph.db` exists and its
   `git_head_sha` equals `HEAD`; returns `{"status":"classified","tiers":{path: {risk, flows,
   untested}}}`. Any other state — no CLI, no DB, stale DB, non-zero exit — returns the fixed
   `unclassified` shape. **The pure-Python path stays the normal one** (operator ruling 2026-08-19).
2. `gates_audit()` stays `False` for every return; `test_risk_seam.py` keeps that pin and gains the
   fresh/stale/absent cases (seen RED first).
3. `/smh-code-review` Step 0.7 prints the tiers beside the overlap list; `/cicd-code-review` gets the
   same lines in its twin step (twins drift otherwise).
**Assertion:** `python3 .agents/scripts/risk_seam.py classify .agents/scripts/check_maps.py` prints
`classified` on a fresh graph and `unclassified` after `git commit --allow-empty` (stale); the test.
**Acceptance row 8 to add to SCC-270 on the go:** "`risk_seam.py classify` returns `classified` tiers
from `code-review-graph detect-changes --json` when the lane's graph is fresh and `unclassified`
otherwise; `gates_audit` stays False (test pinned); `/smh-code-review` Step 0.7 and `/cicd-code-review`'s
twin step print the tiers."

### Part G — AviationChat (AVCH-73, its own lane in `Projects/AGY_AVIATIONCHAT`)
Lane `chore/AVCH-73-code-review-graph-swap` off AGY `main`, opened after Part A passes: `.antigravity/mcp.json`
(gitnexus → code-review-graph; firebase + md-feedback untouched), `.mcp.json` (+ server), `.gitignore`
(`.gitnexus/` → `.code-review-graph/`), delete `.gitnexusignore` + `.gitnexusrc`, NEW
`.code-review-graphignore` (`_bmad/`, `_bmad-output/`, `_artifacts/`, `_my_resources/`, `*.out`,
`*.bak`), `docs/gitnexus.md` → `docs/code-review-graph.md` (same contract; `base=<epic branch>`),
`AGENTS.md` 37–38 + 187–188, `README.md` §3 (113–125) + 39 + 147, delete the six
`.agents/.claude/skills/gitnexus/*`. Its plan lives in AGY's `_artifacts/_main/`, its close-out is its
own. Not this lane's diff — listed so the whole job is visible on one page.

## 4. Port Checklist (`port-checklist.md` — both copies differ, so every check is answered)

Trigger, measured (`git diff --no-index … ; echo differ=$?`): `docs/gitnexus.md` 1 · `.gitnexusignore`
1 · `.gitnexusrc` 0 · `.antigravity/mcp.json` 1 · `.gitignore` 1 · `AGENTS.md` 1 · `.mcp.json` 1 ·
the six gitnexus skill docs 0 (identical). Direction: lobby ↔ AGY, both ways (the contract doc is
authored here and ported there; AGY's richer install notes port back).

| # | Check | Answer, with the command output that produced it |
|---|---|---|
| 1 | A git-given path used as given | n/a — no script in scope calls `--git-common-dir` / `--git-path` (`grep` over `run-hook.sh`, `session-start-context.sh`, `check_maps.py`: no hits); `rule-trigger.py` reads stdin JSON only. |
| 2 | `printf`, not `echo`, for operator-facing lines | `log-rule-load.sh` writes with `printf`; `rule-trigger.py` prints via Python. `grep -n 'echo .*\\' .agents/hooks/*.sh` → no hits today; the test for the new hook greps it. |
| 3 | Verify the FILE, not `$?` | `log-rule-load.sh` ends `>> "$LOG" \|\| exit 0` with no banner; `rule-trigger.py` has no success print. |
| 4 | No `.agents/rules/` path a thin repo lacks | AGY's `.agents/rules/` holds only its seven tier-2 rules (`ls` above). `docs/code-review-graph.md` (AGY copy) names the centre's rules by name, never by path; the hook is lobby-only (`.claude/settings.json` of the lobby). |
| 5 | Both machines | `command -v python3 python` → Mac: `/opt/homebrew/bin/python3` only; `run-hook.sh` already probes `python3 → python`. `core.hooksPath` = `.githooks` in BOTH repos on this Mac (`git config --get`); the PC must be re-armed per repo after clone — stated in `docs/code-review-graph.md`. `pwsh` 7.7 is on the Mac for the sync. |
| 6 | Hooks repo-local, target's OWN key | AGY's `.githooks/` + `.agents/scripts/git-hooks/` (JIRA-ENFORCE, MAIN-PUSH-ENFORCE, MERGE-TARGET-ENFORCE) stay where they are; `jira.conf` there says `AVCH` → the port rides **AVCH-73**, never SCC-270. |

## Declared Change Set

- NEW `_artifacts/_main/2026-08-22_code-review-graph-swap/walkthrough.md` — bake-off evidence, task checklist, your-actions → 1
- NEW `_artifacts/_main/2026-08-22_code-review-graph-swap/task.yaml` — lane manifest, riders filled on the go → 1
- NEW `_artifacts/_memory/base-is-not-a-gitnexus-replacement.md` — the evaluation record, moved onto this lane per AGENTS.md §7 → 1
- EDIT `_artifacts/_memory/MEMORY.md` — its index line → 1
- EDIT `.mcp.json` — gitnexus entry → `code-review-graph serve` → 3
- EDIT `.antigravity/mcp.json` — same swap → 3
- EDIT `.gitignore` — drop `**/.gitnexus/`, add `.code-review-graph/` → 2, 3
- DELETE `.gitnexusignore` → 3
- DELETE `.gitnexusrc` → 3
- NEW `.code-review-graphignore` — scope the lobby index to the manager surface → 3
- DELETE `docs/gitnexus.md` → 2
- NEW `docs/code-review-graph.md` — house contract, tool table, freshness, both-machine install, local override → 2, 5
- EDIT `AGENTS.md` — §8 pointer block (Part C) and the §3 frontmatter sentence (Part E) → 2, 6
- EDIT `.agents/INDEX.md` — lines 19–20 → 2
- EDIT `.agents/skills/workspace-structure/SKILL.md` — lines 27–28 → 2
- EDIT `docs/repo-map.md` — curated header 40–59 → 2
- EDIT `docs/workspace-standard.md` — line 175 wording → 2
- DELETE `.agents/.claude/skills/gitnexus/gitnexus-cli/SKILL.md` → 5
- DELETE `.agents/.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` → 5
- DELETE `.agents/.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` → 5
- DELETE `.agents/.claude/skills/gitnexus/gitnexus-guide/SKILL.md` → 5
- DELETE `.agents/.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` → 5
- DELETE `.agents/.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` → 5
- NEW `.agents/skills/code-review-graph/SKILL.md` — the one house skill (master) → 5
- NEW (generated) `.claude/skills/code-review-graph/SKILL.md` — sync output → 5
- EDIT `.agents/skills/INDEX.md` — Code-quality-gates family row → 5
- EDIT `.agents/commands/cicd-self-audit.md` — lines 11, 143, 149 → 5
- EDIT `.agents/commands/cicd-clean-code-audit.md` — line 156 → 5
- EDIT `.agents/commands/smh-update-maps-indexes.md` — check-9 wording + re-index hand-off → 4, 5
- EDIT `.agents/commands/sentry-security-team-avch.md` — graph enrichment lines → 5
- EDIT `.agents/workflows/sentry-security-team-avch.md` — Antigravity mirror of the same → 5
- EDIT `.agents/workflows/INDEX.md` — line 9 → 5
- EDIT (generated) `.opencode/commands/cicd-self-audit.md` — sync output → 5
- EDIT (generated) `.opencode/commands/cicd-clean-code-audit.md` — sync output → 5
- EDIT (generated) `.opencode/commands/smh-update-maps-indexes.md` — sync output → 5
- EDIT (generated) `.opencode/commands/sentry-security-team-avch.md` — sync output → 5
- EDIT `.agents/scripts/check_maps.py` — check 9 reads `graph.db` metadata; ignore list → 4
- EDIT `.agents/scripts/tests/test_check_maps.py` — check-9 fixture, RED first → 4
- EDIT `.agents/scripts/record_map_changes.py` — ignore list → 4
- EDIT `.agents/scripts/generate_doc_graph.py` — docstring + ignore list → 2
- EDIT `.agents/scripts/evidence_extract.py` — docstring wording → 2
- EDIT `.agents/scripts/tests/test_evidence_extract.py` — line 1404 assertion → 2
- EDIT `.agents/scripts/risk_seam.py` — line 19 → 2
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — line 1830 ignore set → 2
- EDIT `.agents/scripts/INDEX.md` — line 31 → 2
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — §5 check 9, §6 ③, §9 review tools + hook reach → 5
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one line → 5
- EDIT `.agents/rules/000-PLAN-FIRST-GATE.md` — frontmatter → 6
- EDIT `.agents/rules/artifacts-always-first.md` — frontmatter → 6
- EDIT `.agents/rules/code-standards.md` — frontmatter (paths) → 6
- EDIT `.agents/rules/collaborative-debug-first.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/completion-not-illusion.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/constitution.md` — frontmatter (always_on) → 6
- EDIT `.agents/rules/dependency-awareness.md` — frontmatter (paths) → 6
- EDIT `.agents/rules/git-policy.md` — frontmatter → 6
- EDIT `.agents/rules/jira.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/karpathy-guidelines.md` — frontmatter (always_on) → 6
- EDIT `.agents/rules/living-template-sync.md` — frontmatter (paths) → 6
- EDIT `.agents/rules/lobby-search.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/mermaid-diagram-preferences.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/mobile-mode.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/operator-profile.md` — frontmatter (always_on) → 6
- EDIT `.agents/rules/port-checklist.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/powershell-encoding-safety.md` — frontmatter (paths) → 6
- EDIT `.agents/rules/project-law.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/prose-formatting.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/reproduce-before-you-fix.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/smh-target-resolution.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/sop-currency.md` — frontmatter (paths) → 6
- EDIT `.agents/rules/tests-must-gate-for-real.md` — frontmatter (paths) → 6
- EDIT `.agents/rules/work-consolidation.md` — frontmatter (triggers) → 6
- EDIT `.agents/rules/worktree-per-story.md` — frontmatter → 6
- EDIT `.agents/rules/INDEX.md` — "How rules load" mirror contract → 6
- NEW `.agents/scripts/tests/test_rule_frontmatter.py` — frontmatter ↔ INDEX agreement, RED first → 6
- EDIT `.agents/scripts/sync-agents.ps1` — emit `.claude/rules/` for `paths:` rules → 6
- NEW (generated) `.claude/rules/code-standards.md` — sync output → 6
- NEW (generated) `.claude/rules/dependency-awareness.md` — sync output → 6
- NEW (generated) `.claude/rules/powershell-encoding-safety.md` — sync output → 6
- NEW (generated) `.claude/rules/tests-must-gate-for-real.md` — sync output → 6
- NEW (generated) `.claude/rules/living-template-sync.md` — sync output → 6
- NEW (generated) `.claude/rules/sop-currency.md` — sync output → 6
- NEW `.agents/hooks/rule-trigger.py` — UserPromptSubmit rule-trigger hook → 7
- NEW `.agents/scripts/tests/test_rule_trigger.py` — RED first → 7
- NEW `.agents/hooks/log-rule-load.sh` — InstructionsLoaded probe → 7
- EDIT `.agents/hooks/INDEX.md` — both hooks listed → 7
- EDIT `.claude/settings.json` — UserPromptSubmit + InstructionsLoaded entries via run-hook.sh → 7
- NEW (generated) `.claude/hooks/rule-trigger.py` — sync output → 7
- NEW (generated) `.claude/hooks/log-rule-load.sh` — sync output → 7
- EDIT `_routing-canary/README.md` — rule-activation probe section → 7

- DELETE `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` — tracked copy, never sync-managed → 2, 5
- DELETE `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` — tracked copy → 2, 5
- DELETE `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` — tracked copy → 2, 5
- DELETE `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` — tracked copy → 2, 5
- DELETE `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` — tracked copy → 2, 5
- DELETE `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` — tracked copy → 2, 5
- EDIT (generated) `.claude/skills/workspace-structure/SKILL.md` — sync mirror of the master edit → 2
- EDIT `.agents/AGENTS.md` — line 43 comment → 2
- EDIT `docs/AGENTS.md` — line 31 entry → 2
- EDIT `docs/_scc_sops_prds/INDEX.md` — line 11 → 2
- EDIT `docs/_scc_sops_prds/file_folder_structure+maintaining.md` — lines 59, 83, 87, 214, 233, 383, 397 → 2
- EDIT `docs/_scc_sops_prds/tea_deep_reference.md` — line 123 → 2
- EDIT `docs/_scc_sops_prds/tea_testing_guide.md` — lines 156, 203, 498, 523 → 2
- EDIT `docs/migrations/INDEX.md` — lines 7, 78 → 2
- EDIT `docs/migrations/install_guides/new_machine-migration-guide.md` — §326–345 install block becomes the both-machine recipe → 2, 5
- EDIT `.agents/scripts/tests/test_sops_prds_folder.py` — line 9 docstring → 2
- EDIT (generated) `docs/doc-graph.md` — regenerated by generate_doc_graph.py → 2
- EDIT (generated) `docs/doc-graph.json` — regenerated by generate_doc_graph.py → 2
- EDIT `.agents/scripts/risk_seam.py` — Part H classifier behind the seam → 8
- EDIT `.agents/scripts/tests/test_risk_seam.py` — Part H fresh/stale/absent cases, gates_audit pin kept → 8
- EDIT `.agents/commands/smh-code-review.md` — Part H: Step 0.7 prints the tiers → 8
- EDIT `.agents/commands/cicd-code-review.md` — Part H: twin step prints the tiers → 8
- EDIT (generated) `.opencode/commands/smh-code-review.md` — sync output → 8
- EDIT (generated) `.opencode/commands/cicd-code-review.md` — sync output → 8

## 6. Verification plan (exact commands; Mac `python3`, PC `python`)

```bash
# RED first (Parts D, E, F) — run before the matching code lands and paste the failure
python3 .agents/scripts/tests/test_check_maps.py
python3 .agents/scripts/tests/test_rule_frontmatter.py
python3 .agents/scripts/tests/test_rule_trigger.py
# the suite, unpiped, read the exit code
python3 .agents/scripts/tests/run_all.py
python3 .agents/scripts/workflow_lint.py --toolkit-only
python3 .agents/scripts/check_maps.py
python3 .agents/scripts/declared_change_set.py parse _artifacts/_main/2026-08-22_code-review-graph-swap/implementation_plan.md
# acceptance 2
git ls-files | xargs grep -lI -i gitnexus | grep -v -E '^(_artifacts|_my_resources|_bmad)' ; echo "rc=$? (1 = clean)"
# the graph itself, both repos
code-review-graph status --json
printf '%s\n%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}' '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | perl -e 'alarm(40); exec "code-review-graph","serve"' | grep -o '"name":"[a-z_]*_tool"' | wc -l   # expect 30
# sync emits the generated surfaces
pwsh .agents/scripts/sync-agents.ps1 -WhatIf
# the gate at the tip, through the receipt writer (work-consolidation rule 3)
python3 .agents/scripts/gate_receipt.py --repo . --branch chore/SCC-270-code-review-graph-swap
```

Then `/smh-code-review` on the lane, and `/smh-close-task-merge-tree --expect-key SCC-270`
(riders flip first, parent last). AVCH-73 runs and closes in its own repo.

## 7. Open questions — each answered with the default this plan takes

- **Keep GitNexus on the machines until Part A passes?** Yes. Uninstall (`npm rm -g gitnexus`, delete
  `~/.gitnexus` and each repo's `.gitnexus/`, drop the `~/.claude.json` overrides) is a `## Your
  Actions` item after acceptance 1, on each machine.
- **Track the generated `.claude/rules/`?** Yes — exactly like `.claude/skills/`; the sync owns it.
- **Path-scope `mermaid-diagram-preferences` to `*.md`?** No — every Markdown read would load it;
  it stays `model_decision` with `triggers:` ("mermaid", "diagram").

## Self-Audit (2026-08-22)

**Level: LEDGER+BLAST · Mode: PRE-WORK** (the set touches rules, hooks, scripts others import, four
command doors, two platforms, files that exist in both repos, and carries DELETEs).
Repo: `SCC-270-code-review-graph-swap` worktree | Branch: `chore/SCC-270-code-review-graph-swap` (from
`git rev-parse`). Plan: this file. Ticket: SCC-270 (7 acceptance rows, each with an observable — the
Scope Ledger precondition holds; rows quoted from `acli jira workitem view SCC-270`).

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every one of the 89 declared paths tested on disk (EDIT/DELETE must exist, NEW must not;
             relative to origin/main); every cited line number tested for the literal `gitnexus`
             (16 files, 38 lines — 0 misses); 14 plan-named scripts/commands/rules `ls`'d; both-machine
             tool reality (`command -v python3 python pipx perl pwsh code-review-graph gitnexus`,
             `import sqlite3`); `declared_change_set.py parse` (present, 89 entries, 0 incomplete);
             deployable-path scan of the set (none); acceptance rows counted and read; NEW-artefact ×
             acceptance-row ledger; caller count for the new scripts.
read:        _artifacts/_main/2026-08-22_code-review-graph-swap/implementation_plan.md ·
             .agents/commands/{cicd-self-audit,cicd-clean-code-audit,smh-update-maps-indexes,
             smh-code-review,smh-close-task-merge-tree,smh-sync-agents}.md · .agents/scripts/{check_maps,
             evidence_extract,risk_seam,record_map_changes,generate_doc_graph,declared_change_set,
             gate_receipt,jira_feed,link-worktree-assets,workflow_lint,sync-agents.ps1} ·
             .agents/scripts/tests/{run_all,test_evidence_extract,test_command_surfaces,test_risk_seam}.py ·
             .agents/rules/ (25 files + INDEX) · docs/repo-map.md · docs/workspace-standard.md ·
             `acli jira workitem view SCC-270`
verdict:     findings below (F1, F5)
```

```
lens:        2 Parity + Blast
checks_run:  four doors per edited command (skill / opencode / workflow — all present); every tracked
             file outside _artifacts/_my_resources/_bmad carrying `gitnexus` (git ls-files | grep:
             58 files) diffed against the declared set; links to every DELETE target repo-wide
             (7 hits, all declared after F1); workflow_lint rule-frontmatter handling (commands only —
             rules are not frontmatter-linted; `_RULE_POINTERS` unaffected by frontmatter);
             test_command_surfaces door-parity (line 1659: `.claude/skills/<n>/SKILL.md` must match the
             master → sync must run inside Part C); sop_currency `_SURFACES` vs each part's files;
             script callers (.githooks/post-commit → record_map_changes; .claude/settings.json
             SessionStart → check_maps, record_map_changes; 5 commands → check_maps; signatures
             unchanged); sync-agents purge policy (manifest-tracked only — untracked-by-sync copies are
             never purged); `_artifacts/_memory/` = the AGENTS.md §7 lane flow (sanctioned);
             port section present with all six checks + the differ=$? trigger; twins
             (cicd-self-audit ↔ smh-self-audit: only the cicd twin names the graph — divergence
             legitimate, the smh twin never had the step; cicd-code-review ↔ smh-code-review: Part H
             edits both); sibling worktrees after `env -u GITHUB_TOKEN git fetch origin main`
             (origin/main 9d7863b): SCC-269 (5 files) and SCC-271 (0 files vs origin/main) —
             overlap = docs/workspace-standard.md; risk_seam classify → `unclassified` (placeholder).
read:        git ls-files + grep output · .agents/scripts/{sop_currency,workflow_lint,sync-agents.ps1} ·
             .agents/scripts/tests/test_command_surfaces.py:356,448,1644-1659,1820 ·
             .githooks/post-commit · .claude/settings.json · .agents/skills/code-review-engine/steps/
             step-01-review.md, step-02-verify.md · .agents/commands/smh-code-review.md §0.7 ·
             .agents/.sync-manifest.json · git worktree list · git -C <SCC-269 tree> diff --name-only
verdict:     findings below (F2, F3, F6)
```

```
lens:        3 Pre-Mortem (bounded — narratives attached to anchored findings only)
checks_run:  the silent one, the other-machine one, the fresh-clone one, the sibling-lands-first one —
             each tried against F1/F2/F3/F5/F6; unattached narratives discarded.
read:        the findings table below; .agents/rules/sop-currency.md § The gate; memory
             gitnexus-index-not-actually-live (the stripped-PATH scar)
verdict:     narratives attached below; originated nothing
```

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `git ls-files \| xargs grep -lI -i gitnexus` (58 files) vs the first-draft Declared Change Set | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` … `docs/migrations/install_guides/new_machine-migration-guide.md:326 "- **GitNexus**: machine-local, does not travel."` | **F1 + F6.** Acceptance row 2 ("`gitnexus` appears in no tracked file outside `_artifacts/` history") would FAIL at close-out: 20 tracked files carried the word and were not declared — six of them tracked `.claude/skills/gitnexus/*` copies that the sync manifest cannot purge (sync-agents.ps1:39 "absent from the manifest and therefore CANNOT be purged"). Pre-mortem: the lane reaches `/smh-code-review`, the drift check reports 20 undeclared edits, and the grep is red on both machines. **Baked:** all 20 added to the Declared Change Set; Part C `git rm`s the six copies. | high — fixed in plan |
| `.agents/scripts/sop_currency.py:71-77` + `:103` | `_SURFACES = [(".agents/commands/", …), (".agents/rules/", …), (".agents/scripts/git-hooks/", …), (".githooks/", …), (".agents/scripts/", (".py", ".ps1"), …)]` · `if p == "AGENTS.md":` | **F2.** The first draft staged the SOP only in Part D; Parts C (`AGENTS.md`), E (`.agents/rules/*`, `sync-agents.ps1`) and H (`risk_seam.py`) each commit a gated surface. Pre-mortem (the silent one): the armed commit-msg gate rejects Part E's commit mid-lane, the agent adds `[sop-ok]` to get past it, and the SOP drifts — the exact failure the rule names. **Baked:** decision 8 — per-part SOP staging, no `[sop-ok]`. | medium — fixed in plan |
| `command -v pipx` | (no output — ABSENT); `command -v python3` → `/opt/homebrew/bin/python3`; `python` ABSENT | **F5.** Part A step 1 as drafted fails on the first command. Pre-mortem (the other-machine one): even once installed, `pipx` puts the script in `~/.local/bin`, which the GUI-launched editor's stripped `PATH` does not include (memory: the same scar killed the `gitnexus` shim) — the tracked `.mcp.json` would look right and the server would never start. **Baked:** Part A step 1 installs pipx first and names the absolute override path. | medium — fixed in plan |
| `git -C .claude/worktrees/SCC-269-workspace-standard-reconcile diff --name-only origin/main...HEAD` | `docs/workspace-standard.md` · `router.md` · `_artifacts/_main/INDEX.md` … | **F3.** Landing-order dependency on one file. Pre-mortem (sibling-lands-first): SCC-269 lands, line 175 is no longer line 175, Part C edits the wrong line. **Baked:** SCC-269 lands first; Part C absorbs `origin/main` and re-greps. | low — stated in plan |

### Observations (uncounted)
- `task.yaml` and `_artifacts/_memory/base-is-not-a-gitnexus-replacement.md` are declared NEW and
  already sit on disk — both are untracked (absent from `origin/main`), written at plan time; NEW is
  the correct op relative to git.
- Neither artefact is named by an acceptance row; both are mandated by house law (`/smh-plan-task`
  Step 3.2; AGENTS.md §7 "a memory you write during a lane goes ON THE LANE"). Recorded, not a finding.
- The first draft said "26 masters"; there are 25 (+ INDEX). Fixed.
- `rule-trigger.py` and `log-rule-load.sh` each have exactly one caller, `.claude/settings.json`,
  created by this plan — by design for a hook; falsifiable the day a second platform registers them.
- `cicd-code-review.md` carries no `gitnexus` text today, so acceptance row 5's "where they cited" is
  vacuous for it; Part H is what makes the review commands actually consume the graph. It is the
  default this plan takes because it is the operator's stated priority; it is the one scope item for
  the operator to confirm at the stop (acceptance row 8 is added on the go).
- The TEA docs (`tea_testing_guide.md`, `tea_deep_reference.md`) describe a future Test-Impact-Analysis
  design that named GitNexus as its engine; the rewording changes the engine name, not the design.
- `.agents/workflows/` launchers for the four edited commands are thin and carry no graph text;
  the sync regenerates them regardless.

### Sibling landing-order dependency
`SCC-269` (`chore/SCC-269-workspace-standard-reconcile`, In Progress) shares `docs/workspace-standard.md`
with this lane. SCC-269 lands first. If it has not landed when Part C runs, absorb `origin/main`
first; the overlap is one line.

Audit verdict: GO

**Approval (2026-08-22):** the operator's verbatim word this turn — "approved" — given on the message
that presented this plan, its `Audit verdict: GO`, and the proposed part breakdown. It covers **this
plan as it stood at `60b6868`**, the commit whose content the operator read (`git show
60b6868:_artifacts/_main/2026-08-22_code-review-graph-swap/implementation_plan.md` is that text —
that is the mechanically checkable operand `000-PLAN-FIRST-GATE` demands, and no edit to the plan's
substance has been made since). It covers the riders **SCC-272 · SCC-273 · SCC-274 · SCC-275 ·
SCC-276 · SCC-277 · SCC-278**, and Part H stays in scope (it was offered as droppable and was not
dropped). It is **planning approval only** — not merge approval, not a ticket transition, and it does
not carry to `AVCH-73`, which is a different repo and takes its own lane and its own sign-off.
Anything edited into this plan after `60b6868` re-arms that lane's gate.
