# Reference INDEX — deep docs, not commands

Router for `.agents/reference/`. These are **long-form reference docs that are deliberately NOT on any
command surface**. Nothing here is invocable.

## Why this folder exists

The other `.agents/` folders each feed a live surface:

| Folder | Surface it feeds |
|---|---|
| `commands/` | Claude `/` + opencode `/` (filtered by `platforms:` frontmatter) |
| `workflows/` | **Antigravity `/`** — Antigravity surfaces `/` from `workflows/` + `skills/`, never `commands/` |
| `skills/` | Claude + Codex skills |
| `rules/` | always-on guardrails, read in place |

That makes `workflows/` a *command surface*, not a docs folder: anything dropped there becomes a `/`
that Gemini will offer to run. A reference doc for a pipeline that only runs under one LLM therefore
does not belong in `workflows/` — Gemini would list it and try to execute a doc it can't act on.

Note that `platforms: []` frontmatter does **not** solve this: `/smh-sync-agents` vendors the whole master
`.agents/` into each project with a raw directory copy and no platform filtering, so the file would
still land in every project's `workflows/`. Keeping it out of the surface folder is the only fix.

| Doc | What it documents | Reach for it when… |
|---|---|---|
| `autopilot_bmad_dev_loop.md` | The reference for the 4-stage Dev/QA autopilot relay (Plan → Audit → Implement → Review+Fix): engine/harness split, the Engine Adapter, session continuity, the resilience + test-gate model, and the model/effort ladder (§5b). Covers all engines — `/cicd-autopilot-claude`, `/cicd-autopilot-deepseek4`, `/cicd-autopilot-opencode`. (`/autopilot_mobile` was deleted 2026-08-07 — mobile drives the desktop via Remote Control.) | you're running, debugging, extending, or re-tuning the autopilot — or deciding how the loop behaves under a given harness. |

**Adding a reference doc:** drop `<name>.md` here, add a row above. No `commands/` entry, no `platforms:`
frontmatter needed — this folder is off every surface by construction. If the doc *should* be invocable,
it belongs in `commands/` (with `platforms:`) instead.
