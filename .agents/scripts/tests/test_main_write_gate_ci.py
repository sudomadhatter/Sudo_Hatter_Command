"""test_main_write_gate_ci — the SERVER-SIDE half of the main write gate (SCC-118).

The local half already has `test_main_push_gate.py`. This covers what that one structurally
cannot see: a merge performed on GitHub's servers, where no hook exists to run.

Three tiers, and the third is the one that makes the first two mean anything:

  WORKFLOW    the CI job is shaped the way the gate needs — real suite entrypoint, hooks armed
              BEFORE it, no soft steps.
  VALIDATOR   `main_write_gate.py` accepts what it must accept and refuses what it must refuse,
              driven as a pure function and then through a real git repo with a real merge.
  MUTATION    every workflow assertion is re-run against a DELIBERATELY BROKEN workflow and must
              fail. Without this tier the checks could all be vacuous and read identically.

⛔ Two traps this file is built around, both learned the hard way:

  1. `main-write-gate.yml` is heavily commented, and those comments NAME the literals under test
     ("no continue-on-error", "run_all.py", "--toolkit-only"). A plain substring search matches
     the COMMENT and reports the property satisfied when the actual step is missing — the guard
     inverts. Everything here runs against comment-stripped text, and `MUT_COMMENT_ONLY` below
     is the negative control proving the stripping works.

  2. A "contains" check cannot see ORDER. The arm step is worthless after the suite step, and a
     substring search passes identically either way. Order is asserted as an index comparison,
     with a reversed-order mutant to prove the comparison bites.

Stdlib only, no pytest, no PyYAML — same constraint as the rest of this directory, which is why
the workflow is read as text rather than parsed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from _harness import Cases, TempDir

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main_write_gate as mwg  # noqa: E402 — _harness puts .agents/scripts on sys.path

REPO = Path(__file__).resolve().parents[3]
WORKFLOW = REPO / ".github/workflows/main-write-gate.yml"
SCRIPT = REPO / ".agents/scripts/main_write_gate.py"

# The job's `name:` is the required-status-check context in the GitHub ruleset. If these two
# ever drift, `main` waits forever for a check nobody publishes — or requires nothing at all.
CHECK_NAME = "main-write-gate"


# ── reading the workflow ───────────────────────────────────────────────────────────────────
def effective_lines(text: str) -> list[str]:
    """The workflow with comments removed — see trap 1 in the module docstring.

    Whole-line comments go entirely; trailing comments are cut at ` #`. Values in this workflow
    contain no `#`, which is a constraint on the workflow, not an assumption about YAML at
    large — MUT_COMMENT_ONLY is the control that keeps this honest.
    """
    out = []
    for raw in text.splitlines():
        if raw.lstrip().startswith("#"):
            continue
        line = raw.split(" #", 1)[0].rstrip()
        if line.strip():
            out.append(line)
    return out


def idx(lines: list[str], needle: str) -> int:
    """First line index containing `needle`, or -1. Operates on effective lines only."""
    for i, line in enumerate(lines):
        if needle in line:
            return i
    return -1


def has(lines: list[str], needle: str) -> bool:
    return idx(lines, needle) >= 0


# Every workflow property, as a named predicate over effective lines. Written once so the live
# workflow and the mutants below are judged by exactly the same code — a mutation battery that
# re-implements its assertions proves nothing about the real ones.
CHECKS: dict[str, object] = {
    "triggers on PRs into main":
        lambda L: has(L, "pull_request:") and has(L, "branches: [main]"),
    "triggers on the gate/** pre-flight ref":
        lambda L: has(L, "push:") and has(L, "gate/**"),
    "publishes the check name the ruleset requires":
        lambda L: has(L, f"name: {CHECK_NAME}"),
    "checks out full history (fetch-depth: 0)":
        lambda L: has(L, "fetch-depth: 0"),
    "runs the REAL suite entrypoint":
        lambda L: has(L, "python3 .agents/scripts/tests/run_all.py"),
    "lints the toolkit with --toolkit-only":
        lambda L: has(L, "workflow_lint.py --toolkit-only"),
    "runs the source/merge-shape validator":
        lambda L: has(L, "main_write_gate.py"),
    "arms hooks BEFORE running the suite":
        lambda L: 0 <= idx(L, "core.hooksPath .githooks") < idx(L, "run_all.py"),
    "no continue-on-error":
        lambda L: not has(L, "continue-on-error"),
    "no || true":
        lambda L: not has(L, "|| true"),
    "no if: always() on a gating step":
        lambda L: not has(L, "if: always()"),
}

# ── the mutants ────────────────────────────────────────────────────────────────────────────
# Each is the live workflow, broken in exactly one way, and each MUST take at least one check
# down. `MUT_COMMENT_ONLY` is the odd one out: it is broken in a way that must NOT be detected
# as breakage, because a comment is not a step.
MUT_SOFT_GATE = ("adds a real soft step",
                 lambda t: t.replace("        run: python3 .agents/scripts/tests/run_all.py",
                                     "        continue-on-error: true\n"
                                     "        run: python3 .agents/scripts/tests/run_all.py"))
MUT_PARTIAL_SUITE = ("swaps the real entrypoint for a subset",
                     lambda t: t.replace("python3 .agents/scripts/tests/run_all.py",
                                         "python3 .agents/scripts/tests/test_check_maps.py"))
MUT_NO_GATE_TRIGGER = ("drops the gate/** trigger",
                       lambda t: t.replace("      - 'gate/**'", "      - 'nope/**'")
                                  .replace("branches: ['gate/**']", "branches: ['nope/**']"))
MUT_RENAMED_CHECK = ("renames the job away from the ruleset's check",
                     lambda t: t.replace(f"name: {CHECK_NAME}", "name: some-other-check"))
MUT_SHALLOW = ("shallow checkout",
               lambda t: t.replace("fetch-depth: 0", "fetch-depth: 1"))

MUTANTS = [MUT_SOFT_GATE, MUT_PARTIAL_SUITE, MUT_NO_GATE_TRIGGER, MUT_RENAMED_CHECK, MUT_SHALLOW]


def mut_reorder(text: str) -> str:
    """Move the arm step AFTER the suite step — the mutation a 'contains' check cannot see.

    Relocation, never deletion: deleting the arm step would also fail the plain "is it present"
    style of check, so it would not isolate the ordering assertion at all
    ([[source-grep-guards-cannot-see-order]]).
    """
    lines = text.splitlines()
    a = next(i for i, l in enumerate(lines) if "core.hooksPath .githooks" in l and not l.lstrip().startswith("#"))
    b = next(i for i, l in enumerate(lines) if "run_all.py" in l and l.strip().startswith("run:"))
    arm = lines.pop(a)
    lines.insert(b, arm)
    return "\n".join(lines)


# A workflow whose ONLY mention of the banned literals is inside comments. This must be judged
# CLEAN. If comment-stripping regresses, this is the case that catches it — and it is the exact
# shape of the live file, which discusses `continue-on-error` at length in its header.
MUT_COMMENT_ONLY = """\
# This gate has no continue-on-error and no || true anywhere.
# It must not use if: always() either.
name: main write gate
on:
  pull_request:
    branches: [main]
  push:
    branches: ['gate/**']
jobs:
  gate:
    name: main-write-gate
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: git config core.hooksPath .githooks
      - run: python3 .agents/scripts/tests/run_all.py
      - run: python3 .agents/scripts/workflow_lint.py --toolkit-only
      - run: python3 .agents/scripts/main_write_gate.py --mode pr
"""


# ── a real repo with a real merge, for gate mode ───────────────────────────────────────────
def sh(*args: str, cwd: Path) -> tuple[int, str]:
    r = subprocess.run(list(args), cwd=str(cwd), capture_output=True, text=True, errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def make_pair(tmp: Path) -> Path:
    """A work clone with a real `origin`, so `origin/main` and remote branch tips exist.

    The merge-shape check reads remote-tracking refs. A single local repo cannot exercise it,
    and faking the refs would test the fake.
    """
    bare = tmp / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)],
                   capture_output=True, text=True)
    work = tmp / "work"
    subprocess.run(["git", "clone", "-q", str(bare), str(work)], capture_output=True, text=True)
    sh("git", "config", "user.email", "t@t.t", cwd=work)
    sh("git", "config", "user.name", "t", cwd=work)
    (work / ".agents").mkdir(parents=True)
    (work / ".agents/jira.conf").write_text('JIRA_KEYS="SCC"\n', encoding="utf-8")
    (work / "README").write_text("base\n", encoding="utf-8")
    sh("git", "add", "README", ".agents", cwd=work)
    sh("git", "commit", "-qm", "base", cwd=work)
    sh("git", "push", "-q", "origin", "main", cwd=work)
    return work


def land(work: Path, branch: str, filename: str) -> None:
    """Create `branch`, commit on it, push it, and merge it into main with --no-ff."""
    sh("git", "checkout", "-q", "-b", branch, "main", cwd=work)
    (work / filename).write_text("x\n", encoding="utf-8")
    sh("git", "add", filename, cwd=work)
    sh("git", "commit", "-qm", f"work on {branch}", cwd=work)
    sh("git", "push", "-q", "origin", branch, cwd=work)
    sh("git", "checkout", "-q", "main", cwd=work)
    sh("git", "merge", "-q", "--no-ff", "-m", f"merge: {branch} -> main", branch, cwd=work)


def gate_rc(work: Path) -> int:
    r = subprocess.run([sys.executable, str(SCRIPT), "--mode", "gate", "--repo", str(work),
                        "--base", "origin/main", "--head", "HEAD"],
                       cwd=str(work), capture_output=True, text=True, errors="replace")
    return r.returncode


def main() -> int:
    c = Cases("main write gate — server side (SCC-118)")

    # ⛔ EVERY `c.check` SITS UNDER A `c.block` GUARD (test_suite_runner's ORPHAN rule): an
    # unguarded check runs under EVERY `--case` filter and counts toward every filtered tally,
    # so a mutant it kills is attributed to whichever case was named. The blocks were added when
    # SCC-192 wired the first one into this file. ⛔ Anything a LATER block reads stays OUTSIDE
    # them (`text`, `live`, `keys`) - under a filter a sibling block simply does not run, and a
    # fixture defined inside one is then not there at all (SCC-156 paid for that with five files).
    if c.block("T1 · the workflow and the validator exist"):
        c.check("the workflow exists", WORKFLOW.is_file(), str(WORKFLOW))
        c.check("the validator exists", SCRIPT.is_file(), str(SCRIPT))
    if not WORKFLOW.is_file():
        return c.finish()

    text = WORKFLOW.read_text(encoding="utf-8")
    live = effective_lines(text)
    keys = ["SCC"]

    if c.block("T1b · the CI job is shaped the way the gate needs"):
        for name, pred in CHECKS.items():
            c.check(f"workflow · {name}", bool(pred(live)))

    # ── tier 3: the mutation battery ───────────────────────────────────────────────────────
    # Each mutant must take at least one check down. A mutant that changes nothing means the
    # corresponding assertion is decorative.
    if c.block("T3 · the mutation battery over the workflow"):
        for label, mutate in MUTANTS:
            broken = effective_lines(mutate(text))
            caught = [n for n, p in CHECKS.items() if not p(broken)]
            c.check(f"mutant caught · {label}", bool(caught),
                    ", ".join(caught) if caught else "NO CHECK FIRED — the assertion is vacuous")

        reordered = effective_lines(mut_reorder(text))
        c.check("mutant caught · arm step relocated AFTER the suite",
                not CHECKS["arms hooks BEFORE running the suite"](reordered),
                "a 'contains' check passes this identically — only the index comparison bites")
        c.check("relocation left the arm step PRESENT (so only ordering is isolated)",
                any("core.hooksPath .githooks" in l for l in reordered))

        comment_only = effective_lines(MUT_COMMENT_ONLY)
        for banned in ("no continue-on-error", "no || true", "no if: always() on a gating step"):
            c.check(f"comments do not trip · {banned}", bool(CHECKS[banned](comment_only)),
                    "comment stripping regressed — the guard now inverts on the live file")

    # ── tier 2a: the validator, as a pure function ─────────────────────────────────────────
    if c.block("T2a · authorised_branch, as a pure function"):
        for good in ("chore/SCC-118-server-side-main-gate", "epic/SCC-31-thin-toolkit",
                     "chore/SCC-1-a"):
            c.check(f"ALLOWS an authorised source · {good}", mwg.authorised_branch(good, keys)[0])
        for bad, why in (
            ("claude/fit-repo-workflow-integration-xzvg6q", "the branch PR #2 actually came from"),
            ("main", "main itself"),
            ("chore/SCC-118", "no slug — not a branch this system produces"),
            ("chore/AVCH-1-x", "another repo's key"),
            ("feature/SCC-1-x", "not one of the two roads"),
            ("", "nothing at all"),
        ):
            c.check(f"REJECTS · {why}", not mwg.authorised_branch(bad, keys)[0], repr(bad))

        c.check("the key set comes from .agents/jira.conf, not a hardcode",
                mwg.read_jira_keys(REPO) == ["SCC"], str(mwg.read_jira_keys(REPO)))

    # ── tier 2b: the validator, through a real repo and a real merge ───────────────────────
    if c.block("T2b · the validator through a real repo and a real merge"):
      with TempDir() as tmp:
          work = make_pair(tmp)
          land(work, "chore/SCC-1-first", "a.txt")
          c.check("ALLOWS one merge of a pushed chore branch, sitting on origin/main",
                  gate_rc(work) == 0)

          # Batching: a second merge on top, pushed as one. `t_tip == local_sha` would hold the
          # whole way — this is the exact SCC-71 failure the local hook's ^1 check exists for,
          # reproduced on the server side.
          land(work, "chore/SCC-2-second", "b.txt")
          c.check("REJECTS two merges batched into one push",
                  gate_rc(work) != 0, "main must advance by exactly one merge commit")

      with TempDir() as tmp:
          work = make_pair(tmp)
          land(work, "claude/some-story-lane", "a.txt")
          c.check("REJECTS a merge of a story lane (claude/*)", gate_rc(work) != 0)

      with TempDir() as tmp:
          work = make_pair(tmp)
          sh("git", "checkout", "-q", "-b", "chore/SCC-3-unpushed", "main", cwd=work)
          (work / "a.txt").write_text("x\n", encoding="utf-8")
          sh("git", "add", "a.txt", cwd=work)
          sh("git", "commit", "-qm", "work", cwd=work)
          sh("git", "checkout", "-q", "main", cwd=work)
          sh("git", "merge", "-q", "--no-ff", "-m", "merge: chore/SCC-3-unpushed -> main",
             "chore/SCC-3-unpushed", cwd=work)
          c.check("REJECTS a merge of a branch that was never pushed to origin",
                  gate_rc(work) != 0, "nothing on the remote vouches for what was merged")

      with TempDir() as tmp:
          work = make_pair(tmp)
          sh("git", "checkout", "-q", "-b", "chore/SCC-4-ff", "main", cwd=work)
          (work / "a.txt").write_text("x\n", encoding="utf-8")
          sh("git", "add", "a.txt", cwd=work)
          sh("git", "commit", "-qm", "work", cwd=work)
          sh("git", "push", "-q", "origin", "chore/SCC-4-ff", cwd=work)
          sh("git", "checkout", "-q", "main", cwd=work)
          sh("git", "merge", "-q", "--ff-only", "chore/SCC-4-ff", cwd=work)
          c.check("REJECTS a fast-forward (no merge commit at all)", gate_rc(work) != 0)


    # ══ SCC-192 · tier 2c: a PR that IS a close-out must carry the ceremony's RECEIPTS ══════
    #
    # THE DEFECT. An agent can run this ceremony's steps BY HAND instead of invoking
    # `/smh-close-task-merge-tree`, and nothing could tell: the steps it does run all pass.
    # Measured on SCC-164's own landing (PR #13, 2026-08-16) — Step 2.5 (the flight recorder)
    # skipped outright, the preflight run without a fetch. The PR was green throughout.
    #
    # So the gate stops asking whether the ceremony was INTENDED and asks what it LEAVES:
    #   * a preflight receipt for this key + branch, with a fresh comparison and a clear verdict
    #   * a flight event at the walkthrough's governing verdict sha
    #
    # ⛔ THREE CONSTRAINTS, EACH CLOSING A WAY THIS BECOMES A LOOP NOTHING CAN PUSH THROUGH
    # (the operator asked this question before a line was written, and the answers are cases):
    #   1. never key on HEAD — a receipt commit MOVES head, so artifacts-only commits after the
    #      verdict sha must not invalidate anything (A4).
    #   2. `--mode pr` only. Road 2 (`gate/**`) is the local door's road and is untouched.
    #   3. it triggers ONLY on a `task.yaml` naming this door. A PR without one owes nothing
    #      (A5) — and a LIGHTWEIGHT lane, which has a manifest but no review verdict, owes a
    #      receipt and NOT an event (A5b): `/smh-quick-fix` writes no `Verdict:` line, and
    #      `flight_recorder record` REFUSES without one, so demanding it would make the
    #      lightweight lane unlandable. Measured: 10 landed lobby lanes have a door manifest
    #      and no stamp.
    if c.block("SCC-192 · a close-out PR must carry its receipts"):
        import json as _json

        def close_out_pr(tmp, *, receipt: dict | None = None, event: bool = True,
                         verdict: bool = True, manifest: bool = True,
                         extra_artifact_commits: int = 0, upper_stamp: bool = False,
                         raw_receipt: str | None = None, art: str = "",
                         sibling_branch: str = "", foreign_branch: str = "",
                         subtask: bool = False,
                         fenced_decoy: bool = False, second_stamp: bool = False,
                         close_command: str = "smh-close-task-merge-tree"):
            """A lane branch shaped exactly like a real close-out, returned as (work, branch).

            The verdict sha is a REAL commit on the lane, and the walkthrough citing it lands
            afterwards — which is the true shape (the stamp can never cite the commit it rides
            in) and the reason a HEAD-keyed rule could never pass.
            """
            work = make_pair(tmp)
            branch = "chore/SCC-9-lane"
            art = art or "_artifacts/_main/2026-08-17_scc-9-lane"
            if sibling_branch:
                # ⛔ ON `main`, BEFORE THE LANE FORKS. What makes the 57 landed manifests
                # legitimate is that they are UNCHANGED on the base - they only reach the tree
                # diff because `base` is routinely not the merge-base. A fixture that WRITES
                # this file on the lane is modelling a mis-declared branch, not landed history,
                # which is the RED case below.
                sib = work / "_artifacts/_main/2026-08-17_scc-7-other"
                sib.mkdir(parents=True, exist_ok=True)
                (sib / "task.yaml").write_text(
                    f"task_key: SCC-7\nprimary_repo: work\nbranch: {sibling_branch}\n"
                    f"close_command: {close_command}\nsecondary_repos: []\n", encoding="utf-8")
                sh("git", "add", "_artifacts", cwd=work)
                sh("git", "commit", "-qm", "SCC-7 chore: a lane that already landed [sop-ok]",
                   cwd=work)
                sh("git", "push", "-q", "origin", "main", cwd=work)
            sh("git", "checkout", "-q", "-b", branch, "main", cwd=work)
            (work / "docs").mkdir(exist_ok=True)
            (work / "docs/x.md").write_text("the work\n", encoding="utf-8")
            sh("git", "add", "docs/x.md", cwd=work)
            sh("git", "commit", "-qm", "SCC-9 docs: the work", cwd=work)
            code_sha = sh("git", "rev-parse", "HEAD", cwd=work)[1].strip()

            d = work / art
            d.mkdir(parents=True)
            if manifest:
                (d / "task.yaml").write_text(
                    f"task_key: SCC-9\nprimary_repo: work\nbranch: {branch}\n"
                    f"close_command: {close_command}\nsecondary_repos: []\n", encoding="utf-8")
            if subtask:
                # ⛔ NOT a manifest. `endswith("task.yaml")` matches this too, and it carries a
                # door name and no receipt - so a suffix match refuses the PR over a file that
                # is not the thing being checked.
                (d / "subtask.yaml").write_text(
                    f"task_key: SCC-9b\nprimary_repo: work\nbranch: {branch}\n"
                    f"close_command: {close_command}\nsecondary_repos: []\n", encoding="utf-8")
            if foreign_branch:
                # The other half: a manifest THIS PR writes, declaring a branch that is not the
                # PR's. Nothing landed it; it is a typo or a copied folder, and the old
                # print-only skip left the close-out entirely ungated on one wrong character.
                fo = work / "_artifacts/_main/2026-08-17_scc-6-typo"
                fo.mkdir(parents=True, exist_ok=True)
                (fo / "task.yaml").write_text(
                    f"task_key: SCC-6\nprimary_repo: work\nbranch: {foreign_branch}\n"
                    f"close_command: {close_command}\nsecondary_repos: []\n", encoding="utf-8")
            (d / "walkthrough.md").write_text(
                "# SCC-9\n\n## Your Actions\n\nNothing owed.\n"
                # A stamp pasted AS EVIDENCE inside a fence sits at column 0 and matches
                # VERDICT_RE. `strip_fenced` is the only reason it does not govern, and a
                # fenced FAIL here would demand a flight event that cannot exist.
                + ("\n```\nVerdict: FAIL @ 0000000\n```\n" if fenced_decoy else "")
                # An earlier review, superseded. `stamps[-1]` is what makes the LATEST one
                # govern; `stamps[0]` would key the event demand on a dead sha.
                + ("\n## Earlier review\n\nVerdict: CONCERNS @ 1111111\n" if second_stamp else "")
                + (f"\n## Code Review\n\nVerdict: PASS @ "
                   f"{code_sha.upper() if upper_stamp else code_sha}\n" if verdict else ""),
                encoding="utf-8")
            # "AUTO" resolves to the lane's real verdict sha, so a case aimed at ONE field can
            # leave the others valid. Without it every hand-built receipt carried
            # `verdict_sha: None`, which is itself a refusal now - two errors in a fixture
            # written to isolate one.
            r = dict(receipt) if receipt is not None else {
                "schema_v": 1, "task_key": "SCC-9", "branch": branch,
                "verdict_sha": code_sha if verdict else None, "when": None,
                "fetch": True, "fresh": True, "accept_unpushed_main": False,
                "lane": "LOCAL", "verdict": "clear to close out and merge",
                "errors": 0, "warnings": 0, "exit": 0}
            if r.get("verdict_sha") == "AUTO":
                r["verdict_sha"] = code_sha
            if raw_receipt is not None:
                # BYTES, not a dict: `null`, `[1,2]` and `not json at all` are the shapes a
                # dict fixture structurally cannot produce.
                (d / "preflight-receipt.json").write_text(raw_receipt, encoding="utf-8")
            elif r:
                (d / "preflight-receipt.json").write_text(
                    _json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            if event and verdict:
                ev = work / f"_artifacts/_main/workflow-events/2026-08/SCC-9_{code_sha[:7]}.json"
                ev.parent.mkdir(parents=True, exist_ok=True)
                ev.write_text(_json.dumps({"v": 1, "task": "SCC-9", "sha": code_sha}) + "\n",
                              encoding="utf-8")
            sh("git", "add", "_artifacts", cwd=work)
            sh("git", "commit", "-qm", "SCC-9 docs: walkthrough + receipts [sop-ok]", cwd=work)
            for i in range(extra_artifact_commits):
                (d / f"note{i}.md").write_text("an artifacts-only commit after the verdict\n",
                                               encoding="utf-8")
                sh("git", "add", str(d / f"note{i}.md"), cwd=work)
                sh("git", "commit", "-qm", f"SCC-9 chore(recorder): flight event [sop-ok]", cwd=work)
            sh("git", "push", "-q", "origin", branch, cwd=work)
            return work, branch

        def pr_rc(work: Path, branch: str, base: str = "origin/main") -> tuple[int, str]:
            r = subprocess.run([sys.executable, str(SCRIPT), "--mode", "pr", "--repo", str(work),
                                "--branch", branch, "--base", base, "--head", "HEAD"],
                               cwd=str(work), capture_output=True, text=True, errors="replace")
            return r.returncode, (r.stdout or "") + (r.stderr or "")

        with TempDir() as tmp:
            work, branch = close_out_pr(tmp, extra_artifact_commits=2)
            rc, out = pr_rc(work, branch)
            c.check("A4 GREEN: both receipts present, keyed on the verdict sha, TWO "
                    "artifacts-only commits after them", rc == 0, out.strip()[-600:])

        with TempDir() as tmp:
            work, branch = close_out_pr(tmp, event=False)
            rc, out = pr_rc(work, branch)
            c.check("A1 RED: a reviewed close-out with NO flight event is refused, by name",
                    rc != 0 and "flight event" in out.lower(), out.strip()[-600:])

        with TempDir() as tmp:
            work, branch = close_out_pr(tmp, receipt={})
            rc, out = pr_rc(work, branch)
            c.check("A2 RED: no preflight receipt is refused, by name",
                    rc != 0 and "preflight-receipt.json in this PR" in out
                    and "task_preflight.py --expect-key" in out, out.strip()[-600:])

        with TempDir() as tmp:
            work, branch = close_out_pr(tmp, receipt={
                "schema_v": 1, "task_key": "SCC-9", "branch": "chore/SCC-9-lane",
                "verdict_sha": "AUTO", "when": None, "fetch": False, "fresh": False,
                "accept_unpushed_main": False, "lane": "LOCAL",
                "verdict": "clear - but vs the LAST fetch (STALE), not the remote",
                "errors": 0, "warnings": 1, "exit": 1})
            rc, out = pr_rc(work, branch)
            c.check("A3 RED: a receipt whose comparison was NOT fresh is refused, naming the flag",
                    rc != 0 and "the receipt says fresh=false" in out, out.strip()[-600:])

        with TempDir() as tmp:
            work, branch = close_out_pr(tmp, receipt={
                "schema_v": 1, "task_key": "SCC-9", "branch": "chore/SOMEONE-ELSE-1",
                "verdict_sha": "AUTO", "when": None, "fetch": True, "fresh": True,
                "accept_unpushed_main": False, "lane": "LOCAL",
                "verdict": "clear to close out and merge", "errors": 0, "warnings": 0, "exit": 0})
            rc, out = pr_rc(work, branch)
            # ⛔ NAME THE MESSAGE. `"branch" in out` was satisfied by the gate's own PASS line
            # ("authorised source branch"), so this case scored a kill for ANY refusal at all -
            # and once a second refusal path existed, SB-M6 sailed past it.
            c.check("A3b RED: a receipt from ANOTHER branch does not vouch for this lane",
                    rc != 0 and "the receipt records branch `chore/SOMEONE-ELSE-1`" in out,
                    out.strip()[-600:])

        with TempDir() as tmp:
            work, branch = close_out_pr(tmp, receipt={
                "schema_v": 1, "task_key": "SCC-9", "branch": "chore/SCC-9-lane",
                "verdict_sha": "AUTO", "when": None, "fetch": True, "fresh": True,
                "accept_unpushed_main": False, "lane": "LOCAL",
                "verdict": "BLOCKED - resolve the errors above",
                "errors": 2, "warnings": 0, "exit": 2})
            rc, out = pr_rc(work, branch)
            c.check("A3c RED: a receipt recording a BLOCKED verdict is not a pass",
                    rc != 0 and "records the verdict `BLOCKED" in out, out.strip()[-600:])

        with TempDir() as tmp:
            # ⭐ A3d · THE CASE SB-M7 PROVED WAS MISSING. A3 above aims at `fresh`, so dropping
            # `or "stale" in verdict` from the verdict test changed nothing any case could see:
            # the two reads were one assertion wearing two names. A receipt claiming fresh=true
            # while carrying the STALE verdict string is the shape a hand-edited (or
            # half-migrated) receipt takes, and the gate reads a FILE IN THE PR - it cannot
            # assume the two fields agree just because one writer makes them agree.
            work, branch = close_out_pr(tmp, receipt={
                "schema_v": 1, "task_key": "SCC-9", "branch": "chore/SCC-9-lane",
                "verdict_sha": "AUTO", "when": None, "fetch": True, "fresh": True,
                "accept_unpushed_main": False, "lane": "LOCAL",
                "verdict": "clear - but vs the LAST fetch (STALE), not the remote",
                "errors": 0, "warnings": 1, "exit": 1})
            rc, out = pr_rc(work, branch)
            c.check("A3d RED: a 'clear' verdict that says STALE is not a clear preflight",
                    rc != 0 and "records the verdict `clear - but" in out
                    and "STALE" in out, out.strip()[-600:])

        with TempDir() as tmp:
            # ⭐ A6 · THE BLIND LENS'S F2, EXECUTED. `verdict_sha` empty read as AGREEMENT, and
            # `write_receipt` records `null` by design on a lane with no stamp yet - so a
            # receipt taken BEFORE the review resolved, committed once and never refreshed,
            # satisfied the check written to catch exactly that. Empty-means-pass in a gate.
            work, branch = close_out_pr(tmp, receipt={
                "schema_v": 1, "task_key": "SCC-9", "branch": "chore/SCC-9-lane",
                "verdict_sha": None, "when": None, "fetch": True, "fresh": True,
                "accept_unpushed_main": False, "lane": "LOCAL",
                "verdict": "clear to close out and merge", "errors": 0, "warnings": 0,
                "exit": 0})
            rc, out = pr_rc(work, branch)
            c.check("A6 RED: a receipt with NO verdict_sha does not vouch for a reviewed lane",
                    rc != 0 and "verdict_sha" in out, out.strip()[-600:])

        with TempDir() as tmp:
            # A6b CONTROL · VERDICT_RE accepts [0-9a-fA-F] and `git rev-parse` emits lowercase,
            # so an uppercase stamp made all three prefix clauses true and refused a lane whose
            # receipt was correct. The comparison is case-folded; this is the only shape that
            # can tell.
            work, branch = close_out_pr(tmp, upper_stamp=True)
            rc, out = pr_rc(work, branch)
            c.check("A6b CONTROL: an UPPERCASE verdict stamp still matches its own receipt",
                    rc == 0, out.strip()[-600:])

        # ⛔⛔ A7 · A RECEIPT THAT IS NOT AN OBJECT, IN THE THREE SHAPES A DICT FIXTURE CANNOT
        # PRODUCE - and `null` was a LIVE FAIL-OPEN when the test-adequacy audit measured it.
        # `json.loads("null")` is `None`, the guard read `if r is not None`, and so a file of
        # four bytes recorded no failure at all and satisfied the entire gate. The code above it
        # said in capitals that this had been fixed; the fix for a different defect
        # (UnboundLocalError) had silently re-opened it, and no case could tell because every
        # fixture wrote a real dict or no file. This is the whole reason a guard needs a case.
        for label, raw, want in (
                ("null", "null\n", "NoneType, not a receipt object"),
                ("a JSON array", "[1, 2]\n", "list, not a receipt object"),
                ("not JSON at all", "clear to merge, trust me\n", "not readable JSON")):
            with TempDir() as tmp:
                work, branch = close_out_pr(tmp, raw_receipt=raw)
                rc, out = pr_rc(work, branch)
                c.check(f"A7 RED: a receipt containing {label} is refused, and named",
                        rc != 0 and want in out, out.strip()[-600:])

        with TempDir() as tmp:
            # ⭐ A8 · THE pr_branch SKIP, WHICH IS A `continue` - i.e. a BYPASS shape. Widening
            # it turns this gate into a no-op for the lane it exists to judge, and nothing
            # measured it. Both halves matter: the sibling is spared, AND the reason is printed
            # so a genuine key/branch mismatch is never silent.
            # ⛔ `--base origin/main~1`, and that is the REAL shape, not a contrivance: GitHub's
            # `pull_request.base.sha` is routinely a commit or two behind the merge-base (PR #12's
            # was one past), which is the ONLY reason a sibling's landed manifest appears in
            # `base..head` at all. With base == the true merge-base it never reaches the loop,
            # so a fixture that uses it cannot exercise the skip it is written for.
            work, branch = close_out_pr(tmp, sibling_branch="chore/SCC-7-other")
            rc, out = pr_rc(work, branch, base="origin/main~1")
            c.check("A8 GREEN: another lane's LANDED manifest is skipped, and the skip is SAID",
                    rc == 0 and "declares `chore/SCC-7-other`" in out and "skipping" in out,
                    out.strip()[-600:])

        with TempDir() as tmp:
            # ⛔ A8b · AND THE OTHER HALF, WHICH WAS THE HOLE. The skip is print-only, so a
            # manifest declaring the WRONG branch produced judged == 0, no fails, and
            # `[PASS] close-out receipts` - a close-out reaching main with nothing looking at
            # it, on a one-character typo. "Landed" is what earns the skip, not "declares
            # something else".
            work, branch = close_out_pr(tmp, foreign_branch="chore/SCC-6-typo")
            rc, out = pr_rc(work, branch)
            c.check("A8b RED: a manifest this PR WRITES for another branch is refused, not skipped",
                    rc != 0 and "declaring branch `chore/SCC-6-typo`" in out,
                    out.strip()[-600:])

        with TempDir() as tmp:
            # A9 · a non-ASCII lane path. git octal-quotes it, `git show` then fails on the
            # quoted spelling, and the loop `continue`s - the lane is never judged at all. The
            # lens reproduced that with `_SCC-3-café`; `-c core.quotepath=false` is the fix and
            # this is the only shape that can see whether it is still there.
            work, branch = close_out_pr(tmp, art="_artifacts/_main/2026-08-17_scc-9-café",
                                        event=False)
            rc, out = pr_rc(work, branch)
            c.check("A9 RED: a non-ASCII artifacts path is still JUDGED, not silently skipped",
                    rc != 0 and "flight event" in out.lower(), out.strip()[-600:])

        with TempDir() as tmp:
            # A10 · `subtask.yaml` ends with "task.yaml". A suffix match makes this PR red over
            # a file that is not a manifest, and names the wrong file to whoever reads it.
            work, branch = close_out_pr(tmp, subtask=True)
            rc, out = pr_rc(work, branch)
            c.check("A10 GREEN: subtask.yaml is not a manifest (basename, never endswith)",
                    rc == 0, out.strip()[-600:])

        with TempDir() as tmp:
            # A11 · the gate's own verdict reader. A FENCED stamp is evidence quoted in prose,
            # not a verdict; without `strip_fenced` this fenced FAIL @ 0000000 would govern and
            # demand a flight event at a sha that is not a commit - an unlandable lane, fixable
            # only by editing a walkthrough that is already on main.
            work, branch = close_out_pr(tmp, fenced_decoy=True, second_stamp=True)
            rc, out = pr_rc(work, branch)
            c.check("A11 GREEN: a fenced decoy does not govern, and the LATEST real stamp does",
                    rc == 0, out.strip()[-600:])

        # ⭐ A12 · WHAT F6 WAS FOR, PINNED. The blind lens measured this file importing SEVEN
        # local modules - jira_feed, gate_receipt, hooks_armed, walkthrough_roster and the rest -
        # to buy one regex and two helpers, so an import-time break anywhere in that chain
        # became a break in the gate that guards `main`. The primitives moved to `wf_common`
        # (stdlib-only leaf). Nothing else would notice them moving back: re-adding
        # `from task_preflight import ...` passes every case in this file.
        import ast as _ast
        _tree = _ast.parse((SCRIPT).read_text(encoding="utf-8"))
        _names = set()
        for _n in _ast.walk(_tree):
            if isinstance(_n, _ast.ImportFrom) and _n.level == 0 and _n.module:
                _names.add(_n.module.split(".")[0])
            elif isinstance(_n, _ast.Import):
                _names.update(a.name.split(".")[0] for a in _n.names)
        _local = {m for m in _names if (SCRIPT.parent / f"{m}.py").is_file()}
        c.check("A12 the main-write gate imports LEAF modules only (wf_common, sop_currency)",
                _local == {"wf_common", "sop_currency"},
                f"local imports: {sorted(_local)} - a heavier chain puts someone else's "
                f"import-time break in the gate that guards main")

        with TempDir() as tmp:
            # A5 · the control that keeps loop 3 shut: no manifest, no demand.
            work = make_pair(tmp)
            sh("git", "checkout", "-q", "-b", "chore/SCC-8-plain", "main", cwd=work)
            (work / "docs").mkdir(exist_ok=True)
            (work / "docs/y.md").write_text("a lightweight docs fix\n", encoding="utf-8")
            sh("git", "add", "docs/y.md", cwd=work)
            sh("git", "commit", "-qm", "SCC-8 docs: a fix with no ceremony", cwd=work)
            sh("git", "push", "-q", "origin", "chore/SCC-8-plain", cwd=work)
            rc, out = pr_rc(work, "chore/SCC-8-plain")
            c.check("A5 GREEN: a PR with no task.yaml is not a close-out and owes nothing",
                    rc == 0, out.strip()[-600:])

        with TempDir() as tmp:
            # A5b · ⭐ THE LIGHTWEIGHT LANE. A manifest, a receipt, and NO review verdict —
            # `/smh-quick-fix`'s exact shape. It must pass: the recorder cannot record a lane
            # that has no stamp, so demanding an event here would make the lane unlandable.
            work, branch = close_out_pr(tmp, verdict=False, event=False)
            rc, out = pr_rc(work, branch)
            c.check("A5b GREEN: a lightweight lane (manifest + receipt, no verdict stamp) lands",
                    rc == 0, out.strip()[-600:])

        with TempDir() as tmp:
            # A5c · a manifest naming ANOTHER door is not this ceremony.
            work, branch = close_out_pr(tmp, close_command="cicd-push-e2e", event=False,
                                        receipt={})
            rc, out = pr_rc(work, branch)
            c.check("A5c GREEN: a manifest naming another door owes this gate nothing",
                    rc == 0, out.strip()[-600:])

        with TempDir() as tmp:
            # ⛔ MODE SCOPE (loop 2). The same repo state, driven through `gate` mode, must be
            # judged on merge shape alone — the local door's road is untouched by this.
            work, branch = close_out_pr(tmp, receipt={}, event=False)
            sh("git", "checkout", "-q", "main", cwd=work)
            sh("git", "merge", "-q", "--no-ff", "-m", f"merge: {branch} -> main", branch, cwd=work)
            c.check("A-mode GREEN: mode `gate` never asks for receipts (Road 2 untouched)",
                    gate_rc(work) == 0, "the local door's road must not gain a second gate")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
