# Architecture Decision Proposal — Formalizing a Firestore Schema (2026-08-05)

> **Status: 🟡 PROPOSED — pending team review. Not yet approved or implemented.**
> Prepared via AI-assisted research/analysis session, verified directly against the current
> codebase (file:line citations throughout). Open decision for the team in §5.

---

## Context

AviationChat's primary data store, Firestore (`aviationchat-database`), is schemaless by
design — Firestore itself enforces no document shape. As the project has grown (68 backend
files now write across 37+ collections/subcollections), the question came up: should we
formalize a schema on top of it, and if so, how much of one? This document lays out what's
actually true about the current state, a recommendation, and the explicit tradeoffs — so the
team can decide with real evidence instead of a generic "NoSQL needs schema" instinct.

**Bottom line up front: formalize a schema, but scoped to documents with multiple
independent writers — not a blanket migration across all 37+ collections.** The reasoning
follows.

---

## 1. What's actually there today

### An informal schema layer already exists, unevenly applied
`backend/schemas/` has ~30 Pydantic models. Some collections are well-governed:
- **`MasteryRecord`** (`backend/schemas/mastery.py`) — `users/{uid}/mastery/{lesson_id}`.
  `mastery_service.py` round-trips through the model on every read and write inside Firestore
  transactions. This is the gold-standard pattern in the codebase today.
- **`SessionLog`** — mostly model-enforced, with a documented, deliberate carve-out for
  Firestore transform fields (`ArrayUnion`/`Increment`) that can't survive `model_dump()`.

But the **single most-written document, `users/{uid}` (the root user doc), has no model at
all.** At least four independent modules write raw, uncoordinated dicts into different slices
of it: `pending_lesson_service.py`, `routers/consent.py`, `routers/nda.py`, and
`profile_service.py`.

### There is precedent for exactly this problem — and it's already been fixed once
A real production incident (**Story debug-1.5**) happened on this exact doc: two writers
(Mrs. Coleman's onboarding tool calls, and a blind LLM re-sweep of the chat transcript) raced
on identity fields (`name`, `call_sign`, etc.). The re-sweep once `set(merge=True)`-ed a
school code (`TESTPILOT`) over a confirmed call sign. Nothing threw, nothing logged.

The fix was `backend/services/profile_service.py` — a single sanctioned chokepoint for those
fields, with:
- `CANONICAL_FIELDS` — the exact fields it owns
- `AUTHORITY` — a source-ranking table (`admin_manual: 30`, `coleman_tool: 20`, `derived: 10`)
  so a write only lands if it out-ranks whatever's already stored
- `field_provenance` — a side-car map recording who wrote each field and when
- Two CI tests enforcing it: a positive allowlist (`test_all_profile_call_sites_use_profile_service`)
  and an AST-based scan banning module-scope Firestore singleton imports
  (`test_no_module_scope_firestore_singleton_import`)

**This chokepoint does not yet cover the other raw writers on the same document.** And the
same failure shape exists *today*, live, unfixed: `last_active` is written independently by
both `routers/nda.py:59` (`firestore.SERVER_TIMESTAMP`, a Firestore sentinel) and
`profile_service.py:429` (`_now_iso()`, a Python string) — two different writers, two
different value formats, no arbitration. It hasn't caused a visible bug yet only because both
values are "roughly recent" either way — but it's the identical unguarded pattern that caused
the debug-1.5 incident on other fields.

### Firestore security rules cannot be the enforcement mechanism
Checked directly: **every single rule in `firebase/firestore.rules` is `allow write: if
false`** (or `allow read, write: if false`) — for every collection, no exceptions. The Admin
SDK (used by virtually all backend writes) bypasses security rules entirely regardless.
Investing in Firestore-native `request.resource.data` shape validation would be validating a
door that's already welded shut. **Schema enforcement has to live at the application layer
(Pydantic + service chokepoints), not in Firestore rules.**

### The two real production incidents were NOT "missing schema" bugs
Story 11.9 (`set(merge=True)` doesn't expand dotted keys — silently created a broken flat
field instead of a nested map) and Story 14.9 (`set(merge=True)` replaces list fields instead
of appending — silently dropped prior entries) were both **operation-semantics** bugs, not
shape bugs. A schema doesn't prevent either on its own. What actually prevents them is
routing writes through validated service methods that encode the correct
read-modify-write pattern once (see `GlobalProfileService.distill_checkride` as the
reference implementation) — which a chokepoint-based schema rollout naturally supports, but
shouldn't be oversold as a silver bullet for.

### The pilot-identity "sprawl" is intentional, not accidental — verified directly
Initial analysis flagged three overlapping representations of pilot identity
(`profile_service`'s flat fields, `pilot_profile_service`'s Tier 0 doc, `global_profile_service`'s
Tier 1 doc) as risky duplication needing consolidation. **Checking the code directly disproved
this.** `profile_service.py`'s own docstring states explicitly:

> "It is NOT the pilot dossier. `pilot_profile_service.py` (Tier 0) and
> `global_profile_service.py` (Tier 1) own SUBCOLLECTION documents... a different tier with a
> different lifecycle. Folding this module into either of them re-creates the second writer
> story debug-1.5 deleted."

This is a deliberate, documented architectural decision with an explicit warning against
undoing it. **Recommendation: leave this tiering alone.** It's a good example of why
verifying claims against the actual code — not just a first-pass read — matters before this
kind of change gets proposed to a team.

### One stale doc should be retired as part of this work
`.claude/skills/hr-agent-schema-guide/SKILL.md` describes a "TA Agent" data hub with
`get_student_profile()`/`update_student_profile()` tools that don't exist, documents only 3
of the 37+ real collections, and shows a security-rules example (`allow read, write: if
request.auth.uid == userId`) that is the **opposite** of the real rule (`allow write: if
false`). Anyone who greps this file while reasoning about the system gets actively wrong
information. It should be retired or rewritten alongside any schema-formalization work, not
left to rot next to the real source of truth.

---

## 2. The scope decision: targeted vs. full coverage

This is the actual decision for the team. Both options were analyzed; here's the honest
tradeoff.

### Option A — Targeted (schema only where 2+ writers touch the same document)

| | |
|---|---|
| **Pros** | Fast (days, not weeks) — extends the existing `profile_service.py` pattern rather than inventing new infrastructure. Directly closes the one *proven* incident class (debug-1.5-style races), including the live `last_active` example above. Small, maintainable CI surface (a couple of generalized AST tests). Zero wasted effort on the ~30 collections with a single writer and no history of contention — schema wouldn't protect against anything real there. Reversible — extend coverage later if a currently-safe collection grows a second writer. |
| **Cons** | No blanket documentation/type-safety story across the whole data model. Frontend keeps reading most Firestore docs as loosely-typed outside the covered set. Minor inconsistency ("why does mastery have a strict model but bug_reports doesn't?") — mitigated by writing the policy down explicitly. |

### Option B — Full coverage (formal schema across all 37+ collections)

| | |
|---|---|
| **Pros** | Uniform guarantee on every document's shape. Best onboarding story — `backend/schemas/` becomes the real data model instead of grep-archaeology across 68 files. Enables systematic (not ad hoc) frontend type mirroring. |
| **Cons** | **No evidence it's needed** — neither real production incident was a "missing schema" bug. Large surface area for the payoff: many of the 37+ collections are touched only by one-off admin/debug scripts (`fix_all_admins.py`, `clear_db.py`, `check_db.py`) with essentially zero production risk. Touching that many live write paths on an already-live project is itself a source of regressions. CI/maintenance burden scales with collection count — a bloated guardrail is *more* likely to get bypassed by a future contributor in a hurry, not less. Realistic cost: weeks-to-months against a team mid-sprint on product features. |

### The actual fault line in the evidence
Risk doesn't scale with collection *count* — it scales with writer **contention** (multiple
independent writers touching overlapping fields on the same document, with no coordination).
That's `users/{uid}` today, and possibly a handful more once someone does a cheap write-
frequency grep across the other 15 `users/{uid}` subcollections. Below that line, a Pydantic
model is still fine to add opportunistically for read-side convenience — it just doesn't
justify the chokepoint-plus-CI-gate investment that multi-writer documents do.

---

## 3. Recommended plan, if the team chooses Option A

**Phase 0 (small — days):**
1. Extend `profile_service.py`'s chokepoint (or a sibling using its `AUTHORITY`/
   `field_provenance` machinery) to cover the remaining raw `users/{uid}` writers:
   `pending_lesson_service.py`, `routers/consent.py`, `routers/nda.py`, and resolve the
   `last_active` dual-writer conflict specifically.
2. Generalize the existing AST-based CI test
   (`test_no_module_scope_firestore_singleton_import` in
   `backend/tests/routers/test_hr_profile_single_writer.py`) from "profile fields only" to a
   general collection-write scan with a `known_debt` allowlist, so any *new* raw `.set()`/
   `.update()` bypassing a sanctioned model gets caught in CI.
3. Retire or rewrite `.claude/skills/hr-agent-schema-guide/SKILL.md` so it stops being a
   second, wrong source of truth.
4. **Do not** touch the `pilot_profile`/`global_profile` tiering — it's intentional, already
   documented, and merging it was already tried and reverted once.

**Phase 1 (medium, only after Phase 0 ships):** Apply the same one-model-plus-chokepoint
pattern to whichever 2-4 more collections a cheap write-frequency grep shows have genuine
multi-writer contention — not a predetermined list.

**Phase 2 (only after Phase 0/1 stabilize):** Mirror the covered models to TypeScript on the
frontend, following the one precedent that already exists (`frontend/src/types/rkp.ts`,
which explicitly documents itself as mirroring `backend/schemas/rkp.py`). Start with
`users/{uid}`, since `frontend/src/lib/firebase.ts` currently reads it as
`Record<string, unknown>` / `any`.

### Explicit non-goals
- No Firestore security-rules-based shape validation (confirmed low-leverage — see §1).
- No single migration/backfill touching all 37+ collections at once — validate-on-write going
  forward, tolerant construct-with-defaults on read for legacy docs (the same pattern
  `MasteryRecord` and `PilotProfile` already use), so no backfill is required.
- No consolidation of the pilot-identity tiering (§1 — verified intentional).
- Don't oversell this as preventing the two real past incidents (11.9, 14.9) — those were
  operation-semantics bugs; this work prevents the *next* debug-1.5, not those.

---

## 4. Writer contention — the operative concept

"Writer" = any distinct piece of code that independently issues a write against a given
Firestore document — a router, a service, an agent tool, a background job. "Contention" =
when two or more of those writers can touch the *same document* (or the same field) without
any shared coordination, so their writes can race, clobber each other, or disagree on what a
field even means. `last_active` on `users/{uid}` (§1) is a live example of this today, not a
hypothetical. This is the concept Option A's scope test (§2, "actual fault line") is built on.

---

## 5. Open question for the team

Which option — A (targeted) or B (full coverage) — matches the team's risk appetite and
available time? If undecided, Option A's Phase 0 is small and reversible enough to be a
reasonable default while the team decides on B separately.
