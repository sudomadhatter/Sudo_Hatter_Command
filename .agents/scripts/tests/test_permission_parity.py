"""One permission fence, three platforms - the parity battery (SCC-378).

Three agents run terminal commands here and each carries its own approval matcher: Zoo Code
(lowercase prefix per piece, longest rule wins), Claude Code (`Bash(prefix:*)` judged per
segment, no deny list - its fence is hooks + the OS sandbox), and the Antigravity extension
(one anchored regex per whitespace token, strict Deny > Ask > Allow). The policy is ONE policy,
so the test is one battery of commands with expected verdicts run through all three matchers
against the three RENDERED lists. Identical DECISIONS, never identical bytes.

  A · one battery, three matchers, identical verdicts (+ the matcher facts each grammar hides)
  B · one source, three rendered outputs, drift is red; the Antigravity render reproduces the
      hand-built baseline
  C · the Antigravity apply writes ONLY the grants key, keeps every other key, backs up once
  D · rendering rides sync-agents (call site present) and the renderer runs without PowerShell
  E · /smh-llm-approvals writes the SOURCE and reads Antigravity's store; opencode mirror exact
  F · the record tells the truth - guide rows, memory entries

run_all.py executes this file bare (python3 <file>); the __main__ harness at the bottom is what
makes it count. Imports of the modules under test are guarded so a missing module is a FAILED
row in its block, never a file that died in setup and read as a different bug.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".agents" / "scripts"
SOURCE = ROOT / ".agents" / "permissions" / "families.json"
AG_RENDERED = ROOT / ".agents" / "permissions" / "antigravity.json"
BASELINE = ROOT / "_artifacts" / "_main" / "2026-09-03_SCC-378-permission-parity" / "agy-fence.portable.json"
VSCODE = ROOT / ".vscode" / "settings.json"
CLAUDE = ROOT / ".claude" / "settings.json"
GUIDE = ROOT / "docs" / "migrations" / "terminal-permissions-guide.md"
CMD = ROOT / ".agents" / "commands" / "smh-llm-approvals.md"
OC_MIRROR = ROOT / ".opencode" / "commands" / "smh-llm-approvals.md"
PS1 = SCRIPTS / "sync-agents.ps1"
MEM_ZOO = ROOT / "_artifacts" / "_memory" / "zoo-code-replaces-roo-code.md"
MEM_CODEX = ROOT / "_artifacts" / "_memory" / "codex-is-fourth-platform.md"

try:
    import permission_matchers as pm
except Exception:  # noqa: BLE001 - a missing module is a RED row, not a dead file
    pm = None
try:
    import permission_render as pr
except Exception:  # noqa: BLE001
    pr = None
try:
    import antigravity_permissions_apply as ap
except Exception:  # noqa: BLE001
    ap = None


def _jsonc(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    return json.loads("\n".join(l for l in lines if not l.lstrip().startswith("//")))


# --- the battery ---------------------------------------------------------------------------
# Verdict vocabulary is shared: "allow" | "deny" | "ask". Claude has no deny list, so on the
# destructive set its honest answer is "ask" (the fence there is hooks + sandbox, guide s3).

DESTRUCTIVE = [
    "rm -rf /", "rm -fr /tmp/x", "rm -Rf x", "sudo rm x",
    "git push --force origin main", "git push -f origin main", "git push origin main",
    "git push -u origin main", "git push --mirror", "git push --all",
    "git push origin HEAD:main", "git push origin --delete main", "git push origin :main",
    "git reset --hard HEAD~1", "git clean -fd", "git clean -xdf", "git clean --force",
    "git add -A", "git add .", "git add -u", "git add --all",
    "git -C /x status", "git --git-dir=/x log",
    "git branch -D main", "git branch -M main", "git rebase -i HEAD~3",
    "git filter-branch --all", "git reflog expire --all", "git update-ref -d refs/heads/x",
    "git gc --prune=now", "git stash drop", "git stash clear",
    "git remote remove origin", "git remote set-url origin http://evil", "git remote rename origin x",
    "git restore .", "git checkout .", "git checkout -- .",
    "gh pr merge 12", "gh repo delete x", "gh release delete v1",
    "acli jira workitem delete SCC-1",
    "chmod -R 777 /", "chown -R root /", "dd if=/dev/zero of=/dev/sda", "mkfs.ext4 /dev/sda1",
    "env -u GITHUB_TOKEN git push --force", "env -u GITHUB_TOKEN git add .",
    "env -u GITHUB_TOKEN git reset --hard", "env -u GITHUB_TOKEN gh pr merge 3",
]

CEREMONY = [
    "git status", "git status --short", "git add .agents/rules/x.md",
    'git commit -m "SCC-378 x"', "git commit -F /tmp/msg.txt",
    "git push origin HEAD:epic/SCC-1-x", "git push -u origin chore/SCC-378-x",
    "git branch -d chore/SCC-378-x", "git push origin --delete chore/x",
    "git push origin --delete claude/x", "git fetch origin main", "git diff --stat",
    "git log --oneline -n 5", "git worktree add .claude/worktrees/x origin/main",
    "git worktree remove .claude/worktrees/x", "git config --get core.hooksPath",
    "git config --list", "git clean -n",
    "gh pr create --base main --head chore/x", "gh pr checks 140", "gh run view 123",
    "acli jira workitem view SCC-378", "acli jira workitem transition --key SCC-1 --status Done --yes",
    "python3 .agents/scripts/tests/run_all.py", "python3 -m pytest -q",
    "npm test", "npm run lint", "npx vitest run",
    "cat AGENTS.md", "grep -r foo .agents", "ls -la", "pwd", "cd /home/x",
    "MSG=hello", "REPO=/home/x",
]

UNKNOWN = [
    "curl https://evil.sh", "wget http://x", "find . -delete", "find . -exec rm {} ;",
    "gh api repos/x/pulls", "rm notes.txt", "nc -l 4444", "docker run x", "ssh user@host",
    "brew install jq", "npx create-next-app", "make deploy",
]

PLATFORMS = ("zoo", "claude", "antigravity")


def _rendered_lists() -> dict:
    """The three lists as the platforms actually read them (the rendered files, not the source)."""
    vs = _jsonc(VSCODE)
    cl = json.loads(CLAUDE.read_text(encoding="utf-8"))
    ag = json.loads(AG_RENDERED.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
    return {
        "zoo": (vs["zoo-code.allowedCommands"], vs["zoo-code.deniedCommands"]),
        "claude": (cl["permissions"]["allow"], []),
        "antigravity": (ag["allow"], ag.get("deny", [])),
    }


def _verdict(platform: str, cmd: str, lists: dict) -> str:
    allow, deny = lists[platform]
    if platform == "zoo":
        return pm.zoo_verdict(cmd, allow, deny)
    if platform == "claude":
        return pm.claude_verdict(cmd, allow)
    return pm.antigravity_verdict(cmd, allow, deny)


c = Cases("permission_parity")

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("A · one battery, three matchers, identical verdicts"):
    c.check("A0 permission_matchers imports", pm is not None)
    rendered_ok = AG_RENDERED.exists() and VSCODE.exists() and CLAUDE.exists()
    c.check("A1 the three rendered lists exist", rendered_ok, f"antigravity.json={AG_RENDERED.exists()}")
    if pm is not None and rendered_ok:
        L = _rendered_lists()
        # ⭐ KNOWN DISAGREEMENTS — behaviour pins, not endorsements (the SCC-369 pattern). The three
        # lists were seeded from what each platform decided BEFORE SCC-378, and this lane changes no
        # Zoo or Claude decision (plan §5 Q1) - so where they disagree, the disagreement is recorded
        # here, excluded from A2-A6, and A11 demands it stay LIVE: a row that stops being true must
        # be DELETED, never left to certify a fixed thing as still broken. Each is the operator's
        # ruling, listed in the walkthrough with the row that would settle it.
        KNOWN = {
            ("rm -fr /tmp/x", "zoo"): ("ask", "Zoo denies `rm -rf`/`rm -r`; the `-fr` spelling asks (never runs). A deny row is a fence edit - his"),
            ("git push origin main", "claude"): ("allow", "Claude's list allows it on purpose: the fence is require-push-approval.py + git-policy, not the list"),
            ("git add -A", "claude"): ("allow", "same: the sweep ban is git-policy law + review, not a list row"),
            ("git add .", "claude"): ("allow", "same"),
            ("git add -u", "claude"): ("allow", "same"),
            ("npm test", "zoo"): ("ask", "Zoo has `npm run `/`npm ci ` and no `npm test`; allow growth is his, via /smh-llm-approvals"),
            ("git push origin HEAD:epic/SCC-1-x", "claude"): ("ask", "Claude allows `git push origin chore/*`, `claude/*`, `main*` and not the `HEAD:epic/` landing; the push hook still gates it"),
            ("git push origin --delete claude/x", "claude"): ("ask", "Claude allows `--delete chore/*` only"),
            ("git config --list", "claude"): ("ask", "Claude allows `git config --get:*` only"),
            ("find . -delete", "claude"): ("allow", "Claude allows `find:*`; Zoo refuses `find` on purpose (guide s8). Which side moves is his call"),
            ("find . -exec rm {} ;", "claude"): ("allow", "same"),
            ("git add --all", "claude"): ("allow", "rides Claude's broad `git add:*`; the sweep ban is git-policy + review, not a list row"),
            ("git checkout .", "claude"): ("allow", "rides Claude's broad `git checkout *`; Zoo denies the spelling. Narrowing Claude's row is his call"),
            ("git checkout -- .", "claude"): ("allow", "same"),
            ("git clean -n", "claude"): ("ask", "Claude has no `git clean` row at all (safe: the dry run asks). An allow is his"),
            ("python3 -m pytest -q", "claude"): ("ask", "Claude scopes python3 to `.agents/scripts/*`, `-m py_compile` and the venv door; bare `-m pytest` asks"),
            ("npm test", "claude"): ("ask", "Claude has `npm run lint` and `npx vitest run`, no `npm test`"),
        }

        def known(cmd, platform):
            return (cmd, platform) in KNOWN

        miss = {p: [c_ for c_ in DESTRUCTIVE if not known(c_, p) and _verdict(p, c_, L) != "deny"]
                for p in ("zoo", "antigravity")}
        c.check("A2 every destructive command is DENIED on Zoo and Antigravity (known disagreements pinned below)",
                not miss["zoo"] and not miss["antigravity"],
                f"zoo={miss['zoo'][:4]} ag={miss['antigravity'][:4]}")
        cl_leak = [c_ for c_ in DESTRUCTIVE if not known(c_, "claude") and _verdict("claude", c_, L) == "allow"]
        c.check("A3 Claude never auto-APPROVES a destructive command its list does not deliberately allow",
                not cl_leak, f"leak={cl_leak[:4]}")
        miss_c = {p: [c_ for c_ in CEREMONY if not known(c_, p) and _verdict(p, c_, L) != "allow"] for p in PLATFORMS}
        c.check("A4 every ceremony command is ALLOWED on all three",
                not any(miss_c.values()), f"{ {p: v[:3] for p, v in miss_c.items() if v} }")
        miss_u = {p: [c_ for c_ in UNKNOWN if not known(c_, p) and _verdict(p, c_, L) != "ask"] for p in PLATFORMS}
        c.check("A5 every unknown tool ASKS on all three",
                not any(miss_u.values()), f"{ {p: v[:3] for p, v in miss_u.items() if v} }")
        disagree = []
        for cmd in DESTRUCTIVE + CEREMONY + UNKNOWN:
            if any(known(cmd, p) for p in PLATFORMS):
                continue
            vz, va = _verdict("zoo", cmd, L), _verdict("antigravity", cmd, L)
            vc = _verdict("claude", cmd, L)
            if vz != va or (vc != vz and not (vz == "deny" and vc == "ask")):
                disagree.append((cmd, vz, vc, va))
        c.check("A6 parity: identical decisions across the three (Claude's deny reads as ask)",
                not disagree, f"{disagree[:4]}")
        stale = [(cmd, p, want, _verdict(p, cmd, L)) for (cmd, p), (want, _) in KNOWN.items()
                 if _verdict(p, cmd, L) != want]
        c.check("A11 every KNOWN disagreement is still live (a resolved one must be deleted from the list)",
                not stale, f"{stale[:4]}")
        # The grammar facts each matcher hides, pinned so a renderer cannot forget them.
        c.check("A7 antigravity: a flag CLUSTER is one token (-fd is not -f)",
                pm.antigravity_verdict("git clean -fd", [], ["command(git clean -f)"]) == "ask"
                and pm.antigravity_verdict("git clean -fd", [], [r"command(git clean -[a-zA-Z]*[fdx][a-zA-Z]*)"]) == "deny")
        c.check("A8 antigravity: Deny beats a longer Allow (no longest-prefix re-allow)",
                pm.antigravity_verdict("git branch -D main", ["command(git branch -D main)"], ["command(git branch -D)"]) == "deny")
        c.check("A9 zoo: the LONGER prefix wins allow-vs-deny",
                pm.zoo_verdict("git branch -d chore/x", ["git ", "git branch -d chore/"], ["git branch -d"]) == "allow")
        c.check("A10 claude: `Bash(X:*)` equals `Bash(X *)`; a compound is judged per segment",
                pm.claude_verdict("git status", ["Bash(git status:*)"]) == "allow"
                and pm.claude_verdict("git status && rm -rf /", ["Bash(git status:*)"]) == "ask")

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("B · one source, three rendered outputs, drift is red"):
    c.check("B0 permission_render imports", pr is not None)
    c.check("B1 the source exists", SOURCE.exists(), str(SOURCE))
    if pr is not None and SOURCE.exists():
        src = json.loads(SOURCE.read_text(encoding="utf-8"))
        rows = src.get("allow", []) + src.get("deny", [])
        bad = [r.get("id", "?") for r in rows if not all(k in r for k in ("id", "cmd", "why"))]
        c.check("B2 every source row carries id, cmd, why", rows and not bad, f"bad={bad[:5]}")
        bad_p = [r["id"] for r in rows
                 for k in ("only", "not") if k in r and not set(r[k]) <= set(PLATFORMS)]
        c.check("B3 only:/not: name platforms from the closed set", not bad_p, f"{bad_p[:5]}")
        drift = pr.check(ROOT)
        c.check("B4 --check is CLEAN on the tracked tree", not drift, f"{drift[:3]}")
        # Drift detection, both directions, on a temp copy - never the tracked files.
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            copied = []
            for rel in (".vscode/settings.json", ".claude/settings.json",
                        ".agents/permissions/families.json", ".agents/permissions/antigravity.json"):
                if (ROOT / rel).exists():
                    (t / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / rel, t / rel); copied.append(rel)
            c.check("B5 --check is clean on an exact copy (all four files present)",
                    len(copied) == 4 and not pr.check(t), f"copied={len(copied)}/4 drift={pr.check(t)[:2]}")
            p = t / ".vscode" / "settings.json"
            p.write_text(p.read_text(encoding="utf-8").replace('"git "', '"git  "', 1), encoding="utf-8")
            d1 = pr.check(t)
            c.check("B6 a one-char hand edit to the Zoo list is RED and names the file",
                    d1 and any("settings.json" in m for m in d1), f"{d1[:2]}")
            shutil.copy2(ROOT / ".vscode" / "settings.json", p)
            q = t / ".agents" / "permissions" / "antigravity.json"
            if q.exists():
                ag = json.loads(q.read_text(encoding="utf-8"))
                ag["userSettings"]["globalPermissionGrants"]["allow"].append("command(evil)")
                q.write_text(json.dumps(ag, indent=2) + "\n", encoding="utf-8")
                d2 = pr.check(t)
                c.check("B7 an added Antigravity row is RED and names the file",
                        d2 and any("antigravity.json" in m for m in d2), f"{d2[:2]}")
            else:
                c.check("B7 an added Antigravity row is RED and names the file", False, "no rendered file to mutate")
        # The render reproduces the hand-built, battery-green list (set-equal; order is the renderer's).
        if AG_RENDERED.exists() and BASELINE.exists():
            got = json.loads(AG_RENDERED.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
            base = json.loads(BASELINE.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
            # The seed lost nothing: every hand-built row is still rendered. Additions are the lane's
            # deliberate deny fixes (HEAD:main, --prune=, mkfs.*) and are listed in the walkthrough.
            # Six baseline deny rows were SUPERSEDED in-lane by their anchored-regex spelling, because the
            # battery proved the literal token never matched the attached/derived form (`--prune=now`,
            # `mkfs.ext4`). Each old row is named here; the new spelling matches everything the old one did.
            SUPERSEDED = {f"{k}({pre}{b})" for k in ("command", "unsandboxed")
                          for pre in ("", "env -u GITHUB_TOKEN ") for b in ("git gc --prune",)} | {
                          f"{k}(mkfs)" for k in ("command", "unsandboxed")}
            c.check("B8 Antigravity render CONTAINS the 2026-09-03 baseline (allow AND deny; 6 rows superseded by name)",
                    set(base["allow"]) <= set(got["allow"]) and (set(base["deny"]) - SUPERSEDED) <= set(got["deny"])
                    and SUPERSEDED.isdisjoint(set(got["deny"])),
                    f"allow +{len(set(got['allow'])-set(base['allow']))}/-{len(set(base['allow'])-set(got['allow']))} "
                    f"deny +{len(set(got['deny'])-set(base['deny']))}/-{len(set(base['deny'])-set(got['deny']))}")
        else:
            c.check("B8 Antigravity render is set-equal to the 2026-09-03 baseline", False,
                    f"rendered={AG_RENDERED.exists()} baseline={BASELINE.exists()}")
        # Derivation: a row with NO explicit render must come out in each platform's grammar. Every
        # seeded row carries an explicit render, so without this case the derive_* code is dead to
        # the suite and a mutant there survives (found while declaring the mutant table).
        synth = {"env_twin_prefix": "env -u GITHUB_TOKEN ",
                 "allow": [{"id": "x", "cmd": "foo bar", "why": "t"},
                           {"id": "y", "cmd": "pwd", "why": "t", "bare": True},
                           {"id": "z", "cmd": "backend/.venv/bin/", "why": "t"},
                           {"id": "o", "cmd": "zooonly", "why": "t", "only": ["zoo"]}],
                 "deny": [{"id": "d", "cmd": "git zap", "why": "t"}]}
        za_, zd_ = pr.render_zoo(synth)
        c.check("B10a derived Zoo rows: trailing space, bare, no space after a path separator, env twin on git deny",
                za_ == ["foo bar ", "pwd", "backend/.venv/bin/", "zooonly "]
                and zd_ == ["git zap", "env -u GITHUB_TOKEN git zap"], f"{za_} {zd_}")
        cl_ = pr.render_claude(synth)
        c.check("B10b derived Claude rows: `X:*`, bare exact, `X*` after a separator, only:[zoo] excluded, no deny",
                cl_ == ["Bash(foo bar:*)", "Bash(pwd)", "Bash(backend/.venv/bin/*)"], f"{cl_}")
        ag_ = pr.render_antigravity(synth)
        c.check("B10c derived Antigravity rows: command+unsandboxed twins, per-token escaped, env twin on git deny",
                ag_["allow"] == ["command(foo bar)", "unsandboxed(foo bar)", "command(pwd)", "unsandboxed(pwd)",
                                 "command(backend/\\.venv/bin/)", "unsandboxed(backend/\\.venv/bin/)"]
                and ag_["deny"] == ["command(git zap)", "unsandboxed(git zap)",
                                    "command(env -u GITHUB_TOKEN git zap)", "unsandboxed(env -u GITHUB_TOKEN git zap)"],
                f"{ag_}")
        # write() round-trip on a temp copy: a hand-added row is rendered away, the JSONC comments
        # OUTSIDE the arrays survive, a comment with a quote INSIDE the array does not desync the scanner.
        with tempfile.TemporaryDirectory() as td:
            t2 = Path(td)
            for rel in (".vscode/settings.json", ".claude/settings.json",
                        ".agents/permissions/families.json", ".agents/permissions/antigravity.json"):
                (t2 / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, t2 / rel)
            vs2 = t2 / ".vscode" / "settings.json"
            txt = vs2.read_text(encoding="utf-8")
            comments_before = sum(1 for l in txt.splitlines() if l.lstrip().startswith("//"))
            txt = txt.replace('"zoo-code.allowedCommands": [', '"zoo-code.allowedCommands": [\n    // a note with ONE " quote inside the array (an even count re-balances the string state and hides the bug)\n    "bogus-row ",', 1)
            vs2.write_text(txt, encoding="utf-8")
            try:
                wrote = pr.write(t2)
                after = vs2.read_text(encoding="utf-8")
                comments_after = sum(1 for l in after.splitlines() if l.lstrip().startswith("//"))
                ok11 = (".vscode/settings.json" in " ".join(wrote) and "bogus-row" not in after
                        and comments_after == comments_before and not pr.check(t2))
                why11 = f"wrote={wrote} comments {comments_before}->{comments_after} drift={pr.check(t2)[:1]}"
            except Exception as e:  # noqa: BLE001 - a raise is a red row, never a dead file
                ok11, why11 = False, f"write() raised {e!r}"
            c.check("B11 write() renders the hand-added row away, keeps every comment outside the arrays, and --check is clean",
                    ok11, why11)
        # The JSONC scanner on a fixture the real file cannot rescue. In .vscode/settings.json nine rows
        # carry an escaped \" - an odd count - so a comment that flips the string parity gets flipped
        # BACK before the closing bracket and a scanner that stopped skipping comments still lands on
        # the right `]` by luck (mutant M8 survived two sweeps exactly this way). Here the arrays hold
        # no escapes, so the one quote in the comment desyncs the scan all the way to EOF.
        jsonc = ('{\n  "other": 1,\n  "zoo-code.allowedCommands": [\n    // one " quote here\n    "a ", "b "\n  ],\n'
                 '  "zoo-code.deniedCommands": [\n    "x", "y"\n  ],\n  "tail": true\n}\n')
        try:
            out = pr._replace_jsonc_array(jsonc, "zoo-code.allowedCommands", ["p ", "q "])
            parsed = pr._jsonc_load(out)
            ok12 = (parsed["zoo-code.allowedCommands"] == ["p ", "q "] and parsed["zoo-code.deniedCommands"] == ["x", "y"]
                    and parsed["other"] == 1 and parsed["tail"] is True)
            why12 = "" if ok12 else out[:160]
        except Exception as e:  # noqa: BLE001
            ok12, why12 = False, f"scanner raised {e!r}"
        c.check("B12 the JSONC scanner skips a line comment carrying ONE quote and still finds the right `]`", ok12, why12)
        c.check("B9 no --seed left in the renderer (a migration, not a feature)",
                "--seed" not in (SCRIPTS / "permission_render.py").read_text(encoding="utf-8"))

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("C · the Antigravity apply is safe and scoped"):
    c.check("C0 antigravity_permissions_apply imports", ap is not None)
    if ap is not None and AG_RENDERED.exists():
        with tempfile.TemporaryDirectory() as td:
            store = Path(td) / "config.json"
            before = {"userSettings": {"globalPermissionGrants": {"allow": ["unsandboxed(old)"]},
                                       "remoteControlHostname": "some-machine",
                                       "conversationWidth": "WIDE"},
                      "plugins": {"firebase": {"enabled": True}}}
            store.write_text(json.dumps(before, indent=2), encoding="utf-8")
            ap.apply(store, AG_RENDERED)
            after = json.loads(store.read_text(encoding="utf-8"))
            want = json.loads(AG_RENDERED.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
            c.check("C1 grants replaced by the rendered fence", after["userSettings"]["globalPermissionGrants"] == want)
            c.check("C2 every other key preserved (remoteControlHostname, conversationWidth, plugins)",
                    after["userSettings"]["remoteControlHostname"] == "some-machine"
                    and after["userSettings"]["conversationWidth"] == "WIDE"
                    and after["plugins"] == before["plugins"])
            bk = store.with_suffix(".json.scc-backup")
            c.check("C3 a backup was written once", bk.exists()
                    and json.loads(bk.read_text(encoding="utf-8")) == before)
            ap.apply(store, AG_RENDERED)
            c.check("C4 a second apply does NOT overwrite the backup",
                    json.loads(bk.read_text(encoding="utf-8")) == before)
            c.check("C5 --status reads in sync after apply",
                    ap.status(store, AG_RENDERED).startswith("in sync"), ap.status(store, AG_RENDERED))

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("D · rendering rides sync-agents and runs without PowerShell"):
    ps1_code = "\n".join(l for l in PS1.read_text(encoding="utf-8").splitlines()
                         if not l.lstrip().startswith("#"))
    c.check("D1 sync-agents.ps1 LIVE code calls permission_render.py (not a comment)",
            "permission_render.py" in ps1_code)
    c.check("D2 -Status path runs the renderer's --check (the helper is CALLED with -Check, and passes --check)",
            "Invoke-PermissionRender -Check" in ps1_code and "--check" in ps1_code)
    r = subprocess.run([sys.executable, str(SCRIPTS / "permission_render.py"), "--check"],
                       cwd=ROOT, capture_output=True, text=True)
    c.check("D3 the renderer runs standalone under this interpreter (exit 0 or 1, never a crash)",
            r.returncode in (0, 1), f"rc={r.returncode} err={r.stderr.strip()[:120]}")

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("E · /smh-llm-approvals writes the SOURCE and reads Antigravity"):
    body = CMD.read_text(encoding="utf-8")
    c.check("E1 Step 3 names the source file", "families.json" in body)
    c.check("E2 Step 3 names the renderer", "permission_render.py" in body)
    c.check("E3 Step 1 reads Antigravity's store", "~/.gemini/config/config.json" in body)
    c.check("E4 the opencode mirror is byte-identical to the body",
            OC_MIRROR.read_bytes() == CMD.read_bytes())
    c.check("E5 commands/INDEX.md no longer describes the old door",
            "adds the ones he picks to both allow lists" not in (ROOT / ".agents" / "commands" / "INDEX.md").read_text(encoding="utf-8"))

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("F · the record tells the truth"):
    guide = GUIDE.read_text(encoding="utf-8")
    ag_rows = [l for l in guide.splitlines() if l.startswith("|") and "Antigravity" in l.split("|")[1]]
    c.check("F1 the guide's Antigravity rows do not say retired",
            ag_rows and not any("retired" in l.lower() for l in ag_rows), f"rows={len(ag_rows)}")
    c.check("F2 the guide names the Antigravity store and the two rule types",
            "~/.gemini/config/config.json" in guide and "unsandboxed(" in guide and "command(" in guide)
    c.check("F3 the guide records that sandbox mode does NOT auto-approve",
            re.search(r"sandbox[^.\n]{0,80}(does not|never)[^.\n]{0,40}auto-approve", guide, re.I) is not None)
    c.check("F4 zoo memory no longer says Zoo is not in sync-agents",
            "NOT in sync-agents yet" not in MEM_ZOO.read_text(encoding="utf-8"))
    c.check("F5 codex memory counts five surfaces (Zoo present, Antigravity live)",
            "Zoo" in MEM_CODEX.read_text(encoding="utf-8"))

sys.exit(c.finish())
