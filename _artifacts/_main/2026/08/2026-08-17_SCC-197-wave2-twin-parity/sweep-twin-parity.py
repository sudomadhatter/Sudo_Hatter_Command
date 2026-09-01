"""Every mutant review found SURVIVING against test_twin_parity.py, re-run."""
import pathlib, re, subprocess, sys
TREE = pathlib.Path(sys.argv[1])
T = TREE / ".agents/scripts/tests/test_twin_parity.py"
orig = T.read_text(encoding="utf-8")

def run():
    r = subprocess.run([sys.executable, str(T)], cwd=TREE, capture_output=True,
                       text=True, errors="replace")
    return r.returncode, r.stdout + r.stderr

MUTANTS = [
    ("T2 completeness row gutted (unpinned can never be non-empty)",
     "    return sorted(fam - pinned - set(NOT_PAIRED))", "    return []"),
    ("T3 symmetry made ONE-DIRECTIONAL (the reversed arm dropped)",
     "orderings = ((a, b, ta, tb), (b, a, tb, ta))",
     "orderings = ((a, b, ta, tb),)"),
    ("T3b the symmetry PREDICATE itself neutered",
     "    return sorted(k for k in la if k not in lb and k not in db)", "    return []"),
    ("T4 identity predicate hard-wired True",
     "    return law_id in la and law_id in lb and la[law_id] == lb[law_id]", "    return True"),
    ("T6 the fenced-scope row weakened to a bare truthiness",
     "                fenced == sorted(FENCED_TODAY),", "                True,"),
    ("T7 duplicate-id refusal removed",
     '        if law_id in out:\n            bad.append(f"{law_id} (declared twice - the second would overwrite the first)")\n            continue\n', ''),
    ("T8 empty-region refusal removed",
     '        if not region:\n            bad.append(f"{law_id} (empty region - it would compare equal to any other empty one)")\n            continue\n', ''),
    ("T9 unclosed-fence bound removed (swallows the next region)",
     "        stop = opens[n + 1].start() if n + 1 < len(opens) else len(text)",
     "        stop = len(text)"),
    ("T10 E1 back to an arbitrary set member (the flake)",
     '        k = "disposition"\n        drifted', '        k = next(iter(set(la) & set(lb)), None)\n        drifted'),
    ("T11 -AP twins demanded as parity subjects",
     '    fam = {n for n in fam if not n.endswith("-AP.md")}\n', ''),
]
print(f"baseline exit: {run()[0]}  (must be 0)")
surv = 0
for label, old, new in MUTANTS:
    if old not in orig:
        print(f"DEFECTIVE | {label} - pattern not found"); surv = 1; continue
    T.write_text(orig.replace(old, new, 1), encoding="utf-8")
    code, out = run()
    T.write_text(orig, encoding="utf-8")
    named = [l.split(": ", 1)[0].replace("[FAIL] ", "") for l in out.splitlines() if l.startswith("[FAIL]")]
    if code not in (0, 3) and named:
        print(f"KILLED   | {label}  ->  {', '.join(named[:2])}")
    else:
        print(f"SURVIVED | {label}  (exit={code})"); surv = 1
print(f"final exit: {run()[0]}  (must be 0 - tree restored)")
sys.exit(surv)
