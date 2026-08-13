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
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]
MASTER = ROOT / ".agents" / "skills" / "code-review-engine"
CACHE = ROOT / ".claude" / "skills" / "code-review-engine"

SKILL = "SKILL.md"
STEPS = ("steps/step-01-review.md", "steps/step-02-verify.md",
         "steps/step-03-triage.md", "steps/step-04-record.md")
ENGINE_FILES = (SKILL,) + STEPS

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
    ("skill: return block counts applicable lenses", SKILL,
     r"^lenses_run:\s+<n>/<applicable>", re.M,
     "lenses_run:      <n>/<applicable>", "lenses_run:      <n>/<total>"),

    # ── step-01: the fan-out table, the failure contract, NA-vs-dead ────────────────────────
    ("step-01: Blind Hunter is a lens row that always runs", STEPS[0],
     r"^\|\s*\*\*Blind Hunter\*\*\s*\|[^|]*\|\s*always\s*\|", re.M,
     "| **Blind Hunter** | `DIFF` only", "| ~~Blind Hunter~~ | not run,"),
    ("step-01: Edge Case Hunter is a lens row that always runs", STEPS[0],
     r"^\|\s*\*\*Edge Case Hunter\*\*\s*\|[^|]*\|\s*always\s*\|", re.M,
     "| **Edge Case Hunter** | `DIFF` + read access", "| ~~Edge Case Hunter~~ | skipped,"),
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
    ("step-01: only a still-dead lens raises the floor", STEPS[0],
     r"^4\. \*\*Only a lens that is still dead after BOTH the retry and the inline rerun raises",
     re.M, "raises the floor", "leaves the floor alone"),
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
    ("step-01: a spec-less review reports 3/3, not 3/4", STEPS[0],
     r"reports `3/3`, never `3/4`", 0,
     "reports `3/3`, never `3/4`", "reports `3/4`, never `3/3`"),

    # ── step-01 (SCC-125): the hunter contract — the three false-positive gates ─────────────
    ("step-01: the hunter contract binds hunter lenses, now and later", STEPS[0],
     r"^## The hunter contract — binding on every hunter lens, now and later$", re.M,
     "binding on every hunter lens, now and later",
     "binding on every lens, auditors included"),
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
     r"^\|\s*\*\*Blind Hunter\*\*\s*\|[^|]*\|\s*always\s*\|[^|]*\|\s*\*\*never\*\*\s*\|$", re.M,
     "| **never** |", "| yes |"),
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
    ("step-01: the recall cost of a worthiness gate is recorded", STEPS[0],
     r"recall falls from 0\.69 to 0\.52", 0,
     "recall falls from 0.69 to 0.52", "recall is unaffected"),

    # ── step-02: honest scaffold-stage pass-through ─────────────────────────────────────────
    ("step-02: findings carry forward unverified", STEPS[1],
     r"^1\. Carry every step-1 finding forward \*\*unchanged\*\*, marked `verification: none`",
     re.M, "marked `verification: none`", "marked `verification: confirmed`"),
    ("step-02: no revised severity is invented", STEPS[1],
     r"^2\. Set no `revised_severity` on anything", re.M,
     "Set no `revised_severity` on anything", "Set a `revised_severity` on everything"),
    ("step-02: the note names the missing pass", STEPS[1],
     r"`verification pass not yet installed \(SCC-127\)`", 0,
     "verification pass not yet installed (SCC-127)", "verification pass complete"),
    ("step-02: improvising the verifier is forbidden", STEPS[1],
     r"\*\*Do not improvise the verification roles\.\*\*", 0,
     "Do not improvise the verification roles", "Improvise the verification roles"),
    ("step-02: the future rules are marked not-yet-in-force", STEPS[1],
     r"The rules in this section describe behavior that does not exist yet", 0,
     "does not exist yet", "is in force today"),

    # ── step-03: buckets, alias map, and the severity-to-verdict table ──────────────────────
    ("step-03: decision_needed bucket is defined", STEPS[2],
     r"^- \*\*decision_needed\*\* —", re.M,
     "- **decision_needed** — an ambiguous choice", "- ~~decision_needed~~ — removed,"),
    ("step-03: patch bucket is defined", STEPS[2],
     r"^- \*\*patch\*\* —", re.M,
     "- **patch** — a real issue", "- ~~patch~~ — removed,"),
    ("step-03: defer bucket is defined", STEPS[2],
     r"^- \*\*defer\*\* —", re.M,
     "- **defer** — real, but pre-existing", "- ~~defer~~ — removed,"),
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
    ("step-03: scaffold stage gates as hard as the path it replaces", STEPS[2],
     r"gates exactly as hard as the path it replaces", 0,
     "exactly as hard as the path it replaces", "far softer than the path it replaces"),
    ("step-03: no-spec reclassifies decisions rather than parking them", STEPS[2],
     r"becomes `patch` if the fix is\nunambiguous, otherwise `defer`", re.M,
     "becomes `patch` if the fix is", "is discarded rather than being"),
    ("step-03: dismiss is counted and defer is recorded", STEPS[2],
     r"\*\*`dismiss` is counted, `defer` is recorded\.\*\*", 0,
     "`dismiss` is counted, `defer` is recorded", "`dismiss` and `defer` are both discarded"),
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
    c = Cases("review engine (SCC-122 scaffold)")

    # ── 1. Structure ──────────────────────────────────────────────────────────────────────
    for rel in ENGINE_FILES:
        p = MASTER / rel
        c.check(f"{rel} exists with a body", has_body(p),
                "" if has_body(p) else ("absent" if not p.is_file() else "present but under 200 chars"))

    texts = {rel: (read(MASTER / rel) if (MASTER / rel).is_file() else "") for rel in ENGINE_FILES}

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

    return c.finish()


if __name__ == "__main__":
    raise SystemExit(main())
