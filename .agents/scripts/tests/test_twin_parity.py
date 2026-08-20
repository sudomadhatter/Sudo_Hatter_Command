"""SCC-205 · the `cicd-*` <-> `smh-*` twin-parity guard.

⛔ THE GOAL — read this first; it governs every row below, and it must not age into a lie.

The repo carries two command families that are the SAME development system pointed at different
subjects. `.agents/commands/cicd-*.md` does real project work - front end, back end, agent code in
Python, prompting, story lanes, epic branches, sprint boards. `.agents/commands/smh-*.md` is that
same system turned inward on this command centre.

  Operator, 2026-08-17: "they are our same development system, the actual system we use for real
  work on projects. the smh ones are only for working on the system. but they serve the same
  purpose, just optimized for their tasks."

THE STANDARD IS THE SHARED LAW, NOT A FAMILY. Neither prefix owns it. As of 2026-08-17 the law
happened to be more COMPLETE on the smh side for one reason only: that is where the operator was
working while the system was being built.

⛔ THAT IS ABOUT TO INVERT. Operator, 2026-08-17: "we will usually be working with cicd since the
goal is to use the command center for projects. once its working we dont touch SCC that often."
So the next decade of drift runs cicd -> smh, with smh the half left behind. Anyone reading this
later: do NOT infer from "smh was ahead in 2026" that smh is the reference. Measure which half
carries the law, every time. THIS CHECK IS SYMMETRIC PRECISELY BECAUSE THE ANSWER CHANGES.

A difference is a missing-parity DEFECT until proven otherwise. It is legitimate only when the
SUBJECT forces it: the merge target (epic branch vs origin/main) · the spec source (story file +
certification vs implementation_plan.md) · target resolution (cicd binds exactly ONE project and
never this repo) · tooling (this repo has no venv, no ruff, no tsc) · story/board/sprint ceremony.
NOT legitimate: "the fast lane deserves a weaker review" · "that is the other family's way" ·
"BMAD covers it" · anything that is merely older on one side.

WHY THIS FILE EXISTS, in the operator's words: "we made alot of updates to how we want this system
to work and it was all on the smh side before I realized that cicd was not being updated with it."
⭐ The failure was STRUCTURAL, not careless - nothing in the repo compared the two families, so
`workflow_lint --toolkit-only` exited 0 with 172 confirmed drift findings live in the tree. That
zero was the bug. This file is the fix.

── HOW IT WORKS ──────────────────────────────────────────────────────────────────────────────
A command marks a region of SHARED law with a literal fence:

    <!-- twin-law: <id> -->
    ...the law...
    <!-- /twin-law -->

and this file asserts TWO things about every declared pair, not one:

  SYMMETRY  - a law marked in one twin is marked in the other. This is the layer that catches the
              failure that caused the ticket: law written into one family and ABSENT from the
              other. Identity alone sits green through that entire failure, because no counterpart
              region exists to compare.
  IDENTITY  - where both mark it, the regions are byte-identical after whitespace normalisation.

⛔ NEVER WIDEN THIS TO WHOLE FILES. That would force subject-specific law to match and break both
commands. The fence is the scope, and it is deliberately narrow.

The escape hatch is AUDITABLE, not silent: `<!-- twin-divergence: <id> — <reason> -->` in place of
the region declares an intentional asymmetry, and every one is COUNTED and PRINTED, so a deliberate
divergence is a recorded decision rather than a hole.

── WHY NOT test_review_engine.py ─────────────────────────────────────────────────────────────
That file is scoped to the review engine and its callers; the working precedent for this check
lives there (SCC-203, the subagent-law byte-identity block) and this generalises it. But this
check spans six pairs across dev, audit, review and landing - most of which never touch the
engine. It gets its own file, auto-discovered by `run_all.py`.

⛔ NOT the retired `ap_reconciled` stamp re-aimed at these pairs (SCC-209 deleted it anyway): that
mechanism derived the primary from the twin and scanned only the twin's text, so it was
ONE-DIRECTIONAL - the cicd file could drift under a green stamp. Its comparand was whole-file too,
so every commit touching one side's subject-specific text invalidated it, producing reflexive
restamping with nothing read.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases, TempDir

ROOT = Path(__file__).resolve().parents[3]
CMDS = ROOT / ".agents" / "commands"

# ⛔ THE PAIR LIST IS PINNED, and the completeness row below is what stops it going stale.
# Names differ where the SUBJECT differs, which is why this cannot be derived by string
# substitution alone: `cicd-merge-epic-workingtrees` lands story lanes on an epic branch,
# `smh-merge-multiple-workingtrees` lands task lanes on main - same job, different subject,
# different name. `cicd-quick-dev` pairs with `smh-quick-dev`; `smh-quick-fix` is a THIRD
# lane below both and is deliberately unpaired (recorded in NOT_PAIRED).
PAIRS = [
    ("cicd-quick-dev.md", "smh-quick-dev.md"),
    ("cicd-self-audit.md", "smh-self-audit.md"),
    ("cicd-code-review.md", "smh-code-review.md"),
    ("cicd-clean-code-audit.md", "smh-clean-code-audit.md"),
    ("cicd-label-tasks.md", "smh-label-tasks.md"),
    ("cicd-merge-epic-workingtrees.md", "smh-merge-multiple-workingtrees.md"),
    ("cicd-non-crit-pr-push.md", "smh-non-crit-pr-push.md"),
]

# Every `cicd-*` / `smh-*` name-counterpart that is NOT in PAIRS, each with the reason. A new
# counterpart appearing here-less makes the completeness row RED, which is the whole point: the
# next twin someone adds cannot join the tree unpaired and unnoticed.
# ⛔ EVERY `cicd-*` / `smh-*` command is either in PAIRS or recorded HERE with its reason.
# That is what makes the completeness row catch a new twin whose NAMES DIFFER - the shape PAIRS
# itself documents as normal (`cicd-merge-epic-workingtrees` <-> `smh-merge-multiple-workingtrees`)
# and the shape a name-matching deriver is structurally blind to. Measured: with name-matching
# alone, `cicd-zzprobe` + `smh-yyprobe` joined the tree and this row stayed green.
#
# The cost is this list; the benefit is that a NEW command in either family cannot join the tree
# without someone saying which it is. An entry here is a DECISION ("this has no twin, because
# ..."), not a suppression - and it is the reason `NOT_PAIRED` is load-bearing rather than the
# dead set it was, where its one entry could never appear in the derived set anyway.
_ONE_SUBJECT = "single-subject: the other family has no equivalent and should not"
NOT_PAIRED = {
    "smh-quick-fix.md": "a THIRD lane, below both quick-devs - it ejects INTO smh-quick-dev; "
                        "the cicd side has no such lane and that gap is recorded, not faked",
    # ── cicd-only: BMAD story/epic/sprint machinery, deploys, and project-runtime teams ──
    "cicd-write-story-tests.md": _ONE_SUBJECT + " (story ① - there are no stories in the lobby)",
    "cicd-dev-story-tests.md": _ONE_SUBJECT + " (story ② - ditto)",
    # ⛔ NOT `_ONE_SUBJECT`: the smh side DOES have a door, and the two LOOK like a pair
    # until you read where each one lands. A story lands on its EPIC branch - one
    # sanctioned push, main untouched; a Task opens a PULL REQUEST against main and stops
    # for the operator's click. Different target, different law - and today the two bodies
    # share no fenced region at all. Promoting them to PAIRS is a design of its own (fence
    # the preflight, the sign-off and the prune, then hold each identical), and SCC-210
    # deliberately did not do it: it only rebalanced which cicd command owns which step.
    "cicd-close-story-merge-tree.md": "the story DOOR - it lands on the EPIC branch "
                                      "while smh-close-task-merge-tree opens a PR "
                                      "against main, so their bodies share no law "
                                      "fence today; pairing them would mean "
                                      "fence-by-fence law parity (SCC-210)",
    "cicd-update-sprint-memory.md": _ONE_SUBJECT + " (the story SAVE - board flip, "
                                    "learning routing, context budget; no sprint board here)",
    "cicd-create-epic-sprint.md": _ONE_SUBJECT + " (epic kickoff + sprint board)",
    "cicd-boot-sprint-memory.md": _ONE_SUBJECT + " (sprint pick-up)",
    "cicd-prune-worktree.md": _ONE_SUBJECT + " (prunes a story tree; smh prunes in its door)",
    "cicd-push-e2e.md": _ONE_SUBJECT + " (ships an epic to production; the lobby has no deploy)",
    "cicd-e2e.md": _ONE_SUBJECT + " (Firebase-emulator E2E; the lobby has no frontend)",
    "cicd-bdd-tests.md": _ONE_SUBJECT + " (BDD feature suite)",
    "cicd-live-testing-team.md": _ONE_SUBJECT + " (runs the product's servers)",
    "cicd-mobile-error-team.md": _ONE_SUBJECT + " (mobile runtime triage)",
    "cicd-autopilot-claude.md": _ONE_SUBJECT + " (autonomous story loop)",
    "cicd-autopilot-deepseek4.md": _ONE_SUBJECT + " (autopilot, hybrid model lane)",
    "cicd-autopilot-opencode.md": _ONE_SUBJECT + " (autopilot, opencode engine)",
    "cicd-park.md": _ONE_SUBJECT + " (parks a story mid-flight)",
    "cicd-resume.md": _ONE_SUBJECT + " (resumes a parked story)",
    "cicd-prune-context.md": _ONE_SUBJECT + " (trims a long story session)",
    # ── smh-only: the command centre's own doors, board and toolkit plumbing ──
    "smh-close-task-merge-tree.md": "the Task DOOR - it opens a PR against main and stops "
                                    "for the click; the story door above lands on an epic "
                                    "branch, and cicd reaches main only via push-e2e",
    "smh-plan-task.md": _ONE_SUBJECT + " (plans a Task's whole subtask set)",
    "smh-sync-agents.md": _ONE_SUBJECT + " (publishes the toolkit; projects are thin)",
    "smh-update-maps-indexes.md": _ONE_SUBJECT + " (repo maps + INDEX reconciliation)",
    "smh-memory-audit.md": _ONE_SUBJECT + " (audits the shared memory store)",
    "smh-new-project.md": _ONE_SUBJECT + " (scaffolds a new project)",
    "smh-slash-command-updating.md": _ONE_SUBJECT + " (authoring the command surface itself)",
    "smh-adviser-board.md": _ONE_SUBJECT + " (multi-voice advisory board)",
    "smh-review.md": _ONE_SUBJECT + " (ad-hoc read-only review)",
}

# The pairs that carry a fenced shared law TODAY. Three of the seven still carry none - a
# real and defensible starting scope, but it must be STATED: an aggregate "at least one law
# exists" row is green while the unfenced pairs' symmetry rows compare nothing at all.
# SCC-225 review wave: the self-audit pair was rewritten with ZERO fences while parity sat
# green - the structural zero this file's docstring calls "the bug" - so its shared law
# (amendment rule, coverage schema, corroboration, levels shape) is now fenced, and the
# code-review pair's NEW shared law (review_level derivation, declared-set drift) joined
# the roster fence it already carried.
FENCED_TODAY = (
    "cicd-clean-code-audit.md", "smh-clean-code-audit.md",   # twin-law: disposition
    "cicd-code-review.md", "smh-code-review.md",             # twin-law: roster, review-level, declared-drift
    "cicd-self-audit.md", "smh-self-audit.md",               # twin-law: audit-* (amendment, coverage, corroboration, levels-shape)
)

LAW_OPEN = re.compile(r"^<!-- twin-law:\s*([a-z0-9-]+)\s*-->$", re.M)
LAW_CLOSE = "<!-- /twin-law -->"
DIVERGENCE = re.compile(r"^<!-- twin-divergence:\s*([a-z0-9-]+)\s*[-—]+\s*(.+?)\s*-->$", re.M)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def laws(text: str) -> tuple[dict[str, str], list[str]]:
    """Every marked region, keyed by id, whitespace-normalised — plus the MALFORMED ids.

    ⛔ Normalised, never raw: the two families wrap prose at different points for perfectly
    legitimate reasons (one body is wider), and a check that reds on a re-wrap teaches people
    to delete the fence rather than fix the drift.

    Three malformations are refused rather than silently accepted, each measured:

    - **Unclosed.** The search is BOUNDED by the next opening fence. Unbounded, an unclosed
      fence swallows forward to the *next* region's closer, so one typo makes law A absorb
      law B's marker and body — and block C then reports a mismatch attributed to the wrong id.
    - **Duplicate id.** A dict keyed by id lets a second fence OVERWRITE the first. Measured:
      drifting the real region and appending a duplicate carrying the twin's bytes made block
      C pass with genuine drift live in the tree.
    - **Empty.** A well-formed but empty region compares equal to another empty one forever,
      and satisfies a count-based anti-vacuity row. That is the exact shape — identity over
      two empty strings — that the counter-examples exist to prevent.
    """
    out: dict[str, str] = {}
    bad: list[str] = []
    opens = list(LAW_OPEN.finditer(text))
    for n, m in enumerate(opens):
        stop = opens[n + 1].start() if n + 1 < len(opens) else len(text)
        body = text[m.end():stop]
        end = body.find(LAW_CLOSE)
        law_id = m.group(1)
        if end == -1:
            bad.append(f"{law_id} (unclosed before the next fence or EOF)")
            continue
        region = " ".join(body[:end].split())
        if not region:
            bad.append(f"{law_id} (empty region - it would compare equal to any other empty one)")
            continue
        if law_id in out:
            bad.append(f"{law_id} (declared twice - the second would overwrite the first)")
            continue
        out[law_id] = region
    return out, bad


def law_map(text: str) -> dict[str, str]:
    """`laws()` without the malformed list, for the rows that only need the regions."""
    return laws(text)[0]


def divergences(text: str) -> dict[str, str]:
    return {m.group(1): m.group(2) for m in DIVERGENCE.finditer(text)}


def counterparts(root: Path = CMDS) -> set[str]:
    """Every cicd/smh file whose name has a counterpart in the other family.

    Derived from the tree, never from PAIRS - a list that checks itself against itself is a
    list that cannot go stale in the one direction that matters.

    ⛔ Takes a ROOT so the counter-example below can drive it against a fixture. It used to be
    argument-less, and the consequence was measured: E6 could not call it, so E6 asserted set
    arithmetic over two string literals instead - a row that passed for every possible state of
    the tree, including a completeness check gutted to `unpinned = []`.
    """
    cicd = {p.name[len("cicd-"):] for p in root.glob("cicd-*.md")}
    smh = {p.name[len("smh-"):] for p in root.glob("smh-*.md")}
    return {f"cicd-{x}" for x in cicd & smh} | {f"smh-{x}" for x in cicd & smh}


def unpinned_in(root: Path) -> list[str]:
    """A1's PREDICATE, extracted so the counter-example can drive the real thing.

    ⛔ NAME-MATCHING IS NOT ENOUGH, and the file's own PAIRS list proves it: names legitimately
    differ where the subject does (`cicd-merge-epic-workingtrees` <-> `smh-merge-multiple-
    workingtrees`). Deriving only identical stems left the completeness row blind to exactly the
    shape it documents as normal - measured: `cicd-zzprobe`+`smh-yyprobe` joined the tree and A1
    stayed green. So a family member is UNPINNED unless it is pinned, recorded as unpaired, or
    has an identically-named counterpart that is itself pinned.
    """
    pinned = {n for pair in PAIRS for n in pair}
    fam = {p.name for p in root.glob("cicd-*.md")} | {p.name for p in root.glob("smh-*.md")}
    # `-AP` twins are frozen and unpaired by ruling (SCC-209), never a parity subject.
    fam = {n for n in fam if not n.endswith("-AP.md")}
    return sorted(fam - pinned - set(NOT_PAIRED))


def symmetry_orphans(ta: str, tb: str) -> list[str]:
    """Law ids marked in A that B neither marks nor excuses. THE predicate block B uses.

    ⛔ Callers must invoke this BOTH WAYS. Symmetry is the layer that catches one-sided law -
    the failure that caused this ticket - and the operator ruled the drift direction is about
    to invert, so a one-directional check goes blind exactly when it starts to matter.
    """
    la, lb, db = law_map(ta), law_map(tb), divergences(tb)
    return sorted(k for k in la if k not in lb and k not in db)


def identical(ta: str, tb: str, law_id: str) -> bool:
    """Whether both sides carry `law_id` with the same bytes. THE predicate block C uses."""
    la, lb = law_map(ta), law_map(tb)
    return law_id in la and law_id in lb and la[law_id] == lb[law_id]


def main() -> int:
    c = Cases("twin-parity: cicd-* <-> smh- shared law")

    if c.block("A · the pair list is complete (it cannot silently go stale)"):
        # ANTI-VACUITY FIRST. Every row below is a loop over PAIRS, and a loop over an empty
        # or unreadable set passes silently. Assert the inputs exist before asserting on them.
        missing = [n for pair in PAIRS for n in pair if not (CMDS / n).is_file()]
        c.check("A0 every pinned pair file exists on disk (anti-vacuity)",
                bool(PAIRS) and not missing, f"missing={missing}")

        both = sorted({n for pair in PAIRS for n in pair} & set(NOT_PAIRED))
        c.check("A0b no command is BOTH pinned and recorded unpaired (a contradiction)",
                not both, f"in PAIRS and NOT_PAIRED at once: {both}")
        unpinned = unpinned_in(CMDS)
        c.check("A1 every cicd-*/smh-* command is pinned or recorded as unpaired",
                not unpinned,
                "" if not unpinned else
                f"unpinned={unpinned} - add it to PAIRS, or to NOT_PAIRED with the reason")
        found = counterparts()
        c.check("A2 the deriver still works (anti-vacuity)",
                len(found) >= 8, f"{len(found)} same-named counterparts found")

    if c.block("B · SYMMETRY - a law in one twin has a counterpart in the other"):
        seen_any = 0
        for a, b in PAIRS:
            ta, tb = read(CMDS / a), read(CMDS / b)
            la, lb = law_map(ta), law_map(tb)
            da, db = divergences(ta), divergences(tb)
            seen_any += len(la) + len(lb)
            orderings = ((a, b, ta, tb), (b, a, tb, ta))
            # ⛔ BOTH ORDERINGS, PINNED. Dropping the reversed arm makes the guard
            # one-directional, which is the failure this ticket exists to stop AND the one the
            # operator says is about to invert. It survived the sweep because the counter-
            # examples test the predicate, not the loop that drives it.
            c.check(f"B {a} <-> {b} is checked in BOTH directions",
                    {(o[0], o[1]) for o in orderings} == {(a, b), (b, a)},
                    str([(o[0], o[1]) for o in orderings]))
            for side, other, ta2, tb2 in orderings:
                orphans = symmetry_orphans(ta2, tb2)
                c.check(f"B {side} marks no law the twin lacks",
                        not orphans,
                        "" if not orphans else
                        f"{orphans} marked in {side} and absent from {other} - port it, or "
                        f"declare `<!-- twin-divergence: <id> — <reason> -->` in {other}")
        # ⛔ AGGREGATE ANTI-VACUITY HID THE REAL SCOPE. `seen_any > 0` is satisfied by the two
        # fenced pairs while the other four compare {} against {} and print PASS - twelve green
        # rows, eight of them vacuous. So the fenced set is DECLARED, and a pair leaving or
        # joining it has to be a decision rather than a silent drift of coverage.
        fenced = sorted(n for pair in PAIRS for n in pair if law_map(read(CMDS / n)))
        c.check("B* the fenced set is exactly what is declared (scope is a decision)",
                fenced == sorted(FENCED_TODAY),
                f"declared={sorted(FENCED_TODAY)} actual={fenced} - fence the new law on BOTH "
                f"sides and add them here, or remove them if the law moved")

    if c.block("C · IDENTITY - where both mark it, the law is byte-identical"):
        compared = 0
        for a, b in PAIRS:
            la, lb = law_map(read(CMDS / a)), law_map(read(CMDS / b))
            for k in sorted(set(la) & set(lb)):
                compared += 1
                c.check(f"C `{k}` is identical in {a} and {b}",
                        identical(read(CMDS / a), read(CMDS / b), k),
                        "" if la[k] == lb[k] else
                        f"the twins disagree about `{k}`: {a}={len(la[k])}b {b}={len(lb[k])}b "
                        f"- fix ONE and copy it, never edit both by hand")
        c.check("C* the identity rows compared something (anti-vacuity)",
                compared > 0, f"{compared} shared laws compared")

    if c.block("D · every intentional divergence is COUNTED and PRINTED, never silent"):
        rows = [(n, k, why)
                for pair in PAIRS for n in pair
                for k, why in sorted(divergences(read(CMDS / n)).items())]
        for n, k, why in rows:
            print(f"[INFO] twin-divergence · {n} · {k} — {why}")
        c.check("D every divergence carries a reason (an empty one is a hole)",
                all(why.strip() for _, _, why in rows), f"{len(rows)} declared")

    if c.block("E · ⛔ COUNTER-EXAMPLES - a check never seen failing is not a check"):
        # E1/E2 bound the extractor from BOTH sides: perturbing a law must break identity,
        # and law-less text must extract EMPTY. Without E2, an extractor that matched
        # nothing would return {} for both files, compare equal, and pass forever.
        a, b = "cicd-clean-code-audit.md", "smh-clean-code-audit.md"
        la, lb = law_map(read(CMDS / a)), law_map(read(CMDS / b))
        c.check("E0 the fixture pair really does share a law (the setup is not the bug)",
                bool(set(la) & set(lb)), f"{sorted(set(la) & set(lb))}")

        # ⛔ PIN THE ID. `next(iter(set(...)))` picks an ARBITRARY member and string-set order
        # is hash-seed dependent, while the perturbation below is a fixed literal living only
        # in `disposition`. Measured by review: with a second law fenced into this pair, this
        # row went red on 2 runs in 6. A gate that flakes is one people re-run until green.
        k = "disposition"
        drifted = law_map(read(CMDS / a).replace("It's cheap", "It is cheap", 1))
        c.check("E1 perturbing ONE side's law makes identity FAIL",
                k in lb and drifted.get(k) != lb.get(k),
                "" if (k in lb and drifted.get(k) != lb.get(k)) else
                "the perturbation left them equal - the identity check cannot fail")

        c.check("E2 a body with no fence extracts EMPTY (no false match on prose)",
                law_map("# A command\n\nIt does a thing.\n\nThen another.") == {},
                "" if (law_map("# A command\n\nIt does a thing.\n\nThen another.") == {}) else
                "the extractor matches arbitrary prose, so agreement means nothing")

        c.check("E3 an UNCLOSED fence extracts nothing rather than swallowing the file",
                law_map("<!-- twin-law: x -->\nlaw text\n\nmore of the file") == {},
                "" if (law_map("<!-- twin-law: x -->\nlaw text\n\nmore of the file") == {}) else
                "an unterminated marker captured to EOF - one typo would compare whole files")

        # E4: SYMMETRY must fail on the actual disease - law present one side, absent the other.
        gutted = read(CMDS / a).replace("<!-- twin-law: disposition -->", "", 1)
        c.check("E4 deleting one side's fence makes SYMMETRY fail",
                "disposition" in lb and "disposition" not in law_map(gutted),
                "" if ("disposition" in lb and "disposition" not in law_map(gutted)) else
                "removing the marker left the law still extracted - symmetry cannot fail")

        # E5: the divergence hatch must actually silence B, or nobody will use it and the
        # first person who needs one bypasses the gate instead.
        excused = divergences("<!-- twin-divergence: disposition — subject-forced: no venv here -->")
        c.check("E5 a twin-divergence marker parses, with its reason",
                excused.get("disposition", "").startswith("subject-forced"), str(excused))

        # ⛔ E6 DRIVES THE REAL PREDICATE against a fixture tree. The first cut asserted set
        # arithmetic over two string literals, never called the deriver, and never touched the
        # filesystem - so it passed for every possible state of the guard. Measured by review:
        # gutting A1 to `unpinned = []` left E6 green. Under this diff's own
        # `tests-must-gate-for-real` §5, that is a gate that cannot fail.
        with TempDir() as fx:
            for n in ("cicd-clean-code-audit.md", "smh-clean-code-audit.md"):
                (fx / n).write_text("x", encoding="utf-8")   # a PINNED pair: must be silent
            c.check("E6 control: a fixture tree of only PINNED names is clean",
                    unpinned_in(fx) == [], str(unpinned_in(fx)))
            (fx / "cicd-brand-new.md").write_text("x", encoding="utf-8")
            (fx / "smh-brand-new.md").write_text("x", encoding="utf-8")
            c.check("E6 a NEW same-named twin pair is caught",
                    unpinned_in(fx) == ["cicd-brand-new.md", "smh-brand-new.md"],
                    str(unpinned_in(fx)))
            for n in ("cicd-brand-new.md", "smh-brand-new.md"):
                (fx / n).unlink()
            # ⛔ THE SHAPE THE OLD ROW WAS BLIND TO, and the one PAIRS documents as normal.
            (fx / "cicd-zzprobe.md").write_text("x", encoding="utf-8")
            (fx / "smh-yyprobe.md").write_text("x", encoding="utf-8")
            c.check("E6 a new DIFFERENTLY-named twin pair is caught too",
                    unpinned_in(fx) == ["cicd-zzprobe.md", "smh-yyprobe.md"],
                    str(unpinned_in(fx)))
            # ⛔ And a frozen `-AP` twin is NOT a parity subject (SCC-209).
            for n in ("cicd-zzprobe.md", "smh-yyprobe.md"):
                (fx / n).unlink()
            (fx / "cicd-zz-AP.md").write_text("x", encoding="utf-8")
            c.check("E6 a frozen -AP twin is not demanded as a pair",
                    unpinned_in(fx) == [], str(unpinned_in(fx)))

    if c.block("F · ⛔ the GATE's own counter-examples - blocks B and C, not just the extractor"):
        # ⛔ BLOCK E BOUNDS THE EXTRACTOR. It says nothing about whether the SYMMETRY and
        # IDENTITY predicates can fail, and review measured that they could be hard-wired true
        # with the file green: `la[k] == lb[k]` -> `True` survived, and dropping the reversed
        # `(b, a)` arm - making symmetry ONE-DIRECTIONAL - survived too. The shipped guard was
        # not blind (the artifact sweep plants real drift), but a sweep is a one-off script and
        # this file is the gate. These rows put the predicates themselves under test.
        A = "<!-- twin-law: x -->\nthe shared law\n<!-- /twin-law -->\n"
        B = "<!-- twin-law: x -->\nthe shared law\n<!-- /twin-law -->\n"
        c.check("F1 identity: two matching regions agree", identical(A, B, "x"), "")
        c.check("F2 identity FAILS on drifted bytes",
                not identical(A, B.replace("shared", "changed"), "x"),
                "the identity predicate cannot fail")
        c.check("F3 symmetry: matched fences leave no orphan", symmetry_orphans(A, B) == [], "")
        c.check("F4 symmetry FAILS when only side A marks it",
                symmetry_orphans(A, "no fences here") == ["x"], "")
        # ⛔ AND IN THE OTHER DIRECTION. A one-directional check is the exact failure this
        # ticket exists to stop, and the operator ruled the drift direction is INVERTING.
        c.check("F5 symmetry FAILS when only side B marks it (the guard is SYMMETRIC)",
                symmetry_orphans("no fences here", B) == [] and symmetry_orphans(B, "none") == ["x"],
                "the reversed arm is missing - the guard would go blind as drift inverts")
        c.check("F6 an intentional divergence on the other side silences it",
                symmetry_orphans(A, "<!-- twin-divergence: x — subject-forced: no venv -->") == [],
                "the escape hatch does not actually excuse an orphan")
        # ⛔ THE THREE MALFORMATIONS, each measured as a real masking bug before it was refused.
        dup = A + "<!-- twin-law: x -->\nDIFFERENT bytes\n<!-- /twin-law -->\n"
        c.check("F7 a DUPLICATE id is refused, not silently overwritten",
                any("declared twice" in b for b in laws(dup)[1]),
                "a second fence would overwrite the first and mask real drift")
        # ⛔ The markers are LINE-ANCHORED, so the fixture must put them on their own lines -
        # the first draft wrote both on one line, LAW_OPEN never matched, and the row failed
        # for a fixture reason rather than a real one. A red that dies before its assertion.
        hollow = "<!-- twin-law: h -->\n\n<!-- /twin-law -->\n"
        c.check("F8 an EMPTY region is refused (it compares equal to any other empty one)",
                any("empty region" in b for b in laws(hollow)[1])
                and "h" not in law_map(hollow),
                f"an empty fence pair would pass identity and satisfy the count: {laws(hollow)}")
        swallow = ("<!-- twin-law: a -->\nlaw a\n<!-- twin-law: b -->\nlaw b\n<!-- /twin-law -->")
        c.check("F9 an UNCLOSED fence cannot swallow the NEXT region",
                any("unclosed" in b for b in laws(swallow)[1])
                and law_map(swallow).get("b") == "law b",
                f"{law_map(swallow)}")
        # ⛔ AND THE MALFORMED LIST IS REPORTED, not just computed - a refusal nobody prints is
        # a refusal nobody acts on.
        malformed = [(n, b) for pair in PAIRS for n in pair for b in laws(read(CMDS / n))[1]]
        for n, b in malformed:
            print(f"[INFO] malformed twin-law fence · {n} · {b}")
        c.check("F10 the live tree carries no malformed fence", not malformed, str(malformed))
        # ⛔ THE SCOPE ROW'S OWN COUNTER-EXAMPLE. `B*` declares which pairs carry a fenced law;
        # weakening it to a bare truthiness survived the sweep because nothing exercised the
        # comparison it makes. Un-fencing a file must change the computed set.
        unfenced = read(CMDS / "cicd-clean-code-audit.md").replace(
            "<!-- twin-law: disposition -->", "", 1)
        c.check("F11 the fenced-set row is computed, not asserted true",
                bool(law_map(read(CMDS / "cicd-clean-code-audit.md")))
                and not law_map(unfenced),
                "removing a fence left the computed set unchanged - B* proves nothing")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
