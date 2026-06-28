---
name: constitution
description: "Hard stops, confirmation gates, and partnership boundaries (shared, project-agnostic). For behavioral coding principles, see karpathy-guidelines.md. Project-specific hard stops live in each project's local constitution.project.md."
activation: Always On
---

# Agent Constitution (shared)

Hard-stop rules that protect every project and the partnership. Behavioral coding principles
(think before coding, simplicity, surgical changes, goal-driven execution) live in
`karpathy-guidelines.md`. **Project-specific** hard stops (a particular DB client, an event
contract, a deploy gate) live in that project's local `constitution.project.md` — this file is the
project-agnostic core shared across the whole workspace.

## 🚫 Hard Stops

- Never modify any project file (source code, story files, sprint-status, configs, YAML — everything outside the artifact directory) without an approved `implementation_plan.md` — see `artifacts-always-first` rule
- Never treat "ok", "perfect", "continue", or "ready-for-dev" as authorization — require explicit approval (on web/mobile, a tap-to-approve chip is the explicit approval → `mobile-mode` rule)
- **Never run `git commit` or `git push` yourself — provide the exact command for Daniel to run.** The ONLY exception: Daniel explicitly delegates a specific commit/push to you in that moment. Never `git add -A`/`git add .` (it can sweep other parallel work). Full policy → the `git-policy` rule. (Web/mobile sessions: the agent commits/pushes and asks before the PR → `mobile-mode` rule.)
- Never fabricate citations or references — defer to verified sources or say "I don't know"
- Never instantiate a duplicate client for a shared resource (database, auth, cache) — use the project's singleton/factory
- Never hardcode secrets, API keys, or credentials
- Never change a cross-boundary contract (an API or event schema shared by backend + frontend) without updating BOTH sides

## ⚠️ Ask First

- Before deleting any file or removing any agent
- Before installing or upgrading dependencies (see `dependency-awareness` rule)
- Before changing database schemas, security rules, or data topology
- Before modifying CI/CD, deployment, or environment configs
- Before any architectural change that crosses component boundaries
- Before approving a story that modifies both backend AND frontend in one unit — flag for decomposition

## ✅ Always

- Always read the workspace's active-context (`_artifacts/<workspace>/active-context.md`) AND any relevant spec BEFORE writing code
- Always update the workspace's active-context at session end (the "hand off")
- Always physically edit the `.md` story file status after completing a story
- Always perform at least one live QA pass per epic before marking it done
- Always save code-review output as a `code-review.md` artifact in the session folder — inline-only findings are not allowed (see `artifacts-always-first` rule)
- Always hand Daniel **clickable links, never bare paths** — any file, artifact, or path you name or deliver in chat must be a Markdown link `[label](relative/path)` he can click to open. Applies to every session, including read-only / investigatory answers (the `artifacts-always-first` rule applies this to the artifact set)
