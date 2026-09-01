#!/usr/bin/env bash
# SCC-205 Part D — the mutation sweep. Every mutant is drawn from the CODE, not from my cases:
# each is a real edit a future maintainer could plausibly make, and the guard must kill it.
TREE="$1"; C="$TREE/.agents/commands"; T="$TREE/.agents/scripts/tests/test_twin_parity.py"
run() { (cd "$TREE" && python3 .agents/scripts/tests/test_twin_parity.py > /dev/null 2>&1); echo $?; }
kill_or_survive() {  # $1 label, $2 exit code
  if [ "$2" != "0" ]; then echo "KILLED   | $1"; else echo "SURVIVED | $1"; SURV=1; fi
}
SURV=0
echo "baseline exit: $(run)   (must be 0)"

# M1 · a maintainer edits ONE twin's copy of a shared law — the headline drift.
cp "$C/cicd-clean-code-audit.md" /tmp/m1.bak
python3 - "$C/cicd-clean-code-audit.md" <<'PY'
import sys,pathlib;p=pathlib.Path(sys.argv[1]);p.write_text(p.read_text(encoding="utf-8").replace("It's cheap","It is cheap",1),encoding="utf-8")
PY
kill_or_survive "M1 one twin's shared law edited (identity)" "$(run)"
cp /tmp/m1.bak "$C/cicd-clean-code-audit.md"

# M2 · law added to ONE family only — the failure that CAUSED the ticket.
cp "$C/smh-code-review.md" /tmp/m2.bak
printf '\n<!-- twin-law: new-rule -->\nA brand new obligation.\n<!-- /twin-law -->\n' >> "$C/smh-code-review.md"
kill_or_survive "M2 new law in smh only (symmetry)" "$(run)"
cp /tmp/m2.bak "$C/smh-code-review.md"

# M2b · ...and the same in the OTHER direction, because the guard must be SYMMETRIC.
cp "$C/cicd-code-review.md" /tmp/m2b.bak
printf '\n<!-- twin-law: new-rule -->\nA brand new obligation.\n<!-- /twin-law -->\n' >> "$C/cicd-code-review.md"
kill_or_survive "M2b new law in cicd only (symmetry, other direction)" "$(run)"
cp /tmp/m2b.bak "$C/cicd-code-review.md"

# M3 · one twin's fence deleted — the law is still THERE, but no longer compared.
cp "$C/smh-clean-code-audit.md" /tmp/m3.bak
python3 - "$C/smh-clean-code-audit.md" <<'PY'
import sys,pathlib;p=pathlib.Path(sys.argv[1]);p.write_text(p.read_text(encoding="utf-8").replace("<!-- twin-law: disposition -->\n","",1),encoding="utf-8")
PY
kill_or_survive "M3 one twin's fence removed (symmetry)" "$(run)"
cp /tmp/m3.bak "$C/smh-clean-code-audit.md"

# M4 · a new twin pair joins the tree unpinned — the completeness row.
printf -- '---\ndescription: x\n---\n# /cicd-brand-new\n' > "$C/cicd-brand-new.md"
printf -- '---\ndescription: x\n---\n# /smh-brand-new\n' > "$C/smh-brand-new.md"
kill_or_survive "M4 unpinned name-counterpart (completeness)" "$(run)"
rm -f "$C/cicd-brand-new.md" "$C/smh-brand-new.md"

# M5 · THE GUARD ITSELF gutted — the extractor returns nothing. Anti-vacuity must catch it.
cp "$T" /tmp/m5.bak
python3 - "$T" <<'PY'
import sys,pathlib;p=pathlib.Path(sys.argv[1])
p.write_text(p.read_text(encoding="utf-8").replace("    out: dict[str, str] = {}\n","    out: dict[str, str] = {}\n    return out\n",1),encoding="utf-8")
PY
kill_or_survive "M5 extractor gutted to return {} (anti-vacuity)" "$(run)"
cp /tmp/m5.bak "$T"

# M6 · the PAIRS list emptied — every loop becomes a no-op.
cp "$T" /tmp/m6.bak
python3 - "$T" <<'PY'
import sys,pathlib,re;p=pathlib.Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
s=re.sub(r"PAIRS = \[.*?\n\]", "PAIRS = []", s, count=1, flags=re.S)
p.write_text(s,encoding="utf-8")
PY
kill_or_survive "M6 PAIRS emptied (anti-vacuity)" "$(run)"
cp /tmp/m6.bak "$T"

echo "final exit: $(run)   (must be 0 - the tree is restored)"
exit $SURV
