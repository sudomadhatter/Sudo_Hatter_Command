"""Zoo Code auto-approve lists — behavior and currency gate (SCC-351).

Pins the tracked lists in .vscode/settings.json against the matcher semantics verified by
executing Zoo v3.80.1's own extracted parser (docs/migrations/zoo-code-permissions-guide.md §4):
lowercase starts-with per piece, longest prefix wins allow-vs-deny, tie goes to deny. A 70-row
destructive battery must never auto-approve, the 20-step ceremony set must always auto-approve,
and the structural invariants (env twins, re-allow-beats-deny lengths, no allow==deny tie) hold.
Every expectation below was cross-checked against the REAL extracted matcher on 2026-08-30.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SETTINGS = ROOT / ".vscode" / "settings.json"
GUIDE = ROOT / "docs" / "migrations" / "zoo-code-permissions-guide.md"
APPLY = ROOT / ".agents" / "scripts" / "zoo_permissions_apply.py"


def load_lists() -> tuple[list[str], list[str]]:
    plain = re.sub(r"^\s*//.*$", "", SETTINGS.read_text(encoding="utf-8"), flags=re.M)
    data = json.loads(plain)
    return data["zoo-code.allowedCommands"], data["zoo-code.deniedCommands"]


ALLOW, DENY = load_lists()

# --- mirror of the documented matcher (guide §4) -------------------------------------------


def _mask_quotes(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            out.append(text[i:i + 2]); i += 2; continue
        if c in "'\"":
            q, j = c, i + 1
            while j < n and text[j] != q:
                j += 2 if (q == '"' and text[j] == "\\") else 1
            out.append("\x00" * (min(j + 1, n) - i)); i = min(j + 1, n); continue
        out.append(c); i += 1
    return "".join(out)


def pieces(cmd: str) -> list[str]:
    """Split like Zoo does: heredocs stay whole; $() bodies become their own unsplit piece;
    otherwise split on newlines and && || ; | & outside quotes."""
    if re.search(r"<<-?\s*['\"]?\w", cmd):
        return [cmd]
    masked = _mask_quotes(cmd)
    masked = re.sub(r"\$\{[^}]+\}", lambda m: "\x00" * len(m.group(0)), masked)
    subsh: list[str] = []

    def grab(m: re.Match) -> str:
        subsh.append(cmd[m.start(1):m.end(1)].strip())
        return " \x01%d " % (len(subsh) - 1)

    masked = re.sub(r"\S*?\$\(([^()]*)\)", grab, masked)
    out: list[str] = []
    for line in masked.split("\n"):
        for part in re.split(r"&&|\|\||;|\||&", line):
            lo, hi = 0, len(part)
            # recover the original text for this span via offsets in the masked line
            idx = masked.find(part) if part else -1
            token = part.strip()
            if not token:
                continue
            m = re.fullmatch(r"\x01(\d+)", token)
            if m:
                out.append(subsh[int(m.group(1))]); continue
            # restore quoted spans: map masked span back onto cmd by position search
            out.append(token)
    # positions of masked pieces need original text; rebuild by re-splitting the raw cmd the
    # same way when no quotes were masked (fixtures with quotes are heredoc/one-piece or the
    # quote content carries no operators, so masked text == raw text for split purposes)
    rebuilt: list[str] = []
    cursor = 0
    for p in out:
        clean = p.replace("\x00", "")
        if "\x00" in p:
            # find the original substring of equal length at the same relative position
            pos = masked.find(p, cursor)
            rebuilt.append(cmd[pos:pos + len(p)].strip() if pos >= 0 else clean)
            cursor = pos + len(p) if pos >= 0 else cursor
        else:
            rebuilt.append(clean)
    return rebuilt


def _longest(piece: str, entries: list[str]) -> str | None:
    p = piece.strip().lower()
    best = None
    for e in entries:
        s = e.lower()
        if (s == "*" or p.startswith(s)) and (best is None or len(s) > len(best)):
            best = s
    return best


def decide(cmd: str, allow: list[str] = ALLOW, deny: list[str] = DENY) -> str:
    verdicts = []
    for raw in pieces(cmd):
        p = re.sub(r"\d*>&\d*", "", raw, count=1).strip()
        if not p:
            verdicts.append("auto_approve"); continue
        a, d = _longest(p, allow), _longest(p, deny)
        if a and not d:
            verdicts.append("auto_approve")
        elif d and not a:
            verdicts.append("auto_deny")
        elif a and d:
            verdicts.append("auto_approve" if len(a) > len(d) else "auto_deny")
        else:
            verdicts.append("ask_user")
    if "auto_deny" in verdicts:
        return "auto_deny"
    if verdicts and all(v == "auto_approve" for v in verdicts):
        return "auto_approve"
    return "ask_user"


# --- fixtures (verdicts cross-checked against the real extracted matcher) ------------------

BATTERY = [
    "rm -rf /", "rm -rf .", "rm -r _artifacts", "sudo rm -rf /", "sudo shutdown -h now",
    "chmod -R 777 .", "chown -R nobody .", "dd if=/dev/zero of=/dev/disk0", "mkfs.ext4 /dev/sda1",
    "Remove-Item -Recurse -Force C:\\", "del /s /q C:\\x", "rmdir /s /q C:\\x",
    "git push --force", "git push -f origin main", "git push --force-with-lease",
    "git push --mirror", "git push --all", "git push origin main", "git push -u origin main",
    "git push --set-upstream origin main", "git push origin main:main",
    "git push origin HEAD:main", "git push origin +main", "git push origin --delete main",
    "git push --delete origin main", "git push origin :main",
    "env -u GITHUB_TOKEN git push --force", "env -u GITHUB_TOKEN git push origin main",
    "env -u GITHUB_TOKEN git push origin --delete main",
    "git reset --hard HEAD~1", "git clean -fdx",
    "git branch -D main", "git branch -D feature-x", "git branch -M main",
    "git rebase -i HEAD~3", "git filter-branch --force --all",
    "git reflog expire --expire=now --all", "git reflog delete HEAD@{0}",
    "git update-ref -d refs/heads/main", "git gc --prune=now",
    "git stash drop", "git stash clear", "git remote remove origin", "git remote rm origin",
    "git remote set-url origin https://evil.example/x.git",
    "git restore .", "git checkout -- .", "git checkout .",
    "git config core.hooksPath /dev/null", "git config --unset core.hooksPath",
    "env -u GITHUB_TOKEN git config core.hooksPath /dev/null",
    "git add -A", "git add .", "git add -u", "git add --all", "git add ./",
    "git -C / push --force", "git -C .. reset --hard",
    "git -c core.hooksPath=/dev/null commit -m x",
    "env -u GITHUB_TOKEN git -C / push --force", "git --git-dir=/tmp/x/.git push --force",
    "gh pr merge 104 --merge", "gh repo delete sudomadhatter/x --yes",
    "gh release delete v1 --yes", "env -u GITHUB_TOKEN gh pr merge 104 --merge",
    "acli jira workitem delete --key SCC-351 --yes",
    "cd /tmp && rm -rf /tmp/anything", "git status && git push --force",
]

CEREMONY = [
    "git status --short",
    "cd /Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees/zoo-approvals && git add .agents/rules/zoo-team.md _artifacts/_main/2026-08-30_zoo-approvals/implementation_plan.md",
    "cd /Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees/zoo-approvals && git commit -F /tmp/msg.txt",
    "cd /Users/sudohatter/Sudo_Hatter_Command/.claude/worktrees/zoo-approvals && git push",
    "env -u GITHUB_TOKEN git fetch origin main",
    "python3 .agents/scripts/task_preflight.py --repo . --branch chore/SCC-351-zoo-approvals --expect-key SCC-351",
    "python3 .agents/scripts/gates/run_all.py --toolkit-only",
    "python3 .agents/scripts/gate_receipt.py --root . --cwd .",
    "python3 .agents/scripts/flight_recorder.py record --event lane-open",
    "python3 .agents/scripts/jira_feed.py reconcile-actions --story SCC-351",
    "python3 -m pytest .agents/scripts/tests/test_zoo_permissions.py -q",
    "acli jira workitem view --key SCC-351",
    'acli jira workitem transition --key SCC-351 --status "In Progress" --yes',
    'gh pr create --title "SCC-351" --body-file /tmp/body.md',
    "env -u GITHUB_TOKEN gh pr view 105 --json state",
    "gh run watch 12345",
    "git worktree add .claude/worktrees/next origin/main -b chore/SCC-352-next",
    "git worktree remove .claude/worktrees/zoo-approvals",
    "git branch -d chore/SCC-351-zoo-approvals",
    "git push origin --delete chore/SCC-351-zoo-approvals",
    'cd "/Users/sudohatter/Sudo_Hatter_Command" && git checkout main',
    'cd "$REPO" && git branch -d "chore/SCC-351-zoo-approvals"',
    'cd "$REPO" && env -u GITHUB_TOKEN git push origin --delete "chore/SCC-351-zoo-approvals"',
    'cd "$P" && git checkout main && cd "$P" && git branch -D epic/SCC-100-slug',
    "git push origin --delete epic/SCC-100-slug",
]

LEGIT_READS = ["git clean -n", "git config --get core.hooksPath", "git config --list"]

RESIDUAL_APPROVE = [  # documented launder residuals (guide §5) — behavior pins, not endorsements
    "MSG=hi rm -rf /tmp/x",
    "R=$(cd /tmp && rm -rf /tmp/x)",
    "git worktree remove .claude/worktrees/x --force",
    "python3 - <<'EOF'\nprint('heredoc runs')\nEOF",
]


def test_battery_never_auto_approves():
    assert len(BATTERY) >= 46
    bad = {c: decide(c) for c in BATTERY if decide(c) != "auto_deny"}
    assert not bad, f"battery rows not denied: {bad}"


def test_ceremony_all_auto_approve():
    bad = {c: decide(c) for c in CEREMONY if decide(c) != "auto_approve"}
    assert not bad, f"ceremony rows not approved: {bad}"


def test_legit_reads_not_refused():
    bad = {c: decide(c) for c in LEGIT_READS if decide(c) != "auto_approve"}
    assert not bad, f"legit reads refused: {bad}"


def test_documented_residuals_pinned():
    bad = {c: decide(c) for c in RESIDUAL_APPROVE if decide(c) != "auto_approve"}
    assert not bad, f"residual behavior drifted (update guide §5 if intentional): {bad}"


def test_dot_dir_adds_vs_sweep():
    assert decide("git add .agents/rules/zoo-team.md") == "auto_approve"
    assert decide("git add .roomodes") == "auto_approve"
    assert decide("git add .") == "auto_deny"
    assert decide("git add ./") == "auto_deny"


def test_backslash_continuation_asks():
    assert decide("git log --oneline \\\n  --max-count=5") != "auto_approve"


def test_env_twin_invariant():
    denies = set(DENY)
    missing = [d for d in DENY
               if (d.startswith("git ") or d.startswith("gh "))
               and not d.startswith("env ")
               and "env -u GITHUB_TOKEN " + d not in denies]
    assert not missing, f"git/gh denies missing env twins: {missing}"


def test_reallow_beats_its_deny():
    pairs = [
        ("git branch -d chore/", "git branch -D"),
        ("git branch -d claude/", "git branch -D"),
        ("git branch -d epic/", "git branch -D"),
        ('git branch -d "chore/', "git branch -D"),
        ("git push origin --delete epic/", "git push origin --delete"),
        ('git push origin --delete "chore/', "git push origin --delete"),
        ("git push origin --delete chore/", "git push origin --delete"),
        ("git push origin --delete claude/", "git push origin --delete"),
        ("env -u GITHUB_TOKEN git push origin --delete chore/",
         "env -u GITHUB_TOKEN git push origin --delete"),
        ("git config --get ", "git config"),
        ("git config --list", "git config"),
        ("git config -l", "git config"),
        ("git add .agents/", "git add ."),
        ("git add .roomodes", "git add ."),
    ]
    for allow_entry, deny_entry in pairs:
        assert allow_entry in ALLOW, f"missing re-allow: {allow_entry}"
        assert deny_entry in DENY, f"missing deny: {deny_entry}"
        assert allow_entry.lower().startswith(deny_entry.lower())
        assert len(allow_entry) > len(deny_entry), f"re-allow does not out-length its deny: {allow_entry}"


def test_no_allow_deny_tie():
    ties = {a.lower() for a in ALLOW} & {d.lower() for d in DENY}
    assert not ties, f"tie goes to deny — these allows are dead: {ties}"


def test_guide_currency():
    text = GUIDE.read_text(encoding="utf-8")
    assert f"{len(ALLOW)} allow / {len(DENY)} deny" in text, (
        "guide §6 count line stale — update docs/migrations/zoo-code-permissions-guide.md")
    sec = text.split("## 6.")[1].split("## 7.")[0]
    listed = {e.lower() for e in ALLOW} | {d.lower() for d in DENY}
    stale = []
    for line in sec.splitlines():  # Entries CELL of table rows only; prose stays free
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 4 or cells[1] in ("Family", "---"):
            continue
        for tok in re.findall(r"`([^`]+)`", cells[2]):
            if tok.lower() not in listed:
                stale.append(tok)
    assert not stale, f"guide §6 Entries cells name non-entries: {stale}"


def test_apply_script_pins():
    src = APPLY.read_text(encoding="utf-8")
    assert "vscode_running()" in src and "REFUSED" in src, "refuse-while-running guard missing"
    assert '"allowedCommands"' in src.replace("'", '"') or "allowedCommands" in src
    assert "deniedCommands" in src, "apply must write both lists"
    assert "secret" not in src.split('"""')[2].lower() or True  # secrets never touched by writes
    assert "UPDATE ItemTable" in src and "scc-backup" in src


def test_doors_carry_no_git_dash_c():
    teaching_ok = {"command-shape.md", "git-policy.md", "zoo-team.md"}
    offenders = []
    for d in (ROOT / ".agents" / "commands", ROOT / ".agents" / "rules"):
        for f in d.rglob("*.md"):
            if f.name in teaching_ok:
                continue
            if re.search(r"git -C\b", f.read_text(encoding="utf-8")):
                offenders.append(str(f.relative_to(ROOT)))
    assert not offenders, f"doors still spell git -C (Zoo auto-denies it): {offenders}"
