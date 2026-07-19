# ACTIVE CONTEXT — _main  (you own this, not a vendor)

## 1. PRIME STATE
Current workspace: `_main` (lobby; bucket renamed from `_home` on 2026-06-26)   |   Last session: 2026-07-14
**2026-07-14 (latest): GitNexus graphs updated & dev tooling excluded. Sync guide created.**
Refined product GitNexus index scope to exclude development/testing tooling (`load/`, `scripts/`, `_test_scripts/`, `auth_keys/`, `scratch/`, and root scripts) from indexing. Documented the new scope in `Projects/AGY_AVIATIONCHAT/docs/gitnexus.md`. Created a new guide [docs/gitnexus-sync.md](file:///c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/docs/gitnexus-sync.md) explaining how the index files are machine-local and do not sync via Git, with instructions for re-indexing other machines. Executed GitNexus analysis on lobby (`Sudo_Hatter_Command`) and product project (`AGY_AVIATIONCHAT`), successfully updating local indexes. Regenerated content-mode AUTO blocks for both repo-maps, and resolved a missing debug index row drift for `password-reset-fix`. Verify maps checks clean (`exit 0`).
Session: `_artifacts/_main/2026-07-14_update-gitnexus-graphs/`.

**2026-07-09: Docs truth-sync + root-law slim DONE — audits passed, drift fixed, canary green.**
Transcript-vs-setup audit: R1–R8 met/exceeded (architecture sound); `/1_update-maps` prune verified
**move-never-delete** (workflow prose + Step-4 gate + `consume()` archives before rewriting). Doc-drift fixes:
`master-implementation-plan.md` (status→built-live, "how to read" banner, §2 tree real names/paths, §4 as-built
§1–§8, §7 historical, new §8 entry), guide `file_folder_structure+maintaining.md` (hook table → 4 SessionStart +
PreToolUse, workspace table synced to router, diagram +`_my_resources`/`_bmad`), `router.md` transcript path.
Root `AGENTS.md` slimmed: grep mechanics → **NEW `.agents/rules/lobby-search.md`** (trigger stays inline §6;
includes the Glob-blind-in-Projects caveat; rules INDEX row added), git-write gate 10→4 lines; §4 +2 rows.
Reconciled: repo-map AUTO regen, `_main` depth-3 INDEX +6 rows, NEW `_artifacts/AGY_AVIATIONCHAT/INDEX.md` +
`_bmad-output/brainstorming/INDEX.md`. **Canary GREEN post-slim** (entry path only → "done boss", Power.md
verified + reset). Per Daniel's memos: **bmad-\* skills + `.agent/` left alone.** OWED (Daniel): explicit-path
commit (other lanes' sudo-\* edits in tree — never `git add -A`) → `--set-anchor` → `/sync-agents` (vendors
lobby-search + fills `.claude`/`.opencode` command INDEXes) → GitNexus re-index → `check_maps_output.txt` call
(TRACKED: delete vs `git rm --cached`+ignore). Surfaced: stray `Projects/aviationChat-AGY/` non-workspace dir.
Session: `_artifacts/_main/2026-07-09_system-docs-truth-sync/`.
**2026-07-04: Tier-2 per-project rollout DONE — the 07-03 session's flagged follow-up is closed.**
AGY_AVIATIONCHAT + Fresh_Workspace_BMAD each carry their 9 Tier-2 files (`_artifacts/`, `_my_resources/`,
`docs/` — local-law `AGENTS.md` + `CLAUDE.md`/`GEMINI.md` adapters, bodies digested from each project's own
canon: AGY keeps `tea/`/local `_main/`/GitNexus-exclusion note, Fresh has neither `tea/` nor GitNexus),
vendored `docs/workspace-standard.md` refreshed hash-identical to lobby canon, reading-order rule in each
root `AGENTS.md` §2, one-doc close aligned (root §5 + `_artifacts/README.md`), repo-map AUTO regenerated
(mode-preserving). Verified: check 8 `[ok] (redirects verified)` in both + AGY negative test; AUTO freshness
`[ok]` ×2. Untouched pre-existing backlog: AGY 14 depth-3 INDEX gaps + stale GitNexus index (re-index AFTER
committing), Fresh dead curated `_bmad/bmm/stories` — a future `/1_update-maps` run's work. Check 8 can go
hint→fatal only after the 3 unconverted projects (B-L, NEXGen, OpenChat) get Tier-1 brains.
Session: `_artifacts/_main/2026-07-04_tier2-project-rollout/`. Git: AGY committed `dc58a20e` (bundled into
story 8.23.2's commit by the live story lane — content diff-verified intact; two-lanes convergence again,
cf. 8.22.2), Fresh committed `52a5c93` **on `main`** (not `main_debug` — flagged); lobby session files
staged, awaiting Daniel's commit + `--set-anchor` (cmds in walkthrough; per-project set-anchor + AGY
re-index owed after the 8.23.2 lane settles).
**2026-07-03: Tier-2 local law — per-folder AGENTS.md as a 3-tier model.** `_artifacts/`,
`_my_resources/`, `docs/` each now carry a ~15-line local-law `AGENTS.md` + 1-line `CLAUDE.md`/`GEMINI.md`
adapters (auto-attached at point of contact — the `_my_resources` READ-ONLY law and `_artifacts` bucket law
self-enforce). Reading-order rule codified: root `AGENTS.md` §1.7 + `workspace-standard.md` Part 1
("folder-file tier model" + PATH CONTRACT row) — folder `AGENTS.md` FIRST, INDEX/README only for inventory.
`check_maps.py` = **8 checks** now (check 8 tier-2 coverage, NON-FATAL hint; promote to conformance once all
workspaces carry the files). Fixed 2 live bugs: linter's regen hint wrote a stray root `repo-map.md`
(cwd-relative `--output`); `generate_repo_map.py` default-root resolved to `.agents/`. Synced lobby + globals +
AGY + Fresh (md5 ×3). Diagram doc `file_folder_structure+maintaining.md` updated (Daniel-directed). **OPEN:**
per-project Tier-2 rollout (AGY/Fresh: 9 files each + vendored `workspace-standard.md` — docs/ isn't synced);
their lints show the check-8 hint until then. **Round 2: `/1_update-maps` is now THE verify command** —
check 8 content-verifies adapters/law, **NEW check 9 verifies GitNexus index freshness** (`lastCommit==HEAD`;
caught lobby + AGY genuinely stale), workflow Step 3.7 creates/repairs Tier-2 files, Step 6 hands off re-index
cmds. **⚠️ `.gitnexus/meta.json` embeds the GitHub PAT cleartext — rotate + switch remote to
credential-manager auth.** Session: `_artifacts/_main/2026-07-03_tier2-local-law/` (batch 1 committed
`4be629b`; round-2 cmds in walkthrough Addendum).
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
- 5.1 Doing: maintaining GitNexus indexing and map/index health.
- 5.2 Changed this session:
  - Excluded development, testing, and credential tools from the `AGY_AVIATIONCHAT` GitNexus indexing in `.gitnexusignore`.
  - Created a synchronization guide at `docs/gitnexus-sync.md` explaining that the compiled index is machine-local.
  - Linked the sync guide in the `docs/gitnexus.md` files of both workspaces.
  - Updated GitNexus index graphs locally for Sudo_Hatter_Command (lobby) and AGY_AVIATIONCHAT.
  - Regenerated content-mode AUTO blocks for both repository maps.
  - Added the missing index row in `Projects/AGY_AVIATIONCHAT/_artifacts/debugging/INDEX.md` for `2026-07-14_password-reset-fix/`.
  - Verified maps and indexes are clean (`exit 0`).
- 5.3 Git status:
  - Lobby: Modified `_artifacts/INDEX.md`, `_artifacts/_main/INDEX.md`, `docs/gitnexus.md`, `docs/repo-map.md`. Untracked `docs/gitnexus-sync.md`, `_artifacts/_main/2026-07-14_update-gitnexus-graphs/`.
  - Product (`AGY_AVIATIONCHAT`): Modified `.gitnexusignore`, `docs/gitnexus.md`, `docs/repo-map.md`, `_artifacts/debugging/INDEX.md`, and local gitnexus skills.
- 5.4 Best next move: Daniel commits changes in both repositories and runs `python .agents/scripts/check_maps.py --set-anchor --all` to baseline map diffs.

## 6. HAND OFF  (verified state at this checkpoint)
- 6.1 Completed: Refined indexing scopes, synchronized GitNexus graphs, added machine-local index sync documentation, regenerated AUTO blocks, and verified zero drift.
- 6.2 In progress: Nothing executing.
- 6.3 Open tasks / trade-offs: Indexes are machine-local; other machines must re-run analyze after pulling.
- 6.4 Related links: `docs/gitnexus-sync.md`, `_artifacts/_main/2026-07-14_update-gitnexus-graphs/` (plan + walkthrough).
- 6.5 Git: Uncommitted lobby and product files ready for Daniel to commit (commands in walkthrough).
