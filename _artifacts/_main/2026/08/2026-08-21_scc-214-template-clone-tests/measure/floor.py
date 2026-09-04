"""What actually sets the suite's wall clock? Mimic run_all's pool exactly, but record
each file's wall time, so the FLOOR is measured rather than inferred from solo runs."""
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
TESTS = Path(sys.argv[1]); FILES = sorted(p.name for p in TESTS.glob("test_*.py"))
jobs = os.cpu_count() or 1
times = {}
def run(name):
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, str(TESTS / name)], cwd=str(TESTS.parents[2]),
                       capture_output=True, text=True, errors="replace")
    return name, time.monotonic() - t0, p.returncode
print(f"jobs={jobs} files={len(FILES)} load={os.getloadavg()}")
t0 = time.monotonic()
with ThreadPoolExecutor(max_workers=jobs) as ex:
    for name, dt, rc in ex.map(run, FILES):
        times[name] = (dt, rc)
wall = time.monotonic() - t0
total = sum(d for d, _ in times.values())
print(f"WALL {wall:.1f}s | sum-of-files {total:.1f}s | jobs {jobs} | work/jobs {total/jobs:.1f}s")
print("slowest under contention:")
for n, (d, rc) in sorted(times.items(), key=lambda kv: -kv[1][0])[:6]:
    print(f"  {n:42s} {d:6.1f}s rc={rc}")
top = sorted(times.values(), key=lambda v: -v[0])
print(f"\nif the slowest file were HALVED: new floor = max({top[0][0]/2:.1f}, {top[1][0]:.1f}) "
      f"= {max(top[0][0]/2, top[1][0]):.1f}s vs work/jobs {total/jobs:.1f}s")
