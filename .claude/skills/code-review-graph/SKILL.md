---
name: code-review-graph
description: "Use the local code graph to answer who-calls-this, what-breaks-if-I-change-it, what-has-no-test, and what-does-this-diff-risk — instead of grepping blind. Reach for it before editing a symbol, while reviewing a diff, when tracing a bug through unfamiliar code, and before claiming a change is covered. Carries the merge-base rule, the freshness check, and the one measured precision limit (same-named nested closures collapse). Hand-authored: the house contract, not the vendor's."
---

# code-review-graph — ask the graph before you grep

The graph is a local SQLite index built by Tree-sitter over everything `git ls-files` tracks. It is
fast (a full rebuild is seconds), machine-local, per-worktree, and gitignored. Full reference,
install and MCP wiring → [`docs/code-review-graph.md`](../../../docs/code-review-graph.md).

**The one habit this skill exists to install:** when you are about to answer a structural question by
grepping — *who calls this, what does this break, is this tested* — ask the graph first, then read the
source it points you at. The graph narrows where to look. It never replaces looking.

## Step 0 — is the graph there, and is it current?

```bash
code-review-graph status --json      # nodes, edges, files, built_at_commit, current_sha
```

- `built_at_commit` ≠ `current_sha` → `code-review-graph update` (incremental, only changed files).
- No graph at all → `code-review-graph build`. A fresh clone or a fresh worktree has none: the index
  does **not** travel through git.
- Cannot install it → say so and fall back to `grep` + a full regression, and write
  `graph unavailable` into the verdict. Never let a missing index become a silent "no impact".

## Reviewing a diff — the four calls, in this order

```bash
# 1. what this lane changed, and what it puts at risk
code-review-graph detect-changes --base "$(git merge-base HEAD main)" --brief

# 2. the minimum you must read to review it honestly
#    (MCP: get_review_context_tool)

# 3. the blast radius of the changed FILES
#    (MCP: get_impact_radius_tool, get_affected_flows_tool)

# 4. per changed symbol: is it actually covered?
code-review-graph query tests_for <symbol>
```

⛔ **`--base main` is a two-dot diff.** It counts everything that landed on `main` since you branched,
so it silently pulls other lanes' work into "your" review — measured at 104 files for a 12-file lane.
**Always `--base "$(git merge-base HEAD main)"`.** Same distinction as `..` vs `...` in `git diff`.

`detect-changes` returns risk-scored changed functions, affected flows, **named** untested symbols and
suggested review questions. Report the named gaps; a bare risk score tells the operator nothing.

## Before editing a symbol

```bash
code-review-graph query callers_of  <name>     # who breaks if the contract changes
code-review-graph query importers_of <file>    # who imports this module
code-review-graph query tests_for   <name>     # what proves it still works
```

State the blast radius before you edit. If it reaches a surface the plan does not name, that is a
finding about the plan, not a detail to absorb quietly.

## Exploring unfamiliar code

`code-review-graph architecture` for the shape · `communities` for functional areas · `flows` for
execution paths · `search <term>` to find the entry point · `query file_summary <path>` for one file.
For "where is the risk concentrated", `get_hub_nodes_tool` (most-connected) and
`get_bridge_nodes_tool` (chokepoints between areas) — those are the nodes where a small change hurts
most, and they make good review questions via `get_suggested_questions_tool`.

## Tracing a bug

Start at the symptom, walk **up** with `callers_of` until you reach the entry point, then **down** with
`callees_of` from the last place the state was known good. `query tests_for` on each step tells you
which existing test should have caught it — a step with no test is usually where the bug lives.

## ⛔ The measured precision limit

Direct callers of a top-level function are exact. **Same-named nested closures inside one file
collapse.** Measured 2026-08-22 on `AGY_AVIATIONCHAT`: `backend/routers/specialist.py` defines three
nested `event_stream` closures (lines 143, 358, 429) and the graph attributes a call to the wrong one.
(The previous engine had the same limit in the other direction — it reported four upstream entry
points where `grep` confirms one.) So: when the *identity* of a caller decides what you do next,
confirm it with `grep`. When you only need the blast radius, the graph is enough.

## Where this is enforced

`/smh-code-review` and `/cicd-code-review` Step 0.7 (blast radius against current `main`),
`/smh-self-audit` and `/cicd-self-audit` Lens 2 (parity + blast), and `.agents/scripts/risk_seam.py`,
which feeds the graph's risk tiers into those audits automatically when the index is fresh.
