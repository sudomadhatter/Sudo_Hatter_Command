# Rules INDEX — when to use which

Router for `.agents/rules/`. **Scan this to dispatch** — pull the one rule a task calls for instead of
reading all of them (least-context). Each rule also self-describes via its frontmatter `description:`;
this table is the at-a-glance version. This is the shared/master set; a project may vendor extra rules
(see its own `AGENTS.md` routing table).

## How rules load
- **Floor (always-load):** `constitution.md` + `karpathy-guidelines.md` — plus `AGENTS.md` is the map.
  Nothing else is preloaded.
- **Protocol (every work session):** `artifacts-always-first.md` + `git-policy.md` — referenced by the
  constitution; they govern any session that touches files.
- **On-demand (trigger):** the rest load only when their trigger fires (the `Trigger` column below).

## The set

| Rule | Load | Trigger — reach for it when… |
|---|---|---|
| `constitution.md` | floor | always — hard stops, confirmation gates, partnership boundaries (shared). |
| `karpathy-guidelines.md` | floor | always — behavioral coding principles (think first, simplicity, surgical, verify). |
| `artifacts-always-first.md` | protocol | any session that may modify files — the plan-first artifact protocol (plan→approve→build→walkthrough). |
| `git-policy.md` | protocol | any time git comes up — you NEVER commit/push; hand Daniel the command unless he delegates that specific action. |
| `code-standards.md` | on-demand | writing/reviewing backend (Python/FastAPI) or frontend (React/TS) code — style + organization. |
| `dependency-awareness.md` | on-demand | modifying `package.json` / `requirements.txt` / `pyproject.toml` or any dependency manifest. |
| `powershell-encoding-safety.md` | on-demand | writing/restoring file content via shell on Windows — avoid UTF-16/BOM corruption. |
| `bmad_code_review_fast_path.md` | on-demand | the `bmad-code-review` skill/workflow runs — solo-agent sequential review, no halting. |
| `collaborative-debug-first.md` | on-demand | you can't observe runtime (browser/network/Firestore/UI) but Daniel can — instrument + ask, don't guess. |
| `completion-not-illusion.md` | on-demand | a workflow emits polished intermediate artifacts — a polished artifact is a claim, not proof of done. |
| `mermaid-diagram-preferences.md` | on-demand | generating a Mermaid diagram — never `sequenceDiagram`; use `flowchart TD`/`LR`. |
| `prose-formatting.md` | on-demand | writing a conversational chat reply — prose over scaffolding (does NOT govern deliverable docs). |
| `mobile-mode.md` | on-demand (auto on web/mobile) | the session is web/mobile (remote container) or Daniel says "mobile" — adapts git, the approval gate, artifacts, and verification for the phone. |

## Adding a rule
1. Create `<name>.md` with frontmatter: `name:` + a `description:` that states **when it activates** (the
   trigger), mirroring the rows above.
2. Add a row here.
3. If it's project-specific (not shared), keep it in that project's `.agents/rules/` and route it from the
   project `AGENTS.md` instead of here.
