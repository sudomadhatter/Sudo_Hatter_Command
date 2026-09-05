"""claude_permissions_apply.py — the operator-run merge into ~/.claude/settings.json (SCC-415).

Every case runs against FIXTURE files passed by --rendered / --user; the real user file is never
read or written by this test. run_all.py executes test files bare, so the __main__ harness at the
bottom is what makes this file COUNT.

⛔ THE LOAD-BEARING CASE is `test_never_touches_excluded_commands`: excluding a command removes it
from the sandbox and so LOSES the auto-approval — the operator's ruling is that this key is never
the fix, and an apply that drifted into it would re-create the prompts it exists to remove.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".agents" / "scripts" / "claude_permissions_apply.py"

TRACKED = ["Bash(ls:*)", "Bash(git status:*)", "Bash(python3 .agents/scripts/*)"]
USER_BEFORE = {
    "permissions": {"allow": ["Bash(ls:*)", "Bash(gh:*)"], "defaultMode": "auto"},
    "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo hi"}]}]},
    "sandbox": {
        "enabled": True, "autoAllowBashIfSandboxed": True,
        "filesystem": {"allowWrite": ["~/Sudo_Hatter_Command", "/tmp"]},
        "excludedCommands": ["acli", "acli *", "gh", "gh *"],
    },
    "theme": "dark",
}


def run(args: list[str], rendered: Path, user: Path):
    p = subprocess.run([sys.executable, str(SCRIPT), "--rendered", str(rendered), "--user", str(user), *args],
                       capture_output=True, text=True, cwd=str(ROOT), timeout=30, errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def seed(d: Path, user_doc: dict | None = USER_BEFORE) -> tuple[Path, Path]:
    rendered = d / "repo" / ".claude" / "settings.json"
    rendered.parent.mkdir(parents=True)
    rendered.write_text(json.dumps({"permissions": {"allow": TRACKED}}), encoding="utf-8")
    user = d / "home" / ".claude" / "settings.json"
    user.parent.mkdir(parents=True)
    if user_doc is not None:
        user.write_text(json.dumps(user_doc, indent=2), encoding="utf-8")
    return rendered, user


def test_status_is_read_only_and_names_what_would_change():
    with tempfile.TemporaryDirectory() as t:
        rendered, user = seed(Path(t))
        before = user.read_text(encoding="utf-8")
        rc, out = run(["--status"], rendered, user)
        assert rc == 0, out
        assert "2 row(s) to add" in out and "Bash(git status:*)" in out and "Bash(python3 .agents/scripts/*)" in out, out
        assert "4 allowWrite path(s) to add" in out, out
        assert "--apply" in out, "status must print the apply line the operator runs"
        assert user.read_text(encoding="utf-8") == before, "--status must write nothing"


def test_apply_merges_additively_widens_sandbox_and_backs_up():
    with tempfile.TemporaryDirectory() as t:
        rendered, user = seed(Path(t))
        rc, out = run(["--apply"], rendered, user)
        assert rc == 0, out
        after = json.loads(user.read_text(encoding="utf-8"))
        allow = after["permissions"]["allow"]
        assert "Bash(gh:*)" in allow, "a user-only row is KEPT without --prune (SCC-414)"
        for row in TRACKED:
            assert row in allow, f"tracked row missing after apply: {row}"
        assert allow.count("Bash(ls:*)") == 1, "a row present on both sides is not duplicated"
        aw = after["sandbox"]["filesystem"]["allowWrite"]
        for p in ("~/.cache", "~/.npm", "~/.local/share", "~/.config"):
            assert p in aw, f"sandbox path missing: {p}"
        assert "~/Sudo_Hatter_Command" in aw and "/tmp" in aw, "existing paths preserved"
        assert after["hooks"] == USER_BEFORE["hooks"] and after["theme"] == "dark", "unrelated keys untouched"
        assert after["permissions"]["defaultMode"] == "auto"
        assert user.with_suffix(".json.scc-backup").exists(), "a backup is written before the first change"
        assert json.loads(user.with_suffix(".json.scc-backup").read_text(encoding="utf-8")) == USER_BEFORE


def test_never_touches_excluded_commands():
    with tempfile.TemporaryDirectory() as t:
        rendered, user = seed(Path(t))
        run(["--apply"], rendered, user)
        after = json.loads(user.read_text(encoding="utf-8"))
        assert after["sandbox"]["excludedCommands"] == USER_BEFORE["sandbox"]["excludedCommands"], (
            "excludedCommands must be byte-identical across an apply — it is the opposite of the fix")
        src = SCRIPT.read_text(encoding="utf-8")
        assert "excludedCommands" in src and 'fs["allowWrite"]' in src, "the script writes allowWrite, and asserts excludedCommands unchanged"


def test_apply_is_idempotent():
    with tempfile.TemporaryDirectory() as t:
        rendered, user = seed(Path(t))
        run(["--apply"], rendered, user)
        first = user.read_text(encoding="utf-8")
        rc, out = run(["--apply"], rendered, user)
        assert rc == 0 and "already in sync" in out, out
        assert user.read_text(encoding="utf-8") == first, "a second apply must change nothing"


def test_prune_removes_user_only_rows_only_when_asked():
    with tempfile.TemporaryDirectory() as t:
        rendered, user = seed(Path(t))
        rc, out = run(["--apply", "--prune"], rendered, user)
        assert rc == 0 and "PRUNED" in out, out
        allow = json.loads(user.read_text(encoding="utf-8"))["permissions"]["allow"]
        assert "Bash(gh:*)" not in allow, "--prune deletes the user-only row"
        assert set(TRACKED) <= set(allow)


def test_absent_user_file_is_created_not_an_error():
    with tempfile.TemporaryDirectory() as t:
        rendered, user = seed(Path(t), user_doc=None)
        rc, out = run(["--status"], rendered, user)
        assert rc == 0 and "absent - will be created" in out, out
        rc, out = run(["--apply"], rendered, user)
        assert rc == 0 and user.exists(), out
        after = json.loads(user.read_text(encoding="utf-8"))
        assert set(TRACKED) <= set(after["permissions"]["allow"])
        assert "~/.cache" in after["sandbox"]["filesystem"]["allowWrite"]


def test_unreadable_user_file_is_exit_2_and_names_the_file():
    with tempfile.TemporaryDirectory() as t:
        rendered, user = seed(Path(t))
        user.write_text("{ not json", encoding="utf-8")
        rc, out = run(["--apply"], rendered, user)
        assert rc == 2 and str(user) in out, out
        assert user.read_text(encoding="utf-8") == "{ not json", "a file that does not parse is never overwritten"


def test_missing_tracked_list_is_exit_2():
    with tempfile.TemporaryDirectory() as t:
        rendered, user = seed(Path(t))
        rendered.unlink()
        rc, out = run(["--status"], rendered, user)
        assert rc == 2 and "does not exist" in out, out


def test_the_real_tracked_file_wires_shape_block_and_parses():
    """The script's whole premise is the tracked file; the hook that ends the prompts must be in it."""
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    cmds = [h["command"] for g in settings["hooks"]["PreToolUse"] for h in g["hooks"]]
    assert any("shape-block.py" in c for c in cmds), cmds


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
