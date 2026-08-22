---
IsArtifact: true
ArtifactMetadata:
  title: Maps reconcile + artifact-rule verify + opencode .agent→.agents pointer fix (main, aviationchat, clean-bmad)
  type: implementation_plan
  date: 2026-06-26
---

# Plan — Maps + artifact rules + opencode pointer fix across 3 repos

**Scope:** `main` (lobby), `Projects/aviationChat-AGY`, `Projects/clean-bmad-workspace`.
Three asks, folded into one pass:
1. `/1_update-maps` reconciliation for each.
2. Verify the artifact rule is fixed & in place for all.
3. Verify the opencode `.agent` → `.agents` pointer fix Daniel just did.

> These are **3 separate git repos**. The lobby `/1_update-maps` is lobby-only by design; the project
> reconciliations use each project's own vendored tooling. Nothing here commits/pushes — git commands handed off.

---

## PART A — Maps & INDEX (findings; edits gated)

| Repo | Linter | State | Action |
|---|---|---|---|
| **main (lobby)** | `python .agents/scripts/check_maps.py` → **exit 0, clean** | maps + INDEXes agree with disk; working tree clean | No map/INDEX edits. Only gap: **no baseline anchor** (`_docs/.maps-state.json` missing). Set it: `python .agents/scripts/check_maps.py --set-anchor`. |
| **aviationchat** | `python scripts/check_maps.py` (vendored, from project root) → **DRIFT** | **AUTO block STALE** — `epic-15/` on disk, not in map. CURATED paths / folder coverage / INDEX all clean. No anchor. | Regenerate AUTO: `python scripts/generate_repo_map.py --ignore _bmad,_my_resources --mode content`; add a curated `epic-15` routing line if it warrants one (judgment); set anchor. |
| **clean-bmad** | none vendored — has `scripts/generate_repo_map.py` + `check-repo-map-drift.ps1` but **no `check_maps.py`** | map has AUTO sentinels; full lint not possible | Regenerate AUTO with `scripts/generate_repo_map.py`; manual INDEX/curated reconcile. **Decision:** optionally vendor `check_maps.py` from master for parity. |

**Bug flagged (aviationchat):** running the linter via `.agents/scripts/check_maps.py` resolves its root to
`.agents/` and looks for `.agents/docs/repo-map.md` (wrong). The vendored `scripts/check_maps.py` is the
correct entrypoint. Same root-resolution gotcha noted for the generator in the lobby workflow.

---

## PART B — Artifact rules (VERIFIED — no action)

`.agents/rules/artifacts-always-first.md` is present and **byte-identical** in all three repos:
- md5 `404d27dddd797eb0c8fa5898701c551a`, 172 lines, in each `.agents/rules/`.
- Mirrors (`.claude/`, `.opencode/`) do **not** copy rules — rules surface via `@.agents/…` pointers from
  `AGENTS.md`/`CLAUDE.md` + commands. That's by design, not drift.

✅ Artifact rule is fixed and in place for all three. Nothing to change.

---

## PART C — opencode `.agent` → `.agents` pointer fix

Master dir is `.agents/` (plural) in all three. Broken `@.agent/` (singular) pointers don't resolve.

| Repo | `.agents/` master | `.claude/` | `.opencode/` | Status |
|---|---|---|---|---|
| **aviationchat** | 0 | 0 | 0 | ✅ Daniel's fix fully landed |
| **main (lobby)** | 39 | 21 | 23 | ❌ still broken |
| **clean-bmad** | 39 | 24 | 25 | ❌ still broken |

Confirmed mechanical: lobby `@.agent/workflows/…` ↔ aviationchat (fixed) `@.agents/workflows/…`.

### Proposed fix (on approval)
1. Rewrite `@.agent/` → `@.agents/` at the **`.agents/` MASTER** in `main` and `clean-bmad`.
2. Re-sync mirrors so `.claude/` + `.opencode/` inherit the fix (`/sync-agents` per repo — lobby fixes
   master then syncs; project syncs its own master to its mirrors).

### GUARDRAILS (why this is NOT a blind sed)
- **Do NOT touch the real `.opencode/agent/` (singular) directory paths** — that's opencode's own
  agent-definitions dir. Only `@.agent/{workflows,rules,skills,commands,templates}` and `.agent/gemini.md`
  style *toolkit pointers* are the target. (Master files have no `opencode/agent/` refs — confirmed — but the
  `.opencode/` mirror does; scope the replace to `@.agent/` and ` .agent/`, never `opencode/agent/`.)
- **Exclude** binaries/artifacts: `*.pyc`, `.gitnexus/lbug`.
- **`.agents/scripts/generate_doc_graph.py`** contains a `.agent/` string — verify whether it's a pointer to
  fix or a path-literal the script scans before changing it.

---

## Execution order (after "approved")
1. PART C master fixes (main, clean-bmad) → re-sync mirrors.
2. PART A: aviationchat AUTO regen + curated line; clean-bmad AUTO regen; set anchors.
3. Re-run linters to confirm clean.
4. `walkthrough.md` + `task-list.md`; hand off git commands per repo (never commit myself).

## Open questions
- clean-bmad: vendor `check_maps.py` for parity, or leave generator-only?
- aviationchat: does `epic-15/` warrant a curated routing line, or AUTO-only?
- Fix mirrors via `/sync-agents`, or also hand-edit committed mirror files directly this pass?
