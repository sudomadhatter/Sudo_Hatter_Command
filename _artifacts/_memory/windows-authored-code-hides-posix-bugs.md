---
name: windows-authored-code-hides-posix-bugs
description: "This toolkit was authored on Windows, so Windows-only assumptions sat green for months and only failed on the Mac — chmod semantics, hardcoded C:/ discovery paths, ';' PATH separators, $env:USERPROFILE, robocopy, a path-separator mismatch that DELETED ~570 vendored files per project, bare `python` in ~29 DOC lines when only `python3` exists here, and the TRACKED git exec bit (100644 vs 100755) leaving 4 scripts/hooks silently inert on the Mac. Eight found 2026-08-06/08 and 2026-08-27; three printed SUCCESS while failing and one skipped hooks with only a hint."
metadata: 
  node_type: memory
  type: project
  originSessionId: ea1c7963-b655-4c4b-861f-0b832da17b1e
  modified: 2026-08-08T05:56:55.774Z
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

**And a SIXTH, the destructive one (2026-08-07)** — same file, and it deleted real work:

6. **`Get-VendorFileSet` emitted forward-slashed paths and compared them to the back-slashed TRACKED
   manifest.** `$_.FullName.Substring($root.Length).TrimStart('\')` cannot strip a leading `/`, so
   macOS produced `/commands/analyst.md` where Windows had written `commands\analyst.md`. **Zero
   overlap → `Invoke-ManifestPurge` concluded the master had dropped every file it ever owned and
   deleted the entire vendored toolkit — ~570 files per maintained project.** `Join-Path` then
   resolves back-slashed manifest paths fine on macOS, so all 349 deletes SUCCEEDED, and the run
   printed them as an ordinary `purged N retired vendor file(s)` line and exited 0. Because the
   vendored `.agents` is the SOURCE for each project's `.claude`/`.opencode` menus, the next step
   read the emptied dir and published **0 commands**. Fix: `[\\/](bmad|node_modules|__pycache__)[\\/]`
   for the excludes, and `TrimStart('\','/').Replace('/','\')` so every OS emits the back-slashed
   form the tracked manifest uses. (`$IsLobby`'s `TrimEnd('\')` had the same shape — fixed too.)

**A SEVENTH, in the DOCS rather than the code (2026-08-08)** — and it is the longest-lived:

7. **Bare `python` does not exist on this Mac** — not in automation, not in a login shell
   (`zsh -lic 'which python'` → not found). Only `python3` resolves. **~29 `.md` lines across
   `.agents/`, `docs/`, and `_my_resources/_quick_reference/` still instruct the reader to run
   `python .agents/scripts/…`** — every one is a broken instruction on the machine it is read on.
   The SOP quick-reference's copy was wrong twice over: `python … run_all.py — 94 checks` when the
   count was 98 (now 123 across 6 files, ~10 s). Fixed at the SOP doc, `.agents/scripts/INDEX.md`,
   `/update-maps-indexes`, and `run_all.py`'s docstring; **the rest are still stale.** Hooks and
   scripts should probe `python3 → python → py` rather than hardcode one name.

**An EIGHTH, and it is the quietest of all (2026-08-27, AVCH-91)** — the exec bit is TRACKED:

8. **Git stores the executable bit in the tree itself (`100644` vs `100755`), and Windows git cannot
   express it** — so a script or hook authored on the PC lands non-executable and is inert on every
   POSIX machine, while the PC leg's CI stays 100% green because Windows never consults the bit.
   Found four at once in AGY_AVIATIONCHAT: `scripts/tia_gate.sh` (its OWN usage block documents
   `./scripts/tia_gate.sh`, which died `permission denied`; its sibling `scripts/code-graph-update.sh`
   was already `100755`, so the odd-one-out was visible in `git ls-files -s scripts/`), plus
   `.githooks/post-checkout`, `post-merge` and `post-rewrite` — the AVCH-89 **memory-store regression
   hooks**, which had therefore never run on the Mac. **Git skips a non-executable hook with a HINT,
   not an error** (`hook was ignored because it's not set as executable`), and that hint scrolls past
   inside an unrelated command's output — so the whole gate stack reads as ARMED while doing nothing.
   That compounds [[vscode-hides-git-hook-output]]. **`chmod +x` alone does NOT stage the change** —
   the filesystem bit and the tracked bit are separate; you must
   `git update-index --chmod=+x <path>` (a correct mode-only fix commits as
   `N files changed, 0 insertions(+), 0 deletions(-)` with every blob SHA unchanged).

**The rule this forces: a comparison against a TRACKED, cross-machine artifact is a portability
surface.** Separator normalisation is not cosmetic there — it decides whether a purge is a no-op or
a wipe. Anything of the form "delete what is in the manifest but not in the fresh scan" must
normalise BOTH sides before comparing, and should refuse to run when the diff is implausibly large
(a purge proposing ~100% of the manifest is a bug, not a cleanup). **Always `-WhatIf` a sync on a new
platform before letting it write.**

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
success messages. **And treat every documented command as code**: paste it into a shell before
writing it down — a doc line is the one "call site" no test ever executes.
**Audit for it with `git ls-files -s .githooks/ scripts/`** whenever you land on a new POSIX
machine — every shebanged file should read `100755`.
Related: [[zshrc-is-invisible-to-automation]], [[powershell-console-fakes-mojibake]],
[[sop-doc-currency-gate]].
