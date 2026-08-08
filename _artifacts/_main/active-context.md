# ACTIVE CONTEXT — _main  (you own this, not a vendor)

## 1. PRIME STATE
Current workspace: `_main` (lobby; bucket renamed from `_home` on 2026-06-26)   |   Last session: 2026-08-08
**2026-08-08 (latest): toolkit centralization SHIPPED — the thin model is live on every main.**
Epic SCC-31 + AVCH-23: ~1M lines of vendored toolkit removed; every project now carries only tier-2 law
(rules · skills · INDEX router) + the repo-local enforcement carve-out. Self-audit GO. Merged: lobby
`5e9f1ed` · VR `04bf376` · RAG `68cf6fd` · skeleton `6b96deb`; AGY = operator push of `epic/AVCH-23-thin-toolkit`
(ff, deploy-safe). Session: `_artifacts/_main/2026-08-07_toolkit-centralization/`.
**2026-08-04: rule load class has ONE source of truth, and the protocol tier now loads on a BINDING trigger.**
Audit of `.agents/rules/` found the set already clean on the things people check (all 21 have frontmatter,
`name:` matches filename everywhere, INDEX covers all 21, no ghosts). The rot was elsewhere: **load class
had three sources of truth that disagreed** — `AGENTS.md` §3, the INDEX `Load` column, and a frontmatter
`activation:` field on **12 of 21 rules written in Cursor's vocabulary** ("Always On", "Model Decision")
that **nothing reads** (grep-verified across `.agents/`, `docs/`, `.claude/`, `.opencode/`).
`000-PLAN-FIRST-GATE` — the priority-zero kill-chain — had **three sources giving three different answers**
about when it loads; `powershell-encoding-safety` claimed `Always On`. `activation:` deleted from all 12;
`AGENTS.md` §3 now states the INDEX's three tiers. **Token win:** `artifacts-always-first` (21 KB) stops
loading in conversation-only turns. **⚠️ THE LESSON — Daniel caught it, I didn't:** making the protocol tier
conditional without making the condition **binding** is a regression, not an optimization. §3 said "load the
moment a session may touch files" — descriptive; an agent can read that and never load the plan gate. Now
imperative: **load BEFORE the first tool call that creates, edits, or deletes a file — if you are about to
write and they aren't loaded, stop and load them first.** Plus a standing **anchor invariant**: the four
protocol rules are conditional but **their LAW is not** — every gate they carry is also stated inline in
`AGENTS.md` AND the floor `constitution.md`, so the stop binds even in a session that never opens the rule.
*A protocol rule whose law is not anchored in both is a defect — fix the anchor, never promote the rule to
floor.* The invariant **failed its own first test** and exposed `000-PLAN-FIRST-GATE` with zero references
in `constitution.md` (pre-existing; C2 made it load-bearing) — now fixed. Also: 2 de-dupes landed, **the 3rd
deliberately dropped** (stripping the sign-off summary from floor `constitution` would leave floor deferring
to protocol `git-policy`, which may not be loaded — the exact hole just closed); INDEX regrouped by load
class, proven lossless by sorted-line diff; **EOL integrity check added mid-run** (unplanned — a scripted
frontmatter strip is the `powershell-encoding-safety` bug class; all files 100% CRLF, 0 bare LF).
**Propagated:** `project-template` + AGY §4 + Fresh §4 by hand — `/sync-agents` vendors `.agents/` but
**never writes a project's root `AGENTS.md`** (`sync-agents.ps1:525-532`), so root files are always manual.
**OPEN (corrected — Daniel caught my misread):** `NEXgen-VR-Director` is a **healthy Fresh clone on GitHub**
(`sudomadhatter/NEXgen-VR-Director`, private, `main`+`main_debug`, full skeleton, pushed 2026-08-04 04:41) —
but **this desktop never cloned it**; `Projects/NEXgen-VR-Director/` was an empty 2026-07-30 placeholder and
the sync vendored 3 toolkit dirs into it, which now block a clean clone. Fix: clear placeholder → clone →
hand-apply §4 → re-sync. `RAG_Pipeline_AC` has an AGENTS.md but is NOT maintained, so its vendored rules never refresh.
**UNCOMMITTED ×3** (lobby + AGY + Fresh) and **`/sync-agents` owed first.**
Session: `_artifacts/_main/2026-08-04_rules-folder-optimization/`.

**2026-08-04 (latest): `reproduce-before-you-fix` — the house debug loop is now a rule.**
Debug guidance existed as five scattered one-liners (`karpathy-guidelines:20`, `collaborative-debug-first`,
`sudo-quick-dev:40`, `sudo-mobile-error-team` §4, `sudo-live-testing-team:46`) — but `grep -ri reproduc`
over **every rule and every command** returned **one hit**, a disk path in `sudo-close-workingtree`.
**Reproduction had zero coverage**, and nothing anywhere put a stop condition on the guess-loop. New
on-demand rule with **five gates**: G1 reproduce (a *citable* artifact — command, URL+click path, Sentry id,
or a failing test; "I can see it in the code" is a hypothesis) → G1.5 minimize → G2 pin a test **SEEN red**
and commit it → G3 falsify one hypothesis at a time under stop conditions (**10 min / 3 falsified / 2
no-evidence edits**, house-set and labeled tunable) → G4 minimal fix at the mechanism → **G5 revert the fix
hunk, watch the test go red, restore**. G5 is the gate nobody runs and the only cheap proof a pinning test
isn't passing coincidentally. Two legitimate *endings* keep agents from faking a repro: can't-observe →
`collaborative-debug-first`; genuinely non-reproducible → add observability and stop. **Dispatch matters
more than the rule** — an on-demand rule only fires if something reaches for it, so the pointer went into
`karpathy-guidelines` §1, which is floor. It **references, never restates** (`tests-must-gate-for-real` #1
for right-reason reds, its #4 for revert-don't-delete), so there is no duplicated prose to drift. Also
wired into `/sudo-quick-dev` (pinning test seen red BEFORE the fix) and `/sudo-mobile-error-team` (§4's
"fails on broken code" must be **observed**). Sources: MIT 6.031, Verraes, delta debugging, Google SRE.
**UNCOMMITTED**, and **`/sync-agents` owed** (2 command files + shared rules). Deferred by agreement:
`sudo-live-testing-team` (diagnoses only) and `sudo-dev-story-tests:103` (suite failures, not reported bugs).
Session: `_artifacts/_main/2026-08-04_debug-protocol-rule/`.

**2026-08-04 (latest): Auto-memory is now junctioned into the repo — tooling shipped, NOT yet applied.**
Claude memory lives under a slug **derived from the workspace's absolute path**, so it never leaves the
machine and a rename orphans it. **15 files were already dead** (13 + 2 under two stale slugs from past
renames) because `rename-fix.ps1` repairs `.claude\settings.json` but never knew `projects/<slug>/memory/`
existed. Canonical store is now `_artifacts/_memory/`, linked by `.agents/scripts/link-memory.ps1` /
`link-memory.sh` — **twins by contract**, dry-run by default, and they **never merge or delete**: seed if
canonical is empty, otherwise back the local set aside to `memory.local-backup-<ts>` and report.
**⛔ NOTHING WAS APPLIED ON THIS DESKTOP — deliberate.** This box holds the OLDEST memories; the laptop has
the current ones. **The first machine to link SEEDS the shared store**, so the laptop must go first or
stale memory propagates everywhere. Sequence: (1) commit+push the tooling from here, (2) laptop pulls →
`link-memory.ps1 -All` dry run → `-Apply` → commit `_artifacts/_memory/` → push, (3) desktop pulls + runs
it (its 25 stale files get backed up, not lost), (4) MacBook — **run `ls ~/.claude/projects/` and report
before `--apply`**; the macOS slug shape is inferred from Windows paths and the script refuses rather than
guessing. Also tightened `artifacts-always-first.md`: plans must be pasted **FULLY inline** (link-only = a
gate violation) — found via one of the *stranded* memories, which is a neat proof of what stranding costs.
Still open from earlier today: 3 project repos hold **staged, uncommitted** `adk-prompting` deletions, and
**B-L-WorldWide is on `main`** (owner-only).
Session: `_artifacts/_main/2026-08-04_portable-memory-store/`.

**2026-08-04 (latest): INDEX-depth exceptions are a named list; `.agents/` is now linted.**
`check_maps.py` had `_artifacts` hardcoded as the sole depth exception at 3 call sites. It is now two named
sets — `DEPTH3_DIRS` (index deeper) and `DOT_CONTENT_DIRS` (dot-dirs that are content, not tool cache) — so
adding a folder is a one-line edit. Answering "should `.agents/` index deeper": **no.** Six of its ten
subfolders are flat, `skills/` self-describes through `SKILL.md` frontmatter, `bmad/` is regenerated, and
`templates/project-template/` is a scaffold. It already carried `AGENTS.md`, `INDEX.md`, both adapters, and
an `INDEX.md` in all ten subfolders — the gap was that **check 2.5's dot-dir skip (written for `.ruff_cache`)
made the whole master toolkit invisible to the linter**. It is now scanned, and its four Tier-1 law files are
asserted in check 6. Retired the `adk-prompting` skill (4 dirs + sync-manifest entry): an Antigravity guide
misfiled as ADK, unloadable in its richer copy, whose content `v3-prompt-architecture` already covers and
partly corrects; its one unique idea lives on as v3 #21. `check_maps.py --all` shows **zero new drift** — all
three conformant workspaces clean on both changed checks. **UNCOMMITTED:** run `/sync-agents` first (the
`v3-prompt-architecture` mirror is one section stale by design), then the single commit in the walkthrough.
**Open, needs Daniel:** (1) `5_adk_skills/` nesting hides `adk-agent-development` + `adk-testing-patterns`
from the harness entirely — both genuine and matching the pinned `google-adk==1.26.0`; flattening touches the
sync manifest + 4 caches + 3 vendored copies. (2) ~~vendored copies~~ **DONE** — all 12 deleted via `git rm -r`
(explicit paths) across AGY / Fresh / B-L-WorldWide; 16 dirs gone total incl. the lobby's 4, both real ADK
skills intact everywhere. Deletions are **staged, uncommitted** in all 3 repos; ⚠️ B-L-WorldWide is on
`main` = OWNER-ONLY. **Standing lesson from it:** deletion propagation is *surface-specific* —
`/sync-agents` purges `.claude/skills/` (manifest-tracked per skill folder; a retired skill dir is a command
ghost) but NEVER `Projects/<name>/.agents/skills/`, whose vendor is additive by design because the vendored
`.agents` is a hybrid holding project-owned rules/skills a blanket purge would destroy. Retiring a skill
therefore always needs the manual vendored delete too.
**Retracted from this session:** the two "orphan `.claude/skills/` mirrors" were false positives from a scan
that only compared `.agents/skills/` to `.claude/skills/`. `sudo-merge-epic-workingtrees` is generated from
its master COMMAND `.agents/commands/sudo-merge-epic-workingtrees.md`; `gitnexus` is a 6-sub-skill bundle
mastered at `.agents/.claude/skills/gitnexus/`. Both correct — nothing to delete.
**Do not hand-edit `.sync-manifest.json`** — it is the record of what the last sync wrote, and removing an
entry disables the purge that propagates a deletion (learned the hard way this session; edit reverted).
Session: `_artifacts/_main/2026-08-04_index-depth-exception-list/`.

**2026-07-30 (latest): Artifact ownership rule corrected and histories consolidated.**
Every directory under `Projects/` now owns its artifact history project-locally by default, regardless of
cwd or tool. The complete Sudo-managed exception registry contains only `Fresh_Workspace_BMAD` and
`OpenChat-Openrouter`. Canonical rule/skill/checker/standard copies hash-match across AviationChat, Fresh
Workspace, and NEXgen VR. Migrated the former Sudo buckets for AviationChat (18 files / 146677 bytes) and
NEXgen VR (9 files / 57266 bytes), verified SHA-256 manifests, then removed only those two source folders.
The Sudo `_artifacts/` root now contains `_main`, Fresh Workspace, and OpenChat. No git delivery occurred.
Session: `_artifacts/_main/2026-07-30_project-first-artifact-locality/`.

**2026-07-23 (latest): Fan-out map and INDEX reconciliation complete.**
Regenerated the lobby, AGY AviationChat, and Fresh Workspace AUTO map blocks in their declared modes and repaired all deterministic INDEX drift (including the AGY `frontend/test-results/` index). `python .agents/scripts/check_maps.py --all` now reports that all maps and indexes agree with disk. Still informational: lobby GitNexus is stale and needs a post-commit `node .gitnexus/run.cjs analyze`; AGY's active context is 391 lines with no dated session blocks, so it needs a human decision rather than a mechanical prune. Project git discovery required a per-command safe-directory override because the sandbox user differs from the worktree owner. No commits or map anchors were created.
Session: `_artifacts/_main/2026-07-23_update-maps-indexes/`.

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
## 5. PICK UP  (read-only brief)
- 5.1 Doing: map/index maintenance is complete; no process is running.
- 5.2 Changed this session: regenerated three declared-mode AUTO map blocks; added the missing lobby and AGY artifact-ledger rows; created the AGY `frontend/test-results/INDEX.md` and `epic_debug_2/INDEX.md` inventories; verified fan-out lint clean.
- 5.3 Remaining: after the relevant commits, re-anchor with `python .agents/scripts/check_maps.py --set-anchor --all`; re-index lobby GitNexus; decide whether and how to compact AGY's undated 391-line continuity brief.
- 5.4 Git: do not mass-stage the lobbyâ€”it already contained unrelated uncommitted changes before this reconciliation.
- 5.5 Historical hand-off from 2026-07-14 follows.
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
- 6.1 Completed: the fan-out map/index reconciliation; all deterministic linter checks pass.
- 6.2 In progress: nothing.
- 6.3 Open: lobby GitNexus re-index after commit; AGY continuity-brief compaction needs an authoring decision; map anchors await commits.
- 6.4 Session: `_artifacts/_main/2026-07-23_update-maps-indexes/`.
- 6.5 Historical hand-off from 2026-07-14 follows.
- 6.1 Completed: Refined indexing scopes, synchronized GitNexus graphs, added machine-local index sync documentation, regenerated AUTO blocks, and verified zero drift.
- 6.2 In progress: Nothing executing.
- 6.3 Open tasks / trade-offs: Indexes are machine-local; other machines must re-run analyze after pulling.
- 6.4 Related links: `docs/gitnexus-sync.md`, `_artifacts/_main/2026-07-14_update-gitnexus-graphs/` (plan + walkthrough).
- 6.5 Git: Uncommitted lobby and product files ready for Daniel to commit (commands in walkthrough).
