---
IsArtifact: true
ArtifactMetadata:
  title: "Generic /1_update-maps (one tool, not per-repo) + a structure contract + context-hygiene prune"
  type: implementation_plan
  date: 2026-06-27
---

# Plan — make `/1_update-maps` generic + add context-hygiene pruning

## Where this came from (Daniel, this session)
- Context files grow forever → want **pruning** of `active-context.md` (+ `INDEX.md`), semi-automated, folded into `/1_update-maps`.
- "3 sessions seems short" → revisit the rolling window.
- "make it work for all 3" (main · aviationChat · fresh-workspace).
- **The pivot:** "can we make it **not per-repo**? It could be generic if we verify all the file structures stay standard… we just need **a document that's a guide for the exact folder/file structure** we use — we have this a little bit already."

Yes. The enabler already half-exists: `_docs/workspace-standard.md`. The move is to harden it into a real **structure contract**, then make ONE tool rely on it instead of vendoring divergent copies.

## What a "session" is (+ the window)
A **session** = one chat from **"pick up" → "hand off."** Each hand-off prepends **one dated block** (`**YYYY-MM-DD: …**`) to `active-context.md` §1 PRIME STATE and appends **one row** to `INDEX.md`. That dated block stack is the part that grows.
- **Recommended window:** keep the **newest ~10 blocks** in PRIME STATE; archive older to `active-context-archive.md`. **Nag only at >12** (hysteresis — not every session). `INDEX.md`: keep newest **~25 rows**, archive older to `INDEX-archive.md`. All tunable constants. (3 was ~⅓ of a day at your cadence — too short.)

## What I found — the structures are NOT yet uniform (this is the real blocker to "generic")
| Standard element | main (home base) | aviationChat | fresh-workspace |
|---|---|---|---|
| repo-map | `_docs/repo-map.md` | `docs/repo-map.md` | `docs/repo-map.md` |
| continuity `active-context.md` | `_artifacts/_main/…` | **none local**; BMAD `_bmad-output/active-context/…` is what §6 cites | **none local**; home-base bucket `_artifacts/clean-bmad-workspace/…` |
| `INDEX.md` (session ledger) | `_artifacts/INDEX.md` | `_artifacts/INDEX.md` | **none local**; uses home-base bucket |
| artifacts dir | `_artifacts/` (buckets) | `_artifacts/` (project-local) | **`_claude_artifacts/`** (OLD) + home-base bucket |
| open_tasks | `_my_resources/open_tasks/` ✅ | `_my_resources/open_tasks/` ✅ | `_my_resources/open_tasks/` ✅ |
| `check_maps.py` | `.agents/scripts/` | `.agents/scripts/` + `scripts/` | **MISSING (both)** |
| `generate_repo_map.py` | `.agents/scripts/` | both | **only `scripts/`, not `.agents/`** |

Two kinds of divergence: (1) **accidental** (fresh-workspace missing scripts; `_docs` vs `docs`) — fixable; (2) **by-design** ("artifacts go where you work FROM" → home base uses `_artifacts/<bucket>/`, a project uses project-local `_artifacts/`). A generic tool must encode that home-vs-project **mode**, not pretend it away.

## Plan (4 parts)

### Part A — Author the **structure contract** (the doc the tool trusts)
Upgrade `_docs/workspace-standard.md` (its "Supporting files" + "Format checklist" are the seed) with a single **canonical path table**: for every standard element (repo-map · active-context · INDEX · open_tasks · artifacts · `.agents/scripts` · `opencode.json` …), the **exact path**, and where it legitimately differs, the **home-base mode vs project mode** rule. This becomes THE contract `/1_update-maps` and `check_maps.py` rely on.

### Part B — Make the tooling generic (one source, runs anywhere)
- `check_maps.py`: it already takes `--root`. Make it **mode-aware** (detect home-base vs project by presence of `Projects/`), resolve the standard paths from the contract (handle `_docs/` vs `docs/`), and add a **structure-conformance pre-check** (does this workspace have the standard files in the standard places? — the "verify they stay standard" Daniel asked for).
- `/1_update-maps` workflow: drop the "LOBBY only" framing → **"runs against any conformant workspace"** (`--root <path>` / target a `Projects/<name>/`). One workflow, one script.
- **Add the prune phase** (Part D) into that one workflow + a non-fatal size **hint** in the script.

### Part C — Conform the 3 workspaces to the contract
Verify each against Part A; fix deviations: give **fresh-workspace** the missing `check_maps.py` + `.agents/scripts/generate_repo_map.py` (and decide `_claude_artifacts/`→`_artifacts/`); reconcile the `_docs`/`docs` + active-context-location questions per the decisions below. (This directly advances todo **item 3** "fix clean-workspace mirroring.")

### Part D — Context-hygiene prune (the original ask)
In the one workflow, add a **"Context hygiene"** step: count session blocks in the target's `active-context.md`; if over the window, propose archiving the oldest into `active-context-archive.md` (create if missing); same for `INDEX.md` rows → `INDEX-archive.md`. Approval-gated (the workflow already STOPs before edits). `check_maps.py` gains a non-fatal `[context hygiene]` hint when a file is over the soft cap. Session folders under `_artifacts/` are **disk-only** (not loaded into context) → lowest priority, archive-on-epic-close at most.

## Decisions I need from you (recommendations in **bold**)
1. **Central vs vendored tool.** **Recommend: ONE canonical tool at the home base**, invoked with `--root Projects/<name>` to target any workspace; projects keep a *byte-identical synced* copy only for standalone-clone use (never a divergent one). Alternative: pure-central (no project copies at all). — *Pick: central+synced (default) / pure-central?*
2. **repo-map path.** Standardize on **`docs/repo-map.md`** everywhere (home base moves `_docs`→`docs`), OR keep `_docs/` at home base and make the tool **auto-detect both**. **Recommend: auto-detect both** (less invasive; the contract documents both as allowed). — *Pick: auto-detect (default) / standardize the name?*
3. **Canonical `active-context.md` per project.** For the **prune/pickup** continuity file, is it the **project-local `_artifacts/active-context.md`** (create it; the §9 model) or the **BMAD `_bmad-output/active-context/active-context.md`** (what §6 cites today)? **Recommend: the `_artifacts/` continuity one is canonical for pickup/prune; the BMAD one stays BMAD's sprint state** — but this is the tangle behind item 3, so your call. — *Pick?*
4. **Window numbers.** keep **~10** blocks / nag at **12**; INDEX keep **~25**. — *OK or adjust?*

## Out of scope (separate todos)
- todo item 2 (opencode/gemini mirroring) and item 4 (mobile/desktop rules) — not here.
- Deep fresh-workspace cleanup beyond what update-maps needs (full `_claude_artifacts/` retirement) — only the slice item 3 needs.

## Verification
- `check_maps.py --root .` (home base) and `--root Projects/AGY_AVIATIONCHAT` and `--root Projects/Fresh_Workspace_BMAD` all run, conformance-check, and emit the prune hint where due.
- Dry-run the prune on `_artifacts/_main/active-context.md` (the longest one): proposes archiving oldest blocks, keeps newest ~10, writes `active-context-archive.md` — approval-gated.

## Git
No commits by me. Each touched repo (home base; aviationChat; fresh-workspace) gets its exact command in the closing `walkthrough.md`.
