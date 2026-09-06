"""guard-branch-delete.py — the PreToolUse hook that fences `git branch`'s DELETE by TARGET (SCC-411).

⛔ THE HOLE THIS CLOSES, measured 2026-09-06 at `aa408738` against the rendered lists:

    git branch -d chore/SCC-1-x main   ->  allow on zoo, claude AND antigravity
    git branch -r -d origin/main       ->  allow on all three
    git branch -v -d main              ->  allow on claude (`Bash(git branch -v:*)`)
    git branch --delete main           ->  allow on zoo and antigravity

`git branch -d` takes a LIST, and every permission grammar in this house matches a PREFIX or a
per-token regex from the LEFT. Neither can say "exactly one argument, and it starts with chore/",
so the first target satisfies the rule and every target after it rides free — with no shell
metacharacter for a splitter to see. Real git 2.43, verified in a throwaway repo:

    $ git branch -d worktree-agent-x main
    Deleted branch worktree-agent-x (was 9dd7d8f).
    Deleted branch main (was 9dd7d8f).

Claude runs hooks, so on THIS platform the whole family closes in one place. Zoo and Antigravity
get deny rows for every spelling their grammars can express (test_zoo_permissions.py,
test_permission_parity.py); the `-d <list>` escape stays a documented residual there.

⛔ THE TWO LOAD-BEARING INVARIANTS, inherited from shape-block.py:
`test_never_asks` — an ask is an auto-DENY in auto mode and would strand a headless run; and
`test_fails_open_on_what_it_cannot_read` — a guard handed garbage says NOTHING.

⭐ BUT "fails open" IS SCOPED, and the scope is the whole point. Silence is the answer to *"this
is not a branch delete"*. It is NOT the answer to *"this IS a branch delete and I cannot prove the
targets are safe"* — there, the guard DENIES. A guard that shrugged at
`git branch -d "$BRANCH"` would be decorative: the one case an attacker or a careless door
actually produces is the one it cannot read.

run_all.py executes test files bare (python3 <file>, no pytest), so the __main__ harness at the
bottom is what makes this file COUNT (house scar: suite-red-file-may-have-run-nothing).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOOK = ROOT / ".agents" / "hooks" / "guard-branch-delete.py"
INDEX = ROOT / ".agents" / "hooks" / "INDEX.md"
GIT_POLICY = ROOT / ".agents" / "rules" / "git-policy.md"


def run_hook(command: str | None, raw: str | None = None, tool: str = "Bash"):
    payload = raw if raw is not None else json.dumps({
        "session_id": "test", "cwd": str(ROOT), "hook_event_name": "PreToolUse",
        "tool_name": tool, "tool_input": {"command": command},
    })
    p = subprocess.run([sys.executable, str(HOOK)], input=payload, text=True,
                       capture_output=True, cwd=str(ROOT), timeout=30, errors="replace")
    out = p.stdout.strip()
    parsed = None
    if out:
        try:
            parsed = json.loads(out)
        except json.JSONDecodeError:
            parsed = {"__unparseable__": out}
    return p.returncode, parsed, p.stderr


def decision(parsed) -> str | None:
    return ((parsed or {}).get("hookSpecificOutput") or {}).get("permissionDecision")


def reason(parsed) -> str:
    return ((parsed or {}).get("hookSpecificOutput") or {}).get("permissionDecisionReason", "") or ""


# ── DENY · the measured holes, one case per spelling ────────────────────────────────────────

DENIED = {
    "the multi-argument list — the whole reason this hook exists":
        "git branch -d chore/SCC-1-x main",
    "the -D spelling of the same list":
        "git branch -D claude/AVCH-1-x main",
    "a third target hiding behind two legal ones":
        "git branch -d chore/a claude/b main",
    "--delete, the long form no deny grammar reaches":
        "git branch --delete main",
    "-f -d, the flag order the deny expects in position one":
        "git branch -f -d main",
    "-f --delete, the same escape in long form":
        "git branch -f --delete main",
    "-v -d — real git deletes, and `Bash(git branch -v:*)` reads as a LIST grant":
        "git branch -v -d main",
    "-vv -d, the same":
        "git branch -vv -d main",
    "--format=... -d, the same (measured rc=0, branch deleted)":
        "git branch --format=%(refname) -d main",
    "-r -d, the remote-tracking delete that reads allow on all three":
        "git branch -r -d origin/main",
    "-rd, the getopt cluster of it":
        "git branch -rd origin/main",
    "-r --delete, the long form of it":
        "git branch -r --delete origin/main",
    "a remote-tracking ref is NEVER a lane delete, even under a lane-shaped name":
        "git branch -r -d origin/chore/SCC-1-x",
    "the flagship, whatever the fence says":
        "git branch -d main",
    "a backtick substitution cannot be read, so the targets cannot be proved":
        "git branch -d chore/x `echo main`",
    "a $() substitution, the same":
        "git branch -d chore/x $(echo main)",
    "a variable target cannot be read either — THE case a shrugging guard would miss":
        'git branch -d "$BRANCH"',
    "behind a cd compound, the house command shape":
        "cd /home/dlohn/Sudo_Hatter_Command && git branch -d chore/x main",
    "behind the git -C launder (denied elsewhere; this hook does not depend on that)":
        "git -C /home/dlohn/Sudo_Hatter_Command branch -d main",
    "behind a git -c config override":
        "git -c core.hooksPath=/dev/null branch -d main",
    "second in a chain, after something innocent":
        "git status --short && git branch -d main",
    "with the env -u twin the doors print":
        "env -u GITHUB_TOKEN git branch -d chore/x main",
    # ── THE NAMESPACE BOUND. Without these three, widening the lane test from `chore/` to `c`
    # (or dropping the trailing slash) passes every case above, because `main` and `origin/main`
    # fail a one-character test just as surely as a five-character one. Each row below is ONE
    # character from a legal target.
    "a near-miss on chore/ — one character from legal":
        "git branch -d chores/SCC-1-x",
    "a near-miss on claude/":
        "git branch -d claudex/SCC-1-x",
    "a near-miss on epic/":
        "git branch -d epics/SCC-1-x",
    # ── THE REMOTE BOUND. Every other -r row above also fails the namespace test (`origin/main`
    # is not a lane), so without THIS row the remote arm could be deleted and nothing would go
    # red — an unfalsifiable branch is not a fence. Here the target IS lane-shaped, so only the
    # remote arm can refuse it.
    "a remote-tracking ref that happens to be lane-shaped — only the -r arm catches this":
        "git branch -r -d chore/SCC-1-x",
    # ── THE OPTIONAL-ARGUMENT HOLE (SCC-411 review). `--color`, `-t` and `--track` take an
    # OPTIONAL argument, so real git 2.43 does NOT consume the next token — but the hook's
    # value-skip did, and the token it swallowed was the delete flag. Measured: every one of
    # these deleted the branch with the guard SILENT, and the first two read allow on all three
    # platforms via the `-v`/`-vv` read grants. One row per spelling: they are three separate
    # entries in the flag list and a fix that only drops one leaves the other two live.
    "--color between a read flag and the delete flag":
        "git branch -v --color -d main",
    "-t between a read flag and the delete flag":
        "git branch -vv -t -d main",
    "--track between a read flag and the delete flag":
        "git branch -v --track -d main",
    "an optional-argument flag AFTER the delete flag, eating the target instead":
        "git branch -d --color main",
    # ── THE SAME HOLE'S SECOND FACE: the target is eaten and the list comes back EMPTY. Silence
    # there is the shrug the docstring forbids, so an empty target list on a delete is a refusal.
    "a delete whose target was swallowed, leaving nothing readable":
        "git branch -d --sort main",
    # ⛔ THIS ROW IS WHAT MAKES THE SKIP-REFUSAL FALSIFIABLE, and it was missing until the sweep
    # asked. `--sort` genuinely DOES consume its value, so it is still in `_VALUE_FLAGS`; only
    # the "never skip a token starting with `-`" rule stops it eating the delete flag here.
    # Every other row in this block is closed by a second, independent fix as well.
    "a genuinely value-taking flag immediately before the delete flag":
        "git branch --sort -d main",
    # ── A LINE CONTINUATION IS ONE COMMAND. The shell rejoins `\` + newline; the splitter did
    # not, so the verb and its delete flag landed in two different segments and neither looked
    # like a delete.
    "a backslash line continuation between the verb and the delete flag":
        "git branch -v \\\n-d main",
    # ── PRE-SUBCOMMAND OPTIONS THAT TAKE A SEPARATE VALUE ended the invocation match.
    "--work-tree with a separate value in front of the subcommand":
        "git --work-tree /tmp branch -d main",
    # ── A SHELL BODY IS A COMMAND, not an argument. The quote-masking that stops this hook
    # refusing a `grep` for its own literals must NOT stop it reading a script the shell runs.
    "a delete inside a shell -c body":
        'bash -c "git branch -d main"',
    # ── `--` ends flag parsing, so what follows is a target no matter how it is spelled.
    "a dash-leading target after the end-of-flags marker":
        "git branch -d -- -dashy",
}


def test_the_tokenizer_has_not_DRIFTED_from_the_sibling_it_copies():
    """`tokenize()` is a deliberate copy of `allow-readonly-chain.py`'s, and copies drift.

    ⛔ WHY A COPY AND NOT A SHARED HELPER. The sibling's `split_atoms` REFUSES on odd input, which
    is safe there (refusing grants nothing) and wrong here (refusing would fence nothing), so this
    hook cannot delegate its splitter. The tokenizer alone could be shared, but the two use
    DIFFERENT quote sets - this one treats a backtick as a quote - so extracting it would change
    the sibling's behaviour, in a fence that is not this lane's to touch.

    So the copy stays and the DRIFT is what gets fenced: fix a tokenizer bug in one and this goes
    red naming the other. That is the whole risk the duplication carries (SCC-411 review).
    """
    import ast

    def body(path: Path, const: str) -> str:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "tokenize":
                src = ast.unparse(node)
                # The docstrings differ on purpose; the CODE must not.
                if ast.get_docstring(node):
                    node.body = node.body[1:]
                    src = ast.unparse(node)
                return src.replace(const, "QUOTESET")
        raise AssertionError(f"no tokenize() in {path}")

    hooks = Path(__file__).resolve().parents[2] / "hooks"
    mine = body(hooks / "guard-branch-delete.py", "_QUOTES")
    theirs = body(hooks / "allow-readonly-chain.py", "QUOTES")
    assert mine == theirs, (
        "guard-branch-delete.tokenize has drifted from allow-readonly-chain.tokenize. They are "
        "deliberate copies (see this test's docstring): fix BOTH, or make the divergence "
        "explicit here.\n--- guard ---\n" + mine + "\n--- sibling ---\n" + theirs)


def test_the_batteries_did_not_shrink():
    """A row deleted from either dict is a fence quietly retired, and every other case here
    still passes. The zoo battery pins its own length for the same reason (SCC-411 review)."""
    assert len(DENIED) >= 36, f"DENIED lost rows: {len(DENIED)}"
    assert len(ALLOWED) >= 23, f"ALLOWED lost rows: {len(ALLOWED)}"


def test_every_measured_delete_hole_is_DENIED():
    bad = {}
    for why, cmd in DENIED.items():
        _, parsed, err = run_hook(cmd)
        if decision(parsed) != "deny":
            bad[why] = f"{cmd!r} -> {decision(parsed)!r} {err.strip()[:120]}"
    assert not bad, "these delete spellings were not denied:\n  " + "\n  ".join(
        f"{k}: {v}" for k, v in bad.items())


def test_the_refusal_names_the_offending_target_and_the_remedy():
    # ⛔ THE TARGET MUST BE ONE THE PROSE CANNOT SAY BY ITSELF. This asserted `"main" in text`,
    # and the refusal's own static wording contains "main" three times - so replacing the
    # interpolated target list with a constant left the case GREEN (SCC-411 review, gate lens
    # F3). A hook that names the wrong branch, or none, passed the one test written to prove it
    # names the right one. `zzz-victim` appears in no reason string in the file.
    _, parsed, _ = run_hook("git branch -d chore/SCC-1-x zzz-victim")
    text = reason(parsed)
    assert "zzz-victim" in text, f"the refusal must name what it refused to delete: {text!r}"
    assert "chore/" in text and "claude/" in text and "epic/" in text, (
        f"the refusal must state which namespaces ARE deletable: {text!r}")


# ── SILENCE · the ceremonies the doors actually print, and every non-delete ──────────────────

ALLOWED = {
    "smh-close-task-merge-tree.md:763":
        "git branch -d chore/SCC-411-bugs-cycle-11",
    "smh-merge-multiple-workingtrees.md:398 — the quoted spelling":
        'cd "$REPO" && git branch -d "chore/SCC-351-zoo-approvals"',
    "cicd-prune-worktree.md:343":
        "git branch -d claude/SCC-100-story-slug",
    "cicd-create-epic-sprint.md:280 — the epic close's forced delete":
        'cd "$P" && git checkout main && cd "$P" && git branch -D epic/SCC-100-slug',
    "cicd-push-e2e.md:413":
        "git branch -d epic/SCC-100-slug",
    "two lane branches at once is still every-target-safe":
        "git branch -d chore/SCC-1-a claude/SCC-1-b",
    "a listing is not a delete":
        "git branch --list",
    "-a is not a delete (and git REFUSES -a with -d anyway)":
        "git branch -a",
    "-r alone is a read of remote-tracking refs":
        "git branch -r",
    "creating a branch":
        "git branch chore/SCC-1-new",
    "setting an upstream":
        "git branch --set-upstream-to=origin/chore/x chore/x",
    "a rename carries no d/D":
        "git branch -m old-name new-name",
    "--format with no delete flag":
        "git branch --format=%(refname) --list",
    "a substitution with NO delete flag is not this hook's business":
        "git branch --list $(echo chore/x)",
    "not git at all":
        "python3 .agents/scripts/tests/run_all.py --delete main",
    "a different git verb entirely":
        "git status --short",
    "the word branch in another position":
        "git checkout -b chore/SCC-1-x",
    # ── A COMMAND'S TEXT IS NOT WHAT IT RUNS (SCC-411 review). The hook matched its own literals
    # anywhere in the command, so searching this repo for the hole it fences, and writing the
    # commit message that describes it, were both REFUSED. A guard that fences the description
    # of a delete instead of the delete is not stricter, it is wrong — and this repo ships a test
    # file and a git-policy section full of exactly these strings.
    "searching the repo for the literal this hook fences":
        'grep -rn "git branch -d main" .agents/',
    "the same search in single quotes":
        "grep -rn 'git branch -D main' docs/",
    "a commit message DESCRIBING the fence":
        'git commit -m "SCC-411 feat(gate): deny git branch -d main"',
    "a trailing shell comment mentioning a delete that never runs":
        "git branch -d chore/SCC-1-x  # not git branch -d main",
    # ── THE CHAIN SPLITTER IS LOAD-BEARING AND NOTHING BOUNDED IT: with `_SEPARATORS = ""` the
    # whole file stayed green, because no row put ceremony AFTER a legal lane delete. This is the
    # shape `/cicd-prune-worktree` actually prints.
    "a legal lane delete followed by more ceremony":
        "git branch -d chore/SCC-1-x && git worktree prune",
    # ⛔ AND THIS ROW IS WHAT MAKES THE FLAG-LIST CORRECTION FALSIFIABLE. Put `--color` back into
    # `_VALUE_FLAGS` and it eats `chore/SCC-1-x`, the target list comes back empty, and this legal
    # lane delete is REFUSED. Without this row the list correction is belt-and-braces that no case
    # can tell from the belt alone - the same unfalsifiability M8 exposed in pass 1 of the sweep.
    # The flag must sit BETWEEN the delete flag and the target — that is the only position where
    # a wrong `_VALUE_FLAGS` entry can eat the target. In front of `-d` the skip-refusal already
    # covers it, which is exactly why the first spelling of this row let M17 survive.
    "an optional-argument flag between the delete flag and a LEGAL lane target":
        "git branch -d --color chore/SCC-1-x",
}


def test_every_real_ceremony_stays_SILENT():
    bad = {}
    for why, cmd in ALLOWED.items():
        _, parsed, err = run_hook(cmd)
        if parsed is not None:
            bad[why] = f"{cmd!r} -> {parsed} {err.strip()[:120]}"
    assert not bad, "these must pass through untouched:\n  " + "\n  ".join(
        f"{k}: {v}" for k, v in bad.items())


# ── the load-bearing invariants ─────────────────────────────────────────────────────────────

def test_never_asks():
    src = HOOK.read_text(encoding="utf-8")
    assert '"ask"' not in src, (
        "the JSON value ask must not exist in this file — it is an auto-DENY in auto mode and "
        "would strand a headless run (shape-block.py's law)")
    for cmd in list(DENIED.values()) + list(ALLOWED.values()):
        _, parsed, _ = run_hook(cmd)
        assert decision(parsed) != "ask", f"{cmd!r} produced an ask: {parsed}"


def test_fails_open_on_what_it_cannot_read():
    rc, parsed, _ = run_hook(None, raw="this is not json")
    assert rc == 0 and parsed is None, f"garbage stdin must be silence: rc={rc} {parsed}"
    rc, parsed, _ = run_hook("git branch -d main", tool="Write")
    assert rc == 0 and parsed is None, f"a non-Bash tool must be silence: rc={rc} {parsed}"
    rc, parsed, _ = run_hook("")
    assert rc == 0 and parsed is None, f"an empty command must be silence: rc={rc} {parsed}"
    rc, parsed, _ = run_hook(None, raw=json.dumps({"tool_name": "Bash", "tool_input": {}}))
    assert rc == 0 and parsed is None, f"a missing command must be silence: rc={rc} {parsed}"


def test_fails_CLOSED_on_a_delete_it_cannot_read():
    """⛔ THE SCOPE OF "fails open". Silence answers "not a branch delete". It must NEVER answer
    "a branch delete whose targets I could not prove safe" - that is the whole attack surface."""
    for cmd in ('git branch -d "unterminated',
                "git branch -d chore/x `whoami`",
                'git branch -d "$B"',
                "git branch -d ${BRANCH}",
                # ⛔ THE CASES THE FIRST CUT MISSED, and a surviving mutant is what found them.
                # Deleting `$` from _UNREADABLE left every row above still denied — each one also
                # fails the namespace test, so the readability half was carrying nothing and the
                # sweep said so (M8 SURVIVED, 2026-09-06). These two are the rows only the
                # readability half can refuse, because the target is LANE-SHAPED until the shell
                # expands it:
                #   BRANCH="x main"  ->  git branch -d chore/$BRANCH  ->  git branch -d chore/x main
                # An unquoted expansion WORD-SPLITS, so one lane-shaped word becomes two targets
                # and the second one is `main`. The quoted form cannot split but still resolves to
                # a name nothing here has read.
                'git branch -d "chore/$BRANCH"',
                "git branch -d chore/$(git rev-parse --abbrev-ref HEAD)",
                "git branch -d claude/`whoami`"):
        _, parsed, _ = run_hook(cmd)
        assert decision(parsed) == "deny", f"unreadable delete must DENY, got {decision(parsed)!r}: {cmd!r}"


# ── wiring · the real settings file, not a fixture ──────────────────────────────────────────

def test_wired_inside_the_single_pretooluse_bash_group():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    groups = [g for g in settings["hooks"]["PreToolUse"] if g.get("matcher") == "Bash"]
    assert len(groups) == 1, f"there must be exactly one PreToolUse Bash group: {len(groups)}"
    cmds = [h["command"] for h in groups[0]["hooks"]]
    mine = [c for c in cmds if ".agents/hooks/guard-branch-delete.py" in c]
    assert len(mine) == 1, f"guard-branch-delete.py must be wired exactly once: {cmds}"
    assert all("run-hook.sh" in c for c in mine), (
        f"dispatch through run-hook.sh, never a named interpreter: {mine}")


def test_the_hooks_INDEX_carries_it():
    text = INDEX.read_text(encoding="utf-8")
    assert "guard-branch-delete.py" in text, ".agents/hooks/INDEX.md has no row for the guard"


def test_git_policy_names_it_as_a_claude_side_fence():
    """SCC-411 audit finding 2: git-policy.md enumerates the Claude-side git fences. A guard that
    is not named there gets re-derived as absent, and the escape gets filed as a bug again."""
    text = GIT_POLICY.read_text(encoding="utf-8")
    assert "guard-branch-delete.py" in text, (
        ".agents/rules/git-policy.md does not name the branch-delete guard - the next agent will "
        "read that rule, find only require-push-approval.py, and re-file this row")


if __name__ == "__main__":
    import traceback
    _fns = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    _failed = []
    for _name, _fn in _fns:
        try:
            _fn()
        except BaseException:
            _failed.append(_name)
            traceback.print_exc()
    print(f"-- {len(_fns) - len(_failed)}/{len(_fns)} passed --")
    if _failed:
        print(f"FAILED: {', '.join(_failed)}")
    sys.exit(1 if _failed else 0)
