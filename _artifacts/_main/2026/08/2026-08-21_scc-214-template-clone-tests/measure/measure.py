"""Monotonic-clock measurement: full suite, then the two files under the profiler, then receipts, then the stall probe."""
import os, subprocess, sys, time
from pathlib import Path
TREE = Path(sys.argv[1]); OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True); TESTS = TREE / ".agents/scripts/tests"; S = Path(__file__).parent
py = sys.executable
steps = [("full_run_all", [py, str(TESTS / "run_all.py")]),
         ("pf_profile", [py, str(S / "profile_split.py"), str(TESTS), "pf"]),
         ("gh_profile", [py, str(S / "profile_split.py"), str(TESTS), "gh"]),
         ("receipts_solo", [py, str(TESTS / "test_task_preflight_receipts.py")]),
         ("stall_probe_idle", [py, str(S / "stall_probe.py"), str(TESTS)])]
rep = [f"tree={TREE.name} HEAD={subprocess.run(['git','-C',str(TREE),'rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip()} cpus={os.cpu_count()} load_at_start={os.getloadavg()}"]
for name, cmd in steps:
    t0 = time.monotonic(); p = subprocess.run(cmd, cwd=str(TREE), capture_output=True, text=True, errors="replace"); dt = time.monotonic() - t0
    (OUT / f"{name}.log").write_text(p.stdout + "\n--- stderr ---\n" + p.stderr)
    tail = [l for l in p.stdout.splitlines() if "files passed" in l or "passed --" in l or l.startswith(("pf:", "gh:", "  ", "fresh", "reused"))]
    rep.append(f"{name}: {dt:.1f}s rc={p.returncode} load={os.getloadavg()}\n" + "\n".join("    " + l for l in tail[-14:]))
    (OUT / "report.txt").write_text("\n".join(rep) + "\n")
print("\n".join(rep))
