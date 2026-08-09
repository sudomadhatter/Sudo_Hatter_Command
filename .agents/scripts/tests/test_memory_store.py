"""The memory store is read by every platform now (SCC-65) — so its index is a context cost
paid by every session, and its integrity is what recall is worth.

AGENTS.md §7 routes EVERY model on EVERY machine through `_artifacts/_memory/MEMORY.md` at
session start. That contract holds only while three things stay true, and each one rots
silently without a gate:

  * the index stays under 20 KB — the same budget as active-context, because it is loaded
    whole into every session; growth past it means narrative crept into what must stay a
    one-line-per-memory index (content belongs in the memory FILES);
  * every index line points at a file that exists — a dead link is recall of nothing;
  * every memory file has an index line — an unindexed memory is invisible to the exact
    mechanism that makes memory worth writing (`README.md` exempt by name: it documents
    the store, it is not a memory).

⚠ THE TRIGGER (SCC-68). Upkeep used to hang off `/update-maps-indexes` Step 3.9, and so it
never ran: nobody reaches for a MAP workflow because memory feels heavy, and the store filled
to 99.5% of cap with the remedy parked in an unrelated command. Now the gate that already runs
in `run_all` on every close-out, on every machine, raises the alarm itself — at TRIGGER_PCT,
BELOW the cap, while the run still passes. A trigger that only fires at 100% is useless: its
first signal would already be a red blocking unrelated work.

This script cannot ask anything — it runs headless, inside hooks, inside `run_all`; it has
stdout and an exit code. So the ask is a two-part contract: the block below is the imperative,
and root `AGENTS.md` §7 binds every platform to STOP and ask the operator when it appears.
The candidate worklist is computed here so the audit starts from evidence rather than a blank
page — but they are SIGNALS, never verdicts.

Deliberately NOT here: any auto-compaction. Deciding which memories merge or retire is
judgment work — `/memory-audit` proposes it per item and the operator approves. A cheap model
summarizing away a hard-won pitfall is silent, permanent loss of exactly the recall the store
exists for. This gate makes rot loud; it never edits a memory.

Checks run against fixtures both ways (fire on defects, stay quiet on look-alikes), then
against the REAL store — the real store passing is the gate; the fixtures prove the
detector is alive.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases, TempDir

INDEX_CAP = 20 * 1024
TRIGGER_PCT = 0.90          # audit is DUE here — below the cap, on purpose (see module docstring)
BODY_SOFT_CAP = 4 * 1024    # a memory this long is usually narrative that wants compressing
EXEMPT = {"MEMORY.md", "README.md"}
CLOSED_MARKS = ("CLOSED", "RETIRED", "FIXED", "SUPERSEDED", "⛔")

REAL_STORE = SCRIPTS.parent.parent / "_artifacts" / "_memory"


def index_text(store: Path) -> str:
    idx = store / "MEMORY.md"
    return idx.read_text(encoding="utf-8") if idx.is_file() else ""


def check_store(store: Path) -> list[str]:
    """Every problem as one human sentence; empty list = the contract holds."""
    problems: list[str] = []
    idx = store / "MEMORY.md"
    if not idx.is_file():
        return [f"no MEMORY.md index in {store} - the store is unreadable by contract"]
    text = idx.read_text(encoding="utf-8")
    size = len(text.encode("utf-8"))
    if size > INDEX_CAP:
        problems.append(
            f"MEMORY.md is {size} bytes (cap {INDEX_CAP}) - every session on every "
            f"platform pays this; run /memory-audit to retire and compress (the 90% "
            f"trigger fired before this and was not acted on)")
    links = {m.split("/")[-1] for m in re.findall(r"\]\(([^)#]+\.md)\)", text)}
    files = {p.name for p in store.glob("*.md")} - EXEMPT
    for dead in sorted(links - files):
        problems.append(f"MEMORY.md links `{dead}` but no such file is in the store - "
                        f"recall of nothing; fix or delete the line")
    for orphan in sorted(files - links):
        problems.append(f"`{orphan}` has no MEMORY.md line - an unindexed memory is "
                        f"invisible to every session; add a one-line pointer")
    for p in sorted(store.glob("*.md")):
        if p.name in EXEMPT:
            continue
        head = p.read_text(encoding="utf-8", errors="replace")[:800]
        if not head.startswith("---") or "description:" not in head:
            problems.append(f"`{p.name}`: no frontmatter description - recall relevance "
                            f"is judged from it; add the ---/description header")
    return problems


def audit_due(store: Path) -> bool:
    """True once the index crosses TRIGGER_PCT of the cap. Separate from check_store because
    this is NOT a failure - the run still passes; it is a standing request for judgment work."""
    return len(index_text(store).encode("utf-8")) >= INDEX_CAP * TRIGGER_PCT


def audit_signals(store: Path) -> list[str]:
    """A worklist for /memory-audit, derived mechanically so the audit opens on evidence.

    SIGNALS, NOT VERDICTS. Every one of these can be legitimate - a `CLOSED` row whose lesson
    is still load-bearing stays; a dangling `[[link]]` is the sanctioned way to mark a memory
    worth writing later. The audit ground-truths each against the live repo. Nothing here is
    an instruction to delete."""
    out: list[str] = []
    text = index_text(store)

    closed = [ln.strip() for ln in text.splitlines()
              if ln.lstrip().startswith("-") and any(m in ln for m in CLOSED_MARKS)]
    if closed:
        out.append(f"{len(closed)} index row(s) marked {'/'.join(CLOSED_MARKS[:3])} - closed "
                   f"work whose lesson may compress to one line (or retire outright)")

    names = {p.stem for p in store.glob("*.md")} - {Path(e).stem for e in EXEMPT}
    dangling: set[str] = set()
    big: list[str] = []
    for p in sorted(store.glob("*.md")):
        if p.name in EXEMPT:
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        dangling |= {w for w in re.findall(r"\[\[([^\]]+)\]\]", body) if w not in names}
        if len(body.encode("utf-8")) > BODY_SOFT_CAP:
            big.append(p.name)
    if dangling:
        out.append(f"{len(dangling)} dangling [[link]] target(s) ({', '.join(sorted(dangling)[:4])}"
                   f"{'...' if len(dangling) > 4 else ''}) - either a forward reference (fine, "
                   f"leave it) or danglers left behind by a retirement (fix the source)")
    if big:
        out.append(f"{len(big)} memory file(s) over {BODY_SOFT_CAP // 1024} KB "
                   f"({', '.join(big[:3])}{'...' if len(big) > 3 else ''}) - long bodies are "
                   f"usually narrative; the lesson is what earns the space")
    return out


def audit_block(store: Path) -> str:
    """The imperative the agent must surface. Loud on purpose - this is the whole trigger."""
    size = len(index_text(store).encode("utf-8"))
    pct = size * 100 / INDEX_CAP
    lines = [
        "",
        "!! ---------------------------------------------------------------- !!",
        "!!  MEMORY AUDIT DUE                                                 !!",
        "!! ---------------------------------------------------------------- !!",
        f"   MEMORY.md is {size} bytes - {pct:.0f}% of the {INDEX_CAP}-byte cap "
        f"({INDEX_CAP - size} bytes of headroom left).",
        "   Every session on every platform loads this index before doing any work.",
        "",
        "   ACTION REQUIRED OF THE AGENT READING THIS: stop and ask the operator",
        "   whether to run /memory-audit now. Do not compact anything yourself, and",
        "   do not raise the cap - compaction is judgment work and it is the",
        "   operator's call, per AGENTS.md section 7.",
    ]
    sig = audit_signals(store)
    if sig:
        lines.append("")
        lines.append("   Candidates the audit will ground-truth against the live repo:")
        lines += [f"     - {s}" for s in sig]
    lines += ["!! ---------------------------------------------------------------- !!", ""]
    return "\n".join(lines)


def write(store: Path, name: str, text: str) -> None:
    store.mkdir(parents=True, exist_ok=True)
    (store / name).write_text(text, encoding="utf-8")


MEMO = "---\nname: a-fact\ndescription: one fact\n---\n\nThe fact.\n"


def sized_index(pct: float) -> str:
    """An index padded to `pct` of the cap - the pad is a comment line so it stays a valid index."""
    head = "# Index\n- [A fact](a-fact.md) - hook\n"
    return head + "<!-- " + "x" * int(INDEX_CAP * pct - len(head) - 8) + " -->\n"


def main() -> int:
    c = Cases("memory store")

    # ── fixture positive control: a correct tiny store is CLEAN ──
    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", "# Index\n- [A fact](a-fact.md) - hook\n")
        write(s, "README.md", "just a readme, no frontmatter\n")
        got = check_store(s)
        c.check("clean fixture store passes (README exempt by name)", got == [], str(got)[:150])
        c.check("a small index does NOT trigger the audit", not audit_due(s), "")

    # ── each defect fires, separately ──
    with TempDir() as t:
        s = t / "mem"
        write(s, "MEMORY.md", "- [gone](never-written.md) - hook\n")
        got = check_store(s)
        c.check("a dead index link fires", any("never-written.md" in p for p in got),
                str(got)[:150])

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", "# Index\n(no links yet)\n")
        got = check_store(s)
        c.check("an unindexed memory file fires", any("a-fact.md" in p and "no MEMORY.md line"
                in p for p in got), str(got)[:150])

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", "no frontmatter at all\n")
        write(s, "MEMORY.md", "- [A fact](a-fact.md) - hook\n")
        got = check_store(s)
        c.check("a memory without a description fires",
                any("frontmatter" in p for p in got), str(got)[:150])

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", "- [A fact](a-fact.md) - hook\n" + "x" * INDEX_CAP)
        got = check_store(s)
        c.check("an over-budget index fires with the cap named",
                any(str(INDEX_CAP) in p and "/memory-audit" in p for p in got), str(got)[:150])

    with TempDir() as t:
        c.check("a store with no index at all is one loud problem",
                check_store(t / "mem") != [], "")

    # ── the TRIGGER band (SCC-68): fires BELOW the cap, and the run still passes ──
    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", sized_index(0.91))
        c.check("an index at 91% of cap triggers the audit", audit_due(s), "")
        c.check("...and 91% is NOT a failure - the run still passes", check_store(s) == [],
                str(check_store(s))[:150])
        c.check("...and the block names the command + the ask",
                "/memory-audit" in audit_block(s) and "ask the operator" in audit_block(s), "")

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", sized_index(0.89))
        c.check("an index at 89% stays silent (a trigger that cries wolf gets ignored)",
                not audit_due(s), f"{len(index_text(s).encode('utf-8'))} bytes")

    # ── the signal worklist: derived, and honest about being signals ──
    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO.replace("The fact.", "See [[never-written-yet]]."))
        write(s, "MEMORY.md", "# Index\n- [A fact](a-fact.md) - ⛔ RETIRED 08-07\n")
        sig = audit_signals(s)
        c.check("a CLOSED/RETIRED index row surfaces as a candidate",
                any("index row" in x for x in sig), str(sig)[:150])
        c.check("a dangling [[link]] surfaces, described as possibly legitimate",
                any("dangling" in x and "forward reference" in x for x in sig), str(sig)[:150])

    with TempDir() as t:
        s = t / "mem"
        write(s, "a-fact.md", MEMO)
        write(s, "MEMORY.md", "# Index\n- [A fact](a-fact.md) - hook\n")
        c.check("a healthy store produces NO candidates", audit_signals(s) == [],
                str(audit_signals(s))[:150])

    # ── THE gate: the real store honors the contract it advertises ──
    c.check("real store exists where AGENTS.md routes every platform",
            (REAL_STORE / "MEMORY.md").is_file(), str(REAL_STORE))
    got = check_store(REAL_STORE)
    c.check("real store: index <= 20KB, links resolve, no orphans, frontmatter present",
            got == [], " | ".join(got[:4]))

    rc = c.finish()
    # AFTER the tally, so it is the last thing on screen and survives a `| tail`.
    if audit_due(REAL_STORE):
        print(audit_block(REAL_STORE))
    return rc


if __name__ == "__main__":
    sys.exit(main())
