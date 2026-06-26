# Walkthrough — GitNexus Adoption Spike

**Date:** 2026-06-24 · **Status:** spike executed (steps 1–4 done); MCP wiring (gate) + optional embeddings/visualize pending.

## What was done (verified, with evidence)

1. **Installed** `gitnexus@1.6.8` globally (`npm i -g gitnexus`, 267 pkgs, 18s). CLI confirmed; richer than docs (`trace`, `detect-changes`, `cypher`, `check`, `group`).
2. **Indexed `aviationChat-AGY`** (`gitnexus analyze`, 18.1s) → **17,335 nodes · 25,190 edges · 323 clusters · 300 flows** (branch `main_debug`).
3. **Indexed `ingestion-Pipeline-AC`** (5.2s) → **3,967 nodes · 4,207 edges · 19 clusters · 24 flows** (branch `main`).
4. **Registry** (`gitnexus list`) shows both under one server: `AGY_AVIATIONCHAT`, `RAG_Pipeline_AC`.
5. **Capabilities** (`gitnexus doctor`): graph store ✓, FTS ✓, **VECTOR index ✗ (Windows)** → semantic = exact-scan, 10k-chunk cap; local embeddings supported (not yet generated).
6. **Single-repo query** `"verification" -r AGY_AVIATIONCHAT` → surfaced the cross-cutting verification surface (FE `applyVerification`, `ReasonerAgent`, **`VerificationEvent` defined twice** in `reasoner/agent.py` + `schemas/specialist.py`, routers, tests) in one call. Timing ~192ms.
7. **Cross-repo group** `ac-stack` (app/chat + data/ingestion), `group sync` → **139 contracts, 24 cross-links**.

## Findings (the point of the spike)

| Claim | Verdict | Evidence |
|---|---|---|
| Indexing survives the real stack | ✅ | 21k+ nodes across both, <20s each |
| Multi-repo registry / one server | ✅ | both repos in `gitnexus list` |
| Within-repo structural query beats grep | ✅ | verification example surfaced dual-defined class + FE/BE/tests in one call |
| **Cross-repo edges between THESE repos** | ❌ | **all 24 cross-links are `app/chat→app/chat`; ZERO aviationChat↔ingestion** |
| Semantic flow ranking | ⚠️ | top flows were low-value utilities; needs `--embeddings`; VECTOR disabled on Windows |
| Contract method inference | ⚠️ | consumers mislabeled `GET` for `POST` providers |
| Bonus: API-surface map | ✅ | 139-contract FE↔BE map of aviationChat (conf 1.0) |

### KEY FINDING — cross-repo value is contract(HTTP)-based, and the AC stack isn't HTTP-coupled
GitNexus links repos via **HTTP provider/consumer contracts**. aviationChat ↔ ingestion-pipeline couple through a **shared data/RAG store**, not HTTP calls → GitNexus's matcher draws **no edge** between them. Implication for the §9 vision: the multi-repo "portfolio graph" gives you **N rich graphs in one registry**, but **not meaningful edges between data-coupled repos**. Cross-repo "blast radius across projects" only works for HTTP/microservice topologies.

## Preliminary go/no-go
- **GO** for GitNexus as a **within-repo Tier-2 deep-query layer** (per §9 design: derived, disposable, on-demand). Real, fast, useful.
- **NO** on the "one unified portfolio graph with edges between projects" premise — at least for the data-coupled AC stack. Re-scope that expectation: per-repo depth, not cross-repo edges.

## Remaining to fully decide
- [ ] **[GATE]** Wire MCP into `~/.claude/mcp.json` (manual minimal; NOT `gitnexus setup`) → test tools live inside Claude Code.
- [x] Embeddings: **SKIPPED** (Daniel, 2026-06-24) — VECTOR disabled on Windows = slow exact-scan, modest payoff; structural tools suffice.
- [ ] Optional: `gitnexus serve` + web UI for the visualization (Daniel's original want).

## ⚠️ CORRECTION — `analyze` is NOT read-only (discovered 2026-06-24)
Earlier this plan/walkthrough claimed indexing only writes the gitignored `.gitnexus/`. **That is wrong.** Verified via `git status` in both repos: `gitnexus analyze` (plain — no `--skills`, no `setup`) **modified `CLAUDE.md`** (appended a ~80-line "GitNexus — Code Intelligence" section; uncommitted, ` M`) **and added untracked `.claude/skills/gitnexus/`** skill files. It **appended** — it did NOT clobber existing front-door content. The section is NOT in HEAD (new this session). `.gitnexus/` is untracked (0 tracked). This is the §9 front-door-injection risk realized. Fully reversible since nothing is committed. **Decision (Daniel, 2026-06-24): KEEP** the appended section + skill files (it's the mechanism that makes Claude Code auto-use the MCP tools). Working-tree changes stay; commit is Daniel's call later (explicit paths, `.gitnexus/` gitignored first).

## Notes / housekeeping
- Per-repo untracked/modified from GitNexus (BOTH repos): ` M CLAUDE.md`, `?? .claude/skills/gitnexus/`, `?? .gitnexus/`. Add `.gitnexus/` to each repo's `.gitignore` (lines handed to Daniel; NOT auto-edited — those repos have their own approval gate).
- Group stored at `~/.gitnexus/groups/ac-stack` (harmless; `gitnexus group remove`/`clean` to undo).
- Indexed `main_debug` for aviationChat (currently-checked-out branch); pin `--branch main` for a canonical index later.

## MCP wiring (gate step — DONE, approved by Daniel)
Created **project-scoped** `c:\Sudo_Hatter_Command\.mcp.json` (no existing MCP config was clobbered; `~/.claude.json` left untouched):
```json
{ "mcpServers": { "gitnexus": { "command": "cmd", "args": ["/c", "gitnexus", "mcp"] } } }
```
Used the manual minimal form, NOT `gitnexus setup` (which would inject hooks/skills into `.claude`/`.agents`). Visualizer running at http://localhost:4747 (`gitnexus serve`, background).
**To activate:** restart/reconnect Claude Code so it loads the project MCP server, approve `gitnexus` when prompted, then `/mcp` to confirm. The current session will NOT see the tools until reconnect.

## Your Actions (git — home base only; per git-policy I did NOT commit)
Home-base changes this session = spike artifacts + INDEX row + the new `.mcp.json`. To save them:
```
git -C c:\Sudo_Hatter_Command add _artifacts/_home/2026-06-24_gitnexus-adoption-spike/ _artifacts/INDEX.md .mcp.json
git -C c:\Sudo_Hatter_Command commit -m "spike: GitNexus adoption — exec + findings + project .mcp.json (within-repo GO, cross-repo edges N/A for data-coupled AC stack)"
```
(`Projects/` is gitignored in the home base, so the indexes + group don't touch this repo.)
