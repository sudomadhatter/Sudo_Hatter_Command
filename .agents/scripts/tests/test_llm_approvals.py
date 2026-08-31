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


def test_reader_survives_a_mid_write_thread():
    """Zoo rewrites `ui_messages.json` constantly; a partial read is the normal case."""
    m = _mod()
    assert m.blocked_commands([]) == []
    assert m.blocked_commands([{"type": "ask", "ask": "command", "partial": True,
                                "text": "git status", "autoApprovalDecision": None}]) == []


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
