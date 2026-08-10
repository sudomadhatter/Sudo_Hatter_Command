# System Builder — maintaining the home base itself

Pointer target from the root `AGENTS.md` / `router.md`. Read this when the work is about growing or
maintaining the Sudo_Hatter_Command routing system, not about a project inside it.

If what you need isn't here, GO BACK to the root `../router.md` / `../AGENTS.md`.

> Was `_system/AGENTS.md` until 2026-07-25. `_system/` was dissolved — it held only this doc plus the
> new-machine migration kit, which now lives in `_my_resources/migrations/`.

## MISSION
Maintain the Sudo_Hatter_Command routing system itself — add/convert workspaces, keep the master toolkit and
the lobby in sync, and keep `../router.md` current. This is the "system-builder agent": you mostly
talk to *this* workspace to grow the home base.

## TOOLS
- **`/smh-new-project <name>`** → scaffold `Projects/<name>/` by cloning the thin skeleton repo
  (`sudomadhatter/sudo-project-skeleton` — no vendored toolkit; see `.agents/rules/project-law.md`),
  register it in `../router.md`, add it to `../.gitignore`, and `git init` its own repo.
- **`/smh-sync-agents [target]`** → push `.agents/{commands,skills,opencode-agents}` into a target's tool
  dirs (the lobby, or a project). Markdown only — never `node_modules`.
- **`_my_resources/migrations/rename-fix.ps1`** → rename-day restructure: move projects into
  `Projects/` and repair every absolute-path reference in one pass. Dry-run by default; `-Apply`
  to write. Details → `_my_resources/migrations/INDEX.md`.

## RULES
- **Single source of authorship = `.agents/`.** Copies in `.claude/`, `.opencode/`, and per-project
  tool dirs are vendored by `/smh-sync-agents` — never hand-edit a copy; edit the master and re-sync.
- **Lobby = categories only** (`../router.md`); detail lives in each workspace's `AGENTS.md`.
- **Adding a workspace must not require a central rebuild** — folder + `AGENTS.md` + one router row.
- **Don't break projects:** when converting a project, move it into `Projects/`, fix absolute paths
  (`pyrefly.toml`, `pyrightconfig.json`, IDE/user settings) and recreate its `.venv` (git-ignored).

## RELATED
- New-machine setup / secrets restore → `_my_resources/migrations/env-migration-guide.md`
- Workspace shape + health rules → `docs/workspace-standard.md`
- Navigation index → `docs/repo-map.md`
