---
IsArtifact: true
ArtifactMetadata:
  title: System docs truth-sync + always-loaded payload optimization
  type: implementation_plan
  date: 2026-07-09
---

# Implementation Plan — System docs truth-sync + payload optimization

> **Scope.** Fixes driven by two audits run 2026-07-09: (1) the file/folder-system guide + live setup vs the mentor transcript; (2) `_my_resources/docs/master-implementation-plan.md` + the `/1_update-maps`command verification. The command itself verified **correct** — prune/consume is a move-never-delete at every layer (workflow prose, Step-4 approval gate, and `record_map_changes.consume()` which appends to the archive *before* rewriting the live journal). No behavior changes are needed there; everything below is documentation truth-sync plus optional token-payload slimming.

## Goal

Every "source of truth" doc states what is actually on disk; the always-loaded session payload sheds dead weight. No routing-structure redesign — the architecture audit passed.

## Findings driving each phase

| \# | Finding | Where |
| --- | --- | --- |
| F1 | Frontmatter `status: awaiting-go-ahead (Phase A in progress)` — system has been live for weeks; §8 admits the line is historical but the doc never says which sections are record vs current | `_my_resources/docs/master-implementation-plan.md` |
| F2 | §2 tree stale: `_docs\` (retired form; plan actually lives in `_my_resources/docs/`), `_artifacts\_home\` (now `_main/`), session folders list `task-list` (banned by artifacts-always-first), old project names (`aviationChat-AGY`, `clean-bmad-workspace`, `jetChat-AGY`, `ingestion-Pipeline-AC`, `openCode`), `BRKN_Tattoos` missing, `youtube_transcripts\` shown at root (really `_my_resources/youtube_transcripts/`) | same, §0/§2/§3/§4 |
| F3 | §4 root-AGENTS spec drift: numbered 1–7 vs built §1–§8; ALWAYS-LOAD omits `artifacts-always-first.md` | same, §4 |
| F4 | §7 "Progress + immediate next steps" reads as pending work; it is a Phase-A snapshot | same, §7 |
| F5 | `router.md` reference row points at bare `youtube_transcripts/` — no such folder at the lobby root | `router.md` (last row) |
| F6 | Guide doc says 3 SessionStart hooks; `.claude/settings.json` has 4 (+ an undocumented PreToolUse git hook); hook 2 is described as "plan-first gate" but is actually the repo-map drift check (gate text lives inside hook 1) | `_my_resources/diagrams_guides/system/file_folder_structure+maintaining.md` §3/§8 |
| F7 | Guide §7 workspace table stale vs `router.md`: "Ingestion_pipeline_AvCh" vs `RAG_Pipeline_AC`; BRKN_Tattoos (active), AGY_JETCHAT, B-L-WorldWide, NEXGen-Films, OpenChat-Openrouter missing | same, §7 |
| F8 | Guide §1 diagram omits `_my_resources/`, `_bmad/`, `_bmad-output/` (all on disk at lobby root); root `AGENTS.md` §4 table also omits `_bmad/`/`_bmad-output/` | same, §1 + `AGENTS.md` §4 |
| F9 | "9 checks" wording vs code: `check_maps.py` also carries an unnumbered check 2.5 (level-2 INDEX presence) | guide + command doc |
| F10 | 3 skills marked DEPRECATED (`bmad-create-prd`, `bmad-edit-prd`, `bmad-validate-prd`) still load their descriptions into **every** session on every platform | skill surfaces |
| F11 | Root `AGENTS.md` §4 grep-gotcha (\~16 lines) overlaps §6 SEARCH GATE; §6 git-write detail duplicates `git-policy.md` canon — \~25–30 always-loaded lines per session | `AGENTS.md` |
| F12 | Stray `check_maps_output.txt` at repo root; legacy `.agent/` (singular) dir still present — the workspace-standard Appendix retire-list flags it as not-yet-done | lobby root |

## Phases (each independently approvable — say "approved" for all, or name the phases)

### Phase 1 — master-implementation-plan.md truth-sync *(F1–F4)*

`_my_resources/` edit — **authorized by Daniel's direct request this session** ("make sure this is correct and optimized"); outside that request the file stays protected.

1. Frontmatter → `status: built-live — historical rollout record + evolution log (§8)`.
2. Add a 3-line role banner under the title: *§0–§7 = the rollout record (kept verbatim for lineage); the standing spec is* `docs/workspace-standard.md`*; refinements land in §8.* This matches the role `workspace-standard.md` already assigns this doc ("the one-time rollout").
3. In-place fixes for the actively misleading lines only (the tree is small enough to fix, not banner): `_docs\` → `docs\` (+ note the plan's real home `_my_resources/docs/`); `_home` → `_main`; drop `task-list` from the session-folder example; current project names + add `BRKN_Tattoos`; `youtube_transcripts\` → `_my_resources\youtube_transcripts\`.
4. §4: sync the numbered-section list to the built §1–§8 and add `artifacts-always-first.md` to ALWAYS-LOAD.
5. §7 heading → "Progress + immediate next steps (historical — Phase A snapshot; superseded, see §8)".

*Rejected alternative:* full body rewrite to current state — destroys the historical record §8 depends on, high effort, no operational gain (agents take current truth from `workspace-standard.md`).

### Phase 2 — router.md path fix *(F5)*

Reference row: `youtube_transcripts/` → `_my_resources/youtube_transcripts/`. One-line edit.

### Phase 3 — guide-doc sync *(F6–F9)*

In `file_folder_structure+maintaining.md` (also `_my_resources/`, same authorization):

1. §3 + §8: hook table → the real 4 SessionStart hooks (1 continuity+gate+repo-map inject, 2 repo-map drift check, 3 depth-3 nag, 4 maps-journal nag) + the PreToolUse `require-push-approval.py` hook.
2. §7 workspace table: sync names/rows to `router.md` (add BRKN_Tattoos etc.; fix RAG_Pipeline_AC name).
3. §1 diagram: add `_my_resources/`, `_bmad/`, `_bmad-output/` nodes. Mirror one-line mentions into root `AGENTS.md` §4 table (2 rows) — *root-AGENTS edit is outside* `_my_resources`*, flagging explicitly.*
4. Check-count wording → "9 numbered checks + check 2.5 (level-2 INDEX presence)" in guide + command doc, or renumber 2.5 in `check_maps.py` comments (no logic change). Recommend the wording fix (zero risk).

### Phase 4 — always-loaded payload slimming *(F10–F11, optional but recommended)*

1. **Deprecated-skill trio:** first determine the owning layer (BMAD-installed vs vendored in master `.agents/skills/`). If ours → delete at master + `/sync-agents` (purge policy already protects BMAD-owned globals). If BMAD-owned → exclude from the sync surface and note for the v7 upgrade. Report which case it was before deleting anything.
2. **Root** `AGENTS.md` **slim:** move §4's grep-gotcha mechanics to a new `.agents/rules/lobby-search.md`(master), keep the §6 SEARCH GATE line + a pointer; trim §6 git-write detail to pointers at `git-policy.md`. Same dedupe pattern as the 2026-07-06 front-door lean (evolution log §8).
3. Routing structure changed (root `AGENTS.md`) → **re-run** `_routing-canary/` per the standard, and `/1_update-maps` after (structure + INDEX rows).

### Phase 5 — housekeeping *(F12, needs your call — risk gate)*

1. `check_maps_output.txt`: confirm tracked/untracked, then your choice: delete or gitignore.
2. `.agent/` (singular): inventory its contents first and report; retire only what you confirm — this is the standing retire-list item, not a blind delete.

## Execution order

Phase 1 → 2 → 3 (pure doc sync, low risk) → 4 (payload, ends with canary + `/1_update-maps`) → 5 (your calls). Close: ONE `walkthrough.md` with pasted linter/canary output + `## Task Checklist` + `## Your Actions` (per-repo git commands — lobby only, no project repos touched).

## Verification plan

- `python .agents/scripts/check_maps.py --all` exits clean after edits.
- Phase 4: `_routing-canary/` green (`Power.md == "control your agent"`); fresh-session skill list no longer shows the deprecated trio.
- Phase 1/3: re-read edited docs; every path named in them resolves on disk.

## Open questions

1. Phase 4.1: if the deprecated bmad-\* trio turns out BMAD-owned, do you want them force-hidden from Claude surfaces anyway, or wait for BMAD v7?

2. Phase 5.2: want the `.agent/` inventory in this session's walkthrough, or as its own follow-up task?
