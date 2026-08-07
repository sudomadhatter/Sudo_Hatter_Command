---
name: windows-authored-code-hides-posix-bugs
description: "This toolkit was authored on Windows, so Windows-only assumptions sat green for months and only failed on the Mac — chmod semantics, hardcoded C:/ discovery paths, ';' PATH separators, $env:USERPROFILE, robocopy. Five found 2026-08-06; assume more, and note two of them printed SUCCESS first."
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

**Two more in `sync-agents.ps1` itself, and these are the instructive ones — both failed AFTER the
run had already printed success lines**, so the sync looked like it worked (2026-08-06):

4. **`$env:USERPROFILE` is `$null` off Windows**, and `Join-Path $null …` *throws*. It killed the
   whole machine-global stage — opencode + Antigravity + Codex prompts + Codex skills — but only
   after the local sync had printed its `-> 47 cmds` counts. Fix: resolve `$UserHome` once from
   `USERPROFILE ?? HOME ?? GetFolderPath('UserProfile')`.
5. **`robocopy` does not exist off Windows.** The codex-skills mirror died having created exactly
   **one** skill directory — a half-built cache that reads as deliberate, not as a crash. Fix: keep
   robocopy on Windows verbatim, PowerShell-native `Copy-Tree` elsewhere.

Two things that are *not* bugs, so don't "fix" them: pwsh 7's `Join-Path` **normalises** a `\` in a
path literal to `/` on Unix, so the ~20 `".claude\commands"`-style joins are fine; and the manifest
KEYS stay back-slashed deliberately (dictionary keys, not paths — they must match across machines).
What did need fixing there was `ConvertTo-Json`: 5.1 writes a BOM and its own spacing, pwsh 7 writes
neither, so a tracked generated file rewrites entirely on the other machine. Hand-emit canonical
bytes for anything generated **and** tracked.

**How to apply:** on any first-POSIX-machine setup, treat "this whole tier fails" as a portability
bug until proven otherwise — grep the failing path for `C:/`, `\\`, `.exe`, `;` PATH joins,
`Scripts/` vs `bin/`, chmod constants, `USERPROFILE`, and `robocopy`/`cmd`/`xcopy`. Fix the
**master** `.agents/` copy first, then propagate to the maintained projects
([[toolkit-sync-covers-agents-not-docs]]), and make the fix platform-branching rather than Mac-only
— the Windows machines still need their path. **Read the WHOLE output, never the last line**: a
Windows-only call site fails at the point it is reached, which is routinely after several honest
success messages.
Related: [[zshrc-is-invisible-to-automation]], [[powershell-console-fakes-mojibake]].
