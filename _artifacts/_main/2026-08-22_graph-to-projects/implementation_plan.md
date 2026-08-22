---
IsArtifact: true
ArtifactMetadata:
  title: Code graph to projects only; centre maps + SOP self-refresh by hook; tickets become fast reads
  type: implementation_plan
  date: 2026-08-22
  ticket: SCC-288
  riders: [SCC-289, SCC-290, SCC-291]
  twin: AVCH-78
  lane: chore/SCC-288-graph-to-projects
---

# SCC-288 — graph to projects · maps self-refresh · fast-read tickets

**Mode: CONSOLIDATED** — one lane (`chore/SCC-288-graph-to-projects`), one plan with three part
sections, each part a rider under SCC-288 keyed per commit. Why: same repo, same lane class (toolkit
scripts / hooks / commands / rules / docs, zero deployable paths), and the parts share files (the SOP,
`smh-code-review.md`, `jira.md`) so they are sequenced, not parallel. The AviationChat half cannot ride
this lane (its commit gate answers only to `AVCH`) — it is **AVCH-78**, its own lane in that repo, with
its own plan at `Projects/AGY_AVIATIONCHAT/.claude/worktrees/AVCH-78-graph-scope-hooks/_artifacts/_main/2026-08-22_avch-78-graph-scope-hooks/implementation_plan.md`.

**Build order: A → B → C.** A is the smallest and removes noise from every later gate run. B changes
the hooks, so every commit after it exercises the new pre-commit on real work. C last, so this lane's
own close-out is the first to use the new ticket tool on its own tickets.

## 1. Goal — what the operator asked for (2026-08-22, this session)

1. *"I dont think we need this graph at the command center level at all. only the project level. lets
   just remove it and verify the system we have runs well."* and *"if we need it for the /Projects …
   then we keep those parts."* → **Part A.**
2. *"the only place I really wanted a code-graph was for the SOP document … it also has all the
   workflows and scripts … helpful to map."* and *"is there a hook we can do for SCC too so the
   documents folder our sources of truth never get stale? and its always runs? instead of me having
   to run the / command?"* → **Part B.**
3. *"for the jira tickets those need to be fast reads in the description of what the plan is not the
   plan. the plan should always be in the artifacts and attached to the ticket … utilize the
   description for the outline and task list of what we want to do what we did."* → **Part C.**
4. *"Give the agents real tools to do the job."* — every part ships a script with a test, not prose.

## 2. Findings this plan rests on (measured, not believed)

| Finding | Evidence |
|---|---|
| The centre is markdown; the code graph parses code only | `parser.py:715 EXTENSION_TO_LANGUAGE` has no `.md`; GitNexus' old lobby index had 35 `.md` nodes and **zero** under `.agents/` |
| The SOP was the ONE doc GitNexus graphed, and the new engine cannot | `.gitnexus/gitnexus.json` lists `docs/_scc_sops_prds/workflows_testing_SOP.md` |
| The SOP is 3,924 lines, 193 revisions in 30 days, 46 commands, 201 links, 45 mermaid diagrams, zero confirmed drift | `git log --since=30.days --oneline -- docs/_scc_sops_prds/workflows_testing_SOP.md \| wc -l` = 193 |
| `risk_seam.py` has no `--repo`; `_repo_root(None)` = `git rev-parse --show-toplevel` **of cwd** | `risk_seam.py:84-89`, `main()` at 290-297; the 4 doors call it with cwd = the centre |
| `docs/doc-graph.*` was generated from a worktree that no longer exists; nothing regenerates it | `doc-graph.json` `root` = `…/.claude/worktrees/SCC-270-code-review-graph-swap/.agents` |
| The doc graph is deterministic and costs 0.14 s; the repo-map AUTO block is deterministic too | run twice, `diff -q` identical; both AUTO blocks are stale today (6 vs 5 files in `docs/migrations/`; `git-policy.md` out-degree 5 vs 3) |
| `check_maps.py` is not in any git hook; it runs at SessionStart (`--depth3-only`), in the ceremony and in `run_all` | `.githooks/pre-commit` = encoding lint only; `post-commit` = drift recorder |
| acli cannot ADD attachments; its stored credential is not a REST token | `acli jira workitem attachment` = `list`/`delete` only; `/rest/api/3/myself` with the keychain value → **401** |
| ADF `taskList` lands in a description via `--description-file` | SCC-288 created with `['paragraph','heading','taskList','heading','bulletList',…]` — it renders as checkboxes |
| REST attachment add is possible once a token exists | `POST /rest/api/3/issue/{key}/attachments` + `X-Atlassian-Token: no-check` (404 today = unauthenticated) |

## 3. Decisions (read these; the file list follows from them)

1. **The centre runs with no code graph of its own.** No MCP server, no ignore file, no index. Check 9
   in `check_maps.py` already says "No index → skip" and stays as it is. What the centre KEEPS is the
   project-facing tooling: `risk_seam.py`, the `code-review-graph` skill, `docs/code-review-graph.md`
   (rescoped to "this is what projects carry").
2. **The one graph consumer gets a root argument.** `risk_seam.py classify --repo <root> <paths…>`;
   the pure-Python path (no graph → `unclassified`) stays the normal path and is never a gate.
3. **Maps refresh is a `pre-commit` git hook, not a Claude hook.** A Claude `Stop` hook runs only in
   Claude Code and leaves a dirty tree; a git hook fires for all four platforms on both machines, and
   the post-commit recorder already journals drift the same way. The ceremony
   (`/smh-update-maps-indexes`) stays for the **curated** layer — one-line purposes, INDEX prose,
   AGENTS pointers — which a hook cannot write. The hook owns the **generated** layer and makes the
   hand layer fail loud.
4. **The doc graph covers `docs/` as a second root, anchored at the lobby.** No code-graph
   registration of `.md` (tree-sitter has a markdown grammar; mapping headings to function nodes makes
   impact/dead-code/communities nonsense — measured under SCC-270). The doc graph is stdlib, $0,
   deterministic, and already exists.
5. **Truth checks ratchet, they do not demand zero on day one.** Broken-path refs may not INCREASE
   against the committed baseline; the reverse door check ("every house door is named in the SOP")
   is armed at zero misses because the SOP already names all of them.
6. **Ticket descriptions are the fast read; the tree is the spec.** Shape: `Why:` one paragraph ·
   `## Plan` checklist (ADF `taskList`, ticks in Jira) · `## Done` (filled at close-out) · `## Files`
   (repo path + GitHub link + the file attached). One script renders and attaches it.
7. **The attach token is the helper's own, never acli's.** Resolution order `$JIRA_API_TOKEN` →
   OS store entry `sudo-jira` (Mac `security`, PC Credential Manager via PowerShell) → fail with a
   message that says how to store one. The token is never printed, logged, or written.
8. **Operator action, one time, per machine (C0):** create an Atlassian API token and run
   `security add-generic-password -a sudomadhatter@gmail.com -s sudo-jira -w` (Mac; the command
   prompts for the secret — paste, never type it on the line). PC: `cmdkey` cannot store a readable
   secret; use `Set-Secret -Name sudo-jira` (SecretManagement) or `$env:JIRA_API_TOKEN` in the
   user environment. Until C0 is done, `attach` exits 5 with that instruction and nothing else breaks.

## 4. Part A (SCC-289) — Centre drops its own code graph; `risk_seam` reads the PROJECT's graph

| Step | Change | Proof (the assertion `/smh-quick-dev` writes RED first) |
|---|---|---|
| A1 | `.mcp.json`, `.claude/mcp.json`, `.antigravity/mcp.json`: remove the `code-review-graph` server; `md-feedback` stays. `.opencode/mcp.json` already carries only `md-feedback` | `test_command_surfaces.py`: the four MCP configs declare the same server set, and it does not contain `code-review-graph` |
| A2 | DELETE `.code-review-graphignore`. `.gitignore` keeps `.code-review-graph/` (a stray index is still ignored). The two live references found at audit (F6) are edited in the same commit: `docs/_scc_sops_prds/file_folder_structure+maintaining.md:87` and the docstring at `test_sops_prds_folder.py:9` (no assertion reads the file) | grep `code-review-graphignore` outside `_artifacts/` and `docs/code-review-graph.md` = 0 hits |
| A3 | `AGENTS.md:281-282`: "The lobby index maps the master toolkit" → "The lobby carries **no** code graph; projects do. Inside a project, ask the graph before you grep (`.agents/skills/code-review-graph`)" | `test_doc_examples_parse.py` still green; grep `lobby index` = 0 hits |
| A4 | `docs/code-review-graph.md`: the two lobby mentions → projects-only; add §"The centre has no index by design — `check_maps` check 9 skips". **Also** `docs/repo-map.md:39-42` (CURATED): *"ONE index, rooted at the repo root … 1073 of its 1102 nodes are `.agents/`"* describes the index this part removes — rewritten to the projects-only sentence (F5) | grep `lobby` in the doc = 0 hits that claim an index; `docs/repo-map.md` CURATED block no longer names an index |
| A5 | `risk_seam.py`: `classify [--repo <root>] <paths…>`; `_repo_root(root)` keeps the cwd fallback; the JSON echoes `root`; paths are resolved against it | `test_risk_seam.py` new case: run from a temp cwd that is a different git repo, pass `--repo <fixture>`, assert `result["root"] == fixture` and `unclassified` is reported against the FIXTURE's paths, not cwd's |
| A6 | `cicd-code-review.md:118`, `cicd-self-audit.md:166`: add `--repo "$WORKTREE"`; `smh-code-review.md:88`, `smh-self-audit.md:179`: add `--repo "$REPO"` and **trim the dead `test_links` passage** (smh-code-review 91-112) to one paragraph: the centre carries no graph, `unclassified` is the normal answer here | `test_command_surfaces.py`: every `risk_seam.py classify` call site carries `--repo`; `workflow_lint.py` clean |
| A7 | **Verify-only.** At audit time neither `.agents/skills/INDEX.md:24` (the clean-code row) nor `workspace-structure/SKILL.md:28` (points at `docs/code-review-graph.md`) claims a lobby index — expected no-op; a Declared Change Set bullet is added only if the build finds wording to change | grep for "lobby index" across `.agents/skills/` = 0 |
| A8 | `sentry-security-team-avch.md` (command + workflow): its graph calls name `--repo` the AGY root | grep shows `--repo` on each call |
| A9 | SOP: §code review — the risk-seam paragraph says where the graph lives (projects) and what the centre returns (`unclassified`); changelog entry | `sop_currency.py` passes because the SOP is staged |
| A10 | `docs/doc-graph.md` CURATED block: "the layer the code graph does not model" sentence updated to "the centre has no code graph; this IS the centre's graph" | (B10 rewrites this block anyway — A10 is the one-line interim) |

Not touched, on purpose: `check_maps.py` check 9 and `test_check_maps_graph_fresh.py` (skip-on-no-index
is already the behaviour), `.sync-manifest.json` (it syncs the project-facing skill), the
`code-review-graph` skill.

## 5. Part B (SCC-290) — Doc graph covers `docs/` + the SOP; maps self-refresh by pre-commit hook

### B-i · the doc graph grows a second root

| Step | Change | Proof |
|---|---|---|
| B1 | `generate_doc_graph.py`: `--root` becomes repeatable (default `.agents` + `docs` when none given); `--lobby` (default: `git rev-parse --show-toplevel` of the first root, else `root.parent` when `root.name == ".agents"`); node ids and `scope_files` are **lobby-relative** (`.agents/rules/x.md`, `docs/_scc_sops_prds/workflows_testing_SOP.md`); `resolve()` adds the `lobby/<target>` candidate and keeps the basename fallback; `graph["root"]` and the md `Scope:` line carry the relative roots, never an absolute path | new `test_doc_graph.py`: temp lobby with `.agents/rules/a.md` → `../../docs/x.md` and `docs/x.md` → `.agents/rules/a.md`: both `resolved`; a bare `cicd-foo.md` basename resolves when unique; `root` in JSON is relative; two runs → identical bytes; a run from a different cwd → identical bytes |
| B2 | Re-measure the SOP's dangling list after B1 and **work it**: of 38 flagged today, 17 are resolver false positives (gone after B1) and 21 are bare basenames — fix the real ones in the SOP or accept-list them with a reason | walkthrough carries before/after counts; `broken_paths` for the SOP ≤ 21 and every remaining one has a stated reason |
| B3 | `docs/doc-graph.md` CURATED block rewritten for the two-root scope; `docs/doc-graph.*` regenerated from the lobby | file header names both roots; `root` relative |

### B-ii · the hook

| Step | Change | Proof |
|---|---|---|
| B4 | NEW `.agents/scripts/refresh_maps.py` — `--staged` (pre-commit): read `git diff --cached --name-only`; trigger only when a staged path is under `.agents/` or `docs/`, or a top-level entry was added/removed; otherwise exit 0 in < 50 ms. On trigger: regenerate `docs/doc-graph.md` + `.json` (B1 roots) and the `docs/repo-map.md` AUTO block (mode from `check_maps.declared_mode`, ignores from `check_maps.default_regen_ignore` — one source of truth with check 1); write only if changed; `git add -- docs/doc-graph.md docs/doc-graph.json docs/repo-map.md` (explicit paths, the only `git add` the hook ever runs); print one line per refreshed file. `--verify` (pre-push, check 10): regenerate to memory, compare with disk, list what differs, exit 1 | new `test_refresh_maps.py` against `_repo_template.py`: no trigger → nothing written, exit 0; a staged `.agents/rules/new.md` → three files regenerated AND staged (`git diff --cached --name-only` lists them); a second run → no change, nothing staged; `--verify` on a stale map → exit 1 naming the file; a commit made with the hook leaves `--verify` exit 0 |
| B5 | Truth checks inside `--staged` (fatal, bypass = `--no-verify`, kill switch = `.agents/scripts/git-hooks/DISABLE`): **ratchet** — `broken_paths` may not exceed the count in `git show HEAD:docs/doc-graph.json`; prints the NEW broken refs with their source line. **Reverse door check** — every `.agents/commands/<name>.md` (excluding `INDEX.md`, `*-AP.md`, and the vendor set `analyst architect bmad-help bmad-master dev pm qa sm tea tech-writer ux-designer testarch-*`) must be named as `/<name>` in the SOP; armed at zero because the SOP already names all 46 house doors (`sentry-security-team-avch` is verified at build; if it is missing that is a real finding and gets its SOP line, not an exemption) | `test_refresh_maps.py`: add a link to a missing file → exit 1 with the ref named; add `cicd-new.md` without an SOP line → exit 1 naming `/cicd-new`; the vendor set → no failure |
| B6 | NEW `.agents/scripts/git-hooks/pre-commit-maps.sh` (probe `python3 → python → py`, same as the encoding gate; DISABLE switches honoured; missing script → allow). `.githooks/pre-commit` runs **maps first, then encoding** — the encoding lint must see the final staged set. **Arming:** both delegates are tracked at mode `100755` and flagless, exactly like `pre-commit-encoding.sh` — `hooks_armed.py:81-83` executable-checks every tracked `*.sh` in `git-hooks/`, so no `ARM_FLAGS` row is needed. ⚠️ **AUDIT FINDING F2:** `install-encoding-hook.ps1:58-66` overwrites any existing `pre-commit` that merely *contains* the marker `pre-commit-encoding` with its own three-line body, and `.githooks/pre-commit` line 2 carries that marker — a PC run of the installer would silently drop the maps delegate. The installer now refuses when the existing file is ours-but-different (`$existing -ne $body` → the existing "chain it by hand" message) | `test_hooks_armed.py`: `pre-commit-maps.sh` joins the seeded/armed set; `test_git_hooks.py`: pre-commit invokes both delegates in that order; `test_install_git_hooks.py`: an extended dispatcher is REFUSED, an identical one is re-written, a foreign one is refused (existing case) |
| B7 | NEW `.agents/scripts/git-hooks/pre-push-maps-verify.sh`; `.githooks/pre-push` runs it before the merge backstop (it needs no refs). Stale map → push refused with the regen command printed. This is what catches merge commits and `--no-verify` commits | `test_hooks_armed.py` / `test_git_hooks.py`: verify delegate present, armed, ordered before the backstop; a stale tree → push refused |
| B8 | `check_maps.py` **check 10** (fatal): doc-graph freshness via `refresh_maps.verify()` (import, no subprocess). SessionStart wiring unchanged (`--depth3-only` is deliberate). ⚠️ **AUDIT FINDING F1:** `--all` fans out over every conformant project (`fan_out_targets`, `check_maps.py:220`) and no project carries a doc graph — check 10 runs **only where `docs/doc-graph.md` exists**, mirroring check 9's `if not db.exists(): return []` (`check_maps.py:566`); otherwise every project FAILS the ceremony on its next run | `test_check_maps.py`: stale doc-graph → FAIL naming check 10; fresh → clean; **a root with no `docs/doc-graph.md` → check 10 silent** |
| B9 | `smh-update-maps-indexes.md` Step 1: the doc-graph regen line; a note that the hook owns the AUTO layer on every commit and this ceremony reconciles the curated layer; Step 6 close-out mentions check 10 | `workflow_lint.py` clean; SOP staged |
| B10 | Windows: both generators already write `encoding="utf-8"`; `refresh_maps.py` sets `sys.stdout.reconfigure(errors="replace")` and prints ASCII only | `test_refresh_maps.py` asserts ASCII-only output |
| B11 | Memory + continuity: `_artifacts/_memory/sop-doc-currency-gate.md` and `_artifacts/_main/active-context.md` still name `_my_resources/_quick_reference/sudo_workflows_testing.md` (moved 2026-08-10, SCC-74) → `docs/_scc_sops_prds/workflows_testing_SOP.md`. Per AGENTS.md §7 the memory edit rides this lane | `test_memory_store.py` green; grep for the old path = 0 hits in both files |
| B12 | SOP: new §"Maps refresh hook" (what fires, what it stages, the ratchet, the reverse check, the bypasses) + the doc-graph scope; changelog | `sop_currency.py` satisfied |

Performance budget for B4: < 1 s on a triggered commit (doc graph 0.14 s measured; repo-map content
mode is the same regen check 1 already runs at SessionStart). A non-triggered commit pays one
`git diff --cached --name-only`.

## 6. Part C (SCC-291) — Tickets are fast reads; plans live in the tree and attach to the ticket

| Step | Change | Proof |
|---|---|---|
| C1 | NEW `.agents/scripts/jira_ticket.py` (stdlib only; console ASCII; `--site`/`--email` override `acli jira auth status`): **`outline <file.md>`** renders the fast-read ADF to stdout (no network; the dry run); **`describe --key K --outline <file.md> [--files …]`** writes it to the description via `acli … edit --description-file` (reuses `jira_feed.acli_bin` so the test stub works); **`attach --key K --file <path>`** POSTs the file (`X-Atlassian-Token: no-check`, multipart, urllib); **`done --key K --tick <n,m> --done-line "…"`** ticks Plan items and appends to `## Done` by re-rendering from the outline file. Exit codes: 0 ok · 2 bad args/outline · 4 transport · 5 no token (prints the C0 instruction). The token is resolved per Decision 7 and **never printed** | new `test_jira_ticket.py`: `outline` on the house outline → exactly the node sequence SCC-288 has; `describe` through the acli stub passes `--description-file`; `attach` against a local `http.server` thread receives a multipart body with the filename and the no-check header; with no token → exit 5 and the message names `sudo-jira`; token text never appears in stdout/stderr |
| C2 | `.agents/rules/jira.md`: §"The ONE test" SCC row → "the attached plan + the ticket's checklist"; §"Minting them" → `--description-file` from `jira_ticket.py outline`; new §"The description is the fast read" (shape, the four headings, size guidance: a Plan of 4–8 lines) | `test_rule_frontmatter.py` green; `workflow_lint.py` clean |
| C3 | `smh-plan-task.md`: Step 1 writes the parent's outline file beside the plan (`ticket-outline.md`); Step 2 mints riders from rider outlines; Step 3.5 = `describe` + `attach` the plan (path + `blob/<branch>/` link). `smh-close-task-merge-tree.md --after-merge`: `done` ticks the Plan, appends the Done lines from the walkthrough, attaches `walkthrough.md`, rewrites the Files link to `blob/main/` | `test_command_surfaces.py`: both doors name `jira_ticket.py`; SOP staged |
| C4 | `docs/_scc_sops_prds/jira_integration_guide.md` §"Fast-read tickets" (the shape, the C0 token step per machine, the verbs); `jira_manual.md` step 5 (Description = the outline, not the plan); SOP §Jira | `sop_currency.py` satisfied |
| C5 | Flag, not fix: `jira_feed.py mint` still renders a Story description from the story file; it should adopt the same shape. Filed as a line in the walkthrough's deferred work with the structural reason (it is the BMAD lane's seam and this lane is the Task lane) | walkthrough `## Deferred` row |

## 7. Port check (MANDATORY RULE 5) — files that exist in both repos

```
git diff --no-index --quiet -- docs/code-review-graph.md Projects/AGY_AVIATIONCHAT/docs/code-review-graph.md ; echo differ=$?   → differ=1
git diff --no-index --quiet -- .githooks/pre-commit  Projects/AGY_AVIATIONCHAT/.githooks/pre-commit  ; echo differ=$?   → differ=1
git diff --no-index --quiet -- .githooks/post-commit Projects/AGY_AVIATIONCHAT/.githooks/post-commit ; echo differ=$?   → differ=1
record_map_changes.py / check_maps.py / generate_repo_map.py → no AGY copy under .agents/scripts
git diff --no-index --quiet -- .agents/scripts/check_maps.py            Projects/AGY_AVIATIONCHAT/scripts/check_maps.py            ; differ=1   (F8)
git diff --no-index --quiet -- .agents/scripts/generate_repo_map.py     Projects/AGY_AVIATIONCHAT/scripts/generate_repo_map.py     ; differ=1
git diff --no-index --quiet -- .agents/scripts/check-repo-map-drift.ps1 Projects/AGY_AVIATIONCHAT/scripts/check-repo-map-drift.ps1 ; differ=1
```

⚠️ **AUDIT FINDING F8:** AGY carries VENDORED copies of three maintenance scripts under `scripts/`, and all
three already differ from the masters. This lane edits the master `check_maps.py` (check 10) and does
**not** port it: check 10 runs only where `docs/doc-graph.md` exists (F1), so AGY's copy would gain a check
that never fires; the vendored copies are the maintained-projects lint worklist's business, not this lane's.
`generate_repo_map.py` and the drift nag are untouched here.

All three differ **by design, in both directions, and none is ported by this lane**:

- `docs/code-review-graph.md` — two different documents with one name. The centre's copy becomes the
  tool reference projects read; AGY's copy (AVCH-78) documents AGY's scope and hooks. Neither should
  equal the other after this lane; AVCH-78's plan says the same.
- `.githooks/pre-commit` — the centre's carries the SCC-32 worktree guard and, after B6, the maps
  delegate. AGY has no doc graph and reconciles its repo-map through `check_maps.py --root`; porting
  the maps hook there would regenerate a map nothing reads. Not ported.
- `.githooks/post-commit` — AGY's gains the code-graph `update` line (AVCH-78); the centre has no
  graph, so that line is not ported back. The drift recorder call both carry is unchanged.

### Port Checklist — the six checks, answered for the scripts this lane writes

The files in SCOPE that a second repo, a worktree, a submodule or the PC will run are the two hook
delegates, `refresh_maps.py`, `jira_ticket.py` and `risk_seam.py`. Each check below names the command
that answers it; the walkthrough pastes the output at the tip.

| # | Check | Answer | Command that answers it |
|---|---|---|---|
| 1 | A path git gave you is used as given | The delegates do `REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"` exactly like `pre-commit-encoding.sh`; `refresh_maps.py` runs with cwd = that root and passes paths through; `risk_seam.py --repo` uses the argument as passed. Neither touches `--git-common-dir`/`--git-path` | `grep -n 'git-common-dir\|--git-path' -A 6 .agents/scripts/refresh_maps.py .agents/scripts/git-hooks/pre-commit-maps.sh .agents/scripts/git-hooks/pre-push-maps-verify.sh .agents/scripts/risk_seam.py` → 0 hits |
| 2 | `printf`, not `echo`, for operator-facing lines | Both `.sh` delegates use `printf` only; the Python scripts print ASCII via `print()` with `errors="replace"` | `grep -nE '^\s*echo' .agents/scripts/git-hooks/pre-commit-maps.sh .agents/scripts/git-hooks/pre-push-maps-verify.sh` → 0 hits |
| 3 | On a write, verify the FILE, not `$?` | `refresh_maps.py` re-reads each regenerated file and compares bytes before it runs `git add`, and reports "refreshed" only from that comparison; `jira_ticket.py attach` reports success only when the response JSON lists the filename, never from HTTP 200 alone | `test_refresh_maps.py` asserts file bytes and the staged list; `test_jira_ticket.py` asserts the filename in the response is what is reported |
| 4 | No `.agents/rules/` path a thin repo does not carry | The new scripts reference `.agents/scripts/` only, and none of them is ported to a thin repo (§7 ruling) | `grep -n '\.agents/rules' <the five files>` → 0 hits |
| 5 | Runs on BOTH machines | Probe order `python3 → python → py` copied from the encoding gate into both delegates; `core.hooksPath=.githooks` is already armed per machine (both); `refresh_maps.py` is stdlib, writes `encoding="utf-8"`, prints ASCII; the PC run is verified on the next PC session and the walkthrough carries its row | `grep -c 'for c in python3 python py' <both delegates>` → 1 each; PC: `python .agents/scripts/refresh_maps.py --verify` exit 0 |
| 6 | Hooks stay repo-local; a port needs the target's OWN key | Every hook file stays in the centre (`.githooks/` + `.agents/scripts/git-hooks/`); nothing is installed into AGY from here. The AGY half is AVCH-78 in its own repo under its own key | `git -C Projects/AGY_AVIATIONCHAT/.claude/worktrees/AVCH-78-graph-scope-hooks log -1 --format=%s` begins `AVCH-78` |

## Declared Change Set

⚠️ AUDIT FINDING F3 (2026-08-22): the first draft carried eight multi-path bullets; `declared_change_set.py`
takes ONE path per bullet and parked all eight in `incomplete` (17 files undeclared). Rewritten; `parse`
now reports 0 incomplete.

- NEW `_artifacts/_main/2026-08-22_graph-to-projects/implementation_plan.md` — this file → plan
- NEW `_artifacts/_main/2026-08-22_graph-to-projects/task.yaml` — lane manifest, riders SCC-289/290/291 → plan
- NEW `_artifacts/_main/2026-08-22_graph-to-projects/tickets/SCC-288.md` — the parent's fast-read outline (C3 dogfood; `done` re-renders from it) → C
- NEW `_artifacts/_main/2026-08-22_graph-to-projects/tickets/SCC-289.md` → C
- NEW `_artifacts/_main/2026-08-22_graph-to-projects/tickets/SCC-290.md` → C
- NEW `_artifacts/_main/2026-08-22_graph-to-projects/tickets/SCC-291.md` → C
- NEW `_artifacts/_main/2026-08-22_graph-to-projects/walkthrough.md` — evidence, port table, deferred rows → close
- EDIT `_artifacts/_main/INDEX.md` — the session row → plan
- EDIT `.mcp.json` — drop `code-review-graph` → A1
- EDIT `.claude/mcp.json` — drop `code-review-graph` → A1
- EDIT `.antigravity/mcp.json` — drop `code-review-graph` → A1
- DELETE `.code-review-graphignore` → A2
- EDIT `docs/_scc_sops_prds/file_folder_structure+maintaining.md` — line 87 names the deleted file → A2
- EDIT `.agents/scripts/tests/test_sops_prds_folder.py` — docstring line 9 names the deleted file → A2
- EDIT `AGENTS.md` — lines 281-282 → A3
- EDIT `docs/code-review-graph.md` — projects-only scope → A4
- EDIT `docs/repo-map.md` — CURATED paragraph at 39-42 describes the lobby index (rewritten); AUTO block regenerated by the hook → A4, B4
- EDIT `.agents/scripts/risk_seam.py` — `--repo` → A5
- EDIT `.agents/scripts/tests/test_risk_seam.py` — cwd ≠ repo case → A5
- EDIT `.agents/commands/cicd-code-review.md` — `--repo "$WORKTREE"` → A6
- EDIT `.agents/commands/cicd-self-audit.md` — `--repo "$WORKTREE"` → A6
- EDIT `.agents/commands/smh-code-review.md` — `--repo "$REPO"`, dead passage trimmed → A6
- EDIT `.agents/commands/smh-self-audit.md` — `--repo "$REPO"` → A6
- EDIT `.agents/scripts/tests/test_command_surfaces.py` — NEW cases: MCP parity set, `--repo` on every seam call, `jira_ticket.py` named by both doors → A1, A6, C3
- EDIT `.agents/commands/sentry-security-team-avch.md` — `--repo` → A8
- EDIT `.agents/workflows/sentry-security-team-avch.md` — `--repo` → A8
- EDIT `.agents/scripts/generate_doc_graph.py` — repeatable `--root`, `--lobby`, relative ids → B1
- NEW `.agents/scripts/tests/test_doc_graph.py` → B1
- EDIT `docs/doc-graph.md` — regenerated, two roots, CURATED block rewritten → B3, A10
- EDIT `docs/doc-graph.json` — regenerated, relative root → B3
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — real dangling refs fixed; §Maps refresh hook; §code review seam; §Jira fast-read → B2, B12, A9, C4
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` → A9, B12, C4
- NEW `.agents/scripts/refresh_maps.py` → B4, B5
- NEW `.agents/scripts/tests/test_refresh_maps.py` → B4, B5
- NEW `.agents/scripts/git-hooks/pre-commit-maps.sh` → B6
- EDIT `.githooks/pre-commit` — maps delegate first, then encoding → B6
- EDIT `.agents/scripts/git-hooks/install-encoding-hook.ps1` — refuse to overwrite a dispatcher that chains more than the encoding gate (F2) → B6
- NEW `.agents/scripts/git-hooks/pre-push-maps-verify.sh` → B7
- EDIT `.githooks/pre-push` — verify delegate before the backstop → B7
- EDIT `.agents/scripts/tests/test_hooks_armed.py` — new delegates in the seeded/armed set → B6, B7
- EDIT `.agents/scripts/tests/test_git_hooks.py` — dispatcher order → B6, B7
- EDIT `.agents/scripts/tests/test_install_git_hooks.py` — the installer's refuse case (F2) → B6
- EDIT `.agents/scripts/INDEX.md` — rows for `refresh_maps.py` and `jira_ticket.py` (F4) → B4, C1
- EDIT `.agents/scripts/check_maps.py` — check 10, skip where no doc graph (F1) → B8
- EDIT `.agents/scripts/tests/test_check_maps.py` — check 10 cases incl. the project skip → B8
- EDIT `.agents/commands/smh-update-maps-indexes.md` — Step 1 + Step 6 → B9
- EDIT `_artifacts/_memory/sop-doc-currency-gate.md` — SOP path → B11
- EDIT `_artifacts/_main/active-context.md` — SOP path, line 9 → B11
- NEW `.agents/scripts/jira_ticket.py` → C1
- NEW `.agents/scripts/tests/test_jira_ticket.py` → C1
- EDIT `.agents/rules/jira.md` — §The ONE test (313), §Minting them (333), new §The description is the fast read → C2
- EDIT `.agents/commands/smh-plan-task.md` — Steps 1, 2, 3.5 → C3
- EDIT `.agents/commands/smh-close-task-merge-tree.md` — `--after-merge` → C3
- EDIT `docs/_scc_sops_prds/jira_integration_guide.md` — §Fast-read tickets → C4
- EDIT `docs/_scc_sops_prds/jira_manual.md` — step 5 → C4

Generated launcher skills under `.agents/skills/*/SKILL.md` and `.agents/.sync-manifest.json` are
regenerated by `/smh-sync-agents` at the end of the lane; they are listed in the walkthrough's diff, not
here. A7 (`.agents/skills/INDEX.md`, `workspace-structure/SKILL.md`) is verify-only and has no bullet
until the build finds wording to change.

## 8. Gates at the tip (all bare, exit codes read, per `piping-a-gate-hides-its-exit-code`)

```bash
python3 .agents/scripts/tests/run_all.py            # every test incl. the 4 new files   (PC: `python` throughout this block)
python3 .agents/scripts/check_maps.py --all          # checks 1–10; 10 is new
python3 .agents/scripts/workflow_lint.py
python3 .agents/scripts/refresh_maps.py --verify     # the hook's own view of the tree
git -C <tree> commit …                               # the pre-commit fires on every B-onward commit; the walkthrough quotes one
```

Then `/smh-code-review` at the tip → **[STOP]** → `/smh-close-task-merge-tree --expect-key SCC-288`,
whose `--after-merge` uses C1's `done` + `attach` on SCC-288/289/290/291 — the first tickets closed in
the new shape.

## 9. Risks and the answer to each

| Risk | Answer |
|---|---|
| The pre-commit hook regenerates from the WORKING tree, not the index; an unstaged `.agents/` edit leaks into the staged map | Accepted and stated in the hook's header: the post-commit recorder and `--verify` at push catch it; the alternative (regenerate from a temp index checkout) costs seconds per commit |
| A PR merge on GitHub runs no local hook → main's AUTO block can be stale after a merge | B7: the next push from any lane refuses until regenerated; B8: check 10 fails `run_all`/the ceremony; the merge-time staleness window is the same one repo-map already has |
| Two lanes both regenerate `doc-graph.json` → merge conflicts in a 200 KB generated file | Resolve by regenerating, never by hand: `refresh_maps.py --staged` after `git merge` with the file staged; documented in B12 and the hook's refusal text |
| `--no-verify` skips both pre-commit and pre-push | The ceremony + check 10 + `run_all` at close-out; nothing on main bypasses all three |
| The reverse door check fires on a door the operator retires | Retiring = deleting the command file; a deleted door cannot be un-named. A door renamed without an SOP edit is exactly the drift this exists to catch |
| C1's token step is skipped and agents keep pasting plans into descriptions | `attach` exits 5 with the instruction; `describe` still works (it goes through acli) — the fast-read shape lands even before the token exists |
| PC Credential Manager read is untested on this machine | Decision 7: `$JIRA_API_TOKEN` is first in the order and works everywhere; the PC path is verified on the PC and noted in the walkthrough |
| **Landing order — SCC-285** (`chore/SCC-285-agenttool-directive-quote`, a team's lane) edits `cicd-code-review.md` @186-213 and `smh-code-review.md` @157-184; A6 edits @118-121 / @88-112 | Disjoint hunks. Whichever lands second re-merges and re-runs `test_command_surfaces.py`. Both lanes also touch `.agents/.sync-manifest.json` and `.agents/scripts/INDEX.md`: the manifest is regenerated by `/smh-sync-agents` after the merge, never hand-merged; INDEX rows are hand-merged |
| **Landing order — SCC-280** (`claude/teaching-edition`, uncommitted) edits `jira.md` @14-25 (frontmatter triggers) and `scripts/INDEX.md` @28/70/75; C2 edits `jira.md` @308-345 and F4 adds INDEX rows | Disjoint; re-merge. No sibling touches the hooks, `check_maps.py`, `generate_doc_graph.py`, `risk_seam.py` or the SOP |

## 10. Out of scope (said here so nobody infers it later)

- `code-review-graph embed` (local model) and MCP tool trimming (25 → 8) — AVCH side, after a consumer exists.
- A workflow DAG or a queryable markdown graph — the SOP's 45 diagrams are that map, and B makes them link-true.
- `jira_feed.py mint` adopting the fast-read shape (C5 flags it).
- AVCH-77 (TIA off GitNexus) — unchanged.

## Self-Audit (2026-08-22)

**Level: LEDGER+BLAST** (the Declared Change Set touches rules, gates and hooks, scripts others import,
command surfaces on four platforms, one `DELETE`, and files that exist in AGY). **Mode: PRE-WORK.**
Repo: `SCC-288-graph-to-projects` | Branch: `chore/SCC-288-graph-to-projects` @ `a634c35` (= `origin/main`).
Plan: `_artifacts/_main/2026-08-22_graph-to-projects/implementation_plan.md` · ticket SCC-288 (riders
SCC-289 / SCC-290 / SCC-291).

lens:        1 Repo Reality + Scope Ledger
checks_run:
- every `EDIT`/`DELETE` path in the Declared Change Set exists on disk; every `NEW` path is absent (this lane's own untracked artifacts excepted) — 0 mismatches after the rewrite
- `python3 .agents/scripts/declared_change_set.py parse <plan>` → first draft: 26 entries, **8 bullets in `incomplete`** (F3); after the rewrite: 55 entries, 0 incomplete
- both-machine commands: stdlib only, no venv; §8 gate block carried `python3` with no PC spelling (F7)
- lane fit: no `backend/ frontend/ firebase/ functions/ mobile/ .github/` path in the set → `/smh-close-task-merge-tree` is the right door
- Scope Ledger precondition: SCC-288 carries 7 Plan rows, each naming a file, script or gate as its observable ✓
- Scope Ledger table (below): every `NEW` artefact has a requiring row; caller counts printed
- plan step numbers referenced (A1–A10, B1–B12, C0–C5) all exist in the plan ✓
- the B5 assumption "the SOP already names every house door": 46 `.agents/commands/*.md` minus `INDEX`, `*-AP`, the vendor set → `grep -- "/<name>\b" workflows_testing_SOP.md` → **0 missing** ✓ (so the reverse check is armed at zero, as the plan says)
- anchors the plan quotes, re-read: `AGENTS.md:281-282` ("The lobby index maps the **master toolkit**") ✓ · `smh-code-review.md:91-93` ("`risk_seam.py` asks the local code graph…") ✓ · `risk_seam.py:84-89, 290-297` ✓ · `active-context.md:9` (`_my_resources/_quick_reference/sudo_workflows_testing.md`) ✓ · `jira.md:313` ("the ticket description **is** the spec") and `:333` ("### Minting them") ✓ · `check_maps.py:192 default_regen_ignore`, `:251 declared_mode`, `grm.build_auto_body` ✓
- tests-must-gate-for-real: every new test names the case that is RED before the change (A5, B1, B4, B5, B8, C1); the mutant table is the review's sweep, not the plan's
read:        `.agents/scripts/declared_change_set.py` (parse output) · `AGENTS.md:281-282` · `.agents/commands/smh-code-review.md:88-112` · `.agents/commands/cicd-code-review.md:118-121` · `.agents/commands/cicd-self-audit.md:166` · `.agents/commands/smh-self-audit.md:179` · `.agents/scripts/risk_seam.py:84-89,290-297` · `.agents/scripts/check_maps.py:192-260,552-575` · `.agents/scripts/generate_doc_graph.py:121-148,280-300,400-401` · `.agents/scripts/generate_repo_map.py:1-40,188-203` · `_artifacts/_main/active-context.md:9` · `_artifacts/_memory/sop-doc-currency-gate.md` · `.agents/rules/jira.md:300-345,492-505` · `docs/_scc_sops_prds/workflows_testing_SOP.md` (door grep; lines 1467-1506, 3712) · `.agents/commands/` (66 files, names) · `.agents/scripts/tests/` (56 files, names)
verdict:     findings below (F3, F4, F5, F6, F7 — all baked into the plan)

**Scope Ledger — artefacts this plan CREATES × the SCC-288 row that requires them**

| NEW artefact | plan step | SCC-288 Plan row | callers (grep-countable) |
|---|---|---|---|
| `implementation_plan.md`, `task.yaml`, `walkthrough.md` | plan/close | row 7 "Gates green at the tip" — `task_preflight.py --expect-key` refuses a close-out without the manifest and walkthrough | `task_preflight.py`, `walkthrough_roster.py` (existing callers) |
| `tickets/SCC-288..291.md` | C3 | row 6 (C) | `jira_ticket.py done` (created by this plan) + `/smh-close-task-merge-tree --after-merge` |
| `test_doc_graph.py` | B1 | row 3 (B) | `run_all.py` auto-discovery |
| `refresh_maps.py` | B4 | row 4 (B) | 3, all created or edited by this plan: `pre-commit-maps.sh`, `pre-push-maps-verify.sh`, `check_maps.py` check 10 — falsifiable by a second caller: `/smh-update-maps-indexes` Step 1 (B9) names it as the fourth |
| `test_refresh_maps.py` | B4/B5 | row 4 (B) | `run_all.py` |
| `pre-commit-maps.sh`, `pre-push-maps-verify.sh` | B6/B7 | row 4 (B) | `.githooks/pre-commit`, `.githooks/pre-push` |
| `jira_ticket.py` | C1 | row 6 (C) | `smh-plan-task.md`, `smh-close-task-merge-tree.md` (this plan) + this lane's own close-out (live) |
| `test_jira_ticket.py` | C1 | row 6 (C) | `run_all.py` |

No empty acceptance cell → no ledger finding.

lens:        2 Parity + Blast
checks_run:
- command files (8 edited): bodies are read from `.agents/commands/` at run time; the four platform launchers carry no steps and are regenerated by `/smh-sync-agents` (plan §DCS note) ✓; `commands/INDEX.md` unchanged — no rename ✓
- command names: none renamed ✓
- rule (`jira.md`): `workflow_lint.py:70-96 _RULE_POINTERS` has no `jira` row, so no command is required to cite it; citing commands are unaffected by a body edit ✓
- scripts: `risk_seam.py` callers = the 4 doors (all in the set) + `test_risk_seam.py` ✓ · `generate_doc_graph.py` callers = none in `.githooks/` today (that is the defect B fixes) ✓ · `check_maps.py` callers = `.claude/settings.json` SessionStart (`--depth3-only`, untouched by check 10), `run_all`, the ceremony, `record_map_changes.py` — **and `--all` fans out over projects** → **F1**
- `.agents/scripts/INDEX.md:15` lists `risk_seam.py`; `:68` lists `generate_doc_graph.py` — the two NEW scripts need rows → **F4**
- gates/hooks ship ARMED: dispatchers exec the delegates unconditionally; `hooks_armed.py:81-83` executable-checks every tracked `*.sh` in `git-hooks/` — flagless is the encoding gate's own shape ✓; `install-encoding-hook.ps1:58-66` clobber → **F2**
- path delete (`.code-review-graphignore`): repo-wide grep → live references at `docs/repo-map.md:40` (curated), `docs/code-review-graph.md:15` (A4), `docs/_scc_sops_prds/file_folder_structure+maintaining.md:87`, `test_sops_prds_folder.py:9` (docstring, no assertion) → **F5, F6**; `_artifacts/` history mentions are records, not links
- SOP + usage surface in the same commit: `sop_currency.py` is per-commit — see Observations
- `_artifacts/_memory/` edit: AGENTS.md §7 (`:171-186`) makes the repo path canonical and SCC-270 moved a memory file on its lane under the same clause ✓ (`test_memory_store.py` stays in `run_all`)
- file in >1 repo: §7 Port check present; trigger diffs run (`differ=1` ×3), ruling "not ported" per file, six checks answered with the commands that answer them ✓
- twins: `cicd-code-review`↔`smh-code-review` and `cicd-self-audit`↔`smh-self-audit` both edited ✓; `smh-plan-task`, `smh-close-task-merge-tree`, `smh-update-maps-indexes` have no `cicd-` twin ✓; `-AP` twins abandoned, not ported ✓
- sibling worktrees (after `env -u GITHUB_TOKEN git fetch origin main`): `SCC-280-teaching-edition` and `scc-285-agenttool-directive-quote` — overlaps measured by hunk range → landing-order rows in §9 ✓
- risk seam: `risk_seam.py classify .agents/scripts/risk_seam.py .agents/scripts/generate_doc_graph.py .agents/scripts/check_maps.py` → `"status": "unclassified"` (no graph in the centre — the normal path; informs nothing here)
read:        `.agents/scripts/workflow_lint.py:31-63,70-96` · `.agents/scripts/hooks_armed.py:1-96` · `.agents/scripts/git-hooks/` (listing) · `.agents/scripts/git-hooks/install-encoding-hook.ps1:3-73` · `.agents/scripts/tests/test_hooks_armed.py:40-75,150-250,370-385` · `.agents/scripts/tests/test_install_git_hooks.py:44-50` · `.agents/scripts/tests/test_command_surfaces.py:1830` · `.agents/scripts/tests/test_sops_prds_folder.py:9` · `.agents/scripts/INDEX.md:3,15,53,66-68` · `.agents/scripts/check_maps.py:220-248,552-575` · `docs/repo-map.md:36-42` · `docs/_scc_sops_prds/file_folder_structure+maintaining.md:85-89` · `.agents/skills/INDEX.md:24` · `.agents/skills/workspace-structure/SKILL.md:28` · `.agents/skills/code-review-graph/SKILL.md` (grep) · `AGENTS.md:171-186` · `git worktree list` + per-tree `diff -U0 origin/main...HEAD` / `status --short`
verdict:     findings below (F1, F2, F4, F5, F6, F8 — all baked into the plan)

lens:        3 Pre-Mortem
checks_run:
- F1 attached: the operator runs `/smh-update-maps-indexes` on the PC next week; `check_maps.py --all` prints `FAIL check 10` for AviationChat; an agent "fixes" it by generating a doc graph inside AGY — a 200 KB file nothing reads — and the ceremony is now slower and wrong on every project. Closed by the skip-when-absent rule in B8.
- F2 attached: a fresh PC clone follows the new-machine guide's installer line; the tracked dispatcher is overwritten with the encoding-only body; the maps delegate is gone and `git status` shows `M .githooks/pre-commit`, which the operator reads as "the installer touched its own file". Maps go stale on the PC until the first push is refused by B7's verify — loud, but only at push. Closed by the installer's refuse rule in B6.
- F3 attached: `/smh-code-review` Step 2's drift check reconciles the diff against the parsed set; 17 undeclared files read as drift, the reviewer spends its budget on declared-vs-built noise and the real findings sort below it. Closed by the rewrite (0 incomplete).
- no narrative originated by this lens; nothing unattached to report
read:        —
verdict:     attached to F1, F2, F3

### Findings

| # | anchor | literal text read | consequence | severity |
|---|---|---|---|---|
| F1 | `.agents/scripts/check_maps.py:220` + `:566` | `def fan_out_targets(home_root):` … `if not db.exists(): return []` | check 10 as first drafted runs on every fanned-out project, none of which carries `docs/doc-graph.md` → `check_maps --all` (the ceremony, `run_all`) FAILS on every project; breaks SCC-288 row 7 | **HIGH** → fixed inline in B8 (skip where the file is absent) |
| F2 | `.agents/scripts/git-hooks/install-encoding-hook.ps1:58-66` + `.githooks/pre-commit:2` | `if ($existing -notmatch $MARKER) { … REFUSED … }` / `# pre-commit-encoding (installed by …)` | the installer treats a dispatcher that *contains* its marker as its own and overwrites it with the three-line body → the maps delegate is silently removed on the PC | **HIGH** → fixed inline in B6 (refuse when ours-but-different) + `test_install_git_hooks.py` case |
| F3 | `_artifacts/_main/2026-08-22_graph-to-projects/implementation_plan.md` (§Declared Change Set, first draft) | `declared_change_set.py parse` → `incomplete: ["- EDIT `.mcp.json`, `.claude/mcp.json`, `.antigravity/mcp.json` …", …×8]` | 17 files the plan meant to declare were undeclared; the review's drift check would list them all | MEDIUM → fixed (one path per bullet; 55 entries, 0 incomplete) |
| F4 | `.agents/scripts/INDEX.md:15` | `\| `risk_seam.py` \| risk classification for a path set, behind the stable seam …` | the INDEX is the scripts' inventory; `refresh_maps.py` and `jira_ticket.py` had no row and no bullet | LOW → DCS bullet added |
| F5 | `docs/repo-map.md:39-40` | `**code-review-graph (the code graph — on-demand, disposable, machine-local).** ONE index, rooted at the repo root, covering everything `git ls-files` tracks minus the exclusions in `.code-review-graphignore`.` | curated text describing the very index Part A removes, and naming the deleted file | LOW → A4 + DCS bullet |
| F6 | `docs/_scc_sops_prds/file_folder_structure+maintaining.md:87` · `.agents/scripts/tests/test_sops_prds_folder.py:9` | `and in `.code-review-graphignore` — its own local law says` / `in DEFAULT_REGEN_IGNORE for the repo-map, and in .code-review-graphignore --` | two references to a deleted file survive the grep A2 promises to zero | LOW → A2 + DCS bullets |
| F8 | `Projects/AGY_AVIATIONCHAT/scripts/check_maps.py` (vendored copy; `differ=1` vs master) | `def check_graph_fresh(root):` present in both; the AGY copy predates the master's check-9 rewrite | the port section listed only `.agents/scripts/` twins and missed the `scripts/` vendoring; `check_maps.py` IS a file in two repos | LOW → §7 row + ruling added (not ported; check 10 is lobby-only) |
| F7 | step 8 | `python3 .agents/scripts/tests/run_all.py            # every test incl. the 4 new files` | the gate block had no PC spelling; the PC has no `python3` | LOW → note added |

### Observations (uncounted)

- A7 is expected to be a no-op: neither skills file claims a lobby index today (grep at audit time); the step is now verify-only.
- `test_command_surfaces.py` carries no MCP-parity or seam-call assertion today (its only graph mention is an ignore set at `:1830`); the plan's A1/A6/C3 cases are NEW assertions inside an existing file.
- `sop_currency.py` runs per **commit**: every commit that touches a command, rule or hook must stage its SOP hunk (or carry `[sop-ok]` with a reason). "SOP staged" in each part therefore means *in that part's usage-surface commits*, not once at the tip.
- The port section answers the six checks with the commands that will answer them; the scripts are `NEW`, so the output exists only at build time — the walkthrough pastes it. Adequate for PRE-WORK; Lens 2 re-runs at `/smh-code-review` Step 0.7.
- C0 (the operator's one-time token step) is the only item in this plan an agent cannot do. Until it is done, `describe` works (it rides acli) and `attach` exits 5 with the instruction — so the fast-read shape lands either way.

### Sibling landing-order dependencies

- **SCC-285** (`chore/SCC-285-agenttool-directive-quote`, a team's lane; not ours to touch): `cicd-code-review.md` @186-213 and `smh-code-review.md` @157-184 vs A6 @118-121 / @88-112 — **disjoint**. Whichever lands second re-merges and re-runs `test_command_surfaces.py`. Both also touch `.agents/.sync-manifest.json` (regenerate with the sync after merge, never hand-merge) and `.agents/scripts/INDEX.md` (hand-merge rows).
- **SCC-280** (`claude/teaching-edition`, uncommitted changes): `jira.md` @14-25 (frontmatter triggers) vs C2 @308-345 — disjoint; `scripts/INDEX.md` @28/70/75 vs F4's rows — disjoint; re-merge.
- No sibling touches `.githooks/`, `check_maps.py`, `generate_doc_graph.py`, `risk_seam.py` or the SOP.

Audit verdict: GO
