# code-review-graph — code intelligence for the command centre

> Pointer target from the root `AGENTS.md`. The graph guidance lives here so it does not clutter the
> always-read front door. **Static** — no generator rewrites this file.

**What it is.** A local, MIT-licensed code graph (`code-review-graph`, Tree-sitter + SQLite) that
answers *who calls this*, *what breaks if I change it*, *what has no test*, and *what does this diff
put at risk*. It is an **MCP server** (30 tools) and a CLI, and it is the engine `/smh-code-review`,
`/cicd-code-review`, `/smh-self-audit` and `/cicd-self-audit` reach for.

**Scope here.** The lobby index maps the **master toolkit** — `.agents/` (scripts, commands, rules,
skills, hooks) plus `docs/` and `.githooks/`. That is the point of it: **1073 of this repo's 1102
graph nodes are `.agents/`**, and the toolkit is the thing this repo exists to maintain. Product code
lives in the child repos, each with its own graph (`Projects/AGY_AVIATIONCHAT` → its own
`docs/code-review-graph.md`). Scope is set by the committed `.code-review-graphignore`.

## Always do

- **Before editing a symbol, ask who depends on it.**
  `query_graph_tool` with pattern `callers_of` (and `importers_of` for a module) — or the CLI,
  `code-review-graph query callers_of <name>`. Report the blast radius before you edit, not after.
- **Before claiming a change is tested, ask the graph.**
  `query_graph_tool` pattern `tests_for <name>`. "There are tests in the repo" is not the same claim.
- **Before every commit, run change detection against the branch you will actually land on.**
  `detect_changes_tool` / `code-review-graph detect-changes --base <ref>`. It returns risk-scored
  changed functions, affected flows, test gaps and suggested review questions.
- **⛔ Use the MERGE-BASE, never the branch name.** `--base main` is a **two-dot** diff: it reports
  everything that landed on `main` since you branched, so a busy week turns a 12-file lane into a
  104-file "review" of other people's work. The lane-only question is:
  ```bash
  code-review-graph detect-changes --base "$(git merge-base HEAD main)" --brief
  ```
  This is the same `..` vs `...` distinction `/smh-code-review` Step 0.7 already teaches.
- **Warn the operator on HIGH risk before proceeding**, and say what the risk is made of (which
  functions, which missing tests) rather than quoting the score.
- **Read the source the graph points you at.** The graph narrows where to look; it does not replace
  looking. See the precision limit below — it is real and it is measured.

## Never do

- **Never treat the node list as the whole truth.** Measured on `AGY_AVIATIONCHAT` (2026-08-22):
  `backend/routers/specialist.py` defines **three** nested closures all named `event_stream` (lines
  143, 358, 429), and the graph attributes a call to the wrong one. Direct callers of a top-level
  function are exact; **same-named nested closures in one file collapse**. When a caller's identity
  decides your action, confirm it with `grep`.
- **⛔ `callers_of` UNDER-REPORTS attribute-dispatched calls — and `callees_of` is the way to see it.**
  Measured on `AGY_AVIATIONCHAT` (2026-08-22). `SpecialistOrchestrator.handle_socratic` calls
  `self.socratic_teacher.evaluate(...)` at four lines (2373, 2422, 2580, 2630) of
  `backend/agents/specialist/agent.py`. `callers_of SocraticTeacherAgent.evaluate` returns 11 callers
  and **`handle_socratic` is not one of them**. The edge is not lost — it points at a bare `evaluate`
  node the resolver marked `"resolution": "ambiguous"` with **both real candidates named**, and
  `callees_of handle_socratic` shows it. So the two directions disagree, and only one of them tells you.

  The rule: **when `callers_of` returns few or no production callers for a method reached through an
  attribute, it has not proved the method is dead.** Run `callees_of` on the function you suspect, and
  treat an `ambiguous` entry that lists your target in `candidates` as a real call site.

  ⓘ This is the same seam the previous engine failed at, and it fails *better*: GitNexus's `impact()`
  on this exact call chain reported the path as effectively unreached and had to be ground-truthed by
  hand (recorded in that repo's `_bmad/bmm/stories/tea-6-temp0-integration.md`). This engine keeps the edge and
  names the candidates — it just files them somewhere `callers_of` does not look. In a 54-callee
  function, **33 callees were unresolved bare names** (mostly builtins, but `evaluate` among them).
- **Never report a `tests_for` / `test_gaps` miss as a finding without opening the test file.** The
  test link is a CALL-GRAPH link, so **a test that spawns its subject as a subprocess is invisible to
  it**. Measured on this repo (2026-08-22): `detect-changes` listed all eight functions of
  `.agents/hooks/rule-trigger.py` as untested while `test_rule_trigger.py` was exercising every one of
  them through `subprocess.run`. That is most of `.agents/scripts/tests/`, which tests scripts by
  running them. A gap here means *go look*, not *there is no test* — and the two read identically in
  the tool's output.
- **Never trust a stale graph.** The index is machine-local, per-worktree, and gitignored — it does
  **not** travel through git. `check_maps.py` check 9 compares the graph's recorded commit with `HEAD`
  and hints when they diverge; that hint is non-fatal by design, so it is on you to act.
- **Never rename by find-and-replace** when the graph can tell you the call sites.
- **Never point a cloud embedding provider at this repo.** Local embeddings only; the cloud providers
  transmit source-derived text.

## The tools that matter (30 total)

| Tool | Answers |
|---|---|
| `detect_changes_tool` | this diff → risk-scored functions, affected flows, **test gaps**, review questions |
| `get_review_context_tool` | the minimal file set + call chains needed to review a change |
| `get_impact_radius_tool` | blast radius of changed **files** |
| `get_affected_flows_tool` | which execution flows a change disturbs |
| `query_graph_tool` | `callers_of` · `callees_of` · `imports_of` · `importers_of` · `tests_for` · `children_of` · `inheritors_of` · `file_summary` |
| `get_knowledge_gaps_tool` | isolated nodes, untested hotspots, structural fragility |
| `get_hub_nodes_tool` · `get_bridge_nodes_tool` | architectural chokepoints — where a change hurts most |
| `get_suggested_questions_tool` | review questions derived from hubs, bridges and cross-community coupling |
| `get_minimal_context_tool` | the cheapest context for a stated task — call it FIRST |
| `list_repos_tool` · `cross_repo_search_tool` | the multi-repo registry |

CLI equivalents: `build` · `update` · `watch` · `status [--json]` · `detect-changes` · `query` ·
`impact` · `search` · `flows` · `communities` · `architecture` · `dead-code` · `serve`.

## Freshness

```bash
code-review-graph status --json     # nodes, edges, files, built_at_commit, current_sha
code-review-graph update            # incremental — only files whose hash changed
code-review-graph build             # full rebuild (this repo: ~4s; a ~840-file product repo: ~6s)
```

The graph records `git_head_sha` in its own SQLite `metadata` table; that is what check 9 reads, with
stdlib `sqlite3` and no dependency on the CLI being on `PATH`.

## Install — per machine, every machine

The index and the CLI are **both** machine-local. A fresh clone has neither.

```bash
# Mac
brew install pipx && pipx ensurepath
pipx install code-review-graph

# Windows PC
python -m pip install --user pipx
python -m pipx ensurepath
pipx install code-review-graph
#   set PYTHONUTF8=1 for this server, and keep fastmcp >= 3.2.4
```

Then, from each repo root you work in: `code-review-graph build`.

### ⛔ The MCP registration is the half that fails silently

The tracked `.mcp.json` names the command portably (`code-review-graph serve`). That is correct for a
terminal, and **not** always enough for a GUI-launched editor: `launchctl getenv PATH` is unset on
macOS, so an editor started from the Dock hands its children a stripped `PATH` with no `~/.local/bin`
— the server never starts and the session simply has no graph tools, with no error. Do **not** "fix"
the tracked file; add a **local-scope override** (precedence: local > project > user) in
`~/.claude.json` under `projects["<repo path>"].mcpServers`, naming the pipx console script by
absolute path:

```json
"code-review-graph": {
  "command": "/Users/<you>/.local/bin/code-review-graph",
  "args": ["serve"]
}
```

Smoke-test the server without starting a session — macOS has **no `timeout`** binary, so use `perl`:

```bash
{ printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}'
  sleep 1
  printf '%s\n' '{"jsonrpc":"2.0","method":"notifications/initialized"}'
  printf '%s\n' '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
  sleep 3
} | perl -e 'alarm(60); exec "code-review-graph","serve"' | grep -c '_tool"'
```

⚠️ The `notifications/initialized` line is **not optional**. Without it the server answers the
handshake and never lists a tool — which reads exactly like a dead server.

## Licence

MIT. That is why it is here: the previous engine was PolyForm **Noncommercial**, which does not cover
work on a product that earns money.
