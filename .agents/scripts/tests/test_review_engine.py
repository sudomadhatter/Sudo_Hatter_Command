"""The house review engine (SCC-116) — the contract its step files must hold.

`bmad-code-review` is a VENDOR skill: BMAD regenerates it, `customize.toml` only appends, and its
step-04 flips a story to `done` and writes the sprint board — two things this system's law reserves
for the human close-out, plus a third disagreement about where findings live. Containment today is
an adapter rule that has to win an attention contest against the vendor's own instructions on every
single run. `.agents/skills/code-review-engine/` ends that contest by owning the engine outright.

Why this file is the only guard: `workflow_lint.py` checks commands, rules, doors and INDEX rows —
it has NO skill checks at all. Nothing else on this surface is mechanical.

  ── WHY THIS FILE IS SHAPED THE WAY IT IS (SCC-122 review, finding C-1) ─────────────────────
The first version of this test was a keyword grep, and the review broke it in one move: five
stub files, keyword-stuffed, instructing the exact OPPOSITE of every rule the engine exists to
enforce — "skip Blind Hunter", "do not retry", "flip the story to Done and merge" — scored a
clean 80/80. A guard that passes the negation of its own subject is not a guard.

The repair has three parts, and each answers a specific way a source-grep goes blind:

  1. **Checks bind a RELATIONSHIP, not a vocabulary.** `critical` and `FAIL` both appearing
     somewhere in a file proves nothing; `^| `critical`, in ... | **FAIL** |` proves the mapping,
     because a table row is where the meaning lives. Line anchors and adjacency do the work that
     `in text` cannot.
  2. **Every check ships a COUNTER-EXAMPLE and is proven to reject it.** For each rule there is a
     one-substring mutation stating the opposite; the test applies it in memory and requires the
     check to go red. A check that survives its own counter-example is reported as a failure here,
     which makes this file self-proving instead of self-asserting. (The counter must also actually
     apply — a mutation whose target string is absent would make the proof vacuous, so that is
     asserted too.)
  3. **The prohibitions are asserted POSITIVELY.** Banning behavior words does not work in a file
     whose job is to forbid them: "it never merges" contains "merges". So step-04's boundary is
     held by requiring its five bullets verbatim — a stub that says "flip the story to Done and
     merge" cannot simultaneously carry "It never advances a story's state". The identifier bans
     below remain, aimed at the vendor's spellings, and they scan every markdown file in the
     engine (not a hard-coded list) so a new step file cannot smuggle one in.

The negative controls keep their original anti-vacuity design, which the review confirmed sound:
each proves the file EXISTS and is non-empty BEFORE asserting a token is absent, so a missing step
file fails the control instead of satisfying it.

  ── WHAT SCC-447 REMOVED, and why the count halved ──────────────────────────────────────────
This file carried **264 CHECKS rows and now carries 116.** The 148 that went were not weakened;
their subjects were retired. All 78 step-02 rows went with the verify wave (it refuted 2 findings
in 18 reviews), and 70 more with the Blind Hunter, the Literal-Correctness Hunter, the
`EVIDENCE_PACK` priming, the `lens_budget` cost axis, the two `review_level` levels and the
`decision_needed` / `patch` / `dismiss` buckets. A check whose subject no longer exists is not
coverage — it is a row that can never fail, which is exactly what §2 above exists to catch.

⛔ **Where that coverage went, so this is auditable rather than asserted.** The engine's NEW
contract — the three-layer reproduction gate, the four buckets, the provisional floor — is pinned
in `test_review_disposition.py`, which holds 51 engine rows under the same counter-example
discipline. The roster's own invariants stayed in `test_lens_roster_contract.py`, and step-04's
record vocabulary in `test_finding_record.py`. What is deliberately kept HERE is the part none of
those own: vendor containment (the identifier bans), the caller wiring pinned in the callers' own
files, the `.claude/skills/` cache parity, and the rubrics that outlived the roster change. Three
rows were rewritten rather than dropped, each noted at its site, because no sibling covered them.

Stdlib only, no pytest — same constraint as every sibling here.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import walkthrough_roster as roster  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
MASTER = ROOT / ".agents" / "skills" / "code-review-engine"
CACHE = ROOT / ".claude" / "skills" / "code-review-engine"

SKILL = "SKILL.md"
STEPS = ("steps/step-01-review.md", "steps/step-02-verify.md",
         "steps/step-03-triage.md", "steps/step-04-record.md")
ENGINE_FILES = (SKILL,) + STEPS

# The engine's callers are NOT engine files — they are resolved from ROOT, they are exempt from the
# vendor-identifier ban scan (a caller may legitimately still name things the engine may not), and
# they are not part of the `.claude/skills/` cache comparison. But they must be pinned HERE, because
# a rule about a caller that lives only in the engine's own step file is a rule nothing enforces:
# reverting the caller leaves every engine check green while the wiring is gone (SCC-126 review, F7).
# The two INTERACTIVE callers (SCC-147). step-01 defines `lens_budget` and states that a caller
# naming none gets `capped` — the safe default, chosen for the unwatched overnight loop. That
# default is the WRONG budget for a review a human is sitting in front of, and neither of these
# named one, so both silently ran the autopilot's budget and the literal lens lost the top-up it
# is supposed to be able to earn. Pinned in the CALLERS' own bodies for the F7 reason above: the
# rule lived only in step-01, which is a claim about a caller, not a check on one.
CICD_CMD = ".agents/commands/cicd-code-review.md"
SMH_CMD = ".agents/commands/smh-code-review.md"
# ⛔ The THIRD carrier of the probe law. `test_twin_parity.py:117` lists this file as
# having no twin, so nothing else in the suite reaches it — delete its `blocked:`
# clause and every gate stayed green (SCC-263 review, Acceptance Auditor).
DEV_STORY_CMD = ".agents/commands/cicd-dev-story-tests.md"
# SCC-205 made the FAST lane a caller; SCC-444 took it back out. `/cicd-quick-dev` is now the quick
# lane (git-policy § Two toggles): a review runs ONLY when the operator asks, and when he asks it is
# `/cicd-code-review` - already a caller here - not a gate inside the door. The door no longer
# names the engine, so the completeness row below (the caller set is derived from the tree) would
# red on a stale pin. A quick lane with no review writes `Review: none - quick lane; …` and no
# `Verdict:`, which is what keeps `walkthrough_roster.py` out of a lane that ran no lenses.
CALLER_FILES = (CICD_CMD, SMH_CMD)

# Vendor identifiers that must appear NOWHERE in the engine. `HALT` is deliberately the only
# case-SENSITIVE one: lower-case "halt" is ordinary English and banning it generates false reds.
BANNED = (
    ("new_status", r"new_status", re.I),
    ("development_status", r"development_status", re.I),
    ("sprint board file", r"sprint[-_]status", re.I),
    ("HALT marker", r"\bHALT\b", 0),
    ("customization resolver", r"resolve_customization", re.I),
    ("speech-style variable", r"communication_language", re.I),
    ("vendor review skill", r"bmad-code-review", re.I),
)

# (id, file, regex, flags, counter_old, counter_new)
# counter_old MUST be present in the real file and counter_new MUST break the regex.
CHECKS: tuple[tuple[str, str, str, int, str, str], ...] = (
    # ── SKILL.md: the caller contract, the standalone guard, the severity axis ──────────────
    ("skill: tool grant excludes Bash and Edit", SKILL,
     r"^allowed-tools: Read, Write, Glob, Grep, Task$", re.M,
     "allowed-tools: Read, Write, Glob, Grep, Task",
     "allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task"),
    ("skill: menu invocation is refused", SKILL,
     r"were not supplied by a\ncalling command, you were invoked from a menu", re.M,
     "were not supplied by a", "are missing, so resolve them yourself from"),
    ("skill: menu invocation returns without running", SKILL,
     r"\*\*return without reading the step files\.\*\*", 0,
     "return without reading the step files", "carry on into the step files"),
    ("skill: REPO is a required input row", SKILL,
     r"^\|\s*`REPO`\s*\|[^|]*\|\s*yes\s*\|", re.M,
     "| `REPO` | absolute path to the repository root | yes |",
     "| `REPO` | derived from the working directory | no |"),
    ("skill: WORKTREE is a required input row", SKILL,
     r"^\|\s*`WORKTREE`\s*\|[^|]*\|\s*yes\s*\|", re.M,
     "| `WORKTREE` | absolute path to the tree the diff came from (may equal `REPO`) | yes |",
     "| `WORKTREE` | guess it | no |"),
    ("skill: DIFF is a required input row", SKILL,
     r"^\|\s*`DIFF`\s*\|[^|]*\|\s*yes\s*\|", re.M,
     "| `DIFF` | the diff text, or a path to it — already scoped by the caller | yes |",
     "| `DIFF` | run git yourself | no |"),
    ("skill: HEAD_SHA is a required input row", SKILL,
     r"^\|\s*`HEAD_SHA`\s*\|[^|]*\|\s*yes\s*\|", re.M,
     "| `HEAD_SHA` | the sha the diff was taken at, for the record the caller writes | yes |",
     "| `HEAD_SHA` | resolve it yourself | no |"),
    ("skill: review_mode row names both modes and is required", SKILL,
     r"^\|\s*`review_mode`\s*\|[^|]*`full`[^|]*`no-spec`[^|]*\|\s*yes\s*\|", re.M,
     "| `review_mode` | `full` (a spec exists) or `no-spec` (none) | yes |",
     "| `review_mode` | pick one | no |"),
    ("skill: a missing input stops the engine", SKILL,
     r"\*\*A missing required input is a stop, not a guess\.\*\*", 0,
     "is a stop, not a guess", "may be inferred from the working directory"),
    ("skill: never re-derives a resolved input", SKILL,
     r"never re-derive an input the caller already resolved", 0,
     "never re-derive an input", "always re-derive an input"),
    ("skill: an absent optional input is never invented", SKILL,
     r"the engine does \*\*not\*\* invent a path", 0,
     "does **not** invent a path", "invents a path"),
    ("skill: severity axis is stated once, ascending", SKILL,
     r"severity order is `none` < `CONCERNS` < `FAIL`", 0,
     "`none` < `CONCERNS` < `FAIL`", "`FAIL` < `CONCERNS` < `none`"),
    # ⛔ This row USED to be `^lenses_run:\s+<n>/<applicable>` — a prose pin asserting the file
    # contained a shape. It is replaced (SCC-177 step 9) by the round-trip in § 5 below, which feeds
    # the contract's own fixture through the real parser. What stays here is the COUNT, which moved
    # to its own line when the roster became a block: a count is a summary and the rows are the
    # evidence, and the two must not share a line again.
    # ⛔ The RAISE half of the severity axis, re-pinned after SCC-447 made the floor
    # provisional. `test_review_disposition.py` holds the SOFTEN half (exactly two evidence-backed
    # ways down, and any other downgrade refused); this row holds the half that never changed —
    # a caller's own gates may always add severity the lenses never saw. (Named "raise", not
    # "escalate": the finding-level `escalate` bucket was struck 2026-09-11 and this is unrelated.)
    ("skill: caller may raise severity, never soften", SKILL,
     r"The caller may report\nanything MORE severe", 0,
     "anything MORE severe", "anything LESS severe"),
    # ⛔ POSITIVE assertion, per this file's own §3: a stub cannot simultaneously carry the
    # boundary bullets and the behaviour they forbid. The heading's first bullet is the anchor,
    # and SCC-447 made it the no-Bash one — the boundary the whole reproduction contract rests on.
    ("skill: the never-do list is a prohibition, and it opens with the no-execution boundary", SKILL,
     r"## What the engine does NOT do, ever\n[\s\S]{0,200}?"
     r"^- \*\*It never runs a command\.\*\*[\s\S]{0,600}?It never issues the `Verdict:` line", re.M,
     "## What the engine does NOT do, ever",
     "## What the engine also does when convenient"),
    ("skill: the applicable count is its own line, beside the roster", SKILL,
     r"^lenses_counted:\s+<n>/<applicable>", re.M,
     "lenses_counted:  <n>/<applicable>", "lenses_counted:  <n>/<total>"),
    # ⛔ The two files state the spec-less count independently, so they can drift apart; this row
    # is what makes them disagree LOUDLY. SCC-447 moved it from 4/4 to 2/2 when the roster went
    # from five lenses to three, and `test_lens_roster_contract.py` pins step-01's own half.
    ("skill: the spec-less count agrees with step-01 (2/2)", SKILL,
     r"reports `2/2`, never `2/3`", 0,
     "reports `2/2`, never `2/3`", "reports `2/3`, never `2/2`"),
    ("skill: review_runtime is a caller-resolved input", SKILL,
     r"^\|\s*`review_runtime`\s*\|[^|]*`fan-out`[^|]*`inline`[^|]*\|", re.M,
     "| `review_runtime` | `fan-out` or `inline`", "| `review_runtime` | whatever the engine finds"),
    ("skill: the roster is evidence, not a summary of itself", SKILL,
     r"`lenses_run:` is a BLOCK, and its rows are the evidence", 0,
     "its rows are the evidence", "its count is the evidence"),

    # ── step-01: `review_runtime` is READ, and `inline` runs the ladder exactly once ─────────
    ("step-01: review_runtime is read before any lens launches", STEPS[0],
     r"passes the answer down as\n`review_runtime: fan-out \| inline`\.\s*\*\*Read it before you launch anything\.\*\*", re.M,
     "Read it before you launch anything", "Infer it from whether the first lens returns"),
    ("step-01: inline runs the ladder ONCE", STEPS[0],
     r"^\|\s*`inline`\s*\|\s*\*\*the ladder runs ONCE\*\*", re.M,
     "| `inline` | **the ladder runs ONCE**", "| `inline` | try the fan-out first, then"),
    ("step-01: inline never re-attempts the fan-out", STEPS[0],
     r"never attempt the fan-out first[^\n]*\n?[^\n]*never re-attempt it after", 0,
     "never attempt the fan-out first", "always attempt the fan-out first"),
    # ── SCC-203 · under `inline` the blind lens is DROPPED, never faked ─────────────────────
    #
    # ⛔ THE DEFECT, MEASURED ON THE LANE THAT ADDED THIS. `/smh-code-review` Step 0.9 tells the
    # agent to probe whether the runtime can fan out, and the probe conflated two different
    # things: a CAPABILITY (does a subagent tool exist?) and a POLICY (is the agent permitted to
    # use it right now?). A session directive saying "Do not call the AgentTool unless the user requested it" was
    # read as "this runtime is inline", the whole review ran in the BUILDER'S OWN CONTEXT, and
    # the flow recorded that as a legitimate outcome. The operator caught it by reading the chat.
    # Nothing in the system would have.
    #
    # ⭐ THE OPERATOR'S RULING, 2026-08-17: "subagents as the default, and when they're genuinely
    # unavailable, drop the blind lens rather than fake it. Running it inline and counting it in
    # the roster is the worst of the three - it costs tokens and produces a record that says the
    # review was more independent than it was."
    #
    # The Blind Hunter's ENTIRE value is not knowing what the builder knows. Run inline in the
    # builder's context it has already read the plan, the walkthrough and the reasoning, so it can
    # only confirm what the builder already believes: real tokens, zero independent signal. And it
    # is the ONLY lens that needs this - Edge-Case and Literal-Correctness get repo access on
    # purpose, the Acceptance Auditor needs the spec, Test-Adequacy needs the test files. Being
    # informed is their design, which is why isolating all five was always the slow way round.
    # ⛔ ANCHORED ON THE PROSE, NOT THE QUOTE. The first cut pinned the bare phrase "more
    # independent than it was", which now appears TWICE - in the operator's quoted ruling and in
    # the rule's own closing sentence. `replace(old, new, 1)` mutated only the first, the second
    # still matched, and the check survived its own counter-example. The harness caught it.
    # ── SCC-203 · the caller distinguishes CAPABILITY from PERMISSION ───────────────────────
    ("smh: the runtime probe asks about capability, not permission", SMH_CMD,
     r"\*\*capability\*\*[^\n]*\n?[^\n]*never a \*\*policy\*\*", re.M | re.I,
     "never a **policy**", "and also a **policy**"),
    ("smh: invoking the command IS the request for subagents", SMH_CMD,
     r"a `/` command IS a user request", 0,
     "a `/` command IS a user request",
     "the operator must ask for subagents themselves"),
    # ⛔ THE TWIN CARRIES IT TOO. `sudo-commands-have-ap-twins-that-drift`: fix one, diff the
    # twin. The operator caught this omission the first time round - the smh caller was fixed
    # and the cicd one was not, which is how the two lanes end up reviewing to different law.
    ("cicd: the runtime probe asks about capability, not permission", CICD_CMD,
     r"\*\*capability\*\*[^\n]*\n?[^\n]*never a \*\*policy\*\*", re.M | re.I,
     "never a **policy**", "and also a **policy**"),
    ("cicd: invoking the command IS the request for subagents", CICD_CMD,
     r"a `/` command IS a user request", 0,
     "a `/` command IS a user request",
     "the operator must ask for subagents themselves"),
    ("dev-story-tests: invoking the command IS the request for subagents", DEV_STORY_CMD,
     r"a `/` command IS a user request", 0,
     "a `/` command IS a user request",
     "the operator must ask for subagents themselves"),
    ("dev-story-tests: a blocked inline must NAME what blocked it", DEV_STORY_CMD,
     r"inline \(blocked:", 0,
     "inline (blocked:", "a bare inline is fine"),
    ("smh: a blocked inline must NAME what blocked it", SMH_CMD,
     r"inline \(blocked:", 0,
     "inline (blocked:", "a bare inline is fine"),
    ("cicd: a blocked inline must NAME what blocked it", CICD_CMD,
     r"inline \(blocked:", 0,
     "inline (blocked:", "a bare inline is fine"),
    ("step-01: under inline, `ok` is not a legal per-lens state", STEPS[0],
     r"`recovered-inline` for every lens that RAN — `ok` is not a legal state here", 0,
     "`ok` is not a legal state here", "`ok` is fine here too"),
    ("step-01: the blind lens may run concurrently with the receipt, at ONE sha", STEPS[0],
     r"the sha the lenses ran against and the sha on the receipt must be the same value", 0,
     "must be the same value", "may differ by a commit or two"),

    # ── step-01: the fan-out table, the failure contract, NA-vs-dead ────────────────────────
    # SCC-232 made the routing cells level-aware. Each cell is pinned to the CURRENT truth
    # with the OBSOLETE flat-rate "always" as its mutant - the asymmetric pinning that steered
    # maintainers back toward "always" (executed, SCC-225 review wave) is retired with it.
    # SCC-301: a Tree cell sits between Gets and the routing cell, so the row regexes
    # allow exactly TWO cells there - one cell would miss every row now that the table
    # carries six columns, and an unbounded [^|]*-chain would stop anchoring WHICH cell
    # holds the routing text.
    ("step-01: Acceptance Auditor is a lens row gated to full mode", STEPS[0],
     r"^\|\s*\*\*Acceptance Auditor\*\*\s*\|(?:[^|]*\|){2}\s*`review_mode: full` only\s*\|", re.M,
     "| **Acceptance Auditor** | `DIFF` + `STORY_FILE`", "| ~~Acceptance Auditor~~ | dropped,"),
    ("step-01: Test-Adequacy Auditor is a lens row that always runs", STEPS[0],
     r"^\|\s*\*\*Test-Adequacy Auditor\*\*\s*\|(?:[^|]*\|){2}\s*always\s*\|", re.M,
     "| **Test-Adequacy Auditor** | `DIFF` + read access", "| ~~Test-Adequacy Auditor~~ | the QA gate covers it,"),
    ("step-01: a failed lens is retried once", STEPS[0],
     r"^1\. \*\*Retry it once\.\*\*", re.M,
     "1. **Retry it once.**", "1. **Do not retry it.**"),
    ("step-01: a still-failing lens is rerun inline", STEPS[0],
     r"run that lens INLINE yourself, here, in this context", 0,
     "run that lens INLINE yourself", "drop that lens and carry on"),
    # Counter-example must name the retry+inline clause: bare "raises the floor" also occurs in
    # the zero-findings-is-not-dead paragraph above, and `.replace(old, new, 1)` would mutate that
    # one instead — leaving this check unable to fail (SCC-126 review, same class as F12).
    ("step-01: only a still-dead lens raises the floor", STEPS[0],
     r"^4\. \*\*Only a lens that is still dead after BOTH the retry and the inline rerun raises",
     re.M, "the inline rerun raises the floor", "the inline rerun leaves the floor alone"),
    ("step-01: a dead lens raises the floor to CONCERNS", STEPS[0],
     r"^\|\s*died, and the inline rerun also failed\s*\|\s*`dead`\s*\|\s*\*\*raises `severity_floor` to CONCERNS\*\*",
     re.M, "**raises `severity_floor` to CONCERNS**", "**no effect**"),
    ("step-01: a lens recovered inline costs no coverage", STEPS[0],
     r"^\|\s*died, then produced findings when rerun inline\s*\|\s*`recovered-inline`\s*\|\s*\*\*none",
     re.M, "| **none — coverage is complete** |", "| **CONCERNS** |"),
    ("step-01: a mode-skipped lens is not a failure and not counted", STEPS[0],
     r"Record it on `lenses_na`, \*\*not\*\* as a failure, and \*\*not\*\* inside", 0,
     "**not** as a failure, and **not** inside", "as a failure, and inside"),
    ("step-01: a mode-skipped lens never raises the floor", STEPS[0],
     r"^- \*\*A lens skipped by mode never raises `severity_floor`\.\*\*", re.M,
     "never raises `severity_floor`", "also raises `severity_floor`"),
    # Five lenses since SCC-126, and only the Acceptance Auditor is mode-skipped — so the
    # spec-less count is 4/4. The arithmetic is pinned in BOTH files that state it.

    # ── step-01 (SCC-125): the ROUTING that makes the asymmetry real ────────────────────────
    # These bind the `How` cells and the assembly convention, not the prose that describes them.
    # The review of this task proved why: with only the prose pinned, four mutations that told the
    # orchestrator to give every lens both blocks — including deleting the hunter contract from
    # the Edge Case Hunter's wiring — all scored a clean 323/323. A guard on the description of a
    # rule is not a guard on the rule.
    ("step-01: the Edge Case Hunter's row wires in the hunter contract", STEPS[0],
     r"^\|\s*\*\*Edge Case Hunter\*\*\s*\|(?:[^|]*\|){3}[^|]*\+ the hunter contract\s*\|", re.M,
     "the `bmad-review-edge-case-hunter` skill + the hunter contract",
     "the `bmad-review-edge-case-hunter` skill alone"),
    ("step-01: the Acceptance Auditor's row wires in the auditor rubric", STEPS[0],
     r"^\|\s*\*\*Acceptance Auditor\*\*\s*\|(?:[^|]*\|){3}\s*the auditor rubric\s*\|", re.M,
     "| **Acceptance Auditor** | `DIFF` + `STORY_FILE` + any context docs | own worktree copy (`isolation: \"worktree\"`) | `review_mode: full` only | the auditor rubric |",
     "| **Acceptance Auditor** | `DIFF` + `STORY_FILE` + any context docs | own worktree copy (`isolation: \"worktree\"`) | `review_mode: full` only | the hunter contract |"),
    ("step-01: the Test-Adequacy Auditor's row wires in the auditor rubric", STEPS[0],
     r"^\|\s*\*\*Test-Adequacy Auditor\*\*\s*\|(?:[^|]*\|){3}\s*the auditor rubric\s*\|", re.M,
     "| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | own worktree copy (`isolation: \"worktree\"`) | always | the auditor rubric |",
     "| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | own worktree copy (`isolation: \"worktree\"`) | always | the hunter contract |"),
    ("step-01: no lens is given the other role's block", STEPS[0],
     r"every lens gets the block it names, and no lens gets the other's", 0,
     "every lens gets the block it names, and no lens gets the other's",
     "every lens gets both blocks; there is no asymmetry"),
    ("step-01: the How cell is the wiring, not decoration", STEPS[0],
     r"the `How` cell is the wiring and is not optional", 0,
     "the `How` cell is the wiring and is not optional",
     "the `How` cell is a description"),
    ("step-01: blockquoted text is what reaches the lens", STEPS[0],
     r"\*\*Blockquoted text \(`>`\) is appended to the lens's prompt verbatim\.", 0,
     "Blockquoted text (`>`) is appended to the lens's prompt verbatim.",
     "Paraphrase the sections below into each prompt."),
    ("step-01: unquoted text is orchestrator instruction, never sent", STEPS[0],
     r"is never sent to a lens", 0,
     "is never sent to a lens", "is also sent to the lens"),

    # ── step-01 (SCC-125): the vendor-skill collisions are resolved, not left to the model ──
    ("step-01: the contract outranks a vendor skill it is stacked on", STEPS[0],
     r"^## When this contract and a vendor skill disagree, the contract wins$", re.M,
     "## When this contract and a vendor skill disagree, the contract wins",
     "## Vendor skills take precedence over this contract"),
    ("step-01: an unresolved collision is called out as randomness", STEPS[0],
     r"an unresolved collision is resolved by the model at random", 0,
     "an unresolved collision is resolved by the model at random",
     "an unresolved collision is harmless"),
    ("step-01: zero findings is valid and never padded to a count", STEPS[0],
     r"Zero findings is a valid, reportable result", 0,
     "Zero findings is a valid, reportable result",
     "Always reach the required finding count"),
    ("step-01: a fixed vendor output shape still carries severity and the chain", STEPS[0],
     r"Carry the severity, the confidence and the evidence chain INSIDE its free-text field", 0,
     "Carry the severity, the confidence and the evidence chain INSIDE its free-text field",
     "Drop the severity, the confidence and the evidence chain"),
    ("step-01: a severity label is a classification, not an opinion", STEPS[0],
     r"A severity label is a required classification, not an opinion", 0,
     "A severity label is a required classification, not an opinion",
     "A severity label is an opinion and may be omitted"),
    ("step-01: an unlabelled finding is read as suggestion and never gates", STEPS[0],
     r"an unlabelled\n> `critical` is a `critical` you threw away", re.M,
     "an unlabelled", "a labelled"),

    # ── step-01 (SCC-125): the shared rubric reaches BOTH contracts ─────────────────────────
    ("step-01: the shared rubric is appended to both contracts", STEPS[0],
     r"^## The shared rubric — appended to BOTH contracts$", re.M,
     "## The shared rubric — appended to BOTH contracts",
     "## The shared rubric — part of the hunter contract"),
    ("step-01: severity and author-intent bind every lens, hunter and auditor", STEPS[0],
     r"Append this section to every\nlens, hunter and auditor alike", re.M,
     "Append this section to every", "Append this section to every hunter and no other"),

    # ── step-01 (SCC-125): the hunter contract — the three false-positive gates ─────────────
    ("step-01: the hunter contract binds hunter lenses, now and later", STEPS[0],
     r"^## The hunter contract — binding on every hunter lens, now and later$", re.M,
     "binding on every hunter lens, now and later",
     "binding on every lens, auditors included"),
    ("step-01: the contract is routed by the How cell, not to every lens", STEPS[0],
     r"^Append to the prompt of every lens whose `How` cell names this contract", re.M,
     "Append to the prompt of every lens whose `How` cell names this contract",
     "Append to the prompt of EVERY lens, auditors included"),
    ("step-01: the auditor rubric reaches the lens as prompt text, not commentary", STEPS[0],
     r"^> \*\*You are exempt from Gate 1 \(reachability proof\) and Gate 3", re.M,
     "> **You are exempt from Gate 1 (reachability proof) and Gate 3",
     "> **You must pass Gate 1 (reachability proof) and Gate 3"),
    ("step-01: the auditor prompt carries the recall-first rule itself", STEPS[0],
     r"^> \*\*Report recall-first\.\*\*", re.M,
     "> **Report recall-first.**", "> **Report precision-first.**"),
    ("step-01: the auditor prompt still owes the adapted chain", STEPS[0],
     r"You still owe an evidence chain \(Gate 2\), adapted to your subject", 0,
     "You still owe an evidence chain (Gate 2), adapted to your subject",
     "You owe no evidence chain"),
    ("step-01: Gate 1 is a reachability proof", STEPS[0],
     r"\*\*Gate 1 — Reachability Proof\.\*\*", 0,
     "**Gate 1 — Reachability Proof.**", "**Gate 1 — Optional reachability note.**"),
    ("step-01: an untraceable finding is speculation, not a finding", STEPS[0],
     r"it is NOT a finding — it is speculation", 0,
     "it is NOT a finding — it is speculation", "report it and let triage decide"),
    ("step-01: Gate 2 demands a written evidence chain", STEPS[0],
     r"\*\*Gate 2 — Evidence Chain\.\*\* Every finding MUST carry a step-by-step chain", 0,
     "Every finding MUST carry a step-by-step chain", "A step-by-step chain is optional"),
    ("step-01: an unwritable chain means the finding is not reported", STEPS[0],
     r"the finding is not well-evidenced enough to report", 0,
     "the finding is not well-evidenced enough to report", "report the finding regardless"),
    ("step-01: Gate 3 sets a 0.6 confidence floor", STEPS[0],
     r"Report only findings at confidence \*\*0\.6 or above\.\*\*", 0,
     "Report only findings at confidence **0.6 or above.**",
     "Report findings at any confidence."),
    ("step-01: below the floor the lens is guessing and stays silent", STEPS[0],
     r"Below 0\.6: do NOT report — you are guessing", 0,
     "Below 0.6: do NOT report — you are guessing", "Below 0.6: report it with a caveat"),
    ("step-01: doubt drops the finding", STEPS[0],
     r"\*\*When in doubt, DROP the finding\.\*\*", 0,
     "**When in doubt, DROP the finding.**", "**When in doubt, keep the finding.**"),

    # ── step-01 (SCC-125): severity rubric, the five moves, author intent ───────────────────
    ("step-01: the severity rubric demands the full range", STEPS[0],
     r"^### Severity rubric — use the FULL range$", re.M,
     "### Severity rubric — use the FULL range", "### Severity rubric"),
    ("step-01: critical requires an exact failure scenario", STEPS[0],
     r"you can state the EXACT failure scenario", 0,
     "you can state the EXACT failure scenario", "a general concern is enough"),
    ("step-01: a well-calibrated review mixes severities", STEPS[0],
     r"A well-calibrated review has a MIX", 0,
     "A well-calibrated review has a MIX", "A well-calibrated review is all critical"),
    ("step-01: the five review moves are the hunter's method", STEPS[0],
     r"^### How to review — the five moves$", re.M,
     "### How to review — the five moves", "### How to review"),
    ("step-01: move 5 is what is NOT in the diff", STEPS[0],
     r"^> 5\. \*\*Think about what.s NOT in the diff\.\*\*", re.M,
     "5. **Think about what's NOT in the diff.**",
     "5. **Review only what is in the diff.**"),
    ("step-01: author intent is engaged with, never deferred to", STEPS[0],
     r"^### Author intent — engage with it, never defer to it$", re.M,
     "### Author intent — engage with it, never defer to it",
     "### Author intent — defer to it"),
    ("step-01: a finding contradicting stated rationale must rebut it", STEPS[0],
     r"MUST engage with the author.s stated rationale on its merits", 0,
     "MUST engage with the author's stated rationale on its merits",
     "may ignore the author's stated rationale"),

    # ── step-01 (SCC-125): the auditors are exempt, and recall-first ────────────────────────
    ("step-01: both auditors are exempt from Gates 1 and 3", STEPS[0],
     r"\*\*Both auditors are EXEMPT from Gate 1 and Gate 3", 0,
     "**Both auditors are EXEMPT from Gate 1 and Gate 3",
     "**Both auditors must pass Gate 1 and Gate 3",),
    ("step-01: the exemption's reason is that the subject is absent", STEPS[0],
     r"reachability proof is unwritable for a finding whose subject is \*absent\*", 0,
     "reachability proof is unwritable for a finding whose subject is *absent*",
     "reachability proof is writable for every finding"),
    ("step-01: the auditors are recall-first", STEPS[0],
     r"\*\*They are recall-first\.\*\*", 0,
     "**They are recall-first.**", "**They are precision-first.**"),
    ("step-01: an unsure auditor reports the gap and says it is unsure", STEPS[0],
     r"says it is unsure, rather than dropping it", 0,
     "rather than dropping it", "rather than reporting it"),
    ("step-01: Gate 2 still binds the auditors, adapted", STEPS[0],
     r"\*\*Gate 2 still binds, adapted:\*\*", 0,
     "**Gate 2 still binds, adapted:**", "**Gate 2 does not apply to them:**"),

    # ── step-01 (SCC-125): the pack is scoped, and never primes the blind lens ──────────────

    # ── step-01 (SCC-125): no worthiness filter, at this layer or any other ─────────────────
    ("step-01: no noise filter at this layer or any other", STEPS[0],
     r"^## No noise filter — at this layer or any other$", re.M,
     "## No noise filter — at this layer or any other", "## Noise filter"),
    ("step-01: worthiness gating is banned outright", STEPS[0],
     r"Never gate findings on .worthiness.", 0,
     "Never gate findings on", "Gate findings on"),
    # SCC-230 replaced the uncited pr-af recall figure with the fence: the ruling binds
    # diff-anchored review; plan/story audits answer to SCC-225's anchor rule instead, and
    # external benchmarks are cited with source and version or not at all.
    ("step-01: the no-filter ruling is scope-fenced to diff-anchored review", STEPS[0],
     r"applies where findings are anchored to a diff", 0,
     "applies where findings are anchored to a diff", "applies to every audit, diff or not"),
    ("step-01: external benchmarks require source and version", STEPS[0],
     r"cited with source and version", 0,
     "cited with source and version", "cited freely"),

    # ── step-02 (SCC-127) → RETIRED by SCC-447 ─────────────────────────────────────────────
    # The wave refuted 2 findings in 18 reviews while costing a second full fan-out of tokens
    # and wall-clock on every review that collected anything. Its 78 checks retire with it.
    # They are REPLACED rather than deleted: a retirement nothing pins is a retirement the next
    # agent can argue its way out of, and the instinct behind the wave ("something should turn
    # an assertion into evidence") is a good one that will be proposed again. What binds now is
    # the retirement itself — it runs nothing, it says what it was measured at, it passes
    # findings through untouched, it records why the step produced nothing, and it names the
    # bar for bringing a role back.
    ("step-02: the step runs nothing, and says so in its own first line", STEPS[1],
     r"^\*\*This step runs nothing\.\*\* The Evidence Verifier and the Compound Synthesis "
     r"role are retired\.$", re.M,
     "**This step runs nothing.** The Evidence Verifier and the Compound Synthesis role are retired.",
     "**This step runs two roles.** The Evidence Verifier and the Compound Synthesis role run here."),
    ("step-02: the retirement is MEASURED, never argued", STEPS[1],
     r"refuted \*\*2\nfindings in 18 reviews\*\*", 0,
     "refuted **2\nfindings in 18 reviews**",
     "refuted **most of what the lenses claimed**"),
    ("step-02: findings travel to step 3 unchanged, carrying `verification: none`", STEPS[1],
     r"Carry every finding from step 1 to step 3 unchanged, with\n`verification: none`", 0,
     "Carry every finding from step 1 to step 3 unchanged, with\n`verification: none`",
     "Re-grade each finding before step 3 and record a\n`revised_severity:`"),
    ("step-02: the returned notes record the retirement, so the record says why", STEPS[1],
     r"add `verify wave: retired \(SCC-447\)` to the engine's returned `notes`", 0,
     "add `verify wave: retired (SCC-447)` to the engine's returned `notes`",
     "add `verify wave: ran` to the engine's returned `notes`"),
    # ⛔ The one that stops this coming back by argument. The bar is the bar the wave FAILED:
    # show, over reviews on disk, that a second reading refutes findings the reproduction gate
    # does not already drop.
    ("step-02: reinstating a verification role needs a measurement, and the bar is named", STEPS[1],
     r"Do not reinstate a verification role here without a measurement[\s\S]{0,400}?"
     r"the reproduction gate\ndoes not already drop", 0,
     "Do not reinstate a verification role here without a measurement",
     "Reinstate a verification role here whenever it seems useful"),

    # ── step-01 (SCC-126): the literal-correctness lens, and the caps that make it affordable ─
    # This lens is the most instrumented one, so every check below binds either its WIRING
    # (the table cells that route it) or a cap that bounds it. Prose about the lens is not pinned;
    # a description cannot route a lens and cannot bound a cost.
    # The counter-example must name the DISCIPLINE, not just `+ the hunter contract | yes |` —
    # that substring hits the Edge Case Hunter's row first, so `.replace(old, new, 1)` would
    # mutate a different lens and leave this check green. The harness caught exactly that.

    # The discipline itself — as prompt text (blockquoted), or it never reaches the lens.

    # The four caps. Each is the cost contract; an unbounded lens is what this epic cannot ship.
    # ⭐ Every regex here binds the OPERATIVE sentence — the number, the destination, the scoring
    # word — not the bolded headline above it. The review of this task is why: with only the
    # headlines pinned, editing "at most **20**" to "at most **200**" left all 440 cases green
    # while the cap was gone. A guard on the label of a cap is not a guard on the cap.
    # F6: the early-exit must score `ok`. Scored `dead` it would raise the floor on every clean
    # diff; scored `n/a` it would read as degraded. Both are wrong and both look like a pass here.
    # The NUMBER, not the headline.
    # SCC-147 (rolled in on the operator's ruling): the disclosure names PATHS, never a count.
    # A count was useless twice over — the blockquote orders the lens to NAME what it did not
    # get, and the `standard` top-up is earned by naming a specific withheld file. Neither is
    # possible from a number.
    # The THRESHOLD and the DESTINATION, not the headline.

    # lens_budget: defined once, HERE, and NOT the same axis as review_mode. A caller that
    # re-defines a cap — or conflates the two axes — is how cost governance rots overnight.

    # SCC-147, second half (rolled in on the operator's ruling): the top-up ROW is definition
    # only — a table cell is unquoted, and this file pins twice that unquoted text never reaches
    # a lens. So for as long as the row was all there was, `standard` and `capped` were
    # behaviourally identical: a lens never told a top-up exists cannot spend one. The clause is
    # now BLOCKQUOTED and routed by budget; these three pin the quote, the routing, and the
    # capped-side absence that IS the `no top-up` enforcement.

    # Gate 1 adaptation — without it the lens must DROP the defect class it was added to catch.

    # A lens that RAN and found nothing is not a dead lens. Conflating the two caps every clean
    # review at CONCERNS — the same failure F6 guards for the empty-diff case, at diff-wide scale.
    ("step-01: zero findings is explicitly not a dead lens", STEPS[0],
     r"⛔ \*\*First, the distinction this whole section turns on: a lens that ran and found nothing is NOT\s*\na dead lens\.\*\*",
     re.M,
     "a lens that ran and found nothing is NOT", "a lens that ran and found nothing is"),
    ("step-01: the dead-lens contract applies to no usable OUTPUT, not to no findings", STEPS[0],
     r"Applied to any lens that errors, times out, or\s*\nreturns no usable output", re.M,
     "returns no usable output", "comes back empty"),

    # The headless override, and the ordering that keeps the blind lens blind while inline.
    ("step-01: a caller may override the return-the-prompts fallback", STEPS[0],
     r"⭐ \*\*A caller may override that return, and one already does\.\*\*", 0,
     "**A caller may override that return, and one already does.**",
     "**No caller may override that return.**"),
    ("step-01: returning unrun prompts headless is a review that never ran", STEPS[0],
     r"\*\*in a headless pipeline nobody is, and returning unrun prompts is a review\s*\nthat silently never ran\*\*",
     re.M,
     "that silently never ran**", "that is merely deferred**"),
    # ⛔ RETIRED BY SCC-203, and the retirement is the point. This used to pin
    # `ok (not blind — context held <what>)` as the honest way to record a lens that ran without
    # its defining property. The operator ruled that state out entirely: a roster carrying it
    # reports a review that was more independent than it was, which is worse than a smaller
    # review. The state a contaminated blind lens reaches is now `n/a`, and it is not counted.

    # ── step-01 (SCC-126 → SCC-209): the CALLER's wiring, pinned in the caller's own file ──
    # F7 from the SCC-126 review: a rule about a caller that lives only in step-01 is the engine's
    # CLAIM about its caller, not a check on one — reverting a caller left every case green while
    # the wiring was gone. The two INTERACTIVE callers are pinned below for exactly that reason.
    #
    # ⛔ `cicd-code-review-AP.md` USED to carry eight such rows here (`lens_budget: capped`, the
    # inline-lens mandate, the blind-lens ordering, the floor clause). They are gone, on the
    # operator's ruling of 2026-08-18: the `_AP` lane is being REWRITTEN from scratch — the files
    # survive only as reference while it is rebuilt, and their contents are explicitly disposable.
    # Pinning the prose of a file whose prose is declared disposable is a TRAP, not a guard: it
    # reds this suite on the day of the rewrite and sends the fixer to edit a file `workflow_lint`
    # marks UNMAINTAINED. That is the SCC-209 trap relocated into another check, not removed.
    #
    # What still holds AP, deliberately: it stays in `CALLER_FILES`, because three autopilot
    # engines invoke it by name and it is therefore still a LIVE caller. So the existence row in
    # section 1, the completeness row in 2b, and the "names a `lens_budget`" row over `discovered`
    # all still cover it. What is no longer asserted is the CONTENT of a frozen file. When the
    # rewrite lands, the new file earns its own rows here, the same as any other caller.

    # ── SCC-147's two caller rows — RETIRED by SCC-447, and the reason matters ──────────────
    # They pinned `| `lens_budget` | `standard` |` in each interactive caller's invocation table,
    # anchored to the contiguous run of rows under `HEAD_SHA` so an appendix table could not
    # satisfy them (this lane's review killed two looser versions with live mutants). The axis
    # itself is gone: the roster is three lenses, step-01 carries the retirement note instead of
    # a definition, and a caller that still passed a budget would be passing an input the engine
    # no longer reads. A retired input needs the INVERSE guard, and it is asserted over the
    # discovered caller set in the block below — over every caller, not just these two, because
    # the failure mode is one caller keeping the row after the definition left.

    # ── SCC-173 + SCC-177: the callers WRITE what the preflights read ───────────────────────
    # Bound the same contiguous-table way as `lens_budget` above, for the same reason: a
    # `review_runtime` row in some appendix satisfies a loose pattern while the invocation table
    # passes nothing. Row-adjacency to a REQUIRED input is what makes it the real row.
    ("caller /cicd-code-review: passes review_runtime in the invocation table", CICD_CMD,
     r"^\|\s*`HEAD_SHA`[^\n]*\n(?:\|[^\n]*\n)*?\|\s*`review_runtime`\s*\|[^|\n]*PROBED", re.M,
     "| `review_runtime` | `fan-out` or `inline` — **what you PROBED",
     "| `review_runtime` | `fan-out`, which is the usual answer — **what you assume"),
    ("caller /smh-code-review: passes review_runtime in the invocation table", SMH_CMD,
     r"^\|\s*`HEAD_SHA`[^\n]*\n(?:\|[^\n]*\n)*?\|\s*`review_runtime`\s*\|[^|\n]*PROBED", re.M,
     "| `review_runtime` | `fan-out` or `inline` — **what you PROBED",
     "| `review_runtime` | `fan-out`, which is the usual answer — **what you assume"),
    # ⛔ The probe is pinned to a step number BELOW Step 1's, not merely to existing. A probe
    # recorded after the hunt is read off the roster it is supposed to check, and the
    # contradiction rule (`inline` + `ok`) can then never fire — the header would be derived
    # from the states it is meant to disagree with.
    ("caller /cicd-code-review: probes the runtime BEFORE Step 1", CICD_CMD,
     r"^## Step 0\.9 — .*Probe the review runtime and RECORD it[\s\S]*?^## Step 1 ", re.M,
     "## Step 0.9 — ⭐ Probe the review runtime and RECORD it",
     "## Step 4.9 — ⭐ Probe the review runtime and RECORD it"),
    ("caller /smh-code-review: probes the runtime BEFORE Step 1", SMH_CMD,
     r"^## Step 0\.9 — .*Probe the review runtime and RECORD it[\s\S]*?^## Step 1 ", re.M,
     "## Step 0.9 — ⭐ Probe the review runtime and RECORD it",
     "## Step 4.9 — ⭐ Probe the review runtime and RECORD it"),
    ("caller /cicd-code-review: Step 4 writes the roster VERBATIM", CICD_CMD,
     r"the engine's `lenses_run:` block, pasted VERBATIM", 0,
     "pasted VERBATIM", "summarised in a sentence"),
    ("caller /smh-code-review: Step 4 writes the roster VERBATIM", SMH_CMD,
     r"the engine's `lenses_run:` block, pasted VERBATIM", 0,
     "pasted VERBATIM", "summarised in a sentence"),


    # ── step-03: buckets, alias map, and the severity-to-verdict table ──────────────────────
    # ⛔ The `defer` bucket this row once bound is GONE (operator ruling 2026-09-11, together with
    # `escalate`): a bucket for work "this lane cannot hold" was a parking lot with a nicer name,
    # and every entry in it was a reproduced defect nobody fixed. What the row holds now is the
    # closed set — two buckets, no third — stated positively so a stub cannot add one back quietly.
    ("step-03: two buckets, and the sentence that closes the set", STEPS[2],
     r"^\*\*There are two buckets, and there is no third\.\*\*", re.M,
     "**There are two buckets, and there is no third.**",
     "**There are two buckets, and a third may be added when a lane needs one.**"),
    ("step-03: critical accepts high and blocker", STEPS[2],
     r"^\|\s*`critical`\s*\|\s*critical, high, blocker\s*\|", re.M,
     "| `critical` | critical, high, blocker |", "| `critical` | trivial, info |"),
    ("step-03: important accepts medium and major", STEPS[2],
     r"^\|\s*`important`\s*\|\s*important, medium, major\s*\|", re.M,
     "| `important` | important, medium, major |", "| `important` | blocker, high |"),
    ("step-03: suggestion absorbs the unrecognized", STEPS[2],
     r"^\|\s*`suggestion`\s*\|\s*suggestion, minor, low[^|]*\*\*and anything unrecognized\*\*", re.M,
     "suggestion, minor, low — **and anything unrecognized**", "suggestion only"),
    ("step-03: nitpick accepts info, trivia, trivial", STEPS[2],
     r"^\|\s*`nitpick`\s*\|\s*nitpick, info, trivia, trivial\s*\|", re.M,
     "| `nitpick` | nitpick, info, trivia, trivial |", "| `nitpick` | critical, blocker |"),
    # ── step-03: the relevance gate (SCC-160, operator ruling 2026-08-15) ───────────────────
    # TRUE is necessary, not sufficient: hunters have finding-goals, so their volume is a
    # success metric, never a work queue. These three pins bind the ruling's load-bearing
    # sentences: the gate exists, severity cannot bypass it, and the residue class is dead.
    # ── step-03: fix in thread (SCC-160 follow-on, operator ruling 2026-08-15, second) ──────
    # The first cut kept a "rarely — proposed to the operator as a decided chore ticket" leg and
    # its own close-out ended in a ticket-ruling row: "we need the fixes made in thread not a
    # ticket made every story thats an endless loop that never finishes." Two pins bind the
    # recut: a review never produces a ticket, and `defer` is a structural blocker, not
    # "pre-existing". The counter-examples are the exact sentences the first cut shipped.
    ("step-03: a review never produces a ticket", STEPS[2],
     r"⛔ \*\*A review never produces a ticket\.\*\*", 0,
     "⛔ **A review never produces a ticket.**",
     "A finding that survives may be proposed to the operator as a decided chore ticket."),
    ("step-03: only a still-dead lens appears in the table", STEPS[2],
     r"^\|\s*a lens still `dead` after retry AND inline rerun\s*\|\s*\*\*CONCERNS\*\*\s*\|", re.M,
     "a lens still `dead` after retry AND inline rerun", "any lens that errored at all"),
    # step-03 §5 calls itself "the single definition; every caller reads it rather than inventing
    # its own". Step-02 promises CONCERNS for a dead ROLE, and with no row here that promise was
    # unreachable — the orchestrator would apply the single definition, find nothing, return none.
    ("step-03: the floor is the most severe row", STEPS[2],
     r"The floor is the \*\*most severe\*\* applicable row", 0,
     "the **most severe** applicable row", "the **least severe** applicable row"),

    # ── step-04: the record, and the boundary held positively ───────────────────────────────
    ("step-04: an absent sink is reported, never guessed", STEPS[3],
     r"do not pick a file", 0, "do not pick a file", "pick any file you like"),
    # The two rows this replaces pinned the `Defer` box and the `DEFERRED_WORK` bullet — both
    # retired 2026-09-11 on the operator's ruling. Their coverage moved to the retirement itself:
    # nothing is deferred anywhere, and the engine writes neither of the caller's two dispositions.
    ("step-04: nothing is deferred anywhere — the ledger was the queue", STEPS[3],
     r"Nothing is deferred anywhere: a ledger of reproduced defects\s+nobody is fixing is the queue"
     r"\s+this ticket closed", 0,
     "Nothing is deferred anywhere",
     "Deferred work goes to the ledger"),
    ("step-04: held and out-of-lane are the CALLER's, and the engine writes neither", STEPS[3],
     r"this engine never writes either", 0,
     "this engine never writes either",
     "this engine writes both"),
    ("step-04: the summary carries a severity floor", STEPS[3],
     r"^severity_floor:\s+none \| CONCERNS \| FAIL$", re.M,
     "severity_floor:  none | CONCERNS | FAIL", "verdict:  PASS | CONCERNS | FAIL"),
    ("step-04 boundary: never advances a story or writes a board", STEPS[3],
     r"^- \*\*It never advances a story.s state and never writes a board file\.\*\*", re.M,
     "It never advances a story's state", "It advances a story's state"),
    ("step-04 boundary: never issues the verdict line", STEPS[3],
     r"^- \*\*It never issues the verdict line\.\*\*", re.M,
     "It never issues the verdict line", "It issues the verdict line"),
    ("step-04 boundary: never applies fixes on its own initiative", STEPS[3],
     r"^- \*\*It never applies fixes on its own initiative\.\*\*", re.M,
     "It never applies fixes", "It applies fixes"),
    ("step-04 boundary: never merges, pushes or transitions", STEPS[3],
     r"^- \*\*It never merges, pushes, or transitions a ticket\.\*\*", re.M,
     "It never merges, pushes, or transitions a ticket",
     "It merges, pushes, and transitions the ticket"),
)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace")


def has_body(p: Path) -> bool:
    return p.is_file() and len(read(p).strip()) > 200


def main() -> int:
    c = Cases("review engine (SCC-116)")

    # ── 1. Structure ──────────────────────────────────────────────────────────────────────
    for rel in ENGINE_FILES:
        p = MASTER / rel
        c.check(f"{rel} exists with a body", has_body(p),
                "" if has_body(p) else ("absent" if not p.is_file() else "present but under 200 chars"))
    for rel in CALLER_FILES:
        p = ROOT / rel
        c.check(f"{rel} exists with a body", has_body(p),
                "" if has_body(p) else ("absent" if not p.is_file() else "present but under 200 chars"))

    texts = {rel: (read(MASTER / rel) if (MASTER / rel).is_file() else "") for rel in ENGINE_FILES}
    # Callers resolve from ROOT, not from the engine dir. Same CHECKS loop, same counter-example
    # proof — the only difference is where the file lives.
    # ⛔ DEV_STORY_CMD is loaded but is NOT a CALLER_FILE: it carries the probe law without
    # invoking the engine, and section 2b asserts CALLER_FILES is exactly the caller set.
    texts.update({rel: (read(ROOT / rel) if (ROOT / rel).is_file() else "")
                  for rel in CALLER_FILES + (DEV_STORY_CMD,)})

    # ── 2. Content: every rule bound to its meaning, and proven able to reject its negation ─
    for name, rel, pattern, flags, old, new in CHECKS:
        txt = texts.get(rel, "")
        rx = re.compile(pattern, flags)
        c.check(name, bool(txt) and rx.search(txt) is not None,
                "" if txt else f"{rel} missing or empty")
        # The counter-example must apply...
        applies = old in txt
        c.check(f"  ^ counter-example applies", applies,
                "" if applies else f"{rel}: {old!r} not present, so the proof would be vacuous")
        # ...and must make the check go red.
        mutated = txt.replace(old, new, 1) if applies else txt
        c.check(f"  ^ counter-example is rejected",
                applies and rx.search(mutated) is None,
                "" if applies and rx.search(mutated) is None
                else "check survives its own counter-example — it cannot fail on content")

    # ── 2a. SCC-203: the two interactive callers carry the SAME subagent law, byte for byte ──
    #
    # ⛔ TWO PINS ARE NOT A DRIFT CHECK. The rows above assert each caller carries the clause;
    # they say nothing about the two clauses AGREEING. That is the gap `sudo-commands-have-ap-twins
    # -that-drift` names, and it is how this very change nearly shipped: the smh caller was fixed
    # and the cicd twin was not, so the story lane and the task lane would have reviewed to
    # different law with every check green. The operator caught it by reading the diff.
    #
    # `cicd-code-review-AP` is deliberately EXCLUDED: it is headless, it genuinely cannot fan out,
    # and it protects the blind lens by ORDER instead (splitting its ingests so the lens runs
    # before any context lands). Holding it to "subagents are the default" would be law it cannot
    # obey - a rule nobody can follow is a rule that teaches everyone to ignore rules.
    # ⭐ THREE paragraphs, not two. The third is what the runtime answer OBLIGES once given, and
    # it was carried by both callers while pinned by nothing — no CHECKS row named it and this
    # extractor did not match it, so either caller could have lost the consequence with every
    # check green. It is part of the same law, so it belongs in the same byte-identity comparison.
    # ⛔ SCC-447 REPLACED THAT CLAUSE RATHER THAN DROPPING IT. It used to be "an `inline` caller
    # holding the plan DROPS the Blind Hunter rather than faking it" — a rule about a lens that no
    # longer exists, which both doors still carried as live instruction three parts into the lane
    # that retired it. The obligation that survives is the one the roster can still break: under
    # `inline` every lens comes back `recovered-inline`, and the roster may not read as a more
    # independent review than the one that ran.
    def _law_of(txt: str) -> str:
        out = []
        for para in txt.split("\n\n"):
            if ("**capability**" in para or "IS a user request" in para
                    or "may not record a bare" in para
                    or "every lens comes back `recovered-inline`" in para):
                out.append(" ".join(para.split()))
        return "\n".join(out)

    def subagent_law(rel: str) -> str:
        """The capability-vs-policy paragraph, the request clause, and the drop clause,
        whitespace-normalised."""
        return _law_of(texts.get(rel, ""))

    smh_law, cicd_law = subagent_law(SMH_CMD), subagent_law(CICD_CMD)
    c.check("SCC-203 the smh caller states the subagent law at all",
            bool(smh_law), f"{SMH_CMD}: no capability/request paragraph found")
    c.check("SCC-203 ...and the cicd TWIN states it identically (no drift)",
            bool(cicd_law) and smh_law == cicd_law,
            "the two interactive callers disagree about when a review may run inline; "
            f"smh={len(smh_law)}b cicd={len(cicd_law)}b")
    # ⛔ ALL THREE CLAUSES, NAMED. Byte-identity is satisfied by two files that are equally
    # WRONG — drop the drop-clause from both and this still passes. So assert each clause is
    # actually in the extracted law, or the comparison above guards an empty agreement.
    # ⛔ The `blocked:` clause is the SCC-263 addition and is load-bearing, not decoration. The
    # law used to forbid both stopping to ask AND downgrading, while naming no third move — so an
    # agent that believed itself forbidden had no legal option, and the cheapest illegal one is a
    # silent `inline` that reads exactly like a runtime with no subagent tool. Naming the escape
    # hatch is what makes that belief visible in the record instead of laundered out of it.
    for clause, why in (("**capability**", "capability-vs-policy"),
                        ("IS a user request", "a `/` command IS a user request"),
                        ("inline (blocked:", "a blocked inline must NAME what blocked it"),
                        ("every lens comes back `recovered-inline`",
                         "an inline run's roster says inline on every row")):
        c.check(f"  ^ the law includes the {why} clause",
                clause in smh_law and clause in cicd_law,
                f"missing from {'smh' if clause not in smh_law else 'cicd'} caller")
    # ⛔ AND THE COMPARISON'S OWN COUNTER-EXAMPLE — same discipline as section 2's CHECKS rows.
    # Two pins plus an equality still prove nothing about whether that equality can BREAK. A
    # `_law_of` that matched nothing would return "" for both files and compare equal, and a
    # `_law_of` that matched every paragraph would compare two whole files that legitimately
    # differ. Perturbing one caller must make them disagree, and a law-less text must extract
    # empty — together those bound the extractor from both sides.
    drifted = _law_of(texts.get(CICD_CMD, "").replace(
        "IS a user request", "is not a user request", 1))
    c.check("  ^ counter-example: a twin that drifts on the law is caught",
            bool(drifted) and drifted != smh_law,
            "perturbing the cicd law left it byte-identical — the drift check cannot fail")
    c.check("  ^ counter-example: a caller with NO law extracts empty (not a false match)",
            _law_of("# A command\n\nIt does a thing.\n\nThen another thing.") == "",
            "the extractor matches arbitrary prose, so agreement means nothing")

    # ── 2b. SCC-147: CALLER_FILES is the COMPLETE set of engine callers ───────────────────
    # The checks above pin the three callers that exist today, one hand-written row each. That
    # closes the defect and NOT the class: a fourth command wired onto the engine tomorrow can
    # name no budget, silently take `capped`, and every check above stays green because none of
    # them knows it exists. This check is the one that notices — it derives the caller set from
    # the commands themselves and fails when it stops matching what is pinned. Raised by this
    # lane's own review. The default itself is deliberately NOT re-litigated here: `capped` is
    # the right default for an UNWATCHED overnight loop, and the failure being guarded is a
    # caller that never chose at all.
    cmd_dir = ROOT / ".agents" / "commands"
    discovered = sorted(f".agents/commands/{p.name}" for p in cmd_dir.glob("*.md")
                        if "code-review-engine" in read(p)) if cmd_dir.is_dir() else []
    c.check("engine callers were discovered at all (anti-vacuity)", bool(discovered),
            f"{len(discovered)} found")
    c.check("CALLER_FILES is every command that invokes the engine",
            bool(discovered) and set(discovered) == set(CALLER_FILES),
            "" if set(discovered) == set(CALLER_FILES)
            else f"unpinned: {sorted(set(discovered) - set(CALLER_FILES))} | "
                 f"pinned but no longer a caller: {sorted(set(CALLER_FILES) - set(discovered))}")
    # ⛔ Scope of that scan, ruled explicitly rather than left to a reader to wonder about:
    # `.agents/opencode-agents/opus-reviewer.md` also LOADS step-01 and runs the fan-out solo,
    # and it names no budget — so by step-01's default it runs `capped`. That is the CORRECT
    # answer for it: it is a Stage-4 autopilot role, and `capped` is what an unwatched loop
    # should get. It is therefore deliberately out of `CALLER_FILES`, which pins the commands
    # that invoke the engine as a skill. Raised by this lane's review; recorded so the next
    # person does not have to re-derive it.
    #
    # ⛔ SCC-447 INVERTED THIS PAIR. It used to COUNT the rows (exactly one per interactive
    # caller) and require every discovered caller to NAME a budget, because a second,
    # contradictory row elsewhere in the same file is invisible to `re.search` — the review
    # proved it with a "## Step 3.9 — budget override" section that left the Step 1 row
    # untouched and the whole gate green. The axis is retired now: step-01 defines no budget and
    # the three-lens roster has no cost dial to turn, so the failure mode flipped from "a caller
    # names none" to "a caller still passes one". Counting is still what reads it — a file-wide
    # `re.search` for an absent row returns on the first match it does not find, which is exactly
    # as blind in this direction — so the rows are COUNTED to zero, over EVERY discovered caller
    # rather than the two that used to carry them.
    for rel in discovered:
        txt = texts.get(rel) or read(ROOT / rel)
        c.check(f"{Path(rel).name} has a body for the budget scan", len(txt) > 2000,
                "" if len(txt) > 2000 else f"{rel} absent or under 2000 chars")
        n = len(re.findall(r"^\|\s*`lens_budget`\s*\|", txt, re.M))
        c.check(f"{Path(rel).name} passes NO lens_budget row (retired, SCC-447)", n == 0,
                "" if n == 0 else f"found {n} — the engine no longer reads this input")

    # ── 3. Vendor identifiers: scanned across EVERY markdown file in the engine ────────────
    found = sorted(str(p.relative_to(MASTER)).replace("\\", "/")
                   for p in MASTER.rglob("*.md")) if MASTER.is_dir() else []
    c.check("ban scan discovered the engine's markdown", bool(found), f"{len(found)} file(s)")
    c.check("ban scan covers every known engine file",
            set(ENGINE_FILES) <= set(found),
            f"unscanned: {sorted(set(ENGINE_FILES) - set(found))}")
    for rel in found:
        p = MASTER / rel
        body_ok = has_body(p)
        txt = read(p) if p.is_file() else ""
        for label, pattern, flags in BANNED:
            hit = re.search(pattern, txt, flags) if body_ok else None
            c.check(f"{rel} carries no {label}", body_ok and hit is None,
                    "file missing or empty" if not body_ok
                    else (f"found {hit.group(0)!r}" if hit else ""))

    # ── 4. Registered, and the Claude cache agrees byte for byte ──────────────────────────
    idx_master, idx_cache = ROOT / ".agents/skills/INDEX.md", ROOT / ".claude/skills/INDEX.md"
    idx_txt = read(idx_master) if idx_master.is_file() else ""
    c.check("skills INDEX routes to the engine as caller-only",
            re.search(r"`code-review-engine`[^|]*never run standalone", idx_txt) is not None,
            "" if idx_txt else "INDEX missing")
    c.check("skills INDEX master and cache are identical",
            idx_master.is_file() and idx_cache.is_file()
            and idx_master.read_bytes() == idx_cache.read_bytes())

    def tree(root: Path) -> dict[str, bytes]:
        if not root.is_dir():
            return {}
        return {str(p.relative_to(root)).replace("\\", "/"): p.read_bytes()
                for p in sorted(root.rglob("*")) if p.is_file()}

    m, k = tree(MASTER), tree(CACHE)
    c.check("engine is published to the Claude cache", bool(k), "" if k else f"missing: {CACHE}")
    only_m, only_k = sorted(set(m) - set(k)), sorted(set(k) - set(m))
    c.check("cache holds the same file set as master", bool(m) and set(m) == set(k),
            f"master-only={only_m} cache-only={only_k}" if (only_m or only_k) else "")
    drifted = sorted(f for f in set(m) & set(k) if m[f] != k[f])
    c.check("cache is byte-identical to master", bool(m) and m == k,
            "differs: " + ", ".join(drifted) if drifted else "")

    # ── 5. SCC-177 step 9: the return shape ROUND-TRIPS through the parser that reads it ───
    # ⛔ WHAT THIS REPLACES, AND WHY. The old check here was `^lenses_run:\s+<n>/<applicable>` —
    # a source grep asserting SKILL.md contained a shape. It could not see whether anything
    # downstream could READ that shape, which is the entire question: the engine publishes a
    # return block, the callers paste it into the walkthrough, and `walkthrough_roster.py` gates
    # the close-out on it. Three surfaces, one format, and until now nothing joined them — the
    # engine could have gone on publishing a shape the parser was blind to, with every check on
    # both sides green. So the contract's OWN block is now filled in and parsed for real.
    contract = re.search(r"^```\n([\s\S]*?^lenses_run:[\s\S]*?)^```", texts[SKILL], re.M)
    c.check("SKILL.md publishes a fenced return block containing the roster",
            contract is not None,
            "" if contract else "no fenced block with a `lenses_run:` line — nothing to round-trip")
    if contract:
        # Fill the placeholders WITHOUT hard-coding their wording: every `- ` row becomes a real
        # roster row and the runtime line gets a real value; everything else is left exactly as
        # the contract wrote it. Shape-driven, so re-wording a placeholder does not fake a pass —
        # and collapsing the block back to one counted line leaves zero rows, which fails below.
        rows = 0
        filled = []
        for ln in contract.group(1).splitlines():
            if ln.startswith("- "):
                rows += 1
                filled.append(f"- lens-{rows} · recovered-inline — fan-out unavailable")
            elif re.match(r"^review[-_]runtime\s*:", ln, re.I):
                filled.append("review-runtime: inline")
            else:
                filled.append(ln)
        c.check("the contract's roster carries per-lens ROWS, not just a count", rows >= 2,
                "" if rows >= 2
                else f"{rows} row(s) — fewer than two is a summary with extra steps")

        # The walkthrough a caller would produce from this block, in the shape both preflights read.
        page = ("# W\n\n" + "\n".join(filled) + "\n\n"
                "## Step 0.7 — re-derivation\n\n"
                "1. What moved: nothing.\n2. What that changes here: nothing.\n"
                "3. What was re-measured: the anchors.\n\n"
                "## Code Review\n\n" + "\n".join(filled) + "\n\nVerdict: PASS @ abc1234\n")
        data = roster.parse(page)
        read_n = len(data["lenses"])
        c.check("round-trip: the parser reads every lens row the contract promises",
                read_n == rows and rows > 0,
                "" if read_n == rows and rows > 0
                else f"contract wrote {rows} row(s), parser read {read_n} — the engine's format "
                     f"and the close-out gate's format have drifted apart")
        c.check("round-trip: the parser reads the runtime header the contract names",
                data["runtime"] == "inline",
                "" if data["runtime"] == "inline"
                else f"parser read runtime={data['runtime']!r} — the header the engine publishes "
                     f"is not the header `walkthrough_roster.py` looks for")
        ok, why = roster.judge(page, "_artifacts/_main/2026-08-16_x/walkthrough.md", "PASS")
        c.check("round-trip: a walkthrough built from the contract PASSES the close-out gate",
                ok, "" if ok
                else f"the engine's own published shape is refused by the gate that reads it: {why}")

        # Anti-vacuity, both directions. The retired one-line form must be UNREADABLE here, or
        # the round-trip above would pass on a contract that says nothing.
        legacy = page.replace("\n".join(filled),
                              "lenses_run:      5/5   (per-lens: ok | recovered-inline | dead)")
        legacy_ok = roster.parse(legacy)["lenses"] == []
        c.check("round-trip: the retired counted form reads as NO roster", legacy_ok,
                "" if legacy_ok
                else "the pre-SCC-173 shape still parses as a roster, so the round-trip is vacuous")

    # ── 6. The dev-side recording point (SCC-177 step 6, F24) ─────────────────────────────
    # Neither lobby dev door is an engine caller — `/smh-dev-task-tests` (the full Task lane) and
    # `/smh-quick-dev` (the quick lane, SCC-445) never invoke the skill, so both are correctly
    # absent from CALLER_FILES and from the discovery check above. They are pinned here anyway,
    # because each owns its lane's walkthrough header: if it does not write `review-runtime:`
    # at Step 0, that lane's review (on the quick lane: the one the operator asks for) is judged
    # against a header nobody recorded.
    for door in ("smh-dev-task-tests", "smh-quick-dev"):
        qd = ROOT / f".agents/commands/{door}.md"
        qd_txt = read(qd) if qd.is_file() else ""
        c.check(f"/{door} exists with a body", len(qd_txt.strip()) > 200,
                "" if qd_txt else "absent")
        step0 = re.search(r"^## Step 0 —[\s\S]*?^## Step 0\.5 ", qd_txt, re.M)
        c.check(f"/{door} records review-runtime inside Step 0, before the worktree exists",
                step0 is not None and "review-runtime:" in step0.group(0),
                "" if step0 else "Step 0 / Step 0.5 headings not found — the anchor moved")
        named = re.search(r"`review-runtime:`[^\n]*header", qd_txt) is not None
        c.check(f"/{door}'s walkthrough contents name the header it must carry", named,
                "" if named else "the walkthrough step lists its sections; a header no section "
                                 "names is a header nobody writes")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
