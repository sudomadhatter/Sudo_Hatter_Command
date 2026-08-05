# MASTER ROUTER — sudo-command-center (the map)

You are in the LOBBY. This table is the directory: pick the workspace, then read **its** `AGENTS.md`.
Lobby = categories only; detail lives on each floor. If a request isn't listed here, **ASK — don't guess.**
Any workspace may send you BACK here ("if not here, go to root router").

> **Note:** all projects live under `Projects/`, each keeping its own git repo. "Converted" = the
> project has pointer `CLAUDE.md`/`GEMINI.md` + a workspace `AGENTS.md` (Layer-2 map) + vendored `.agents/`.

## Artifact ownership

**Default:** every current or future directory under `Projects/` owns its artifacts in its own
`Projects/<name>/_artifacts/`, regardless of where the chat starts or which agent/tool runs it.

**Sudo-managed exception registry:** *(empty)*

Every project follows the project-owned default. Adding an exception requires an explicit edit to this
registry — never infer one.

## The routing table

**This table is empty on purpose.** A fresh command center routes nowhere yet. You add one row per
project as you create it, and the row is what lets an agent find the right workspace without reading
the whole tree.

| If the work is about… | Go to | Read first | Status |
|---|---|---|---|
| Maintaining THIS home-base system | `docs/` | `docs/workspace-standard.md` | active |
| *(your first project — add a row here)* | `Projects/<name>/` | its `AGENTS.md` | — |

### Adding your first row

Clone the project skeleton (see `/sudo-tour` stop 2), then add a row describing **the kind of work**,
not the technology. An agent matches on the work: *"aviation ground-school app"* routes better than
*"FastAPI service"*, because the question arriving is *"fix the lesson quiz"*, never *"fix the FastAPI."*

Keep the row's **Status** honest — `pending`, `active`, `converted` — because it tells the next agent
how much of the standard it can assume is already in place.
