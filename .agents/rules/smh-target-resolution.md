---
name: smh-target-resolution
description: "The canonical Step-0 target-resolution ladder every /cicd-* command binds with: self fast-path → $ARGUMENTS inline override → .agents/active-project.txt pointer → STOP-and-ask. Variants: §ASK (boot — always confirm, never silently reuse the pointer) and §DUAL (park/resume — lobby + active project, both repos). Plus §BIND (everything resolves under PROJECT_ROOT; missing path → STOP; binding = reading the project's `.agents/INDEX.md` law) and the echo contract. Commands state the obligations inline and point here for the mechanics."
trigger: model_decision
triggers: [target resolution, step 0, project_root, bind the project, which project]
# Intent-shaped: no glob can catch it, because the trigger is what the operator ASKS,
# not what gets opened. Antigravity judges `description:` against the request;
# `.agents/hooks/rule-trigger.py` matches these keywords and injects a pointer.

---

# Sudo Target Resolution — the Step-0 ladder (single source)

Every `/cicd-*` command operates on exactly ONE target — never the lobby. The command's own Step 0 keeps
the obligations (echo contract · STOP-and-ask · binding STOPs) inline and points at the variant here for
the mechanics. This file is the only place the ladder is written out.

> **The one named exception: `/cicd-label-tasks` (SCC-56, 2026-08-09; renamed from
> `/cicd-parallel-check` by SCC-155).** It does not walk this ladder
> at all — it derives its target from the Jira key it was given, via each repo's `.agents/jira.conf`
> (`AVCH-13` → `Projects/AGY_AVIATIONCHAT`, `SCC-12` → the lobby), so the target is never asked and never
> guessed. **The lobby is in scope for it, and only for it,** because the lobby carries a full BMAD
> install and qualifies the day it holds BMAD stories — the discriminator is *BMAD stories*, not
> project-vs-lobby. It stays `/cicd-*` because it does not *roam* the lobby: it follows the epic it was
> handed. See `.agents/commands/cicd-label-tasks.md` Step 0. Its `smh-` twin `/smh-label-tasks`
> varies the same way, for the same reason.
>
> ⛔ **This exception is CLOSED, not a precedent.** It is one named command with a derived, single
> target. A command that resolves its target by asking, by the active-project pointer, or by standing in
> a directory does not get the lobby — that is the ladder above, and it has no opt-out. Any future
> variance is another named line here, added deliberately; *"unless the command says otherwise"* would
> void the rule, since every command would then say otherwise.

## §STD — the standard ladder (default)

Walk the cases in order; the first match wins:

0. **Self (sub-project fast path — check FIRST, and STOP here if it matches)** — if this repo has **no**
   `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip straight to §BIND. Do NOT
   read `active-project.txt`, parse `$ARGUMENTS` for a project name, or ask which project — cases 1–3 are
   command-center-only (the lobby that hosts children under `Projects/`).
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is
   the target; consume that first token (the remainder is the real argument — story id, focus, …). Write
   the name alone into `.agents/active-project.txt` (overwrite) so later commands inherit it.
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under `Projects/`,
   use it.
3. **Ask** — else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* —
   never guess, never operate on the lobby.

Then set `PROJECT_ROOT = Projects/<name>` (or `.` on the fast path) and **echo exactly**
`Target: Projects/<name>` before any work.

## §ASK — the boot variant (`/cicd-boot-sprint-memory`)

Cases 0–1 as in §STD (boot's case 1 is the normal way to set the session's active project, e.g.
`/cicd-boot-sprint-memory AGY_AVIATIONCHAT`). But with no inline name (the usual case — most UIs fire `/`
the instant it's selected), do NOT silently reuse the pointer: read `.agents/active-project.txt`, list the
folders under `Projects/`, and ASK Daniel *"Active project is `<pointer, or none>`. Which project this
session?"* with that list. A plain confirmation keeps the pointer; otherwise write his choice into
`.agents/active-project.txt` (overwrite). If Daniel already named a project in this chat, treat that as his
answer — don't re-ask. Never guess, never operate on the lobby.

## §DUAL — the machine-switch variant (`/cicd-park` · `/cicd-resume`)

Two separate git repos are in play and BOTH are in scope:

1. **The lobby** — the repo you are standing in (`Sudo_Hatter_Command`): `_artifacts/`, `.agents/`, board
   sessions, open tasks.
2. **The active project** — read `.agents/active-project.txt`; set `PROJECT_ROOT = Projects/<name>`. Pointer
   missing → ASK which project, never guess. (**Fast path:** no `Projects/` subfolder → lobby and project
   are the same repo; do the project half only.)

Echo exactly `Parking: lobby + Projects/<name>` / `Resuming: lobby + Projects/<name>` before any git
command.

## §BIND — the binding rule (every variant, applies to EVERY step of the calling command)

Every "THIS repo", every `{project-root}`, and every bare path (`_bmad-output/…`, `_bmad/…`,
`_artifacts/…`, story files, test commands) resolves **under `PROJECT_ROOT`**, never the lobby. When the
command invokes any nested `bmad-*` / `1_*` skill, bind its `{project-root}` to `PROJECT_ROOT`, run it
against that directory, and read/write only there. A needed path missing under `PROJECT_ROOT` → **STOP and
say so — never fall back to the lobby.**

**Binding loads the project's law.** On binding `PROJECT_ROOT` — before any other step of the calling
command — read `PROJECT_ROOT/.agents/INDEX.md` and honor its `Load` column: floor rules immediately,
protocol rules before your first write in that project, on-demand rules on their triggers. In a
**converted** (thin, tier-2) project that INDEX routes the project's own `rules/` + `skills/`; if it is
missing there → **STOP and say so** — absence is a defect, never a default (full contract →
`project-law.md`). In a still-vendored project the file is the toolkit inventory — reading it costs one
small file and changes nothing. The self fast-path (case 0) binds the same obligation with
`PROJECT_ROOT = .`.
