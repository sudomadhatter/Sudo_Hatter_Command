# <PROJECT> — workspace map  (Layer 2)

If what you need isn't here, GO BACK to the home-base root `../../router.md` (or `../../AGENTS.md`).

## MAP / MISSION / SUPPORT
- **MAP:** this workspace handles `<scope>`. Key folders: `<list them>`.
- **MISSION:** `<the process for this project, in order>`.
- **SUPPORT:** the shared toolkit is vendored at `.agents/` (rules · skills · commands) — load only what the routing table calls for.

## ALWAYS-LOAD (small)
- `.agents/rules/constitution.md` + `.agents/rules/karpathy-guidelines.md`.
- Project-specific hard stops: `constitution.project.md` (create it only if this project needs any).
- **Web / mobile session (`CLAUDE_CODE_REMOTE=true`)?** Also load `.agents/rules/mobile-mode.md` (the
  web/mobile lane). It applies ONLY when that env var is `true`; on a desktop IDE session it's unset →
  ignore it and use the desktop defaults below. `mobile-mode.md` owns the trigger.

## GATES (consult before acting)
- **GIT — the dev standard is `main_debug` → `main`** (canonical → `.agents/rules/git-policy.md` § "Branch
  model"). `main` is LIVE PRODUCTION — never work on it; all dev flows `claude/*` → PR → **`main_debug`**;
  promoting to `main` is Daniel's deliberate manual call. **Desktop default:** agents **never** run
  `git commit`/`push` themselves unless Daniel delegates it in the moment. On **web/mobile**
  (`CLAUDE_CODE_REMOTE=true`) the agent owns git delivery instead → `.agents/rules/mobile-mode.md`. The
  push-approval hook (`.claude/hooks/`) gates `main_debug`/`main`.
- **ROUTING + RISK:** confirm the target before touching files; never delete/overwrite/publish without an
  explicit go-ahead. Full hard stops → `.agents/rules/constitution.md`.

## ROUTING TABLE  (the most important thing — task → read these / skip these / skills)
| Task | Read these | Skip these | Skills |
|---|---|---|---|
| `<example task>` | `<spec/context files>` | `<unrelated dirs>` | `.agents/skills/<skill>/SKILL.md` |
| **"What's next" / open tasks / what's left** (Daniel's notes) | `_my_resources/open_tasks/` — `todo_list.md` + plan/PRP notes · **READ-ONLY** (never edit; cross-check vs live files) | — | — |

## NAMING / ARTIFACTS (project-local)
- Dated output `YYYY-MM-DD_<slug>.md`; versioned drafts `<slug>_v2.md` / `_final.md`.
- Artifacts are **project-local** — write into this repo's own `_artifacts/`: random task → `<YYYY-MM-DD>_<slug>/`,
  story → `<epic>/<story>/`, retired → `_archived/`. Append a row to `_artifacts/INDEX.md` at close. Full model →
  `../../AGENTS.md` §5 + `.agents/rules/artifacts-always-first.md`.

## PERSISTENCE
- "pick up" / "hand off" → project-local `_artifacts/` (dated session folders + `<epic>/<story>/` + `_archived/`),
  so history travels with the repo. Sessions run *from the home base* instead land in `../../_artifacts/<PROJECT>/`
  — check **both** to reconstruct full history.
- **"pick up" also surfaces open tasks:** after the active-context brief, read `_my_resources/open_tasks/todo_list.md`
  (+ any plan/PRP `.md` notes there) and add a one-line "what's queued." **READ-ONLY** (Daniel's notes; never edit).
