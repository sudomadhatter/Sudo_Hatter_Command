# permissions — INDEX

The ONE terminal-approval source and its rendered outputs (SCC-378). Three agents fence terminal
commands here — Zoo Code, Claude Code, the Antigravity extension — with three different matchers; the
policy is one policy, so it is written once and rendered three ways. **Identical decisions, never
identical bytes.** Law and mechanics: [`docs/migrations/terminal-permissions-guide.md`](../../docs/migrations/terminal-permissions-guide.md).

| File | What it is | Who writes it |
|---|---|---|
| `families.json` | **The source.** One row per family — `id`, `cmd`, `why`, optional `only:`/`not:` platform scope, optional `render:` with a platform's exact rule text (the rows seeded from the pre-SCC-378 lists carry their historical spellings this way; a new row is DERIVED from `cmd` by each platform's grammar) | a human, or `/smh-llm-approvals` Step 3 — never a render |
| `antigravity.json` | **Rendered** — `userSettings.globalPermissionGrants` (`allow` / `deny`) for the Antigravity extension, pushed per machine by `antigravity_permissions_apply.py --apply` | `permission_render.py` only; a hand edit is drift |

The other two rendered outputs live where their platforms read them: `.vscode/settings.json`
(`zoo-code.allowedCommands` / `deniedCommands`) and `.claude/settings.json` (`permissions.allow`).
`python3 .agents/scripts/permission_render.py --check` is the drift test (`/smh-sync-agents -Status`
runs it); `tests/test_permission_parity.py` proves the three give the same verdict on one battery.
