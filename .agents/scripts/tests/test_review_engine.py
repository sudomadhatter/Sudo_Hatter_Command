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
AP_CMD = ".agents/commands/cicd-code-review-AP.md"
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
# SCC-205: the FAST lane became a caller. `/cicd-quick-dev` used to invoke
# `bmad-review-adversarial-general` bare - one lens, no roster, no verification, no triage - so it
# was the only dev lane in either family whose review produced no `lenses_run` block, which is
# exactly the evidence `walkthrough_roster.py` reads at close-out. Routing it through the engine is
# MORE BMAD, not less: the engine runs those lenses under a hunter contract with triage on top.
# ⭐ This line was added because the completeness row below CAUGHT the omission - the caller set is
# derived from the tree, so wiring a new caller and forgetting to pin it goes red rather than
# silently inheriting the autopilot's `capped` budget (SCC-147).
QUICK_CMD = ".agents/commands/cicd-quick-dev.md"
CALLER_FILES = (AP_CMD, CICD_CMD, SMH_CMD, QUICK_CMD)

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
    ("skill: caller may escalate, never soften", SKILL,
     r"report the floor or anything MORE severe", 0,
     "anything MORE severe", "anything LESS severe"),
    ("skill: the never-do list is a prohibition", SKILL,
     r"\*\*What the engine does NOT do, ever\*\*[^\n]*\n?[^\n]*issue the `Verdict:` line", 0,
     "What the engine does NOT do, ever", "What the engine also does when convenient"),
    # ⛔ This row USED to be `^lenses_run:\s+<n>/<applicable>` — a prose pin asserting the file
    # contained a shape. It is replaced (SCC-177 step 9) by the round-trip in § 5 below, which feeds
    # the contract's own fixture through the real parser. What stays here is the COUNT, which moved
    # to its own line when the roster became a block: a count is a summary and the rows are the
    # evidence, and the two must not share a line again.
    ("skill: the applicable count is its own line, beside the roster", SKILL,
     r"^lenses_counted:\s+<n>/<applicable>", re.M,
     "lenses_counted:  <n>/<applicable>", "lenses_counted:  <n>/<total>"),
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
    # use it right now?). A session directive saying "do not spawn subagents unless asked" was
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
    ("step-01: under inline the blind lens is DROPPED, not run", STEPS[0],
     r"^\|\s*`inline`\s*\|[^|]*\*\*the Blind Hunter is DROPPED\*\*", re.M,
     "**the Blind Hunter is DROPPED**", "**the Blind Hunter runs first**"),
    ("step-01: a dropped blind lens is recorded n/a, never `ok`", STEPS[0],
     r"never as `ok`, never as\s+`recovered-inline`, and never inside the count", 0,
     "never as `ok`, never as", "recorded however it turned out, and"),
    # ⛔ ANCHORED ON THE PROSE, NOT THE QUOTE. The first cut pinned the bare phrase "more
    # independent than it was", which now appears TWICE - in the operator's quoted ruling and in
    # the rule's own closing sentence. `replace(old, new, 1)` mutated only the first, the second
    # still matched, and the check survived its own counter-example. The harness caught it.
    ("step-01: the reason a faked blind lens is worse than none is STATED", STEPS[0],
     r"a roster carrying a lens\s+that ran without its defining property reports a review that "
     r"was more independent", re.M,
     "that ran without its defining property", "that ran in a warm context"),
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
    ("skill: the spec-less count agrees with step-01 (4/4)", SKILL,
     r"reports `4/4`, never `4/5`", 0,
     "reports `4/4`, never `4/5`", "reports `4/5`, never `4/4`"),

    # ── step-01: the fan-out table, the failure contract, NA-vs-dead ────────────────────────
    # SCC-232 made the routing cells level-aware. Each cell is pinned to the CURRENT truth
    # with the OBSOLETE flat-rate "always" as its mutant - the asymmetric pinning that steered
    # maintainers back toward "always" (executed, SCC-225 review wave) is retired with it.
    ("step-01: Blind Hunter routes standard-only (quick skips it)", STEPS[0],
     r"^\|\s*\*\*Blind Hunter\*\*\s*\|[^|]*\|\s*standard level \(quick skips it\)\s*\|", re.M,
     "| **Blind Hunter** | `DIFF` only — no spec, no repo access, no context docs | standard level (quick skips it) |",
     "| **Blind Hunter** | `DIFF` only — no spec, no repo access, no context docs | always |"),
    ("step-01: Edge Case Hunter routes standard-only (quick skips it)", STEPS[0],
     r"^\|\s*\*\*Edge Case Hunter\*\*\s*\|[^|]*\|\s*standard level \(quick skips it\)\s*\|", re.M,
     "| **Edge Case Hunter** | `DIFF` + read access to `REPO` | standard level (quick skips it) |",
     "| **Edge Case Hunter** | `DIFF` + read access to `REPO` | always |"),
    ("step-01: Acceptance Auditor is a lens row gated to full mode", STEPS[0],
     r"^\|\s*\*\*Acceptance Auditor\*\*\s*\|[^|]*\|\s*`review_mode: full` only\s*\|", re.M,
     "| **Acceptance Auditor** | `DIFF` + `STORY_FILE`", "| ~~Acceptance Auditor~~ | dropped,"),
    ("step-01: Test-Adequacy Auditor is a lens row that always runs", STEPS[0],
     r"^\|\s*\*\*Test-Adequacy Auditor\*\*\s*\|[^|]*\|\s*always\s*\|", re.M,
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
    ("step-01: a spec-less review reports 4/4, not 4/5", STEPS[0],
     r"reports `4/4`, never `4/5`", 0,
     "reports `4/4`, never `4/5`", "reports `4/5`, never `4/4`"),

    # ── step-01 (SCC-125): the ROUTING that makes the asymmetry real ────────────────────────
    # These bind the `How` cells and the assembly convention, not the prose that describes them.
    # The review of this task proved why: with only the prose pinned, four mutations that told the
    # orchestrator to give every lens both blocks — including deleting the hunter contract from
    # the Edge Case Hunter's wiring — all scored a clean 323/323. A guard on the description of a
    # rule is not a guard on the rule.
    ("step-01: the Blind Hunter's row wires in the hunter contract", STEPS[0],
     r"^\|\s*\*\*Blind Hunter\*\*\s*\|[^|]*\|[^|]*\|[^|]*\+ the hunter contract\s*\|", re.M,
     "the `bmad-review-adversarial-general` skill + the hunter contract",
     "the `bmad-review-adversarial-general` skill alone"),
    ("step-01: the Edge Case Hunter's row wires in the hunter contract", STEPS[0],
     r"^\|\s*\*\*Edge Case Hunter\*\*\s*\|[^|]*\|[^|]*\|[^|]*\+ the hunter contract\s*\|", re.M,
     "the `bmad-review-edge-case-hunter` skill + the hunter contract",
     "the `bmad-review-edge-case-hunter` skill alone"),
    ("step-01: the Acceptance Auditor's row wires in the auditor rubric", STEPS[0],
     r"^\|\s*\*\*Acceptance Auditor\*\*\s*\|[^|]*\|[^|]*\|\s*the auditor rubric\s*\|", re.M,
     "| **Acceptance Auditor** | `DIFF` + `STORY_FILE` + any context docs | `review_mode: full` only | the auditor rubric |",
     "| **Acceptance Auditor** | `DIFF` + `STORY_FILE` + any context docs | `review_mode: full` only | the hunter contract |"),
    ("step-01: the Test-Adequacy Auditor's row wires in the auditor rubric", STEPS[0],
     r"^\|\s*\*\*Test-Adequacy Auditor\*\*\s*\|[^|]*\|[^|]*\|\s*the auditor rubric\s*\|", re.M,
     "| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | always | the auditor rubric |",
     "| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | always | the hunter contract |"),
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
    ("step-01: a repo-less hunter runs the gates inside its diff", STEPS[0],
     r"^> \*\*If you were given no repo access\*\*, run both traceable gates inside the diff", re.M,
     "**If you were given no repo access**, run both traceable gates inside the diff",
     "**If you were given no repo access**, skip Gate 1 and Gate 2"),
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
    ("step-01: the Blind Hunter runs the gates inside the diff, at the same bar", STEPS[0],
     r"\*\*The Blind Hunter passes these gates inside the diff\.\*\*", 0,
     "**The Blind Hunter passes these gates inside the diff.**",
     "**The Blind Hunter is exempt from these gates.**"),
    ("step-01: the blind lens never lowers the bar to compensate", STEPS[0],
     r"it never downgrades the bar to compensate", 0,
     "it never downgrades the bar to compensate", "it lowers the bar to compensate"),

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
    ("step-01: the pack goes to repo-access lenses only", STEPS[0],
     r"^## The evidence pack — repo-access lenses only$", re.M,
     "## The evidence pack — repo-access lenses only",
     "## The evidence pack — every lens is primed"),
    ("step-01: the Blind Hunter's row is marked never-primed", STEPS[0],
     r"^\|\s*\*\*Blind Hunter\*\*\s*\|[^|]*\|\s*standard level \(quick skips it\)\s*\|[^|]*\|\s*\*\*never\*\* — starved by design\s*\|$",
     re.M, "| **never** — starved by design |", "| yes |"),
    ("step-01: the Acceptance Auditor is not primed either", STEPS[0],
     r"^\|\s*\*\*Acceptance Auditor\*\*\s*\|[^|]*\|[^|]*\|[^|]*\|\s*\*\*never\*\* — cannot verify it\s*\|$",
     re.M, "| **never** — cannot verify it |", "| yes |"),
    ("step-01: the reason it is excluded is that it cannot verify the pack", STEPS[0],
     r"it cannot do the one thing the pack instruction demands", 0,
     "it cannot do the one thing the pack instruction demands",
     "it can verify the pack against live files"),
    ("step-01: priming the Blind Hunter is forbidden outright", STEPS[0],
     r"⛔ \*\*The Blind Hunter is never primed with the pack\.\*\*", 0,
     "**The Blind Hunter is never primed with the pack.**",
     "**The Blind Hunter is primed with the pack like the others.**"),
    ("step-01: the SCC-124 measurement is cited for that ban", STEPS[0],
     r"\+38\.6 s", 0, "+38.6 s", "no measurable cost"),
    ("step-01: the pack is a starting point, not the search space", STEPS[0],
     r"\*\*the pack is a starting point, not the search space\*\*", 0,
     "**the pack is a starting point, not the search space**",
     "the pack is the search space"),

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

    # ── step-02 (SCC-127): the two roles run as ONE self-gating wave ────────────────────────
    ("step-02: both roles run concurrently in one wave", STEPS[1],
     r"\*\*concurrently, in ONE wave\*\*", 0,
     "**concurrently, in ONE wave**", "one after the other, in two waves"),
    # The gate table's COLUMN ORDER is wiring, not layout: with only the body rows pinned, swapping
    # the two header cells turns "verifier runs alone at 1 finding" into its opposite and every
    # case still passed. Same for the two `##` role headings — swapping them publishes the compound
    # prompt as the verifier's, so nothing is ever verified. Both mutations are bound below by
    # spanning a heading to the first line of the prompt it routes.
    ("step-02: the gate table's columns are verifier then compound", STEPS[1],
     r"^\| Findings from step 1 \| Evidence Verifier \| Compound Synthesis \|$", re.M,
     "| Findings from step 1 | Evidence Verifier | Compound Synthesis |",
     "| Findings from step 1 | Compound Synthesis | Evidence Verifier |"),
    ("step-02: the Evidence Verifier heading routes the investigator prompt", STEPS[1],
     r"## Evidence Verifier\n[^#]*?> You are not the original reviewer", re.S,
     "## Evidence Verifier", "## Compound Synthesis"),
    ("step-02: the Evidence Verifier heading routes the output fields", STEPS[1],
     r"## Evidence Verifier\n[^#]*?> revised_severity:", re.S,
     "> revised_severity:", "> severity_guess:"),
    ("step-02: the Compound Synthesis heading routes the synthesis prompt", STEPS[1],
     r"## Compound Synthesis\n[^#]*?> You are given every finding", re.S,
     "> You are given every finding", "> You are given one finding"),
    ("step-02: the Compound Synthesis heading routes the parents rule", STEPS[1],
     r"## Compound Synthesis\n[^#]*?contributing_findings", re.S,
     "## Compound Synthesis\n\nAssemble", "## Evidence Verifier\n\nAssemble"),
    ("step-02: the verifier is assembled WITH the dossier block", STEPS[1],
     r"## Evidence Verifier\n\nAssemble as: \*\*the prompt below, then the dossier block\*\*", 0,
     "Assemble as: **the prompt below, then the dossier block**",
     "Assemble as: **the prompt below** alone"),
    ("step-02: compound is assembled WITH the dossier block too", STEPS[1],
     r"## Compound Synthesis\n\nAssemble the same way — \*\*the prompt below, then the dossier block\*\*",
     0, "Assemble the same way — **the prompt below, then the dossier block**",
     "Assemble the same way — **the prompt below** alone"),

    ("step-02: the gate table gives 0 findings neither role", STEPS[1],
     r"^\|\s*0\s*\|\s*\*\*does not run\*\*\s*\|\s*\*\*does not run\*\*\s*\|", re.M,
     "| 0 | **does not run** | **does not run** |", "| 0 | runs | runs |"),
    ("step-02: the gate table gives 1 finding the verifier only", STEPS[1],
     r"^\|\s*1\s*\|\s*runs\s*\|\s*\*\*does not run\*\*\s*\|", re.M,
     "| 1 | runs | **does not run** |", "| 1 | runs | runs |"),
    ("step-02: the gate table gives 2+ findings both roles", STEPS[1],
     r"^\|\s*2 or more\s*\|\s*runs\s*\|\s*runs\s*\|", re.M,
     "| 2 or more | runs | runs |", "| 2 or more | runs | **does not run** |"),
    ("step-02: zero findings skips the entire step", STEPS[1],
     r"\*\*0 findings → skip this entire step\.\*\*", 0,
     "**0 findings → skip this entire step.**", "**0 findings → run the wave anyway.**"),
    ("step-02: a clean diff costs no new wall-clock", STEPS[1],
     r"no role launched, no tokens spent and\s*\n?\s*no wall-clock added", re.M,
     "no role launched, no tokens spent and", "a role launched, tokens spent and"),
    ("step-02: under two findings there is no compound pass", STEPS[1],
     r"\*\*Fewer than 2 findings → no compound pass\.\*\*", 0,
     "**Fewer than 2 findings → no compound pass.**",
     "**Fewer than 2 findings → run the compound pass anyway.**"),
    ("step-02: a skipped wave is recorded, never silent", STEPS[1],
     r"⛔ \*\*A skipped wave is recorded, never silent\.\*\*", 0,
     "**A skipped wave is recorded, never silent.**", "**A skipped wave needs no note.**"),
    ("step-02: the skip note names the zero-finding gate", STEPS[1],
     r"`verify wave: skipped \(0 findings\)`", 0,
     "verify wave: skipped (0 findings)", "verify wave: complete"),
    ("step-02: the skip note names the compound gate", STEPS[1],
     r"`compound: skipped \(<2 findings\)`", 0,
     "compound: skipped (<2 findings)", "compound: complete"),
    ("step-02: verified-nothing and all-confirmed must read differently", STEPS[1],
     r"are different evidence, and a reader who\s*\n?\s*cannot tell them apart", re.M,
     "are different evidence, and a reader who", "are the same evidence, and a reader who"),

    # ── step-02 (SCC-127): the dossier is code, and the join is by index ────────────────────
    ("step-02: the orchestrator never runs the extractor itself", STEPS[1],
     r"the orchestrator never runs the extractor\s*\n?\s*itself", re.M,
     "the orchestrator never runs the extractor", "the orchestrator runs the extractor"),
    ("step-02: each role runs the extractor as its own first action", STEPS[1],
     r"\*\*Each role runs the extractor itself\*\*, as its own first action", 0,
     "**Each role runs the extractor itself**, as its own first action",
     "**The roles are handed whatever evidence is lying around**, as their first action"),
    # The instruction to RUN the extractor has to reach the role, so it is pinned inside the
    # blockquote that step-01's convention says is the only text sent verbatim. Pinned in the
    # orchestrator's prose alone, it was a rule nobody was told — the wave ran cold every time.
    ("step-02: the dossier block is prompt text appended to BOTH roles", STEPS[1],
     r"^### The dossier block — appended to BOTH role prompts$", re.M,
     "### The dossier block — appended to BOTH role prompts",
     "### The dossier block — for the orchestrator's reference"),
    ("step-02: the role is TOLD to build the dossier, in its own prompt", STEPS[1],
     r"^> \*\*Before you review anything, build your evidence dossier\.\*\*", re.M,
     "> **Before you review anything, build your evidence dossier.**",
     "> **A dossier has already been built for you.**"),
    ("step-02: the extractor invocation is pinned inside the prompt", STEPS[1],
     r"^> python3 <WORKTREE>/\.agents/scripts/evidence_extract\.py --repo <WORKTREE> --findings findings\.json --diff diff\.patch$",
     re.M,
     "> python3 <WORKTREE>/.agents/scripts/evidence_extract.py --repo <WORKTREE> --findings findings.json --diff diff.patch",
     "> python3 <WORKTREE>/.agents/scripts/evidence_extract.py --repo $REPO --pack changed.py"),
    ("step-02: the invocation carries the two-machine interpreter note", STEPS[1],
     r"On Windows that interpreter is `python`, not `python3`", 0,
     "On Windows that interpreter is `python`, not `python3`",
     "That interpreter is `python3` on every machine"),
    ("step-02: placeholders are substituted, never sent as shell variables", STEPS[1],
     r"⛔ \*\*Substitute every placeholder before you send a prompt\.\*\*", 0,
     "**Substitute every placeholder before you send a prompt.**",
     "**The role will resolve the placeholders itself.**"),
    ("step-02: the extractor is pointed at WORKTREE, never REPO", STEPS[1],
     r"⛔ \*\*The extractor reads `WORKTREE`, never `REPO`, wherever the two differ\.\*\*", 0,
     "**The extractor reads `WORKTREE`, never `REPO`, wherever the two differ.**",
     "**The extractor reads `REPO`.**"),
    ("step-02: reading the wrong tree refutes correct findings", STEPS[1],
     r"reads\s*\n?`main`'s copy of every file at the lane's line numbers", re.M,
     "`main`'s copy of every file at the lane's line numbers",
     "the same file the lane changed"),
    ("step-02: a failed extractor leaves the role COLD, not stopped", STEPS[1],
     r"^> \*\*If that command fails for any reason, carry on COLD:\*\*", re.M,
     "> **If that command fails for any reason, carry on COLD:**",
     "> **If that command fails for any reason, stop and report it:**"),
    ("step-02: the cold rule covers BOTH roles, and names which", STEPS[1],
     r"This applies to \*\*both\*\* roles, and\s*\n?naming the role in the note is what keeps one cold role distinguishable", re.M,
     "This applies to **both** roles, and",
     "This applies to the verifier only, and"),
    ("step-02: the findings JSON carries the keys the extractor reads", STEPS[1],
     r"carrying the keys the extractor reads: `title` · `file_path` ·\s*\n?\s*`line_start` · `body` · `evidence`",
     re.M, "carrying the keys the extractor reads: `title` · `file_path` ·",
     "carrying whichever keys you feel like sending:"),
    ("step-02: the roles are handed the findings in step-1 order", STEPS[1],
     r"as a JSON list, \*\*in step-1 order\*\*", 0,
     "as a JSON list, **in step-1 order**", "as a JSON list, in any order"),
    ("step-02: the join is by index, never by title", STEPS[1],
     r"⭐ \*\*The join is BY INDEX, never by title\.\*\*", 0,
     "**The join is BY INDEX, never by title.**", "**The join is BY TITLE.**"),
    ("step-02: titles are not unique, so position is the join", STEPS[1],
     r"titles are NOT unique", 0, "titles are NOT unique", "titles are unique"),
    ("step-02: a failed extractor leaves that role running cold", STEPS[1],
     r"\*\*If the extractor fails, that role runs COLD\*\*", 0,
     "**If the extractor fails, that role runs COLD**",
     "**If the extractor fails, skip that role**"),
    ("step-02: the cold run is named in the record, per role", STEPS[1],
     r"`evidence extractor unavailable: <role> ran cold`", 0,
     "evidence extractor unavailable: <role> ran cold", "verification complete"),
    ("step-02: a cold role does NOT cap the verdict", STEPS[1],
     r"⛔ \*\*A cold role does NOT cap the verdict\.\*\*", 0,
     "**A cold role does NOT cap the verdict.**",
     "**A cold role caps the verdict at CONCERNS.**"),
    ("step-02: an inline rerun is cold by construction and recorded so", STEPS[1],
     r"⚠ \*\*A role you rerun inline is COLD by construction, and must be recorded that way\.\*\*",
     0, "**A role you rerun inline is COLD by construction, and must be recorded that way.**",
     "**A role you rerun inline has the same dossier as any other.**"),
    ("step-02: the inline-cold note is pinned", STEPS[1],
     r"`<role> rerun inline: cold \(no dossier\)`", 0,
     "<role> rerun inline: cold (no dossier)", "<role> rerun inline"),
    ("step-02: an inline rerun still costs coverage nothing", STEPS[1],
     r"It is still `recovered-inline` and still does not raise\s*\n?the floor", re.M,
     "It is still `recovered-inline` and still does not raise",
     "It is a dead role and does raise"),
    ("step-02: a dead script is not a dead role", STEPS[1],
     r"a dead script is not a dead role", 0,
     "a dead script is not a dead role", "a dead script is a dead role"),

    # ── step-02 (SCC-127): the Evidence Verifier's role framing and output contract ─────────
    ("step-02: the verifier is neither reviewer nor adversary", STEPS[1],
     r"^> You are not the original reviewer, and you are not the adversary\.", re.M,
     "You are not the original reviewer, and you are not the adversary.",
     "You are the original reviewer, reading your own work again."),
    ("step-02: the verifier is an independent investigator", STEPS[1],
     r"You are an independent\s*\n?> investigator", re.M,
     "You are an independent", "You are a second"),
    ("step-02: the extracted code and the live repo are both authorities", STEPS[1],
     r"Where the two disagree, open the file", 0,
     "Where the two disagree, open the file", "Where the two disagree, trust the extraction"),
    ("step-02: Q1 — does the code behave as claimed", STEPS[1],
     r"\*\*Does the code actually behave as the reviewer claims\?\*\*", 0,
     "**Does the code actually behave as the reviewer claims?**",
     "**Assume the reviewer's claim is accurate.**"),
    ("step-02: Q2 — is the scenario reachable", STEPS[1],
     r"\*\*Is the described scenario actually reachable\?\*\*", 0,
     "**Is the described scenario actually reachable?**",
     "**Reachability is not your concern.**"),
    ("step-02: Q3 — what the broader context reveals", STEPS[1],
     r"\*\*What does the broader context reveal\?\*\*", 0,
     "**What does the broader context reveal?**", "**Judge each finding in isolation.**"),
    ("step-02: Q4 — is the severity proportionate", STEPS[1],
     r"\*\*Is the severity proportionate\*\*", 0,
     "**Is the severity proportionate**", "**Keep the severity you were given**"),
    ("step-02: results come back in the order they were given", STEPS[1],
     r"\*\*in the order you were given them\*\*", 0,
     "**in the order you were given them**", "in whatever order suits you"),
    ("step-02: the result carries a verified boolean", STEPS[1],
     r"^> verified:\s+true \| false$", re.M, "true | false", "always true"),
    ("step-02: the result carries what the code actually does", STEPS[1],
     r"^> actual_behavior:\s+what the code actually does at that location$", re.M,
     "what the code actually does at that location", "your impression of the code"),
    ("step-02: the result carries a revised severity on the house scale", STEPS[1],
     r"^> revised_severity:\s+critical \| important \| suggestion \| nitpick$", re.M,
     "critical | important | suggestion | nitpick", "whatever word you prefer"),
    ("step-02: the result carries a revised confidence", STEPS[1],
     r"^> revised_confidence:\s+0\.0–1\.0$", re.M, "0.0–1.0", "any number"),
    ("step-02: the result carries verification notes", STEPS[1],
     r"^> verification_notes:\s+what you checked, and what settled it$", re.M,
     "what you checked, and what settled it", "optional"),
    ("step-02: a refuted finding is a full result, not a failure", STEPS[1],
     r"`verified: false` is a full result, not a failure", 0,
     "`verified: false` is a full result, not a failure",
     "`verified: false` means you failed"),
    ("step-02: an unsettled finding is returned, never dropped", STEPS[1],
     r"never\s*\n?> drop a finding you could not settle", re.M,
     "drop a finding you could not settle", "report a finding you could not settle"),

    # ── step-02 (SCC-127): Compound Synthesis — new findings only, parents named ────────────
    ("step-02: compound launches beside the verifier, not after it", STEPS[1],
     r"launch it \*\*at the same\s*\n?time as the verifier, not after it\.\*\*", re.M,
     "launch it **at the same", "launch it once the verifier returns **at the same"),
    ("step-02: compound asks what the findings mean together", STEPS[1],
     r"Your question is what these findings mean TOGETHER", 0,
     "Your question is what these findings mean TOGETHER",
     "Your question is whether each finding is correct"),
    ("step-02: compound emits NEW findings only", STEPS[1],
     r"\*\*Emit NEW findings only\. Never restate, re-rank or summarize the originals\*\*", 0,
     "**Emit NEW findings only. Never restate, re-rank or summarize the originals**",
     "**Restate and re-rank the originals**"),
    ("step-02: every compound finding names its parents", STEPS[1],
     r"MUST carry `contributing_findings`: the exact titles of the findings it is", 0,
     "MUST carry `contributing_findings`: the exact titles of the findings it is",
     "may carry `contributing_findings`: the rough gist of the findings it is"),
    ("step-02: a parentless compound is not a synthesis", STEPS[1],
     r"is not a synthesis, it is a fresh assertion", 0,
     "is not a synthesis, it is a fresh assertion", "is a synthesis all the same"),
    ("step-02: compound has a 0.6 confidence floor and evidence", STEPS[1],
     r"\*\*Emit only at confidence 0\.6 or above, and only with concrete evidence\.", 0,
     "**Emit only at confidence 0.6 or above, and only with concrete evidence.",
     "**Emit at any confidence, with or without evidence.",),
    ("step-02: an empty compound list is valid and expected", STEPS[1],
     r"An EMPTY LIST is a\s*\n?> valid and expected answer\*\*", re.M,
     "An EMPTY LIST is a", "An empty list means you did not try hard enough and is a"),

    # ── step-02 (SCC-127): what reaches triage — nothing dropped, nothing invented ──────────
    ("step-02: every step-1 finding is carried forward annotated", STEPS[1],
     r"^1\. \*\*Every step-1 finding, carried forward\*\* — annotated with its verifier result",
     re.M, "**Every step-1 finding, carried forward**",
     "**Only the findings the verifier confirmed**"),
    ("step-02: an unverified finding keeps the hunter's severity", STEPS[1],
     r"is marked `verification: none` and\s*\n?\s*keeps its hunter-asserted severity", re.M,
     "keeps its hunter-asserted severity", "is dropped from the record"),
    ("step-02: compound findings reach triage tagged as their own source", STEPS[1],
     r"appended as a new finding\*\* with `source: compound`", 0,
     "appended as a new finding** with `source: compound`",
     "merged into its parents** with `source: compound`"),
    ("step-02: the compound gate counts RAW findings, before dedupe", STEPS[1],
     r"\*\*The count is the RAW step-1 count, before dedupe\.\*\*", 0,
     "**The count is the RAW step-1 count, before dedupe.**",
     "**The count is taken after dedupe.**"),
    ("step-02: zero findings from dead lenses reads differently", STEPS[1],
     r"⚠ \*\*Zero findings has two causes and the note must say which\.\*\*", 0,
     "**Zero findings has two causes and the note must say which.**",
     "**Zero findings has one cause.**"),
    ("step-02: the dead-lens variant of the skip note is pinned", STEPS[1],
     r"`verify wave: skipped \(0 findings — but <n> lens\(es\) dead\)`", 0,
     "verify wave: skipped (0 findings — but <n> lens(es) dead)",
     "verify wave: skipped (0 findings)"),
    ("step-02: an unverified compound gating a merge is a stated decision", STEPS[1],
     r"⚠ \*\*A compound finding can FAIL a merge on less evidence than any other finding, and that is a\s*\n?decision, not an oversight\.\*\*",
     re.M, "and that is a", "and that is an"),
    ("step-02: the compound exemption is revisited when re-verify exists", STEPS[1],
     r"\*\*Revisit this the moment a compound re-verify pass exists\*\*", 0,
     "**Revisit this the moment a compound re-verify pass exists**",
     "This needs no revisiting"),
    ("step-02: this step drops nothing", STEPS[1],
     r"⛔ \*\*This step drops NOTHING\.\*\*", 0,
     "**This step drops NOTHING.**", "**This step drops what it refutes.**"),
    ("step-02: a refuted finding still reaches triage", STEPS[1],
     r"A refuted finding travels to triage annotated `verified: false`", 0,
     "A refuted finding travels to triage annotated `verified: false`",
     "A refuted finding is deleted here"),
    ("step-02: the no-noise-filter law binds at this layer too", STEPS[1],
     r"step 1's no-noise-filter law binds at this layer exactly as hard", 0,
     "no-noise-filter law binds at this layer exactly as hard",
     "no-noise-filter law stops at step 1"),
    ("step-02: fabricating a verification is forbidden", STEPS[1],
     r"⛔ \*\*Never mark a finding verified that no role verified\.\*\*", 0,
     "**Never mark a finding verified that no role verified.**",
     "**Mark the findings verified once the wave is over.**"),

    # ── step-02 (SCC-127): the failure contract is step-01's, unchanged ─────────────────────
    ("step-02: a failed role is retried once", STEPS[1],
     r"^1\. \*\*Retry it once\.\*\*", re.M,
     "1. **Retry it once.**", "1. **Do not retry it.**"),
    ("step-02: a still-failing role is rerun inline", STEPS[1],
     r"run that role INLINE yourself, here, in this context", 0,
     "run that role INLINE yourself", "drop that role and carry on"),
    ("step-02: only a still-dead role raises the floor", STEPS[1],
     r"^4\. \*\*Only a role that is still dead after BOTH the retry and the inline rerun raises the floor\*\*",
     re.M, "raises the floor** to\n   CONCERNS", "leaves the floor alone** and costs\n   nothing"),
    ("step-02: a gate-skipped role is not a dead role", STEPS[1],
     r"A role the self-gate skipped is \*\*not\*\* a dead role and never raises the floor", 0,
     "is **not** a dead role and never raises the floor",
     "is a dead role and raises the floor"),
    # ── step-01 (SCC-126): the literal-correctness lens, and the caps that make it affordable ─
    # This lens is the most instrumented one, so every check below binds either its WIRING
    # (the table cells that route it) or a cap that bounds it. Prose about the lens is not pinned;
    # a description cannot route a lens and cannot bound a cost.
    ("step-01: Literal-Correctness Hunter routes standard-only (quick skips it)", STEPS[0],
     r"^\|\s*\*\*Literal-Correctness Hunter\*\*\s*\|[^|]*\|\s*standard level \(quick skips it\)\s*\|",
     re.M,
     "| **Literal-Correctness Hunter** | `DIFF` + read access to `REPO` | standard level (quick skips it) |",
     "| **Literal-Correctness Hunter** | `DIFF` + read access to `REPO` | always |"),
    ("step-01: the quick level is EXACTLY Test-Adequacy + Acceptance (SCC-232's "
     "pre-registered membership - an inversion re-seats the 1,082 s lens)", STEPS[0],
     r"^\|\s*`quick`\s*\|\s*\*\*Test-Adequacy \+ Acceptance\*\* Auditor\s*\|", re.M,
     "| `quick` | **Test-Adequacy + Acceptance** Auditor |",
     "| `quick` | the full roster |"),
    ("step-01: the literal lens's row wires in the hunter contract", STEPS[0],
     r"^\|\s*\*\*Literal-Correctness Hunter\*\*\s*\|[^|]*\|[^|]*\|[^|]*\+ the hunter contract\s*\|",
     re.M,
     "the literal-correctness discipline + the hunter contract",
     "the literal-correctness discipline alone"),
    # The counter-example must name the DISCIPLINE, not just `+ the hunter contract | yes |` —
    # that substring hits the Edge Case Hunter's row first, so `.replace(old, new, 1)` would
    # mutate a different lens and leave this check green. The harness caught exactly that.
    ("step-01: the literal lens is primed with the evidence pack", STEPS[0],
     r"^\|\s*\*\*Literal-Correctness Hunter\*\*\s*\|[^|]*\|[^|]*\|[^|]*\|\s*yes\s*\|$", re.M,
     "the literal-correctness discipline + the hunter contract | yes |",
     "the literal-correctness discipline + the hunter contract | **never** |"),

    # The discipline itself — as prompt text (blockquoted), or it never reaches the lens.
    ("step-01: the literal lens opens the real definition of what the code leans on", STEPS[0],
     r"^> .*open the actual definition and verify the assumption holds", re.M,
     "open the actual definition and verify the assumption holds",
     "assume the definition matches what its name suggests"),
    ("step-01: the literal lens is exhaustive, not selective", STEPS[0],
     r"^> \*\*Be EXHAUSTIVE, not selective\.\*\*", re.M,
     "> **Be EXHAUSTIVE, not selective.**", "> **Sample the most interesting ones.**"),
    ("step-01: the literal lens is a discipline, not a bug checklist", STEPS[0],
     r"^> This is a reasoning DISCIPLINE, not a bug checklist", re.M,
     "This is a reasoning DISCIPLINE, not a bug checklist",
     "This is a checklist of bug categories to pattern-match"),

    # The four caps. Each is the cost contract; an unbounded lens is what this epic cannot ship.
    # ⭐ Every regex here binds the OPERATIVE sentence — the number, the destination, the scoring
    # word — not the bolded headline above it. The review of this task is why: with only the
    # headlines pinned, editing "at most **20**" to "at most **200**" left all 440 cases green
    # while the cap was gone. A guard on the label of a cap is not a guard on the cap.
    ("step-01: the literal lens is diff-scoped, never whole-repo", STEPS[0],
     r"diff-scoped, never whole-repo\.\*\* Repo access\s*\n?> exists for exactly one purpose", re.M,
     "Repo access\n> exists for exactly one purpose",
     "Repo access\n> exists to survey whatever seems related"),
    ("step-01: the diff-scope rule is BLOCKQUOTED, so it reaches the lens", STEPS[0],
     r"^> \*\*Your subject is the diff, never the repository", re.M,
     "> **Your subject is the diff, never the repository",
     "**Your subject is the diff, never the repository"),
    ("step-01: sweeping is forbidden in the lens's own prompt", STEPS[0],
     r"^> specific symbol on a specific changed line\.$", re.M,
     "> specific symbol on a specific changed line.",
     "> whatever else looks worth a look."),
    ("step-01: an empty patch set early-exits the literal lens", STEPS[0],
     r"\*\*An empty patch set → the lens early-exits\.\*\* No changed patches means there is nothing to verify,\s*\nso do not launch it at all",
     re.M,
     "so do not launch it at all", "so launch it against the whole tree"),
    # F6: the early-exit must score `ok`. Scored `dead` it would raise the floor on every clean
    # diff; scored `n/a` it would read as degraded. Both are wrong and both look like a pass here.
    ("step-01: the early-exit is recorded ok, never dead and never n/a", STEPS[0],
     r"record \*\*`ok` with zero findings\*\*, never `dead` and never `n/a`", 0,
     "record **`ok` with zero findings**, never `dead` and never `n/a`",
     "record **`dead`**, like any lens that returned nothing"),
    # The NUMBER, not the headline.
    ("step-01: the literal lens caps at 20 changed files", STEPS[0],
     r"\*\*A 20-file cap\.\*\* Hand over at most \*\*20\*\* changed files", 0,
     "Hand over at most **20** changed files", "Hand over at most **200** changed files"),
    # SCC-147 (rolled in on the operator's ruling): the disclosure names PATHS, never a count.
    # A count was useless twice over — the blockquote orders the lens to NAME what it did not
    # get, and the `standard` top-up is earned by naming a specific withheld file. Neither is
    # possible from a number.
    ("step-01: withheld files are disclosed by NAME, never as a count", STEPS[0],
     r"you MUST tell the lens WHICH files it did not receive — the paths,\s*\nnever just a count",
     re.M,
     "WHICH files it did not receive — the paths,", "how many files it did not receive —"),
    ("step-01: the truncation still reaches the engine's notes", STEPS[0],
     r"Carry the truncation into the engine's returned `notes` yourself", 0,
     "Carry the truncation into the engine's returned `notes` yourself",
     "The truncation needs no note of the engine's own"),
    ("step-01: the lens is told to report truncation FIRST in its output", STEPS[0],
     r"^> your output\*\*, naming what you got and what you did not", re.M,
     "> your output**, naming what you got and what you did not",
     "> your output**, if you consider it worth mentioning"),
    # The THRESHOLD and the DESTINATION, not the headline.
    ("step-01: the literal lens spills above ~9,000 chars to a context file", STEPS[0],
     r"\*\*Spill above ~9,000 chars\.\*\* Past that, write the patch material to a context file in\s*\n`ARTIFACT_DIR`",
     re.M,
     "Past that, write the patch material to a context file in",
     "Past that, inline the patch material rather than writing it to"),

    # lens_budget: defined once, HERE, and NOT the same axis as review_mode. A caller that
    # re-defines a cap — or conflates the two axes — is how cost governance rots overnight.
    ("step-01: the cost axis is named lens_budget and defined once", STEPS[0],
     r"^### `lens_budget` — the literal-correctness lens's cost axis, defined here, once \(SCC-147\)$", re.M,
     "### `lens_budget` — the literal-correctness lens's cost axis, defined here, once (SCC-147)",
     "### `lens_budget` — each caller sets its own"),
    ("step-01: lens_budget is explicitly NOT review_mode", STEPS[0],
     r"⛔ \*\*`lens_budget` is NOT `review_mode`, and the two are independent\.\*\*", 0,
     "**`lens_budget` is NOT `review_mode`, and the two are independent.**",
     "**`lens_budget` is another name for `review_mode`.**"),
    ("step-01: full review_mode plus capped budget is the normal state", STEPS[0],
     r"routinely `review_mode: full`\s*\nand `lens_budget: capped` at the same time", re.M,
     "routinely `review_mode: full`", "never `review_mode: full`"),
    ("step-01: a caller names the budget and never re-defines the caps", STEPS[0],
     r"A caller \*\*names\*\* its `lens_budget`; it never re-defines the caps", 0,
     "A caller **names** its `lens_budget`; it never re-defines the caps",
     "A caller may raise or lower the caps to suit its budget"),
    ("step-01: an unnamed budget defaults to capped, the safe side", STEPS[0],
     r"\*\*A caller that names none gets `capped`\*\*", 0,
     "**A caller that names none gets `capped`**",
     "**A caller that names none gets `standard`**"),
    ("step-01: capped is the autopilot's, with the caps mandatory and no top-up", STEPS[0],
     r"^\|\s*`capped`\s*\|\s*`/cicd-code-review-AP` \(autopilot\)[^|]*\|[^|]*MANDATORY[^|]*\*\*no top-up\*\*",
     re.M,
     "the same caps, MANDATORY, and **no top-up**", "the caps are advisory"),
    ("step-01: standard budget still binds the caps, and its top-up is earned", STEPS[0],
     r"^\|\s*`standard`\s*\|\s*interactive callers\s*\|\s*MANDATORY as written in that lens's Scope section;[^|]*\*\*earn\*\*",
     re.M,
     "| `standard` | interactive callers | MANDATORY as written in that lens's Scope section;",
     "| `standard` | interactive callers | caps are optional;"),

    # SCC-147, second half (rolled in on the operator's ruling): the top-up ROW is definition
    # only — a table cell is unquoted, and this file pins twice that unquoted text never reaches
    # a lens. So for as long as the row was all there was, `standard` and `capped` were
    # behaviourally identical: a lens never told a top-up exists cannot spend one. The clause is
    # now BLOCKQUOTED and routed by budget; these three pin the quote, the routing, and the
    # capped-side absence that IS the `no top-up` enforcement.
    ("step-01: the top-up clause is blockquoted, so it reaches the lens", STEPS[0],
     r"^> \*\*You may earn ONE top-up past the file cap\.\*\*", re.M,
     "> **You may earn ONE top-up past the file cap.**",
     "**You may earn ONE top-up past the file cap.**"),
    ("step-01: the top-up quote is routed to standard runs only", STEPS[0],
     r"you append\s*\nit \*\*only when the caller passed `lens_budget: standard`\*\*", re.M,
     "it **only when the caller passed `lens_budget: standard`**",
     "it **on every run, whatever the budget**"),
    ("step-01: under capped, absence of the clause is the enforcement", STEPS[0],
     r"a lens that was never handed\s*\nthe clause has no top-up to spend", re.M,
     "a lens that was never handed", "a lens may assume a top-up even when it was never handed"),

    # Gate 1 adaptation — without it the lens must DROP the defect class it was added to catch.
    ("step-01: Gate 1 is adapted for the literal lens, and only for it", STEPS[0],
     r"^> \*\*Gate 1 is adapted for you, and only for you\.\*\*", re.M,
     "> **Gate 1 is adapted for you, and only for you.**",
     "> **Gate 1 binds you exactly as it binds every other hunter.**"),
    ("step-01: for always-raised violations the changed line IS the proof", STEPS[0],
     r"\*\*the changed line IS the reachability\s*\n> proof\*\* and you owe no further trace", re.M,
     "**the changed line IS the reachability", "**a full production trace IS the reachability"),
    ("step-01: state-dependent violations still owe the full Gate 1 trace", STEPS[0],
     r"\*\*Gate 1 binds in full\*\* and\s*\n> you owe the ordinary trace\. Gates 2 and 3 bind unchanged", re.M,
     "**Gate 1 binds in full** and", "**Gate 1 is waived** and"),

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
    ("step-01: inline execution must run the blind lens FIRST, on the diff alone", STEPS[0],
     r"run the blind lens \*\*first — on the diff alone, before\s*\nany spec, plan, walkthrough or evidence pack is pulled into context\.\*\*",
     re.M,
     "**first — on the diff alone, before", "**last — after everything else, including"),
    # ⛔ RETIRED BY SCC-203, and the retirement is the point. This used to pin
    # `ok (not blind — context held <what>)` as the honest way to record a lens that ran without
    # its defining property. The operator ruled that state out entirely: a roster carrying it
    # reports a review that was more independent than it was, which is worse than a smaller
    # review. The state a contaminated blind lens reaches is now `n/a`, and it is not counted.
    ("step-01: a contaminated blind lens is DROPPED and recorded n/a", STEPS[0],
     r"`blind-hunter · n/a — context contaminated \(<what it held>\)`", 0,
     "`blind-hunter · n/a — context contaminated (<what it held>)`", "`ok`"),
    ("step-01: the retired `ok (not blind ...)` state is gone from the engine", STEPS[0],
     r"that state is \*\*retired\*\*", 0,
     "that state is **retired**", "that state is still available"),

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

    # ── SCC-147: the INTERACTIVE callers name their budget, in their own invocation tables ────
    # The counter-example here is `capped` — not a nonsense string — because `capped` is the
    # exact value these two silently inherited by naming nothing. A row that says `capped`
    # reads as deliberate and is the defect; the check has to reject it, not just notice an
    # absent word.
    #
    # ⛔ The pattern is anchored to the ENGINE-INVOCATION TABLE, and that shape is the whole
    # point. This lane's review ran two mutants against the first version — a bare
    # `^\|\s*`lens_budget`\s*\|\s*`standard`` — and BOTH survived with every case green:
    #   A. move the row out of the invocation table into any other table in the file. The
    #      caller then passes NO budget and silently takes `capped` — the exact defect this
    #      ticket exists to fix — while a file-wide grep still sees a matching row somewhere.
    #   B. leave the row where it is and append "— but pass `capped` when the diff is large"
    #      INSIDE the same cell, which the old pattern never read: it stopped at the value
    #      token and never closed the cell.
    # `^\|\s*`HEAD_SHA`` + `(?:\|[^\n]*\n)*?` binds the row to the same CONTIGUOUS run of table
    # rows as a required engine input — a blank line or any prose ends the run, so an appendix
    # table cannot satisfy it. That kills A. The tempered `(?:(?!capped)[^|\n])*\|` reads to the
    # cell's closing pipe and refuses `capped` anywhere inside it. That kills B — and it is why
    # neither row's prose may name `capped`: they say "the autopilot's budget" instead.
    # This is the `source-grep-guards-cannot-see-order` class caught inside a guard written to
    # close SCC-126's F7, which is the same defect one layer up.
    ("interactive caller /cicd-code-review: invocation table passes lens_budget standard",
     CICD_CMD,
     r"^\|\s*`HEAD_SHA`[^\n]*\n(?:\|[^\n]*\n)*?\|\s*`lens_budget`\s*\|\s*`standard`"
     r"(?:(?!capped)[^|\n])*\|", re.M,
     "| `lens_budget` | `standard`", "| `lens_budget` | `capped`"),
    ("interactive caller /smh-code-review: invocation table passes lens_budget standard",
     SMH_CMD,
     r"^\|\s*`HEAD_SHA`[^\n]*\n(?:\|[^\n]*\n)*?\|\s*`lens_budget`\s*\|\s*`standard`"
     r"(?:(?!capped)[^|\n])*\|", re.M,
     "| `lens_budget` | `standard`", "| `lens_budget` | `capped`"),

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
    ("step-03: decision_needed bucket is defined", STEPS[2],
     r"^- \*\*decision_needed\*\* —", re.M,
     "- **decision_needed** — an ambiguous choice", "- ~~decision_needed~~ — removed,"),
    ("step-03: patch bucket is defined", STEPS[2],
     r"^- \*\*patch\*\* —", re.M,
     "- **patch** — a real issue", "- ~~patch~~ — removed,"),
    ("step-03: defer bucket is defined", STEPS[2],
     r"^- \*\*defer\*\* —", re.M,
     "- **defer** — real, worth fixing, **and this lane", "- ~~defer~~ — removed,"),
    ("step-03: dismiss bucket is defined", STEPS[2],
     r"^- \*\*dismiss\*\* —", re.M,
     "- **dismiss** — noise, false positive", "- ~~dismiss~~ — removed,"),
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
    ("step-03: a revised severity outranks the hunter", STEPS[2],
     r"\*\*A revised severity outranks the hunter's\.\*\*", 0,
     "outranks the hunter's", "is ignored in favour of the hunter's"),
    ("step-03: an unverified finding keeps the hunter's severity", STEPS[2],
     r"⚠ \*\*A finding with no revised severity keeps the hunter's\*\*", 0,
     "**A finding with no revised severity keeps the hunter's**",
     "**A finding with no revised severity is dropped**"),
    ("step-03: an unverified finding is not a softer finding", STEPS[2],
     r"an\s*\n?unverified finding is not a softer finding", re.M,
     "unverified finding is not a softer finding", "unverified finding is a softer finding"),
    ("step-03: the engine gates as hard as the path it replaces", STEPS[2],
     r"gates exactly as hard as the path it replaces", 0,
     "exactly as hard as the path it replaces", "far softer than the path it replaces"),
    ("step-03: compound is a first-class finding source", STEPS[2],
     r"^\|\s*`source`\s*\|[^|]*`compound`[^|]*\|", re.M,
     "· `compound`, or merged", ", or merged"),
    ("step-03: no-spec keeps the decision instead of parking it as a blocker-less defer", STEPS[2],
     r"becomes `patch` if the fix is\nunambiguous; otherwise it is STILL `decision_needed`", re.M,
     "unambiguous; otherwise it is STILL `decision_needed`",
     "unambiguous, otherwise `defer`"),
    ("step-03: dismiss is counted and a relevance kill is named", STEPS[2],
     r"\*\*`dismiss` is counted — and a relevance kill is counted AND named\.\*\*", 0,
     "**`dismiss` is counted — and a relevance kill is counted AND named.**",
     "**`dismiss` and `defer` are both discarded silently.**"),
    # ── step-03: the relevance gate (SCC-160, operator ruling 2026-08-15) ───────────────────
    # TRUE is necessary, not sufficient: hunters have finding-goals, so their volume is a
    # success metric, never a work queue. These three pins bind the ruling's load-bearing
    # sentences: the gate exists, severity cannot bypass it, and the residue class is dead.
    ("step-03: the relevance gate exists — TRUE is not WORTH DOING", STEPS[2],
     r"### The relevance gate — TRUE is not the same as WORTH DOING", 0,
     "### The relevance gate — TRUE is not the same as WORTH DOING",
     "### The relevance pass — everything TRUE is implemented"),
    ("step-03: severity does not bypass the relevance gate", STEPS[2],
     r"Severity does not\s+bypass the gate — an `important` with no realistic path is still dead", 0,
     "Severity does not\nbypass the gate — an `important` with no realistic path is still dead",
     "Severity bypasses the gate — an `important` is implemented on rank alone"),
    ("step-03: the residue class is retired", STEPS[2],
     r"⛔ \*\*The residue class is RETIRED\.\*\*", 0,
     "⛔ **The residue class is RETIRED.**",
     "The residue pile is owed to ONE follow-on ticket"),
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
    ("step-03: survivors are fixed in this lane before the verdict", STEPS[2],
     r"\*\*A finding that survives\s+this gate is fixed in this lane, in this thread, before the verdict — full stop\.\*\*", 0,
     "**A finding that survives\nthis gate is fixed in this lane, in this thread, before the verdict — full stop.**",
     "A finding that survives this gate is fixed in this lane, or ledgered, or — rarely — proposed as a decided chore ticket."),
    ("step-03: defer is a structural blocker, not pre-existing", STEPS[2],
     r"^- \*\*defer\*\* — real, worth fixing, \*\*and this lane structurally cannot hold the fix\*\*", re.M,
     "- **defer** — real, worth fixing, **and this lane structurally cannot hold the fix**",
     "- **defer** — real, worth fixing, but pre-existing and not caused by this change."),
    ("step-03: critical maps to FAIL", STEPS[2],
     r"^\|\s*`critical`, in `decision_needed` or `patch`\s*\|\s*\*\*FAIL\*\*\s*\|", re.M,
     "| `critical`, in `decision_needed` or `patch` | **FAIL** |",
     "| `critical`, in `decision_needed` or `patch` | **never gate** |"),
    ("step-03: important maps to CONCERNS", STEPS[2],
     r"^\|\s*`important`, in `decision_needed` or `patch`\s*\|\s*\*\*CONCERNS\*\*\s*\|", re.M,
     "| `important`, in `decision_needed` or `patch` | **CONCERNS** |",
     "| `important`, in `decision_needed` or `patch` | **FAIL** |"),
    ("step-03: suggestion and nitpick never gate", STEPS[2],
     r"^\|\s*`suggestion` or `nitpick`, any bucket\s*\|\s*\*\*never gate\*\*", re.M,
     "| `suggestion` or `nitpick`, any bucket | **never gate**",
     "| `suggestion` or `nitpick`, any bucket | **FAIL**"),
    ("step-03: a deferred finding never gates", STEPS[2],
     r"^\|\s*anything in `defer`\s*\|\s*\*\*never gate\*\*", re.M,
     "| anything in `defer` | **never gate**", "| anything in `defer` | **FAIL**"),
    ("step-03: only a still-dead lens appears in the table", STEPS[2],
     r"^\|\s*a lens still `dead` after retry AND inline rerun\s*\|\s*\*\*CONCERNS\*\*\s*\|", re.M,
     "a lens still `dead` after retry AND inline rerun", "any lens that errored at all"),
    # step-03 §5 calls itself "the single definition; every caller reads it rather than inventing
    # its own". Step-02 promises CONCERNS for a dead ROLE, and with no row here that promise was
    # unreachable — the orchestrator would apply the single definition, find nothing, return none.
    ("step-03: a dead step-2 role raises the floor too", STEPS[2],
     r"^\|\s*a step-2 role still `dead` after retry AND inline rerun\s*\|\s*\*\*CONCERNS\*\*\s*\|",
     re.M, "| a step-2 role still `dead` after retry AND inline rerun | **CONCERNS** |",
     "| a step-2 role still `dead` after retry AND inline rerun | **never gate** |"),
    ("step-03: a recovered or gate-skipped role never gates", STEPS[2],
     r"neither does a\s*\n?step-2 role that recovered inline — including one recorded `cold \(no dossier\)`",
     re.M, "step-2 role that recovered inline — including one recorded `cold (no dossier)`",
     "step-2 role that died outright"),
    ("step-03: the floor is the most severe row", STEPS[2],
     r"The floor is the \*\*most severe\*\* applicable row", 0,
     "the **most severe** applicable row", "the **least severe** applicable row"),

    # ── step-04: the record, and the boundary held positively ───────────────────────────────
    ("step-04: an absent sink is reported, never guessed", STEPS[3],
     r"do not pick a file", 0, "do not pick a file", "pick any file you like"),
    ("step-04: decision findings are written unresolved", STEPS[3],
     r"^- \[ \] \[Review\]\[Decision\]", re.M,
     "- [ ] [Review][Decision]", "- [x] [Review][Decision]"),
    ("step-04: patch findings are written unresolved", STEPS[3],
     r"^- \[ \] \[Review\]\[Patch\]", re.M,
     "- [ ] [Review][Patch]", "- [x] [Review][Patch]"),
    ("step-04: deferred findings are written unresolved", STEPS[3],
     r"^- \[ \] \[Review\]\[Defer\]", re.M,
     "- [ ] [Review][Defer]", "- [x] [Review][Defer]"),
    ("step-04: deferred work is routed out of the review", STEPS[3],
     r"Every `defer` also gets a bullet in `DEFERRED_WORK`", 0,
     "also gets a bullet in `DEFERRED_WORK`", "is dropped after the review"),
    ("step-04: dismissed findings are counted, not written", STEPS[3],
     r"Dismissed findings are \*\*not\*\* written here", 0,
     "are **not** written here", "are written here"),
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
    ("step-04 boundary: never pauses the caller for a decision", STEPS[3],
     r"^- \*\*It never pauses the caller.s flow for a decision\.\*\*", re.M,
     "It never pauses the caller's flow", "It pauses the caller's flow"),
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
    # ⭐ THREE paragraphs, not two. The `rather than faking it` clause — where an `inline` caller
    # holding the plan DROPS the Blind Hunter — was carried by both callers and pinned by nothing:
    # no CHECKS row named it, and this extractor did not match it, so either caller could have
    # lost the consequence while every check stayed green. It is part of the same law (what a
    # runtime answer OBLIGES), so it belongs in the same byte-identity comparison.
    def _law_of(txt: str) -> str:
        out = []
        for para in txt.split("\n\n"):
            if ("**capability**" in para or "IS a user request" in para
                    or "may not record a bare" in para
                    or "rather than faking it" in para):
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
                        ("rather than faking it", "a contaminated Blind Hunter is DROPPED")):
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
    # A SECOND, contradictory row elsewhere in the same file is invisible to `re.search`, which
    # returns on first match. The review proved it: a later "## Step 3.9 — budget override"
    # section carrying `| `lens_budget` | `capped` — overrides the Step 1 table |` left the
    # Step 1 row untouched and the whole gate green, while an LLM reading the command
    # top-to-bottom passes `capped`. So the rows are COUNTED, not just found.
    for rel in (CICD_CMD, SMH_CMD):
        txt = texts.get(rel) or read(ROOT / rel)
        n = len(re.findall(r"^\|\s*`lens_budget`\s*\|", txt, re.M))
        c.check(f"{Path(rel).name} carries exactly ONE lens_budget row", n == 1,
                "" if n == 1 else f"found {n} — a second row can contradict the first")
    # Every caller must NAME a budget. Which value is each caller's own business — the AP twin's
    # `capped` is as correct as an interactive `standard` — but naming nothing is the defect.
    for rel in discovered:
        txt = texts.get(rel) or read(ROOT / rel)
        named = re.search(r"lens_budget`?\s*[|:]\s*`?(standard|capped)\b", txt) is not None
        c.check(f"{Path(rel).name} names a lens_budget explicitly", named,
                "" if named else "names none, so it silently inherits `capped` (SCC-147)")

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
    # `/smh-quick-dev` is NOT an engine caller — it never invokes the skill, so it is correctly
    # absent from CALLER_FILES and from the discovery check above. It is pinned here anyway,
    # because it owns the Task lane's walkthrough header: if it does not write `review-runtime:`
    # at Step 0, the Task lane's review is judged against a header nobody recorded.
    qd = ROOT / ".agents/commands/smh-quick-dev.md"
    qd_txt = read(qd) if qd.is_file() else ""
    c.check("/smh-quick-dev exists with a body", len(qd_txt.strip()) > 200,
            "" if qd_txt else "absent")
    step0 = re.search(r"^## Step 0 —[\s\S]*?^## Step 0\.5 ", qd_txt, re.M)
    c.check("/smh-quick-dev records review-runtime inside Step 0, before the worktree exists",
            step0 is not None and "review-runtime:" in step0.group(0),
            "" if step0 else "Step 0 / Step 0.5 headings not found — the anchor moved")
    named = re.search(r"`review-runtime:`[^\n]*header", qd_txt) is not None
    c.check("/smh-quick-dev's walkthrough contents name the header it must carry", named,
            "" if named else "Step 5 lists the walkthrough's sections; a header no section "
                             "names is a header nobody writes")

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
