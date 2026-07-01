# ACTIVE CONTEXT — _main  (you own this, not a vendor)

## 1. PRIME STATE
Current workspace: `_main` (lobby at `C:\Sudo_Hatter_Command`; bucket renamed from `_home` on 2026-06-26)   |   Last session: 2026-06-26
**2026-06-26 (latest): artifact-placement standard codified as 3 rules + `_home`→`_main` rename.** (1) project
work → `_artifacts/<project>/` (create-if-missing), (2) main/cross-project → `_artifacts/_main/` (renamed from
`_home` via `git mv`), (3) stories → under the parent epic folder. **opencode** mirrors all 3 inside its own
`_artifacts/opencode/` namespace. Updated every live standard doc (`AGENTS.md` §5/§7, master
`artifacts-always-first.md`, `workspace-standard.md`, `repo-map.md`, `INDEX.md`) + the SessionStart hook path +
all artifact READMEs (added `_main/` + `Fresh_Workspace_BMAD/` ones). Re-vendored the standard into AGY_AVIATIONCHAT
+ clean-bmad (aviationChat's copy was stale pre-work-from-cwd — re-vendor fixed it). Fixed the 3 `_my_resources/`
diagrams. Zero live `_home` refs remain. Session: `_artifacts/_main/2026-06-26_artifact-placement-standard/`
(UNCOMMITTED — home + both project repos; cmds in walkthrough).
**2026-06-26: owned doc-wiring graph extractor built.** Filled the prose "what references what" layer
GitNexus is blind to (it extracts headings, not doc refs) — surfaced when comparing GitNexus (= our own
`gitnexus@1.6.8`, abhigyanpatwari upstream — we're on latest) vs **graphify** (safishamsi, MIT). Chose owned /
deterministic / no-LLM / $0 over graphify's LLM layer. New `.agents/scripts/generate_doc_graph.py` (mirrors
`generate_repo_map.py`) → `_docs/doc-graph.md` (human: hubs + broken-path/ambiguous/orphan reports) +
`_docs/doc-graph.json` (full): **979 docs / 2427 edges**. Report-only. **Partially addresses the open `.agent/`
(singular) dangling-refs item below** — it auto-surfaces some (`bmad-sm.md → .agent/gemini.md` + 2 ambiguous), but
basename fallback masks others, so a grep sweep is still the exhaustive route. Session:
`_artifacts/_main/2026-06-26_doc-graph-extractor/` (UNCOMMITTED — cmd in walkthrough). graphify noted as the named
MIT break-glass engine for the GitNexus license tripwire.
**2026-06-25: `_my_resources/open_tasks/` standardized as the "what's next" check.** Asking "what's next /
open tasks / what's left" now reads Daniel's notes for **where you work FROM** (lobby → home-base folder; inside a
converted project → that project's own) — on-demand, READ-ONLY, no SessionStart hook. Executed for converted
projects only: **AGY_AVIATIONCHAT** (`git mv`'d 5 notes `_Open_Task/`→`open_tasks/`, removed empty dir, seeded
`todo_list.md`, added READ-ONLY routing row to `AGENTS.md`); **Fresh_Workspace_BMAD** (seeded `open_tasks/todo_list.md`
+ routing row); **lobby** `router.md` row 20 + `_docs/repo-map.md` resolve by where-you-work-from; **memory**
`my-resources-personal-area-protected` carve-out upgraded to system-wide. Committed on origin/main as `fa8bf1b`.
Session: `_artifacts/_main/2026-06-25_open-tasks-standard/`. Maps/indexes verified current this pass (router ✓,
repo-map drift exit 0 ✓, INDEX row ✓).
Phase A + rename-day restructure DONE. **Workspace Standard + repo-map hybrid + artifacts parity landed
(home-base portion).** `_experiment/` is now `_routing-canary/`. One canonical git policy.
**2026-06-25: mobile-mode lane added** — the command center is now driven from a phone; `.agents/rules/mobile-mode.md`
adapts git (agent commits/pushes, asks before PR), the approval gate (tap-to-approve), artifacts (TL;DR-first),
and verification (agent runs in-container) for web/mobile sessions. See `_artifacts/_main/2026-06-25_mobile-mode-rule/`.
**2026-06-25: WS7 + artifact-rule.** The home base now has its own `_docs/repo-map.md` + a SessionStart drift hook
(master `check-repo-map-drift.ps1` gained `-Root`/`-MapPath`; direct `.claude/settings.json` edit worked).
**Artifact rule revised → "artifacts go WHERE YOU WORK FROM"** (cwd decides): from the home base → a per-project
bucket `_artifacts/<project>/` or `_artifacts/_main/`; inside a project → project-local (AGENTS §5/§7, workspace-standard,
INDEX, memory). This session also ran aviationChat **Phase 2** (collapsed `.agent/`→`.agents/`, deleted 1,059 files,
removed forked `.claude/rules/`, GitNexus zero-code) — it lives in `_artifacts/AGY_AVIATIONCHAT/2026-06-25_ws7-and-phase2/`.
**2026-06-25: artifacts-policy reconciliation FINISHED** — wrote `_artifacts/README.md` (the how-to), reconciled
the last stale `_artifacts/<workspace>/` refs (`AGENTS.md` §3 · `workspace-standard.md` Part 1 + appendix · master
`artifacts-always-first.md`) to **work-from-cwd**, refreshed `_docs/repo-map.md` (`--mode content`, drift clean),
and renamed the policy memory → `artifacts-go-where-you-work-from`. Session:
`_artifacts/_main/2026-06-25_artifacts-policy-finish-and-drift-backport/` (commit pending — see its walkthrough).
**2026-06-25: GitNexus index = the command center + open_tasks "what's next".** ONE lobby GitNexus repo
**`SUDO_COMMAND`** = the command center itself — all of `.agents/` (rules · workflows · commands · skills ·
scripts, ~17k nodes), rooted directly at `.agents/` with `--skip-git` to beat GitNexus's dot-folder skip
(`--index-only`; re-index manually after toolkit edits; `.agents/.gitnexus/` gitignored). (A first-pass thin
"portfolio map" showing projects-as-nodes was tried then **dropped** per Daniel — index + its root
`.gitnexusignore` removed.) Caveat: GitNexus extracts headings not doc-refs from markdown → thin edges between
rule/workflow `.md`; read/grep for "what references what". `_my_resources/open_tasks/` is now the READ-ONLY
"what do we do next" source (wired into `router.md` + `_docs/repo-map.md` + the protection memory). Surfaced (open):
~50+ dangling `.agent/` (singular) refs across the master toolkit — needs a deliberate pass, not a blind replace.
Session: `_artifacts/_main/2026-06-25_home-base-maps-gitnexus-opentasks/`. NB: commit `8a40c0f` (on origin/main)
already bundled this session's first-pass repo edits with the prior self-audit work — confirm that was intentional.

## 5. PICK UP  (read-only brief)
- 5.1 Doing: building the home base (folder-as-workspace routing). Latest session executed the approved plan
  `_artifacts/_main/2026-06-24_workspace-standard-and-repo-map/` — Parts F, E, D, A, C + the home-base portion
  of B. Lab-prove + propagation are BLOCKED (see 5.4).
- 5.2 Changed this session:
  - **Rename:** `_experiment/` → `_routing-canary/` (git mv); README rewritten with "when to run" triggers.
  - **Git policy LOCKED (canonical):** never run `git commit`/`push` yourself — hand Daniel the command;
    only commit/push when he explicitly delegates it in the moment. Lives in `.agents/rules/git-policy.md`
    (renamed from the contradictory `git-closeout-commits.md`); `constitution.md` + `artifacts-always-first.md`
    + `AGENTS.md` §6 reconciled to it.
  - **New canonical doc:** `_docs/workspace-standard.md` (how to FORMAT + UPKEEP a workspace; repo-map two
    modes; retire-list appendix). To be vendored into every project's `docs/` later.
  - **Artifacts org scheme** (in `artifacts-always-first.md` §2): bucket rule (file under the workspace the work
    changes; `_main` for cross-project) + random-task `<date>_<slug>` vs story `<epic>/<story>` folders.
  - **Lobby parity:** `AGENTS.md` now has the mandatory artifacts gate + always-loads `artifacts-always-first`;
    NEW `.claude/settings.json` SessionStart hook injects this file + the gate (verified, UTF-8).
  - **Repo-map generator:** `.agents/scripts/generate_repo_map.py` (AST + collapse + curated-header sentinels).
    Proven read-only on ingestion: **514 → 192 lines**, data dirs collapsed.
- 5.3 Earlier (still true): Phase A spine + master toolkit done; rename-day restructure moved 7 projects into
  `Projects\` + path-fixed 262 files; home-base repo pushed (`036ae32`, branch `main`, origin
  github.com/sudomadhatter/Sudo_Hatter_Command, private; `Projects/` gitignored); all 7 project repos
  committed/pushed to their own remotes.
- 5.4 BLOCKED:
  - **CORRECTED 2026-06-25:** the earlier "clean-bmad is OFF-LIMITS / another team" note was wrong.
    `Projects/Fresh_Workspace_BMAD` is **Daniel's own clean-shell template** (the project he clones to start a
    new one). It is fully editable. Active work: `_artifacts/Fresh_Workspace_BMAD/2026-06-25_workspace-standard-cleanup/`
    (standard-conformance + repo-map index; `_01_My/` → protected `_my_resources/`).
  - 5 venvs still hardcode the old path; recreate per-project when next used.
- 5.5 Best next move: (1) finish the clean-bmad workspace-standard cleanup (AGENTS.md renumber, vendor
  workspace-standard + generator, build `docs/repo-map.md`, protect `_my_resources/`); (2) seed the
  generator + standard + hook into the project template and `/sync-agents`. ((3) retire-list `_claude_artifacts/`
  follow-up — ✓ DONE 2026-06-27: autopilot `.ps1` + `1_*` commands repointed to `_artifacts/`, fresh-workspace
  converted to project-local, dead store deleted.)

## 6. HAND OFF  (verified state at this checkpoint)
- 6.1 Completed: Phase A; rename-day restructure; **this session's home-base Parts F/E/D/A/C/B-home** (see 5.2),
  all verified (hook output + generator 514→192 proof pasted in the session walkthrough).
- 6.2 In progress: nothing executing. Plan `2026-06-24_workspace-standard-and-repo-map` is closed for its
  home-base scope; its lab/propagation scope is parked pending clearance.
- 6.3 Open tasks / trade-offs: lab-prove + propagate the repo-map/standard once clean-bmad is cleared; vendor
  `workspace-standard.md` into each project; retire-list `_claude_artifacts/` follow-up ✓ done 2026-06-27;
  per-project rule reconciliation happens during each conversion; cross-LLM cold test of `_routing-canary/` in
  opencode + Antigravity still to run.
- 6.4 Related links: `_docs/workspace-standard.md`, `_docs/master-implementation-plan.md`,
  `_artifacts/_main/2026-06-24_workspace-standard-and-repo-map/` (plan + walkthrough + task-list).
- 6.5 Git: prior home-base sessions (maps/GitNexus, open-tasks standard) are committed on origin/main — latest
  `fa8bf1b`. **UNCOMMITTED now:** the 2026-06-26 doc-graph-extractor session (new `generate_doc_graph.py`,
  `_docs/doc-graph.{md,json}`, `repo-map.md` pointer, this active-context + INDEX). Commit cmd in its `walkthrough.md`.
  Per-session "Your Actions" git commands remain in each `walkthrough.md` for the record.
