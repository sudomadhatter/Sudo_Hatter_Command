---
IsArtifact: true
ArtifactMetadata:
  title: Toolkit Centralization — full re-audit after the Jira integration (v4 draft)
  type: reaudit
  date: 2026-08-07
  status: DRAFT — folds into implementation_plan.md on the first keyed commit of the resume pre-flight
---

# Re-audit v4 — the plan vs the Jira-integrated system

**Why:** between P2 landing and now, the Jira integration went LIVE (guide:
`_my_resources/diagrams_guides/system/jira_integration_guide.md`). 27 commits on `main` vs our epic's 3.
Goals unchanged; the ground under P3–P6 moved. **Verdict: GO — with a mandatory resume pre-flight.**

## What the Jira work changed (verified against main @ b7683bc)
1. **Keys are law, gate ARMED (ENFORCE) in lobby + AGY.** `jira.conf` per repo (SCC / AVCH,
   wrong-project keys rejected), tracked `JIRA-ENFORCE`, `commit-msg` hook live on this Mac
   (`core.hooksPath` set in both repos). EVERY branch + commit carries a key — `epic/<KEY>-<slug>`,
   `claude/<KEY>-<slug>`, `chore/<KEY>-<slug>`; chores need tickets too.
2. **The /sudo-* seats are WIRED on main** (further than the guide's §12): kickoff Step 1.5 cuts
   `epic/<JIRA-KEY>-<slug>` + mint instructions; close-out gained Step 4.5 (AUTOMATIC acli ticket
   transition) + keyed landing templates; `/sudo-push-e2e` carries the Jira SOP (+62 lines).
   → **3 of our 4 P2 `JIRA-HOOK:` seats are superseded** (kickoff, close-out, push-e2e — drop at merge).
   The 4th (in `require-push-approval.py`) stays: the pre-push/CI enforcement layer is still unbuilt.
3. **Scrum board retired (SCC-13):** `sudo-update-scrum-board` deleted ×3 surfaces; `workflow_lint`
   slimmed. Jira is the human view; `sprint-status.yaml` stays source of truth for sprint state.
4. **Fresh retired (SCC-25)** — duplicates our P2 de-list (reconcile at merge). There is currently NO
   template; P5's skeleton becomes THE template.
5. **A new file class exists: repo-local enforcement.** `.githooks/` shims + `.agents/scripts/git-hooks/`
   (script + tracked ENFORCE flag) + `.agents/jira.conf` are PER-REPO BY DESIGN — git runs hooks in the
   repo it gates; conf is project identity; deliberately excluded from sync (both vendor + manifest).
6. AGY: AVCH board backfilled (~20 open items), `jira_key:` frontmatter stamped in story files.
7. Atlassian MCP declared but **unauthenticated for agent sessions** (needs `/mcp`); `acli` is the
   working agent surface (keychain-authed).

## Epic ↔ main conflict map (3 vs 27 — resolve at the pre-flight merge)
| File | Ours (epic) | Theirs (main) | Resolution |
|---|---|---|---|
| `.agents/rules/INDEX.md` | +project-law row | +jira.md row | keep BOTH rows |
| `.agents/rules/constitution.md` | +binding hard stop | git bullet now key-aware | keep both |
| `.agents/maintained-projects.txt` | full header rewrite + de-list | SCC-25 de-list | ours (fuller), fold their note |
| `sudo-create-epic-sprint.md` | JIRA-HOOK comment | keyed Step 1.5 + mint | THEIRS — drop our comment |
| `sudo-update-sprint-memory.md` | JIRA-HOOK comment | Step 4.5 + keyed templates | THEIRS — drop our comment |
| `sudo-push-e2e.md` | JIRA-HOOK comment | Jira SOP | THEIRS — drop our comment |
| `.agents/scripts/sync-agents.ps1` | vendor path DELETED | +jira.conf vendor exclusion | OURS — deletion wins; exclusion moot (nothing vendors), note it in the header comment |
| `.agents/commands/INDEX.md` | autopilot_mobile retired | scrum-board retired | keep both retirements |
| `.agents/rules/mobile-mode.md` | dead ref removed | small edit | keep both |
| hook / check_maps / project-law | ours only | untouched | ours (with F8/F11 fixes below) |

## New findings
| # | Sev | Finding | Fix |
|---|---|---|---|
| F8 | **HIGH** | P2's thin-floor `vendor_markers` flags `.githooks` + `.agents/scripts` — in AGY those now HOLD the armed Jira gate; unfixed, the lint orders P3 to strip the audit-trail enforcement | P2.1 follow-on: drop `.githooks` from markers; sentinel `.agents/scripts/check_maps.py` instead of `.agents/scripts`; never flag `jira.conf`/`git-hooks/`. P3(f) strip list explicitly EXCLUDES the enforcement set |
| F9 | **HIGH** | The epic itself is un-keyed + pre-Jira: no SCC key in the branch name; its tree lacks hook script/conf, so every new lane re-hits the shim crash and no commit can pass the armed gate | Resume pre-flight: mint the SCC epic ticket (acli, paired with Daniel), rename branch → `epic/SCC-<n>-toolkit-centralization`, merge `origin/main` into it (conflict map above), key all future commits |
| F10 | MED | `.githooks/commit-msg` shim still has no missing-script guard — any pre-Jira worktree hard-crashes on commit (hit us once in P2) | one-line guard: exists→exec, else warn + allow (matches "loud alarm, not locked door") — pre-flight |
| F11 | MED | P1's `project-law.md` tier-2 = "rules/ + skills/ + INDEX.md ONLY" — now wrong; it would class the enforcement set as vendor | P1.1 follow-on: add the repo-local-enforcement carve-out (jira.conf + git-hooks + .githooks + tracked flags; BMAD-toml precedent: "identity + enforcement live where git runs them"); mirror in workspace-standard thin rows |
| F12 | LOW | P5 skeleton lacks the Jira seats | ship `.githooks/` shims + git-hooks scripts + `jira.conf.example` (no keys = gate off, graceful) + `jira_key:` story-frontmatter convention + mint quick-start in README |
| F13 | LOW | P6 sweep list predates SCC-13/25 | add: scrum-board memory retirements, quick-ref already updated by their side — dedupe, don't redo |
| F14 | INFO | VR + RAG have no Jira project — the gate no-ops there (no jira.conf, by design) | P4 branches/commits carry SCC keys anyway (they are SCC system work; harmless in un-gated repos, keeps the trail whole) |

## Phase deltas (everything else in plan v3 stands)
- **NEW — Resume pre-flight (one lane, `claude/SCC-<n>-tc-reaudit`):** mint SCC epic ticket → rename the
  epic branch to keyed form (push new ref, prune old) → merge `origin/main` into the epic per the
  conflict map → F10 shim guard → F8 marker fix → F11 law amendment → fold this draft into
  `implementation_plan.md` → land keyed. Gate: `run_all.py` 5/5 + lobby lint.
- **P3 (AGY):** epic branch = `epic/AVCH-<n>-thin-toolkit` (mint the AVCH epic). Strip PRESERVES the
  enforcement set (`.githooks/`, `.agents/scripts/git-hooks/`, `.agents/jira.conf`). Decision 2 is
  REVERSED: hooks are load-bearing — do NOT unset `core.hooksPath`; VERIFY it on both machines instead.
  Stories already carry `jira_key:` — untouched. AVCH commits only (SCC rejected there by design).
- **P4:** SCC-keyed branches/commits (F14); scope otherwise unchanged.
- **P5:** + F12. The skeleton is now the ONLY template (Fresh retired, none exists in the interim).
- **P6:** + F13; the epic reaches `main` through the NEW push-e2e Jira SOP (tickets → Done + gate
  evidence on the ticket).
- **Decisions:** D2 REVERSED (project githooks stay — armed Jira gate). D5 NEW: repo-local enforcement
  is a permanent carve-out class, never centralized, never synced. D6 NEW: our 3 superseded JIRA-HOOK
  seats yield to the real wiring; the push-hook seat remains for the unbuilt pre-push/CI layer.

## Blockers needing Daniel
1. **Mint the SCC epic ticket** for this centralization epic (and the AVCH epic when P3 starts) — acli is
   ready; pairing per the SOP. Without a key, the armed gate correctly refuses every further commit.
2. Optional: authorize the **Atlassian MCP** (`/mcp` in an interactive session) if you want me reading
   the board directly; `acli` covers everything otherwise.

**Audit verdict: GO** — pre-flight first, then P3 under the new rules. Every v3 goal survives; the Jira
system removed work (board apparatus, 3 seat comments) and added guardrails we now build inside.
