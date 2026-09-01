# SCC-145 — Mutation doctrine: name it, load it into the task lane, and gate it

- **Ticket:** SCC-145 (Bug) · **Lane:** `chore/SCC-145-mutation-doctrine` · **Repo:** `Sudo_Hatter_Command`
- **Branched from:** `5dadcd6` → **absorbed** `ba062a0` (SCC-144) mid-lane → **build sha** `268f894`
- **Date:** 2026-08-13

## Task Checklist

- [x] **Step 0 / 0.5** — repo + lane pinned from `rev-parse`; SCC-145 → `In Progress` (`jira_feed start`, exit 0)
  - Sibling lanes read at open: SCC-129 (`gate-the-gate`) and SCC-144 (`merge-target-guard`), **zero
    functional-file overlap**; only ledger-class files shared.
- [x] **Step 1** — checkable list taken from the ticket's own `ACCEPTANCE` block (authority order #1)
- [x] **Step 1.5** — plan written, `/smh-self-audit` **GO** (FULL tier), stopped for the literal `approved`
  - ⚠ **Amended after approval, on the operator's call to pull first** — see *Deviations* #1.
- [x] **Step 2** — RED: **49/52, exit 1**, three cases failing for the right reason
- [x] **Step 3** — GREEN: **52/52, exit 0** (→ **57/57** after the review fixes); sync run; SOP +
  ledger row staged in the same commit
- [x] **Step 3b** — mutation sweep #1: **8 declared, 8 killed**, tree verified restored
- [x] **Step 4** — `/smh-code-review` — two independent lenses; **7 more survivors found**, all fixed,
  then re-swept as **sweep #2 (14 mutants)**. See `## Code Review`.
- [x] **Step 5** — artifacts, manifest, Dev Record

## What was actually wrong

Mutation testing was practiced constantly and written down almost nowhere. Re-measured on this tree
before a line was edited:

| Claim | Measurement |
|---|---|
| The practice is absent from the command surface | `grep -rn "mutant\|mutation\|mutate" .agents/commands/` → **2 hits**: a script that mutates `_my_resources/`, and *"Lynn Margulis — merger beats mutation"* in the adviser board. A biologist. |
| The doctrine is one sub-bullet, filed under another concern | `tests-must-gate-for-real.md` → `## The Rule` → item **4** (headlined *"Certification is measured at the SHIPPING SHA"*) → **fourth** sub-bullet |
| The normative text never names the practice | the word "mutation" appeared **twice** in that file, at lines 76-77, inside `## Why` — the provenance narrative, not the binding rule |
| The one technique given does not transfer | *relocate, never delete* assumes a structural guard + behavioral test in one file. A shell gate has **nothing to relocate** — the useful mutant **inverts a decision** |
| ⭐ It reaches the STORY lane but not the TASK lane | loaded by 6 story-lane commands; on the task lane only `/smh-code-review` — **after** the mutants are designed. `/smh-quick-dev` (writes the assertions) and `/smh-self-audit` (judges the plan that picks the strategy) loaded it **not at all** |
| Nothing mechanical could see any of it | `grep -rln "Rules in force" .agents/scripts/tests/*.py` → **zero files.** No test anywhere asserted on any rules-in-force block |
| The operator's own SOP never named it either | `grep -i "mutant\|mutation"` over `workflows_testing_SOP.md` → **zero hits** (not in the ticket; found while fixing it) |

## Evidence

| Acceptance item | The assertion that proves it | RED → GREEN |
|---|---|---|
| #1 rule in the rules-in-force block of `smh-quick-dev` + `smh-self-audit` | `test_command_surfaces.py` — *"the mutation rule is LOADED …"*, scoped by `rif_block` | `['smh-quick-dev.md', 'smh-self-audit.md']` → `[]` |
| #2 Step 3 carries the mutant-table obligation | *"/smh-quick-dev Step 3 carries the mutant-table obligation…"*, scoped by `md_section` | missing `['mutant table', 'one sweep', 'DEFECTIVE', 'from the code', 'git status']` → `[]` |
| #3 rule has a section named for the practice, all techniques | *"the mutation rule has a section whose HEADING names the practice…"* | `no ## heading names mutation` → `[]` |
| #4 guards pin the BLOCK, not the filename anywhere | 6 controls + the M1/M7 mutants below | proven, not assumed — see *Mutation* |
| #5 gate green at the shipping sha | `run_all` · `workflow_lint --toolkit-only` · `check_maps --depth3-only --strict`, all **bare** | see *Gates* |
| #6 SOP currency | SOP staged in the same commit as the usage-surface change | `268f894` |

**RED** (`red-01-mutation-doctrine.txt`, bare, exit **1**):

```
[FAIL] the mutation rule is LOADED (in the rules-in-force block) by every task-lane command …
       ['smh-quick-dev.md', 'smh-self-audit.md'] - cite `.agents/rules/tests-must-gate-for-real.md`
       INSIDE the block, not in step prose.
[FAIL] /smh-quick-dev Step 3 carries the mutant-table obligation …
       missing from `## Step 3`: ['mutant table', 'one sweep', 'DEFECTIVE', 'from the code', 'git status']
[FAIL] the mutation rule has a section whose HEADING names the practice, carrying every technique
       no `##` heading in tests-must-gate-for-real.md names mutation
-- 49/52 passed --
```

**GREEN** (`green-01-mutation-doctrine.txt`, bare, exit **0**): `-- 52/52 passed --`

⛔ **One case went red in between, and that was the mechanism working.** Editing two command bodies
without re-syncing turned *"every mirror door still says what its brain says"* red — the SCC-113
door-parity check catching a forgotten sync. `/smh-sync-agents` cleared it. The failure mode is loud,
exactly as the plan's Phase 1 predicted.

## Mutation

**8 declared before mutating, run as ONE sweep, drawn from the code, restored in a `finally`.** The
sweep refused to start dirty and re-checked `git status` on exit — so the doctrine this ticket ships
is the doctrine that proved it. Sweep script kept out of the tree (running mutation *in the gate* is
explicitly out of scope); the table is the artifact.

| # | Mutant | File | Named case it must kill | Result |
|---|---|---|---|---|
| M1 | the rule's line deleted from the rules-in-force block | `smh-quick-dev.md` | the rule is LOADED | **KILLED** |
| M2 | the whole rules-in-force block header deleted | `smh-self-audit.md` | the rule is LOADED | **KILLED** |
| M3 | the mutant-table bullet **relocated** out of Step 3 into Step 2 | `smh-quick-dev.md` | Step 3 carries the obligation | **KILLED** |
| M4 | `## Mutation Testing` heading demoted to bold prose | `tests-must-gate-for-real.md` | the section names the practice | **KILLED** |
| M5 | `DEFECTIVE` removed from its subsection heading | `tests-must-gate-for-real.md` | the section names the practice | **KILLED** |
| M6 | the whole `CODE-DERIVED` technique deleted | `tests-must-gate-for-real.md` | the section names the practice | **KILLED** |
| M7 | ⭐ `rif_block` returns the whole file (block-scoping collapses to a file grep) | `test_command_surfaces.py` | *CONTROL: cited only in BODY PROSE is NOT loaded* | **KILLED** |
| M8 | ⭐ `md_section` loses its `## ` boundary (sections run on forever) | `test_command_surfaces.py` | *CONTROL: `## Step 3` does not swallow `## Step 3.5`* | **KILLED** |

**8/8 killed. `restored clean: YES`.**

⭐ **M7 and M8 are the CODE-DERIVED half, and they are the point.** M1–M6 mutate the documents the
guard reads — useful, but drawn close to the cases. M7 and M8 mutate **the guard's own helpers**,
which is where a vacuous check would actually live. SCC-144's review measured why this matters: its 14
case-derived mutants were all killed, while a later set drawn from the code left **24 of 25
surviving** — every survivor a hole the first sweep had reported as covered.

⭐ **M1 proves the block-scoping is load-bearing rather than decorative**, and it was verified
mechanically rather than argued. With M1 applied to `smh-quick-dev.md`:

```
file-wide grep still finds the rule (a naive guard PASSES): True
block-scoped check finds it (the real guard FAILS):         False
```

The rule name survives in Step 3's own prose, so the obvious implementation of this guard — *"does
the file mention the rule?"* — would have shipped green against a command that had just lost it.
That is `prose-pinning-guards-are-vacuous` (SCC-125), defeated in advance instead of in hindsight.

## Deviations from the ticket, and why

1. **The plan was amended after `approved`, and the amendment is recorded in the plan itself.** The
   operator called for a pull before work began; `main` had moved `5dadcd6` → `ba062a0`. SCC-144's
   walkthrough `Your Actions` is addressed **to this ticket by name** and carries two techniques the
   ticket predates: **CODE-DERIVED** (its review's own finding) and **RESTORE on interrupt** (a
   `timeout`-killed sweep left `commit-msg-jira.sh` mutated on disk, uncommitted — reverted to the
   exact bug that lane existed to remove). Both are additive inside acceptance item #3, which already
   demanded the practice's own section, so the change set did not grow. The section ships **four
   techniques plus the DEFECTIVE rule**, not three.
2. ⭐ **FIX 4's first bullet was deliberately NOT implemented as written, and this is the one call
   worth overruling if you disagree.** The ticket says *every* command that writes or judges tests
   must cite the rule inside its own rules-in-force block. Measured, that guard goes red on **five**
   commands — two of which (`cicd-code-review`, `cicd-write-story-tests`) have **no such block at
   all**, and two of which carry `-AP` twins owing a twin re-diff. (Six commands sit outside this
   ticket's two-command edit set, but one of those six — `smh-code-review` — already complies, so
   five is the number that would actually go red. The guard's own comment said five; these two
   artifacts said six, and the review caught the mismatch.) Widening is 5 primaries + 2 twins = 7
   files against the ticket's 2, ~3.5× the edit set,
   entering through a guard's phrasing rather than through its acceptance block. The binding list
   (Step 1's authority order #1) names only the two task-lane commands. **Pinned here:**
   `smh-quick-dev`, `smh-self-audit`, and `smh-code-review` — the last because it already complied,
   and an unpinned compliance is one edit from being gone. The five story-lane commands keep the
   *stronger* form: the rule baked into the step bodies that route the work
   (`restate-alwayson-obligations-in-command-bodies`). Widening them is its own ticket.
3. **The SOP gained a section the ticket did not ask for.** `workflows_testing_SOP.md` had **zero**
   mentions of mutation — the operator's own reference had never named the practice either. Fixing
   the commands while leaving the SOP silent would have satisfied the gate and missed the point.
4. **No mutation harness in the gate.** Unchanged from the ticket's *Out of scope*: `run_all.py`
   stays stdlib-only and deterministic. The sweep script lives in the scratchpad, not the tree.

## Gates

**Certification measured at `54ce267`** — the post-absorb tree, every command **bare** (a piped gate
returns the *pipe's* exit code, and `zsh` has no `PIPESTATUS[0]`).

| Gate | Result |
|---|---|
| Enforcement suite | `run_all.py` → **23/23 files, 1875/1875 cases, exit 0** |
| Toolkit lint | `workflow_lint.py --toolkit-only` → **0 errors, 0 warnings, 8 info, exit 0** |
| Map / INDEX | `check_maps.py --depth3-only --strict` → **exit 0** |
| SOP currency | `sop_currency.py --paths <16 changed> --message "<subject>"` → **exit 0** |
| `py_compile` | `test_command_surfaces.py` → **OK** |
| Link + anchor | every repo path the new prose names resolves — see the one false positive below |
| Door parity | both `.opencode` mirrors **byte-identical** to their `.agents/commands/` source |
| Assertion evidence | RED **49/52 exit 1** → GREEN **52/52 exit 0**, both captured bare and committed |
| Mutation | **8/8 killed**, `restored clean: YES` |

**Case total exactly additive — and MEASURED, after the first attempt did not add up.** `main`'s own
baseline was taken by running the suite in a detached worktree at `8ce9abb`: **1861**. This lane:
**1875**. Delta **+14**, matching `test_command_surfaces.py` 43 → 57 exactly — 9 from the build and
**5 added by the review**, each pinning a mutant that had been a live survivor. This lane touches no
other test file, so the delta is fully attributable.

⛔ **The first post-absorb run gave 1872, not 1875, and the "exactly additive" claim was false as
stated.** Found by diffing the **per-file** summary lines rather than trusting the total: file 12,
`test_main_ruleset_armed.py`, ran **2/2 here against 5/5 on main**. Not a regression and not this
lane's doing — that file is not in this diff. Its server-side half queries the GitHub ruleset API,
could not reach GitHub during that run, and degraded to `[SIGNAL]` by its author's design, which says
the half is *"UNVERIFIED in this run, not proven absent."* Re-run with the network back: **1875, zero
SIGNAL lines**. The total alone read as a clean pass both times — only the per-file comparison showed
three cases had silently not run, which is this ticket's own subject one layer out.

⚠ **One link-sweep false positive, reported rather than hidden:** the sweep flagged
`commit-msg-jira.sh` as DEAD. It is a **bare filename in prose**, not a repo-relative path — the real
file is `.agents/scripts/git-hooks/commit-msg-jira.sh` and it exists. This is exactly the
false-positive class SCC-87 is open to handle.

## Your Actions

- **Review and close out** — `/smh-close-task-merge-tree` is yours, and typing it is the merge sign-off.
- ⭐ **The one judgement call to confirm or overrule:** *Deviations #2* — the in-block citation is
  pinned for the two task-lane commands plus `smh-code-review`, not for all eight commands that write
  or judge tests. Say the word and the wider guard is a follow-on ticket.
- **Still owed, deliberately not smuggled in here:**
  - **SCC-143** — `/cicd-code-review` passes no `lens_budget`, so an interactive review silently takes
    the autopilot's `capped` default. Separate contract, separate ticket, no file overlap with this
    lane. It was checked for duplication against this ticket and is **not** a duplicate.
  - SCC-144's other open handoffs: the SOP mermaid node for the merge-target gate, and propagating
    its hooks to `Projects/*` (repo-local by law — needs its own key per repo).

---

## Code Review (2026-08-13)

Verdict: PASS @ 0692f0c
Suite evidence measured at `54ce267` (the absorb merge); `0692f0c` is the doc-only commit carrying it, which Rule 4 exempts. **Re-stamped** — the first verdict was `PASS @ 3809e00`, and a re-run of this gate found `main` had moved under it (see *Step 0.7, second pass*).

**Scope** — `main...HEAD`, 17 files. **Method** — two independent clean-room lenses (blind
adversarial hunt on the diff with the walkthrough withheld; acceptance audit against the ticket's
own `ACCEPTANCE` block), then every finding re-verified by me against real bytes before disposition,
then a second declared mutation sweep.

⛔ **The review changed the outcome of this lane.** It found **seven surviving mutants** the builder's
own 8-mutant sweep did not — including a control that could not fail, sitting inside the guard whose
subject is checks that cannot fail. All seven are fixed and re-swept.

### Findings

| # | file:line | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| F1 | `test_command_surfaces.py:752, 771-773` | **HIGH** | `STEP3_RX`'s `(?![\d.])` lookahead could be **deleted with all 52 cases green**. Its control fed both headings in file order, so `md_section` takes `## Step 3` on first-match with or without the lookahead — the control passed against the guard *and* its mutant. The input it actually guards is the one where `## Step 3` is **absent**: without the lookahead `## Step 3.5` stands in, and an obligation that drifted into the eject step reads as compliance | **applied** — added the discriminating control; kept the old one, which now states what it cannot do (M12) |
| F2 | `test_command_surfaces.py:733` | **HIGH** | `LOADERS` gutted to `("smh-code-review.md",)` — dropping **both** commands this ticket exists to protect — left the suite **fully green**. Same for emptying either term list. The section's entire scope was an unpinned constant | **applied** — scope pinned by name + non-empty (M9/M10/M11) |
| F3 | `tests-must-gate-for-real.md:73-77` | **MED** | The whole **RELOCATE** technique could be deleted and the guard stayed green: the bare token survives one bullet down inside INVERT's prose (*"the shape RELOCATE does not transfer to"*). The guard held the four techniques that happened to be unique and let go of the one the section exists to correct | **applied** — every technique anchored to its own bullet lead, not the bare word (M14) |
| F4 | `test_command_surfaces.py:234-237` | **MED** | `rif_block`'s `break` → `continue` degenerates it into *"any blockquote anywhere in the file"*, and these commands carry later `> **Note:**` asides. The only negative control used plain prose, which the mutant also passes | **applied** — control added putting the rule name in a **later** blockquote (M13) |
| F5 | `workflows_testing_SOP.md:1103, 1112-1136` | **MED** | The SOP's entire mutation section **and** its mermaid node could be deleted with the suite green. `sop_currency.py` forces the SOP to be *staged*, never to still *say* anything — so the operator's own reference was the one surface that could silently rot | **applied** — the SOP is now gated on naming the practice + carrying the obligation (M15) |
| F6 | `smh-quick-dev.md:238` | **MED** | *"A surviving mutant is a finding"* — the single most load-bearing sentence in the doctrine — had **no pinned term at all** and could be deleted silently | **applied** — pinned via `surviving`/`survivor` (M16) |
| F7 | `test_command_surfaces.py:760` vs `rule:82` / `SOP:1129` | **MED** | **False-red risk.** The rule and SOP name the technique `CODE-DERIVED` where the command said *"from the code"*, and the guard pinned the literal — so **harmonising the three surfaces**, exactly what a findability ticket invites, would have gone RED | **applied** — obligations are concept rows with alternatives, case-folded on both sides |
| F8 | `_artifacts/…/green-02-run-all.txt` (committed) | **HIGH** | The diff shipped **red gate evidence**: the committed run_all artifact read `21/22 FAILED: test_check_maps.py`, captured before the ledger row existed. The corrected 22/22 capture, the lint artifact and the whole certification table lived only in the working tree | **applied** — committed at `3809e00`; `green-03` now records its exit code, since an empty file is indistinguishable from a command that never ran |
| F9 | plan + walkthrough | **MED** | Both narrative artifacts said the wider FIX-4 guard *"goes red on **six** commands"*. It goes red on **five** — six sit outside the edit set but `smh-code-review` already complies. The guard's own comment said five all along, so the operator was being asked to affirm a ruling on a mis-stated count | **applied** — corrected in both; magnitude restated as 5 primaries + 2 `-AP` twins = 7 files vs the ticket's 2 |
| F10 | `rule:84-86` (+3 copies) | **LOW** | *"24 of 25 code-derived mutants survived the 14 case-derived ones"* does not parse — mutants do not survive other mutants. Faithfully copied from SCC-144 into four surfaces | **applied** — restated in all four as what it measured |
| F11 | `.agents/rules/INDEX.md:41` | **MED** | The rule's routing row never mentioned mutation, so the **first place anyone greps** still described the rule as being about soft gates — directly against this ticket's stated purpose | **applied** |
| F12 | `smh-self-audit.md:19` | **LOW** | Mapped the *"gate that cannot fail"* tripwire to Rule 3 alone; that command's own Phase 2 defines it as soft gates (Rule 3) **plus** *"a check whose empty input reads as a pass"* (Rule 1 + § Mutation Testing) | **applied** |
| F13 | `rule:58` / `:79`, plus § casing | **LOW** | *"the three shapes it does not transfer to"* where the section names one; and four of five cross-references said `§ Mutation testing` against a heading reading `## Mutation Testing` — for a findability ticket, grepping one spelling missed the others | **applied** |
| F14 | `md_section` docstring | **LOW** | Claimed "mutation" appeared *once, at line 76*; it appears **twice, at 76-77** | **applied** |
| R1 | — | — | ⛔ **REJECTED, with the reason recorded.** A lens reported the command surface has **one** mutation hit, not two, calling the ticket's premise wrong. Its grep omitted `mutate`, missing `smh-update-maps-indexes.md:300`. Verified on `main`: `git grep "mutant\|mutation\|mutate" -- .agents/commands/` → **2 hits**. The ticket's number stands | **dismissed** |
| K1 | `test_command_surfaces.py:712-715` | — | **Known limit, recorded not fixed.** A rule section meaning the *opposite* (*"do NOT relocate; a DEFECTIVE mutant is fine, believe it"*) still scores green — the tokens are present. The artifact **is** prose, so presence is the strongest available pin; `52/52` is evidence the doctrine is **present and correctly placed**, never that it is correctly *argued*. Stated so nobody reads the number as more than it is | **deferred** (inherent to prose-pinning) |

### Mutation sweep #2 — 14 declared, 14 killed

The original 8 re-run plus the 7 the review exposed (M3/M6 folded into their re-aimed successors).
Every mutant CODE-DERIVED where the code allows it; sweep refused to start dirty, restored in a
`finally`, `restored clean: YES`.

⛔ **The sweep caught its own defect, which is the doctrine working on itself for the third time in
this lane.** M10 and M11 first "killed" with **zero failing cases** — a non-zero exit and no `[FAIL]`
line, because the splice left unbalanced parentheses and the file died on a `SyntaxError`. That is a
**DEFECTIVE mutant** by this ticket's own definition: it proved Python rejects broken syntax, never
that the anti-vacuity case fires. Both re-aimed to a syntactically valid `= ()`; both then killed
with a real red. **A kill with no named case failing is not a kill** — worth adding to the rule if it
recurs.

| Mutant | Killed by |
|---|---|
| M1 rule line out of the rules-in-force block | the rule is LOADED |
| M2 the whole block header deleted | the rule is LOADED |
| M4 `## Mutation Testing` demoted to bold prose | the section names the practice |
| M5 DEFECTIVE dropped from its subsection heading | the section names the practice |
| M7 ⭐ `rif_block` returns the whole file | CONTROL: body prose is NOT loaded |
| M8 ⭐ `md_section` loses its `## ` boundary | CONTROL: Step 3 does not swallow Step 3.5 |
| M9 ⭐ `LOADERS` gutted to the compliant command | the LOADERS scope cannot be narrowed |
| M10 ⭐ `STEP3_OBLIGATIONS` emptied *(re-aimed)* | the lists still name what they pin |
| M11 ⭐ `TECHNIQUES` emptied *(re-aimed)* | the lists still name what they pin |
| M12 ⭐ the `(?![\d.])` lookahead deleted | CONTROL: Step 3.5 must not stand in for Step 3 |
| M13 ⭐ `rif_block` `break` → `continue` | CONTROL: a LATER blockquote is not the block |
| M14 the whole RELOCATE technique deleted | the section carries every technique |
| M15 the SOP's section + mermaid node deleted | the SOP names the practice |
| M16 "a surviving mutant is a finding" deleted | Step 3 carries the obligation |

⭐ marks the CODE-DERIVED mutants — 7 of 14, against 2 of 8 in sweep #1. Every one of the seven was a
**live survivor** before this review.

### Step 0.7 — blast radius re-derived against current `main`

1. **Nothing moved.** `merge-base HEAD main` == `main` == `origin/main` == `ba062a0`; zero files landed
   while building. Every path the new prose names re-resolved OK.
2. **True overlap with the live sibling (SCC-129): two ledger-class files.** `merge-tree` says
   `workflows_testing_SOP.md` **auto-merges** (my hunks ~1100-1140, theirs ~1292) and
   `_artifacts/_main/INDEX.md` **CONFLICTS** — both prepend a row.
3. **Landing order is FREE, but the resolution rule is not.** Whoever lands second resolves
   `INDEX.md` by **keeping both rows**; dropping the other lane's row is the known failure mode, and
   `check_maps --strict` catches it (it is what caught this lane's own missing row).

### Gates

| Gate | Result |
|---|---|
| Enforcement suite | `run_all.py` → **23/23 files, 1875/1875 cases, exit 0** @ `54ce267` |
| Toolkit lint | `workflow_lint.py --toolkit-only` → **0 errors, 0 warnings, 8 info, exit 0** |
| Map / INDEX | `check_maps.py --depth3-only --strict` → **exit 0** |
| Assertion evidence | every Step 2 RED is GREEN; guard **52 → 57 cases** after the review fixes |
| Mutation | **14/14 killed**, `restored clean: YES` |
| Clean code | no banned patterns in 257 added lines (grep exit 1, run **bare** — the first attempt piped through `head` and could not distinguish clean from never-ran); no secrets; `py_compile` OK |
| Door parity | both `.opencode` mirrors byte-identical after re-sync |

### Changes applied

All 14 findings applied; 1 rejected with evidence; 1 recorded as an inherent limit. Commits
`07c490f` (guard + doc fixes) and `3809e00` (evidence + count correction).

---

## Code Review — second pass (2026-08-13, re-invoked)

**Verdict: PASS @ `0692f0c`** (suite measured at `54ce267`; `0692f0c` is doc-only, which Rule 4 exempts).

The gate was re-invoked after the first verdict. **It was right to be** — Step 0.7 found `main` had
moved underneath the lane, so the earlier `PASS @ 3809e00` was a verdict about a repo that no longer
existed. Nothing about the lane's own work changed; the re-stamp is what makes the verdict true of
the tree that will actually merge.

### Step 0.7, second pass — `main` moved

1. **SCC-129 landed at `8ce9abb`** (review-engine negative control) while this lane was in review.
   `merge-base` was still `ba062a0`. **Nothing this diff references moved** — all seven paths the new
   prose names re-resolved OK — and SCC-129 touches **no file this lane edits** (verified by grep over
   `ba062a0..main`: no `test_command_surfaces`, no `tests-must-gate-for-real`, no `smh-quick-dev`,
   no `smh-self-audit`, no `rules/INDEX`).
2. **True overlap: two ledger-class files**, exactly as this lane's *first* Step 0.7 predicted in
   writing before it happened. `merge-tree` called it precisely: `workflows_testing_SOP.md`
   **auto-merges** (this lane's hunks ~1100–1140, SCC-129's ~1292); `_artifacts/_main/INDEX.md`
   **CONFLICTS** — both lanes prepend a row.
3. **Absorbed here, not at merge time** (`54ce267`), because conflicts belong on this branch and never
   on `main`. The ledger conflict was resolved by **keeping BOTH rows** — dropping the other lane's row
   is the known failure mode of this conflict class, it is what `check_maps --strict` catches, and
   SCC-129's own absorb commit hit the same thing one lane earlier. Verified after resolution: **zero
   conflict markers, all three rows present** (145, 129, 144).

### ⛔ The additivity claim was false as first stated, and the total would never have shown it

`main`'s baseline was **measured**, not assumed — the suite run in a detached worktree at `8ce9abb`:
**1861**. First post-absorb run of this lane: **1872**. That is **+11** against a guard that added
**+14**, so three cases were unaccounted for.

Found by diffing the **per-file** summary lines instead of trusting the total: file 12,
`test_main_ruleset_armed.py`, ran **2/2** here against **5/5** on `main`. Not a regression, and not
this lane's doing — that file is not in this diff. Its server-side half queries the GitHub ruleset
API, could not reach GitHub during that run, and degraded to `[SIGNAL]` by its author's design, which
states the half is *"UNVERIFIED in this run, not proven absent."* Re-run with the network back:
**1875 cases, zero SIGNAL lines** — those three verified green and the arithmetic closes exactly at
**1861 + 14 = 1875**.

**The total alone read as a clean pass both times.** Only the per-file comparison showed three cases
had silently not run — which is this ticket's own subject, one layer out: *a check that did not run is
not a check that passed.*

Separately, an interrupted run left a **partial artifact** on disk — 789 cases, cut mid-suite, exit
code lost — which was overwritten by the complete run. Same residue class as the `timeout`-killed
sweep that motivated the **RESTORE** technique this lane adds to the rule.

### Gates, re-run on the post-absorb tree

| Gate | Result |
|---|---|
| Enforcement suite | `run_all.py` → **23/23 files, 1875/1875 cases, 0 failing, 0 SIGNAL, exit 0** @ `54ce267` |
| Toolkit lint | `workflow_lint.py --toolkit-only` → **0 errors, 0 warnings, 8 info, exit 0** |
| Map / INDEX | `check_maps.py --depth3-only --strict` → **exit 0** (after the ledger reconcile) |
| This lane's guard | **57/57, exit 0** |
| Mutation | sweep #2 re-run post-absorb: **14/14 killed**, `restored clean: YES` |
| Merge state | conflicts resolved on this branch; `main` untouched |

### Changes applied in this pass

The absorb merge and the re-stamp. **No code or doctrine changed** — the first pass's fourteen
findings all still stand as applied, and the guard still kills all fourteen mutants on the merged
tree, which is the thing absorbing a sibling lane could plausibly have broken.
