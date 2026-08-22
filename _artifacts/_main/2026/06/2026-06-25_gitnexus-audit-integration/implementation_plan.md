# Implementation Plan — Wire GitNexus into the Self-Audit Gate

**Workspace:** `_home` (Sudo_Hatter_Command), crossing into `Projects/aviationChat-AGY`
**Date:** 2026-06-25
**Status:** ✅ EXECUTED 2026-06-25 (approved + built). 3 files written per §9. See `walkthrough.md`. Both repos uncommitted (Your Actions in walkthrough). Sections 3–4 SUPERSEDED by §8; §9 was the build spec.
**Follows:** `_artifacts/_home/2026-06-24_gitnexus-adoption-spike/` (GitNexus adopted, MCP live in interactive sessions). This is spike bridge #3 ("blast-radius into the gate").

---

## 1. Goal

Make the pre-dev self-audit reach for the GitNexus code graph during its **Phase 1 — Blast-Radius Trace** instead of grepping blind — but **conditionally**, so it degrades cleanly to grep where the graph isn't available (headless autopilot, non-indexed repos). Daniel asked for this AND for the aviationChat copy to be updated.

## 2. Headless finding (the constraint that shapes the edit)

The autopilot QA stage (`/1_self-audit-stress-test_AP`) runs as `claude -p … --permission-mode bypassPermissions` with **no `--mcp-config`**, in a project that has **no `.mcp.json`** and **no `enabledMcpjsonServers` setting**. → **Headless autopilot cannot call the GitNexus MCP tools.** Daniel's call: don't wire MCP into headless. Therefore the workflow edit MUST frame GitNexus as *"use if available, else grep"* so the same file works for both the interactive run (tools present) and the `_AP` run (tools absent).

## 3. Scope

- **Edit ONE file:** `Projects/aviationChat-AGY/.agent/workflows/1_self-audit-stress-test.md` — Phase 1 only. This file is the body that BOTH `/1_self-audit-stress-test` and `/1_self-audit-stress-test_AP` load (the home-base `.agents/commands/*` are thin adapters that delegate here), so one edit covers both paths.
- **No home-base edit:** the home base ships only the command adapter (no workflow body at root) and is not a GitNexus-indexed repo, so nothing to wire there.
- **No `detect_changes`:** it reads an uncommitted diff; a pre-dev plan audit has no diff. Out of scope for this gate (it belongs to the dev/review stages, already covered by aviationChat's CLAUDE.md).

## 4. The exact edit (Phase 1)

Insert a lead-in before the existing grep block, roughly:

> **Graph-first when available.** This repo is indexed by GitNexus (`AGY_AVIATIONCHAT`). When the GitNexus MCP tools are present (interactive Claude Code sessions), use them for the authoritative blast radius instead of grepping blind:
> - `impact({ target: "Symbol", direction: "upstream", repo: "AGY_AVIATIONCHAT", summaryOnly: true })` → who breaks if this changes (the "upstream setters / downstream readers" columns, from the real call graph).
> - `context({ name: "Symbol", repo: "AGY_AVIATIONCHAT" })` → callers/callees + the flows a symbol participates in.
> - **Read the confidence column:** code edges = `1.0`; `_bmad/**` story-doc mentions = `0.8` (breadcrumbs, not code).
> - **Caveat:** GitNexus does NOT model the app↔ingestion shared-data-store coupling (no cross-repo edges) — the Contract two-sidedness check below still needs manual reasoning.
>
> **Fall back to grep** when the tools aren't available (headless autopilot, a non-indexed repo) — and keep grep as a cross-check for dynamic/string references the AST graph can miss.

The existing grep one-liner + the blast-radius table + the contract/reinvention/constitution bullets stay exactly as they are.

## 5. Gate / approval path

- aviationChat enforces its own `artifacts-always-first` gate (plan → "approved" → edit). This plan is the sign-off artifact for the aviationChat edit. On "approved" I'll mirror a short copy into `Projects/aviationChat-AGY/_claude_artifacts/2026-06-25_gitnexus-audit-phase1/` per that repo's convention, make the edit, and write its walkthrough there.
- Git: I will NOT commit. The walkthrough's "Your Actions" carries the exact command for Daniel.

## 6. Decision criteria (done = )

1. Interactive `/1_self-audit-stress-test` on an aviationChat plan now uses `impact`/`context` in Phase 1, reports a graph-backed blast radius, and reads confidence.
2. Headless `_AP` run still completes on grep alone (no attempt to call absent tools, no crash).
3. The curated workflow header + every other phase are untouched.

## 7. Out of scope (this plan)

- Enabling GitNexus MCP in headless autopilot (Daniel: skip).
- `ingestion-Pipeline-AC` (also indexed) — same edit could apply; **offered as a follow-on**, not in this plan.
- `jetChat` — NEVER-INDEX (commercial); no change.
- Any home-base toolkit "master workflow" restructuring (the per-project body is the durable target today). **[SUPERSEDED — see §8: the per-project body is now gone; the master IS the target.]**

---

## 8. POST-CONVERSION RE-SCAN (2026-06-25) — revised approach

aviationChat was converted to the **workspace standard** (`_artifacts/2026-06-25_workspace-standard-conversion/`, Phase 1). Re-scan findings:

1. **The self-audit workflow BODY is gone from aviationChat.** The new command adapter (`.claude/commands/1_self-audit-stress-test.md`) points at `@.agents/workflows/1_self-audit-stress-test.md`, but that file does **not exist** — `.agents/workflows/` holds only `autopilot_bmad_dev_loop.md` + `INDEX.md`. The old `.agent/workflows/` (singular) body was retired in the conversion. **The command currently dangles.**
2. **The master `.agents/` toolkit never had the self-audit body either** (home base `.agents/workflows/` has the same two files only). So this is a **systemic gap**: converting a project to the standard *loses* the self-audit workflow, because the master it vendors from is missing it. The body survives only in the two UNCONVERTED projects (`jetChat`, `ingestion-Pipeline-AC`) under old `.agent/workflows/`.
3. **GitNexus survived into `AGENTS.md`** (always-load, sentinel block `<!-- gitnexus:start/end -->`): still mandates `impact` before edits, `detect_changes` before commits; §3 ALWAYS-LOAD names the code-graph. Strong, but framed around *code edits* — a pre-dev *plan* audit still needs its own explicit Phase-1 nudge.
4. **Headless unchanged:** no `.mcp.json` in aviationChat, no `enabledMcpjsonServers` → autopilot `_AP` still cannot call GitNexus. Keep the Phase-1 step **conditional** (graph if available, else grep).
5. **Artifact location for the aviationChat edit** is now its local `_artifacts/<date>_<slug>/` (the repo adopted `_artifacts/`; `_claude_artifacts/` is gone).

### Revised scope = restore the body in the master, with GitNexus baked in
The task is no longer "edit Phase 1 of an existing file." It is: **(re)create `.agents/workflows/1_self-audit-stress-test.md` in the home-base master**, recovering the full Phase 0–5 content (source: ingestion-Pipeline-AC's surviving copy / the pre-conversion aviationChat body), with the **GitNexus-aware, conditional Phase 1** (the §4 lead-in). Then sync the master into aviationChat so its dangling command resolves. This fixes the conversion gap AND lands the integration in one move, and propagates to every future converted project.

### Open DECISION for Daniel (pick a direction before I touch anything)
- **A (recommended):** Restore the body into the **master** `.agents/workflows/` (GitNexus Phase 1 baked in) + sync to aviationChat. Fixes the dangling command everywhere; single-source-correct.
- **B:** Patch **aviationChat only** (recreate its local body). Narrower, but fights the single-source standard and leaves the master + home-base gap.
- **C:** **Fold into your conversion Phase 2** — Phase 2 already plans to "repoint `1_*` writers / retire old `.agent/`"; restoring the self-audit body belongs there. I just hand you the GitNexus Phase-1 block to drop in then.

Also confirm this restore doesn't collide with whatever your conversion Phase 2 intends for workflow bodies.

---

## 9. EXECUTION (Option A — concrete build spec)

**Source for the body:** ingestion-Pipeline-AC's surviving `.agent/workflows/1_self-audit-stress-test.md` (= the pre-conversion aviationChat body, verified identical). Full Phase 0–5 recovered.

**Generalization (light — recommended):** the master serves all projects, so soften the few hardest aviationChat-only tokens to generic-with-example form, keeping all rigor:
- "a new Firestore client instead of `get_db()`" → "a new DB client instead of the shared singleton (e.g. `get_db()`)"
- "SSE/WebSocket event, API schema, Firestore doc shape" → "SSE/WebSocket event, API schema, DB doc/row shape, function signature"
- Phase 3 "simultaneous SSE / Firestore" examples kept as *examples*, not hard requirements.
- Everything else (Phase 0 right-size gate, Phase 2 over-engineering tripwires, Phase 4 verdict, Phase 5 copy-paste block) stays verbatim. aviationChat/ingestion lose nothing — the examples still apply.

**The new conditional GitNexus Phase 1 lead-in (generic — no hardcoded repo name):**
> **Graph-first when the repo is GitNexus-indexed and the MCP tools are present.** If AGENTS.md has a "GitNexus — Code Intelligence" section, use the graph for the authoritative blast radius instead of grepping blind:
> - `impact({ target: "Symbol", direction: "upstream", summaryOnly: true })` — who breaks if this changes (the upstream/downstream columns, from the real call graph). Add `repo: "<IndexName>"` when >1 repo is indexed.
> - `context({ name: "Symbol" })` — callers/callees + the flows it participates in.
> - **Read confidence:** code edges ≈ 1.0; doc/story-file mentions ≈ 0.8 (breadcrumbs, not code).
> - **Caveat:** GitNexus links repos only via HTTP contracts — it will NOT show coupling through a shared DB/data store; the Contract two-sidedness check below still needs manual reasoning.
>
> **Fall back to the `grep` below** when the tools aren't available (headless autopilot, or a non-indexed repo); keep grep as a cross-check for dynamic/string references the AST graph can miss.

This sits ABOVE the existing grep block; the grep one-liner, the blast-radius table, and all other bullets stay as-is.

**Files touched (3):**
1. **CREATE** `c:\Sudo_Hatter_Command\.agents\workflows\1_self-audit-stress-test.md` — the master body (generalized + GitNexus Phase 1). This is the durable single source.
2. **CREATE** `Projects\aviationChat-AGY\.agents\workflows\1_self-audit-stress-test.md` — same content, so aviationChat's command (`@.agents/workflows/...`) resolves. (Its `.agents/` is a vendored copy; this is the "sync".)
3. **EDIT (optional, flagged)** `c:\Sudo_Hatter_Command\.agents\commands\1_self-audit-stress-test.md` — repoint `@.agent/workflows/` → `@.agents/workflows/` so the home base's OWN command resolves to the new master body. (Pre-existing dangle, not caused by us. Skip if you'd rather fold all home-base adapter repointing into your conversion work.)

**NOT in scope (flagged for your Phase 2 / later):** the home-base `.claude/` + `.opencode/` command copies still say `.agent/` (singular); ingestion + jetChat keep their own old-style bodies (unconverted). Propagating the master to those is a broader sync, not this task.

**Gate / artifacts:** this home-base plan is the sign-off and **explicitly lists the aviationChat file (#2)**, so "approved" covers that cross-repo write. Closing `walkthrough.md` lands in THIS home-base folder with a "Your Actions" git section for BOTH repos. I do not commit.

**Verification (done =):** after writing, confirm file #2 exists at the exact path aviationChat's command references; spot-read both new files to confirm the GitNexus lead-in + Phase 0–5 are intact and the curated content is unchanged.
