#!/usr/bin/env python3
"""SCC-212 — the acceptance assertions for the twin-parity CONTENT ports, as one scripted pass.

Every row reads a file through `src()`, so the SAME rows run against the PRE-EDIT blobs
(`--red <ref>`) to prove each one actually failed before the edit. A check never seen red is a
description, not a gate (`tests-must-gate-for-real` Rule 1).

    python3 assert-scc212.py                    # the working tree (expect all PASS at the end)
    python3 assert-scc212.py --red origin/main  # the pre-edit blobs (expect the ports to FAIL)
    python3 assert-scc212.py --case "QD ·"      # one block (the harness filter)

⛔ ONE CASE PER LIVE FINDING, named by its backlog ID, so `mutation_sweep.py` can attribute a
kill to the finding it belongs to. A finding whose case cannot be made to fail at `origin/main`
is not a finding — it is already-settled work, and it belongs in the walkthrough's ledger as
SETTLED instead of here.

⛔ Absence rows (`gone()`) are the ones that need `--red` most: they pass trivially against any
file that never had the text, which is every file that does not exist. `gone()` guards itself
against that one case — an unreadable path makes it FAIL, never pass — and `--red` is what proves
the text was there to begin with.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / ".agents" / "scripts" / "tests"))

from _harness import Cases  # noqa: E402

CMD = ".agents/commands"
DS = f"{CMD}/cicd-dev-story-tests.md"
WS = f"{CMD}/cicd-write-story-tests.md"
ME = f"{CMD}/cicd-merge-epic-workingtrees.md"
SM = f"{CMD}/smh-merge-multiple-workingtrees.md"
QD = f"{CMD}/cicd-quick-dev.md"
SQ = f"{CMD}/smh-quick-dev.md"
CE = f"{CMD}/cicd-create-epic-sprint.md"
CC = f"{CMD}/cicd-clean-code-audit.md"
SC = f"{CMD}/smh-clean-code-audit.md"
CR = f"{CMD}/cicd-code-review.md"
SR = f"{CMD}/smh-code-review.md"
SA = f"{CMD}/cicd-self-audit.md"
GP = ".agents/rules/git-policy.md"
TP = ".agents/scripts/tests/test_twin_parity.py"
CS = ".agents/scripts/tests/test_command_surfaces.py"

REF = ""
_argv = sys.argv[1:]
for _i, _a in enumerate(_argv):
    # ⛔ A LOST VALUE IS A REFUSAL, NEVER A DEFAULT. `--red` with nothing after it, `--red=` or
    # `--red ""` used to leave REF falsy — which is exactly how `src()` spells "read the working
    # tree". The run then measured HEAD, printed `109/109`, and dropped the `[RED @ …]` marker from
    # the banner, so the transcript was byte-identical to a genuine green. A RED pass that silently
    # becomes a green pass is the whole failure mode this file exists to prevent
    # (`_harness._case_filter` took the same scar; do not re-plant it).
    if _a == "--red":
        if _i + 1 >= len(_argv) or not _argv[_i + 1].strip() or _argv[_i + 1].startswith("--"):
            sys.exit("--red needs a ref (e.g. --red origin/main); refusing to measure the "
                     "working tree under a RED flag")
        REF = _argv[_i + 1]
    elif _a.startswith("--red="):
        REF = _a.split("=", 1)[1]
        if not REF.strip():
            sys.exit("--red= needs a ref; refusing to measure the working tree under a RED flag")

_cache: dict[str, str] = {}


def src(path: str) -> str:
    """The file's text — from the working tree, or from `--red <ref>`'s blob."""
    if path in _cache:
        return _cache[path]
    if REF:
        r = subprocess.run(["git", "-C", str(REPO), "show", f"{REF}:{path}"],
                           capture_output=True, text=True, errors="replace")
        text = r.stdout if r.returncode == 0 else ""
    else:
        p = REPO / path
        text = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""
    _cache[path] = text
    return text


def rif(path: str) -> str:
    """The `Rules in force` blockquote ONLY — the same shape `test_command_surfaces.rif_block`
    reads. A rule cited in step prose is NOT loaded (its control pins exactly that), so a
    pointer row that greps the whole file would pass on the shape the house calls broken."""
    out, seen = [], False
    for line in src(path).splitlines():
        if not seen:
            if "Rules in force for this command" in line:
                seen = True
                out.append(line)
            continue
        if line.startswith(">"):
            out.append(line)
        else:
            break
    return "\n".join(out)


def main() -> int:
    c = Cases(f"SCC-212 twin-parity content ports{f' [RED @ {REF}]' if REF else ''}")

    def flat(text: str) -> str:
        """Whitespace-normalised, so a row cannot red on a RE-WRAP.

        ⛔ The same rule `test_twin_parity.laws()` documents: these bodies wrap prose at ~100
        columns, so a sentence that fits on one line today spans two after the next edit. A
        needle-spanning-a-newline row fails for a formatting reason, which is indistinguishable
        in a transcript from the port having been reverted — and it teaches people to delete
        the row rather than fix the drift. Measured here: DEV-05a and DEV-06 both went red on
        their own correctly-applied edits.
        """
        return " ".join(text.split())

    def has(case: str, path: str, needle: str, n: int = 1) -> None:
        got = flat(src(path)).count(flat(needle))
        c.check(f"{case} — {Path(path).name} carries {needle[:52]!r}",
                got >= n, f"found {got}, want >= {n}")

    def gone(case: str, path: str, needle: str) -> None:
        text = src(path)
        c.check(f"{case} — {Path(path).name} no longer carries {needle[:52]!r}",
                bool(text) and flat(needle) not in flat(text),
                "file unreadable" if not text else
                f"still present x{flat(text).count(flat(needle))}")

    def loaded(case: str, path: str, rule: str) -> None:
        c.check(f"{case} — {Path(path).name} LOADS {rule} in its rules-in-force block",
                rule in rif(path), "cite it INSIDE the block, not in step prose")

    # ── 1 · cicd-dev-story-tests (DEV-*) ──────────────────────────────────────────────
    if c.block("DEV · the story lane's dev command"):
        loaded("DEV-16a", DS, "worktree-per-story.md")
        loaded("DEV-16b", DS, "000-PLAN-FIRST-GATE.md")
        loaded("DEV-16c", DS, "artifacts-always-first.md")
        loaded("DEV-16d", DS, "tests-must-gate-for-real.md")
        loaded("DEV-16e", DS, "code-standards.md")
        loaded("DEV-14", DS, "reproduce-before-you-fix.md")
        loaded("DEV-15", DS, "work-consolidation.md")
        has("DEV-01", DS, "Backticks in `-m")
        has("DEV-01-rule", GP, "Backticks in `-m")
        has("DEV-02", DS, "gate_receipt.py run --story")
        has("DEV-03a", DS, "§ Mutation Testing")
        # ⛔ T3: a single generic word is not a pin — `DEFECTIVE` alone survives the sentence
        # being gutted. Key on the DECISION the finding is about, never on its vocabulary.
        has("DEV-03b", DS, "counts as a survivor until re-aimed")
        has("DEV-04a", DS, "review-runtime:")
        has("DEV-04b", DS, "capability, never a policy")
        has("DEV-05a", DS, "WHICH LINE RAISED")
        has("DEV-05b", DS, "RED output")
        has("DEV-06", DS, "A `NO-GO` stops the lane")
        has("DEV-09", DS, "EJECT TRIPWIRE")
        has("DEV-10", DS, "landing-order dependency")
        has("DEV-11", DS, "merge --no-edit origin/epic/")
        has("DEV-12", DS, "link-worktree-assets.py")
        has("DEV-12b", WS, "link-worktree-assets.py")
        has("DEV-17", DS, "Never write an assertion after the edit and present it as a red")
        # ⛔ T2 — both mutation-doctrine bullets were portable and unasserted.
        has("DEV-03c", DS, "the closing green is not the kills")
        has("DEV-03d", DS, "Restore in a `finally`/trap")
        # The rule-side residue of the same law QD-C1 removed from the command (SCC-211).
        gone("QD-C1-rule", GP, "merged back to `main` in the same session")

    # ── 2 · cicd-merge-epic-workingtrees (MERGE-*) ────────────────────────────────────
    if c.block("MERGE · the multi-lane door"):
        has("MERGE-01a", ME, 'git -C "$TREE" merge origin/epic/')
        has("MERGE-01b", ME, "WRONG TREE")
        has("MERGE-02", ME, "modify / delete")
        has("MERGE-03a", ME, "closeout_preflight.py")
        # ⛔ PIN THE FLAG TO THE CALL, not to the file. `--expect-key` is also named in the prose
        # that explains why it is required, so a file-wide row stayed GREEN when the sweep struck
        # it out of the invocation itself (M9 SURVIVED on the first run). The call is what an
        # agent copies; the prose is what it skims.
        has("MERGE-03b", ME, "--expect-key <JIRA-KEY> --branch claude/<JIRA-KEY>-<slug> --worktree")
        has("MERGE-04a", ME, "VOIDS it")
        has("MERGE-04b", ME, "Post-absorb re-measurement")
        has("MERGE-05", ME, "A lane that changes commit or push machinery lands LAST")
        has("MERGE-06", ME, "Verify, THEN report")
        has("MERGE-07a", ME, "rewrite vs edit")
        has("MERGE-07b", ME, "gate or script")
        has("MERGE-07c", ME, "REGENERATING")
        has("MERGE-08a", ME, "jira_feed.py devrecord")
        has("MERGE-08b", ME, "--landing-ref")
        has("MERGE-09", ME, "empty eligible set is a STOP")
        # ⛔ T2 — the `landed` exemption is the one row this step tells you to wave through, so it
        # is the one an agent will over-apply. It was portable and unasserted; both halves are
        # pinned now — the carve-out AND the sentence that stops it swallowing the second error.
        has("MERGE-09b", ME, "it is a ROW, not a section")
        has("MERGE-09c", ME, "Do NOT wave through the whole `landed` section")
        has("MERGE-11", ME, "the case totals must be additive")
        # ⛔ NOT the bare word `BARE` — it already appears at :88 ("BARE `key: status` rows"),
        # so that row was green before the edit. Keyed on the instruction instead.
        has("MERGE-12", ME, "gate BARE")
        has("MERGE-14", ME, "the Step 3 map did not classify")
        has("MERGE-15", ME, "rev-list --count")
        has("MERGE-16", ME, "unmerged branch in another repo")

    # ── 3 · cicd-quick-dev (QD-*) ─────────────────────────────────────────────────────
    if c.block("QD · the project fast lane"):
        has("QD-C1a", QD, "ship_preflight.py")
        gone("QD-C1b", QD, "there is none")
        has("QD-C4a", QD, "Step 0.7 — Probe the review runtime")
        has("QD-C4b", QD, "twin-law: review-runtime-probe")
        has("QD-C7a", QD, 'git -C "$PROJECT_ROOT" fetch origin')
        has("QD-C7b", QD, "branch --unset-upstream")
        has("QD-C8", QD, "landing-order dependency")
        has("QD-C9a", QD, "EXPECTED_KEY")
        has("QD-C9b", QD, "jira_feed.py start --key")
        has("QD-C10", QD, "Backticks in `-m")
        has("QD-C11", QD, "link-worktree-assets.py")
        has("QD-C12", QD, "close_command:")
        has("QD-C14", QD, "smh-close-task-merge-tree Projects/")
        # The pins this lane must NOT break (SCC-226 / SCC-119).
        has("QD-pin1", QD, "RE-ARMS the plan-first gate")
        gone("QD-pin2", QD, "## Declared Change Set")

    # ── 4 · cicd-create-epic-sprint (PAIR-*) ──────────────────────────────────────────
    if c.block("PAIR · the epic kickoff"):
        has("PAIR-01a", CE, "Rules in force for this command")
        loaded("PAIR-01b", CE, "000-PLAN-FIRST-GATE.md")
        loaded("PAIR-01c", CE, "artifacts-always-first.md")
        has("PAIR-02", CE, "are **not** approval")
        has("PAIR-05a", CE, 'git -C "$PROJECT_ROOT" add _bmad-output/planning-artifacts/epics.md')
        has("PAIR-05b", CE, 'git -C "$PROJECT_ROOT" push origin HEAD:epic/')
        has("PAIR-05c", CE, "rev-list --left-right --count")
        has("PAIR-06", CE, "Key the epic and cut its branch")
        has("PAIR-07", CE, 'git -C "$PROJECT_ROOT" checkout -b epic/')
        has("PAIR-08", CE, "acli jira workitem search")
        # The epic-level test-design path the backlog got wrong (verified against workflow.yaml).
        has("PAIR-05d", CE, "test-design-epic-<N>.md")

    # ── 5 · cicd-clean-code-audit (clean-code QD-*) ───────────────────────────────────
    if c.block("CC · the clean-code audit"):
        # ⛔ The predicate must key on the SHAPE, not on a trailing space. `startswith("git diff
        # --name-only ")` reds on a semantically identical line whose comment was removed (false
        # red) and greens on `git diff --name-only origin/main`, which reads a REF and never the
        # worktree (false green). Split the arguments and look at what is actually there.
        def _bare_diff(line: str) -> bool:
            code = line.split("#", 1)[0].strip()
            if not code.startswith("git diff --name-only"):
                return False
            rest = code[len("git diff --name-only"):].split()
            return not rest                       # no ref, no --cached, no paths = the worktree
        c.check("QD-C5 — cicd-clean-code-audit reads UNSTAGED edits too",
                any(_bare_diff(ln) for ln in src(CC).splitlines()),
                "a bare `git diff --name-only` with NO arguments is what sees saved-but-unstaged "
                "work; one carrying a ref reads that ref instead")
        has("QD-C4b-cc", CC, "never fall back to the lobby")
        has("QD-C3-cc", CC, "twin-law: memory-sweep")
        has("QD-C3-sc", SC, "twin-law: memory-sweep")
        # ⛔ Keyed on the SCAN BULLET, never on the phrase: `a gate that cannot fail` also
        # appears in the rules-in-force pointer at :13, which sits above Step 2 already — so a
        # phrase-keyed row was GREEN before the edit and proved nothing (measured, first run).
        _cc, _bullet, _step2 = src(CC), "- **A gate that cannot fail?**", "\n## Step 2"
        c.check("QD-C1/C2-cc — the gate + both-machines scan bullets run on EVERY run "
                "(they sat in Step 2B, which an embedded run skips)",
                all(x in _cc for x in (_bullet, _step2, "- **Does it run on both machines?**"))
                and _cc.find(_bullet) < _cc.find(_step2)
                and _cc.find("- **Does it run on both machines?**") < _cc.find(_step2),
                "both scan bullets must sit ABOVE the `## Step 2` heading")
        has("QD-C2-cc", CC, "Path(__file__)")

    # ── 6 · cicd-code-review + smh-code-review ────────────────────────────────────────
    if c.block("CR · the review command"):
        has("QD-C3-cr", CR, "Step 0.6 — Resolve the diff")
        # ⛔ The HEADING is not the finding. QD-C3 is that uncommitted work is never swept into a
        # review silently — so the row must pin the `status --short` line, not the section that
        # contains it: the sweep deleted the line and the heading-keyed row stayed green
        # (M13 SURVIVED on the first run).
        has("QD-C3-cr-b", CR, 'git -C "$WORKTREE" status --short')
        has("QD-C7-cr", CR, "_artifacts/_memory/")
        has("QD-C6-cr", CR, "re-taken in that worktree")
        has("QD-C5-cr", CR, "cannot fail is a finding")
        has("QD-C4-cr-a", CR, "acceptance matrix from Step 1.5")
        has("QD-C4-cr-b", CR, "twin-law: rederive-record")
        has("QD-C4-sr", SR, "twin-law: rederive-record")
        gone("QD-C1-cr", CR, "--after-merge")
        # ⛔ NOT the bare literal `check-actions` — the FALSE sentence this finding replaces
        # already contains it, so that row was green before the edit. Keyed on the replacement,
        # which names WHICH door enforces it and WHEN (SCC-210/242 made the claim true).
        has("QD-C2-cr", CR, "twice: its Step 2 runs")
        has("QD-C9-sr", SR, "DEFERRED_WORK")
        # ⛔ T2 — the highest-consequence port in the whole lane had NO assertion anywhere. This is
        # the gate-that-cannot-fail class the ticket exists to close: with the STOP deleted, the
        # engine, the acceptance audit and the entire test gate run on an empty set and report a
        # verdict. Pinned at Step 0.6 (where it is derived) AND at Step 3.5 (where it is enforced).
        has("CR-emptydiff-a", CR, "An empty set is a STOP, not a pass")
        has("CR-emptydiff-b", CR, "Step 3.5 restates it at the gate")
        # The Step 0.7 answer list CS-11 pins — proof the F24 edit landed on the right lines.
        # ⛔ NOT the bare word `merge-tree`: it occurs five times as the NAME of a command
        # (`/cicd-close-story-merge-tree`, `/smh-close-task-merge-tree`), so deleting the whole of
        # Step 0.7 left that row PASS. Keyed on the invocation Step 0.7 actually makes — the same
        # call-not-prose rule MERGE-03b and QD-C3-cr were re-aimed for.
        has("CR-pin", CR, 'merge-tree --write-tree --messages HEAD "origin/$EPIC"')

    # ── 7 · cicd-self-audit ───────────────────────────────────────────────────────────
    if c.block("SA · the pre-work audit"):
        has("QD-C2-sa-a", SA, 'git -C "$PROJECT_ROOT" worktree list')
        has("QD-C2-sa-b", SA, "status --short")
        # The EPIC ref, never the trunk (SCC-165) — keyed on the ref shape, not on wrapped prose:
        # a newline-bearing needle reds on a re-wrap, which teaches people to delete the row.
        has("QD-C2-sa-c", SA, "origin/<epic-branch>...HEAD")

    # ── 8 · the guard itself — fences declared, pairs pinned ──────────────────────────
    if c.block("GUARD · fences and the pins that measure them"):
        for law, a, b in (("memory-sweep", CC, SC),
                          ("review-runtime-probe", QD, SQ),
                          ("merge-empty-set-stop", ME, SM),
                          ("merge-machinery-last", ME, SM),
                          ("merge-cross-repo-order", ME, SM),
                          ("rederive-record", CR, SR)):
            open_, close = f"<!-- twin-law: {law} -->", "<!-- /twin-law -->"
            ta, tb = src(a), src(b)
            both = open_ in ta and open_ in tb
            c.check(f"FENCE {law} — marked on BOTH twins", both,
                    f"{Path(a).name}={open_ in ta} {Path(b).name}={open_ in tb}")
            # ⛔ The identity row runs on EVERY path, including the one where the fence is
            # missing. Guarding it with `if both:` made six checks DISAPPEAR under `--red`
            # (103 rows instead of 109) with nothing saying so — and a check that is absent
            # reads in a transcript exactly like a check that passed.
            if both:
                ra = " ".join(ta.split(open_, 1)[1].split(close, 1)[0].split())
                rb = " ".join(tb.split(open_, 1)[1].split(close, 1)[0].split())
                c.check(f"FENCE {law} — byte-identical after whitespace normalisation",
                        bool(ra) and ra == rb, f"cicd={len(ra)}b smh={len(rb)}b")
            else:
                c.check(f"FENCE {law} — byte-identical after whitespace normalisation", False,
                        "not fenced on both twins, so there is nothing to compare - the row is "
                        "RED, never absent")
        # ⛔ Read the FENCED_TODAY TUPLE, not the file: every pair name also appears in `PAIRS`
        # thirty lines above, so a file-wide grep was green before the edit (measured, first run).
        # ⛔ Close on a `)` AT THE START OF A LINE, never the first `)` in the text: the tuple's
        # trailing comments contain parentheses ("audit-* (amendment, coverage, …)"), so a
        # first-paren split truncated the region and reported four false failures against a tuple
        # that was already correct — measured here, with the real gate green beside it.
        _tp = src(TP)
        _ft = (_tp.split("FENCED_TODAY = (", 1)[-1].split("\n)", 1)[0]
               if "FENCED_TODAY = (" in _tp else "")
        for _case, _name in (("FENCED_TODAY-quickdev", "cicd-quick-dev.md"),
                             ("FENCED_TODAY-merge", "cicd-merge-epic-workingtrees.md"),
                             ("FENCED_TODAY-smh-merge", "smh-merge-multiple-workingtrees.md"),
                             ("FENCED_TODAY-smh-quickdev", "smh-quick-dev.md")):
            c.check(f"{_case} — {_name} is declared INSIDE the FENCED_TODAY tuple",
                    f'"{_name}"' in _ft, "B* compares the computed fenced set to this tuple")
        # LOADERS gains the story lane; the :969 scope set must gain it too, or M15's mutant
        # (deleting the rule line from the block) survives — the loop would iterate a set the
        # file is no longer in. Both are asserted.
        # ⛔ Bind BEFORE the predicate, never with a walrus inside a conditional expression's true
        # arm: when the guard is False the name is never bound, and the NEXT row dies with
        # `UnboundLocalError` — which raises out of `main()` instead of printing a `FAILED:` line,
        # so `mutation_sweep.judge` scores the run a SWEEP ERROR rather than a kill. A row that
        # cannot report its own failure is worse than a red one.
        _cs = src(CS)
        _loaders = _cs.split("LOADERS = (", 1)[-1].split("\n)", 1)[0] if "LOADERS = (" in _cs else ""
        c.check("LOADERS-devstory — cicd-dev-story-tests.md is in LOADERS",
                '"cicd-dev-story-tests.md"' in _loaders,
                "the mutation-rule row iterates LOADERS")
        c.check("LOADERS-scope — the LOADERS scope pin covers the story lane too",
                _cs.count('"cicd-dev-story-tests.md"') >= 2,
                "one in LOADERS, one in the <= set(LOADERS) scope pin; with only the first, "
                "removing the file from LOADERS empties the check and M15 survives")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
