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

import ast
import importlib.util
import shutil
import subprocess
import sys
import threading
import time
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

    # ── CASE · a multi-match is NAMED, never collapsed into a count (SCC-156 #1) ─────────
    if c.block("CASE · a multi-match names every block that ran"):
        # `--case "E"` on a 40-block file ran all 40 and the sweep recorded "killed by case
        # E". Substring stays (a family prefix is a legitimate multi-select); what changed is
        # that the transcript lists every matched label, so attribution reads NAMES.
        with TempDir() as t:
            d = sandbox(t, FAKE)
            rc, out = run(d / "test_fake.py", "--case", "the")     # matches all three
            c.check("CASE · a multi-match still runs every matching block",
                    rc == 0 and "matched 3/3 blocks" in out, out[-300:])
            c.check("CASE · ...and the transcript NAMES each matched block",
                    "-- matched blocks: ALPHA · the first block | BETA · the second block | "
                    "GAMMA · the third block --" in out, out[-300:])
            rc, out = run(d / "test_fake.py", "--case", "BETA")
            c.check("CASE · a single match prints no matched-blocks line (the count suffices)",
                    rc == 0 and "matched 1/3 blocks" in out and "matched blocks:" not in out,
                    out[-300:])

    # ── CASE · the `--case=<label>` spelling is the same contract (SCC-156 #3) ───────────
    if c.block("CASE · the --case=<label> spelling runs only its block"):
        with TempDir() as t:
            d = sandbox(t, FAKE)
            rc, out = run(d / "test_fake.py", "--case=BETA")
            c.check("CASE · --case=BETA runs only BETA",
                    rc == 0 and "BETA · one" in out and "ALPHA · one" not in out
                    and "-- 1/1 passed --" in out, f"rc={rc} out={out!r}")
            rc, out = run(d / "test_fake.py", "--case=this-label-matches-nothing")
            c.check("CASE · --case=<typo> is exit 3, same as the two-token form",
                    rc == 3 and "NO CASES RAN" in out, f"rc={rc} out={out!r}")

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

    # ── CASE · ⛔ A LOST LABEL IS THE SAME ERROR AS A TYPO'D ONE ─────────────────────────
    # All five review lenses found this independently, which is the signal that it is not a
    # nitpick. `_case_filter` returned None for a bare trailing `--case`, and None means
    # UNFILTERED — so the sweep ran the whole file, printed no filter line at all, and exited
    # 0/1. `--case ""` and `--case=` were worse: the empty string is `in` every label, so all
    # blocks ran while a filter note claimed `matched N/N`.
    #
    # Both are the shape `NO_MATCH` exists for — "the label was lost" — and both landed on the
    # two codes it exists to avoid. The cost is not wall-clock: a mutant that dies to ANY case
    # in the file is recorded as killed by a named case that never ran in isolation, so the
    # mutation record certifies a boundary nothing holds. This repo already carries the memory
    # for the shell half of it (`zsh-does-not-word-split-gate-args`): an empty variable does
    # not become an empty argument, it vanishes, turning `--case "$L"` into a bare `--case`.
    if c.block("CASE · ⛔ a LOST label (bare --case, empty value) is exit 3, not a full run"):
        with TempDir() as t:
            d = sandbox(t, FAKE)
            rc, out = run(d / "test_fake.py", "--case")
            c.check("CASE · a bare trailing --case exits 3, never a silent full run",
                    rc == 3, f"rc={rc} out={out!r}")
            c.check("CASE · ...and says the label was lost, not that nothing matched",
                    "no label" in out.lower(), out)
            rc2, out2 = run(d / "test_fake.py", "--case", "")
            c.check("CASE · an EMPTY --case value exits 3 (it matched every block before)",
                    rc2 == 3, f"rc={rc2} out={out2!r}")
            rc3, out3 = run(d / "test_fake.py", "--case=")
            c.check("CASE · the --case= spelling of the same mistake also exits 3",
                    rc3 == 3, f"rc={rc3} out={out3!r}")
            # ⭐ THE CONTROL. Refusing an empty label must not refuse a real one, and the
            # `--case=<label>` form is shipped, advertised in the docstring, and was covered
            # by nothing (Test-Adequacy lens) — so it is pinned here rather than assumed.
            rc4, out4 = run(d / "test_fake.py", "--case=BETA")
            c.check("CASE · CONTROL the --case=<label> form still selects its block",
                    rc4 == 0 and "matched 1/3" in out4, f"rc={rc4} out={out4!r}")
            # A WHITESPACE-ONLY value is the same lost label wearing a space: `" " in label`
            # is True for every label, so without the strip it ran everything, printed
            # `matched 3/3`, and exited 0 (SCC-160 review, Blind Hunter — the hole SCC-156
            # closed for "" re-opened one character over).
            rc5, out5 = run(d / "test_fake.py", "--case", "  ")
            c.check("CASE · a whitespace-only --case value is exit 3 (lost label), never a full run",
                    rc5 == 3 and "no label" in out5 and "matched 0/3" in out5,
                    f"rc={rc5} out={out5!r}")

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

    # ── RUNALL · ⛔ THE DELIVERABLE ITSELF HAD NO KILLER CASE ─────────────────────────────
    # Two review lenses independently copied the runner to a scratch dir, pinned
    # `max_workers=1`, and watched the file stay green. Every assertion above — the summary
    # line, the FAILED list, the exit codes, the alphabetical order — holds IDENTICALLY in
    # serial, because ordering comes from `ex.map` yielding in INPUT order, not from overlap.
    # So the one thing this ticket exists to deliver, a 186 s wall becoming 69 s, was the one
    # thing nothing could see. That is precisely the WIDTH-mutant class the rule file this
    # same lane edits now demands be killed by a named case.
    #
    # The pin is causal, not a race: four stubs that each sleep, run at a width that MUST
    # overlap. Serial cannot finish inside the serial floor, so the margin is structural.
    if c.block("RUNALL · ⭐ the pool is genuinely CONCURRENT, and stderr survives it"):
        def suite2(root: Path, files: dict[str, str]) -> Path:
            d = root / "s2"
            d.mkdir(exist_ok=True)
            shutil.copy2(RUN_ALL, d / "run_all.py")
            shutil.copy2(HARNESS, d / "_harness.py")
            for n, body in files.items():
                (d / n).write_text(body, encoding="utf-8")
            return d

        SLEEP = 0.7
        NFILES = 4
        slow = {f"test_s{i}.py": (f"import sys, time\ntime.sleep({SLEEP})\n"
                                  f"print('S{i}')\nsys.exit(0)\n") for i in range(NFILES)}
        with TempDir() as t:
            d = suite2(t, slow)
            t0 = time.monotonic()
            rc_p, out_p = run(d / "run_all.py", "--jobs", str(NFILES))
            wall_p = time.monotonic() - t0

            t0 = time.monotonic()
            rc_s, out_s = run(d / "run_all.py", "--serial")
            wall_s = time.monotonic() - t0

            serial_floor = SLEEP * NFILES                      # 2.8 s of unavoidable sleeping
            c.check("RUNALL · --serial really is serial (wall >= the sum of the sleeps)",
                    rc_s == 0 and wall_s >= serial_floor,
                    f"serial wall {wall_s:.2f}s vs floor {serial_floor:.2f}s")
            c.check("RUNALL · the default pool OVERLAPS — a width-1 pool cannot reach this wall",
                    rc_p == 0 and wall_p < serial_floor * 0.6,
                    f"parallel wall {wall_p:.2f}s vs serial {wall_s:.2f}s "
                    f"(floor {serial_floor:.2f}s)")
            c.check("RUNALL · ...and overlapping did not cost a single file",
                    f"{NFILES}/{NFILES} files passed" in out_p
                    and f"{NFILES}/{NFILES} files passed" in out_s, out_p[-200:])

        # STDERR. `run_one` concatenates stdout + stderr, and every existing stub prints to
        # stdout only — so a lens dropped `+ (r.stderr or "")` and the file stayed green. The
        # cost of that regression is the worst kind: a file dies on an uncaught exception, the
        # transcript names it in `FAILED:` and shows no traceback at all.
        with TempDir() as t:
            d = suite2(t, {"test_boom.py": "import sys\n"
                                           "sys.stderr.write('BOOM-TRACEBACK\\n')\n"
                                           "sys.exit(1)\n"})
            rc_p, out_p = run(d / "run_all.py")
            rc_s, out_s = run(d / "run_all.py", "--serial")
            c.check("RUNALL · a child's STDERR reaches the transcript in PARALLEL mode",
                    rc_p == 1 and "BOOM-TRACEBACK" in out_p, out_p[-300:])
            c.check("RUNALL · ...and in serial mode, identically",
                    rc_s == 1 and "BOOM-TRACEBACK" in out_s, out_s[-300:])

    # ── RUNALL · ⛔ zero files is exit 2, never `0/0 files passed` (SCC-156 #7) ────────────
    if c.block("RUNALL · zero files is exit 2, never a green 0/0"):
        # The vacuous-green class one level UP from the harness's exit-3 rule: a tests dir
        # that lost its files (bad checkout, sparse clone, wrong root) must not print a PASS
        # line a receipt could adopt to authorize a gate SKIP.
        with TempDir() as t:
            d = t / "empty"
            d.mkdir()
            shutil.copy2(RUN_ALL, d / "run_all.py")
            rc, out = run(d / "run_all.py")
            c.check("RUNALL · an empty tests dir exits 2 (misconfigured, not a result)",
                    rc == 2, f"rc={rc} out={out!r}")
            c.check("RUNALL · ...names the reason and prints NO `files passed` line",
                    "no test_*.py files found" in out and "files passed" not in out,
                    out[-300:])

    # ── RUNALL · an interrupt STOPS the run — queue cancelled, children ended (SCC-156 #4) ─
    if c.block("RUNALL · an interrupt cancels queued files AND ends running children"):
        # The review's one-word fix (`cancel_futures=True`) was measured insufficient while
        # pinning it: `Executor.map` already cancels the queue when its iteration dies, so the
        # mutant survived. What actually made an 88 s suite unstoppable was `shutdown(wait=True)`
        # WAITING for the N children already running. So the pin drives a REAL interrupt
        # (`_thread.interrupt_main`, cross-platform — no signal plumbing) into a pool of real
        # sleeping children and requires all three: the interrupt propagates, the queued file
        # never starts, and the running children are gone well before their sleep would end.
        import _thread
        import signal
        # `_thread.interrupt_main` is a documented no-op when SIGINT is ignored - and a
        # process launched from `sh -c '... &'`, cron, or a wrapper INHERITS SIG_IGN, so
        # under those launchers the interrupt never fires and both blocks would run their
        # children to completion as a false red (edge-case lens). Install the default
        # handler for the duration of these blocks and restore it after.
        prev_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal.default_int_handler)

        def fire_when(ready, deadline: float = 8.0) -> threading.Thread:
            """Interrupt the main thread once `ready()` is true (or the deadline passes) -
            never on a fixed timer: under a loaded machine two children may not have
            registered/started within a second, and firing early tests nothing."""
            def go():
                end = time.monotonic() + deadline
                while time.monotonic() < end and not ready():
                    time.sleep(0.05)
                _thread.interrupt_main()
            th = threading.Thread(target=go, daemon=True)
            th.start()
            return th

        with TempDir() as t:
            d = t / "intr"
            d.mkdir()
            shutil.copy2(RUN_ALL, d / "run_all.py")
            SLEEP = 6.0
            for i in range(3):
                (d / f"test_i{i}.py").write_text(
                    f"import sys, time\nprint('START{i}', flush=True)\ntime.sleep({SLEEP})\n"
                    f"print('END{i}')\nsys.exit(0)\n", encoding="utf-8")
            spec = importlib.util.spec_from_file_location("run_all_intr", d / "run_all.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            files = ["test_i0.py", "test_i1.py", "test_i2.py"]

            t0 = time.monotonic()
            interrupted = False
            try:
                fire_when(lambda: len(mod._RUNNING) == 2)   # both in flight, one queued
                mod.run_pool(files, 2)
            except KeyboardInterrupt:
                interrupted = True
            wall = time.monotonic() - t0
            # Give terminated children a moment to be reaped by their worker threads.
            deadline = time.monotonic() + 3.0
            while mod._RUNNING and time.monotonic() < deadline:
                time.sleep(0.05)
            c.check("RUNALL · the interrupt propagates out of run_pool (not swallowed)",
                    interrupted, f"wall={wall:.2f}s")
            c.check("RUNALL · running children are ENDED, not waited out",
                    interrupted and not mod._RUNNING and wall < SLEEP - 1.0,
                    f"still running={len(mod._RUNNING)} wall={wall:.2f}s (sleep was {SLEEP}s)")
            # The queued third file must never have started: its START line never printed.
            # We cannot read the pool's transcript after the raise, so ask the children
            # themselves — a started child writes a marker file.
        with TempDir() as t:
            d = t / "intr2"
            d.mkdir()
            shutil.copy2(RUN_ALL, d / "run_all.py")
            for i in range(3):
                (d / f"test_j{i}.py").write_text(
                    f"import sys, time, pathlib\n"
                    f"pathlib.Path(__file__).with_suffix('.started').write_text('1')\n"
                    f"time.sleep(6)\nsys.exit(0)\n", encoding="utf-8")
            spec = importlib.util.spec_from_file_location("run_all_intr2", d / "run_all.py")
            mod2 = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod2)
            both = lambda: (d / "test_j0.started").exists() and (d / "test_j1.started").exists()
            try:
                fire_when(both)      # interrupt only once both in-flight children have started
                mod2.run_pool(["test_j0.py", "test_j1.py", "test_j2.py"], 2)
            except KeyboardInterrupt:
                pass
            time.sleep(0.5)
            started = sorted(p.name for p in d.glob("*.started"))
            c.check("RUNALL · the queued file never starts after the interrupt",
                    started == ["test_j0.started", "test_j1.started"], f"started={started}")
        signal.signal(signal.SIGINT, prev_sigint)
        # Control: the same pool, uninterrupted, runs every file in order with no failures.
        spec = importlib.util.spec_from_file_location("run_all_under_test", RUN_ALL)
        mod3 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod3)
        ran: list[str] = []
        files = [f"test_q{i}.py" for i in range(6)]
        fails = mod3.run_pool(files, 1, runner=lambda n: (ran.append(n), (n, 0, ""))[1])
        c.check("RUNALL · control: an uninterrupted pool runs every file, in order, no failures",
                ran == files and fails == [], f"ran={ran} fails={fails}")

    # ── ORPHAN · no `c.check` outside every block, AST-verified (SCC-156 #8) ─────────────
    if c.block("ORPHAN · every c.check in a wired file sits under a c.block guard"):
        # A `c.check` outside every `if c.block(...)` runs under EVERY filter and counts
        # toward EVERY filtered tally — a mutant it kills is attributed to whichever case
        # was named. Zero exist today; the reviewer CREATED one mid-review and caught it
        # only by reading a count. This walks the AST so the count is no longer the guard.
        def orphans(path: Path) -> list[int]:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            # Each child remembers its parent AND which field it sits in: a `c.check` in
            # the `else:` of `if c.block(...)` runs under every filter that does NOT match
            # that block - it is an orphan wearing the guard's clothes (review, Blind
            # Hunter), so only the If's BODY counts as guarded.
            for parent in ast.walk(tree):
                for field, value in ast.iter_fields(parent):
                    kids = value if isinstance(value, list) else [value]
                    for child in kids:
                        if isinstance(child, ast.AST):
                            child._parent = parent  # type: ignore[attr-defined]
                            child._field = field    # type: ignore[attr-defined]
            found: list[int] = []
            for n in ast.walk(tree):
                if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and n.func.attr == "check" and isinstance(n.func.value, ast.Name)
                        and n.func.value.id == "c"):
                    continue
                a = n
                guarded = False
                while hasattr(a, "_parent"):
                    via = a._field  # type: ignore[attr-defined]
                    a = a._parent   # type: ignore[attr-defined]
                    if (isinstance(a, ast.If) and isinstance(a.test, ast.Call)
                            and isinstance(a.test.func, ast.Attribute)
                            and a.test.func.attr == "block" and via == "body"):
                        guarded = True
                        break
                if not guarded:
                    found.append(n.lineno)
            return found

        wired = [p for p in sorted(HERE.glob("test_*.py"))
                 if "c.block(" in p.read_text(encoding="utf-8")]
        c.check("ORPHAN · at least one wired file was found to inspect (the case is not vacuous)",
                len(wired) >= 1, f"wired={[p.name for p in wired]}")
        for p in wired:
            o = orphans(p)
            c.check(f"ORPHAN · {p.name} has no c.check outside a c.block guard",
                    o == [], f"c.check not under an `if c.block(...):` BODY at lines {o} - "
                             f"that is the only guard idiom this walker recognises")
        # The walker must be able to SEE an orphan, or the loop above proves nothing.
        with TempDir() as t:
            bad = t / "test_orphan.py"
            bad.write_text("def main():\n    c = None\n    if c.block('A'):\n"
                           "        c.check('a', True)\n    c.check('orphan', True)\n",
                           encoding="utf-8")
            c.check("ORPHAN · control: the walker flags a planted orphan at its line",
                    orphans(bad) == [5], f"got {orphans(bad)}")
            bad2 = t / "test_orphan_else.py"
            bad2.write_text("def main():\n    c = None\n    if c.block('A'):\n"
                            "        c.check('a', True)\n    else:\n"
                            "        c.check('runs-when-A-does-NOT', True)\n",
                            encoding="utf-8")
            c.check("ORPHAN · control: a c.check in the ELSE of a block guard is an orphan",
                    orphans(bad2) == [6], f"got {orphans(bad2)}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
