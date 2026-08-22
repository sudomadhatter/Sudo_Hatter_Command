---
IsArtifact: true
ArtifactMetadata:
  title: System docs truth-sync + root-law slim — walkthrough
  type: walkthrough
  date: 2026-07-09
---

# Walkthrough — System docs truth-sync + root-law slim

> Plan: [`implementation_plan.md`](implementation_plan.md) — approved via "review the edits then approved";
> Daniel's two MD-Feedback memos amended scope: **bmad-\* skills left alone** (BMAD updates overwrite) and
> **`.agent/` left alone**. The md-feedback MCP server was not connected this session, so the two memo
> blocks remain `status="open"` in the plan file — resolve them from a session with the server up (never
> hand-edit the HTML blocks).

## What drove this (the audits — both passed)

1. **Setup vs the mentor transcript:** R1–R8 met or exceeded; no structural change needed. All findings
   were documentation drift (see the plan's F1–F12).
2. **`/1_update-maps` prune = move, never delete — verified at all three layers:** the workflow prose
   (Step 3.5 "archiving is a move, not a rewrite", Step 5.5, Guardrails), the Step-4 approval gate (prunes
   are proposed, never auto-applied), and the only scripted prune —
   `record_map_changes.consume()` — **appends consumed journal lines to
   `docs/.maps-journal-archive.jsonl` BEFORE rewriting the live journal** (no data-loss window) and
   fail-safes to consuming nothing if the anchor sha is absent. `check_maps.py` itself never edits
   content; its `PRUNE_*` constants only drive nags.

## What changed, file by file

**Phase 1 — [`_my_resources/docs/master-implementation-plan.md`](../../../_my_resources/docs/master-implementation-plan.md)** (Daniel-authorized `_my_resources` edit)
- Frontmatter `status:` → `built-live — historical rollout record + evolution log (§8)`.
- New "How to read this doc" banner: §0–§7 = rollout record; standing spec = `docs/workspace-standard.md`.
- §2 tree: `_docs\`→`docs\` (+ real plan location), `_home\`→`_main\`, dropped the banned `task-list`
  artifact, real project names (`AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`, + `BRKN_Tattoos` etc.),
  `youtube_transcripts\`→`_my_resources\` node.
- §4 numbered-section spec synced to the as-built root law (§1–§8, ALWAYS-LOAD includes
  `artifacts-always-first.md`).
- §7 marked historical; new §8 evolution-log entry for this session.

**Phase 2 — [`router.md`](../../../../../router.md):** reference row `youtube_transcripts/` →
`_my_resources/youtube_transcripts/`.

**Phase 3 — [`file_folder_structure+maintaining.md`](../../../../../_my_resources/diagrams_guides/system/file_folder_structure+maintaining.md) + [`AGENTS.md`](../../../../../AGENTS.md) + [`.agents/commands/1_update-maps.md`](../../../.agents/commands/1_update-maps.md)**
- Hook table → the real **4** SessionStart hooks + the PreToolUse `require-push-approval.py` guard.
- §7 workspace table synced to `router.md` (+BRKN_Tattoos, RAG_Pipeline_AC name, 4 pending projects).
- §1 diagram + root `AGENTS.md` §4 table: added `_my_resources/` and `_bmad/`+`_bmad-output/`.
- Check-count wording now names the unnumbered check 2.5 (guide ×3 spots + the command doc).

**Phase 4 (amended) — root-law slim + NEW rule**
- **NEW [`.agents/rules/lobby-search.md`](../../../../../.agents/rules/lobby-search.md)** — the grep-gotcha
  mechanics moved out of the front door, PLUS the session-verified Glob caveat (Glob can false-negative
  under `Projects/` even with an in-project path — verify with Bash `find`). Row added to
  [`.agents/rules/INDEX.md`](../../../../../.agents/rules/INDEX.md).
- Root `AGENTS.md`: §4 gotcha 16 lines → 3 (trigger warning stays inline — honors the 2026-07-06
  "foot-gun stays inline" invariant; mechanics routed); §6 SEARCH GATE points at the rule; §6 git-write
  block 10 → 4 lines (canon = `git-policy.md`). ~20 always-loaded lines saved per session.
- **bmad-\* skills NOT touched** (Daniel's memo).

**Reconcile ride-along (the `/1_update-maps` pass the plan promised)**
- `docs/repo-map.md` AUTO regenerated ×2 (mode=content; second pass because the new INDEX files changed
  folder summaries).
- `_artifacts/_main/INDEX.md`: +6 missing depth-3 rows (the 07-06/07-09 sessions) + this session's row.
- **NEW** `_artifacts/AGY_AVIATIONCHAT/INDEX.md` (bucket hit ≥2 sessions) and
  `_bmad-output/brainstorming/INDEX.md` (level-2 requirement).
- `_artifacts/INDEX.md` +1 ledger row; `_artifacts/_main/active-context.md` hand-off block prepended.

## What fought back
- The big `AGENTS.md` blockquote Edit missed on first try (my paste had a drifted sentence) — re-read the
  exact text and replaced cleanly.
- `generate_repo_map.py --root C:\Sudo_Hatter_Command` under Git Bash mangled the path and wrote a stray
  `C:\Sudo_Hatter_Command\Sudo_Hatter_Command\docs\repo-map.md`. Removed the junk folder immediately and
  re-ran with `--root .` (the workflow's own example form). Lesson reinforced: **always `--root .` from
  the workspace root.**

## Verification (real output)

**Routing canary — GREEN after the root-law slim.** Fresh subagent given ONLY `_routing-canary/CLAUDE.md`:
```
agent reply: done boss
Power.md:    control your agent
```
`Power.md` reset to the placeholder line afterward (per the canary README).

**Linter — before → after.** Before (lobby): AUTO stale, 3 level-2 INDEX missing, 1 depth-3 INDEX missing
+ 6 missing rows. After:
```
[AUTO block freshness]        [ok] clean
[repo-map paths]              [ok] clean
[folder coverage]             [ok] clean
[INDEX.md paths]              [ok] clean
[level-2 INDEX presence]      [x] .claude/commands/INDEX.md: missing
                              [x] .opencode/commands/INDEX.md: missing
[depth-3 _artifacts INDEX]    [ok] clean
[structure conformance]       [ok] clean
[context hygiene]             [ok]
[tier-2 local law]            [ok] guarded dirs carry AGENTS.md + adapters (redirects verified)
[gitnexus index]              [hint] STALE - indexed at c2ee6b7, HEAD is c28d070
```
The two remaining `[x]` are **vendored copies `/sync-agents` fills** (the master
`.agents/commands/INDEX.md` exists); the gitnexus hint is the standing re-index-after-commit hand-off.

**Deferred / surfaced (not mine to act on):**
- `check_maps_output.txt` at repo root is **git-tracked** — your call: delete (`git rm`) or keep local
  but untrack (`git rm --cached` + `.gitignore` line).
- Fan-out lint surfaced a stray **`Projects/aviationChat-AGY/`** directory (non-workspace, no
  `AGENTS.md`) sitting beside `Projects/AGY_AVIATIONCHAT/` — possibly an old pre-rename copy. Worth a look.
- Daniel's two MD-Feedback memos in the plan remain `open` (server not connected this session).
- Pre-existing modified files from other lanes (sudo-code-review\*/sudo-dev-story-tests\* masters +
  mirrors) are in the working tree — **excluded from the commit below.**

## Task Checklist
- [x] Audit setup + guide vs the mentor transcript (R1–R8 pass; findings = doc drift)
- [x] Verify `/1_update-maps` prune is move-never-delete (workflow + gate + `consume()` code)
- [x] Phase 1 — master-implementation-plan.md truth-sync (10 edits)
- [x] Phase 2 — router.md transcript path fix
- [x] Phase 3 — guide + command doc + root AGENTS.md table sync
- [x] Phase 4 — root-law slim + NEW `lobby-search.md` rule + rules INDEX row (bmad-\* skipped per memo)
- [x] Phase 4.3 — canary re-run GREEN + reset; repo-map regen; INDEX reconcile (depth-2/-3, 2 new INDEXes)
- [x] Phase 5.1 — `check_maps_output.txt` status confirmed (tracked → decision handed to Daniel)
- [ ] Phase 5.2 — `.agent/` inventory — SKIPPED per Daniel's memo ("leave this alone")
- [ ] Resolve the 2 plan memos via md-feedback MCP — deferred (server not connected this session)

## Your Actions
1. **Commit (lobby only — explicit paths; other lanes' sudo-\* edits stay out):**
   ```bash
   git add AGENTS.md router.md docs/repo-map.md .agents/commands/1_update-maps.md .agents/rules/lobby-search.md .agents/rules/INDEX.md "_my_resources/docs/master-implementation-plan.md" "_my_resources/diagrams_guides/system/file_folder_structure+maintaining.md" _artifacts/INDEX.md _artifacts/_main/INDEX.md _artifacts/_main/active-context.md _artifacts/AGY_AVIATIONCHAT/INDEX.md _bmad-output/brainstorming/INDEX.md _artifacts/_main/2026-07-09_system-docs-truth-sync/
   git commit -m "docs: truth-sync master plan + guide + router; extract lobby-search rule; reconcile maps + INDEXes"
   ```
2. **Re-anchor AFTER committing:** `python .agents/scripts/check_maps.py --set-anchor`
3. **`/sync-agents`** — vendors `lobby-search.md` + the rules INDEX + command-doc fix to `.claude/`,
   `.opencode/`, the globals, and both projects; also clears the 2 remaining level-2 INDEX flags.
4. **GitNexus re-index (after commit):** `node .gitnexus/run.cjs analyze` — and since this run touched
   `.agents/**`, the `SUDO_COMMAND` index needs its manual re-analyze too (it's `--skip-git`; check 9
   can't see it).
5. **Your call — `check_maps_output.txt` (tracked):** delete → `git rm check_maps_output.txt`; or keep
   local but untrack → `git rm --cached check_maps_output.txt` + add `check_maps_output.txt` to `.gitignore`.
6. ~~Worth a look: the stray `Projects/aviationChat-AGY/` directory~~ — **RESOLVED in the addendum below.**

---

## Addendum (same session) — "fix 1 and 2" + md-feedback rollout + guide rewrite

**Fix 1 — stray `Projects/aviationChat-AGY/` DELETED.** Inspected first: it contained only an empty
`frontend/` folder — **0 bytes, no `.git`** — an accidental husk under the old project name, not a
repo. Removed (`rm -rf`; under gitignored `Projects/`, so no lobby commit involved). Live-config sweep
for the old name found one mention: `python_inter_venv_fix/SKILL.md` uses it as a *historical example*
of a stale path (that's literally the skill's topic) — harmless, left alone.

**Fix 2 — md-feedback memos: ROOT CAUSE found and fixed.** Commit `7567807` configured md-feedback in
`.claude/mcp.json` / `.opencode/mcp.json` / `.antigravity/mcp.json` at the **lobby only** — but Claude
Code reads project MCP servers from the **root `.mcp.json`** (which held only gitnexus — that's exactly
why gitnexus tools work and md-feedback never appeared). Neither project had ANY md-feedback config.
Wired now (guide-pattern + the root-file fix), merging into existing files, never overwriting:

| Workspace | `.mcp.json` (root — the Claude Code fix) | `.claude/mcp.json` | `.opencode/mcp.json` | `.antigravity/mcp.json` |
|---|---|---|---|---|
| Lobby | **ADDED** (beside gitnexus) | already had it | already had it | already had it |
| AGY_AVIATIONCHAT | **NEW** | **NEW** | **NEW** | **MERGED** (kept firebase + gitnexus) |
| Fresh_Workspace_BMAD | **NEW** | **NEW** | **NEW** | **MERGED** (kept firebase w/ `{{PROJECT_NAME}}`) |

The two open USER_MEMO blocks in this session's plan remain untouched (hand-editing corrupts tracking
hashes); once the server loads (restart + approve), say "review" and they can be resolved via
`apply_memo`. Note: `_my_resources/open_tasks/md_feedback_setup_guide.md` documents only the
`.claude/mcp.json` path — it's missing the root-`.mcp.json` requirement for Claude Code (your doc; not
edited).

**Guide rewritten (Daniel-directed):**
[`file_folder_structure+maintaining.md`](../../../../../_my_resources/diagrams_guides/system/file_folder_structure+maintaining.md)
is now the full "what we built and how it works" guide & overview — the idea, the routing walk, tier
model, artifacts/persistence, the two-layer INDEX contract, the maintaining system, sync/anti-drift,
git model, the MD Feedback loop (§9, incl. where it's wired), workspace status, key files, and a
when-to-run-what playbook (§12). All content grounded in this session's verified state.

## Your Actions (addendum — three repos now)
1. **Lobby commit** — use the command in item 1 above **plus** `.mcp.json` and note the guide file is
   already in the list:
   ```bash
   git add .mcp.json   # add to the item-1 git add list before committing
   ```
2. **AGY_AVIATIONCHAT commit:**
   ```bash
   git -C Projects/AGY_AVIATIONCHAT add .mcp.json .claude/mcp.json .opencode/mcp.json .antigravity/mcp.json
   git -C Projects/AGY_AVIATIONCHAT commit -m "chore: wire md-feedback MCP across all platform configs"
   ```
3. **Fresh_Workspace_BMAD commit:**
   ```bash
   git -C Projects/Fresh_Workspace_BMAD add .mcp.json .claude/mcp.json .opencode/mcp.json .antigravity/mcp.json
   git -C Projects/Fresh_Workspace_BMAD commit -m "chore: wire md-feedback MCP across all platform configs (template)"
   ```
4. **Restart Claude Code** (and opencode/Antigravity) so the new md-feedback server loads — approve it
   when prompted — then say **"review"** on the plan to resolve the two open memos.
5. Optionally add the root-`.mcp.json` step to your `md_feedback_setup_guide.md` (your file — not touched).
