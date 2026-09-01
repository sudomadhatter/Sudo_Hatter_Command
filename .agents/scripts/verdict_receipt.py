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
  * Edits that do not ADD a stamp - defusing an old stamp, moving a section, context
    lines in a hunk.

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

OPTOUT = "[verdict-ok]"
MARKER = Path(".agents/scripts/git-hooks/VERDICT-ENFORCE")
# The stamp is machine-read at line start, unfenced (walkthrough_roster.py strips fences,
# closeout_preflight reads the first match) - so line start is where this gate reads too.
GATED_RE = re.compile(r"^\+Verdict:\s*(PASS|CONCERNS)\b")
FILE_RE = re.compile(r"^\+\+\+ b/(.+)$")


def has_optout(message: str) -> bool:
    return OPTOUT in message


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
            out.setdefault(current, []).append(v.group(1))
    return out


def problems(diff_text: str, repo: Path) -> list[str]:
    """Every refusal the staged diff earns. Pure given (diff, tree) - the test surface."""
    probs: list[str] = []
    for wt_path, verdicts in sorted(added_gated_stamps(diff_text).items()):
        gates_dir = (repo / wt_path).parent / "gates"
        receipt = gates_dir / "suite.json"
        if not receipt.is_file():
            probs.append(
                f"{wt_path}: adds `Verdict: {verdicts[0]}` with NO suite receipt at "
                f"{gates_dir.relative_to(repo)}/suite.json - run the suite through "
                f"gate_receipt.py first (there is no --result flag to fake)")
            continue
        try:
            data = json.loads(receipt.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
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
            ["git", "diff", "--cached", "--no-color", "--unified=0"],
            cwd=repo, capture_output=True, text=True, check=True).stdout
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
