# Step 3 — Normalize, dedupe, gate on reproduction, bucket, score

Be precise. When uncertain between two categories, take the more conservative one.

## 1. Normalize into one shape

Every lens emits a different format — adversarial prose, edge-case JSON with `location` /
`trigger_condition` / `guard_snippet` / `potential_consequence`, auditor lists with an acceptance
reference. Best-effort parse anything that does not match its expected shape, and note the parsing
problem rather than dropping the finding.

Each finding becomes:

| field | meaning |
|---|---|
| `id` | sequential integer |
| `source` | `edge` · `acceptance` · `test-adequacy`, or merged (`edge+test-adequacy`) |
| `title` | one line |
| `detail` | the full description, plus any evidence |
| `location` | `file:line` when available |
| `severity` | normalized per §2 |
| `reproduce` | the command the lens ran, from the repo root — required on `critical` / `important` |
| `expected_wrong_output` | what that command prints or does that is wrong — required with it |
| `reproduced` | `yes` + the output the lens actually saw when it ran the command itself |

## 2. Severity — normalize the aliases FIRST

Reviewer models emit whatever vocabulary they like, in whatever case. Fold every one of them into
the four house levels before anything downstream looks at severity:

| House level | Accepts |
|---|---|
| `critical` | critical, high, blocker |
| `important` | important, medium, major |
| `suggestion` | suggestion, minor, low — **and anything unrecognized** |
| `nitpick` | nitpick, info, trivia, trivial |

Case-insensitive. The unrecognized-falls-to-`suggestion` rule is deliberate: an unknown word must
never be *promoted* into something that gates a merge.

The severity a lens wrote is the severity that is used. There is no revised severity any more — the
step-2 wave that produced one is retired (SCC-447), and what makes a severity load-bearing now is
§4's reproduction gate, not a second reader's opinion.

## 3. Deduplicate

Two findings describing the same issue merge into one: keep the most specific as the base (prefer
the one carrying a `location`), fold every unique detail and reference from the others into its
`detail`, and set `source` to the merged sources. Do not merge two findings that share a file but
describe different failures — that hides one of them. Keep the surviving base's `reproduce:` — if
only the folded-away finding carried one, keep that one instead.

## 4. The reproduction gate, then the bucket — exactly one per finding

### 4a. The gate — presence first, and it is not a judgment

Read every `critical` and `important`. It must carry `reproduce:` and `expected_wrong_output:`. Missing either → **drop**, counted.

The same is true of the lens's own run. A lens that did
not run its own command has not met the hunter contract → **drop**, counted. Step 1 tells every lens
to run its command in its own copy and delete the finding when it does not fail as predicted, so a
finding arriving without `reproduced: yes` is a finding its own author did not stand behind.

**This engine cannot run it, by design** — the `allowed-tools` grant in `SKILL.md` includes
no Bash, so nothing here executes. The gate at this step is a **presence** check and nothing more,
and the floor this step scores in §5 is therefore **provisional**.

**The CALLER runs the command again, on the REAL
tree, through `repro_receipt.py`**, and that receipt is what binds. The named reason is SCC-295,
which measured a lens's own copy becoming a mutant of the code being shipped: three of five lenses
edited the builder's working tree mid-review, and one reported a RED result no version of the real
code could produce. A lens proves a defect exists in its own copy; only the caller proves it exists
in shipping code.

A `suggestion` or a `nitpick` is never reproduced and never bucketed. It is a count in the summary
and nothing else — which is the point: the reproduction tax is severity-gated, so the only move it
prices out is inflating a nitpick to be heard.

### 4b. The bucket — one per surviving finding

- **fix** — a reproduced `critical` or `important`. **The caller fixes it in this lane, before its
  verdict**, under `reproduce-before-you-fix` G1–G5: a pin seen red, the minimal fix, then green.
  Pre-existing is not an exemption — a reproduced finding in a file this lane touched is fixed where
  it was found. Two things the caller may meet at fix time are dispositions of the CALLER, not
  buckets of this engine, and `code-standards.md` §6.5 owns both: a fix the agent may not apply
  alone (the constitution's Ask First list, or a spec conflict) is written as a patch beside its
  receipt and `held` for the operator's word; a defect in a file this lane did not touch is
  `out-of-lane` and takes the `work-consolidation` ladder with its receipt.
- **drop** — did not reproduce, arrived without a command, or is noise (false positive, misparse,
  duplicate of handled work). Counted in ONE line in the summary, never written up individually.

**There are two buckets, and there is no third.** Three have been struck, each for putting work in
front of the operator that the review was built to settle itself.

**There is no `decision_needed` bucket any more.** An open decision holds a ticket forever at
`finish`, which is the loop. `jira_feed.py finish` decides `Done` from the open `- [ ]` rows under
`## Your Actions`, so a decision row parked there is a ticket that can never close on its own. What
used to be a decision either reproduces — and is fixed, or held as a written patch when the fix
needs the operator's permission — or it is dropped.

**There is no `escalate` bucket and no `defer` bucket** (operator ruling 2026-09-11). The first
cut of SCC-447 handed a reproduced `important` to the operator with a recommendation and parked a
fix "this lane structurally cannot hold" behind a named blocker; both put a reproduced defect in
front of him to read, and the lenses were made to reproduce precisely so that nobody has to. A
finding that reproduced is fixed. What needs his permission reaches him as a written patch with the
verdict, never as a question; what is outside this lane's files takes the consolidation ladder.

⛔ **A review never produces a ticket.** Not a residue ticket, not a "proposed" ticket, not a
"decided" ticket the operator is asked to rule on, not a ticket-ruling row in `## Your Actions`.
The first cut of this rule (SCC-160, 2026-08-15) allowed "rarely — proposed to the operator as a
decided chore ticket" and its own close-out ended in a `Rule on Ticket A and Ticket B` row; the
operator ruled that the same loop under a new name: "we need the fixes made in thread not a
ticket made every story thats an endless loop that never finishes." A ticket asserts a decision
already made (`jira.md` §Who mints tickets); a review is where the work gets done, not where the
next ticket gets born. **A finding that survives the
gate is fixed in this thread, never a ticket.** The one ticket-shaped exit is a reproduced defect in a
file this lane did not touch, which takes the `work-consolidation` ladder the operator himself ruled
(2026-08-16) — with its receipt, so the next lane starts from a proven bug and a command — and that
is consolidation, not a review minting a ticket.

**The drop count is never omitted.** A review that silently discards what it rejected is a summary
of its own conclusion. Name individually only a finding whose reproduction disagreed with its label,
in either direction — that is the calibration signal.

## 5. Score the severity floor — on the rows that are still OPEN at the stamp

⛔ **This is the change SCC-447 exists for.** The floor used to be computed here, from everything the
lenses returned, and it never moved again — so fixing a finding did not lower it, and
the only road from CONCERNS to PASS was a second full fan-out over the same diff. Across 138 reviews that
road worked one time in seven and cost a full roster every time. The floor this step returns is
therefore **provisional**: the caller resolves it at the stamp, against the rows that are still open
*then*.

| Row still OPEN at the stamp | Effect on `severity_floor` |
|---|---|
| a reproduced `critical` in `fix` that is not yet fixed and pinned — or `held` for the operator's word | **FAIL** |
| a reproduced `important` `held` for the operator's word (Ask First, or a spec conflict), its patch written | **CONCERNS** — authority |
| a reproduced `important` in `fix` that is neither fixed nor held | **CONCERNS** provisionally, at this step — at the stamp it is not a verdict at all: the stamp is refused (`walkthrough_roster.py`, SCC-447 Part 3) and the caller finishes the fix |
| a `suggestion` or `nitpick`, any bucket | **never gates** — recorded, never raising the floor |
| a lens still `dead` after retry AND inline rerun | **CONCERNS** |

The floor is the **most severe** applicable row, on the axis `none` < `CONCERNS` < `FAIL`. A lens
recorded `recovered-inline` is not a dead lens and does not appear here at all. A row closed by a fix and a green pin
does not appear here. The two CONCERNS rows that can stand at the stamp are `code-standards.md` §7's
two grounds — the held row is *authority*, the dead-lens row is *coverage* — and a still-open
`important` is neither: it is unfinished work, and the stamp waits for it.

**CONCERNS is not a stop.** `code-standards.md` §7 is the law: it is a shippable verdict, the
go/no-go is the operator's word, and no command, door or agent may treat it as a blocker on its own
authority. FAIL is the blocker.

## 6. Nothing left

If zero findings survive: report a clean review. If zero survive **and** a lens is `dead`, report
the degradation instead — the review may simply not have looked where the problem is.

## NEXT

Read fully and follow `./step-04-record.md`.
