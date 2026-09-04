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

⛔ That vocabulary is a SAMPLE, and the tests below pin the module for failing OPEN against it. The
first cut filtered asks through an allow-list built from these five names; Zoo emits more, and the
one it emits when auto-approval hits its cap — the moment the operator is most needed — was not in
it. `test_ask_outside_the_measured_sample_still_pages` is the assertion that keeps it open.

run_all.py executes this file bare (python3 <file>, no pytest), so the __main__ harness at the
bottom is what makes it COUNT — without it the suite scores this file green having run nothing
(the house scar: suite-red-file-may-have-run-nothing, green edition).

⛔ Every path assertion compares `Path` PARTS, never `str(...)`. Two cases here once asserted
`endswith("…zoo-code/tasks")` and `startswith("/tmp/elsewhere")`, which are False the moment
`Path` is a `WindowsPath` — so the suite this repo runs on BOTH machines was authored to go red on
one of them. [[mac-authored-code-hides-windows-bugs]]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
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


class _Stop(Exception):
    """Breaks watch()'s `while True` from inside its own sleep."""


def _store(tmp: Path, messages: list[dict], task: str = "01a05116") -> Path:
    d = tmp / task
    d.mkdir(parents=True, exist_ok=True)
    (d / "ui_messages.json").write_text(json.dumps(messages), encoding="utf-8")
    return d / "ui_messages.json"


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


def test_say_completion_result_tail_also_classifies_as_turn_end():
    """The `say` branch, which no fixture reached: the turnend fixture tails on an ASK."""
    m = _mod()
    msgs = _load("zoo_ui_messages_turnend.json")
    msgs[-1] = {"ts": 9, "type": "say", "say": "completion_result", "text": "done"}
    assert m.classify(msgs) == "turn_end"


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


def test_partial_ask_still_pages_because_zoo_never_clears_it():
    """⛔ SCC-355 regression. This test replaces `test_partial_ask_never_fires`, which pinned the
    BUG as intended behaviour and is why 38 green tests never caught it.

    The shipped guard returned None for any tail flagged `partial: True`, reasoning that a stream
    in flight is not a decision point. That is true of a `say` and FALSE of an `ask`: Zoo clears
    `partial` when ITS OWN matcher auto-approves, and leaves it standing when the operator must
    answer. Measured on the live store at fix time: 10 asks carry `partial=True` AND
    `isAnswered=True` — Zoo stamped the answer on top and never cleared the flag — and 13 of the
    16 `tool` asks that wanted the operator were flagged partial, i.e. 81% of them were dropped.
    `tool` is the `newTask` subagent launch, which is exactly the sits-blocked-and-nobody-knows
    case this module exists to end."""
    m = _mod()
    msgs = _load("zoo_ui_messages_ask.json")
    assert msgs[-1].get("partial") is True, "fixture drifted: the captured tail must be partial"
    assert m.classify(msgs) == "ask"


def test_partial_say_still_never_fires():
    """The half of the old guard that was RIGHT, kept: a SAY still streaming is not news.

    ⛔ This case used to tail on `say: "reasoning"` and it was VACUOUS — the mutation sweep proved
    it by deleting the guard entirely and watching the case pass anyway. `reasoning` is not
    `completion_result`, so `classify` returned None down the fall-through path whether the guard
    existed or not. The ONLY tail where this guard decides anything is a `completion_result` that
    is still streaming; without it, a half-written turn-end pages the operator early and then the
    finished one pages him again.
    """
    m = _mod()
    msgs = _load("zoo_ui_messages_ask.json")
    msgs[-1] = {"ts": 9, "type": "say", "say": "completion_result", "partial": True, "text": "..."}
    assert m.classify(msgs) is None
    msgs[-1]["partial"] = False              # positive control: finished, so it DOES page
    assert m.classify(msgs) == "turn_end"


def test_a_finalised_ask_pages_exactly_as_a_partial_one_does():
    """Both spellings are the same decision, so the verdict must not depend on the flag."""
    m = _mod()
    msgs = _load("zoo_ui_messages_ask.json")
    msgs[-1]["partial"] = False
    assert m.classify(msgs) == "ask"
    del msgs[-1]["partial"]
    assert m.classify(msgs) == "ask"


def test_finalising_a_partial_ask_in_place_does_not_double_page():
    """Why dropping the guard needs no new dedupe: `thread_signature` keys on the tail's own ts
    and the message count, and finalising an ask rewrites it in place — both are unchanged."""
    m = _mod()
    partial = _load("zoo_ui_messages_ask.json")
    final = _load("zoo_ui_messages_ask.json")
    final[-1]["partial"] = False
    assert m.classify(partial) == m.classify(final) == "ask"
    assert m.thread_signature(partial, "ask") == m.thread_signature(final, "ask")


def test_no_door_tells_an_agent_to_skip_a_partial_ask():
    """⛔ SCC-355 REACH check. `reproduce-before-you-fix` asks what else shares the mechanism, then
    says go look — and looking found `/smh-llm-approvals` carrying the identical filter in prose:
    "`type` is `ask`, `ask` is `command`, `partial` is not `true`". That door exists to show the
    operator which commands stopped and waited for him; measured on the live store it listed 23
    and silently dropped 4. Fixing `classify()` alone would have left him reading an
    under-reporting list and concluding the notification fix had failed.

    ⛔ This asserts on the REQUIREMENT SENTENCE, not on a repo-wide grep for the word. The fix adds
    a warning paragraph that quotes the old filter, so a naive `grep -c partial` matches the very
    text proving it was fixed and can never go red. [[comment-literals-invert-source-grep-tests]]
    """
    # ⛔ THE ANTIGRAVITY DOOR IS NOT IN THIS LIST, and that is deliberate (SCC-370). It used to be,
    # and it passed only because this command was 7,998 bytes and so shipped as a verbatim mirror.
    # Its door is a thin LAUNCHER, carrying no sentences of its own — so asserting a requirement
    # sentence there asserts the wrong surface. It is checked below for the only thing a launcher
    # can be wrong about: pointing somewhere else.
    #
    # ⭐ AND THAT DOOR MOVED (SCC-394). Antigravity retires workflows on 2026-11-01 and invokes
    # `.agents/skills/<name>/SKILL.md` as `/<name>`, so its door is now the SAME launcher skill
    # Claude and Codex read. The assertion is unchanged in substance — exists, points at this
    # brain, says END TO END — only the surface underneath it is different.
    doors = [ROOT / ".agents" / "commands" / "smh-llm-approvals.md",
             ROOT / ".opencode" / "commands" / "smh-llm-approvals.md"]
    ag = ROOT / ".agents" / "skills" / "smh-llm-approvals" / "SKILL.md"
    assert ag.is_file(), f"{ag} is missing — the door lost its launcher skill"
    _ag = ag.read_text(encoding="utf-8")
    assert "`.agents/commands/smh-llm-approvals.md`" in _ag and "END TO END" in _ag, \
        f"{ag.name}: the launcher skill no longer sends the agent to this command's body"
    for door in doors:
        assert door.is_file(), f"{door} is missing — the door lost a platform mirror"
        sentence = [ln for ln in door.read_text(encoding="utf-8").splitlines()
                    if "`ask` is `command`" in ln]
        assert sentence, f"{door.name}: the Zoo requirement sentence is gone — did it get reworded?"
        for line in sentence:
            assert "partial" not in line, f"{door.name} still filters stopped commands on partial: {line}"
            assert "autoApprovalDecision" in "".join(sentence), \
                f"{door.name}: the real signal must still be named"


def test_fixtures_are_real_captures_not_hand_written_stubs():
    """⛔ SCC-355's miss, pinned. Both fixtures shipped as 4-5 message stubs with `partial: False`
    tails while real threads run 76-413 messages and flag their operator-facing asks partial. A
    battery whose fixtures cannot express the bug cannot catch it, however many tests it holds."""
    ask = _load("zoo_ui_messages_ask.json")
    turnend = _load("zoo_ui_messages_turnend.json")
    assert len(ask) > 50, f"ask fixture is a stub again: {len(ask)} messages"
    assert len(turnend) > 50, f"turn-end fixture is a stub again: {len(turnend)} messages"
    assert ask[-1].get("partial") is True, "the ask fixture must carry the shape Zoo really writes"
    assert any(m.get("autoApprovalDecision") == "approve" for m in ask), \
        "a real thread contains auto-approved asks; a fixture without them cannot test the filter"
    body = (FIXTURES / "zoo_ui_messages_ask.json").read_text(encoding="utf-8")
    assert "/Users/" not in body and "C:\\" not in body, "capture leaked a real path — redact it"


def test_empty_thread_is_silent():
    m = _mod()
    assert m.classify([]) is None


def test_ask_outside_the_measured_sample_still_pages():
    """⛔ The deny-list, pinned. `auto_approval_max_req_reached` is raised BECAUSE auto-approval
    hit its cap and the operator must step in — an allow-list drawn from two threads dropped it
    silently, which is the exact blocked-and-nobody-knows state this script exists to end."""
    m = _mod()
    for ask in ("auto_approval_max_req_reached", "api_req_failed", "mistake_limit_reached",
                "use_mcp_server", "browser_action_launch"):
        msgs = _load("zoo_ui_messages_ask.json")
        msgs[-1]["ask"] = ask
        assert m.classify(msgs) == "ask", f"{ask} must page the operator, not vanish"


def test_completion_result_is_the_only_ask_that_is_not_a_decision():
    m = _mod()
    msgs = _load("zoo_ui_messages_ask.json")
    msgs[-1]["ask"] = "completion_result"
    assert m.classify(msgs) == "turn_end"


# --- thread_signature(): two consecutive asks are two notifications -----------------------

def test_signature_distinguishes_two_asks_in_the_same_state():
    """Keyed on the event word alone, ask #2 reads as 'not news' and is dropped in silence."""
    m = _mod()
    a = _load("zoo_ui_messages_ask.json")
    b = a + [{"ts": a[-1]["ts"] + 1, "type": "ask", "ask": "command",
              "partial": False, "autoApprovalDecision": None, "text": "rm -rf build"}]
    assert m.thread_signature(a, "ask") != m.thread_signature(b, "ask")


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


def test_compose_takes_the_first_line_only_and_truncates_at_120():
    """An ask whose text is a 4KB diff must not become the whole banner and the whole push."""
    m = _mod()
    assert "line2" not in m.compose("ask", "p", "line1\nline2")["message"]
    long = m.compose("ask", "p", "x" * 300)["message"]
    assert long.endswith("..."), long
    assert len(long) < 160, len(long)


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


# --- banner_cmd(): BOTH machines actually raise something ---------------------------------

def test_banner_cmd_mac_uses_terminal_notifier():
    m = _mod()
    cmd = m.banner_cmd({"title": "T", "message": "M"}, platform="darwin")
    assert cmd[0] == "terminal-notifier" and "T" in cmd and "M" in cmd, cmd


def test_banner_cmd_windows_actually_shows_a_toast():
    """⛔ The first cut loaded the WinRT type, discarded it, and Write-Output-ed into a captured
    pipe — nothing appeared on screen while the run reported banner=sent."""
    m = _mod()
    cmd = m.banner_cmd({"title": "T", "message": "M"}, platform="win32")
    assert cmd[0] == "powershell", cmd
    body = cmd[-1]
    assert "CreateToastNotifier" in body and ".Show(" in body, body
    assert "ToastNotification]::new" in body, body
    assert "Write-Output" not in body, "printing to a captured pipe is not a notification"
    assert "$ErrorActionPreference='Stop'" in body, "a failed toast must exit non-zero"


def test_banner_cmd_returns_none_where_there_is_no_channel():
    m = _mod()
    assert m.banner_cmd({"title": "T", "message": "M"}, platform="linux") is None


# --- send(): the dry-run promise, and an honest banner result -----------------------------

def test_dry_run_opens_nothing_and_raises_nothing():
    """The one safety property in the CLI contract. Deleting its guard once left the suite green."""
    m = _mod()
    def _boom(*a, **k):
        raise AssertionError("--dry-run must not run a subprocess or open the network")
    m.subprocess = type("S", (), {"run": staticmethod(_boom),
                                  "SubprocessError": Exception})()
    m.urllib = type("U", (), {"request": type("R", (), {
        "Request": staticmethod(_boom), "urlopen": staticmethod(_boom)})()})()
    assert m.send({"title": "T", "message": "M", "ntfy_url": "https://ntfy.sh/x"},
                  dry_run=True) == {"banner": "skipped", "push": "skipped"}


def test_a_banner_that_exits_non_zero_is_not_reported_as_sent():
    """`check=False` plus an unconditional 'sent' is the false green B4 must be able to see.

    ⛔ `banner_cmd` is pinned rather than left to `sys.platform`: on Linux it correctly returns
    None, so `send()` never runs a banner and this asserts nothing. CI runs Linux — a THIRD machine
    beside the Mac and the PC, and the one that gates `main`."""
    m = _mod()
    class _Proc:
        returncode = 1
    m.banner_cmd = lambda payload, platform=None: ["fake-notifier"]
    m.subprocess = type("S", (), {"run": staticmethod(lambda *a, **k: _Proc()),
                                  "SubprocessError": Exception})()
    m.urllib = type("U", (), {"request": type("R", (), {
        "Request": staticmethod(lambda *a, **k: None),
        "urlopen": staticmethod(lambda *a, **k: type("C", (), {"close": lambda s: None})())})()})()
    out = m.send({"title": "T", "message": "M", "ntfy_url": "https://ntfy.sh/x"})
    assert out["banner"].startswith("failed:"), out


def test_no_banner_channel_reports_skipped_not_sent_and_not_failed():
    """The Linux branch, which is CI's — and CI is the machine that gates `main`. With no channel,
    `send()` must say `skipped`: `sent` would be a false green, `failed:` a false alarm that makes
    --self-test exit 1 on a machine where nothing is wrong."""
    m = _mod()
    def _boom(*a, **k):
        raise AssertionError("there is no banner channel here; nothing should be run")
    m.subprocess = type("S", (), {"run": staticmethod(_boom), "SubprocessError": Exception})()
    m.urllib = type("U", (), {"request": type("R", (), {
        "Request": staticmethod(lambda *a, **k: None),
        "urlopen": staticmethod(lambda *a, **k: type("C", (), {"close": lambda s: None})())})()})()
    m.banner_cmd = lambda payload, platform=None: None
    out = m.send({"title": "T", "message": "M", "ntfy_url": "https://ntfy.sh/x"})
    assert out["banner"] == "skipped", out
    assert out["push"] == "sent", out


# --- read_thread() / newest_thread(): the store is rewritten under us ---------------------

def test_read_thread_survives_a_half_written_file():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "ui_messages.json"
        p.write_text("[{", encoding="utf-8")
        assert m.read_thread(p) == []


def test_newest_thread_picks_the_most_recently_touched():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        old = _store(root, [], task="old")
        new = _store(root, [], task="new")
        os.utime(old, (1_000_000, 1_000_000))
        os.utime(new, (2_000_000, 2_000_000))
        assert m.newest_thread(root) == new


# --- project_name(): the TASK's project, never the watcher's cwd --------------------------

def test_project_name_comes_from_the_threads_own_history_item():
    """One --watch daemon polls every project, so a cwd-derived name is wrong for all but one."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        thread = _store(Path(d), [])
        (thread.parent / "history_item.json").write_text(
            json.dumps({"workspace": "/Users/x/Projects/AGY_AVIATIONCHAT"}), encoding="utf-8")
        assert m.project_name(thread) == "AGY_AVIATIONCHAT"


def test_project_name_falls_back_to_the_task_id_not_the_cwd():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        thread = _store(Path(d), [], task="01a05116")
        assert m.project_name(thread) == "01a05116"


# --- watch(): priming, and one notification per DISTINCT ask ------------------------------

def test_watch_primes_silently_then_pages_each_distinct_ask():
    """⛔ Two defects in one loop: a cold `seen` pages the whole historical backlog on the first
    sweep, and a state-word key drops a second ask that arrives in the same state."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        f = _store(root, _load("zoo_ui_messages_ask.json"))
        # ⭐ Stamp it OLD. This test's subject is the historical BACKLOG, and a backlog thread is
        # stale by definition — leaving it at "now" made it accidentally fresh, which the
        # freshness exception below correctly pages for. Making the mtime match the intent is
        # what lets both behaviours be pinned at once instead of trading one for the other.
        os.utime(f, (1_000_000, 1_000_000))
        sent: list[dict] = []
        m.send = lambda payload, dry_run=False: (
            sent.append(payload) or {"banner": "x", "push": "x"})
        after_priming: list[int] = []
        unchanged: list[int] = []
        state = {"n": 0}

        def _sleep(_seconds):
            state["n"] += 1
            if state["n"] == 1:
                after_priming.append(len(sent))          # the whole backlog, silently primed
                msgs = json.loads(f.read_text(encoding="utf-8"))
                msgs[-1]["ts"] += 1                      # ask #1 becomes news
                f.write_text(json.dumps(msgs), encoding="utf-8")
                os.utime(f, (2_000_000, 2_000_000))
            elif state["n"] == 2:
                # Zoo rewrites ui_messages.json on every token, so the mtime moves constantly
                # while the tail ask sits unchanged. That must NOT re-page him every 5 seconds —
                # it is the whole reason the guard is a transition test and not `if event`.
                os.utime(f, (2_500_000, 2_500_000))
            elif state["n"] == 3:
                unchanged.append(len(sent))   # measured AFTER the rewritten-but-unchanged sweep
                msgs = json.loads(f.read_text(encoding="utf-8"))
                msgs[-1]["isAnswered"] = True            # he answered #1 ...
                msgs.append({"ts": msgs[-1]["ts"] + 5, "type": "ask", "ask": "command",
                             "partial": False, "autoApprovalDecision": None,
                             "text": "rm -rf build"})   # ... and Zoo raised #2, same poll window
                f.write_text(json.dumps(msgs), encoding="utf-8")
                os.utime(f, (3_000_000, 3_000_000))
            else:
                raise _Stop()

        m.time = type("T", (), {"sleep": staticmethod(_sleep),
                                "time": staticmethod(lambda: 3_000_000.0)})()
        try:
            m.watch([root], 1, dry_run=False)
        except _Stop:
            pass
        assert after_priming == [0], "the first sweep must page nobody — it primes"
        assert unchanged == [1], "a rewritten file in the SAME state is not news; it must not re-page"
        assert len(sent) == 2, f"both distinct asks must page; got {len(sent)}"
        assert "rm -rf build" in sent[-1]["message"], sent[-1]


def test_priming_pages_a_FRESH_pending_ask_but_never_the_stale_backlog():
    """⛔ SCC-355: the reboot case, which `KeepAlive` turns from exotic into routine.

    Priming exists so a restart does not page once per historical thread — Zoo keeps every task
    directory forever and a finished thread's tail stays an ask on disk. But once the watcher is
    a launchd agent it restarts at every login and after every crash, and asks measurably sit
    open for 17+ minutes (SCC-355 diagnosis). So "restarted while Zoo is blocked waiting" is the
    normal case, and a silent prime loses exactly the page that mattered.

    The exception is narrow on purpose: during priming, an UNANSWERED ASK whose thread was
    written inside the freshness window pages; everything else — stale asks, and turn-ends at any
    age — stays silent. A turn-end is not blocking anyone, so it never earns the exception."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        fresh = _store(root, _load("zoo_ui_messages_ask.json"), task="fresh")
        stale = _store(root, _load("zoo_ui_messages_ask.json"), task="stale")
        done = _store(root, _load("zoo_ui_messages_turnend.json"), task="done")
        now = 3_000_000.0
        os.utime(fresh, (now - 10, now - 10))       # Zoo is waiting on him RIGHT NOW
        os.utime(stale, (now - 9_999, now - 9_999))  # answered days ago; tail never rewritten
        os.utime(done, (now - 10, now - 10))         # fresh, but finished — not blocking

        sent: list[dict] = []
        m.send = lambda payload, dry_run=False: (
            sent.append(payload) or {"banner": "x", "push": "x"})

        def _sleep(_seconds):
            raise _Stop()
        m.time = type("T", (), {"sleep": staticmethod(_sleep),
                                "time": staticmethod(lambda: now)})()
        try:
            m.watch([root], 1, dry_run=False)
        except _Stop:
            pass

        assert len(sent) == 1, f"exactly the fresh pending ask pages; got {len(sent)}: {sent}"
        assert sent[0]["event"] == "ask", sent[0]
        assert sent[0]["title"] == "Zoo Code - needs you", sent[0]
        # ⛔ WHICH thread paged, not just how many. Counting alone is vacuous: the mutation sweep
        # inverted the comparison to `>=`, which pages the STALE thread and silences the fresh one
        # — still exactly one page, still an ask, still the same title. Only naming the thread
        # tells the two apart, and telling them apart is the entire point of the window.
        assert "fresh" in sent[0]["message"], f"the STALE thread paged instead: {sent[0]}"
        assert "stale" not in sent[0]["message"], sent[0]


def test_priming_freshness_window_is_configurable_and_zero_means_silent():
    """A zero window restores the old always-silent prime — the escape hatch if it ever nags."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        f = _store(root, _load("zoo_ui_messages_ask.json"), task="fresh")
        now = 3_000_000.0
        os.utime(f, (now - 10, now - 10))
        sent: list[dict] = []
        m.send = lambda payload, dry_run=False: (
            sent.append(payload) or {"banner": "x", "push": "x"})

        def _sleep(_seconds):
            raise _Stop()
        m.time = type("T", (), {"sleep": staticmethod(_sleep),
                                "time": staticmethod(lambda: now)})()
        try:
            m.watch([root], 1, dry_run=False, fresh=0)
        except _Stop:
            pass
        assert sent == [], "fresh=0 must prime in total silence"


# --- store_root(): BOTH machines, profiles, and the configurable path ---------------------

def test_store_root_resolves_on_mac_and_on_windows():
    """[[two-machines-mac-and-pc]] — a hardcoded Application Support path is a PC no-op."""
    m = _mod()
    home = Path("/Users/x")          # SAME home both times, or the paths differ for that reason
    mac = m.store_root(platform="darwin", home=home, appdata=None)
    win = m.store_root(platform="win32", home=home, appdata=home / "AppData" / "Roaming")
    assert "Application Support" in mac.parts, mac
    assert "AppData" in win.parts, win
    assert "Application Support" not in win.parts, "the PC must not resolve to the Mac's path"
    assert win != mac, (win, mac)
    assert mac.parts[-2:] == (m.EXTENSION_DIR, "tasks"), mac


def test_custom_storage_path_setting_wins():
    """zoo-code.customStoragePath is a real Zoo setting; ignoring it watches the wrong dir."""
    m = _mod()
    got = m.store_root(platform="darwin", home=Path("/Users/x"), appdata=None,
                       custom=Path("/tmp/elsewhere"))
    assert got == Path("/tmp/elsewhere") / "tasks", got


def test_custom_storage_path_is_actually_read_from_settings():
    """⛔ The parameter existed from the first cut and NOTHING passed it — a documented setting
    that no entry point could reach. This is the wiring, not the parameter."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        user = Path(d)
        (user / "settings.json").write_text(
            json.dumps({m.SETTING_CUSTOM_STORE: "/tmp/elsewhere"}), encoding="utf-8")
        assert m.read_custom_store(user) == Path("/tmp/elsewhere")


def test_custom_storage_path_is_read_from_a_named_profile_too():
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        user = Path(d)
        (user / "settings.json").write_text("{}", encoding="utf-8")
        prof = user / "profiles" / "abc123"
        prof.mkdir(parents=True)
        (prof / "settings.json").write_text(
            json.dumps({m.SETTING_CUSTOM_STORE: "/tmp/profiled"}), encoding="utf-8")
        assert m.read_custom_store(user) == Path("/tmp/profiled")


def test_store_roots_enumerates_named_profiles():
    """`zoo_permissions_apply.py` already globs profiles/*/globalStorage for this same extension,
    so a named profile is a live case here — resolving only the default one reports 'is Zoo Code
    installed?' on a machine where it plainly is."""
    m = _mod()
    with tempfile.TemporaryDirectory() as d:
        home = Path(d)
        user = home / "Library" / "Application Support" / "Code" / "User"
        (user / "globalStorage" / m.EXTENSION_DIR / "tasks").mkdir(parents=True)
        (user / "profiles" / "builtin" / "globalStorage" / m.EXTENSION_DIR / "tasks").mkdir(
            parents=True)
        roots = m.store_roots(platform="darwin", home=home, appdata=None)
        assert len(roots) == 2, roots
        assert any("profiles" in r.parts for r in roots), roots


# --- main(): the CLI contract, run for real -----------------------------------------------

def test_missing_store_exits_2_not_0():
    """The only signal separating 'Zoo is not installed' from 'nothing needed notifying'."""
    proc = subprocess.run(
        [sys.executable, str(NOTIFY), "--once", "--store", "/nonexistent-zoo-store", "--dry-run"],
        capture_output=True, text=True, timeout=30)
    assert proc.returncode == 2, (proc.returncode, proc.stdout, proc.stderr)


def test_main_actually_honours_custom_storage_path_end_to_end():
    """⛔ The WIRING, run for real — not the helper. The first cut pinned `store_root(custom=…)`
    while `main()` called `store_root()` with no arguments, so the documented setting was dead and
    the test read as coverage. This drives the CLI with a fake HOME and no --store: it can only
    find the thread if main() read settings.json for itself."""
    with tempfile.TemporaryDirectory() as d:
        home = Path(d)
        # ⛔ Ask the module where it looks; never hardcode one platform's path. This case built
        # the MAC dir (`Library/Application Support/Code/User`) and isolated the child with
        # `HOME=` alone. On Windows neither holds: `Path.home()` reads USERPROFILE, not HOME, and
        # the Windows branch of `user_dir` reads APPDATA — so the fake home was ignored, the child
        # read the operator's REAL Zoo store, found a real already-answered thread, and printed
        # "needs nothing". A test that silently escapes its sandbox and reads live user data is
        # worse than a red one; it was red only by luck. Now the sandbox is airtight on both
        # machines. [[mac-authored-code-hides-windows-bugs]] (SCC-338)
        appdata = home / "AppData" / "Roaming"
        user = _mod().user_dir(home=home, appdata=appdata)
        user.mkdir(parents=True)
        elsewhere = home / "elsewhere"
        _store(elsewhere / "tasks", _load("zoo_ui_messages_ask.json"))
        (user / "settings.json").write_text(
            json.dumps({"zoo-code.customStoragePath": str(elsewhere)}), encoding="utf-8")
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), APPDATA=str(appdata))
        env.pop("NTFY_TOPIC", None)
        proc = subprocess.run([sys.executable, str(NOTIFY), "--once", "--dry-run"],
                              capture_output=True, text=True, timeout=30, env=env)
        assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
        assert "waiting on approval" in proc.stdout, proc.stdout


def test_self_test_reports_exit_1_when_a_channel_did_not_fire():
    """The PC's whole problem was a banner that showed nothing and reported success. --self-test
    is the five-second proof, so it must FAIL when a channel fails, not just print prettily."""
    m = _mod()
    class _Proc:
        returncode = 1
    m.banner_cmd = lambda payload, platform=None: ["fake-notifier"]   # Linux has no channel
    m.subprocess = type("S", (), {"run": staticmethod(lambda *a, **k: _Proc()),
                                  "SubprocessError": Exception})()
    m.urllib = type("U", (), {"request": type("R", (), {
        "Request": staticmethod(lambda *a, **k: None),
        "urlopen": staticmethod(lambda *a, **k: type("C", (), {"close": lambda s: None})())})()})()
    assert m.self_test(dry_run=False) == 1


def test_self_test_dry_run_opens_nothing_and_claims_nothing():
    """Exit 0 is not the whole contract. A dry run sends nothing, so it must not go on to report
    'both channels reported OK' — that turns the proof command into a source of false evidence."""
    import contextlib, io
    m = _mod()
    def _boom(*a, **k):
        raise AssertionError("--self-test --dry-run must not fire either channel")
    m.subprocess = type("S", (), {"run": staticmethod(_boom), "SubprocessError": Exception})()
    m.urllib = type("U", (), {"request": type("R", (), {
        "Request": staticmethod(_boom), "urlopen": staticmethod(_boom)})()})()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.self_test(dry_run=True)
    out = buf.getvalue()
    assert rc == 0, rc
    assert "banner=skipped" in out and "push=skipped" in out, out
    assert "reported OK" not in out, "a dry run must not claim the channels work: " + out


def test_self_test_needs_no_thread_store():
    """It proves the CHANNELS. Requiring a store would make it unusable on a fresh machine —
    exactly the machine you most want to prove."""
    proc = subprocess.run([sys.executable, str(NOTIFY), "--self-test", "--dry-run"],
                          capture_output=True, text=True, timeout=30,
                          env=dict(os.environ, HOME="/nonexistent-home"))
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert "self-test" in proc.stdout, proc.stdout


def test_dry_run_is_a_modifier_not_a_mode():
    """The INDEX row once listed it beside --once/--watch; argparse rejects it alone."""
    proc = subprocess.run([sys.executable, str(NOTIFY), "--dry-run"],
                          capture_output=True, text=True, timeout=30)
    assert proc.returncode == 2 and "--once" in proc.stderr, proc.stderr


def test_interval_below_one_is_rejected_at_the_boundary():
    """--interval 0 spun the poll loop at 100% of a core; --interval -1 crashed time.sleep."""
    for bad in ("0", "-1"):
        proc = subprocess.run([sys.executable, str(NOTIFY), "--watch", "--interval", bad],
                              capture_output=True, text=True, timeout=30)
        assert proc.returncode == 2, (bad, proc.returncode, proc.stderr)


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
