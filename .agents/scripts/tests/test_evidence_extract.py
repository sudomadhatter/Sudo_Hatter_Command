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
by running the script with **process creation blocked inside the interpreter** — a sitecustomize.py
on PYTHONPATH that makes every spawn primitive raise, with a control shell-out asserted to die
under the same block — and requiring byte-identical output. (Emptying PATH proves nothing: CPython
falls back to `os.defpath`, so `/bin/grep` survives a no-PATH run untouched.) A source-level ban
on the word `subprocess` ships too, but only as a cheap tripwire — a comment containing the banned
literal inverts that style of check, which is a known house pitfall.

Stdlib only, no pytest, ASCII output — same constraints as every script under `.agents/scripts/`.
"""
from __future__ import annotations

import ast
import contextlib
import io
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

    def block(self, label: str) -> bool:
        """Pass-through to `Cases.block`, so `--case` can select a section of this file.

        Added for SCC-187: `mutation_sweep.py` appends `--case <block>` to every mutant run, and
        a file declaring NO blocks leaves `blocks_run` at 0, which `_harness.finish()` turns into
        `NO_MATCH` (exit 3). The sweep reads that as SWEEP ERROR rather than a kill — correctly —
        so an unblocked file cannot be swept at all. Unfiltered, every block still runs and this
        is always True, so the file behaves exactly as it did before it was wired.
        """
        return self._cases.block(label)

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
    # blast-radius fixture with the identifier match DEEP in the file and a decoy at the head:
    # an implementation that ignores identifiers and dumps the head emits the decoy and never
    # the marker, so the pair discriminates where a "something came back" row could not.
    write(root, "src/pkg/blast_deep.py",
          "\n".join(["# BLAST_HEAD_DECOY - an identifier-blind impl emits this line"]
                    + [f"# filler {i}" for i in range(2, 29)]
                    + ["def blast_helper():",
                       "    return target_fn(3)  # BLAST_MATCH_MARKER"]) + "\n")
    # named by NO finding in any fixture: the cross-ref and blast negatives anchor on it
    write(root, "src/pkg/never_named.py", "NEVER_NAMED_MARKER = 'not in any finding body'\n")

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
    # a nested checkout: ANOTHER BRANCH's copy of the repo, which must never be evidence
    write(root, ".claude/worktrees/lane/scripts/wt_dup.py", "import flat_tool\n")
    write(root, ".claude/worktrees/lane/wt_caller.py", "target_fn(996)  # CALLER_HIDDEN_MARKER\n")

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


# Every rank tag the subject can emit. `[unranked]` is the honest third state: the importer walk
# blew its deadline, so "does not import the subject" is unknown rather than false. A helper that
# does not know a tag silently reports it as untagged AND mis-parses the path out of the snippet,
# so this tuple and `evidence_extract`'s tag literals must stay in step.
_CALLER_TAGS = ("[importer] ", "[name-match] ", "[unranked] ")


def caller_tag(snippet: str) -> str:
    """The rank tag a caller snippet leads with, or '' when it carries none (SCC-187)."""
    return next((t.strip() for t in _CALLER_TAGS if snippet.startswith(t)), "")


def caller_files(pkg: dict) -> list[str]:
    """The FILE of each caller snippet, tag stripped, in emitted order.

    ⚠ Read the file through this, never with `snippet.startswith("<path>:")`. Once a snippet can
    lead with a tag, a bare `startswith` on the path is False for EVERY snippet whether or not the
    thing it guards against happened — a negative assertion written that way passes vacuously and
    stops being evidence. That is exactly what the self-reference counter-example below was.

    ⚠ The path is recovered as `header.rsplit(":", 1)[0]`, never `split(":", 1)[0]`. A POSIX path
    may legally contain a colon, and a first-colon split turns `pkg/a:b.py:4` into `pkg/a` — the
    subject's own bug, mirrored here, would make this helper blind to it.
    """
    files = []
    for snippet in pkg.get("caller_snippets", []):
        for tag in _CALLER_TAGS:
            if snippet.startswith(tag):
                snippet = snippet[len(tag):]
                break
        files.append(snippet.split("\n", 1)[0].rsplit(":", 1)[0])
    return files


def pkg_for(out: str, title: str) -> dict:
    """The package for `title` out of findings-mode stdout — a LIST of packages since the
    duplicate-title fix. Unparseable or wrong-shaped stdout yields {}, so rows fail on their
    own assertions rather than on a raise here."""
    try:
        data = json.loads(out)
    except ValueError:
        return {}
    if not isinstance(data, list):
        return {}
    return next((p for p in data if isinstance(p, dict) and p.get("finding_title") == title), {})


def main() -> int:
    c = Guard("evidence_extract (SCC-123)")

    # ── 0. the subject exists and refuses nonsense ────────────────────────────
    # ⛔ The hard stop and `src` stay OUTSIDE the block guard, deliberately. `--case` can select
    # a later block, and section 7 reads `src` — bound here, it would be UNBOUND under any filter
    # that skips this block, and every filtered run would die on a NameError instead of testing
    # what it selected. A block guards CHECKS; it must never guard the setup a later block needs.
    if not TARGET.is_file():
        # Guarded like every other check, because the walker recognises exactly one idiom and a
        # bare check here is an orphan whatever its intent. Under a filter that selects some
        # other block this reports nothing and exits NO_MATCH — correct: the subject is missing,
        # so no filtered selection could have been tested either.
        if c.block("0 · the subject exists and refuses nonsense"):
            c.check("evidence_extract.py exists", False, str(TARGET))
        return c.finish()

    src = TARGET.read_text(encoding="utf-8", errors="replace")

    if c.block("0 · the subject exists and refuses nonsense"):
        c.check("evidence_extract.py exists", True, str(TARGET))
        rc, _, _ = run_ee()
        c.check("no arguments is a usage error (exit 2)", rc == 2, f"exit {rc}")
        rc, _, _ = run_ee("--repo", ".", "--pack", "a.py", "--findings", "f.json")
        c.check("both modes at once is a usage error (exit 2)", rc == 2, f"exit {rc}")
        rc, _, _ = run_ee("--repo", ".", "--pack", "a.py", "--diff", "x.patch")
        c.check("pack with --diff is a usage error (exit 2), not silently ignored",
                rc == 2, f"exit {rc}")
        rc, _, _ = run_ee("--repo", "/nonexistent/repo/path", "--pack", "a.py")
        c.check("a repo path that does not exist is a usage error (exit 2)", rc == 2, f"exit {rc}")

    # ── 1. pack mode ──────────────────────────────────────────────────────────
    with TempDir() as tmp:
        if c.block("1 · pack mode"):
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
            # This control asserted `len(out.strip()) >= 16000` until SCC-125. That exact-byte
            # equality was an artifact of the old `[:16000]` slice, not the contract: the pack now
            # trims whole LINES, so a fixture that overruns lands just under the cap instead of
            # exactly on it. The intent is unchanged and is now asserted directly -- the CHAR cap
            # bit, which is only provable by the file being cut below the 400-line cap that would
            # otherwise bound it.
            header = next((ln for ln in out.splitlines()
                           if ln.startswith("### big/imported_long.py")), "")
            shown_n = (int(header.split("showing first ")[1].split(" of ")[0])
                       if "showing first " in header else -1)
            c.check("pack COUNTER-EXAMPLE: that file really did hit the CHAR cap, not just the line cap",
                    0 < shown_n < 400 and 15000 < len(out.strip()) <= 16000,
                    f"shown={shown_n} lines (line cap 400), {len(out.strip())} chars")

            # ── the budget is DIVIDED across files, never spent first-come (SCC-125) ──────
            # SCC-124's B2 meta-finding: a real run packed `task_preflight.py` at 11 of its 686
            # lines while quoting smaller files in full, because the assembled blob was simply
            # sliced at _PACK_MAX_CHARS and whatever sat at the end lost. The lens was told the
            # largest file in the change set was a stub. The total cap is unchanged and still
            # pinned above; what changes is that each file gets a share of it.
            budget = tmp / "repoBudget"
            budget.mkdir()
            for name, tag in (("first", "a"), ("second", "b")):
                write(budget, f"hog/{name}.py",
                      "\n".join(f"{name}_{i} = '{tag * 55}'" for i in range(400)) + "\n")
            write(budget, "hog/last.py", "LAST_SENTINEL = 1\nlast_tail = 2\n")
            rc, out, _ = run_ee("--repo", str(budget), "--pack",
                                "hog/first.py", "hog/second.py", "hog/last.py")
            heads = pack_of(out)
            c.check("pack: every packed file keeps its header when the char cap bites",
                    heads == ["hog/first.py", "hog/second.py", "hog/last.py"], f"headers={heads}")
            c.check("pack: the file packed LAST is not starved by the ones before it",
                    "LAST_SENTINEL" in out, "the last file lost its whole body to earlier files")
            c.check("pack: two oversized files each keep a fair share of the budget",
                    out.count("first_") > 40 and out.count("second_") > 40,
                    f"first={out.count('first_')} lines second={out.count('second_')} lines")
            c.check("pack: a share-truncated file says how much of it is shown",
                    out.count("(showing first ") >= 2,
                    f"{out.count('(showing first ')} truncation notice(s) for 2 cut files")
            c.check("pack COUNTER-EXAMPLE: the total cap still holds under the split",
                    len(out.strip()) <= 16000, f"{len(out.strip())} chars")
            fixture_chars = sum(len((budget / "hog" / f"{n}.py").read_text(encoding="utf-8"))
                                for n in ("first", "second"))
            c.check("pack COUNTER-EXAMPLE: the fixture really did exceed the budget",
                    fixture_chars > 16000,
                    f"{fixture_chars} chars - too small to exercise the split")

            # A share the whole-lines rule cannot spend must not be thrown away (SCC-125 review F2).
            # The split allocates smallest-block-first and carries the residue forward; without that
            # carry, rounding down to whole lines left up to half the budget unused while the file
            # that needed it most was the one being cut.
            c.check("pack: the split spends the budget it divided, rather than rounding it away",
                    len(out.strip()) > 13000, f"only {len(out.strip())} of 16000 chars used")

            # ONE-LINE FILES (SCC-125 review F1). A minified bundle, a lock file or a base64 data URI
            # is a single line longer than any share. Trimming whole lines alone kept ZERO of them and
            # emitted a header over an empty fence, which tells the lens the file is empty -- a
            # regression against even the old blob-slice, which at least handed over a prefix.
            one = tmp / "repoOneLine"
            one.mkdir()
            write(one, "dist/bundle.js", "var BUNDLE_SENTINEL=1;" + "z" * 40000 + "\n")
            write(one, "src/plain.py", "\n".join(f"plain_{i} = {i}" for i in range(400)) + "\n")
            rc, out1, _ = run_ee("--repo", str(one), "--pack", "dist/bundle.js", "src/plain.py")
            c.check("pack: a single-line file too long for its share is NOT emitted as empty",
                    "BUNDLE_SENTINEL" in out1, "the one-line file was packed as an empty fence")
            c.check("pack: and it is labelled as a partial line, not as a whole file",
                    "showing part of line 1 of 1" in out1,
                    "label does not disclose that the line was cut")
            c.check("pack COUNTER-EXAMPLE: the label never claims zero lines of a non-empty file",
                    "showing first 0 of" not in out1, "a 'showing first 0' label was emitted")
            c.check("pack: every code fence it emits is closed",
                    out1.count("```") % 2 == 0, f"{out1.count('```')} fence markers - odd means unclosed")
            c.check("pack COUNTER-EXAMPLE: the one-line fixture really did overrun its share",
                    len(out1.strip()) <= 16000 and "z" * 100 in out1,
                    f"{len(out1.strip())} chars - fixture did not exercise the partial path")

            # skips
            rc, out, _ = run_ee("--repo", str(repo), "--pack", "node_modules/evil.py")
            c.check("pack: a node_modules path yields nothing", out.strip() == "", out[:80])
            write(repo, "assets/blob.bin", "\x00\x01binary\x00")
            rc, out, _ = run_ee("--repo", str(repo), "--pack", "assets/blob.bin")
            c.check("pack: a non-text extension yields nothing", out.strip() == "", out[:80])

            # the cap counts files PACKED, not files asked for: six bad paths must not evict the
            # one real file into an empty pack with a clean exit
            rc, out, _ = run_ee("--repo", str(repo), "--pack",
                                *[f"ghost/g{i}.py" for i in range(6)], "src/pkg/target.py")
            c.check("pack: 6 invalid targets do not evict the valid 7th",
                    "TARGET_SENTINEL" in out, "the real file was sliced away before validation")

            # silent-empty is closed at the CLI: a bad target degrades WITH a stderr note
            rc, out, err = run_ee("--repo", str(repo), "--pack", "does/not/exist.py")
            c.check("pack: a nonexistent target still exits 0 with empty output",
                    rc == 0 and out.strip() == "", f"exit {rc} out={out[:80]!r}")
            c.check("pack: ...and stderr NAMES the skipped path (no silent empties)",
                    "note:" in err and "does/not/exist.py" in err, err[:160] or "stderr empty")

    # ── 2. findings mode — shape, snippets, caps ──────────────────────────────
    with TempDir() as tmp:
        if c.block("2 · findings mode — shape, snippets, caps"):
            repo = tmp / "repoA"
            repo.mkdir()
            build_python_repo(repo)

            diff = repo / "_diff.patch"
            # THREE hunks with the finding's line in the MIDDLE one: an implementation that always
            # returns the first hunk, always returns the last, or dumps the whole patch fails this
            # fixture three different ways. The prior two-hunk fixture put the target in the LAST
            # hunk, and an always-the-last-hunk mutant scored a full pass.
            diff.write_text(
                "diff --git a/src/pkg/target.py b/src/pkg/target.py\n"
                "--- a/src/pkg/target.py\n"
                "+++ b/src/pkg/target.py\n"
                "@@ -1,3 +1,4 @@\n"
                " head_context\n"
                "+FIRST_HUNK_MARKER\n"
                " more_head\n"
                "@@ -39,3 +40,4 @@\n"
                " mid_context\n"
                "+MIDDLE_HUNK_MARKER\n"
                " more_mid\n"
                "@@ -78,3 +80,4 @@\n"
                " tail_context\n"
                "+THIRD_HUNK_MARKER\n"
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
                                  "--diff", str(diff),
                                  "--blast-radius", "src/pkg/blast_deep.py", "src/pkg/never_named.py")
            c.check("findings: exits 0", rc == 0, f"exit {rc} err={err[:160]}")

            try:
                data = json.loads(out)
            except json.JSONDecodeError as exc:
                data = []
                c.check("findings: stdout is valid JSON", False, str(exc))
            else:
                c.check("findings: stdout is valid JSON", True)

            c.check("findings: output is a LIST of packages, one per finding",
                    isinstance(data, list) and len(data) == 1,
                    f"type={type(data).__name__}")
            pkg = data[0] if isinstance(data, list) and data else {}
            c.check("findings: the package names its finding",
                    pkg.get("finding_title") == "target_fn returns the wrong value",
                    f"finding_title={pkg.get('finding_title')!r}")

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
            # Read through caller_files(), NOT `s.startswith("src/pkg/target.py:")` — see its
            # docstring: a tagged snippet makes the bare form False for every entry, and this row
            # would pass while reporting nothing (SCC-187).
            c.check("findings COUNTER-EXAMPLE: the finding's own file is not its own caller",
                    "src/pkg/target.py" not in caller_files(pkg),
                    "self-reference reported")

            xrefs = "\n".join(pkg.get("cross_ref_snippets", []))
            c.check("findings: a real path named in the body is cross-referenced",
                    "other_fn" in xrefs, "cross-ref missing")
            c.check("findings COUNTER-EXAMPLE: a file named by NO finding is never cross-referenced",
                    "NEVER_NAMED_MARKER" not in xrefs,
                    "an unnamed file leaked in - a return-everything impl passes the row above")

            hunk = pkg.get("diff_hunk", "")
            c.check("findings: diff_hunk is the hunk CONTAINING the line - of three, the middle",
                    "MIDDLE_HUNK_MARKER" in hunk and "FIRST_HUNK_MARKER" not in hunk
                    and "THIRD_HUNK_MARKER" not in hunk,
                    hunk[:120] or "empty diff_hunk")

            related = pkg.get("related_code", "")
            c.check("findings: related_code is anchored AT the identifier match, deep in the file",
                    "src/pkg/blast_deep.py:30" in related and "BLAST_MATCH_MARKER" in related,
                    related[:120] or "empty related_code")
            c.check("findings COUNTER-EXAMPLE: related_code is not the blast file's HEAD",
                    "BLAST_HEAD_DECOY" not in related,
                    "file-head dump - an identifier-blind impl emits line 1, not line 30")
            c.check("findings COUNTER-EXAMPLE: a blast file with NO mentioned identifier "
                    "contributes nothing",
                    "NEVER_NAMED_MARKER" not in related, "identifier-free blast file leaked in")

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
            many_pkg = pkg_for(out, "many identifiers")
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
            prose = pkg_for(out, "prose only")
            c.check("findings: a stop-word-only body yields no caller search",
                    prose.get("caller_snippets") == [], str(prose.get("caller_snippets"))[:120])
            c.check("findings COUNTER-EXAMPLE: that same body still returns primary_code",
                    "TARGET_SENTINEL" in prose.get("primary_code", ""),
                    "empty package - the check above would pass vacuously")

            # two findings SHARING a title must both survive, each with its OWN file's code:
            # duplicate titles are the expected case for a multi-lens fan-out over one diff, and
            # a dict keyed by title collapsed them onto one package with the wrong file's code
            fpath = findings_file(repo, [
                {"title": "dup", "body": "", "evidence": "",
                 "file_path": "src/pkg/target.py", "line_start": 41},
                {"title": "dup", "body": "", "evidence": "",
                 "file_path": "src/pkg/sibling.py", "line_start": 2},
            ])
            rc, out, _ = run_ee("--repo", str(repo), "--findings", fpath)
            parsed = json.loads(out) if out.strip() else []
            dups = ([p for p in parsed if p.get("finding_title") == "dup"]
                    if isinstance(parsed, list) else [])
            c.check("findings: two findings sharing a title BOTH survive",
                    len(dups) == 2, f"{len(dups)} packages for 'dup'")
            c.check("findings: ...each carrying its OWN file's code, in input order",
                    len(dups) == 2 and "TARGET_SENTINEL" in dups[0].get("primary_code", "")
                    and "SIBLING_MARKER" in dups[1].get("primary_code", ""),
                    "wrong primary_code pairing")

    # ── 2b. the caps that had no rows: callers 10 · cross-refs 10 · blast 5 · slice 1200 ──
    with TempDir() as tmp:
        if c.block("2b · the caps that had no rows"):
            repo = tmp / "caps"
            repo.mkdir()
            write(repo, "lib/subject.py", "def capped_fn():\n    return 1\n")
            for i in range(14):
                write(repo, f"callers/c{i:02d}.py", f"capped_fn()  # CAP_CALLER_{i:02d}\n")
            for i in range(12):
                write(repo, f"refs/r{i:02d}.py", f"REF_MARKER_{i:02d} = {i}\n")
            for i in range(8):
                write(repo, f"blast/b{i}.py", f"x = capped_fn  # BLAST_CAP_{i}\n")

            body = ("`capped_fn` misbehaves. See "
                    + " and ".join(f"refs/r{i:02d}.py" for i in range(12)) + ".")
            fpath = findings_file(repo, [{
                "title": "caps", "body": body, "evidence": "",
                "file_path": "lib/subject.py", "line_start": 1,
            }])
            rc, out, _ = run_ee("--repo", str(repo), "--findings", fpath,
                                "--blast-radius", *[f"blast/b{i}.py" for i in range(8)])
            cap_pkg = pkg_for(out, "caps")
            c.check("findings: caller snippets cap at 10 (fixture offers 14)",
                    len(cap_pkg.get("caller_snippets", [])) == 10,
                    f"{len(cap_pkg.get('caller_snippets', []))} snippets")
            c.check("findings: cross-ref files cap at 10 (fixture names 12)",
                    len(cap_pkg.get("cross_ref_snippets", [])) == 10,
                    f"{len(cap_pkg.get('cross_ref_snippets', []))} snippets")
            blast_hits = sum(1 for i in range(8)
                             if f"BLAST_CAP_{i}" in cap_pkg.get("related_code", ""))
            c.check("findings: blast-radius snippets cap at 5 (fixture offers 8)",
                    blast_hits == 5, f"{blast_hits} blast snippets")

            write(repo, "lib/heavy.py",
                  "\n".join(f"import module_{i:03d}_{'x' * 40}" for i in range(40)) + "\n")
            rc, out, _ = run_ee("--repo", str(repo), "--pack", "lib/heavy.py")
            seg = out.split("_import/usage context:_ ", 1)[-1].split("\n```", 1)[0]
            c.check("pack: the import-context slice caps at exactly 1200 chars",
                    len(seg) == 1200, f"{len(seg)} chars")

    # ── 2c. caller snippets are RANKED by import, never filtered (SCC-187 A1) ──
    with TempDir() as tmp:
        if c.block("SCC-187-A1 · caller ranking"):
            repo = Path(tmp)
            build_python_repo(repo)
            # The stock fixture already carries both classes for `target_fn`:
            #   src/pkg/user_chain.py   `from pkg.target import target_fn` AND calls it -> importer
            #   caller_visible / sibling / blast_deep   call it, import nothing -> name-match
            # and the importer sorts LAST in the walk, so an unranked run puts it at the bottom.
            fpath = findings_file(repo, [{
                "title": "ranking",
                "body": "`target_fn` is wrong",
                "evidence": "",
                "file_path": "src/pkg/target.py",
                "line_start": 41,
            }])
            rc, out, err = run_ee("--repo", str(repo), "--findings", fpath)
            rank_pkg = pkg_for(out, "ranking")
            snippets = rank_pkg.get("caller_snippets", [])
            files = caller_files(rank_pkg)
            # Keyed to a SET, not last-write-wins: with one file contributing two snippets a
            # plain dict silently hides a mis-tag on the second one.
            tags: dict[str, set[str]] = {}
            for f, s in zip(files, snippets):
                tags.setdefault(f, set()).add(caller_tag(s))
            tag_of = {f: (next(iter(v)) if len(v) == 1 else f"MIXED{sorted(v)}")
                      for f, v in tags.items()}

            c.check("ranking: exits 0", rc == 0, f"exit {rc} err={err[:160]}")
            c.check("ranking: no file carries two different tags",
                    all(len(v) == 1 for v in tags.values()),
                    f"a file was tagged inconsistently: {tag_of}")
            # Ranking must not INVENT callers either. other_root.py imports target_fn and never
            # calls it, so it belongs in IMPORTED BY and nowhere in the caller list.
            c.check("ranking COUNTER-EXAMPLE: an importer that never CALLS is not a caller",
                    "src/pkg/other_root.py" not in files,
                    f"a non-calling importer leaked into the callers: {files}")
            c.check("ranking: a file that IMPORTS the subject is tagged [importer]",
                    tag_of.get("src/pkg/user_chain.py") == "[importer]",
                    f"user_chain tagged {tag_of.get('src/pkg/user_chain.py')!r}")
            c.check("ranking: a file that only NAME-MATCHES is tagged [name-match]",
                    tag_of.get("src/pkg/caller_visible.py") == "[name-match]",
                    f"caller_visible tagged {tag_of.get('src/pkg/caller_visible.py')!r}")
            # ⛔ The load-bearing row. Ranking must never become filtering: a hard import filter
            # would drop attribute-dispatch call sites, which the module docstring names as
            # exactly the shape a review needs to see. M1 is the mutant that proves this row.
            c.check("ranking: BOTH classes survive — ranking is not filtering",
                    "src/pkg/user_chain.py" in files and "src/pkg/caller_visible.py" in files,
                    f"a class was dropped; got {files}")
            # Computed defensively: an unranked run tags nothing, so a bare `min(...)` over the
            # name-match indices raises ValueError and the row DIES IN SETUP instead of failing.
            # A red that raises is indistinguishable from a red that asserts, and only one of
            # those is evidence.
            imp_at = files.index("src/pkg/user_chain.py") if "src/pkg/user_chain.py" in files else -1
            nm_at = [i for i, f in enumerate(files) if tag_of.get(f) == "[name-match]"]
            c.check("ranking: the importer sorts ahead of every name-match",
                    imp_at >= 0 and bool(nm_at) and imp_at < min(nm_at),
                    f"importer at {imp_at}, name-matches at {nm_at}, order is {files}")

    # ── 2d. a LATE importer survives both caps (SCC-187 A2) ───────────────────
    with TempDir() as tmp:
        if c.block("SCC-187-A2 · late importer"):
            repo = Path(tmp)
            write(repo, "pkg/__init__.py", "")
            write(repo, "pkg/target.py", "def target_fn(v):\n    return v\n")
            # 12 name-match callers that sort BEFORE the importer, so the walk fills its own
            # _CALLER_SNIPPETS cap before ever reaching it. Measured at plan time: on unranked
            # code the importer is resolved correctly and is ABSENT from the snippets entirely,
            # which is why a downstream sort alone cannot satisfy this row — the snippet was
            # never collected. Both the walk order and the cross-identifier sort are required.
            for i in range(12):
                write(repo, f"pkg/aa_{i:02d}_caller.py", "x = target_fn(1)  # NAME_MATCH\n")
            write(repo, "pkg/zz_importer.py",
                  "from pkg.target import target_fn\n\ny = target_fn(2)  # LATE_IMPORTER\n")

            fpath = findings_file(repo, [{
                "title": "late",
                "body": "`target_fn` is wrong",
                "evidence": "",
                "file_path": "pkg/target.py",
                "line_start": 1,
            }])
            rc, out, err = run_ee("--repo", str(repo), "--findings", fpath)
            late_pkg = pkg_for(out, "late")
            late_files = caller_files(late_pkg)

            c.check("late importer: exits 0", rc == 0, f"exit {rc} err={err[:160]}")
            c.check("late importer: it is COLLECTED despite sorting past the walk's own cap",
                    "pkg/zz_importer.py" in late_files,
                    f"the importer never made it into the snippets; got {late_files}")
            c.check("late importer: and it survives the cross-identifier slice at the top",
                    late_files[:1] == ["pkg/zz_importer.py"],
                    f"first snippet is {late_files[:1]}")
            c.check("late importer COUNTER-EXAMPLE: the cap still holds at 10",
                    len(late_files) == 10, f"{len(late_files)} snippets")

    # ── 2e. the OUTER sort, across identifiers (SCC-187 A2, second half) ──────
    with TempDir() as tmp:
        if c.block("SCC-187-A2b · the outer sort"):
            repo = Path(tmp)
            # Found by a SURVIVING MUTANT, not by design: 2d proves the walk order (`prefer`)
            # and nothing else. With one identifier the importer is collected first, so it is
            # already at index 0 and moving the sort after the slice changes nothing — M2 sailed
            # through. The outer sort only bites ACROSS identifiers: `_extract_one` concatenates
            # one caller list per mentioned identifier and slices the CONCATENATION, so a noisy
            # first identifier can fill all ten slots before a later identifier's importer hit
            # is ever considered. That is what this case pins.
            write(repo, "pkg/__init__.py", "")
            write(repo, "pkg/target.py",
                  "def aaa_fn(v):\n    return v\n\n\ndef zzz_fn(v):\n    return v\n")
            for i in range(12):                       # 12 > the 10-snippet cap, none an importer
                write(repo, f"pkg/n_{i:02d}.py", "x = aaa_fn(1)  # NOISE\n")
            write(repo, "pkg/zimporter.py",
                  "from pkg.target import zzz_fn\n\ny = zzz_fn(2)  # OUTER_SORT_IMPORTER\n")

            # Both identifiers named, `aaa_fn` FIRST — so its 10 hits arrive before zzz_fn's one.
            fpath = findings_file(repo, [{
                "title": "outer",
                "body": "`aaa_fn` is wrong, and so is `zzz_fn`",
                "evidence": "",
                "file_path": "pkg/target.py",
                "line_start": 1,
            }])
            rc, out, err = run_ee("--repo", str(repo), "--findings", fpath)
            outer_pkg = pkg_for(out, "outer")
            outer_files = caller_files(outer_pkg)

            c.check("outer sort: exits 0", rc == 0, f"exit {rc} err={err[:160]}")
            c.check("outer sort: a LATER identifier's importer is not crowded out by an "
                    "earlier identifier filling the cap",
                    "pkg/zimporter.py" in outer_files,
                    f"the importer was sliced away; got {outer_files}")
            c.check("outer sort COUNTER-EXAMPLE: the noise really did overflow the cap",
                    len(outer_files) == 10 and sum(1 for f in outer_files
                                                   if f.startswith("pkg/n_")) >= 9,
                    f"fixture did not overflow as intended; got {outer_files}")

    # ── 2f. the RESERVE: importers may never starve the name-match class ──────
    with TempDir() as tmp:
        if c.block("SCC-187-A1e · the reserve"):
            repo = Path(tmp)
            # Found by the review fan-out, and it was a REGRESSION: with enough importer call
            # sites to fill the walk's own cap, the pre-reserve code returned ten `[importer]`
            # snippets and ZERO name-matches — so attribute dispatch, the shape this module
            # exists to surface, vanished. Measured against origin/main, which returned the
            # opposite. Ordering may decide which evidence leads; never that a class is absent.
            write(repo, "pkg/__init__.py", "")
            write(repo, "pkg/target.py", "def target_fn(v):\n    return v\n")
            for i in range(12):                       # 12 importers that all CALL it
                write(repo, f"pkg/imp_{i:02d}.py",
                      "from pkg.target import target_fn\n\nx = target_fn(1)  # IMPORTER\n")
            # sorts FIRST, imports nothing, and is the attribute-dispatch shape
            write(repo, "pkg/aa_attr.py", "y = obj.target_fn(9)  # ATTR_DISPATCH\n")

            fpath = findings_file(repo, [{"title": "reserve", "body": "`target_fn` is wrong",
                                          "evidence": "", "file_path": "pkg/target.py",
                                          "line_start": 1}])
            rc, out, err = run_ee("--repo", str(repo), "--findings", fpath)
            res = pkg_for(out, "reserve")
            res_files = caller_files(res)
            res_tags = [caller_tag(s) for s in res.get("caller_snippets", [])]

            c.check("reserve: exits 0", rc == 0, f"exit {rc} err={err[:160]}")
            c.check("reserve: the name-match class SURVIVES a cap-filling importer group",
                    "pkg/aa_attr.py" in res_files,
                    f"attribute-dispatch caller starved out; got {res_files}")
            c.check("reserve: importers still lead", res_tags[:1] == ["[importer]"],
                    f"first tag is {res_tags[:1]}")
            c.check("reserve COUNTER-EXAMPLE: the cap still holds at 10",
                    len(res_files) == 10, f"{len(res_files)} snippets")
            c.check("reserve COUNTER-EXAMPLE: the fixture really did overfill with importers",
                    sum(1 for t in res_tags if t == "[importer]") == 9,
                    f"tags were {res_tags}")

    # ── 2g. tags on a subject NOTHING imports, and exact-not-substring ────────
    with TempDir() as tmp:
        if c.block("SCC-187-A1f · zero importers and exact membership"):
            repo = Path(tmp)
            # Both rows here killed a mutant that SURVIVED the whole suite before this block:
            # dropping the tag entirely when `importer_set` is empty (the common shape — a leaf
            # module nothing imports yet), and testing membership with a substring instead of an
            # exact path, which promotes `sub/util.py` over the real `util.py`.
            # The substring trap needs a REAL importer whose path is a suffix of a non-importer's
            # path: `util.py` imports the subject, `sub/util.py` only name-matches. A substring
            # test asks `"util.py" in "sub/util.py:1 | ..."` and wrongly promotes the decoy.
            write(repo, "pkg/__init__.py", "")
            write(repo, "pkg/target.py", "def target_fn(v):\n    return v\n")
            write(repo, "util.py",
                  "from pkg.target import target_fn\n\ny = target_fn(1)  # TRUE_IMPORTER\n")
            write(repo, "sub/__init__.py", "")
            write(repo, "sub/util.py", "z = target_fn(2)  # SUBSTRING_DECOY - imports nothing\n")
            write(repo, "lonely.py", "def lonely_fn(v):\n    return v\n")
            write(repo, "calls_lonely.py", "w = lonely_fn(2)  # NAME_MATCH_ONLY\n")

            zpath = findings_file(repo, [{"title": "zero", "body": "`lonely_fn` is wrong",
                                          "evidence": "", "file_path": "lonely.py",
                                          "line_start": 1}])
            rc, out, _ = run_ee("--repo", str(repo), "--findings", zpath)
            zero_pkg = pkg_for(out, "zero")
            zero_tags = [caller_tag(s) for s in zero_pkg.get("caller_snippets", [])]
            c.check("zero importers: snippets are STILL tagged, all [name-match]",
                    bool(zero_tags) and set(zero_tags) == {"[name-match]"},
                    f"tags were {zero_tags}")
            c.check("zero importers COUNTER-EXAMPLE: the caller really was found",
                    "calls_lonely.py" in caller_files(zero_pkg),
                    str(caller_files(zero_pkg)))

            spath = findings_file(repo, [{"title": "exact", "body": "`target_fn` is wrong",
                                          "evidence": "", "file_path": "pkg/target.py",
                                          "line_start": 1}])
            rc, out, _ = run_ee("--repo", str(repo), "--findings", spath)
            sub_pkg = pkg_for(out, "exact")
            sub_tags = dict(zip(caller_files(sub_pkg),
                                [caller_tag(s) for s in sub_pkg.get("caller_snippets", [])]))
            c.check("membership is EXACT: a path CONTAINING an importer's path is not promoted",
                    sub_tags.get("sub/util.py") == "[name-match]",
                    f"sub/util.py tagged {sub_tags.get('sub/util.py')!r} - substring match?")
            c.check("exact membership COUNTER-EXAMPLE: the real importer IS promoted",
                    sub_tags.get("util.py") == "[importer]",
                    f"util.py tagged {sub_tags.get('util.py')!r}; files={list(sub_tags)}")

    # ── 2h. a colon in a caller's path must not corrupt its tag ───────────────
    with TempDir() as tmp:
        if c.block("SCC-187-A1g · a colon in the path"):
            repo = Path(tmp)
            # `<rel>:<line>` is the snippet header, and a POSIX path may hold a colon, so the file
            # must be recovered from the header's LAST colon. Splitting on the first one cut
            # `pkg/a:b.py:3` to `pkg/a`, which is in no importer set — so a genuine importer was
            # labelled [name-match] while IMPORTED BY listed it, in the same JSON object.
            write(repo, "pkg/__init__.py", "")
            write(repo, "pkg/target.py", "def target_fn(v):\n    return v\n")
            write(repo, "pkg/a:b.py",
                  "from pkg.target import target_fn\n\nq = target_fn(1)  # COLON_IMPORTER\n")
            cpath = findings_file(repo, [{"title": "colon", "body": "`target_fn` is wrong",
                                          "evidence": "", "file_path": "pkg/target.py",
                                          "line_start": 1}])
            rc, out, _ = run_ee("--repo", str(repo), "--findings", cpath)
            colon_pkg = pkg_for(out, "colon")
            colon_tags = dict(zip(caller_files(colon_pkg),
                                  [caller_tag(s) for s in colon_pkg.get("caller_snippets", [])]))
            c.check("a colon in the path: the importer is still tagged [importer]",
                    colon_tags.get("pkg/a:b.py") == "[importer]",
                    f"tagged {colon_tags.get('pkg/a:b.py')!r}; files={list(colon_tags)}")
            c.check("a colon in the path COUNTER-EXAMPLE: the package does not contradict itself",
                    "pkg/a:b.py" in imported_by(colon_pkg.get("import_context", "")),
                    imported_by(colon_pkg.get("import_context", ""))[:120])

    # ── 2i. the precomputed importer list is really SPENT, not just accepted ──
    with TempDir() as tmp:
        if c.block("SCC-187-A1h · import_context in findings mode"):
            repo = Path(tmp)
            build_python_repo(repo)
            # Every IMPORTED BY *content* row in this file runs through --pack, which recomputes
            # internally; nothing proved the list `_extract_one` threads in is spent correctly.
            # A mutant passing `[]` here survived the entire suite before this row existed.
            ipath = findings_file(repo, [{"title": "ctx", "body": "`target_fn` is wrong",
                                          "evidence": "", "file_path": "src/pkg/target.py",
                                          "line_start": 41}])
            rc, out, _ = run_ee("--repo", str(repo), "--findings", ipath)
            ctx = imported_by(pkg_for(out, "ctx").get("import_context", ""))
            c.check("findings mode: IMPORTED BY carries the real importers",
                    "src/pkg/user_chain.py" in ctx, ctx[:160] or "empty")
            c.check("findings mode COUNTER-EXAMPLE: a same-package non-importer is absent",
                    "src/pkg/unrelated.py" not in ctx, ctx[:160])

    # ── 3. IMPORTED BY — the reason this subtask exists ───────────────────────
    with TempDir() as tmp:
        if c.block("3 · IMPORTED BY (python)"):
            repo = tmp / "repoA"
            repo.mkdir()
            build_python_repo(repo)

            rc, out, _ = run_ee("--repo", str(repo), "--pack", "scripts/flat_tool.py")
            line = imported_by(out)
            c.check("python flat: a bare `import flat_tool` on sys.path IS found",
                    "scripts/flat_user.py" in line, line or "no IMPORTED BY line")
            c.check("python flat COUNTER-EXAMPLE: `import flat_toolbox` is NOT a hit for flat_tool",
                    "scripts/box_user.py" not in line, line)
            c.check("python flat COUNTER-EXAMPLE: a nested checkout under .claude/worktrees is "
                    "NOT an importer",
                    ".claude/worktrees" not in line, line)

            # the OTHER leg of the nested-checkout prune: a DIRECT request for a worktrees path.
            # The walk prune cannot stop this one -- _resolve_rel joins the path straight to disk,
            # so only _under_skip_dir's pair clause refuses it. The re-review's one surviving
            # mutant deleted exactly that clause and scored a full pass; these two rows pin it.
            rc, out, err = run_ee("--repo", str(repo), "--pack",
                                  ".claude/worktrees/lane/scripts/wt_dup.py")
            c.check("pack: a DIRECT target inside .claude/worktrees is refused, with a note",
                    rc == 0 and out.strip() == "" and "note:" in err,
                    f"exit {rc} out={out[:80]!r}")
            fpath = findings_file(repo, [{"title": "wt", "body": "", "evidence": "",
                                          "file_path": ".claude/worktrees/lane/wt_caller.py",
                                          "line_start": 1}])
            rc, out, _ = run_ee("--repo", str(repo), "--findings", fpath)
            c.check("findings: a file_path inside .claude/worktrees yields empty primary_code",
                    pkg_for(out, "wt").get("primary_code", "x") == ""
                    and "CALLER_HIDDEN_MARKER" not in out,
                    out[:120])

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
        if c.block("3b · IMPORTED BY (ts/js)"):
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

    # a tsconfig that EXISTS but declares no `paths` means the repo has no alias; inventing
    # the `@/ -> src/` default there produces confident wrong resolutions
    with TempDir() as tmp:
        if c.block("3c · a tsconfig with no paths declares no alias"):
            repo = tmp / "repoC"
            repo.mkdir()
            write(repo, "tsconfig.json", json.dumps({"compilerOptions": {"strict": True}}))
            write(repo, "src/components/Thing.tsx", "export const Thing = () => null;\n")
            write(repo, "pages/uses.tsx", "import { Thing } from '@/components/Thing';\n")
            rc, out, _ = run_ee("--repo", str(repo), "--pack", "src/components/Thing.tsx")
            line = imported_by(out)
            c.check("ts: a tsconfig WITHOUT `paths` gets no invented alias root",
                    line.endswith("none"), line or "no IMPORTED BY line")

            repo = tmp / "repoD"
            repo.mkdir()
            write(repo, "src/components/Thing.tsx", "export const Thing = () => null;\n")
            write(repo, "pages/uses.tsx", "import { Thing } from '@/components/Thing';\n")
            rc, out, _ = run_ee("--repo", str(repo), "--pack", "src/components/Thing.tsx")
            line = imported_by(out)
            c.check("ts COUNTER-EXAMPLE: with NO config at all, the `@/ -> src/` default still applies",
                    "pages/uses.tsx" in line, line or "no IMPORTED BY line")

            # JSONC (comments, trailing commas) is legal in real tsconfigs and fails strict
            # json.loads -- the skip must be NAMED, or an aliased frontend silently reads
            # IMPORTED BY: none with no way to know why
            repo = tmp / "repoE"
            repo.mkdir()
            write(repo, "tsconfig.json",
                  '{\n  // a JSONC comment, legal for TypeScript, fatal for json.loads\n'
                  '  "compilerOptions": {"paths": {"@/*": ["./src/*"]}}\n}\n')
            write(repo, "src/components/Thing.tsx", "export const Thing = () => null;\n")
            write(repo, "pages/uses.tsx", "import { Thing } from '@/components/Thing';\n")
            rc, out, err = run_ee("--repo", str(repo), "--pack", "src/components/Thing.tsx")
            c.check("ts: an unparseable (JSONC) tsconfig is NAMED on stderr, never skipped silently",
                    "note:" in err and "tsconfig.json" in err, err[:160] or "silent skip")

    # ── 4. path normalization where the repo name recurs (D3) ─────────────────
    with TempDir() as tmp:
        if c.block("4 · path normalization where the repo name recurs"):
            repo = tmp / "myrepo"
            repo.mkdir()
            build_recurrence_repo(repo)
            rc, out, _ = run_ee("--repo", str(repo), "--pack", "myrepo/core.py")
            c.check("a path whose first segment repeats the repo name still resolves",
                    "RECURRENCE_SENTINEL" in out, out[:120] or "empty pack")

    # ── 4b. evidence never leaves the repo ────────────────────────────────────
    with TempDir() as tmp:
        if c.block("4b · evidence never leaves the repo"):
            repo = tmp / "inner"
            repo.mkdir()
            build_python_repo(repo)
            write(tmp, "outside_secret.py", "OUTSIDE_MARKER = 'must never be evidence'\n")

            rc, out, err = run_ee("--repo", str(repo), "--pack", "../outside_secret.py")
            c.check("pack: a relative path escaping the repo is refused",
                    rc == 0 and "OUTSIDE_MARKER" not in out and out.strip() == "",
                    f"exit {rc} out={out[:80]!r}")
            c.check("pack: ...and the refusal is on stderr", "note:" in err, err[:120] or "no note")

            fpath = findings_file(repo, [{"title": "escape", "body": "", "evidence": "",
                                          "file_path": "../outside_secret.py", "line_start": 1}])
            rc, out, _ = run_ee("--repo", str(repo), "--findings", fpath)
            esc = pkg_for(out, "escape")
            c.check("findings: an escaping file_path yields an empty package, not the file",
                    esc.get("primary_code", "x") == "" and "OUTSIDE_MARKER" not in out, out[:120])

    # ── 4c. non-ASCII content on a cp1252 console (the PC's default) ──────────
    with TempDir() as tmp:
        if c.block("4c · non-ASCII content on a cp1252 console"):
            repo = tmp / "uni"
            repo.mkdir()
            write(repo, "src/naive.py",
                  'label = "naïve café ✓"  # UNICODE_SENTINEL\n')
            env = {**os.environ, "PYTHONIOENCODING": "cp1252"}
            rc, out, err = run_ee("--repo", str(repo), "--pack", "src/naive.py", env=env)
            c.check("pack: non-ASCII repo content survives a cp1252 console",
                    rc == 0 and "UNICODE_SENTINEL" in out, f"exit {rc} err={err[:160]}")

    # ── 5. degrade, never die (plan D6) ───────────────────────────────────────
    with TempDir() as tmp:
        if c.block("5 · degrade, never die"):
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
            packages = json.loads(out) if out.strip() else []
            by_title = ({p.get("finding_title"): p for p in packages}
                        if isinstance(packages, list) else {})
            c.check("degrade: the missing-file package is empty, not absent",
                    by_title.get("gone", {}).get("primary_code", None) == "",
                    str(by_title.get("gone"))[:120])
            c.check("degrade: the missing file is NAMED in a stderr note, not skipped silently",
                    "note:" in err and "does_not_exist" in err, err[:200] or "stderr empty")
            # A finding with no line number reads from line 1. Anchored by EXACT first-line
            # equality: "1: # padding 1" as a substring also matches "11: # padding 11", which is
            # how a wrong fallback (line 41's window starts at 11) passed this row's earlier form.
            head = by_title.get("no line number", {}).get("primary_code", "")
            first = head.split("\n", 1)[0]
            c.check("degrade: an absent line_start falls back to the head of the file (line 1 exactly)",
                    first == "1: # padding 1", f"first emitted line is {first!r}")
            c.check("degrade: no traceback reaches stderr",
                    "Traceback" not in err, err[:160])

            # line_start 1e400 is legal JSON and parses to float infinity; int() then raises
            # OverflowError, which is NOT a ValueError. Uncaught, it escaped the thread pool and
            # took every finding's evidence down with it.
            overflow = repo / "_overflow.json"
            overflow.write_text('[{"title": "overflow line", "body": "", "evidence": "", '
                                '"file_path": "src/pkg/target.py", "line_start": 1e400}, '
                                '{"title": "bystander", "body": "", "evidence": "", '
                                '"file_path": "src/pkg/target.py", "line_start": 41}]',
                                encoding="utf-8")
            rc, out, err = run_ee("--repo", str(repo), "--findings", str(overflow))
            c.check("degrade: line_start 1e400 (JSON infinity) cannot kill the run",
                    rc == 0 and "Traceback" not in err, f"exit {rc} err={err[:200]}")
            over = pkg_for(out, "overflow line")
            c.check("degrade: ...it falls back to the file head",
                    over.get("primary_code", "").split("\n", 1)[0] == "1: # padding 1",
                    repr(over.get("primary_code", "")[:60]))
            c.check("degrade: ...and the BYSTANDER finding keeps its evidence",
                    "TARGET_SENTINEL" in pkg_for(out, "bystander").get("primary_code", ""),
                    "the poisoned finding took the healthy one down with it")

            # junk entries degrade IN PLACE: titles are not unique (the duplicate-title fix), so a
            # consumer's only reliable join is by index -- a silently dropped entry would misassign
            # every package after it. 4 in, 4 out, order kept, every field present.
            mixed = repo / "_mixed.json"
            mixed.write_text('[{"title": "first ok", "body": "", "evidence": "", '
                             '"file_path": "src/pkg/target.py", "line_start": 41}, '
                             '"just a string", '
                             '{"body": "titleless", "file_path": "src/pkg/target.py"}, '
                             '{"title": "last ok", "body": "", "evidence": "", '
                             '"file_path": "src/pkg/target.py", "line_start": 41}]',
                             encoding="utf-8")
            rc, out, err = run_ee("--repo", str(repo), "--findings", str(mixed))
            mixed_pkgs = json.loads(out) if out.strip() else []
            c.check("degrade: junk findings yield packages IN PLACE - 4 in, 4 out, order kept",
                    rc == 0 and isinstance(mixed_pkgs, list) and len(mixed_pkgs) == 4
                    and mixed_pkgs[0].get("finding_title") == "first ok"
                    and mixed_pkgs[3].get("finding_title") == "last ok",
                    f"exit {rc} len={len(mixed_pkgs) if isinstance(mixed_pkgs, list) else '-'}")
            pkg_fields = ("finding_title", "primary_code", "caller_snippets", "cross_ref_snippets",
                          "diff_hunk", "import_context", "related_code")
            c.check("degrade: the junk entries still carry every field",
                    len(mixed_pkgs) == 4
                    and all(k in mixed_pkgs[1] and k in mixed_pkgs[2] for k in pkg_fields),
                    "degraded package missing fields")

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

    # ── 5b. isolation and the diff splitter, proven in process ────────────────
    sys.path.insert(0, str(SCRIPTS))
    import evidence_extract as ee

    with TempDir() as tmp:
        if c.block("5d · a truncated importer walk must not ASSERT [name-match]"):
            # `[name-match]` is a claim that this file does NOT import the subject. A walk that
            # died on its deadline cannot support that claim — the file may simply sit past where
            # it stopped — and the only disclosure is a stderr note no consumer of stdout reads.
            # So a partial walk degrades the label to [unranked] rather than asserting a negative.
            trepo = tmp / "trunc"
            trepo.mkdir()
            write(trepo, "pkg/__init__.py", "")
            write(trepo, "pkg/target.py", "def target_fn(v):\n    return v\n")
            write(trepo, "pkg/caller.py", "u = target_fn(1)  # SOME_CALLER\n")

            real = ee._python_importers
            ee._python_importers = lambda repo, rel: ([], False)   # a walk that ran out of time
            try:
                trunc_pkg = ee._extract_one(str(trepo), {
                    "title": "t", "body": "`target_fn` is wrong", "evidence": "",
                    "file_path": "pkg/target.py", "line_start": 1}, {}, [])
            finally:
                ee._python_importers = real

            ttags = [caller_tag(s) for s in trunc_pkg.get("caller_snippets", [])]
            c.check("truncated walk: the tag degrades to [unranked], never [name-match]",
                    bool(ttags) and set(ttags) == {"[unranked]"},
                    f"tags were {ttags} - a partial walk asserted a negative")
            c.check("truncated walk COUNTER-EXAMPLE: a COMPLETE walk still says [name-match]",
                    {caller_tag(s) for s in ee._extract_one(str(trepo), {
                        "title": "t", "body": "`target_fn` is wrong", "evidence": "",
                        "file_path": "pkg/target.py", "line_start": 1}, {}, []
                    ).get("caller_snippets", [])} == {"[name-match]"},
                    "the control did not produce [name-match] - the row above proves nothing")

        if c.block("5b · isolation, in process"):
            repo = tmp / "repoA"
            repo.mkdir()
            build_python_repo(repo)

            class Poison(dict):
                """A finding whose every access raises: the shape no pre-screen can see coming."""

                def get(self, key, default=None):
                    raise RuntimeError("poisoned finding")

            cap = io.StringIO()
            try:
                with contextlib.redirect_stderr(cap):
                    packages = ee.extract_for_findings(
                        str(repo),
                        [Poison(), {"title": "healthy", "body": "", "evidence": "",
                                    "file_path": "src/pkg/target.py", "line_start": 41}],
                        {}, [])
            except Exception as exc:  # a raise here must be a RED ROW, not a dead guard --
                packages = []         # every row after this section would go unreported otherwise
                c.check("isolation: extract_for_findings must not raise in-process", False, repr(exc))
            c.check("isolation: a finding that raises degrades ALONE; its sibling keeps its evidence",
                    len(packages) == 2
                    and "TARGET_SENTINEL" in packages[1].get("primary_code", "")
                    and packages[0].get("primary_code") == "",
                    f"{len(packages)} packages")
            fields = ("finding_title", "primary_code", "caller_snippets", "cross_ref_snippets",
                      "diff_hunk", "import_context", "related_code")
            c.check("isolation: the degraded package still carries every field",
                    bool(packages) and all(f in packages[0] for f in fields),
                    f"missing={[f for f in fields if f not in packages[0]] if packages else 'all'}")
            c.check("isolation: the degradation is NAMED on stderr, not silent",
                    "degraded to an empty package" in cap.getvalue(),
                    cap.getvalue()[:120] or "silent")

    # header detection is positional: an added source line beginning `++ ` renders as `+++ `,
    # and an implementation that headers on the TEXT truncates the patch and invents a key
    if c.block("5c · the diff splitter"):
        tricky = ("diff --git a/real.py b/real.py\n"
                  "--- a/real.py\n"
                  "+++ b/real.py\n"
                  "@@ -1,4 +1,5 @@\n"
                  " context\n"
                  "+++ this ADDED line begins with two pluses\n"
                  "--- this REMOVED line begins with two minuses\n"
                  " more\n"
                  "diff --git a/second.py b/second.py\n"
                  "--- a/second.py\n"
                  "+++ b/second.py\n"
                  "@@ -1,1 +1,2 @@\n"
                  "+SECOND_FILE_LINE\n")
        split = ee.split_unified_diff(tricky)
        c.check("diff split: keys are exactly the two real files (no key invented from a body line)",
                sorted(split) == ["real.py", "second.py"], f"keys={sorted(split)}")
        c.check("diff split: an added `++ ...` body line stays IN the patch as content",
                "++ this ADDED line" in split.get("real.py", ""), split.get("real.py", "")[:120])
        c.check("diff split: a removed `-- ...` body line stays IN the patch as content",
                "-- this REMOVED line" in split.get("real.py", ""), split.get("real.py", "")[:120])

    # ── 6. no grep subprocess — proven by behaviour, not by grepping source ───
    with TempDir() as tmp:
        if c.block("6 · no grep subprocess"):
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
            blocked_pkg = pkg_for(out_d, "spawn-blocked path coverage")
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
    if c.block("7 · source-level tripwires"):
        code_only = "\n".join(ln for ln in src.splitlines() if not ln.strip().startswith("#"))
        c.check("tripwire: imports no subprocess module",
                "import subprocess" not in code_only, "subprocess import present")
        # Every import checked against the interpreter's own stdlib list: a name test for two
        # hand-picked packages let `import numpy` straight through.
        tops: set[str] = set()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                tops.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                tops.add(node.module.split(".")[0])
        non_stdlib = sorted(tops - set(sys.stdlib_module_names))
        c.check("tripwire: every import is stdlib (checked against sys.stdlib_module_names)",
                not non_stdlib, f"non-stdlib imports: {non_stdlib}")
        c.check("docstring records the GitNexus decision (plan D7)",
                "GitNexus" in src[:4000] and "machine-local" in src[:4000],
                "rationale missing from the module docstring")
        c.check("docstring records the port source and SHA",
                "8593130" in src[:4000] and "pr-af" in src[:4000], "provenance missing")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
