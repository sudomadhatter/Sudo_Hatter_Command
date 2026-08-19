"""Re-run the mutants review found SURVIVING against check_both_machines."""
import pathlib, re, subprocess, sys
TREE = pathlib.Path(sys.argv[1])
LINT = TREE / ".agents/scripts/workflow_lint.py"
TEST = TREE / ".agents/scripts/tests/test_workflow_lint.py"
orig = LINT.read_text(encoding="utf-8")

def run():
    r = subprocess.run([sys.executable, str(TEST)], cwd=TREE,
                       capture_output=True, text=True, errors="replace")
    return r.returncode, r.stdout + r.stderr

MUTANTS = [
    ("W1 scan cut to commands/ only",
     '("commands", "rules", "skills", "scripts")', '("commands",)'),
    ("W2 the native Windows BACKSLASH spelling dropped",
     r'_WINDOWS_VENV = re.compile(r"\.venv[\\/]+Scripts\b")',
     r'_WINDOWS_VENV = re.compile(r"\.venv/Scripts\b")'),
    ("W3 window widened to swallow everything", "_WINDOW = 4", "_WINDOW = 400"),
    ("W4 off-switch loosened back to the bare word POSIX",
     r'_POSIX_AWARE = re.compile(r"\.venv[\\/]+bin\b")',
     r'_POSIX_AWARE = re.compile(r"\.venv[\\/]+bin\b|POSIX|\bbin/\b")'),
    ("W5 severity downgraded to info", 'rep.warn("both-machines",\n                         f"{f.relative_to(lobby)}:{i + 1}: hardcodes',
     'rep.info("both-machines",\n                         f"{f.relative_to(lobby)}:{i + 1}: hardcodes'),
    ("W6 off-switch deleted entirely (the widening the first cut proved)",
     "                if _POSIX_AWARE.search(window):\n                    continue\n", ""),
    ("U1 UNWIRED from main()", "        check_both_machines(lobby, rep)\n", ""),
    ("X1 the crash guards dropped",
     'if not f.is_file() or f.suffix.lower() not in (".md", ".py", ".ps1", ".sh"):\n                continue',
     'if f.suffix.lower() not in (".md", ".py", ".ps1", ".sh"):\n                continue'),
    ("X2 the opt-out honoured for every file (a mute switch)",
     "            if BOTH_MACHINES_OPT_OUT in text:\n                continue\n",
     "            if True:\n                pass\n"),
]
base = run()[0]
print(f"baseline exit: {base}  (must be 0)")
surv = 0
for label, old, new in MUTANTS:
    if old not in orig:
        print(f"DEFECTIVE | {label} - pattern not found, mutant removed NOTHING"); surv = 1; continue
    LINT.write_text(orig.replace(old, new, 1), encoding="utf-8")
    code, out = run()
    LINT.write_text(orig, encoding="utf-8")
    named = [l.split(": ", 1)[0].replace("[FAIL] ", "")
             for l in out.splitlines() if l.startswith("[FAIL]")]
    if code not in (0, 3) and named:
        print(f"KILLED   | {label}  ->  {', '.join(named[:3])}")
    else:
        print(f"SURVIVED | {label}  (exit={code})"); surv = 1
print(f"final exit: {run()[0]}  (must be 0 - tree restored)")
sys.exit(surv)
