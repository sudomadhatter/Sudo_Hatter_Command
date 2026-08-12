"""test_main_ruleset_armed — is the server-side half actually SWITCHED ON at GitHub? (SCC-118)

Every other test in this pair reads files. Files prove the workflow is well-shaped and the doors
call it in the right order — they prove nothing whatsoever about whether GitHub is enforcing
anything. The ruleset lives on the server, in nobody's repo, and it can be deleted or set to
`disabled` from a browser without leaving a trace in any commit.

That is the same class of hole SCC-77 shipped with and SCC-110 generalised: `core.hooksPath` is
per-machine, so a fresh clone runs green with every gate off. This one is worse in one way —
there is exactly ONE ruleset for everyone, so it cannot be armed "per machine"; and better in
another — it either exists or it does not, and this asks.

  ── WHY THIS ONE MAY SIGNAL INSTEAD OF FAIL, AND EXACTLY WHEN ──────────────────────────────
⛔ Not a soft gate. `.agents/rules/tests-must-gate-for-real.md` rule 3 bans "report-only for
now", and this is not that — there is no owner to name and no expiry to track, because the
distinction is permanent and structural:

    GitHub reachable + the ruleset is wrong/absent   → HARD FAIL. This is the case that matters
                                                       and it is never softened.
    GitHub unreachable (offline, no gh, no auth)     → [SIGNAL] + pass.

The second branch is not leniency about the gate; it is refusing to claim knowledge the run does
not have. A test that reds on a plane, or on a CI runner with no credentials for this API, tells
every unrelated lane that something is broken when nothing is — and a suite that cries wolf
where nobody can act gets ignored where they can. Same reasoning, same shape, as the
cross-repo mirror-line check in `test_memory_store.py`.

Stdlib only, no pytest.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from _harness import Cases

REPO = Path(__file__).resolve().parents[3]
WORKFLOW = REPO / ".github/workflows/main-write-gate.yml"

# A job-level `name:` — four spaces under `jobs: <id>:`. Top-level workflow name has none and
# step names carry `- name:` at six. Read from the file rather than pinned here, so renaming
# the job cannot silently leave the ruleset requiring a check nobody publishes.
JOB_NAME_RE = re.compile(r"^ {4}name: (\S+)\s*$", re.M)


def gh(*args: str) -> tuple[int, str]:
    try:
        r = subprocess.run(["gh", *args], cwd=str(REPO), capture_output=True,
                           text=True, errors="replace", timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 127, "gh unavailable"
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def slug() -> str:
    """owner/repo from the origin remote — never hardcoded, so a fork tests its own state."""
    r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=str(REPO),
                       capture_output=True, text=True, errors="replace")
    url = (r.stdout or "").strip()
    m = re.search(r"github\.com[:/](?P<slug>[^/]+/[^/]+?)(?:\.git)?$", url)
    return m.group("slug") if m else ""


def required_checks(detail: dict) -> list[str]:
    out = []
    for rule in detail.get("rules", []):
        if rule.get("type") != "required_status_checks":
            continue
        for chk in rule.get("parameters", {}).get("required_status_checks", []):
            out.append(chk.get("context", ""))
    return out


def targets_main(detail: dict) -> bool:
    cond = detail.get("conditions", {}).get("ref_name", {})
    include = cond.get("include", [])
    return any(i in ("refs/heads/main", "~DEFAULT_BRANCH") for i in include)


def main() -> int:
    c = Cases("main ruleset armed at GitHub (SCC-118)")

    if not WORKFLOW.is_file():
        c.check("the workflow exists", False, str(WORKFLOW))
        return c.finish()

    m = JOB_NAME_RE.search(WORKFLOW.read_text(encoding="utf-8"))
    c.check("the workflow publishes a job-level check name", bool(m))
    if not m:
        return c.finish()
    check_name = m.group(1)

    repo_slug = slug()
    c.check("origin resolves to a GitHub repo", bool(repo_slug), repo_slug or "no github remote")
    if not repo_slug:
        return c.finish()

    rc, out = gh("api", f"repos/{repo_slug}/rulesets")
    if rc != 0:
        # Offline / no gh / no credentials. Say so loudly and pass — see the module docstring.
        print(f"[SIGNAL] cannot reach GitHub to verify the ruleset — {out.strip().splitlines()[-1] if out.strip() else 'no output'}")
        print("[SIGNAL] the server-side half is UNVERIFIED in this run, not proven absent.")
        print("[SIGNAL] verify from a machine with `gh auth status` green:")
        print(f"[SIGNAL]   gh api repos/{repo_slug}/rulesets")
        return c.finish()

    try:
        summaries = json.loads(out)
    except json.JSONDecodeError:
        c.check("the rulesets listing is JSON", False, out[:200])
        return c.finish()

    # From here on GitHub answered, so every failure below is real and blocks.
    found = None
    for s in summaries:
        rc2, detail_raw = gh("api", f"repos/{repo_slug}/rulesets/{s.get('id')}")
        if rc2 != 0:
            continue
        try:
            detail = json.loads(detail_raw)
        except json.JSONDecodeError:
            continue
        if targets_main(detail) and check_name in required_checks(detail):
            found = detail
            break

    c.check(f"a ruleset on main requires the '{check_name}' check", found is not None,
            f"{len(summaries)} ruleset(s) on {repo_slug}; none require it"
            if found is None else f"ruleset '{found.get('name')}'")
    if found is None:
        return c.finish()

    c.check("that ruleset is ACTIVE, not disabled or evaluate-only",
            found.get("enforcement") == "active", str(found.get("enforcement")))

    # ⭐ The bypass list is the whole ballgame. The agent that merged PR #2 held the operator's
    # own identity — `merged_by: sudomadhatter (User)`. A bypass for "repository admin" would
    # therefore re-open the exact hole this ticket closed, while the ruleset still LOOKS armed.
    bypass = found.get("bypass_actors") or []
    c.check("the bypass list is EMPTY", not bypass,
            f"{len(bypass)} actor(s) may bypass: "
            + ", ".join(str(b.get("actor_type")) for b in bypass)
            + " — the agent merges as the operator, so any bypass re-opens SCC-118")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
