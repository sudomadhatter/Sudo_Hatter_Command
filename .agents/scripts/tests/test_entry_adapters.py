"""An entry adapter is a REDIRECT, and nothing else — checked, not asserted in prose.

Three documents already say this: the folder-as-workspace plan's R8 ("nothing model-specific in
shared files"), `docs/workspace-standard.md` Part 1 Layer 1 ("one-line adapters, identical
everywhere ... Nothing model-specific beyond the name"), and root `AGENTS.md` §8 ("`CLAUDE.md` /
`GEMINI.md` are one-line adapters pointing here"). Nothing read any of them.

⚠ WHAT THAT COST (SCC-279, found 2026-08-22 by SCC-269's audit). Root `GEMINI.md` carried three
"GEMINI SPECIFIC HARD RULES" for an unknown length of time, and the two failure modes it produced
are the reason this file exists rather than a fourth paragraph of prose:

  * LAW THAT BINDS EVERYONE, WRITTEN WHERE ONE MODEL READS IT. None of the three was Gemini-specific
    in substance — explicit staging is `git-policy.md`, worktree-before-edit is
    `worktree-per-story.md`. A Claude or Codex session never opened the file. The worst available
    shape: shared law hidden behind a model's name.
  * A SHARED FILE ROTS UNWATCHED. Rule 1 told Gemini to run `sync-agents.ps1 -Maintained`, a flag
    RETIRED 2026-08-07 that now exits 1 with an explanatory error, and named a "top maintained
    project" de-listed the same day. An adapter is the one file nobody re-reads, so a dead
    instruction can sit in the entry point of the workspace and still be the first thing one
    platform loads every session.

⛔ THE HOLE THIS CLOSES, precisely. `check_maps.py` already looks at adapters — and it asks whether
the redirect is PRESENT (`ADAPTER_PHRASE in text`, check 8). The broken file contained the redirect.
It passed. "Contains the redirect" and "is the redirect" are different claims, and only the second
one is what the three documents actually promise. This asserts the second, against the REAL tree, in
the armed suite — `check_maps`' own version is a non-fatal hint over Tier-2 dirs only, and never
looked at a root adapter's body at all.

Fixtures fire both ways first (the detector must be alive before its silence means anything), then
the live tree is read. `ADAPTER_PHRASE` is imported from `check_maps`, never re-typed: two spellings
of one house sentence is how the check and the file drift apart.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from _harness import SCRIPTS, Cases   # noqa: F401  (Cases prints the tree guard)

import check_maps  # noqa: E402  (must follow the _harness path insert)

REPO_ROOT = SCRIPTS.parents[1]
ADAPTER_NAMES = ("CLAUDE.md", "GEMINI.md")

# Named exemptions, each with the reason it is not the house adapter. An exemption list is only
# honest while every entry says WHY — an unexplained skip is how the next block of hard rules
# gets parked somewhere this test does not look.
EXEMPT = {
    # The routing canary is a deliberate probe, not a workspace: its adapters point at `agent.md`
    # (the canary's own script) rather than an `AGENTS.md`, by design. Holding it to the house
    # sentence would force the canary to stop testing what it exists to test.
    "_routing-canary": "routing canary — adapters point at `agent.md` by design",
}


def tracked_adapters(root: Path) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Every TRACKED entry adapter, split into (checked, exempt-with-reason).

    Tracked, not globbed: a worktree carries untracked scratch copies of anything, and a gate
    that reads whatever is on disk reports a different result per lane.
    """
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root,
                         capture_output=True, text=True, check=False)
    checked: list[Path] = []
    exempt: list[tuple[Path, str]] = []
    for rel in out.stdout.split("\0"):
        if not rel or Path(rel).name not in ADAPTER_NAMES:
            continue
        p = Path(rel)
        reason = next((r for d, r in EXEMPT.items() if d in p.parts), None)
        (exempt.append((p, reason)) if reason else checked.append(p))
    return sorted(checked), sorted(exempt)


# A floor-rule IMPORT is a pointer, not law: `@.agents/rules/<name>.md` inlines a SHARED rule at
# session start (Claude Code and Gemini both resolve the syntax). It is allowed on the ROOT
# adapters only (SCC-346 Part F): a nested adapter also importing the floor would double-load it,
# and an import of anything OUTSIDE .agents/rules/ is exactly the model-specific-law smell this
# test exists to catch.
FLOOR_IMPORT = re.compile(r"^@\.agents/rules/[A-Za-z0-9_\-]+\.md$")


def adapter_violations(text: str, allow_floor_imports: bool = False) -> list[str]:
    """Every line that makes this file MORE than a redirect, quoted so the failure names itself.

    Allowed, and nothing else: one `#` title, the redirect sentence, and the house parenthetical
    footnote — plus, on a ROOT adapter only, `@.agents/rules/<name>.md` floor imports. Blank lines
    are free. Anything else — a heading, a numbered rule, a mandate — is the defect, because
    whatever it says binds only the platform whose name is on the file.
    """
    problems: list[str] = []
    saw_title = False
    saw_redirect = False
    for i, raw in enumerate(text.splitlines(), 1):
        ln = raw.strip()
        if not ln:
            continue
        if not saw_title and ln.startswith("# "):
            saw_title = True
            continue
        if check_maps.ADAPTER_PHRASE in ln:
            saw_redirect = True
            continue
        if ln.startswith("(") and ln.endswith(")"):
            continue
        if allow_floor_imports and FLOOR_IMPORT.match(ln):
            continue
        problems.append(f"L{i}: {ln[:72]}")
    if not saw_redirect:
        problems.insert(0, f"no redirect line — expected `{check_maps.ADAPTER_PHRASE} ...`")
    return problems


HOUSE = ("# Entry — Sudo_Hatter_Command (Gemini / Antigravity)\n\n"
         "Read `AGENTS.md` in this same folder and follow it. That is the single source of truth.\n\n"
         "(Every `CLAUDE.md` / `GEMINI.md` in this system says exactly this — one front door per "
         "LLM, one brain in `AGENTS.md`.)\n")


def main() -> int:
    c = Cases("entry adapters are redirects and nothing else (SCC-279)")

    if c.block("A · the detector fires on the shapes that broke"):
        c.check("the house adapter is clean", adapter_violations(HOUSE) == [],
                " | ".join(adapter_violations(HOUSE)))
        c.check("title + redirect alone is clean (the footnote is optional)",
                adapter_violations("# Entry — x\n\nRead `AGENTS.md` in this same folder and "
                                   "follow it. That is the single source of truth.\n") == [])
        # The exact file this ticket fixed: the redirect IS present, which is why check_maps
        # passed it. Every added rule must be named, not just the section heading.
        broke = HOUSE + ("\n## GEMINI SPECIFIC HARD RULES:\n"
                         "1. **SYNC MAINTAINED PROJECTS ONLY**: never across all `Projects/*`.\n"
                         "2. **WORKTREE ENFORCEMENT BEFORE CODE EDITS**: create a worktree first.\n"
                         "3. **EXPLICIT GIT COMMITS ONLY**: never `git add -A`.\n")
        got = adapter_violations(broke)
        c.check("model-specific hard rules are caught even though the redirect is present",
                len(got) == 4, f"{len(got)} flagged: {' | '.join(got)}")
        c.check("a file with the footnote but NO redirect is caught",
                any("no redirect line" in p for p in adapter_violations(
                    "# Entry — x\n\n(Every `CLAUDE.md` / `GEMINI.md` says this.)\n")))
        # NEGATIVE CONTROL: the canary shape. Flagged here on purpose — that is precisely why it
        # is on EXEMPT by name and not silently passing a check it would fail.
        c.check("the canary's `agent.md` redirect does NOT pass as the house adapter",
                adapter_violations("# _routing-canary — entry\n\nRead `agent.md` in this same "
                                   "folder and follow it exactly.\n") != [])
        # SCC-346 Part F: floor imports — allowed at the root, flagged everywhere else, and never
        # a licence to import something that is not a shared rule.
        with_import = HOUSE + "\n@.agents/rules/constitution.md\n"
        c.check("a floor import passes on a ROOT adapter (allow_floor_imports=True)",
                adapter_violations(with_import, allow_floor_imports=True) == [])
        c.check("the same import is flagged on a NESTED adapter (default strictness)",
                adapter_violations(with_import) != [])
        c.check("an import OUTSIDE .agents/rules/ is flagged even with the allowance",
                adapter_violations(HOUSE + "\n@docs/some-model-notes.md\n",
                                   allow_floor_imports=True) != [])

    if c.block("B · the real tree"):
        checked, exempt = tracked_adapters(REPO_ROOT)
        c.check("the tree actually has adapters to check (a silent empty sweep is not a pass)",
                len(checked) >= 4, f"{len(checked)} tracked adapters")
        bad: list[str] = []
        for rel in checked:
            is_root = len(rel.parts) == 1        # only the ROOT adapters may import the floor
            v = adapter_violations((REPO_ROOT / rel).read_text(encoding="utf-8", errors="replace"),
                                   allow_floor_imports=is_root)
            if v:
                bad.append(f"{rel}: {'; '.join(v)}")
        c.check("every tracked CLAUDE.md / GEMINI.md is the redirect and nothing more "
                "(workspace-standard Part 1 Layer 1 · AGENTS.md §8)",
                bad == [], " || ".join(bad))

        rc = c.finish()
        # Coverage stated, never implied — the same contract test_memory_store.py holds itself to.
        print(f"[COVERAGE] adapters read this run: {len(checked)} "
              f"({', '.join(str(p) for p in checked)})")
        for p, reason in exempt:
            print(f"[SKIP] {p} — {reason}")
        return rc

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
