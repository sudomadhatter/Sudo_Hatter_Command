"""Shared plumbing for the workflow-script tests.

Stdlib only and no pytest, matching the scripts under test — these have to run on a fresh
machine before anything is installed, which is exactly when the workflow scripts get used.
"""
from __future__ import annotations

import contextlib
import functools
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

# ⛔ THE SUITE'S OWN CASE NAMES CONTAIN `⛔` AND `⭐`, AND cp1252 CANNOT ENCODE EITHER (SCC-321).
# Windows gives a NON-CONSOLE stdout - a pipe, a redirect, `run_all.py`'s child - the locale
# codec, so `check()` raises UnicodeEncodeError mid-print and the file dies part-run. Nothing
# distinguishes that from an ordinary red, so it reads as a test failure about the code.
# `run_all.py` pins its children through the environment; this pins the OTHER door - the single
# file run by hand or by `mutation_sweep.py`, which never passes through the runner at all.
# Windows-only: POSIX streams are already UTF-8, so the Mac is byte-identical.
if os.name == "nt":  # pragma: no cover - platform branch
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")


def _tree_guard() -> None:
    """SCC-190's wrong-tree refusal, at the one chokepoint every test file passes through.

    ⛔ WHY HERE AND NOT ONLY IN `run_all.py` (SCC-240). Sibling lanes live in
    `.claude/worktrees/<slug>/`, each a full checkout with its own copy of these files, and a
    shell's cwd silently resets to the MAIN checkout. `run_all.py` refused that shape since
    SCC-190 - and every SINGLE-FILE run (`python3 tests/test_x.py --case …`, which is the
    review loop and the only way `mutation_sweep.py` runs a test) walked straight past it.
    Measured in the lane that closed this: a block edited in the worktree, `47/47 passed`
    recorded against `main`, and the only tell an unrelated `matched 0/0 blocks` line. A
    wrong-tree pass is byte-identical to a right-tree pass in every transcript.

    Refuses with EXIT 2 - not 1 (a real failure) and not 3 (an empty filter) - and prints no
    `FAILED:` line, which is exactly the shape `mutation_sweep.judge()` refuses to score, so a
    wrong-tree refusal can never be recorded as a kill.

    Two overrides, both meaning "I know this is main": `--on-main` on the command line (the
    hand-typed door - identical on zsh and PowerShell, which an env var is not), and
    `WF_ON_MAIN` in the environment (how `run_all --on-main` reaches its children).

    ⛔ DEGRADES TO SILENCE, never takes a suite down - the constraint `run_all.py` documents
    for itself: this file is copied bare into temp dirs by its own tests, where `wf_common`
    and git are both absent. A harness that refuses to start is a worse defect than the one
    this guard exists to prevent. On an allowed run it prints ONE line naming the tree, so
    even a permitted single-file run states what it measured.
    """
    if "--on-main" in sys.argv[1:] or os.environ.get("WF_ON_MAIN"):
        return
    try:
        import wf_common as wf
        tag = wf.tree_tag(SCRIPTS)
        refusal = wf.tree_guard(SCRIPTS, who=Path(sys.argv[0]).name or "test", tag=tag)
    except Exception:   # noqa: BLE001 - no helper, no git, no guard; never "no suite"
        return
    if refusal:
        print(refusal, file=sys.stderr)
        sys.exit(2)
    top, br, is_main = tag
    print(f"-- tree: {Path(top).name} [{br or 'DETACHED'}] - "
          f"{'MAIN CHECKOUT' if is_main else 'worktree'} --")


def _write_text_lf() -> bool:
    """Make `Path.write_text` emit LF on Windows, as it already does on the Mac (SCC-321).

    ⛔⛔ THIS IS THE SINGLE ROOT CAUSE OF MOST OF THIS SUITE'S WINDOWS FAILURES, AND IT IS
    INVISIBLE AT EVERY CALL SITE. Python's text mode translates `\\n` to `os.linesep` on write,
    so on Windows `p.write_text("minted=1756143820\\n")` puts `minted=1756143820\\r\\n` on disk.
    The fixture LOOKS right in every editor and in `read_text()`, which translates back. Then a
    POSIX consumer reads the field as `1756143820\\r`:

        `$(( minted ))`  -> "the approval token's timestamp is not a number"   (the main write gate)
        `#!/bin/sh\\r`    -> shebang names an interpreter that does not exist   (any written script)
        `grep -x val`    -> no match, because the line ends in a carriage return

    Every one of those reads as a REAL failure of the thing under test. The main write gate's
    behavioural half failed 16 cases this way, and the diagnosis for each looked like a
    different bug.

    ⭐ WHY PATCH THE SEAM AND NOT 482 CALL SITES. This directory has 482 `write_text` calls
    across 49 files. Every one of them is writing a fixture for a POSIX consumer, and every one
    of them wants LF — there is no call site here that wants CRLF, because THE MAC HAS NEVER
    WRITTEN ONE and the suite is green there. So this does not introduce a behaviour: it deletes
    a platform divergence nobody chose, and makes the two machines write byte-identical
    fixtures. Patching call sites instead would be 482 edits that the 483rd would undo.

    Scoped deliberately: the test process only, writes only, and `newline=` still wins if a
    caller passes it explicitly. `_harness` is the seam every file in this directory imports,
    which is why it goes here and not in a file someone can forget to import.

    Returns whether the patch was applied, so `test_suite_runner` can assert it is live — a
    silent seam that silently stops working is the failure mode this whole suite exists to
    catch.
    """
    if os.name != "nt":
        return False                          # POSIX already writes LF; nothing to correct

    original = Path.write_text

    @functools.wraps(original)
    def write_text(self, data, encoding=None, errors=None, newline=None):
        return original(self, data, encoding=encoding, errors=errors,
                        newline="\n" if newline is None else newline)

    Path.write_text = write_text               # type: ignore[method-assign]
    return True


WRITES_LF = _write_text_lf()
"""True when `Path.write_text` has been corrected to emit LF (Windows only) — see above."""


NO_MATCH = 3
"""Exit code for a filter that selected NOTHING to run (SCC-156).

Distinct from 1 on purpose. A mutation sweep reads a non-zero exit as "the mutant was
killed" and a zero as "it survived" — so a typo'd `--case` label, a file that declares no
blocks, or a block that matches and asserts nothing must be neither. They are an error in
the SWEEP, not evidence about the code, and 3 is what says so.
"""


def _case_filter() -> str | None:
    """`--case <substring>` / `--case=<substring>`, read straight off argv.

    No argparse: these files are run bare by the sweep, by run_all and by hand, and an
    arg parser that rejects an unknown flag would turn a harmless extra argument into a
    dead suite. Anything that is not --case is ignored.

    ⛔ A `--case` WITH NO VALUE RETURNS `""`, NOT `None`, AND THE TWO MEAN OPPOSITE THINGS.
    `None` is "no filter was asked for" — run everything. `""` is "a filter was asked for and
    its label was LOST", which is the same error class as a typo and must reach `NO_MATCH`.
    The first cut returned `None` for a bare trailing `--case`, so the sweep ran the whole
    file, printed no filter line, and exited 0/1; `--case ""` and `--case=` were worse, since
    `"" in label` is true for every label, so every block ran under a note claiming
    `matched N/N`. Either way a mutant that dies to ANY case in the file is recorded as
    killed by a named case that never ran alone. All five review lenses found this.
    """
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        # `.strip()` HERE, once: a whitespace-only value (`--case " "`, a variable holding a
        # blank) is a lost label, not a filter that matches every block - which is exactly
        # what `" " in label` would have made it (SCC-160 review, Blind Hunter).
        if a == "--case":
            return argv[i + 1].strip() if i + 1 < len(argv) else ""
        if a.startswith("--case="):
            return a.split("=", 1)[1].strip()
    return None


class Cases:
    def __init__(self, title: str) -> None:
        self.title = title
        self.rows: list[tuple[str, bool, str]] = []
        self.filter = _case_filter()
        self.blocks_seen = 0
        self.blocks_run = 0
        # Every label that MATCHED, in file order — the transcript names them all, so a
        # mutation record can never say "killed by case P" when 22 blocks ran (SCC-156 #1).
        self.blocks_matched: list[str] = []
        # ⛔ TITLE FIRST, GUARD SECOND. `mutation_sweep.py` and `run_all.py` read the
        # `FAILED:` and `-- n/m passed --` lines; the title line is matched by eye, and a
        # reader scanning for `== <name> ==` must still find it unchanged and first.
        print(f"== {title} ==")
        _tree_guard()

    def block(self, label: str) -> bool:
        """Guard for one named block of cases: `if c.block("B · the target"): ...`

        ⛔ An `if`, never a context manager. These files are written as sequential inline
        `with TempDir():` blocks rather than functions, and a context manager cannot skip
        its own body — `__enter__` returning False still runs everything under it. The
        truthiness of a plain call is the only thing that can.

        Unfiltered, every block runs and this is always True, so a file reads and behaves
        exactly as it did before it was wired.
        """
        self.blocks_seen += 1
        if self.filter is None:                       # no filter asked for: run everything
            self.blocks_run += 1
            return True
        if self.filter and self._matches(label):
            self.blocks_run += 1
            self.blocks_matched.append(label)
            return True
        # An EMPTY filter is a lost label, never "matches everything". Falling through here
        # leaves blocks_run at 0, which finish() turns into NO_MATCH.
        return False

    def _matches(self, label: str) -> bool:
        """Substring, case-insensitive, whitespace-trimmed — and every match is RECORDED.

        The over-match is real (SCC-156 review #1: `--case "E"` on a 40-block file ran all
        40 and the sweep recorded "killed by case E"). The fix is not an exact-match mode —
        a family prefix like `CASE ·` is a legitimate multi-select — it is that a
        multi-match can never be INVISIBLE: `finish()` prints every matched label, so the
        attribution reads the names, never the count.
        """
        return self.filter.lower() in label.strip().lower()

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        self.rows.append((name, bool(ok), detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))

    def finish(self) -> int:
        failed = [n for n, ok, _ in self.rows if not ok]
        print(f"-- {len(self.rows) - len(failed)}/{len(self.rows)} passed --")
        if failed:
            print("FAILED: " + ", ".join(failed))
        if self.filter is not None:
            print(f"-- filter '{self.filter}': matched "
                  f"{self.blocks_run}/{self.blocks_seen} blocks --")
            if self.blocks_run > 1:
                # A multi-match is legal (a family prefix like `CASE ·`) but it must be
                # VISIBLE: attribution reads this line, not the count. Labels carry `⛔`/`⭐`
                # and this is the first time they are PRINTED - on a cp1252 pipe (the PC) a
                # raw print raises AFTER the rows, exit 1, and a sweep reads "killed" for a
                # mutant that survived. Encode for the stream, escaping what it cannot hold.
                line = "-- matched blocks: " + " | ".join(self.blocks_matched) + " --"
                enc = getattr(sys.stdout, "encoding", None) or "utf-8"
                print(line.encode(enc, "backslashreplace").decode(enc))
            if not self.blocks_run or not self.rows:
                if not self.filter:
                    why = ("--case was given no label (a bare `--case`, `--case=`, or an "
                           "empty value — a shell variable that vanished)")
                elif not self.blocks_run:
                    why = "no block matched"
                else:
                    why = "the matched block ran no cases"
                print(f"NO CASES RAN: {why} — this is a filter error, not a result.")
                return NO_MATCH
        return 1 if failed else 0


def utf8_env(**extra: str) -> dict:
    """`os.environ` with the child's text encoding PINNED to UTF-8 (SCC-321).

    ⛔ `text=True` WITHOUT `encoding=` DECODES WITH THE LOCALE, and on Windows that is `cp1252`
    while the child writes UTF-8 — so `·` came back as `Â·` and any case comparing a label
    containing a non-ASCII character failed on a string that was never wrong, only mis-decoded.

    Pinning ONE side is not enough, and that is the subtle half: a child left on the locale
    writes `cp1252`, and a parent hard-coded to UTF-8 then mis-decodes in the opposite
    direction. Both ends are pinned here so the answer cannot depend on the machine's locale.
    On the Mac, where the locale is already UTF-8, all of this is a no-op.

    ⛔ An earlier draft of this docstring said "this machine happens to export
    PYTHONIOENCODING=utf-8" and treated that as the reason only the parent needed fixing. **It
    does not export it** — that was true of the one shell the fix was measured in, and believing
    it is what let 22 files sit red on a bare run while a suite total of 61/61 stood recorded.
    Nothing in this file may assume that variable is set; that is why it is passed explicitly.
    """
    return {**os.environ, "PYTHONIOENCODING": "utf-8", **extra}


def run_script(name: str, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(SCRIPTS / name), *args],
                       capture_output=True, text=True, errors="replace",
                       encoding="utf-8", env=utf8_env())
    return r.returncode, (r.stdout or "") + (r.stderr or "")


@contextlib.contextmanager
def unset_hooks_path():
    """Make a fixture repo's `core.hooksPath` genuinely UNSET, whatever this machine sets.

    ⛔⛔ A FIXTURE CANNOT ASSUME "UNSET" — IT HAS TO ENFORCE IT (SCC-321). `core.hooksPath` is
    inherited from GLOBAL config, and this system's own setup instructions tell the operator to
    run `git config --global core.hooksPath .githooks` so every repo on a machine is armed. Where
    that was done, a brand-new temp repo is born ARMED: the "fresh clone has no gates" fixture
    describes a state the machine cannot produce, and cases asserting an error find none.

    The real damage is that such a case measures the OPERATOR'S GIT CONFIG rather than the code.
    It flips between machines, and between two clones on one machine, for reasons that have
    nothing to do with what is under test. `GIT_CONFIG_GLOBAL` / `GIT_CONFIG_SYSTEM` pointed at an
    empty file is git's own supported way to say "read no config except this repo's" (git ≥ 2.32).

    ⓘ Separately worth the operator's attention: `hooks_armed`'s own REMEDY constant says NOT
    `--global`, because a relative path set globally arms `.githooks/` in every repo on the
    machine — including third-party clones that happen to ship that directory.
    """
    saved = {k: os.environ.get(k) for k in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM")}
    with tempfile.TemporaryDirectory() as cfg:
        empty = Path(cfg, "empty-gitconfig")
        empty.write_text("", encoding="utf-8")
        os.environ["GIT_CONFIG_GLOBAL"] = str(empty)
        os.environ["GIT_CONFIG_SYSTEM"] = str(empty)
        try:
            yield
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


def fake_exe(bindir, name: str, body: str) -> str:
    """A stub binary running `body` (Python source), findable and runnable on BOTH machines.

    ⛔⛔ A SHEBANG SCRIPT IS NOT AN EXECUTABLE ON WINDOWS, AND IT IS INVISIBLE TWICE OVER (SCC-321).
    `#!/usr/bin/env python3` is a kernel convention POSIX has and Windows does not, so:

      `shutil.which("acli")`   finds NOTHING — Windows resolves names through `PATHEXT`, and an
                               extensionless file is not on that list. Production code probing
                               with `which` therefore reports the tool ABSENT, and the test reads
                               as "the fallback works" when the fixture was simply never seen.
      `subprocess.run([stub])` raises `OSError [WinError 193] %1 is not a valid Win32 application`
                               — or, worse for a fixture whose whole job is to record its argv,
                               never runs, so the `argv.json` the case reads is not there and the
                               file dies at `FileNotFoundError` before scoring a single case.

    Both failures name something other than their cause, which is why this is centralised rather
    than solved three times. On Windows the stub is a `.cmd` launcher (on `PATHEXT`, and
    CreateProcess runs it) delegating to a `.py` beside it; on POSIX it stays the shebang script
    it always was. `__file__` inside `body` resolves to the same directory either way, so a stub
    that writes `argv.json` next to itself keeps working unchanged.

    Returns the path to invoke — pass it to `ACLI_BIN`-style env vars, or put `bindir` on `PATH`.
    """
    bindir = Path(bindir)
    bindir.mkdir(parents=True, exist_ok=True)

    if os.name != "nt":
        script = bindir / name
        script.write_text(f"#!{sys.executable}\n{body}", encoding="utf-8")
        script.chmod(0o755)
        return str(script)

    (bindir / f"{name}.py").write_text(body, encoding="utf-8")
    launcher = bindir / f"{name}.cmd"
    # `%*` forwards every argument; cmd propagates the child's exit code as its own.
    launcher.write_text(f'@echo off\r\n"{sys.executable}" "%~dp0{name}.py" %*\r\n',
                        encoding="utf-8", newline="")
    return str(launcher)


def path_entry(p) -> str:
    """`p` spelled the way a POSIX shell's `$PATH` can actually read it (SCC-321).

    ⛔ A POSIX `$PATH` is COLON-separated, and a Windows path carries a colon at character two.
    So `C:/Users/me/shim` in `$PATH` is not one entry — it is two, `C` and `/Users/me/shim`, and
    neither exists. Nothing errors; the directory is simply never searched.

    Git Bash reads `/c/Users/me/shim`, which has no colon and resolves to the same place.
    On POSIX this is the identity function.
    """
    if os.name != "nt":
        return str(p)
    drive, rest = os.path.splitdrive(str(p))
    if not drive:
        return str(p).replace(os.sep, "/")
    return f"/{drive[0].lower()}{rest.replace(os.sep, '/')}"


def sh_with_path(sh: str, prepend, argv: list[str]) -> list[str]:
    """An argv that runs `argv` under `sh` with `prepend` FIRST on `$PATH` (SCC-321).

    ⛔⛔ PASSING PATH IN `env=` DOES NOT WORK ON WINDOWS, AND IT FAILS SILENTLY. `C:\\Git\\bin\\sh.exe`
    rewrites the environment it is given and puts its OWN `/mingw64/bin:/usr/bin` at the FRONT — so
    an injected shim lands behind the very binary it exists to shadow, the real one runs, and the
    test measures the unshimmed system while reporting normally. Measured: `command -v git` answered
    `/mingw64/bin/git` with the shim dir present but later in the list.

    Setting `$PATH` INSIDE the started shell is after that rewrite, so it wins. Combined with
    `path_entry` (a Windows path is unreadable in a colon-separated `$PATH`), the shim resolves.

    `sh -c '<script>' <argv0> <args...>` is the POSIX form: `$0` is the name, `$@` the rest — hence
    the `"sh"` placeholder before the real command.
    """
    return [sh, "-c", 'PATH="$1:$PATH"; shift; exec "$@"', "sh", path_entry(prepend), *argv]


def run_stdin_lf(args, *, stdin: str = "", **kw) -> subprocess.CompletedProcess:
    """Run `args` feeding `stdin` BYTE-EXACT, and hand back decoded text (SCC-321).

    ⛔⛔ `subprocess.run(..., text=True, input="a b\\n")` DOES NOT SEND WHAT IT SAYS ON WINDOWS.
    Text mode wraps the child's stdin in a `TextIOWrapper` with `newline=None`, which translates
    `\\n` to `os.linesep` on write — so the child receives `a b\\r\\n`. It is the same defect as
    `Path.write_text` (see `_write_text_lf`), reached by a completely different road, and it is
    the one the main write gate died on.

    ⭐ WHAT IT LOOKS LIKE, because it is worth recognising on sight. `pre-push` is fed
    `<ref> <local> <ref> <remote>` on stdin; the trailing field arrived as `84ad225…\\r`, so the
    gate's `[ "$parent1" != "$remote_sha" ]` was TRUE and it refused a perfectly good merge. Its
    refusal then printed both values — and they looked IDENTICAL, because a carriage return just
    moves the cursor to the start of the line. A diagnosis by reading the error message is
    therefore guaranteed to be wrong: the message is honest, the terminal is not.

    ⭐ WHY A HELPER AND NOT A SEAM PATCH like the `write_text` one. Neutralising this inside
    `subprocess` means rebuilding the child's stdin wrapper after `Popen.__init__` has already
    made it — two wrappers over one buffer, with the close/detach hazard that implies. That is
    fragile magic in the file every test imports, which is a worse trade than nineteen explicit
    call sites. Here the byte-exactness is *visible where it matters*.

    Returns a `CompletedProcess` whose `stdout`/`stderr` are `str`, so it drops into a call site
    that had `text=True, capture_output=True` unchanged.
    """
    kw.pop("text", None)
    kw.pop("universal_newlines", None)
    kw.pop("input", None)
    kw.setdefault("capture_output", True)
    r = subprocess.run(list(args), input=stdin.encode("utf-8"), **kw)
    decode = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else b   # noqa: E731
    return subprocess.CompletedProcess(r.args, r.returncode, decode(r.stdout), decode(r.stderr))


@functools.lru_cache(maxsize=1)
def posix_sh() -> str | None:
    """Absolute path to a POSIX shell that can read THIS machine's paths, or None (SCC-321).

    ⛔ Never write `subprocess.run(["sh", ...])`. Windows has no `sh` on PATH, so that call
    raises `FileNotFoundError [WinError 2]` — and because it raises rather than returning a
    bad exit code, it takes the ENTIRE file down before a single case is scored. The file
    reads as one failure in the summary; it is really "none of this ran".

    ⛔ `bash` is not a fallback on Windows. `System32\\bash.exe` is the WSL launcher, and WSL
    mounts this drive at `/mnt/c`, so a `C:\\...` argument resolves to nothing inside it. It
    would fail later, and far less legibly, than finding no shell at all. Git for Windows
    ships the shell these scripts were written for, so ask `git` where it lives instead of
    guessing an install directory — the answer is right whether Git sits in `C:\\Git` or in
    `C:\\Program Files\\Git`.
    """
    def usable(p: str | None) -> str | None:
        if not p:
            return None
        if os.name == "nt" and Path(p).parent.name.lower() == "system32":
            return None                       # the WSL launcher — a different filesystem view
        return p

    found = usable(shutil.which("sh"))
    if found:
        return found

    if os.name == "nt":
        try:
            exec_path = subprocess.run(["git", "--exec-path"], capture_output=True,
                                       text=True, timeout=15).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            exec_path = ""
        if exec_path:
            # …/<git-root>/mingw64/libexec/git-core  ->  …/<git-root>/bin/sh.exe
            candidate = Path(exec_path).parents[2] / "bin" / "sh.exe"
            if candidate.is_file():
                return str(candidate)

    return usable(shutil.which("bash"))


class TempDir:
    """A scratch directory that cleans up even after a chmod'd read-only file."""

    def __enter__(self) -> Path:
        self.path = Path(tempfile.mkdtemp(prefix="wfscripts-"))
        return self.path

    def __exit__(self, *exc: object) -> None:
        def force(func, path, _info):  # read-only files (and .git objects) on Windows
            Path(path).chmod(0o700)
            func(path)
        shutil.rmtree(self.path, onerror=force)
