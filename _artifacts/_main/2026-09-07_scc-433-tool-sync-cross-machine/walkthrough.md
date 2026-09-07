# SCC-433 — Cross-machine tool connections & Keyway MCP sync documentation

Authoritative documentation for cross-machine tool connections, MCP server synchronization, and Keyway credential flow across Mac, PC/WSL2, and Linux environments.

## Task Checklist
- [x] **Add Step 6d to [`docs/migrations/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/migrations/INDEX.md)**: Added Step 6d to the ordered machine setup matrix detailing platform MCP configuration generation (`tool_sync.py --apply`) following `keyway pull`.
- [x] **Update [`docs/migrations/install_guides/machine_setup_card.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/migrations/install_guides/machine_setup_card.md)**: Added Tool & MCP configs row to §3 and added `tool_sync.py --check` verification command to §4.
- [x] **Add Section 11 to [`docs/_scc_sops_prds/sharing_keys_secrets_secure.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/sharing_keys_secrets_secure.md)**: Documented the end-to-end secrets bridge architecture (Keyway cloud vault -> `.env` -> git worktree symlinks via `link-worktree-assets.py` -> `connections.json` -> multi-platform MCP outputs) and updated Quick Reference.
- [x] **Cross-Machine Quick Reference in [`docs/_scc_sops_prds/workflows_testing_SOP.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md)**: Confirmed that Tool & MCP connections restoration and verification flow is current.
- [x] **Update [`_artifacts/_main/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/_artifacts/_main/INDEX.md)**: Added session row for `2026-09-07_scc-433-tool-sync-cross-machine/`.

## Evidence
1. **Migrations Kit Verification**:
   - [`docs/migrations/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/migrations/INDEX.md) Step 6d provides clear platform-specific instructions for generating MCP configs across Windows, macOS, and Linux/WSL2 without hardcoded paths.
   - [`docs/migrations/install_guides/machine_setup_card.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/migrations/install_guides/machine_setup_card.md) documents that git worktrees receive credentials automatically via `link-worktree-assets.py`.
2. **Keyway & Tool Sync Integration**:
   - [`docs/_scc_sops_prds/sharing_keys_secrets_secure.md`](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/sharing_keys_secrets_secure.md) Section 11 outlines how `${SENTRY_AUTH_TOKEN}` and other credentials travel in the Keyway encrypted vault, resolve locally into `.env`, and populate MCP configs at runtime.

## Suite Ledger
- `test_check_maps.py`: 37/37 passed
- `test_tool_sync.py`: 12/12 passed
- `check_maps.py --depth3-only --strict`: clean (0 drift)
- `workflow_lint.py --toolkit-only`: 0 errors
- `check_links.py --base origin/main`: 0 broken links

## Your Actions
No manual action required.
