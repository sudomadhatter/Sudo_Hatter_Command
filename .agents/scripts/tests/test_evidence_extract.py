"""test_evidence_extract.py — the guard for `evidence_extract.py` (SCC-123, 2026-08-12).

WHY THIS FILE IS SHAPED THE WAY IT IS
-------------------------------------
SCC-122's code review broke that lane's guard in one move: it replaced the files under test with
stubs instructing the OPPOSITE of every rule, and the guard reported a clean 80/80. The lesson,
recorded in that walkthrough: *a check that cannot fail is a finding*, and a red proving only
"the file did not exist yet" is not discrimination.

The subject here is a real program, not markdown, so the counter-example takes its natural form:
**paired fixtures.** Nearly every behavioural claim below is asserted twice — once on a repo where
the thing is true and must be FOUND, and once on a repo where it is false and must be ABSENT. A
naive implementation that reports everything fails the negative row; one that reports nothing fails
the positive row. Neither half is meaningful alone, which is why they are written together.

Two of those pairs are the whole reason SCC-123 exists:

  * `flat_toolbox` must NOT be reported as importing `flat_tool` — a substring match passes the
    positive row and fails here.
  * an `@/`-aliased import must be found where the alias root is declared by a NESTED tsconfig
    (`frontend/tsconfig.json` -> `frontend/src/`). An implementation that assumes a repo-root
    `src/` resolves the specifier to a path that does not exist, reports `IMPORTED BY: none`, and
    reproduces the exact silent emptiness this subtask was written to remove (plan finding F3).

One check deliberately does NOT use a source grep as its evidence. "No `grep` subprocess" is proven
by running the script with **PATH emptied** and requiring byte-identical output; a source-level ban
on the word `subprocess` ships too, but only as a cheap tripwire — a comment containing the banned
literal inverts that style of check, which is a known house pitfall.

Stdlib only, no pytest, ASCII output — same constraints as every script under `.agents/scripts/`.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

SCRIPTS = Path(__file__).resolve().parents[1]
TARGET = SCRIPTS / "evidence_extract.py"


class Guard:
    """`Cases`, with one correction: a detail string explains a FAILURE.

    `Cases.check` prints its detail on every row, so a message written for the failing case
    ("caller missing") is printed beside a green PASS and reads as a contradiction. Here the
    detail is suppressed on success; `show()` is the opt-in for evidence worth printing either way.
    """

    def __init__(self, title: str) -> None:
        self._cases = Cases(title)

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        self._cases.check(name, bool(ok), "" if ok else detail)

    def show(self, name: str, ok: bool, detail: str = "") -> None:
        self._cases.check(name, bool(ok), detail)

    def finish(self) -> int:
        return self._cases.finish()


# ── running the subject ───────────────────────────────────────────────────────
def run_ee(*args: str, env: dict[str, str] | None = None,
           stdin: str | None = None) -> tuple[int, str, str]:
    """Run evidence_extract.py. Returns (exit code, stdout, stderr) kept SEPARATE.

    Separate on purpose: a JSON payload on stdout must stay parseable, and merging a warning
    into it would make every findings-mode assertion silently depend on stderr being empty.
    """
    proc = subprocess.run(
        [sys.executable, str(TARGET), *args],
        capture_output=True, text=True, errors="replace",
        input=stdin, env=env,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


_BLOCKER = '''\
"""Injected by test_evidence_extract.py: make spawning a child process impossible."""
import os
import subprocess


def _blocked(*args, **kwargs):
    raise OSError("process spawning is disabled by the SCC-123 guard")


subprocess.Popen = _blocked
subprocess.run = _blocked
subprocess.call = _blocked
subprocess.check_output = _blocked
os.system = _blocked
os.execv = _blocked
os.execvp = _blocked
os.execvpe = _blocked
if hasattr(os, "posix_spawn"):
    os.posix_spawn = _blocked
'''


def env_no_subprocess(blocker_dir: Path) -> dict[str, str]:
    """A child environment in which the script CANNOT shell out to anything.

    ⚠ Emptying PATH is NOT enough, and believing it was is how this check nearly shipped
    vacuous. When PATH is empty or unset, CPython falls back to `os.defpath` (`:/bin:/usr/bin`),
    so `["grep", ...]` still resolves to /bin/grep and a shell-out survives the "no PATH" run
    untouched. The author's own mutation proof caught this: a reintroduced grep subprocess flipped
    only the source tripwire, never this row.

    So the block is installed in the interpreter instead. `sitecustomize` is imported by `site`
    at startup, before the script under test, and replaces every spawn primitive with a raise.
    Anything shelling out now either dies loudly or degrades - and either way the output stops
    being byte-identical, which is what this check actually measures. PATH is emptied as well,
    since defence in depth costs nothing here.
    """
    (blocker_dir / "sitecustomize.py").write_text(_BLOCKER, encoding="utf-8")
    env = {"PATH": "", "PYTHONPATH": str(blocker_dir), "PYTHONIOENCODING": "utf-8"}
    for keep in ("SYSTEMROOT", "SystemRoot", "COMSPEC", "TEMP", "TMP"):
        if keep in os.environ:
            env[keep] = os.environ[keep]
    return env


def write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


# ── fixtures ──────────────────────────────────────────────────────────────────
def build_python_repo(root: Path) -> None:
    """A repo carrying BOTH Python import shapes plus the negative controls for each.

    `src/` has no `__init__.py` and `src/pkg/` has one, so `src/pkg/target.py` is importable as
    `pkg.target` (package chain) and as `src.pkg.target` (root-relative dotted). `scripts/` is the
    shape this repo's own safety-net scripts use: a directory on sys.path holding flat modules, so
    `scripts/flat_tool.py` is imported as bare `flat_tool` and by no other name.
    """
    write(root, "src/pkg/__init__.py", "")
    # 40 padding lines put `def target_fn` on line 41 exactly; the assertions below cite that
    # number, so the fixture and the expectation cannot drift apart silently.
    write(root, "src/pkg/target.py",
          "\n".join([f"# padding {i}" for i in range(1, 41)]
                    + ["def target_fn(value):", "    return value + 1", "TARGET_SENTINEL = 1"]
                    + [f"# tail {i}" for i in range(1, 40)]) + "\n")

    # positive: imports by the package-chain name
    write(root, "src/pkg/user_chain.py", "from pkg.target import target_fn\n\ndef go():\n    return target_fn(1)\n")
    # positive: imports by the root-relative dotted name
    write(root, "src/other_root.py", "from src.pkg.target import target_fn\n")
    # positive: the `from <parent> import <leaf>` form, where the leaf IS the module
    write(root, "src/pkg/user_parent.py", "from pkg import target\n")
    # COUNTER-EXAMPLE: same parent, different leaf
    write(root, "src/pkg/parent_other.py", "from pkg import sibling\n")
    # COUNTER-EXAMPLE: imports a different module in the same package
    write(root, "src/pkg/unrelated.py", "from pkg.sibling import other_fn\n")
    # sibling.py doubles as the blast-radius fixture, so it must genuinely reference an
    # identifier the finding mentions -- otherwise related_code is empty for a reason that
    # has nothing to do with the code under test.
    write(root, "src/pkg/sibling.py", "def other_fn():\n    return target_fn(0)  # SIBLING_MARKER\n")

    # the flat sys.path shape
    write(root, "scripts/flat_tool.py", "def flat_helper():\n    return 'flat'\n")
    write(root, "scripts/flat_user.py", "import flat_tool\n\nflat_tool.flat_helper()\n")
    # COUNTER-EXAMPLE: a longer name that CONTAINS the module name
    write(root, "scripts/flat_toolbox.py", "def unrelated():\n    return 1\n")
    write(root, "scripts/box_user.py", "import flat_toolbox\n")

    # caller of target_fn in a third file, and one that must never be reported
    write(root, "src/pkg/caller_visible.py",
          "\n".join([f"# pad {i}" for i in range(1, 20)]
                    + ["result = target_fn(7)  # CALLER_VISIBLE_MARKER"]) + "\n")
    write(root, "node_modules/evil.py", "target_fn(999)  # CALLER_HIDDEN_MARKER\n")
    write(root, ".venv/also_evil.py", "target_fn(998)  # CALLER_HIDDEN_MARKER\n")

    write(root, "docs/notes.md", "# notes\nMentions target_fn but is prose.\n")


def build_ts_repo(root: Path) -> None:
    """A Next-shaped frontend: the tsconfig is NESTED, and its alias root is relative to itself.

    Copied in shape from the one real frontend in this system
    (`Projects/AGY_AVIATIONCHAT/frontend/tsconfig.json`, `"@/*": ["./src/*"]`), because a
    repo-root assumption is precisely the defect this fixture exists to catch.
    """
    write(root, "frontend/tsconfig.json",
          json.dumps({"compilerOptions": {"paths": {"@/*": ["./src/*"]}}}, indent=2))
    write(root, "frontend/src/components/Widget.tsx",
          "export const Widget = () => null;  // WIDGET_SENTINEL\n")
    write(root, "frontend/src/components/Other.tsx", "export const Other = () => null;\n")
    write(root, "frontend/src/components/index.ts", "export * from './Widget';\n")

    # positive: relative specifier
    write(root, "frontend/src/pages/rel.tsx",
          "import { Widget } from '../components/Widget';\nexport default Widget;\n")
    # positive: alias specifier through the NESTED tsconfig root
    write(root, "frontend/src/pages/alias.tsx",
          "import { Widget } from '@/components/Widget';\nexport default Widget;\n")
    # positive: require() form
    write(root, "frontend/src/pages/req.js",
          "const { Widget } = require('../components/Widget');\n")
    # positive for index.ts only: a directory import
    write(root, "frontend/src/pages/dir.tsx",
          "import { Widget } from '@/components';\nexport default Widget;\n")
    # COUNTER-EXAMPLE: imports a sibling, must never be listed for Widget
    write(root, "frontend/src/pages/other.tsx",
          "import { Other } from '@/components/Other';\nexport default Other;\n")
    # COUNTER-EXAMPLE: names Widget in prose/JSX but imports nothing from it
    write(root, "frontend/src/pages/mentions.tsx",
          "// Widget is discussed here but never imported\nexport const x = 'Widget';\n")


def build_recurrence_repo(root: Path) -> None:
    """A repo containing a directory named after the repo itself (plan D3 / acceptance 11).

    pr-af's `_normalize_relative_path` strips a `<repo-name>/` marker found ANYWHERE in the path,
    which turns `myrepo/core.py` into `core.py` and reads an empty file. Their own fix -- try the
    direct join first, normalize only as a fallback -- is what this fixture pins.
    """
    write(root, "myrepo/core.py",
          "\n".join([f"# line {i}" for i in range(1, 10)] + ["RECURRENCE_SENTINEL = True"]) + "\n")


def findings_file(root: Path, payload: list[dict]) -> str:
    path = root / "_findings.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def pack_of(out: str) -> list[str]:
    """The `### <path>` headers a pack emitted, in order."""
    return [ln[4:].split(" (showing")[0].strip()
            for ln in out.splitlines() if ln.startswith("### ")]


def imported_by(blob: str) -> str:
    """The IMPORTED BY line out of an import-context blob ('' when absent)."""
    for ln in blob.splitlines():
        if ln.startswith("IMPORTED BY:"):
            return ln
    return ""


def main() -> int:
    c = Guard("evidence_extract (SCC-123)")

    # ── 0. the subject exists and refuses nonsense ────────────────────────────
    c.check("evidence_extract.py exists", TARGET.is_file(), str(TARGET))
    if not TARGET.is_file():
        return c.finish()

    src = TARGET.read_text(encoding="utf-8", errors="replace")

    rc, _, _ = run_ee()
    c.check("no arguments is a usage error (exit 2)", rc == 2, f"exit {rc}")
    rc, _, _ = run_ee("--repo", ".", "--pack", "a.py", "--findings", "f.json")
    c.check("both modes at once is a usage error (exit 2)", rc == 2, f"exit {rc}")
    rc, _, _ = run_ee("--repo", "/nonexistent/repo/path", "--pack", "a.py")
    c.check("a repo path that does not exist is a usage error (exit 2)", rc == 2, f"exit {rc}")

    # ── 1. pack mode ──────────────────────────────────────────────────────────
    with TempDir() as tmp:
        repo = tmp / "repoA"
        repo.mkdir()
        build_python_repo(repo)

        rc, out, err = run_ee("--repo", str(repo), "--pack", "src/pkg/target.py")
        c.check("pack: exits 0", rc == 0, f"exit {rc} err={err[:120]}")
        c.check("pack: emits the file body with line numbers",
                "TARGET_SENTINEL" in out and "41: def target_fn(value):" in out,
                "sentinel or numbered line missing")
        c.check("pack: carries an import-context block",
                "IMPORTS:" in out and "IMPORTED BY:" in out, "context block missing")

        # COUNTER-EXAMPLE: a file nothing imports must report none
        rc, lone, _ = run_ee("--repo", str(repo), "--pack", "src/pkg/unrelated.py")
        c.check("pack COUNTER-EXAMPLE: a file nobody imports reports IMPORTED BY: none",
                imported_by(lone).endswith("none"), imported_by(lone) or "no line")

        # file cap: 8 candidates, 6 allowed
        many = [f"many/f{i}.py" for i in range(8)]
        for i, rel in enumerate(many):
            write(repo, rel, f"VALUE_{i} = {i}\n")
        rc, out, _ = run_ee("--repo", str(repo), "--pack", *many)
        c.check("pack: caps at 6 files", len(pack_of(out)) == 6, f"{len(pack_of(out))} headers")
        c.check("pack COUNTER-EXAMPLE: the 7th and 8th files are absent",
                "VALUE_6" not in out and "VALUE_7" not in out, "an over-cap file leaked in")

        # line cap: 450 lines, 400 shown
        write(repo, "big/long.py", "\n".join(f"row_{i} = {i}" for i in range(1, 451)) + "\n")
        rc, out, _ = run_ee("--repo", str(repo), "--pack", "big/long.py")
        c.check("pack: caps at 400 lines and says so",
                "showing first 400 of 450" in out and "400: row_400 = 400" in out,
                "truncation notice or 400th line missing")
        c.check("pack COUNTER-EXAMPLE: line 401 and beyond are absent",
                "row_401" not in out and "row_450" not in out, "an over-cap line leaked in")

        # char cap: six 400-line files of wide rows blow past 16000
        wide = [f"wide/w{i}.py" for i in range(6)]
        for rel in wide:
            write(repo, rel, "\n".join("x" * 60 + f" = {i}" for i in range(400)) + "\n")
        rc, out, _ = run_ee("--repo", str(repo), "--pack", *wide)
        c.check("pack: caps total output at 16000 chars", len(out.strip()) <= 16000, f"{len(out)} chars")
        c.check("pack COUNTER-EXAMPLE: the cap actually bit (output is not trivially short)",
                len(out.strip()) > 8000, f"{len(out)} chars - fixture failed to exceed the cap")

        # A single big file fills the whole 16000-char budget, so anything emitted AFTER the body
        # is truncated away. Found by running this on a real file in this repo, not by fixtures:
        # `wf_common.py` produced 16093 bytes with no IMPORTED BY line at all. The import context
        # is the reason a lens is primed, so it must survive its own file being too long.
        write(repo, "big/imported_long.py",
              "\n".join([f"filler_{i} = '{'y' * 55}'" for i in range(1, 451)]) + "\n")
        write(repo, "big/long_user.py", "import imported_long\n")
        rc, out, _ = run_ee("--repo", str(repo), "--pack", "big/imported_long.py")
        c.check("pack: a file long enough to hit the char cap STILL carries its import context",
                "big/long_user.py" in imported_by(out),
                imported_by(out) or "IMPORTED BY was truncated off the end of the pack")
        c.check("pack COUNTER-EXAMPLE: that file really did hit the cap",
                len(out.strip()) >= 16000, f"{len(out.strip())} chars - cap never bit")

        # skips
        rc, out, _ = run_ee("--repo", str(repo), "--pack", "node_modules/evil.py")
        c.check("pack: a node_modules path yields nothing", out.strip() == "", out[:80])
        write(repo, "assets/blob.bin", "\x00\x01binary\x00")
        rc, out, _ = run_ee("--repo", str(repo), "--pack", "assets/blob.bin")
        c.check("pack: a non-text extension yields nothing", out.strip() == "", out[:80])

    # ── 2. findings mode — shape, snippets, caps ──────────────────────────────
    with TempDir() as tmp:
        repo = tmp / "repoA"
        repo.mkdir()
        build_python_repo(repo)

        diff = repo / "_diff.patch"
        diff.write_text(
            "diff --git a/src/pkg/target.py b/src/pkg/target.py\n"
            "--- a/src/pkg/target.py\n"
            "+++ b/src/pkg/target.py\n"
            "@@ -1,3 +1,4 @@\n"
            " head_context\n"
            "+FIRST_HUNK_MARKER\n"
            " more_head\n"
            "@@ -39,3 +40,4 @@\n"
            " tail_context\n"
            "+SECOND_HUNK_MARKER\n"
            " more_tail\n",
            encoding="utf-8")

        fpath = findings_file(repo, [{
            "title": "target_fn returns the wrong value",
            "body": "The function `target_fn` is called from src/pkg/caller_visible.py and is wrong.",
            "evidence": "see src/pkg/sibling.py",
            "file_path": "src/pkg/target.py",
            "line_start": 41,
        }])

        rc, out, err = run_ee("--repo", str(repo), "--findings", fpath,
                              "--diff", str(diff), "--blast-radius", "src/pkg/sibling.py")
        c.check("findings: exits 0", rc == 0, f"exit {rc} err={err[:160]}")

        try:
            data = json.loads(out)
        except json.JSONDecodeError as exc:
            data = {}
            c.check("findings: stdout is valid JSON", False, str(exc))
        else:
            c.check("findings: stdout is valid JSON", True)

        pkg = data.get("target_fn returns the wrong value", {})
        c.check("findings: keyed by finding title", bool(pkg), f"keys={list(data)[:3]}")

        fields = ("primary_code", "caller_snippets", "cross_ref_snippets",
                  "diff_hunk", "import_context", "related_code")
        c.check("findings: carries all six EvidencePackage fields",
                all(f in pkg for f in fields), f"missing={[f for f in fields if f not in pkg]}")

        c.check("findings: primary_code is the code AT the finding's line",
                "TARGET_SENTINEL" in pkg.get("primary_code", "")
                and "41: def target_fn(value):" in pkg.get("primary_code", ""),
                "wrong window or unnumbered")
        # Anchored on the emitted line NUMBER, not on body text: "# padding 1" is a substring of
        # "# padding 11", so a content match here would have proven nothing either way.
        first_line = pkg.get("primary_code", "").split("\n", 1)[0]
        c.check("findings COUNTER-EXAMPLE: primary_code is a window (starts at line 11), "
                "not the whole file",
                first_line.startswith("11: "),
                f"first emitted line is {first_line!r}, expected the +/-30 window to start at 11")

        callers = "\n".join(pkg.get("caller_snippets", []))
        c.check("findings: a call site in another file is found",
                "CALLER_VISIBLE_MARKER" in callers, "caller missing")
        c.check("findings COUNTER-EXAMPLE: call sites under skip-dirs are never reported",
                "CALLER_HIDDEN_MARKER" not in callers, "a node_modules/.venv hit leaked in")
        c.check("findings COUNTER-EXAMPLE: the finding's own file is not its own caller",
                not any(s.startswith("src/pkg/target.py:") for s in pkg.get("caller_snippets", [])),
                "self-reference reported")

        xrefs = "\n".join(pkg.get("cross_ref_snippets", []))
        c.check("findings: a real path named in the body is cross-referenced",
                "other_fn" in xrefs, "cross-ref missing")

        c.check("findings: diff_hunk is the hunk containing the line, not the first hunk",
                "SECOND_HUNK_MARKER" in pkg.get("diff_hunk", "")
                and "FIRST_HUNK_MARKER" not in pkg.get("diff_hunk", ""),
                pkg.get("diff_hunk", "")[:80])

        c.check("findings: related_code comes from the blast-radius file",
                "other_fn" in pkg.get("related_code", ""), "blast-radius snippet missing")

        # identifier cap: 12 mentioned, at most 8 searched
        # Each identifier must resolve to EXACTLY ONE file, or the 10-snippet cap truncates
        # before the 8-identifier cap does and this measures the wrong limit. Hence the
        # definition is written without a call-shaped `name(` occurrence.
        for i in range(12):
            write(repo, f"idents/mod_{i}.py", f"ident_{i:02d} = None\n")
            write(repo, f"idents/call_{i}.py", f"ident_{i:02d}(1)  # IDENT_CALL_{i:02d}\n")
        body = " ".join(f"ident_{i:02d}()" for i in range(12))
        fpath = findings_file(repo, [{
            "title": "many identifiers", "body": body, "evidence": "",
            "file_path": "src/pkg/target.py", "line_start": 41,
        }])
        rc, out, _ = run_ee("--repo", str(repo), "--findings", fpath)
        many_pkg = json.loads(out).get("many identifiers", {})
        hit = {i for i in range(12)
               if f"IDENT_CALL_{i:02d}" in "\n".join(many_pkg.get("caller_snippets", []))}
        c.check("findings: at most 8 identifiers are searched per finding",
                len(hit) <= 8, f"{len(hit)} identifiers searched")
        c.check("findings COUNTER-EXAMPLE: the identifier cap bit (fixture offered 12)",
                len(hit) == 8, f"{len(hit)} - expected exactly the cap")

        # stop-words
        fpath = findings_file(repo, [{
            "title": "prose only",
            "body": "The value should return the data from this file when there is an error.",
            "evidence": "", "file_path": "src/pkg/target.py", "line_start": 41,
        }])
        rc, out, _ = run_ee("--repo", str(repo), "--findings", fpath)
        prose = json.loads(out).get("prose only", {})
        c.check("findings: a stop-word-only body yields no caller search",
                prose.get("caller_snippets") == [], str(prose.get("caller_snippets"))[:120])
        c.check("findings COUNTER-EXAMPLE: that same body still returns primary_code",
                "TARGET_SENTINEL" in prose.get("primary_code", ""),
                "empty package - the check above would pass vacuously")

    # ── 3. IMPORTED BY — the reason this subtask exists ───────────────────────
    with TempDir() as tmp:
        repo = tmp / "repoA"
        repo.mkdir()
        build_python_repo(repo)

        rc, out, _ = run_ee("--repo", str(repo), "--pack", "scripts/flat_tool.py")
        line = imported_by(out)
        c.check("python flat: a bare `import flat_tool` on sys.path IS found",
                "scripts/flat_user.py" in line, line or "no IMPORTED BY line")
        c.check("python flat COUNTER-EXAMPLE: `import flat_toolbox` is NOT a hit for flat_tool",
                "scripts/box_user.py" not in line, line)

        rc, out, _ = run_ee("--repo", str(repo), "--pack", "src/pkg/target.py")
        line = imported_by(out)
        c.check("python package: the package-chain name (pkg.target) is found",
                "src/pkg/user_chain.py" in line, line or "no IMPORTED BY line")
        c.check("python package: the root-dotted name (src.pkg.target) is found",
                "src/other_root.py" in line, line)
        c.check("python package: the `from pkg import target` form is found",
                "src/pkg/user_parent.py" in line, line)
        c.check("python package COUNTER-EXAMPLE: `from pkg import sibling` is NOT a hit for target",
                "src/pkg/parent_other.py" not in line, line)
        c.check("python package COUNTER-EXAMPLE: an importer of a sibling module is NOT listed",
                "src/pkg/unrelated.py" not in line, line)

    with TempDir() as tmp:
        repo = tmp / "repoB"
        repo.mkdir()
        build_ts_repo(repo)

        rc, out, _ = run_ee("--repo", str(repo), "--pack", "frontend/src/components/Widget.tsx")
        line = imported_by(out)
        c.check("ts: a relative import is found",
                "frontend/src/pages/rel.tsx" in line, line or "no IMPORTED BY line")
        c.check("ts: a require() import is found",
                "frontend/src/pages/req.js" in line, line)
        c.check("ts: an @/ alias resolved through the NESTED tsconfig is found (plan F3)",
                "frontend/src/pages/alias.tsx" in line, line)
        c.check("ts COUNTER-EXAMPLE: an importer of a SIBLING component is NOT listed",
                "frontend/src/pages/other.tsx" not in line, line)
        c.check("ts COUNTER-EXAMPLE: naming the symbol without importing it is NOT a hit",
                "frontend/src/pages/mentions.tsx" not in line, line)
        c.check("ts COUNTER-EXAMPLE: a directory import belongs to index.ts, not to Widget.tsx",
                "frontend/src/pages/dir.tsx" not in line, line)

        rc, out, _ = run_ee("--repo", str(repo), "--pack", "frontend/src/components/index.ts")
        line = imported_by(out)
        c.check("ts: a directory import IS found for the index file",
                "frontend/src/pages/dir.tsx" in line, line or "no IMPORTED BY line")

    # ── 4. path normalization where the repo name recurs (D3) ─────────────────
    with TempDir() as tmp:
        repo = tmp / "myrepo"
        repo.mkdir()
        build_recurrence_repo(repo)
        rc, out, _ = run_ee("--repo", str(repo), "--pack", "myrepo/core.py")
        c.check("a path whose first segment repeats the repo name still resolves",
                "RECURRENCE_SENTINEL" in out, out[:120] or "empty pack")

    # ── 5. degrade, never die (plan D6) ───────────────────────────────────────
    with TempDir() as tmp:
        repo = tmp / "repoA"
        repo.mkdir()
        build_python_repo(repo)

        fpath = findings_file(repo, [
            {"title": "gone", "body": "x", "evidence": "",
             "file_path": "src/pkg/does_not_exist.py", "line_start": 5},
            {"title": "binary", "body": "x", "evidence": "",
             "file_path": "assets/blob.bin", "line_start": 1},
            {"title": "no line number", "body": "x", "evidence": "",
             "file_path": "src/pkg/target.py"},
        ])
        write(repo, "assets/blob.bin", "\x00\x01binary\x00")
        rc, out, err = run_ee("--repo", str(repo), "--findings", fpath)
        c.check("degrade: a missing file, a binary file and an absent line still exit 0",
                rc == 0, f"exit {rc} err={err[:160]}")
        degraded = json.loads(out) if out.strip() else {}
        c.check("degrade: the missing-file package is empty, not absent",
                degraded.get("gone", {}).get("primary_code", None) == "",
                str(degraded.get("gone"))[:120])
        # A finding with no line number reads from line 1 -- so the proof that this run did not
        # wholesale degrade is the FILE HEAD, not the line-43 sentinel.
        c.check("degrade: an absent line_start falls back to the head of the file",
                "1: # padding 1" in degraded.get("no line number", {}).get("primary_code", ""),
                "the whole run degraded - the check above would pass vacuously")
        c.check("degrade: no traceback reaches stderr",
                "Traceback" not in err, err[:160])

        bad = repo / "_bad.json"
        bad.write_text("{not json at all", encoding="utf-8")
        rc, _, _ = run_ee("--repo", str(repo), "--findings", str(bad))
        c.check("an unreadable findings file is a usage error (exit 2)", rc == 2, f"exit {rc}")

        rc, out, _ = run_ee("--repo", str(repo), "--findings", "-",
                            stdin=json.dumps([{"title": "via stdin", "body": "",
                                               "evidence": "", "file_path": "src/pkg/target.py",
                                               "line_start": 41}]))
        c.check("findings accepts '-' for stdin",
                rc == 0 and "via stdin" in (out or ""), f"exit {rc}")

    # ── 6. no grep subprocess — proven by behaviour, not by grepping source ───
    with TempDir() as tmp:
        repo = tmp / "repoA"
        repo.mkdir()
        build_python_repo(repo)

        blocker = tmp / "blocker"
        blocker.mkdir()

        rc_a, out_a, _ = run_ee("--repo", str(repo), "--pack", "scripts/flat_tool.py")
        rc_b, out_b, err_b = run_ee("--repo", str(repo), "--pack", "scripts/flat_tool.py",
                                    env=env_no_subprocess(blocker))
        c.check("pack runs with process-spawning disabled and still exits 0",
                rc_b == 0, f"exit {rc_b} err={err_b[:200]}")
        c.check("no grep subprocess in pack mode: byte-identical with spawning disabled",
                out_a == out_b and out_a != "", "output differed or was empty")
        c.check("spawn-blocked COUNTER-EXAMPLE: that output is real work, not silence",
                "scripts/flat_user.py" in imported_by(out_b), imported_by(out_b) or "empty")

        # ⚠ Pack mode alone does NOT reach the caller search, the cross-ref reads or the
        # blast-radius walk -- the three places pr-af shells out or would. A proof that only
        # ran --pack left the busiest search path untested, and the author's mutation run
        # caught exactly that. Findings mode is where those code paths live, so it is proven
        # under the same block.
        fpath = findings_file(repo, [{
            "title": "spawn-blocked path coverage",
            "body": "The function `target_fn` is called from src/pkg/caller_visible.py.",
            "evidence": "see src/pkg/sibling.py",
            "file_path": "src/pkg/target.py", "line_start": 41,
        }])
        rc_c, out_c, _ = run_ee("--repo", str(repo), "--findings", fpath,
                                "--blast-radius", "src/pkg/sibling.py")
        rc_d, out_d, err_d = run_ee("--repo", str(repo), "--findings", fpath,
                                    "--blast-radius", "src/pkg/sibling.py",
                                    env=env_no_subprocess(blocker))
        c.check("findings runs with process-spawning disabled and still exits 0",
                rc_d == 0, f"exit {rc_d} err={err_d[:200]}")
        c.check("no grep subprocess in findings mode: byte-identical with spawning disabled",
                out_c == out_d and out_c != "", "output differed or was empty")
        blocked_pkg = json.loads(out_d).get("spawn-blocked path coverage", {}) if out_d.strip() else {}
        c.check("spawn-blocked COUNTER-EXAMPLE: the caller search really ran under the block",
                "CALLER_VISIBLE_MARKER" in "\n".join(blocked_pkg.get("caller_snippets", [])),
                "no caller found - the two rows above would compare two empty results")
        # The blocker itself must be provably live, or the three rows above are vacuous: a
        # sitecustomize that failed to load would let ANY implementation pass them.
        probe = tmp / "probe.py"
        probe.write_text("import subprocess\n"
                         "subprocess.run(['echo', 'hi'])\n", encoding="utf-8")
        proc = subprocess.run([sys.executable, str(probe)], capture_output=True, text=True,
                              env=env_no_subprocess(blocker), errors="replace")
        c.check("spawn-blocker is genuinely installed (a control shell-out dies under it)",
                proc.returncode != 0 and "disabled by the SCC-123 guard" in (proc.stderr or ""),
                f"exit {proc.returncode} stderr={(proc.stderr or '')[:160]}")

        rc_c, out_c, _ = run_ee("--repo", str(repo), "--pack", "scripts/flat_tool.py")
        c.check("deterministic: the same inputs give byte-identical output",
                out_a == out_c, "two runs differed")

    # ── 7. source-level tripwires (cheap, NOT the evidence above) ─────────────
    code_only = "\n".join(ln for ln in src.splitlines() if not ln.strip().startswith("#"))
    c.check("tripwire: imports no subprocess module",
            "import subprocess" not in code_only, "subprocess import present")
    c.check("tripwire: no third-party import (stdlib only)",
            "pydantic" not in code_only and "import requests" not in code_only,
            "third-party import present")
    c.check("docstring records the GitNexus decision (plan D7)",
            "GitNexus" in src[:4000] and "machine-local" in src[:4000],
            "rationale missing from the module docstring")
    c.check("docstring records the port source and SHA",
            "8593130" in src[:4000] and "pr-af" in src[:4000], "provenance missing")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
