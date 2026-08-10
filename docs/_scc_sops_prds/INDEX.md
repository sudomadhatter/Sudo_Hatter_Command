# SOPs & PRDs — Index

**Every procedural document in this system lives here.** These are the pages that tell the operator
what to do and what to type — as opposed to `.agents/rules/` and `.agents/commands/`, which describe
the system to an *agent*. Consolidated by SCC-74 (2026-08-10) from `_my_resources/_quick_reference/`
and `_my_resources/diagrams_guides/`.

## Why this folder exists

The docs below rotted for years, and not from neglect. They lived in `_my_resources/`, which is named
in `SCAN_IGNORES` (`check_maps.py`), in `DEFAULT_REGEN_IGNORE` for the repo-map, and in the GitNexus
ignore list — its own local law says *"excluded from repo-map regen + linter scans … do not fix
that."* **Every drift-checker in this system was forbidden to look at them.** The index they lived
under listed 2 files that did not exist and omitted 4 that did, and nothing could notice.

Operator ruling 2026-08-10 makes the division permanent:

| Folder | What it is | Staleness |
|---|---|---|
| `_my_resources/` | Daniel's human thinking + brainstorming space. **Agents ignore it unless he links a specific document.** | fine by design |
| `docs/` | the maintained surface | **must never go stale** |

A procedural doc sitting in the first is therefore a defect by definition. Two mechanisms enforce it:
`.agents/scripts/tests/test_sops_prds_folder.py` (in `run_all`) checks this INDEX against the
directory both ways, that every link resolves, and that every `/command` reference names a real
command master; `check_maps.py` independently covers INDEX-path validity and level-2 INDEX presence
now that the docs are inside `docs/`.

**Adding a doc here** is a deliberate act: drop the file, add a row below, and add its filename to
`EXPECTED` in that test. The manifest is a contract — a doc appearing without a test change is
exactly the drift being guarded against.

## The operator's PRD

| Doc | What it is |
|---|---|
| [workflows_testing_SOP.md](workflows_testing_SOP.md) | **THE quick reference — start here.** The whole dev system on one page: the lifecycle map, every `/` command by lane (story loop ①②③, shipping, autopilot, toolkit upkeep), the test gate + verdicts, the P0–P3 risk matrix, and the TEA cheat-sheet. The one page that answers *what do I type*, and the only one an operator reads start to finish. Protected by an armed commit-msg gate (`sop_currency.py`): change how the system is USED and this page moves in the same commit, or the commit is rejected. Was `_my_resources/_quick_reference/sudo_workflows_testing.md`; renamed here because SCC-63 retired the `sudo-` prefix. |

## Jira & git — the manual half

| Doc | What it is |
|---|---|
| [jira_manual.md](jira_manual.md) | **Everything *you* do by hand** — no commands, no agents, no terminal. Creating a backlog item, §2.2.1 choosing the work type, moving it through a sprint, §2.6 flagging something broken (you never create a Bug ticket — the shipped ticket wears the flag), then the source-control half in the VS Code panel: branch naming, staging file-by-file, commit format, the three armed hooks and **where VS Code hides their output**, and §3.8 the one-command close-out. |
| [jira_integration_guide.md](jira_integration_guide.md) | **How work becomes an auditable record** — and why almost none of it depends on a model being available. The two-channel model, §6 the work-item type rule, the BMAD-number↔Jira-key join, §7 all three lanes (Story · Task · Epic), Smart Commits, the `commit-msg` gate plus the encoding and SOP-currency hooks, an `acli` + `jira_feed.py` cheat-sheet, and the honest enforcement picture (GitHub Free = alarm, not lock). |
| [git_walkthrough_settings.md](git_walkthrough_settings.md) | **The git config, explained from scratch** — what each of the ten machine-wide settings does and why. Picture-first; read once and merge-vs-rebase-vs-fast-forward stops being mysterious. ⚠ `~/.gitconfig` follows the *profile*, not you: it does not travel between machines. |

## The system itself

| Doc | What it is |
|---|---|
| [file_folder_structure+maintaining.md](file_folder_structure+maintaining.md) | **The one-stop guide to the home base** — the folder-as-workspace routing system, what lives where, and how it is kept healthy. The living overview that sits on top of `../workspace-standard.md`. |
| [complete-system-overview.md](complete-system-overview.md) | The full breakdown of the routing system, top to bottom. Deeper background than the guide above. |
| [autopilot_bmad_dev_loop.md](autopilot_bmad_dev_loop.md) | **The autopilot reference** — the 4-stage Dev/QA relay (Plan → Audit → Implement → Review+Fix): engine/harness split, the Engine Adapter, session continuity, the resilience + test-gate model, the model/effort ladder (§5b), and the worktree-based concurrency model. Covers every engine — `/cicd-autopilot-claude`, `/cicd-autopilot-deepseek4`, `/cicd-autopilot-opencode`. Was `.agents/reference/`; moved here by SCC-74, which also retired a six-week-stale duplicate. |
| [md_feedback_setup_guide.md](md_feedback_setup_guide.md) | Setting up the **MD Feedback** MCP server (annotations read straight from markdown) for Claude, opencode and Antigravity on a new machine. |

## Testing & quality

| Doc | What it is |
|---|---|
| [tea_testing_guide.md](tea_testing_guide.md) | The deep TEA reference: BMAD Test Architect agents, the ATDD red→green contract, test levels + the priorities matrix, and NFR / trace / gate mechanics. |
| [tea_deep_reference.md](tea_deep_reference.md) | The deep archive `workflows_testing_SOP.md` was carved from (2026-07-14): full command call-graphs, the TEA method curriculum, the Epic-8 anchor index, and the 42-fragment library. Kept for depth, not daily use. |
| [tdad_stack_install_guide.md](tdad_stack_install_guide.md) | Install/setup for the TDAD (test-driven agentic dev) stack — the BDD contract layer added to both the manual and autonomous workflows. |

## Security & advisory

| Doc | What it is |
|---|---|
| [sentry_error_response_team.md](sentry_error_response_team.md) | AviationChat's automated incident-response system (Epic 16): production breaks → a cloud agent investigates, builds the fix on its own hotfix branch, and the report lands on Daniel's phone. |
| [smh-adviser-board-REFERENCE.md](smh-adviser-board-REFERENCE.md) | The `/smh-adviser-board` roster: every mind with a full cognitive signature, so any bench mind can be subbed into a seat with a copy-paste. |

## A note inherited from `.agents/reference/`

That folder existed to hold long-form docs **deliberately off every command surface** — anything
dropped in `.agents/workflows/` becomes a `/` that Antigravity will offer to *run*, and
`platforms: []` does not help, because `/smh-sync-agents` vendors the directory wholesale. SCC-74
retired the folder by moving its one occupant here. The constraint still holds and is better served:
a doc in `docs/` is not on any command surface by construction.
