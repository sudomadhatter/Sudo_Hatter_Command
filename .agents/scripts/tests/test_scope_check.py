"""scope_check.py — the quick lane's line, as a script (SCC-443).

The quick lane needs a line or it becomes the default because it is faster. The line is a list
of CRITICAL SURFACES (auth, billing, security rules, FAA-facing answers, CI) declared per repo in
`.agents/critical-surfaces.json`, and this script answers one question from PATHS: does the
planned set — or the real diff — touch one? `OVERLAP` is a SOFT stop: the agent stops, prints
what overlaps and why, and only the operator's word moves the lane past it. The script never
prompts, never writes, and has no override flag, so the only override that can exist is a
quoted sentence in the plan.

  ── WHY THESE CASES ────────────────────────────────────────────────────────────────────────
Each case pins a way the check could go quiet. A repo map must WIN over the generic set (a
project's own list is the law; the generic set is the fallback for a repo that wrote none). A
missing map must be LOUD (`MAP: none`), because a silent fallback reads as "nothing critical
here". Empty input must be an ERROR, never `CLEAR` — silence is unknown scope, the tripwire
`lane_qualify.py` and `/smh-self-audit` both name. A trailing slash is a prefix and nothing
else is, so `backend-notes/` does not match `backend/`. And the generic fragments match a path
SEGMENT, never a substring, or `docs/author-guide.md` overlaps `auth` in every unmapped repo and
the first thing the operator does is switch the stop off (the plan's own audit, finding 1).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, run_script
import _pf_fixtures as pf

ROOT = SCRIPTS.parents[1]
RULE = ROOT / ".agents" / "rules" / "critical-surfaces.md"
LOBBY_MAP = ROOT / ".agents" / "critical-surfaces.json"
SCRIPT = SCRIPTS / "scope_check.py"
FIVE = ("auth", "billing", "rules", "answers", "ci")


def write_map(repo: Path, surfaces: dict) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "critical-surfaces.json").write_text(
        json.dumps({"surfaces": surfaces}), encoding="utf-8")


def run(repo: Path, *args: str) -> tuple[int, list[str]]:
    rc, out = run_script("scope_check.py", "--repo", str(repo), *args)
    return rc, out.splitlines()


def first(lines: list[str]) -> str:
    return lines[0].strip() if lines else ""


def main() -> int:
    c = Cases("scope_check.py — the quick lane's line, as a script (SCC-443)")

    if c.block("A · the rule and the lobby's map exist"):
        rule = RULE.read_text(encoding="utf-8") if RULE.exists() else ""
        c.check("critical-surfaces.md exists and is a rule (frontmatter + body)",
                len(rule) > 1500 and rule.startswith("---"), f"{len(rule)} bytes")
        for word in ("Auth", "Billing", "Security rules", "FAA-facing", "CI"):
            c.check(f"the rule names the surface: {word}", word in rule,
                    "five surfaces, one reason each")
        c.check("the rule states the map format (critical-surfaces.json)",
                "critical-surfaces.json" in rule and '"surfaces"' in rule,
                "each repo declares its own paths; the lobby's script only reads them")
        c.check("the rule says the stop is SOFT and only the operator's word overrides",
                re.search(r"soft", rule, re.I) is not None
                and "Scope override" in rule, "no agent override exists; the script never asks")
        lobby = {}
        try:
            lobby = json.loads(LOBBY_MAP.read_text(encoding="utf-8")) if LOBBY_MAP.exists() else {}
        except json.JSONDecodeError:
            lobby = {}
        surfaces = lobby.get("surfaces", {})
        c.check("the lobby's map parses and carries all five keys",
                all(k in surfaces for k in FIVE), f"keys={sorted(surfaces)}")
        c.check("every lobby surface carries a `why` and a `paths` list",
                bool(surfaces) and all(isinstance(v.get("why"), str) and v["why"]
                    and isinstance(v.get("paths"), list) for v in surfaces.values()),
                "a surface that does not apply says so; a reader sees the decision, not a gap")
        c.check("the lobby's CI surface names the gates (.github/, the hooks, a preflight)",
                any(p == ".github/" for p in surfaces.get("ci", {}).get("paths", []))
                and any(p.endswith("task_preflight.py")
                        for p in surfaces.get("ci", {}).get("paths", [])),
                str(surfaces.get("ci", {}).get("paths")))

    if c.block("B · the check reads a repo map: one RED per surface, then CLEAR"):
        with TempDir() as t:
            repo = t / "repo"
            write_map(repo, {
                "auth":    {"why": "every user's account", "paths": ["backend/auth/", "app/login.py"]},
                "billing": {"why": "revenue", "paths": ["backend/billing.py"]},
                "rules":   {"why": "the last wall", "paths": ["firebase/firestore.rules"]},
                "answers": {"why": "regulatory guidance", "paths": ["backend/agents/specialist/"]},
                "ci":      {"why": "what green means", "paths": [".github/"]},
            })
            for surface, path in (("auth", "backend/auth/token.py"), ("auth", "app/login.py"),
                                  ("billing", "backend/billing.py"),
                                  ("rules", "firebase/firestore.rules"),
                                  ("answers", "backend/agents/specialist/faa.py"),
                                  ("ci", ".github/workflows/pr-check.yml")):
                rc, lines = run(repo, "--paths", "docs/readme.md", path)
                hit = [ln for ln in lines if ln.startswith(path)]
                c.check(f"RED · {path} overlaps `{surface}`: OVERLAP on line 1, exit 3",
                        first(lines) == "OVERLAP" and rc == 3, f"rc={rc} line1={first(lines)!r}")
                c.check("   ...and the overlap line carries the surface and its why",
                        len(hit) == 1 and f"{surface}:" in hit[0] and
                        (path != "backend/billing.py" or "revenue" in hit[0]),
                        str(hit))
            rc, lines = run(repo, "--paths", "docs/readme.md", "_artifacts/x/walkthrough.md",
                            "frontend/src/components/Button.tsx")
            c.check("CLEAR · docs, artifacts and an ordinary component: CLEAR on line 1, exit 0",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} lines={lines}")
            c.check("   ...and no MAP: none line when the repo carries a map",
                    first(lines) == "CLEAR" and not any(ln.startswith("MAP:") for ln in lines),
                    str(lines))
            # The generic set is NOT consulted when a map exists: `auth` as a fragment is
            # generic, but this map lists only backend/auth/ and app/login.py.
            rc, lines = run(repo, "--paths", "frontend/auth/theme.css")
            c.check("a repo map WINS: a generic fragment hit outside the map is CLEAR",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} lines={lines}")
            # ⛔ AND THE SAME PATH MUST OVERLAP WHERE NO MAP EXISTS, or the case above proves
            # only that something printed CLEAR (SCC-446 review). The pair is the claim: the
            # generic `auth` fragment is live, and the map is what suppressed it.
            with TempDir() as t2:
                bare = t2 / "unmapped"
                bare.mkdir()
                rc2, lines2 = run(bare, "--paths", "frontend/auth/theme.css")
            c.check("   ...and the SAME path is OVERLAP in an unmapped repo - the map suppressed "
                    "a live fragment, it did not merely fail to match",
                    first(lines2) == "OVERLAP" and rc2 == 3, f"rc={rc2} lines={lines2}")
            # A trailing slash is a prefix; anything else is exact.
            rc, lines = run(repo, "--paths", "backend/billing.py.bak", "backend/auth-notes/x.md")
            c.check("exact means exact: `backend/billing.py.bak` is not `backend/billing.py`, "
                    "`backend/auth-notes/` is not `backend/auth/`",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} lines={lines}")

    if c.block("C · no map: the generic set, and it is LOUD"):
        with TempDir() as t:
            repo = t / "repo"
            repo.mkdir()
            rc, lines = run(repo, "--paths", ".github/workflows/x.yml", "docs/guide.md")
            c.check("missing map: `MAP: none` is printed and `.github/x.yml` still overlaps",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("MAP: none") for ln in lines), f"rc={rc} {lines}")
            for path, why in (("backend/auth/x.py", "auth"), ("src/auth_service.py", "auth"),
                              ("lib/session.ts", "auth"), ("api/billing-routes.py", "billing"),
                              ("api/payment.py", "billing"), ("api/entitlement/x.py", "billing"),
                              ("firebase/firestore.rules", "rules"), ("firebase.json", "rules"),
                              (".agents/hooks/x.py", "ci"), (".agents/scripts/git-hooks/x.sh", "ci")):
                rc, lines = run(repo, "--paths", path)
                c.check(f"generic · {path} overlaps `{why}`",
                        first(lines) == "OVERLAP" and rc == 3
                        and any(ln.startswith(path) and f"{why}:" in ln for ln in lines),
                        f"rc={rc} {lines}")
            for path in ("docs/author-guide.md", "backend/authors.py", "src/sessions-history.md",
                         "backend-notes/x.md", "docs/paymentless.md", "README.md"):
                rc, lines = run(repo, "--paths", path)
                c.check(f"⛔ a SUBSTRING is not a hit: {path} is CLEAR",
                        first(lines) == "CLEAR" and rc == 0, f"rc={rc} {lines}")

    if c.block("D · silence and breakage are ERRORS, never CLEAR"):
        with TempDir() as t:
            repo = t / "repo"
            repo.mkdir()
            # ⛔ `ERROR` on line 1, not merely "not CLEAR": a MISSING script also exits 2, and
            # the first cut of these three cases passed with no script on disk at all.
            rc, lines = run(repo, "--paths")
            c.check("empty --paths exits 2 and line 1 is the word ERROR",
                    rc == 2 and first(lines) == "ERROR", f"rc={rc} {lines}")
            (repo / ".agents").mkdir()
            (repo / ".agents" / "critical-surfaces.json").write_text("{not json", encoding="utf-8")
            rc, lines = run(repo, "--paths", "docs/x.md")
            c.check("a map that does not parse exits 2 with ERROR on line 1, never CLEAR",
                    rc == 2 and first(lines) == "ERROR", f"rc={rc} {lines}")
            # ⛔ A WRONG-SHAPE MAP IS AN ERROR, NOT AN EMPTY ONE. Each of these parses as JSON
            # and would otherwise reach `rows == []`, which now falls back to the generic set —
            # so without these rows a malformed map is indistinguishable from a deliberate
            # "nothing applies here", and the author's mistake reads as a decision.
            for label, blob in (
                    ("a top-level list, no `surfaces` object", "[]"),
                    ("`surfaces` is a string, not an object", '{"surfaces": "all of them"}'),
                    ("a surface with no `paths` key", '{"surfaces": {"ci": {"why": "x"}}}'),
                    ("`paths` is a string, not a list", '{"surfaces": {"ci": {"paths": ".github/"}}}'),
                    ("a null path entry - `str(None)` is the dead pattern \"None\"",
                     '{"surfaces": {"ci": {"paths": [null]}}}'),
                    ("an empty-string path entry - it would match nothing and read as protection",
                     '{"surfaces": {"ci": {"paths": ["  "]}}}')):
                (repo / ".agents" / "critical-surfaces.json").write_text(blob, encoding="utf-8")
                rc, lines = run(repo, "--paths", "docs/x.md")
                c.check(f"wrong-shape map · {label}: exit 2, line 1 is ERROR",
                        rc == 2 and first(lines) == "ERROR", f"rc={rc} {lines}")
                c.check("   ...and line 2 names the map so the author can find it",
                        len(lines) > 1 and ".agents/critical-surfaces.json" in lines[1],
                        str(lines))
            (repo / ".agents" / "critical-surfaces.json").unlink()
            # ⛔ AN EMPTY `--repo` IS THE CWD, AND THE CWD IS THE LOBBY (SCC-446 review,
            # reproduced). `cd ""` exits 0 without moving, so an unbound `$REPO` arrives as ""
            # and `Path("").resolve()` is a real git repo: every check passes and the script
            # answers confidently about the wrong tree.
            rc, out = run_script("scope_check.py", "--repo", "", "--paths", "backend/auth/x.py")
            elines = out.splitlines()
            c.check("⛔ an EMPTY --repo is refused: exit 2, line 1 is ERROR",
                    rc == 2 and first(elines) == "ERROR", f"rc={rc} {elines}")
            c.check("   ...and the reason names the unbound variable, not just 'bad input'",
                    any("empty" in ln.lower() and "cwd" in ln.lower() for ln in elines[1:]),
                    str(elines))
            rc, out = run_script("scope_check.py", "--paths", "docs/x.md")
            c.check("--repo is required, and the refusal names it (a MISSING script also exits 2)",
                    rc == 2 and "--repo" in out, f"rc={rc} {out[:200]!r}")
            src = SCRIPT.read_text(encoding="utf-8") if SCRIPT.exists() else ""
            c.check("the script never prompts (no input( call) and never writes (no write_text/open(..., 'w'))",
                    bool(src) and "input(" not in src and "write_text" not in src
                    and re.search(r"open\([^)]*['\"]w", src) is None, "it reads and prints")
            c.check("the script has no override flag - the only override is the operator's quoted word",
                    bool(src) and "override" not in src.lower().replace("no override", "")
                    .replace("no agent override", ""), "grep -c override")

    if c.block("E · --diff reads the MERGE-BASE diff of the real branch"):
        with TempDir() as t:
            repo = pf.make_repo(t)
            pf.branch(repo, "chore/SCC-11-ci", {".github/workflows/x.yml": "name: x\n"})
            rc, lines = run(repo, "--diff", "main")
            c.check("a branch that touched .github/ reports OVERLAP against --diff main",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith(".github/workflows/x.yml") for ln in lines),
                    f"rc={rc} {lines}")
            c.check("   ...and says how many files it compared (DIFF: n file(s) vs main)",
                    any(re.match(r"DIFF: 1 file\(s\) vs main", ln) for ln in lines), str(lines))
            pf.git(repo, "checkout", "-q", "main")
            pf.branch(repo, "chore/SCC-11-docs", {"docs/x.md": "hi\n"})
            rc, lines = run(repo, "--diff", "main")
            c.check("a branch that touched only docs/ is CLEAR against --diff main",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} {lines}")
            rc, lines = run(repo, "--diff", "no-such-ref")
            c.check("a --diff base git cannot resolve exits 2 with ERROR on line 1, never CLEAR",
                    rc == 2 and first(lines) == "ERROR", f"rc={rc} {lines}")

    if c.block("F · a map that declares NOTHING is treated as no map, and says which"):
        # ⛔ The skeleton ships a placeholder with all five surfaces empty, and the rule
        # sanctions an empty `paths` per surface. A map matching nothing while ALSO suppressing
        # the generic fallback is strictly weaker than having no file at all — it would print a
        # bare CLEAR where an unmapped repo prints `MAP: none` and still checks the generic set.
        with TempDir() as t:
            repo = t / "repo"
            write_map(repo, {s: {"why": f"{s} does not apply here", "paths": []} for s in FIVE})
            rc, lines = run(repo, "--paths", "backend/auth/token.py")
            c.check("all-empty map: the generic set still fires - OVERLAP, exit 3",
                    first(lines) == "OVERLAP" and rc == 3, f"rc={rc} {lines}")
            c.check("   ...and the MAP: line says DECLARES NO PATHS, not `none` - the two "
                    "situations are different and the author needs to know which one this is",
                    any(ln.startswith("MAP: ") and "declares no paths" in ln for ln in lines),
                    str(lines))
            rc, lines = run(repo, "--paths", "docs/readme.md")
            c.check("...and an ordinary docs path is still CLEAR under the fallback",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} {lines}")
            # One surface with a path is a real map: no fallback, no MAP: line.
            write_map(repo, {**{s: {"why": "n/a", "paths": []} for s in FIVE},
                             "ci": {"why": "the gates", "paths": [".github/"]}})
            rc, lines = run(repo, "--paths", "backend/auth/token.py")
            c.check("⛔ ONE declared path is a real map: the generic `auth` fragment is OFF again",
                    first(lines) == "CLEAR" and rc == 0 and not any(ln.startswith("MAP:") for ln in lines),
                    f"rc={rc} {lines}")

    if c.block("G · the doors actually call it - Step 1 on the plan, the tripwire on the diff"):
        # A checker nothing invokes is a checker that never fires. Both quick lanes must carry
        # BOTH calls: `--paths` at Step 1 (the planned set) and `--diff` at the eject tripwire
        # (the real branch), because an under-declared Step 1 is caught only by the diff.
        for door in ("smh-quick-dev.md", "cicd-quick-dev.md"):
            body = (ROOT / ".agents" / "commands" / door).read_text(encoding="utf-8")
            c.check(f"{door} calls scope_check.py with --paths (Step 1, the planned set)",
                    re.search(r"scope_check\.py[^\n]*--paths", body) is not None, door)
            c.check(f"{door} calls scope_check.py with --diff (the eject tripwire, the real branch)",
                    re.search(r"scope_check\.py[^\n]*--diff", body) is not None, door)
            calls = [ln.strip() for ln in body.splitlines()
                     if "scope_check.py" in ln and "--" in ln]
            c.check(f"{door} passes an explicit --repo on every call (never the cwd)",
                    bool(calls) and all(re.search(r'--repo\s+"?\S', ln) for ln in calls), calls)

    if c.block("H · registered where the house looks"):
        sidx = (ROOT / ".agents" / "scripts" / "INDEX.md").read_text(encoding="utf-8")
        ridx = (ROOT / ".agents" / "rules" / "INDEX.md").read_text(encoding="utf-8")
        c.check(".agents/scripts/INDEX.md carries a row for scope_check.py",
                "`scope_check.py`" in sidx, "test_shape_scan.py precedent")
        c.check(".agents/rules/INDEX.md carries an on-demand row for critical-surfaces.md",
                "`critical-surfaces.md`" in ridx, "test_rule_frontmatter.py requires it")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
