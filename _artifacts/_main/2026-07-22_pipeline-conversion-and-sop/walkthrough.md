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
- [ ] Story 6-3 re-balance — **plan awaiting approval** (project-local artifact in the pipeline repo)
- [x] P6 — Drive pull proven byte-identical (base64 + CRLF mechanic discovered)

## Your Actions

**1. Commit the pipeline conversion.** Single repo, single `main` branch (no debug branch, per your
memo). This touches nearly everything, so explicit top-level paths rather than `git add -A`:

```bash
cd c:/Sudo_Hatter_Command/Projects/RAG_Pipeline_AC
git add -A .agents .claude .opencode .gemini _artifacts _bmad-output _docs _my_resources \
          AGENTS.md CLAUDE.md GEMINI.md README.md .mcp.json \
          curriculum_components docs pipeline specialist_curriculum src
git commit -m "chore(workspace): convert to house standard, lean toolkit, grounding gate, BMAD-lite

- front doors: CLAUDE.md/GEMINI.md pointers + Layer-2 AGENTS.md workspace map
- vendored .agents (19 master rules), pruned to a LEAN set: 8 skills, 1 command
  (no sudo flow, no autopilots, no BMAD/TEA testing family, no app-only skills)
- project rules: constitution.project.md (data-side hard stops) + credential-resolution
- new faa-grounding-gate skill; wired into rkp-manifest-creation + quiz-bank-generation
- artifacts consolidated _claude_artifacts/_opencode_artifacts -> _artifacts (history via git mv)
- BMAD-lite board state in _bmad-output (no _bmad module by design)
- GitNexus dropped: de-grouped from ac-stack, local index deleted
- 16 level-2 INDEX.md + repo-map; conformance lint exit 0; 33 tests green
- branch model: single main BY DESIGN (workhorse repo, deployed nowhere)
- two-team SOP (_docs/SOP_curriculum_operations.md) + quiz re-balance plan (story 6-3, awaiting go)"
```

(The 2026-07-23 additions — SOP, plan artifact, board updates — all fall under the paths already
listed, so the one command captures the whole thing.)

**2. Lobby + AGY each picked up small pointer edits on 2026-07-23** (your `aab6491`/`6ff0aad`
commits covered everything earlier):

```bash
cd c:/Sudo_Hatter_Command
git add router.md _artifacts/INDEX.md _artifacts/_main/2026-07-22_pipeline-conversion-and-sop
git commit -m "docs(router): RAG_Pipeline_AC -> converted; session record: SOP shipped + quiz audit"

cd c:/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT
git add AGENTS.md
git commit -m "docs(agents): route curriculum content upstream to RAG_Pipeline_AC + its SOP"
```

**3. Decisions still open:**
- **Story 6-3 re-balance plan** — review
  `Projects/RAG_Pipeline_AC/_artifacts/2026-07-23_quiz-rebalance-firestore-truth/implementation_plan.md`
  and answer its 3 open questions (letter-free prose? batch cadence? legacy folder committed?).
  Say "approved" to start R1.
- **Delete `specialist_curriculum/`?** Dead folder, byte-identical duplicate. One word and it's gone.
- (Optional) a README banner inside `_my_resources/_docs/specialist_lesson/` in AGY — that's your
  protected area, so it's yours to add; the SOP already records the mirror policy.
