#!/usr/bin/env python3
"""SCC-449 — the close-out must actually DELETE the branch it merged, and may not excuse itself.

⛔ THE DEFECT THIS CLOSES, measured 2026-09-11 at the close of SCC-447.

`git branch -d` refused a branch that was fully merged (`git rev-list --count origin/main..<branch>`
returned 0). It refused because it checks merged-into-UPSTREAM when an upstream is set and
merged-into-HEAD when one is not; this house pushes without `-u` (the sandbox cannot write the
lobby's `.git/config`), so there was no upstream, and the HEAD it fell back to was the SHARED lobby
standing on a `main` that was 20 commits stale. It answered honestly about the wrong reference.

That alone is a bug. What made it PERMANENT is the three things around it:

  1. the door asserted a FALSE diagnosis - "a refusal means the merge did not land" - so the agent
     went looking for a failed merge, found a landed one, and had no instruction for that state;
  2. Step 6's report template offered `(or why it was retained)`, so the verify step accepted its
     own failure as a valid outcome and could never go red;
  3. the correct mechanism was already written down in `/cicd-prune-worktree` Step 5 (measured
     2026-08-01) and was never ported here - a half-port, in the door that closes SCC-447's lane.

Measured before the cleanup: 7 local and 10 remote lane branches left behind, 5 of the 7 local ones
carrying no upstream at all. The enforcement suite was 90/90 green the whole time, because nothing in
the repo could see any of it. These checks are what can see it.
"""
import re
import sys
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]

TASK_DOOR = ".agents/commands/smh-close-task-merge-tree.md"
TASK_MIRROR = ".opencode/commands/smh-close-task-merge-tree.md"
PRUNE_DOOR = ".agents/commands/cicd-prune-worktree.md"
DOORS_WITH_MECHANISM = (TASK_DOOR, PRUNE_DOOR)


def one_line(text: str) -> str:
    """A literal sentence, matched across whatever line breaks the file wraps it at.

    Words are the law; where the line ends is not. (Carried from SCC-447, where binding the two
    together broke three checks nobody had changed.)
    """
    return r"\s+".join(re.escape(w) for w in text.split())


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def check_rows(checks) -> list[tuple[str, bool, str]]:
    """Every check's three rows - the check, its counter-example's applicability, its rejection.

    RETURNS the rows rather than calling `c.check` itself: `test_suite_runner.py`'s ORPHAN walker
    recognises exactly one guard idiom, a `c.check` inside the BODY of an `if c.block(...)`.
    """
    rows: list[tuple[str, bool, str]] = []
    for name, rel, pattern, flags, old, new in checks:
        txt = read(rel)
        rx = re.compile(pattern, flags)
        rows.append((name, bool(txt) and rx.search(txt) is not None,
                     "" if txt else f"{rel} missing or empty"))
        # ⛔ The counter-example is matched wrap-TOLERANTLY, exactly like the pattern it must defeat.
        # A plain `old in txt` binds the prose's line breaks, so re-flowing a paragraph makes the
        # counter-example "not present" and the check reports itself vacuous - a law nobody changed
        # going red. SCC-447 learned this for the pattern side and left the mutation side literal;
        # this is the same lesson one level over.
        hit = re.compile(one_line(old)).search(txt)
        applies = hit is not None
        rows.append(("  ^ counter-example applies", applies,
                     "" if applies else f"{rel}: {old!r} not present, so the proof would be vacuous"))
        mutated = (txt[:hit.start()] + new + txt[hit.end():]) if applies else txt
        rejected = applies and rx.search(mutated) is None
        rows.append(("  ^ counter-example is rejected", rejected,
                     "" if rejected
                     else "check survives its own counter-example - it cannot fail on content"))
    return rows


# The one sentence BOTH doors must carry, in the same words. `/cicd-prune-worktree` has said it since
# 2026-08-01; the Task door never got it. Pinning it in both is what makes the next half-port fail.
MECHANISM = ("`git branch -d` checks merged-into-**upstream** when an upstream exists, and "
             "merged-into-**HEAD** when one does not.")

CHECKS_A: tuple[tuple[str, str, str, int, str, str], ...] = (
    # ── The ORDER. Remote first removes the upstream in every case, which forces `-d` onto a real
    # ancestry question. The Task door used the opposite order, which on a `-u`-less push asks
    # nothing at all.
    ("A · the Task door deletes the REMOTE first, then the local branch", TASK_DOOR,
     r"git push origin --delete chore/<JIRA-KEY>-<slug>[\s\S]{0,120}?"
     r"^git branch -d chore/<JIRA-KEY>-<slug>", re.M,
     "git push origin --delete chore/<JIRA-KEY>-<slug>\ngit branch -d chore/<JIRA-KEY>-<slug>",
     "git branch -d chore/<JIRA-KEY>-<slug>\nenv -u GITHUB_TOKEN git push origin --delete chore/<JIRA-KEY>-<slug>"),
    ("A · and says the order is load-bearing, not a preference", TASK_DOOR,
     one_line("Deleting the remote FIRST removes the upstream, which forces `-d` onto a real "
              "ancestry question"), 0,
     "forces `-d` onto a real ancestry question",
     "is tidier to read in the report"),
)

CHECKS_B: tuple[tuple[str, str, str, int, str, str], ...] = (
    # ── The DIAGNOSIS. The old sentence was false and is what sent every agent to the wrong place.
    ("B · a refusal is NOT read as a failed merge", TASK_DOOR,
     one_line("A refusal here does NOT mean the merge failed"), 0,
     "A refusal here does NOT mean the merge failed",
     "A refusal here after a successful Step 3 means the merge did not land"),
    ("B · the real cause is named: no upstream, so `-d` falls back to a stale shared HEAD", TASK_DOOR,
     one_line("there is no upstream, `-d` falls back to HEAD - the shared lobby standing on `main` - "
              "and that checkout can be many commits behind the merge you just made"), 0,
     "the shared lobby standing on `main`",
     "the branch genuinely never landed"),
    ("B · the ladder PROVES the landing before touching anything", TASK_DOOR,
     r"git rev-list --count origin/main\.\.chore/<JIRA-KEY>-<slug>[^\n]*0 = every commit landed", 0,
     "0 = every commit landed",
     "run it if you are curious"),
    ("B · then aims the check at the ref that HAS the merge, unbypassed", TASK_DOOR,
     r"git branch --set-upstream-to=origin/main chore/<JIRA-KEY>-<slug>", 0,
     "git branch --set-upstream-to=origin/main chore/<JIRA-KEY>-<slug>",
     "git branch -D chore/<JIRA-KEY>-<slug>"),
    ("B · `-D` stays banned, and so does pulling the shared lobby", TASK_DOOR,
     one_line("Never `-D`, and never pull the shared lobby to fix this"), 0,
     "never pull the shared lobby to fix this",
     "pull the lobby and try again"),
    # The note's SECOND measured refusal (SCC-430, 2026-09-07), ported here so it survives the note.
    ("B · the REMOTE delete's stale-maps refusal is named, with its remedy", TASK_DOOR,
     one_line("Run that one push from the LANE worktree, whose maps are current, before step 2 "
              "removes it"), 0,
     "Run that one push from the LANE worktree, whose maps are current",
     "Re-run it with `--no-verify`"),
)

CHECKS_C: tuple[tuple[str, str, str, int, str, str], ...] = (
    # ── The ESCAPE. A verify step that accepts its own failure can never go red.
    ("C · Step 6 requires BOTH branch lists to come back empty", TASK_DOOR,
     one_line("Both list commands must come back EMPTY. A branch proven merged and still present is "
              "a close-out that did not finish"), 0,
     "a close-out that did not finish",
     "reported as retained, with the reason"),
    ("C · the one legal retention is a branch that did NOT land, and it is provable", TASK_DOOR,
     one_line("The one legal retention is a branch that did not land"), 0,
     "The one legal retention is a branch that did not land",
     "Retention is legal whenever `-d` refuses"),
)

CHECKS_D: tuple[tuple[str, str, str, int, str, str], ...] = tuple(
    (f"D · the mechanism sentence is carried by {Path(rel).name}", rel, one_line(MECHANISM), 0,
     "merged-into-**upstream** when an upstream exists",
     "merged-into-**main** whenever the lobby is current")
    for rel in DOORS_WITH_MECHANISM
)

# The retired sentences. Each is the exact text that licensed the failure; a door carrying one again
# has re-opened it.
DOOR_BANS: tuple[tuple[str, str, int, tuple[str, ...]], ...] = (
    ("the FALSE diagnosis that a refusal means the merge did not land",
     one_line("A refusal here after a successful Step 3 means the merge did not land"), 0, (TASK_DOOR,)),
    ("the blanket retention escape in the report template",
     r"\*\(or why it was retained\)\*", 0, (TASK_DOOR,)),
)


def main() -> int:
    c = Cases("close-out branch delete (SCC-449)")

    if c.block("A · the order: remote first, then local"):
        for name, ok, detail in check_rows(CHECKS_A):
            c.check(name, ok, detail)

    if c.block("B · the refusal ladder: prove it landed, then aim the check at the right ref"):
        for name, ok, detail in check_rows(CHECKS_B):
            c.check(name, ok, detail)

    if c.block("C · Step 6 may not accept its own failure"):
        for name, ok, detail in check_rows(CHECKS_C):
            c.check(name, ok, detail)

        for name, pattern, flags, files in DOOR_BANS:
            rx = re.compile(pattern, flags | re.M)
            for rel in files:
                txt = read(rel)
                # Anti-vacuity FIRST: a deleted door must FAIL its bans, never satisfy them.
                c.check(f"C · {Path(rel).name} has a body for the ban scan", len(txt) > 2000,
                        "" if len(txt) > 2000 else f"{rel} absent or under 2000 chars")
                c.check(f"C · {Path(rel).name}: no {name}",
                        bool(txt) and rx.search(txt) is None,
                        "" if rx.search(txt) is None else f"{rel} still carries {name}")

    if c.block("D · both doors state the mechanism in the SAME words"):
        for name, ok, detail in check_rows(CHECKS_D):
            c.check(name, ok, detail)

        # The half-port guard proper: the sentence must be the SAME sentence, not merely present in
        # each. `/cicd-prune-worktree` has carried it since 2026-08-01; the Task door is the copy.
        rx = re.compile(one_line(MECHANISM))
        found = []
        for rel in DOORS_WITH_MECHANISM:
            m = rx.search(read(rel))
            found.append(" ".join(m.group(0).split()) if m else "")
        c.check("D · both doors carry the mechanism sentence", all(found),
                "" if all(found) else
                f"missing from {[Path(r).name for r, f in zip(DOORS_WITH_MECHANISM, found) if not f]}")
        c.check("D · it is the SAME sentence in both", bool(found[0]) and found[0] == found[1],
                "" if found[0] == found[1] else "the two doors state the mechanism differently")

    if c.block("E · the Task door's byte mirror carries the fix too"):
        m, mir = read(TASK_DOOR), read(TASK_MIRROR)
        c.check("E · master and mirror both have a body", len(m) > 2000 and len(mir) > 2000,
                "" if len(m) > 2000 and len(mir) > 2000 else "master or mirror absent/short")
        c.check("E · the mirror is byte-identical", bool(m) and m == mir,
                "" if m == mir else f"{TASK_MIRROR} has drifted from the master")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
