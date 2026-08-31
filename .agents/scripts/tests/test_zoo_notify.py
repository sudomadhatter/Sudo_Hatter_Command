"""Zoo Code notification parity with Claude — behavior gate (SCC-355).

Zoo v3.80.1 contributes NO notification surface: its manifest declares 19 settings keys and 20
commands and not one of them is a notification, a sound, or an event hook (measured at plan time,
recorded in the walkthrough). So the trigger cannot be a hook — it is a watcher over the thread
store Zoo already writes, and THAT is what these tests pin.

The store's own vocabulary, read off two real threads (154 messages) rather than assumed:
  type            "ask" | "say"
  ask             "command" | "tool" | "followup" | "completion_result" | "resume_completed_task"
  say             "api_req_started" | "reasoning" | "text" | "command_output" |
                  "user_feedback" | "completion_result"
  isAnswered      True (41) | absent (12)  — never literal False, so "pending" is `is not True`
  partial         False (34) | absent (19)
  autoApprovalDecision  "approve" (34) | None (14) | "deny" (5)

⭐ `autoApprovalDecision is None` is the operator-was-needed signal: Zoo records its OWN verdict, so
an ask it auto-approved never interrupted anyone and must NOT raise a banner. A notifier that fires
on every ask would page the operator 34 times for the 14 that actually needed him — which is the
failure this whole subtask exists to prevent, so it is pinned as a test, not a comment.

run_all.py executes this file bare (python3 <file>, no pytest), so the __main__ harness at the
bottom is what makes it COUNT — without it the suite scores this file green having run nothing
(the house scar: suite-red-file-may-have-run-nothing, green edition).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
NOTIFY = ROOT / ".agents" / "scripts" / "zoo_notify.py"


def _load(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _mod():
    """Import zoo_notify.py by path — it is a script, not a package member."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("zoo_notify", NOTIFY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- the module has to exist at all -------------------------------------------------------

def test_notifier_script_exists():
    assert NOTIFY.is_file(), f"{NOTIFY} does not exist — SCC-355 step B1 has not been built"


# --- classify(): which threads deserve to interrupt the operator --------------------------

def test_pending_ask_classifies_as_ask():
    m = _mod()
    assert m.classify(_load("zoo_ui_messages_ask.json")) == "ask"


def test_completed_turn_classifies_as_turn_end():
    m = _mod()
    assert m.classify(_load("zoo_ui_messages_turnend.json")) == "turn_end"


def test_auto_approved_ask_never_fires():
    """Zoo already decided it. The operator was not needed, so he is not paged."""
    m = _mod()
    msgs = _load("zoo_ui_messages_ask.json")
    msgs[-1]["autoApprovalDecision"] = "approve"
    # deliberately NOT setting isAnswered: the mutation sweep proved that setting it made the
    # isAnswered guard catch this case first, leaving the autoApprovalDecision guard untested
    assert m.classify(msgs) is None
    msgs[-1]["autoApprovalDecision"] = "deny"
    assert m.classify(msgs) is None


def test_answered_ask_is_not_pending():
    m = _mod()
    msgs = _load("zoo_ui_messages_ask.json")
    msgs[-1]["isAnswered"] = True
    assert m.classify(msgs) is None


def test_partial_ask_never_fires():
    """A streaming partial is not a decision point; firing on it double-pages every ask."""
    m = _mod()
    msgs = _load("zoo_ui_messages_ask.json")
    msgs[-1]["partial"] = True
    assert m.classify(msgs) is None


def test_empty_thread_is_silent():
    m = _mod()
    assert m.classify([]) is None


# --- compose(): pure, and provably makes no network call ----------------------------------

def test_compose_is_pure_and_touches_no_network():
    m = _mod()
    import urllib.request
    real = urllib.request.urlopen

    def _boom(*a, **k):
        raise AssertionError("compose() must not open the network")

    urllib.request.urlopen = _boom
    try:
        out = m.compose("ask", project="Sudo_Hatter_Command", text="acli jira workitem view SCC-352")
    finally:
        urllib.request.urlopen = real
    assert out["title"], "banner needs a title"
    assert "Sudo_Hatter_Command" in out["message"], "banner names the project, like Claude's does"
    assert out["ntfy_url"].startswith("https://ntfy.sh/"), out["ntfy_url"]


def test_ntfy_topic_defaults_to_the_existing_topic():
    m = _mod()
    os.environ.pop("NTFY_TOPIC", None)
    assert m.compose("ask", project="p", text="t")["ntfy_url"] == "https://ntfy.sh/mac-sudo-command"


def test_ntfy_topic_env_override_wins():
    """The guide says switch to a long random topic if the payload ever carries real text."""
    m = _mod()
    os.environ["NTFY_TOPIC"] = "a-long-random-topic"
    try:
        assert m.compose("ask", project="p", text="t")["ntfy_url"].endswith("/a-long-random-topic")
    finally:
        os.environ.pop("NTFY_TOPIC", None)


def test_ask_and_turn_end_are_distinguishable():
    m = _mod()
    a = m.compose("ask", project="p", text="t")
    b = m.compose("turn_end", project="p", text="t")
    assert a["title"] != b["title"] or a["message"] != b["message"], \
        "the operator must be able to tell 'needs you' from 'finished' without opening the window"


# --- store_root(): BOTH machines, and the configurable path -------------------------------

def test_store_root_resolves_on_mac_and_on_windows():
    """[[two-machines-mac-and-pc]] — a hardcoded Application Support path is a PC no-op."""
    m = _mod()
    home = Path("/Users/x")          # SAME home both times, or the paths differ for that reason
    mac = m.store_root(platform="darwin", home=home, appdata=None)
    win = m.store_root(platform="win32", home=home, appdata=home / "AppData" / "Roaming")
    assert "Application Support" in str(mac), mac
    assert "AppData" in str(win), win
    assert "Application Support" not in str(win), "the PC must not resolve to the Mac's path"
    assert str(win) != str(mac), (win, mac)
    assert str(mac).endswith("zoocodeorganization.zoo-code/tasks"), mac


def test_custom_storage_path_setting_wins():
    """zoo-code.customStoragePath is a real Zoo setting; ignoring it watches the wrong dir."""
    m = _mod()
    got = m.store_root(platform="darwin", home=Path("/Users/x"), appdata=None,
                       custom=Path("/tmp/elsewhere"))
    assert str(got).startswith("/tmp/elsewhere"), got


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
