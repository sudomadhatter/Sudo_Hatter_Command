"""Time every block of test_task_preflight.py IN ONE PROCESS, so the seam is chosen by
measurement. Wraps Cases.block to stamp each transition; templates stay shared, exactly as
they are in a real run."""
import io, contextlib, sys, time
from pathlib import Path
TESTS = Path(sys.argv[1]); sys.path.insert(0, str(TESTS)); sys.argv = [sys.argv[0]]
import _harness
marks = []
_orig = _harness.Cases.block
def block(self, label):
    marks.append((label, time.monotonic()))
    return _orig(self, label)
_harness.Cases.block = block
import test_task_preflight as mod
buf = io.StringIO()
t0 = time.monotonic()
with contextlib.redirect_stdout(buf):
    rc = mod.main()
end = time.monotonic()
rows = []
for i, (label, ts) in enumerate(marks):
    stop = marks[i + 1][1] if i + 1 < len(marks) else end
    rows.append((stop - ts, label))
total = sum(d for d, _ in rows)
print(f"rc={rc} total={end-t0:.1f}s  blocks={len(rows)}  "
      f"{[l for l in buf.getvalue().splitlines() if 'passed --' in l][-1]}")
run = 0.0
for d, label in rows:
    run += d
    print(f"  {d:6.2f}s  cum {run:6.1f}s  {label[:66]}")
print(f"\nBALANCE POINT (half of {total:.1f}s = {total/2:.1f}s):")
run = 0.0
for i, (d, label) in enumerate(rows):
    run += d
    if run >= total / 2:
        print(f"  after block {i+1}/{len(rows)}: cum {run:.1f}s | remainder {total-run:.1f}s")
        print(f"  seam label -> {label[:70]}")
        break
