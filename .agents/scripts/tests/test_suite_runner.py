"""The suite's own runners: the harness `--case` block filter, and run_all's job control.

SCC-156. Every case here drives the REAL files as subprocesses against a throwaway tests
directory — a copied `_harness.py` plus fabricated `test_*.py` bodies — never a grep of
their source. That shape is deliberate: the thing under test IS the exit code and the
printed tally, and a source-grep guard cannot see either (SCC-125).

⛔ The exit contract this file pins, because a sweep's verdict rides on it:
    0  filter matched, every case that ran passed
    1  cases ran and at least one FAILED
    3  the filter selected NOTHING to run — a typo'd label, an unwired file, or a matched
       block that executed zero checks. Never 0: a vacuous green reads as SURVIVED in a
       mutation sweep, which is the exact lie the filter exists to make cheap, not cheaper.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases, TempDir  # noqa: E402

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "_harness.py"
RUN_ALL = HERE / "run_all.py"

# Three blocks, four checks. ALPHA carries two so a filtered tally is distinguishable from
# an unfiltered one by COUNT alone, not just by which names printed.
FAKE = '''\
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases


def main() -> int:
    c = Cases("fake suite")
    if c.block("ALPHA · the first block"):
        c.check("ALPHA · one", True)
        c.check("ALPHA · two", True)
    if c.block("BETA · the second block"):
        c.check("BETA · one", True)
    if c.block("GAMMA · the third block"):
        c.check("GAMMA · one", True)
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
'''

# A block that matches and then runs no checks at all. Without the exit-3 rule this file
# prints "-- 0/0 passed --" and exits 0 — a filter that selected nothing, reporting success.
FAKE_EMPTY_BLOCK = '''\
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases


def main() -> int:
    c = Cases("fake empty")
    if c.block("HOLLOW · matches but asserts nothing"):
        pass
    if c.block("REAL · has a case"):
        c.check("REAL · one", True)
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
'''

# No block() call anywhere — the shape of the 23 files this lane does NOT wire. Asking one
# for a case must be a hard error, never a silent full-file run that a sweep would time.
FAKE_UNWIRED = '''\
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases


def main() -> int:
    c = Cases("fake unwired")
    c.check("plain · one", True)
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
'''

FAKE_FAILING = '''\
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases


def main() -> int:
    c = Cases("fake failing")
    if c.block("ALPHA · the first block"):
        c.check("ALPHA · one", True)
    if c.block("BETA · the second block"):
        c.check("BETA · one", False, "on purpose")
    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
'''


def sandbox(root: Path, body: str, name: str = "test_fake.py") -> Path:
    """A throwaway tests dir holding the REAL harness and a fabricated test file."""
    d = root / "t"
    d.mkdir(exist_ok=True)
    shutil.copy2(HARNESS, d / "_harness.py")
    (d / name).write_text(body, encoding="utf-8")
    return d


def run(path: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(path), *args],
                       capture_output=True, text=True, errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    c = Cases("suite runners — --case filter and run_all job control")

    # ── CASE · the unfiltered contract is untouched ─────────────────────────────────────
    if c.block("CASE · the unfiltered contract is untouched"):
        with TempDir() as t:
            d = sandbox(t, FAKE)
            rc, out = run(d / "test_fake.py")
            c.check("CASE · unfiltered runs every block", rc == 0 and "-- 4/4 passed --" in out,
                    f"rc={rc} out={out!r}")
            # Positive evidence REQUIRED on both halves: a crashing harness prints no filter
            # note either, and would score this green while proving nothing.
            c.check("CASE · unfiltered prints no filter note",
                    rc == 0 and "-- 4/4 passed --" in out and "filter" not in out.lower(), out)

    # ── CASE · a filter runs ONLY its block ─────────────────────────────────────────────
    if c.block("CASE · a filter runs ONLY its block"):
        with TempDir() as t:
            d = sandbox(t, FAKE)
            rc, out = run(d / "test_fake.py", "--case", "BETA")
            c.check("CASE · --case runs only the matching block",
                    rc == 0 and "BETA · one" in out and "ALPHA · one" not in out,
                    f"rc={rc} out={out!r}")
            c.check("CASE · the filtered tally counts only what ran",
                    "-- 1/1 passed --" in out, out)

    # ── CASE · matching is substring, case-insensitive ──────────────────────────────────
    if c.block("CASE · matching is substring, case-insensitive"):
        with TempDir() as t:
            d = sandbox(t, FAKE)
            rc, out = run(d / "test_fake.py", "--case", "beta")
            c.check("CASE · match is case-insensitive", rc == 0 and "BETA · one" in out,
                    f"rc={rc} out={out!r}")
            rc, out = run(d / "test_fake.py", "--case", "second")
            c.check("CASE · match is a substring of the label, not the whole label",
                    rc == 0 and "BETA · one" in out, f"rc={rc} out={out!r}")

    # ── CASE · ⛔ zero match is exit 3, never a green ────────────────────────────────────
    if c.block("CASE · ⛔ zero match is exit 3, never a green"):
        with TempDir() as t:
            d = sandbox(t, FAKE)
            rc, out = run(d / "test_fake.py", "--case", "NOSUCHBLOCK")
            c.check("CASE · a typo'd label exits 3", rc == 3, f"rc={rc} out={out!r}")
            c.check("CASE · the zero-match message names the filter",
                    "NOSUCHBLOCK" in out and "0/3" in out, out)
            c.check("CASE · zero match runs no cases at all", rc == 3 and "[PASS]" not in out,
                    out)

    # ── CASE · ⛔ an unwired file cannot be filtered — exit 3, not a full run ────────────
    if c.block("CASE · ⛔ an unwired file cannot be filtered — exit 3, not a full"):
        with TempDir() as t:
            d = sandbox(t, FAKE_UNWIRED)
            rc, out = run(d / "test_fake.py", "--case", "plain")
            c.check("CASE · a file declaring no blocks exits 3 under a filter", rc == 3,
                    f"rc={rc} out={out!r}")
            c.check("CASE · the unwired file still runs green unfiltered",
                    run(d / "test_fake.py")[0] == 0, "")

    # ── CASE · ⛔ a matched block that asserts nothing is exit 3 (the vacuous green) ─────
    if c.block("CASE · ⛔ a matched block that asserts nothing is exit 3 (the vac"):
        with TempDir() as t:
            d = sandbox(t, FAKE_EMPTY_BLOCK)
            rc, out = run(d / "test_fake.py", "--case", "HOLLOW")
            c.check("CASE · a matched block running zero checks exits 3", rc == 3,
                    f"rc={rc} out={out!r}")
            rc, out = run(d / "test_fake.py", "--case", "REAL")
            c.check("CASE · a sibling block with a real case still exits 0", rc == 0,
                    f"rc={rc} out={out!r}")

    # ── CASE · a failure inside the filter is 1, distinct from 3 ────────────────────────
    if c.block("CASE · a failure inside the filter is 1, distinct from 3"):
        with TempDir() as t:
            d = sandbox(t, FAKE_FAILING)
            rc, out = run(d / "test_fake.py", "--case", "BETA")
            # A crash also exits 1, so the filter must be PROVEN to have run — the named case
            # printed, its sibling block absent — before this row means anything.
            c.check("CASE · a failing filtered case exits 1, not 3",
                    rc == 1 and "BETA · one" in out and "ALPHA · one" not in out,
                    f"rc={rc} out={out!r}")
            c.check("CASE · the FAILED line still names the case", "FAILED: BETA · one" in out,
                    out)
            rc, out = run(d / "test_fake.py")
            c.check("CASE · unfiltered failure is still exit 1",
                    rc == 1 and "ALPHA · one" in out and "-- 1/2 passed --" in out,
                    f"rc={rc} out={out!r}")

    # ── RUNALL · parallel and serial are the same contract ──────────────────────────────
    if c.block("RUNALL · parallel and serial are the same contract"):
        # The summary line and the exit code are consumed by CI, by four command bodies and by
        # gate_receipt's classifier. Parallelism may change the WALL, and nothing else.
        def suite(root: Path, files: dict[str, str]) -> Path:
            d = root / "s"
            d.mkdir(exist_ok=True)
            shutil.copy2(RUN_ALL, d / "run_all.py")
            shutil.copy2(HARNESS, d / "_harness.py")
            for n, body in files.items():
                (d / n).write_text(body, encoding="utf-8")
            return d

        def stub(marker: str, rc: int = 0, sleep: float = 0.0) -> str:
            return (f"import sys, time\ntime.sleep({sleep})\n"
                    f"print({marker!r})\nsys.exit({rc})\n")

        GREEN3 = {"test_a.py": stub("AAA"), "test_m.py": stub("MMM"),
                  "test_z.py": stub("ZZZ")}

        with TempDir() as t:
            d = suite(t, GREEN3)
            rc_p, out_p = run(d / "run_all.py")
            rc_s, out_s = run(d / "run_all.py", "--serial")
            c.check("RUNALL · all-green summary is unchanged",
                    rc_p == 0 and "3/3 files passed" in out_p, f"rc={rc_p} out={out_p!r}")
            c.check("RUNALL · --serial gives the identical summary and exit",
                    rc_s == rc_p and "3/3 files passed" in out_s, f"rc={rc_s} out={out_s!r}")
            c.check("RUNALL · every file's output is present in both modes",
                    all(m in out_p and m in out_s for m in ("AAA", "MMM", "ZZZ")),
                    f"parallel={out_p!r} serial={out_s!r}")

        with TempDir() as t:
            # The slowest file sorts FIRST: if output were printed as futures resolve, the fast
            # ones would jump the queue and the transcript would stop being diffable run to run.
            d = suite(t, {"test_a.py": stub("AAA", sleep=0.6), "test_z.py": stub("ZZZ")})
            rc, out = run(d / "run_all.py")
            c.check("RUNALL · output order stays alphabetical, not completion order",
                    rc == 0 and out.index("AAA") < out.index("ZZZ"), out)

        with TempDir() as t:
            d = suite(t, {"test_a.py": stub("AAA"), "test_b.py": stub("BBB", rc=1),
                          "test_c.py": stub("CCC", rc=1)})
            rc_p, out_p = run(d / "run_all.py")
            rc_s, out_s = run(d / "run_all.py", "--serial")
            c.check("RUNALL · a red file reds the run in parallel",
                    rc_p == 1 and "1/3 files passed" in out_p, f"rc={rc_p} out={out_p!r}")
            c.check("RUNALL · the FAILED list names every failure, in file order",
                    "FAILED: test_b.py, test_c.py" in out_p, out_p)
            c.check("RUNALL · serial reds identically",
                    rc_s == 1 and "FAILED: test_b.py, test_c.py" in out_s, out_s)

        with TempDir() as t:
            d = suite(t, GREEN3)
            rc1, out1 = run(d / "run_all.py", "--jobs", "1")
            c.check("RUNALL · --jobs 1 is a legal degenerate run",
                    rc1 == 0 and "3/3 files passed" in out1, f"rc={rc1} out={out1!r}")
            rc0, _ = run(d / "run_all.py", "--jobs", "0")
            c.check("RUNALL · --jobs 0 is refused, not silently treated as unlimited",
                    rc0 == 2, f"rc={rc0}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
