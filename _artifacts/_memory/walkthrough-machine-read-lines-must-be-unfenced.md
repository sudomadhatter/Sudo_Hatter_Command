---
name: walkthrough-machine-read-lines-must-be-unfenced
description: The walkthrough's `lenses_run:` roster and its `Verdict: … @ <sha>` stamp are parsed as PLAIN markdown — put either inside a ``` fence and the gate reads it as absent, silently and with a misleading message.
metadata:
  type: project
---

Measured twice in one close-out (SCC-355, 2026-08-31). Both machine-read lines in `walkthrough.md`
were written inside code fences, which reads naturally and breaks both gates:

- `walkthrough_roster.py --gate` returned `lenses_counted: 0`, `runtime: null` — it names the
  fence in its error, but only once rows exist to complain about.
- `task_preflight.py` reported *"verdict stamp(s) exist only in 1 walkthrough(s) whose task.yaml
  does not declare SCC-355 — foreign evidence never gates this lane"*, which reads as a
  **task.yaml/ownership** problem and is actually *"your stamp is in a fence so I cannot see it."*
  It silently withheld the suite SKIP as a result.

**Why:** these are stamps, not code samples. The parsers walk plain lines (`_ROSTER_ROW_RE` wants
`- <lens> · <state>` bullets; the verdict wants a bare `Verdict: … @ <sha>` line), and a fence is
skipped wholesale so the file looks like it never carried one.

**How to apply:** write them unfenced — `review-runtime:` on its own line, `lenses_run:` followed
by `- <lens> · <state>` **bullets**, `lenses_na: <lens> · n/a - <reason>` (a bare `n/a` with no
reason is REFUSED), then `dispositions:` and `drift:` each on ONE line (a wrapped line truncates at
the break), and `Verdict: <RESULT> @ <sha>` bare. Then run
`walkthrough_roster.py <walkthrough> --gate --verdict <RESULT>` and read the **exit code** before
opening the PR — it is the only thing that proves the close-out can read what you wrote. Related:
[[story-artifacts-live-in-the-tree]], [[closeout-target-is-a-machine-contract]].
