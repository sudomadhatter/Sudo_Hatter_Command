"""step-01's lens-roster contract — one section, five scars, one invariant. (SCC-229/230/232)

Five sections accreted one ticket at a time all answered "which lenses actually ran, under
what constraint": lens_budget (SCC-147), review_runtime (SCC-177), cannot-launch
(SCC-173), the inline Blind-Hunter drop (SCC-203), skipped-by-mode. SCC-229 collapses
them into ONE contract built on the invariant that subsumes them. One mutation per scar
ticket pins that the consolidation lost nothing; the invariant may appear exactly once.
SCC-230's doc-truth guards and SCC-232's level checks ride the same file. RED-first.
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
    buddefs = [m.start() for m in re.finditer(r"^### `lens_budget`", t, re.M)]
    contract_h2 = re.search(r"^## .*lens-roster contract.*$", t, re.M | re.I)
    c.check("SCC-147: lens_budget defined exactly once, inside the contract (anchored "
            "on the h2, not the first mention)",
            contract_h2 is not None and len(buddefs) == 1
            and buddefs[0] > contract_h2.start(),
            f"defs={len(buddefs)} h2@{contract_h2.start() if contract_h2 else -1}")
    c.check("SCC-147: the top-up clause still reaches only `standard`",
            "You may earn ONE top-up" in t and "Under `capped` you append nothing" in t,
            "top-up mechanics lost")
    c.check("SCC-147: review_mode and lens_budget still declared independent",
            "`lens_budget` is NOT `review_mode`" in t, "independence guard lost")

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

    # ── SCC-203: the Blind Hunter is dropped, never faked ─────────────────────
    c.check("SCC-203: contamination drops the lens rather than faking it",
            "DROPPED" in t and "context contaminated" in t, "drop rule lost")
    c.check("SCC-203: the retired not-blind state cannot return",
            "retired" in t and "ok (not blind" in t, "retirement record lost")

    # ── skipped-by-mode ≠ dead ────────────────────────────────────────────────
    c.check("mode-skip is declared, uncounted, and never raises the floor",
            "lenses_na" in t and "never raises `severity_floor`" in t
            and "`4/4`, never `4/5`" in t, "distinction lost")

    # ── SCC-230: doc-truth — no unfunded cost claim, the fence on :440 ────────
    c.check("SCC-230: the unfunded cost headline is struck",
            "the one lens with a real token cost" not in t, "claim survives")
    c.check("SCC-230: per-lens cost speaks only from the measured table, cited",
            "scoring.md" in t and "220.5" in t and "180.9" in t and "127.4" in t
            and "75.3" in t, "measured table absent")
    c.check("SCC-230: Literal-Correctness is labelled unmeasured",
            "unmeasured" in t, "label absent")
    c.check("SCC-230: the note for the record - most expensive AND the one unseeded "
            "true positive",
            "unseeded true" in t, "cost-is-not-the-whole-ledger note absent")
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

    # ── SCC-232: two levels, derived from measured radius, membership data-gated ─
    c.check("SCC-232: quick and standard are defined as lens SETS in the contract",
            "### The two levels" in t and "quick" in t and "standard" in t,
            "level section absent")
    c.check("SCC-232: quick = Test-Adequacy + Acceptance (the measured split)",
            "Test-Adequacy + Acceptance" in t, "membership not the measured one")
    # Part G's data-gating promise, landed for real: the addendum FILE is opened and the
    # cited number cross-checked against it - deleting the file or drifting the citation
    # goes red, where the old substring check stayed green through both (executed).
    addendum = ROOT / "_artifacts/_main/2026/08/2026-08-20_scc-225-review-surface/lc-cost-measurement.md"
    if not addendum.is_file():
        addendum = ROOT / "_artifacts/_main/2026-08-20_scc-225-review-surface/lc-cost-measurement.md"
    c.check("SCC-232: the measurement addendum file EXISTS where step-01 cites it",
            addendum.is_file(), str(addendum))
    add_txt = addendum.read_text(encoding="utf-8") if addendum.is_file() else ""
    c.check("SCC-232: step-01's cited number matches the addendum's measured datum",
            "1,082" in t and "lc-cost-measurement.md" in t and "1,082.0" in add_txt,
            "citation and source disagree, or the datum left the addendum")
    c.check("SCC-232: the level is DERIVED from Step 0.7, never a caller flag",
            "never a flag the caller" in t, "derivation rule absent")
    c.check("SCC-232: no `--level` caller flag exists on any surface (the promised "
            "absence check)",
            "--level" not in t, "a caller flag grew back")
    c.check("SCC-232: the two-levels section still declares no budgets and no caps",
            "No minute budget and no finding cap exists on either level" in t,
            "the no-budget law left the level section")
    c.check("SCC-232: a lens excluded by level reports skipped-by-mode, never dead",
            "level: quick" in t, "exclusion state absent")
    # The quick rule is stated once in the contract and restated in three caller surfaces;
    # the ≤3-file threshold is the load-bearing token, so every restatement is pinned to it -
    # changing one site to ≤5 goes red HERE, not in nobody's diff review (executed mutant:
    # token-presence alone survived the inversion "review_level is NOT derived").
    # the SOP legitimately re-orders the sentence, so the pinned token is the THRESHOLD
    # itself - the part whose silent drift (≤3 → ≤5) re-scopes which lenses run
    QUICK_TOKEN = "≤3 source files"
    c.check("SCC-232: the contract's own quick rule carries the threshold token",
            QUICK_TOKEN in t, "the contract lost its own threshold")
    for name, cmd_path in (("smh", ".agents/commands/smh-code-review.md"),
                           ("cicd", ".agents/commands/cicd-code-review.md")):
        cmd = (ROOT / cmd_path).read_text(encoding="utf-8")
        c.check(f"SCC-232: {name} Step 0.7 derives the level from its own measured "
                f"radius",
                "review_level" in cmd and "derived" in cmd.lower(), "derivation absent")
        c.check(f"SCC-232: {name}'s restated quick rule matches the contract's "
                f"threshold verbatim",
                QUICK_TOKEN in cmd, "restatement drifted from the contract")
        c.check(f"SCC-232: {name}'s derivation paragraph sits inside a twin-law fence "
                f"(parity guards the restatements against each other)",
                "<!-- twin-law: review-level -->" in cmd, "fence removed")
        c.check(f"SCC-232: {name} carries no `--level` caller flag either",
                "--level" not in cmd, "a caller flag grew back")
    sop = (ROOT / "docs/_scc_sops_prds/workflows_testing_SOP.md").read_text(encoding="utf-8")
    c.check("SCC-232: the SOP's restated quick rule matches the contract's threshold",
            QUICK_TOKEN in sop, "SOP restatement drifted")

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
    blind = next((ln for ln in t.splitlines() if ln.startswith("| **Blind Hunter**")), "")
    c.check("SCC-301 B2b: ...and the Blind Hunter's row says NO tree at all",
            "no tree" in blind, f"DIFF-only lens must not get a repo copy: {blind[:160]}")
    # Every lens row's Tree cell individually (review: B1's whole-file grep let one row's
    # cell be rewritten while the string survived in the other rows).
    rows = [ln for ln in t.splitlines()
            if ln.startswith("| **") and "Hunter**" in ln or ln.startswith("| **") and "Auditor**" in ln]
    bad = [ln.split("|")[1].strip() for ln in rows
           if 'isolation: "worktree"' not in ln.split("|")[3] and "no tree" not in ln.split("|")[3]]
    c.check("SCC-301 B2c: EVERY lens row's Tree cell is a worktree copy or an explicit "
            "no-tree - none may share the builder's tree",
            len(rows) == 5 and not bad, f"rows={len(rows)} bad={bad}")
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
