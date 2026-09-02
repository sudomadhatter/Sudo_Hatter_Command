"""shape-guard.py — the PostToolUse nag that points an agent back at command-shape.md (SCC-369).

The measured problem: `command-shape.md` is standing law on every platform and was violated in
1,946 of 8,355 Bash calls across 25 sessions — 23.3% of every Bash call made. Restating the
rule in a fifth place does not work; a message at the moment of the mistake does.

⛔ THE LOAD-BEARING ASSERTION IN THIS FILE is `test_never_blocks`. A nag that can block is not a
nag: `permissionDecision: "ask"` becomes an auto-DENY in auto mode (see require-push-approval.py's
own header) and a PostToolUse `decision: "block"` feeds an error to the model. Either would strand
a headless run over a style note. A mutant that makes the hook block MUST turn this file red.

run_all.py executes test files bare (python3 <file>, no pytest), so the __main__ harness at the
bottom is what makes this file COUNT — without it the suite scores it green having run nothing
(house scar: suite-red-file-may-have-run-nothing).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / ".agents" / "hooks" / "shape-guard.py"
SETTINGS = ROOT / ".claude" / "settings.json"
RULE_PATH = ".agents/rules/command-shape.md"


def run_hook(command: str | None, raw: str | None = None):
    """Drive the hook exactly as Claude Code does: JSON on stdin, JSON or nothing on stdout.

    `sys.executable` carries whichever interpreter launched the suite down to the child — the Mac
    has no bare `python` and the PC has no `python3`, so naming either here would pass on one
    machine and die on the other (code-standards §5 Both machines).
    """
    payload = raw if raw is not None else json.dumps({
        "session_id": "test", "cwd": str(ROOT),
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "tool_response": {"stdout": "", "stderr": "", "interrupted": False},
    })
    p = subprocess.run([sys.executable, str(HOOK)], input=payload, text=True,
                       capture_output=True, cwd=str(ROOT), timeout=20)
    out = p.stdout.strip()
    parsed = None
    if out:
        try:
            parsed = json.loads(out)
        except json.JSONDecodeError:
            parsed = {"__unparseable__": out}
    return p.returncode, parsed


def nag_text(parsed) -> str:
    if not parsed:
        return ""
    return (parsed.get("hookSpecificOutput") or {}).get("additionalContext", "") or ""


def assert_cites_the_rule(text: str) -> None:
    """⛔ The nag's ONE job is to send the agent to the law, so pin the PATH, not the word.

    `assert "command-shape" in text` was vacuous: the hook's own preamble carries that word
    independently of `RULE`, so a mutant setting `RULE = "docs/does-not-exist.md"` kept every
    case green while the nag pointed at nothing (SCC-369 review, reproduced by mutation).
    """
    assert RULE_PATH in text, f"the nag must CITE {RULE_PATH}, got: {text!r}"
    assert (ROOT / RULE_PATH).exists(), (
        f"the nag cites {RULE_PATH}, which does not exist — a citation to nowhere is not a citation")


# ── the three violations it must catch ──────────────────────────────────────────────────────

def test_piped_gate_nags_rule_3():
    rc, parsed = run_hook("python3 .agents/scripts/tests/run_all.py | tail -5")
    assert rc == 0, f"a nag must never fail the call; exit={rc}"
    text = nag_text(parsed)
    assert text, "a piped gate produced no nag"
    assert_cites_the_rule(text)
    assert "rule 3" in text.lower(), f"the nag must name which rule, got: {text!r}"
    assert "> out.txt" in text, (
        f"the nag must name the REMEDY (redirect, then read the file), not just the fault: {text!r}")


def test_exit_echo_tail_nags_rule_2():
    rc, parsed = run_hook('python3 .agents/scripts/tests/run_all.py; echo "EXIT=$?"')
    assert rc == 0
    text = nag_text(parsed)
    assert text, "an exit-echo tail produced no nag"
    assert_cites_the_rule(text)
    assert "rule 2" in text.lower(), f"got: {text!r}"
    assert "exit code" in text.lower(), (
        f"the nag must name the REMEDY (the harness already shows the exit code): {text!r}")


def test_git_dash_c_nags_rule_1_with_the_remedy():
    rc, parsed = run_hook("git -C /some/repo status --porcelain")
    assert rc == 0
    text = nag_text(parsed)
    assert text, "a git -C invocation produced no nag"
    assert_cites_the_rule(text)
    assert "rule 1" in text.lower(), f"got: {text!r}"
    assert "cd " in text and "&&" in text, (
        f"the nag must name the REMEDY (cd <abs> && git), not just the fault: {text!r}")


def test_every_gate_spelling_fires_rule_3():
    """⛔ Seven of the eight spellings in the rule-3 regex had no case at all.

    A regex nobody exercises is a regex that can silently lose an alternative — which is exactly
    how a diverged private copy of the detector stayed invisible (SCC-369 review).
    """
    spellings = [
        "python3 .agents/scripts/tests/run_all.py", "python3 -m pytest", "npx vitest run",
        "ruff check .", "pyrefly check", "npx tsc --noEmit",
        "npm run test", "npm run lint", "python3 .agents/scripts/tests/test_shape_scan.py",
    ]
    missed = []
    for gate in spellings:
        _, parsed = run_hook(f"{gate} | head -20")
        if "rule 3" not in nag_text(parsed).lower():
            missed.append(gate)
    assert not missed, f"these gate spellings are piped and NOT nagged: {missed}"


# ── the negative battery: silence is the correct answer ──────────────────────────────────────

def test_reading_a_test_file_through_a_pipe_is_silent():
    """⛔ The rule-3 twin of `test_grep_for_the_string_is_silent`, and it was missing.

    `GATE` matched a gate's NAME anywhere in a pipe piece, so reading a test file was reported as
    piping a gate. Measured on the live corpus at 170 of 779 rule-3 hits (21.8%) — noise that also
    inflated the published baseline the whole ruling rests on (SCC-369 review, two lenses).
    """
    readers = [
        "sed -n '1,80p' .agents/scripts/tests/test_shape_guard.py | head -40",
        "cat .agents/scripts/tests/test_zoo_permissions.py | head -60",
        "grep -rn run_all.py .agents/ | head -20",
        "wc -l .agents/scripts/tests/test_shape_guard.py | cat",
        "git log --oneline -- .agents/scripts/tests/test_rule_frontmatter.py | head -5",
    ]
    nagged = [c for c in readers if nag_text(run_hook(c)[1])]
    assert not nagged, f"reading a file was nagged as piping a gate: {nagged}"


def test_searching_for_the_exit_tail_is_silent():
    """⛔ The rule-2 twin of the same control, and it was missing too.

    Rule 2 cannot strip quotes (`$?` lives inside them), so it needs the quoted POSITIONS instead.
    Without that, a search for the banned tail — and a commit message containing it — were both
    nagged for writing it. This lane newly puts that literal in six documents, so grepping for it
    is now a normal action (SCC-369 review).
    """
    searches = [
        """grep -rn '; echo "EXIT=$?"' .agents/rules/""",
        'git commit -m "SCC-1 fix; echo $? was wrong"',
    ]
    nagged = [c for c in searches if nag_text(run_hook(c)[1])]
    assert not nagged, f"a SEARCH for the tail literal was nagged as a USE of it: {nagged}"

def test_clean_command_is_silent():
    rc, parsed = run_hook("cd /repo && git status --porcelain")
    assert rc == 0
    assert not nag_text(parsed), (
        f"a correctly-shaped command was nagged — noise trains the agent to ignore it: {parsed!r}")


def test_grep_for_the_string_is_silent():
    """A search FOR `git -C` is not a USE of it. This false positive beat the first scanner."""
    rc, parsed = run_hook('grep -rn "git -C" .agents/')
    assert rc == 0
    assert not nag_text(parsed), f"a grep for the literal was nagged: {parsed!r}"


def test_quoted_prose_mentioning_the_spelling_is_silent():
    """The case that actually pins `strip_quoted`.

    The mutation sweep proved `test_grep_for_the_string_is_silent` does NOT pin it: in
    `grep -rn "git -C" …` the character before `git` is a quote, which the rule-1 leading class
    `[;&|(\\s]` already rejects — so deleting the quote strip left that case green and the mutant
    survived as DEFECTIVE rather than as a coverage gap. Here the mention sits after a SPACE
    inside the quotes, so only the strip can keep it quiet.
    """
    rc, parsed = run_hook('echo "reminder: never use git -C in a door"')
    assert rc == 0
    assert not nag_text(parsed), (
        f"prose inside quotes was read as a command — strip_quoted is not holding: {parsed!r}")


def test_heredoc_body_is_silent():
    """A heredoc body is DATA, not commands. The first scanner counted it as commands."""
    rc, parsed = run_hook("cat > note.txt <<'EOF'\ngit -C x status\ngit add -A\nEOF")
    assert rc == 0
    assert not nag_text(parsed), f"a heredoc payload was nagged: {parsed!r}"


def test_non_bash_tool_is_silent():
    """⛔ The payload MUST carry a `command` key, or this pins nothing.

    The sweep proved it: with `file_path` only, deleting the `tool_name != "Bash"` guard left
    this green anyway, because the empty-command guard caught it — a DEFECTIVE mutant, not a
    coverage gap. A non-Bash tool whose input happens to have a `command` field is the only
    shape that isolates the tool filter.
    """
    payload = json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Read",
                          "tool_input": {"command": "git -C /repo status"}})
    rc, parsed = run_hook(None, raw=payload)
    assert rc == 0 and not nag_text(parsed), f"a non-Bash tool was nagged: {parsed!r}"


# ── fails open, and never blocks ─────────────────────────────────────────────────────────────

def test_malformed_stdin_fails_open():
    rc, parsed = run_hook(None, raw="{not json at all")
    assert rc == 0, f"a hook that cannot parse must ALLOW, not fail; exit={rc}"
    assert not nag_text(parsed)


def test_empty_stdin_fails_open():
    rc, parsed = run_hook(None, raw="")
    assert rc == 0 and not nag_text(parsed)


def test_never_blocks():
    """⛔ THE LOAD-BEARING ONE. Every path — hits included — must exit 0 and emit no blocking key.

    `permissionDecision: "ask"` auto-DENIES in auto mode; a PostToolUse `decision: "block"` feeds
    an error to the model. A mutant introducing either must turn this red.
    """
    cases = [
        "python3 .agents/scripts/tests/run_all.py | tail -5",
        'python3 x.py; echo "EXIT=$?"',
        "git -C /some/repo status",
        "cd /repo && git status",
        "grep -rn 'git -C' .",
    ]
    for cmd in cases:
        rc, parsed = run_hook(cmd)
        assert rc == 0, f"BLOCKING PATH: {cmd!r} exited {rc}; a nag must never fail the call"
        if not parsed:
            continue
        assert "decision" not in parsed, f"BLOCKING KEY on {cmd!r}: {parsed!r}"
        hso = parsed.get("hookSpecificOutput") or {}
        assert "permissionDecision" not in hso, f"permissionDecision on {cmd!r}: {parsed!r}"
        # ⛔ `continue: false` halts the session outright and OUTRANKS `decision` — the strongest
        # stop lever in the contract, and the one this test used to miss entirely (SCC-369 review,
        # reproduced: emitting it left the file 13/13 green).
        assert "continue" not in parsed and "stopReason" not in parsed, (
            f"SESSION-STOPPING KEY on {cmd!r}: {parsed!r}")
        # Whitelist the shape rather than blacklisting keys, so the NEXT blocking key ever added
        # to the contract fails here without anyone remembering to name it.
        assert set(parsed) == {"hookSpecificOutput"}, (
            f"the nag emitted keys beyond hookSpecificOutput on {cmd!r}: {sorted(parsed)}")


# ── registration: the SCC-77 seam ────────────────────────────────────────────────────────────

def test_registered_through_run_hook_never_a_bare_interpreter():
    """SCC-77: naming one platform's binary exits 127 IN SILENCE on the other machine.

    `run-hook.sh` probes `python3 → python → py`; every other hook is wired through it. The probe
    that proved this nag's channel was registered as `python3 <path>`, so shipping that shape
    would reproduce the bug exactly.
    """
    cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    entries = cfg.get("hooks", {}).get("PostToolUse", [])
    cmds, matchers = [], []
    for group in entries:
        for h in group.get("hooks", []):
            if "shape-guard" in h.get("command", ""):
                cmds.append(h["command"])
                matchers.append(group.get("matcher"))
    assert cmds, "shape-guard.py is not registered under PostToolUse"
    for c in cmds:
        assert "run-hook.sh" in c, f"must dispatch through run-hook.sh, got: {c!r}"
        assert not c.strip().startswith(("python3 ", "python ", "py ")), (
            f"bare interpreter in the registration — dies on the other machine: {c!r}")
    # ⛔ A matcher that is not `Bash` makes the nag a permanent no-op, and the string checks above
    # never noticed. Both sibling hooks already assert this; this one did not (SCC-369 review).
    assert matchers == ["Bash"] * len(matchers), (
        f"the nag must be matched on Bash or it can never fire: {matchers}")
    # ⛔ And the path must RESOLVE. A one-character typo made `run-hook.sh` print
    # "not found — skipped" and exit 0 — the silent-127 class this test's own docstring names.
    for c in cmds:
        named = [w.strip('"\'') for w in c.split() if "shape-guard" in w]
        assert named, f"no script path in the registration: {c!r}"
        for n in named:
            rel = n.replace("$CLAUDE_PROJECT_DIR/", "").replace("${CLAUDE_PROJECT_DIR}/", "")
            assert (ROOT / rel).exists(), f"the registration points at a missing file: {rel}"


def _posix_shell() -> str:
    """The shell that actually runs a registered hook command - probed, never named.

    ⛔ `subprocess.run(cmd, shell=True)` is NOT that shell on Windows: there it is
    `cmd.exe /c`, which cannot expand `$CLAUDE_PROJECT_DIR`. `sh` was handed the literal string
    `$CLAUDE_PROJECT_DIR/.agents/hooks/run-hook.sh` as a FILENAME and exited 127, so this file
    reported the wiring dead on the PC while the nag was demonstrably firing in live sessions
    there. A false red costs what a false green costs: it sends the next reader after a bug that
    is not there. Same "probe, never name one platform's binary" discipline run-hook.sh enforces.

    ⛔ And it cannot just probe PATH. Claude Code ships its own POSIX shell and never
    consults the user's PATH; on the PC `sh` is absent from PATH under PowerShell, which is how
    the suite gets run there. So the fallback DERIVES the shell from wherever `git` itself
    resolved to - Git for Windows always carries `sh.exe` beside it - rather than naming an
    install directory. Naming one was the first cut of this fallback and it missed immediately:
    this PC keeps Git at `C:/Git`, not `C:/Program Files/Git`. An install path is a guess about
    a machine; `git`'s own location is a fact reported by it.
    """
    found = shutil.which("sh")
    if found:
        return found
    git = shutil.which("git")
    if git:
        base = Path(git).resolve().parent.parent      # .../cmd/git.exe -> the Git root
        for rel in ("usr/bin/sh.exe", "bin/sh.exe"):
            candidate = base / rel
            if candidate.exists():
                return str(candidate)
    raise AssertionError(
        "no POSIX shell found on this machine, so the registered hook command could not be "
        "exercised at all - run-hook.sh is sh-launched, so this is a real gap, not a skip")


def test_the_registered_command_actually_produces_a_nag():
    """⛔ End-to-end through the REGISTERED string — the only check that proves the wiring runs.

    Every assertion above reads text. This one executes what Claude Code executes, so a matcher
    swap, a path typo, or a run-hook.sh regression fails HERE rather than shipping as silence.
    """
    cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    cmd = next(h["command"] for g in cfg["hooks"]["PostToolUse"] for h in g.get("hooks", [])
               if "shape-guard" in h.get("command", ""))
    payload = json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Bash",
                          "tool_input": {"command": "git -C /some/repo status"}})
    shell = _posix_shell()
    # ⛔ The registered string's FIRST word is itself `sh`, so the CHILD has to resolve `sh`
    # too. Claude Code's hook shell carries it on PATH; a suite launched from PowerShell does not,
    # and the inner `sh` died 127 while the outer one ran perfectly - the same false red one layer
    # down. Putting the resolved shell's own directory in front of PATH reproduces the environment
    # Claude Code actually provides instead of asserting against one it never uses.
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT),
           "PATH": os.path.dirname(shell) + os.pathsep + os.environ.get("PATH", "")}
    p = subprocess.run([shell, "-c", cmd], input=payload, text=True,
                       capture_output=True, cwd=str(ROOT), env=env, timeout=30)
    assert p.returncode == 0, f"the registered command failed: rc={p.returncode} {p.stderr!r}"
    assert RULE_PATH in p.stdout, (
        f"the REGISTERED command produced no nag — the wiring is dead: "
        f"stdout={p.stdout!r} stderr={p.stderr!r}")


def test_hook_is_indexed():
    """An unindexed hook is invisible to the next reader; that INDEX calls itself the MASTER."""
    idx = (ROOT / ".agents" / "hooks" / "INDEX.md").read_text(encoding="utf-8")
    assert "shape-guard.py" in idx, ".agents/hooks/INDEX.md has no row for shape-guard.py"



def test_law_4_wsl_file_not_inline():
    """SCC-376 · the front door must carry law 4, and carry the REMEDY, not just the ban.

    Three probes in that lane answered confidently about the Windows clone because an inline
    `wsl.exe … bash -c "cd ~/repo && …"` had run in wsl.exe's start directory. A rule that only said
    "do not do that" would not have helped - the fix is a shape (a file, absolute paths, CRLF stripped),
    so the shape is what this pins. Deleting the section leaves the law silent, which is how a law is
    actually lost (the SCC-369 affirmative-half lesson)."""
    text = (ROOT / ".agents" / "rules" / "command-shape.md").read_text(encoding="utf-8")
    for phrase, why in (
        ("send a FILE, never an inline command", "the law itself"),
        ("/mnt/c/", "the Windows cwd the command silently lands in"),
        ("tr -d", "the CRLF strip, without which bash reports a file that exists as missing"),
        ("absolute", "the path rule that makes the file immune to the inherited cwd"),
    ):
        assert phrase.lower() in text.lower(), (
            f"command-shape.md law 4 no longer states {phrase!r} ({why})")


if __name__ == "__main__":
    import traceback
    _fns = [(n, f) for n, f in sorted(globals().items())
            if n.startswith("test_") and callable(f)]
    _failed = []
    for _name, _fn in _fns:
        try:
            _fn()
        except BaseException:
            _failed.append(_name)
            traceback.print_exc()
    print(f"-- {len(_fns) - len(_failed)}/{len(_fns)} passed --")
    # ⛔ `FAILED:` must START the line. mutation_sweep.judge() attributes a kill with
    # `ln.startswith("FAILED:")`, so the house inline form (`-- 10/12 passed --  FAILED: x`)
    # reads as "exit 1 with no FAILED: line" and every real kill comes back unattributable.
    if _failed:
        print(f"FAILED: {', '.join(_failed)}")
    sys.exit(1 if _failed else 0)
