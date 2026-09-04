"""The read-only-chain auto-allow hook: what it may permit, and everything it must not (SCC-287).

⛔ WHY THIS HOOK IS ALLOWED TO SEE A METACHARACTER AT ALL, WHEN `allow-scratchpad.py` IS NOT.
That file's rule 1 refuses every metacharacter because its allow-list is over PATHS: it says yes
to `rm -rf <path>`, so a construct it misparses is a delete in the wrong place. This one's
allow-list is over VERBS, and every verb on it reads. The four characters it adds - `'`, `"`,
`|`, `&`, `;` - are paid for by three rules that this file exists to pin:

    rule 2  a separator inside quotes, or an unbalanced quote, is a REFUSAL, not a guess -
            so the split this hook performs provably equals the shell's
    rule 3  `&` only ever as `&&` (a lone `&` BACKGROUNDS, detaching the command from the
            approval that authorised it); `;` exactly one; `|` one or two
    rule 4  flags are an allow-list PER VERB, because a read-only verb is not enough:
            `sort -o`, `sed -i`, `find -exec` and `find -delete` all write

⛔ AND THE CLAIM THAT MATTERS IS "GRANTS NOTHING NEW", WHICH IS TESTED IN BOTH DIRECTIONS.
Two independent conditions must hold for every atom: (A) the committed read-only verb+flag list,
(B) the atom already matches one of the operator's own `permissions.allow` rules. Blocks J and K
prove each one is load-bearing by defeating it alone - a command that satisfies (A) and no rule,
and a command that satisfies a rule and not (A). Without those two blocks a mutant that deleted
either condition would survive, and the "nothing new" claim would be prose.

⭐ THE FIXTURE RULE SET DELIBERATELY CONTAINS MUTATING RULES. The operator really does allow
`Bash(git checkout *)`, `Bash(git add:*)`, `Bash(cp:*)`, and this hook must refuse all of them
inside a chain. A fixture carrying only read-only rules would prove nothing about (A).

⛔ THE HOOK HAS EXACTLY TWO LEGAL OUTPUTS: `allow`, or SILENCE. Never `ask`, never `deny`.
`ask` is auto-DENY in non-interactive mode. `allowed()` and `silent()` below are deliberately NOT
each other's negation, so an `ask` or a `deny` fails both.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, posix_sh

ROOT = SCRIPTS.parents[1]
HOOK = SCRIPTS.parent / "hooks" / "allow-readonly-chain.py"

# The operator's real rule set, reduced to the SHAPES that matter. Read-only rules, mutating
# rules, a wildcard rule, a two-word rule, and two rules (`tee`, `bash`) whose verbs are off the
# committed list on purpose - block J turns those into the proof that (A) is doing work.
RULES = [
    "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(grep:*)", "Bash(rg:*)",
    "Bash(find:*)", "Bash(wc:*)", "Bash(sort:*)", "Bash(uniq:*)", "Bash(cut:*)", "Bash(tr:*)",
    "Bash(sed -n:*)", "Bash(diff:*)", "Bash(stat:*)", "Bash(file:*)", "Bash(du:*)",
    "Bash(echo:*)", "Bash(cmp:*)", "Bash(basename:*)", "Bash(dirname:*)",
    "Bash(acli jira workitem view:*)", "Bash(acli jira workitem search:*)",
    # ⚠ `--yes` is not decoration: `test_jira_feed.py`'s yes-guard scans every `workitem
    # transition` under `.agents/` and fails any that could sit waiting for a prompt an agent
    # shell cannot answer. These are refusal fixtures and never run, but the guard reads text.
    "Bash(acli jira workitem transition --yes *)", "Bash(acli jira workitem create:*)",
    "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(git show:*)",
    "Bash(git rev-parse:*)", "Bash(git ls-files:*)", "Bash(git branch --list:*)",
    "Bash(git worktree list:*)", "Bash(git stash list:*)",
    "Bash(git -C * status:*)", "Bash(git -C * log:*)", "Bash(git -C * diff:*)",
    # ⭐ MUTATING, and really in the operator's file. (A) must refuse every one of these.
    "Bash(git checkout *)", "Bash(git add:*)", "Bash(git commit:*)", "Bash(git merge *)",
    "Bash(git branch -d chore/*)", "Bash(git worktree remove *)", "Bash(git push origin main*)",
    "Bash(cp:*)", "Bash(mkdir:*)",
    # Verbs that are off the committed read-only list even though a rule names them.
    "Bash(tee:*)", "Bash(bash:*)", "Bash(cd:*)",
    "Bash(python3 .agents/scripts/:*)", "Bash(python3 /private/tmp/claude-501/:*)",
]


def seed(d: Path, allow: list[str] | None = None, deny: list[str] | None = None,
         ask: list[str] | None = None) -> Path:
    """A synthetic project root carrying nothing but a permissions file.

    ⭐ The hook judges the command STRING and reads only settings; it never touches the tree. So
    a fixture root needs no repo, no worktree and no files.
    """
    (d / ".claude").mkdir(parents=True, exist_ok=True)
    perms: dict = {"allow": RULES if allow is None else allow}
    if deny:
        perms["deny"] = deny
    if ask:
        perms["ask"] = ask
    (d / ".claude" / "settings.json").write_text(
        json.dumps({"permissions": perms}), encoding="utf-8")
    return d


def call(command: str, root: Path, raw: str | None = None,
         tool: str = "Bash") -> tuple[int, str]:
    """Run the hook against a synthetic root.

    ⛔ `HOME` IS REDIRECTED AT THE FIXTURE TOO. `permission_rules()` also reads
    `~/.claude/settings.json`, and on the machine this was written that file may carry rules of
    its own - so every REFUSAL case would be judged against the developer's real permissions and
    could pass, or fail, for a reason no fixture states. `USERPROFILE` is the same lever on the
    PC, where `expanduser` does not read `HOME`.
    """
    if raw is None:
        raw = json.dumps({"tool_name": tool, "tool_input": {"command": command},
                          "session_id": "fixture"})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root),
           "HOME": str(root), "USERPROFILE": str(root)}
    p = subprocess.run([sys.executable, str(HOOK)], input=raw, env=env,
                       capture_output=True, text=True, errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def allowed(out: str) -> bool:
    try:
        return (json.loads(out.strip())["hookSpecificOutput"]["permissionDecision"] == "allow")
    except Exception:  # noqa: BLE001
        return False


def silent(out: str) -> bool:
    return out.strip() == ""


def main() -> int:
    c = Cases("allow-readonly-chain: the compound commands it may permit (SCC-287)")

    with TempDir() as tmp:
        root = seed(tmp)

        # ── A · ANTI-VACUITY · the fixture is real, and the hook can say yes ────────────────
        if c.block("A · anti-vacuity - the fixture grants at all"):
            _, out = call("git diff | grep -n def", root)
            c.check("A1 a plain read-only pipeline IS allowed", allowed(out), out.strip()[:200])
            code, out = call("git diff | grep -n def", root)
            c.check("A2 and it exits 0", code == 0, f"exit={code}")
            # If the rules file could not be read at all, every case below would pass by
            # accident. This is what says the fixture wired through.
            _, out = call("cat x.txt", root)
            c.check("A3 a single allow-listed command is allowed (rules loaded)",
                    allowed(out), out.strip()[:200])

        # ── B · THE SHAPES THIS EXISTS FOR ───────────────────────────────────────────────────
        # Every one of these is a real command from the transcript that measured the problem.
        if c.block("B · the real compound commands it must unblock"):
            for label, cmd in [
                ("pipe", "git diff --stat | tail -20"),
                ("pipe into wc", "git ls-files | wc -l"),
                ("two pipes", "git log --oneline -20 | grep -n SCC | head -5"),
                ("chain", "git status --short && git log --oneline -5"),
                ("semicolon", "ls -la ; git status --short"),
                ("or-chain", "git rev-parse --short HEAD || echo none"),
                ("quoted operand with a space", "grep -rn SCC-287 . | head -20"),
                ("sed -n through a pipe", "git show HEAD | sed -n 1,40p"),
                ("git -C wildcard rule", "git -C /tmp/lane status --short | head -5"),
                ("sort into uniq", "git log --format=%an | sort | uniq -c"),
                ("find into grep", "find . -name INDEX.md | head -5"),
                ("interpreter as pipe SOURCE",
                 "python3 .agents/scripts/check_maps.py | tail -20"),
            ]:
                _, out = call(cmd, root)
                c.check(f"B · allows {label}", allowed(out), f"{cmd!r} -> {out.strip()[:160]}")

        # ── C · RULE 1 · the character allow-list ────────────────────────────────────────────
        # ⛔ Each of these is a construct `allow-scratchpad.py`'s SCC-263 review found an escape
        # in. They are unreachable here BY CONSTRUCTION, and "unreachable by construction" is a
        # claim until it is an assertion.
        if c.block("C · rule 1 - every construct the character set excludes"):
            for label, cmd in [
                ("redirect", "git diff | tee out.txt > saved.txt"),
                ("append redirect", "git log --oneline >> log.txt"),
                ("heredoc", "cat <<EOF | head -1"),
                ("here-string", "cat <<< hello | wc -l"),
                ("input redirect", "wc -l < file.txt"),
                ("command substitution", "git log -1 --format=$(echo %H) | cat"),
                ("backtick substitution", "echo `git rev-parse HEAD` | cat"),
                ("subshell", "(git status) | head -5"),
                ("variable expansion", "echo $HOME | cat"),
                ("glob", "grep -n SCC *.py | head -5"),
                ("brace expansion", "cat file.{a,b} | wc -l"),
                ("bracket glob", "ls [ab]* | wc -l"),
                ("comment hiding the tail", "git status --short | head -5 # rm -rf ."),
                ("history expansion", "echo hi | grep -n !!"),
                ("backslash continuation", "git status \\ | head -5"),
            ]:
                _, out = call(cmd, root)
                c.check(f"C · silent on {label}", silent(out), f"{cmd!r} -> {out.strip()[:160]}")

        # ── D · RULE 2 · quotes, and refusing rather than guessing ──────────────────────────
        if c.block("D · rule 2 - a separator inside quotes is a refusal, not a guess"):
            # ⛔ THE WHOLE REASON RULE 2 EXISTS. The shell runs ONE grep here. A splitter that
            # split on the quoted `;` would be describing a command that is never run - and the
            # only honest answer to a parse it cannot vouch for is silence.
            for label, cmd in [
                ("a semicolon inside double quotes", 'grep -n "a;b" file.txt'),
                ("a pipe inside double quotes", 'grep -n "a|b" file.txt'),
                ("an ampersand inside single quotes", "grep -n 'a&&b' file.txt"),
                ("an unbalanced double quote", 'grep -n "abc | head -5'),
                ("an unbalanced single quote", "grep -n 'abc | head -5"),
            ]:
                _, out = call(cmd, root)
                c.check(f"D · silent on {label}", silent(out), f"{cmd!r} -> {out.strip()[:160]}")
            # ...and a quoted operand with NO separator in it is ordinary, and must still work.
            _, out = call('grep -rn "def main" . | head -20', root)
            c.check("D · a quoted operand with a space is still allowed",
                    allowed(out), out.strip()[:160])

        # ── E · RULE 3 · separator runs are exact ────────────────────────────────────────────
        if c.block("E · rule 3 - `&&` only, one `;`, one or two `|`"):
            for label, cmd in [
                # ⛔ A LONE `&` BACKGROUNDS. The command detaches from the approval that
                # authorised it and outlives the turn; nothing downstream can see it finish.
                ("a lone & (backgrounding)", "git status --short & git log --oneline -5"),
                ("a trailing & ", "git status --short &"),
                ("a doubled ;;", "ls -la ;; git status"),
                ("a tripled |||", "git diff ||| head -5"),
                ("a leading separator", "| git status --short"),
                ("a trailing separator", "git status --short |"),
                ("an empty atom between separators", "git status && && git log"),
            ]:
                _, out = call(cmd, root)
                c.check(f"E · silent on {label}", silent(out), f"{cmd!r} -> {out.strip()[:160]}")

        # ── F · RULE 4 · a read-only VERB is not enough ─────────────────────────────────────
        # ⛔ THE CLASS THIS BLOCK OWNS: every one of these commands has an allow-listed verb, an
        # allow rule that matches it, and WRITES. If the flag allow-list were dropped, all six
        # would be granted and every other block here would still be green.
        if c.block("F · rule 4 - the flags that turn a read-only verb into a write"):
            for label, cmd in [
                ("sort -o writes a file", "git log --oneline | sort -o out.txt"),
                ("sort --output writes a file", "git log --oneline | sort --output=out.txt"),
                ("sed -i edits in place", "git status --short && sed -i s/a/b/ AGENTS.md"),
                ("sed -i.bak glues its value to the flag",
                 "git status --short && sed -n -i.bak s/a/b/ AGENTS.md"),
                ("find -delete unlinks every hit", "find . -name x.tmp -delete | wc -l"),
                ("find -exec runs anything", "find . -name x -exec rm -rf . + | wc -l"),
                ("find -fprint writes a named file", "find . -name x -fprint out.txt | wc -l"),
                ("git --output= is a diff option on log, diff AND show",
                 "git diff --output=stolen.txt | head -1"),
                ("git -c rewrites configuration for the call",
                 "git -c core.hooksPath=none status --short | head -5"),
                ("an unlisted flag on a listed verb", "cat --unknown-flag f | head -1"),
            ]:
                _, out = call(cmd, root)
                c.check(f"F · silent on {label}", silent(out), f"{cmd!r} -> {out.strip()[:160]}")
            # ⛔ EXACT MATCH BEFORE BUNDLING, or `find -name` reads as `-n -a -m -e`. Both
            # spellings are pinned because getting one right at the cost of the other is the
            # regression this ordering exists to prevent.
            _, out = call("find . -maxdepth 2 -name INDEX.md | head -5", root)
            c.check("F · a single-dash long predicate is NOT bundle-split",
                    allowed(out), out.strip()[:160])
            _, out = call("git diff | grep -rn SCC | head -5", root)
            c.check("F · a genuine short bundle (-rn) still works", allowed(out),
                    out.strip()[:160])

        # ── G · RULE 5 · a quoted flag is still a flag ───────────────────────────────────────
        if c.block("G · rule 5 - the shell strips the quotes, so the flag test must too"):
            _, out = call('git log --oneline | sort "-o" out.txt', root)
            c.check("G1 a double-quoted -o is still refused", silent(out), out.strip()[:160])
            _, out = call("git log --oneline | sort '-o' out.txt", root)
            c.check("G2 a single-quoted -o is still refused", silent(out), out.strip()[:160])
            _, out = call('find . -name x "-delete" | wc -l', root)
            c.check("G3 a quoted -delete is still refused", silent(out), out.strip()[:160])
            # ⛔ AND THE OTHER HALF OF THE SAME RULE, which a naive `.split()` got backwards.
            # `grep "a -o b" f` is a grep for the TEXT `a -o b` - the shell hands grep one argv
            # element, and there is no flag in it. Splitting on whitespace invented one and
            # refused the command; the same bug refused `acli … --jql 'a >= -3d'` over a token
            # spelled `-3d'`. What the verb receives is what rule 4 must judge.
            _, out = call('grep -n "a -o b" AGENTS.md | head -3', root)
            c.check("G4 a flag-shaped WORD inside one quoted argument is an operand",
                    allowed(out), out.strip()[:160])

        # ── H · RULE 6 · an interpreter may not be a pipe sink ───────────────────────────────
        if c.block("H · rule 6 - an interpreter reading its program off a pipe"):
            _, out = call("python3 .agents/scripts/check_maps.py | head -20", root)
            c.check("H1 an interpreter as the pipe SOURCE is allowed", allowed(out),
                    out.strip()[:160])
            _, out = call("cat evil.py | python3", root)
            c.check("H2 an interpreter as the pipe SINK is refused", silent(out),
                    out.strip()[:160])
            _, out = call("git show HEAD | python3 .agents/scripts/check_maps.py", root)
            c.check("H3 refused even when the rule names the script path", silent(out),
                    out.strip()[:160])
            # `&&` is not a pipe: nothing is fed to the interpreter's stdin.
            _, out = call("git status --short && python3 .agents/scripts/check_maps.py", root)
            c.check("H4 the same interpreter after && IS allowed", allowed(out),
                    out.strip()[:160])
            # ⛔ `bash` and `sh` are off the list entirely, rule and all.
            _, out = call("git status --short && bash script.sh", root)
            c.check("H5 bash is refused even though a rule allows it", silent(out),
                    out.strip()[:160])

        # ── I · GIT · the subcommand decides, not the verb ───────────────────────────────────
        if c.block("I · git - a read-only subcommand, and the mutating ones the operator allows"):
            for label, cmd in [
                ("git checkout", "git status --short && git checkout main"),
                ("git add", "git status --short && git add AGENTS.md"),
                ("git commit", "git status --short && git commit -m x"),
                ("git merge", "git status --short && git merge chore/x"),
                ("git push", "git status --short && git push origin main"),
                ("git branch -d", "git branch --list | head -5 && git branch -d chore/x"),
                ("git worktree remove", "git worktree list && git worktree remove /tmp/x"),
                ("git with flags but no subcommand", "git --no-pager | head -1"),
                ("git stash (bare, which STASHES)", "git status --short && git stash"),
            ]:
                _, out = call(cmd, root)
                c.check(f"I · silent on {label}", silent(out), f"{cmd!r} -> {out.strip()[:160]}")
            for label, cmd in [
                ("git worktree list", "git worktree list | wc -l"),
                ("git branch --list", "git branch --list | head -10"),
                ("git stash list", "git stash list | head -5"),
                ("git ls-files", "git ls-files | grep -n hooks"),
            ]:
                _, out = call(cmd, root)
                c.check(f"I · allows {label}", allowed(out), f"{cmd!r} -> {out.strip()[:160]}")

        # ── N · THE THREE WIDENINGS, EACH ONE MEASURED, AND EACH ONE'S EDGE ─────────────────
        # ⛔ THESE ARE NOT CONVENIENCES, THEY ARE THE DIFFERENCE BETWEEN A HOOK THAT WORKS AND
        # ONE THAT DOES NOT. The first cut refused all three and removed 15 prompts out of 370.
        # The diagnosis over the same transcript: 201 commands carried `2>/dev/null` or `2>&1`,
        # 103 carried a QUOTED glob, and `acli` - the Jira CLI, read-only for `view`/`search` -
        # was not a verb it knew. Each widening below is paired with the edge that keeps it
        # narrow, because a carve-out with no edge is just a hole.
        if c.block("N · the /dev/null carve-out, quoted globs, `~`, and acli"):
            for label, cmd in [
                ("2>&1 names no destination", "git status 2>&1 | head -5"),
                ("2>/dev/null discards", "grep -rn SCC . 2>/dev/null | head -20"),
                (">/dev/null 2>&1 is two removals", "git diff >/dev/null 2>&1 && git status"),
                ("a QUOTED glob is text, not a glob",
                 "grep -rn SCC --include='*.md' . | head -20"),
                ("a quoted expression with spaces and >=",
                 "acli jira workitem search --jql 'project = SCC AND created >= -3d' | head -40"),
                ("acli view is read-only", "acli jira workitem view SCC-287 --json | head -40"),
                ("~ expands to a path and nothing else", "cat ~/.claude/settings.json | head -5"),
                ("$ inside SINGLE quotes is literal", "grep -n '$HOME' AGENTS.md | head -3"),
            ]:
                _, out = call(cmd, root)
                c.check(f"N · allows {label}", allowed(out), f"{cmd!r} -> {out.strip()[:160]}")
            for label, cmd in [
                # ⛔ THE STRIP REMOVES, IT NEVER REWRITES. A real redirect that survives it still
                # carries a `>` into rule 1, and rule 1 still refuses.
                ("a real redirect alongside a /dev/null one",
                 "git diff 2>/dev/null > stolen.txt"),
                ("a near-miss destination", "git diff >/dev/nullx | head -1"),
                ("an append to a real file", "git log --oneline 2>&1 >> log.txt"),
                # The glob carve-out is QUOTED-ONLY. Unquoted it still expands after this hook
                # has judged the tokens, which is flag injection past rule 4.
                ("an UNQUOTED glob", "grep -rn SCC --include=*.md . | head -20"),
                ("an unquoted brace", "cat file.{a,b} | wc -l"),
                # `$` and `\` are what the shell still ACTS on inside double quotes.
                ("$ inside DOUBLE quotes", 'grep -n "$HOME" AGENTS.md | head -3'),
                ("a backslash inside double quotes", 'grep -n "a\\|b" AGENTS.md | head -3'),
                # acli splits exactly the way git does.
                ("acli transition writes to a live board",
                 "acli jira workitem view SCC-287 | head -5 && acli jira workitem transition --yes SCC-287 Done"),
                ("acli create writes to a live board",
                 "acli jira workitem view SCC-287 | head -5 && acli jira workitem create --project SCC"),
            ]:
                _, out = call(cmd, root)
                c.check(f"N · silent on {label}", silent(out), f"{cmd!r} -> {out.strip()[:160]}")
            # ⭐ And the strip respects quotes: inside them, that text is an operand.
            _, out = call('grep -n "2>/dev/null" AGENTS.md | head -3', root)
            c.check("N · a QUOTED `2>/dev/null` is an operand, not a redirect",
                    allowed(out), out.strip()[:160])

        # ── Q · MULTI-LINE COMMANDS, `cd`, AND `echo` ───────────────────────────────────────
        # ⛔ THE `cd` RULE IS THE COMPLEMENT OF `guard-cwd-escape.py`, NOT A RELAXATION OF IT.
        # That hook flags a top-level `cd` LEAVING the workspace - the SCC-182 bug where the
        # session's cwd silently resets to the main checkout and every later relative path reads
        # the wrong tree - and passes untouched every `cd` that stays inside. This permits
        # exactly that set, so the two can never disagree about one command. A RELATIVE target is
        # refused outright: there is no cwd here to resolve it against.
        if c.block("Q · multi-line commands, `cd` inside the workspace, and `echo`"):
            # ⛔ POSIX-spelled, because this string goes INSIDE a shell command (SCC-321). The
            # Bash tool runs Git Bash on Windows, where `\` is the ESCAPE character — so a native
            # `C:\Users\me\ws` reaches the hook (and the shell) as `C:Usersmews`. The payload's
            # root stays native, because that is what Claude Code actually sends; `cd_ok` is what
            # reconciles the two spellings.
            inside = str(root).replace("\\", "/")
            for label, cmd in [
                ("a leading cd to the workspace root",
                 f"cd {inside}\ngit status --short\nls -la"),
                ("a cd to a directory inside it", f"cd {inside}/.claude && ls -la"),
                ("blank lines and indentation between lines",
                 f"cd {inside}\n\n  git status --short\n\n  wc -l AGENTS.md"),
                ("a section header echo whose argument starts with a dash",
                 'echo "--- branches ---" && git branch --list'),
                ("the shape that motivated all three",
                 f'cd {inside}\necho "=== masters ==="\ngrep -rn SCC .agents/ | head -20'),
            ]:
                _, out = call(cmd, root)
                c.check(f"Q · allows {label}", allowed(out),
                        f"{cmd!r} -> {out.strip()[:160]}")
            for label, cmd in [
                ("a cd OUT of the workspace", "cd /etc && ls -la"),
                ("a cd to the workspace's parent", f"cd {os.path.dirname(inside)} && ls -la"),
                ("a RELATIVE cd, which cannot be verified", "cd .. && ls -la"),
                ("a cd with no target", "cd && ls -la"),
                ("a cd with two targets", f"cd {inside} {inside}/.claude && ls"),
                # ⛔ A newline separates; it does not excuse. Every line is still an atom.
                ("a write on the second line", "git status --short\nrm -rf .agents"),
                ("a write on the third line",
                 f"cd {inside}\ngit status --short\ngit checkout main"),
                ("a newline inside quotes is a script, not a command",
                 'grep -n "a\nb" AGENTS.md'),
            ]:
                _, out = call(cmd, root)
                c.check(f"Q · silent on {label}", silent(out),
                        f"{cmd!r} -> {out.strip()[:160]}")

        # ── R · THE MSYS `/c/…` SPELLING, WHICH IS THE ONE THE SHELL ACTUALLY USES ──────────
        # ⛔ FOURTH INSTANCE OF THE ABSOLUTE-PATH-HAS-TWO-SPELLINGS BUG. SCC-321 taught `_is_abs`
        # the drive-lettered form (`C:/ws`) after `startswith("/")` refused every Windows `cd`;
        # `run-hook.sh` and the push gates (SCC-171/172) were the two before it. The spelling
        # missed that time is the one Git Bash — the shell the Bash tool actually runs on
        # Windows — produces for itself: `/c/Sudo_Hatter_Command`. `_is_abs` accepts it (it does
        # start with `/`), so it reaches `_canon`, which rewrites only backslashes — leaving
        # `/c/sudo_hatter_command` to be compared against a root of `c:/sudo_hatter_command`.
        # They never match, so EVERY `cd /c/<repo> && …` chain fell through to a prompt.
        # Measured over 18 transcripts: 114 calls, 7.0% of every prompt the operator answered.
        # It fails safe (a prompt, never a wrong grant), which is exactly why it survived — and
        # why the fixtures above could not see it: every one of them spells the root `C:/…`.
        if c.block("R · the MSYS `/c/...` spelling of a Windows absolute path"):
            if os.name == "nt":
                native = str(root)
                msys = f"/{native[0].lower()}{native[2:].replace(chr(92), '/')}"
                for label, cmd in [
                    ("a cd to the workspace root", f"cd {msys} && git status --short"),
                    ("a cd to a directory inside it", f"cd {msys}/.claude && ls -la"),
                    ("the multi-line shape", f"cd {msys}\ngit status --short\nls -la"),
                ]:
                    _, out = call(cmd, root)
                    c.check(f"R · allows {label}, MSYS-spelled", allowed(out),
                            f"{cmd!r} -> {out.strip()[:160]}")
            # ⛔ The REJECT half runs on BOTH machines: the rewrite must never make an MSYS path
            # OUTSIDE the workspace look inside it, and on POSIX `/c/...` is an ordinary path
            # that is outside this fixture root either way.
            for label, cmd in [
                ("an MSYS path outside the workspace", "cd /c/Windows && ls -la"),
                ("an MSYS path on another drive", "cd /d/Somewhere && ls -la"),
                ("a bare drive root", "cd /c && ls -la"),
                ("a write on the second atom, MSYS-spelled", "cd /c/Windows && rm -rf x"),
            ]:
                _, out = call(cmd, root)
                c.check(f"R · silent on {label}", silent(out),
                        f"{cmd!r} -> {out.strip()[:160]}")

        # ── L · the two legal outputs, and failing silent ────────────────────────────────────
        if c.block("L · two legal outputs, and every failure is silence"):
            probes = ["git diff | grep -n def", "git status && git checkout main",
                      "cat <<EOF", "git status --short & ls"]
            outs = [call(p, root)[1] for p in probes]
            c.check("L1 never emits `ask`", not any('"ask"' in o for o in outs), str(outs)[:200])
            c.check("L2 never emits `deny`", not any('"deny"' in o for o in outs), str(outs)[:200])
            c.check("L3 every probe exits 0",
                    all(call(p, root)[0] == 0 for p in probes))
            code, out = call("", root, raw="not json at all")
            c.check("L4 unparseable stdin is silent, exit 0", silent(out) and code == 0,
                    f"exit={code} {out.strip()[:160]}")
            code, out = call("", root, raw='{"tool_name":"Bash"}')
            c.check("L5 a payload with no command is silent, exit 0", silent(out) and code == 0,
                    f"exit={code} {out.strip()[:160]}")
            code, out = call("git diff | grep -n def", root, tool="Read")
            c.check("L6 a non-Bash tool is silent", silent(out) and code == 0,
                    f"exit={code} {out.strip()[:160]}")
            c.check("L7 no traceback ever reaches the transcript",
                    all("Traceback" not in o for o in outs), str(outs)[:200])

    # ── J · CONDITION (B) IS LOAD-BEARING · satisfies (A), matches no rule ──────────────────
    # ⛔ THE "GRANTS NOTHING NEW" CLAIM, TESTED BY DEFEATING IT. `date -u` is on the committed
    # read-only list with `-u` on its flag set - so (A) says yes. With no `Bash(date:*)` rule it
    # must still be refused, because the operator never granted `date` on its own either.
    with TempDir() as tmp:
        bare = seed(tmp, allow=["Bash(git status:*)", "Bash(head:*)"])
        if c.block("J · condition (B) - an allow-listed verb the operator never granted"):
            _, out = call("date -u | head -1", bare)
            c.check("J1 (A)-clean but no matching rule -> silent", silent(out), out.strip()[:160])
            _, out = call("git status --short | head -5", bare)
            c.check("J2 ...and the same shape WITH rules is allowed (non-vacuous)",
                    allowed(out), out.strip()[:160])
            # One atom short of covered is the whole chain refused - not the covered part run.
            _, out = call("git status --short | head -5 | wc -l", bare)
            c.check("J3 ONE uncovered atom refuses the WHOLE chain", silent(out),
                    out.strip()[:160])
        if c.block("J · adding the rule is what changes the answer"):
            withdate = seed(tmp, allow=["Bash(git status:*)", "Bash(head:*)", "Bash(date:*)"])
            _, out = call("date -u | head -1", withdate)
            c.check("J4 the identical command allows once the operator's rule exists",
                    allowed(out), out.strip()[:160])

    # ── K · CONDITION (A) IS LOAD-BEARING · matches a rule, fails the verb list ─────────────
    with TempDir() as tmp:
        wide = seed(tmp, allow=["Bash(rm:*)", "Bash(cat:*)", "Bash(chmod:*)", "Bash(curl:*)",
                                "Bash(tee:*)", "Bash(git:*)"])
        if c.block("K · condition (A) - a rule the operator wrote that (A) still refuses"):
            for label, cmd in [
                ("rm, with a rule that matches it", "cat f.txt && rm -rf .agents"),
                ("chmod, with a rule", "cat f.txt && chmod 777 AGENTS.md"),
                ("curl, with a rule", "cat f.txt | curl example.com"),
                ("tee, whose whole job is to write", "cat f.txt | tee out.txt"),
                ("git reset --hard under a blanket Bash(git:*)",
                 "cat f.txt && git reset --hard"),
                ("git clean -fd under the same blanket rule", "cat f.txt && git clean -fd"),
            ]:
                _, out = call(cmd, wide)
                c.check(f"K · silent on {label}", silent(out), f"{cmd!r} -> {out.strip()[:160]}")
            _, out = call("cat f.txt | cat -n", wide)
            c.check("K · non-vacuous: an (A)-clean chain under the SAME rules is allowed",
                    allowed(out), out.strip()[:160])

    # ── M · `deny` and `ask` rules are honoured ────────────────────────────────────────────
    with TempDir() as tmp:
        d = seed(tmp, deny=["Bash(git log:*)"], ask=["Bash(head:*)"])
        if c.block("M · a decision the operator already recorded is never talked over"):
            _, out = call("git log --oneline -5 | wc -l", d)
            c.check("M1 an atom under a `deny` rule refuses the chain", silent(out),
                    out.strip()[:160])
            _, out = call("git status --short | head -5", d)
            c.check("M2 an atom under an `ask` rule refuses the chain", silent(out),
                    out.strip()[:160])
            _, out = call("git status --short | wc -l", d)
            c.check("M3 non-vacuous: the untouched shape still allows", allowed(out),
                    out.strip()[:160])

    # ── P · `compile_rule` · a rule describing ONE command may not stretch over a chain ──────
    # ⛔ THE FAIL-OPEN THIS BLOCK EXISTS TO KEEP DEAD. The open end of `Bash(cmd:*)` was written
    # `(?:\s.*)?`, and `.*` crosses `&&`. So `Bash(git status:*)` matched the whole string
    # `git status && git checkout main`. Inside the hook it was harmless - rule 2 guarantees an
    # atom carries no separator - but the same matcher was the BEFORE half of this lane's
    # measurement, where it reported 82% of commands already auto-approved against an operator
    # who was approving nine in ten. A matcher that is only correct because of its caller is one
    # refactor from being wrong.
    if c.block("P · compile_rule - the prefix rule's open end stops at a separator"):
        sys.path.insert(0, str(SCRIPTS.parent / "hooks"))
        import importlib.util as ilu
        spec = ilu.spec_from_file_location("chain_mod", HOOK)
        chain = ilu.module_from_spec(spec)
        spec.loader.exec_module(chain)
        for label, rule, text, want in [
            ("an exact command", "cat:*", "cat", True),
            ("a command with arguments", "cat:*", "cat AGENTS.md", True),
            # ⛔ A token boundary, or `Bash(cat:*)` grants `category-tool`.
            ("a longer word with the same prefix", "cat:*", "category-tool x", False),
            ("a chain past the prefix", "git status:*", "git status && git checkout main", False),
            ("a pipe past the prefix", "git status:*", "git status | rm -rf .", False),
            ("a semicolon past the prefix", "git status:*", "git status ; rm -rf .", False),
            # A prefix ending in punctuation continues into the rest of the path, with no
            # boundary to insist on - but still not across a separator.
            ("a path prefix", "python3 .agents/scripts/:*", "python3 .agents/scripts/x.py", True),
            ("a path prefix, chained", "python3 .agents/scripts/:*",
             "python3 .agents/scripts/x.py && rm -rf .", False),
            ("a wildcard rule", "git -C * status:*", "git -C /tmp/lane status --short", True),
            ("a wildcard that would have to cross a separator", "git -C * status:*",
             "git -C /tmp && rm status", False),
            ("an exact rule with no open end", "git version", "git version", True),
            ("an exact rule is not a prefix", "git version", "git version --build-options", False),
        ]:
            got = bool(chain.compile_rule(rule).match(text))
            c.check(f"P · {label}", got == want, f"Bash({rule}) vs {text!r}: got {got}")

    # ── WIRING · reads the REAL repo files, not a fixture ───────────────────────────────────
    if c.block("WIRING · the master and the settings entry agree on the single source"):
        master = ROOT / ".agents/hooks/allow-readonly-chain.py"
        c.check("WIRING · the master exists", master.is_file(), str(master))
        settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        groups = [g for g in settings["hooks"]["PreToolUse"] if g.get("matcher") == "Bash"]
        c.check("WIRING · there is exactly one PreToolUse Bash matcher", len(groups) == 1,
                f"found {len(groups)}")
        cmds = [h["command"] for h in groups[0]["hooks"]] if groups else []
        mine = [x for x in cmds if "allow-readonly-chain.py" in x]
        c.check("WIRING · the hook is wired into it", len(mine) == 1, str(cmds))
        c.check("WIRING · it points directly to .agents/hooks/allow-readonly-chain.py",
                any(".agents/hooks/allow-readonly-chain.py" in x for x in mine), str(mine))
        # ⛔ The interpreter seam. `.claude/settings.json` is shared across a Mac with no bare
        # `python` and a PC with no `python3`; naming either directly is the SCC-77 exit-127 bug,
        # which is silent. `run-hook.sh` probes.
        c.check("WIRING · it is dispatched through run-hook.sh, never a named interpreter",
                all("run-hook.sh" in x for x in mine), str(mine))
        # ⛔ The stray-copy check: wired into SessionStart it is inert, and every symptom of that
        # is identical to a hook that works.
        ss = [h["command"] for g in settings["hooks"].get("SessionStart", []) for h in g["hooks"]]
        c.check("WIRING · it is NOT also wired into SessionStart (inert there, and silent)",
                not any("allow-readonly-chain.py" in x for x in ss), str(ss))

    # ── E2E · through the seam Claude Code actually uses ────────────────────────────────────
    if c.block("E2E · the hook answers correctly through run-hook.sh"):
        # ⛔ Never `["sh", ...]` (SCC-321): Windows has no `sh` on PATH, and the resulting
        # FileNotFoundError RAISES — killing every remaining case in this file rather than
        # failing one. A NAMED failure, never a silent skip: any machine with git installed
        # has a POSIX shell, so "none found" is a real finding about the machine.
        sh = posix_sh()
        if sh is None:
            c.check("E2E · a POSIX shell is available to dispatch run-hook.sh", False,
                    "no usable sh found — WSL's bash does not count, it cannot read a C:\\ path")
        else:
            with TempDir() as tmp:
                # ⛔ The fixture rules must live where `CLAUDE_PROJECT_DIR` points, because
                # that is what the hook reads - but run-hook.sh resolves the SCRIPT relative
                # to the same variable. So the script is dispatched by absolute path here and
                # the variable is left pointing at the fixture, which is the only way both
                # halves stay honest.
                root = seed(tmp)
                payload = json.dumps({"tool_name": "Bash",
                                      "tool_input": {"command": "git diff | grep -n def"},
                                      "session_id": "fixture"})
                p = subprocess.run([sh, str(SCRIPTS.parent / "hooks" / "run-hook.sh"),
                                    str(HOOK)],
                                   input=payload, capture_output=True, text=True,
                                   cwd=str(ROOT), errors="replace",
                                   env={**os.environ, "CLAUDE_PROJECT_DIR": str(root),
                                        "HOME": str(root), "USERPROFILE": str(root)})
                c.check("E2E · run-hook.sh dispatches it and it allows", allowed(p.stdout),
                        (p.stdout + p.stderr).strip()[:200])
                c.check("E2E · exit 0 through the seam", p.returncode == 0,
                        f"exit={p.returncode}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
