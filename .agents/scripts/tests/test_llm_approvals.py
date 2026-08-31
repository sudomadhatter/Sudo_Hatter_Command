"""`/smh-llm-approvals` — the door that reads a chat and proposes allow rows (SCC-354).

The problem it solves, stated once: Zoo Code has no "don't ask again" affordance. Its decisions
live in VS Code `globalState`, the tracked settings file seeds that store ONCE on a fresh machine
and denies never seed at all, so the allow list only ever grows by somebody reading a thread by
eye and working out which prefix would have let a blocked command through. Claude Code grows its
own list from its approval prompt; Zoo cannot. This is the platform that cannot help itself.

What these tests pin, in the order the door does it:

  the reader     every command Zoo actually STOPPED on — `autoApprovalDecision is None`, which is
                 Zoo's own record that its matcher had no opinion and the operator was needed. An
                 ask Zoo auto-approved never blocked anyone and needs no new row, so a reader that
                 returns it is proposing rows for commands that already run.
  the proposer   replays each blocked command through `zoo_matcher.decide` — the SAME mirror the
                 78-row battery pins, never a second copy — and emits the shortest prefix that
                 flips it to `auto_approve`.
  the floor      ⛔ and the shortest prefix is NOT safe on its own. Measured against the live
                 lists: the shortest prefix flipping `npx create-next-app my-app` to
                 `auto_approve` is the single character `n`, and it leaks ZERO of the 78 battery
                 rows — so both of the obvious assertions pass while that row silently
                 auto-approves `npm publish`, `node evil.js`, `nc -l 4444` and
                 `netsh advfirewall set allprofiles state off`. The floor is the third assertion.
  the door       prints, and writes nothing — to any store, on any platform.

run_all.py executes this file bare (python3 <file>, no pytest), so the __main__ harness at the
bottom is what makes it COUNT — without it the suite scores this file green having run nothing
(the house scar: suite-red-file-may-have-run-nothing, green edition). `FAILED:` is printed on its
OWN line because `mutation_sweep.py` attributes a kill by a line STARTING with that token; on the
tally line it reads as an unattributable sweep error and every mutant comes back as no evidence.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".agents" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
ZOO_THREAD = FIXTURES / "zoo_ui_messages_ask.json"

sys.path.insert(0, str(SCRIPTS))


def _mod():
    """Import llm_approvals.py by path — it is a script, not a package member."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "llm_approvals", SCRIPTS / "llm_approvals.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- the reader ----------------------------------------------------------------------------

def test_reader_extracts_only_the_blocked_command():
    """A2 — the discriminating assertion, not just a count.

    The fixture carries TWO `ask`/`command` messages on purpose: `ls -la` with
    `autoApprovalDecision: "approve"` (Zoo let it through; nobody was blocked) and
    `acli jira workitem view SCC-352` with `null` (Zoo asked). A reader that returns both
    passes any assertion about "it found the commands" while proposing an allow row for a
    command that already runs — so `ls -la` being ABSENT is the half that carries the meaning.
    """
    m = _mod()
    got = m.blocked_commands(json.loads(ZOO_THREAD.read_text(encoding="utf-8")))
    assert got == ["acli jira workitem view SCC-352"], got
    assert "ls -la" not in got, "an auto-approved ask never blocked anyone and needs no row"


def test_reader_skips_an_ask_zoo_denied():
    """WIDTH — the boundary, not just the existence of a filter.

    Zoo records three verdicts, and only `null` means it asked. A reader that filters on
    "not approved" instead of "no decision" proposes an allow row for a command the fence
    REFUSED — the door growing the fence backwards, one row at a time. The fixture carries
    approve and null, so the deny arm needs its own case or nothing pins it.
    """
    m = _mod()
    denied = [{"type": "ask", "ask": "command", "partial": False,
               "text": "git push --force", "autoApprovalDecision": "deny"}]
    assert m.blocked_commands(denied) == []


def test_reader_survives_a_mid_write_thread():
    """Zoo rewrites `ui_messages.json` constantly; a partial read is the normal case."""
    m = _mod()
    assert m.blocked_commands([]) == []
    assert m.blocked_commands([{"type": "ask", "ask": "command", "partial": True,
                                "text": "git status", "autoApprovalDecision": None}]) == []


# --- the proposer, and the floor that makes it safe ------------------------------------------

def _battery():
    """The 78-row destructive battery, imported from the file that owns it.

    Not copied. That battery IS the fence, and a second copy of a fence is a fence that can
    disagree with itself — the same reason the matcher itself became one module in step 1.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "test_zoo_permissions", Path(__file__).resolve().parent / "test_zoo_permissions.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BLOCKED = [
    "npx create-next-app my-app",
    "docker compose up -d",
    "pnpm install --frozen-lockfile",
]


def test_every_proposed_row_allows_its_own_command():
    """A3(a) — the row has to actually do the job it was proposed for."""
    m = _mod()
    import zoo_matcher
    for cmd in BLOCKED:
        row = m.propose(cmd, zoo_matcher.ALLOW, zoo_matcher.DENY)
        assert row, f"no row proposed for {cmd!r}"
        assert zoo_matcher.decide(cmd, zoo_matcher.ALLOW + [row], zoo_matcher.DENY) == "auto_approve", (
            f"{row!r} does not auto-approve {cmd!r}")


def test_no_proposed_row_unlocks_the_deny_battery():
    """A3(b) — allows may be broad, denies are the fence (standing ruling, SCC-351)."""
    m = _mod()
    import zoo_matcher
    battery = _battery().BATTERY
    for cmd in BLOCKED:
        row = m.propose(cmd, zoo_matcher.ALLOW, zoo_matcher.DENY)
        leaked = [b for b in battery
                  if zoo_matcher.decide(b, zoo_matcher.ALLOW + [row], zoo_matcher.DENY) != "auto_deny"]
        assert not leaked, f"row {row!r} unlocks {len(leaked)} destructive rows: {leaked[:3]}"


def test_breadth_floor_refuses_a_bare_letter():
    """A3(c) — ⛔ THE assertion, and the one the first cut of this plan did not have.

    Measured against the live lists: the shortest prefix flipping `npx create-next-app my-app`
    to auto_approve is the single character `n`. It leaks ZERO of the 78 battery rows, so (a)
    and (b) above BOTH pass while that row silently auto-approves `npm publish`, `node evil.js`,
    `nc -l 4444` and `netsh advfirewall set allprofiles state off` — none of which is in the
    battery, and none of which anyone asked for. Shortest is not safest.

    The floor: a row is at least the command's full first token, and never stops inside a token
    it does not complete.
    """
    m = _mod()
    import zoo_matcher
    cmd = "npx create-next-app my-app"
    row = m.propose(cmd, zoo_matcher.ALLOW, zoo_matcher.DENY)
    assert row != "n", "the bare letter is the hole this floor exists to close"
    assert row.split()[0] == cmd.split()[0], (
        f"{row!r} stops inside the first token of {cmd!r}")
    for hostile in ("npm publish", "node evil.js", "nc -l 4444",
                    "netsh advfirewall set allprofiles state off"):
        assert zoo_matcher.decide(hostile, zoo_matcher.ALLOW + [row], zoo_matcher.DENY) != "auto_approve", (
            f"row {row!r} silently auto-approves {hostile!r}")


def test_floor_holds_at_every_token_boundary():
    """WIDTH, not only existence: every row must end on a boundary, not just the first one."""
    m = _mod()
    import zoo_matcher
    for cmd in BLOCKED:
        row = m.propose(cmd, zoo_matcher.ALLOW, zoo_matcher.DENY)
        tokens = cmd.split()
        boundaries = {" ".join(tokens[:k]) for k in range(1, len(tokens) + 1)}
        assert row in boundaries, f"{row!r} is not a token-boundary prefix of {cmd!r}"


if __name__ == "__main__":
    # run_all.py executes test files bare — without this block the whole gate is a silent no-op.
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
    if _failed:
        # mutation_sweep.py attributes a kill by a line STARTING with "FAILED:" (its L186), so
        # this must be its own line - on the tally line it reads as an unattributable sweep error
        print("FAILED: " + ", ".join(_failed))
    sys.exit(1 if _failed else 0)
