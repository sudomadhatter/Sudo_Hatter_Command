# Skills INDEX — when to use which (family map)

Router for `.agents/skills/` (~100 skills). Unlike rules, **skills already self-route**: each has a
`SKILL.md` with a `description:` that the harness surfaces, so you rarely pick one by hand — you invoke
by intent or `/<skill-name>`. This INDEX is therefore a **family map** (so you know what domains exist),
not a per-skill list — that would go stale. To find one skill, match your task to a family, then to the
skill's own description.

| Family | Covers | Examples |
|---|---|---|
| **BMAD agents** | the named personas | `bmad-agent-dev` (Amelia) · `-pm` (John) · `-architect` (Winston) · `-analyst` (Mary) · `-ux-designer` (Sally) · `-tech-writer` (Paige) |
| **BMAD lifecycle** | plan → build → ship a story | `bmad-prd` · `bmad-create-architecture` · `bmad-create-epics-and-stories` · `bmad-create-story` · `bmad-dev-story` · `bmad-code-review` · `bmad-sprint-planning`/`-status` · `bmad-retrospective` · `bmad-correct-course` |
| **BMAD test architecture** | quality, NFR, automated tests | `bmad-tea` (Murat) · `bmad-testarch-*` (atdd, automate, ci, framework, nfr, test-design, test-review, trace) · `bmad-qa-generate-e2e-tests` |
| **BMAD thinking/editorial** | ideation + adversarial review | `bmad-brainstorming` · `bmad-advanced-elicitation` · `bmad-party-mode` · `bmad-editorial-review-*` · `bmad-review-*` · `bmad-investigate` |
| **BMAD research/specs** | research + distillation | `bmad-domain-research` · `bmad-market-research` · `bmad-technical-research` · `bmad-spec` · `bmad-product-brief` · `bmad-prfaq` |
| **Firebase / GCP** | infra + deploy | `firebase-*-basics` (auth, firestore, hosting, app-hosting, data-connect, ai-logic) · `gcp-cloud-run` · `deploy-backend` · `troubleshoot-cloudrun-deployment` |
| **Backend / Python** | server + language patterns | `backend-dev-guidelines` · `python-patterns` · `python_inter_venv_fix` |
| **Frontend / UI** | React + design | `react-best-practices` · `ui-ux-pro-max` |
| **Voice / AI / RAG** | model + retrieval topology | `3_voice-ai-development` · `gemini-live-api` · `rag-implementation` · `6_dual-store-rag-patterns` · `4_sse-streaming-patterns` |
| **Prompting / diagrams / debug** | cross-cutting craft | `adk-prompting` · `v3-prompt-architecture` · `mermaid-diagram-standards` · `systematic-debugging` |
| **Workspace / system craft** | how the repo is organized | `workspace-structure` (tier model · reading-order · AGENTS.md-vs-INDEX.md · naming — the decision layer over `docs/workspace-standard.md`) |
| **Project domain** (project-specific) | this app's internals | `agent-handoff-patterns` · `hr-agent-schema-guide` · `regulatory-verification-protocol` · `specialist_agents_team` · `architectural-propagation` |

**Adding a skill:** create `<name>/SKILL.md` with a `description:` that states when it applies (that's the
router), slot it into a family above if you keep this map current, and re-run `/sync-agents`.
