"""memory_probe.py — make a memory prove it is STILL TRUE (SCC-401).

`_artifacts/_memory/` holds 147 files that every agent on every platform loads and treats as
fact. Nothing in the suite could tell one that is still true from one that stopped being true.
That is the defect this closes — not any single stale file.

The case that produced it: `two-machines-mac-and-pc.md` was confirmed by the operator on
2026-08-08, went false when SCC-376 moved the working environment into WSL2 on 2026-09-02, and
stayed loaded and trusted for two more days while an agent used it to tell Mr. Hatter four wrong
things in one afternoon. `test_memory_store.py` flags memories by AGE and by SHAPE, and neither
can separate an old fact that is still true from a recent one that just broke.

THE MECHANISM. A memory that asserts something checkable carries its own falsifier:

    metadata:
      probe: "test -d /mnt/c/Sudo_Hatter_Command"

A plain shell command. Exit 0 means the claim still holds. No DSL, nothing to learn — the probe
IS the command you would type to check by hand, which is the only form that stays honest, because
an author who cannot type it cannot write it.

⛔ A PROBE IS READ-ONLY. This runner executes strings out of tracked text files, inside the suite,
on every machine. That is only safe while a probe is an OBSERVATION. `refuse_reason()` rejects the
mutating and network shapes outright and the runner reports them as failures — a probe that writes
is a bug in the memory, not a test to skip.

⛔ PROBE WHAT IS STABLE, NOT WHAT IS TRUE TODAY. A commit count, a file count or a timestamp
changes on its own and would red the suite for a reason no author can fix — and a gate that cries
wolf is one people learn to skip, which is the disease this file exists to cure. Probe existence,
identity and shape.

Standalone: `python3 .agents/scripts/memory_probe.py [--store <path>] [--timeout N]`
In the suite: `test_memory_store.py` calls `run_store()` and goes red on any failure, naming the file.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

EXEMPT = {"MEMORY.md", "README.md"}
DEFAULT_TIMEOUT = 10

# A probe observes. These shapes do not - they mutate the box or reach the network, and neither
# belongs in a check the whole team runs on every suite pass.
_BANNED_CMDS = (
    "rm", "mv", "cp", "dd", "mkdir", "rmdir", "touch", "chmod", "chown", "ln", "truncate",
    "kill", "pkill", "sudo", "doas", "curl", "wget", "nc", "ssh", "scp", "rsync", "pip",
    "pip3", "npm", "npx", "apt", "apt-get", "brew", "tee", "install", "shred", "unlink",
)
_BANNED_GIT = ("push", "commit", "checkout", "reset", "clean", "rebase", "merge", "fetch",
               "pull", "rm", "mv", "add", "stash", "config", "worktree", "submodule")

# ⛔ COMMAND POSITION, not "anywhere in the string". The first cut matched `\bsudo\b` and refused
# a correct probe because the ntfy TOPIC is named `mac-sudo-command` - `-` is a word boundary, so
# a banned verb fired on a hyphenated identifier. A probe is refused only when the verb is what
# the shell would actually EXECUTE: at the start, or right after a separator that begins a new
# command. Found by running the runner (SCC-401).
_CMD_POS = r"(?:^|[;&|(){}\n]|\|\||&&|`|\$\()\s*(?:!\s*)?(?:sudo\s+)?"
_BANNED_RE = [
    (re.compile(_CMD_POS + r"(" + "|".join(re.escape(c) for c in _BANNED_CMDS) + r")(?=\s|$)"), 1),
    (re.compile(_CMD_POS + r"(git\s+(?:" + "|".join(_BANNED_GIT) + r"))(?=\s|$)"), 1),
    # any redirection that WRITES a file (`2>&1` and `>=` are not writes)
    (re.compile(r"(>>)"), 1),
    (re.compile(r"(?<![0-9<>])(>)(?![&=])"), 1),
]


def refuse_reason(cmd: str) -> str | None:
    """Why this probe must not run, or None if it is an observation.

    Deliberately conservative: a false refusal costs the author one rewrite into a read-only
    form, while a false ACCEPT runs an unreviewed mutation on every machine in the fleet."""
    for rx, grp in _BANNED_RE:
        m = rx.search(cmd)
        if m:
            return (f"probe is not read-only (`{m.group(grp).strip()}`) - a probe OBSERVES; "
                    f"rewrite it as a test/grep/ls that exits 0 when the claim holds")
    return None


def probe_of(text: str) -> str | None:
    """The `probe:` value from the frontmatter, or None.

    Read only inside the leading `---` block, so the word `probe:` in a body (this file is quoted
    in the memory rule, and rules get quoted into memories) is never mistaken for a directive."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    for line in text[3:end].splitlines():
        m = re.match(r'\s*probe:\s*(.+?)\s*$', line)
        if not m:
            continue
        val = m.group(1)
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        return val or None
    return None


def names_a_path(text: str) -> bool:
    """The body asserts an absolute or `~/` path — the class that rots silently.

    This is what makes a MISSING probe worth flagging as an audit candidate: a memory naming
    `/mnt/c/...` or `~/.gemini/...` is making a claim about one machine's disk, and that is
    exactly the claim that goes false without anyone noticing."""
    body = text.split("\n---", 1)[-1] if text.startswith("---") else text
    return re.search(r"[`\s(]([~/][\w./~-]{4,})", body) is not None


def run_one(cmd: str, cwd: Path, timeout: int = DEFAULT_TIMEOUT) -> tuple[bool, str]:
    """(passed, detail). A refusal, a timeout and a nonzero exit are all failures."""
    why = refuse_reason(cmd)
    if why:
        return False, why
    try:
        # encoding PINNED (SCC-335): bare `text=True` decodes with the machine locale, which is
        # the ANSI code page on the Windows side - the same class of defect
        # [[mac-authored-code-hides-windows-bugs]] records. `replace` so a probe whose output is
        # not text still reports its exit code instead of raising here.
        r = subprocess.run(["bash", "-c", cmd], cwd=str(cwd), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s - a probe must answer fast or it is not a probe"
    except OSError as e:
        return False, f"could not run: {e}"
    if r.returncode == 0:
        return True, ""
    tail = (r.stderr or r.stdout or "").strip().splitlines()
    return False, f"exit {r.returncode}" + (f" - {tail[-1][:160]}" if tail else "")


def run_store(store: Path, cwd: Path, timeout: int = DEFAULT_TIMEOUT) -> tuple[list, list, list]:
    """(passed, failed, unprobed) - each a list of (name, detail)."""
    passed, failed, unprobed = [], [], []
    for p in sorted(store.glob("*.md")):
        if p.name in EXEMPT:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        cmd = probe_of(text)
        if cmd is None:
            unprobed.append((p.name, "path-naming" if names_a_path(text) else ""))
            continue
        ok, detail = run_one(cmd, cwd, timeout)
        (passed if ok else failed).append((p.name, detail or cmd))
    return passed, failed, unprobed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--store", default="_artifacts/_memory")
    ap.add_argument("--cwd", default=".", help="working dir probes run in (the repo root)")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--quiet", action="store_true", help="print failures only")
    a = ap.parse_args()

    store, cwd = Path(a.store), Path(a.cwd)
    if not store.is_dir():
        print(f"memory_probe: no store at {store}", file=sys.stderr)
        return 2

    passed, failed, unprobed = run_store(store, cwd, a.timeout)
    if not a.quiet:
        for name, _ in passed:
            print(f"[PASS] {name}")
    for name, detail in failed:
        print(f"[FAIL] {name}: {detail}")
    candidates = [n for n, why in unprobed if why]
    print(f"\n{len(passed)} probe(s) passed, {len(failed)} failed, "
          f"{len(unprobed)} memor(ies) carry no probe "
          f"({len(candidates)} of them name a path - audit candidates).")
    if failed:
        print("\nA failing probe means the memory is no longer true. Rewrite it to what IS true, "
              "or delete it if it was only ever true somewhere that no longer exists.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
