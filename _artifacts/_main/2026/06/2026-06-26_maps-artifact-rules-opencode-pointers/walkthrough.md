---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — maps reconcile + artifact-rule verify + opencode .agent→.agents fix
  type: walkthrough
  date: 2026-06-26
---

# Walkthrough — main + aviationchat + clean-bmad

Three asks, one pass, run from the lobby. Nothing was committed (per git-policy) — commands handed off below.

## What I did

### 1. Verified the opencode `.agent` → `.agents` pointer fix (your recent work)
Mapped every `.agent` (singular) reference across all three repos' `.agents/.claude/.opencode`:
- **aviationchat** — 0 broken; your fix had fully landed there. It became the reference for the correct form.
- **main** — 39 (`.agents`) / 21 (`.claude`) / 23 (`.opencode`) still broken.
- **clean-bmad** — 39 / 24 / 25 still broken.

**This was NOT a blind sed** — the careful part was separating real broken pointers from intentional usages:
- **Python module refs** (`from ….agent import`, `.agent_evaluator`) — left alone; they're followed by space/`_`, not `/` or `\`, so scoping the replace to `.agent/` and `.agent\` skipped them automatically.
- **`.opencode/agent/`** (opencode's real singular dir) — never collides, because the substring is `/agent`, not `.agent`.
- **4 intentional-prose files excluded:** `generate_doc_graph.py` (a comment *about* stale `.agent/` refs), `skills_explained.md` (vendored Antigravity explainer describing the native `.agent/skills` convention), `antigravity.md` (line deliberately shows BOTH `.agent/skills` and `.agents/skills` — confirmed the only true dual-convention line, would have become a redundant duplicate), and `adk_file_formating.md` (handled with a targeted rewrite instead — see below).

Applied via a scoped script (literal `.agent/`→`.agents/` and `.agent\`→`.agents\`, idempotent):
```
[APPLIED] 162 files, 304 replacements
```
Post-fix sanity: **0** broken `@.agent/` pointers remain anywhere (the one match left is `.agents/.gitnexus/lbug`, a gitignored GitNexus binary log — not a pointer).

### 2. Two targeted fixes (folded in per your "fix that too" / careful-handling)
- **clean-bmad `.agents/rules/adk_file_formating.md:50`** pointed at a stale hardcoded Antigravity scratch path (`c:\Users\dlohn\.gemini\antigravity\scratch\AGY_AVIATIONCHAT\.agent\skills\v2-prompt-architecture\SKILL.md`). A mechanical swap would still leave it broken (absolute path, `v2`). Rewrote it to match aviationchat's corrected line → `.agents/skills/v3-prompt-architecture/SKILL.md` (the in-repo doctrine; verified clean-bmad has `v3-prompt-architecture`, not `v2`).
- **The `/1_ccps_*` broken wrappers** ("fix that too"): the `command-workflow-parity-sync` work is actually **done** (it has a walkthrough + task-list now, and no `ccps` command/workflow files exist in main or clean-bmad). The only live leftover was **`clean-bmad/AGENTS.md:45`** still routing session-boot to the removed `/1_ccps_boot-context` → fixed to `/boot-sprint-context` (matches aviationchat's AGENTS.md; verified the command exists in clean-bmad).

### 3. Fixed the aviationchat `check_maps.py` root-resolution bug ("fix it")
`default_root = here.parent.parent` resolved to `.agents/` when the **master** copy was run directly (looked for `.agents/docs/repo-map.md`). Replaced it with a walk-up that finds the dir holding `AGENTS.md` + `docs/repo-map.md`, so **both** the vendored `scripts/` copy and the master `.agents/scripts/` copy resolve the project root. Applied to the master, then `cp`'d to the vendored copy to keep them byte-identical (md5 `d27880f…`).

Proof both entrypoints now agree:
```
--- via .agents/scripts (was broken) ---   --- via vendored scripts ---
  AUTO block is STALE … on disk but not in map: epic-15/   (identical)
  [repo-map paths] [ok] clean
```

### 4. Maps reconciled (all three "correct")
- **main (lobby)** — linter already exit 0; no map/INDEX edits. `All maps & INDEXes agree with disk.`
- **aviationchat** — AUTO block was stale (`epic-15/` on disk, not mapped). Regenerated mode-preserving (`--mode content`); diff = `epic-15/` added + two file-count refreshes. No curated line needed (epics are an already-documented `epic-N/story/` pattern). Re-lint: `All maps & INDEXes agree with disk.`
- **clean-bmad** — AUTO regen (`--ignore _bmad`, mode=auto) produced **no diff** (already current). It has no `check_maps.py`, so I hand-checked the curated block and found one dead path: `_bmad-output/active-context.md` → fixed to `_bmad-output/active-context/active-context.md` (the real location; the other curated row already had it right).

### 5. Artifact rules — verified, no action
`.agents/rules/artifacts-always-first.md` is **byte-identical** in all three repos (md5 `404d27dddd797eb0c8fa5898701c551a`, 172 lines). Mirrors reference it via `@.agents/…` rather than copying — by design.

## Final linter output
```
MAIN:        All maps & INDEXes agree with disk. [ok]   (only: no baseline anchor yet)
AVIATIONCHAT: All maps & INDEXes agree with disk. [ok]  (only: no baseline anchor yet)
CLEAN-BMAD:  AUTO regen no-diff; curated dead path fixed (no automated linter present)
```

## Files changed
- **main:** 80 files — all `.agent`→`.agents` pointer fixes in `.agents/` + `.claude/` + `.opencode/`.
- **aviationchat:** 3 files — `.agents/scripts/check_maps.py`, `scripts/check_maps.py`, `docs/repo-map.md`.
- **clean-bmad:** 87 files — pointer fixes + `.agents/rules/adk_file_formating.md` + `AGENTS.md` + `docs/repo-map.md`.

## Deviations from plan
- The `/1_ccps_*` fix turned out to be near-complete already (one stale routing row, not a wrapper rebuild).
- Found + fixed two extra real issues during the careful pass: the clean-bmad curated dead path and the adk-rule stale absolute path.
- Anchors NOT set (workflow says anchor *after* commit, never against an uncommitted tree) — see Your Actions.

## Your Actions

These are **3 separate repos** — commit each in its own tree. Review the diffs, then:

**1. main (lobby)** — pointer fixes only:
```bash
cd /c/Sudo_Hatter_Command
git add .agents .claude .opencode _artifacts
git commit -m "fix: repoint stale .agent/ -> .agents/ toolkit pointers across lobby tool dirs"
python .agents/scripts/check_maps.py --set-anchor   # AFTER the commit
```

**2. aviationChat-AGY** — check_maps bug + repo-map:
```bash
cd /c/Sudo_Hatter_Command/Projects/aviationChat-AGY
git add .agents/scripts/check_maps.py scripts/check_maps.py docs/repo-map.md
git commit -m "fix(maps): robust check_maps root resolution + regen repo-map (epic-15)"
python scripts/check_maps.py --set-anchor           # AFTER the commit
```

**3. clean-bmad-workspace** — pointers + adk rule + AGENTS route + curated dead path:
```bash
cd /c/Sudo_Hatter_Command/Projects/clean-bmad-workspace
git add .agents .claude .opencode AGENTS.md docs/repo-map.md
git commit -m "fix: repoint .agent/ -> .agents/, adk rule path, /boot-sprint-context route, repo-map dead path"
```

**Optional follow-ups (your call — the plan's open questions):**
- Vendor `check_maps.py` into clean-bmad for linter parity (it only has the generator today).
- Re-sync mirrors via `/sync-agents` if you prefer the canonical path over the direct mirror edits I made (results are identical either way).
