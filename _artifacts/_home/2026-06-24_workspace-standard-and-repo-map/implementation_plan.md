---
IsArtifact: true
ArtifactMetadata:
  title: Workspace Standard + Repo-Map Hybrid + Home-Base Artifacts Parity
  type: implementation_plan
  date: 2026-06-24
---

# Workspace Standard, Repo-Map Hybrid, and Artifacts Discipline — Implementation Plan

> **STATUS: PLAN — AWAITING "approved" before any file outside `_artifacts/` is touched.**
> **Workspace:** `_home` (canonical deliverables are home-base). **Lab/testbed:** `Projects/clean-bmad-workspace/`
> (clone of aviationChat-AGY without the live project) — prove everything here before touching live projects.
> **Endgame:** this structure + standard lands on **every** project (aviationChat last), per
> `_docs/master-implementation-plan.md`.
> **Related (separate) plan:** `_artifacts/clean-bmad-workspace/2026-06-24_agents-format-conversion/implementation_plan.md`
> (`.agent/`→`.agents/` conversion + autopilot). See "Coordination" below — that plan and this one overlap in
> clean-bmad-workspace and should be sequenced, not merged.

---

## Goal

Turn the folder-as-workspace routing idea into **durable, enforced doctrine** by delivering four interlocking things:

1. A single canonical reference doc — **`_docs/workspace-standard.md`** — that says how to *format* a workspace
   and how to *upkeep* it, distilled from the transcript theory but written as an evergreen standard.
2. A **repo-map hybrid** that fixes the bloat we found (auto-generated AST signatures for code, collapsed
   data/asset dirs, a preserved human-curated routing header) — built and proven in the clean-bmad lab.
3. **Home-base parity + optimization** of the artifacts / plan-first discipline so the lobby enforces the
   same "sign off on a documented plan, not chat" rule the projects already do.
4. A refined **artifacts organization scheme**: random tasks named by description; stories nested under an
   epic folder so all stories group by parent epic — all under `_artifacts/`.
5. A **reconciliation / de-contradiction pass** over the accumulated rule set (the "starting fresh" cleanup):
   months of edits left the same rule existing in several places with conflicting content; collapse it to the
   home-base `.agents/` single source, resolve the conflicts, and re-vendor so nothing contradicts.

## Findings (answering "did the aviationChat rules make it to the top level, and do they work the same here?")

- **Yes — the rules are present and in better shape at the top level.** `.agents/rules/` has all 12. The two
  that matter here are already genericized and repointed to the shared store:
  - `artifacts-always-first.md` — `activation: Always On`; writes to `_artifacts/<workspace>/…`, references
    `_home`, the `INDEX.md` ledger, and `active-context.md`. (Already ahead of the project copies, which still
    say `_claude_artifacts/`.)
  - `constitution.md` — `activation: Always On`; project-agnostic core + pointer to a per-project
    `constitution.project.md`; reads/writes `_artifacts/<workspace>/active-context.md`.
- **The gap is wiring, not content.** Home-base `AGENTS.md` lists only `constitution.md` + `karpathy-guidelines.md`
  in §3 ALWAYS-LOAD and mentions the artifact protocol only under §7 PERSISTENCE — there is no prominent
  "Artifacts Protocol — MANDATORY FIRST ACTION" gate like the project `CLAUDE.md` files carry.
- **There is no `.claude/settings.json` at the home base** — so the lobby has no SessionStart hook (no
  auto-injection of active-context, no repo-map injection, no forced rule load). Projects have this; the lobby
  does not. This is the core of "make it work the same here."

## Definition of done

1. `_docs/workspace-standard.md` exists: Format half + Upkeep half, universal (defines both a **code-workspace**
   and a **content-workspace** repo-map mode), and names the artifacts org scheme + repo-map standard.
2. Repo-map hybrid proven in `clean-bmad-workspace`: a generated `docs/repo-map.md` (curated header preserved +
   auto body), a working `scripts/generate_repo_map.py` (signatures + dir-collapse), and a SessionStart hook that
   injects the map and emits a detect-only drift line with a sane ignore list.
3. The rule set is **internally consistent**: one `artifacts-always-first.md` and one `constitution.md` (in
   `.agents/`), one git-close-out policy, one artifacts store (`_artifacts/`), zero references to `_claude_artifacts/`
   or `task.md`; legacy/contradictory files (`mandatory-session-artifacts.md`, dead gates) marked for retirement.
4. Home base enforces the same discipline: `AGENTS.md` carries a mandatory Artifacts Protocol gate + ALWAYS-LOAD
   includes `artifacts-always-first`; a home-base `.claude/settings.json` SessionStart hook injects
   `_artifacts/_home/active-context.md` (+ the artifacts gate reminder).
5. `.agents/rules/artifacts-always-first.md` updated with the new org scheme (random-task vs epic/story nesting).
6. Propagation path exists: standard doc + generator + hook config + starter repo-map seeded into the project
   template and master `.agents/`, so `/new-project` stamps them and `/sync-agents` distributes them.
7. Nothing committed/pushed without explicit go-ahead; the one deletion (a stray duplicate map) is confirmed first.

---

## Part A — `_docs/workspace-standard.md` (the canonical reference)

Author one doc, two halves, written as a standard (not a video recap, not a rollout timeline).

- **A1. Part 1 — How to FORMAT a workspace.** The required file set for a compliant workspace and the spec for
  each: one-line `CLAUDE.md`/`GEMINI.md` adapters; the numbered `AGENTS.md` (Map/Mission/Support + routing table
  + "route up to `../../router.md`"); the `docs/repo-map.md` standard; `_artifacts/<project>/` wiring; the
  vendored `.agents/` toolkit. Effectively a checklist `/new-project` (or a person) can follow.
- **A2. Part 2 — How to UPKEEP a workspace.** The maintenance cadence + who/when: router rows on add/remove;
  repo-map drift reconciliation; `active-context.md` + `INDEX.md` on handoff; `.agents/` single-source-of-authorship
  + `/sync-agents` discipline; the end-of-task checklist; the gates. The repo-map standard (Part B) and the
  artifacts org scheme (Part D) are documented here. **Also captures the `_routing-canary/` regression cadence** —
  the standing trigger for *when* to re-run the routing canary (after any change to `AGENTS.md`/`router.md` routing
  structure or the adapter/skill pattern, and whenever qualifying a new LLM/CLI), not just the how (which the
  `_routing-canary/README.md` already has — that README gets the triggers added too). This makes the "when to use it"
  evergreen instead of trapped in the rollout plan or a chat. (Folder renamed from `_experiment/` — see Part F.)
- **A3. Universality.** Explicitly define the two repo-map modes so the standard fits non-code projects too
  (e.g. NEXGen Films): **code-workspace** (signatures + collapsed data dirs) and **content-workspace**
  (folder-level only). Keep the doc model-agnostic (no Claude-only content) so it serves opencode/Antigravity.
- **A4. Cross-link.** Reference it from root `AGENTS.md` §3 and `_system/AGENTS.md`; cite the transcript as
  source theory and `master-implementation-plan.md` as the rollout.

## Part B — Repo-map hybrid (build in the lab, then promote)

- **B1. Generator** — `scripts/generate_repo_map.py` (prototype in clean-bmad-workspace):
  - Emit **AST signatures** (functions/classes) for code dirs.
  - **Collapse** any directory over a threshold (default **8** files) into ONE summarized line —
    e.g. "`rkp_manifests/` — 47 per-lesson JSON, named `PPL_PA_<area>_<task>_<n>_rkp.json`" — instead of
    enumerating every file. This is what cuts ingestion's map from 514 → ~120 lines.
  - **Mode detection:** code-workspace vs content-workspace (presence of `backend/`/`src/` with code →
    code mode; otherwise folder-level content mode).
- **B2. Curated header, preserved on regen** — the generator only rewrites an auto block between sentinels
  (`<!-- REPO-MAP:AUTO-START -->` … `<!-- REPO-MAP:AUTO-END -->`); the human-written "to find X → look here"
  routing table + knowledge map above it (`<!-- REPO-MAP:CURATED-START/END -->`) is never clobbered. This keeps
  the high-value half (which a script can't write) and the always-fresh half (which a human won't maintain).
- **B3. SessionStart hook** — wire into `clean-bmad-workspace/.claude/settings.json`: inject `docs/repo-map.md`
  + run the **detect-only** drift check (list real subdirs, skip an ignore list — `__pycache__`, `.venv`,
  `.pytest_cache`, `node_modules`, `.adk`, `_test_scripts`, `_debug_audio`, `__tests__` — flag any folder on
  disk but missing from the map). Detection nags; the human/agent supplies the purpose line at end-of-task.
- **B4. Make the lab's dangling references real** — clean-bmad's template `CLAUDE.md` already *promises* a
  repo-map + hook that don't exist; B1–B3 deliver them, so the template stops lying.
- **B5. Promote** — once green in the lab: copy generator → master `.agents/scripts/`; seed generator +
  hook config + starter `repo-map.md` + the standard doc into the project template; document in Part A.

## Part C — Home-base artifacts / plan-first parity + optimization

Make the lobby enforce the same documented-sign-off discipline as the projects, optimized (least-context, no dup).

- **C1. `AGENTS.md` gate** — add a prominent **"Artifacts Protocol — MANDATORY FIRST ACTION"** section (mirroring
  the project `CLAUDE.md`) and add `artifacts-always-first` to the §3 ALWAYS-LOAD set. Keep it lean — point to the
  rule, don't restate it.
- **C2. Home-base `.claude/settings.json`** — create it with a SessionStart hook that injects
  `_artifacts/_home/active-context.md` (and a one-line artifacts-gate reminder). This is the lobby parity for what
  projects already get. (Repo-map injection at the lobby is optional — the lobby's "map" is `router.md`, already
  cheap; decide during execution whether to also inject it.)
- **C3. Optimize, don't duplicate** — verify the genericized `.agents/rules/` are the single source and that
  `AGENTS.md` references them by path rather than copying text. Confirm `karpathy` + `constitution` +
  `artifacts-always-first` are the only always-on set; everything else stays on-demand (least-context).

## Part D — Artifacts organization scheme (new convention)

Refine `.agents/rules/artifacts-always-first.md` §2 and document in the standard:

- **Random task** → `_artifacts/<workspace>/<YYYY-MM-DD>_<task-description-slug>/` (date-first keeps chronological
  sort; slug = the task description).
- **Story** → `_artifacts/<workspace>/<epic-name>/<story-name>/` — an **epic folder houses all its stories**, so
  stories are grouped by parent epic rather than sprinkled flat. (Story folders are epic-scoped, not date-prefixed,
  so they read as `epic-9/story-9.4-foo/`.)
- Both still: live TodoWrite during work, `implementation_plan.md` sign-off gate, `walkthrough.md` + `task-list.md`
  at close, one `INDEX.md` row per session.
- **Which workspace bucket** (the question that prompted this): file under the workspace whose files the work
  *primarily changes*. Project-scoped work → that project (e.g. the conversion plan correctly sits under
  `clean-bmad-workspace/`). Home-base / cross-project work → `_home` (e.g. THIS plan: its deliverables are the
  standard doc, master `.agents/`, and the template — home-base, used by all projects; clean-bmad is only the lab).
  This rule gets written into the standard so the choice stops being ad-hoc.

## Part E — Reconcile & de-contradict the accumulated rule set ("starting fresh")

The real problem behind this whole effort: months of edits left the **same rule existing in several places with
conflicting content**. The fix is to make home-base `.agents/` the ONE reconciled source, resolve each conflict
once, re-vendor to every project, and delete the divergent legacy copies — then document the resolved policy in the
standard so it can't re-fork.

**Documented contradictions found (evidence):**
- **`artifacts-always-first.md` exists in 3 incompatible versions.** Home `.agents/` → writes to `_artifacts/`,
  "commit your OWN work at close-out, ask before push," has self-audit §7. clean-bmad & ingestion `.claude/rules/`
  → write to `_claude_artifacts/`, "**NEVER** run git commit/push — provide the command." aviationChat → 
  `_claude_artifacts/` but "you **MAY** commit… ask before push." Three stores, two opposite git policies.
- **`constitution.md` conflicts on git.** Home `.agents/` → "you MAY commit at close-out." clean-bmad & ingestion
  → "**Never** execute git commit or git push." Direct contradiction of the same hard-stop.
- **`mandatory-session-artifacts.md`** (clean-bmad `.claude/rules/`) mandates a `task.md` tracker and an
  "Antigravity artifact directory" and cites a dead `000-PLAN-FIRST-GATE.md` — directly contradicting
  `artifacts-always-first` ("do NOT hand-maintain a parallel `task.md`"). It is legacy and should be retired.
- **Dual rule mirrors** (`.agent/rules/` *and* `.claude/rules/`) coexist in projects from the old two-format world.
- **Stray duplicate** `aviationChat-AGY/_docs/repo-map.md` shadows the live `docs/repo-map.md`.

**The fix (this plan does the home-base + lab portion; live projects follow in the propagation plan):**
- **E1.** Lock the home-base `.agents/` versions as canonical (they are already the most-evolved). Resolve the two
  open policy conflicts explicitly — see Open Question 5 (git close-out policy) — and bake the decision into
  `constitution.md` + `artifacts-always-first.md` + the standard so there is ONE answer.
- **E2.** Mark the legacy/contradictory files for retirement: `mandatory-session-artifacts.md`, dead gate files,
  and every project copy that points at `_claude_artifacts/` or carries the opposite git policy. (Actual deletion
  in live projects = the separate propagation plan + the conversion plan's retire step; here we retire them in the
  **lab** and define the retire-list.)
- **E3.** Re-vendor from master via `/sync-agents` so each project's rules become byte-identical copies of the one
  source — no more per-project drift.
- **E4.** Write the anti-fork rule into the standard: rules are authored ONLY in `.agents/`; project copies are
  vendored, never hand-edited; project-specific hard-stops live in `constitution.project.md`, not in edited copies.

## Part F — Rename `_experiment/` → `_routing-canary/`

"Experiment" mislabels a permanent regression check as throwaway. Rename the folder to `_routing-canary/` and
update every reference in lockstep so nothing dangles:
- Move the folder (git-aware move to preserve history): `_experiment/` → `_routing-canary/` (its internal files —
  `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `agent.md`, `control/agent.md`, `skills/skill.md`, `Power.md`, `README.md`
  — travel with it; only the `_experiment` self-references inside need a path touch where any exist).
- Update references in: root `AGENTS.md` §4 table, `_docs/master-implementation-plan.md`, the `README.md` heading,
  and this plan. **Leave the YouTube transcript as-is** — it's a historical source describing the generic concept.
- Do this BEFORE Part A writes the standard, so the standard documents the final name from the start.

## Propagation model (open call — default chosen)

**Default: vendored copy via sync.** The standard doc lives canonically at `_docs/workspace-standard.md` and is
copied into each project (the same way `.agents/rules/*` are already vendored) so every repo is self-contained and
portable. Alternative (a one-line pointer back to home base) is rejected by default because a project cloned alone
would lose the doc. **Override before approving if you'd rather use pointers.**

## Coordination with the agents-format-conversion plan

That plan rewrites clean-bmad's `AGENTS.md`/`opencode.json` and deletes `.agent/`. To avoid clobbering:
- **Recommended order:** land Part A (the standard) FIRST so the conversion — and every future conversion —
  targets a written spec; then the conversion; then Part B's repo-map hook (so it isn't overwritten by the
  conversion's settings rewrite).
- These stay **separate artifacts**; this plan does not execute the conversion.

---

## Execution order (once approved)

1. **Part F (rename)** — `_experiment/` → `_routing-canary/` + reference updates (quick, do it before the standard
   so docs use the final name).
2. **Part E (reconcile)** — resolve the rule conflicts at the source (`.agents/`), since the standard and
   everything downstream must describe a single coherent rule set, not the contradictory current one. Needs the
   git-policy decision (Open Q5).
3. **Part A** — write `_docs/workspace-standard.md` against the now-reconciled rules (doc; unblocks everything).
4. **Part D** — update `.agents/rules/artifacts-always-first.md` with the org scheme + bucket rule.
5. **Part C** — wire home-base `AGENTS.md` gate + create home `.claude/settings.json` SessionStart hook.
6. **Part B** — build + prove the repo-map hybrid in clean-bmad-workspace (generator, curated header, hook, drift).
7. **B5 promote + E3 re-vendor** — seed generator/hook/map/standard into master `.agents/` + template; `/sync-agents`
   so the lab's rules are byte-identical to the source.
8. Report for verification. **Live-project propagation (Phase 4) is a SEPARATE plan**, executed only after the lab is green.

## Risk / blast radius

- Parts A, C, D and the lab work in B are additive (new files + home-base wiring + a throwaway clone). 
- The only irreversible step in scope is deleting the **stray duplicate** `aviationChat-AGY/_docs/repo-map.md`
  — and that is deferred to the separate live-propagation plan, confirmed before it runs.
- No live project files (aviationChat, ingestion, etc.) are touched by THIS plan. `git commit`/`push` only on
  explicit go-ahead; the `walkthrough.md` will document the exact commands either way.

## Open questions — resolved to defaults (override any before "approved")

1. **Propagation:** vendored copy via sync ✅ (default). → pointer-only if you prefer.
2. **Collapse threshold:** 8 files ✅ (default). → name a different N.
3. **Lobby repo-map injection (C2):** inject `active-context` only, leave `router.md` as the lobby map ✅
   (default). → also inject a root repo-map if you want one.
4. **Random-task folder naming:** keep `YYYY-MM-DD_` date prefix ✅ (default, matches existing). → drop the date
   if you want pure description.
5. **Git close-out policy (needs your call — no safe default).** This is the core contradiction in Part E. Two
   stances exist in the current rules:
   (a) **"Never commit/push — always hand Daniel the command"** (the clean-bmad / ingestion stance), vs.
   (b) **"At story close-out you MAY commit your OWN work via explicit paths, then ask before push"** (the
   aviationChat / current home-base stance, from `git-closeout-commits.md`, written for the multi-team `main_debug`
   repo). Pick the ONE canonical rule for the whole system. My lean: **(a) for the home base and solo projects**
   (simplest, safest, matches "I sign off on everything"), keeping (b) available only where a repo is genuinely
   worked by parallel teams. Tell me which, and I'll bake it into `constitution.md` + `artifacts-always-first.md`.
6. **This folder's location (`_home`):** keep it ✅ (default, per the bucket rule above). → move under
   `clean-bmad-workspace/` if you'd rather co-locate with the conversion plan.
