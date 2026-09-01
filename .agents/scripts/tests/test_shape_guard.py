"""shape-guard.py — the PostToolUse nag that points an agent back at command-shape.md (SCC-369).

The measured problem: `command-shape.md` is standing law on every platform and was violated in
1,933 of 7,858 Bash calls across 25 sessions — 98.9% of every detectable violation. Restating the
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
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / ".agents" / "hooks" / "shape-guard.py"
SETTINGS = ROOT / ".claude" / "settings.json"


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


# ── the three violations it must catch ──────────────────────────────────────────────────────

def test_piped_gate_nags_rule_3():
    rc, parsed = run_hook("python3 .agents/scripts/tests/run_all.py | tail -5")
    assert rc == 0, f"a nag must never fail the call; exit={rc}"
    text = nag_text(parsed)
    assert text, "a piped gate produced no nag"
    assert "command-shape" in text, f"the nag must CITE the rule file, got: {text!r}"
    assert "rule 3" in text.lower(), f"the nag must name which rule, got: {text!r}"


def test_exit_echo_tail_nags_rule_2():
    rc, parsed = run_hook('python3 .agents/scripts/tests/run_all.py; echo "EXIT=$?"')
    assert rc == 0
    text = nag_text(parsed)
    assert text, "an exit-echo tail produced no nag"
    assert "command-shape" in text and "rule 2" in text.lower(), f"got: {text!r}"


def test_git_dash_c_nags_rule_1_with_the_remedy():
    rc, parsed = run_hook("git -C /some/repo status --porcelain")
    assert rc == 0
    text = nag_text(parsed)
    assert text, "a git -C invocation produced no nag"
    assert "command-shape" in text and "rule 1" in text.lower(), f"got: {text!r}"
    assert "cd " in text and "&&" in text, (
        f"the nag must name the REMEDY (cd <abs> && git), not just the fault: {text!r}")


# ── the negative battery: silence is the correct answer ──────────────────────────────────────

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


# ── registration: the SCC-77 seam ────────────────────────────────────────────────────────────

def test_registered_through_run_hook_never_a_bare_interpreter():
    """SCC-77: naming one platform's binary exits 127 IN SILENCE on the other machine.

    `run-hook.sh` probes `python3 → python → py`; every other hook is wired through it. The probe
    that proved this nag's channel was registered as `python3 <path>`, so shipping that shape
    would reproduce the bug exactly.
    """
    cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    entries = cfg.get("hooks", {}).get("PostToolUse", [])
    cmds = [h.get("command", "") for group in entries for h in group.get("hooks", [])]
    ours = [c for c in cmds if "shape-guard" in c]
    assert ours, f"shape-guard.py is not registered under PostToolUse: {cmds}"
    for c in ours:
        assert "run-hook.sh" in c, f"must dispatch through run-hook.sh, got: {c!r}"
        assert not c.strip().startswith(("python3 ", "python ", "py ")), (
            f"bare interpreter in the registration — dies on the other machine: {c!r}")


def test_hook_is_indexed():
    """An unindexed hook is invisible to the next reader; that INDEX calls itself the MASTER."""
    idx = (ROOT / ".agents" / "hooks" / "INDEX.md").read_text(encoding="utf-8")
    assert "shape-guard.py" in idx, ".agents/hooks/INDEX.md has no row for shape-guard.py"


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
