"""SCC-439: the vendor token-size gate in bmad-quick-dev is RETIRED in this house.

BMAD ships a 900-1600 token spec-size guideline (SKILL.md § SCOPE STANDARD, spec-template.md's
header comment) and a Split/Keep halt driven by it (step-02-plan.md step 6). That is a vendor
default, not house law: the operator ruled it out on 2026-09-10, and the halt it produces is an
approval stop with no value (`approval-cost-is-a-threat`).

This guard asserts BOTH halves:
  - the durable half — `_bmad/custom/bmad-quick-dev.toml` carries the retirement fact. That file
    survives a BMAD update; the skill directory does not.
  - the current install — neither lobby copy of the skill still carries the guideline.

And it asserts what must NOT go with it: the single-goal scope test at step-01 step 4 is a
different halt on a real product question, and it stays.

SCOPE IS THE LOBBY ONLY. Every path below resolves under ROOT and none may reach `Projects/`,
whose copies belong to other repos on other boards (SCC-399: an assertion whose only fix is
deleting files out of a shipped product blocks every unrelated lane instead).

Two mechanics that are invisible at the call site and were both measured, not reasoned:

  1. EVERY read passes `encoding="utf-8"`, and every banned term is ASCII. The range separator in
     `900-1600` on disk is U+2013 EN DASH (e2 80 93). Decoded utf-8, `"900–1600" in text` is
     True; decoded cp1252 -- which is what `read_text()` with no `encoding=` does on the Windows
     side of this one PC -- it is False, while ASCII `"1600" in text` stays True. An en-dash
     assertion is a real check on WSL and a permanent no-op on the PC, and both machines print
     [PASS]. `_harness.py` pins the OUTPUT stream for this class of bug, never the input decode.

  2. `vendor-copies-stripped` counts the files it read and checks a string the edit KEEPS, before
     it asserts any absence. A negative assertion over an unresolved path is trivially true -- the
     suite would report the gate retired while it sat on disk fully armed.
"""
from __future__ import annotations

from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]

# The scan roots. LOBBY ONLY -- `scan-roots-are-lobby-only` pins this.
SKILL_DIRS = (
    ROOT / ".claude" / "skills" / "bmad-quick-dev",   # Claude's door
    ROOT / ".agent" / "skills" / "bmad-quick-dev",    # Antigravity's door
)
GATE_FILES = ("SKILL.md", "step-02-plan.md", "spec-template.md")
OVERRIDE = ROOT / "_bmad" / "custom" / "bmad-quick-dev.toml"

# ASCII only -- see the module docstring, mechanic 1.
BANNED = ("1600", "900", "Token count check", "token count")
# The positive control: text the edit deliberately KEEPS, proving the read returned real content.
KEEP = "single user-facing goal"

# A BMAD update reinstalls the vendor skill and re-arms the guideline, so this block goes red for
# someone standing in an unrelated lane. Name the cause AND the remedy in the failure itself.
BMAD_UPDATE_HINT = (
    "a BMAD update reinstalled the vendor skill -- re-apply the three edits per door "
    "(SKILL.md § SCOPE STANDARD, step-02-plan.md item 6 + CHECKPOINT 1, spec-template.md:9); "
    "_bmad/custom/bmad-quick-dev.toml is the durable half and is untouched by the update"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def main() -> int:
    c = Cases("bmad_token_gate_retired")

    # ── the durable half ─────────────────────────────────────────────────────
    if c.block("override-fact"):
        toml = _read(OVERRIDE)
        # positive control first: prove we read the real override, not an empty string
        c.check("override toml exists and is the real file",
                "persistent_facts" in toml and "COMMIT CONTRACT" in toml,
                f"did not read a populated override at {OVERRIDE}")
        c.check("override retires the token-size guideline",
                "TOKEN-SIZE GATE RETIRED" in toml,
                "no `TOKEN-SIZE GATE RETIRED` fact in _bmad/custom/bmad-quick-dev.toml")
        c.check("override forbids counting or showing a token count",
                "never count" in toml and "never show" in toml,
                "the retirement fact does not forbid counting/showing a token count")
        c.check("override names the single-goal test as the only scope judgement",
                "single-goal test" in toml,
                "the retirement fact does not name the single-goal test as the scope judgement")

    # ── the current install, both doors ──────────────────────────────────────
    if c.block("vendor-copies-stripped"):
        paths = [d / f for d in SKILL_DIRS for f in GATE_FILES]
        present = [p for p in paths if p.is_file()]
        # 1. the floor -- an unresolved root reds here instead of passing vacuously below
        c.check("all six vendor gate files resolve on disk",
                len(present) == len(paths),
                f"read {len(present)} of {len(paths)}: missing "
                f"{[str(p.relative_to(ROOT)) for p in paths if not p.is_file()]}")
        texts = {p: _read(p) for p in present}
        # 2. the positive control -- prove the reads returned real content
        skills = [p for p in present if p.name == "SKILL.md"]
        c.check("both SKILL.md still carry the single-goal text (read is real)",
                len(skills) == 2 and all(KEEP in texts[p] for p in skills),
                f"positive control absent from {[str(p) for p in skills if KEEP not in texts[p]]}")
        # 3. only now, the absence
        for term in BANNED:
            hits = sorted(str(p.relative_to(ROOT)) for p, t in texts.items() if term in t)
            c.check(f"no vendor copy carries {term!r}", not hits,
                    f"{term!r} still in {hits} -- {BMAD_UPDATE_HINT}")

    # ── what must NOT go with it ─────────────────────────────────────────────
    if c.block("single-goal-test-survives"):
        for d in SKILL_DIRS:
            rel = d.relative_to(ROOT)
            skill = _read(d / "SKILL.md")
            c.check(f"{rel}/SKILL.md keeps the single-goal scope standard",
                    KEEP in skill and "add dark mode toggle AND refactor auth to JWT" in skill,
                    "the single-goal paragraph or its examples went with the token range")
            route = _read(d / "step-01-clarify-and-route.md")
            c.check(f"{rel}/step-01 keeps the multi-goal halt",
                    "Multi-goal check" in route
                    and "[S] Split — pick first goal, defer the rest" in route,
                    "step-01's multi-goal halt was deleted -- that is the scope test we KEEP; "
                    "only step-02's token halt is retired")

    # ── the scope of this guard is the lobby, and only the lobby ─────────────
    if c.block("scan-roots-are-lobby-only"):
        scanned = [d / f for d in SKILL_DIRS for f in GATE_FILES] + [OVERRIDE]
        outside = [str(p) for p in scanned if ROOT not in p.parents and p.parent != ROOT
                   and not str(p).startswith(str(ROOT) + "/")]
        c.check("every scanned path is under the repo root", not outside, f"outside ROOT: {outside}")
        submodule = [str(p.relative_to(ROOT)) for p in scanned
                     if "Projects" in p.relative_to(ROOT).parts]
        c.check("no scanned path reaches a Projects/ submodule", not submodule,
                f"would scan another repo's copy: {submodule} -- those are AVCH/NVS work on their "
                "own boards (SCC-399)")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
