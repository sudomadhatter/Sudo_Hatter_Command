---
IsArtifact: true
ArtifactMetadata:
  title: Two-Team Operating System — pipeline conversion, lean toolkit, grounding gate, BMAD-lite, Drive proof
  type: walkthrough
  date: 2026-07-22
---

# Walkthrough — RAG_Pipeline_AC conversion (P0–P4 + P6)

**Stopped at P5 by Daniel's instruction** — he wants a different model for writing the SOP document.
Everything else in the approved plan is done and verified. P5 (the SOP + cross-links) is the only
remaining phase.

---

## What happened, in order

### P0 — operator-profile parity (AGY)
Turned out to be nearly self-resolving. The rule file was already byte-identical across lobby / AGY /
Fresh (`7fe82504…`), and AGY's rules `INDEX.md` already carried the floor-tier row — but AGY's
`AGENTS.md` never actually loaded it (`grep -c operator-profile` = **0**). Added it to §4 ALWAYS-LOAD
with the lobby's exact wording. Daniel committed this mid-session (`6ff0aad`), so AGY is clean.

### P1 — structure conversion
Front doors replaced: `CLAUDE.md` (full protocol doc → 3-line pointer), new root `GEMINI.md`,
`.gemini/GEMINI.md` repointed at the root `AGENTS.md`. Wrote a real Layer-2 `AGENTS.md` — routing
table, source-of-truth table, stores table, gates, persistence, curriculum story lifecycle.

Vendored the master toolkit with `/sync-agents -Target`. Deleted the two forked rule dirs
(`.claude/rules/` 14 files, `.agent/`), the GitNexus skills bundle, and `src/pipeline/` (empty but
for a `__pycache__` — the dead 6-phase lifecycle the README already said was removed).

Consolidated artifacts with `git mv` so history survives: 11 session folders from
`_claude_artifacts/` → `_artifacts/`, both retired dirs deleted. Added `_artifacts/README.md` +
`INDEX.md`, seeded `_my_resources/` (protected README + `open_tasks/todo_list.md` carrying the real
debt register).

**GitNexus dropped** (rider confirmed): removed `data/ingestion: RAG_Pipeline_AC` from
`~/.gitnexus/groups/ac-stack/group.yaml`, deleted the local `.gitnexus/` index (**51 MB** of it was
a single `lbug` blob), and the governance blocks died with the front-door rewrites. The repo was
never in `registry.json`, so nothing to remove there. `md-feedback` MCP wired via a new `.mcp.json`.

### P1b — the prune (Daniel's mid-flight correction)
> *"you added everything to the rag pipeline? we talked about this we dont need it heavy like this"*

He was right, and the fault was mine: `/sync-agents` is an all-or-nothing vendor, so it pushed the
full house kit — 17 Claude commands, 43 opencode commands, 45 skills including the whole `sudo-*`
dev flow, three autopilots, and the entire BMAD/TEA testing family — into a repo that runs basic
tasks. Pruned to a **lean, deliberate set**:

| Surface | Before | After |
|---|---|---|
| `.claude/skills/` | 45 | **8** (4 curriculum + 4 hygiene) |
| `.claude/commands/` | 17 | **1** (`update-maps-indexes`) |
| `.opencode/commands/` | 43 | **1** |
| `.agents/` subdirs | 10 | **4** (rules · skills · scripts · hooks) |

Also removed `.agents/workflows|commands|opencode-agents|templates|reference` and a pre-conversion
ghost dir I'd missed on the first pass: `.claude/workflows/` (9 stale `1_*` workflows including the
`1_ccps_*` pair purged system-wide weeks ago) plus `.opencode/agent/`.

Wrote `.agents/skills/INDEX.md` as the **keep-list**, and put a warning in `AGENTS.md` §3: a blanket
`/sync-agents -Target` re-imports everything, so re-prune after any rules refresh. That's the trap
that would otherwise undo this.

### P2 — the rules that actually matter here
New `constitution.project.md` (always-loaded) encoding the **data-side** hard stops, because this
repo's production surface is the stores, not a branch: dry-run reviewed in-session before any
`--execute`; never commit generated import manifests (`curriculum.jsonl`, `library_metadata.jsonl`
— the repo's own gitignore warns a partial manifest + FULL reconciliation *wipes the live store*);
no PDFs in git; no invented FAA facts; done requires `probe_bridge_hop` proof; Drive is the
authoring surface, the repo `.md` is machine truth; **never create `main_debug` here** (your review
memo, recorded so a future parity pass can't "fix" it back).

Rewrote `credential-resolution.md` for this repo. Dropped the five app-only rules that came with the
old fork (`voice-agent-architecture`, `useEffect-dep-array-stability`, `prompt-tdd`,
`adk_file_formating`, `pyrefly-paths` — no frontend, no voice agents, no pyrefly here).

### P3 — the grounding gate
The three authoring skills already existed and are good, so the work was the missing gate plus
wiring. New **`faa-grounding-gate`** skill: the golden rule, a table of every permitted source *with
its exact on-disk path*, what must be grounded, citation formats, the four hallucination red flags,
and the "won't ground → stop and flag for Daniel" protocol. Wired into both authoring skills as a
mandatory Step 0 plus an anti-pattern row.

**What fought back — and it matters.** I wrote the verification mechanic as "read the source PDF,"
then tested it. It doesn't work here: `Read` can't render PDFs (**poppler/pdftoppm not installed**)
and **`pypdf` isn't installed and isn't in `requirements.txt`**. I'd written aspirational fiction —
a gate that reads convincingly and cannot be executed. Rewrote §3 around what actually works:
**Path A** query DB2 (the FAA library is already ingested, 27 docs, credentials present in
`auth_keys/`), **Path B** ask Daniel for the operative text (he's the CFI — the designed gate, not
an escalation), **Path C** propose adding `pypdf` to unlock local extraction (dependency changes are
ask-first, so it's a proposal, not a fait accompli). The skill now says plainly: *don't claim you
read the PDF — you currently can't.*

Three stale-doc fixes: the phantom `reimport_with_metadata.py` paragraph in `curriculum_lifecycle.md`
§4 (which contradicted that same file's own banner), the wrong `scripts/ingest_quiz_banks.py` path,
and the `asset_registry.md` SJT row — see the finding below.

### P4 — BMAD-lite **(deviation from the approved plan)**
The plan said hand-copy `_bmad/` from `Fresh_Workspace_BMAD`. After your "not heavy" note I did
**not** install the module — only the board state. Rationale: the `sudo-*` skills are
*command-center → child project* tools; they read a child's `active-context` + `sprint-status`, and
the lobby holds the BMAD install. So the pipeline only needs honest state, and skipping the module
avoids re-importing the whole TEA/testing family you just told me to strip. Reversible if you want
the module later.

Seeded `_bmad-output/`: `README.md` (explains the lite shape), `project-context.md`,
`active-context/active-context.md`, `implementation-artifacts/sprint-status.yaml`. Epics = ACS Areas
II/IV/V/VIII/XII + an infrastructure epic carrying the four grounded debt items.

**Continuity-file conflict I hit:** I first put `active-context.md` in `_artifacts/` per AGY's
AGENTS.md §9 — then checked AGY on disk and found it has **no** `_artifacts/active-context.md`; the
real file lives at `_bmad-output/active-context/`. AGY's own doc is stale on that point. Followed
AGY's *practice* (not its doc), moved the file, and repointed `AGENTS.md` §6/§9 +
`_artifacts/README.md` so there's exactly one continuity file.

Area **titles left deliberately blank** in the board. No in-repo source has them (the Curriculum Key
only lists existing lessons) and the ACS PDFs aren't machine-readable here — so writing them would
have violated the gate I'd just authored. They're marked "TBD at kickoff, read from
`docs/private_airplane_acs_6.pdf`."

### P6 — Drive wiring proof
Pulled **"Area 6 Task B PPL.md"** from Drive `AVIAIONCHAT/ACS Modules` through the connector and
diffed it against `curriculum_components/curriculum_modules/`.

First comparison said *not identical* — the Drive payload looked like one 94,064-character line. It
turned out to be **base64-encoded**: the connector returns raw (non-Google-Docs) files encoded, and
these masters use CRLF. Decoded → exactly **70,548 bytes**, matching Drive's own `fileSize`, and:

```
IDENTICAL after decode+normalize: True
  drive md5: fe13a1491c75605a54897e639adc29d8
  repo  md5: fe13a1491c75605a54897e639adc29d8
  drive lines: 473   repo lines: 473
  drive [cite_start]: 399   repo: 399
```

**Byte-identical.** Drive and repo are in sync for this master, and the pull path is proven. The
base64 + CRLF handling is a mechanic the SOP must document — an agent that skips the decode will
"diff" garbage and wrongly conclude the master drifted.

---

## Findings for you (not fixed — they're your calls)

**1. The quiz answer key has a serious positional skew.** Measured across all 48 banks / 384
questions:

| | A | B | C | D |
|---|---|---|---|---|
| All questions | 19 | **258 (67%)** | 70 | 37 |
| risk_management (SJT) | 3 | **59 (61%)** | 2 | 32 (33%) |

Two-thirds of every correct answer is "B". And the app does **not** shuffle options —
`quiz_bank_service.py` shuffles *question order* only (`random.shuffle(buckets[...])`), and there's
no option shuffling in the frontend. So the skew is exposed to students as a real tell. It sits
below the 80% pass threshold, so it can't be brute-forced into a pass, but it's well above the 25%
chance baseline.

**This also breaks the SJT convention three ways at once.** The `quiz-bank-generation` skill says
"OPTION D → ✅ CORRECT, always"; the PRD says that rule was retired; the data says D is correct only
33% of the time. I did **not** edit the skill's convention — "what should the SJT pattern be" is your
pedagogy call, and my read is the right answer is *no positional meaning at all*, which implies
re-balancing 384 existing questions. I replaced the false `asset_registry.md` row ("Always D") with
the measured reality plus the open decision, and filed it as board story `6-3-quiz-answer-key-balance`.

**2. `specialist_curriculum/` is dead.** One leftover file, `1 ACS Curriculum Key.json`,
**byte-identical** (md5 `8ab095f7…`) to the live copy in `pipeline/curriculum/`. Nothing reads it. I
wrote an INDEX marking it LEGACY rather than deleting — deletion is a gated action. **Recommend
deleting the folder; say the word.**

**3. `docs/` vs `_docs/` both exist** (ACS PDFs + repo-map in one, all documentation in the other).
Tooling auto-detects, so it's not breaking anything. Left alone, flagged for the SOP debt register.

**4. No `.venv` in this repo.** Tests ran on the global interpreter and passed, but per the AGY
lesson (`agy-venv-interpreter-discipline`) a drifted global can produce false missing-dep findings.
Worth creating one before the first real authoring batch.

---

## Verification (actual output)

**Structure conformance — clean:**
```
MAP & INDEX DRIFT LINT  (BMAD project: RAG_Pipeline_AC)
  [ok] clean   ×7
  [ok] continuity brief + INDEX within the prune window
  [ok] no GitNexus index in this workspace - nothing to verify
All maps & INDEXes agree with disk. [ok]          EXIT: 0
```
(First run failed with 16 missing level-2 INDEX.md files + "not conformant — missing structure
standard"; wrote all 16 INDEXes and vendored `docs/workspace-standard.md`. Second run needed the
BMAD-mode ignore flags — `--ignore _my_resources,_bmad` — because adding `_bmad-output/` flipped the
detected project mode. Third run clean.)

**Offline test gate — green, unchanged:**
```
sssss............................    [100%]
28 passed, 5 skipped in 0.13s
```
(= the documented 33; structure work touched no `src/` code beyond deleting the empty `src/pipeline/`.)

**Shared rules byte-identical to the lobby master:**
```
MATCH  constitution.md          MATCH  karpathy-guidelines.md
MATCH  operator-profile.md      MATCH  artifacts-always-first.md
MATCH  git-policy.md
```

**Ghost sweep:** `1_ccps` / `1_live_testing` / `1_run-restart` references outside frozen history =
**0**. GitNexus blocks in front doors = **0**. Remaining `_claude_artifacts` matches are all
*prohibitions* ("never write here") or frozen `_artifacts/20*` history — except two provenance links
to folders I moved, which I repointed. Cross-repo dead-provenance links in
`self_learning_tracking_metrics.md` left alone per house precedent.

---

## Continuation — 2026-07-23 (P5 executed + live-store audit)

Daniel switched models and said go: "write the shared document, then we can fix all of those."

- **P5 shipped.** `_docs/SOP_curriculum_operations.md` written — three stations, source-of-truth
  ladder, **STANDING RULE: new curriculum is pulled from Drive** (`ACS Modules`, base64+CRLF decode
  documented), per-lesson lifecycle with owners, quiz answer policy (no positional meaning),
  live-store discipline + drift doctrine, app consumption map, debt-register pointer. Cross-links:
  lobby `router.md` pipeline row → **converted** (+ SOP pointer), AGY `AGENTS.md` §6 upstream row,
  pipeline README doc-index row, stale `_artifacts/active-context` mention in pipeline AGENTS §3
  fixed. Conformance lint re-run: **exit 0**.
- **One planned edit deliberately NOT made:** the 48+48 mirror actually lives at
  `_my_resources/_docs/specialist_lesson/` — inside Daniel's **protected personal area** (the plan
  assumed `_docs/`). No README written there; the SOP's mirror-policy section covers it instead.
- **Read-only Firestore audit** (Daniel: "first pull the real ones from firebase") — script + full
  pull saved in the session scratchpad (`firestore_readonly_audit.py`, `firestore_pull/`):
  - **Skew confirmed live and identical to repo:** `correct_answer` B 258/384 (**67%**), C 70, D 37,
    A 19; safety perspective has **zero** correct-D; SJTs (risk_management) B 61% / D 33%.
  - **Zero content drift** repo↔live on any shared field; the only difference is **206 empty
    `sjt_rationale` fossils** live-side (`merge=True` never deletes a removed field). Manifests
    **48/48 byte-identical**. Rotation state (`seen_by`) empty everywhere — cleanest moment to fix.
  - App serves `sjt_rationale` to students (`backend/routers/quiz.py:217`); **263/384 explanations
    + all 92 real SJT rationales reference options by letter** — that prose re-anchor is the real
    workload of the fix, not the shuffle.
- **Remediation plan written** (story `6-3` → ready-for-dev), project-local:
  `Projects/RAG_Pipeline_AC/_artifacts/2026-07-23_quiz-rebalance-firestore-truth/implementation_plan.md`
  — R1 legacy snapshot → R2 deterministic re-letter (exactly 2 per letter per bank) → R3 letter-free
  prose re-anchor → R4 permanent distribution test → R5 fossil `DELETE_FIELD` → R6 dry-run/
  `--execute`/prove → R7 delete legacy. **Awaiting Daniel's "approved" + its 3 open questions.**

## Continuation — 2026-07-23 (later): 6-3 approved & EXECUTING — R1/R2/R4/R5 done, R3 fleet paused

Daniel's answers: **letter-free prose · multi-agent workflow for R3 · legacy folder committed.**

- **R1** — `curriculum_components/quiz_banks_legacy_2026-07-23/` snapshot, 48/48 md5-identical +
  README/INDEX. The repo's blanket `*.json` credentials guard was silently hiding the snapshot from
  git — added a temporary `.gitignore` carve-out (removed with the folder at R7).
- **R2** — NEW `scripts/rebalance_quiz_answers.py` executed. Format round-trip proven 48/48 BEFORE
  writing (caught 14 banks with a variant trailing-newline convention), then A19/B258/C70/D37 →
  **96/96/96/96**, 283/384 keys moved, the "None of the above" pin held at D (`PPL_PA_I_G_05`
  Q004), texts/pins/non-option fields hard-asserted unchanged. Letter table saved project-local:
  `_artifacts/2026-07-23_quiz-rebalance-firestore-truth/r2_letter_map.md`.
- **R3 — in flight, paused on the Claude session limit.** Targeting scan corrected the audit: the
  true letter-anchored set is **282 explanations + 63 sjt_rationales on 315 questions** (the audit's
  263 missed parenthetical "(A)" refs; its "all 92" rationale claim was loose — 29 are already
  letter-free; "W&B" / "A&P" / "HAVE A PLAN" were false positives). Workflow per bank: rewrite
  (from the LEGACY file, so original letters resolve) → independent adversarial verify (letter-lint
  + factual invariance) → one repair round. **Two fleet launches hit the session limit** (~1.8M
  subagent tokens): 9 banks' rewrites journal-cached, 16 valid rewrite files on disk, none verified
  yet. **Resume after the 3:20pm ET reset** — cached agents replay free, then apply → suite green.
- **R4 + R5 — your frozen parallel task had already built both from the approved plan** (mtimes
  00:52 ET); verified line-by-line and kept: `src/tests/test_answer_distribution.py` (per-bank
  2-per-letter · corpus uniform scaled to bank count · letter-free lint; **red on lint for all 48
  banks BY DESIGN until R3 applies** — suite currently 78 pass / 48 expected-red / 5 skip) and the
  ingester `sjt_rationale: DELETE_FIELD` delta (dry-run announces 292 clears; ~206 hit live fossils).
- **Mid-flight sweep commits `22be19e`/`73632c7`** (00:52–00:57 ET, authored while the first fleet
  was dying — your side, not mine) captured the whole conversion + R1/R2 + SOP/skill edits.
  **Audited clean: no credentials, no PDFs, no generated import manifests.** The frozen task's
  uncommitted leftovers (board comment, quiz_banks INDEX rewrite, `r2_letter_map.md`) were accurate
  and kept.
- **Drift-proofing (your mid-turn directive)** — SOP **§6** now carries the full authoring
  direction: balanced **{A,A,B,B,C,C,D,D}** key, LETTER-FREE feedback prose (name content/behavior;
  "Class B airspace" proper names fine), Chain-of-Cues shape, enforcement pointer. And the
  `quiz-bank-generation` skill (master + `.claude` mirror) is de-positionalized — the old
  "A=get-there-itis … D=correct" SJT grid that CAUSED the skew is retired at the authoring surface,
  replaced with attitude-tags-travel-with-text + balanced-key rules.
- **New bug found reviewing R5 — story `6-5` filed:** the ingester always writes `seen_by: []` /
  `last_seen_at: None` into the merge payload, so ANY re-ingest resets live rotation state
  (contradicts its own docstring). Harmless today — the audit proved rotation state is empty
  everywhere — but real once students accumulate history. Fix before the next re-ingest after launch.
- **Blast radius (your directive) — verified:** the complete reader surface of `quiz_banks/*.json`
  is `src/config.py` (path def) · the ingester (reviewed) · `generate_state_map.py` (counts only —
  letter-invariant) · the rebalance script · the new test. The app consumes **Firestore**, not repo
  files — and **zero store writes happened** (the only Firestore touch this session was the earlier
  read-only audit). App repo mirror in protected `_my_resources/` untouched. RKP manifests, DB1/DB2,
  `src/utils/schema.py`, app `backend/schemas/quiz.py` untouched. Legacy folder invisible to every
  tool (`config.QUIZ_BANKS_DIR` still points at `quiz_banks/`). Conformance lint EXIT 0.

## Continuation — 2026-07-23 (late): R3 finished, story 6-3 code-complete

**The multi-agent fleet failed three times and I stopped using it.** Two Fable launches and one
Opus launch burned **~5.6M subagent tokens** and each one died on the account session limit — the
Opus attempt pushed the reset to 9:20pm and still only finished **19 of 48** banks. A 48-bank
fleet does not fit inside one session window, and every retry ate budget that blocks your other
work. Your plan listed per-batch inline rewriting as the sanctioned alternative, so I switched to it.

**What replaced it — surgical positional replacement.** Instead of regenerating whole explanations
(expensive, and every regeneration risks factual drift), the inline tooling re-finds each
letter-referencing span *in document order* and swaps in a content phrase, leaving **every other
byte of the field untouched** — factual invariance by construction. Scratchpad tools:
`r3_surgical_extract.py` (shows only the letter spans + the option map) and `r3_surgical_apply.py`
(positional replace, then re-lint). The 19 completed Opus banks were kept and lint-gated.

**Result — all verified against the frozen legacy snapshot:**

| Check | Result |
|---|---|
| Answer key distribution | **96 / 96 / 96 / 96** |
| Feedback fields rewritten | **345** (282 explanations + 63 SJT rationales, all 48 banks) |
| Option-letter references remaining | **0** |
| Test suite | **126 passed · 5 skipped · 0 failed** |
| Fabricated facts (number/citation not in the question) | **0** |
| Lost citations | **0** (the one flagged "180" was a tokenization artifact — `FL180` is in both) |
| Non-prose fields (ids, stems, `far_reference`, `acs_element`) | **byte-identical to legacy** |
| Conformance lint | exit 0 |

**Two correctness catches worth knowing about.** First, the narrow "Option X" regex — the one the
permanent test uses — **misses bare references** like "while C and D have errors" and parenthetical
lists like "(A, D)". I scanned all 48 banks: 884 narrow refs but only ~5 genuine bare ones. The
parenthetical-list form is now caught by the permanent test (safe, unambiguous); the handful of
bare-prose ones were fixed explicitly. Second, a bare "safer than B" hid inside `PPL_PA_I_G_04_Q006`
alongside nested parentheticals — fixed with explicit pre-replacements.

**R6 EXECUTED — Daniel approved and spot-checked the prose ("passes the in person test").**
Ingested **384 questions across 48 lessons**; **292** `sjt_rationale` DELETE_FIELDs sent.

| Live proof (read-only audit re-run after the write) | Result |
|---|---|
| Live `correct_answer` distribution | **96 / 96 / 96 / 96** (25% each) — was B 258 (67%) |
| Safety perspective correct-D | **24** — was **zero** |
| repo ↔ live drift | **identical=48, differs=0** — the 206 `sjt_rationale` fossils are **gone** |
| RKP manifests | identical=48 (untouched, as planned) |
| Rotation state (`seen_by`) | still empty on all 384 — no student state disturbed |
| `generate_state_map.py --live` | clean |
| `probe_bridge_hop.py` | **48/48 lessons ≥1 DB2 hit** — bridge intact |

**Only R7 remains:** delete `quiz_banks_legacy_2026-07-23/` + its `.gitignore` carve-out, on
Daniel's explicit word. Until then that frozen snapshot is the rollback path.

## Task Checklist

- [x] P0 — operator-profile wired into AGY `AGENTS.md` §4 (rule + INDEX row already in place)
- [x] P1 — front doors, Layer-2 `AGENTS.md`, toolkit vendored, artifacts consolidated (history via `git mv`), `_my_resources/` seeded, repo-map generated, GitNexus dropped, md-feedback wired
- [x] P1b — pruned to the lean set (skills 45→8, commands 17/43→1/1) + keep-list INDEX + re-sync warning
- [x] P1c — 16 level-2 `INDEX.md` files, `workspace-standard.md` vendored, conformance lint exit 0
- [x] P2 — `constitution.project.md`, `credential-resolution.md`, 5 app-only rules dropped
- [x] P3 — `faa-grounding-gate` authored (corrected after testing), wired into both authoring skills, 3 stale-doc fixes
- [x] P4 — BMAD board state seeded (**deviation:** no `_bmad/` module — see above)
- [x] P5 — SOP + cross-links shipped 2026-07-23 (mirror README skipped — folder is inside protected `_my_resources/`; policy lives in the SOP instead)
- [x] Live Firestore audit (read-only): skew confirmed live, zero content drift, manifests clean
- [x] Story 6-3 **code-complete** — R1 snapshot · R2 rebalance (96×4) · R3 letter-free prose (345 fields, 0 refs, 0 fabricated facts) · R4 gate green (126 passed) · R5 fossil delta · R6 dry-run reviewed. **Blocked only on your `--execute` word, then R7**
- [x] Blast-radius sweep + SOP §6/skill drift-proofing (Daniel's two mid-turn directives)
- [x] P6 — Drive pull proven byte-identical (base64 + CRLF mechanic discovered)

## Your Actions

**1. ~~Commit the pipeline conversion~~ — already happened.** The sweep commits `22be19e` +
`73632c7` (00:52–00:57 ET 2026-07-23, made from your side while the R3 fleet ran) captured the
conversion, R1/R2, SOP and skill edits — audited clean (no credentials/PDFs/generated manifests).
The AGY pointer row also landed (`8bc8420b`), and the earlier lobby pointer edits are in. What
remains is the small 6-3 execution delta:

```bash
cd c:/Sudo_Hatter_Command/Projects/RAG_Pipeline_AC
git add -A .gitignore curriculum_components docs _docs _bmad-output _artifacts \
          AGENTS.md README.md .agents .claude src scripts
git commit -m "feat(6-3): letter-free quiz feedback prose, shipped; docs merged into docs/

- R3 complete: 345 feedback fields (282 explanations + 63 SJT rationales) across all 48
  banks now reference option CONTENT, never letters -> a future re-letter is free
- verified vs the frozen legacy snapshot: 0 letter refs remain, 0 fabricated facts,
  0 lost citations, non-prose fields byte-identical; suite 126 passed / 5 skipped
- test gate also catches parenthetical letter lists ((A, D)); ~5 bare refs fixed by hand
- gitignore carve-out so the 48 legacy snapshot JSONs are tracked (removed at R7)
- shipped to Firestore: 384 questions / 48 lessons, 292 sjt_rationale DELETE_FIELDs;
  live proof 96x4, drift identical=48 (fossils gone), manifests 48, bridge 48/48
- R7: legacy snapshot + its gitignore carve-out deleted; story 6-3 closed
- docs: _docs/ merged into docs/ (one documentation folder); _my_resources/ is personal
  again. Fixed two generator scripts that hardcoded the path as a quoted segment and
  silently recreated a ghost _docs/ on every run
- instrument track prepped: SOP section 10 + epic-7-instrument-kickoff
- NEW stories: 6-5 (re-ingest resets seen_by rotation state) and 6-6 (a lesson is
  invisible to students until the app's curriculum_key.json lists it)"
```

**2. Lobby session record delta** (today's walkthrough + INDEX updates):

```bash
cd c:/Sudo_Hatter_Command
git add _artifacts/INDEX.md _artifacts/_main/2026-07-22_pipeline-conversion-and-sop
git commit -m "docs(session): 6-3 approved+executing - R1/R2/R4/R5 done, R3 fleet paused at session limit"
```

**3. Story 6-3 is CLOSED.** R7 done on your word — legacy snapshot and its `.gitignore` carve-out
deleted, board → `done`. Nothing outstanding on it.

**4. Docs merged into one `docs/` folder** (your `_docs` → `_my_resources` move would have broken
~40 references and was silently recreating a ghost `_docs/` on every state-map run). `_my_resources/`
is purely personal again. **The two-team guide you asked for is at
`Projects/RAG_Pipeline_AC/docs/SOP_curriculum_operations.md`.**

**5. Instrument track is prepped** — SOP §10 + `epic-7-instrument-kickoff` on the board. Three
decisions are yours before authoring starts: the lesson-id prefix (it becomes the app's permanent
certificate namespace), the Drive master naming suffix, and the per-Area epics. New story `6-6`
flags the cross-repo gap: a lesson isn't visible to students until the **app's**
`backend/data/curriculum_key.json` lists it.

**4. Decisions still open:**
- **Delete `specialist_curriculum/`?** Dead folder, byte-identical duplicate. One word and it's gone.
- (Optional) a README banner inside `_my_resources/_docs/specialist_lesson/` in AGY — that's your
  protected area, so it's yours to add; the SOP already records the mirror policy.
- Story `6-5` (rotation-state reset on re-ingest) sits in the backlog for prioritization.
