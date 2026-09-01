---
name: mac-authored-code-hides-windows-bugs
description: "The MIRROR of windows-authored-code-hides-posix-bugs: the enforcement suite was written on the Mac, so 18/61 files were red on the PC and EIGHT live defects sat in shipped code — every cd refused, a gate that never judged, a sweep that left live mutants. The rule: fork BEHAVIOUR, converge DATA — and gate every separator rewrite to Windows."
metadata: 
  node_type: memory
  type: project
  originSessionId: b93ad8ff-4583-4d2c-96b3-58f746f45e90
  modified: 2026-08-25T18:31:32.886Z
---

`.agents/scripts/tests/` was authored on the Mac and the PC never drove it, so nothing forced the
portability question. SCC-321 (2026-08-25) took it from **43/61 to 61/61** on Windows. This is the
mirror of [[windows-authored-code-hides-posix-bugs]] and the classes are completely different.

**The two root causes that explained most of it — neither was in my first triage:**

1. **Text mode translates newlines on Windows, at TWO seams.** `Path.write_text("x\n")` writes
   `x\r\n`, and `subprocess.run(text=True, input="x\n")` sends `x\r\n` (the child's stdin is a
   `TextIOWrapper` with `newline=None`). Invisible at the call site because `read_text()` translates
   back. A POSIX consumer then sees `minted=1756…\r` → *"not a number"*; `#!/bin/sh\r` → an
   interpreter that does not exist. **One error message printed two values that looked IDENTICAL**
   because a carriage return only moves the cursor — diagnosing from the message is guaranteed wrong.
2. **A stub binary Windows cannot see or launch.** `shutil.which` resolves through `PATHEXT`, so an
   extensionless fixture is never FOUND; and a shebang is a POSIX kernel convention, so it cannot be
   LAUNCHED. Two files ran **zero cases** because of it.

**Other Windows facts, all measured:**

- `d / "C:"` **is `d`** — pathlib reads a bare drive letter as a DRIVE, so the join collapses.
  `shutil.rmtree(d / "C:", ignore_errors=True)` deleted the whole fixture repo, silently. Build such
  a path from ONE string (`Path(f"{d}{os.sep}C:")`); the collapse is a rule about *joining*.
- `C:\Git\bin\sh.exe` **rewrites the env it is given** and puts its own `/mingw64/bin` FIRST, so an
  `env=`-injected PATH shim always loses. Set `$PATH` *inside* the started shell instead.
- A POSIX `$PATH` is colon-separated, so `C:/x` is **two** entries. Use `/c/x`.
- `CreateProcess` appends **`.exe` and only `.exe`** — it never consults `PATHEXT` (that is
  `cmd.exe`'s behaviour). So a `.cmd` shim is unreachable from `subprocess.run(["git", …])`.
- `bash` on PATH is `System32\bash.exe`, the **WSL launcher**, which sees the drive as `/mnt/c` and
  cannot read a `C:\` argument. Derive Git Bash from `git --exec-path` instead.
- `chmod(0o555)` **does** hold (writes raise `PermissionError`), but `stat().st_mode & 0o111` is
  False for `.sh` — CPython sets exec bits only for `.exe/.bat/.cmd/.com`. A freeze keyed on the exec
  bit therefore freezes **nothing**. Ask about writability (`& 0o222 == 0`), not an exact mode.
- `SIGTERM` is **never delivered** — `signal.signal` accepts it, so the code reads as covered, but a
  terminate goes through `TerminateProcess` and no handler or `finally` runs. `SIGBREAK`
  (`CTRL_BREAK_EVENT` + `CREATE_NEW_PROCESS_GROUP`) is the one interruption that IS deliverable.
- A directory **cannot be deleted while a process has it as cwd**, and `proc.kill()` misses
  grandchildren → `PermissionError [WinError 32]`. Use `taskkill /T /F`.
- `:` is **illegal in a filename** (NTFS alternate data stream). `ntpath.expanduser` reads
  `USERPROFILE` FIRST, so setting `HOME` alone does not move `~`.
- `git config` **escapes backslashes** in a value: the URL is stored `C:\\Users\\…`. A `str(root)`
  search matches none of it.
- `text=True` without `encoding=` decodes with the **locale** (cp1252), while git writes UTF-8 —
  pin `encoding="utf-8"` AND `PYTHONIOENCODING=utf-8`, because pinning one side breaks the other.

**Why:** eight of these were defects in *shipped* code, not tests, and every one was silent — the cwd
guard refused **every `cd`** on the PC (and `ask` is auto-DENY headless); `main_write_gate` **never
judged** a lane with a non-ASCII path; `mutation_sweep` left **live mutants** on an interrupt, which
is verbatim the SCC-144 incident it exists to prevent. A suite nobody runs on a machine is not
protecting that machine.

**⛔ A SUITE GREEN IS SCOPED TO THE SHELL *AND* THE CHECKOUT IT RAN IN (SCC-338, 2026-09-01).**
The same tree, same commit, four different answers: worktree+Git Bash **71/71**, main+Git Bash
**69/71**, main+PowerShell **68/71**. Three separate causes, and I reported the wrong one twice
before getting it right.
- **Shell:** `subprocess.run(cmd, shell=True)` on Windows is **cmd.exe**, which never expands
  `$VAR`; and `sh` is on PATH under Git Bash but **NOT under PowerShell**, so `["sh","-c",cmd]`
  dies `FileNotFoundError [WinError 2]` in the shell the operator actually uses. **Probe** for a
  POSIX shell, and derive the fallback from `shutil.which("git")` — Git for Windows ships `sh.exe`
  beside it. Never name an install dir (this PC keeps Git at `C:/Git`, not `C:/Program Files/Git`).
  The registered hook string's own first word is `sh`, so the CHILD must resolve it too: prepend the
  resolved shell's dir to the child's PATH.
- **Checkout:** a worktree has no `Projects/` (gitignored), so scans that crash in the main checkout
  pass there. A **Windows long-path** `FileNotFoundError [WinError 3]` past `MAX_PATH` — a torch
  `dist-info/licenses` tree inside a project worktree's `.venv` — kills a whole gate in main and is
  invisible from a lane.
- **A test that says it SKIPPED is not a pass.** `CS-18 L` prints *"This is a SKIP, not a pass about
  the cache; the claim binds in main"* — and I closed SCC-338 on a 29/29 that contained it. Read the
  per-case text, never the tally. [[suite-red-file-may-have-run-nothing]]

**How to apply:** **fork BEHAVIOUR, converge DATA.** Fork where the platforms genuinely differ (uid
roots, `PATHEXT`, drive letters, junction-vs-symlink, `:` in a filename) — two arms, both asserting
something real, neither a skip. Converge where the divergence was accidental (line endings, stdin
translation, printed separators): the Mac was already right, and forking would preserve the bug at
every reader forever. ⛔ **Gate every separator rewrite to `os.name == "nt"`** — on POSIX a backslash
is a legal FILENAME character, so `p.replace("\\","/")` there is not a separator fix but a path
rewrite, and it widens a containment guard (`/ws\x` is a sibling file at `/`, not `/ws/x`). And when
a lesson gets fixed, **carry it to the sibling copies**: "absolute has two spellings" (SCC-171/172)
and "`encoding="utf-8"` is load-bearing" (SCC-160) both recurred here in helpers that never got the
fix. Related: [[two-machines-mac-and-pc]], [[suite-red-file-may-have-run-nothing]],
[[test-certification-at-shipping-sha]].
