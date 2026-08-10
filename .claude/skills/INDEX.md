# Skills INDEX — when to use which (family map)

Router for the **skill surface an agent actually sees (~90)**, which comes from two places: the **32**
authored skills in `.agents/skills/` (this repo is their master — shared, project-agnostic ONLY; a
product's domain packs live in that product's own `.agents/skills/`, per `project-law.md`) plus the **56** `bmad-*` skills BMAD
installs directly into `.claude/skills/` — the BMAD families below live there, not here, so don't go
looking for them in the master dir. Unlike rules, **skills already self-route**: each has a
`SKILL.md` with a `description:` that the harness surfaces, so you rarely pick one by hand — you invoke
by intent or `/<skill-name>`. This INDEX is therefore a **family map** (so you know what domains exist),
not a per-skill list — that would go stale. To find one skill, match your task to a family, then to the
skill's own description.

| Family | Covers | Examples |
|---|---|---|
| **BMAD agents** | the named personas | `bmad-agent-dev` (Amelia) · `-pm` (John) · `-architect` (Winston) · `-analyst` (Mary) · `-ux-designer` (Sally) · `-tech-writer` (Paige) |
| **BMAD lifecycle** | plan → build → ship a story | `bmad-prd` · `bmad-create-architecture` · `bmad-create-epics-and-stories` · `bmad-create-story` · `bmad-dev-story` · `bmad-code-review` · `bmad-sprint-planning`/`-status` · `bmad-retrospective` · `bmad-correct-course` |
| **BMAD test architecture** | quality, NFR, automated tests | `bmad-tea` (Murat) · `bmad-testarch-*` (atdd, automate, ci, framework, nfr, test-design, test-review, trace) · `bmad-qa-generate-e2e-tests` |
| **BMAD thinking/editorial** | ideation + adversarial review | `bmad-brainstorming` · `bmad-advanced-elicitation` · `bmad-party-mode` · `bmad-editorial-review-*` · `bmad-review-*` · `bmad-investigate` · `smh-adviser-board` (open-table board of historical minds → Brainstorm → Plan → Market → BMAD handoff) |
| **BMAD research/specs** | research + distillation | `bmad-domain-research` · `bmad-market-research` · `bmad-technical-research` · `bmad-spec` · `bmad-product-brief` · `bmad-prfaq` |
| **Firebase / GCP** | infra + deploy | `firebase-*-basics` (auth, firestore, hosting, app-hosting, data-connect, ai-logic) · `cicd-deploy-backend` · `troubleshoot-cloudrun-deployment` |
| **Backend / Python** | server + language patterns | `backend-dev-guidelines` · `python-patterns` |
| **Frontend / UI** | React + design | `react-best-practices` · `ui-ux-pro-max` · `webm-alpha-video` (green-screen MP4 → alpha-transparent WebM via ffmpeg; skill only, no slash command) |
| **Prompting / diagrams / debug** | cross-cutting craft | `adk-prompting` · `v3-prompt-architecture` · `mermaid-diagram-standards` · `systematic-debugging` |
| **Code quality gates** | is the code clean, and can you prove it | `cicd-clean-code-audit` — the auditor for `.agents/rules/code-standards.md`: machine floor (ruff · eslint · pyrefly · tsc) that can FAIL + a judgment pass (comment contract, AI-drift bans) that caps at CONCERNS. Diff-scoped. Runs standalone and as `/cicd-code-review` Step 3.5. |
| **Workspace / system craft** | how the repo is organized and Task work lands | `workspace-structure` (tier model · reading-order · AGENTS.md-vs-INDEX.md · naming — the decision layer over `docs/workspace-standard.md`) · `smh-close-task-merge-tree` (gate · merge · Jira Dev Record · prune for a non-BMAD Task) |

**Naming (SCC-63):** skills carry **no family prefix** — `cicd-`/`smh-`/`sentry-` mark *commands*, and a
prefix here would imply a slash command that does not exist. A **generated launcher** inherits its
command's name (so `cicd-code-review/` is the door for `/cicd-code-review`); a **hand-authored** skill is
named for what it knows (`python-patterns`, `webm-alpha-video`).

**Adding a skill:** create `<name>/SKILL.md` with a `description:` that states when it applies (that's the
router), slot it into a family above if you keep this map current, and re-run `/smh-sync-agents`.
