# <PROJECT> — workspace map  (Layer 2)

If what you need isn't here, GO BACK to the home-base root `../../router.md` (or `../../AGENTS.md`).

## MAP / MISSION / SUPPORT
- **MAP:** this workspace handles `<scope>`. Key folders: `<list them>`.
- **MISSION:** `<the process for this project, in order>`.
- **SUPPORT:** the shared toolkit is vendored at `.agents/` (rules · skills · commands) — load only what the routing table calls for.

## ALWAYS-LOAD (small)
Three tiers — only the first is actually always-on. `.agents/rules/INDEX.md`'s `Load` column states this
same classification; if the two disagree they are both wrong. A rule's frontmatter does **not** declare
its own load class.
- **FLOOR — every session:** `.agents/rules/operator-profile.md` (who you're talking to) +
  `.agents/rules/constitution.md` (hard stops) + `.agents/rules/karpathy-guidelines.md` (how to work).
- **PROTOCOL — load BEFORE the first tool call that creates, edits, or deletes a file** (if you are about
  to write and they are not loaded, stop and load them first): `.agents/rules/artifacts-always-first.md` ·
  `.agents/rules/000-PLAN-FIRST-GATE.md` · `.agents/rules/git-policy.md` ·
  `.agents/rules/worktree-per-story.md`. Conditional — but their LAW is also stated inline in this file
  (the ARTIFACTS section + the GATES below) and in the floor `constitution.md`, so the stop binds even in
  a session that never opens them.
- **ON-DEMAND — everything else**, per its trigger in `.agents/rules/INDEX.md`. Do not preload.
- Project-specific hard stops: `constitution.project.md` (create it only if this project needs any).
- **Web / mobile session (`CLAUDE_CODE_REMOTE=true`)?** Also load `.agents/rules/mobile-mode.md` (the
  web/mobile lane). It applies ONLY when that env var is `true`; on a desktop IDE session it's unset →
  ignore it and use the desktop defaults below. `mobile-mode.md` owns the trigger.

## GATES (consult before acting)
- **GIT — the dev standard is epic branches → `main`** (canonical → `.agents/rules/git-policy.md`
  § "Branch model"). `main` is LIVE PRODUCTION and the only long-lived branch — never work on it;
  each epic gets a short-lived `epic/<slug>` off `main`, story work flows `claude/*` worktree →
  epic branch, and the epic merges to `main` only via `/sudo-push-e2e` (full gate + Daniel's
  sign-off). On **web/mobile** (`CLAUDE_CODE_REMOTE=true`) git delivery mechanics →
  `.agents/rules/mobile-mode.md`. The push-approval hook (`.claude/hooks/`) gates `main`.
- **ROUTING + RISK:** confirm the target before touching files; never delete/overwrite/publish without an
  explicit go-ahead. Full hard stops → `.agents/rules/constitution.md`.

## ROUTING TABLE  (the most important thing — task → read these / skip these / skills)
| Task | Read these | Skip these | Skills |
|---|---|---|---|
| `<example task>` | `<spec/context files>` | `<unrelated dirs>` | `.agents/skills/<skill>/SKILL.md` |
| **"What's next" / open tasks / what's left** (Daniel's notes) | `_my_resources/open_tasks/` — `todo_list.md` + plan/PRP notes · **READ-ONLY** (never edit; cross-check vs live files) | — | — |

## NAMING / ARTIFACTS (project-local)
- Dated output `YYYY-MM-DD_<slug>.md`; versioned drafts `<slug>_v2.md` / `_final.md`.
- Artifacts are **project-local** — write into this repo's own `_artifacts/`: story → `<epic>/<story>/`; no home yet /
  random task → `_main/<YYYY-MM-DD>_<slug>/` (holding bucket — never dated at the root); retired → `_archived/`. Append a row to `_artifacts/INDEX.md` at close. Full model →
  `.agents/rules/artifacts-always-first.md`. This remains true when a chat starts outside the repository.

## PERSISTENCE
- "pick up" / "hand off" → project-local `_artifacts/` (dated session folders + `<epic>/<story>/` + `_archived/`),
  so history travels with the repo. There is no second home-base project bucket.
- **"pick up" also surfaces open tasks:** after the active-context brief, read `_my_resources/open_tasks/todo_list.md`
  (+ any plan/PRP `.md` notes there) and add a one-line "what's queued." **READ-ONLY** (Daniel's notes; never edit).
