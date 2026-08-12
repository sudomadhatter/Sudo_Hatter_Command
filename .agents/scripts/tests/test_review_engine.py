"""The house review engine (SCC-116) — the contract its step files must hold.

`bmad-code-review` is a VENDOR skill: BMAD regenerates it, `customize.toml` only appends, and its
step-04 flips a story to `done` and writes the sprint board — two things this system's law reserves
for the human close-out, plus a third disagreement about where findings live. Containment today is
an adapter rule that has to win an attention contest against the vendor's own instructions on every
single run. `.agents/skills/code-review-engine/` ends that contest by owning the engine outright.

Why this file is the only guard: `workflow_lint.py` checks commands, rules, doors and INDEX rows —
it has NO skill checks at all. Nothing else on this surface is mechanical.

  ── THE NEGATIVE CONTROLS, AND WHY THEY ARE WRITTEN THIS WAY ────────────────────────────────
Five of these checks assert that a token is ABSENT. An absent-token check on a file that does not
exist passes for the wrong reason — the vacuous green that `e2e-gate-fiction` already cost this
system once. So every one of them proves the file EXISTS and is non-empty FIRST, and a missing
step file fails the negative control instead of satisfying it.

The corollary binds the authored files: a source-grep cannot tell prose from instruction, so the
step files must not NAME the banned tokens even to disown them. "The engine never advances a
story's board state" is the way to say it; quoting the vendor's field name is not.

Stdlib only, no pytest — same constraint as every sibling here.
"""
from __future__ import annotations

import re
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]
MASTER = ROOT / ".agents" / "skills" / "code-review-engine"
CACHE = ROOT / ".claude" / "skills" / "code-review-engine"

STEPS = ("step-01-review.md", "step-02-verify.md", "step-03-triage.md", "step-04-record.md")

# Tokens that must appear NOWHERE in the engine. Each is a distinctive marker of something the
# engine is forbidden to carry, not a general-purpose bad word.
BANNED = {
    # the vendor's status-flip machinery (its step-04 section 6)
    "new_status": r"new_status",
    "development_status": r"development_status",
    "sprint board file": r"sprint[-_]status",
    # BMAD-interactive plumbing: an engine invoked BY a command must not stop the caller's flow,
    # and must not reach for the vendor's customization resolver or its speech-style variable.
    "HALT marker": r"\bHALT\b",
    "customization resolver": r"resolve_customization",
    "speech-style variable": r"communication_language",
    # circularity: the engine replaces the vendor skill, it never calls it
    "vendor review skill": r"bmad-code-review",
}


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace")


def has_body(p: Path) -> bool:
    """Exists, is a file, and carries more than frontmatter-sized noise."""
    return p.is_file() and len(read(p).strip()) > 200


def main() -> int:
    c = Cases("review engine (SCC-122 scaffold)")

    # ── 1. Structure ──────────────────────────────────────────────────────────────────────
    skill = MASTER / "SKILL.md"
    c.check("SKILL.md exists with a body", has_body(skill), str(skill))
    for name in STEPS:
        c.check(f"{name} exists with a body", has_body(MASTER / "steps" / name))

    # ── 2. Caller contract ────────────────────────────────────────────────────────────────
    skill_txt = read(skill) if skill.is_file() else ""
    for var in ("REPO", "WORKTREE", "DIFF", "STORY_FILE", "HEAD_SHA", "review_mode"):
        c.check(f"SKILL.md names input {var}", bool(skill_txt) and var in skill_txt)
    c.check("SKILL.md names both review modes",
            "no-spec" in skill_txt and re.search(r"\bfull\b", skill_txt) is not None)
    c.check("SKILL.md states the engine does not resolve its own inputs",
            re.search(r"never resolves|does not resolve", skill_txt, re.I) is not None)

    # ── 3. step-01: the fan-out, the failure contract, NA-vs-died ─────────────────────────
    s1 = read(MASTER / "steps" / "step-01-review.md") if (MASTER / "steps" / "step-01-review.md").is_file() else ""
    for lens in ("Blind Hunter", "Edge Case Hunter", "Acceptance Auditor", "Test-Adequacy Auditor"):
        c.check(f"step-01 carries the {lens} lens", lens in s1)
    c.check("step-01 carries the retry-then-inline failure contract",
            bool(re.search(r"retry", s1, re.I)) and bool(re.search(r"inline", s1, re.I)))
    c.check("step-01 caps a lens that never ran at CONCERNS",
            "CONCERNS" in s1 and bool(re.search(r"never ran|did not run", s1, re.I)))
    c.check("step-01 records a mode-skipped lens as n/a (mode)", "n/a (mode)" in s1)
    c.check("step-01 says a mode skip does NOT cap the verdict",
            bool(re.search(r"does not cap|never caps", s1, re.I)))

    # ── 4. step-03: buckets, alias map, severity to verdict ───────────────────────────────
    s3 = read(MASTER / "steps" / "step-03-triage.md") if (MASTER / "steps" / "step-03-triage.md").is_file() else ""
    for bucket in ("decision_needed", "patch", "defer", "dismiss"):
        c.check(f"step-03 carries the {bucket} bucket", bucket in s3)
    for alias in ("blocker", "major", "minor", "trivial"):
        c.check(f"step-03 normalizes the alias {alias}", alias in s3.lower())
    for sev in ("critical", "important", "suggestion", "nitpick"):
        c.check(f"step-03 defines severity {sev}", sev in s3.lower())
    c.check("step-03 maps critical to FAIL and important to a CONCERNS floor",
            "FAIL" in s3 and "CONCERNS" in s3)
    c.check("step-03 says suggestion/nitpick never gate",
            bool(re.search(r"never gate", s3, re.I)))
    c.check("step-03 gives a verifier-revised severity precedence",
            bool(re.search(r"revised", s3, re.I)))

    # ── 5. step-02 self-gates, step-04 records only ───────────────────────────────────────
    s2 = read(MASTER / "steps" / "step-02-verify.md") if (MASTER / "steps" / "step-02-verify.md").is_file() else ""
    c.check("step-02 self-gates on zero findings", bool(re.search(r"\b(0|zero)\b.*finding", s2, re.I)))
    c.check("step-02 declares its scaffold-stage pass-through honestly",
            bool(re.search(r"SCC-127", s2)))

    s4p = MASTER / "steps" / "step-04-record.md"
    s4 = read(s4p) if s4p.is_file() else ""
    c.check("step-04 routes deferred findings to deferred-work", "deferred-work" in s4)
    c.check("step-04 writes findings where the caller asked",
            bool(re.search(r"finding", s4, re.I)))

    # Negative controls — existence proven first, so a missing file FAILS instead of passing.
    for target in ("SKILL.md",) + tuple(f"steps/{n}" for n in STEPS):
        p = MASTER / target
        body_ok = has_body(p)
        txt = read(p) if p.is_file() else ""
        for label, pattern in BANNED.items():
            hit = re.search(pattern, txt, re.I) if body_ok else None
            c.check(f"{target} carries no {label}",
                    body_ok and hit is None,
                    "file missing or empty" if not body_ok else (f"found {hit.group(0)!r}" if hit else ""))

    # ── 6. Registered, and the Claude cache agrees byte for byte ──────────────────────────
    idx_master = ROOT / ".agents" / "skills" / "INDEX.md"
    idx_cache = ROOT / ".claude" / "skills" / "INDEX.md"
    c.check("skills INDEX routes to the engine",
            idx_master.is_file() and "code-review-engine" in read(idx_master))
    c.check("skills INDEX master and cache are identical",
            idx_master.is_file() and idx_cache.is_file()
            and idx_master.read_bytes() == idx_cache.read_bytes())

    def tree(root: Path) -> dict[str, bytes]:
        if not root.is_dir():
            return {}
        return {str(p.relative_to(root)).replace("\\", "/"): p.read_bytes()
                for p in sorted(root.rglob("*")) if p.is_file()}

    m, k = tree(MASTER), tree(CACHE)
    c.check("engine is published to the Claude cache", bool(k), str(CACHE))
    c.check("cache holds the same file set as master",
            bool(m) and set(m) == set(k),
            f"master-only={sorted(set(m) - set(k))} cache-only={sorted(set(k) - set(m))}"
            if set(m) != set(k) else "")
    drifted = sorted(f for f in set(m) & set(k) if m[f] != k[f])
    c.check("cache is byte-identical to master", bool(m) and m == k,
            "differs: " + ", ".join(drifted) if drifted else "")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
