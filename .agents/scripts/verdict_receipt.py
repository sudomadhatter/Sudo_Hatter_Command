#!/usr/bin/env python3
"""verdict_receipt.py - a stamped verdict arrives with evidence the suite ran (SCC-363).

THE DEFECT THIS CLOSES, measured on AVCH-106 (2026-08-31): a review section carrying
`Verdict: PASS` was committed while the standing suite was RED. Nothing mechanical linked
the stamp to a suite that ran - the verdict was prose, and prose is exactly what a cheap
model rationalizes past. `closeout_preflight` catches it at close-out, but that is turns
later; this gate refuses at the moment the stamp is WRITTEN, which is the only moment the
author still has the context (the same argument as sop_currency.py, one gate over).

THE RULE: a commit whose staged diff ADDS a `Verdict: PASS` or `Verdict: CONCERNS` line
to any `walkthrough.md` must carry a usable `suite` receipt (gate_receipt.py: result
pass/warn) in the lane's `gates/` directory beside that walkthrough. Deliberately NOT
gated:

  * `Verdict: FAIL` - recording a failure must never require a green suite.
  * `Verdict: WAIVED` - the operator's own act, and it exists precisely when gates are
    not green. (A Zoo seat may not stamp ANY verdict - that is seat law, SCC-362; this
    gate is the backstop for every author, not the seat rule.)
  * Edits that do not ADD a stamp - defusing an old stamp (`Superseded stamp ...`), and
    context lines in a hunk.
    NOT in this list, though an earlier draft claimed it: MOVING a section. Git cannot
    distinguish a move from an add - reordering `## Code Review` emits `-Verdict:` in one
    hunk and `+Verdict:` in another, and the gate refuses it whenever the lane's receipt has
    since gone missing or red. That is a true refusal, not a false one: the commit really is
    republishing a stamp the tree can no longer evidence.

KNOWN GAP - `--amend` AND SQUASH ARE BLIND, and the preflights are the backstop. During an
amend, HEAD is still the pre-amend commit, so `git diff --cached` is index-vs-HEAD and a stamp
already carried forward shows as no change at all; an interactive-rebase squash skips this hook
by the `rebase-merge` carve-out outright. So a logged `[verdict-ok]` bypass CAN be amended away
(reproduced at review). Closing it needs amend detection this hook cannot do reliably, and the
close-out preflights re-read the stamp against the receipt turns later, which is where it is
caught. Stated here so the next reader does not mistake the silence for coverage.

STALENESS STAYS WITH THE PREFLIGHTS. The receipt just written at commit time necessarily
records the parent sha over a dirty tree, so tree-identity cannot be judged here without
lying; `closeout_preflight` / `task_preflight` own that half (one receipt format, one
reader - receipt_defect() is shared). This gate is the tripwire for the observed forgery:
a stamp with NO receipt, or one whose recorded result is not a pass.

Escape hatch: `[verdict-ok]` in the commit message - logged in git forever, auditable,
same design as `[sop-ok]`. Disarm to warn-only: delete
`.agents/scripts/git-hooks/VERDICT-ENFORCE`.

Both machines: stdlib only, ASCII output, invoked via the interpreter probe in
verdict-receipt.sh (python3 -> python -> py, never assumed).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from gate_receipt import receipt_defect

# ⛔ SCOPE: THIS GATE RUNS IN THE COMMAND CENTRE ONLY, and the defect it cites was measured
# in another repo. Git hooks are repo-local by design and `sync-agents.ps1` does not ship
# `git-hooks/`, so AGY_AVIATIONCHAT has no verdict stage in its own `.githooks/commit-msg` and
# the next AVCH stamp over a red suite commits exactly as before. Porting it needs an AVCH
# ticket of its own (`cross-repo-work-needs-a-ticket-per-repo`); until then this covers
# `_artifacts/_main/` task lanes here, where the flat `<lane>/gates/suite.json` convention holds.

OPTOUT = "[verdict-ok]"
MARKER = Path(".agents/scripts/git-hooks/VERDICT-ENFORCE")
# ⛔ GATE WHAT ANY DOWNSTREAM READER WILL TREAT AS A STAMP — not what THIS file would prefer.
# The first cut anchored hard at line start ("unfenced law: line start or nothing") and exempted
# an indented `  Verdict: PASS`. Measured, the two readers DISAGREE: `wf.VERDICT_RE` (the
# preflights) rejects the indented line, but `walkthrough_roster._CLI_VERDICT_RE` — whose
# leading class is `[>\-*#\s]*` — FINDS it and judges it. So the indent was never a carve-out;
# it was a hole that produced a stamp the roster gate would act on and this gate never demanded
# a receipt for. This class mirrors the roster's, which is the widest reader in the system.
GATED_RE = re.compile(r"^\+[>\-*#\s]*\**\s*Verdict\s*:\**\s*\**(PASS|CONCERNS)\b",
                      re.IGNORECASE)  # the readers are case-insensitive; so is this
# ⛔ The `b/` prefix is git's DEFAULT, not a guarantee — and this gate fails OPEN without it.
# `diff.noprefix=true` emits `+++ path`, `diff.mnemonicPrefix=true` emits `+++ i/path`, and
# `diff.dstPrefix` sets it to anything at all. Any of the three makes this regex match nothing,
# so `current` stays None, no stamp is ever seen, and the commit is allowed in SILENCE — not
# even the warn-only line prints. Both halves of the fix matter: the prefix is made optional
# here, and `main()` pins the config on the git call so the common case stays exact.
FILE_RE = re.compile(r"^\+\+\+ (?:[abciwo]/)?(.+)$")
# The config pins for the staged-diff read. `--no-ext-diff` is the fourth leg: a configured
# `diff.external` driver replaces the output wholesale, which this parser cannot read at all.
DIFF_PINS = ["-c", "diff.noprefix=false", "-c", "diff.mnemonicPrefix=false",
             "-c", "diff.srcPrefix=a/", "-c", "diff.dstPrefix=b/"]


def message_body(raw: str) -> str:
    """The message GIT WILL KEEP — everything above the scissors, comments dropped.

    ⛔ `git commit -v` (and `commit.verbose=true`) appends the whole staged diff to
    COMMIT_EDITMSG below a scissors line, and git strips that section before storing the
    commit. Grepping the raw file therefore searched the DIFF for the opt-out token — and
    `[verdict-ok]` is a literal in this repo's own sources (this file, the wrapper, the SOP,
    the lane tickets). Any `-v` commit touching one of them got a silent bypass whose token
    never appeared in the shipped message, so the docstring's "logged in git forever,
    auditable" was false on exactly that path (review finding, reproduced).
    """
    out: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith("# ------------------------ >8 ------------------------"):
            break
        if s.startswith("#"):
            continue
        out.append(line)
    return "\n".join(out)


def has_optout(message: str) -> bool:
    return OPTOUT in message_body(message)


def added_gated_stamps(diff_text: str) -> dict[str, list[str]]:
    """walkthrough.md paths -> the gated verdicts their staged hunks ADD."""
    out: dict[str, list[str]] = {}
    current: str | None = None
    for line in diff_text.splitlines():
        m = FILE_RE.match(line)
        if m:
            p = m.group(1)
            current = p if Path(p).name == "walkthrough.md" else None
            continue
        if current is None or line.startswith("+++"):
            continue
        v = GATED_RE.match(line)
        if v:
            out.setdefault(current, []).append(v.group(1).upper())
    return out


def tracked_receipt(repo: Path, rel: str) -> str | None:
    """The receipt AS THE COMMIT WILL CARRY IT — read from the index, never the disk.

    ⛔ `Path.is_file()` was the original read and it fails OPEN. The house bans `git add -A`,
    so explicit-path staging is the default: `git add <lane>/walkthrough.md && git commit`
    stages the STAMP and leaves an untracked `gates/suite.json` sitting on disk. The old check
    saw that file, passed, and the commit landed carrying a verdict its own tree cannot
    evidence — exactly the AVCH-106 artifact this gate exists to prevent, and unrecoverable
    from a fresh clone or after `worktree remove --force` eats the untracked file.
    """
    try:
        r = subprocess.run(["git", "show", f":{rel}"], cwd=repo,
                           capture_output=True, encoding="utf-8", text=True)
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def problems(diff_text: str, repo: Path) -> list[str]:
    """Every refusal the staged diff earns. Pure given (diff, tree) - the test surface."""
    probs: list[str] = []
    for wt_path, verdicts in sorted(added_gated_stamps(diff_text).items()):
        gates_dir = (repo / wt_path).parent / "gates"
        receipt = gates_dir / "suite.json"
        rel = f"{Path(wt_path).parent.as_posix()}/gates/suite.json"
        blob = tracked_receipt(repo, rel)
        if blob is None:
            on_disk = receipt.is_file()
            why = ("is on disk but NOT STAGED - stage it so the commit carries its own evidence"
                   if on_disk else
                   "does not exist - run the suite through gate_receipt.py first "
                   "(it writes the result from a real exit code; there is no --result flag)")
            probs.append(
                f"{wt_path}: adds `Verdict: {verdicts[0]}` and the suite receipt at "
                f"{rel} {why}")
            continue
        try:
            data = json.loads(blob)
        except (json.JSONDecodeError, OSError):
            data = None
        # ⛔ A SUCCESSFUL parse of a NON-OBJECT is the trap (review finding, reproduced):
        # `json.loads("[]")` returns a list, `receipt_defect` calls `.get` on it, and the
        # AttributeError escaped uncaught. Because `problems()` runs before BOTH hatches in
        # `main()`, a malformed receipt made the gate impossible to disarm OR bypass.
        if not isinstance(data, dict):
            data = None
        defect = receipt_defect(data)
        if defect:
            probs.append(
                f"{wt_path}: adds `Verdict: {verdicts[0]}` but the suite receipt is "
                f"unusable ({defect}) - a verdict cannot stand on a suite that did not pass")
    return probs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--message-file", required=True)
    args = ap.parse_args()
    repo = Path(args.repo).resolve()

    try:
        diff = subprocess.run(
            ["git", *DIFF_PINS, "diff", "--cached", "--no-ext-diff", "--no-color",
             "--no-renames", "--unified=0"],
            cwd=repo, capture_output=True, encoding="utf-8", text=True, check=True).stdout
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"  ! verdict-receipt: could not read the staged diff ({exc}) - "
              "check skipped, commit allowed.")
        return 0

    probs = problems(diff, repo)
    if not probs:
        return 0

    message = Path(args.message_file).read_text(encoding="utf-8", errors="replace")
    if has_optout(message):
        print(f"  verdict-receipt: {OPTOUT} - stamp allowed without a receipt, "
              "and this bypass is now logged in git.")
        return 0

    armed = (repo / MARKER).is_file()
    print("  verdict-receipt: a Verdict stamp is EVIDENCE, and evidence needs a receipt "
          "(SCC-363):")
    for p in probs:
        print(f"    - {p}")
    if not armed:
        print("  (warn-only: VERDICT-ENFORCE marker absent - commit allowed.)")
        return 0
    print(f"  Fix: run the suite via gate_receipt.py run --gate suite, or put {OPTOUT} "
          "in the message to log the bypass.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
