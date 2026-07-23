---
IsArtifact: true
ArtifactMetadata:
  title: Two-Team Operating System — RAG_Pipeline_AC conversion, authoring skills, BMAD-lite, SOP, Drive wiring
  type: implementation_plan
  date: 2026-07-22
---

# Implementation Plan — Two-Team Operating System (App ↔ Curriculum Pipeline)

## Goal

Make `Projects/RAG_Pipeline_AC/` a first-class house workspace — same rules and file/folder structure as the lobby and `AGY_AVIATIONCHAT` — and make it the **explicit owner of curriculum authoring** (RKP manifests, quiz banks) via project skills hard-grounded in ACS + FAA source documents only. Bind the two teams with one SOP document, add a lean BMAD layer for tracking, and wire the Google Drive "ACS Modules" folder in as the authoring station. One parity fix outside the pipeline: vendor `operator-profile.md` into AGY.

## Decisions this plan encodes (Daniel, 2026-07-22)

1. **Manifest + quiz creation is owned by the ingestion pipeline project** → codify as skills that verify everything against ACS and FAA documents ONLY.
2. **House file/folder structure gets implemented in the pipeline project** (it is confirmed absent).
3. **Drive "ACS Modules" folder is agent-accessible** — sync/pull the ACS docs from there.
4. **operator-profile.md lives in the command center AND AviationChat.** (Lobby already has it, uncommitted since 2026-07-22; AGY is the gap.)
5. **GitNexus on the pipeline: recommend DROP** — pending Daniel's confirmation (Open Question 1).

## Audit findings this plan rests on (2026-07-22 session, this folder's chat)

Three-station flow confirmed: Drive `AVIAIONCHAT/ACS Modules` (authoring, heavy media; folder id `1eiHjhYBd1bb2h7-M-8DTz3DjxGYVs5-S`) → pipeline repo (transform + gated ingest → DB1/DB2/Firestore) → app (consumes only). Pipeline repo is pre-conversion era: no `.agents/`, stale + app-polluted `.claude/rules/` + `.agent/rules/`, retired `_claude_artifacts/`+`_opencode_artifacts/`, full-size `CLAUDE.md`, opencode-protocol `AGENTS.md`, ghost `/1_ccps_*` commands, single `main` branch, no BMAD. Grounding sources already on disk: `docs/private_airplane_acs_6.pdf` (+ instrument/commercial ACS), `pipeline/curriculum/1 ACS Curriculum Key.json`, FAA PDFs in `pipeline/library/new/`(all PDFs gitignored by design). App repo carries an unowned mirror of 48 manifests + 48 quiz banks at `_docs/specialist_lesson/`. App `docs/` has zero pipeline references. Podcasts (34) orphaned — no ingest script. 13 lessons cite sources not in DB2. Areas II/IV/V/VIII/XII not started.

---

## Phases

### P0 — Rule parity: operator-profile → AGY (small, independent)

| Action | File |
| --- | --- |
| Copy lobby master rule (byte-identical) | `.agents/rules/operator-profile.md` → `Projects/AGY_AVIATIONCHAT/.agents/rules/operator-profile.md` |
| Add floor-tier INDEX row (mirror lobby wording) | `Projects/AGY_AVIATIONCHAT/.agents/rules/INDEX.md` |
| Prepend to ALWAYS-LOAD §4 (mirror lobby §3 wording) | `Projects/AGY_AVIATIONCHAT/AGENTS.md` |

Lobby side is already done (2026-07-22 session, uncommitted) — commit command goes in the walkthrough.

### P1 — Pipeline structure conversion (house standard)

All paths relative to `Projects/RAG_Pipeline_AC/` unless noted.

| Action | Detail |
| --- | --- |
| Branch model: single `main` — **by design** (Daniel, review memo 2026-07-22) | Workhorse repo, deployed nowhere; the live risk is the DATA stores, guarded by the P2 constitution gates — not branches. New AGENTS.md GATES states "single-branch by design" so no future parity pass re-adds `main_debug`. Push-approval hook still deploys (any agent commit on `main` prompts, per desktop git policy) |
| `CLAUDE.md` → 3-line pointer | Replace full doc with the standard "Read AGENTS.md" pointer |
| Root `GEMINI.md` (NEW) → pointer | Same pointer pattern; `.gemini/GEMINI.md` content superseded by new AGENTS.md |
| `AGENTS.md` → rewrite as Layer-2 workspace map | ROOT LAW (pipeline mission + Jobs/Woz) · START HERE · MAP/MISSION/SUPPORT · ALWAYS-LOAD (constitution, karpathy, artifacts-always-first, operator-profile) · ROUTING TABLE (authoring / ingesting / verifying / state-map / SOP rows) · source-of-truth table · GATES (git + pipeline hard stops pointer) · PERSISTENCE |
| Vendor `.agents/` toolkit | `/sync-agents -Target Projects/RAG_Pipeline_AC` (additive; deploys rules/commands/skills/scripts + `.agents/hooks/require-push-approval.py` → `.claude/hooks/`; populates `.claude/` + `.opencode/` platform-filtered) |
| Delete forked rule dirs | `.claude/rules/` (14 stale/polluted files) + `.agent/` (old Antigravity dir) — AGY-conversion precedent |
| Consolidate artifacts | `git mv` `_claude_artifacts/*` + `_opencode_artifacts/*` → `_artifacts/` (+ standard `_artifacts/README.md` + `INDEX.md`); delete empty old dirs |
| Seed `_my_resources/open_tasks/` | `todo_list.md` (+ protected-area README) — READ-ONLY carve-out per house standard |
| Generate `docs/repo-map.md` | Standard generator; `docs/.maps-state.json` already exists (tooling half-expects this home); run `check_maps.py --root` conformance |
| Purge ghost commands | Old `/1_ccps_*` tables die with the AGENTS/CLAUDE rewrite; vendored command set replaces them |
| Strip GitNexus governance (pending OQ1) | Remove `gitnexus:start/end` blocks from `AGENTS.md`+`CLAUDE.md`; remove repo from `~/.gitnexus/groups/` ac-stack `group.yaml` + registry; delete local `.gitnexus/` (incl. 51MB `lbug` junk) |
| (Optional, OQ4) root `.mcp.json` | md-feedback wiring like lobby/AGY/Fresh |

### P2 — Pipeline-specific rules (project-local additions in `.agents/rules/`)

| Action | File |
| --- | --- |
| NEW `constitution.project.md` — data-side hard stops | never `--execute` without a reviewed dry-run in the same session · never commit generated import manifests (`curriculum.jsonl`, `library_metadata.jsonl` — partial manifest + FULL reconciliation wipes the live store) · `*.pdf` never enters git · an ingest is "done" only with `probe_bridge_hop` ≥1-hit proof + `pytest src/tests/` green · citation changes require Daniel's verification · Drive = authoring surface, repo `.md` = machine truth (no silent master overwrites outside a pull session) |
| KEEP (refresh) `credential-resolution.md` | Project-local; pattern already matches (`auth_keys/` root + env override) — refresh wording, drop app-repo references |
| DROP app-only rules | `voice-agent-architecture`, `useEffect-dep-array-stability`, `prompt-tdd`, `adk_file_formating`, `pyrefly-paths` (no pyrefly here) — vanish with the forked-dir deletion; not re-added |
| Update vendored `INDEX.md` | Add project-local rows (constitution.project, credential-resolution) |

### P3 — Curriculum authoring skills (project-local `.agents/skills/` → mirrored `.claude/skills/`)

| Skill (NEW) | Built from | Core contract |
| --- | --- | --- |
| `rkp-manifest-authoring` | `_docs/instruction_docs/rkp_creation_guide.md` + `bridge_key_guide.md` | 3–6 RKPs w/ title/why/knowledge/acs_elements/far_references/bridge_keys + 500–1000-word lesson_overview; bridge keys must exist in the DB2 24-tag vocabulary; `knowledge_formatted` stays empty (script-owned) |
| `quiz-bank-authoring` | `_docs/instruction_docs/quiz_authoring_guide.md` | 8 Qs per lesson (2 legal / 2 safety / 2 application / 2 risk_management) authored FROM the RKP `knowledge`; `correct` flag, no positional rule (retired "SJT answer is D" explicitly named as dead) |
| `faa-grounding-gate` | Adapted from AGY's `regulatory-verification-protocol` skill | Every factual claim traces to a named permitted source: `docs/private_airplane_acs_6.pdf`, `pipeline/curriculum/1 ACS Curriculum Key.json`, FAA docs in `pipeline/library/` / DB2 vocabulary — NEVER model memory; unverifiable ⇒ flag for Daniel, never invent; both authoring skills invoke this gate |
| Surgical stale-doc fixes | `_docs/docs_prds/asset_registry.md` (delete the two stale "SJT always D" rows) · `_docs/instruction_docs/curriculum_lifecycle.md` §4/§5 (phantom `reimport_with_metadata.py` → `reimport_db1_keys.py`; `scripts/ingest_quiz_banks.py` → `src/gcp/`) | Keeps guides from contradicting the new skills |

### P4 — BMAD-lite

| Action | Detail |
| --- | --- |
| Install `_bmad/` | HAND-COPY from `Projects/Fresh_Workspace_BMAD/_bmad/` (house memory: never via /sync-agents); includes guard TOMLs — verify their artifact paths say `_artifacts/` |
| Seed `_bmad-output/` | `project-context.md` (pipeline-adapted: mission, stores, gated-tools table, sources of truth) · `active-context/active-context.md` · `implementation-artifacts/sprint-status.yaml` |
| Seed the real backlog | Epics = ACS Areas (II, IV, V, VIII, XII) + one infra epic (podcast ingestion script · 13 reference-only lessons / DB2 source additions · Phase-2 `data/` merge) |
| Story definition-of-done | Uses the pipeline's OWN gates (pytest 33 · dry-run reviewed · `--execute` · `probe_bridge_hop` · `generate_state_map.py --live` counts) — NOT app-style test tiers; no ATDD/TEA gate here |

### P5 — The SOP + cross-links

| Action | File |
| --- | --- |
| NEW SOP (canonical) | `Projects/RAG_Pipeline_AC/_docs/SOP_curriculum_operations.md` — the three stations & ownership · per-lesson lifecycle checklist w/ owner per step (Daniel: author, verify citations, approve; agent: everything mechanical) · Drive conventions ("Area N Task X PPL" naming, Doc → `.md` export, folder id) · heavy-file policy (Drive / local-gitignored / GCS / never-git) · bridge-key 3-layer contract · app-side consumption map · mirror policy (OQ2) · debt register (podcasts, missing Areas, 13 fallback lessons, docs/ vs \_docs/) |
| Pipeline `AGENTS.md` routing row → SOP | (written as part of the P1 rewrite; SOP row lands here) |
| AGY routing row | `Projects/AGY_AVIATIONCHAT/AGENTS.md` §6: "Curriculum content / manifests / quizzes / FAA sources → upstream `Projects/RAG_Pipeline_AC/` + its SOP" |
| Lobby router row | `router.md`: pipeline status `pending` → `converted`, description gains "curriculum ops (SOP)" |
| Mirror policy (OQ2) | NEW `Projects/AGY_AVIATIONCHAT/_docs/specialist_lesson/README.md`: reference-only, may lag, source of truth = pipeline repo |

### P6 — Drive wiring smoke test (no files; proof)

Pull one master (e.g. "Area 6 Task B PPL.md") from Drive `ACS Modules` via the connector, diff against `curriculum_components/curriculum_modules/`, report identical-or-drift in the walkthrough. This proves the "agent pulls new Area docs on request" flow the SOP documents.

---

## Execution order

P0 → P1 → P2 → P3 → P4 → P5 → P6. P0 is independent (can run any time). Natural review checkpoints after P1 (structure visible) and P3 (skills reviewable) — I'll pause and show state at each rather than run the arc silently.

## Open questions (answer at approval)

1. **GitNexus:** drop from the pipeline entirely (strip blocks + deregister from ac-stack + delete `.gitnexus/`)? My recommendation: yes — 4k-symbol script repo, shallow call graphs; its real risk is data-side (live-store wipes) which a code graph can't see; index rots per-machine; and cross-repo tracing adds \~nothing because the repos share JSON contracts, not imports.
2. **App-repo mirror** (`_docs/specialist_lesson/` 48+48): keep as reference-only + README banner (my rec), or delete the mirror?
3. **BMAD source:** hand-copy from `Fresh_Workspace_BMAD` (house discipline) — confirm.
4. **md-feedback MCP** into the pipeline (`.mcp.json`, 1 file) — want it?
5. **SOP home:** `_docs/SOP_curriculum_operations.md` in the pipeline repo (canonical) + pointer rows elsewhere — OK?

## Verification plan

- `check_maps.py --root Projects/RAG_Pipeline_AC` → conformance exit 0; repo-map drift clean.
- `python -m pytest src/tests/ -q` still 33 green (structure work must not touch `src/`).
- Shared rules md5-match the lobby master set (spot-check like prior parity sessions); zero `_claude_artifacts`/`.agent/` references left outside frozen history.
- Skills resolve in a pipeline-cwd Claude session (`/` menu) after restart; BMAD `bmad-help` resolves.
- P6 Drive pull result pasted in the walkthrough.
- Ghost-check: no `/1_ccps_*` references anywhere in the repo.

## Deliberate non-changes

- `docs/` vs `_docs/` split stays (tooling auto-detects map home; ACS PDFs stay in `docs/`, library in `_docs/`) — flagged in the SOP debt register, not churned now.
- No content/data work: no ingests, no store writes, no STATE `--live` regen required by this plan.
- App repo untouched except P0 + the P5 routing row + mirror README.
- `_my_resources/` untouched everywhere (protected).
- Pipeline `src/` code untouched (podcast ingest script etc. become BMAD stories, not this session).
