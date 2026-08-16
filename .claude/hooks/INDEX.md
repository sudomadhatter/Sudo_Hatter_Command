# hooks — INDEX

PreToolUse/PostToolUse hooks (e.g. `require-push-approval.py`). MASTER here — mirrors to `.claude/hooks/` and project vendored copies via `/smh-sync-agents`.

⚠ **This is the Claude-only layer and nothing depends on it.** The `main` write gate is
`.githooks/pre-push` (pure `sh`, no interpreter) — see `.agents/rules/git-policy.md` § "The write
gate". These hooks prompt earlier and read better; if they die, the gate still holds. That
separation exists because every hook here was wired to `powershell`/`python` — neither of which
exists on the Mac — and exited 127 in silence for weeks (SCC-77).

## Top-level contents
<!-- auto-listed by /smh-update-maps-indexes — refresh via /smh-update-maps-indexes; do not hand-edit entries -->
- `guard-cwd-escape.py`
- `require-push-approval.py`
- `run-hook.sh`
- `session-start-context.sh`
