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
  G · the Claude harvest reads the two machine-local lists, reports allow only, and has no apply

run_all.py executes this file bare (python3 <file>); the __main__ harness at the bottom is what
makes it count. Imports of the modules under test are guarded so a missing module is a FAILED
row in its block, never a file that died in setup and read as a different bug.
"""
from __future__ import annotations

import contextlib
import io
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
try:
    import claude_permissions_status as cs
except Exception:  # noqa: BLE001
    cs = None


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
    # code review 2026-09-03: the spellings that slipped past Antigravity's literal single-token
    # denies while Zoo's prefix rows caught them - flag clusters, `=`-attached values, scope flags,
    # and targets Zoo denies by prefix (everything but chore/ claude/ epic/, HEAD:epic/)
    "git push -fu origin main", "git push --force-with-lease=main:abc origin main",
    "git branch -Df main", "git branch -d main", "git branch -m main x",
    "git add -Av", "git add ./", "git add ../",
    "git config --local core.hooksPath /dev/null", "git config --unset core.hooksPath", "git config user.email x",
    "git push --delete origin main", "git push origin --delete develop",
    "git push origin HEAD:develop", "git push origin HEAD:refs/heads/main", "git push origin :feature",
]

CEREMONY = [
    "git status", "git status --short", "git add .agents/rules/x.md",
    'git commit -m "SCC-378 x"', "git commit -F /tmp/msg.txt",
    "git push origin HEAD:epic/SCC-1-x", "git push -u origin chore/SCC-378-x",
    "git branch -d chore/SCC-378-x", "git push origin --delete chore/x",
    "git push origin --delete claude/x", "git fetch origin main", "git diff --stat",
    "git log --oneline -n 5", "git worktree add .claude/worktrees/x origin/main",
    "git worktree remove .claude/worktrees/x", "git config --get core.hooksPath",
    "git config --list", "git config -l", "git clean -n",
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
    "HOME=/x rm -rf /",   # an assignment prefix outside the named door variables (code review 2026-09-03)
]

# The house command shape (command-shape.md rule 1): every door command is `cd <abs> && <verb>`.
# The vendor documents per-token matching on a line's LEADING tokens and nothing about chains, so the
# render writes a `cd .* && ` twin of every Antigravity deny - this is the battery that pins the twin.
HOUSE = "cd /home/x/Sudo_Hatter_Command && "

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
            ("git config -l", "claude"): ("ask", "same"),
            ("find . -delete", "claude"): ("allow", "Claude allows `find:*`; Zoo refuses `find` on purpose (guide s8). Which side moves is his call"),
            ("find . -exec rm {} ;", "claude"): ("allow", "same"),
            ("git add --all", "claude"): ("allow", "rides Claude's broad `git add:*`; the sweep ban is git-policy + review, not a list row"),
            ("git checkout .", "claude"): ("allow", "rides Claude's broad `git checkout *`; Zoo denies the spelling. Narrowing Claude's row is his call"),
            ("git checkout -- .", "claude"): ("allow", "same"),
            ("git clean -n", "claude"): ("ask", "Claude has no `git clean` row at all (safe: the dry run asks). An allow is his"),
            ("git add -Av", "claude"): ("allow", "rides Claude's broad `git add:*` (same ruling as `git add -A`)"),
            ("git add ./", "claude"): ("allow", "same"),
            ("git add ../", "claude"): ("allow", "same"),
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
        # House-shaped battery (code review 2026-09-03). Zoo splits the chain and denies the tail;
        # Antigravity, if it reads the whole line, sees `cd` first - the `cd .* && ` twin is what denies it.
        house_miss = {p: [c_ for c_ in DESTRUCTIVE if not known(c_, p) and _verdict(p, HOUSE + c_, L) != "deny"]
                      for p in ("zoo", "antigravity")}
        c.check("A12 every destructive command is still DENIED on Zoo and Antigravity behind the house `cd <abs> && ` shape",
                not house_miss["zoo"] and not house_miss["antigravity"],
                f"zoo={house_miss['zoo'][:3]} ag={house_miss['antigravity'][:3]}")
        house_cer = [c_ for c_ in CEREMONY if not known(c_, "antigravity") and _verdict("antigravity", HOUSE + c_, L) != "allow"]
        c.check("A13 antigravity: the twin denies nothing ceremony - every ceremony command stays ALLOWED behind the house shape",
                not house_cer, f"{house_cer[:3]}")
        c.check("A14 antigravity: without the twin the house shape would auto-approve a force push (the mechanism the twin closes)",
                pm.antigravity_verdict(HOUSE + "git push --force origin main", ["command(cd)"], ["command(git push --force.*)"]) == "allow"
                and pm.antigravity_verdict(HOUSE + "git push --force origin main", ["command(cd)"],
                                           ["command(cd .* && git push --force.*)"]) == "deny")
        # SCC-387: the shipped fence must carry a DIRECTORY read grant for the Claude memory store.
        # A per-file grant is what the operator's "always allow" clicks write, and it buys one file;
        # the vendor grants a directory recursively, so the row has to be a directory to be worth having.
        ag_live = json.loads(AG_RENDERED.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
        reads = [r for r in ag_live["allow"] if r.startswith("read_file(")]
        c.check("A15 the Antigravity fence grants the Claude memory store as a DIRECTORY (recursive), not "
                "as the single files a click writes - and file grants never leak into the deny fence",
                any(r.endswith("/memory)") and "*" not in r and not r.endswith("/)") for r in reads)
                and not [r for r in ag_live["deny"] if r.startswith("read_file(")], f"{reads}")

        # ⛔ SCC-393 · the corpus above is COMMANDS, so every verdict row in this block is blind to
        # a `read_file` grant - a different rule kind the same source file ships. Rendered, a row
        # {"cmd": "/home/dlohn", "grant": "read_file"} becomes read_file(/home/dlohn), which the
        # vendor grants RECURSIVELY: ~/.ssh, cloud credentials and every .env under the home dir,
        # readable by the extension. `--check` prints *in sync* (the renderer produced it), no
        # command verdict moves, and A15 only asserts a /memory row still exists - so before this
        # case the whole battery stayed green while the fence had a hole in it. Found by the gate
        # lens on SCC-393's own review, rendered live to confirm rather than argued.
        SENSITIVE = ("/.ssh", "/.aws", "/.gnupg", "/.config/gcloud", "/.kube", "/.docker",
                     "/.netrc", "/.gnupg", "/.password-store")
        def _covers(granted: str, secret_tail: str) -> bool:
            """A recursive dir grant covers a path if that path is at or under it."""
            home = str(Path.home())
            return (granted == home or granted == "/"
                    or (home + secret_tail).startswith(granted.rstrip("/") + "/"))
        leaks = [r for r in reads
                 for tail in SENSITIVE
                 if _covers(r[len("read_file("):-1], tail)]
        c.check("A16 no read_file grant reaches a credential store - a recursive dir grant is the one "
                "rule kind this battery's command corpus cannot see",
                not leaks, f"leaks={leaks[:3]}")
        # The control: without it, A16 passes by having nothing to find.
        c.check("A16b ...and the check BITES - a home-directory grant is reported",
                [1 for tail in SENSITIVE if _covers(str(Path.home()), tail)],
                "a read_file(<home>) row must be seen as covering ~/.ssh")

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("B · one source, three rendered outputs, drift is red"):
    c.check("B0 permission_render imports", pr is not None)
    c.check("B1 the source exists", SOURCE.exists(), str(SOURCE))
    if pr is not None and SOURCE.exists():
        src = json.loads(SOURCE.read_text(encoding="utf-8"))
        rows = src.get("allow", []) + src.get("deny", [])
        bad = [r.get("id", "?") for r in rows if not all(k in r for k in ("id", "cmd", "why"))
               or not str(r.get("cmd", "")).strip()
               or any(isinstance(v, str) or not all(isinstance(x, str) for x in v) for v in (r.get("render") or {}).values())]
        ids = [r.get("id") for r in rows]
        dup = sorted({i for i in ids if ids.count(i) > 1})
        c.check("B2 every source row carries a unique id, a non-empty cmd, why, and list-shaped renders",
                rows and not bad and not dup, f"bad={bad[:5]} dup={dup[:5]}")
        # The renderer refuses the malformed shapes by NAME (code review 2026-09-03): an empty cmd was
        # a bare IndexError, a string render spread into one-letter Zoo allows (`g`, `i`, `t`).
        def _raises(src_):
            try:
                pr.render_zoo(src_)
            except ValueError as e:
                return str(e)
            except Exception as e:  # noqa: BLE001 - a bare crash is a red row (it names no row), never a dead file
                return f"CRASH {e!r}"
            return ""
        e1 = _raises({"allow": [{"id": "empty-cmd", "cmd": "  ", "why": "t"}]})
        e2 = _raises({"allow": [{"id": "str-render", "cmd": "git status", "why": "t", "render": {"zoo": "git status "}}]})
        e3 = _raises({"deny": [{"id": "twice", "cmd": "a", "why": "t"}, {"id": "twice", "cmd": "b", "why": "t"}]})
        c.check("B2b the renderer refuses an empty cmd, a string render, and a duplicate id, naming the row",
                "empty-cmd" in e1 and "str-render" in e2 and "twice" in e3, f"{e1!r} {e2!r} {e3!r}")
        e4 = _raises({"allow": [{"id": "typo-grant", "cmd": "/x", "why": "t", "grant": "read"}]})
        c.check("B2c the renderer refuses an unknown grant kind, naming the row (a typo must not fall "
                "through and render a bare PATH as an allowed command prefix)",
                "typo-grant" in e4 and "read" in e4, f"{e4!r}")
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
        # The render lost no DECISION the hand-built, battery-green baseline made (2026-09-03 morning):
        # every command the baseline denied is still denied, every one it allowed is still allowed,
        # measured over the battery through the Antigravity mirror. Rows are compared as behaviour, not
        # text, because the code review re-spelled the push/branch/add/config denies as cluster classes
        # and target lookaheads and narrowed the `[A-Z_]+=` allow to the named door variables - a row
        # that vanished OUTSIDE those families is still red here, by name.
        if AG_RENDERED.exists() and BASELINE.exists() and pm is not None:
            got = json.loads(AG_RENDERED.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
            base = json.loads(BASELINE.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
            regress = [(cmd, vb, vg) for cmd in DESTRUCTIVE + CEREMONY + UNKNOWN
                       for vb in [pm.antigravity_verdict(cmd, base["allow"], base["deny"])]
                       for vg in [pm.antigravity_verdict(cmd, got["allow"], got["deny"])]
                       if vb != vg and (vb, vg) not in {("allow", "deny"), ("allow", "ask"), ("ask", "deny")}]
            RESPELLED = re.compile(r"^(command|unsandboxed)\((env -u GITHUB_TOKEN )?"
                                   r"(git (push|branch|add|config|gc --prune)\b|mkfs\)|\[A-Z_\]\+=)")
            gone = sorted((set(base["allow"]) | set(base["deny"])) - set(got["allow"]) - set(got["deny"]))
            unexplained = [r for r in gone if not RESPELLED.match(r)]
            c.check("B8 Antigravity render keeps every baseline DECISION (deny stays deny, allow stays allow or tightens) "
                    "and every dropped baseline row belongs to a re-spelled family",
                    not regress and not unexplained,
                    f"regress={regress[:3]} unexplained={unexplained[:3]} dropped={len(gone)} "
                    f"allow {len(base['allow'])}->{len(got['allow'])} deny {len(base['deny'])}->{len(got['deny'])}")
        else:
            c.check("B8 Antigravity render keeps every baseline DECISION", False,
                    f"rendered={AG_RENDERED.exists()} baseline={BASELINE.exists()}")
        # Derivation: a row with NO explicit render must come out in each platform's grammar. Every
        # seeded row carries an explicit render, so without this case the derive_* code is dead to
        # the suite and a mutant there survives (found while declaring the mutant table).
        synth = {"env_twin_prefix": "env -u GITHUB_TOKEN ", "house_twin_prefix": "cd .* && ",
                 "allow": [{"id": "x", "cmd": "foo bar", "why": "t"},
                           {"id": "y", "cmd": "pwd", "why": "t", "bare": True},
                           {"id": "z", "cmd": "backend/.venv/bin/", "why": "t"},
                           {"id": "o", "cmd": "zooonly", "why": "t", "only": ["zoo"]}],
                 "deny": [{"id": "d", "cmd": "git zap -f", "why": "t"}]}
        za_, zd_ = pr.render_zoo(synth)
        c.check("B10a derived Zoo rows: trailing space, bare, no space after a path separator, env twin on git deny",
                za_ == ["foo bar ", "pwd", "backend/.venv/bin/", "zooonly "]
                and zd_ == ["git zap -f", "env -u GITHUB_TOKEN git zap -f"], f"{za_} {zd_}")
        cl_ = pr.render_claude(synth)
        c.check("B10b derived Claude rows: `X:*`, bare exact, `X*` after a separator, only:[zoo] excluded, no deny",
                cl_ == ["Bash(foo bar:*)", "Bash(pwd)", "Bash(backend/.venv/bin/*)"], f"{cl_}")
        ag_ = pr.render_antigravity(synth)
        ZAP = "git zap -[a-zA-Z]*f[a-zA-Z]*"
        c.check("B10c derived Antigravity rows: command+unsandboxed twins, per-token escaped, `.*` tail after a separator, "
                "a deny's single-letter flag becomes its cluster class, env twin and house `cd .* && ` twin on the deny",
                ag_["allow"] == ["command(foo bar)", "unsandboxed(foo bar)", "command(pwd)", "unsandboxed(pwd)",
                                 "command(backend/\\.venv/bin/.*)", "unsandboxed(backend/\\.venv/bin/.*)"]
                and ag_["deny"] == [f"command({ZAP})", f"unsandboxed({ZAP})",
                                    f"command(env -u GITHUB_TOKEN {ZAP})", f"unsandboxed(env -u GITHUB_TOKEN {ZAP})",
                                    f"command(cd .* && {ZAP})", f"unsandboxed(cd .* && {ZAP})",
                                    f"command(cd .* && env -u GITHUB_TOKEN {ZAP})", f"unsandboxed(cd .* && env -u GITHUB_TOKEN {ZAP})"],
                f"{ag_}")
        # A file grant is a different RULE KIND, not a different spelling of a command rule (SCC-387).
        synth_r = {"allow": [{"id": "r", "cmd": "/home/x/.claude/projects/slug/memory", "why": "t",
                              "grant": "read_file", "only": ["antigravity"]}], "deny": []}
        agr = pr.render_antigravity(synth_r)
        c.check("B10e a read_file row renders as ONE bare read_file(<dir>) - no command/unsandboxed twins, "
                "no per-token regex escaping (the vendor matches file targets as paths), and nothing at all "
                "for Zoo or Claude",
                agr == {"allow": ["read_file(/home/x/.claude/projects/slug/memory)"], "deny": []}
                and pr.render_zoo(synth_r) == ([], [])
                and pr.render_claude(synth_r) == [],
                f"{agr} {pr.render_zoo(synth_r)} {pr.render_claude(synth_r)}")
        c.check("B10f a read_file row is skipped even without only:[antigravity] - the derivation, not the "
                "scope, is what keeps a bare path out of the command fences",
                pr.render_zoo({"allow": [{"id": "r2", "cmd": "/etc", "why": "t", "grant": "read_file"}],
                               "deny": []}) == ([], [])
                and pr.render_claude({"allow": [{"id": "r2", "cmd": "/etc", "why": "t", "grant": "read_file"}]}) == [])
        c.check("B10d the derived Antigravity rows MATCH what their Zoo twins match (the drift the renderer exists to prevent)",
                pm is not None
                and pm.antigravity_verdict("backend/.venv/bin/pytest -q", ag_["allow"], []) == "allow"
                and pm.zoo_verdict("backend/.venv/bin/pytest -q", za_, []) == "allow"
                and pm.antigravity_verdict("git zap -fd", [], ag_["deny"]) == "deny"
                and pm.zoo_verdict("git zap -fd", [], zd_) == "deny")
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
            # drift the other two targets as well, so write()'s Claude and Antigravity branches are DRIVEN
            # (until the code review of 2026-09-03 only the Zoo file was drifted and both branches could be
            # disabled without a red row)
            cl2 = t2 / ".claude" / "settings.json"
            cdoc = json.loads(cl2.read_text(encoding="utf-8")); cdoc["permissions"]["allow"].append("Bash(bogus-claude:*)")
            cl2.write_text(json.dumps(cdoc, indent=2) + "\n", encoding="utf-8")
            ag2 = t2 / ".agents" / "permissions" / "antigravity.json"
            adoc = json.loads(ag2.read_text(encoding="utf-8")); adoc["userSettings"]["globalPermissionGrants"]["deny"].append("command(bogus-ag)")
            ag2.write_text(json.dumps(adoc, indent=2) + "\n", encoding="utf-8")
            try:
                wrote = pr.write(t2)
                after = vs2.read_text(encoding="utf-8")
                comments_after = sum(1 for l in after.splitlines() if l.lstrip().startswith("//"))
                ok11 = (set(wrote) == {".vscode/settings.json", ".claude/settings.json", ".agents/permissions/antigravity.json"}
                        and "bogus-row" not in after and "bogus-claude" not in cl2.read_text(encoding="utf-8")
                        and "bogus-ag" not in ag2.read_text(encoding="utf-8")
                        and comments_after == comments_before and not pr.check(t2))
                why11 = f"wrote={wrote} comments {comments_before}->{comments_after} drift={pr.check(t2)[:1]}"
            except Exception as e:  # noqa: BLE001 - a raise is a red row, never a dead file
                ok11, why11 = False, f"write() raised {e!r}"
            c.check("B11 write() renders a hand-added row away in ALL THREE files, keeps every comment outside the arrays, and --check is clean",
                    ok11, why11)
            # The JSONC shapes VS Code accepts (code review 2026-09-03): a comment trailing a value, a
            # block comment carrying a `]` inside the array, a trailing comma. check() read them as a
            # traceback and write() spliced into the block comment.
            txt3 = vs2.read_text(encoding="utf-8")
            txt3 = txt3.replace('"zoo-code.allowedCommands": [', '"zoo-code.allowedCommands": [ // trailing note\n    /* block ] note */', 1)
            txt3 = txt3.replace('"zoo-code.deniedCommands": [', '"zoo-code.deniedCommands": [ /* another ] */', 1)
            vs2.write_text(txt3, encoding="utf-8")
            try:
                d13 = pr.check(t2)
                parsed13 = pr._jsonc_load(txt3)
                ok13 = (d13 == [] and parsed13["zoo-code.allowedCommands"] == pr.render_zoo(pr.load_source(t2))[0]
                        and pr._jsonc_load('{"a": [1, 2,], "b": {"c": "x // not a comment",},}') == {"a": [1, 2], "b": {"c": "x // not a comment"}})
                why13 = f"drift={d13[:1]}"
            except Exception as e:  # noqa: BLE001
                ok13, why13 = False, f"raised {e!r}"
            c.check("B13 --check reads inline `//`, `/* ] */` and trailing-comma JSONC as in sync, never as a crash", ok13, why13)
            vs2.write_text(txt3.replace('"zoo-code.deniedCommands"', '"zoo-code.deniedCommands" oops', 1), encoding="utf-8")
            try:
                d14 = pr.check(t2)
                ok14 = len(d14) == 1 and "settings.json" in d14[0] and "unreadable" in d14[0]
                why14 = f"{d14[:1]}"
            except Exception as e:  # noqa: BLE001
                ok14, why14 = False, f"raised {e!r}"
            c.check("B14 a file that will not parse is reported as DRIFT naming the file, never a traceback", ok14, why14)
            # write() is all-or-nothing in effect (code review 2026-09-03): run from Claude Code the sandbox
            # refuses `.claude/settings.json`, and the old Zoo-first order left the Zoo list ahead of the other
            # two. The Claude file is written FIRST, so a refusal there leaves every other file untouched.
            vs2.write_text(txt3, encoding="utf-8")
            vtxt = vs2.read_text(encoding="utf-8").replace('"zoo-code.allowedCommands": [', '"zoo-code.allowedCommands": [\n    "bogus-again ",', 1)
            vs2.write_text(vtxt, encoding="utf-8")
            cdoc = json.loads(cl2.read_text(encoding="utf-8")); cdoc["permissions"]["allow"].append("Bash(bogus-claude-2:*)")
            cl2.write_text(json.dumps(cdoc, indent=2) + "\n", encoding="utf-8")
            cl2.chmod(0o444)
            try:
                try:
                    pr.write(t2); raised15 = "nothing raised"
                except PermissionError as e:
                    raised15 = f"PermissionError({e.filename})"
                ok15 = raised15.startswith("PermissionError") and "bogus-again" in vs2.read_text(encoding="utf-8")
                why15 = f"{raised15}; zoo untouched={'bogus-again' in vs2.read_text(encoding='utf-8')}"
            finally:
                cl2.chmod(0o644)
            c.check("B15 a refused Claude write leaves the Zoo file UNTOUCHED (Claude is written first; nothing runs ahead)", ok15, why15)
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
                                       "remoteControlHostname": "hätter-pc",
                                       "conversationWidth": "WIDE"},
                      "plugins": {"firebase": {"enabled": True}}}
            store.write_text(json.dumps(before, indent=2, ensure_ascii=False), encoding="utf-8")
            ap.apply(store, AG_RENDERED)
            after = json.loads(store.read_text(encoding="utf-8"))
            want = json.loads(AG_RENDERED.read_text(encoding="utf-8"))["userSettings"]["globalPermissionGrants"]
            c.check("C1 grants replaced by the rendered fence", after["userSettings"]["globalPermissionGrants"] == want)
            c.check("C2 every other key preserved (remoteControlHostname, conversationWidth, plugins) - non-ASCII kept as written",
                    after["userSettings"]["remoteControlHostname"] == "hätter-pc"
                    and "hätter-pc" in store.read_text(encoding="utf-8")
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
            # The operator's instrument must be seen saying DRIFT (code review 2026-09-03: a status()
            # that always said in-sync passed C5). One deny dropped from the store -> DRIFT with counts.
            drifted = json.loads(store.read_text(encoding="utf-8"))
            drifted["userSettings"]["globalPermissionGrants"]["deny"].pop()
            store.write_text(json.dumps(drifted, indent=2), encoding="utf-8")
            s6 = ap.status(store, AG_RENDERED)
            c.check("C6 --status reads DRIFT with counts when the store lost a deny row",
                    s6.startswith("DRIFT") and "tracked-missing=1" in s6, s6)
            try:
                rc7 = ap.main(["--apply", "--store", str(store), "--rendered", str(Path(td) / "nope.json")])
            except Exception as e:  # noqa: BLE001 - a traceback is the failure this row exists to catch
                rc7 = f"raised {e!r}"
            c.check("C7 --apply with a missing rendered file exits 2 with an ERROR line, and writes nothing",
                    rc7 == 2 and json.loads(store.read_text(encoding="utf-8")) == drifted, f"rc={rc7}")

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("D · rendering rides sync-agents and runs without PowerShell"):
    ps1_code = "\n".join(l for l in PS1.read_text(encoding="utf-8").splitlines()
                         if not l.lstrip().startswith("#"))
    # The sync path must CALL the helper, not merely define it (code review 2026-09-03: the definition
    # alone satisfied the old grep), and after the Zoo surfaces so a render sees the synced tree.
    call_sync = ps1_code.find("Invoke-PermissionRender -WhatIf:$WhatIf")
    call_zoo = ps1_code.find("Sync-ZooSurfaces ")
    c.check("D1 sync-agents.ps1 LIVE code CALLS the renderer on the sync path, after the Zoo surfaces",
            "permission_render.py" in ps1_code and call_sync > 0 and 0 < call_zoo < call_sync,
            f"sync-call@{call_sync} zoo-call@{call_zoo}")
    c.check("D2 -Status path runs the renderer's --check (the helper is CALLED with -Check, and passes --check)",
            "Invoke-PermissionRender -Check" in ps1_code and "--check" in ps1_code)
    r = subprocess.run([sys.executable, str(SCRIPTS / "permission_render.py"), "--check"],
                       cwd=ROOT, capture_output=True, text=True)
    c.check("D3 the renderer runs standalone under this interpreter and reads the tracked tree as in sync (exit 0)",
            r.returncode == 0 and "in sync" in r.stdout, f"rc={r.returncode} out={r.stdout.strip()[:80]} err={r.stderr.strip()[:120]}")
    helper_start = ps1_code.find("function Invoke-PermissionRender")
    helper = ps1_code[helper_start:helper_start + 1500]
    c.check("D4 a renderer that dies during a sync is NAMED, not swallowed ($LASTEXITCODE read inside the helper)",
            helper_start > 0 and "$LASTEXITCODE" in helper and "permission render FAILED" in helper)

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
    c.check("E6 Step 1 reads BOTH machine-local Claude lists by name",
            "~/.claude/settings.json" in body and ".claude/settings.local.json" in body)
    c.check("E7 the door states Claude has no apply, names the script, AND keeps the never-edits law "
            "- the plan promised all three and only two were pinned (acceptance lens)",
            "Claude has no apply" in body and "claude_permissions_status.py" in body
            and "does not edit the two machine-local Claude files" in body)
    c.check("E8 the door names the two blank-cheque rows it must not promote silently",
            "Bash(bash:*)" in body and "Bash(sh:*)" in body)

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
    mem_zoo = MEM_ZOO.read_text(encoding="utf-8")
    mem_index = (ROOT / "_artifacts" / "_memory" / "MEMORY.md").read_text(encoding="utf-8")
    c.check("F4 zoo memory no longer says Zoo is not in sync-agents - body, frontmatter description, and the MEMORY.md hook",
            not re.search(r"not (yet )?in sync-agents", mem_zoo, re.I)
            and not re.search(r"zoo-code-replaces-roo-code[^\n]*not in sync-agents", mem_index, re.I))
    c.check("F6 the guide records the house `cd .* && ` deny twin and the chain residual it does not cover",
            "cd .* && " in guide and re.search(r"chain", guide, re.I) is not None)
    c.check("F5 codex memory counts five surfaces (Zoo present, Antigravity live)",
            "Zoo" in MEM_CODEX.read_text(encoding="utf-8"))

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("G · the Claude harvest reads the machine-local lists"):
    c.check("G0 claude_permissions_status imports", cs is not None)
    if cs is not None:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            def _write(name, allow, deny=None):
                perms = {"allow": allow}
                if deny is not None:
                    perms["deny"] = deny
                (d / name).write_text(json.dumps({"permissions": perms}), encoding="utf-8")
                return d / name
            tracked = _write("tracked.json", ["Bash(git status:*)", "Bash(ls:*)"])
            user = _write("user.json", ["Bash(git status:*)", "Bash(npm:*)"], deny=["Bash(rm:*)"])
            missing = d / "never-written.json"
            c.check("G1 a row the tracked list does not carry is reported, named",
                    cs.local_only(tracked, user, missing)[user] == ["Bash(npm:*)"],
                    str(cs.local_only(tracked, user, missing)[user]))
            c.check("G2 a row present in BOTH is not reported",
                    "Bash(git status:*)" not in cs.local_only(tracked, user, missing)[user])
            c.check("G3 an absent machine-local file counts as EMPTY, not an error",
                    cs._allow(missing) == set() and cs.local_only(tracked, user, missing)[missing] == [])
            # deny is the fence; this door never reads or writes one, so a report that surfaced a
            # deny row would invite exactly the edit that law forbids.
            c.check("G4 a deny row is never reported, even when the two files disagree on it",
                    not any("rm" in r for rows in cs.local_only(tracked, user, missing).values() for r in rows))
            s_local = cs.status(tracked, user, missing)
            c.check("G5 status names the count when rows are machine-local",
                    s_local.startswith("MACHINE-LOCAL") and "1" in s_local, s_local)
            # ⛔ G5 alone cannot tell rows from files: its fixture has one of each, so a status()
            # counting FILES ships green. Two rows in one file plus one in another, asserted as the
            # exact string, is the only shape that separates them (test-adequacy lens, 2026-09-04).
            two = _write("two.json", ["Bash(git status:*)", "Bash(npm:*)", "Bash(jq:*)"])
            one = _write("one.json", ["Bash(rsync:*)"])
            c.check("G5b the count is ROWS, not files - 3 across two files, split by ROLE not basename",
                    cs.status(tracked, two, one)
                    == "MACHINE-LOCAL allow rows: 3 (user=2 project=1) - they decide on this machine only",
                    cs.status(tracked, two, one))
            # Claude offers the SAME grant at user and project scope, so one rule in both files is
            # an ordinary state - and the headline is the number the door quotes (edge lens).
            dup = _write("dup.json", ["Bash(rsync:*)"])
            c.check("G5c one rule granted at BOTH scopes is one rule, not two",
                    cs.status(tracked, one, dup).startswith("MACHINE-LOCAL allow rows: 1 "),
                    cs.status(tracked, one, dup))
            # `{"permissions": null}` is legal JSON; a .get default never fires for an explicit null.
            nul = d / "null.json"
            nul.write_text('{"permissions": null}', encoding="utf-8")
            bom = d / "bom.json"
            bom.write_bytes(b'\xef\xbb\xbf{"permissions": {"allow": ["Bash(jq:*)"]}}')
            try:
                g5d = (cs._allow(nul), cs._allow(bom))
            except Exception as e:  # noqa: BLE001 - a traceback IS the failure these rows catch
                g5d = f"raised {e!r}"
            c.check("G5d an explicit null permissions block, and a Windows BOM, are both read - not raised",
                    g5d == (set(), {"Bash(jq:*)"}), str(g5d)[:90])
            # The instrument must be SEEN saying the other thing too - a status() hard-wired to
            # one answer passes a one-sided check (the lesson C6 records for the sibling script).
            same = _write("same.json", ["Bash(git status:*)"])
            c.check("G6 status reads clean when nothing is machine-local",
                    cs.status(tracked, same, missing) == cs.NOTHING_LOCAL, cs.status(tracked, same, missing))
            c.check("G7 a missing tracked list exits 2 and says so",
                    cs.main(["--rendered", str(missing), "--user", str(user), "--project", str(missing)]) == 2)
            # A file the operator is TOLD to edit by hand must name itself when it does not parse,
            # not die in a traceback part-way through the door's Step 1 (blind lens, 2026-09-04).
            bad = d / "bad.json"
            bad.write_text('{"permissions": {"allow": ["Bash(ls:*)",]}}', encoding="utf-8")
            try:
                rc9 = cs.main(["--rendered", str(tracked), "--user", str(bad), "--project", str(missing)])
            except Exception as e:  # noqa: BLE001 - a traceback IS the failure this row exists to catch
                rc9 = f"raised {e!r}"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_ok = cs.main(["--rendered", str(tracked), "--user", str(user), "--project", str(missing)])
            out = buf.getvalue()
            c.check("G7b a clean run exits 0 AND PRINTS the harvested row - the list is the only product",
                    rc_ok == 0 and "Bash(npm:*)" in out and "MACHINE-LOCAL" in out,
                    f"rc={rc_ok} printed={len(out)}b")
            c.check("G7c the three default paths resolve as the docstring advertises",
                    cs.RENDERED == CLAUDE and cs.USER == Path.home() / ".claude" / "settings.json"
                    and cs.PROJECT == ROOT / ".claude" / "settings.local.json",
                    f"{cs.RENDERED}")
            empty = d / "empty.json"
            empty.write_text("", encoding="utf-8")
            c.check("G3b an EMPTY machine-local file is EMPTY too - it declares no rows, which is not damage",
                    cs._allow(empty) == set())
            try:
                rc9d = cs.main(["--rendered", str(tracked), "--user", str(d), "--project", str(missing)])
            except Exception as e:  # noqa: BLE001 - a traceback IS the failure this row exists to catch
                rc9d = f"raised {e!r}"
            c.check("G9d a machine-local path that cannot be READ exits 2 too, never a traceback",
                    rc9d == 2, f"rc={rc9d}")
            c.check("G9 a machine-local file that does not parse exits 2, never a traceback",
                    rc9 == 2, f"rc={rc9}")
            try:
                cs._allow(bad)
                g9b = "did not raise"
            except ValueError as e:
                g9b = str(e)
            c.check("G9b and the error NAMES the file - exit 2 alone passes without the guard, "
                    "because JSONDecodeError already subclasses ValueError",
                    "bad.json" in g9b and "not readable JSON" in g9b, g9b[:90])
            # The law, pinned structurally: Claude's rendered file IS its live file, so an apply
            # here would have nothing to write into and could only destroy. It must never appear.
            # Scan the CODE, not the prose: the module docstring STATES the law ("there is NO
            # --apply"), and a substring check over the whole file reads its own law as a breach.
            # ⛔ `.split('"""')[2]` was the first spelling and it was VACUOUS - segment 2 is only the
            # slice between the module docstring and the first function docstring (454 of 4,886
            # chars), so `main()` was never scanned and an --apply added there passed. Every EVEN
            # segment is code, every odd one a docstring; join the even ones (blind lens, 2026-09-04,
            # reproduced with an apply-mutant).
            src8 = (SCRIPTS / "claude_permissions_status.py").read_text(encoding="utf-8")
            code = "".join(src8.split('"""')[0::2])
            c.check("G8a the no-apply scan covers the WHOLE file, main() included - not one 454-char slice",
                    "def main(" in code and "def _allow(" in code and "def status(" in code,
                    f"scanned={len(code)} of {len(src8)}")
            c.check("G8 the script has NO apply and writes nothing - read-only by construction",
                    not hasattr(cs, "apply") and "--apply" not in code
                    and not any(w in code for w in ("write_text", "write_bytes", "open(")),
                    f"apply_attr={hasattr(cs, 'apply')}")

# ═══════════════════════════════════════════════════════════════════════════════════════════
if c.block("H · the door carries its own road - SCC-393"):
    body = CMD.read_text(encoding="utf-8")
    rule = (ROOT / ".agents" / "rules" / "artifacts-always-first.md").read_text(encoding="utf-8")

    # ⛔ EVERY ROW IN THIS BLOCK IS SECTION-SCOPED, and that is not style. The first cut of this
    # block was seven body-wide substring greps, and a blind lens killed FIVE of them with real
    # mutants: the fence-battery block was moved from Step 3 into Step 5 under "afterwards, if you
    # feel like it" and the ordering check stayed green; the whole apply paragraph was deleted and
    # the sandbox check stayed green on an unrelated `sandbox off` in Step 4; and the SCC-393
    # exemption was replaced with its literal INVERSE ("is NOT exempt ... takes the FULL lane")
    # and the rule check stayed green, because the four strings it greps for appear in that text
    # too. A substring over a whole document cannot express WHERE, and every property here is a
    # property about where.
    def section(text: str, head: str, nxt: str) -> str:
        a = text.find(head)
        b = text.find(nxt, a + 1) if a >= 0 else -1
        return text[a:b] if a >= 0 and b > a else ""

    step3 = section(body, "## Step 3 — Write what he picked", "## Step 4 — Land it")
    step4 = section(body, "## Step 4 — Land it", "## Step 5 — Report what changed")
    skip  = section(rule, "## When to Skip", "\n## ")
    c.check("H0 the sections this block scopes to all resolve - a renamed heading must FAIL here, "
            "not silently make every row below vacuous",
            len(step3) > 500 and len(step4) > 500 and len(skip) > 500,
            f"step3={len(step3)} step4={len(step4)} skip={len(skip)}")

    # The road. git-policy.md bans a self-merge for EVERY door in this repo ("no eligibility test,
    # no 'small enough' class, no self-merge"), and this door was written once with exactly that
    # road - checkout main, merge --no-ff, mint, push origin main - while the suite stayed green,
    # because test_door_preflight_order.py's DOORS dict did not name it. It does now; these two
    # rows are the local half.
    c.check("H1 Step 4 lands through a PR and takes NONE of the banned road (no merge, no token, "
            "no main push, no branch switch) - git-policy bans all four for every door",
            "gh pr create" in step4
            and not any(w in step4 for w in ("mint-push-token", "git push origin main",
                                             "checkout main", "merge --no-ff", "refs/heads/gate/")),
            f"pr={'gh pr create' in step4}")
    c.check("H1b Step 4 pushes the chore branch before opening the PR - an unpushed head is a PR "
            "that cannot open",
            step4.find("git push -u origin chore/") > 0
            and step4.find("git push -u origin chore/") < step4.find("gh pr create"))

    # ORDER, not presence: the fence check is worthless after the report.
    c.check("H2 the fence battery is named INSIDE Step 3 - moving it after the report must fail, "
            "which a body-wide substring cannot see",
            "test_permission_parity.py" in step3 and "run_all.py" in step3,
            f"in_step3={'test_permission_parity.py' in step3}")
    c.check("H2b Step 3 tells the reader a red row is not always a pick to back out - A11 goes red "
            "when a GOOD pick RESOLVES a known disagreement, and the test requires that row be "
            "deleted, which the back-it-out instruction alone forbids",
            "A11" in step3 and "resolve" in step3.lower())
    c.check("H2c ...and that a refused pick may have NO deny row - npx is pinned by a battery case, "
            "so promising a deny row unconditionally makes the reporter invent one",
            "no deny row" in step3.lower())

    # Scoped to the APPLY paragraph, not the document: Step 1 carries an unrelated `sandbox off`
    # caveat about claude_permissions_status.py, and Step 4 carries another about config.lock.
    c.check("H3 the SANDBOX warning sits in Step 3 with the applies - not Step 1's unrelated "
            "caveat and not Step 4's config.lock note",
            re.search(r"sandbox off", step3, re.I) is not None
            and "Read-only file system" in step3)
    c.check("H3b ...and it does not attribute write_text to BOTH applies - zoo_permissions_apply "
            "writes through sqlite3/copy2 and raises a different error",
            "sqlite3" in step3 or "readonly database" in step3)
    c.check("H4 the window reload sits with the Antigravity apply in Step 3",
            re.search(r"reload", step3, re.I) is not None)

    # The exemption, scoped to the section that IS the law, and to the bullet that names the door.
    bullet = ""
    for chunk in skip.split("\n- "):
        if "/smh-llm-approvals" in chunk:
            bullet = chunk
            break
    c.check("H5 the exemption is a real bullet in When-to-Skip naming the door - replacing it with "
            "its inverse must FAIL here (a blind lens did exactly that and the first cut passed)",
            len(bullet) > 400 and "skip the plan" in bullet, f"bullet={len(bullet)}ch")
    c.check("H5b the SAME bullet carries all four guards, including the operator's pick, and names "
            "run_all.py - NOT the battery alone: the one-interpreter law that refused a harvested "
            "row lives in test_settings_allowlist.py, which the battery does not run",
            all(g in bullet for g in ("permission_render.py --check", "run_all.py",
                                      "families.json", "pick")),
            f"missing={[g for g in ('permission_render.py --check', 'run_all.py', 'families.json', 'pick') if g not in bullet]}")
    c.check("H5c the bullet does NOT claim the ceremony reviewed the harvested rows - it did not: "
            "the SCC-392 harvest branch carried no plan, no walkthrough and no review at all",
            "five-lens review passed" not in bullet and "review passed" not in bullet)

    # RUN the classifier; do not grep the file for one spelling of the widening it forbids.
    sys.path.insert(0, str(SCRIPTS))
    import lane_qualify as lq  # noqa: E402
    v_perm, _ = lq.classify(ROOT, [".agents/permissions/families.json"], False, None)
    v_all, _ = lq.classify(ROOT, [".agents/permissions/families.json", ".claude/settings.json",
                                  ".vscode/settings.json", ".agents/permissions/antigravity.json"],
                           False, None)
    c.check("H6 lane_qualify STILL answers TASK for the fence - run it, never grep it: the first "
            "cut checked one literal and a mutant that spelled the prefix by concatenation passed",
            v_perm == "TASK" and v_all == "TASK", f"one={v_perm} four={v_all}")

sys.exit(c.finish())
