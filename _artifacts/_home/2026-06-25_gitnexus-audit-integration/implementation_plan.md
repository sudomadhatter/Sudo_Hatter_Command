# Implementation Plan — Wire GitNexus into the Self-Audit Gate

**Workspace:** `_home` (Sudo_Hatter_Command), crossing into `Projects/aviationChat-AGY`
**Date:** 2026-06-25
**Status:** ⏸️ ON HOLD (2026-06-25) — aviationChat-AGY is being restructured. Do NOT edit yet. When the update lands, re-inspect the new setup (workflow path, the CLAUDE.md GitNexus section, any new `.mcp.json`/settings) and REVISE this plan before seeking approval. The §3/§4 file paths below are pre-restructure and may move.
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
- Any home-base toolkit "master workflow" restructuring (the per-project body is the durable target today).
