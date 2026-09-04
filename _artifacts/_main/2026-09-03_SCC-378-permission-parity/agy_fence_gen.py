#!/usr/bin/env python3
"""Translate the Zoo canonical fence into Antigravity's permission grammar.

Antigravity matches each whitespace-separated token as an ANCHORED regex
(^(?:tok)$), leading-token-prefix style, with strict Deny > Ask > Allow
precedence. Three consequences drive every choice below:

  1. Deny wins outright -- Zoo's "longer allow beats the deny" trick does NOT
     port. Denies must be surgical, naming the dangerous TARGET via alternation
     instead of relying on prefix length.
  2. Regex metacharacters must be escaped. Unescaped `git add .` means
     `git add <any single char>`, which is not what anyone intends.
  3. Rules match the leading tokens only, so `env -u GITHUB_TOKEN git push ...`
     is NOT caught by a `git push ...` deny. Every deny needs its env twin,
     exactly as in Zoo.

Emits command() for execution plus an unsandboxed() twin per allow family, so
the fence holds whether or not --sandbox is ever used.
"""
import json

# ---------------------------------------------------------------- ALLOW
# Broad working families. Written WITHOUT absolute paths so one list serves
# the Mac and the PC.
ALLOW = [
    # navigation + the read-only / fs helper set (Claude + Zoo parity)
    "cd", "ls", "pwd", "true", "date", "echo", "printf",
    "cat", "head", "tail", "sort", "uniq", "wc", "grep", "rg", "sed", "awk",
    "cut", "tr", "diff", "cmp", "basename", "dirname", "readlink", "file",
    "stat", "du", "which", "jq", "touch", "mktemp", "sleep", "ps",
    "command -v", "test", "cp", "mkdir", "ln -s",

    # git, broad -- the damage spellings are denied below and Deny outranks this
    "git", "env -u GITHUB_TOKEN git",

    # GitHub CLI: PRs and run inspection. `gh api` deliberately absent.
    "gh pr", "gh run", "env -u GITHUB_TOKEN gh pr", "env -u GITHUB_TOKEN gh run",

    # interpreters + toolchain
    "python3", "node", "npm run", "npm ci", "npm test", "npx vitest", "java -version",
    r"backend/\.venv/bin/.*", r"\.venv/bin/python -m pytest", r"\.venv/bin/ruff check",
    r"firebase/tests/node_modules/\.bin/firebase emulators:exec",

    # PowerShell, scoped to the repo's own generators (-Command NOT allowed)
    r"pwsh -NoProfile -File \.agents/scripts/.*",

    # Jira board work inside ceremonies. Widened from `acli jira workitem` to
    # `acli jira` so auth/board/project reads stop asking; the one destructive
    # verb (workitem delete) is denied below and Deny outranks this.
    "acli jira",

    # the standalone VAR= assignments the doors print, as ONE rule instead of
    # Zoo's 35. Carries the same documented env-prefix residual Zoo has.
    r"[A-Z_]+=.*",
]

# ---------------------------------------------------------------- DENY
# Every row names real damage. Because Deny is absolute here, anything with a
# legitimate counterpart is written to name the TARGET, not the verb.
DENY = [
    # filesystem. Flag CLUSTERS, not single flags: tokens are anchored, so a
    # literal `-f` never matches the combined `-fd` a real command actually
    # types. Caught by the destructive battery, not by reading.
    r"rm -[a-zA-Z]*[rR][a-zA-Z]*", "rm --recursive",
    "sudo", r"chmod -[a-zA-Z]*R[a-zA-Z]* 777", r"chown -[a-zA-Z]*R[a-zA-Z]*",
    r"dd if=.*", "mkfs",

    # outward git -- main is never an agent's, history rewrites never auto-run
    "git push --force", "git push -f", "git push --force-with-lease",
    "git push --mirror", "git push --all",
    "git push origin main", "git push -u origin main",
    "git push --set-upstream origin main",
    r"git push origin main:.*", r'git push origin "main.*',
    r"git push origin \+.*",
    # surgical: deleting a LANE branch stays legal, deleting main never is
    "git push origin --delete (main|master)",
    "git push origin :(main|master)",

    # work destruction
    "git reset --hard",
    # same cluster problem: -fd / -xdf are single tokens. The dry run `git
    # clean -n` stays approvable because it carries none of f/d/x.
    r"git clean -[a-zA-Z]*[fdx][a-zA-Z]*", "git clean --force",
    "git rebase", "git filter-branch",
    "git reflog expire", "git reflog delete", "git update-ref",
    "git gc --prune", "git stash drop", "git stash clear",
    r"git restore \.", r"git checkout \.", "git checkout --",
    # surgical: -D on a protected branch. Lane/epic force-deletes still run,
    # and unlike Zoo the regex is case-sensitive so -d is untouched.
    "git branch -D (main|master|develop)",
    "git branch -M",

    # reroute / disarm -- a config WRITE can disarm the hooks; reads stay legal
    "git remote remove", "git remote rm", "git remote rename",
    "git remote set-url",
    "git config --global", "git config --system", r"git config core\.hooksPath",

    # sweeps (the git-policy ban) -- dots escaped so .agents/ staging still works
    "git add -A", r"git add \.", "git add -u", "git add --all",

    # launder shapes: they would bypass every verb deny above. Trailing .*
    # because the attached spellings (`--git-dir=/x`, `-C/x`) are ONE token and
    # an anchored bare flag misses them -- the battery's second catch.
    r"git -C.*", r"git --git-dir.*", "git -c",

    # outward tools -- merges are the operator's click, deletions his words
    "gh pr merge", "gh repo delete", "gh release delete",
    "acli jira workitem delete",
]

ENV = "env -u GITHUB_TOKEN "


def build():
    allow, deny = [], []
    for fam in ALLOW:
        allow.append(f"command({fam})")
        allow.append(f"unsandboxed({fam})")
    for row in DENY:
        deny.append(f"command({row})")
        deny.append(f"unsandboxed({row})")
        # env twin: the broad `env -u GITHUB_TOKEN git` allow would else bypass it
        if row.startswith(("git ", "gh ")):
            deny.append(f"command({ENV}{row})")
            deny.append(f"unsandboxed({ENV}{row})")
    return allow, deny


if __name__ == "__main__":
    a, d = build()
    out = {"allow": a, "deny": d}
    print(json.dumps(out, indent=2))
    import sys
    print(f"\n# allow rules: {len(a)}  ({len(ALLOW)} families x2)", file=sys.stderr)
    print(f"# deny rules:  {len(d)}  ({len(DENY)} spellings, env twins on git/gh)", file=sys.stderr)
