---
name: windows-authored-code-hides-posix-bugs
description: "This toolkit was authored on Windows, so Windows-only assumptions sat green for months and only failed on the Mac — chmod semantics, hardcoded C:/ discovery paths, ';' PATH separators. Three found 2026-08-06; assume more."
metadata:
  node_type: memory
  type: project
---

Every repo here was written on Windows first. Windows-only assumptions therefore pass CI and local
runs indefinitely and surface **only** on the first POSIX machine — where they read as "the Mac is
broken" rather than "this code never ran anywhere else."

**Three found in one sweep (2026-08-06), all previously green on Windows:**

1. **`os.chmod` semantics.** `.agents/scripts/tests/test_story_status.py` restored a file with bare
   `stat.S_IWRITE` (0o200 = **write-only** on POSIX), then read it back. Windows `os.chmod` only
   toggles the read-only attribute, so the file stayed readable and the test passed; on macOS it
   raised `PermissionError` and took the **entire** `run_all.py` gate down with it. Fix:
   `stat.S_IREAD | stat.S_IWRITE`.
2. **Hardcoded Windows discovery paths.** Both emulator orchestrators
   (`frontend/e2e/run-e2e.mjs`, `backend/tests/e2e_emulator/run-emulator-e2e.mjs`) looked for Java
   ONLY in `C:/Program Files/Eclipse Adoptium`, then `process.exit(1)`. On any Mac the ONE e2e suite
   died before starting. Fix: a `process.platform === 'darwin'` branch probing
   `/usr/libexec/java_home -v 17` then the Homebrew prefixes.
3. **`;` as the PATH separator**, hardcoded in the same two files. Fix: `delimiter` from `node:path`.

**How to apply:** on any first-POSIX-machine setup, treat "this whole tier fails" as a portability
bug until proven otherwise — grep the failing path for `C:/`, `\\`, `.exe`, `;` PATH joins,
`Scripts/` vs `bin/`, and chmod constants. Fix the **master** `.agents/` copy first, then propagate
to the maintained projects ([[toolkit-sync-covers-agents-not-docs]]), and make the fix
platform-branching rather than Mac-only — the Windows machines still need their path.
Related: [[zshrc-is-invisible-to-automation]], [[powershell-console-fakes-mojibake]].
