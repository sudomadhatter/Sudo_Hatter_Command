# Rules INDEX — when to use which

Router for `.agents/rules/`. **Scan this to dispatch** — pull the one rule a task calls for instead of
reading all of them (least-context). Each rule also self-describes via its frontmatter `description:`;
this table is the at-a-glance version. This is the shared/master set; a project may vendor extra rules
(see its own `AGENTS.md` routing table).

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

## The set

| Rule | Load | Trigger — reach for it when… |
|---|---|---|
| `operator-profile.md` | floor | always — who Daniel is, the Jobs/Woz division of labor, and the eight speaking obligations. The upstream WHY behind `prose-formatting`, `mermaid-diagram-preferences`, `collaborative-debug-first`, and the clickable-links / inline-key-points rules. |
| `constitution.md` | floor | always — hard stops, confirmation gates, partnership boundaries (shared). |
| `karpathy-guidelines.md` | floor | always — behavioral coding principles (think first, simplicity, surgical, verify). |
| `artifacts-always-first.md` | protocol | any session that may modify files — the plan-first artifact protocol (plan→approve→build→walkthrough). |
| `git-policy.md` | protocol | any time git comes up — the branch model + the write gate: your `claude/*` branch is free (commit AND push), the epic branch lands at Daniel's sign-off, `main` is his alone (epic merges via `/sudo-push-e2e`). |
| `worktree-per-story.md` | protocol | a sudo story lane (①/②/quick-dev/autopilot) starts work that will produce commits — worktree off the epic branch first, commit freely inside, land + prune via close-out. Ad-hoc non-story work: NO worktree — `chore/*` branch off `main`. |
| `000-PLAN-FIRST-GATE.md` | protocol | any dev work or BMAD dev-skill run — incl. lobby-rooted `quick-dev` maintenance — PRIORITY-ZERO kill-chain: no project file modified until Daniel approves an `implementation_plan.md`; the `_bmad/custom/` guard tomls load it into every dev-story/quick-dev run (parity across lobby + AGY + Fresh, 2026-07-09). |
| `sudo-target-resolution.md` | on-demand | any `/sudo-*` command's Step 0 — the canonical target-resolution ladder (§STD/§ASK/§DUAL) + the `PROJECT_ROOT` §BIND rule that the commands point at instead of restating. |
| `code-standards.md` | on-demand | writing, reviewing, or gating code — **the house definition of "clean"**: the comment contract (`Story X.Y` provenance + `AIDEV-NOTE` anchors), the AI-drift bans, style/organization, the machine floor (ruff · eslint · pyrefly · tsc), and the FAIL-vs-CONCERNS split. The `clean-code-audit` skill and `/sudo-code-review` Step 3.5 both enforce THIS file — edit the standard here and the gate follows. |
| `dependency-awareness.md` | on-demand | modifying `package.json` / `requirements.txt` / `pyproject.toml` or any dependency manifest. |
| `powershell-encoding-safety.md` | on-demand | writing/restoring file content via shell on Windows — avoid UTF-16/BOM corruption. |
| `lobby-search.md` | on-demand | searching the tree FROM the lobby root — Grep/Glob are blind to `Projects/` (gitignore); the correct search patterns. Lobby-specific. |
| `bmad_code_review_sudo_fix.md` | on-demand | the `bmad-code-review` skill/workflow runs — run-to-completion review (any agent), no halting; stops at `review`. |
| `reproduce-before-you-fix.md` | on-demand | **something is reported broken** — a bug, a red suite, an incident, "it's not working". The house debug loop as five gates: reproduce (citable, or say it doesn't) → minimize → pin with a test SEEN red → falsify one hypothesis at a time under a stop condition → minimal fix at the cause → prove it by reverting the fix. Pulled by `karpathy-guidelines` §1; `collaborative-debug-first` is its G1 branch. |
| `collaborative-debug-first.md` | on-demand | you can't observe runtime (browser/network/Firestore/UI) but Daniel can — instrument + ask, don't guess. The **G1 can't-observe branch** of `reproduce-before-you-fix`. |
| `completion-not-illusion.md` | on-demand | a workflow emits polished intermediate artifacts — a polished artifact is a claim, not proof of done. |
| `tests-must-gate-for-real.md` | on-demand | writing acceptance/ATDD tests, scaffolding/reviewing a CI gate, or marking a suite report-only/soft/skip — a red must fail for the right reason, CI must run the REAL suite, and no gate is soft forever. |
| `mermaid-diagram-preferences.md` | on-demand | generating a Mermaid diagram — never `sequenceDiagram`; use `flowchart TD`/`LR`. |
| `prose-formatting.md` | on-demand | writing a conversational chat reply — prose over scaffolding (does NOT govern deliverable docs). |
| `mobile-mode.md` | on-demand (auto on web/mobile) | the session is web/mobile (remote container) or Daniel says "mobile" — adapts git, the approval gate, artifacts, and verification for the phone. |
| `living-template-sync.md` | on-demand | you change a shared rule, the front-door pattern, or a folder/workspace convention at the home base — propagate it into `Fresh_Workspace_BMAD` (the living template new projects clone from) so new projects start current, not stale. |



## Adding a rule
1. Create `<name>.md` with frontmatter: `name:` + a `description:` that states **when it activates** (the
   trigger), mirroring the rows above.
2. Add a row here.
3. If it's project-specific (not shared), keep it in that project's `.agents/rules/` and route it from the
   project `AGENTS.md` instead of here.
