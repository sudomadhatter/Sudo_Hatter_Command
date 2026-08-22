# SOPs & PRDs — Index

**Every procedural document in this system lives here.** These are the pages that tell the operator
what to do and what to type — as opposed to `.agents/rules/` and `.agents/commands/`, which describe
the system to an *agent*. Consolidated by SCC-74 (2026-08-10) from `_my_resources/_quick_reference/`
and `_my_resources/diagrams_guides/`.

## Why this folder exists

The docs below rotted for years, and not from neglect. They lived in `_my_resources/`, which is named
in `SCAN_IGNORES` (`check_maps.py`), in `DEFAULT_REGEN_IGNORE` for the repo-map, and in the code-graph
ignore list — its own local law says *"excluded from repo-map regen + linter scans … do not fix
that."* **Every drift-checker in this system was forbidden to look at them.** The index they lived
under listed 2 files that did not exist and omitted 4 that did, and nothing could notice.

Operator ruling 2026-08-10 makes the division permanent:

| Folder | What it is | Staleness |
|---|---|---|
| `_my_resources/` | Daniel's human thinking + brainstorming space. **Agents ignore it unless he links a specific document.** | fine by design |
| `docs/` | the maintained surface | **must never go stale** |

A procedural doc sitting in the first is therefore a defect by definition. Two mechanisms enforce
this folder, and they cover **different things** — neither is a substitute for the other:

| Mechanism | What it actually catches | Blind to |
|---|---|---|
| `.agents/scripts/tests/test_sops_prds_folder.py` (in `run_all`) | this INDEX vs the directory **both ways**, every **markdown link** target, every `/command` reference resolving to a real master, the 13-doc manifest, and the SOP gate's two paths agreeing | prose that names no link |
| `check_maps.py` | **backticked multi-segment paths inside table rows**, plus level-2 INDEX presence and repo-map coverage | markdown links, and anything outside a table row |
| T9 in that same test (SCC-83) | **backticked paths in PROSE** — sentences and bullets: the gap between the two rows above | paths written *without* backticks, and the interior of a project this machine has not checked out |

⚠️ **T9 gives the same answer from a lane as from `main`, and that equality is the feature.**
`Projects/*` are separate gitignored repos, so `git worktree add` leaves them as empty stubs — a lane
sees 9, `main` sees 1. The first build of T9 coped with that through a `strict` mode, and the mode
turned out to be **off in both checkouts**, which made the primary check dead code while every gate
read green (SCC-83 code review, 2026-08-11). T9 now resolves project roots from `git rev-parse
--git-common-dir` instead of the working directory, so coverage no longer depends on where you are
standing: a lane and `main` return an **identical** finding set — **0 and 0** as shipped, **8 and 8**
with every by-design exemption lifted, keys *and* values equal both ways. Anything still unreachable
(an uninitialised submodule) is **named in the run output along with the docs that reference it**, so
a reduced run is visible and never reads as a clean one.

⛔ **On non-backticked paths — the honest version.** Strip the code spans and the markdown links and a couple of
hundred slash-bearing tokens remain, but they are overwhelmingly prose: `Dev/QA`, `and/or`,
`PASS/CONCERNS/FAIL`, `7/7`. Widening the net trades a handful of real checks for hundreds of false
ones, so **the backtick convention is the boundary** — not because few paths escape it, but because
nothing outside it can be told from ordinary writing. (An earlier version of this row claimed
"exactly 2", which was never measured, and claimed fenced blocks were covered, which is impossible —
the matcher requires backticks.)

⛔ **And `git log` cannot tell you which of these is rotting.** SCC-74 moved every file here with
`git mv` on 2026-08-10, so a bare last-commit date reports *when the file was relocated or last
touched editorially*, never when its content was last true — the dates cluster on the move and on
whatever ticket edited a page since, in neither case telling you anything about staleness. Use
`git log --follow -- <file>` for real content history.

That split is worth knowing before trusting either: `check_maps.py` reads table cells, so a dead
markdown link sails past it — T2/T3 are what catch those. Verified in both directions when this
folder landed (a planted dead path fails one, a planted dead link fails the other).

**Adding a doc here** is a deliberate act: drop the file, add a row below, and add its filename to
`EXPECTED` in that test. The manifest is a contract — a doc appearing without a test change is
exactly the drift being guarded against. **Removing one is the same three edits in reverse** — file,
row, `EXPECTED` — and the test fails loudly if you do fewer than all three.

**What does not belong here:** machine-setup and install guides. They tell you how to *build a
workstation*, not how to run the workflow, and they are read once per machine rather than during
work. `../md_feedback_setup_guide.md` was moved up to `docs/` on that basis (2026-08-10). It stays
inside `docs/`, so it is still on the maintained surface and still covered by `check_maps.py` — the
boundary being drawn is "SOP vs setup," never "watched vs unwatched."

## The operator's PRD

| Doc | What it is |
|---|---|
| [workflows_testing_SOP_changelog.md](workflows_testing_SOP_changelog.md) | **The SOP's change history** — one line per change: date · ticket · what changed for the operator, newest first. Exists so the SOP itself can state the *current* system with no change-narration (the writing contract: `sop-currency.md` §Writing the update, habit 4). A gate-driven SOP update puts its delta description here, in the same commit. |
| [workflows_testing_SOP.md](workflows_testing_SOP.md) | **THE quick reference — start here.** The whole dev system on one page: the lifecycle map, every `/` command by lane (story loop ①②③, shipping, autopilot, toolkit upkeep), the test gate + verdicts, the P0–P3 risk matrix, the TEA cheat-sheet — and, since SCC-161, **the command atlas** (Part VI): the call graph, who writes the board, where each command stops for you, and one mermaid diagram per critical command, each checked against the live command body. The one page that answers *what do I type*, and the only one an operator reads start to finish. Protected by an armed commit-msg gate (`sop_currency.py`): change how the system is USED and this page moves in the same commit, or the commit is rejected. Was the `sudo_workflows_testing.md` quick-reference in Daniel's personal area; renamed here because SCC-63 retired the `sudo-` prefix. |

## Jira & git — the manual half

| Doc | What it is |
|---|---|
| [jira_manual.md](jira_manual.md) | **Everything *you* do by hand** — no commands, no agents, no terminal. Creating a backlog item, §2.2.1 choosing the work type, moving it through a sprint, §2.6 flagging something broken (you never create a Bug ticket — the shipped ticket wears the flag), then the source-control half in the VS Code panel: branch naming, staging file-by-file, commit format, the three armed hooks and **where VS Code hides their output**, and §3.8 the one-command close-out. |
| [jira_integration_guide.md](jira_integration_guide.md) | **How work becomes an auditable record** — and why almost none of it depends on a model being available. The two-channel model, §6 the work-item type rule, the BMAD-number↔Jira-key join, §7 all three lanes (Story · Task · Epic), Smart Commits, the `commit-msg` gate plus the encoding and SOP-currency hooks, an `acli` + `jira_feed.py` cheat-sheet, and the honest enforcement picture (GitHub Free = alarm, not lock). |
| [git_walkthrough_settings.md](git_walkthrough_settings.md) | **The git config, explained from scratch** — what each of the ten machine-wide settings does and why. Picture-first; read once and merge-vs-rebase-vs-fast-forward stops being mysterious. ⚠ `~/.gitconfig` follows the *profile*, not you: it does not travel between machines. |

## The system itself

| Doc | What it is |
|---|---|
| [file_folder_structure+maintaining.md](file_folder_structure+maintaining.md) | **The one-stop guide to the home base — and the single system overview.** SCC-80 retired `complete-system-overview.md` into it (2026-08-10): 7 of that doc's 10 sections had a counterpart here, its §8 named a script that no longer exists and its §9 was a completed rollout plan. Its Glossary survives as §10a. — the folder-as-workspace routing system, what lives where, and how it is kept healthy. The living overview that sits on top of `../workspace-standard.md`. |
| [autopilot_bmad_dev_loop.md](autopilot_bmad_dev_loop.md) | **The autopilot reference** — the 4-stage Dev/QA relay (Plan → Audit → Implement → Review+Fix): engine/harness split, the Engine Adapter, session continuity, the resilience + test-gate model, the model/effort ladder (§5b), and the worktree-based concurrency model. Covers every engine — `/cicd-autopilot-claude`, `/cicd-autopilot-deepseek4`, `/cicd-autopilot-opencode`. Moved out of the toolkit's retired `reference` folder by SCC-74, which also resolved a six-week-stale duplicate. |

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
| [sharing_keys_secrets_secure.md](sharing_keys_secrets_secure.md) | **How to get a key onto a teammate's machine without it ever existing in a chat message.** The Keyway vault: install per machine, `keyway login` + `keyway init` per repo, and the daily loop — `keyway run` injects secrets into RAM so nothing durable lands on disk. The team half is the point: GitHub repo access decides **who is in at all**, production is a permission boundary rather than a label, and **offboarding is three steps — revoke, clear the dashboard role, then rotate**, because cutting GitHub access cannot un-copy a `.env` someone already pulled. Documents the flags that destroy data (`push --prune` against a stale file silently deletes your teammates' keys; `sync` is bidirectional and the one command defaulting to **production**; `-e` means `--exclude` on `scan` alone) and ⛔ **the hazard the tool creates itself: `keyway push` appends `.env*` to your `.gitignore` unprompted** — observed live, which is why `git diff .gitignore` after a first push is in the card. Also records why Keyway over GCP Secret Manager or Vault. Flags checked command-by-command against the live 0.5.3 binary (SCC-37). |
| [smh-adviser-board-REFERENCE.md](smh-adviser-board-REFERENCE.md) | The `/smh-adviser-board` roster: every mind with a full cognitive signature, so any bench mind can be subbed into a seat with a copy-paste. |

## Frontend & UI/UX design

| Doc | What it is |
|---|---|
| [frontend_UI_design_guide.md](frontend_UI_design_guide.md) | **The unified house frontend design and animation guide** — the three pillars of UI craft: visual intelligence and design systems ([`.agents/skills/ui-ux-pro-max`](../../.agents/skills/ui-ux-pro-max/SKILL.md)), fluid motion and spring physics (the Emil Kowalski animation skills suite: `emil-design-eng`, `apple-design`, `animate`, `review-animations`, `find-animation-opportunities`), and rich transparent video overlays ([`.agents/skills/webm-alpha-video`](../../.agents/skills/webm-alpha-video/SKILL.md)). Carries the agent routing matrix and the pre-delivery UI quality checklist. |

## A note inherited from the toolkit's retired reference folder

That folder existed to hold long-form docs **deliberately off every command surface** — anything
dropped in `.agents/workflows/` becomes a `/` that Antigravity will offer to *run*, and
`platforms: []` does not help, because `/smh-sync-agents` vendors the directory wholesale. SCC-74
retired the folder by moving its one occupant here. The constraint still holds and is better served:
a doc in `docs/` is not on any command surface by construction.
