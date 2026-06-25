# ACTIVE CONTEXT — _home  (you own this, not a vendor)

## 1. PRIME STATE
Current workspace: `_home` (lobby at `C:\Sudo_Hatter_Command`)   |   Last session: 2026-06-25
Phase A + rename-day restructure DONE. **Workspace Standard + repo-map hybrid + artifacts parity landed
(home-base portion).** `_experiment/` is now `_routing-canary/`. One canonical git policy.
**2026-06-25: mobile-mode lane added** — the command center is now driven from a phone; `.agents/rules/mobile-mode.md`
adapts git (agent commits/pushes, asks before PR), the approval gate (tap-to-approve), artifacts (TL;DR-first),
and verification (agent runs in-container) for web/mobile sessions. See `_artifacts/_home/2026-06-25_mobile-mode-rule/`.
**2026-06-25: WS7 + artifact-rule.** The home base now has its own `_docs/repo-map.md` + a SessionStart drift hook
(master `check-repo-map-drift.ps1` gained `-Root`/`-MapPath`; direct `.claude/settings.json` edit worked).
**Artifact rule revised → "artifacts go WHERE YOU WORK FROM"** (cwd decides): from the home base → a per-project
bucket `_artifacts/<project>/` or `_artifacts/_home/`; inside a project → project-local (AGENTS §5/§7, workspace-standard,
INDEX, memory). This session also ran aviationChat **Phase 2** (collapsed `.agent/`→`.agents/`, deleted 1,059 files,
removed forked `.claude/rules/`, GitNexus zero-code) — it lives in `_artifacts/aviationChat-AGY/2026-06-25_ws7-and-phase2/`.
**2026-06-25: artifacts-policy reconciliation FINISHED** — wrote `_artifacts/README.md` (the how-to), reconciled
the last stale `_artifacts/<workspace>/` refs (`AGENTS.md` §3 · `workspace-standard.md` Part 1 + appendix · master
`artifacts-always-first.md`) to **work-from-cwd**, refreshed `_docs/repo-map.md` (`--mode content`, drift clean),
and renamed the policy memory → `artifacts-go-where-you-work-from`. Session:
`_artifacts/_home/2026-06-25_artifacts-policy-finish-and-drift-backport/` (commit pending — see its walkthrough).

## 5. PICK UP  (read-only brief)
- 5.1 Doing: building the home base (folder-as-workspace routing). Latest session executed the approved plan
  `_artifacts/_home/2026-06-24_workspace-standard-and-repo-map/` — Parts F, E, D, A, C + the home-base portion
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
    changes; `_home` for cross-project) + random-task `<date>_<slug>` vs story `<epic>/<story>` folders.
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
    `Projects/clean-bmad-workspace` is **Daniel's own clean-shell template** (the project he clones to start a
    new one). It is fully editable. Active work: `_artifacts/clean-bmad-workspace/2026-06-25_workspace-standard-cleanup/`
    (standard-conformance + repo-map index; `_01_My/` → protected `_my_resources/`).
  - 5 venvs still hardcode the old path; recreate per-project when next used.
- 5.5 Best next move: (1) finish the clean-bmad workspace-standard cleanup (AGENTS.md renumber, vendor
  workspace-standard + generator, build `docs/repo-map.md`, protect `_my_resources/`); (2) seed the
  generator + standard + hook into the project template and `/sync-agents`; (3) tackle the retire-list follow-up
  (autopilot `.ps1` + `1_*` commands still reference `_claude_artifacts/` — engine-coupled, check engine first).

## 6. HAND OFF  (verified state at this checkpoint)
- 6.1 Completed: Phase A; rename-day restructure; **this session's home-base Parts F/E/D/A/C/B-home** (see 5.2),
  all verified (hook output + generator 514→192 proof pasted in the session walkthrough).
- 6.2 In progress: nothing executing. Plan `2026-06-24_workspace-standard-and-repo-map` is closed for its
  home-base scope; its lab/propagation scope is parked pending clearance.
- 6.3 Open tasks / trade-offs: lab-prove + propagate the repo-map/standard once clean-bmad is cleared; vendor
  `workspace-standard.md` into each project; retire-list follow-up (autopilot/commands `_claude_artifacts/`);
  per-project rule reconciliation happens during each conversion; cross-LLM cold test of `_routing-canary/` in
  opencode + Antigravity still to run.
- 6.4 Related links: `_docs/workspace-standard.md`, `_docs/master-implementation-plan.md`,
  `_artifacts/_home/2026-06-24_workspace-standard-and-repo-map/` (plan + walkthrough + task-list).
- 6.5 Git: home-base changes are UNCOMMITTED — exact `git add` (explicit paths) + commit command is in this
  session's `walkthrough.md` "Your Actions". I did not commit (per the git policy).
