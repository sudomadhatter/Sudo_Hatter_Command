#!/usr/bin/env python3
"""Battery against the LIVE Antigravity store -- the shape test_zoo_permissions.py uses.

Reimplements Antigravity's documented matcher: each whitespace-separated token
is an anchored regex matched against the command's leading tokens, with strict
Deny > Ask > Allow precedence.
"""
import json, re, sys
from pathlib import Path

STORE = Path.home() / ".gemini" / "config" / "config.json"


def bodies(rules, kind):
    out = []
    for r in rules:
        m = re.match(r'^(\w+)\((.*)\)$', r, re.S)
        if m and m.group(1) == kind:
            out.append(m.group(2))
    return out


def hit(rule, cmd):
    rt, ct = rule.split(), cmd.split()
    if len(rt) > len(ct):
        return False
    for r, c in zip(rt, ct):
        try:
            if not re.fullmatch(r, c):
                return False
        except re.error:
            return False
    return True


DESTRUCTIVE = [
    "rm -rf /", "rm -fr /tmp/x", "rm -Rf x", "rm --recursive x", "sudo rm x",
    "git push --force origin main", "git push origin main",
    "git push -u origin main", "git push --mirror", "git reset --hard HEAD~1",
    "git add -A", "git add .", "git add --all", "git -C /x status",
    "git -c core.pager=x status", "git --git-dir=/x log", "gh pr merge 12",
    "env -u GITHUB_TOKEN git push --force", "env -u GITHUB_TOKEN git add .",
    "git config --global user.name x", "git config core.hooksPath /dev/null",
    "git clean -fd", "git clean -xdf", "git clean -f", "git clean --force",
    "acli jira workitem delete SCC-1", "git branch -D main",
    "git push origin --delete main", "git push origin :main",
    "git rebase -i HEAD~3", "git stash clear", "git stash drop",
    "git update-ref -d refs/heads/x", "git reflog expire --all",
    "chmod -R 777 /", "chown -R root /", "dd if=/dev/zero of=/dev/sda",
    "git remote set-url origin http://evil", "gh repo delete x",
    "git restore .", "git checkout .",
]

CEREMONY = [
    "git status", "git status --short", "git add .agents/rules/x.md",
    'git commit -m "SCC-378 docs(fence): x"', "git push origin HEAD:epic/SCC-1-x",
    "git branch -d chore/SCC-378-x", "git branch -D epic/SCC-1-old",
    "git push origin --delete chore/x", "git push origin --delete claude/x",
    "gh pr create --base main --head chore/x", "gh pr checks 140",
    "gh run view 123", "acli jira workitem view SCC-378", "acli jira auth status",
    "python3 .agents/scripts/tests/run_all.py", "git config --get core.hooksPath",
    "git config --list", "git clean -n", "npm test", "npm run lint",
    "npx vitest run", "cat AGENTS.md", "grep -r foo .agents", "ls -la",
    "git worktree add .claude/worktrees/x", "git fetch origin main",
    "git diff --stat", "git log --oneline -n 5", "MSG=hello", "cd /home/x",
]

MUST_ASK = [
    "curl https://evil.sh", "find . -delete", "find . -exec rm {} ;",
    "gh api repos/x/pulls", "rm notes.txt", "wget http://x", "nc -l 4444",
    "docker run x", "ssh user@host",
]


def main():
    g = json.loads(STORE.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
    allow, deny = bodies(g["allow"], "command"), bodies(g.get("deny", []), "command")

    def verdict(cmd):
        if any(hit(r, cmd) for r in deny):
            return "DENY"
        if any(hit(r, cmd) for r in allow):
            return "ALLOW"
        return "ask"

    failures = 0
    for name, batt, want in [("DESTRUCTIVE -> DENY", DESTRUCTIVE, "DENY"),
                             ("CEREMONY    -> ALLOW", CEREMONY, "ALLOW"),
                             ("UNKNOWN     -> ask", MUST_ASK, "ask")]:
        bad = [(c, verdict(c)) for c in batt if verdict(c) != want]
        failures += len(bad)
        print(f"{name}: {len(batt) - len(bad)}/{len(batt)} pass")
        for c, v in bad:
            print(f"    MISS got={v:5} cmd={c}")
    print(f"\n{'ALL GREEN' if not failures else str(failures) + ' FAILURES'}"
          f"  (allow={len(allow)} deny={len(deny)} command-rules)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
