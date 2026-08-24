# Skills INDEX — when to use which (family map)

Router for the **skill surface an agent actually sees (~129)**: **73** local directories in
`.agents/skills/` (**34** hand-authored skills + **39** generated command launchers), plus the **56**
`bmad-*` skills BMAD installs directly into `.claude/skills/`. This repo is the local skills' master — shared, project-agnostic ONLY; a
product's domain packs live in that product's own `.agents/skills/`, per `project-law.md`. The BMAD families below live there, not here, so don't go
looking for them in the master dir. Unlike rules, **skills already self-route**: each has a
`SKILL.md` with a `description:` that the harness surfaces, so you rarely pick one by hand — you invoke
by intent or `/<skill-name>`. This INDEX is therefore a **family map** (so you know what domains exist),
not a per-skill list — that would go stale. To find one skill, match your task to a family, then to the
skill's own description.

| Family | Covers | Examples |
|---|---|---|
| **BMAD agents** | the named personas | `bmad-agent-dev` (Amelia) · `-pm` (John) · `-architect` (Winston) · `-analyst` (Mary) · `-ux-designer` (Sally) · `-tech-writer` (Paige) |
| **BMAD lifecycle** | plan → build → ship a story | `bmad-prd` · `bmad-create-architecture` · `bmad-create-epics-and-stories` · `bmad-create-story` · `bmad-dev-story` · `bmad-sprint-planning`/`-status` · `bmad-retrospective` · `bmad-correct-course` (the vendor review skill is RETIRED — reviews run on `code-review-engine`, below) |
| **BMAD test architecture** | quality, NFR, automated tests | `bmad-tea` (Murat) · `bmad-testarch-*` (atdd, automate, ci, framework, nfr, test-design, test-review, trace) · `bmad-qa-generate-e2e-tests` |
| **BMAD thinking/editorial** | ideation + adversarial review | `bmad-brainstorming` · `bmad-advanced-elicitation` · `bmad-party-mode` · `bmad-editorial-review-*` · `bmad-review-*` · `bmad-investigate` · `smh-adviser-board` (open-table board of historical minds → Brainstorm → Plan → Market → BMAD handoff) |
| **BMAD research/specs** | research + distillation | `bmad-domain-research` · `bmad-market-research` · `bmad-technical-research` · `bmad-spec` · `bmad-product-brief` · `bmad-prfaq` |
| **Firebase / GCP** | infra + deploy | `firebase-*-basics` (auth, firestore, hosting, app-hosting, data-connect, ai-logic) · `cicd-deploy-backend` · `troubleshoot-cloudrun-deployment` |
| **Backend / Python** | server + language patterns | `backend-dev-guidelines` · `python-patterns` |
| **Frontend / UI** | React, design systems & fluid motion | `react-best-practices` · `ui-ux-pro-max` (styles, palettes, charts, stacks) · `playwright-frontend-check` (**read a running frontend** — console, `pageerror`, failing network rows with bodies, screenshots; Node, and it carries the sandbox + project-dependency traps. The instrument `/cicd-live-testing-team` reaches for; NOT the E2E door, which is `/cicd-e2e`) · `webm-alpha-video` (green-screen MP4 → alpha-transparent WebM) · **Emil motion & UI craft:** `emil-design-eng` · `apple-design` · `animate` · `animate-expo` · `review-animations` · `find-animation-opportunities` · `improve-animations` · `animation-vocabulary` · `ask-sonner` · `pick-ui-library` · `prototype` · `write-swift` · *PRD Guide:* `docs/_scc_sops_prds/frontend_UI_design_guide.md` |
| **Prompting / diagrams / debug** | cross-cutting craft | `v3-prompt-architecture` · `mermaid-diagram-standards` · `systematic-debugging` |
| **Code quality gates** | is the code clean, and can you prove it | `cicd-clean-code-audit` — the auditor for `.agents/rules/code-standards.md`: machine floor (ruff · eslint · pyrefly · tsc) that can FAIL + a judgment pass (comment contract, AI-drift bans) that caps at CONCERNS. Diff-scoped. Runs standalone and as `/cicd-code-review` Step 3.5. · `code-review-engine` — the house review engine (SCC-116): lens fan-out → verify → triage → record over a diff the CALLER resolved, returning a severity floor. Invoked by the review commands, never run standalone. · `code-review-graph` — the house contract for the local code graph (MIT, Tree-sitter + SQLite, 30 MCP tools): ask it who-calls-this, what-breaks, what-has-no-test and what-does-this-diff-risk before you grep. Carries the merge-base rule and the measured precision limit. |
| **Workspace / system craft** | how the repo is organized, secrets, and Task work lands | `workspace-structure` (tier model · reading-order · AGENTS.md-vs-INDEX.md · naming — the decision layer over `docs/workspace-standard.md`) · `keyway-secrets` (cross-platform secrets sharing & in-memory execution via Keyway) · `smh-close-task-merge-tree` (gate · merge · Jira Dev Record · prune for a non-BMAD Task) |

**Naming (SCC-63):** skills carry **no family prefix** — `cicd-`/`smh-`/`sentry-` mark *commands*, and a
prefix here would imply a slash command that does not exist. A **generated launcher** inherits its
command's name (so `cicd-code-review/` is the door for `/cicd-code-review`); a **hand-authored** skill is
named for what it knows (`python-patterns`, `webm-alpha-video`).

**Adding a skill:** create `<name>/SKILL.md` with a `description:` that states when it applies (that's the
router), slot it into a family above if you keep this map current, and re-run `/smh-sync-agents`.
