# SCC-334 — the adviser-board cast gate is five lines, and stage rooms seat by judgment

**Ticket:** SCC-334 (subtask of SCC-318) · **Branch:** `chore/SCC-334-adviser-board-gate-five-rooms`
**Change class:** prompt prose only — no scripts, no tests, no runtime behaviour.

## What shipped

- **The debate gate is five lines, not seven.** The two stage rooms — 🔧 Execution Reality and
  📣 Sales — are normally cast at Step 7, so writing a gate line for them during the debate was a
  constant wearing a judgment's formatting. Either one seats on the debate gate **by the
  orchestrator's read** when the topic *is* its subject: a question about what actually gets built,
  or one that opens as an offer. No enumerated trigger list; if seated, its line looks like any other.
- **Seated rooms print first** with triad and named axes; **every cut room collapses onto one
  combined line** with a short reason naming what goes unexamined. The separate `Cost of the cut:`
  clause is deleted — the example SCC-333 shipped had obeyed it in one room out of five, and a reason
  worth printing already names the cost.
- **Step 7 defines its own stage gate.** It used to say "the same cast gate" — pointing at a gate
  that no longer covers the rooms Step 7 casts.
- **`TEAMS.md`** header and Execution Reality's charter now say the same thing the command does —
  the old charter clause banned the room from the debate absolutely, which made an execution-shaped
  topic unable to seat its own owner.
- **SOP** adviser-board subsection rewritten in timeless present (habit 4); its change story moved to
  the changelog, including a backfilled row for SCC-333, which had never filed one.

## Why this branch was reset

The first pass (10 commits, old tip `433fab4a`, recoverable from reflog) built a 39-check test file
and a 14-mutant sweep around this prompt. The operator rejected that instrument: a command file is
read by an LLM exercising discretion, and hard rules — word caps, charter-language matching,
enumerated exceptions — are the wrong tool for it. The branch was reset to `origin/main` and the
surviving prose re-shipped as one commit. The lane mis-routing that caused it (everything under
`.agents/commands/` answers TASK, which runs assert-first even when the diff is prose) is filed
separately.

## Gates

Suite `run_all.py`, `workflow_lint.py --toolkit-only`, `check_links.py --base origin/main` — results
in the commit's verification note. The one known red, `test_allow_scratchpad.py` case E
(`os.getuid`, POSIX-only), reproduces identically on `origin/main` and is the pre-existing
portability instance SCC-321 tracks.
