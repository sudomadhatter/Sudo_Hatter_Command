"""closeout-nag.py — PostToolUse nag for close-out procedure & failed push/PR (SCC-381).

Tests positive triggers (push targeting main, failed git push, failed gh pr create, git merge main),
negative batteries (clean branch push, grep searches, heredocs, non-Bash tools),
and safety invariants (never blocks, fails open, registered through run-hook.sh, indexed).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / ".agents" / "hooks" / "closeout-nag.py"
SETTINGS = ROOT / ".claude" / "settings.json"
GIT_POLICY = ".agents/rules/git-policy.md"
SOP_DOC = "docs/_scc_sops_prds/workflows_testing_SOP.md"


def run_hook(command: str | None, tool_response: dict | str | None = None, raw: str | None = None):
    if raw is not None:
        payload = raw
    else:
        resp = tool_response if tool_response is not None else {"stdout": "", "stderr": "", "exit_code": 0}
        payload = json.dumps({
            "session_id": "test", "cwd": str(ROOT),
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
            "tool_response": resp,
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


# ── positive cases ─────────────────────────────────────────────────────────────

def test_push_to_main_triggers_nag():
    cases = [
        "git push origin main",
        "git push -u origin main",
        "git push origin HEAD:main",
        "cd /repo && git push origin main",
    ]
    for cmd in cases:
        rc, parsed = run_hook(cmd)
        assert rc == 0, f"must exit 0: {cmd}"
        text = nag_text(parsed)
        assert text, f"push to main produced no nag: {cmd}"
        assert GIT_POLICY in text, f"nag must cite {GIT_POLICY}"
        assert "NEVER PUSH DIRECTLY TO `main`" in text


def test_failed_git_push_triggers_nag():
    rc, parsed = run_hook("git push origin chore/my-fix",
                          tool_response={"stderr": "error: failed to push some refs to origin", "exit_code": 1})
    assert rc == 0
    text = nag_text(parsed)
    assert text, "failed git push produced no nag"
    assert "git push` command failed" in text
    assert GIT_POLICY in text
    assert "/smh-close-task-merge-tree" in text


def test_failed_gh_pr_create_triggers_nag():
    rc, parsed = run_hook("gh pr create --base main --head chore/my-fix --fill",
                          tool_response={"stderr": "a pull request already exists for chore/my-fix", "exit_code": 1})
    assert rc == 0
    text = nag_text(parsed)
    assert text, "failed gh pr create produced no nag"
    assert "gh pr create` command failed" in text
    assert "/smh-close-task-merge-tree" in text


def test_checkout_or_merge_main_triggers_nag():
    cases = [
        "git checkout main && git merge chore/foo",
        "git switch main",
    ]
    for cmd in cases:
        rc, parsed = run_hook(cmd)
        assert rc == 0
        text = nag_text(parsed)
        assert text, f"checkout/merge to main produced no nag: {cmd}"
        assert "main" in text


# ── negative battery: silence is required ─────────────────────────────────────

def test_clean_allowed_branch_push_is_silent():
    allowed = [
        "git push origin chore/SCC-10-fix",
        "git push -u origin claude/SCC-10-story",
        "git push origin epic/SCC-1-sprint",
    ]
    for cmd in allowed:
        rc, parsed = run_hook(cmd, tool_response={"stdout": "Everything up-to-date", "exit_code": 0})
        assert rc == 0
        assert not nag_text(parsed), f"successful branch push was nagged: {cmd}"


def test_grep_for_push_command_is_silent():
    rc, parsed = run_hook('grep -rn "git push origin main" .agents/')
    assert rc == 0
    assert not nag_text(parsed), "searching for git push was nagged"


def test_heredoc_is_silent():
    payload = "cat > script.sh << 'EOF'\ngit push origin main\nEOF"
    rc, parsed = run_hook(payload)
    assert rc == 0
    assert not nag_text(parsed), "heredoc containing push was nagged"


def test_non_bash_tool_is_silent():
    raw = json.dumps({
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {"command": "git push origin main"},
        "tool_response": {"exit_code": 1},
    })
    rc, parsed = run_hook(None, raw=raw)
    assert rc == 0
    assert not nag_text(parsed)


# ── invariants ────────────────────────────────────────────────────────────────

def test_never_blocks():
    cases = [
        ("git push origin main", {"exit_code": 1}),
        ("gh pr create --fill", {"exit_code": 1}),
        ("git status", {"exit_code": 0}),
    ]
    for cmd, resp in cases:
        rc, parsed = run_hook(cmd, tool_response=resp)
        assert rc == 0, f"nag must exit 0, got {rc}"
        if parsed:
            assert "decision" not in parsed
            hso = parsed.get("hookSpecificOutput") or {}
            assert "permissionDecision" not in hso
            assert "continue" not in parsed


def test_fails_open():
    rc, parsed = run_hook(None, raw="{broken json")
    assert rc == 0
    assert not nag_text(parsed)
    rc, parsed = run_hook(None, raw="")
    assert rc == 0
    assert not nag_text(parsed)


def test_hook_is_indexed():
    idx = (ROOT / ".agents" / "hooks" / "INDEX.md").read_text(encoding="utf-8")
    assert "closeout-nag.py" in idx, "closeout-nag.py must be indexed in .agents/hooks/INDEX.md"


def test_registered_in_settings():
    cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    post_tool = cfg.get("hooks", {}).get("PostToolUse", [])
    cmds = [h.get("command", "") for g in post_tool for h in g.get("hooks", [])]
    matched = [c for c in cmds if "closeout-nag.py" in c]
    assert matched, "closeout-nag.py is not registered in .claude/settings.json under PostToolUse"
    assert "run-hook.sh" in matched[0], f"must be wired via run-hook.sh, got: {matched[0]}"


if __name__ == "__main__":
    _fns = [(n, f) for n, f in sorted(globals().items())
            if n.startswith("test_") and callable(f)]
    _failed = []
    for _name, _fn in _fns:
        try:
            _fn()
        except BaseException as exc:
            _failed.append(_name)
            import traceback
            traceback.print_exc()
    print(f"-- {len(_fns) - len(_failed)}/{len(_fns)} passed --")
    if _failed:
        print(f"FAILED: {', '.join(_failed)}")
    sys.exit(1 if _failed else 0)
