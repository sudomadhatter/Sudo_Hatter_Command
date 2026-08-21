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
import sys
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

# SCC-231/233 record lines (this parser is their ONLY machine tier — measured base rate for
# prose-only obligations: 12 of 142 walkthroughs complied, this module's own docstring). The
# LAST occurrence governs, same rule as the roster: a re-review appends.
_DISPO_RE = re.compile(r"^[>\-*#\s]*\**\s*dispositions\s*:\**\s*(.+)$", re.I | re.M)
_DRIFT_RE = re.compile(r"^[>\-*#\s]*\**\s*drift\s*:\**\s*(.+)$", re.I | re.M)
# Lanes dated before the lines became law are exempt, same mechanism as CUTOFF.
DISPO_CUTOFF = "2026-08-20"

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

    Deliberately total: it never raises and never decides. `judge()` decides.

    ⛔ TWO OF THE RETURNED FIELDS ARE DIAGNOSTICS, NOT DATA ABOUT THE REVIEW (SCC-240).
    `roster_header_fenced` and `roster_header_empty` record HOW a roster went missing, so
    `judge` can say which of three things happened instead of reporting all three as "no
    roster". They are computed here, beside the parse that loses the information, because a
    caller re-deriving them would have to re-implement `strip_fenced` to do it - which is the
    two-callers-one-rule problem this module exists to end. They stay FLAGS: `parse` still
    never decides.
    """
    raw_lines = text.splitlines()
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

    dispo = _DISPO_RE.findall(text)
    drift = _DRIFT_RE.findall(text)

    # ⛔ THE TWO WAYS A ROSTER GOES MISSING WHILE BEING VISIBLY PRESENT (SCC-240).
    # They are mutually exclusive BY CONSTRUCTION, and the construction is the point: a header
    # that survives stripping is not a fenced one, so a document carrying both a fenced example
    # AND a real-but-empty header reports `empty` - which is the header its author must fix.
    # Fixing the example would leave the lane refused for the same reason twice.
    head_raw = any(_ROSTER_HEAD_RE.match(ln) for ln in raw_lines)
    head_kept = any(_ROSTER_HEAD_RE.match(ln) for ln in lines)

    return {"lenses": lenses,
            "lenses_na": na,
            "runtime": rt.group(1).lower() if rt else None,
            "rederive_lines": rederived,
            "dispositions": dispo[-1].strip() if dispo else None,
            "drift": drift[-1].strip() if drift else None,
            "roster_header_fenced": head_raw and not head_kept,
            "roster_header_empty": head_kept and not lenses}


def roster_defect(data: dict, verdict: str | None = None) -> str | None:
    """Why the roster cannot be READ, or None if it can. (SCC-240)

    ⭐ THREE CAUSES, THREE ANSWERS. Until now all three arrived as one message describing the
    roster's FORMAT - useless advice to an author whose roster is in the file and correctly
    formatted. On SCC-210 the fenced case and the blank-line case were hit in that order, each
    costing a full preflight round trip plus a read of this module to work out what it had
    actually seen.

    ⛔ ONE COPY, TWO CALLERS, and that is the point. `judge` asks this as part of a gate
    decision; the CLI asks it ALONE, because at review time the stamp, `dispositions:`,
    `drift:` and Step 0.7 do not exist yet and the only answerable question is "can this
    roster be read?". A second copy would drift exactly the way the two verdict readers this
    module was built to unify did.

    ⛔ Neither rule is relaxed to make the message nicer: `strip_fenced` stays (SCC-154 paid for
    it with a live miss) and contiguity stays (it is what stops a stray bullet elsewhere in the
    document silently extending the roster). Only the diagnosis changes.

    `verdict` is cosmetic here - it only leads the sentence, so the CLI can ask the same
    question with no stamp in hand and get the same three answers.
    """
    if data["lenses"]:
        return None
    lead = f"Verdict {verdict}" if verdict else "This walkthrough"
    if data["roster_header_empty"]:
        # ⛔ NAME THE ROW GRAMMAR, NOT ONLY THE BLANK LINE (SCC-240 review, Edge-Case + Blind
        # Hunter). Zero rows is produced by a blank line AND by a contiguous row the regex does
        # not match - a state word outside `ok|recovered-inline|dead`, a lens name starting
        # with punctuation. An imperative that says only "no blank line between" sends an author
        # whose rows ARE contiguous back to look for whitespace that was never there, which is
        # the same wasted round trip in a new coat.
        return (f"{lead}: a `lenses_run:` header is here but NO rows were collected under it. "
                f"The rows must be CONTIGUOUS with the header - a blank line, or any line that "
                f"is not a `- <lens> · <state>` row, ends the roster, because one that ran past "
                f"a blank would swallow every bullet later in the document. Check BOTH: no "
                f"blank line between the header and the first row, AND every row shaped "
                f"`- <lens> · ok|recovered-inline|dead` (the state word is one of those three, "
                f"exactly).")
    if data["roster_header_fenced"]:
        return (f"{lead}: your `lenses_run:` roster is INSIDE A CODE FENCE, and fences are "
                f"stripped before this is read (SCC-154 - a canonical verdict pasted as evidence "
                f"inside a fence once became the governing verdict). Paste the block WITHOUT the "
                f"``` fence: the header line, then one `- <lens> · ok|recovered-inline|dead` row "
                f"per lens, as plain lines in `## Code Review`. An UNCLOSED fence earlier in the "
                f"document does this too - everything after it is dropped.")
    # ⛔ UNKNOWN, NOT CLEAN, and this message is the one that must NOT change (SCC-173). It is
    # the original refusal, kept byte-identical when a verdict leads it: a PASS with no roster
    # is not evidence that the review ran, it is the absence of evidence either way.
    absent_lead = f"Verdict {verdict} with NO" if verdict else "NO"
    return (f"{absent_lead} `lenses_run:` roster. A verdict is the review's conclusion; "
            f"the roster is what shows it happened. Record it in `## Code Review` as "
            f"`lenses_run:` followed by one `- <lens> · ok|recovered-inline|dead` row per lens.")


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
        reasons.append(roster_defect(data, v) or "")
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

    if date is None or date >= DISPO_CUTOFF:
        # ⛔ SCC-231/233 (2026-08-20). Both lines exist so their data is READ by a machine, not
        # remembered by an agent: `dispositions:` is the per-lens death-count record (the SCC-233
        # enabler — after N runs the Blind Hunter question is answerable from data), `drift:` is
        # the declared-set reconciliation result (SCC-231 — a drift check that ran and was never
        # recorded is indistinguishable from one that never ran). Presence is what this tier
        # gates; the shape is the twins' law.
        if data["dispositions"] is None:
            reasons.append(
                "the `## Code Review` section has no `dispositions:` line. Paste the engine "
                "summary's line verbatim - `dispositions: per-lens: "
                "<lens>=<survived>/<dismissed>/<relevance-killed> · ...` - the per-lens death "
                "counts are the SCC-233 record and nothing else carries them.")
            return False, reasons
        if data["drift"] is None:
            reasons.append(
                "the `## Code Review` section has no `drift:` line. Record Step 2's declared-set "
                "reconciliation in one line - `drift: undeclared=<n> · unimplemented=<n> · "
                "incomplete=<n> - dispositions in the findings table` (or name why there was no "
                "block to reconcile).")
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


# ⛔ WHY THIS MODULE HAS A CLI AT ALL (SCC-240). It was library-only - no `main()`, no
# `if __name__` - and every caller reached it through a preflight. So the ONLY way to find out
# what it had seen in a walkthrough was to run a close-out and read the refusal, or to write a
# throwaway script against these internals. That is the defect under the other two: there was
# no way to check a block until the gate refused it, which is the most expensive moment to find
# out. Both review commands now run this at Step 4, right after pasting the roster.
#
# ⛔ IT IS A SELF-CHECK, NOT A SECOND GATE. `closeout_preflight` and `task_preflight` keep their
# own verdict readers (one lenient, one strict) and go on calling `judge` with the verdict THEY
# resolved - that is the SCC-173 contract and this must not become a third opinion. The reader
# below is deliberately the lenient one, and `--verdict` exists for the moment that matters
# most: checking a `## Code Review` section BEFORE its stamp is written.
_CLI_VERDICT_RE = re.compile(r"^[>\-*#\s]*\**\s*Verdict\s*:\**\s*\**"
                             r"(PASS|CONCERNS|FAIL|WAIVED)\b", re.I | re.M)


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser(
        prog="walkthrough_roster.py",
        description="Print what this parser reads out of a walkthrough. By DEFAULT it answers "
                    "one question - can the `lenses_run:` roster be READ? - which is the only "
                    "question answerable at review time, when the verdict stamp and the "
                    "record lines do not exist yet. Use --gate for the full close-out "
                    "judgement. (SCC-240)")
    ap.add_argument("walkthrough", help="path to the walkthrough .md")
    ap.add_argument("--gate", action="store_true",
                    help="run the FULL close-out judgement, not just the roster read: the "
                         "dead-lens contradiction, `lenses_na` legality, `dispositions:` and "
                         "`drift:` presence, and Step 0.7's three lines. Needs a verdict - "
                         "the last `Verdict:` line, or --verdict")
    ap.add_argument("--verdict", choices=("PASS", "CONCERNS", "FAIL", "WAIVED"),
                    help="judge against THIS verdict instead of the last `Verdict:` line - "
                         "use it with --gate to check a `## Code Review` section before its "
                         "stamp exists")
    a = ap.parse_args(argv)

    path = Path(a.walkthrough)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        # ⛔ EXIT 2, NOT 1, AND NAME THE REAL CAUSE (SCC-240 review, Edge-Case + Literal-
        # Correctness). A path that is missing, a DIRECTORY, or a file this decoder cannot read
        # is a broken invocation, not a statement about a roster - and exit 1 means REFUSED, so
        # letting an unreadable file take that code reports a plumbing failure as a roster
        # defect. The old text said "no such walkthrough" for a directory sitting right there,
        # and a latin-1 byte raised a traceback under exit 1 - real on a repo whose files are
        # authored on two machines.
        print(f"walkthrough_roster: cannot read {path}: "
              f"{type(exc).__name__} - {exc}", file=sys.stderr)
        return 2

    data = parse(text)
    # ⛔ STAMPS COME FROM THE STRIPPED TEXT, like everything else this module reads (SCC-240
    # review, Blind Hunter). Reading them RAW made one invocation disagree with itself: a
    # walkthrough quoting a canonical verdict inside a fence AS EVIDENCE - the literal SCC-154
    # scar - handed the CLI a verdict `parse` and `judge` could not see.
    stamps = _CLI_VERDICT_RE.findall(strip_fenced(text))
    # The LAST stamp governs - a re-review APPENDS, same rule the roster itself follows, and
    # the same rule `task_preflight` was corrected to at `found[-1]`.
    verdict = a.verdict or (stamps[-1].upper() if stamps else None)

    print(json.dumps({**data, "verdict": verdict, "lane_date": lane_date(path),
                      "lenses_counted": len(data["lenses"])}, indent=1, ensure_ascii=False))

    # ⭐ THE DEFAULT IS THE ROSTER READ, AND THAT IS WHAT MAKES THE STEP-4 INSTRUCTION TRUE
    # (SCC-240 review, Literal-Correctness + Blind Hunter + Test-Adequacy + Acceptance - four
    # lenses, one defect). The commands tell an author to run this the moment the roster is
    # pasted. At that moment `dispositions:`, `drift:`, Step 0.7 and the `Verdict:` line are
    # still unwritten, so the full gate answers a question nobody asked: it refused on a
    # missing `dispositions:` line and the doc told the author it must be a fence problem.
    # Worse, with no stamp `judge` returns (True, []) - so the check exited 0 on the fenced
    # roster it exists to catch. The roster read needs no stamp and no record lines, so it is
    # answerable exactly when it is asked.
    defect = roster_defect(data, verdict)
    if defect:
        print("REFUSED: " + defect, file=sys.stderr)
        return 1
    print(f"ok:  roster reads - {len(data['lenses'])} lens/lenses"
          + (f", {len(data['lenses_na'])} n/a" if data["lenses_na"] else ""), file=sys.stderr)

    if not a.gate:
        if verdict is None:
            print("note: no `Verdict:` line yet, which is NORMAL at Step 4. The roster above "
                  "is readable; the record lines and the stamp are checked by --gate, or at "
                  "close-out.", file=sys.stderr)
        return 0

    if verdict is None:
        print("--gate needs a verdict and this walkthrough has no `Verdict:` line - "
              "pass --verdict PASS|CONCERNS|FAIL|WAIVED to judge the section anyway.",
              file=sys.stderr)
        return 2
    ok, why = judge(text, path, verdict)
    for line in why:
        print(("ok:  " if ok else "REFUSED: ") + line, file=sys.stderr)
    # ⛔ SAME PARSER, DIFFERENT QUESTION - say so rather than imply agreement (SCC-240 review,
    # Literal-Correctness). This reads the LAST stamp; `closeout_preflight` reads the FIRST
    # (`_VERDICT_RE.search`), so on a re-reviewed STORY lane whose stamps run FAIL-then-PASS
    # the two resolve different verdicts from one file. Task lanes go through
    # `task_preflight`, which reads the last and agrees with this. Pass --verdict to pin it.
    if len(stamps) > 1:
        print(f"note: {len(stamps)} `Verdict:` stamps - judged the LAST ({verdict}). A story "
              f"lane's `closeout_preflight` reads the FIRST ({stamps[0].upper()}); pass "
              f"--verdict to remove the ambiguity.", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
