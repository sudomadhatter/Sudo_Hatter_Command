---
IsArtifact: true
ArtifactMetadata:
  title: SCC-240 — self-diagnosing readers (roster + declared-set)
  type: walkthrough
  date: 2026-08-20
---

review-runtime: fan-out

# SCC-240 — the machine-read blocks stop being taught in a form their own parser rejects

**Lane:** `chore/SCC-240-self-diagnosing-readers` · **Repo:** command centre · **Base:** `origin/main` @ `db253fc`
**Plan:** [`implementation_plan.md`](implementation_plan.md) — `Audit verdict: GO`, operator `approved` 2026-08-20.

## What this fixes, in one line

A close-out is gated on markdown blocks written by hand, every place the `lenses_run:` roster was **taught** showed it inside a code fence, and `walkthrough_roster.strip_fenced` deletes fenced content before anything reads it — so an agent doing exactly what the instruction said produced a roster the gate could not see, and was told it had no roster. Measured on SCC-210: two preflight round trips, ~12 minutes, on one lane that had done nothing wrong, recurring on every lane that writes a roster.

## Task Checklist

- [x] **Give `walkthrough_roster.py` a CLI** — it was library-only (no `main()`, no `if __name__`), so the only way to learn what it saw was to run a close-out and read the refusal.
- [x] **Make the refusal diagnostic** — three causes, three answers, with the two new branches mutually exclusive by construction.
- [x] **Attach a reason to every `declared_change_set` `incomplete` row** — four rejection paths, three reasons, declared precedence.
  - The plan said three paths; Lens 1 of the self-audit found a **fourth** (`- foo → ` fails the left side *and* has an empty row). Precedence declared — left side wins — and pinned by case `R5`.
- [x] **Fix the teaching surfaces so the taught form parses** — commands unfenced, engine templates keep their fence and gain the instruction.
  - The Antigravity workflow mirrors were declared as EDIT and are correctly **unchanged**: both command bodies exceed the 12k cap, so that surface carries a thin launcher, not a mirror. Declared set amended in place.
  - `.agents/.sync-manifest.json` was **undeclared** — the same sync run rewrites it. Amended in.
- [x] **Pin it with a test that cannot go stale** — `test_doc_examples_parse.py` extracts every taught example *from the documents* and runs it through the real parser.
  - Its first cut over-reached: for a `.py` docstring it walked to the next `##` heading and swallowed prose bullets, producing a red about the extractor wearing the costume of a red about the document. Bounded to the contiguous bullet run.
  - Block `C` (declared-set half) is **GREEN first** — the only taught declared-set example already parses. Written as a regression pin and said so, rather than presented as a red.
- [x] **Resolve the engine's self-contradiction about the verify wave** — one grouping owner, named where the work happens.
- [x] Suite receipt, mutation sweep, review gate.
  - `test_suite_runner.py` caught a defect of **mine**: adding a block to a flat test file left orphan checks outside any guard. Then running each block alone found the second half — three borrowed names from earlier blocks. Both fixed.

## Evidence

Every acceptance row from the ticket → the assertion that proves it → RED before, GREEN after.

### 1 · The roster reader is runnable

RED (`test_walkthrough_roster.py --case "F · the refusal"`, at `db253fc`):

    [FAIL] F1 · the module runs as a command at all: rc=0 out='' - a library-only reader can only be interrogated by writing a script against its internals
    [FAIL] F1b · on a good walkthrough it PRINTS what it parsed and exits 0: rc=0 stdout='' err=''
    [FAIL] F1c · on a REFUSED walkthrough it exits non-zero and prints the reason: rc=0 out=''
    [FAIL] F1d · a missing file is a loud exit 2, never a verdict about content: rc=0 out='' err=''

GREEN:

    [PASS] F1 · the module runs as a command at all: rc=0 out='usage: walkthrough_roster.py [-h] [--verdict {PASS,CONCERNS,FAIL,WAIVED}]\n                             walkthrough\n\nPrin'
    [PASS] F1b · on a good walkthrough it PRINTS what it parsed and exits 0: rc=0 stdout='{\n "lenses": [\n  {\n   "lens": "correctness",\n   "state": "ok",...
    [PASS] F1c · on a REFUSED walkthrough it exits non-zero and prints the reason: rc=1
    [PASS] F1d · a missing file is a loud exit 2, never a verdict about content: rc=2 out=''

### 2 · A fenced roster is named as fenced · 3 · A non-contiguous roster is named as such

RED — both cases got the same sentence, and it described the roster's *format* to an author whose roster was already in the file and correctly formatted:

    [FAIL] F2 · a roster lost to a code FENCE is named as fenced: ["Verdict PASS with NO `lenses_run:` roster. A verdict is the review's conclusion; the roster is what shows it happened. ..."]
    [FAIL] F3 · a roster ended by a BLANK LINE after its header is named as non-contiguous: ["Verdict PASS with NO `lenses_run:` roster. ..."]

GREEN:

    [PASS] F2 ...: ['Verdict PASS: your `lenses_run:` roster is INSIDE A CODE FENCE, and fences are stripped before this is read (SCC-154 - a canonical verdict pasted as evidence inside a fence once became the governing verdict). Paste the block WITHOUT the ``` fence: ...']
    [PASS] F3 ...: ['Verdict PASS: a `lenses_run:` header is here but NO rows were collected under it. The rows must be CONTIGUOUS with the header - a blank line, or any line that is not a `- <lens> · <state>` row, ends the roster, because one that ran past a blank would swallow every bullet later in the document. ...']

### 4 · A genuinely absent roster reads as it does now

The control, green throughout — it is what stops the new branches leaking into a case they do not describe:

    [PASS] F4 · a genuinely ABSENT roster keeps today's message, unchanged
    [PASS] F4b · ...and it does NOT blame a fence or contiguity that was never there

One **existing** case was amended rather than left: `P-F2` pinned the fenced roster's refusal to the word-for-word old message ("exactly as if it had none"). Its blocking half was always right and is unchanged; its message half is precisely what this ticket fixed. It now pins that the lane still BLOCKS **and** that the fence is named.

### 5 · Every `incomplete` bullet carries a reason

RED (`test_declared_change_set.py --case "R · every incomplete"`):

    [FAIL] R1 · every rejected bullet carries a reason, and the reasons DISTINGUISH the failure modes: 0/4 reasoned, 0 distinct

GREEN — four rejected bullets, three distinct reasons, precedence held:

    '- EDIT `no/arrow.md` — never mapped to a row'      ← no `→` row separator - every bullet ends `→ <the acceptance row it serves>`
    '- `no/op.md` — forgot the op marker → B'           ← the left side is not `<OP> <path>` - the op marker is NEW, EDIT or DELETE, then ONE repo-relative path (backticked or bare)
    '- EDIT `empty/row.md` — mapped to nothing →'       ← the row text after the last `→` is empty
    '- both/broken.md →'                                ← the left side is not `<OP> <path>` ...   (LEFT wins - R5)

### 6 · No doc teaches an unparseable block

RED (`test_doc_examples_parse.py`) — the scan found the four known sites and the two paste-ready ones both yielded zero lenses:

    [FAIL] D1 · a paste-ready roster example parses through the REAL parser, exactly as the document writes it: 2 taught example(s) yield ZERO lenses when pasted verbatim: ['.agents/commands/cicd-code-review.md:380 [fenced]', '.agents/commands/smh-code-review.md:378 [fenced]']
    [FAIL] D2 · a fenced TEMPLATE says the fence is illustration and must not be pasted: 2 fenced template(s) with no such instruction: ['.agents/skills/code-review-engine/SKILL.md:70', '.agents/skills/code-review-engine/steps/step-04-record.md:53']

GREEN: `0 taught example(s) yield ZERO lenses`, `0 fenced template(s) with no such instruction`. Anti-vacuity rows carried throughout — `D0` (70 files globbed), `D0b` (4 examples found), `D0c` (2 paste-ready), `D3` (the control proving a fenced roster still reads as zero and the same rows unfenced read as two).

### 7 · The verify wave's grouping owner is unambiguous

RED: `G1`, `G2`, `G3`, `G4` — `group@-1`, i.e. nothing in the file named who groups.
GREEN: `group@2653 serialise@2850` — the owner is named, and named **before** the instruction it governs.

### The gates

| Gate | Result |
|---|---|
| `run_all.py` (via `gate_receipt.py`) | **PASS** exit 0, 124.8s @ `a0e36d54`, `dirty_tree: false` — `40/40 files passed` · receipt `gates/suite.json` |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, 8 info** (pre-existing BOM notices on `testarch-*`) |
| `check_maps.py --depth3-only --strict` | **exit 0** |
| `tests/test_sops_prds_folder.py` | **61/61** |
| `lane_qualify.py` on the real diff | `TASK` — the correct verdict for this lane; **no deployable path**, so no eject |
| `declared_change_set.py diff` (declared vs real) | `undeclared=0 · unimplemented=0 · incomplete=0` after the in-block amendment |

⛔ Gates were run **bare**. Early in the lane I read exit codes through `${PIPESTATUS[0]}`, which is a bashism — empty in zsh — so every exit code read blank. Caught and re-run; noted because it is the same class as the repo's own `piping-a-gate-hides-its-exit-code` scar.

### Mutation sweep — `sweep.json`, declared before mutating, drawn from the code

    -- sweep clean: 6/6 killed by their declared case --
    -- restore verified: bytes match, nothing was committed, and `git diff --quiet f4e6721b` is clean --

| # | Mutant | Killed by |
|---|---|---|
| M1 | the fenced-header flag forced `False` | `F2` |
| M2 | the two diagnostic branches swapped, so each case gets the other's answer | `F3` |
| M3 | the CLI always returns 0 | `F1c` |
| M4 | the missing-arrow bullet told the left side failed instead | `R2` |
| M5 | the taught roster example put back inside a code fence | `D1` |
| M6 | the verify wave's grouping sentence removed | `G1` |

All three test files were then re-run **full and unfiltered** — the run that catches a mutant riding in behind green scoped filters.

**HEAD:** `a0e36d5` · branch pushed to `origin/chore/SCC-240-self-diagnosing-readers`.

## Your Actions

Nothing is owed. The lane is review-complete and pushed; the close-out is yours to invoke when you want it.

- [x] Plan written, self-audited (`Audit verdict: GO`) and approved.
- [x] Suite, lint, INDEX and SOP gates green at the shipping sha, with a receipt.
- [x] Mutation sweep clean, restore verified.
