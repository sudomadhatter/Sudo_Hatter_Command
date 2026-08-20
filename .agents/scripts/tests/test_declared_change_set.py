"""declared_change_set.py — the machine-readable form of the plan's touch-list. (SCC-226)

The block already existed as prose law (`artifacts-always-first.md` §2, Create the artifact
folder + plan: "every file touched with links"); SCC-226 gives it ONE fixed shape and this
parser. Consumers:
the self-audit's Scope Ledger (SCC-227) reads the created set, the code-review drift check
(SCC-231) diffs declared against the real diff. Absence is a DEFINED case for both - a
plan with no block must parse to present=False, never crash, because the vacuous-green
mutation (absent block silently reading as "nothing declared, nothing drifted") is exactly
what SCC-231's important-severity finding exists to catch.

Written RED first against the module. Stdlib only, no pytest.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import declared_change_set as dcs  # noqa: E402


BLOCK = """---
IsArtifact: true
---

# Plan

## Declared Change Set

- EDIT `.agents/rules/artifacts-always-first.md` — name the block → A
- NEW `.agents/scripts/declared_change_set.py` — stdlib parser → A, F
- EDIT (wholesale rewrite) `.agents/commands/smh-self-audit.md` — three lenses → B
- DELETE `.agents/old/dead.md` → C
- EDIT `.agents/scripts/INDEX.md` — rows for the new scripts
- `.agents/scripts/risk_seam.py` — forgot the op marker → C
- EDIT .agents/rules/bare-path.md → D
- EDIT `.agents/docs/renames.md` — rename foo → bar everywhere → E
* NEW `.agents/star/bullet.py` — wrong list marker → F

*(an italic parenthetical about the block — prose, not a declaration attempt)*

```markdown
- NEW `example/fenced-fake.py` — a TAUGHT example, not a declaration → A
```

## Execution order

- EDIT `.agents/after/terminator.md` — outside the section → Z
"""

NO_BLOCK = """# Plan

## Goal
Ship it.
"""


def main() -> int:
    c = Cases("declared_change_set")

    # ── the fixed shape parses ────────────────────────────────────────────────
    r = dcs.parse(BLOCK)
    c.check("block found", r["present"] is True, str(r["present"]))
    by = {e["path"]: e for e in r["entries"]}
    c.check("EDIT bullet: path + op + row",
            by.get(".agents/rules/artifacts-always-first.md", {}).get("op") == "EDIT"
            and by[".agents/rules/artifacts-always-first.md"]["row"] == "A",
            str(by.get(".agents/rules/artifacts-always-first.md")))
    c.check("NEW bullet carries a multi-row mapping verbatim",
            by.get(".agents/scripts/declared_change_set.py", {}).get("row") == "A, F",
            str(by.get(".agents/scripts/declared_change_set.py")))
    c.check("a parenthetical qualifier after the op is accepted",
            by.get(".agents/commands/smh-self-audit.md", {}).get("op") == "EDIT",
            str(by.get(".agents/commands/smh-self-audit.md")))
    c.check("DELETE with no prose still maps its row",
            by.get(".agents/old/dead.md", {}).get("op") == "DELETE"
            and by[".agents/old/dead.md"]["row"] == "C",
            str(by.get(".agents/old/dead.md")))
    c.check("a bare (unbackticked) path parses too",
            by.get(".agents/rules/bare-path.md", {}).get("row") == "D",
            str(by.get(".agents/rules/bare-path.md")))
    c.check("an arrow inside the why-prose does not corrupt the row - the LAST arrow "
            "is the separator",
            by.get(".agents/docs/renames.md", {}).get("row") == "E",
            str(by.get(".agents/docs/renames.md")))
    c.check("a fenced example bullet is NOT an entry (SCC-154's scar, inherited)",
            "example/fenced-fake.py" not in by
            and not any("fenced-fake" in raw for raw in r["incomplete"]),
            str(sorted(by)))
    c.check("a bullet after the terminating heading is NOT an entry - the section "
            "boundary is real",
            ".agents/after/terminator.md" not in by, str(sorted(by)))

    # ── incomplete is REPORTED, never guessed ─────────────────────────────────
    c.check("a bullet missing its row mapping lands in incomplete",
            any("INDEX.md" in raw for raw in r["incomplete"]), str(r["incomplete"]))
    c.check("a bullet missing its op marker lands in incomplete",
            any("risk_seam" in raw for raw in r["incomplete"]), str(r["incomplete"]))
    c.check("a star-marker bullet is an ATTEMPT: reported in incomplete, never "
            "silently skipped (the prefilter hole, executed this review wave)",
            any("star/bullet.py" in raw for raw in r["incomplete"])
            and ".agents/star/bullet.py" not in by, str(r["incomplete"]))
    c.check("an *(italic)* prose line is NOT an attempt - markdown list markers "
            "need a following space",
            not any("italic parenthetical" in raw for raw in r["incomplete"]),
            str(r["incomplete"]))
    c.check("incomplete bullets are NOT entries",
            ".agents/scripts/risk_seam.py" not in by and
            ".agents/scripts/INDEX.md" not in by, str(sorted(by)))

    # ── a SECOND block is loud, not silently discarded ────────────────────────
    r3 = dcs.parse("## Declared Change Set\n\n- EDIT `one.md` → A\n\n"
                   "## Declared Change Set\n\n- EDIT `two.md` → B\n")
    c.check("a second '## Declared Change Set' heading is REPORTED in incomplete "
            "(amendments go inside the one block)",
            len(r3["entries"]) == 1 and r3["entries"][0]["path"] == "one.md"
            and any("second" in raw for raw in r3["incomplete"]), str(r3))

    # ── absence is a defined case ─────────────────────────────────────────────
    r2 = dcs.parse(NO_BLOCK)
    c.check("no block parses to present=False with empty sets",
            r2["present"] is False and r2["entries"] == [] and r2["incomplete"] == [],
            str(r2))

    # ── the two-sided diff (SCC-231's left-hand side) ─────────────────────────
    d = dcs.diff([e["path"] for e in r["entries"]],
                 [".agents/rules/artifacts-always-first.md",
                  ".agents/scripts/declared_change_set.py",
                  ".agents/commands/cicd-quick-dev.md"])
    c.check("edited-but-never-declared is drift.undeclared",
            d["undeclared"] == [".agents/commands/cicd-quick-dev.md"], str(d))
    c.check("declared-but-untouched is drift.unimplemented",
            sorted(d["unimplemented"]) == [".agents/commands/smh-self-audit.md",
                                           ".agents/docs/renames.md",
                                           ".agents/old/dead.md",
                                           ".agents/rules/bare-path.md"], str(d))
    c.check("planning dirs never count as drift",
            dcs.diff([], ["_artifacts/_main/x/implementation_plan.md",
                          "_bmad-output/y.md"])["undeclared"] == [],
            str(dcs.diff([], ["_artifacts/_main/x/implementation_plan.md"])))

    # ── SCC-231: both review twins carry the SECOND left-hand side ────────────
    root = Path(__file__).resolve().parents[3]
    smh = (root / ".agents/commands/smh-code-review.md").read_text(encoding="utf-8")
    cicd = (root / ".agents/commands/cicd-code-review.md").read_text(encoding="utf-8")
    for name, cmd in (("smh Step 2", smh), ("cicd Step 1.5", cicd)):
        c.check(f"{name}: keeps the acceptance reconciliation it always had",
                "anything in the diff beyond the list is drift" in cmd, "first side lost")
        c.check(f"{name}: adds the declared-set reconciliation, both directions, "
                f"under the tool's ACTUAL key names",
                "**`undeclared`**" in cmd and "**`unimplemented`**" in cmd
                and "drift.undeclared" not in cmd,
                "second side absent, or the dead drift.* spelling is back")
        c.check(f"{name}: severity mapping is pinned PER BULLET - undeclared=important, "
                f"unimplemented=suggestion, incomplete=important",
                bool(re.search(r"\*\*`undeclared`\*\*.{0,200}?\*\*important\*\*", cmd, re.S))
                and bool(re.search(r"\*\*`unimplemented`\*\*.{0,200}?\*\*suggestion\*\*", cmd, re.S))
                and bool(re.search(r"\*\*`incomplete`\*\*.{0,300}?\*\*important\*\*", cmd, re.S)),
                "a severity swap in the mapping would go unnoticed")
        c.check(f"{name}: the diff verb's incomplete carry-through is law (grammar "
                f"rejections must stay visible at review time)",
                "carries them through" in cmd, "incomplete invisible at review")
        c.check(f"{name}: names the parser as the source of truth",
                "declared_change_set.py" in cmd, "parser not wired")
        c.check(f"{name}: a missing BLOCK is an *important* finding, an absent plan "
                f"FILE is a loud error - both stated",
                "no declared set to reconcile against" in cmd
                and "loud exit-2 error" in cmd, "vacuous-green case open")
        c.check(f"{name}: the planning-dir carve-out is DOCUMENTED where the reviewer "
                f"reads, not only in the module",
                "carved out on BOTH" in cmd, "silent blind spot")
        c.check(f"{name}: promised checks reconcile like files (assertion-level drift "
                f"is drift)",
                "Declared checks reconcile like declared files" in cmd,
                "assertion tier unlegislated")
        c.check(f"{name}: no drift row auto-fails - the disposition bullet stands AND "
                f"the contract phrase appears at least twice",
                "Every drift row takes the same contract" in cmd
                and cmd.count("cut it, or name why it stays") >= 2,
                "disposition contract lost or diluted")
        c.check(f"{name}: the re-taken diff is rename-stable (--no-renames in the "
                f"documented one-liner)",
                "--no-renames" in cmd, "rename lanes yield config-dependent drift")

    # ── the PRODUCER side: every plan-emitting command teaches the block ──────
    # Part A's promised structure check, landed by the review wave. cicd-quick-dev is
    # a NON-emitter by design (the fast lane skips plans; its eject defers to the full
    # lane's plan machinery) - that ground truth is PINNED here so the next reader gets
    # a red, not an archaeology project, if the lane ever grows a plan template.
    EMITTERS = ("smh-quick-dev.md", "smh-plan-task.md", "cicd-dev-story-tests.md")
    for fname in EMITTERS:
        body = (root / ".agents/commands" / fname).read_text(encoding="utf-8")
        c.check(f"emitter {fname}: its plan template names the `## Declared Change "
                f"Set` block",
                "Declared Change Set" in body, "block not taught at the source")
    quick = (root / ".agents/commands/cicd-quick-dev.md").read_text(encoding="utf-8")
    c.check("cicd-quick-dev stays a NON-emitter: it never teaches the `## Declared "
            "Change Set` template, and its eject re-arms the plan-first gate (where "
            "the block then applies); its drift line says plan-exempt, not silence",
            "## Declared Change Set" not in quick
            and "RE-ARMS the plan-first gate" in quick
            and "no Declared Change Set — plan-exempt lane" in quick,
            "the fast lane grew plan machinery, or its drift-line answer went silent - "
            "either teach the block or re-ground this pin")

    # ── the CLI itself, subprocess tier - verbs, exit codes, the carry ────────
    import json as _json
    import subprocess
    import tempfile
    mod = Path(__file__).resolve().parents[1] / "declared_change_set.py"
    with tempfile.TemporaryDirectory() as td:
        plan = Path(td) / "plan.md"
        plan.write_text(BLOCK, encoding="utf-8")
        pr = subprocess.run([sys.executable, str(mod), "parse", str(plan)],
                            capture_output=True, text=True)
        c.check("CLI parse: exit 0 + JSON with entries and incomplete",
                pr.returncode == 0 and _json.loads(pr.stdout)["present"] is True,
                f"rc={pr.returncode} out={pr.stdout[:120]}")
        dr = subprocess.run([sys.executable, str(mod), "diff", str(plan), "--changed"],
                            capture_output=True, text=True)
        dj = _json.loads(dr.stdout) if dr.returncode == 0 else {}
        c.check("CLI diff: an EMPTY re-taken diff is a legitimate boundary (exit 0, "
                "everything declared reads unimplemented)",
                dr.returncode == 0 and dj.get("undeclared") == []
                and len(dj.get("unimplemented", [])) > 0,
                f"rc={dr.returncode} out={dr.stdout[:120]} err={dr.stderr[:120]}")
        c.check("CLI diff: carries incomplete through - grammar rejections stay "
                "visible at review time",
                "incomplete" in dj and any("star/bullet.py" in raw
                                           for raw in dj["incomplete"]),
                str(dj.get("incomplete"))[:150])
        ab = subprocess.run([sys.executable, str(mod), "parse", str(Path(td) / "no.md")],
                            capture_output=True, text=True)
        c.check("CLI: an absent plan FILE is a loud exit-2 error, never present:false",
                ab.returncode == 2 and "no such plan" in ab.stderr and not ab.stdout.strip(),
                f"rc={ab.returncode} err={ab.stderr[:100]}")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
