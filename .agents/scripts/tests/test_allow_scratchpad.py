"""The scratchpad auto-allow hook: what it may permit, and everything it must not (SCC-263).

⛔ THE TWELVE ESCAPES THIS FILE EXISTS TO KEEP DEAD. The first implementation asked "are all the
absolute paths I can find inside the sandbox?" - a deny-list over a surface it had to recognise
first. Five review lenses reproduced twelve escapes, every one the same shape: something not
recognised AS a path was treated as harmless. `rm -rf /<sb>/rt .agents` · `rm -rf .git # /<sb>` ·
`> "out.txt"` · `>| out.txt` · `>&out.txt` · `tar -C/<repo>` · `--out=/<repo>/x` · `"curl"` ·
`\\curl` · `/usr/bin/sudo` · `git -C /<sb>/r log && git reset --hard` · `cp /<sb>/x
/opt/homebrew/bin/git`. Block ESCAPES replays all twelve; none may ever return `allow` again.

The rewrite inverted the question into an allow-list of SHAPES - no metacharacters, a bare-name
executable from a literal list, every non-flag token an absolute path inside THIS session's
scratchpad - so most of those escapes are now unreachable by construction rather than by a
pattern. The block still runs them because "unreachable by construction" is a claim, and this is
what makes it an assertion.

⛔ THE HOOK HAS EXACTLY TWO LEGAL OUTPUTS: `allow`, or SILENCE. Never `ask`, never `deny`.
`ask` is auto-DENY in non-interactive mode; `deny` is worse. A convenience hook that emitted
either would block the very lanes it exists to unblock. `allowed()` and `silent()` below are
deliberately NOT each other's negation, so an `ask` or a `deny` fails both.

⭐ WHY THE FIXTURES BUILD NO DIRECTORIES. The hook judges the command STRING and never touches
disk, so a fixture path only has to MATCH the sandbox shape. Block WIRING is the exception and
says so - it reads the real repo files.
"""
from __future__ import annotations

import json
import subprocess
import sys

from _harness import SCRIPTS, Cases

ROOT = SCRIPTS.parents[1]
HOOK = SCRIPTS.parent / "hooks" / "allow-scratchpad.py"

SID = "697c65e7-558e-4bf4-975f-ad474d8bb76d"
SB = f"/private/tmp/claude-501/-Users-sudohatter-Sudo-Hatter-Command/{SID}/scratchpad"
# macOS symlinks `/tmp` -> `/private/tmp`; both spellings reach the same bytes.
SB_ALT = f"/tmp/claude-501/-Users-sudohatter-Sudo-Hatter-Command/{SID}/scratchpad"
REPO = "/Users/sudohatter/Sudo_Hatter_Command"


def call(command: str, tool: str = "Bash", raw: str | None = None,
         session: str | None = SID) -> tuple[int, str]:
    if raw is None:
        payload: dict = {"tool_name": tool, "tool_input": {"command": command}}
        if session is not None:
            payload["session_id"] = session
        raw = json.dumps(payload)
    p = subprocess.run([sys.executable, str(HOOK)], input=raw,
                       capture_output=True, text=True, errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def decision(out: str) -> str | None:
    """The decision, or None for silence. A traceback is silence, not a decision."""
    try:
        d = json.loads(out.strip() or "{}")
    except json.JSONDecodeError:
        return None
    return d.get("hookSpecificOutput", {}).get("permissionDecision")


def allowed(out: str) -> bool:
    return decision(out) == "allow"


def silent(out: str) -> bool:
    """⛔ NOT `not allowed()`. An `ask` or a `deny` is neither allow nor silence, and collapsing
    the two would let the outputs this hook must never produce pass every decline case here."""
    return out.strip() == ""


def main() -> int:
    c = Cases("scratchpad auto-allow hook (SCC-263)")

    # ── A · the traffic the hook exists to permit ────────────────────────────────────────
    if c.block("A · real harness shapes are ALLOWED"):
        for label, cmd in [
            ("mkdir -p, two dirs", f"mkdir -p {SB}/rt/notarepo {SB}/rt/lane"),
            ("bash a script", f"bash {SB}/rt/run.sh"),
            ("python3 with spaced flags", f"python3 {SB}/rt/h.py --repo {SB}/a --worktree {SB}/b"),
            ("python3 with --flag=path", f"python3 {SB}/rt/h.py --repo={SB}/a"),
            ("rm -rf", f"rm -rf {SB}/rt"),
            ("chmod +x", f"chmod +x {SB}/rt/run.sh"),
            ("chmod 755", f"chmod 755 {SB}/rt/run.sh"),
            ("cat", f"cat {SB}/out.txt"),
            ("head -20", f"head -20 {SB}/out.txt"),
            ("cp within the sandbox", f"cp {SB}/a {SB}/b"),
            ("the /tmp spelling", f"bash {SB_ALT}/rt/run.sh"),
        ]:
            code, out = call(cmd)
            c.check(f"A · {label} is allowed", allowed(out), out.strip()[:160])
            c.check(f"A · {label} exits 0", code == 0, f"exit={code}")

    # ── ESCAPES · the twelve the lenses reproduced against v1 ───────────────────────────
    if c.block("ESCAPES · every hole the review found stays dead"):
        for label, cmd in [
            ("a relative arg beside a sandbox path", f"rm -rf {SB}/rt .agents"),
            ("a sandbox path inside a # COMMENT", f"rm -rf .git # cleanup under {SB}/rt"),
            ("a QUOTED redirect target", f'bash {SB}/rt/run.sh > "out.txt"'),
            ("a noclobber redirect", f"bash {SB}/rt/run.sh >| out.txt"),
            (">&FILE, which writes a file not an fd", f"bash {SB}/rt/run.sh >&out.txt"),
            ("a path glued to a short flag", f"tar -C{REPO} -xf {SB}/payload.tar"),
            ("a path glued to a long flag", f"python3 {SB}/h.py --out={REPO}/AGENTS.md"),
            ("a QUOTED deny word", f'"curl" -so {SB}/f example.com/p'),
            ("a backslash-escaped deny word", f"\\curl -so {SB}/f example.com/p"),
            ("an absolutely-pathed sudo", f"/usr/bin/sudo rm -rf {SB}"),
            ("an absolutely-pathed git", f"/usr/bin/git clean -fdx && ls {SB}"),
            ("one -C licensing a second bare git", f"git -C {SB}/repo log && git reset --hard"),
            ("a write into a system prefix by ARGUMENT", f"cp {SB}/payload /opt/homebrew/bin/git"),
            ("tilde-USER expansion", f"cp {SB}/x.sh ~sudohatter/.ssh/authorized_keys"),
            ("a heredoc body", f"python3 - <<'EOF'\nopen('AGENTS.md','w')\nEOF\ncat {SB}/f"),
            ("a newline-chained second command", f"bash {SB}/r.sh\nrm -rf .agents"),
        ]:
            _, out = call(cmd)
            c.check(f"ESCAPES · silent on {label}", silent(out), out.strip()[:160])

    # ── B · rule 1 — one simple command, or nothing ─────────────────────────────────────
    if c.block("B · rule 1 · every shell metacharacter refuses the whole command"):
        for ch in "`$|&;<>()[]{}*?!#~'\"\\":
            _, out = call(f"cat {SB}/a{ch}b")
            c.check(f"B · silent on a command containing {ch!r}", silent(out), out.strip()[:120])
        _, out = call(f"cat {SB}/a\nrm -rf .agents")
        c.check("B · silent on a newline", silent(out), out.strip()[:120])

    # ── C · rule 2 — a bare name from the list ──────────────────────────────────────────
    if c.block("C · rule 2 · the executable is a bare allow-listed name"):
        for label, cmd in [
            ("an unlisted executable", f"tar -xf {SB}/p.tar"),
            ("git, which is never listed", f"git status {SB}"),
            ("curl, which is never listed", f"curl {SB}/f"),
            ("an ABSOLUTE path to a listed name", f"/bin/cat {SB}/f"),
            ("an absolute path to an interpreter", f"/usr/bin/env python3 {SB}/x.py"),
        ]:
            _, out = call(cmd)
            c.check(f"C · silent on {label}", silent(out), out.strip()[:160])

    # ── D · rule 3 — every non-flag token is a sandboxed absolute path ──────────────────
    if c.block("D · rule 3 · a non-flag token that is not a sandboxed path refuses"):
        for label, cmd in [
            ("a bare relative name", f"cp {SB}/x conftest.py"),
            ("a relative path with a slash", f"cp {SB}/x tests/conftest.py"),
            ("an absolute path outside", f"cp {SB}/x {REPO}/AGENTS.md"),
            ("a system path as a write target", f"cp {SB}/x /usr/local/bin/gh"),
            ("a --flag= value outside", f"python3 {SB}/h.py --out={REPO}/x"),
            ("flags only, naming no subject", "ls -la"),
        ]:
            _, out = call(cmd)
            c.check(f"D · silent on {label}", silent(out), out.strip()[:160])

    # ── E · rule 4 — the SESSION's scratchpad, not the uid's ───────────────────────────
    if c.block("E · rule 4 · the sandbox root is this session's scratchpad"):
        for label, cmd in [
            ("the uid root", "rm -rf /private/tmp/claude-501/"),
            ("a project dir above the session", "rm -rf /private/tmp/claude-501/-Some-Proj/"),
            ("another session's scratchpad",
             "rm -rf /private/tmp/claude-501/-P/aaaaaaaa-bbbb-cccc/scratchpad"),
            ("a sibling of scratchpad", f"rm -rf /private/tmp/claude-501/-P/{SID}/tasks"),
            ("the claude-501x near-miss",
             f"rm -rf /private/tmp/claude-501x/-P/{SID}/scratchpad/rt"),
            # ⛔ `scratchpad` must end at a boundary. Without `(?:/|$)` a SIBLING whose name
            # merely starts with it — `scratchpadX` — reads as inside the sandbox.
            ("a sibling whose name merely starts with scratchpad",
             f"rm -rf /private/tmp/claude-501/-Users-sudohatter-Sudo-Hatter-Command/{SID}"
             f"/scratchpadX/rt"),
            # ⛔ `sandboxed()` must anchor with match(), never search(): a path merely CONTAINING
            # the sandbox shape is not inside it. This mutant survived 70/70 in the v1 suite.
            ("a path merely CONTAINING the shape",
             f"rm -rf {REPO}/backup/private/tmp/claude-501/-P/{SID}/scratchpad/x"),
        ]:
            _, out = call(cmd)
            c.check(f"E · silent on {label}", silent(out), out.strip()[:160])
        # The session pin: the same path, under a different session's id.
        _, out = call(f"rm -rf {SB}/rt", session="ffffffff-0000-0000-0000-000000000000")
        c.check("E · a path from a DIFFERENT session is refused", silent(out), out.strip()[:160])
        # ...and when no session id arrives, the shape alone still has to hold.
        _, out = call(f"rm -rf {SB}/rt", session=None)
        c.check("E · with no session_id the shape alone still allows a real scratchpad",
                allowed(out), out.strip()[:160])
        _, out = call("rm -rf /private/tmp/claude-501/", session=None)
        c.check("E · with no session_id the uid root is STILL refused",
                silent(out), out.strip()[:160])

    # ── F · the one non-flag, non-path token the hook accepts ──────────────────────────
    if c.block("F · the chmod mode token is scoped to chmod, and to first position"):
        _, out = call(f"chmod u+rw,go-w {SB}/x")
        c.check("F · a symbolic mode is allowed", allowed(out), out.strip()[:160])
        _, out = call(f"cp +x {SB}/x")
        c.check("F · `+x` is NOT a free token for other commands", silent(out), out.strip()[:160])
        _, out = call(f"chmod {SB}/x +x")
        c.check("F · a mode in second position refuses", silent(out), out.strip()[:160])

    # ── G · the two guarantees that make the hook safe to install at all ───────────────
    if c.block("G · ⛔ NEVER `ask`, NEVER `deny`, ALWAYS exit 0"):
        probes = [
            ("malformed JSON", "{not json at all"),
            ("empty stdin", ""),
            ("no tool_input", json.dumps({"tool_name": "Bash"})),
            ("a null tool_input", json.dumps({"tool_name": "Bash", "tool_input": None})),
            ("a non-string command",
             json.dumps({"tool_name": "Bash", "tool_input": {"command": 42}})),
            ("a whitespace-only command",
             json.dumps({"tool_name": "Bash", "tool_input": {"command": "   "}})),
        ]
        for label, raw in probes:
            code, out = call("", raw=raw)
            # ⛔ `silent`, not `decision != "ask"`. The v1 suite asserted only the weaker form,
            # and a mutant that printed `deny` from the exception handler survived it — turning
            # a convenience hook into a hard blocker on every Bash call.
            c.check(f"G · `{label}` is SILENT", silent(out), out.strip()[:160])
            c.check(f"G · `{label}` exits 0", code == 0, f"exit={code}")
        # ⛔ Non-vacuous: this payload carries a REAL allowable command, so silence can only come
        # from the tool_name guard. The v1 version passed `file_path` instead, so the empty-command
        # guard produced the silence and deleting the tool_name check survived the whole suite.
        _, out = call("", raw=json.dumps(
            {"tool_name": "Write", "tool_input": {"command": f"ls {SB}"}, "session_id": SID}))
        c.check("G · a non-Bash tool carrying an allowable command is still silent",
                silent(out), out.strip()[:160])

    # ── WIRING · reads the REAL repo files, not a fixture ──────────────────────────────
    if c.block("WIRING · the deployed copy and the settings entry agree with the master"):
        master = ROOT / ".agents/hooks/allow-scratchpad.py"
        deployed = ROOT / ".claude/hooks/allow-scratchpad.py"
        c.check("WIRING · the master exists", master.is_file(), str(master))
        c.check("WIRING · the deployed copy exists", deployed.is_file(), str(deployed))
        if master.is_file() and deployed.is_file():
            same = master.read_bytes() == deployed.read_bytes()
            c.check("WIRING · deployed copy is byte-identical to the master", same,
                    "" if same else "they have diverged — re-run /smh-sync-agents")
        settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        groups = [g for g in settings["hooks"]["PreToolUse"] if g.get("matcher") == "Bash"]
        c.check("WIRING · there is exactly one PreToolUse Bash matcher", len(groups) == 1,
                f"found {len(groups)}")
        cmds = [h["command"] for h in groups[0]["hooks"]] if groups else []
        mine = [x for x in cmds if "allow-scratchpad.py" in x]
        c.check("WIRING · the hook is wired into it", len(mine) == 1, str(cmds))
        c.check("WIRING · it is FIRST in the chain",
                bool(cmds) and "allow-scratchpad.py" in cmds[0], str(cmds[:1]))
        # ⛔ The interpreter seam. `.claude/settings.json` is shared across a Mac with no bare
        # `python` and a PC with no `python3`; naming either directly is the SCC-77 exit-127 bug,
        # which is silent. `run-hook.sh` probes. A mutant naming `python` survived the v1 suite.
        c.check("WIRING · it is dispatched through run-hook.sh, never a named interpreter",
                all("run-hook.sh" in x for x in mine), str(mine))
        # ⛔ The stray-copy check. This hook was first wired into SessionStart by mistake, where it
        # is inert and every symptom is identical to a hook that works.
        ss = [h["command"] for g in settings["hooks"].get("SessionStart", []) for h in g["hooks"]]
        c.check("WIRING · it is NOT also wired into SessionStart (inert there, and silent)",
                not any("allow-scratchpad.py" in x for x in ss), str(ss))

    # ── E2E · through the seam Claude Code actually uses ──────────────────────────────
    if c.block("E2E · the hook answers correctly through run-hook.sh"):
        payload = json.dumps(
            {"tool_name": "Bash", "tool_input": {"command": f"bash {SB}/rt/run.sh"},
             "session_id": SID})
        p = subprocess.run(["sh", str(SCRIPTS.parent / "hooks" / "run-hook.sh"),
                            ".claude/hooks/allow-scratchpad.py"],
                           input=payload, capture_output=True, text=True,
                           cwd=str(ROOT), errors="replace")
        c.check("E2E · run-hook.sh dispatches it and it allows", allowed(p.stdout),
                (p.stdout + p.stderr).strip()[:200])
        c.check("E2E · exit 0 through the seam", p.returncode == 0, f"exit={p.returncode}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
