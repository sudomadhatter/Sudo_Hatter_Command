---
name: hook-background-work-gets-sigterm
description: "Claude Code SIGTERMs a hook's process group ~15 ms after the hook shell exits; anything backgrounded (curl &, a detached subshell mid-python) dies. Survive with trap '' TERM inside a detached subshell (setsid is Linux-only)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43de34ca-a9ce-48d3-9400-509bcdca5db2
  modified: 2026-09-02T18:23:02.069Z
---

Measured 2026-09-02 on Ubuntu (WSL2), Claude Code 2.1.x, SCC-376: about 15 ms after a hook's shell
exits, Claude sends SIGTERM to the hook's process group. A `curl … &` at the end of a notifier, or a
`( … ) &` subshell still running python3, dies with it. The Mac's original `notify.sh` had exactly
that shape, so its phone push could be lost while its foreground banner always landed.

**Why:** hooks are killed as a tree on completion, not just on timeout. `async: true` does not change
it. A traced detached body caught the TERM 16 ms after start (its python3 exited 143) and only
finished because it trapped the signal; a `setsid` twin was never signalled, but macOS has no `setsid`.

**How to apply:** in any hook that must outlive its shell, read stdin in the foreground, then run the
body as `( trap '' TERM HUP INT; … ) >/dev/null 2>&1 </dev/null &` and `exit 0`. SIG_IGN is inherited
across exec, so python3 and curl inside survive too, and the hook returns instantly whether async or
not. Proof lives in the SCC-376 plan (Phase 3, "the Mac is optimised by the SAME file"). Related:
[[claude-notifications-hook-schema-and-ntfy]], [[interactive-startup-files-are-invisible-to-automation]].
