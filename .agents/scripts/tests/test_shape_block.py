"""shape-block.py — the PreToolUse hook that refuses heredocs and proves leading assignments (SCC-415).

The measured problem: across 20 sessions, 13 of the operator's 15 hours of approval stops were two
command shapes the prefix matcher cannot read — heredocs (7h17m) and leading `VAR=` assignments
(5h44m). No allow row can fix a shape; this hook refuses the first BEFORE the permission gate and
proves the second harmless by the same nothing-new test allow-readonly-chain.py uses.

⛔ THE TWO LOAD-BEARING ASSERTIONS: `test_never_asks` — an ask is an auto-DENY in auto mode and
would strand a headless run; and `test_fails_open` — a hook that cannot judge must say nothing.

run_all.py executes test files bare (python3 <file>, no pytest), so the __main__ harness at the
bottom is what makes this file COUNT (house scar: suite-red-file-may-have-run-nothing).

Every case runs against a FIXTURE root with `HOME` redirected, because `already_allowed()` reads
`~/.claude/settings.json` too — judged against the developer's real rules, an allow or a
fall-through could pass for a reason no fixture states (the allow-readonly-chain test's own lesson).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / ".agents" / "hooks" / "shape-block.py"
RULE_PATH = ".agents/rules/command-shape.md"

FIXTURE_ALLOW = ["Bash(python3 .agents/scripts/*)", "Bash(ls:*)", "Bash(git status:*)"]


def seed(d: Path, allow=None, ask=None, deny=None) -> Path:
    (d / ".claude").mkdir(parents=True, exist_ok=True)
    perms: dict = {"allow": FIXTURE_ALLOW if allow is None else allow}
    if ask:
        perms["ask"] = ask
    if deny:
        perms["deny"] = deny
    (d / ".claude" / "settings.json").write_text(json.dumps({"permissions": perms}), encoding="utf-8")
    return d


def run_hook(command: str | None, root: Path, raw: str | None = None, tool: str = "Bash"):
    payload = raw if raw is not None else json.dumps({
        "session_id": "test", "cwd": str(root), "hook_event_name": "PreToolUse",
        "tool_name": tool, "tool_input": {"command": command},
    })
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root), "HOME": str(root), "USERPROFILE": str(root)}
    p = subprocess.run([sys.executable, str(HOOK)], input=payload, text=True, capture_output=True,
                       cwd=str(ROOT), timeout=30, env=env, errors="replace")
    out = p.stdout.strip()
    parsed = None
    if out:
        try:
            parsed = json.loads(out)
        except json.JSONDecodeError:
            parsed = {"__unparseable__": out}
    return p.returncode, parsed, p.stderr


def decision(parsed) -> str | None:
    return ((parsed or {}).get("hookSpecificOutput") or {}).get("permissionDecision")


def reason(parsed) -> str:
    return ((parsed or {}).get("hookSpecificOutput") or {}).get("permissionDecisionReason", "") or ""


def _fixture():
    d = tempfile.TemporaryDirectory()
    return d, seed(Path(d.name))


# ── rule 5 · heredocs are refused, and the refusal carries the reshape ──────────────────────

def test_heredoc_python_is_denied_and_names_the_reshape():
    d, root = _fixture()
    with d:
        rc, parsed, err = run_hook("python3 - <<'PY'\nprint(1)\nPY", root)
        assert rc == 0, f"a hook must exit 0 even when it denies; exit={rc} {err}"
        assert decision(parsed) == "deny", f"expected deny, got {parsed}"
        text = reason(parsed)
        assert RULE_PATH in text, f"the refusal must CITE {RULE_PATH}: {text!r}"
        assert (ROOT / RULE_PATH).exists(), "a citation to a file that does not exist is not a citation"
        for phrase in ("Write tool", "python3 <that path>", "git commit -F"):
            assert phrase in text, f"the refusal must name the reshape ({phrase!r}): {text!r}"


def test_heredoc_commit_message_is_denied():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("git commit -q -F - <<'MSG'\nSCC-1 fix\nMSG", root)
        assert decision(parsed) == "deny", parsed


def test_heredoc_after_a_cd_pin_is_denied():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("cd /abs/tree && python3 - <<'PY'\nx=1\nPY", root)
        assert decision(parsed) == "deny", parsed


def test_quoted_double_angle_is_not_a_heredoc():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook('python3 -c "print(1 << 2)"', root)
        assert parsed is None, f"a `<<` inside quotes is a bit-shift, not a heredoc: {parsed}"


def test_grep_for_the_heredoc_literal_is_not_a_heredoc():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("grep -rn '<<EOF' .agents", root)
        assert parsed is None, f"searching for the literal is not using it: {parsed}"


# ── rule 6 · leading literal assignments are stripped, and only a proven remainder is allowed ─

def test_leading_literal_assignment_is_stripped_and_allowed():
    d, root = _fixture()
    with d:
        _, parsed, err = run_hook("S=/tmp/x; python3 .agents/scripts/gate_receipt.py list", root)
        assert decision(parsed) == "allow", f"expected allow, got {parsed} {err}"
        assert RULE_PATH in reason(parsed)


def test_two_assignments_and_an_env_prefix_form_are_allowed():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook('A=1; B="/tmp/y z" python3 .agents/scripts/x.py --flag', root)
        assert decision(parsed) == "allow", parsed


def test_export_form_is_allowed():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("export S=/tmp/x; ls -la", root)
        assert decision(parsed) == "allow", parsed


def test_assignment_with_substitution_falls_through():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("S=$(pwd); python3 .agents/scripts/x.py", root)
        assert parsed is None, f"a $( ) value is not a literal; the hook must stay silent: {parsed}"


def test_assignment_with_dollar_var_falls_through():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("S=$TMPDIR; python3 .agents/scripts/x.py", root)
        assert parsed is None, parsed


def test_assignment_before_a_compound_falls_through():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("S=/tmp/x; ls a; ls b", root)
        assert parsed is None, f"the remainder is a chain, not one atom: {parsed}"


def test_assignment_before_a_remainder_with_substitution_falls_through():
    """Width, not existence: the value was a literal, but the REMAINDER carries a $( ) — it is
    not one atom, and `already_allowed` must never be asked about it."""
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("S=/tmp/x; ls $(rm -rf /)", root)
        assert parsed is None, f"a remainder with a substitution is not one atom: {parsed}"


def test_assignment_before_an_unallowed_command_falls_through():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("S=/tmp/x; rm -rf /", root)
        assert parsed is None, f"nothing-new means NOTHING new: {parsed}"


def test_assignment_before_an_ask_rule_falls_through():
    d = tempfile.TemporaryDirectory()
    with d:
        root = seed(Path(d.name), ask=["Bash(python3 .agents/scripts/danger.py:*)"])
        _, parsed, _ = run_hook("S=1; python3 .agents/scripts/danger.py", root)
        assert parsed is None, f"an operator's own ask row must never be talked over: {parsed}"


def test_plain_command_is_silent():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("python3 .agents/scripts/x.py", root)
        assert parsed is None, f"no shape to fix means the normal flow decides: {parsed}"


def test_cd_compound_is_silent():
    d, root = _fixture()
    with d:
        _, parsed, _ = run_hook("cd /abs && git status --short", root)
        assert parsed is None, f"cd-compounds never waited (measured 57/57); not this hook's job: {parsed}"


# ── the two load-bearing invariants ─────────────────────────────────────────────────────────

def test_never_asks():
    src = HOOK.read_text(encoding="utf-8")
    assert '"ask"' not in src, "the JSON value ask must not exist in this file — it is an auto-DENY in auto mode"
    d, root = _fixture()
    with d:
        for cmd in ("python3 - <<'PY'\nx\nPY", "S=/tmp/x; ls", "S=$(pwd); ls", "ls"):
            _, parsed, _ = run_hook(cmd, root)
            assert decision(parsed) != "ask", f"{cmd!r} produced an ask: {parsed}"


def test_fails_open():
    d, root = _fixture()
    with d:
        rc, parsed, _ = run_hook(None, root, raw="this is not json")
        assert rc == 0 and parsed is None, f"garbage stdin must be silence: rc={rc} {parsed}"
        rc, parsed, _ = run_hook("python3 - <<'PY'\nx\nPY", root, tool="Write")
        assert rc == 0 and parsed is None, f"a non-Bash tool must be silence: rc={rc} {parsed}"
        rc, parsed, _ = run_hook("", root)
        assert rc == 0 and parsed is None, f"an empty command must be silence: rc={rc} {parsed}"


# ── wiring · the real settings file, not a fixture ──────────────────────────────────────────

def test_wired_inside_the_single_pretooluse_bash_group():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    groups = [g for g in settings["hooks"]["PreToolUse"] if g.get("matcher") == "Bash"]
    assert len(groups) == 1, f"there must be exactly one PreToolUse Bash group (allow-readonly-chain pins it): {len(groups)}"
    cmds = [h["command"] for h in groups[0]["hooks"]]
    mine = [c for c in cmds if ".agents/hooks/shape-block.py" in c]
    assert len(mine) == 1, f"shape-block.py must be wired exactly once: {cmds}"
    assert all("run-hook.sh" in c for c in mine), f"dispatch through run-hook.sh, never a named interpreter: {mine}"
    ss = [h["command"] for g in settings["hooks"].get("SessionStart", []) for h in g["hooks"]]
    assert not any("shape-block.py" in c for c in ss), "inert in SessionStart, and silent about it"


def test_rule_carries_laws_5_and_6():
    text = (ROOT / RULE_PATH).read_text(encoding="utf-8").lower()
    for phrase, why in (
        ("never a heredoc", "rule 5 — the law itself"),
        ("write tool", "rule 5 — the remedy"),
        ("git commit -f", "rule 5 — the commit-message remedy"),
        ("leading assignment", "rule 6 — the law itself"),
        ("shape-block.py", "the enforcement is named, so a reader knows it is a block, not a nag"),
    ):
        assert phrase in text, f"{RULE_PATH} no longer states {phrase!r} ({why})"


if __name__ == "__main__":
    import traceback
    _fns = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    _failed = []
    for _name, _fn in _fns:
        try:
            _fn()
        except BaseException:
            _failed.append(_name)
            traceback.print_exc()
    print(f"-- {len(_fns) - len(_failed)}/{len(_fns)} passed --")
    if _failed:
        print(f"FAILED: {', '.join(_failed)}")
    sys.exit(1 if _failed else 0)
