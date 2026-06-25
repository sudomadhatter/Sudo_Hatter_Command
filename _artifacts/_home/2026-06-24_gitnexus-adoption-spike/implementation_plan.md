# Implementation Plan — GitNexus Adoption Spike (home base)

**Workspace:** `_home` (Sudo_Hatter_Command)
**Date:** 2026-06-24
**Status:** PROPOSAL — awaiting Daniel's approval (artifacts gate). No repo edits until approved.
**Decision context:** Adopt GitNexus as the multi-repo graph RAG / MCP context layer for Claude Code. Shannon is a separate AviationChat track; OpenJarvis set aside (it's a runtime, not a graph). See memory `tooling-gitnexus-shannon-tracks`.

---

## 1. Goal (what this spike decides)

A time-boxed evaluation answering one question: **does GitNexus earn a permanent place as the cross-repo context layer for this home base, or not?** Go/no-go, with evidence — not a commitment to keep it.

Original goal it serves: *visualize all my projects + give Claude Code agents real cross-repo context instead of blind grep.*

## 2. Scope guardrails

- **Read-only on the codebases.** Indexing only reads; GitNexus writes to `.gitnexus/` (gitignored) and `~/.gitnexus/registry.json` (outside the repos). No source files change.
- **One config edit is the ONLY repo-touching step** (wiring the MCP server into Claude Code — `.claude/settings.json` / `.mcp.json`). That step is flagged and needs explicit approval before it runs.
- **Front-door files are untouchable.** GitNexus can *generate* AGENTS.md/CLAUDE.md — we treat that output as reference only and never let it overwrite the hand-crafted front door. (Generate into the spike folder, not into repo roots.)
- Time box: ~half a day of hands-on. If it fights us harder than that, that itself is a signal.

## 3. Pre-flight (Step 0 — verify before running anything)

1. Open the **actual** GitNexus README/docs and confirm real CLI syntax, install method, and Node version. The commands below are from a summarizer and may be wrong — **do not run blind.**
2. Confirm Node is present (`node -v`, `npx -v`) — Windows 11 / PowerShell.
3. Confirm the **license** (PolyForm Noncommercial) is acceptable for intended internal/non-commercial use. **Flag explicitly if any indexed repo (esp. aviationChat-AGY) is or may become commercial** — that changes the answer.

## 4. Steps (after approval)

| # | Step | Touches repo? | Notes |
|---|------|---------------|-------|
| 0 | Verify CLI + license (section 3) | no | gating |
| 1 | Install GitNexus CLI (`npx gitnexus ...` or global) | no | local tool |
| 2 | Index **one** repo first: `aviationChat-AGY` (Python + TS, the richest target) | no (writes `.gitnexus/`, gitignored) | proves indexing survives a real codebase |
| 3 | Open the graph / web UI on that repo | no | the "visualize" check |
| 4 | Index a 2nd + 3rd repo (e.g. this home base + `clean-bmad`) into the multi-repo **registry** | no | proves the "one server, all projects" claim |
| 5 | Start the MCP server (`gitnexus serve` / stdio) | no | server runs locally |
| 6 | **[APPROVAL GATE]** Wire MCP server into Claude Code config | **YES** | the one repo/config edit — Daniel approves first |
| 7 | Exercise the tools in a live Claude Code session: `impact`, `context`, `detect_changes` on a known area | no | the real test — see criteria |
| 8 | Generate context files (`gitnexus wiki` / AGENTS.md) **into this spike folder** | no | evaluate as reference, do NOT overwrite front door |
| 9 | Write `walkthrough.md` + go/no-go in this folder; update INDEX | artifacts only | handoff |

## 5. Decision criteria (what "earns its place" means)

Go only if **most** of these hold:

1. **It indexes a real repo** (aviationChat-AGY) to completion without choking on the stack.
2. **The tools beat grep** — `impact`/`context` give an agent accurate blast-radius in one call that would've taken several exploratory greps. Concretely better, not just different.
3. **Multi-repo registry works** — one MCP server genuinely serves all indexed repos to Claude Code.
4. **Generated context is useful as reference** and does not conflict with / pressure the hand-crafted AGENTS.md front door.
5. **Maintenance is bearable** — re-index cadence + server uptime are acceptable for a one-person home base.
6. **License posture is clean** for how we'll actually use it.

No-go signals: indexing fails/garbles the stack, low-confidence/inaccurate edges, it only restates what grep already gives, or it can't be kept in sync without babysitting.

## 6. Risks / open questions

- **License:** PolyForm Noncommercial — fine for personal/internal; a question mark if aviationChat is commercial. Resolve in Step 0.
- **Front-door conflict:** auto-generated AGENTS.md/CLAUDE.md vs. "one front door, one brain" doctrine. Mitigation: generate into spike folder only.
- **Another moving part:** an MCP server + re-index loop to maintain.
- **Browser ~5k file limit:** use CLI/backend for large repos (not a blocker, just routing).
- **Accuracy:** graph is deterministic AST (good), but confidence/coverage varies by language — verify on *our* stack, not the demo.

## 7. Out of scope

- Building anything custom (rejected direction).
- OpenJarvis / local-first runtime.
- Shannon (separate AviationChat security track).
- Any commitment beyond the spike.

## 8. Deliverables in this folder

- `implementation_plan.md` (this file)
- `walkthrough.md` (after execution: what happened, evidence, go/no-go)
