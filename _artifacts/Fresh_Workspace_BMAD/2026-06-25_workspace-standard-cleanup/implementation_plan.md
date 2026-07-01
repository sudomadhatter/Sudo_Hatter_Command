---
title: clean-bmad-workspace — Workspace-Standard Cleanup + Repo-Map Index
type: implementation_plan
workspace: clean-bmad-workspace
date: 2026-06-25
status: AWAITING-APPROVAL
owner: Daniel
author: Claude (Opus 4.8)
related:
  - _docs/workspace-standard.md            # the "new file strategy" (the spec we conform to)
  - _docs/master-implementation-plan.md    # the rollout this fits into (Phase B)
  - _artifacts/clean-bmad-workspace/active-context.md
  - _artifacts/clean-bmad-workspace/2026-06-24_agents-format-conversion/   # prior partial conversion
---

# clean-bmad-workspace — Workspace-Standard Cleanup + Repo-Map Index

## 0. Goal (Daniel's ask, restated)
Assess whether it is **safe** to apply the new file strategy (`_docs/workspace-standard.md`) to
clean-bmad-workspace, clean up stale documents, conform the workspace to the standard, and **build the
navigation index** ("index all the folders and files") so the workspace is ready to work in.

**Verdict up front: SAFE to proceed.** It is a low-risk target — a structural *skeleton* (backend = 7
files, frontend = 0 `.ts/.tsx`), no real product code to break, already half-converted, its own git repo,
clean working tree. The risk is not "breaking code"; it's **scope discipline** (don't fork vendored files,
don't bake domain values, don't move the autopilot engine's artifact paths carelessly).

---

## 1. ⚠️ BLOCKER TO CONFIRM BEFORE ANY EDIT — "off-limits / another team"
Three of your own canonical docs flag clean-bmad as off-limits:
- `_docs/workspace-standard.md` (Appendix retire-list — "in off-limits projects")
- `_my_resources/diagrams_guides/system/gitnexus-usage-guide.md` (today, 2026-06-25): *"Never index: …
  clean-bmad-workspace (another team, off-limits)."*
- `_artifacts/INDEX.md` row 2026-06-24: *"BLOCKED: clean-bmad off-limits (other team)."*

**This contradicts the live reality:** you describe it as *your* aviationChat mirror, it was already
converted (`2026-06-24_agents-format-conversion`), and memory `clean-bmad-workspace-is-template` calls it
*your* template. Most likely the "another team" note is stale/incorrect (or referred only to **GitNexus
indexing**, a license-hygiene call — separate from editing the docs).

**Action:** Daniel confirms clean-bmad is his to edit. If yes, those three stale notes get corrected as a
small follow-up (home-base files, not part of the clean-bmad diff). **No clean-bmad edits happen until this
is confirmed.**

---

## 2. Assessment — current state vs the standard (the gap)
Format checklist from `_docs/workspace-standard.md` Part 1, scored against clean-bmad today:

| Standard item | Status | Note |
|---|---|---|
| `CLAUDE.md` + `GEMINI.md` one-line adapters | ✅ | Both clean, no placeholders |
| `AGENTS.md` numbered (1–9) + Map/Mission/Support + routing table + up-route | ⚠️ Partial | Has MMS + table + up-route, but **not numbered**; **references the dead `_claude_artifacts/` store**; missing ARTIFACTS-PROTOCOL + NAMING + GATES + PERSISTENCE-numbered sections |
| `.agents/` vendored; `opencode.json` points at it | ✅ | Done in prior conversion |
| `docs/repo-map.md` present + current | ❌ **MISSING** | This is the "index" you asked for. `docs/` has only `skills-registry.md` + `tech-stack.md` |
| `_artifacts/<ws>/active-context.md` exists | ✅ | At home base |
| Registered in root `router.md` | ⚠️ | Row exists but status is stale: *"first conversion (next)"* |
| Vendored `docs/workspace-standard.md` | ❌ **MISSING** | |
| `generate_repo_map.py` vendored in `.agents/scripts/` | ❌ **MISSING** | Exists in **master** `.agents/scripts/`; not synced into clean-bmad (only `new-project.ps1` + `sync-agents.ps1` are) |

**Stale documents found:**
- `_claude_artifacts/` — dead store (1 file: `README.md`). The standard retired this; artifacts live at
  home-base `_artifacts/clean-bmad-workspace/`. Referenced in: `AGENTS.md`, `scripts/autopilot-dev-story.ps1`,
  and **vendored** copies under `.claude/` + `.opencode/` (5 commands each), `settings.json`(+`.local`), one
  `SKILL.md`. → see §3 Workstream 4 for the fork-safe handling.
- `_bmad-output/` — only 2 files (`project-context.md`, `active-context/active-context.md`), both
  `{{PLACEHOLDER}}` skeletons (the BMAD template blanks).
- `README.md`, `.antigravity/mcp.json` — also carry `{{PLACEHOLDER}}` tokens.

> **`_01_My/` is NOT a stale-doc target — it is Daniel's PROTECTED personal area (per his review).** It
> becomes `_my_resources/` (§3 WS5) and is treated as a risk zone, not cleaned/triaged. See the guardrail.

**Placeholder decision (recommended):** Keep clean-bmad **GENERIC** — its own `AGENTS.md` says *"keep it
generic… it's the reference sandbox, not a product,"* and memory marks it as the template. So structural
`{{PLACEHOLDER}}` blanks in `_bmad-output/` + `README.md` **stay** (they are the template's fill-in points).
We only remove **dead/duplicate** docs, not the template skeleton. (If you'd rather make it a concrete working
sandbox, that flips placeholder handling — flag it and I'll adjust.)

### 2a. ⛔ NEW HARD GUARDRAIL (Daniel's review) — the `_my_resources/` personal area
- `_01_My/` is renamed to **`_my_resources/`** to match the home base, and **everything in it is treated as
  Daniel's personal brainstorming — a RISK ZONE: possibly stale, NOT authoritative.**
- **Agents must NOT edit any file under `_my_resources/` unless Daniel explicitly tells them to** (the
  one-time rename/reorg in WS5 is that explicit instruction; after it, hands off).
- **Agents must NOT reference / pull context from anything in `_my_resources/` unless Daniel links the
  specific document.** It is not auto-context.
- This is enforced in three places: the new `_my_resources/README.md`, the `AGENTS.md` GATES section, and a
  `docs/repo-map.md` flag so the area shows up as "personal · do-not-touch · do-not-reference."

---

## 3. Plan of work (proposed — execute only after approval)

**Scope boundary (important):** clean-bmad's `.claude/` + `.opencode/` command/skill files are **vendored
copies** synced from master `.agents/`. Per the anti-fork rule, those are **not** edited here — they're fixed
at master + re-synced as a separate home-base propagation task. This plan edits only files **authored to
clean-bmad** (`AGENTS.md`, project-local `scripts/`, `docs/`, `README.md`, `_01_My/`) plus generated output.

### WS1 — Conform `AGENTS.md` to the 9-section standard
- Renumber to: `1 ROOT LAW · 2 START HERE · 3 MAP/MISSION/SUPPORT · 4 ALWAYS-LOAD · 5 ARTIFACTS PROTOCOL ·
  6 ROUTING TABLE · 7 NAMING · 8 GATES · 9 PERSISTENCE`.
- Drop `_claude_artifacts/` from the MAP; point PERSISTENCE at home-base `_artifacts/clean-bmad-workspace/`.
- Update the MAP: `_01_My/` → `_my_resources/` (personal · protected).
- Add the mandatory ARTIFACTS-FIRST gate text + `artifacts-always-first.md` to ALWAYS-LOAD.
- **Add to §8 GATES — the `_my_resources/` guardrail (§2a):** "`_my_resources/` is Daniel's personal area.
  Do NOT edit any file in it unless Daniel explicitly says so. Do NOT reference its contents unless Daniel
  links the specific document. Treat everything in it as personal brainstorming that may be stale."
- Preserve the existing routing table content (it's good) — just re-home it under §6.

### WS2 — Vendor the two missing standard files
- Copy `_docs/workspace-standard.md` → `docs/workspace-standard.md` (vendored, never hand-edited).
- Sync `generate_repo_map.py` into `.agents/scripts/` (run `/sync-agents` for clean-bmad, or copy the master
  script). Hand Daniel the command — no auto-commit.

### WS3 — Build the index `docs/repo-map.md`  ← the headline deliverable
- Run `generate_repo_map.py` against clean-bmad (read-only generation) to produce the AUTO body
  (`<!-- REPO-MAP:AUTO-START -->…END`), with the collapse rule applied to skeleton dirs.
- Hand-author the CURATED header (`<!-- REPO-MAP:CURATED-START -->…END`): the "to find X → look here" routing
  table + the "which doc to read when" knowledge map. This is the navigable index you work from.
- **Flag `_my_resources/` in the curated header** as "personal · do-not-edit · do-not-reference unless Daniel
  links it" so the index itself enforces the §2a guardrail.

### WS4 — Retire the dead `_claude_artifacts/` store (fork-safe)
- **Locally authored** refs → repoint to home-base `_artifacts/`: `AGENTS.md` (done in WS1),
  `scripts/autopilot-dev-story.ps1` (project-local by design — but **verify the `$RepoRoot` path binding
  before moving any artifact path**, per the standard's appendix warning), and delete/relocate
  `_claude_artifacts/README.md`.
- **Vendored** refs (the 10+ `.claude`/`.opencode` command + skill + settings files) → **NOT touched here.**
  Logged as the master-level retire-list propagation task (already on the standard's retire-list). Recommend
  doing that as its own home-base session so it propagates to all projects at once.

### WS5 — Personal area: rename `_01_My/` → `_my_resources/` + protect it (Daniel's review, CONFIRMED)
His personal docs are **not** triaged, deleted, rewritten, or reorganized. The only edit is the one-time
parent-folder rename; then the area is locked behind the §2a guardrail.
- **Rename the parent only:** `_01_My/` → `_my_resources/`. **Keep all subfolders exactly as they are**
  (`Agentic_Loops/`, `Docs/`, `Visual_Diagrams/`) — no remapping, contents moved verbatim. (Daniel's call,
  2026-06-25.)
- **Add `_my_resources/README.md`** explaining *what these are*: Daniel's personal docs — brainstorming,
  PRPs, loops, diagrams. Personal use only, **may be stale, NOT authoritative**. Use caution. **Agents may
  not edit anything here unless Daniel explicitly says so; do not reference anything here unless Daniel links
  the specific doc.** Always check against live project files.
- **Knowledge-architecture note (Daniel's intent):** `docs/` is the **agent's verified reference shelf**
  (incl. BMAD docs to reference, and `_artifacts/` chats it can dig into when needed). `_my_resources/` is
  Daniel's **personal staging** — he will *slowly* promote files from `_my_resources/` → `docs/` himself,
  only once he's verified they're current. Agents pull reference context from `docs/` + `_artifacts/`, never
  proactively from `_my_resources/`.
- **Do NOT** archive/delete the "superseded" autopilot doc or any other personal file — leave it as-is.
- Root `router.md` row → update status `"first conversion (next)"` → `"converted · standard-compliant"`.

### WS6 — Register + verify + hand off
- Stamp the Part-1 format checklist.
- Re-run `_routing-canary/` (AGENTS.md renumber = a routing-structure change → standard requires it).
- Cold-route smoke test: "work on clean-bmad-workspace" lands in the folder.
- Write `walkthrough.md` (+ "Your Actions" with the exact git command), `task-list.md` snapshot, update
  `active-context.md`, append `INDEX.md` row.

---

## 4. Risks / guardrails
- **`_my_resources/` is OFF-LIMITS (Daniel's review):** no agent edits there except the one-time WS5
  rename/reorg he authorized; no referencing its contents unless he links a specific doc. Personal, may be
  stale, not authoritative.
- **Anti-fork:** never hand-edit vendored `.claude/`·`.opencode/` copies — fix master + re-sync (WS4 scope).
- **Autopilot engine:** do not move its artifact paths without verifying the `$RepoRoot`/`$PSScriptRoot`
  binding (appendix warning) — docs and engine move together or not at all.
- **Keep generic:** no aviationChat domain values leak into this template/sandbox.
- **Git:** I never commit/push — every change ships with the exact command for Daniel in `walkthrough.md`.
- **GitNexus is N/A here:** clean-bmad is not indexed and is off-limits to index; it has no real code to
  graph. Code connectivity lives in `AGY_AVIATIONCHAT` (indexed) — see chat note.

## 5. Out of scope (explicitly)
- Master-level `_claude_artifacts/` → `_artifacts/` propagation across all projects (own session).
- Converting aviationChat itself (Phase C — last, per master plan).
- Filling clean-bmad with real product code (it stays a skeleton template).
