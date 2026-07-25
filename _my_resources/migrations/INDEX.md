# _system — Home-Base System Builder

If what you need isn't here, GO BACK to the root `../router.md` / `../AGENTS.md`.

## MISSION
Maintain the Sudo_Hatter_Command routing system itself — add/convert workspaces, keep the master toolkit and
the lobby in sync, and keep `../router.md` current. This is the "system-builder agent": you mostly
talk to *this* workspace to grow the home base.

## TOOLS
- **`/new-project <name>`** → scaffold `Projects/<name>/` from `.agents/templates/project-template/`,
  register it in `../router.md`, add it to `../.gitignore`, and `git init` its own repo.
- **`/sync-agents [target]`** → push `.agents/{commands,skills,opencode-agents}` into a target's tool
  dirs (the lobby, or a project). Markdown only — never `node_modules`.

## RULES
- **Single source of authorship = `.agents/`.** Copies in `.claude/`, `.opencode/`, and per-project
  tool dirs are vendored by `/sync-agents` — never hand-edit a copy; edit the master and re-sync.
- **Lobby = categories only** (`../router.md`); detail lives in each workspace's `AGENTS.md`.
- **Adding a workspace must not require a central rebuild** — folder + `AGENTS.md` + one router row.
- **Don't break projects:** when converting a project, move it into `Projects/`, fix absolute paths
  (`pyrefly.toml`, `pyrightconfig.json`, IDE/user settings) and recreate its `.venv` (git-ignored).
