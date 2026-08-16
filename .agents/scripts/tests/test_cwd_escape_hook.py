"""A `cd` outside the workspace silently retargets every later relative path (SCC-182).

The Bash tool's cwd persists between calls UNTIL a command ends outside the workspace root.
The harness then resets cwd to the PRIMARY working directory - the MAIN checkout - and every
relative path after that reads main instead of the lane worktree. Nothing errors: the same path
exists in both trees and both are valid git repos, so the wrong answer is well-formed. It cost
this lane twice (a script written into main; main's 333-line file read as the lane's 463-line one).

A subshell does the work outside and leaves the parent's cwd intact - measured, not assumed:
    ( cd /tmp && ... )  -> cwd unchanged      cd /tmp && ...  -> reset to the main checkout
So the rule this hook enforces is narrow: a TOP-LEVEL `cd` out of the workspace. Everything else
- the subshell form, `git -C`, absolute paths - passes untouched.

⛔ It must FAIL OPEN. A guard that cannot parse its input has learned nothing, and a hook that
blocks on confusion is worse than the bug it chases (SCC-77: announce, never fail silently).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir

ROOT = SCRIPTS.parents[1]
HOOK = SCRIPTS.parent / "hooks" / "guard-cwd-escape.py"
WS = ""   # a REAL directory, built in main(): the hook fails open on a root that
          # does not exist, and a fixture that trips THAT path proves nothing.


def call(command: str, cwd: str = WS, tool: str = "Bash", raw: str | None = None) -> tuple[int, str]:
    payload = raw if raw is not None else json.dumps(
        {"tool_name": tool, "tool_input": {"command": command}, "cwd": cwd})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": WS}
    p = subprocess.run([sys.executable, str(HOOK)], input=payload, capture_output=True,
                       text=True, env=env, errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def blocked(out: str) -> bool:
    """True only for a well-formed `ask`. A crash prints a traceback, not a decision."""
    try:
        d = json.loads(out.strip() or "{}")
    except json.JSONDecodeError:
        return False
    return d.get("hookSpecificOutput", {}).get("permissionDecision") == "ask"


def main() -> int:
    global WS
    c = Cases("cwd escape hook (SCC-182)")
    tmp_ctx = TempDir()
    ws = tmp_ctx.__enter__()
    WS = str(ws)
    (ws / ".agents" / "scripts").mkdir(parents=True)
    (ws / ".claude" / "worktrees" / "lane-x").mkdir(parents=True)
    (ws.parent / "other-repo").mkdir(exist_ok=True)

    if c.block("M1 · a top-level cd out of the workspace is refused, with both remedies"):
        code, out = call("cd /tmp && ls")
        c.check("M1 `cd /tmp && ls` is refused", blocked(out), out.strip()[:200])
        c.check("M1 the hook still exits 0 (the decision is the payload, not the exit code)",
                code == 0, f"exit={code}")
        c.check("M1 the reason names the SUBSHELL remedy", "( cd" in out, out.strip()[:300])
        c.check("M1 the reason names the -C / absolute-path remedy",
                "-C" in out and "absolute" in out.lower(), out.strip()[:300])
        c.check("M1 the reason names the CONSEQUENCE, not just the rule",
                "main" in out.lower() and ("relative" in out.lower()), out.strip()[:300])

    if c.block("M2 · the sanctioned subshell form passes untouched"):
        for cmd in ("( cd /tmp && ls )",
                    "(cd /tmp && ls)",
                    "echo a && ( cd /tmp && ls ) && echo b"):
            code, out = call(cmd)
            c.check(f"M2 allowed: {cmd}", not blocked(out) and code == 0,
                    f"exit={code} {out.strip()[:150]}")

    if c.block("M3 · a cd that stays inside the workspace passes untouched"):
        for cmd in (f"cd {WS}/.agents && ls",
                    f"cd {WS} && ls",
                    "cd .agents/scripts && ls",
                    f"cd {WS}/.claude/worktrees/lane-x && python3 t.py"):
            code, out = call(cmd)
            c.check(f"M3 allowed: {cmd}", not blocked(out) and code == 0,
                    f"exit={code} {out.strip()[:150]}")

    if c.block("M4 · every other way of leaving the workspace is caught"):
        for cmd in ("cd", "cd ~", "cd ~/Downloads", "cd -", "cd $HOME", "cd ..",
                    "pushd /tmp", f"cd {Path(WS).parent}/other-repo && git status",
                    # dir BOUNDARY: a sibling whose name merely EXTENDS the root is OUTSIDE.
                    # `startswith(root)` without the trailing `/` reads it as inside.
                    f"cd {WS}-sibling && ls",
                    # an apostrophe in a COMMENT opens a quote that would swallow the rest of
                    # the command — including the real `cd` — unless comments are skipped first.
                    "ls   # don't do it this way\ncd /tmp && ls"):
            code, out = call(cmd)
            c.check(f"M4 refused: {cmd!r}", blocked(out), out.strip()[:160])

    if c.block("M5 · a `cd` that is not a COMMAND is not a cd"):
        quiet = {
            "inside double quotes": 'echo "cd /tmp"',
            "inside single quotes": "grep -n 'cd /tmp' notes.md",
            "a comment": "ls   # cd /tmp would be wrong here",
            "a heredoc body": "cat > f.sh <<'EOF'\ncd /tmp\nEOF",
            "a substring of another word": "./mycd /tmp && ls",
            "an argument, not the command": "echo cd /tmp",
            "a path that merely contains cd": "ls /var/cd/tmp",
        }
        for label, cmd in quiet.items():
            code, out = call(cmd)
            c.check(f"M5 not a cd: {label}", not blocked(out) and code == 0,
                    f"exit={code} {out.strip()[:150]}")

    if c.block("M6 · the guard FAILS OPEN on anything it cannot judge"):
        for label, kw in (("unparseable stdin", {"raw": "not json at all"}),
                          ("empty stdin", {"raw": ""}),
                          ("no command key", {"raw": json.dumps({"tool_name": "Bash",
                                                                 "tool_input": {}})}),
                          ("a different tool", {"command": "cd /tmp", "tool": "Read"})):
            code, out = call(**kw) if "command" in kw else call("", **kw)
            c.check(f"M6 allowed on {label}", not blocked(out) and code == 0,
                    f"exit={code} {out.strip()[:120]}")
        env = {**os.environ}
        env.pop("CLAUDE_PROJECT_DIR", None)
        p = subprocess.run([sys.executable, str(HOOK)],
                           input=json.dumps({"tool_name": "Bash",
                                             "tool_input": {"command": "cd /tmp"}}),
                           capture_output=True, text=True, env=env, errors="replace")
        c.check("M6 allowed when the workspace root cannot be resolved",
                not blocked(p.stdout or "") and p.returncode == 0,
                f"exit={p.returncode} {(p.stdout or p.stderr or '').strip()[:150]}")
        c.check("M6 no traceback ever reaches the transcript",
                "Traceback" not in (p.stdout or "") + (p.stderr or ""),
                (p.stderr or "").strip()[:160])

    if c.block("M7 · the hook is WIRED, on the run-hook seam"):
        s = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        pre = s.get("hooks", {}).get("PreToolUse", [])
        bash = [h for e in pre if e.get("matcher") == "Bash" for h in e.get("hooks", [])]
        cmds = [h.get("command", "") for h in bash]
        c.check("M7 a PreToolUse/Bash entry runs guard-cwd-escape.py",
                any("guard-cwd-escape.py" in x for x in cmds), f"{cmds}")
        c.check("M7 it goes through run-hook.sh, never a bare interpreter name (the exit-127 class)",
                all("run-hook.sh" in x for x in cmds if "guard-cwd-escape.py" in x), f"{cmds}")
        c.check("M7 the existing push-approval hook is still wired beside it",
                any("require-push-approval.py" in x for x in cmds), f"{cmds}")
        c.check("M7 the deployed .claude/hooks copy matches the canonical .agents/hooks source",
                (ROOT / ".claude/hooks/guard-cwd-escape.py").is_file()
                and (ROOT / ".claude/hooks/guard-cwd-escape.py").read_bytes() == HOOK.read_bytes(),
                "deployed copy missing or drifted")

    tmp_ctx.__exit__()
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
