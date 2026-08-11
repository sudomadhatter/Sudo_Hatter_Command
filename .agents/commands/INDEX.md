---
description: Commands INDEX — catalog of the invocable command set (not a slash command itself)
platforms: []
---

# Commands INDEX — when to use which

**⭐ Naming law (SCC-63).** The prefix declares the family, and it is load-bearing — it decides what the
command may touch. **`cicd-*`** = the BMAD-paired story/epic dev loop and its logistics; binds
`smh-target-resolution.md`, so it operates on exactly ONE project and **never the lobby**. **`smh-*`** =
workflows run ON the command centre and everyday operator tasks; allowed to act on the repo you are
standing in. **`sentry-*`** = the Sentry incident system. Hyphens only, never underscores; an autopilot
twin appends `-AP`; vendor BMAD bridges keep their upstream names and take no prefix; skills take no
prefix at all. ⛔ **The `sudo-` prefix is RETIRED — any `/sudo-` reference anywhere in this system is
stale by definition**, which is exactly why it was retired outright instead of aliased. New command →
pick `cicd-` or `smh-` by the target rule above; `workflow_lint.py --toolkit-only` rejects anything else.

Router for `.agents/commands/`. **Scan to dispatch.** Each command is invoked by natural-language intent
or through the platform surface named below and carries its own frontmatter `description:`; this groups
them by purpose. `.agents/commands/` is the canonical workflow body even when a platform enters through a
thin native skill launcher. `/smh-sync-agents` publishes it to Claude (`.claude/commands/` and skills),
opencode (`.opencode/commands/` + global `~/.config/opencode/commands`), and Antigravity/Gemini (global
`~/.gemini/antigravity/global_workflows` — it calls our commands "workflows"). Codex discovers
`.agents/skills/` natively; its deprecated custom-prompt fallback is namespaced `/prompts:<name>`, never
the top-level `/<name>` used by the other command menus.

**Platform reach.** A command may add `platforms: [claude, opencode, antigravity, codex]` to its
frontmatter to limit where it syncs. **Absent = universal** (all four). Tagged today: `cicd-autopilot-claude`,
`cicd-mobile-error-team` → `[claude]`; `cicd-autopilot-opencode` → `[opencode]`; the `_AP` trio → `[claude, opencode]`;
`sentry-security-team-avch` → `[opencode, antigravity, codex]` (deliberately NOT in the Claude menu);
`smh-adviser-board` → `[claude, opencode, codex]` (25k body exceeds Antigravity's 12k workflow limit — AG gets the hand-authored thin launcher `.agents/workflows/smh-adviser-board.md`, prune-protected in the sync's `$excluded` list).
**Robot-lane rule (2026-07-14):** `*_AP` commands vendor ONLY into project tool dirs (where the autopilot
engines read them) — the sync skips them for the lobby menus and the global caches.
**Antigravity actually honors that reach as of 2026-08-09 (SCC-56).** The `.agents/workflows/` mirror used
to filter by FILENAME first (`sudo-*`, `1_*`, `smh-new-project`, `smh-slash-command-updating`) and only then read
`platforms:` — so four commands that claim Antigravity never reached it: `smh-close-task-merge-tree`,
`smh-sync-agents`, `smh-review`, and `cicd-clean-code-audit`, which names `antigravity` outright.
`platforms:` is now the only gate. `.agents/workflows/` is **generated** — edit the command, never a copy.

| Group | Commands | Reach for it when… |
|---|---|---|
| **BMAD agent personas** | `analyst` (Mary) · `architect` (Winston) · `dev` (Amelia) · `pm` (John) · `qa`/`tea` (Murat) · `sm` · `tech-writer` (Paige) · `ux-designer` (Sally) | you want a specific BMAD role to drive (planning, design, story dev, QA). |
| **BMAD routing** | `bmad-help` · `bmad-master` | unsure which agent/workflow — ask for a recommendation. |
| **BMAD test architecture** (commands) | `testarch-atdd` · `testarch-automate` · `testarch-ci` · `testarch-framework` · `testarch-nfr` · `testarch-test-design` · `testarch-test-review` · `testarch-trace` | thin slash-command wrappers that invoke the matching `bmad-testarch-*` skill (ATDD red-phase, automate coverage, CI pipeline, framework init, NFR audit, test design, test review, traceability matrix). |
| **Autopilot (Claude-only engine)** | `cicd-autopilot-claude` · `cicd-autopilot-deepseek4` · `cicd-dev-story-tests-AP` · `cicd-self-audit-AP` · `cicd-code-review-AP` | run the autonomous Dev/QA loop on one story (`/cicd-autopilot-claude <story>`). `_AP` = headless robot-lane variants; never invoked by a human, live only inside project tool dirs. |
| **Autopilot (opencode engine)** | `cicd-autopilot-opencode` | the opencode-native sibling of `/cicd-autopilot-claude` — a real, built pipeline (`Projects/<name>/scripts/autopilot-dev-story-opencode.ps1`, 843 lines — the engine is **project-local**, so the path never resolves from the lobby): same 4 stages via the same `_AP` commands, same artifact contract, session continuity, retries, cost caps, independent test gate and story→review flip. Drives `opencode run` instead of `claude -p` (Dev on the selected default model, QA pinned to GLM 5.2 at max). Only gap vs the Claude engine: no per-story concurrency lockfile. |
| **Sudo dev flow** (TEA-gated, human lane) | `cicd-boot-sprint-memory` · `cicd-create-epic-sprint` · `cicd-write-story-tests` · `cicd-bdd-tests` · `cicd-dev-story-tests` · `cicd-self-audit` · `cicd-code-review` · `cicd-update-sprint-memory` | two phases — **epic kickoff** (`cicd-create-epic-sprint`: create epic + stories → sprint → interactive P0–P3 risk-score, once per epic) then the **per-story loop** with testing baked in: boot/pick-up → write red tests (Vision Lock inside) → plan+self-audit+implement+automate → review+gate → close-out save. Run in that order; `cicd-self-audit` auto-runs inside `cicd-dev-story-tests`. The gate (suite + TEA trace/nfr/test-review → PASS/CONCERNS/FAIL/WAIVED) lives inside `cicd-code-review`. |
| **Parallel planning** (once an epic's stories are written) | `cicd-parallel-check` | `/cicd-parallel-check <EPIC-KEY>` — the answer to *"which of these can I run side by side?"*, as an explicitly-stamped **snapshot** over ONE BMAD epic's children. Reads every child's story file (or plan, or branch diff — in that authority order), extracts what each will actually **modify** as opposed to merely mention, computes the largest set with no source-file overlap, and rewrites `parallel-ok` across the whole epic — adding it to the 🟢 set **and stripping it from everyone else**, which is what makes it self-correcting where ①'s per-story writer rotted. `parallel-ok` is a property of a **set at a moment**, so ① Step 1.6 can never rule it (it mints 19.1's ticket before 19.2's file exists) — SCC-56 moved the writer here, and ⛔ it must never move back. **No story file, no verdict** — the answer is `/cicd-write-story-tests <id>`, never a guess. Fails toward 🔒. Refuses a **grouping** epic by name. Target is derived from the key via each repo's `.agents/jira.conf`, so the lobby qualifies the day it carries BMAD stories. `parallel_check.py check --parent <KEY>` re-asks whether the stamp still matches the epic's children — a set that has changed reads *"re-run me"*, never as a verdict. **States, never starts;** writes labels and one comment, and transitions nothing. |
| **Epic merge + code hygiene** | `cicd-merge-epic-workingtrees` · `cicd-clean-code-audit` | `cicd-merge-epic-workingtrees` lands several finished story worktrees from one epic in a single reviewed pass (per-lane verdict re-point, overlap detection, board merge) instead of N separate close-outs. `cicd-clean-code-audit` is the standalone dead-code / duplication / drift sweep — the same lens `cicd-code-review` folds in per story, run across a whole surface. |
| **Sudo quick-fix flow** (fast track) | `cicd-quick-dev` | fast-track dev flow on the `bmad-quick-dev` engine (one-shot route) — clarify intent and FIX acceptance criteria, implement, then a **mandatory review gate** (an independent adversarial reviewer always; on code, an acceptance audit + the clean-code machine floor + scoped tests; on docs, link/anchor + SOP currency). Skips the *pipeline* — no ATDD red phase, no full suite, no three-reviewer panel — **not** the review. Ejects to the full ①②③ lane on a protected surface or when the router says the work needs planning. **Stops for human review; it never closes out.** |
| **Task dev lane** (the non-BMAD dev cycle) | `smh-self-audit` · `smh-quick-dev` · `smh-code-review` · `smh-clean-code-audit` | the `smh-*` counterparts of the `cicd-*` dev loop, for command-centre work that is **not** part of a BMAD sprint — no story file, no sprint board, no epic branch, no status flip. Runs on `chore/<KEY>-<slug>` off `main` and closes through `smh-close-task-merge-tree`. **Every one of them acts on the repo you are standing in**, so the lobby is a valid subject; none of them binds `smh-target-resolution.md`, which is the whole reason the `cicd-*` twins cannot do this work. Order: `smh-quick-dev` (plan → `smh-self-audit` → the literal `approved` → write the assertion RED → make it GREEN) → `smh-code-review` (clean-room adversarial hunt → acceptance audit → the command-centre gate → `smh-clean-code-audit` at Step 3.5) → STOP → the operator's `smh-close-task-merge-tree`. **The floor is a different floor:** there is no venv, no `ruff`, no `tsc` in the command centre, so `smh-clean-code-audit` gates on `run_all.py` + `workflow_lint.py --toolkit-only` + `sop_currency.py` + `py_compile` + link/anchor + door parity, and judges against the SOP's own conventions (naming law, one-door law, gates ship armed, both machines). `gate_receipt.py` **cannot run here** — it resolves a BMAD board — so evidence is pasted output plus a recorded sha. Deliberate cross-family duplicates of `cicd-self-audit` / `cicd-quick-dev` / `cicd-code-review` / `cicd-clean-code-audit`: fix a shared idea in one and diff the twin. |
| **Shipping** (the e2e gate) | `cicd-e2e` · `cicd-push-e2e` | `cicd-e2e` runs the hermetic end-to-end suite (emulators + seeded users) → GREEN/RED verdict, solo or as the gate; `cicd-push-e2e` is the ONE shipping command — the epic branch's merge to `main` (full gate: backend suite + frontend build + `cicd-e2e` GREEN + Daniel's sign-off, `--no-ff` merge, epic branch deleted after), then CI/CD + Cloud Run deploy + live verify + ledger. |
| **Task close-out** (the non-BMAD lane) | `smh-close-task-merge-tree` · `smh-merge-multiple-workingtrees` | **Which one:** ONE finished lane → `smh-close-task-merge-tree`. **Several at once** → `smh-merge-multiple-workingtrees`, which does the set-level work a single close-out structurally cannot: derives the landing order from measured overlap, classifies every shared file (ledger → keep both rows · rewrite-vs-edit → re-author · modify-delete → rule it and prove the survivor exists first · gate-or-script → order matters), forces lanes that change commit or push machinery to the END, honours cross-repo dependencies, and finishes with a **combined gate on `main`** — the only run that sees the whole set together, and the one that caught SCC-96, a defect every individual lane was green against. It still **stops before every merge**: a Task lane lands on `main` directly, so N lanes are N production merges and one invocation never authorises two (SCC-71). It automates the analysis, the reconcile, the gate and the prune — never the authorisation. Sibling of `cicd-merge-epic-workingtrees`, which may take one sign-off for its whole set precisely because it lands on an epic branch rather than production. — close **Task** work — a `chore/<JIRA-KEY>-<slug>` branch with no epic, no story file and often no board, which is exactly why `/cicd-update-sprint-memory` cannot close it. Invoke `/smh-close-task-merge-tree` on the direct command surfaces; in Codex select it through `/skills` or type `$smh-close-task-merge-tree` (Codex does not support repo-defined top-level slash commands). `task_preflight.py` checks branch shape + key, clean/`0 0`, `origin/main` absorbed, the walkthrough, and **the LANE**; then the lane's gate runs, `--no-ff` merge to `main`, one Dev Record + ticket → Done, branch pruned. Invoking it IS the merge sign-off. **The E2E question is answered mechanically, not asserted:** the repo either has no deployable surface at all (the command centre — no E2E suite exists to skip) or the diff misses every deployable dir; touch one and it refuses outright and hands the work to `/cicd-push-e2e`, with no override flag. Deliberately `smh-*` and not `cicd-*` — that family is barred from the lobby by `smh-target-resolution.md`, and toolkit tasks live in the lobby. |
| **Live debugging** | `cicd-live-testing-team` | boots backend+frontend, watches backend logs while the human flies the app, coaches the DevTools check, and files researched bug docs that feed the story loop. Writes no code. |
| **Document review** | `smh-review` | invokes the `md-feedback` MCP server to view and review changes the user made to a document. |
| **Session / project ops** | `smh-update-maps-indexes` · `smh-memory-audit` · `cicd-park` · `cicd-resume` · `cicd-close-workingtree` · `cicd-prune-context` | `smh-update-maps-indexes` refreshes the repo map + every INDEX + context hygiene + open-tasks list. `smh-memory-audit` owns the shared memory store `_artifacts/_memory/` — every platform loads its index before doing any work, so it is the one doc whose upkeep everyone pays for and nobody owned. It ground-truths each candidate memory against the live repo (does the rule/script/flag it names still exist? is the thing it calls CLOSED actually gone?), then proposes retire / merge / compress / **relocate** with bytes freed and applies **only what is approved per item**. Triggered by `tests/test_memory_store.py` at 90% of the **25 KB** index cap — below the cap, so the trigger prevents the red rather than being it (SCC-68 moved this out of `smh-update-maps-indexes` Step 3.9, where it never ran). **Relocation is the fourth disposition and the first lever (SCC-73):** the store is two-tier, so a fact true only inside one project moves to `Projects/<name>/_artifacts/_memory/` — two repos, two commits, two ticket keys — while cross-project law stays in the lobby. SCC-69 measured compaction spent (145 memories, 633 bytes freed), which is why moving beats squeezing. `cicd-park` / `cicd-resume` are the desktop⇄laptop⇄mobile handoff pair — **park** before closing a lid (commit explicit paths + merge the epic branch inside each story worktree + push every `claude/*` branch, the epic branch, and both repos + write one live resume card), **resume** after opening one (fetch, find the live epic + story branches via `git ls-remote` because `git worktree list` shows nothing on a fresh machine, re-create the worktree off the epic branch or check the branch out, hand off to the boot). `cicd-close-workingtree` safely verifies a completed story has landed on its epic branch, removes its local worktree, and prunes both local and remote GitHub `claude/*` branches. `cicd-prune-context` enforces the active-context ≤20 KB budget + the pitfall sweeps (invoked by `cicd-update-sprint-memory` Step 5; also standalone whenever boot feels heavy). |
| **Adviser board** (ideation) | `smh-adviser-board` | convene the open-table board of historical minds (5 challenge teams + Real-World marketing squad) for an operator-chaired Brainstorm → Plan → Market session; closes with a self-contained brief in `_my_resources/board_sessions/`, ready to seed whatever build workflow the operator calls next. Deep roster reference: `docs/_scc_sops_prds/smh-adviser-board-REFERENCE.md`. |
| **Security / error team** | `cicd-mobile-error-team` · `sentry-security-team-avch` | **`cicd-mobile-error-team` is the LIVE responder** — the command an incident page tells you to run (`/cicd-mobile-error-team AVIATIONCHAT-42`). It picks up where the machine lane stops: re-verifies the auto-triage report, weighs rollback vs fix-forward with time-to-recovery for both, writes a minimal fix + regression test on `claude/incident-<id>`, gates it on real CI via a draft PR to `main` (the documented hotfix carve-out), and stops twice for Daniel. Never merges on its own initiative. Claude-only (mobile-first). `sentry-security-team-avch` is the separate quarterly **DRILL** harness for the same runbook — not the live lane, not in the Claude menu. |
| **System builder** (lobby) | `smh-new-project` · `smh-sync-agents` · `smh-slash-command-updating` | scaffold a workspace, push the master toolkit into a target, or refresh global command caches. |

**⭐ Renamed — the whole surface (2026-08-09, SCC-63): the `sudo-` prefix is RETIRED.** Every command
now declares its family in its name: **`cicd-*`** = the BMAD-paired story/epic dev loop and its
logistics · **`smh-*`** = workflows run ON the command centre and everyday operator tasks ·
**`sentry-*`** = the Sentry incident system. Hyphens only (`autopilot_claude` → `cicd-autopilot-claude`,
`slash_command_updating` → `smh-slash-command-updating`); an autopilot twin's `_AP` suffix became
`-AP`. Vendor BMAD bridges (`dev`, `pm`, `qa`, `testarch-*`, …) keep their upstream names and take no
prefix; so do knowledge skills. **Any surviving `/sudo-` reference is therefore stale by definition** —
that is the point of retiring the prefix outright rather than aliasing it. `/webm-alpha-video` was
retired as a command in the same pass and is now a skill only. Names below this line are HISTORY.

**Renamed / retired (2026-07-14):** `sudo-incident-response` → `sentry-security-team-avch` ·
`1_update-maps` → `smh-update-maps-indexes` · `1_live_testing_team` → `cicd-live-testing-team` (revamped) ·
`1_push-to-main-and-deploy` → `cicd-push-e2e` (now carries the mandatory e2e gate) · deleted:
`1_run-all-tests-back_front` (③ runs suites directly), `1_run-restart-dev-env` (absorbed into
`cicd-live-testing-team`), `1_check-for-tech-stack-updates`, `1_clean-test-scripts`,
`1_firebase-user-cleanup`, `1_make-workflow-from-chat` (all recoverable from git history).

**Renamed (2026-08-02) — then RETIRED, see below:** `update-personal-sprint-map` →
`sudo-update-scrum-board` (board doc renamed `sprint-dependency-map.md` → `sprint_scrum_board_map.md`;
five-zone layout, team-lane plan gated on grounded stories). **History only — neither name is live.**

**Retired (2026-08-07):** `merge_main_debug` — died with the `main_debug` integration branch
(branch-model migration, `git-policy.md`); the epic→`main` merge is `/cicd-push-e2e`, and stories land
on their epic branch via `/cicd-update-sprint-memory` Step 7.

**Retired (2026-08-07):** `sudo-update-scrum-board` — deleted with the local scrum board (SCC-13,
commit `8144518`). **The Jira board is the human-facing "what runs next"**, and `To Do Next` is the
queue; there is no local board doc to rebuild. This row stayed on the live list until **2026-08-09**
and sent the operator looking for a command that no longer existed — which is the whole cost of a
stale INDEX. Recover the old body if a step of it is ever needed again (its Step 2.5 is the ancestor
of `/cicd-parallel-check`):

```bash
git show 8144518^:.agents/commands/sudo-update-scrum-board.md
```

**Retired (2026-08-07):** `autopilot_mobile` — deleted (operator ruling, centralization epic): mobile
drives the desktop via Remote Control now; the desktop engines are the only autopilots. The manifest
ghost-purge retires every platform cache copy on the next `/smh-sync-agents`.

**Adding a command:** create `<name>.md` with a `description:` frontmatter stating when it fires (add an
optional `platforms:` line only if it's not universal), add it to the right group above, and re-run
`/smh-sync-agents` to propagate to all platforms + the global caches.
