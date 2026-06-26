---
title: GitNexus → Self-Audit Gate Integration — Walkthrough
type: walkthrough
workspace: _home (+ Projects/aviationChat-AGY)
date: 2026-06-25
status: COMPLETE — both repos UNCOMMITTED (Your Actions below). End-to-end run is Daniel's (needs an aviationChat-cwd session).
plan: ./implementation_plan.md
---

# Walkthrough — Wire GitNexus into the Self-Audit Gate (Option A: restore in master + sync)

## What this was
Daniel wanted the pre-dev `/1_self-audit-stress-test` to use the GitNexus code graph for its blast-radius
trace. While planning, the target moved twice: aviationChat got converted to the workspace standard
(Phase 1 **and** Phase 2), and Phase 2 **deleted `.agent/`** — which is where the self-audit *workflow body*
lived. The command (`@.agents/workflows/1_self-audit-stress-test.md`) was left pointing at a file that
didn't exist; the master `.agents/` never carried that body. So the job became: **restore the body in the
master with the GitNexus step baked in, then sync it into aviationChat.** (Direction A, Daniel-approved.)

## Why this didn't collide with the conversion
Confirmed via `_artifacts/INDEX.md`: the `ws7-and-phase2` session already ran Phase 2 (deleted `.agent/`
= 1,059 files, repointed commands `.agent/`→`.agents/`). That repoint is what orphaned the command. This
restore **completes** that work — it puts the missing body where the repointed command already looks.

## What changed (3 files)

| # | File | Change |
|---|------|--------|
| 1 | `.agents/workflows/1_self-audit-stress-test.md` (home-base **master**) | **CREATED.** The durable single source. Full Phase 0–5 recovered + lightly generalized + new conditional GitNexus lead-in in Phase 1. Carries a one-line "edit the master, not copies" comment. |
| 2 | `Projects/aviationChat-AGY/.agents/workflows/1_self-audit-stress-test.md` | **CREATED** (identical to #1). aviationChat's `.agents/` is a vendored copy; this is the "sync" so its command resolves. |
| 3 | `.agents/commands/1_self-audit-stress-test.md` (home-base master adapter) | **EDITED** — repointed `@.agent/workflows/` → `@.agents/workflows/` so the home base's OWN command resolves to the new master body. (Optional file #3 — my call; reversible.) |

## Recovery source + a correction to the plan
The plan said the two surviving bodies (jetChat, ingestion) were "identical." They are **not**: aviationChat's
pre-conversion copy carried a **Phase 5 — Deliver the Findings as a Copy-Paste Block (MANDATORY)** that
ingestion's copy lacks. I used the **richer aviationChat version** (with Phase 5) as the master base, so the
master is the most-complete form, not the lesser one.

## Light generalization (master serves all projects)
Kept every bit of rigor; softened only the hardest aviationChat-only tokens to generic-with-example form:
- `a new Firestore client instead of get_db()` → `a new DB client instead of the shared singleton (e.g. get_db())`
- `SSE/WebSocket event, API schema, Firestore doc shape` → `… DB doc/row shape, function signature`
- `external state (Firestore docs, GCP IAM, env vars)` → `external state (DB docs/rows, cloud IAM, env vars)`
- Phase 4 `Firestore schema/rules` → `DB schema/rules`
- "both backend Python AND frontend TypeScript" → "both backend AND frontend (e.g. Python AND TypeScript)"
- Phase 3 "simultaneous SSE" kept as an *example* (parenthetical), not a requirement.

## The GitNexus step (conditional by design)
Phase 1 now leads with a **graph-first-when-available** block: use `impact({...summaryOnly:true})` and
`context({name})` for the authoritative blast radius **if** the repo is GitNexus-indexed (AGENTS.md/CLAUDE.md
has the "GitNexus — Code Intelligence" section) and the MCP tools are present; **fall back to the existing
grep** otherwise. It also tells the auditor to read the confidence column (code ≈ 1.0; doc/story mentions
≈ 0.8) and warns that GitNexus shows no cross-repo edges for shared-data-store coupling (the contract
two-sidedness check stays manual). The grep one-liner, the blast-radius table, and all other phases are
unchanged.

**Why conditional:** the headless autopilot QA stage (`/1_self-audit-stress-test_AP`) runs
`claude -p --permission-mode bypassPermissions` with no `--mcp-config`, in a project with no `.mcp.json` and
no `enabledMcpjsonServers` → it **cannot** call GitNexus. The "fall back to grep" wording keeps that path
working untouched; the interactive run gets the graph.

## Verification
- **Path match (structural):** aviationChat's command (`.claude/commands/1_self-audit-stress-test.md`,
  `.agents/commands/...`, `.opencode/commands/...`) references `@.agents/workflows/1_self-audit-stress-test.md`;
  file #2 now exists at exactly that path. The dangling reference is resolved.
- **Tools themselves** were proven live earlier this session: `list_repos` (both repos), `context` on
  `VerificationEvent` (caught the dual definition), `impact` by UID (12 affected, MEDIUM, depth+confidence).
- **NOT done by me (yours):** a true end-to-end `/1_self-audit-stress-test` run inside an **aviationChat-cwd**
  session — that needs the project open as the working dir, which this home-base session isn't. Low risk
  (it's a doc-load + the tools are confirmed), but it's the real proof.

## Deviations from plan
- Included **optional file #3** (home-base adapter repoint) — leaving a knowingly-dangling pointer next to a
  fix felt wrong. Fully reversible (`.agents/`→`.agent/`).
- Corrected the "identical bodies" assumption (Phase 5 — see above).

## Still open / NEXT (not this task)
- **Home base's actually-loaded copies still dangle:** `.claude/commands/` + `.opencode/commands/`
  `1_self-audit-stress-test.md` at the home base still say `@.agent/workflows/`. I only fixed the `.agents/`
  master adapter. They'll resolve once re-synced from the master. (Same for propagating the new body to other
  converted projects via `/sync-agents`.)
- **ingestion-Pipeline-AC / jetChat** are unconverted and keep their own old-style `.agent/workflows/` bodies
  (no change). ingestion is indexed (`RAG_Pipeline_AC`) — same edit could apply when it's converted.
- A future `gitnexus analyze` re-index will re-touch each repo's AGENTS.md GitNexus block (sentinel-managed).

## ⚠️ Your Actions (I do NOT commit/push — git-policy)

**1) Home base** (`c:/Sudo_Hatter_Command`, branch `main`) — the master body, the adapter repoint, and this session's artifacts:
```bash
cd "c:/Sudo_Hatter_Command"
git add .agents/workflows/1_self-audit-stress-test.md \
        .agents/commands/1_self-audit-stress-test.md \
        _artifacts/_home/2026-06-25_gitnexus-audit-integration/ \
        _artifacts/INDEX.md
git status   # confirm ONLY these (plus the diagrams_guides docs below if you want them)
git commit -m "feat(toolkit): restore self-audit workflow body in master .agents/ with conditional GitNexus Phase-1 (graph-first, grep fallback); repoint home-base adapter"
git push
```
> Earlier this session I also wrote `_my_resources/diagrams_guides/system/gitnexus-usage-guide.md` (the usage
> guide) + updated `_my_resources/diagrams_guides/INDEX.md`. Add those two paths to the commit if you want
> them included; otherwise leave them.

**2) aviationChat** (`c:/Sudo_Hatter_Command/Projects/aviationChat-AGY`, branch `main_debug`) — one new file. NOTE: this repo already has the **full Phase 1+2 conversion uncommitted** (per the `ws7-and-phase2` handoff). Add this file to that pending commit, or commit it on its own:
```bash
cd "c:/Sudo_Hatter_Command/Projects/aviationChat-AGY"
git add .agents/workflows/1_self-audit-stress-test.md
git status   # this is one addition on top of the pending conversion change set
# fold into your conversion commit, or:
git commit -m "feat: restore self-audit workflow body (synced from master, GitNexus-aware Phase 1)"
git push
```
