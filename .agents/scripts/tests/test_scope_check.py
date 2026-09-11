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
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, run_script
import _pf_fixtures as pf
import scope_check as sc          # noqa: E402

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


def run_from(cwd: Path, repo: Path, *args: str) -> tuple[int, list[str]]:
    """The same call, launched with a CHOSEN cwd - the doors run Step 1 from the lobby."""
    r = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo), *args],
                       cwd=str(cwd), capture_output=True, text=True, errors="replace")
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).splitlines()


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
        # ⛔ THE FIVE BARE-RUN GATE SCRIPTS WERE OFF THE LINE (SCC-441 review row 7, reproduced).
        # The lobby's Step 3 floor runs workflow_lint, check_links and check_maps bare, the
        # sweep is what proves a test can fail, and epic_mode routes every door's Step 0 - all
        # five answered CLEAR, so a quick lane could edit the linter and then report its green.
        # Run against the REAL lobby map: the worktree root is the repo.
        for name in ("workflow_lint.py", "check_links.py", "check_maps.py",
                     "mutation_sweep.py", "epic_mode.py"):
            rc, lines = run(ROOT, "--paths", f".agents/scripts/{name}")
            c.check(f"SCC-441 row 7 · the real lobby map: .agents/scripts/{name} is OVERLAP under `ci`",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith(f".agents/scripts/{name}") and "ci:" in ln for ln in lines),
                    f"rc={rc} {lines}")

    if c.block("B · the check reads a repo map: one RED per surface, then CLEAR"):
        with TempDir() as t:
            repo = t / "repo"
            # The three exact-file rows below name REAL files: an exact row that names nothing
            # is a dead row and an ERROR since review 2 (rows 7/15), so the fixture carries them.
            for rel in ("app/login.py", "backend/billing.py", "firebase/firestore.rules"):
                (repo / rel).parent.mkdir(parents=True, exist_ok=True)
                (repo / rel).write_text("# fixture\n", encoding="utf-8")
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
            # ⛔ AN ABSOLUTE PATH DEFEATED A MAPPED REPO'S CHECK (SCC-441 review row 3, reproduced).
            # `--repo` is absolute by contract, so the same command line silently required the
            # others to be relative: `<repo>/app/login.py` was compared to `app/login.py` as a
            # string and printed CLEAR - the pass word - exactly where the map is the authority.
            rc, lines = run(repo, "--paths", str(repo / "app" / "login.py"))
            c.check("SCC-441 row 3 · an ABSOLUTE path inside the repo is rebased and judged: OVERLAP "
                    "on the repo-relative line",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("app/login.py") for ln in lines), f"rc={rc} lines={lines}")
            outside = str(t / "elsewhere" / "login.py")
            rc, lines = run(repo, "--paths", outside)
            c.check("SCC-441 row 3 · an absolute path OUTSIDE the repo is ERROR, exit 2, and line 2 "
                    "names which path",
                    first(lines) == "ERROR" and rc == 2 and len(lines) > 1 and outside in lines[1],
                    f"rc={rc} lines={lines}")

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
            # ⛔ THE GENERIC SET DID NOT PROTECT THE LINE ITSELF (SCC-441 review row 21,
            # reproduced). In an unmapped repo - today every project - a quick lane could write
            # the repo's first map, edit this script or rewrite the rule without tripping the
            # line. The lobby's map row says why ("a line that can widen itself is not a line");
            # a map row cannot say it where there is no map.
            for path in (".agents/critical-surfaces.json", ".agents/scripts/scope_check.py",
                         ".agents/rules/critical-surfaces.md"):
                rc, lines = run(repo, "--paths", path)
                c.check(f"SCC-441 row 21 · generic · {path} overlaps `ci` (an exact file)",
                        first(lines) == "OVERLAP" and rc == 3
                        and any(ln.startswith(path) and "ci:" in ln for ln in lines),
                        f"rc={rc} {lines}")

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
            # ⛔ A BARE WORD IN A REPO'S OWN MAP WAS A SILENTLY DEAD PATTERN (SCC-441 review
            # row 6, reproduced). With fragments off it fell to `path == pattern`, so
            # `"paths": ["auth"]` matched only a root file literally named `auth` and answered
            # CLEAR for `backend/auth/token.py` - the likeliest authoring mistake, because the
            # rule publishes `auth`/`session`/`billing` as the generic fragment list one page
            # above the map format, and the exact class the `null`-entry guard above refuses.
            write_map(repo, {"auth": {"why": "accounts", "paths": ["auth"]}})
            rc, lines = run(repo, "--paths", "backend/auth/token.py")
            c.check("SCC-441 row 6 · a bare word naming NO root file is ERROR, exit 2 - never a "
                    "quiet CLEAR", rc == 2 and first(lines) == "ERROR", f"rc={rc} {lines}")
            c.check("   ...and line 2 names the entry and both remedies (a trailing `/` for a "
                    "directory; the generic set for a fragment)",
                    len(lines) > 1 and "`auth`" in lines[1] and "trailing `/`" in lines[1]
                    and "generic set" in lines[1], str(lines))
            (repo / "auth").mkdir()
            rc, lines = run(repo, "--paths", "auth/token.py")
            c.check("SCC-441 row 6 · a bare word naming a root DIRECTORY is the same ERROR (it "
                    "wanted `auth/`)", rc == 2 and first(lines) == "ERROR", f"rc={rc} {lines}")
            (repo / "auth").rmdir()
            (repo / "auth").write_text("#!/bin/sh\n", encoding="utf-8")
            (repo / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
            write_map(repo, {"auth": {"why": "accounts", "paths": ["auth"]},
                             "ci": {"why": "the image", "paths": ["Dockerfile"]}})
            rc, lines = run(repo, "--paths", "auth")
            c.check("SCC-441 row 6 · a bare word naming an EXISTING root file stays legal and "
                    "matches it exactly: `auth` is OVERLAP",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("auth ") for ln in lines), f"rc={rc} {lines}")
            rc, lines = run(repo, "--paths", "Dockerfile")
            c.check("   ...and a `Dockerfile`-style root file is exactly that case: OVERLAP",
                    first(lines) == "OVERLAP" and rc == 3, f"rc={rc} {lines}")
            # ⛔ THE `fragments and` GUARD WAS DEAD TO THIS FILE (SCC-441 review row 18,
            # reproduced): every map path in block B carries a `/` or a `.`, so no case ever
            # reached the branch and dropping the guard survived 80/80. A declared root file is
            # exact, never a segment fragment - `backend/auth/token.py` must stay CLEAR.
            rc, lines = run(repo, "--paths", "backend/auth/token.py", "backend/Dockerfile")
            c.check("SCC-441 row 18 · a declared root file is EXACT, never a segment fragment: "
                    "`backend/auth/token.py` and `backend/Dockerfile` are CLEAR",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} {lines}")
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
            # §5 nitpick (SCC-441 review): only `""` was ever tested, so `.strip()` was dead.
            rc, out = run_script("scope_check.py", "--repo", "  ", "--paths", "backend/auth/x.py")
            elines = out.splitlines()
            c.check("SCC-441 §5 nitpick · a WHITESPACE-only --repo is refused the same way: exit 2, "
                    "line 1 is ERROR", rc == 2 and first(elines) == "ERROR", f"rc={rc} {elines}")
            rc, out = run_script("scope_check.py", "--paths", "docs/x.md")
            c.check("--repo is required, and the refusal names it (a MISSING script also exits 2)",
                    rc == 2 and "--repo" in out, f"rc={rc} {out[:200]!r}")
            src = SCRIPT.read_text(encoding="utf-8") if SCRIPT.exists() else ""
            c.check("the script never prompts (no input( call) and never writes (no write_text/open(..., 'w'))",
                    bool(src) and "input(" not in src and "write_text" not in src
                    and re.search(r"open\([^)]*['\"]w", src) is None, "it reads and prints")
            # ⛔ THE NO-BYPASS CLAIM WAS A SOURCE GREP FOR ONE WORD (SCC-441 review row 4,
            # reproduced): a real `--force` flag and a `SCOPE_CHECK_SKIP` env check both printed
            # CLEAR and left this file 80/80. Three behavioural pins replace it - the parser's
            # option set is exactly the four, each named bypass flag is refused by argparse with
            # no verdict word on line 1, and the source reads no environment at all.
            rc, out = run_script("scope_check.py", "--help")
            opts = re.split(r"^(?:options|optional arguments):", out, maxsplit=1, flags=re.M)[-1]
            flags = set(re.findall(r"^  (-{1,2}[\w-]+)", opts, re.M))
            c.check("SCC-441 row 4 · the parser's option set is exactly {-h, --repo, --paths, --diff}",
                    rc == 0 and flags == {"-h", "--repo", "--paths", "--diff"},
                    f"rc={rc} flags={sorted(flags)}")
            for flag in ("--force", "--yes", "--skip", "--no-check"):
                rc, out = run_script("scope_check.py", "--repo", str(repo), "--paths",
                                     "backend/auth/x.py", flag)
                flines = out.splitlines()
                c.check(f"SCC-441 row 4 · `{flag}` is refused by argparse: exit 2, no verdict word "
                        "on line 1",
                        rc == 2 and first(flines) not in ("CLEAR", "OVERLAP") and "unrecognized" in out,
                        f"rc={rc} line1={first(flines)!r}")
            c.check("SCC-441 row 4 · the source never reads the environment (no os.environ, no getenv)",
                    bool(src) and "os.environ" not in src and "getenv" not in src, "grep -c environ")

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
            # ⛔ THE MERGE-BASE IS THE WHOLE POINT OF --diff AND NO CASE TOLD IT FROM THE TWO-DOT
            # DIFF (SCC-441 review row 5, reproduced): this block never moved `main` after the
            # fork, so the two spellings were identical here and the mutant survived 80/80.
            # `main` moving under a lane is the house's normal state, and the two-dot diff makes
            # the eject tripwire fire on a `.github/` file the lane never touched.
            pf.git(repo, "checkout", "-q", "main")
            pf.write(repo, ".github/workflows/ci.yml", "name: ci\n")
            pf.commit(repo, "SCC-11 ci: main moves under the lane")
            pf.git(repo, "checkout", "-q", "chore/SCC-11-docs")
            rc, lines = run(repo, "--diff", "main")
            c.check("SCC-441 row 5 · main landed .github/ AFTER the fork: the docs lane is still "
                    "CLEAR (the merge-base diff, never the two-dot one)",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} {lines}")
            c.check("   ...and it compared exactly the lane's ONE file (DIFF: 1 file(s) vs main)",
                    any(re.match(r"DIFF: 1 file\(s\) vs main", ln) for ln in lines), str(lines))
            # ⛔ ZERO CHANGED FILES PRINTED THE PASS WORD (SCC-441 review row 20, reproduced).
            # The `--paths` arm refuses empty as UNKNOWN scope; this arm sat in the other branch
            # of the same `if` and said `CLEAR` over `DIFF: 0` - reachable on uncommitted-only
            # work, or a --repo standing on the base itself.
            pf.git(repo, "checkout", "-q", "main")
            rc, lines = run(repo, "--diff", "main")
            c.check("SCC-441 row 20 · --diff with ZERO changed files is ERROR, exit 2 - never CLEAR",
                    first(lines) == "ERROR" and rc == 2, f"rc={rc} {lines}")
            c.check("   ...and the reason says the lane has no committed diff vs the base",
                    any("no committed diff" in ln and "main" in ln for ln in lines[1:]), str(lines))
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

    if c.block("SCC-441 review-2 row 14 · --diff judges against the BASE's map too"):
        # ⛔ `--diff` read the map from the LANE's tree, so a lane that pruned the map's self
        # rows (or wrote a repo's first one-row map) judged its real diff against a map it had
        # just written and read CLEAR (reproduced C1/C3). The line's self-protection was a row
        # the lane could delete. Now the map as it stood at the merge-base is read too and the
        # diff is judged against the UNION: base rows ∪ HEAD rows, or - where the base had no
        # map - the generic set ∪ HEAD rows. A `MAP:` line says which.
        SELF = [".agents/critical-surfaces.json", ".agents/scripts/scope_check.py",
                ".agents/rules/critical-surfaces.md"]
        with TempDir() as t:
            repo = pf.make_repo(t)
            write_map(repo, {"ci": {"why": "the gates", "paths": [".github/", "gates/", *SELF]}})
            pf.write(repo, "gates/x.sh", "exit 0\n")
            pf.commit(repo, "SCC-11 chore: the map and a gate, on main")
            pf.git(repo, "push", "-q", "origin", "main")
            fork = pf.git(repo, "rev-parse", "HEAD").stdout.strip()
            pf.branch(repo, "chore/SCC-11-prune", {
                ".agents/critical-surfaces.json":
                    json.dumps({"surfaces": {"ci": {"why": "the gates", "paths": [".github/"]}}}),
                "gates/x.sh": "exit 1\n"})
            rc, lines = run(repo, "--diff", "main")
            c.check("SCC-441 review-2 row 14 · C1: the lane pruned the map's self rows and `gates/` "
                    "and edited gates/x.sh - OVERLAP under `ci` on the BASE's rows, exit 3",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("gates/x.sh") and "ci:" in ln for ln in lines)
                    and any(ln.startswith(".agents/critical-surfaces.json") and "ci:" in ln
                            for ln in lines), f"rc={rc} {lines}")
            c.check("   ...and the MAP: line names both maps used (base <fork-8> + HEAD)",
                    any(ln.startswith("MAP:") and f"base {fork[:8]}" in ln and "HEAD" in ln
                        for ln in lines), str(lines))
            c.check("   ...one overlap line per path still (two paths, two lines)",
                    sum(1 for ln in lines if "  ci:" in ln) == 2, str(lines))
        with TempDir() as t:
            repo = pf.make_repo(t)
            fork = pf.git(repo, "rev-parse", "HEAD").stdout.strip()
            pf.branch(repo, "chore/SCC-11-first-map", {
                ".agents/critical-surfaces.json":
                    json.dumps({"surfaces": {"ci": {"why": "the gates", "paths": [".github/"]}}})})
            rc, lines = run(repo, "--diff", "main")
            c.check("SCC-441 review-2 row 14 · an UNMAPPED base: the lane's first one-row map is "
                    "judged against the generic set - the map file itself is OVERLAP under `ci`",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith(".agents/critical-surfaces.json") and "ci:" in ln
                            for ln in lines), f"rc={rc} {lines}")
            c.check("   ...and the MAP: line says none at base <fork-8>, generic surfaces + HEAD map",
                    any(ln.startswith("MAP:") and f"none at base {fork[:8]}" in ln
                        and "generic" in ln and "HEAD" in ln for ln in lines), str(lines))
        with TempDir() as t:
            # CONTROL: a lane that only ADDS rows is still judged - on the base's rows AND its own.
            repo = pf.make_repo(t)
            write_map(repo, {"ci": {"why": "the gates", "paths": [".github/", "gates/"]}})
            pf.write(repo, "gates/x.sh", "exit 0\n")
            pf.commit(repo, "SCC-11 chore: the map and a gate, on main")
            pf.git(repo, "push", "-q", "origin", "main")
            pf.branch(repo, "chore/SCC-11-adds", {
                ".agents/critical-surfaces.json":
                    json.dumps({"surfaces": {"ci": {"why": "the gates", "paths": [".github/", "gates/"]},
                                             "auth": {"why": "accounts", "paths": ["backend/auth/"]}}}),
                "gates/x.sh": "exit 1\n",
                "backend/auth/token.py": "x = 1\n"})
            rc, lines = run(repo, "--diff", "main")
            c.check("SCC-441 review-2 row 14 · CONTROL: a lane that only ADDS a row is judged on the "
                    "base's row (gates/x.sh under ci) AND its own new row (backend/auth/ under auth)",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("gates/x.sh") and "ci:" in ln for ln in lines)
                    and any(ln.startswith("backend/auth/token.py") and "auth:" in ln for ln in lines),
                    f"rc={rc} {lines}")

    if c.block("SCC-441 review-2 rows 7/15 · a row that can never match is an ERROR, not a guard"):
        # ⛔ A directory declared without its `/`, a leading-`/` path and a typo'd exact file
        # were all stored as exact patterns that no real path equals - silently dead rows the
        # author believes are protecting something (reproduced A1-A3, all CLEAR). ONE rule for
        # every non-prefix, non-`*.` pattern: it names a real file (a symlink counts), or it is
        # gitignored (the lobby's own `.claude/settings.local.json` is absent in a fresh clone).
        with TempDir() as t:
            repo = t / "repo"
            repo.mkdir()
            pf.git(repo, "init", "-q", "-b", "main")
            (repo / ".gitignore").write_text(".claude/settings.local.json\n", encoding="utf-8")
            (repo / "backend" / "auth").mkdir(parents=True)
            (repo / "backend" / "auth" / "token.py").write_text("x = 1\n", encoding="utf-8")
            for label, pat, needle in (
                    ("a DIRECTORY without its trailing slash", "backend/auth", "trailing `/`"),
                    ("a LEADING slash", "/backend/auth/", "leading /"),
                    ("a typo'd exact file", "backend/auth/tokn.py", "names no file")):
                write_map(repo, {"auth": {"why": "accounts", "paths": [pat]}})
                rc, lines = run(repo, "--paths", "backend/auth/token.py")
                c.check(f"SCC-441 review-2 rows 7/15 · {label} (`{pat}`) is ERROR, exit 2 - never a "
                        f"quiet CLEAR over `backend/auth/token.py`",
                        rc == 2 and first(lines) == "ERROR", f"rc={rc} {lines}")
                c.check(f"   ...and line 2 names the entry and the remedy ({needle})",
                        len(lines) > 1 and f"`{pat}`" in lines[1] and needle in lines[1], str(lines))
            write_map(repo, {"ci": {"why": "the fence", "paths": [".claude/settings.local.json"]}})
            rc, lines = run(repo, "--paths", "docs/x.md")
            c.check("SCC-441 review-2 rows 7/15 · a GITIGNORED file that is absent (the lobby's "
                    "per-machine settings in a fresh clone) is accepted: CLEAR on an unrelated path",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} {lines}")
            rc, lines = run(repo, "--paths", ".claude/settings.local.json")
            c.check("   ...and it still MATCHES: the gitignored row is live, not skipped",
                    first(lines) == "OVERLAP" and rc == 3, f"rc={rc} {lines}")
            write_map(repo, {"auth": {"why": "accounts", "paths": ["backend/auth/token.py"]}})
            rc, lines = run(repo, "--paths", "backend/auth/token.py")
            c.check("SCC-441 review-2 rows 7/15 · an exact row naming an EXISTING file is accepted "
                    "and matches",
                    first(lines) == "OVERLAP" and rc == 3, f"rc={rc} {lines}")
            (repo / "backend" / "auth" / "link.py").symlink_to("token.py")
            write_map(repo, {"auth": {"why": "accounts", "paths": ["backend/auth/link.py"]}})
            rc, lines = run(repo, "--paths", "docs/x.md")
            c.check("SCC-441 review-2 rows 7/15 · a SYMLINK counts as a file (lexists, not exists)",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} {lines}")

    if c.block("SCC-441 review-2 row 16 · a lobby-relative or ..-relative path is rebased, or "
               "refused - never compared as a string"):
        # ⛔ Only ABSOLUTE paths were rebased (row 3). The doors run Step 1 from the lobby with
        # `--repo "$PROJECT_ROOT"`, and a lobby session spells the file the way `git status`
        # there does: `Projects/X/backend/auth.py`. Compared as a string to the map's
        # `backend/auth.py` it answered CLEAR (reproduced B1); so did `../../../backend/auth.py`
        # from inside a worktree dir (B4). A path that exists under the cwd and resolves INSIDE
        # the repo is rebased; outside is an ERROR; a `..` path nothing resolves cannot be judged.
        with TempDir() as t:
            lobby = t / "lobby"
            proj = lobby / "Projects" / "X"
            proj.mkdir(parents=True)
            (lobby / "README.md").write_text("# the lobby\n", encoding="utf-8")
            (proj / "backend").mkdir()
            (proj / "backend" / "auth.py").write_text("x = 1\n", encoding="utf-8")
            write_map(proj, {"auth": {"why": "accounts", "paths": ["backend/auth.py", "backend/auth/"]}})
            rc, lines = run_from(lobby, proj, "--paths", "Projects/X/backend/auth.py")
            c.check("SCC-441 review-2 row 16 · B1: from the lobby, `Projects/X/backend/auth.py` is "
                    "rebased onto the repo and judged: OVERLAP on the repo-relative line",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("backend/auth.py") for ln in lines), f"rc={rc} {lines}")
            rc, lines = run_from(lobby, proj, "--paths", "backend/auth.py")
            c.check("SCC-441 review-2 row 16 · B2 CONTROL: a repo-relative path from the lobby cwd "
                    "is still judged as repo-relative", first(lines) == "OVERLAP" and rc == 3,
                    f"rc={rc} {lines}")
            wtdir = proj / ".claude" / "worktrees" / "slug"
            wtdir.mkdir(parents=True)
            rc, lines = run_from(wtdir, proj, "--paths", "../../../backend/auth.py")
            c.check("SCC-441 review-2 row 16 · B4: a `..`-relative path that resolves INSIDE the "
                    "repo is rebased and judged: OVERLAP",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("backend/auth.py") for ln in lines), f"rc={rc} {lines}")
            rc, lines = run_from(wtdir, proj, "--paths", "../../../../../README.md")
            c.check("SCC-441 review-2 row 16 · a `..` path that resolves OUTSIDE the repo (the "
                    "lobby's README from a worktree dir) is ERROR, exit 2, naming the repo",
                    rc == 2 and first(lines) == "ERROR" and any("outside" in ln for ln in lines[1:]),
                    f"rc={rc} {lines}")
            rc, lines = run_from(lobby, proj, "--paths", "README.md")
            c.check("SCC-441 review-2 row 16 · CONTROL: `README.md` from the lobby, absent in the "
                    "project, is a planned NEW repo-relative file - judged, never an ERROR (the "
                    "lobby's own README of that name is not it)",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} {lines}")
            rc, lines = run_from(lobby, proj, "--paths", "../nowhere/auth.py")
            c.check("SCC-441 review-2 row 16 · a `..` path nothing resolves cannot be judged: "
                    "ERROR, exit 2",
                    rc == 2 and first(lines) == "ERROR"
                    and any("cannot be judged" in ln for ln in lines[1:]), f"rc={rc} {lines}")
            rc, lines = run_from(lobby, proj, "--paths", "backend/auth/new_token.py", "docs/new.md")
            c.check("SCC-441 review-2 row 16 · a planned NEW file typed repo-relative is still judged "
                    "(nothing exists yet, so it stays repo-relative): OVERLAP under auth",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("backend/auth/new_token.py") for ln in lines),
                    f"rc={rc} {lines}")

    if c.block("SCC-441 review-2 row 17 · a planned DIRECTORY is a planned prefix"):
        # ⛔ `backend/` and `.` were compared as strings: `"backend/".startswith("backend/auth/")`
        # is False, so a plan declared at directory granularity was CLEAR over a critical child
        # and the lane found out at Step 5, after the build (reproduced D1/D2). A directory
        # overlaps a prefix row when either starts with the other, an exact row the row starts
        # with, a generic fragment `segment_hit` fires on; `.` is the whole repo.
        with TempDir() as t:
            repo = t / "repo"
            (repo / "backend" / "auth").mkdir(parents=True)
            (repo / "backend" / "auth" / "t.py").write_text("x\n", encoding="utf-8")
            (repo / "docs").mkdir()
            (repo / "docs" / "readme.md").write_text("x\n", encoding="utf-8")
            write_map(repo, {"auth": {"why": "accounts", "paths": ["backend/auth/", "app/login.py"]}})
            (repo / "app").mkdir()
            (repo / "app" / "login.py").write_text("x\n", encoding="utf-8")
            rc, lines = run(repo, "--paths", "backend/")
            c.check("SCC-441 review-2 row 17 · D1: `backend/` over the critical child `backend/auth/` "
                    "is OVERLAP, exit 3, printed as `backend/  auth: ...`",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("backend/  auth:") for ln in lines), f"rc={rc} {lines}")
            rc, lines = run(repo, "--paths", ".")
            c.check("SCC-441 review-2 row 17 · D2: `.` is the whole repo and overlaps the first row",
                    first(lines) == "OVERLAP" and rc == 3, f"rc={rc} {lines}")
            rc, lines = run(repo, "--paths", "docs/")
            c.check("SCC-441 review-2 row 17 · a directory with NO critical child (`docs/`) is CLEAR",
                    first(lines) == "CLEAR" and rc == 0, f"rc={rc} {lines}")
            rc, lines = run(repo, "--paths", "backend")
            c.check("SCC-441 review-2 row 17 · an EXISTING directory named without its slash "
                    "(`backend`) is normalised to a prefix: OVERLAP",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("backend/  auth:") for ln in lines), f"rc={rc} {lines}")
            rc, lines = run(repo, "--paths", "app/")
            c.check("SCC-441 review-2 row 17 · a directory over an EXACT row (`app/` over "
                    "`app/login.py`) is OVERLAP",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("app/  auth:") for ln in lines), f"rc={rc} {lines}")
        with TempDir() as t:
            repo = t / "unmapped"
            (repo / "src" / "auth").mkdir(parents=True)
            rc, lines = run(repo, "--paths", "src/auth/")
            c.check("SCC-441 review-2 row 17 · in an UNMAPPED repo a directory whose segment is a "
                    "generic fragment (`src/auth/`) is OVERLAP",
                    first(lines) == "OVERLAP" and rc == 3, f"rc={rc} {lines}")
            rc, lines = run(repo, "--paths", "src/")
            c.check("SCC-441 review-2 row 17 · ...and `src/` alone stays CLEAR (a prefix cannot see "
                    "into the files it will hold)", first(lines) == "CLEAR" and rc == 0,
                    f"rc={rc} {lines}")

    if c.block("SCC-441 review-2 rows 31/32 · the empty string and the PC spellings"):
        # Row 31: `--paths ""` is what a quoted, unset shell variable becomes. The guard existed
        # (`if not p: continue`) and no case pinned it - `continue` → `pass` survived 106/106.
        with TempDir() as t:
            repo = t / "repo"
            (repo / "backend" / "auth").mkdir(parents=True)
            write_map(repo, {"auth": {"why": "accounts", "paths": ["backend/auth/"]},
                             "ci": {"why": "the gates", "paths": [".github/"]}})
            rc, lines = run(repo, "--paths", "")
            c.check("SCC-441 review-2 row 31 · `--paths \"\"` (an unset variable) is ERROR, exit 2",
                    rc == 2 and first(lines) == "ERROR", f"rc={rc} {lines}")
            rc, lines = run(repo, "--paths", "", "backend/auth/x.py")
            c.check("SCC-441 review-2 row 31 · `--paths \"\" backend/auth/x.py` drops the empty entry "
                    "and judges the rest: OVERLAP",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith("backend/auth/x.py") for ln in lines), f"rc={rc} {lines}")
            # Row 32: the PC spelling and the `./` spelling both reach the `.github/` prefix.
            rc, lines = run(repo, "--paths", ".github\\workflows\\x.yml")
            c.check("SCC-441 review-2 row 32 · `.github\\workflows\\x.yml` (backslashes) is OVERLAP "
                    "under `ci`", first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith(".github/workflows/x.yml") for ln in lines),
                    f"rc={rc} {lines}")
            rc, lines = run(repo, "--paths", "./.github/workflows/x.yml")
            c.check("SCC-441 review-2 row 32 · `./.github/workflows/x.yml` is OVERLAP under `ci`",
                    first(lines) == "OVERLAP" and rc == 3
                    and any(ln.startswith(".github/workflows/x.yml") for ln in lines),
                    f"rc={rc} {lines}")
            # CONTROL: the RAW backslash string does not match on its own - the normalisation is
            # what earns the OVERLAP above (wf_common.norm_path is outside this lane's diff).
            rows = [("ci", ".github/", "the gates")]
            c.check("SCC-441 review-2 row 32 · CONTROL: the raw `.github\\workflows\\x.yml` fed "
                    "straight to pattern_hit/overlaps matches NOTHING",
                    not sc.pattern_hit(".github\\workflows\\x.yml", ".github/", fragments=False)
                    and not sc.overlaps([".github\\workflows\\x.yml"], rows, fragments=False),
                    "so the OVERLAP above is the normalisation's work")

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
