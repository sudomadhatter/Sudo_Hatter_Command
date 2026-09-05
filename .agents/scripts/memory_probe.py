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

⛔ AND THE DENYLIST'S REACH IS STATED, NOT ASSUMED. It catches what an author types by accident —
a bare verb, one behind `sudo`/`env`/`xargs`, a `\rm`, a `git -C <path> push`, any writing
redirect, `find … -delete`, `sed -i`. It does NOT catch a deliberate evasion: `sh -c "rm …"`
and `python3 -c "…"` run — catching those needs an allowlist of observation verbs, which is a
different design. That boundary is a decision, not an oversight — the store is reviewed,
tracked text and the probe's author is its reviewer, so the denylist's job is to stop a mistake,
not an adversary. `test_memory_probe.py` pins BOTH sides of that line so it stays a decision.

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
import shutil
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
_BANNED_GIT = ("push", "commit", "checkout", "restore", "switch", "reset", "clean", "rebase",
               "merge", "fetch", "pull", "rm", "mv", "add", "stash", "config", "worktree",
               "submodule")

# Verbs that mutate nothing themselves but CARRY another command. Stepped over rather than
# banned, or `env rm -rf x` and `xargs rm` read as observations (SCC-401 review).
_WRAPPERS = ("env", "command", "exec", "nohup", "time", "nice", "stdbuf", "xargs")

# ⛔ COMMAND POSITION, not "anywhere in the string". The first cut matched `\bsudo\b` and refused
# a correct probe because the ntfy TOPIC is named `mac-sudo-command` - `-` is a word boundary, so
# a banned verb fired on a hyphenated identifier. A probe is refused only when the verb is what
# the shell would actually EXECUTE: at the start, or right after a separator that begins a new
# command. Found by running the runner (SCC-401).

_CMD_POS = (
    r"(?:^|[;&|(){}\n]|\|\||&&|`|\$\()\s*(?:!\s*)?"                     # a command starts here
    r"(?:\\?(?:sudo|doas)\s+)?"                                           # ...possibly elevated
    r"(?:\\?(?:" + "|".join(_WRAPPERS) + r")\s+(?:-\S+\s+|\w+=\S+\s+)*)*"  # ...behind wrappers
    r"\\?"                                                                 # ...or `\rm`-escaped
)
_BANNED_RE = [
    (re.compile(_CMD_POS + r"(" + "|".join(re.escape(c) for c in _BANNED_CMDS) + r")(?=\s|$)"), 1),
    # `git -C <path> push` and `git --git-dir=… push` are the same act as `git push`.
    (re.compile(_CMD_POS + r"(git\s+(?:(?:-C\s+\S+|--\S+)\s+)*(?:"
                + "|".join(_BANNED_GIT) + r"))(?=\s|$)"), 1),
    # In-place edits carry their mutation in a FLAG, not a verb, so the position rules cannot see
    # them: `find … -delete`, `find … -exec rm`, `sed -i`, `perl -pi -e` (SCC-401 review).
    (re.compile(r"\b(find\b[^;&|]*\s-(?:delete|exec)\b)"), 1),
    (re.compile(r"\b((?:sed|perl|ruby)\s+(?:-\w*\s+)*-\w*i\w*)(?=\s|$)"), 1),
    # ⛔ ANY redirect that writes. `2>&1` duplicates an fd and is the ONE shape spared; the first
    # cut spared EVERY numbered fd, so `echo x 1> /tmp/f` was accepted (SCC-401 review).
    (re.compile(r"(>>?)(?![&=])"), 1),
]

# ⛔ The redirect scan runs on the string with QUOTED SPANS BLANKED. Without that there is no legal
# way to probe for a mermaid edge or a markdown blockquote: `grep -q 'A --> B' docs/x.md` reads as
# a write, and every spelling of `-->` contains `>`, so the "one rewrite into a read-only form" the
# refusal offers does not exist for that class (SCC-401 review). Verb rules still see the raw
# string - a quoted `rm` is not executed, but blanking quotes for THEM would hide `sh -c "rm …"`
# no more than it already is, and the redirect rule is the only one whose token is punctuation.
_QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")
_REDIRECT_RULES = 2          # the LAST n rules above are the ones scanned quote-blanked


def refuse_reason(cmd: str) -> str | None:
    """Why this probe must not run, or None if it is an observation.

    Deliberately conservative: a false refusal costs the author one rewrite into a read-only
    form, while a false ACCEPT runs an unreviewed mutation on every machine in the fleet."""
    blanked = _QUOTED.sub(lambda m: " " * len(m.group(0)), cmd)
    for i, (rx, grp) in enumerate(_BANNED_RE):
        m = rx.search(blanked if i >= len(_BANNED_RE) - _REDIRECT_RULES else cmd)
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
    return re.search(r"[`\s(](~/[\w.~-]|/[\w.~-]+/)", body) is not None


# Shell words that carry no subject - a probe made only of these observes nothing in particular.
_NOISE = {"test", "grep", "ls", "cat", "head", "tail", "printf", "echo", "stat", "wc", "find",
          "git", "command", "true", "false", "not", "sort", "uniq", "cut", "awk", "sed", "diff",
          "python", "python3", "and", "the", "then", "else", "exit"}


def probe_subject(cmd: str) -> list[str]:
    """The tokens a probe actually OBSERVES - flags, operators and shell verbs removed."""
    words = re.split(r"[\s;&|()`$'\"]+", cmd)
    return [w for w in words if len(w) >= 4 and not w.startswith("-") and w not in _NOISE]


def is_anchored(text: str, cmd: str) -> bool:
    """Does this probe observe something the memory itself NAMES?

    ⛔ THE DEFECT THIS EXISTS TO STOP, measured on this file's own first cut (SCC-401 review).
    54 of the first 59 probes were `test -e <some tracked repo path>` - and for most, the path had
    nothing to do with the memory's claim. `vscode-hides-git-hook-output.md` was guarded by
    `test -e .agents/jira.conf`; five unrelated memories shared `test -e .agents/commands`; four
    shared `test -e _artifacts/_memory`, the directory the runner is walking as it checks them.
    Every one exits 0 forever, in every checkout, whatever happens to the claim. The gate reported
    them PASSED, which is worse than no probe: it is `two-machines-mac-and-pc` with a green tick.

    A falsifier has to be WIRED to the thing it falsifies. The cheapest honest test of that wiring
    is that the probe names something the memory's own body names. It cannot prove a probe is a
    GOOD falsifier - nothing mechanical can - but it makes the failure mode above impossible to
    write by accident, which is the one that actually happened."""
    body = text.split("\n---", 1)[-1] if text.startswith("---") else text
    subject = probe_subject(cmd)
    return any(w.strip(".,'\"`") in body for w in subject) if subject else False


_EXISTS_ONLY = re.compile(r"^\s*(?:!\s*)?(?:test|\[)\s+-[efdxsr]\s+(\S+?)\s*\]?\s*$")


def cannot_fail(cmd: str, cwd: Path) -> str | None:
    """Why this probe can never go red, or None if it can.

    ⛔ A BARE EXISTENCE CHECK ON A TRACKED PATH IS NOT A FALSIFIER (SCC-401 review). git guarantees
    it: the file is in every checkout, so the probe exits 0 forever whatever happens to the claim.
    54 of this file's own first 59 probes were exactly that shape - five unrelated memories shared
    `test -e .agents/commands`, and four shared `test -e _artifacts/_memory`, the directory the
    runner walks to reach them. The gate printed `59 probe(s) passed`, which is worse than no probe
    at all: it is the `two-machines-mac-and-pc` failure wearing a green tick.

    An existence probe is still right for a path git does NOT carry - a per-machine artifact, a
    generated file, a mount. What is banned is asserting that the repo contains the repo."""
    m = _EXISTS_ONLY.match(cmd)
    if not m:
        return None
    target = m.group(1).strip("'\"")
    r = subprocess.run(["git", "ls-files", "--error-unmatch", "--", target],
                       cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return None
    return (f"`{cmd}` cannot fail - git tracks `{target}`, so every checkout has it. Probe what "
            f"the memory CLAIMS, or drop the probe: a ruling needs none")


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
    tail = (r.stderr or "").strip().splitlines()
    return False, f"exit {r.returncode}" + (f" - {tail[-1][:160]}" if tail else "")


NO_SHELL = "no-shell"          # an `unprobed` reason, NOT a failure - see run_store


def scan_store(store: Path) -> list[tuple[str, str | None, bool]]:
    """(name, probe_or_None, names_a_path) for every memory. Reads text; runs NOTHING.

    The audit signal only ever needed this. It used to call `run_store` and throw away both result
    lists, which executed every probe a second time - at the invoker's cwd rather than the repo
    root, so the answers it discarded were wrong ones (SCC-401 review)."""
    out = []
    for p in sorted(store.glob("*.md")):
        if p.name in EXEMPT:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        out.append((p.name, probe_of(text), names_a_path(text)))
    return out


def weak_probes(store: Path, cwd: Path) -> list[tuple[str, str]]:
    """(name, why) for every probe that cannot falsify its own memory - the SCC-401 review gate."""
    weak = []
    for p in sorted(store.glob("*.md")):
        if p.name in EXEMPT:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        cmd = probe_of(text)
        if cmd is None:
            continue
        why = cannot_fail(cmd, cwd)
        if why is None and not is_anchored(text, cmd):
            why = (f"`{cmd}` names nothing this memory's body names - a falsifier has to be wired "
                   f"to the claim it falsifies")
        if why:
            weak.append((p.name, why))
    return weak


def run_store(store: Path, cwd: Path, timeout: int = DEFAULT_TIMEOUT) -> tuple[list, list, list]:
    """(passed, failed, unprobed) - each a list of (name, detail).

    ⛔ A probe runs under `bash`, and the Windows side of this PC has none. A machine with no
    POSIX shell reports every probe as UNGATED (`NO_SHELL`), never as failed: a red no author on
    that machine can fix is the cry-wolf gate this whole file exists to avoid, and `port-checklist`
    § *It runs on BOTH sides* is the standing law it would break."""
    passed, failed, unprobed = [], [], []
    have_shell = shutil.which("bash") is not None
    for name, cmd, pathy in scan_store(store):
        if cmd is None:
            unprobed.append((name, "path-naming" if pathy else ""))
        elif not have_shell:
            unprobed.append((name, NO_SHELL))
        else:
            ok, detail = run_one(cmd, cwd, timeout)
            (passed if ok else failed).append((name, detail or cmd))
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
    candidates = [n for n, why in unprobed if why == "path-naming"]
    skipped = [n for n, why in unprobed if why == NO_SHELL]
    if skipped:
        print(f"[SKIP] no `bash` on this machine - {len(skipped)} probe(s) NOT gated here.")
    print(f"\n{len(passed)} probe(s) passed, {len(failed)} failed, "
          f"{len(unprobed) - len(skipped)} memor(ies) carry no probe "
          f"({len(candidates)} of them name a path - audit candidates).")
    if failed:
        print("\nA failing probe means the memory is no longer true. Rewrite it to what IS true, "
              "or delete it if it was only ever true somewhere that no longer exists.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
