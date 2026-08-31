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


def test_group_skips_a_command_the_live_lists_already_allow():
    """A command blocked LAST week may be allowed today. Proposing a row for it is noise —
    and noise in a pick-list is how the operator stops reading the pick-list."""
    m = _mod()
    import zoo_matcher
    rows = m.group(["git status", "npx create-next-app my-app"],
                   zoo_matcher.ALLOW, zoo_matcher.DENY)
    assert [r for r, _ in rows] == ["npx"], rows


def test_group_merges_commands_that_share_one_row():
    """One row per family, with every command it covers — not one row per command."""
    m = _mod()
    import zoo_matcher
    rows = m.group(["npx create-next-app a", "npx shadcn add button"],
                   zoo_matcher.ALLOW, zoo_matcher.DENY)
    assert len(rows) == 1, rows
    row, covers = rows[0]
    assert row == "npx" and len(covers) == 2, rows


def test_group_drops_what_the_fence_denies():
    """⛔ The door grows the ALLOW list. A denied command has no row, and inventing one would be
    the door quietly dismantling the fence one proposal at a time."""
    m = _mod()
    import zoo_matcher
    assert m.group(["git push --force"], zoo_matcher.ALLOW, zoo_matcher.DENY) == []


# --- the door: it PRINTS, and it says what it scanned ---------------------------------------

def test_zero_results_still_name_the_root_and_the_counts():
    """A4 — ⛔ "nothing found" and "broken" must not read identically.

    Measured on the sibling: from the lobby the Claude-store count is 6 and from a worktree the
    identical command returns 1, because Projects/* are gitlink stubs. A door that prints
    nothing when it finds nothing turns every environment fact into a suspected bug, and the
    operator has no way to tell which. zoo_notify.py already prints its root and its thread
    count for this reason.
    """
    m = _mod()
    root = Path("/somewhere/globalStorage/zoo/tasks")
    out = m.render([root], threads=0, blocked=[], proposals=[])
    assert str(root) in out, "the door must name the root it scanned"
    assert "0" in out, "the door must print its counts even when they are zero"
    assert "nothing" in out.lower() or "no " in out.lower(), (
        "zero results need a sentence, not an empty section")


def test_the_door_writes_nothing():
    """A4 — the door PROPOSES. Applying is the operator's, and it is a different command.

    Asserted as bytes, not as an absence of code: a door that edits an approval list is a door
    that can approve things on its own behalf.
    """
    import tempfile
    m = _mod()
    with tempfile.TemporaryDirectory() as tmp:
        store = Path(tmp) / "settings.json"
        store.write_text('{"zoo-code.allowedCommands": []}', encoding="utf-8")
        before = store.read_bytes()
        m.render([Path(tmp)], threads=1, blocked=["npx create-next-app my-app"],
                 proposals=[("npx", ["npx create-next-app my-app"])])
        assert store.read_bytes() == before, "render() touched a store"


def test_the_report_shows_each_row_with_the_commands_it_covers():
    """The operator picks rows, so a row he cannot trace back to a command is unpickable."""
    m = _mod()
    out = m.render([Path("/x/tasks")], threads=2,
                   blocked=["npx create-next-app my-app", "docker compose up -d"],
                   proposals=[("npx", ["npx create-next-app my-app"]),
                              ("docker", ["docker compose up -d"])])
    assert "npx" in out and "docker" in out
    assert "create-next-app my-app" in out, "the row must show what it unblocks"


# --- Claude: a hand-off block, never a write --------------------------------------------------

CLAUDE_SESSION = FIXTURES / "claude_session_sample.jsonl"


def test_claude_reader_pairs_the_denial_back_to_its_command():
    """A6 — the denial record does NOT carry the command.

    Claude writes the rejection as a `tool_result` holding only a `tool_use_id`; the command
    lives in the earlier assistant `tool_use` with that id. A reader that scans for the
    rejection text alone finds the denials and cannot say what was denied — which is the whole
    job. So the pairing is the assertion, not the grep.
    """
    m = _mod()
    got = m.claude_blocked_commands(CLAUDE_SESSION.read_text(encoding="utf-8").splitlines())
    assert got == ["npx create-next-app my-app", "pnpm install --frozen-lockfile"], got
    assert "git status --short" not in got, "an allowed command was never blocked"


def test_claude_reader_ignores_a_denied_non_bash_tool():
    """⛔ Re-aimed after the mutation sweep, and the re-aim is the point.

    This case first denied a `Write`, and the sweep proved it vacuous: dropping the
    `name == "Bash"` guard changed nothing, because a `Write` has no `command` field and the
    presence check already dropped it. The guard was never exercised.

    An MCP tool CAN carry a `command` input, and a refusal of one is not a Bash refusal — a
    `Bash(docker *)` rule would not have allowed it, so proposing one tells the operator he has
    fixed something he has not. That record is what isolates the guard, so the fixture carries it
    now and the `Write` stays as the no-command arm.
    """
    m = _mod()
    got = m.claude_blocked_commands(CLAUDE_SESSION.read_text(encoding="utf-8").splitlines())
    assert not any("redacted.md" in c for c in got), got
    assert "docker system prune -af" not in got, (
        "an MCP tool's refusal is not a Bash refusal, and no Bash rule would have allowed it")


def test_handoff_block_names_one_resolved_store_and_real_rules():
    """A6 — one store, resolved from where you stand, and rules in this house's own shape.

    Claude Code cannot edit its own settings, so this block is what gets pasted to an agent that
    can. It has to name an ABSOLUTE path: "add it to .claude/settings.json" is ambiguous across
    six of them in this workspace, and the one that matters is the repo you were standing in.
    """
    m = _mod()
    repo = Path("/Users/x/Some_Repo")
    block = m.claude_handoff(repo, ["npx create-next-app my-app", "pnpm install --frozen-lockfile"])
    assert str(repo / ".claude" / "settings.json") in block, block
    assert "Bash(npx *)" in block and "Bash(pnpm *)" in block, block
    assert "permissions" in block and "allow" in block


def test_handoff_writes_nothing_to_the_store_it_names():
    """A6 — asserted as bytes. The block is text to paste, not an edit."""
    import tempfile
    m = _mod()
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / ".claude").mkdir()
        store = repo / ".claude" / "settings.json"
        store.write_text('{"permissions": {"allow": []}}', encoding="utf-8")
        before = store.read_bytes()
        m.claude_handoff(repo, ["npx create-next-app my-app"])
        assert store.read_bytes() == before, "claude_handoff() touched the store it names"


def test_handoff_says_so_when_there_is_nothing_to_hand_off():
    """Same law as the Zoo half: zero results are a sentence, not an empty screen."""
    m = _mod()
    block = m.claude_handoff(Path("/Users/x/Some_Repo"), [])
    assert block.strip(), "an empty string is indistinguishable from a crash"
    assert "Bash(" not in block, "no commands means no rules"


def test_repo_root_walks_up_to_the_git_dir():
    """A6 — "the repo you are standing in" has to be resolved, not assumed to be cwd.

    The door is run from anywhere inside a tree, and the store it must name lives at the top.
    A worktree's `.git` is a FILE, not a directory, so the check is existence — testing for a
    directory silently walks past every worktree in this repo and names the lobby instead.
    """
    import tempfile
    m = _mod()
    with tempfile.TemporaryDirectory() as tmp:
        top = Path(tmp) / "repo"
        deep = top / "a" / "b"
        deep.mkdir(parents=True)
        (top / ".git").write_text("gitdir: elsewhere", encoding="utf-8")   # worktree shape
        assert m.repo_root(deep) == top.resolve()   # /var -> /private/var on the Mac


def test_handoff_rule_is_the_command_word_not_the_first_token():
    """⛔ Found by running the door against real sessions, not by reading it.

    A real refused command was `W=/Users/.../tree; cd "$W" && python3 ...`. Splitting on
    whitespace and taking [0] proposed `Bash(W=/Users/.../tree; *)` — a rule that matches
    exactly one command that will never be typed again, offered to the operator as though it
    were useful. Multi-line commands were worse: the whole block became one "token".

    So the rule comes from the command WORD of each shell piece, using the same splitter the
    matcher uses, and a leading VAR=value assignment is stepped over rather than named.
    """
    m = _mod()
    block = m.claude_handoff(
        Path("/Users/x/Some_Repo"),
        ['W=/tmp/tree; cd "$W" && python3 .agents/scripts/tests/run_all.py'])
    assert "Bash(W=" not in block, "an assignment is not a command word"
    assert "Bash(cd *)" in block or "Bash(python3 *)" in block, block


def test_handoff_covers_every_piece_of_a_multiline_command():
    """One refusal can carry several commands, and a rule for only the first leaves the operator
    approving the same block again tomorrow for the second."""
    m = _mod()
    block = m.claude_handoff(Path("/Users/x/Some_Repo"),
                             ["git fetch origin main\ngit log --oneline -1"])
    assert "Bash(git *)" in block, block


def test_a_redirection_is_not_a_command_word():
    """⛔ Also found by running the door, not by reading it.

    `acli jira workitem view SCC-352 2>&1 | head -100` proposed `Bash(1 *)`. The matcher's
    splitter breaks on `&`, so `2>&1` becomes a piece whose first token is the bare digit `1`
    — and `decide()` never sees that because it masks redirections BEFORE it splits. Reusing
    the splitter without reusing the mask reproduced the exact bug the mask exists to prevent,
    one layer up.
    """
    m = _mod()
    words = m.command_words("acli jira workitem view SCC-352 2>&1 | head -100")
    assert "1" not in words, words
    assert "acli" in words and "head" in words, words


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
