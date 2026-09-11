"""SCC-447 — the disposition doctrine: reproduce or drop, then fix, one review per lane.

⛔ WHAT THIS FILE EXISTS FOR, measured. The review engine had no stop condition an agent could
reach on its own. Its lenses are instructed to be exhaustive and are judged by what they return,
the assessor was told to fix everything that survived triage, the verdict floor was computed
BEFORE the fixes and never moved with them, and the preflight's remedy for FAIL said "re-run the
review". Over every review on disk (138 with a verdict, 88 with per-lens ledgers): 17.9 fixes per
review, 52% of them on severities that can never block, re-review converting a non-PASS to PASS 1
time in 7, the verify wave refuting 2 findings in 18 reviews. SCC-441 ran that machine three times
over a 155-file diff and burned a week of credit without closing.

The doctrine that replaces it is four sentences, and this file is what holds each of them:

  1. **Reproduce or drop.** A `critical` or `important` with no receipt on disk does not exist.
  2. **Fix what reproduced.** A reproduced `critical` or `important` is fixed in the lane with a
     pin. A fix the agent may not apply alone is written as a patch and `held`; nothing is
     escalated and nothing is deferred (operator ruling 2026-09-11 — both buckets struck the day
     the first cut of this doctrine landed, because each put a reproduced defect in front of him).
  3. **The floor is computed AT THE STAMP, on rows still OPEN.** A row closed by a fix and a green
     pin does not gate. CONCERNS has exactly two grounds — coverage (a dead lens) and authority (a
     held fix) — and ships on the operator's word; FAIL is the blocker.
  4. **One review per lane.** The retest is the pins plus the suite, never a second fan-out.

  ── WHY THIS FILE IS SHAPED THE WAY IT IS (the SCC-122 pattern, inherited) ───────────────────
A keyword grep is not a guard: five keyword-stuffed stubs instructing the exact OPPOSITE of the
engine's rules once scored 80/80 on the first version of `test_review_engine.py`. So every content
check here obeys the same three disciplines that repair proved:

  1. **Checks bind a RELATIONSHIP, not a vocabulary.** `important` and `fixed` both appearing
     somewhere proves nothing; a table row mapping the one to the other proves the mapping.
  2. **Every check ships a COUNTER-EXAMPLE and is proven to reject it.** The harness applies the
     mutation in memory and requires the check to go red. A check that survives its own
     counter-example is reported as a failure here. The counter must also APPLY — a mutation whose
     target string is absent would make the proof vacuous, so that is asserted too.
  3. **Prohibitions are asserted POSITIVELY.** "The wave is retired" contains "the wave"; banning
     a word in a file whose job is to name what it retired cannot work. The retired machinery is
     held by requiring the retirement note that names it, plus identifier bans (§5) that scan for
     the SPELLINGS a live caller would have to use — `lens_budget:`, `review_level:` — which a
     retirement note never writes.

Stdlib only, no pytest — same constraint as every sibling here.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _harness import Cases

ROOT = Path(__file__).resolve().parents[3]

RULE = ".agents/rules/code-standards.md"
RULE_TWIN = ".claude/rules/code-standards.md"

ENGINE = ".agents/skills/code-review-engine"
CACHE = ".claude/skills/code-review-engine"
SKILL = f"{ENGINE}/SKILL.md"
S1 = f"{ENGINE}/steps/step-01-review.md"
S2 = f"{ENGINE}/steps/step-02-verify.md"
S3 = f"{ENGINE}/steps/step-03-triage.md"
S4 = f"{ENGINE}/steps/step-04-record.md"
ENGINE_RELS = ("SKILL.md", "steps/step-01-review.md", "steps/step-02-verify.md",
               "steps/step-03-triage.md", "steps/step-04-record.md")

# (id, file, regex, flags, counter_old, counter_new)
# counter_old MUST be present in the real file and counter_new MUST break the regex.

# ── BLOCK A — the doctrine's home: code-standards.md §6.5 and §7 ───────────────────────────────
#
# ⛔ WHY THE RULE FILE AND NOT THE ENGINE. §6.5 governs every command that produces findings —
# both code reviews, both clean-code audits, both self-audits — and §7 already owns the
# FAIL-vs-CONCERNS split. An engine step file is law for one caller; this rule is law for all of
# them, which is why SCC-205 hoisted the disposition ruling here in the first place.
CHECKS_A: tuple[tuple[str, str, str, int, str, str], ...] = (
    # Gate 0 — the reproduction gate, and its evidence shape
    ("§6.5: a critical/important that did not reproduce DOES NOT EXIST", RULE,
     r"`critical` or `important` that did not reproduce does not exist", 0,
     "that did not reproduce does not exist",
     "that did not reproduce is downgraded to `suggestion`"),
    ("§6.5: the evidence is a receipt written by repro_receipt.py, per finding id", RULE,
     r"repro_receipt\.py run --root <artifacts> --id <finding-id>", 0,
     "repro_receipt.py run --root <artifacts> --id <finding-id>",
     "repro_receipt.py record --root <artifacts>"),
    ("§6.5: no --result flag — a receipt implies EXECUTION", RULE,
     r"no `--result` flag — a receipt implies execution", 0,
     "There is no `--result` flag — a receipt implies execution",
     "Pass `--result reproduced` when you are confident"),
    ("§6.5: a finding whose command does not fail is DROPPED and counted", RULE,
     r"does not fail when it is run, is \*\*dropped and counted\*\*", 0,
     "does not fail when it is run, is **dropped and counted**",
     "does not fail when it is run, is still worth reporting"),
    # The action policy — one row per severity, each binding severity to ACTION
    ("§6.5 policy: a reproduced CRITICAL or IMPORTANT is FIXED in this lane, with a pin", RULE,
     r"^\|\s*reproduced `critical` or `important`\s*\|[^|]*fixes it, in this lane, with a pin"
     r"[^|]*\|[^|]*`fixed @<sha> · pin <test>\[:<case>\] · repro <id>`", re.M,
     "| reproduced `critical` or `important` | fixes it, in this lane, with a pin",
     "| reproduced `critical` or `important` | hands it to the operator"),
    # ⛔ Operator ruling 2026-09-11: the ESCALATE row this replaces handed a reproduced `important`
    # to him with a recommendation — a finding to read, which is the review he asked to be designed
    # out of. The one row that reaches him now is a fix the agent may not APPLY alone, and it
    # reaches him written, never as a question.
    ("§6.5 policy: a fix the agent may not apply alone is HELD as a written patch, never asked", RULE,
     r"^\|\s*reproduced, and the fix needs the operator's permission[^|]*\|[^|]*writes the fix "
     r"and its pin as a patch[^|]*does \*\*not\*\* apply it[^|]*\|"
     r"\s*`held — <reason> · repro <id> · patch <path>`", re.M,
     "writes the fix and its pin as a patch",
     "asks the operator what to do"),
    ("§6.5 policy: no reproduction → dropped, counted, never written up individually", RULE,
     r"^\|\s*`critical` or `important` that did not reproduce\s*\|[^|]*dropped, counted[^|]*\|"
     r"\s*`dropped — no reproduction`", re.M,
     "| `critical` or `important` that did not reproduce | dropped, counted",
     "| `critical` or `important` that did not reproduce | investigated further"),
    ("§6.5 policy: suggestion/nitpick is a COUNT and nothing else", RULE,
     r"^\|\s*`suggestion` or `nitpick`\s*\|\s*nothing at all; a count\s*\|\s*`recorded`", re.M,
     "| `suggestion` or `nitpick` | nothing at all; a count | `recorded` |",
     "| `suggestion` or `nitpick` | fix the cheap ones | `fixed` |"),
    # The DEFER row this replaces was a parking lot with a nicer name: "this lane structurally
    # cannot hold the fix" was the excuse that filled it. A defect outside the lane's files was
    # never a disposition of the review — it is out-of-lane work with the ladder it always had.
    ("§6.5 policy: a defect outside this lane's files is OUT-OF-LANE, down the consolidation ladder", RULE,
     r"^\|\s*reproduced, in a file this lane did not touch[^|]*\|[^|]*`work-consolidation` ladder "
     r"with its receipt attached\s*\|\s*`out-of-lane — <where it went>`", re.M,
     "`work-consolidation` ladder with its receipt attached",
     "deferred ledger, against a named blocker"),
    ("§6.5: a reproduced finding is FIXED — no third bucket, and both retired ones are named", RULE,
     r"\*\*A reproduced finding is fixed\. There is no third bucket\.\*\*[\s\S]{0,400}?"
     r"`escalate` bucket[\s\S]{0,300}?`defer` bucket", 0,
     "There is no third bucket.",
     "The agent chooses a bucket."),
    ("§6.5: `held` is never a question — the patch is written and applies on the tip", RULE,
     r"\*\*`held` is the one row the operator sees, and it is never a question\.\*\*"
     r"[\s\S]{0,900}?`git apply --check` passes on the lane tip", 0,
     "and it is never a question",
     "and it is his question to answer"),
    # §7 — the floor, the verdict meanings, and the one-review rule
    ("§7: FAIL is an OPEN REPRODUCED critical at the stamp, whatever the reason", RULE,
     r"^\|\s*\*\*FAIL\*\*\s*\|\s*An \*\*open reproduced\*\* `critical` at the stamp, "
     r"whatever the reason[^|]*with its receipt on disk", re.M,
     "| **FAIL** | An **open reproduced** `critical` at the stamp, whatever the reason",
     "| **FAIL** | Anything a lens labelled `critical`"),
    # ⛔ THE GROUNDS FOR CONCERNS, defined (operator, 2026-09-11: "What would be fair grounds
    # based off previous evidence to flag the CONCERNS, instead of PASS ... we have to define that
    # now"). Two, both evidence, and the row says "Nothing else" so a third cannot drift in.
    ("§7: CONCERNS has exactly TWO grounds — coverage (a dead lens) and authority (a held fix)", RULE,
     r"^\|\s*\*\*CONCERNS\*\*\s*\|\s*Exactly two grounds, both evidence\. \*\*Coverage:\*\* "
     r"a lens still `dead`[^|]*\*\*Authority:\*\* an \*\*open reproduced\*\* `important` `held`"
     r"[^|]*Nothing else\.", re.M,
     "Nothing else.",
     "Also any judgment call a lens raised."),
    ("§7: taste never raises the floor — §1/§2 judgment calls are counts, not a verdict", RULE,
     r"Taste does not — it is recorded, never a verdict: §1 comment-contract gaps and §2 judgment "
     r"calls[\s\S]{0,200}?no longer raise the floor", 0,
     "no longer raise the floor",
     "raise the floor to CONCERNS"),
    ("§7: PASS needs no OPEN reproduced finding (not zero findings)", RULE,
     r"^\|\s*\*\*PASS\*\*\s*\|[^|]*no open reproduced finding", re.M,
     "and no open reproduced finding.",
     "and no findings at all."),
    ("§7: the floor is computed AT THE STAMP on rows still OPEN", RULE,
     r"The floor is computed AT THE STAMP, on the rows that are still OPEN \(SCC-447\)", 0,
     "The floor is computed AT THE STAMP, on the rows that are still OPEN (SCC-447)",
     "The floor is computed at triage, from what the lenses returned"),
    ("§7: a row closed by a fix and a green pin does not hold the lane", RULE,
     r"A row closed by a\nfix and a green pin is not a reason to hold a lane", 0,
     "A row closed by a\nfix and a green pin is not a reason to hold a lane",
     "Every row a lens returned holds the lane\nuntil a fresh review clears it"),
    ("§7: CONCERNS SHIPS on the operator's word; FAIL is the blocker", RULE,
     r"\*\*CONCERNS is a shippable verdict, and the go/no-go is the operator's word\.\*\*", 0,
     "**CONCERNS is a shippable verdict, and the go/no-go is the operator's word.**",
     "**CONCERNS does not ship by itself.**"),
    ("§7: no command or agent may treat CONCERNS as a blocker on its own authority", RULE,
     r"no command, door or agent may treat it as a blocker on its own authority", 0,
     "no command, door or agent may treat it as a blocker on its own authority",
     "a door may hold the lane until it is cleared"),
    ("§7: ONE review per lane — the retest is pins plus the suite, not a fan-out", RULE,
     r"\*\*One review per lane\.\*\* The lenses run ONCE\.", 0,
     "**One review per lane.** The lenses run ONCE.",
     "**Re-review after every fix batch.** The lenses run again."),
    ("§7: the retest is the named pins plus ONE suite run, never a second fan-out", RULE,
     r"the pins\nnamed in the `fixed` rows plus the enforcement suite once through the receipt "
     r"writer — never a second\nfan-out", 0,
     "never a second\nfan-out",
     "then a second\nfan-out"),
    ("§7: a second full roster needs the OPERATOR's written word", RULE,
     r"A second full roster needs the operator's written word, and `walkthrough_roster\.py` refuses",
     0,
     "A second full roster needs the operator's written word",
     "A second full roster is the agent's call"),
)

# ── BLOCK B — the engine's four steps carry the same doctrine ──────────────────────────────────
CHECKS_B: tuple[tuple[str, str, str, int, str, str], ...] = (
    # step-01: the roster, and the reproduction field every lens owes
    ("step-01: Edge Case Hunter runs ALWAYS and owes a reproduction field", S1,
     r"^\|\s*\*\*Edge Case Hunter\*\*\s*\|[^|]*\|[^|]*\|\s*always\s*\|[^|]*\|"
     r"\s*required on every `critical`/`important`\s*\|", re.M,
     "| **Edge Case Hunter** | `DIFF` + read access to `REPO` | own worktree copy "
     "(`isolation: \"worktree\"`) | always |",
     "| **Edge Case Hunter** | `DIFF` + read access to `REPO` | own worktree copy "
     "(`isolation: \"worktree\"`) | standard level (quick skips it) |"),
    ("step-01: Acceptance Auditor is full-mode only and owes a reproduction field", S1,
     r"^\|\s*\*\*Acceptance Auditor\*\*\s*\|[^|]*\|[^|]*\|\s*`review_mode: full` only\s*\|[^|]*\|"
     r"\s*required on every `critical`/`important`\s*\|", re.M,
     "| **Acceptance Auditor** | `DIFF` + `STORY_FILE` + any context docs",
     "| **Acceptance Auditor (optional)** | `DIFF` + `STORY_FILE` + any context docs"),
    ("step-01: Test-Adequacy Auditor runs ALWAYS and owes a reproduction field", S1,
     r"^\|\s*\*\*Test-Adequacy Auditor\*\*\s*\|[^|]*\|[^|]*\|\s*always\s*\|[^|]*\|"
     r"\s*required on every `critical`/`important`\s*\|", re.M,
     # ⛔ The mutation must hit a cell the regex READS. The first cut of this counter-example
     # rewrote the `Gets` cell, which the regex spans with `[^|]*` — so the check survived it and
     # the anti-vacuity row is what said so. The binding here is lens → `always`, so that is the
     # cell the counter has to move.
     "| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | own worktree copy "
     "(`isolation: \"worktree\"`) | always |",
     "| **Test-Adequacy Auditor** | `DIFF` + read access to `REPO` | own worktree copy "
     "(`isolation: \"worktree\"`) | `review_mode: full` only |"),
    ("step-01: the roster is CLOSED at three, and the retirement is measured", S1,
     r"\*\*Three lenses, and the roster is closed \(SCC-447\)\.\*\*", 0,
     "**Three lenses, and the roster is closed (SCC-447).**",
     "**Three lenses for now, and more may be added when useful.**"),
    ("step-01: the retirement names every retired piece by name", S1,
     r"The Blind Hunter, the Literal-Correctness\nHunter, the two `review_level` levels, "
     r"`lens_budget`, the `EVIDENCE_PACK` priming and the step-2 verify\nwave are \*\*retired\*\*",
     0,
     "wave are **retired**",
     "wave are **optional**"),
    ("step-01: a lens comes back by MEASUREMENT, never by argument", S1,
     r"A lens is added back by measurement, never by argument\.", 0,
     "A lens is added back by measurement, never by argument.",
     "A lens is added back whenever a reviewer asks for it."),
    ("step-01 hunter contract: critical/important MUST carry a runnable reproduction", S1,
     r"^> - \*\*A `critical` or `important` MUST carry a runnable reproduction\.\*\* Two fields",
     re.M,
     "> - **A `critical` or `important` MUST carry a runnable reproduction.** Two fields",
     "> - **A `critical` or `important` SHOULD carry a reproduction where practical.** Two fields"),
    ("step-01 hunter contract: both fields are named, in the finding", S1,
     r"`reproduce: <command>` — run from the repo root — and\n"
     r">\s*`expected_wrong_output: <what it prints or does that is wrong>`", 0,
     "`expected_wrong_output: <what it prints or does that is wrong>`",
     "`notes: <anything else worth saying>`"),
    ("step-01 hunter contract: without both fields it is DROPPED UNREAD, not downgraded", S1,
     r"without both fields is \*\*dropped unread\*\*; it is not downgraded", 0,
     "without both fields is **dropped unread**; it is not downgraded",
     "without both fields is **downgraded to `suggestion`**; it is not dropped"),
    # ⭐ THE PART THAT KILLS A TRIVIAL FINDING BEFORE IT IS EVER WRITTEN (operator, 2026-09-11:
    # "if the reporting agent had to actually have evidence and recreate the issue they are
    # reporting … it would not lead to all the trivial findings"). The lens INHERITS full tools
    # and holds its own worktree copy, so it can run the command it just wrote. Requiring it
    # prices the finding at the moment the finding is cheapest to abandon: the lens already has
    # the file open and the reasoning in context, and the assessor has neither.
    ("step-01 hunter contract: the LENS runs its own command before reporting", S1,
     r"^> - \*\*RUN IT YOURSELF, in your own copy, before you report it\.\*\*", re.M,
     "> - **RUN IT YOURSELF, in your own copy, before you report it.**",
     "> - **The assessor will run your command for you.**"),
    ("step-01 hunter contract: a command that does not fail as predicted DELETES the finding", S1,
     r"If it does not fail the way you\n> +predicted, you have not found a defect — delete the "
     r"finding", 0,
     "you have not found a defect — delete the finding",
     "report it anyway and let the assessor decide"),
    # ⛔ Anchored to the HUNTER's bullet, not to the bare phrase. The auditor rubric owes the same
    # field, so `reproduced: yes` appears twice in this file — and a counter-example that replaces
    # only the first occurrence left the second one satisfying a bare-phrase regex. The check could
    # not fail on content until it bound the bullet it is actually about.
    ("step-01 hunter contract: the lens reports what its own run showed", S1,
     r"^> - \*\*Report what your own run showed\.\*\* Add `reproduced: yes` \+ the output you "
     r"actually saw", re.M,
     "**Report what your own run showed.** Add `reproduced: yes` + the output you actually saw",
     "**Report your confidence.** Add `confidence: high` when you are sure"),
    ("step-01 auditor rubric: the same requirement, adapted to an ABSENCE", S1,
     r"^> - \*\*A `critical` or `important` MUST carry a runnable reproduction\*\*, adapted to "
     r"your\n> +subject", re.M,
     "> - **A `critical` or `important` MUST carry a runnable reproduction**, adapted to your",
     "> - **An auditor is exempt from the reproduction requirement**, unlike your"),
    ("step-01: the roster count is 3/3", S1,
     r"`lenses_counted: 3/3`", 0,
     "`lenses_counted: 3/3`",
     "`lenses_counted: 5/5`"),
    # step-02: the wave is retired and the step is a pass-through
    ("step-02: the verify wave is RETIRED and the step runs nothing", S2,
     r"^\*\*This step runs nothing\.\*\* The Evidence Verifier and the Compound Synthesis role "
     r"are retired\.", re.M,
     "**This step runs nothing.** The Evidence Verifier and the Compound Synthesis role are retired.",
     "**This step runs two roles.** The Evidence Verifier and the Compound Synthesis role run here."),
    ("step-02: the retirement is measured — 2 refutations in 18 reviews", S2,
     r"refuted \*\*2\nfindings in 18 reviews\*\*", 0,
     "refuted **2\nfindings in 18 reviews**",
     "refuted **most of what the lenses claimed**"),
    ("step-02: reproduction in step 3 is what replaces it", S2,
     r"step 3's \*\*reproduction gate\*\*", 0,
     "step 3's **reproduction gate**",
     "a lighter second reading"),
    ("step-02: findings travel unchanged with `verification: none`", S2,
     r"Carry every finding from step 1 to step 3 unchanged, with\n`verification: none`", 0,
     "Carry every finding from step 1 to step 3 unchanged, with\n`verification: none`",
     "Re-grade each finding before step 3 and record a\n`revised_severity:`"),
    ("step-02: the notes line records the retirement", S2,
     r"add `verify wave: retired \(SCC-447\)` to the engine's returned `notes`", 0,
     "add `verify wave: retired (SCC-447)` to the engine's returned `notes`",
     "add `verify wave: ran` to the engine's returned `notes`"),
    # step-03: the gate, the four buckets, the floor on open rows
    ("step-03: the reproduction gate runs BEFORE the bucket", S3,
     r"^## 4\. The reproduction gate, then the bucket — exactly one per finding$", re.M,
     "## 4. The reproduction gate, then the bucket — exactly one per finding",
     "## 4. Bucket — exactly one per finding"),
    ("step-03: missing either field → DROP, counted", S3,
     r"It must carry `reproduce:` and `expected_wrong_output:`\. Missing either → \*\*drop\*\*, "
     r"counted\.", 0,
     "Missing either → **drop**, counted.",
     "Missing either → treat it as a `suggestion`."),
    ("step-03: a lens that did not run its own command has not met the contract", S3,
     r"A lens that did\nnot run its own command has not met the hunter contract → \*\*drop\*\*", 0,
     "A lens that did\nnot run its own command has not met the hunter contract",
     "A lens may leave the running to the assessor"),
    # ⛔ THE ARCHITECTURAL FACT THIS TURNS ON, verified 2026-09-11: the engine's SKILL.md grants
    # `Read, Write, Glob, Grep, Task` — NO Bash. The engine literally cannot execute a command,
    # and that grant is deliberate (a reviewer that can execute is one edit from being an editor;
    # SCC-295 measured three of five lenses writing to the builder's tree). So the reproduction
    # splits: the LENS proves it in its own copy, the engine checks the claim is THERE, and the
    # CALLER — which has Bash — re-runs it on the real tree and owns the receipt.
    ("step-03: the ENGINE cannot execute, and says so — the caller runs the receipt", S3,
     r"\*\*This engine cannot run it, by design\*\*[^\n]*\n[^\n]*no Bash", 0,
     "**This engine cannot run it, by design**",
     "**This engine runs it here**"),
    ("step-03: the caller re-runs on the REAL tree, and that receipt is what binds", S3,
     r"The CALLER runs the command again, on the REAL\ntree, through `repro_receipt\.py`", 0,
     "The CALLER runs the command again, on the REAL\ntree, through `repro_receipt.py`",
     "The lens's own result is taken as final"),
    ("step-03: a lens's own tree may be a MUTANT — SCC-295 is the named reason", S3,
     r"SCC-295[^\n]*\n?[^\n]*lens's own (copy|mutant)", 0,
     "SCC-295",
     "a hypothetical concern"),
    ("step-03: a suggestion/nitpick is never reproduced and never bucketed", S3,
     r"A `suggestion` or a `nitpick` is never reproduced and never bucketed", 0,
     "A `suggestion` or a `nitpick` is never reproduced and never bucketed",
     "A `suggestion` or a `nitpick` is bucketed like anything else"),
    ("step-03 bucket: FIX is a reproduced critical OR important, pinned with a test seen red", S3,
     r"^- \*\*fix\*\* — a reproduced `critical` or `important`\.[^\n]*\n[^\n]*"
     r"reproduce-before-you-fix` G1–G5", re.M,
     "- **fix** — a reproduced `critical` or `important`.",
     "- **fix** — anything the assessor judges worth fixing."),
    ("step-03: TWO buckets, and the two struck ones are named with the ruling", S3,
     r"\*\*There are two buckets, and there is no third\.\*\*[\s\S]{0,900}?`escalate` bucket"
     r"[\s\S]{0,300}?`defer` bucket[\s\S]{0,400}?2026-09-11", 0,
     "There are two buckets, and there is no third.",
     "There are two buckets, and a third may be added when a lane needs one."),
    ("step-03: held and out-of-lane are the CALLER's dispositions, not engine buckets", S3,
     r"dispositions of the CALLER, not\s+buckets of this engine[\s\S]{0,400}?`held`"
     r"[\s\S]{0,300}?`out-of-lane`", 0,
     "dispositions of the CALLER, not",
     "two more buckets this engine assigns, not"),
    ("step-03 bucket: DROP covers no-reproduction, no-command and noise, counted in one line", S3,
     r"^- \*\*drop\*\* — did not reproduce, arrived without a command, or is noise", re.M,
     "- **drop** — did not reproduce, arrived without a command, or is noise",
     "- **dismiss** — noise, false positive, already handled elsewhere"),
    ("step-03: decision_needed is GONE, because an open decision holds the ticket", S3,
     r"\*\*There is no `decision_needed` bucket any more\.\*\* An open decision holds a ticket "
     r"forever at\n`finish`, which is the loop\.", 0,
     "**There is no `decision_needed` bucket any more.**",
     "**The `decision_needed` bucket is unchanged.**"),
    ("step-03: a survivor is fixed IN THIS THREAD, never a ticket", S3,
     r"\*\*A finding that survives the\ngate is fixed in this thread, never a ticket\.\*\*", 0,
     "gate is fixed in this thread, never a ticket.**",
     "gate is owed to a follow-on ticket.**"),
    ("step-03 §5: the floor is read at the STAMP, on rows still OPEN", S3,
     r"^## 5\. Score the severity floor — on the rows that are still OPEN at the stamp$", re.M,
     "## 5. Score the severity floor — on the rows that are still OPEN at the stamp",
     "## 5. Score the severity floor — the one place severity becomes a verdict"),
    ("step-03 §5: the old always-on floor is named as the loop it caused", S3,
     r"the only road from CONCERNS to PASS was a second full fan-out", 0,
     "the only road from CONCERNS to PASS was a second full fan-out",
     "the floor was simply conservative"),
    ("step-03 §5: an OPEN reproduced critical is FAIL — unfixed, or held", S3,
     r"^\|\s*a reproduced `critical` in `fix` that is not yet fixed and pinned — or `held`[^|]*\|"
     r"\s*\*\*FAIL\*\*", re.M,
     "| a reproduced `critical` in `fix` that is not yet fixed and pinned — or `held`",
     "| any `critical` a lens reported"),
    ("step-03 §5: a HELD reproduced important is CONCERNS — authority", S3,
     r"^\|\s*a reproduced `important` `held` for the operator's word[^|]*\|\s*\*\*CONCERNS\*\* "
     r"— authority", re.M,
     "**CONCERNS** — authority",
     "**FAIL** — authority"),
    # ⛔ An `important` that is neither fixed nor held is not a verdict of any kind: the stamp is
    # refused and the caller finishes. This is what replaced "escalate → CONCERNS": the old row
    # let an unfixed reproduced defect ship with a label; this one lets it ship only fixed.
    ("step-03 §5: an important neither fixed nor held is NOT a verdict — the stamp is refused", S3,
     r"^\|\s*a reproduced `important` in `fix` that is neither fixed nor held\s*\|[^|]*"
     r"the stamp is refused", re.M,
     "the stamp is refused",
     "the lane ships as CONCERNS"),
    ("step-03 §5: a fixed-and-pinned row does not appear in the table at all", S3,
     r"A row closed by a fix and a green pin\ndoes not appear here\.", 0,
     "A row closed by a fix and a green pin\ndoes not appear here.",
     "Every row the lenses returned appears here\nuntil the next review."),
    ("step-03 §5: CONCERNS is not a stop, and §7 is named as the law", S3,
     r"\*\*CONCERNS is not a stop\.\*\*[^\n]*`code-standards\.md` §7", 0,
     "**CONCERNS is not a stop.**",
     "**CONCERNS holds the lane.**"),
    # step-04: the record vocabulary
    ("step-04: the FIX box carries its pin and its repro id", S4,
     r"^- \[ \] \[Review\]\[Fix\] <title> \[<file>:<line>\] src=<lens> · repro <id>$", re.M,
     "- [ ] [Review][Fix] <title> [<file>:<line>] src=<lens> · repro <id>",
     "- [ ] [Review][Patch] <title> [<file>:<line>] src=<lens>"),
    ("step-04: there is NO Escalate box and NO Defer box, and the ruling is named", S4,
     r"\*\*There is no `Escalate` box and no `Defer` box \(SCC-447, operator ruling 2026-09-11\)"
     r"\.\*\*", 0,
     "There is no `Escalate` box and no `Defer` box",
     "The `Escalate` box and the `Defer` box are written below"),
    ("step-04: src= is one of the THREE surviving lens short names", S4,
     r"One lens by its short name \(`edge`, `acceptance`, `test-adequacy`\)", 0,
     "One lens by its short name (`edge`, `acceptance`, `test-adequacy`)",
     "One lens by its short name (`blind`, `edge`, `literal`, `acceptance`, `test-adequacy`)"),
    ("step-04: the summary counts fix, then dropped and recorded — nothing else", S4,
     r"^findings: {8}<f> fix {3}\(<d> dropped — no reproduction · <r> recorded\)$", re.M,
     "findings:        <f> fix   (<d> dropped — no reproduction · <r> recorded)",
     "findings:        <f> fix · <e> escalate · <w> defer   "
     "(<d> dropped — no reproduction · <r> recorded)"),
    ("step-04: held and out-of-lane are written by the CALLER at fix time, never by the engine", S4,
     r"both\s+are the CALLER's dispositions, written at fix time, and this engine never writes either",
     0,
     "this engine never writes either",
     "this engine writes both"),
    # SKILL.md: the caller contract matches
    ("SKILL: the description says it reproduces, not that it verifies", SKILL,
     r"^description:[^\n]*reproduces what they find", re.M,
     "reproduces what they find",
     "verifies findings"),
    ("SKILL: the return block matches step-04's counts", SKILL,
     r"^findings: {8}<f> fix {3}\(<d> dropped — no reproduction · <r> recorded\)$", re.M,
     "findings:        <f> fix   (<d> dropped — no reproduction · <r> recorded)",
     "findings:        <f> fix · <e> escalate · <w> defer   "
     "(<d> dropped — no reproduction · <r> recorded)"),
    ("SKILL: step 2 is declared a pass-through in the flow list", SKILL,
     r"^2\. `steps/step-02-verify\.md` — pass-through \(the verify wave is retired, SCC-447\)$",
     re.M,
     "2. `steps/step-02-verify.md` — pass-through (the verify wave is retired, SCC-447)",
     "2. `steps/step-02-verify.md` — verification pass over what the lenses found"),
    # ⭐ THE STOP CONDITION, IN ONE PARAGRAPH. The loop existed because the floor had no legal way
    # DOWN: it was computed from what the lenses returned, fixing never lowered it, so the only
    # road from CONCERNS to PASS was another full fan-out. Two evidence-backed downgrades replace
    # that dead end — and both are machine-checkable, which is why they cannot be argued into
    # existence the way a judgment call can.
    ("SKILL: the returned floor is PROVISIONAL — the caller resolves it at the stamp", SKILL,
     r"The floor this\nengine returns is \*\*provisional\*\*, and the caller resolves it at the "
     r"stamp\.", 0,
     "The floor this\nengine returns is **provisional**, and the caller resolves it at the stamp.",
     "The floor this\nengine returns is **final**, and the caller may never come back below it."),
    ("SKILL: exactly TWO ways down, both evidence — a receipt, or a fix with a pin", SKILL,
     r"exactly TWO\nways a caller may come back LESS severe[^\n]*\n[^\n]*both are evidence, never\n"
     r"judgment", 0,
     "both are evidence, never\njudgment",
     "both are the caller's\njudgment"),
    ("SKILL: any OTHER downgrade is the caller overruling the review, and is refused", SKILL,
     r"Any other downgrade is the caller overruling the review, which it may not do\.", 0,
     "Any other downgrade is the caller overruling the review, which it may not do.",
     "Any other downgrade is the caller's call."),
    # ⛔ The engine NEVER runs a command (D1), so it never writes a receipt and `ARTIFACT_DIR`
    # stays optional. The boundary section says so positively — a stub that grants itself Bash
    # cannot simultaneously carry this bullet.
    ("SKILL: the engine never runs a command — the caller owns the receipt", SKILL,
     r"^- \*\*It never runs a command\.\*\*", re.M,
     "- **It never runs a command.**",
     "- **It runs each reproduction command itself.**"),
)

# ── §5's identifier bans: the SPELLINGS a live caller would have to write ──────────────────────
# Asserted with anti-vacuity (the file must EXIST and be non-empty first), so a deleted step file
# fails the control instead of satisfying it. These are the machine-readable forms — `lens_budget:`
# with its colon is what a caller passes; a retirement note naming `lens_budget` never writes one.
BANS: tuple[tuple[str, str], ...] = (
    ("a live lens_budget input", r"`lens_budget: (standard|capped)`"),
    ("a live review_level input", r"`review_level: (quick|standard)`"),
    ("a live EVIDENCE_PACK priming instruction", r"prime the lenses[^\n]*with it"),
    ("the retired decision_needed bucket as a live bucket", r"^- \*\*decision_needed\*\*"),
    ("the retired patch bucket as a live bucket", r"^- \*\*patch\*\* —"),
    # Struck 2026-09-11 (operator ruling) — the two buckets SCC-447's own first cut shipped.
    ("the retired escalate bucket as a live bucket", r"^- \*\*escalate\*\* —"),
    ("the retired defer bucket as a live bucket", r"^- \*\*defer\*\* —"),
    ("a live DEFERRED_WORK input row", r"^\| `DEFERRED_WORK` \|"),
    ("a live Escalate or Defer record box", r"^- \[ \] \[Review\]\[(Escalate|Defer)\]"),
)


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def run_checks(c: Cases, checks) -> None:
    for name, rel, pattern, flags, old, new in checks:
        txt = read(rel)
        rx = re.compile(pattern, flags)
        c.check(name, bool(txt) and rx.search(txt) is not None,
                "" if txt else f"{rel} missing or empty")
        applies = old in txt
        c.check("  ^ counter-example applies", applies,
                "" if applies else f"{rel}: {old!r} not present, so the proof would be vacuous")
        mutated = txt.replace(old, new, 1) if applies else txt
        c.check("  ^ counter-example is rejected",
                applies and rx.search(mutated) is None,
                "" if applies and rx.search(mutated) is None
                else "check survives its own counter-example — it cannot fail on content")


def main() -> int:
    c = Cases("review disposition doctrine (SCC-447)")

    if c.block("A · doctrine (code-standards §6.5 + §7)"):
        run_checks(c, CHECKS_A)

        # The twin is a BYTE copy, and the copy is where three of the four readers actually look:
        # Claude Code loads `.claude/rules/`, and a rule that drifted between the two is two
        # different laws with every check green.
        master, twin = read(RULE), read(RULE_TWIN)
        c.check("A · the rule has a body", len(master) > 2000,
                "" if len(master) > 2000 else f"{RULE} is {len(master)} chars — too short to be law")
        c.check("A · the twin has a body", len(twin) > 2000,
                "" if len(twin) > 2000 else f"{RULE_TWIN} is {len(twin)} chars")
        c.check("A · .claude/rules twin is byte-identical", bool(master) and master == twin,
                "" if master == twin else "the two copies of code-standards.md have drifted")

    if c.block("B · engine (the four steps + SKILL)"):
        run_checks(c, CHECKS_B)

        for name, pattern in BANS:
            rx = re.compile(pattern, re.M)
            for rel in (SKILL, S1, S2, S3, S4):
                txt = read(rel)
                # Anti-vacuity FIRST: an absent file must fail, never satisfy, a ban.
                c.check(f"B · {Path(rel).name} has a body for the ban scan", len(txt) > 200,
                        "" if len(txt) > 200 else f"{rel} absent or under 200 chars")
                c.check(f"B · {Path(rel).name}: no {name}",
                        bool(txt) and rx.search(txt) is None,
                        "" if rx.search(txt) is None else f"{rel} still carries {name}")

        # The `.claude/skills/` cache is what Claude Code actually reads. A master edited without
        # its cache copy ships the OLD engine to the one runtime that runs it most.
        for rel in ENGINE_RELS:
            m, k = read(f"{ENGINE}/{rel}"), read(f"{CACHE}/{rel}")
            c.check(f"B · cache {rel} has a body", len(m) > 200 and len(k) > 200,
                    "" if len(m) > 200 and len(k) > 200 else "master or cache absent/too short")
            c.check(f"B · cache {rel} is byte-identical", bool(m) and m == k,
                    "" if m == k else f"{CACHE}/{rel} has drifted from the master")

    return c.finish()


if __name__ == "__main__":
    sys.exit(main())
