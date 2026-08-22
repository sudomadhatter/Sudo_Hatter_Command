"""The scratchpad auto-allow hook: what it may permit, and everything it must not (SCC-263).

Every verification lane builds a throwaway harness under the session scratchpad and runs it -
twenty-odd approvals per `/smh-code-review`, for a directory that dies with the session. Bash
permission rules match the COMMAND STRING by prefix and the scratchpad path carries a per-session
UUID, so settings cannot pre-grant it. A PreToolUse hook is the only layer that sees the resolved
command. This file is the contract on what that hook is allowed to wave through.

⛔ THE HOOK HAS EXACTLY TWO LEGAL OUTPUTS: `allow`, or SILENCE. Never `ask`.
`ask` is auto-DENY in non-interactive mode, so a convenience hook that emitted it would block the
very lanes it exists to unblock - and it would do so wearing the word "ask", which reads in a
transcript like a question that was never asked. `allowed()` below therefore refuses to treat
anything but a well-formed `allow` as permission, and block H asserts the `ask` ban directly.

⭐ WHY MOST BLOCKS BUILD NO DIRECTORIES. The hook judges the command STRING and never touches
disk, so a fixture path only has to MATCH the sandbox shape, not exist. Blocks that do read real
files (I) say so.

Retrofit honesty: blocks A-I were written against a working hook and passed on their first run
(`test-debt-stories-are-characterization`). Block J was written RED - rule 7 did not exist - and
is the only part of this file that ever failed for the right reason. The mutation sweep is what
keeps the other nine from being decorative.
"""
from __future__ import annotations

import json
import subprocess
import sys

from _harness import SCRIPTS, Cases

ROOT = SCRIPTS.parents[1]
HOOK = SCRIPTS.parent / "hooks" / "allow-scratchpad.py"

# A path with the sandbox SHAPE. It need not exist - see the module docstring.
SB = "/private/tmp/claude-501/-Users-sudohatter-Sudo-Hatter-Command/697c65e7/scratchpad"
# The `/tmp` spelling of the same tree: macOS symlinks `/tmp` -> `/private/tmp`, so both reach
# the same bytes and a hook that recognised only one would decline half of its own traffic.
SB_ALT = "/tmp/claude-501/-Users-sudohatter-Sudo-Hatter-Command/697c65e7/scratchpad"
REPO = "/Users/sudohatter/Sudo_Hatter_Command"


def call(command: str, tool: str = "Bash", raw: str | None = None) -> tuple[int, str]:
    payload = raw if raw is not None else json.dumps(
        {"tool_name": tool, "tool_input": {"command": command}})
    p = subprocess.run([sys.executable, str(HOOK)], input=payload,
                       capture_output=True, text=True, errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def decision(out: str) -> str | None:
    """The hook's decision, or None for silence. A traceback is silence, not a decision."""
    try:
        d = json.loads(out.strip() or "{}")
    except json.JSONDecodeError:
        return None
    return d.get("hookSpecificOutput", {}).get("permissionDecision")


def allowed(out: str) -> bool:
    return decision(out) == "allow"


def silent(out: str) -> bool:
    """⛔ Not `not allowed()`. An `ask` is neither allow nor silence, and collapsing the two
    would let the one output this hook must never produce pass every decline case in the file."""
    return out.strip() == ""


def main() -> int:
    c = Cases("scratchpad auto-allow hook (SCC-263)")

    # ── A · the shapes that caused the twenty prompts, all of them permitted ───────────────
    if c.block("A · real /smh-code-review harness shapes are ALLOWED"):
        for label, cmd in [
            ("mkdir", f"mkdir -p {SB}/rt/notarepo {SB}/rt/lane"),
            ("bash a script", f"bash {SB}/rt/run.sh"),
            ("python3 with flags", f"python3 {SB}/rt/harness.py --repo {SB}/rt/notarepo "
                                   f"--worktree {SB}/rt/lane"),
            ("rm -rf", f"rm -rf {SB}/rt"),
            ("absolute interpreter", f"/usr/bin/env python3 {SB}/probe.py"),
            ("chmod then run", f"chmod +x {SB}/rt/run.sh && bash {SB}/rt/run.sh"),
            ("git with -C inside", f"git -C {SB}/rt/repo status"),
            ("pipe to a coreutil", f"cat {SB}/out.txt | head -20"),
            ("the /tmp spelling", f"bash {SB_ALT}/rt/run.sh"),
        ]:
            code, out = call(cmd)
            c.check(f"A · {label} is allowed", allowed(out), out.strip()[:160])
            c.check(f"A · {label} exits 0", code == 0, f"exit={code}")

    # ── B · rule 1 — no sandbox path means this is ordinary repo work ──────────────────────
    if c.block("B · rule 1 · a command naming NO sandbox path is left alone"):
        for cmd in ["rm -rf .agents", "git status",
                    "python3 -m py_compile .agents/hooks/allow-scratchpad.py"]:
            _, out = call(cmd)
            c.check(f"B · silent on `{cmd}`", silent(out), out.strip()[:160])

    # ── C · rule 2 — one path outside is one path too many ────────────────────────────────
    if c.block("C · rule 2 · ANY absolute path outside the sandbox declines the whole command"):
        for label, cmd in [
            ("a read out of the repo", f"cp {REPO}/AGENTS.md {SB}/"),
            ("a delete that also eats the repo", f"rm -rf {SB} {REPO}/.git"),
            ("an outside write target", f"cp {SB}/out.txt /etc/hosts"),
        ]:
            _, out = call(cmd)
            c.check(f"C · silent on {label}", silent(out), out.strip()[:160])
        # The near-miss that proves the boundary is a boundary and not a prefix-match:
        # `claude-501x` shares every character of the real root up to the digits.
        _, out = call("rm -rf /private/tmp/claude-501x/scratchpad/rt")
        c.check("C · `claude-501x` is NOT the sandbox (boundary, not prefix)",
                silent(out), out.strip()[:160])

    # ── D · rule 3 — a relative escape from inside lands outside ──────────────────────────
    if c.block("D · rule 3 · a `..` segment declines"):
        _, out = call(f"rm -rf {SB}/../../..")
        c.check("D · silent on a `..` escape", silent(out), out.strip()[:160])

    # ── E · rule 4 — an unexpanded path is a path the hook cannot judge ───────────────────
    if c.block("E · rule 4 · shell expansion the hook cannot resolve declines"):
        for label, cmd in [
            ("a project-dir variable", f"cp $CLAUDE_PROJECT_DIR/AGENTS.md {SB}/"),
            ("command substitution", f"bash {SB}/$(whoami).sh"),
            ("backticks", f"bash {SB}/`whoami`.sh"),
            ("a tilde home path", f"cp ~/.ssh/id_rsa {SB}/"),
        ]:
            _, out = call(cmd)
            c.check(f"E · silent on {label}", silent(out), out.strip()[:160])

    # ── F · rule 5 — reach past the filesystem and the paths stop mattering ───────────────
    if c.block("F · rule 5 · egress and privilege escalation decline"):
        for label, cmd in [
            ("curl", f"curl -o {SB}/x.tgz https://example.com/x.tgz"),
            ("wget", f"wget -O {SB}/x.tgz https://example.com/x.tgz"),
            ("sudo", f"sudo rm -rf {SB}"),
            ("rsync to a remote", f"rsync -a {SB}/ remote:/tmp/"),
            ("ssh", f"ssh host 'cat > {SB}/x'"),
        ]:
            _, out = call(cmd)
            c.check(f"F · silent on {label}", silent(out), out.strip()[:160])

    # ── G · rule 6 — bare `git` reads the AMBIENT repo, sandbox paths notwithstanding ─────
    if c.block("G · rule 6 · `git` without a sandboxed `-C` declines"):
        for label, cmd in [
            ("git add of a sandbox file", f"git add {SB}/out.txt"),
            ("git -C pointing at the repo", f"git -C {REPO} commit -F {SB}/msg.txt"),
        ]:
            _, out = call(cmd)
            c.check(f"G · silent on {label}", silent(out), out.strip()[:160])

    # ── H · the ban that makes the hook safe to install at all ───────────────────────────
    if c.block("H · ⛔ it NEVER emits `ask`, and NEVER exits non-zero"):
        probes = [
            ("well-formed allow", None, json.dumps(
                {"tool_name": "Bash", "tool_input": {"command": f"ls {SB}"}})),
            ("a declined command", None, json.dumps(
                {"tool_name": "Bash", "tool_input": {"command": "rm -rf .agents"}})),
            ("malformed JSON", None, "{not json at all"),
            ("empty stdin", None, ""),
            ("no tool_input", None, json.dumps({"tool_name": "Bash"})),
            ("a non-Bash tool", None, json.dumps(
                {"tool_name": "Write", "tool_input": {"file_path": f"{SB}/x"}})),
            ("an empty command", None, json.dumps(
                {"tool_name": "Bash", "tool_input": {"command": "   "}})),
        ]
        for label, _unused, raw in probes:
            code, out = call("", raw=raw)
            c.check(f"H · `{label}` never yields ask", decision(out) != "ask", out.strip()[:160])
            c.check(f"H · `{label}` exits 0", code == 0, f"exit={code}")
        # A non-Bash tool must be silence specifically - the hook is registered on a Bash
        # matcher today, but a matcher is configuration and this is the code's own guarantee.
        _, out = call("", raw=json.dumps(
            {"tool_name": "Write", "tool_input": {"file_path": f"{SB}/x"}}))
        c.check("H · a non-Bash tool is silence, not allow", silent(out), out.strip()[:160])

    # ── I · the wiring — reads the REAL repo files, not a fixture ────────────────────────
    if c.block("I · the deployed copy and the settings wiring agree with the master"):
        master = ROOT / ".agents/hooks/allow-scratchpad.py"
        deployed = ROOT / ".claude/hooks/allow-scratchpad.py"
        c.check("I · the master exists", master.is_file(), str(master))
        c.check("I · the deployed copy exists", deployed.is_file(), str(deployed))
        if master.is_file() and deployed.is_file():
            c.check("I · deployed copy is byte-identical to the master",
                    master.read_bytes() == deployed.read_bytes(),
                    "they have diverged — re-run /smh-sync-agents")
        settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        bash_groups = [g for g in settings["hooks"]["PreToolUse"] if g.get("matcher") == "Bash"]
        c.check("I · there is a PreToolUse Bash matcher", len(bash_groups) == 1,
                f"found {len(bash_groups)}")
        if bash_groups:
            cmds = [h["command"] for h in bash_groups[0]["hooks"]]
            c.check("I · the hook is wired into it",
                    any("allow-scratchpad.py" in x for x in cmds), str(cmds))
            # FIRST, so its `allow` is on record before the later gates speak. A sibling
            # `ask`/`deny` still wins - that ordering is the safe direction and is intended.
            c.check("I · it is FIRST in the chain",
                    bool(cmds) and "allow-scratchpad.py" in cmds[0], str(cmds[:1]))
        # ⛔ The stray-copy check. This hook was first wired into `SessionStart` by mistake,
        # where it is inert: it reads a payload with no `tool_name`, returns silently, and
        # every symptom is identical to a hook that is working. Nothing else would catch it.
        ss = [h["command"] for g in settings["hooks"].get("SessionStart", [])
              for h in g["hooks"]]
        c.check("I · it is NOT also wired into SessionStart (inert there, and silent about it)",
                not any("allow-scratchpad.py" in x for x in ss), str(ss))

    # ── J · rule 7 — the hole the self-audit found (written RED) ─────────────────────────
    if c.block("J · rule 7 · a redirect target outside the sandbox declines"):
        for label, cmd in [
            ("a RELATIVE redirect", f"bash {SB}/rt/run.sh > out.txt"),
            ("a relative append", f"bash {SB}/rt/run.sh >> log.txt"),
            ("a relative stderr redirect", f"python3 {SB}/probe.py 2> err.txt"),
            ("a relative combined redirect", f"bash {SB}/rt/run.sh &> all.txt"),
            ("tee to a relative path", f"bash {SB}/rt/run.sh | tee out.txt"),
            ("a redirect into the repo", f"bash {SB}/rt/run.sh > {REPO}/out.txt"),
            # ⛔ `/usr/` is in SAFE_PREFIXES, so rule 2 waves this through: those prefixes exist
            # so an absolute interpreter can be READ. Only rule 7's separate, narrower WRITE_OK
            # stops it, and this case is the only thing that proves the two lists stayed apart.
            ("a redirect into a system prefix", f"bash {SB}/rt/run.sh > /usr/local/lib/x"),
        ]:
            _, out = call(cmd)
            c.check(f"J · silent on {label}", silent(out), out.strip()[:160])
        # The other half: a redirect that STAYS inside must still be allowed, or rule 7 has
        # simply banned redirection and taken the feature down with the hole.
        for label, cmd in [
            ("a sandboxed redirect", f"bash {SB}/rt/run.sh > {SB}/out.txt"),
            ("a sandboxed append", f"bash {SB}/rt/run.sh >> {SB}/log.txt"),
            ("/dev/null", f"bash {SB}/rt/run.sh > /dev/null 2>&1"),
            ("tee to a sandboxed path", f"bash {SB}/rt/run.sh | tee {SB}/out.txt"),
        ]:
            _, out = call(cmd)
            c.check(f"J · still allows {label}", allowed(out), out.strip()[:160])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
