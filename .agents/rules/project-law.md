---
name: project-law
description: "The two-tier rule model. The command center owns ALL workflow law (rules, commands, skills, sync); a project owns ONLY its own product law — `.agents/rules/` + `.agents/skills/` routed by its `.agents/INDEX.md`. Fires when you BIND a project (every /sudo-* Step 0 — reading that INDEX is mandatory, not optional), and when you AUTHOR a rule/skill and must decide which tier it belongs to."
---

# Project Law — the two-tier rule model

The command center is the single home of **how we work**. A project is the single home of **what this
product is**. Both are law; they live in different places on purpose, and the center is what carries
work between them.

| Tier | Lives at | Holds | Reaches |
|---|---|---|---|
| **Tier 1 — workflow law** | the command center's `.agents/` | rules · commands · skills · workflows · scripts · templates | every project, every platform, every session |
| **Tier 2 — project law** | `Projects/<name>/.agents/` | `rules/` + `skills/` + `INDEX.md` **only** | that one project |

A project carries **no** copy of tier 1. No vendored commands, workflows, scripts, or shared rules; no
tracked `.claude/`, `.opencode/`, `.gemini/`, `.antigravity/`. Sessions run from the command center, so
tier 1 is already loaded — a second copy inside the project is dead weight that drifts.

## ⛔ Binding a project MEANS loading its law

**This is the load-bearing obligation of this file.** Tier 2 is invisible unless something reads it, and
the only moment that reliably happens is when a target gets bound.

> **On binding `PROJECT_ROOT` — before any other step of the calling command — read
> `PROJECT_ROOT/.agents/INDEX.md` and honor its `Load` column.** Load its floor rules immediately; note
> its protocol rules as due before your first write in that project; leave on-demand rules for their
> triggers. A converted project whose `.agents/INDEX.md` is **missing** → **STOP and say so** — never
> proceed as if the project had no law. Absence is a defect, never a default.

This is bound into `sudo-target-resolution.md` §BIND (which every `/sudo-*` Step 0 walks), stated inline
in the lobby and project `AGENTS.md`, carried as a Hard Stop in the always-loaded `constitution.md`, and
enforced by `check_maps.py` (a converted project with no `.agents/INDEX.md` is a lint ERROR). Five
anchors, one obligation — if you ever find a sixth path that binds a project without reading its INDEX,
that is a defect: close the path, don't weaken the rule.

## The project's `.agents/INDEX.md`

Same shape and the same three load classes as the master rules INDEX, scoped to one project:

- **floor** — load at bind, every session touching this project (its `constitution.project.md`,
  its architecture invariants).
- **protocol** — load before the first tool call that writes a file *in this project*.
- **on-demand** — load when the `Trigger` column fires.

It routes both `rules/` and `skills/`. **Tier-2 skills load by PATH from the INDEX, never as slash
commands** — `/name` invocation is a machine-global surface, so it stays tier 1. A tier-2 skill is
reference material the INDEX points you at; that is the whole difference.

## Authoring — which tier does this belong to?

**The command center authors project law.** When a session (usually `/sudo-update-sprint-memory`'s
learning-routing step) produces a durable lesson, rule, or reference, it is written into the tier its
content belongs to — and a project-specific one goes into **that project's** `.agents/`, never the
master.

Apply this test, in order:

1. **Would this be true in a project we haven't built yet?** → tier 1. How we branch, how we gate, how
   we test, how we speak, how we close a story.
2. **Does it name this product's components, contracts, stack, or domain?** → tier 2. Its agent
   architecture, its schema, its credential paths, its framework quirks, its regulatory domain.
3. **Genuinely both?** → the generic law goes to tier 1 and the project's specifics go to tier 2 as a
   short rule that points at it. Never fork the shared rule into a project.

Symmetry matters: a rule that leaks *up* is as bad as one that leaks *down*. Product-domain skills sitting
in the master pollute every unrelated session's skill list; shared workflow rules copied into a project
drift from the master and start contradicting it.

**The one exception is a hard dependency.** A file that a project's own machinery must load by path at
runtime — where no center path survives both machines and a git worktree — is inlined into that
machinery rather than referenced. The BMAD `_bmad/custom/*.toml` guard files carry the plan-first gate
this way. Inline it, and leave the full rule at the center as the canonical copy.

## Hard stops

- NEVER bind a project without reading its `.agents/INDEX.md` — missing INDEX in a converted project is a
  STOP, not a shrug.
- NEVER vendor tier 1 into a project. `/sync-agents` targets the command center and the machine-global
  caches only.
- NEVER write a project-specific rule or skill into the master `.agents/`, or a shared workflow rule into
  a project.
- NEVER register a tier-2 skill as a slash command — route it by path from the project INDEX.
