# SCC-360 — Zoo fix: harden the Wonderland team

**Status: APPROVED** — operator, 2026-08-31: "Ok this is perfect you understand how to fix the
team, you see the vision. lets add those all to a SCC-360 make this ticket a Zoo fix and have
them all as sub tasks to run on one tree."

## The problem

The Zoo Code team (cheap models in the Wonderland seats) does not defy the machines — it
out-argues the prose. Evidence from the AVCH-101/AVCH-106 audit (2026-08-31): review level
rationalized down to `quick` past the contract-surface clause; full-suite certification skipped
with a plausible-sounding reason; findings dismissed in blanket rulings; a fix recorded as
applied that was never applied; an unrequested ③ run self-stamped `Verdict: PASS` over a red
standing suite. Separately, work kept flowing through Zoo's **stock Ask mode**, which carries no
seat law at all (operator observation). Profiles are for **Models** and cannot fix any of this —
the law lives in the **Modes**, and the mechanical lever is a mode's `groups`, which the
extension enforces regardless of what a model rationalizes.

## The fix — three parts, one tree (`chore/SCC-360-cheshire-cat-rename`)

The Carpenter → Cheshire Cat rename (already landed on this branch) is part 0 of the same
Zoo-fix job.

### Part 1 — The Gnat claims the `ask` slug (read-only LIBRARIAN)

Named for the Looking-Glass Gnat. A sixth seat over Zoo's `ask` slug so no law-free door remains
in the picker. Charter: looking things up — unbiased, fact-driven research backed by facts from
the project; cites file:line evidence; never speculates. **Groups: `[read]` only** — structurally
unable to edit a file or run a command, whatever it talks itself into.

- New master `.agents/commands/smh-team-gnat.md` (mode-slug `ask`, mode-name
  `🦟🔍 The Gnat — LIBRARIAN`, mode-groups `[read]`).
- `sync-agents.ps1` `$seats` table gains the row; header comments updated (six seats, ask claimed).
- `.agents/rules/zoo-team.md`: roster row; the "ask deliberately unclaimed" paragraph replaced
  with the Gnat's charter; triggers gain `gnat`/`librarian`.
- `test_zoo_team.py`: law set gains `ask`; `READONLY_SLUGS` law — the Gnat's groups are exactly
  `{read}`, and a Gnat that grows `edit`/`command` FAILS (mutants prove both directions).
- Generated surfaces regenerated: `.roomodes`, `.roo/rules-ask/01-persona.md`, launcher.

### Part 2 — ③ is the operator's model-switch gate

The dev split the operator chartered: Fable runs `/cicd-create-epic-sprint` and
`/cicd-write-story-tests` (①); the Zoo seats run ② (`/cicd-dev-story-tests` or `/smh-quick-dev`)
**to review-ready and stop**; the operator switches the model and Fable runs `/cicd-code-review`
or `/smh-code-review` (③). The verdict never comes from the seat that built or tested the work.

- `zoo-team.md`: a "③ is the operator's model-switch gate" law paragraph binding every seat.
- Queen of Hearts master rescoped: she keeps the red phase, the testarch doors, mutation/adequacy
  hunting, and pre-review QA prep; the review doors and the `Verdict:` stamp leave her charter.
- March Hare: parks at review-ready; `/smh-code-review` leaves his closing-door list.
- Every seat master gains the refusal: never write a `## Code Review` section or a `Verdict:`
  stamp; review-ready is where the seat stops.
- `test_zoo_team.py` B4 re-pinned to the new charter (red phase + never-weaken + the
  no-verdict refusal; review doors ABSENT).

### Part 3 — the verdict-receipt gate (mechanical)

A `Verdict: PASS|CONCERNS` stamp is only evidence if a real suite ran at that tree. A new
commit-msg gate refuses a commit that ADDS a `Verdict:` line to any `walkthrough.md` unless a
fresh `suite` gate receipt (per `gate_receipt.py`, result pass/warn, same tree) is present for
that lane. Logged opt-out token in the message, mirroring `[sop-ok]`. Lobby repo only on this
ticket — arming the same gate in AGY is cross-repo work and takes an AVCH ticket
(`cross-repo-work-needs-a-ticket-per-repo`).

- `.agents/scripts/verdict_receipt.py` + `.agents/scripts/git-hooks/verdict-receipt.sh`,
  dispatched from `.githooks/commit-msg`, armed by a `VERDICT-ENFORCE` marker file.
- Tests in `.agents/scripts/tests/` (mutants first: a forged stamp with no receipt REFUSED, a
  stamped verdict with a fresh receipt allowed, opt-out logged path allowed).

## Done means

`test_zoo_team.py` green with the new law; `run_all.py` fully green; surfaces regenerated and
current; SOP page + changelog updated in the same commits; all three subtasks ride this branch
(`riders:` in task.yaml) and flip at the parent's close ceremony.
