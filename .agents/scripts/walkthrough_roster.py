#!/usr/bin/env python3
"""walkthrough_roster — the ONE parser for a lane's review roster (SCC-173 + SCC-177).

⛔ WHY THIS FILE EXISTS AT ALL.

`closeout_preflight.py` and `task_preflight.py` both gate a lane on its walkthrough's
`Verdict:` line — and **a `Verdict: PASS @ <sha>` with zero lenses actually run merges
cleanly**. Nothing in this repo could tell the difference between a review that ran and a
review that was narrated, because the only evidence a review left behind was the one line
asserting its own conclusion. That is self-certification with an extra step, and it was found
by SCC-163's own self-audit *while that lane was closing*.

Measured 2026-08-15 across 142 walkthroughs: **12 carried a roster, 130 did not**, and only 45
carried a `Verdict:` at all. So the requirement is scoped by a **dated cutoff** rather than
applied retroactively — see `CUTOFF`.

⭐ ONE PARSER, TWO CALLERS, ON PURPOSE. Story lanes close through `closeout_preflight.py` and
Task lanes through `task_preflight.py`; the two read `Verdict:` with *different* regexes
already (one lenient, one strict), and a second copy of this logic would drift the same way.
Each caller passes the verdict IT read, so the scoping question — "is this lane in scope for a
roster?" — is answered by the reader's own eyes, never by a third opinion.

⛔ IT BLOCKS. Operator ruling 2026-08-15, verbatim: *"I dont see a case in enterprise dev where
a warn should make it to prod ?"* … *"yes you can use those as my words update the plan so we
dont have to do that at all"*. There is no `--strict-lenses` opt-in to build; blocking IS the
shipped behaviour, and the dated cutoff is the scope limiter rather than a warn tier. The
escape hatch is not a bypass — it is the inline ladder: run the lenses inline, record
`recovered-inline`, and take the CONCERNS floor.
"""
from __future__ import annotations

import re
from pathlib import Path

# ⛔ A LITERAL DATE, NOT "the day E lands" (F28). The plan first wrote the cutoff as the day
# this shipped, which would have made the lane that BUILT the parser legacy — the first lane it
# did not bind would be the one that wrote it. A literal is also deterministic on both machines
# and on a fresh clone, where "today" is whatever the runner says.
CUTOFF = "2026-08-15"

# Per-lens outcomes. `recovered-inline` is not a lesser `ok`: it records that the lens ran
# INLINE after fan-out was unavailable, which is the legal state under `review-runtime: inline`
# and the thing that makes a CONCERNS floor honest rather than a downgrade.
STATES = ("ok", "recovered-inline", "dead")

RUNTIMES = ("fan-out", "inline")

_ROSTER_HEAD_RE = re.compile(r"^[>\-*#\s]*\**\s*lenses_run\s*:\**\s*$", re.I)
_ROSTER_ROW_RE = re.compile(r"^\s*[-*]\s*`?([A-Za-z0-9][\w \-/]*?)`?\s*[·:|]\s*"
                            r"`?(ok|recovered-inline|dead)`?\s*(?:[—\-]\s*(.*))?$", re.I)
# ⛔ BOTH SPELLINGS, DELIBERATELY. The caller contract names the input `review_runtime` (house
# style, matching `review_mode` and `lens_budget`); the walkthrough header is written
# `review-runtime:`. An agent reading the contract and writing the header will sometimes carry the
# underscore across, and a header this regex cannot see is not an error anyone gets told about —
# `runtime` comes back `None`, I3 never fires, and the gate reports clean. Reading both costs one
# character class; refusing one costs a silent hole of exactly the kind this lane exists to close.
_RUNTIME_RE = re.compile(r"^[>\-*#\s]*\**\s*review[-_]runtime\s*:\**\s*\**(fan-out|inline)\**",
                         re.I | re.M)
_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

# E7 — Step 0.7's re-derivation. The heading is matched loosely because it is prose written by
# hand; what is COUNTED is the three numbered lines under it. "nothing moved" is a valid line.
_REDERIVE_HEAD_RE = re.compile(r"^#{1,6}\s.*(0\.7|re-?deriv)", re.I)
_LIST_ROW_RE = re.compile(r"^\s*(?:\d+\.|[-*])\s+\S")


def lane_date(path: Path | str) -> str | None:
    """The lane's date, from the ARTIFACT FOLDER's `YYYY-MM-DD` prefix — never the file's
    mtime (a checkout rewrites it) and never `git log` (a rebase rewrites that too)."""
    for part in reversed(Path(path).resolve().parts):
        m = _DATE_RE.match(part)
        if m:
            return m.group(1)
    return None


def parse(text: str) -> dict:
    """Everything this module reads out of a walkthrough, in one pass.

    Deliberately total: it never raises and never decides. `judge()` decides."""
    lines = text.splitlines()
    lenses: list[dict] = []
    for i, ln in enumerate(lines):
        if not _ROSTER_HEAD_RE.match(ln):
            continue
        for row in lines[i + 1:]:
            if not row.strip():
                break
            if row.lstrip().startswith("#"):
                break
            m = _ROSTER_ROW_RE.match(row)
            if not m:
                # A non-matching line ends the roster. Anything else would let a stray bullet
                # elsewhere in the document silently extend it.
                break
            lenses.append({"lens": m.group(1).strip(),
                           "state": m.group(2).lower(),
                           "notes": (m.group(3) or "").strip()})
        if lenses:
            break

    rt = _RUNTIME_RE.search(text)

    rederived = 0
    for i, ln in enumerate(lines):
        if not _REDERIVE_HEAD_RE.match(ln):
            continue
        for row in lines[i + 1:]:
            if row.lstrip().startswith("#"):
                break
            if _LIST_ROW_RE.match(row):
                rederived += 1
        break

    return {"lenses": lenses,
            "runtime": rt.group(1).lower() if rt else None,
            "rederive_lines": rederived}


def judge(text: str, path: Path | str, verdict: str | None,
          today_cutoff: str = CUTOFF) -> tuple[bool, list[str]]:
    """(ok, reasons). `verdict` is what THE CALLER's own regex read — None means it found none.

    Scope, in order, because each gate below is meaningless without the one above it:
      1. no verdict the caller could read  -> out of scope entirely; this module says nothing
      2. lane date < CUTOFF                -> legacy; a note, never a block (130/142 have no roster)
      3. everything else                   -> in scope, and the rules below BLOCK
    """
    reasons: list[str] = []
    if not verdict:
        return True, reasons

    date = lane_date(path)
    if date is not None and date < today_cutoff:
        reasons.append(f"legacy lane ({date} < {today_cutoff}) - roster not required, not backfilled")
        return True, reasons

    v = verdict.upper()
    data = parse(text)
    lenses = data["lenses"]
    dead = [l["lens"] for l in lenses if l["state"] == "dead"]

    if v == "FAIL":
        # Blocks on its own account upstream; saying so here keeps the reason in one place.
        reasons.append("Verdict FAIL")
        return False, reasons

    if not lenses:
        # ⛔ UNKNOWN, NOT CLEAN. This is the whole defect: a PASS with no roster is not evidence
        # that the review ran, it is the absence of evidence either way.
        reasons.append(
            f"Verdict {v} with NO `lenses_run:` roster. A verdict is the review's conclusion; "
            f"the roster is what shows it happened. Record it in `## Code Review` as "
            f"`lenses_run:` followed by one `- <lens> · ok|recovered-inline|dead` row per lens.")
        return False, reasons

    if v == "PASS" and dead:
        # ⛔ THE CONTRADICTION. A lens that never produced a finding cannot support a PASS -
        # nobody looked through it. The engine's own contract (step-01-review.md:398) raises the
        # floor to CONCERNS when a lens is still dead after retry + inline rerun, so a PASS here
        # means the floor was not taken.
        reasons.append(
            f"Verdict PASS with {len(dead)} DEAD lens/lenses ({', '.join(dead)}). A dead lens "
            f"saw nothing, so it cannot support a PASS. The engine's floor for a still-dead "
            f"lens is CONCERNS - record that instead; CONCERNS + dead is consistent and passes.")
        return False, reasons

    if data["runtime"] == "inline" and any(l["state"] == "ok" for l in lenses):
        # I3 (F20). Under a declared `inline` runtime the ladder runs ONCE, so `recovered-inline`
        # is the only legal per-lens state. An `ok` here means either the header is wrong or a
        # fan-out was attempted against the declaration - either way the data disagrees with
        # itself, and that shows up here rather than in nobody's notes.
        oks = [l["lens"] for l in lenses if l["state"] == "ok"]
        reasons.append(
            f"header says `review-runtime: inline` but {len(oks)} lens/lenses report `ok` "
            f"({', '.join(oks)}). Under `inline` the ladder runs once and every lens is "
            f"`recovered-inline`; an `ok` means the header and the roster disagree.")
        return False, reasons

    if data["rederive_lines"] < 3:
        # E7. Step 0.7 is three lines: what moved, what it changes for this lane, what was
        # re-measured. "nothing moved" IS a line - the cheap answer is allowed, the silent one
        # is not.
        reasons.append(
            f"Step 0.7's re-derivation has {data['rederive_lines']} line(s), needs 3 "
            f"(what moved / what it changes here / what was re-measured). "
            f"\"nothing moved\" is a valid line; leaving it out is not.")
        return False, reasons

    reasons.append(f"Verdict {v} with {len(lenses)} lens/lenses recorded"
                   + (f", {len(dead)} dead (consistent with {v})" if dead else ""))
    return True, reasons
