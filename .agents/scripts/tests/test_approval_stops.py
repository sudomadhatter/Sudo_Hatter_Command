"""approval_stops.py — the door must measure STOPS, not refusals (SCC-407).

⛔ THE REGRESSION THIS FILE EXISTS TO HOLD. `/smh-llm-approvals` Step 1 used to harvest Claude
transcripts for a `tool_result` carrying `is_error` and *"doesn't want to proceed with this tool
use"* — commands the operator REFUSED. The door's purpose is the opposite event: the trivial
command that stopped and waited, which he then approved. **A granted approval writes nothing to the
transcript**, so the old reading could not see a single one. Measured 2026-09-04: one refusal found
across 20 sessions, reported as "nothing to harvest", in a window holding 34 real stops and 39
minutes of waiting.

Every case below is built on a SYNTHETIC transcript, so it binds on any machine — including CI,
where `~/.claude/projects/` is empty and a test that read the live store would pass vacuously
forever (the house scar: an assertion that cannot fail is not an assertion).

run_all.py executes this file bare, so the __main__ harness at the bottom is what makes it count.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".agents" / "scripts" / "approval_stops.py"
DOOR = ROOT / ".agents" / "commands" / "smh-llm-approvals.md"

_spec = importlib.util.spec_from_file_location("approval_stops", SCRIPT)
aps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(aps)

PREFIXES = ["git status", "ls", "cat"]


def _t(seconds: int) -> str:
    return "2026-09-04T00:%02d:%02dZ" % (seconds // 60, seconds % 60)


def _transcript(path: Path, rows) -> None:
    """rows: (command, wait_seconds, error_or_None[, escalated[, tool_name]]) -> a transcript."""
    out, clock = [], 0
    for i, row in enumerate(rows):
        cmd, wait, err = row[0], row[1], row[2]
        escalated = row[3] if len(row) > 3 else False
        tool = row[4] if len(row) > 4 else "Bash"
        uid = "tu_%d" % i
        inp = {"command": cmd} if tool == "Bash" else {"skill": cmd}
        if escalated:
            inp["dangerouslyDisableSandbox"] = True
        out.append({"timestamp": _t(clock), "message": {"content": [
            {"type": "tool_use", "id": uid, "name": tool, "input": inp}]}})
        clock += wait
        block = {"type": "tool_result", "tool_use_id": uid, "content": err or "ok"}
        if err:
            block["is_error"] = True
        out.append({"timestamp": _t(clock), "message": {"content": [block]}})
        clock += 1
    path.write_text("\n".join(json.dumps(r) for r in out), encoding="utf-8")


def _scan(rows, wait=20.0):
    """Run the real scan() against a synthetic store, with the allow list stubbed."""
    with tempfile.TemporaryDirectory() as td:
        home = Path(td) / "projects" / "p"
        home.mkdir(parents=True)
        _transcript(home / "s.jsonl", rows)
        real_glob, real_allow = aps.glob.glob, aps.allow_prefixes
        aps.glob.glob = lambda _pat: [str(home / "s.jsonl")]
        aps.allow_prefixes = lambda _root: PREFIXES
        try:
            return aps.scan(ROOT, 20, wait)
        finally:
            aps.glob.glob, aps.allow_prefixes = real_glob, real_allow


# --- the regression itself -------------------------------------------------------------------

def test_A0_control_the_harness_can_see_a_stop():
    """CONTROL: without this, every case below could pass by finding nothing at all."""
    r = _scan([("npx playwright test", 90, None)])
    assert r["heads"], "the harness found NO stop in a transcript built to contain exactly one"
    assert "npx playwright" in r["heads"], r["heads"]


def test_A_a_GRANTED_approval_is_reported():
    """⛔ THE BUG. This command was approved, so it carries no error - the old step saw nothing."""
    r = _scan([("npx playwright test", 120, None)])
    assert len(r["stops"]) == 1, r["stops"]
    assert r["stops"][0][1] == "waited", r["stops"][0]
    assert round(r["heads"]["npx playwright"][0]) == 120


def test_A_control_a_FAST_uncovered_call_is_not_a_stop():
    """Polarity: uncovered alone must not count, or every command in the log is a 'stop'."""
    r = _scan([("npx playwright test", 2, None)])
    assert not r["stops"], "a 2-second call was reported as though a human was asked"


def test_B_a_refusal_is_counted_but_kept_SEPARATE():
    r = _scan([("rm -rf /", 0, "The user doesn't want to proceed with this tool use")])
    kinds = [k for _, k, _ in r["stops"]]
    assert kinds == ["refused-by-operator"], kinds


def test_C_the_classifier_refusal_is_seen_at_all():
    """The class the old step never looked for; it fired 4x in the session that found this bug."""
    r = _scan([("python3 x.py", 0,
                "Permission for this action was denied by the Claude Code auto mode classifier.")])
    kinds = [k for _, k, _ in r["stops"]]
    assert kinds == ["refused-by-classifier"], kinds


def test_D_a_COVERED_command_never_reports_however_long_it_waited():
    """A slow `git status` is git being slow, not the operator being asked."""
    r = _scan([("git status --porcelain", 600, None)])
    assert not r["stops"], "a command already on the allow list was reported as a stop"


def test_D_b_a_BARE_STAR_row_is_stripped_to_its_prefix():
    """⛔ THE PART B BUG. Battery A2b established that a prefix ending in `/ = - :` must be
    spelled `Bash(X/*)`, because Claude reads `Bash(X:*)` as `Bash(X *)` — so the bare-star
    spelling is the WORKING one. `allow_prefixes()` stripped `:*` and ` *` and never a bare `*`,
    so 54 of the 153 rendered Claude `Bash(...)` rows came back with the `*` still attached and
    matched nothing. Reads the REAL allow_prefixes(), not the stub the other cases use.
    """
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        (repo / ".claude").mkdir()
        (repo / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": [
            "Bash(python3 .agents/scripts/*)",     # bare star - the working spelling
            "Bash(git status:*)",                  # colon star
            "Bash(ls *)",                          # space star
            "Read(//home/**)",                     # not a Bash rule at all
        ]}}), encoding="utf-8")
        got = aps.allow_prefixes(repo)
    assert got == ["python3 .agents/scripts/", "git status", "ls"], got


def test_D_c_a_slow_call_a_BARE_STAR_row_covers_is_not_a_stop():
    """The consequence of D_b on the door itself, end to end through the real scan().

    With the `*` still attached the prefix matches nothing, so a command an existing allow row
    already approves is billed to the operator as an interruption. That is the instrument error
    that inflated SCC-406's claimed savings.
    """
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        (repo / ".claude").mkdir()
        (repo / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": [
            "Bash(python3 .agents/scripts/*)"]}}), encoding="utf-8")
        store = repo / "projects" / "p"
        store.mkdir(parents=True)
        _transcript(store / "s.jsonl", [("python3 .agents/scripts/check_maps.py", 600, None)])
        real_glob = aps.glob.glob
        aps.glob.glob = lambda _pat: [str(store / "s.jsonl")]
        try:
            r = aps.scan(repo, 20, 20.0)
        finally:
            aps.glob.glob = real_glob
    assert not r["stops"], "a command a bare-star allow row already covers was billed as a stop"


def test_E_a_self_explaining_wait_is_dropped():
    """⛔ Written `\\d` instead of `\\d+`, this matched `timeout 9` inside `timeout 900` and then
    failed the boundary against the second `0` - so the rows the filter existed to drop stayed at
    the TOP of the ranking and read as real findings. Three digits is the case that broke."""
    for cmd in ("timeout 900 ./slow", "timeout 9 ./slow", "gh pr checks 5 --watch"):
        r = _scan([(cmd, 400, None)])
        assert not r["stops"], "%r was credited as an approval stop" % cmd
    # `sleep` is NOT in this list: a foreground sleep is a HARNESS BAN (case M), which outranks
    # self-explaining. Ordered the other way round, the operator's five identical `sleep 60; …`
    # retries vanished into this bin instead of reporting with their remedy.
    r = _scan([("sleep 300", 400, None)])
    assert [k for _, k, _ in r["stops"]] == ["harness-ban"], r["stops"]


def test_F_shell_scaffolding_is_dropped_no_rule_could_fix_it():
    """`for i`/`set -e`/`done` are lines of a multi-line script, not commands that were approved."""
    r = _scan([("set -e\nfor i in 1 2 3; do\n  echo $i\ndone", 300, None)])
    assert not r["heads"], "scaffolding was ranked as though one allow row would fix it: %s" % r["heads"]
    assert r["scaffolding"] == 1, r["scaffolding"]


def test_F2_control_scaffolding_AROUND_a_real_command_still_reports_it():
    """Polarity for F: the drop must be about the head, not about multi-line commands as a class."""
    r = _scan([("set -e\nnpx playwright test", 300, None)])
    assert "npx playwright" in r["heads"], r["heads"]


def test_G_a_continuation_fragment_is_not_a_command():
    """`-rl '^riders:'` is the second half of a wrapped grep. It ranked FIRST, at 18m27s."""
    r = _scan([("-rl '^riders:' .", 300, None)])
    assert not r["heads"], r["heads"]


def test_H_ranking_is_by_TIME_not_count():
    """The expensive stop is the one he was away from; count-ranking buries it under fast noise."""
    rows = [("npx playwright test", 600, None)] + [("nm -C sym", 25, None) for _ in range(8)]
    r = _scan(rows)
    ranked = sorted(r["heads"].items(), key=lambda kv: -sum(kv[1]))
    assert ranked[0][0] == "npx playwright", [(k, len(v), sum(v)) for k, v in ranked]
    assert len(r["heads"]["nm -C"]) == 8


def test_I_heredoc_bodies_never_become_commands():
    """The first version of this measurement ranked `---` as the top interruption."""
    r = _scan([("python3 - <<'PY'\nprint('---')\ndone\nPY", 300, None)])
    assert "---" not in r["heads"] and "done" not in r["heads"], r["heads"]


# --- the three classes the operator's own eight stops exposed (2026-09-04) --------------------

def test_L_an_ALLOWED_command_run_with_the_sandbox_off_is_still_a_stop():
    """⛔ HIS STOP #3, and a FALSE NEGATIVE the coverage filter caused.

    `git worktree remove --force … && git branch -d …` was ALREADY on the allow list and stopped
    anyway: the escalation gate is a second, independent gate. Judged on coverage alone the scan
    marked it covered and hid a stop he actually paid for.
    """
    covered_cmd = "git status --porcelain"
    plain = _scan([(covered_cmd, 120, None, False)])
    assert not plain["stops"], "polarity: without escalation a covered command must stay silent"
    esc = _scan([(covered_cmd, 120, None, True)])
    assert [k for _, k, _ in esc["stops"]] == ["escalation"], esc["stops"]


def test_M_a_harness_banned_shape_is_NOT_offered_as_an_allow_candidate():
    """⛔ HIS STOPS #4-8: five identical `sleep 60; …` retries. No permission row fixes a shape the
    harness refuses, so these must carry their own remedy, not sit in the allow list."""
    r = _scan([("sleep 60; gh pr view 154", 90, None)])
    assert [k for _, k, _ in r["stops"]] == ["harness-ban"], r["stops"]
    assert not r["heads"], "a banned shape was offered as an allow candidate: %s" % r["heads"]
    assert "Monitor" in "".join(r["remedies"].values()), r["remedies"]


def test_M2_the_ban_row_names_the_OFFENCE_not_the_line_it_sat_in():
    """Keyed on the first two words, `cat > x && git -C y` reported `cat >` with a git -C remedy."""
    r = _scan([("cat > /tmp/x && git -C /repo status", 90, None)])
    assert "git -C" in r["blocked"], r["blocked"]


def test_N_a_non_Bash_tool_is_seen_but_its_DURATION_is_never_charged_to_him():
    """⛔ HIS STOP #1 is `Skill(code-review-engine)` — invisible while this read only Bash.

    But `Agent(general-purpose)` ran 63x for 11h37m in the live window: a subagent WORKING, not
    him waiting. Crediting that put a fabricated 11 hours at the top of a report whose only value
    is being believable about cost.
    """
    r = _scan([("code-review-engine", 279, None, False, "Skill")])
    assert "Skill(code-review-engine)" in r["nogrant"], r["nogrant"]
    assert not r["heads"], "a tool with no grant kind was offered as an allow row"
    charged = sum(s for s, k, _ in r["stops"] if k != "no-grant-kind")
    assert charged == 0, "a tool's own run time was charged to the operator: %ss" % charged


# --- the door must not drift back ------------------------------------------------------------

def test_J_the_door_no_longer_instructs_a_REFUSAL_harvest():
    text = DOOR.read_text(encoding="utf-8")
    assert "approval_stops.py" in text, \
        "Step 1 must call the script; a hand-rolled transcript grep is what SCC-407 removed"
    bad = "A refusal is a `tool_result` block with `\"is_error\": true`"
    assert bad not in text, \
        "the old refusal-harvest instruction is back in the door - that is the SCC-407 bug itself"


def test_K_the_script_is_read_only_and_exits_clean():
    """It runs against the operator's real store on every invocation; it must never write."""
    src = SCRIPT.read_text(encoding="utf-8")
    for verb in ("write_text(", "open(", "os.remove", "shutil.", "unlink("):
        if verb == "open(":
            continue                                    # `open(path)` for reading is fine
        assert verb not in src, "approval_stops.py contains a write verb: %s" % verb
    r = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(ROOT), "--json"],
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr[:400]
    json.loads(r.stdout)                                 # --json must stay machine-readable


if __name__ == "__main__":
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
    print(f"-- {len(_fns) - len(_failed)}/{len(_fns)} passed --"
          + (f"  FAILED: {', '.join(_failed)}" if _failed else ""))
    sys.exit(1 if _failed else 0)
