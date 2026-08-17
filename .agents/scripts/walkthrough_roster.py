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

# ⛔ THE DROPPED LENS — the one roster state with NO machine reader until now (SCC-203).
# `step-01-review.md` retired `ok (not blind — context held <what>)` and put a dropped Blind
# Hunter on `lenses_na:` instead, as `blind-hunter · n/a — context contaminated (<what>)`. That
# was the right record to write and nothing downstream could read it: `lenses_na:` is a separate
# field, so the row never reaches `_ROSTER_ROW_RE`, and a lens declared not-applicable was
# invisible to both preflights. The hole that opens is exact — under `review-runtime: fan-out` a
# clean subagent context exists BY CONSTRUCTION, so "my context is contaminated" cannot be true;
# a caller that writes it anyway skips the highest-value lens in the set and gates green. The
# whole SCC-203 ruling is that a roster may not claim more independence than the review had, and
# an unread `n/a` claims exactly that.
_NA_HEAD_RE = re.compile(r"^[>\-*#\s]*\**\s*lenses_na\s*:\**\s*(.*)$", re.I)
# ⛔ THE SEPARATOR NEEDS ITS SPACES. A lens name legitimately contains a hyphen (`blind-hunter`),
# and the reason separator may be written as one, so an unspaced `[—-]` lets the engine split the
# NAME: non-greedy group 1 settles on `blind`, and `hunter · n/a — ...` becomes the reason. That
# parses, reports a lens nobody has, and still looks reasoned. Requiring whitespace on BOTH sides
# makes the internal hyphen unmatchable and the real separator unambiguous.
_NA_ROW_RE = re.compile(r"^\s*(?:[-*]\s+)?`?([A-Za-z0-9][\w /-]*?)`?"
                        r"(?:\s*[·:|]\s*`?n/a`?)?"
                        r"(?:\s+[—–-]\s+(.*))?\s*$", re.I)
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


def strip_fenced(text: str) -> str:
    """Markdown code fences removed before anything here reads the document.

    ⛔ THIS LIVES IN THE PARSER, NOT IN THE CALLERS, AND THAT IS THE WHOLE POINT OF ONE PARSER.
    `task_preflight` already stripped fences before calling (SCC-154 paid for that rule with a
    live miss: a canonical stamp pasted AS EVIDENCE inside a fence became the governing verdict
    and permanently blocked a lane). `closeout_preflight` passed raw text — so a walkthrough whose
    only roster was a **fenced example** satisfied the story-lane gate while the Task-lane gate
    refused the identical file. Found by this lane's own inline review, and it was self-inflicted:
    the Step 4 instructions this lane wrote *teach* the roster inside a fence, so copying the
    example was enough to pass. A rule two callers must each remember is a rule one of them forgets.

    Fences close per CommonMark: the SAME marker kind, at least the opening length. A ```` or ~~~
    block whose content holds a ``` pair must not leak its inner lines back into the scan. An
    unclosed fence drops everything after it — no roster then, which BLOCKS, the safe direction.
    """
    out: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        m = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
            continue
        if fence is None:
            out.append(line)
    return "\n".join(out)


def parse(text: str) -> dict:
    """Everything this module reads out of a walkthrough, in one pass.

    Deliberately total: it never raises and never decides. `judge()` decides."""
    text = strip_fenced(text)
    lines = text.splitlines()
    lenses: list[dict] = []
    for i, ln in enumerate(lines):
        if not _ROSTER_HEAD_RE.match(ln):
            continue
        # ⛔ THE LAST ROSTER GOVERNS, NEVER THE FIRST — the same rule the verdict readers apply
        # (`verdicts[-1]` in check_gate), for the same reason: a RE-REVIEW APPENDS. A lane whose
        # first pass had a dead lens, and which then did exactly what the refusal asked — re-run
        # the review — ends up with two `## Code Review` sections. Reading the first one hands the
        # gate the superseded roster, so the remedy for a dead lens can never clear it, and the
        # lane is wedged by the evidence of its own fix. This lane shipped that defect once
        # already at `task_preflight`'s call site (`found[0]` where the rest of the function reads
        # `found[-1]`); this is the same bug one layer down, found by the same question.
        found: list[dict] = []
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
            found.append({"lens": m.group(1).strip(),
                          "state": m.group(2).lower(),
                          "notes": (m.group(3) or "").strip()})
        if found:
            lenses = found

    # `lenses_na:` in either shape the contract permits: inline on the header line
    # (`lenses_na: none`, `lenses_na: blind-hunter · n/a — ...`) or a block of rows beneath it.
    # "none" is the normal answer and means exactly zero dropped lenses.
    na: list[dict] = []
    for i, ln in enumerate(lines):
        m = _NA_HEAD_RE.match(ln)
        if not m:
            continue
        found_na: list[dict] = []
        inline_val = (m.group(1) or "").strip()
        rows = ([inline_val] if inline_val else []) + list(lines[i + 1:])
        for row in rows:
            if not row.strip() or row.lstrip().startswith("#"):
                break
            if row is not inline_val and not row.lstrip().startswith(("-", "*")):
                break
            if row.strip().lower().strip("`*") in ("none", "n/a", "-"):
                continue
            rm = _NA_ROW_RE.match(row)
            if not rm:
                break
            found_na.append({"lens": rm.group(1).strip(),
                             "reason": (rm.group(2) or "").strip()})
        if found_na:
            na = found_na
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
            "lenses_na": na,
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

    na = data["lenses_na"]
    if na and data["runtime"] == "fan-out":
        # ⛔ SCC-203. A lens may be DROPPED only when the order cannot protect it, and under a
        # declared fan-out it always can: a subagent starts with a clean context by construction,
        # so "my context is contaminated" is not a statement this runtime can make. Dropping the
        # Blind Hunter here removes the only lens whose value comes from starvation and reports
        # the result as a full review - the exact claim the ruling forbids.
        reasons.append(
            f"header says `review-runtime: fan-out` but {len(na)} lens/lenses are recorded "
            f"`n/a` ({', '.join(l['lens'] for l in na)}). A dropped lens is legal only under "
            f"`inline`, where the builder's own context is the reason; a fan-out gives every "
            f"lens a clean context, so run it or declare the runtime honestly.")
        return False, reasons

    unreasoned = [l["lens"] for l in na if len(l["reason"]) < 4]
    if unreasoned:
        # The reason IS the evidence. `blind-hunter · n/a` alone is indistinguishable from a lens
        # nobody bothered to run, which is what step-01 requires the `(<what it held>)` clause for.
        reasons.append(
            f"{len(unreasoned)} lens/lenses recorded `n/a` with no reason "
            f"({', '.join(unreasoned)}). Record why the order could not protect it - "
            f"`<lens> · n/a - context contaminated (<what it held>)`.")
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
