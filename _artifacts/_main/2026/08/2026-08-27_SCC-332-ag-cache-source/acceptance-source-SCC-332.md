Description: The Antigravity machine cache is sourced from .agents/commands/ (raw command bodies) instead of .agents/workflows/ (the thin launchers the sync generates for exactly this surface).

sync-agents.ps1 ~line 999 sets ONE source for BOTH global caches:
  $GlobalCmdSrc = Join-Path $Master "commands"
then feeds it to opencode AND antigravity. opencode wants raw commands; Antigravity must not have them.

MEASURED on main at 548e9b31:
  smh-update-maps-indexes.md   command 43,813 B | workflow 876 B | cache 43,813 B
  smh-quick-dev.md             command 31,554 B | workflow 860 B | cache 31,554 B
  cicd-dev-story-tests.md      command 28,426 B | workflow 873 B | cache 28,426 B

Antigravity TRUNCATES at 12,000 chars rather than rejecting, so from a project workspace the agent receives roughly the first 27% of smh-update-maps-indexes and improvises the rest - including past the Step 4 approval gate it never sees. That is the exact SCC-135 failure, still live on the global surface.

It also blows the SCC-195 menu budget: the cache carries FULL descriptions, not the 135-char cut ones.

And it is why smh-adviser-board is absent from the global menu: the emit filters .agents/commands/ by platforms:, and that command declares [claude, opencode, codex]. Its Antigravity door is the hand-owned .agents/workflows/smh-adviser-board.md, which the global emit never reads.

FIX: source the antigravity cache from .agents/workflows/, leaving opencode on .agents/commands/. Thin launchers everywhere, and hand-owned doors picked up for free.

DO NOT instead add antigravity to smh-adviser-board platforms: - the command is 14,732 B and would truncate.

TESTS TO ADD: no file in the Antigravity global cache exceeds the 12,000-char cap; every .agents/workflows door claiming antigravity has a cache twin.
