"""step-01's lens-roster contract — one section, one invariant. (SCC-229/230/232, cut by SCC-447)

Five sections accreted one ticket at a time all answered "which lenses actually ran, under
what constraint": lens_budget (SCC-147), review_runtime (SCC-177), cannot-launch
(SCC-173), the inline Blind-Hunter drop (SCC-203), skipped-by-mode. SCC-229 collapses
them into ONE contract built on the invariant that subsumes them, and the checks below pin
that the consolidation lost nothing; the invariant may appear exactly once.

⛔ THREE OF THE FIVE SCARS ARE NOW RETIREMENTS, and the checks changed shape rather than
disappearing. SCC-447 cut the roster to three lenses, which took `lens_budget` (SCC-147),
the inline Blind-Hunter drop (SCC-203) and the two `review_level` levels (SCC-232) with it —
each had exactly one lens to protect and that lens is gone. A deletion cannot be pinned by a
keyword ban here, because the retirement note has to NAME what it retired; so each is held
positively instead: the note names it, the defining section is absent, and the input spelling
a live caller would have to write is absent. `review_runtime` (SCC-177) and the dead-lens
ladder (SCC-173) survive unchanged — they were never about a particular lens. RED-first.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _harness import Cases  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
STEP01 = (ROOT / ".agents/skills/code-review-engine/steps/step-01-review.md").read_text(encoding="utf-8")
STEP04 = (ROOT / ".agents/skills/code-review-engine/steps/step-04-record.md").read_text(encoding="utf-8")


def main() -> int:
    c = Cases("lens_roster_contract")
    t = STEP01

    # ── the consolidation itself ──────────────────────────────────────────────
    c.check("ONE roster-contract section exists",
            len(re.findall(r"^## .*lens-roster contract", t, re.M | re.I)) == 1,
            str(re.findall(r"^## .*$", t, re.M)[:3]))
    inv = re.findall(r"ends the run in exactly one declared state", t)
    c.check("the invariant sentence is stated exactly once", len(inv) == 1, f"{len(inv)}x")
    for gone in (r"^## ⭐ `review_runtime`", r"^## When a lens cannot be launched",
                 r"^## Skipped-by-mode"):
        c.check(f"old standalone h2 gone: {gone[4:40]}",
                not re.search(gone, t, re.M), "still present as its own h2")

    # ── SCC-147: the budget axis, defined once, inside the contract ───────────
    # ⛔ Anchor on the HEADING, not the first casual mention: `find("lens-roster contract")`
    # hit the :200 forward-pointer, 232 lines above the real h2 - executed mutant (SCC-225
    # review wave): the whole lens_budget subsection moved ABOVE the contract and this check
    # stayed green, because 27774 > 13121. The consolidation guarantee is position, so the
    # position must be the section's, not a sentence's.
    # ── SCC-147 → RETIRED by SCC-447. `lens_budget` was the Literal-Correctness Hunter's cost
    # axis, and it retired with that lens. Asserted POSITIVELY — the retirement note names it —
    # plus the absence of the heading a live definition would need. A bare "`lens_budget` not in
    # t" is unwritable here: the retirement note has to say the word to retire it.
    buddefs = [m.start() for m in re.finditer(r"^### `lens_budget`", t, re.M)]
    contract_h2 = re.search(r"^## .*lens-roster contract.*$", t, re.M | re.I)
    c.check("SCC-447: the lens_budget axis is retired — no defining section remains",
            contract_h2 is not None and not buddefs,
            f"defs={len(buddefs)} h2@{contract_h2.start() if contract_h2 else -1}")
    c.check("SCC-447: the retirement NAMES lens_budget, so the word cannot be banned outright",
            "`lens_budget`, the `EVIDENCE_PACK` priming" in t,
            "the retirement note stopped naming what it retired")
    c.check("SCC-447: no live caller could pass a budget — the input spelling is gone",
            not re.search(r"`lens_budget: (standard|capped)`", t),
            "a live `lens_budget:` input spelling survives in step-01")

    # ── SCC-177: runtime declared by the caller + the measured expectations ───
    c.check("SCC-177: inline + `ok` is still a checked contradiction",
            "`inline` + a lens reported `ok` is a contradiction" in t, "guard lost")
    c.check("SCC-177: never re-attempt the fan-out after inline",
            "never re-attempt it after" in t, "re-fan-out ban lost")
    c.check("SCC-177: the measured runtime expectations are carried (slow = a lens, "
            "never the harness)",
            "0.19" in t and "35–65" in t and "22–44" in t, "scoring.md numbers absent")

    # ── SCC-173: launch failure is a recorded outcome ─────────────────────────
    c.check("SCC-173: the dead-lens ladder survives (retry → inline → record → floor)",
            "Retry it once" in t and "raises `severity_floor` to CONCERNS" in t,
            "ladder lost")
    c.check("SCC-173: recovered-inline never reads as a gap",
            "`recovered-inline`" in t and "cost time, not coverage" in t, "state lost")

    # ── SCC-203 → RETIRED by SCC-447 with the lens it protected ───────────────
    # The drop rule existed because the Blind Hunter's value was its starvation, and an inline
    # run in a contaminated context produced a roster claiming more independence than the review
    # had. No lens on the roster now depends on starvation, so the rule has nothing to guard.
    # Pinned by the retirement note plus the absence of the row.
    c.check("SCC-447: the Blind Hunter is retired, by name, in the retirement note",
            "The Blind Hunter, the Literal-Correctness" in t,
            "the retirement stopped naming the lens it retired")
    c.check("SCC-447: no Blind Hunter row survives in the fan-out table",
            not re.search(r"^\|\s*\*\*Blind Hunter\*\*", t, re.M),
            "a retired lens is still routed by the table")

    # ── skipped-by-mode ≠ dead ────────────────────────────────────────────────
    c.check("mode-skip is declared, uncounted, and never raises the floor",
            "lenses_na" in t and "never raises `severity_floor`" in t
            and "`2/2`, never `2/3`" in t, "distinction lost")

    # ── SCC-230: doc-truth — no unfunded cost claim, the fence on :440 ────────
    c.check("SCC-230: the unfunded cost headline is struck",
            "the one lens with a real token cost" not in t, "claim survives")
    # SCC-230's per-lens cost table measured five lenses, three of which no longer exist; it
    # retired with them. What the ticket actually bought was the DISCIPLINE — a cost or value
    # claim about a lens speaks from data or not at all — and SCC-447's retirement is the same
    # discipline applied to the roster itself. That is what is pinned now: the retirement cites
    # its measurement, and the re-entry rule names measurement as the only road back.
    c.check("SCC-447: the retirement cites its own measurement, not an argument",
            "17.9 fixes per review" in t and "2 findings in 18 reviews" in t,
            "the retirement lost the numbers that justify it — an unfunded claim again")
    c.check("SCC-447: a lens returns by MEASUREMENT, and the bar is named",
            "A lens is added back by measurement, never by argument." in t
            and "per-lens ledger data" in t,
            "the re-entry rule is missing or names no bar")
    c.check("SCC-230: the surviving cost datum still cites scoring.md",
            "scoring.md" in t and "220.5" in t, "the measured citation was dropped")
    c.check("SCC-230: the noise-filter ruling still binds diff-anchored review",
            'Never gate findings on "worthiness"' in t, "the ruling was repealed")
    c.check("SCC-230: the ruling is scope-fenced to diff-anchored review",
            "applies where findings are anchored to a diff" in t
            and "anchor rule of SCC-225 governs" in t, "fence absent")
    c.check("SCC-230: external benchmarks need source and version, and the uncited "
            "one is gone",
            "source and version" in t and "0.69" not in t and "0.52" not in t,
            "pr-af number still cited without a source")
    c.check("SCC-230: the paragraph no longer forbids its own revision",
            "this paragraph is the answer" not in t, "self-sealing clause survives")

    # ── SCC-232 → RETIRED by SCC-447: there are no levels ─────────────────────
    # `quick` and `standard` split the ROSTER by the caller's measured radius, so a small diff
    # got two lenses and a large one got five. The roster is three lenses on every review now,
    # and the thing that scales with radius is the SCOPE of the diff handed in (`review_scope.py`,
    # Part 2) — not the number of readers. The level's own surfaces retire with it in Part 4;
    # what is pinned here is that step-01, the one place it was DEFINED, no longer defines it.
    c.check("SCC-447: no two-levels section survives",
            not re.search(r"^### The two levels", t, re.M),
            "the level section is still here")
    c.check("SCC-447: the retirement names the levels it retired",
            "the two `review_level` levels" in t, "the retirement stopped naming them")
    c.check("SCC-447: no live review_level input spelling survives",
            not re.search(r"`review_level: (quick|standard)`", t),
            "a live `review_level:` input spelling survives in step-01")
    c.check("SCC-447: no `--level` caller flag exists on this surface",
            "--level" not in t, "a caller flag grew back")
    # ⛔ The `Runs when` column is what the level used to drive, so it is the cell a level would
    # grow back in. Bind it POSITIVELY to the only two values the roster now allows.
    runs_when = {ln.split("|")[4].strip() for ln in t.splitlines()
                 if ln.startswith("| **") and ln.count("|") >= 6}
    c.check("SCC-447: every `Runs when` cell is `always` or the Acceptance mode-skip",
            runs_when == {"always", "`review_mode: full` only"},
            f"the fan-out table's Runs-when values are {sorted(runs_when)}")

    # ── the return shape ROUND-TRIPS through the parser that reads it ─────────
    # Presence ("lenses_run:" in STEP04) was the shipped check - a reshaped line passed it
    # while breaking the one machine reader. Same cure as SKILL.md's block: fill the
    # placeholders and parse for real.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import walkthrough_roster as roster  # noqa: E402
    m = re.search(r"^```\n(review-runtime:[\s\S]*?^lenses_run:[\s\S]*?)^```", STEP04, re.M)
    c.check("step-04 publishes the SAME fenced return block as SKILL.md (block "
            "lenses_run, never the retired counted line)",
            m is not None, "no fenced block opening with review-runtime + lenses_run rows")
    if m:
        rows, filled = 0, []
        for ln in m.group(1).splitlines():
            if ln.startswith("- "):
                rows += 1
                filled.append(f"- lens-{rows} · ok")
            elif re.match(r"^review[-_]runtime\s*:", ln, re.I):
                filled.append("review-runtime: fan-out")
            else:
                filled.append(ln)
        data = roster.parse("# W\n\n## Code Review\n\n" + "\n".join(filled) + "\n")
        c.check("step-04 round-trip: the parser reads every roster row the block "
                "promises",
                rows >= 2 and len(data["lenses"]) == rows,
                f"wrote {rows}, parser read {len(data['lenses'])}")
        c.check("step-04 round-trip: the dispositions template line is readable by the "
                "machine tier that gates it",
                data["dispositions"] is not None
                and data["dispositions"].startswith("per-lens:"),
                repr(data["dispositions"]))

    # ── SCC-301: the TREE half of isolation - a lens could edit the tree it reviews ──────
    # Measured twice (SCC-298, SCC-295 lanes): three of five lenses edited the builder's
    # working tree mid-review, and one reported a RED result no version of the code under
    # review can produce - the builder was reading a lens's own mutant. "Clean context" was
    # only half the launch contract; this is the other half, pinned.
    SKILL = (ROOT / ".agents/skills/code-review-engine/SKILL.md").read_text(encoding="utf-8")
    dup = t.count("in parallel, each in its own clean context")
    c.check("SCC-301 B5: the launch sentence appears exactly ONCE (aafe0d4's duplicate gone)",
            dup == 1, f"{dup}x - the sentence was pasted twice at :27-31 by aafe0d4 (SCC-190)")
    c.check("SCC-301 B1: the launch states the TREE half - worktree isolation, by name",
            'isolation: "worktree"' in t,
            "the launch paragraph must name the Agent tool's worktree isolation, or every "
            "lens inherits write access to the tree under review")
    c.check("SCC-301 B2: the lens table carries a Tree column",
            "| Tree |" in t, "per-lens isolation is table wiring, not prose")
    # SCC-301 B2b retired with the Blind Hunter: it was the only DIFF-only lens, and the
    # `no tree` cell existed for it alone. Every surviving lens reads the repo, so the
    # invariant below is now unconditional — a worktree copy in EVERY row, with no exception
    # left to hide behind.
    rows = [ln for ln in t.splitlines()
            if ln.startswith("| **") and "Hunter**" in ln or ln.startswith("| **") and "Auditor**" in ln]
    bad = [ln.split("|")[1].strip() for ln in rows
           if 'isolation: "worktree"' not in ln.split("|")[3]]
    c.check("SCC-301 B2c: EVERY lens row's Tree cell is its own worktree copy - none may "
            "share the builder's tree, and no row is exempt any more",
            len(rows) == 3 and not bad, f"rows={len(rows)} bad={bad}")
    c.check("SCC-301 B4: a lens that writes to its tree is a HARD FAILURE, not a warning",
            "A lens that WRITES is a hard failure" in t,
            "without this the roster records `ok` for a lens that rewrote its own subject")
    c.check("SCC-301 B3a: the engine's return states the isolation mode (SKILL.md)",
            "lens_isolation:" in SKILL, "the contract line is the checkable surface")
    c.check("SCC-301 B3b: ...and the recorded roster carries the same line (step-04)",
            "lens_isolation:" in STEP04, "a mode stated but never recorded cannot be audited")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
