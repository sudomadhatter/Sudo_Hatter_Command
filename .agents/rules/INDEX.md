# Rules INDEX — when to use which

Router for `.agents/rules/`. **Scan this to dispatch** — pull the one rule a task calls for instead of
reading all of them (least-context). Each rule also self-describes via its frontmatter `description:`;
this table is the at-a-glance version. This is the **tier-1 shared set** — the only copy, read in place
from here by every session. A project carries only its OWN rules, routed from its `.agents/INDEX.md`
(thin model → `project-law.md`); nothing is vendored into projects any more.

## How rules load
- **Floor (always-load):** `operator-profile.md` + `constitution.md` + `karpathy-guidelines.md` — plus
  `AGENTS.md` is the map. Nothing else is preloaded. (`operator-profile` is floor by necessity: an
  on-demand "how to talk to him" rule would load *after* the reply that needed it.)
- **Protocol (load BEFORE the first file-writing tool call):** `artifacts-always-first.md` +
  `000-PLAN-FIRST-GATE.md` + `git-policy.md` + `worktree-per-story.md`. Conditional, but every gate they
  carry is *also* stated inline in `AGENTS.md` (§3's ⛔ ARTIFACTS block, §6's WORKTREE + GIT WRITE gates)
  and in the floor `constitution.md` Hard Stops — so the stop binds even if the rule never opens. They
  carry the mechanics, not the only copy of the law.
- **On-demand (trigger):** the rest load only when their trigger fires (the `Trigger` column below).

### The Load column is the classification; the frontmatter MIRRORS it

Two platforms now load rules by themselves, and each reads a different field, so every rule carries
activation frontmatter that must agree with the `Load` column above. `test_rule_frontmatter.py`
fails when they disagree — the table stays the source of truth, the frontmatter is its projection.

| Load here | `trigger:` | Also carries | Who acts on it |
|---|---|---|---|
| floor | `always_on` | — | Antigravity loads it every session; Claude gets it via `AGENTS.md` §3 |
| protocol | `model_decision` | — | judged against the request; the gate is *also* inline in `AGENTS.md`, so it binds either way |
| on-demand, **file**-shaped | `glob` | `globs:` **and** `paths:` (same set) | Antigravity reads `globs:`; Claude Code reads `paths:` from the generated `.claude/rules/<name>.md` and loads the rule ONLY when it opens a matching file |
| on-demand, **intent**-shaped | `model_decision` | `triggers:` (keywords) | Antigravity judges `description:`; `.agents/hooks/rule-trigger.py` matches `triggers:` against the prompt and injects a one-line pointer |

⛔ **`paths:` never goes on a floor or protocol rule.** A rule *without* `paths:` loads at launch,
unconditionally — which is right for the floor and wrong for everything else. Path-scoping a
protocol rule would bury a gate until something happened to open a matching file.

⛔ **`.claude/rules/` holds generated COPIES, not symlinks** — a Windows checkout without Developer
Mode materialises a symlink as a text file containing a path, so the rule would load as one line of
nonsense on the machine least likely to notice. `/smh-sync-agents` writes them and retires any whose
master stopped being path-scoped.

## The set

| Rule | Load | Trigger — reach for it when… |
|---|---|---|
| `operator-profile.md` | floor | always — who Mr. Hatter is (Sudo Mad Hatter / SMH), the Jobs/Woz division of labor, and the **nine** speaking obligations - #9 (close the loop; a finding without a fix is a bill) is the one the house breaks most, and it binds every reply, not just a review. The upstream WHY behind `mermaid-diagram-preferences`, `collaborative-debug-first`, and the clickable-links / inline-key-points rules — and, since SCC-333, the sole home of the formatting doctrine that `prose-formatting.md` used to contradict. |
| `constitution.md` | floor | always — hard stops, confirmation gates, partnership boundaries (shared). |
| `karpathy-guidelines.md` | floor | always — behavioral coding principles (think first, simplicity, surgical, verify). |
| `artifacts-always-first.md` | protocol | any session that may modify files — the plan-first artifact protocol (plan→approve→build→walkthrough). |
| `git-policy.md` | protocol | any time git comes up — the branch model + the write gate: your `claude/*` branch is free (commit AND push), the epic branch lands at Mr. Hatter's sign-off, `main` is his alone (epic merges via `/cicd-push-e2e`). |
| `worktree-per-story.md` | protocol | ANY lane starts work that will produce commits (SCC-62: the trigger is concurrency, not work type) — worktree BEFORE the first edit: story lane → `claude/*` off the epic branch, ad-hoc/Task → `chore/*` off `main`; commit freely inside, each pruned by its own close-out. |
| `000-PLAN-FIRST-GATE.md` | protocol | any dev work or BMAD dev-skill run — incl. lobby-rooted `quick-dev` maintenance — PRIORITY-ZERO kill-chain: no project file modified until Mr. Hatter approves an `implementation_plan.md`; the `_bmad/custom/` guard tomls carry it INLINE in every dev-story/quick-dev run (2026-08-07: inlined in AGY + VR + the skeleton, since the tomls load from inside a project where no center path resolves). |
| `smh-target-resolution.md` | on-demand | any `/cicd-*` command's Step 0 — the canonical target-resolution ladder (§STD/§ASK/§DUAL) + the `PROJECT_ROOT` §BIND rule that the commands point at instead of restating. |
| `project-law.md` | on-demand | binding a project — §BIND makes reading `PROJECT_ROOT/.agents/INDEX.md` mandatory (missing in a converted project = STOP) — or authoring a rule/skill and deciding its tier: the center owns workflow law; a project owns ONLY its own `rules/` + `skills/` + `INDEX.md` (plus the repo-local enforcement carve-out). |
| `port-checklist.md` | on-demand | **a file in SCOPE exists in more than one repo**, or the ticket says the work is a port (SCC-176) — lobby→project and project→lobby are the same operation, so it runs in BOTH directions. Six checks, each with the command that answers it: a git-given path used as given · `printf` not `echo` · verify the FILE not `$?` · no `.agents/rules/` path a thin repo lacks · `python3`-vs-`python` and per-machine `core.hooksPath` · hooks stay repo-local and the port needs the target's own Jira key. Items 4 and 6 cite `project-law.md` rather than restating it. `workflow_lint`'s `_RULE_POINTERS` warns when a command describes a port and cites nothing. |
| `work-consolidation.md` | on-demand | work is DISCOVERED mid-lane, or a Task's subtasks are being planned (SCC-170) — look for a home before you mint; when able ONE worktree/branch carries the whole Task with its subtasks as `riders:`, keyed per-commit by the subtask, closed once under the parent; two stops, artifact-first, verify the outcome. Judgment, not a gate. |
| `jira.md` | on-demand | the Jira board comes up outside a sudo command — reading/moving/minting tickets, JQL, "what's In Progress?". The board is reachable NOW via the authenticated `acli` CLI (no MCP, no config); this rule carries the cheat-sheet, flag traps, ticket↔file join, and guardrails. |
| `zoo-team.md` | on-demand | the Wonderland team comes up — the Zoo Code mode picker's six seats (March Hare — TEAM LEAD autopilot · White Rabbit — PM · Carpenter — ENGINEER · Caterpillar — DESIGNER · Cheshire Cat — TESTER · Queen of Hearts — QA, edit-stripped), the hand-off order, the cicd-vs-smh routing law, and the per-machine auto-approve tiles delegation needs. Synced verbatim into `.roo/rules/` so every Zoo seat carries it always-on; masters are `.agents/commands/smh-team-*.md` (SCC-350). |
| `command-shape.md` | on-demand | composing any shell command that is compound (cd chains, `&&` sequences), piping/tailing a gate run, or an approval prompt fires on a command you believed was allowlisted — every platform's allowlist is a PREFIX matcher, so the three bans (no cd-chains → `git -C`/absolute paths · no `; echo "EXIT=$?"` tails · no piped gates) are what keep pre-approval working at all. Read-only chains stay legal on Claude via `allow-readonly-chain.py` (SCC-287). |
| `code-standards.md` | on-demand | writing, reviewing, or gating code — **the house definition of "clean"**: the comment contract (`Story X.Y` provenance + `AIDEV-NOTE` anchors), the AI-drift bans, style/organization, the machine floor (ruff · eslint · pyrefly · tsc), and the FAIL-vs-CONCERNS split. The `cicd-clean-code-audit` skill and `/cicd-code-review` Step 3.5 both enforce THIS file — edit the standard here and the gate follows. |
| `dependency-awareness.md` | on-demand | modifying `package.json` / `requirements.txt` / `pyproject.toml` or any dependency manifest. |
| `powershell-encoding-safety.md` | on-demand | writing/restoring file content via shell on Windows — avoid UTF-16/BOM corruption. |
| `lobby-search.md` | on-demand | searching the tree FROM the lobby root — Grep/Glob are blind to `Projects/` (gitignore); the correct search patterns. Lobby-specific. |
| `reproduce-before-you-fix.md` | on-demand | **something is reported broken** — a bug, a red suite, an incident, "it's not working". The house debug loop as five gates: reproduce (citable, or say it doesn't) → minimize → pin with a test SEEN red → falsify one hypothesis at a time under a stop condition → minimal fix at the cause → prove it by reverting the fix. Pulled by `karpathy-guidelines` §1; `collaborative-debug-first` is its G1 branch. |
| `collaborative-debug-first.md` | on-demand | you can't observe runtime (browser/network/Firestore/UI) but Mr. Hatter can — instrument + ask, don't guess. The **G1 can't-observe branch** of `reproduce-before-you-fix`. |
| `completion-not-illusion.md` | on-demand | a workflow emits polished intermediate artifacts — a polished artifact is a claim, not proof of done. |
| `tests-must-gate-for-real.md` | on-demand | writing acceptance/ATDD tests, scaffolding/reviewing a CI gate, marking a suite report-only/soft/skip, **or running a MUTATION sweep** — a red must fail for the right reason, CI must run the REAL suite, no gate is soft forever, and §&nbsp;Mutation&nbsp;Testing carries the procedure: declare the table first, draw mutants from the CODE, a survivor is a finding, a mutant that removes nothing is DEFECTIVE. |
| `mermaid-diagram-preferences.md` | on-demand | generating a Mermaid diagram — never `sequenceDiagram`; use `flowchart TD`/`LR`. |
| `mobile-mode.md` | on-demand (auto on web/mobile) | the session is web/mobile (remote container) or Mr. Hatter says "mobile" — adapts git, the approval gate, artifacts, and verification for the phone. |
| `living-template-sync.md` | on-demand | you change the **front door, folder layout, thin-project floor, enforcement set, or the BMAD tomls** at the home base — hand-mirror it into the `sudo-project-skeleton` repo (the clone source) or every new project starts stale. Shared rules/commands/skills need NO mirroring: projects read them from the center. |
| `sop-currency.md` | on-demand | you change how the command center is **USED** — a `/` command (add/rename/retire), a rule, a safety-net script, a commit gate, or the root `AGENTS.md`. The SOP quick-reference `docs/_scc_sops_prds/workflows_testing_SOP.md` is the operator's PRD and must move **in the same commit**; an armed commit-msg gate rejects the commit otherwise, with `[sop-ok]` as the logged opt-out. Sibling of `living-template-sync` — that one keeps new projects from being born stale, this one keeps the manual from going stale. |



## Adding a rule
1. Create `<name>.md` with frontmatter: `name:` + a `description:` that states **when it activates** (the
   trigger), mirroring the rows above.
2. Add a row here.
3. If it's project-specific (not shared), keep it in that project's `.agents/rules/` and route it from the
   project `AGENTS.md` instead of here.
