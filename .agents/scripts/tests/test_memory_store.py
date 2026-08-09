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

Deliberately NOT here: any auto-compaction. Deciding which memories merge or retire is
judgment work — `/update-maps-indexes` PROPOSES it and the operator approves. This gate
only makes rot loud.

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
EXEMPT = {"MEMORY.md", "README.md"}

REAL_STORE = SCRIPTS.parent.parent / "_artifacts" / "_memory"


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
            f"platform pays this; compress closed lessons to one line and move narrative "
            f"into the memory files (propose retirements via /update-maps-indexes)")
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


def write(store: Path, name: str, text: str) -> None:
    store.mkdir(parents=True, exist_ok=True)
    (store / name).write_text(text, encoding="utf-8")


MEMO = "---\nname: a-fact\ndescription: one fact\n---\n\nThe fact.\n"


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
                any(str(INDEX_CAP) in p and "compress" in p for p in got), str(got)[:150])

    with TempDir() as t:
        c.check("a store with no index at all is one loud problem",
                check_store(t / "mem") != [], "")

    # ── THE gate: the real store honors the contract it advertises ──
    c.check("real store exists where AGENTS.md routes every platform",
            (REAL_STORE / "MEMORY.md").is_file(), str(REAL_STORE))
    got = check_store(REAL_STORE)
    c.check("real store: index <= 20KB, links resolve, no orphans, frontmatter present",
            got == [], " | ".join(got[:4]))

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
