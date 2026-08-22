"""mutation_sweep.py — run a declared mutant table, and PROVE the tree came back (SCC-179).

The sweep was prose in two places (`smh-quick-dev.md`, `.agents/rules/tests-must-gate-for-real.md`)
and every clause of it was self-reported. It failed live twice:

  * SCC-144 — a timeout killed the sweep mid-mutant and left residue in the tree, where it is
    indistinguishable from the author's own edits.
  * 8681d83 — a mutant was COMMITTED AND PUSHED into the gate. The scoped `--case` re-runs never
    exercised the mutated pattern, so nothing was red until a receipt failed later: a diagnosis,
    a fix commit, and another full suite run.

Both are things a script can check and a paragraph cannot. This is that script.

    mutation_sweep.py --table sweep.json [--repo .]

THE TABLE (JSON). `test` is the command that runs the test file, WITHOUT any case filter -
the sweep appends `--case <kills>` itself, and runs it bare once at the end:

    {
      "test": ["python3", ".agents/scripts/tests/test_gate_receipt.py"],
      "mutants": [
        {"id":  "M1 widen the exemption to all of _artifacts/",
         "file": ".agents/scripts/gate_receipt.py",
         "original": "<exact text, must occur EXACTLY once>",
         "mutated":  "<what to replace it with>",
         "case":  "J3c",
         "block": "SCC-178"}
      ]
    }

`case` is the label that must appear on the runner's `FAILED:` line — that is ATTRIBUTION.
`block` is what gets passed to `--case`, and the harness filters by BLOCK label, not case label —
that is SELECTION. They are different namespaces and conflating them is a sweep that cannot run:
`--case "J3c"` matches no block, the harness exits 3, and the sweep correctly refuses to call that
a kill. `block` defaults to `case` for a file whose blocks and cases share a prefix. A mutant may
also carry its own `"test"` to override the table's.

`"unfiltered": true` runs the whole file instead, and is the ONLY honest answer for a test
file that declares no `c.block()` at all (`test_label_tasks.py`): there is no label to
select, so a filter - any filter - matches nothing, the harness exits 3, and every mutant
comes back a sweep error rather than a result. ⛔ It is not a convenience switch. Selection
exists so the re-run provably exercises the mutated pattern (the 8681d83 clause); running the
WHOLE file is strictly more coverage than a filtered run, never less, and it cannot be a
typo'd label the way a filter can. Attribution is unchanged and still strict - the declared
`case` must name a case on the `FAILED:` line - and exit 3 simply cannot arise. Declaring
both `unfiltered` and `block` is a contradiction and refused at load.

WHAT COUNTS AS A KILL, and why it is this strict. The harness protocol is: 0 = every selected
case passed, non-zero = something failed, **3 = the filter selected NOTHING** (`_harness.NO_MATCH`,
added by SCC-156 for exactly this reader). A sweep that reads any non-zero as "killed" launders
a typo'd label into evidence. So a kill requires all three of:

  * a non-zero exit that is not 3, AND
  * a `FAILED:` line in the output, AND
  * the declared `case` label naming a case ON that line.

Anything else is a SWEEP ERROR, reported as such and never as a result about the code. The
attribution clause is SCC-156 review #1 made mechanical: `--case "E"` matched 40 blocks and the
sweep recorded "killed by case E" for a case that never ran alone.

THE END-STATE CHECK (K1), which is the whole point:

  * every table file must be CLEAN AT START — otherwise residue and your own edits are the same
    bytes and no check afterwards can separate them (the SCC-144 clause, now mechanical);
  * the exact pre-sweep BYTES of every table file are held in memory and restored in a `finally`
    and on SIGTERM/SIGINT;
  * at the end, both halves must agree: the bytes match the snapshot, AND
    `git diff --quiet <pinned pre-sweep sha> -- <every mutated file>` is clean. The pinned sha,
    not bare HEAD: a commit landing mid-sweep would otherwise turn a correct restore into a
    false alarm, and a check that cries wolf gets ignored.

K4 — after the mutants, the FULL file runs ONCE, unfiltered. That is the run that would have
caught 8681d83, and a scoped subset is exactly what did not.
"""
from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
from pathlib import Path

# SCC-190 · the tree banner. ⛔ OPTIONAL BY CONSTRUCTION: this file is copied into bare temp dirs
# by its own tests, and a sweep that will not start is worse than the wrong-tree run the banner
# exists to make obvious.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import wf_common as wf  # noqa: E402
except Exception:           # noqa: BLE001
    wf = None

SWEEP_ERROR = 2
"""Exit 2 = the SWEEP is broken (bad table, dirty start, unattributable kill). Distinct from 1,
which means the sweep ran and the CODE is what failed - a surviving mutant or a red full run."""


class Terminated(Exception):
    """SIGTERM/SIGINT, raised so the `finally` that restores the tree actually runs."""


def die(msg: str) -> int:
    print(f"[SWEEP ERROR] {msg}")
    return SWEEP_ERROR


def git(args: list[str], repo: Path) -> subprocess.CompletedProcess:
    # encoding pinned: git writes UTF-8 and the PC's locale codec is cp1252 (SCC-160).
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def file_is_dirty(repo: Path, rel: str) -> bool:
    """Uncommitted change OR untracked, for one path. `git status --porcelain -- <path>` covers
    both in one call; `git diff --quiet` alone is blind to a file git has never seen."""
    return bool(git(["status", "--porcelain", "--", rel], repo).stdout.strip())


def load_table(path: Path) -> tuple[dict, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f"cannot read the table {path}: {exc}"
    mutants = data.get("mutants")
    if not isinstance(mutants, list):
        return {}, f"{path}: `mutants` must be a list"
    # F21: a sweep of nothing is not a clean sweep. An empty table exiting 0 is how a sweep
    # that was never written reports success.
    if not mutants:
        return {}, (f"{path}: the mutant table is EMPTY. A sweep of nothing is not a clean "
                    "sweep - declare the mutants, drawn from the code, before mutating.")
    for i, m in enumerate(mutants):
        if m.get("kills") and not m.get("case"):
            # `kills` was one field doing two jobs in two namespaces (SCC-179, found by this
            # script's sweep of itself). Read it as `case` so an old table still runs.
            m["case"] = m.pop("kills")
        missing = [k for k in ("id", "file", "original", "mutated", "case") if not m.get(k)]
        if missing:
            return {}, f"{path}: mutant #{i + 1} is missing {', '.join(missing)}"
        if m["original"] == m["mutated"]:
            return {}, f"{path}: mutant {m['id']} does not change anything"
        if m.get("unfiltered") and m.get("block"):
            return {}, (f"{path}: mutant {m['id']} declares BOTH `unfiltered` and `block` - "
                        "run the whole file or select a block, not both")
    if not data.get("test") and not all(m.get("test") for m in mutants):
        return {}, f"{path}: no `test` command - set it on the table or on every mutant"
    return data, None


def run_test(cmd: list[str], repo: Path, case: str | None) -> tuple[int, str]:
    full = [*cmd, "--case", case] if case else list(cmd)
    p = subprocess.run(full, cwd=str(repo), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def judge(code: int, out: str, case: str) -> tuple[bool, str]:
    """Killed? — and the one-line reason. See the module docstring for why this is strict."""
    if code == 0:
        return False, "SURVIVED - the named case still passed with the mutant in place"
    if code == 3:
        return False, ("SWEEP ERROR - exit 3: the --case filter selected NO cases "
                       "(_harness.NO_MATCH). A lost label, not a result about the code")
    failed = [ln for ln in out.splitlines() if ln.startswith("FAILED:")]
    if not failed:
        return False, (f"SWEEP ERROR - exit {code} with no `FAILED:` line, so the kill cannot "
                       "be attributed to a named case")
    # ⛔ The LAST `FAILED:` line, never the first. A test file that runs other processes
    # prints THEIR summaries too - this script's own suite spawns sweeps whose fixture
    # runners emit their own `FAILED:` lines - and the harness's own summary is what
    # `finish()` prints last. Reading `failed[0]` attributed the kill to a nested fixture's
    # case and reported a real kill as unattributable (found sweeping this file, M1).
    if case.lower() not in failed[-1].lower():
        return False, (f"SWEEP ERROR - something died, but not `{case}`. The kill is not "
                       f"evidence about the declared case. Got -> {failed[-1][:160]}")
    return True, f"KILLED by {case}"


def main() -> int:
    # ⛔ The two verdict lines print `⛔`, and the PC's console codec is cp1252, which cannot
    # encode U+26D4: `print()` would raise UnicodeEncodeError from inside the mutant loop.
    # That exception is not `Terminated`, so it escapes `main()` BEFORE the K1 end-state
    # check and the K4 full unfiltered run - the two things this script exists for - and it
    # exits 1, the code reserved for "a mutant survived". A crash would be indistinguishable
    # from a result. Same call `_harness.py` already makes for the same reason (SCC-160).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except (AttributeError, ValueError):        # not a reconfigurable text stream
            pass

    ap = argparse.ArgumentParser(description="Run a declared mutant table and verify the restore")
    ap.add_argument("--table", required=True, help="the mutant table (JSON)")
    ap.add_argument("--repo", default=".", help="repo root the paths are relative to")
    args = ap.parse_args()

    # SCC-190: a sweep WRITES to the tree it measures. Saying which one first is
    # the difference between a restore that verified and a restore in another repo.
    if wf is not None:
        wf.say_tree("mutation_sweep", args.repo)

    repo = Path(args.repo).resolve()
    data, err = load_table(Path(args.table))
    if err:
        return die(err)

    mutants = data["mutants"]
    files = sorted({m["file"] for m in mutants})

    # ── refuse to start dirty ────────────────────────────────────────────────────────────
    # Scoped to the TABLE'S files, which is where the reason bites: a surviving mutant sitting
    # beside your own uncommitted edit to the same file is the same bytes. Dirt elsewhere in
    # the tree (a plan, a walkthrough) cannot be confused with residue and does not block -
    # a refusal that fires mid-lane every time is a refusal nobody keeps.
    dirty = [f for f in files if file_is_dirty(repo, f)]
    if dirty:
        return die("these files are already dirty, so residue left by this sweep would be "
                   "INDISTINGUISHABLE from your own edits (SCC-144):\n         "
                   + "\n         ".join(dirty)
                   + "\n         Commit them first, then sweep what will actually land.")

    for m in mutants:
        src = repo / m["file"]
        if not src.is_file():
            return die(f"mutant {m['id']}: no such file - {m['file']}")
        n = src.read_text(encoding="utf-8").count(m["original"])
        if n != 1:
            return die(f"mutant {m['id']}: its `original` occurs {n} times in {m['file']}, "
                       "and it must be UNIQUE - a non-unique anchor mutates a line you did "
                       "not declare, and the kill is attributed to the wrong code.")

    pre_sha = git(["rev-parse", "HEAD"], repo).stdout.strip()
    snapshot = {f: (repo / f).read_bytes() for f in files}

    def restore() -> None:
        for rel, blob in snapshot.items():
            if (repo / rel).read_bytes() != blob:
                (repo / rel).write_bytes(blob)

    def on_signal(signum, _frame):
        raise Terminated(f"signal {signum}")

    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, on_signal)

    print(f"-- sweep: {len(mutants)} mutant(s) over {len(files)} file(s) @ {pre_sha[:8]} --")
    verdicts: list[tuple[str, bool, str]] = []
    try:
        for m in mutants:
            src = repo / m["file"]
            before = src.read_text(encoding="utf-8")
            src.write_text(before.replace(m["original"], m["mutated"], 1), encoding="utf-8")
            # The anchor was verified UNIQUE before the sweep started, so a no-op apply means
            # the file is not in its pre-sweep state - the previous mutant was not restored.
            # The doctrine already called this out ("a mutant that removes nothing is
            # DEFECTIVE - a SKIP that counts as a survivor"); it is checked here because the
            # symptom is silent: the stale mutation keeps failing the same case, and the
            # sweep happily reports a second kill it never earned.
            if src.read_text(encoding="utf-8") == before:
                why = ("SWEEP ERROR - the mutant did not APPLY: its anchor is not in the file. "
                       "The file is not in its pre-sweep state, so nothing before this can be "
                       "believed either")
                verdicts.append((m["id"], False, why))
                print(f"⛔ NOT KILLED {m['id']}\n            {why}")
                continue
            cmd = m.get("test") or data["test"]
            sel = None if m.get("unfiltered") else (m.get("block") or m["case"])
            code, out = run_test(cmd, repo, sel)
            restore()                      # immediately, so the next mutant starts clean
            killed, why = judge(code, out, m["case"])
            verdicts.append((m["id"], killed, why))
            print(f"{'KILLED   ' if killed else '⛔ NOT KILLED'} {m['id']}")
            print(f"            {why}")
            # SCC-156 #1: an over-match is legal but must be VISIBLE - attribution reads this.
            for ln in out.splitlines():
                if ln.startswith("-- filter "):
                    print(f"            {ln}")
    except Terminated as exc:
        restore()
        print(f"[SWEEP ERROR] interrupted ({exc}) - the tree was RESTORED before exiting")
        return SWEEP_ERROR
    finally:
        restore()

    # ── the end-state check (K1): both halves must agree ─────────────────────────────────
    residue = [f for f in files if (repo / f).read_bytes() != snapshot[f]]
    diff = git(["diff", "--quiet", pre_sha, "--", *files], repo)
    if residue:
        return die("RESTORE FAILED - these files do not match their pre-sweep bytes: "
                   + ", ".join(residue))
    if diff.returncode != 0:
        changed = git(["diff", "--name-only", pre_sha, "--", *files], repo).stdout.split()
        return die(f"the tree does not match the pre-sweep commit {pre_sha[:8]}: "
                   + ", ".join(changed))
    # ...and the half the byte check CANNOT do: did a mutant reach HISTORY? Restoring the
    # working tree hides a commit completely - `git status` is clean and the mutant is in the
    # branch. That is 8681d83 exactly, and the only thing that sees it is comparing the pinned
    # pre-sweep sha to HEAD. Anything can land one: the test command itself, a hook, the
    # operator in another shell.
    landed = git(["diff", "--quiet", pre_sha, "HEAD", "--", *files], repo)
    if landed.returncode != 0:
        names = git(["diff", "--name-only", pre_sha, "HEAD", "--", *files], repo).stdout.split()
        return die("a table file was COMMITTED during the sweep. The working tree restored "
                   "clean, so `git status` shows nothing - but the change is in HISTORY now, "
                   "which is how 8681d83 shipped a live mutant into the gate: "
                   + ", ".join(names))
    print(f"-- restore verified: bytes match, nothing was committed, and "
          f"`git diff --quiet {pre_sha[:8]}` is clean --")

    # ── K4: the FULL file, once, unfiltered. The run that would have caught 8681d83. ─────
    failures = [f"{mid}: {why}" for mid, killed, why in verdicts if not killed]
    for cmd in [list(x) for x in {tuple(m.get("test") or data["test"]) for m in mutants}]:
        code, out = run_test(cmd, repo, None)
        print(f"-- full file, unfiltered: {' '.join(cmd)} -> exit {code} --")
        # Prefixed, because this tail is ANOTHER process's output and it can carry its own
        # `-- SWEEP FAILED --` (this script's suite spawns sweeps). Unprefixed, a green run
        # printed a nested failure banner directly above its own verdict and read as failed.
        for ln in out.strip().splitlines()[-6:]:
            print(f"        | {ln}")
        if code != 0:
            failures.append(f"the FULL unfiltered run failed (exit {code}) - a scoped `--case` "
                            "subset is exactly what let 8681d83 through")

    if failures:
        print("\n-- SWEEP FAILED --")
        for f in failures:
            print(f"  * {f}")
        return 1
    print(f"\n-- sweep clean: {len(mutants)}/{len(mutants)} killed by their declared case --")
    return 0


if __name__ == "__main__":
    sys.exit(main())
