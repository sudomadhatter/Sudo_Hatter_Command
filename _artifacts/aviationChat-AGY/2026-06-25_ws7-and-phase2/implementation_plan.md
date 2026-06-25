---
IsArtifact: true
ArtifactMetadata:
  title: "WS7 home-base drift hook + aviationChat Phase 2 (collapse & reconcile)"
  type: implementation_plan
  date: 2026-06-25
---

# WS7 (home base) + aviationChat Phase 2 — implementation plan

Two workstreams in one session, per Daniel's "ws7 along with the next phase."
- **Part A = WS7 (home base):** give the home base its own repo-map + drift hook (the open follow-up).
  Artifacts: this folder (`_artifacts/_home/…`).
- **Part B = aviationChat Phase 2 (project work):** collapse the duplicate toolkit + reconcile the stale
  forked config. Execution walkthrough for Part B lands **project-local** in
  `Projects/aviationChat-AGY/_artifacts/2026-06-25_phase2-rule-reconcile/`.

Recommended execution order: **Part A first** (small, low-risk, finishes the open item), then Part B.

---

## TWO HEADLINE DECISIONS (your informed "approved" covers these)

**D1 — Delete the old `.agent/` (singular, 1,059 files) outright.** Verified fully superseded by the new
`.agents/`: `.agent/skills/` = 0 unique files (all 1,025 already in `.agents/skills/`); `.agent/workflows/`
14 files were reclassified as `.agents/commands/1_*` during conversion; `.agent/rules/` only 2 unique —
`git-closeout-commits.md` (deliberately dropped — contradicts never-commit) and `000-PLAN-FIRST-GATE.md`
(captured by AGENTS.md §5 + `artifacts-always-first.md`). `gemini.md`'s roster/models/DB-topology is folded
into AGENTS.md §1/§6 (+ `_bmad-output/project-context.md`). → **Recommend: delete after a preserve-sweep.**
It's in git history if ever needed. (RISK GATE: deleting files — needs your explicit ok.)

**D2 — Remove the forked `.claude/rules/` (18 files).** The home base's `.claude/` has **no** `rules/` folder —
rules load on demand via `AGENTS.md` → `.agents/rules/` (least-context by design). aviationChat's
`.claude/rules/` is a stale fork that still ships `git-closeout-commits.md` (the OLD "you may commit at
close-out" policy that **contradicts** the new never-commit `git-policy.md`) and `_claude_artifacts/` refs.
→ **Recommend: remove `.claude/rules/`** to match the home base; the canonical, current rules live in
`.agents/rules/`. (Alternative: re-sync `.claude/rules/` from `.agents/` as a mirror — but that keeps two
copies to drift. Not recommended.)

---

## PART A — WS7: home-base repo-map + drift hook

**A1. Enhance the master drift script (backward-compatible).**
`.agents/scripts/check-repo-map-drift.ps1` currently hard-detects `$root = parent of scripts/` and reads
`docs/repo-map.md`. Add two **optional** params — `-Root <path>` (override the auto-detected root) and
`-MapPath <rel>` (override `docs/repo-map.md`). Defaults unchanged → projects keep calling their vendored
`scripts/` copy with no new args. This lets the home base call the master copy directly against
`_docs/repo-map.md` without duplicating the script into a home-base `scripts/`. Re-vendor the updated script
to `Projects/aviationChat-AGY/scripts/check-repo-map-drift.ps1` (keep master↔vendor identical).

**A2. Generate the home-base `_docs/repo-map.md`** (matches the home base's existing `_docs/` convention).
Run `.agents/scripts/generate_repo_map.py --mode content --ignore _artifacts,_my_resources,Projects`
(output → `_docs/repo-map.md`). Curated header (one-line purpose per top-level area: `_docs/`, `_system/`,
`_routing-canary/`, `.agents/`, plus a `Projects/` row that points to each project's own
`Projects/<name>/docs/repo-map.md`) + the auto body between the sentinels. `Projects/` is **ignored** from the
auto-scan (each project owns its own map) and represented as a single curated pointer.

**A3. Wire the home-base SessionStart hook to repo-map + drift.** Update `.claude/settings.json` so block 1
also injects `_docs/repo-map.md` into continuity, and add a block 2 that calls
`powershell -NoProfile -ExecutionPolicy Bypass -Command "& (Join-Path $env:CLAUDE_PROJECT_DIR
'.agents/scripts/check-repo-map-drift.ps1') -Root $env:CLAUDE_PROJECT_DIR -MapPath '_docs/repo-map.md'"`.
**Caveat:** self-editing the active session's `.claude/settings.json` was auto-mode-**blocked** in both prior
conversions. I'll attempt the direct edit; if blocked, I deliver `settings.json.proposed` in this artifact
folder for you to copy over `.claude/settings.json` (same hand-off pattern you already know).

**A4. One-line AGENTS.md note (home base).** Add `_docs/repo-map.md` as the home-base navigation index
(drift-checked at SessionStart) to AGENTS.md §4's table. Small, surgical.

## PART B — aviationChat Phase 2 (project-local)

**B1. Preserve-sweep (read-only verify, then tiny fold-in if needed).** Confirm `.agent/gemini.md`'s
sub-agent roster (TA, chat-classifier, talker, reasoner, lesson_planner, socratic_teacher, quiz_tutor) +
Schema-Change-Protocol are present in `_bmad-output/project-context.md` (source of truth). If a useful bit is
missing anywhere, fold a one-liner into AGENTS.md. No code touched.

**B2. Retire the old `.agent/` (D1).** `git rm -r Projects/aviationChat-AGY/.agent` (handed to you as the
command — agents don't commit). I'll remove it from the working tree; you commit. Fix the few live refs that
still point at `.agent/…`: `1_run-all-tests-back_front.md` (`@.agent/rules/constitution.md` → `.agents/rules/
constitution.md`) and any `slash_command_updating`/README pointer that names `.agent/`.

**B3. Remove the forked `.claude/rules/` (D2).** Delete `Projects/aviationChat-AGY/.claude/rules/` (18 files).
Canonical rules remain in `.agents/rules/`, loaded per AGENTS.md §4 (3 always-load) + on demand.

**B4. Repoint live `_claude_artifacts/` → `_artifacts/` writers.** Edit in the `.agents/commands/` master copy:
`1_check-for-tech-stack-updates.md`, `1_ccps_update-active-context.md` (also drop the dead
`your-action-required.md` mention), `1_make-workflow-from-chat.md`, `1_run-all-tests-back_front.md`,
`autopilot.md` (5 refs incl. `_autopilot-run.log` + `<date>_autopilot-<id>/`). Then re-sync
`.claude/commands/` + `.opencode/commands/` from `.agents/commands/`. (Historical mentions inside
`_artifacts/**`, `_bmad*/**`, `_my_resources/**` are **left as-is** — they're history / BMAD-owned / protected.)

**B5. Fix stale paths in `.agents/rules/`.** `pyrefly-paths.md` (`c:\Sudo_Hatter_Command\aviationChat-AGY\…`
→ `…\Projects\aviationChat-AGY\…`, double-backslash form). `adk_file_formating.md` line 10 (old external
`c:\Users\dlohn\.gemini\antigravity\scratch\AGY_AVIATIONCHAT\.agent\skills\v2-prompt-architecture\SKILL.md`
→ the in-repo skill path, or drop the absolute path). Mirror to `.claude/`/`.opencode/` only if those keep the
rule (they won't, after B3).

**B6. Re-sync engine mirrors.** Refresh `.claude/` + `.opencode/` command/agent mirrors from the cleaned
`.agents/` master so all three engines see identical, current tooling. **Do NOT touch `.claude/skills/bmad-*`
or `_bmad/`** — BMAD-owned, regenerated by BMAD releases (the standing guardrail).

**B7. Regenerate `docs/repo-map.md` + drift check.** Top-level changed (`.agent/` gone), so rebuild
`Projects/aviationChat-AGY/docs/repo-map.md` (`--mode content`, same `--ignore` as Phase 1) and run the drift
script to confirm clean.

---

## Files touched (summary)

| # | File / area | Change |
|---|---|---|
| A1 | `.agents/scripts/check-repo-map-drift.ps1` (+ aviationChat `scripts/` vendor) | add optional `-Root`/`-MapPath` |
| A2 | `_docs/repo-map.md` (NEW) | generate hybrid (curated + auto body) |
| A3 | `.claude/settings.json` (or `…/settings.json.proposed`) | inject repo-map + drift hook |
| A4 | `AGENTS.md` (home base) §4 | add `_docs/repo-map.md` row |
| B2 | `Projects/aviationChat-AGY/.agent/` (1,059) | **delete** (preserve-sweep first) |
| B3 | `Projects/aviationChat-AGY/.claude/rules/` (18) | **delete** |
| B4 | `.agents/commands/{5 files}` + `.claude/`/`.opencode/` mirrors | repoint `_claude_artifacts/`→`_artifacts/` |
| B5 | `.agents/rules/{pyrefly-paths, adk_file_formating}.md` | fix stale paths |
| B6 | `.claude/` + `.opencode/` mirrors | re-sync (skip BMAD) |
| B7 | `Projects/aviationChat-AGY/docs/repo-map.md` | regenerate + drift-check |

## Open questions
1. **D1** — delete old `.agent/` outright (recommended) vs archive-then-delete vs keep?
2. **D2** — remove forked `.claude/rules/` (recommended) vs re-sync as a mirror?
3. Home-base repo-map at **`_docs/repo-map.md`** (recommended, matches `_docs/`) vs a new bare `docs/`?

## Verification plan
- A: home-base drift script runs silent when current, nags on a planted `_drifttest/`, exits 0; `_docs/repo-map.md`
  lists every shown top-level folder; settings hook (or `.proposed`) parses as valid JSON.
- B: `Get-ChildItem` shows `.agent/` and `.claude/rules/` gone; `grep _claude_artifacts` over **live wiring only**
  (`.agents/`, `.claude/`, `.opencode/` commands/rules/workflows) returns zero; `grep \.agent[/\\]` over live
  wiring returns zero; aviationChat drift script silent (map current). GitNexus `detect_changes(scope:all)` to
  confirm **zero code symbols** touched (config/docs-only), same as Phase 1.

## Your Actions (filled in at close-out)
- Commit home base (Part A) — explicit-path command in the Part A walkthrough.
- Commit aviationChat (Part B) — explicit-path command in the project-local walkthrough.
- Apply any `settings.json.proposed` (A3) if the direct edit was auto-blocked.
