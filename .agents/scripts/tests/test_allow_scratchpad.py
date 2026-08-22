"""The scratchpad auto-allow hook: what it may permit, and everything it must not (SCC-263).

⛔ THE TWELVE ESCAPES THIS FILE EXISTS TO KEEP DEAD. The first implementation asked "are all the
absolute paths I can find inside the sandbox?" - a deny-list over a surface it had to recognise
first. Five review lenses reproduced twelve escapes, every one the same shape: something not
recognised AS a path was treated as harmless. `rm -rf /<sb>/rt .agents` · `rm -rf .git # /<sb>` ·
`> "out.txt"` · `>| out.txt` · `>&out.txt` · `tar -C/<repo>` · `--out=/<repo>/x` · `"curl"` ·
`\\curl` · `/usr/bin/sudo` · `git -C /<sb>/r log && git reset --hard` · `cp /<sb>/x
/opt/homebrew/bin/git`. Block ESCAPES replays them; none may ever return `allow` again.

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
import os
import subprocess
import sys

from _harness import SCRIPTS, Cases

# ⛔ Imported, not re-typed. The constants below are pinned as CLOSED SETS, and a pin that
# restates the literal by hand drifts away from the module it claims to guard.
sys.path.insert(0, str(SCRIPTS.parent / "hooks"))
import importlib.util as _ilu  # noqa: E402
_spec = _ilu.spec_from_file_location(
    "allow_scratchpad", SCRIPTS.parent / "hooks" / "allow-scratchpad.py")
hook = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(hook)

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
            # These four were REFUSED before the second review and are ordinary harness spelling.
            # Each miss is a prompt this hook exists to remove, so they are pinned as ALLOWED.
            ("chmod -R with the mode after the flag", f"chmod -R 755 {SB}/rt"),
            ("head -n with a separate count", f"head -n 5 {SB}/out.txt"),
            ("tail -c with a separate count", f"tail -c 100 {SB}/out.txt"),
            ("-- end-of-options", f"rm -rf -- {SB}/rt"),
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

    # ── TRAVERSAL · rules 5 and 6, the two the REWRITE got wrong ────────────────────────
    # ⛔ A different class from the twelve above. These tokens ARE recognised as paths and DO
    # match the sandbox — they simply resolve outside it. `SANDBOX_RE.match` stops at
    # `scratchpad/` and never looks further, so `..` sailed through every rule and the session
    # pin passed because the real id genuinely is in the string. Two lenses reproduced it.
    if c.block("TRAVERSAL · rules 5 and 6 · a path that MATCHES but RESOLVES outside"):
        up = "/../../../../../.."
        for label, cmd in [
            ("rm through ..", f"rm -rf {SB}{up}/Users/sudohatter/Sudo_Hatter_Command/.agents"),
            ("the sandbox's own parent", f"rm -rf {SB}/.."),
            ("a write through ..", f"cp {SB}/evil {SB}{up}/Users/sudohatter/.zshenv"),
            ("execution through ..", f"bash {SB}{up}/Users/sudohatter/x.sh"),
            # ⛔ The `--flag=VALUE` split is the fix for v1's glued-path hole; traversal walked
            # straight through it, so the fix needed the same normalisation as everything else.
            ("traversal inside a --flag= value",
             f"python3 {SB}/h.py --out={SB}{up}/Users/x/AGENTS.md"),
            ("`.` interleaved with `..`", f"rm -rf {SB}/./../../"),
            ("the sibling-of-scratchpad case, spelled with ..", f"rm -rf {SB}/../tasks"),
        ]:
            _, out = call(cmd)
            c.check(f"TRAVERSAL · silent on {label}", silent(out), out.strip()[:160])
        # ⭐ ...and an interior `..` that stays INSIDE must still be allowed, or normalisation has
        # simply banned a legal path and taken the feature down with the hole.
        _, out = call(f"cat {SB}/a/../b")
        c.check("TRAVERSAL · still allows an interior .. that stays inside",
                allowed(out), out.strip()[:160])
        # Rule 6 — `ln` has an IMPLICIT destination no argument inspection can see.
        for label, cmd in [
            ("ln with one operand (writes into the CWD)", f"ln -sf {SB}/AGENTS.md"),
            ("ln at all, even two-operand and in-sandbox", f"ln -s {SB}/a {SB}/b"),
        ]:
            _, out = call(cmd)
            c.check(f"TRAVERSAL · silent on {label}", silent(out), out.strip()[:160])

    # ── B · rule 1 — one simple command, or nothing ─────────────────────────────────────
    if c.block("B · rule 1 · every shell metacharacter refuses the whole command"):
        for ch in "`$|&;<>()[]{}*?!#~'\"\\":
            _, out = call(f"cat {SB}/a{ch}b")
            c.check(f"B · silent on a command containing {ch!r}", silent(out), out.strip()[:120])
        _, out = call(f"cat {SB}/a\nrm -rf .agents")
        c.check("B · silent on a newline", silent(out), out.strip()[:120])
        # ⛔ NON-VACUOUS. The case above passes even with `\n` removed from FORBIDDEN, because
        # `.agents` fails rule 3 on its own. Here EVERY token of both commands is a sandbox path,
        # so only rule 1 can refuse it.
        _, out = call(f"cat {SB}/f\nbash {SB}/evil.sh")
        c.check("B · silent on a newline whose second command is ALL sandbox paths",
                silent(out), out.strip()[:120])
        _, out = call(f"cat {SB}/f\rbash {SB}/evil.sh")
        c.check("B · silent on a carriage return", silent(out), out.strip()[:120])

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
            # ⛔ On a LISTED executable, so rule 2 cannot mask the miss. The ESCAPES row for this
            # class uses `tar`, which is refused one rule earlier — leaving FLAG_RE untested.
            ("a path glued to a short flag", f"cp {SB}/payload -t{REPO}/.agents"),
            ("a path glued to a short flag, no dash-dash", f"python3 {SB}/h.py -o{REPO}/AGENTS.md"),
            ("flags only, naming no subject", "ls -la"),
            # ⛔ The value slot after a counting flag accepts DIGITS ONLY. Widen it to "anything"
            # and it becomes a free pass for one arbitrary token per command — a path the walk
            # never checks. Nothing else in this file isolates that slot.
            ("a path in a counting flag's value slot", f"head -n /etc/passwd {SB}/x"),
            ("a relative name in a counting flag's value slot", f"head -n .agents {SB}/x"),
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
            ("a `scratchpad.bak` sibling", f"rm -rf /private/tmp/claude-501/-P/{SID}/scratchpad.bak/x"),
            ("a too-short session segment", "rm -rf /private/tmp/claude-501/-P/abcdef/scratchpad/x"),
            ("an EMPTY project segment", f"rm -rf /private/tmp/claude-501//{SID}/scratchpad/x"),
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
        # ⛔ POSITIONAL, not containment. The pin used to be `f"/{sid}/" in token`, so a path under
        # ANOTHER live lane's session with our id as a leaf directory name satisfied it — a
        # sibling review's harness was writable. Two lenses found it.
        _, out = call(f"cp {SB}/p /private/tmp/claude-501/-Users-sudohatter-Sudo-Hatter-Command"
                      f"/ffffffff-0000-0000-0000-000000000000/scratchpad/{SID}/stomp")
        c.check("E · our session id as a LEAF of another session's path is refused",
                silent(out), out.strip()[:160])
        # ⛔ The uid is this process's, not `\\d+`: another account's tree is not our sandbox.
        _, out = call(f"rm -rf /private/tmp/claude-999/-P/{SID}/scratchpad/x")
        c.check("E · a FOREIGN uid's tree is refused", silent(out), out.strip()[:160])
        # With no session_id the shape alone still has to pin uid, depth and boundary.
        _, out = call("rm -rf /private/tmp/claude-501/-P/aaaabbbbccccdddd/scratchpad")
        c.check("E · ANOTHER session's scratchpad is refused", silent(out), out.strip()[:160])
        # ⛔ NO SESSION ID, NO GRANT. Judging by shape alone let ANY live lane's scratchpad
        # through, and an absent or non-string id used to DOWNGRADE to that shape-only judgement
        # rather than refuse. Both spellings are pinned here.
        _, out = call(f"rm -rf {SB}/rt", session=None)
        c.check("E · with NO session_id even our own scratchpad is refused",
                silent(out), out.strip()[:160])
        _, out = call("", raw=json.dumps({"tool_name": "Bash",
                                          "tool_input": {"command": f"rm -rf {SB}/rt"},
                                          "session_id": 12345}))
        c.check("E · a NON-STRING session_id is refused, not downgraded",
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

    # ── CLOSED · the sets are CLOSED, and adding to one is a change, not a tweak ────────
    # ⛔ A review hand-wrote 22 mutants against the previous cut and ALL 22 SURVIVED. The single
    # biggest reason: every set here was pinned only by examples. Adding `env`, `chown`, `find`
    # or `xargs` to ALLOWED left the whole suite green — and `env /<sb>/x` runs ANY binary, so
    # one silent addition undoes rule 2 entirely. Example-pinning is what let v1 pass 70/70 with
    # twelve live holes; these four assertions are the closed-set answer.
    if c.block("CLOSED · the allow-list, the ban-list and the value-flag table are closed sets"):
        c.check("CLOSED · ALLOWED is exactly this set",
                hook.ALLOWED == frozenset({
                    "mkdir", "rmdir", "rm", "cp", "mv", "touch", "chmod",
                    "ls", "cat", "head", "tail", "wc", "diff", "cmp", "file", "stat", "du",
                    "bash", "sh", "python3", "python", "node"}),
                f"changed: {sorted(hook.ALLOWED)}")
        c.check("CLOSED · `ln` is NOT on it (it has an implicit destination)",
                "ln" not in hook.ALLOWED, "ln is back on the allow-list")
        c.check("CLOSED · FORBIDDEN is exactly this set",
                hook.FORBIDDEN == set("`$|&;<>()[]{}*?!#~'\"\\\n\r"),
                f"changed: {sorted(hook.FORBIDDEN)}")
        c.check("CLOSED · VALUE_FLAGS is exactly this table",
                hook.VALUE_FLAGS == {"head": {"-n", "-c"}, "tail": {"-n", "-c"}, "wc": {"-L"}},
                f"changed: {hook.VALUE_FLAGS}")
        # Every allow-listed name gets ONE positive case: dropping a member is a silent friction
        # regression (the prompts come back) that example-based coverage cannot see.
        for name in sorted(hook.ALLOWED):
            cmd = (f"chmod 755 {SB}/x" if name == "chmod" else
                   f"{name} {SB}/a {SB}/b" if name in ("cp", "mv", "diff", "cmp") else
                   f"{name} {SB}/a")
            _, out = call(cmd)
            c.check(f"CLOSED · `{name}` is allowed on a sandbox path", allowed(out),
                    out.strip()[:120])

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
        # ⛔ `CLAUDE_PROJECT_DIR`, not `cwd`. run-hook.sh resolves its target as
        # `${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}/$SCRIPT`, so the env var is
        # consulted FIRST and `cwd=` only matters when it is unset. Under a real session it points
        # at the MAIN checkout, which carries its own copy of this hook — so this block measured
        # main's file while reporting on the lane's, the wrong-tree class `_harness._tree_guard`
        # exists to prevent (SCC-263 review, Literal-Correctness Hunter).
        p = subprocess.run(["sh", str(SCRIPTS.parent / "hooks" / "run-hook.sh"),
                            ".claude/hooks/allow-scratchpad.py"],
                           input=payload, capture_output=True, text=True,
                           cwd=str(ROOT), env={**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT)},
                           errors="replace")
        c.check("E2E · run-hook.sh dispatches it and it allows", allowed(p.stdout),
                (p.stdout + p.stderr).strip()[:200])
        c.check("E2E · exit 0 through the seam", p.returncode == 0, f"exit={p.returncode}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
