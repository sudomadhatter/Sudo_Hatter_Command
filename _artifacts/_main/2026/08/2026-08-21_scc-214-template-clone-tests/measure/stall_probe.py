"""Is the first launch of a FRESH executable stub slow on this Mac (per-file first-run stall)?"""
import os, subprocess, sys, time
from pathlib import Path
TESTS = Path(sys.argv[1]); sys.path.insert(0, str(TESTS))
import _pf_fixtures as pf
from _harness import TempDir
def t(cmd, env=None):
    t0 = time.perf_counter(); subprocess.run(cmd, capture_output=True, env=env); return time.perf_counter() - t0
for i in range(3):
    with TempDir() as d:
        pf.board(d)                                   # fresh acli launcher + stub + state file
        launcher = os.environ["ACLI_BIN"]
        a = t([launcher, "jira", "workitem", "search", "--jql", "x"])
        b = t([launcher, "jira", "workitem", "search", "--jql", "x"])
        print(f"fresh board stub #{i}: first {a:.3f}s  second {b:.3f}s")
# same content, reused file across 'scenarios': only the STATE file changes
with TempDir() as keep:
    pf.board(keep); launcher = os.environ["ACLI_BIN"]
    for i in range(3):
        with TempDir() as d:
            st = d / "state.json"; st.write_text('{"children": [], "fail": false}')
            env = dict(os.environ, PF_BOARD_STATE=str(st))
            print(f"reused launcher, new state #{i}: {t([launcher, 'jira', 'workitem', 'search'], env):.3f}s")
# and a fresh plain shell script that execs nothing python
for i in range(2):
    with TempDir() as d:
        s = d / "stub.sh"; s.write_text("#!/bin/sh\nexit 0\n"); s.chmod(0o755)
        print(f"fresh sh stub #{i}: first {t([str(s)]):.3f}s second {t([str(s)]):.3f}s")
