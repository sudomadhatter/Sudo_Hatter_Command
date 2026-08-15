"""task_preflight's VERDICT + RECEIPT gate — the SCC-146/SCC-154 half.

Split from `test_task_preflight.py` (SCC-156), which was the slowest file in `run_all` and so
set the floor for the whole parallel suite. The seam is the one the code already had: every
case here drives `check_gate()` — the walkthrough's `Verdict:` line, which walkthroughs
GOVERN, which stamp wins, and when a `gate: SKIP` is allowed to replace the printed plan —
and nothing here is reachable from the lane/shape half.

Real git repositories in temp dirs, with a real bare `origin`, and real `gate_receipt.py`
subprocesses: the questions are ancestry, freshness and file-content questions, and a mocked
git would only prove the mock agrees with itself.
"""
from __future__ import annotations

import json
import sys


from _harness import Cases, TempDir, run_script
from _pf_fixtures import (ADIR, MANIFEST, WALKTHROUGH, branch, commit, git,
                          make_repo, preflight, stamp_and_verdict, write)


def main() -> int:
    c = Cases("task_preflight — verdict + receipts")
    # ── SCC-146: the close-out reads the review VERDICT and the gate RECEIPTS ────────────
    if c.block("SCC-146: the close-out reads the review VERDICT and the gate REC"):
        # check_artifacts only ever proved a walkthrough EXISTS. The review's canonical
        # `Verdict: ... @ <sha>` line was never read, so a FAIL review did not block the merge,
        # and a PASS could not spare the lane its fourth identical suite run. The contract:
        #   FAIL                                       -> exit 2, the merge is refused
        #   PASS/CONCERNS + code-fresh + receipts valid + clean -> `gate: SKIP` prints
        #   code moved / dirty tree / no receipt        -> the gate commands print, as today
        # "code-fresh" deliberately means `git diff <verdict-sha>..HEAD` touches nothing
        # outside `_artifacts/` — /smh-code-review Step 3's own rule ("artifact- and doc-only
        # commits after that run do not invalidate it; code or test changes do") made
        # mechanical, and the only reading under which a lane can ever reach ONE suite run
        # end-to-end: the verdict always lands as a docs commit AFTER the sha it cites
        # (SCC-149 review, compound finding C4 — observed live, twice).


        with TempDir() as t:   # the ALLOW half (acceptance 4)
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = stamp_and_verdict(repo, "PASS")
            code, out = preflight(repo)
            c.check("SCC-146 PASS + code-fresh + receipt + clean -> gate: SKIP, exit 0",
                    code == 0 and "gate: SKIP" in out and "receipts valid" in out,
                    f"exit {code}: " + out.strip()[-400:])
            c.check("SCC-146 the SKIP names the verdict and its sha",
                    f"PASS @ {sha[:8]}" in out, out.strip()[-300:])
            # The fixture itself pins the C4 deviation: HEAD is the artifacts commit, NOT the
            # verdict sha, and the SKIP must survive that — else no real lane can ever SKIP.
            c.check("SCC-146 artifacts-only commits since the verdict do not invalidate it",
                    git(repo, "rev-parse", "HEAD").stdout.strip() != sha,
                    "fixture must move HEAD past the verdict sha")

        with TempDir() as t:   # acceptance 5a — code moved since the verdict
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "PASS")
            write(repo, "docs/x.md", "changed after the verdict\n")
            commit(repo, "SCC-11 chore: code moved after the verdict")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-146 code moved since the verdict -> commands print, never SKIP",
                    code == 0 and "gate: SKIP" not in out and "run_all.py" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # acceptance 5b — dirty tree
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "PASS")
            write(repo, "docs/x.md", "uncommitted\n")
            code, out = preflight(repo)
            c.check("SCC-146 a dirty tree never SKIPs (sync blocks AND the commands print)",
                    code == 2 and "gate: SKIP" not in out and "run_all.py" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # acceptance 5c — no receipt
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "PASS", receipt=False)
            code, out = preflight(repo)
            c.check("SCC-146 verdict PASS but NO receipt -> commands print (fail toward running)",
                    code == 0 and "gate: SKIP" not in out and "run_all.py" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # a STALE verdict must not ride a FRESH receipt (M4's killer)
            # The real shape: review stamps the verdict, then "one more fix" commit lands, the
            # suite is re-run and re-stamped mechanically — receipt fresh, verdict stale. The
            # verdict-freshness check is the ONLY thing standing between that lane and a SKIP
            # citing evidence about code that no longer exists; the first sweep proved the
            # receipt check alone cannot see it (receipt sha == verdict sha in every fixture
            # above, so mutant M4 survived at 115/115).
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "PASS", receipt=False)     # verdict cites sha W
            write(repo, "docs/x.md", "the one-more-fix commit\n")
            commit(repo, "SCC-11 chore: code moved after the verdict")
            run_script("gate_receipt.py", "run", "--task", "SCC-11",   # re-stamped at C: FRESH
                       "--gate", "suite", "--root", str(repo / ADIR), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            commit(repo, "SCC-11 chore: receipt re-stamped (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-146 a STALE verdict cannot ride a FRESH receipt - verdict freshness "
                    "is checked independently",
                    code == 0 and "gate: SKIP" not in out and "code moved since the verdict" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # receipts exist, but none of them is the SUITE run
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "lint",
                       "--root", str(repo / ADIR), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            stamp_and_verdict(repo, "PASS", receipt=False)   # lint receipt only, no `suite`
            code, out = preflight(repo)
            c.check("SCC-146 receipts WITHOUT a `suite` receipt never SKIP - the one that "
                    "matters must have run",
                    code == 0 and "gate: SKIP" not in out and "run_all.py" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # the REJECT half (acceptance 6)
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "FAIL")
            code, out = preflight(repo)
            c.check("SCC-146 a FAIL verdict BLOCKS the merge (exit 2), and says why",
                    code == 2 and "FAIL" in out, f"exit {code}: " + out.strip()[-300:])

    # ── SCC-154 A0 · conjunct killers, landed BEFORE any check_gate change (C2/C3) ────────
    if c.block("SCC-154 A0 · conjunct killers, landed BEFORE any check_gate chan"):
        # Characterization-green by design and declared as such: each pins a branch of check_gate
        # that the SCC-146 review measured as deletable with the suite staying green (finding 7),
        # plus the allow-half gaps it listed (finding 17). ⛔ Deliberately NO pin of multi-stamp
        # semantics here — pinning today's any(FAIL) would cement defect #1 (verifier id 33); the
        # multi-stamp cases land WITH the resolution change below.

        with TempDir() as t:   # A0-a · a receipt whose result is FAIL never SKIPs
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "suite",
                       "--root", str(repo / ADIR), "--cwd", str(repo), "--allow-fail",
                       "--", sys.executable, "-c", "import sys; sys.exit(1)")
            stamp_and_verdict(repo, "PASS", receipt=False)
            code, out = preflight(repo)
            c.check("SCC-154 a FAILING receipt never SKIPs (bad-existing-receipt conjunct)",
                    code == 0 and "gate: SKIP" not in out and "result=fail" in out
                    and "run_all.py" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # A0-b · a receipt stamped over NON-artifacts dirt never SKIPs
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            write(repo, "docs/dirt.txt", "uncommitted while stamping\n")     # NON-artifacts dirt
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "suite",
                       "--root", str(repo / ADIR), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            # the dirt lands BEFORE the verdict so the DIRTY conjunct is the only refusing one —
            # committing it beside the walkthrough would trip code-fresh instead (wrong-reason pass)
            commit(repo, "SCC-11 chore: the dirt lands")
            stamp_and_verdict(repo, "PASS", receipt=False)
            code, out = preflight(repo)
            c.check("SCC-154 a receipt stamped over NON-artifacts dirt never SKIPs",
                    code == 0 and "gate: SKIP" not in out and "DIRTY" in out
                    and "run_all.py" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # A0-c · an unreadable receipt never SKIPs
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            write(repo, f"{ADIR}/gates/suite.json", "{not json")
            stamp_and_verdict(repo, "PASS", receipt=False)
            code, out = preflight(repo)
            c.check("SCC-154 an UNREADABLE receipt never SKIPs",
                    code == 0 and "gate: SKIP" not in out and "unreadable" in out
                    and "run_all.py" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # A0-d · verdict FRESH, receipt STALE — M4's mirror
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "suite",
                       "--root", str(repo / ADIR), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            commit(repo, "SCC-11 chore: receipt stamped (artifacts only)")
            write(repo, "docs/x.md", "code moved AFTER the receipt\n")
            commit(repo, "SCC-11 chore: the one-more-fix commit")
            stamp_and_verdict(repo, "PASS", receipt=False)     # verdict cites the post-move sha
            code, out = preflight(repo)
            c.check("SCC-154 a FRESH verdict cannot ride a STALE receipt (M4's mirror)",
                    code == 0 and "gate: SKIP" not in out and "stamped at" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # A0-e · an unknown verdict sha is never fail-open
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review (2026-08-08)\n\nVerdict: PASS @ {'c' * 40}\n")
            commit(repo, "SCC-11 chore: walkthrough (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 an UNKNOWN verdict sha warns and the full gate runs (never fail-open)",
                    code != 2 and "gate: SKIP" not in out and "cannot verify" in out
                    and "run_all.py" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # A0-f/g · the allow-half: CONCERNS skips, WAIVED stands the plan
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = stamp_and_verdict(repo, "CONCERNS")
            code, out = preflight(repo)
            c.check("SCC-154 CONCERNS is the allow-half: SKIP with valid receipts",
                    code == 0 and "gate: SKIP" in out and f"CONCERNS @ {sha[:8]}" in out,
                    f"exit {code}: " + out.strip()[-300:])
        with TempDir() as t:
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "WAIVED")
            code, out = preflight(repo)
            c.check("SCC-154 WAIVED never SKIPs - the printed gate plan stands",
                    code == 0 and "gate: SKIP" not in out and "WAIVED" in out
                    and "run_all.py" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # A0-h · the --json gate field carries the SKIP
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            stamp_and_verdict(repo, "PASS")
            code, out = preflight(repo, "--json")
            try:
                gate = (json.loads(out).get("gate") or [])
            except ValueError:
                gate = []
            c.check("SCC-154 --json carries the SKIP in its gate field",
                    code == 0 and bool(gate) and gate[0].startswith("SKIP"),
                    f"exit {code}: gate={str(gate)[:200]}")

    # ── SCC-154 A1 · verdict RESOLUTION: the governing pool and the latest stamp ──────────
    if c.block("SCC-154 A1 · verdict RESOLUTION: the governing pool and the late"):
        # The review proved the pool wrong live: THIS system's own SCC-146 close-out saw 2 hits,
        # one of them a foreign lane's walkthrough carrying its own PASS stamp (findings 1/2/3).

        with TempDir() as t:   # FAIL-then-PASS — the re-reviewed lane must un-wedge
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "suite",
                       "--root", str(repo / ADIR), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: FAIL @ {sha}\n"
                  + f"\n## Code Review (re-run)\n\nVerdict: PASS @ {sha}\n")
            commit(repo, "SCC-11 chore: walkthrough + receipts (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 FAIL-then-PASS: the re-review's LATEST stamp governs (un-wedges)",
                    code == 0 and "gate: SKIP" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # PASS-then-FAIL — the other direction still blocks
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {sha}\n"
                  + f"\n## Code Review (re-run)\n\nVerdict: FAIL @ {sha}\n")
            commit(repo, "SCC-11 chore: walkthrough (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 PASS-then-FAIL: the latest stamp blocks (exit 2)",
                    code == 2 and "FAIL" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # a FOREIGN stamped walkthrough can never GRANT a skip
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            fdir = "_artifacts/_main/2026-08-08_scc-99-other"
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            # receipt FIRST, on the clean tree — a receipt stamped beside uncommitted files records
            # DIRTY and today's dirty conjunct would refuse the SKIP before the governing-pool hole
            # this case exists to expose ever gets asked (the wrong-reason-pass trap)
            run_script("gate_receipt.py", "run", "--task", "SCC-99", "--gate", "suite",
                       "--root", str(repo / fdir), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            write(repo, f"{fdir}/task.yaml", MANIFEST.replace("SCC-11", "SCC-99"))
            write(repo, f"{fdir}/walkthrough.md",
                  "# another lane\n\nmentions SCC-11 in passing\n\n"
                  f"## Code Review\n\nVerdict: PASS @ {sha}\n")
            commit(repo, "SCC-11 chore: a foreign lane's artifacts (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 a FOREIGN stamped walkthrough (task.yaml elsewhere) never grants SKIP",
                    code == 0 and "gate: SKIP" not in out and "run_all.py" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # ...and a FOREIGN FAIL never BLOCKS this lane either
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            fdir = "_artifacts/_main/2026-08-08_scc-99-other"
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            write(repo, f"{fdir}/task.yaml", MANIFEST.replace("SCC-11", "SCC-99"))
            write(repo, f"{fdir}/walkthrough.md",
                  "# another lane\n\nmentions SCC-11 in passing\n\n"
                  f"## Code Review\n\nVerdict: FAIL @ {sha}\n")
            commit(repo, "SCC-11 chore: a foreign lane's artifacts (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 a FOREIGN FAIL never blocks this lane (foreign evidence gates nothing)",
                    code != 2, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # substring pooling: SCC-1 on SCC-11's evidence (SCC-14 ⊂ SCC-146)
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-1-thing", {"docs/x.md": "x\n"})
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "suite",
                       "--root", str(repo / ADIR), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {sha}\n")
            commit(repo, "SCC-1 chore: the sibling's artifacts (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-1-thing")
            code, out = preflight(repo, expect="SCC-1")
            c.check("SCC-154 substring pooling: SCC-1 never SKIPs on SCC-11's stamped evidence",
                    code != 2 and "gate: SKIP" not in out and "run_all.py" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # TWO stamped walkthroughs under one key: ambiguous, no SKIP
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            d2 = "_artifacts/_main/2026-08-09_scc-11-more"
            # stamps land one committed tree at a time (the SCC-146 lane's own live lesson) — a
            # second stamp beside the first's untracked receipt records DIRTY and hides the
            # ambiguity hole this case exists to expose
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "suite",
                       "--root", str(repo / ADIR), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            commit(repo, "SCC-11 chore: first receipt (artifacts only)")
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "suite",
                       "--root", str(repo / d2), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            commit(repo, "SCC-11 chore: second receipt (artifacts only)")
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {sha}\n")
            write(repo, f"{d2}/task.yaml", MANIFEST)
            write(repo, f"{d2}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {sha}\n")
            commit(repo, "SCC-11 chore: two stamped walkthroughs (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 two stamped walkthroughs under one key: ambiguous, no SKIP",
                    code == 0 and "gate: SKIP" not in out and "run_all.py" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # a NEAR-MISS stamp is an error, never a silent demotion
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\n**Verdict: FAIL @ {sha}**\n")
            commit(repo, "SCC-11 chore: walkthrough (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 a bolded FAIL stamp is an ERROR, never a demotion to a clean run",
                    code == 2 and "does not parse" in out, f"exit {code}: " + out.strip()[-300:])

        # ── SCC-154 review fixes: the FAIL block outranks ambiguity, settled lanes step aside,
        # fences close by kind+length, and the near-miss class stops false-redding evidence ──────

        with TempDir() as t:   # R1 · a governing latest-FAIL blocks EVEN under ambiguity
            # The review's convergent finding (three lenses + compound): the len>1 info-return sat
            # ABOVE the FAIL branch, so a typo'd FAIL blocked harder than a canonical one.
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            d2 = "_artifacts/_main/2026-08-09_scc-11-more"
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: FAIL @ {sha}\n")
            write(repo, f"{d2}/task.yaml", MANIFEST)
            write(repo, f"{d2}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {sha}\n")
            commit(repo, "SCC-11 chore: two stamped walkthroughs, one FAIL (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 a governing latest-FAIL blocks even when a second stamped "
                    "walkthrough makes the SKIP ambiguous",
                    code == 2 and "FAIL" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # R2 · a LANDED lane's dir is history: it neither governs nor
            # counts as ambiguity (same manifest_settled rule check_manifest already applies).
            # The landed dir lives ON MAIN (declaring its own, pruned branch); THIS lane's
            # manifest is authored on the branch, the way quick-dev actually writes it.
            repo = make_repo(t, walkthrough=False, manifest=False)
            d0 = "_artifacts/_main/2026-08-01_scc-11-landed"
            base = git(repo, "rev-parse", "HEAD").stdout.strip()
            write(repo, f"{d0}/task.yaml", MANIFEST.replace("chore/SCC-11-thing",
                                                            "chore/SCC-11-old"))
            write(repo, f"{d0}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {base}\n")
            commit(repo, "SCC-11 chore: a landed lane's artifacts on main")
            git(repo, "push", "-q", "origin", "main")
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n",
                                                f"{ADIR}/task.yaml": MANIFEST})
            stamp_and_verdict(repo, "PASS")
            code, out = preflight(repo)
            c.check("SCC-154 a landed lane's stamped dir does not wedge the follow-on "
                    "(settled = history, not ambiguity)",
                    code == 0 and "gate: SKIP" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # R3/R4 · fences close by KIND and LENGTH: wrapped inner fences
            # never leak a pasted stamp into the scan (verified live by the review: the shipped
            # toggle flipped on any marker, so a quoted FAIL after the real PASS became governing)
            for label, fence_open, fence_close in (("4-backtick", "````", "````"),
                                                   ("tilde", "~~~", "~~~")):
                repo_dir = t / f"repo-{label}"
                repo_dir.mkdir()
                repo = make_repo(repo_dir, walkthrough=False)
                branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
                sha = stamp_and_verdict(repo, "PASS", commit_docs=False)
                write(repo, f"{ADIR}/walkthrough.md",
                      WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {sha}\n"
                      + f"\nevidence paste (markdown containing its own fence):\n\n"
                      + f"{fence_open}\n```\nVerdict: FAIL @ {sha}\n```\n{fence_close}\n")
                commit(repo, "SCC-11 chore: walkthrough + receipts (artifacts only)")
                git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
                code, out = preflight(repo)
                c.check(f"SCC-154 a {label}-wrapped inner fence never leaks its stamp "
                        f"(the real PASS still SKIPs)",
                        code == 0 and "gate: SKIP" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # R5 · the UNCLOSED fence drops the tail — pinned as the declared
            # design (fail toward running: no verdict -> the full gate runs, no err either way)
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + "\nan unclosed evidence fence:\n\n```\n"
                  + f"Verdict: FAIL @ {sha}\n")
            commit(repo, "SCC-11 chore: walkthrough (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 an UNCLOSED fence drops the tail: full gate, no block, no SKIP",
                    code == 0 and "gate: SKIP" not in out and "run_all.py" in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # R6 · an INDENTED canonical stamp is evidence, not a near-miss
            # (the review's false-red: \s in the prefix class exit-2'd correct evidence content)
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = stamp_and_verdict(repo, "PASS", commit_docs=False)
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {sha}\n"
                  + f"\nprior review, quoted as an indented code block:\n\n"
                  + f"    Verdict: PASS @ {sha}\n")
            commit(repo, "SCC-11 chore: walkthrough + receipts (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 an INDENTED quoted stamp never false-reds (the real PASS SKIPs)",
                    code == 0 and "gate: SKIP" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # R7/R8 · the detector's WIDTH: lowercase and heading shapes err
            for label, stamp_line in (("lowercase", "verdict: fail @ {sha}"),
                                      ("heading", "## Verdict: FAIL @ {sha}")):
                repo_dir = t / f"repo-{label}"
                repo_dir.mkdir()
                repo = make_repo(repo_dir, walkthrough=False)
                branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
                sha = git(repo, "rev-parse", "HEAD").stdout.strip()
                write(repo, f"{ADIR}/walkthrough.md",
                      WALKTHROUGH + "\n## Code Review\n\n" + stamp_line.format(sha=sha) + "\n")
                commit(repo, "SCC-11 chore: walkthrough (artifacts only)")
                git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
                code, out = preflight(repo)
                c.check(f"SCC-154 a {label} FAIL stamp is an ERROR (detector width)",
                        code == 2 and "does not parse" in out,
                        f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # R9 · a canonical PASS beside a malformed FAIL still blocks
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = stamp_and_verdict(repo, "PASS", commit_docs=False)
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {sha}\n"
                  + f"\n**Verdict: FAIL @ {sha}**\n")
            commit(repo, "SCC-11 chore: walkthrough + receipts (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 a canonical PASS cannot ride past a malformed FAIL beside it",
                    code == 2 and "does not parse" in out and "gate: SKIP" not in out,
                    f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # R10 · PASS-then-WAIVED: the latest stamp governs there too
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = stamp_and_verdict(repo, "PASS", commit_docs=False)
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + f"\n## Code Review\n\nVerdict: PASS @ {sha}\n"
                  + f"\n## Code Review (re-run)\n\nVerdict: WAIVED @ {sha}\n")
            commit(repo, "SCC-11 chore: walkthrough + receipts (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 PASS-then-WAIVED: WAIVED governs, the plan stands (no SKIP)",
                    code == 0 and "gate: SKIP" not in out and "WAIVED" in out
                    and "run_all.py" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # R11 · a WARN receipt is SKIP-eligible (the pass-or-warn width)
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "suite",
                       "--warn-exit", "1", "--root", str(repo / ADIR), "--cwd", str(repo),
                       "--", sys.executable, "-c", "import sys; sys.exit(1)")
            stamp_and_verdict(repo, "PASS", receipt=False)
            code, out = preflight(repo)
            c.check("SCC-154 a WARN receipt (advisory findings) is SKIP-eligible",
                    code == 0 and "gate: SKIP" in out, f"exit {code}: " + out.strip()[-300:])

        with TempDir() as t:   # a FENCED canonical stamp is evidence, not a verdict
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            sha = git(repo, "rev-parse", "HEAD").stdout.strip()
            write(repo, f"{ADIR}/walkthrough.md",
                  WALKTHROUGH + "\nevidence paste:\n\n```\n"
                  + f"Verdict: FAIL @ {sha}\n```\n")
            commit(repo, "SCC-11 chore: walkthrough (artifacts only)")
            git(repo, "push", "-q", "origin", "chore/SCC-11-thing")
            code, out = preflight(repo)
            c.check("SCC-154 a FENCED stamp is evidence, not a verdict (no block, full gate runs)",
                    code == 0 and "gate: SKIP" not in out and "run_all.py" in out,
                    f"exit {code}: " + out.strip()[-300:])

    # ── SCC-154 A2 · a SKIP spares the SUITE only (C4) ────────────────────────────────────
    if c.block("SCC-154 A2 · a SKIP spares the SUITE only (C4)"):
        with TempDir() as t:
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing",
                   {"docs/x.md": "x\n",
                    ".agents/scripts/workflow_lint.py": "# fixture\n",
                    ".agents/scripts/check_maps.py": "# fixture\n"})
            stamp_and_verdict(repo, "PASS")
            code, out = preflight(repo)
            c.check("SCC-154 SKIP spares the SUITE only - artifact-scoped checks still print",
                    code == 0 and "gate: SKIP" in out
                    and "check_maps.py --depth3-only --strict" in out
                    and "workflow_lint.py" in out and "run_all.py" not in out,
                    f"exit {code}: " + out.strip()[-400:])

    # ── SCC-154 A4 · reader-side dirt exemption (C6): artifacts-only dirt may still SKIP ──
    if c.block("SCC-154 A4 · reader-side dirt exemption (C6): artifacts-only dir"):
        with TempDir() as t:
            repo = make_repo(t, walkthrough=False)
            branch(repo, "chore/SCC-11-thing", {"docs/x.md": "x\n"})
            write(repo, "_artifacts/_main/notes.md", "another session's scratch\n")
            run_script("gate_receipt.py", "run", "--task", "SCC-11", "--gate", "suite",
                       "--root", str(repo / ADIR), "--cwd", str(repo),
                       "--", sys.executable, "-c", "print('ok')")
            stamp_and_verdict(repo, "PASS", receipt=False)     # commits the scratch too
            code, out = preflight(repo)
            c.check("SCC-154 a receipt whose only dirt was _artifacts/ may still SKIP "
                    "(the recorder stays strict; the READER exempts)",
                    code == 0 and "gate: SKIP" in out, f"exit {code}: " + out.strip()[-300:])

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
