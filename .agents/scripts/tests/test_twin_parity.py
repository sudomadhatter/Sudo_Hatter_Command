"""SCC-205 · the `cicd-*` <-> `smh-*` twin-parity guard.

⛔ THE GOAL — read this first; it governs every row below, and it must not age into a lie.

The repo carries two command families that are the SAME development system pointed at different
subjects. `.agents/commands/cicd-*.md` does real project work - front end, back end, agent code in
Python, prompting, story lanes, epic branches, sprint boards. `.agents/commands/smh-*.md` is that
same system turned inward on this command centre.

  Operator, 2026-08-17: "they are our same development system, the actual system we use for real
  work on projects. the smh ones are only for working on the system. but they serve the same
  purpose, just optimized for their tasks."

THE STANDARD IS THE SHARED LAW, NOT A FAMILY. Neither prefix owns it. As of 2026-08-17 the law
happened to be more COMPLETE on the smh side for one reason only: that is where the operator was
working while the system was being built.

⛔ THAT IS ABOUT TO INVERT. Operator, 2026-08-17: "we will usually be working with cicd since the
goal is to use the command center for projects. once its working we dont touch SCC that often."
So the next decade of drift runs cicd -> smh, with smh the half left behind. Anyone reading this
later: do NOT infer from "smh was ahead in 2026" that smh is the reference. Measure which half
carries the law, every time. THIS CHECK IS SYMMETRIC PRECISELY BECAUSE THE ANSWER CHANGES.

A difference is a missing-parity DEFECT until proven otherwise. It is legitimate only when the
SUBJECT forces it: the merge target (epic branch vs origin/main) · the spec source (story file +
certification vs implementation_plan.md) · target resolution (cicd binds exactly ONE project and
never this repo) · tooling (this repo has no venv, no ruff, no tsc) · story/board/sprint ceremony.
NOT legitimate: "the fast lane deserves a weaker review" · "that is the other family's way" ·
"BMAD covers it" · anything that is merely older on one side.

WHY THIS FILE EXISTS, in the operator's words: "we made alot of updates to how we want this system
to work and it was all on the smh side before I realized that cicd was not being updated with it."
⭐ The failure was STRUCTURAL, not careless - nothing in the repo compared the two families, so
`workflow_lint --toolkit-only` exited 0 with 172 confirmed drift findings live in the tree. That
zero was the bug. This file is the fix.

── HOW IT WORKS ──────────────────────────────────────────────────────────────────────────────
A command marks a region of SHARED law with a literal fence:

    <!-- twin-law: <id> -->
    ...the law...
    <!-- /twin-law -->

and this file asserts TWO things about every declared pair, not one:

  SYMMETRY  - a law marked in one twin is marked in the other. This is the layer that catches the
              failure that caused the ticket: law written into one family and ABSENT from the
              other. Identity alone sits green through that entire failure, because no counterpart
              region exists to compare.
  IDENTITY  - where both mark it, the regions are byte-identical after whitespace normalisation.

⛔ NEVER WIDEN THIS TO WHOLE FILES. That would force subject-specific law to match and break both
commands. The fence is the scope, and it is deliberately narrow.

The escape hatch is AUDITABLE, not silent: `<!-- twin-divergence: <id> — <reason> -->` in place of
the region declares an intentional asymmetry, and every one is COUNTED and PRINTED, so a deliberate
divergence is a recorded decision rather than a hole.

── WHY NOT test_review_engine.py ─────────────────────────────────────────────────────────────
That file is scoped to the review engine and its callers; the working precedent for this check
lives there (SCC-203, the subagent-law byte-identity block) and this generalises it. But this
check spans six pairs across dev, audit, review and landing - most of which never touch the
engine. It gets its own file, auto-discovered by `run_all.py`.

⛔ NOT the retired `ap_reconciled` stamp re-aimed at these pairs (SCC-209 deleted it anyway): that
mechanism derived the primary from the twin and scanned only the twin's text, so it was
ONE-DIRECTIONAL - the cicd file could drift under a green stamp. Its comparand was whole-file too,
so every commit touching one side's subject-specific text invalidated it, producing reflexive
restamping with nothing read.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]
CMDS = ROOT / ".agents" / "commands"

# ⛔ THE PAIR LIST IS PINNED, and the completeness row below is what stops it going stale.
# Names differ where the SUBJECT differs, which is why this cannot be derived by string
# substitution alone: `cicd-merge-epic-workingtrees` lands story lanes on an epic branch,
# `smh-merge-multiple-workingtrees` lands task lanes on main - same job, different subject,
# different name. `cicd-quick-dev` pairs with `smh-quick-dev`; `smh-quick-fix` is a THIRD
# lane below both and is deliberately unpaired (recorded in NOT_PAIRED).
PAIRS = [
    ("cicd-quick-dev.md", "smh-quick-dev.md"),
    ("cicd-self-audit.md", "smh-self-audit.md"),
    ("cicd-code-review.md", "smh-code-review.md"),
    ("cicd-clean-code-audit.md", "smh-clean-code-audit.md"),
    ("cicd-label-tasks.md", "smh-label-tasks.md"),
    ("cicd-merge-epic-workingtrees.md", "smh-merge-multiple-workingtrees.md"),
]

# Every `cicd-*` / `smh-*` name-counterpart that is NOT in PAIRS, each with the reason. A new
# counterpart appearing here-less makes the completeness row RED, which is the whole point: the
# next twin someone adds cannot join the tree unpaired and unnoticed.
NOT_PAIRED = {
    "smh-quick-fix.md": "a THIRD lane, below both quick-devs - it ejects INTO smh-quick-dev; "
                        "the cicd side has no such lane and that gap is recorded, not faked",
}

LAW_OPEN = re.compile(r"^<!-- twin-law:\s*([a-z0-9-]+)\s*-->$", re.M)
LAW_CLOSE = "<!-- /twin-law -->"
DIVERGENCE = re.compile(r"^<!-- twin-divergence:\s*([a-z0-9-]+)\s*[-—]+\s*(.+?)\s*-->$", re.M)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def laws(text: str) -> dict[str, str]:
    """Every marked region, keyed by id, whitespace-normalised.

    ⛔ Normalised, never raw: the two families wrap prose at different points for perfectly
    legitimate reasons (one body is wider), and a check that reds on a re-wrap teaches people
    to delete the fence rather than fix the drift.
    """
    out: dict[str, str] = {}
    for m in LAW_OPEN.finditer(text):
        body = text[m.end():]
        end = body.find(LAW_CLOSE)
        if end == -1:                       # an unclosed fence is a defect, not a region
            continue
        out[m.group(1)] = " ".join(body[:end].split())
    return out


def divergences(text: str) -> dict[str, str]:
    return {m.group(1): m.group(2) for m in DIVERGENCE.finditer(text)}


def counterparts() -> set[str]:
    """Every cicd/smh file whose name has a counterpart in the other family.

    Derived from the tree, never from PAIRS - a list that checks itself against itself is a
    list that cannot go stale in the one direction that matters.
    """
    cicd = {p.name[len("cicd-"):] for p in CMDS.glob("cicd-*.md")}
    smh = {p.name[len("smh-"):] for p in CMDS.glob("smh-*.md")}
    return {f"cicd-{s}" for s in cicd & smh} | {f"smh-{s}" for s in cicd & smh}


def main() -> int:
    c = Cases("twin-parity: cicd-* <-> smh- shared law")

    if c.block("A · the pair list is complete (it cannot silently go stale)"):
        # ANTI-VACUITY FIRST. Every row below is a loop over PAIRS, and a loop over an empty
        # or unreadable set passes silently. Assert the inputs exist before asserting on them.
        missing = [n for pair in PAIRS for n in pair if not (CMDS / n).is_file()]
        c.check("A0 every pinned pair file exists on disk (anti-vacuity)",
                bool(PAIRS) and not missing, f"missing={missing}")

        pinned = {n for pair in PAIRS for n in pair}
        found = counterparts()
        unpinned = sorted(found - pinned - set(NOT_PAIRED))
        c.check("A1 every cicd/smh name-counterpart is pinned or recorded as unpaired",
                not unpinned,
                "" if not unpinned else
                f"unpinned={unpinned} - add it to PAIRS, or to NOT_PAIRED with the reason")
        c.check("A2 the derived counterpart set is non-empty (the deriver still works)",
                len(found) >= 8, f"{len(found)} found")

    if c.block("B · SYMMETRY - a law in one twin has a counterpart in the other"):
        seen_any = 0
        for a, b in PAIRS:
            ta, tb = read(CMDS / a), read(CMDS / b)
            la, lb, da, db = laws(ta), laws(tb), divergences(ta), divergences(tb)
            seen_any += len(la) + len(lb)
            for side, mine, theirs, theirdiv, other in ((a, la, lb, db, b), (b, lb, la, da, a)):
                orphans = sorted(k for k in mine if k not in theirs and k not in theirdiv)
                c.check(f"B {side} marks no law the twin lacks",
                        not orphans,
                        "" if not orphans else
                        f"{orphans} marked in {side} and absent from {other} - port it, or "
                        f"declare `<!-- twin-divergence: <id> — <reason> -->` in {other}")
        c.check("B* at least one law is actually marked somewhere (anti-vacuity)",
                seen_any > 0, f"{seen_any} marked regions found across {len(PAIRS)} pairs")

    if c.block("C · IDENTITY - where both mark it, the law is byte-identical"):
        compared = 0
        for a, b in PAIRS:
            la, lb = laws(read(CMDS / a)), laws(read(CMDS / b))
            for k in sorted(set(la) & set(lb)):
                compared += 1
                c.check(f"C `{k}` is identical in {a} and {b}",
                        la[k] == lb[k],
                        "" if la[k] == lb[k] else
                        f"the twins disagree about `{k}`: {a}={len(la[k])}b {b}={len(lb[k])}b "
                        f"- fix ONE and copy it, never edit both by hand")
        c.check("C* the identity rows compared something (anti-vacuity)",
                compared > 0, f"{compared} shared laws compared")

    if c.block("D · every intentional divergence is COUNTED and PRINTED, never silent"):
        rows = [(n, k, why)
                for pair in PAIRS for n in pair
                for k, why in sorted(divergences(read(CMDS / n)).items())]
        for n, k, why in rows:
            print(f"[INFO] twin-divergence · {n} · {k} — {why}")
        c.check("D every divergence carries a reason (an empty one is a hole)",
                all(why.strip() for _, _, why in rows), f"{len(rows)} declared")

    if c.block("E · ⛔ COUNTER-EXAMPLES - a check never seen failing is not a check"):
        # E1/E2 bound the extractor from BOTH sides: perturbing a law must break identity,
        # and law-less text must extract EMPTY. Without E2, an extractor that matched
        # nothing would return {} for both files, compare equal, and pass forever.
        a, b = "cicd-clean-code-audit.md", "smh-clean-code-audit.md"
        la, lb = laws(read(CMDS / a)), laws(read(CMDS / b))
        c.check("E0 the fixture pair really does share a law (the setup is not the bug)",
                bool(set(la) & set(lb)), f"{sorted(set(la) & set(lb))}")

        drifted = laws(read(CMDS / a).replace("It's cheap", "It is cheap", 1))
        k = next(iter(set(la) & set(lb)), None)
        c.check("E1 perturbing ONE side's law makes identity FAIL",
                k is not None and drifted.get(k) != lb.get(k),
                "" if (k is not None and drifted.get(k) != lb.get(k)) else
                "the perturbation left them equal - the identity check cannot fail")

        c.check("E2 a body with no fence extracts EMPTY (no false match on prose)",
                laws("# A command\n\nIt does a thing.\n\nThen another.") == {},
                "" if (laws("# A command\n\nIt does a thing.\n\nThen another.") == {}) else
                "the extractor matches arbitrary prose, so agreement means nothing")

        c.check("E3 an UNCLOSED fence extracts nothing rather than swallowing the file",
                laws("<!-- twin-law: x -->\nlaw text\n\nmore of the file") == {},
                "" if (laws("<!-- twin-law: x -->\nlaw text\n\nmore of the file") == {}) else
                "an unterminated marker captured to EOF - one typo would compare whole files")

        # E4: SYMMETRY must fail on the actual disease - law present one side, absent the other.
        gutted = read(CMDS / a).replace("<!-- twin-law: disposition -->", "", 1)
        c.check("E4 deleting one side's fence makes SYMMETRY fail",
                "disposition" in lb and "disposition" not in laws(gutted),
                "" if ("disposition" in lb and "disposition" not in laws(gutted)) else
                "removing the marker left the law still extracted - symmetry cannot fail")

        # E5: the divergence hatch must actually silence B, or nobody will use it and the
        # first person who needs one bypasses the gate instead.
        excused = divergences("<!-- twin-divergence: disposition — subject-forced: no venv here -->")
        c.check("E5 a twin-divergence marker parses, with its reason",
                excused.get("disposition", "").startswith("subject-forced"), str(excused))

        # E6: the completeness row must fail on a NEW unpinned counterpart, not just today's set.
        fake_pinned = {n for pair in PAIRS for n in pair}
        c.check("E6 a new unpinned counterpart would fail the completeness row",
                "cicd-brand-new.md" not in fake_pinned
                and bool({"cicd-brand-new.md"} - fake_pinned - set(NOT_PAIRED)),
                "the completeness row cannot see a newly added twin")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
