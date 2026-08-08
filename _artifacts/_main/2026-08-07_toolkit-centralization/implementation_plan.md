---
IsArtifact: true
ArtifactMetadata:
  title: Toolkit Centralization — thin projects, command-center-only rules/commands
  type: implementation_plan
  date: 2026-08-07
  rebaselined: 2026-08-07 post branch-model migration (fa1c221)
---

# Toolkit Centralization — implementation plan (v3, re-baselined)

**Goal:** the command center becomes the ONLY home of workflow rules, commands, skills, and sync; projects hold only project-relevant content (code, `_bmad/` + `_bmad-output/`, `_artifacts/`, `_my_resources/`, docs, own project law). Removes **\~4,250 tracked vendor files** (AGY 1,532 · NEXgen-VR 2,628 · RAG 86 — measured post-migration; Fresh keeps its 2,628 as the frozen fallback) and ends the per-project sync fan-out. **Umbrella:** one lobby epic; each phase = its own lane with per-phase approval.

## Already delivered upstream — branch-model migration (2026-08-07, fa1c221)

- `main_debug` retired in EVERY repo, local + origin; all 8 project repos stand on `main`, `0 0`, clean. The old "245 commits ahead" reconcile is done. Gate at merge: toolkit 5/5, AGY 3025 + E2E 31/31.
- `/merge_main_debug` deleted (4 surfaces + manifests) and its job folded: close-out Step 7 lands on `epic/*`; `/sudo-push-e2e` is the one gated door to `main`. Both INDEXes mark it Retired.
- New standard live: `git-policy.md` + `worktree-per-story.md` rewritten (epic branches off `main`, story worktrees off the epic, `chore/*` for ad-hoc); `/sudo-create-epic-sprint` exists (Step 1.5 cuts + pushes the epic branch). 23 residual `main_debug` mentions are all deliberate history notes.
- Push hook rewritten to gate `main` only — **but audit F7 SURVIVES the rewrite (re-verified):**`git -C <path> push|commit` bypasses both jobs (`\bgit\s+push\b` regex + cwd-resolved HEAD).
- **Unchanged, so still ours:** `-Maintained` fan-out intact; Fresh still on `maintained-projects.txt`; `living-template-sync.md` still mandates Fresh; `check_maps.py` floor unchanged. P2/P5/P6 scope confirmed.

## Target architecture

- **Center owns:** `.agents/` master, lobby `.claude/`+`.opencode/` copies, machine-global caches (opencode, Antigravity, Codex). `/sync-agents` = lobby + globals only; filtering + manifest stay.
- **Thin project owns:** `AGENTS.md`, `CLAUDE.md`/`GEMINI.md` pointers, **tier-2 law:** `.agents/rules/` **+** `.agents/skills/` **+** `.agents/INDEX.md`, `_bmad/` (stories + custom tomls), `_bmad-output/`, `_artifacts/`, `_my_resources/`, `docs/` (+`repo-map.md`), code + stack configs, `.gitignore` (keeps ignoring `.claude/` — worktrees stay machine-local).
- **Deleted from projects:** vendored `.agents/{commands,workflows,scripts,opencode-agents,hooks, templates,reference,bmad,adapters,manifests,pointer txts}`, non-project skills/rules, tracked `.claude/`, `.opencode/`, `.gemini/`, `.antigravity/`, `opencode.json`, `.mcp.json`, `.githooks/`.

## Tier-2 project law (rules AND skills)

- Project `.agents/` holds ONLY its own law; `.agents/INDEX.md` routes it (floor = load at bind; protocol = before first write there; on-demand = trigger). Paths keep the `.agents/...` form so existing references survive. Draft ready: `project-law_draft.md` (this folder) → installs as `.agents/rules/project-law.md` in P1.
- **The center AUTHORS project law** — project-specific rules/skills are written into THAT project's tier-2, never the master; `/sudo-update-sprint-memory` learning-routing gains this destination. Project skills load by PATH via the INDEX; slash-everywhere stays master.
- AGY domain skills move home (voice/SSE/RAG/ADK/schema/cloud-run set + `python_inter_venv_fix`). ⚠️ AUDIT F6: `deploy-backend` + `troubleshoot-cloudrun-deployment` STAY master — wired into `/sudo-push-e2e` + `/sudo-mobile-error-team` (migration just re-touched deploy-backend; still master-referenced). Final list confirmed in P3.

## ⛔ The always-check guarantee (the main threat)

Binding a project MUST load its law — five anchors, one mechanism:

1. `sudo-target-resolution.md` **§BIND**: after binding PROJECT_ROOT, read `PROJECT_ROOT/.agents/INDEX.md`, honor its Load column; missing INDEX in a converted project → STOP.
2. New master rule `project-law.md` (tier-2 contract + authoring duty).
3. `constitution.md` line: "binding a project = loading its `.agents/INDEX.md` law."
4. Lobby + project `AGENTS.md` inline anchors.
5. `check_maps.py`: missing INDEX = ERROR — and the BMAD tomls' persistent_facts gain "check {project-root}/.agents/INDEX.md".

## Execution model — under the new git standard

- **Kickoff:** cut `epic/toolkit-centralization` from lobby `main` + push. Manual cut per `git-policy.md` — `/sudo-create-epic-sprint` is project-scoped by design ("never operate on the lobby"); the precedent is the migration itself (`epic/branch-model-migration`). First commit on the epic: this plan v3 + `project-law_draft.md`.
- **Lobby phases P1 → P2 → P6 run sequentially:** each in a worktree `claude/tc-<phase>` off the epic branch, landed on the epic with per-phase approval (close-out or in-the-moment "approved").
- **P3 / P4 / P5 are independent → 2–4 parallel lanes** (the standard lane model). Each target repo gets its own short-lived `epic/thin-toolkit` cut from ITS `main`. The lobby-side halves of those phases (master skill INDEX updates, `autopilot_glm` promote, `/new-project` re-point) land on the LOBBY epic, sequenced there — they all touch master INDEX files, so they never ride project lanes.
- **Landings:** AGY → its `main` via `/sudo-push-e2e` (full gate freshly proven). VR / RAG / skeleton → suite-if-present + Daniel's sign-off. After each project lands: lobby gitlink bump on the lobby epic. Every landing verified per-repo `0 0` + clean.
- **Epic → lobby** `main`**:** `.agents/scripts/tests/run_all.py` green (the 5/5 gate) + Daniel's sign-off, `--no-ff`, branch deleted — the migration's exact landing shape.
- **Jira (separate story, later — per operator memo):** not built in this epic, but the mount seats get marked NOW. P2 drops `JIRA-HOOK:` anchor comments at the four of them: `/sudo-create-epic-sprint` Step 1.5 (ticket mint at the branch cut) · `/sudo-update-sprint-memory` Step 7 (ticket-moved check before the landing push) · `require-push-approval.py` (the enforcement seat for "no push until the ticket moves") · `/sudo-push-e2e` Step 4 (ticket → Done at the epic merge). The Jira story greps `JIRA-HOOK:` and lands on pre-mapped points.

## Phases

**P1 — Law (lobby).** Install `project-law.md` from the draft; §BIND addition; constitution line; `rules/INDEX.md` row; lobby `AGENTS.md` + `router.md` "converted" redefinition; `workspace-standard.md` thin floor. Verify: anchors present; lobby lint pass.

**P2 — Enforcement (lobby scripts).** `check_maps.py`: thin-project floor + STALE-VENDOR ERROR. `sync-agents.ps1`: delete `-Maintained` fan-out + project-vendor + project `-Target` (flag → explanatory error). De-list `Fresh_Workspace_BMAD` from `maintained-projects.txt` HERE (confirmed still listed; else its deliberate old vendor reds the lint until P6). Harden `require-push-approval.py` — F7 re-verified live post-rewrite: cover `git -C <path> push|commit`(regex + resolve HEAD of the `-C` target, not cwd). Delete `/autopilot_mobile` (Decision 1: gone, not parked): `git rm` the master command + `.claude/` copy + INDEX rows — the manifest ghost-purge retires every cache copy on the next sync. Drop the four `JIRA-HOOK:` anchors (kickoff Step 1.5 · close-out Step 7 · this hook · push-e2e Step 4). Verify: `-WhatIf` sync; `tests/run_all.py`; `check_maps --all` (reds = P3/P4 worklist only).

**P3 — AGY pilot** (1,532 tracked vendor files; 29 rules ≈ 7 own + 22 vendored). On AGY `epic/thin-toolkit`. Pre-flight: no live worktrees, clean status, autopilot idle. (a) Inline the gate into `_bmad/custom/bmad-dev-story.toml` + `bmad-quick-dev.toml` — the P3 sub-plan drafts the EXACT toml text (kill-chain + artifact-path facts from `000-PLAN-FIRST-GATE.md`). (b) Engines `scripts/autopilot-dev-story*.ps1`: child cwd = lobby, project as leading $ARGUMENTS; master autopilot docs updated. (c) Tier-2: `.agents/INDEX.md` + own rules + moved-in skills; master + AGY skills INDEXes (lobby epic). (d) Promote `autopilot_glm.md` to master (lobby epic). (e) Rewrite `AGENTS.md` (22 refs) incl. AGY's vendored doc copies (`docs/workspace-standard.md`, `docs/file_structure_rules/*`, `master-implementation-plan.md`): re-point or delete. (f) Delete vendor set; keep pointers; `.gitignore` keeps `.claude/`; unset `core.hooksPath` (both machines). Verify: lint green; `/sudo-boot-sprint-memory AGY` smoke; bmad-quick-dev dry-run SHOWS the inlined gate; dead-ref grep (excl. `_artifacts/`, `_bmad-output/`); land via `/sudo-push-e2e` (full suite + E2E); lobby gitlink bump; `0 0` + clean.

**P4 — NEXgen-VR + RAG_Pipeline_AC.** Same pattern, own epic branches, sign-off merges, gitlink bumps. VR (2,628 files): 2 tomls + 2 engines; content-diff its 30 rules against AGY/master before keeping (stale seeded clones must not survive as "VR law"). RAG (86-file partial vendor, 21 rules): NOT on the maintained list — its vendor is frozen-stale, safe to strip; no tomls/hooks/engines.

**P5 — Skeleton (**`sudomadhatter/sudo-project-skeleton`**).** Clone fresh, measure, strip/build to the thin template: template `AGENTS.md`, pointers, `.agents/INDEX.md` stub, inlined-gate tomls, keep `_bmad/` module + `_bmad-output/` + `_artifacts/` + `_my_resources/` + stack. README = clone quick-start. The `/new-project` + `new-project.ps1` re-point lands HERE (clone skeleton → strip `.git` → `git init` → set `_bmad` identity → print router/.gitmodules rows) — not earlier, so the old-shape window never opens. Verify: fresh clone passes floor lint; `/new-project` dry-run.

**P6 — Freeze + sweep (lobby epic, last lane).** Fresh router status → frozen archive; **rewrite** `living-template-sync.md` (verified still Fresh-mandating) → skeleton-based rule. Docs: `system-builder.md`, repo-map regen, `/update-maps-indexes`. Memory rewrites (\~9: fresh-template, allowlist, sync-scope, autopilot×3 — incl. retiring `autopilot-mobile-mirrors-claude`, AP-twins, check-maps, sudo-skills). No-skeletons ref-grep across lobby + 3 projects + skeleton; full `/sync-agents`; end-to-end sudo smoke on AGY. Then the epic lands: 5/5 gate + sign-off → `main`, branch pruned.

## Decisions (resolved 2026-08-07)

1. `/autopilot_mobile` → **DELETED** — upgraded from "parked" per operator memo: P2 removes `.agents/commands/autopilot_mobile.md` + the `.claude/` copy + INDEX rows; the sync-manifest ghost-purge retires every platform cache copy; P6 retires its memories. Mobile drives the desktop via Remote Control.
2. Project githooks → **dropped** (inert on Mac; lint runs deliberately).

<!-- USER_MEMO
  id="GqN0MiZ8"
  type="question"
  status="needs_review"
  owner="human"
  source="generic"
  color="blue"
  text="we can delete this and remove it from the / commands its gone.&#10;&#10;we are also going to impliment Jira hooks that will be a seperate story but I want you to know that when setting this up you can note were it applys"
  anchorText=""
  anchor="L62|00001505"
  createdAt="2026-08-07T13:26:05.642Z"
  updatedAt="2026-08-07T13:37:20.904Z"
  anchorConfidence="exact"
-->
<!-- REVIEW_RESPONSE to="GqN0MiZ8" -->
Both directives are in the plan (note: the MCP's policy blocks apply_memo on question-type memos, so the edits were made directly and this thread records them):

1. **Decision 1 flipped parked → DELETED.** P2 now `git rm`s `.agents/commands/autopilot_mobile.md` + the `.claude/` copy + INDEX rows; the sync-manifest ghost-purge retires every platform cache copy on the next `/sync-agents`; P6 retires the `autopilot-mobile-mirrors-claude` memory (memory-rewrite count → ~9).

2. **Jira mapped, not built.** The Execution-model bullet now names the four mount seats, and P2 drops a `JIRA-HOOK:` anchor comment at each while it's already in those files: `/sudo-create-epic-sprint` Step 1.5 (ticket mint at the branch cut) · `/sudo-update-sprint-memory` Step 7 (ticket-moved check before the landing push) · `require-push-approval.py` (the enforcement seat for "no push until the ticket moves" — the same hook P2 hardens for F7) · `/sudo-push-e2e` Step 4 (ticket → Done at the epic merge). The future Jira story greps `JIRA-HOOK:` and finds every seat pre-mapped.

Also repaired the two list numberings the editor reflow garbled (five-anchors + decisions). Nothing else changed.
<!-- /REVIEW_RESPONSE -->
3. B-L / BRKN / NEXGen-Films / OpenChat → **untouched**, frozen as-is.
4. `main_debug` retirement + close-out fold → **done upstream** by the branch-model migration; this epic starts clean from `main` under the new rules.

## Risks / skeleton-prevention

Silent gates get POSITIVE verification in P3 before deletions commit. Reachers fixed before their targets are deleted. Pre-flight refuses open story lanes. History docs + history-note `main_debug`mentions stay as-is. Parallel P3/P4/P5 lanes touch disjoint repos; their lobby-side hunks all land sequentially on the lobby epic (shared master INDEX files — never in project lanes). Windows: pull, re-run `/sync-agents`, unset per-project `core.hooksPath`, verify one sudo flow before next sprint. Fresh keeps old vendor deliberately, off the lint list from P2.

## Verification (system-level)

`check_maps.py --all` green after P4; `sync-agents.ps1 -WhatIf` shows zero project targets; AGY ① → ③ story flow runs end-to-end from the lobby; skeleton clone passes floor lint; per-repo `0 0` + clean at every landing.

## Self-Audit (2026-08-07 · re-checked post-migration)

**Level: Full** (enforcement scripts + rule law + multi-repo deletions). Target = lobby + the 3 converting repos + skeleton (home-base plan; child-only default deviated, stated).

- **P0 Scope/AC:** every stated goal traces to a phase; per-phase approval model sound. Cleared.
- **P1 Blast-radius:** traced tomls, engines (cwd verified in both .ps1), hooks (inert on Mac — `core.hooksPath` unset), platform caches (all 3 globals verified live), EnterWorktree nested-repo path, BMAD `{project-root}` binding (unchanged), sync-manifest interplay (P2 before P3 ordering holds). Findings F1–F7 below.
- **P2 Over-engineering:** no tripwires — five anchors justified by operator-named threat; tier-2 skills justified by operator ask; no new abstractions. Cleared.
- **P3 Pre-mortem:** mid-migration Windows session (per-phase atomic landings + P6 verify), lanes open during strip (pre-flight), /new-project between P2–P5 (F2 re-order), gate silently dead (positive dry-run check), Fresh false-reds (F1). Survivor: none unhandled.

| Finding | Severity | Failure scenario | Disposition |
| --- | --- | --- | --- |
| F1 Fresh on lint list until P6 | low | STALE-VENDOR reds mask real signal | fixed — de-list in P2 (re-verified: still listed) |
| F2 /new-project re-pointed before skeleton thin | med | scaffolds old-shape project in window | fixed — moved to P5 |
| F3 AGY doc copies + skills INDEXes unnamed | low | doc skeletons survive the sweep | fixed — named in P3(e)(c) |
| F4 "inline the gate" underspecified | med | dev guesses gate text; gate weakens silently | fixed — P3 sub-plan drafts exact text |
| F5 VR seeded rule copies kept blind | low | stale AGY clones become "VR law" | fixed — content-diff in P4 |
| F6 `deploy-backend`/`troubleshoot-cloudrun` move breaks `/sudo-push-e2e` refs | med | master command loads missing skill | fixed — both stay master (re-verified post-migration) |
| F7 push-hook misses `git -C … push` | med | landing push skips approval prompt | **still live after hook rewrite** — harden in P2 |

**Gates:** verification strategy present per phase ✅ · destructive steps = mass `git rm` (git- recoverable, per-phase sign-off gates) ✅ · vague steps tightened (F3/F4) ✅ · quality fit: phases anchor to existing conventions (INDEX pattern, §BIND, manifest, migration landing shape) ✅.

**Audit verdict: GO** (7 fixes baked; re-baseline 2026-08-07 changed no disposition — F7 confirmed still required, P0-retire-main_debug removed as done upstream).


---

## Self-Audit (2026-08-07) — post-build, pre-merge (operator-ordered)

Right-size: **Full** — audited base `88b079a` (lane) plus all four child branch heads.
P0 scope: traced all six phases against the five branches. P1 blast-radius: `merge-tree`
vs every repo's `main` = **0 conflicts**; full deletion review (~5,700 deleted files) for
load-bearing losses — none found; AGY diff touches nothing under `backend/`/`frontend/`.
P2 drift gate: audit remediation is INDEX routers + map reconciles only — no new
abstraction. P3 pre-mortem: enforcement executed, not assumed — commit hooks run with
bad/good messages, push-approval hook probed three ways, `run_all` re-run at head.

| Finding | Sev | Disposition |
|---|---|---|
| Epic branch sat at P2 (`35b2d80`); pre-flight + P5 + P6 lived only on the `claude/SCC-32-preflight` lane | HIGH | **FIXED** — epic fast-forwarded to the lane head (this commit) |
| All 4 child repos failed the thin floor: tier-2 `rules` / `scripts` / `skills` INDEX routers missing, repo-map AUTO blocks stale | HIGH | **FIXED** — AGY `9627e7e0` · VR `54e6a02` · RAG `5789062` · skeleton `9f2f68c`; all four lint clean |
| Skeleton default branch is still the FAT template (3,239 files) and `/new-project` clones the default branch | HIGH | **SEQUENCING** — merge `chore/SCC-31-thin-template` before any `/new-project` run; `/new-project` gained a post-clone map-localize step |
| Lobby main checkout carries the other lane's uncommitted WIP (mcp.json ×4, `.agents/commands/INDEX.md` + `review.md`, sync-manifest, 2 memory/docs); `.agents/commands/INDEX.md` is also changed by this epic | MED | **PRE-MERGE** — that lane must commit/stash before the lobby merge or git refuses the checkout |
| `reaudit_v4.md` + `.md-feedback/` untracked in the main checkout | MED | reaudit was already tracked at `88b079a` (untracked twin is byte-identical); `.md-feedback/workflow.json` lands in this commit |
| VR carried `.agents/.claude/` gitnexus-skill residue | LOW | **FIXED** in `54e6a02` |
| Center `.agents/skills/` still carries 13 AGY domain packs (tier-2 content in tier-1: hr-agent-schema-guide, voice-ai, SSE patterns, …) — reverse-vendoring, drift risk | LOW | **REPORTED** — one follow-on commit on the operator's word |
| Stale vendored-era prose survives: `docs/workspace-standard.md` (VR · RAG · skeleton), AGY `README.md` toolkit sections, VR/skeleton `AGENTS.md` autopilot row | LOW | **REPORTED** — post-merge doc-sweep candidate |
| Lobby map drift (SCC-26 curated rot + rename journal) predates the epic | LOW | post-merge `/update-maps-indexes` on main |
| False alarms cleared: `_my_resources` conflict-marker = SCC-30 teaching sample (identical on main) · toml "gate refs" = provenance comments, zero `file:` load directives · VR `bmad-*` skills = repo-local BMAD machinery by design (VR ∩ center = ∅) | — | no action |

Environment notes: AGY's working checkout moved to `chore/AVCH-41-sop-twin-jira-flow`
mid-audit (same commit `ec0ba3b2`; fixes went through a temp worktree, since removed).
AGY's 3 residual lint flags there are worktree artifacts — gitignored `.env` / `.venv`
absent in the worktree, present in the real checkout. Session limit blocked subagents;
the audit ran inline.

Verification at head: `run_all` **5/5 files, 20/20 checks** · armed commit gates
live-tested (lobby + AGY: bad msg rc=1, good rc=0; skeleton disarmed: rc=0 + warning) ·
push-approval hook: `main` push → ask, lane push → allow, `git -C <lane> push` → allow ·
secrets scan of the full lane patch: 0 hits · sync `-WhatIf`: machine caches only, zero
project targets.

**Audit verdict: GO** — merge order: **skeleton → lobby → AGY (via `/sudo-push-e2e`) →
VR → RAG**, then gitlink bumps. Lobby precondition: the other lane's WIP lands first.
