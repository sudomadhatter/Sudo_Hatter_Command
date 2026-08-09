# Implementation Plan — GitNexus Adoption Spike (home base)

**Workspace:** `_home` (Sudo_Hatter_Command)
**Date:** 2026-06-24
**Status:** APPROVED 2026-06-24 by Daniel — proceed to execution (Step 0 first). Indexing is read-only (writes gitignored `.gitnexus/`); the MCP-config wiring (Step 6) is the one repo/config edit.
**Decision context:** Adopt GitNexus as the multi-repo graph RAG / MCP context layer for Claude Code. Shannon is a separate AviationChat track; OpenJarvis set aside (it's a runtime, not a graph). See memory `tooling-gitnexus-shannon-tracks`.

---

## 1. Goal (what this spike decides)

A time-boxed evaluation answering one question: **does GitNexus earn a permanent place as the cross-repo context layer for this home base, or not?** Go/no-go, with evidence — not a commitment to keep it.

Original goal it serves: *visualize all my projects + give Claude Code agents real cross-repo context instead of blind grep.*

## 2. Scope guardrails

- **CORRECTION (2026-06-24):** indexing is NOT purely read-only. `gitnexus analyze` writes `.gitnexus/` (untracked) AND **appends a "GitNexus — Code Intelligence" section to `CLAUDE.md` + adds `.claude/skills/gitnexus/`** in the indexed repo (verified via git status in both repos; uncommitted, reversible). It appends, not clobbers. Treat analyze as a repo-modifying command, not a read.
- **One config edit is the ONLY repo-touching step** (wiring the MCP server into Claude Code — `.claude/settings.json` / `.mcp.json`). That step is flagged and needs explicit approval before it runs.
- **Front-door files are untouchable.** GitNexus can *generate* AGENTS.md/CLAUDE.md — we treat that output as reference only and never let it overwrite the hand-crafted front door. (Generate into the spike folder, not into repo roots.)
- Time box: ~half a day of hands-on. If it fights us harder than that, that itself is a signal.

## 3. Pre-flight (Step 0 — verify before running anything)

1. Open the **actual** GitNexus README/docs and confirm real CLI syntax, install method, and Node version. The commands below are from a summarizer and may be wrong — **do not run blind.**
2. Confirm Node is present (`node -v`, `npx -v`) — Windows 11 / PowerShell.
3. **LICENSE — Daniel's decision (2026-06-24):** GitNexus is PolyForm **Noncommercial** (no internal-tooling carve-out; "anticipated commercial application" technically covers a planned-paid product). Daniel was advised of the strict reading twice and **accepts the grey-area risk while aviationChat is pre-revenue / non-profit** (he currently pays for others to use it; it is a private LOCAL dev tool, never shipped in production). **aviationChat-AGY is IN scope as the primary spike target for now.**
   - **TRIPWIRE (hard stop):** the moment aviationChat begins charging / becomes for-profit → STOP indexing it and DELETE its `.gitnexus/`. Then for that repo: get an akonlabs commercial quote OR move it to a permissive/MIT Tier-2 engine (the §9 design is engine-swappable for exactly this).
   - **Same test applies to every repo:** index freely now; any repo that later starts earning money trips the same wire.
   - **NEVER-INDEX LIST (current):** `jetChat` (already commercial — Daniel 2026-06-24), `clean-bmad-workspace` (another team, off-limits). aviationChat stays IN until the tripwire fires.
   - GitNexus output stays local/gitignored and is NEVER bundled into any production build.

## 4. Steps (after approval)

| # | Step | Touches repo? | Notes |
|---|------|---------------|-------|
| 0 | Verify CLI + license (section 3) | no | gating |
| 1 | `npm install -g gitnexus` (global CLI; Node v24.12 confirmed) | no | machine-level, not a repo edit |
| 2 | Index **aviationChat-AGY**: from `Projects\aviationChat-AGY` run `gitnexus analyze` (plain — NO `--skills`, so nothing is written into the repo) | no (writes gitignored `.gitnexus/`) | proves indexing survives Python+TS; verify `gitnexus status` |
| 3 | Index **ingestion-Pipeline-AC** (functional pair w/ aviationChat — the ideal cross-repo test): from its root run `gitnexus analyze`, then `gitnexus list` | no | proves the multi-repo registry (one server, both repos) |
| 4 | Visualize: `gitnexus serve` (→ localhost:4747) + open the web UI | no | the "see my projects" check |
| 5 | **[APPROVAL GATE — config edit]** Register MCP with Claude Code: **manual minimal** entry in `~/.claude/mcp.json` (cmd `npx -y gitnexus@latest mcp`) — NOT `gitnexus setup` (it also installs hooks/skills that must be reviewed vs. the existing .claude/.agents setup) | **YES (~/.claude)** | Daniel approves; the one config edit |
| 6 | Exercise tools live in Claude Code: `impact`/`context`/`detect_changes` on a known **cross-repo** call (aviationChat ↔ ingestion) | no | the real value test → criteria §5 |
| 7 | Optionally generate context (`gitnexus wiki`) **into this spike folder only** | no | evaluate as reference; do NOT overwrite the front door |
| 8 | Write `walkthrough.md` + go/no-go; update `INDEX.md` | artifacts only | handoff |

## 5. Decision criteria (what "earns its place" means)

Go only if **most** of these hold:

1. **It indexes a real repo** (aviationChat-AGY) to completion without choking on the stack.
2. **The tools beat grep** — `impact`/`context` give an agent accurate blast-radius in one call that would've taken several exploratory greps. Concretely better, not just different.
3. **Multi-repo registry works** — one MCP server genuinely serves all indexed repos to Claude Code.
4. **Generated context is useful as reference** and does not conflict with / pressure the hand-crafted AGENTS.md front door.
5. **Maintenance is bearable** — re-index cadence + server uptime are acceptable for a one-person home base.
6. **License posture is clean** for how we'll actually use it.
7. **It stays subordinate to the map** (see §9) — it can serve as a Tier-2 on-demand index without becoming a source of truth. If GitNexus vanished, the workspace must still work.

No-go signals: indexing fails/garbles the stack, low-confidence/inaccurate edges, it only restates what grep already gives, or it can't be kept in sync without babysitting.

## 6. Risks / open questions

- **License:** PolyForm Noncommercial — fine for personal/internal; a question mark if aviationChat is commercial. Resolve in Step 0.
- **Front-door conflict:** auto-generated AGENTS.md/CLAUDE.md vs. "one front door, one brain" doctrine. Mitigation: generate into spike folder only.
- **Another moving part:** an MCP server + re-index loop to maintain.
- **Browser ~5k file limit:** use CLI/backend for large repos (not a blocker, just routing).
- **Accuracy:** graph is deterministic AST (good), but confidence/coverage varies by language — verify on *our* stack, not the demo.

## 9. Pairing with the workspace standard — the two-tier context design

The point of adoption is not "add a graph"; it's to fill the empty Tier-2 slot in the existing least-context system **without** violating the standard's own principles (P4 no DB/framework as spine, P5 own-your-memory, P6 no lock-in).

**The one hard rule:** GitNexus is a **derived index, never a source of truth.** If it vanished tomorrow, the workspace still works. Everything canonical stays in plain markdown we own; the graph is a disposable accelerator.

**Two tiers:**
- **Tier 1 — the MAP** (`repo-map.md` + `router.md`): cheap, always-on via the SessionStart hook, canonical, owned plain markdown. Answers *where is X / what shape*. **Unchanged by this work.**
- **Tier 2 — the GRAPH** (GitNexus): expensive, on-demand **only**, derived/disposable. Pulled by specific routing-table rows the way Layer-3 skills are ("referenced, never preloaded"). Answers *what depends on X / blast radius / process trace / cross-repo*. **Never auto-loaded** (that would break P1 least-context).

**Three bridges (where they reinforce, evaluated in the spike):**
1. **Generator, not replacement:** GitNexus enriches the AUTO body of `repo-map.md` (via `generate_repo_map.py`'s sentinel zone) with relationship data; the CURATED human header stays sacred and untouched. Graph = engine, markdown = contract.
2. **Portfolio graph at the router level:** the multi-repo registry = one unified graph across all 7 `Projects/`; `router.md` rows stay the contract, the graph is queryable depth behind a row.
3. **Blast-radius into the gate:** `impact`/`detect_changes` populate the blast-radius section of `implementation_plan.md` — making the mandatory plan-first gate smarter (`completion-not-illusion`).

**Anti-goals (lock-in tripwires to watch in the spike):**
- Do NOT let GitNexus become the auto-loaded always-on layer (breaks least-context).
- Do NOT let it overwrite `AGENTS.md` / `router.md` / the curated repo-map header.
- Do NOT make any canonical artifact *depend* on the graph existing.

## 7. Out of scope

- Building anything custom (rejected direction).
- OpenJarvis / local-first runtime.
- Shannon (separate AviationChat security track).
- Any commitment beyond the spike.

## 8. Deliverables in this folder

- `implementation_plan.md` (this file)
- `walkthrough.md` (after execution: what happened, evidence, go/no-go)
