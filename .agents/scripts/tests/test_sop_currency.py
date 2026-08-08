"""sop_currency.py must fire on real usage changes and stay quiet on everything else.

Two failure modes matter more than the happy path:

  1. A gate that fires on inventory churn (INDEX.md, its own tests) trains the operator to
     reach for the escape hatch reflexively, and then it is checking nothing.
  2. A gate that can be satisfied by git's own commit-message comment block is WORSE than
     absent: it reports success forever. That is not hypothetical — the Jira gate shipped
     with exactly this bug, because git appends the staged-file list to the message file
     and an unstripped read finds any path it is looking for. Case S is that regression.

Stdlib only, no pytest — same constraint as the script under test.
"""
from __future__ import annotations

import sys

from _harness import Cases, TempDir, run_script

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from sop_currency import SOP_DOC, classify, evaluate  # noqa: E402

MARKER = ".agents/scripts/git-hooks/SOP-ENFORCE"


def main() -> int:
    c = Cases("sop_currency")

    # ── A-E: the surfaces that MUST fire ──────────────────────────────────────
    for label, path in [
        ("A a /command file", ".agents/commands/sudo-push-e2e.md"),
        ("B a rule", ".agents/rules/git-policy.md"),
        ("C a safety-net script", ".agents/scripts/closeout_preflight.py"),
        ("D a commit gate", ".agents/scripts/git-hooks/commit-msg-jira.sh"),
        ("E the front door", "AGENTS.md"),
    ]:
        ok, off, _ = evaluate([path], "SCC-31 change something")
        c.check(f"{label} without the SOP doc is blocked", not ok and len(off) == 1,
                f"{path} -> {off[0][1] if off else 'NOT FLAGGED'}")

    ok, _, _ = evaluate([".githooks/commit-msg"], "SCC-31 rewire")
    c.check("F an installed hook shim is a surface", not ok)

    ok, _, _ = evaluate([".agents/scripts/sync-agents.ps1"], "SCC-31 sync change")
    c.check("G the .ps1 propagation engine counts, not just .py", not ok)

    # ── H-N: the exemptions ───────────────────────────────────────────────────
    for label, path in [
        ("H rules INDEX churn", ".agents/rules/INDEX.md"),
        ("I commands INDEX churn", ".agents/commands/INDEX.md"),
        ("J this gate's own tests", ".agents/scripts/tests/test_sop_currency.py"),
        ("K reference material", ".agents/reference/INDEX.md"),
        ("L templates", ".agents/templates/story.md"),
        ("M skills", ".agents/skills/foo/SKILL.md"),
        ("N artifacts history", "_artifacts/_main/x/implementation_plan.md"),
    ]:
        ok, _, _ = evaluate([path], "SCC-31 housekeeping")
        c.check(f"{label} does not fire", ok, path)

    ok, _, _ = evaluate([SOP_DOC], "SCC-31 doc-only edit")
    c.check("O the SOP doc alone is never its own trigger", ok)

    # A CHILD project's toolkit is tier-2 and has its own law; this gate guards the CENTER.
    ok, _, _ = evaluate(["Projects/AGY_AVIATIONCHAT/.agents/rules/local.md"], "AVCH-23 x")
    c.check("P a project's own .agents/ is out of scope", ok)

    # ── Q-R: satisfying the gate ──────────────────────────────────────────────
    ok, _, why = evaluate([".agents/commands/x.md", SOP_DOC], "SCC-31 add /x + document it")
    c.check("Q staging the SOP doc alongside passes", ok, why)

    ok, _, why = evaluate([".agents/commands/x.md"], "SCC-31 typo in a comment [sop-ok]")
    c.check("R the escape hatch passes", ok, why)

    ok, _, _ = evaluate([".agents/commands/x.md"], "SCC-31 [SOP-OK] shouting at 2am")
    c.check("R2 the escape hatch is case-insensitive", ok)

    # ── S: THE REGRESSION. git appends the staged-file list to the message file. ──
    with TempDir() as tmp:
        msg = tmp / "COMMIT_EDITMSG"
        msg.write_text(
            "SCC-31 rename a command\n"
            "#\n"
            "# Changes to be committed:\n"
            f"#\tmodified:   {SOP_DOC}\n"
            "#\tmodified:   .agents/commands/x.md\n",
            encoding="utf-8")
        rc, out = run_script("sop_currency.py", "--repo", str(tmp),
                             "--message-file", str(msg),
                             "--paths", ".agents/commands/x.md")
        # Marker absent in the temp repo -> warn mode -> rc 0. The proof is the COMPLAINT.
        c.check("S git's comment block cannot satisfy the gate",
                "was not updated" in out, f"rc={rc}")

    # ── T-U: armed vs warn ────────────────────────────────────────────────────
    with TempDir() as tmp:
        (tmp / ".agents" / "scripts" / "git-hooks").mkdir(parents=True)
        rc_warn, _ = run_script("sop_currency.py", "--repo", str(tmp),
                                "--message", "SCC-31 x", "--paths", ".agents/commands/x.md")
        c.check("T disarmed: complains but allows the commit", rc_warn == 0, f"rc={rc_warn}")

        (tmp / MARKER).write_text("armed\n", encoding="utf-8")
        rc_armed, out = run_script("sop_currency.py", "--repo", str(tmp),
                                   "--message", "SCC-31 x", "--paths", ".agents/commands/x.md")
        c.check("U armed: rejects the commit", rc_armed == 1 and "rejected" in out,
                f"rc={rc_armed}")

        rc_ok, _ = run_script("sop_currency.py", "--repo", str(tmp),
                              "--message", "SCC-31 x [sop-ok]", "--paths", ".agents/commands/x.md")
        c.check("V armed + escape hatch: allows", rc_ok == 0, f"rc={rc_ok}")

    # ── W: never a false block ────────────────────────────────────────────────
    ok, _, _ = evaluate([], "SCC-31 empty stage")
    c.check("W an empty change set passes", ok)

    c.check("X windows-style separators normalize",
            classify(r".agents\commands\x.md") is not None)

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
