"""memory_store_check.py must make silent memory-store damage LOUD (SCC-319).

The store is a live symlinked asset every session reads, and ordinary git commands
(`reset --keep`, `checkout`, `merge`) mutate it without a trace: a store missing three
files is indistinguishable from a store that never had them. Measured 2026-08-24 - the
lobby store WAS damaged by `git reset --keep HEAD~1` and restored by hand.

Two halves, both pinned here:
  * INTEGRITY (promoted from test_memory_store.py's check_store): a MEMORY.md row that
    resolves to no file is a hard exit.
  * DELTA (the incident's shape): the checker keeps a per-working-tree baseline of the
    store's file names; files present last run and gone now are SHOUTED by name. The
    incident reverts MEMORY.md along with the files, so integrity alone stays green -
    only the baseline sees the drop.

Both ways, per tests-must-gate-for-real Rule 5: the checker must also stay SILENT on a
move that touches nothing under the store, or it fires always and is ignored in a week.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir, run_script


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def seed_repo_with_store(root: Path, n_files: int = 2) -> Path:
    repo = root / "repo"
    store = repo / "_artifacts" / "_memory"
    store.mkdir(parents=True)
    rows = []
    for i in range(1, n_files + 1):
        name = f"mem-{i}.md"
        (store / name).write_text(
            f"---\nname: mem-{i}\ndescription: memory {i}\n---\n\nfact {i}\n",
            encoding="utf-8")
        rows.append(f"- [Memory {i}]({name}) — fact {i}")
    (store / "MEMORY.md").write_text("# Memory index\n\n" + "\n".join(rows) + "\n",
                                     encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t.t")
    git(repo, "config", "user.name", "t")
    git(repo, "add", "_artifacts/_memory")
    git(repo, "commit", "-qm", "seed store")
    return repo


def check(*args: str) -> tuple[int, str]:
    return run_script("memory_store_check.py", *args)


def main() -> int:
    c = Cases("memory_store_check")

    if c.block("SCC-319 I1 · standalone integrity: whole store exits 0, dead index row exits loud"):
        with TempDir() as tmp:
            repo = seed_repo_with_store(tmp)
            store = repo / "_artifacts" / "_memory"
            code, out = check("--store", str(store))
            c.check("I1a a whole store exits 0", code == 0, f"exit={code}\n{out}")

            idx = store / "MEMORY.md"
            idx.write_text(idx.read_text(encoding="utf-8")
                           + "- [Gone](never-written.md) — a row that resolves to nothing\n",
                           encoding="utf-8")
            code, out = check("--store", str(store))
            c.check("I1b a MEMORY.md row naming an absent file exits non-zero",
                    code != 0, f"exit={code}")
            c.check("I1c ...and NAMES the file", "never-written.md" in out, out[-300:])

    if c.block("SCC-319 I2 · the promoted function is THE function (one implementation, two callers)"):
        import memory_store_check as msc
        import test_memory_store as tms
        c.check("I2a test_memory_store.check_store IS memory_store_check.check_store",
                tms.check_store is msc.check_store, "the test defines its own copy")
        c.check("I2b index cap constant is shared, not duplicated",
                tms.INDEX_CAP == msc.INDEX_CAP, f"{tms.INDEX_CAP} != {msc.INDEX_CAP}")

    if c.block("SCC-319 I3 · the incident, reproduced: reset --keep removes files, the delta SHOUTS them"):
        with TempDir() as tmp:
            repo = seed_repo_with_store(tmp)
            store = repo / "_artifacts" / "_memory"
            # Baseline the healthy 2-file store, exactly as a hook run would.
            code, out = check("--store", str(store), "--delta")
            c.check("I3a first delta run is silent (baseline written, nothing to compare)",
                    code == 0 and "MISSING" not in out, f"exit={code}\n{out}")

            # Commit three more memories - the shape of the incident's cc6eb69.
            idx = store / "MEMORY.md"
            rows = []
            for name in ("similarity-gate.md", "transition-probe.md", "field-paths.md"):
                (store / name).write_text(
                    f"---\nname: {name[:-3]}\ndescription: d\n---\n\nfact\n", encoding="utf-8")
                rows.append(f"- [{name}]({name}) — hook")
            idx.write_text(idx.read_text(encoding="utf-8") + "\n".join(rows) + "\n",
                           encoding="utf-8")
            git(repo, "add", "_artifacts/_memory")
            git(repo, "commit", "-qm", "five memories")
            code, out = check("--store", str(store), "--delta")
            c.check("I3b delta after the commit is clean (files grew, nothing missing)",
                    code == 0 and "MISSING" not in out, f"exit={code}\n{out}")

            # The operator's exact sequence: branch keeps the commit, reset undoes it on disk.
            git(repo, "branch", "keeper")
            git(repo, "reset", "--keep", "-q", "HEAD~1")
            missing = [n for n in ("similarity-gate.md", "transition-probe.md", "field-paths.md")
                       if not (store / n).is_file()]
            c.check("fixture: the reset really removed the files from disk",
                    len(missing) == 3, f"missing={missing}")

            code, out = check("--store", str(store), "--delta")
            c.check("I3c the delta run SHOUTS and names every removed file",
                    "similarity-gate.md" in out and "transition-probe.md" in out
                    and "field-paths.md" in out, out[-400:])
            # Integrity alone would stay green here - MEMORY.md was reverted with the files.
            # The shout must not depend on a dead index row existing.

    if c.block("SCC-319 I4 · silent on a move that touches nothing under the store"):
        with TempDir() as tmp:
            repo = seed_repo_with_store(tmp)
            store = repo / "_artifacts" / "_memory"
            check("--store", str(store), "--delta")            # baseline
            (repo / "other.txt").write_text("x\n", encoding="utf-8")
            git(repo, "add", "other.txt")
            git(repo, "commit", "-qm", "unrelated")
            git(repo, "checkout", "-q", "-b", "side")
            code, out = check("--store", str(store), "--delta")
            c.check("I4a a store-untouched move reports nothing missing",
                    code == 0 and "MISSING" not in out, f"exit={code}\n{out}")

    if c.block("SCC-319 I5 · the three post-move hooks exist, probe the interpreter, and cannot block"):
        hooks_dir = Path(SCRIPTS).parent.parent / ".githooks"
        for name in ("post-checkout", "post-merge", "post-rewrite"):
            p = hooks_dir / name
            text = p.read_text(encoding="utf-8") if p.is_file() else ""
            c.check(f"I5 {name} exists and calls memory_store_check.py",
                    p.is_file() and "memory_store_check.py" in text,
                    f"exists={p.is_file()}")
            c.check(f"I5 {name} probes python3 -> python -> py (two machines)",
                    "python3 python py" in text, "hardcoded interpreter")
            c.check(f"I5 {name} is advisory - it exits 0 whatever the checker says",
                    "exit 0" in text, "a post-* hook cannot veto, and must not look like it can")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
