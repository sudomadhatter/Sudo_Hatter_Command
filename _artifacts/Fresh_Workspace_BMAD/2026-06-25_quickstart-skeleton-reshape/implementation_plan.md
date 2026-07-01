---
title: clean-bmad-workspace — Re-purpose into the AGY Quick-Start Project Skeleton (home-base-aligned) + hybrid auto-updating repo-map hook
type: implementation_plan
workspace: clean-bmad-workspace
date: 2026-06-25
status: APPROVED — executing (WS7 added post-approval at Daniel's request)
owner: Daniel
author: Claude (Opus 4.8)
related:
  - _docs/workspace-standard.md                                              # the organizational DNA to mirror
  - _artifacts/clean-bmad-workspace/2026-06-25_workspace-standard-cleanup/   # the prior (completed) conformance pass
  - Projects/clean-bmad-workspace/AGENTS.md
  - Projects/clean-bmad-workspace/docs/repo-map.md
---

# clean-bmad-workspace → AGY Quick-Start Project Skeleton

## 0. Goal (reconciled from your ask + 3 live corrections)
Optimize `clean-bmad-workspace` to serve its real purpose: **the quick-start skeleton you clone to start a new
project.** Re-cast its identity from *"the aviationChat app"* to *"a generic, ready-to-build skeleton that carries
the AGY default stack and is organized/indexed/routed exactly like this home-base repo."*

**"Mirror the main repo instead of aviationChat" = mirror the home base's *system DNA*** (workspace-standard:
least-context routing, `docs/repo-map.md` indexing, `_artifacts/` memory, 9-section `AGENTS.md`, naming, gates) —
**not** turn it into a markdown-only lobby.

### ⚠️ Correction to the option you picked (read this first)
You selected **"Generic indexed workspace,"** whose preview said *REMOVED: backend/ frontend/ firebase* firestore*
pyproject…*. Your follow-ups override that line:
- *"keep the tech stack from aviationchat"* · *"I use that on almost all projects"* · *"we are optimizing this to be
  a quick start project skeleton."*

**So the stack STAYS.** We keep the runnable scaffold (`backend/`, `frontend/`, firebase/firestore configs, python
configs, `.env.example`, `docs/tech-stack.md`). We strip aviationChat's **product domain**, not its **stack**. If I've
mis-read and you *did* want the scaffold gone, say so and I'll flip back.

---

## 1. Decisions locked
| # | Decision | Source |
|---|---|---|
| D1 | Target = **quick-start project skeleton** (clone → rename → build) | your msg |
| D2 | **Keep the AGY tech stack** scaffold + configs (FastAPI/ADK · Next.js/React/TS · Firebase) | your msg |
| D3 | Organize/index/route/govern to the **home-base workspace-standard** | your ask |
| D4 | Strip aviationChat **product domain** identity (not the stack) | inferred from D1–D3 |
| D5 | Keep it **generic** — no product values baked in; it's the template | memory + AGENTS.md ROOT LAW |
| D6 | Keep **BMAD** (`_bmad/` + `_bmad-output/` skeleton) — it's the method this skeleton runs on | unchanged |
| D7 | Add the **hybrid auto-updating repo-map feature** (SessionStart hook: inject `docs/repo-map.md` + detect-only drift nag), like the home base | your msg (post-approval) |

---

## 2. Current state → target (what STAYS · what CHANGES · what we DON'T touch)

**STAYS (the stack + structure you keep):**
- `backend/` (FastAPI+ADK skeleton: `agents/ routers/ schemas/ services/ tools/ tests/` + `requirements.txt`)
- `frontend/` (Next.js/React scaffold: `package.json` + lock)
- Stack configs: `firebase.json`, `firestore.rules`, `firestore.indexes.json`, `storage.rules`, `pyproject.toml`,
  `conftest.py`, `pyrefly.toml`, `pyrightconfig.json`, `.env.example`, `.gitignore`, `.gitattributes`
- `docs/tech-stack.md` (the AGY default stack — the thing you reuse everywhere)
- `_bmad/` (BMAD module) + `_bmad-output/` (state skeleton, `{{PLACEHOLDER}}` fill-ins)
- `docs/workspace-standard.md` (vendored) + `scripts/generate_repo_map.py` (the indexer)

**CHANGES (authored files — re-cast to skeleton + home-base DNA):**
- `AGENTS.md` — ROOT LAW + MAP + routing table re-cast from "aviationChat app" → "AGY quick-start skeleton";
  keep the 9-section numbering (already compliant) and the stack-level routing rows.
- `README.md` — rewrite to the current shape: fix stale `.agent/`→`.agents/`, drop `.gemini/gemini.md`/`633 skills`
  cruft, point to `AGENTS.md` + `docs/repo-map.md`; keep the clone→rename→find&replace→build quick-start flow.
- `docs/repo-map.md` — regenerate the AUTO body after edits; rewrite the CURATED header to describe the skeleton +
  AGY stack + home-base-mirroring, with the `_my_resources/` protection flag.
- `docs/skills-registry.md` — light refresh only (stale `.agent/` paths); content is stack-aligned, keep it.
- `_bmad-output/project-context.md` + `.antigravity/mcp.json` + README placeholder table — keep as generic
  `{{PLACEHOLDER}}` template fill-ins (no aviationChat values).

**DON'T TOUCH (scope discipline / anti-fork):**
- Everything under `.agents/`, `.claude/`, `.opencode/` — **vendored** copies. Pruning aviationChat-specific
  *skills/rules* from the vendored set is a **master + `/sync-agents`** job → §5 follow-up, not this diff.
- `_my_resources/` — Daniel's protected personal area (no edits, no references). Untouched.
- `_claude_artifacts/` — already deprecated; full retirement stays a pending master pass (engine path check first).

---

## 3. Workstreams (execute only after approval)

### WS1 — Re-cast `AGENTS.md` (identity, not structure)
- **ROOT LAW** → *"Quick-start project skeleton: the AGY default stack (FastAPI+ADK backend · Next.js+React+TS
  frontend · Firebase), BMAD-driven, organized and indexed to the home-base workspace-standard. Clone → rename →
  fill placeholders → build. Keep generic — it carries the stack, not a product."*
- **MAP** — keep `backend/`+`frontend/` as the stack scaffold; drop any aviationChat-product phrasing; keep the
  `_my_resources/` protected note.
- **Routing table** — keep the stack-level rows (backend ADK, frontend, voice/SSE, story/PRD/arch/review/autopilot).
  Audit for any row pointing at an aviationChat **product** skill (dual-store-rag, hr-agent-schema,
  regulatory-verification, specialist_agents_team) — none are in the table today; confirm and keep clean.
- Persistence path stays literal `../../_artifacts/clean-bmad-workspace/` (clone-time swap handled by README find/replace — see D-note §4).

### WS2 — Rewrite `README.md` to the real, current skeleton
- Replace the stale tree/`.agent/`(singular)/`.gemini/`/`gemini.md`/`633 skills` content with the actual structure
  (`.agents/` plural, `AGENTS.md` brain, `docs/repo-map.md` index, artifacts → home base).
- Keep + sharpen the **quick-start flow**: clone → strip `.git` → `git init` → find/replace placeholders → set up
  backend/frontend → install skills → `/bmad-*` build. (This is the doc's whole reason to exist.)
- Refresh the placeholder table to the tokens that actually remain.

### WS3 — Re-index (`docs/repo-map.md`) — the headline deliverable
- Run `python scripts/generate_repo_map.py --ignore _bmad` (read-only generation) → fresh AUTO body.
- Rewrite the CURATED header: "to find X → look here" + "which doc to read when," describing the **AGY quick-start
  skeleton**, the kept stack, the home-base-mirroring, and the `_my_resources/` do-not-touch flag.

### WS4 — Keep & verify the stack (explicit no-op on removals)
- Confirm the stack scaffold + configs above are present and untouched (this is the reversal of the menu preview).
- Light refresh: fix stale `.agent/` path refs in `docs/skills-registry.md`. No stack content removed.

### WS5 — Genericize residual placeholders (authored files only)
- Ensure `.antigravity/mcp.json`, `_bmad-output/project-context.md`, and the README table carry **generic**
  `{{PLACEHOLDER}}` tokens — no leaked aviationChat product values.

### WS7 — Hybrid auto-updating repo-map feature (added post-approval) ← Daniel's "add the feature we added to sudohattercommand"
**Finding:** clean-bmad's `.claude/settings.json` has **no SessionStart hook** (permissions only); the home base's
hook injects continuity + the artifacts/git gate. The repo-map generator + curated/auto hybrid already exist here,
but nothing *injects the map or detects drift* — that's the missing "auto-updating" half (it's documented in
workspace-standard Part 3 but not yet wired anywhere). This WS completes it.
- **New `scripts/check-repo-map-drift.ps1`** (project-local authored file, alongside the autopilot engine): list the
  project's real top-level subdirs, skip the standard ignore set (`__pycache__ .venv node_modules .next .adk
  _test_scripts _debug_audio __tests__ .git .agents .claude .opencode _artifacts _claude_artifacts _bmad …`), flag
  any folder on disk that isn't named in `docs/repo-map.md`. **Detect-only — nags, never self-heals; always exit 0.**
- **Wire `.claude/settings.json` SessionStart hook** (new — clean-bmad has none): (a) inject continuity from
  `../../_artifacts/clean-bmad-workspace/active-context.md` (Test-Path guarded, like the home base), (b) inject the
  artifacts/git gate, (c) inject `docs/repo-map.md`, (d) run the drift check. `-NoProfile`, UTF-8 pinned.
- **Anti-fork note:** `.claude/settings.json` is **workspace-specific**, not vendored from `.agents/` — so authoring
  it here is legitimate (it is NOT overwritten by `/sync-agents`).
- **Skeleton portability:** all paths are `$CLAUDE_PROJECT_DIR`-relative + Test-Path-guarded, so a clone degrades
  gracefully before the active-context exists; the active-context folder name is a clone-time find/replace (README).
- **Offered follow-up (keeps home base ↔ projects in sync):** promote `check-repo-map-drift.ps1` to master
  `.agents/scripts/` and wire the *home base's* own SessionStart hook to the same check, so they don't diverge.

### WS6 — Register + verify + hand off
- `router.md` row: description "aviationChat clone/template" → "AGY quick-start project skeleton (home-base-aligned,
  repo-map indexed)."
- Re-stamp the workspace-standard **Part 1 format checklist** (all 7).
- Update `active-context.md`, append an `_artifacts/INDEX.md` row, write `walkthrough.md` (+ exact git commands for
  both repos) + `task-list.md` snapshot.
- **Update memory** `clean-bmad-workspace-is-template`: it now mirrors the **home-base system DNA + AGY stack**, not
  aviationChat. (Memory currently says "mirror FROM aviationChat-AGY" — that's now stale.)
- Optional: re-run `_routing-canary/` + a cold-route smoke test ("work on a new project") — routing *content*
  changed, structure didn't, so this is offered, not required.

---

## 4. Risks / guardrails
- **Anti-fork:** never hand-edit vendored `.agents/`·`.claude/`·`.opencode/` — fix master + re-sync (§5).
- **`_my_resources/` off-limits:** no edits, no references (its README + AGENTS §8 + repo-map flag already enforce).
- **Keep-stack (D2):** do **not** delete `backend/ frontend/ firebase* firestore* pyproject conftest .env.example`
  — the menu preview said to; your correction overrides it.
- **Clone-time paths:** the skeleton stays internally consistent with literal `clean-bmad-workspace` paths; the
  README's find/replace step is what re-points them at clone time. (Alternative: tokenize to `{{PROJECT_NAME}}` —
  flag if you prefer that; default is literal + README, matching today.)
- **Keep generic (D5):** zero aviationChat product values leak into the skeleton.
- **Git:** I never commit/push — `walkthrough.md` hands you the exact commands (two repos: clean-bmad + home base).

## 5. Out of scope / follow-ups (separate sessions)
- **Prune aviationChat-specific skills/rules from the vendored `.agents/` set** — define a "generic skeleton" sync
  profile at master, then `/sync-agents` into clean-bmad. This is the biggest remaining aviationChat-DNA removal,
  but it's master-level + anti-fork, so it is **not** in this diff.
- **`_claude_artifacts/` full retirement** — pending master pass (verify autopilot engine `$RepoRoot` first).
- **Filling real product code** — never; it stays a skeleton.

## 6. Verification (what I'll paste into the walkthrough)
- `generate_repo_map.py` clean run (exit 0, `_bmad` excluded).
- Grep of authored files for aviationChat-product residue (Sully/Igor, dual-store, regulatory, HR-schema) → expect none.
- Part-1 format checklist: 7/7.
- `git status` (clean-bmad) preview of the changed/renamed files.

---

## ✋ STOP — awaiting your "approved"
No file outside `_artifacts/` will be touched until you approve. Reply **approved** to execute, or tell me what to
adjust (esp. the keep-stack reversal in §0, and the literal-vs-token path choice in §4).
