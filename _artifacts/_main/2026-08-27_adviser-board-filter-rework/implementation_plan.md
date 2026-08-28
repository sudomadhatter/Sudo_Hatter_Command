# Implementation Plan — Adviser Board filter rework (`/smh-adviser-board`)

**Date:** 2026-08-27 · **Workspace:** `_main` (lobby / home-base) · **Status:** awaiting operator approval
**Design status:** SETTLED — brainstormed and approved live with Mr. Hatter. This plan turns the approved
design into a concrete, file-grounded change list. Do not deviate from the design decisions in §3.

---

## 1. Goal

Rework `/smh-adviser-board` from a **team/caucus** architecture (one subagent per team of 3 minds, 5
hidden debate cycles, one ~250-word card per team) to a **filter** architecture:

> **One filter = one mind = one subagent.** Collision happens across the board, visible to the chair —
> not inside a sealed caucus.

The board becomes four visible rounds (READ → ATTACK → BALCONY → SETTLE), each filter is one spawn
carrying the shared context, and the chair sees every statement verbatim instead of a card that is a
summary of a summary.

## 2. Background — why

- **Sub-chats are invisible.** The current debate runs 3–5 cycles inside one spawn per team
  ([`SPAWNS.md` §4](.agents/commands/adviser-board/SPAWNS.md)); the chair sees only the card. The
  argument he most wants — the collision — is the part he never sees.
- **The card is a summary of a summary.** [`CARD.md`](.agents/commands/adviser-board/CARD.md) forces
  three minds into one ~250-word card in "one voice"; the caucus clause asks the card to be "true of the
  floor" the chair cannot read. Attribution gets mushy at exactly the point the board exists to be sharp.
- **"We need 5 teams for this?"** — the operator pushed back twice in one session
  ([memory: adviser-board-roster-is-product-shaped](../../_memory/adviser-board-roster-is-product-shaped.md)):
  casting for coverage buries him in cards that restate each other. The caucus memory
  ([adviser-board-caucus-card-contract](../../_memory/adviser-board-caucus-card-contract.md)) locked the
  presentation preferences (one voice, credited originators, withheld deliberation) — those *principles*
  survive, but their *mechanism* (hidden caucus + presenting speaker) becomes obsolete under one-mind
  spawns: one voice is now structural, credit is now trivially correct, and deliberation is now visible
  rather than withheld.
- **Inspiration:** [`bmad-party-mode/SKILL.md`](.claude/skills/bmad-party-mode/SKILL.md) — one subagent
  per voice, fresh spawn per round with a running summary (≤400 words, refreshed every 2–3 rounds) plus
  the other voices' latest statements, cross-talk as a primitive, an optional orchestrator note. Adopt
  the spawn/round mechanics; **do not** adopt its memlog/party-memory — the board's no-memory rule stands.

## 3. Approved design decisions (condensed — settled with the operator)

1. **Kill the sub-chats.** Unit of work: one filter = one mind = one subagent. No teams, no rooms, no
   caucuses, no floors.
2. **Vocabulary: teams/rooms → filters.** A filter is the lens; the seated historical mind is who looks
   through it. Stage rooms (Execution Reality, Sales) lose special status — ordinary filters the cast can
   seat like any other. **Step 7 (stage change) and the stage gate are DELETED.**
3. **Round 0 — the cast menu (new Step 2).** After recon, the orchestrator picks the filters (scale rule
   survives: count distinct failure surfaces; cut lines shown for refused filters — keep the
   "write the negative" gate), then for EACH seated filter suggests its **TOP 3 minds** from the full
   43-mind roster, each with ONE line on the angle that mind would take on THIS topic. Operator picks one
   mind per filter, or says "your pick" (orchestrator's top line). "Gavel" begins the session. All 43
   minds stay eligible — the menu is a shortlist, not a bench. The default-triad concept dies; each
   filter gets a ranked top-3 ordering rule instead.
4. **Board rounds** (replaces the 5-cycle hidden caucus) — four visible rounds, each filter = one spawn
   carrying ground brief, third-side stance, running summary (≤400 words, refreshed every 2–3 rounds),
   and every other filter's latest statement; **all spawns parallel in one message**:
   - **R1 READ** — independent takes, written before any mind sees another's (absorbs the old separate
     Read round / Step 3 — with one mind per filter a separate comprehension pass is redundant).
   - **R2 ATTACK** — each filter attacks the statement it finds weakest, naming whose.
   - **R3 BALCONY** — is the disagreement real, or is the frame wrong? Reframes minted here (third-side
     discipline unchanged).
   - **R4 SETTLE** — concede, entrench, or adopt the reframe; unresolved splits named.
5. **Render (Step 5 replacement):** each filter's statement verbatim (~250-word ceiling per statement),
   then the `⚖` sharpest cross-filter collision line, then deduped COULDN'T SETTLE questions capped at
   two, then STOP — no menu. Narrative read first (operator-profile obligation 2).
6. **Traffic table collapses** to six moves: react to another filter · swap the mind in a seat (top-3
   menu again, lead with what is lost) · unpack · just-Feynman · new angle (recast) · close the board.
   Twelve moves → six.
7. **Keep unchanged:** Step 0 convene/flags; Step 1 recon → ground brief ≤500 words with mandatory
   `UNVERIFIED:` line; the chair rules (advance only on the operator's word, ask rather than guess, no
   process talk, stop after each round); third-side doctrine; endorsement ledger (★ verbatim, ↓ cooled);
   failure playbook (adapted: "near-identical safe verdicts" → respawn one filter against the strongest
   opposing statement); no-memory rule; "board sees what the chair sees" (simplified — with no caucus
   there are no floors, so the floor-circulation rules reduce to: statements circulate, nothing else);
   context discipline; session brief template + close (Step 8: narrative ~400 words, brief to
   `_artifacts/board_sessions/YYYY-MM-DD-<topic-slug>.md`, INDEX.md row); `--solo`/`--inline` mode
   (SIMPLER — inline degradation rules shrink since one spawn per filter was the expensive part; keep the
   capability test; keep "balcony never cuts").
8. **Contract changes:** `CARD.md` → STATEMENT contract (one voice = the mind itself, ~250-word ceiling,
   keep THE THIRD SIDE slot — outranks THE MOVE — COULDN'T SETTLE ≤2, ASSUMED, SPLIT,
   credit-to-originator; DELETE the caucus clause and presenting-voice rules). `TEAMS.md` → filter
   charters (one seat each; keep "Owns the blind spot / Seat it when / Do NOT seat it when"; delete
   default triads). `ROSTER.md` keeps all 43 minds, adds the per-filter top-3 ranking rule (ranked by fit
   to the topic, informed by `Best against` and the situation index). `SPAWNS.md` rewritten for one-mind
   spawns + round-0 menu mechanics; keep §7 inline protocol. `DOCTRINE.md` and `THIRD-SIDE.md` largely
   survive — update only where they reference teams/triads/caucus.
9. **Memory fallout (plan-only note):** `adviser-board-caucus-card-contract.md`'s mechanics become
   obsolete (its principles are now structural). Flag for compression/retire via the sanctioned memory
   flow (`/smh-memory-audit` / `/cicd-update-sprint-memory` routing) — **do NOT edit memory files in this
   task.** ⚠️ AUDIT FINDING F7: a second memory rides the same close-out flag —
   [`adviser-board-roster-is-product-shaped.md`](../../_memory/adviser-board-roster-is-product-shaped.md)
   (its "seat 2–3 lenses" guidance goes obsolete under filters, though its core — charters are
   product-shaped; borrowed-analogy failure — survives). Both flags are close-out memory-flow work, not
   implementation scope; the no-direct-edits stance is unchanged.
10. **Spawn/round mechanics source:** `bmad-party-mode` (see §2). No memlog, no party-memory.

## 4. File-by-file change list

All paths relative to repo root. The command body is the single source of truth; the folder files are
its contracts.

### 4.1 `.agents/commands/smh-adviser-board.md` — section by section

| Section (current) | Change |
| --- | --- |
| Frontmatter `description` | Rewrite: filters not teams/rooms; one mind per filter; four visible rounds; no stage rooms; drop "THREE minds per room", "3–5 cycles", "one ~250-word card", "Stages into Execution Reality and Sales". Keep the third-side framing, the 43-mind board, the trigger phrases. Watch the Antigravity menu budget if a workflow mirror description is derived from it (SCC-331 cut it to 121 chars against a 135-char budget). |
| Intro + "The folder" table | Update reader column: `TEAMS.md` → filter charters (read at cast time); `CARD.md` → statement contract (orchestrator + every filter spawn); `SPAWNS.md` → every spawn; `minds/<slug>.md` → **the filter's own subagent** reads exactly its one mind's card. Update the "Seat three minds and exactly three cards open" affordability line → one mind seated = one card opened. |
| Arguments | Unchanged (`$ARGUMENTS`, `--project`, `--solo`/`--inline`, `--model`). |
| "Running without subagents — inline mode" | Shrink: the expensive degradation (one context simulating 3-mind teams × 5 cycles) is gone. Inline now means: the orchestrator voices each filter's mind itself, in sequence, keeping R1 statements independent (write all R1 takes before any is revised — the one invariant that survives). Keep the capability test, the one-line announcement, and "balcony never cuts". Delete the floors-to-file rule (no floors exist). |
| "The chair" | Unchanged (4 rules). |
| Step 0 — Convene | Unchanged. |
| Step 1 — Recon | Unchanged (2 parallel recon spawns, GROUND BRIEF ≤500 words, mandatory combined `UNVERIFIED:` line). |
| Step 2 — Cast, and stop | **Rewritten as Round 0 — the cast menu.** Keep the scale rule (distinct failure surfaces table) and the "write the negative" gate (one line per filter, cut lines included). DELETE: the single-room cast block, "Staffing a room" (two-axis triad rule), stage-room cast-at-Step-7 carve-out. ADD: per seated filter, the TOP 3 mind menu from `ROSTER.md` — one line each on the angle that mind would take on THIS topic; operator picks one per filter or says "your pick"; "gavel" starts the rounds. Stage filters (Execution Reality, Sales) appear in the same gate as ordinary filters. |
| Step 3 — The Read | **DELETED** (absorbed into R1). |
| Step 4 — Debate | **Replaced by Board rounds R1–R4** (see §3.4). One spawn per filter per round, all spawns in one message, each carrying ground brief · doctrine · third-side stance · running summary (≤400 words) · every other filter's latest statement. Keep the file-read cap (≤3 files; Execution Reality ≤6) and "what cannot be settled becomes a question, never an invention". |
| Step 5 — Read it to him | Keep the narrative-first obligation (3–5 sentences prose). Then: each filter's statement verbatim (~250-word ceiling per statement), `⚖ {sharpest cross-filter collision, named minds}`, deduped COULDN'T SETTLE capped at two, stop. No menu. |
| Step 6 — Traffic | Collapse the 12-row table to six moves: react to another filter · swap the mind in a seat (top-3 menu, lead with what is lost) · unpack (now: quote the filter's prior round statement verbatim — no floor files) · just-Feynman (unchanged, §6 spawn) · new angle: X (recast) · close the board. Delete: collide/push-back/seat-on/expand rows (subsumed by "react"), stage-change row. |
| Step 7 — Stage change | **DELETED entirely**, including the stage gate. |
| Step 8 — Close | Unchanged (narrative ~400 words in chat; brief to `_artifacts/board_sessions/YYYY-MM-DD-<topic-slug>.md`; INDEX.md row; link). Update the brief template's header line: "Lenses seated" → filters + their minds; "Stages run" → delete; "Findings" → the surviving statement per filter, credited. |
| Standing rules | "You are the orchestrator, never a voice" — keep. No memory — keep. "Board sees what the chair sees" — simplify: statements circulate into every later spawn; there are no floors; nothing else circulates. Context discipline — keep (running summary ≤400 words, refreshed every 2–3 rounds; spawn payload list updated to statements-not-cards). Endorsement ledger — keep verbatim. Failure playbook — adapt: card-contract respawn → statement-contract respawn; "near-identical safe verdicts" → respawn one filter against the strongest opposing statement; keep the circling rule. |
| Session brief template | Update per Step 8 above; keep all other sections (third side, endorsements, still open, roads not taken, coined questions, build seed). |
| Exit | Unchanged. |

### 4.2 `.agents/commands/adviser-board/TEAMS.md` → filter charters

- Retitle: "Filter Charters". Seven filters, no debate/stage distinction — Execution Reality and Sales
  are ordinary filters seatable at the cast gate.
- Per filter keep: **Owns the blind spot / Seat it when / Do NOT seat it when / Pool**.
- **Delete:** every "Default triad" block; the two-axis staffing preamble ("three minds on two
  independent axes"); the "three minds per team is that discipline made structural" paragraph; the
  stage-room convene-after-agreement clauses (Execution Reality's "convened after the debate agrees",
  Sales' "seated from round one" special case — both become plain seat-it-when lines).
- Add: one line stating each charter is a **filter** — the lens the problem is viewed through — and the
  seated mind is who looks through it; casting picks ONE mind per filter via the ROSTER top-3 rule.

### 4.3 `.agents/commands/adviser-board/ROSTER.md`

- Keep all 43 minds, both tables, the situation index, cross-lens regulars.
- Remove stage-room annotations `*(stage room)*` from the Execution Reality and Sales section headers.
- Replace the two-axis casting guidance with the **per-filter top-3 ranking rule**: for each seated
  filter, rank 3 minds by fit to THIS topic, informed by `Best against` and the situation index; the
  orchestrator writes one line per candidate on the angle that mind would take on this topic. All 43
  eligible; the menu is a shortlist, not a bench.
- Update the "read by the team subagent" line → read by the filter's own subagent (one card).

### 4.4 `.agents/commands/adviser-board/CARD.md` → STATEMENT contract

- Retitle: "The Statement — contract". One statement per filter per round.
- **Shape:** `{icon} {FILTER} — {Mind}` header; 4–6 sentences of prose **in the mind's own voice** (the
  mind itself is the voice — no presenting speaker, no team voice); slots: `THE THIRD SIDE` (optional,
  outranks THE MOVE), `THE MOVE`, `COULDN'T SETTLE` (≤2), `ASSUMED`, `SPLIT`.
- **~250-word ceiling per statement** (keep the hard-ceiling pattern; set hard ceiling 320 as today).
- **Delete:** the caucus clause ("must be true of the floor" — no floor exists); the presenting-voice
  rules ("the round's speaker", "the unattributed team"); the triad-shaped examples.
- **Keep:** third-side-outranks-move + do-not-manufacture; credit-to-originator (now trivially the mind
  itself, but keep the decoration-attribution rule); kills in the killer's method; COULDN'T SETTLE/SPLIT
  not-both-empty + the one corrective respawn; bounded questions → ASSUMED; questions in the mind's own
  method; no process talk; rendering rules (narrative first, verbatim, ⚖ line, capped questions, stop).

### 4.5 `.agents/commands/adviser-board/SPAWNS.md`

- **Rewrite §3–§5** for one-mind spawns + round-0 menu mechanics:
  - §1/§2 Recon A/B — unchanged.
  - New: **Round-0 menu** is orchestrator work off `ROSTER.md` (no spawn) — document the top-3 line
    format here.
  - §3 (old Read) → **R1 READ spawn**: one mind, its one persona card, ground brief, doctrine,
    third-side stance, chair's topic; returns its independent take per the statement contract. No other
    filters' statements (independence is structural now, not instructed).
  - §4 (old Debate) → **R2/R3/R4 spawn template**: one mind + running summary (≤400 words) + every other
    filter's latest statement; the round's job stated in one block (ATTACK: name whose statement you
    attack / BALCONY: the reframe discipline, 3A trap / SETTLE: concede, entrench, or adopt; splits
    named). Keep the ≤3-file read cap (Execution Reality ≤6), the never-write rule, and the
    floor/card split becomes statement-only (no floor section in the return).
  - §5 (old stage room) → folded into the main template as a scope clause used when Execution Reality or
    Sales is seated as an ordinary filter (keep the six-file read cap for Execution Reality).
  - §6 just-Feynman — unchanged.
  - §7 inline — shrink per §3.7: no floors-to-file, no last-seated-team rule as written (adapt: R1 takes
    written before any revision), keep capability test, announcement, "balcony never cuts", recon
    one-pass rule.
  - Model selection — update: R1 may take a fast model; R2–R4 take the session default; `--model` pins.

### 4.6 `.agents/commands/adviser-board/DOCTRINE.md`

- Survives nearly intact. Update only: "no team wastes a round" → "no filter wastes a round"; "in the
  card" → "in the statement"; "any team that believes" → "any filter/mind that believes".

### 4.7 `.agents/commands/adviser-board/THIRD-SIDE.md`

- Survives intact in substance. Update only team/triad references: the intro line ("the lenses, the
  triads, the cycles, the card") → "the filters, the rounds, the statements"; § "Why three minds" —
  rewrite: the third side is no longer a third mind in a room, it is the third position across the
  board's filters (the balcony round is where it is sought); delete the two-axis casting paragraph.

### 4.8 `minds/` — inventory only

43 persona cards verified present (aurelius … wegener). **No changes required** — cards are per-mind and
the new architecture reads exactly one per spawn. (If any card internally references triads/teams, fix
only if trivially worded; otherwise leave — cards are characters, not process docs.)

### 4.9 What gets deleted (summary)

- Command body: Step 3 (The Read), Step 7 (Stage change + stage gate), 6 of 12 traffic moves, the
  single-room cast block, the staffing-a-room two-axis rule, the floors rule in standing rules.
- `TEAMS.md`: all default triads, stage-room special status.
- `CARD.md`: caucus clause, presenting-voice rules.
- `SPAWNS.md`: §3 Read template, §4 five-cycle template, §5 stage-room template, §7 floor-file protocol.

### 4.10 Audit-remediation additions (⚠️ AUDIT FINDINGS F3–F5 — same lane, same commit)

- ⚠️ AUDIT FINDING F3 — `docs/_scc_sops_prds/workflows_testing_SOP.md` — **modify**: update the four
  board-usage passages (≈ :101 quick-reference row, :318 mermaid, :1603 cast-gate section, :4161
  "three minds each") to the filter model, plus a `workflows_testing_SOP_changelog.md` convention row.
  Unconditional — see §6.
- ⚠️ AUDIT FINDING F4 — `docs/_scc_sops_prds/smh-adviser-board-REFERENCE.md` — **modify**: the board's
  own pointer doc teaches the retired model ("default triad" :9, "the ~250-word card contract" :13,
  "the six spawn templates" :14, "build a triad on two independent axes" :26); rewrite to the filter
  model (table-row updates + history note; `docs/_scc_sops_prds/INDEX.md:108` describes this pointer
  and rides with the fix).
- ⚠️ AUDIT FINDING F5 — `.agents/commands/INDEX.md` — **modify row**: the `smh-adviser-board` row
  carries the full retired model ("5 debate lenses + 2 stage rooms … casts 3 minds per lens … one
  ~250-word card"); rewrite to filters / one mind per filter / four rounds.

## 5. Door sync (SCC-331 pitfall — do not skip)

The command body is the brain; every door is generated. After editing `.agents/commands/smh-adviser-board.md`:

1. Run `/smh-sync-agents` to regenerate the **`.claude/skills/` launcher** (Claude + Codex entry point)
   and the **`.opencode/commands/` mirror**; verify byte-identical against the brain.
2. Check the **Antigravity workflow mirror** (`.agents/workflows/`) — its description has a ~135-char
   menu budget; cut the description to fit rather than exempting (hand-owned means fix it by hand).
   ⚠️ AUDIT FINDING F6: the launcher is hand-authored and prune-protected
   ([`sync-agents.ps1`](.agents/scripts/sync-agents.ps1) `$excluded` list) — sync will never fix its
   **body**, which carries "team charters … card contract" wording. Update the body by hand in the same
   pass, and extend the §8 grep gate to cover `.agents/workflows/smh-adviser-board.md`.
3. ⛔ No hand-authored `smh-adviser-board` skill may exist anywhere — the generator owns the door
   (SCC-331 deleted a stale hand-authored `SKILL.md`; do not recreate one).
4. `workflow_lint.py --toolkit-only` must pass (naming law: hyphens, no `sudo-` references).

## 6. Out of scope

- Memory store edits (the caucus-card-contract memory is flagged only; routing happens through the
  sanctioned flows after this lands).
- `bmad-party-mode` itself — read as inspiration, never modified.
- Persona cards in `minds/` beyond trivial wording, if anything at all.
- Any other command, rule, or SOP file — except the SOP-currency set below, which is **unconditional**
  (⚠️ AUDIT FINDING F3): `docs/_scc_sops_prds/workflows_testing_SOP.md` describes the board's usage in
  at least four passages (≈ lines 101, 318, 1603, 4161) and MUST be updated **in the same commit**,
  including a `workflows_testing_SOP_changelog.md` row per house convention (SCC-333/SCC-334 precedent)
  — or the armed `sop_currency.py` gate rejects the commit. `[sop-ok]` is not available here: the usage
  genuinely changes.
- Jira ticket minting happens at implementation start (§10), not in this plan.

## 7. Risks & mitigations

| Risk | Mitigation |
| --- | --- |
| **A lone mind has no internal devil's advocate** — the old triad guaranteed an in-room collision. | Collision moves across the board where the chair can see it: R2 ATTACK forces each filter to name and attack the weakest opposing statement; the adapted failure playbook respawns a filter against the strongest opposing statement when verdicts converge safely. The operator accepted this trade explicitly. |
| **Menu fatigue at Round 0** — one top-3 menu per filter could balloon. | Top-3, not top-5 (operator chose 3); one line per candidate; "your pick" is always available; the scale rule still caps filter count before any menu is shown. |
| **Stale generated doors** (SCC-331's actual failure — CI caught it). | §5 door sync is a mandatory step, verified byte-identical before the lane's gates run. |
| **Inline mode drift** — degradation rules shrinking could silently drop invariants. | Keep the two named invariants explicitly: R1 independence (write-before-revise) and "balcony never cuts". |
| **Vocabulary residue** — "team/room/triad/caucus/floor" surviving in the folder. | Grep gate in §8. |

## 8. Verification

Verification executes the `## Acceptance` rows: check 1 → rows (a)+(b), check 2 → row (c), checks 3+5 →
row (e), check 4 → row (d).

1. **Dry-run session** on a real topic (operator-chosen): confirm Round 0 menu renders top-3 per filter
   with one-line angles; four rounds run with parallel spawns; render shows verbatim statements + ⚖ line
   - ≤2 questions + stop; traffic table accepts the six moves; close writes the brief + INDEX row.
2. **Grep gates for retired vocabulary** across `.agents/commands/smh-adviser-board.md`,
   `.agents/commands/adviser-board/` (excluding `minds/`), and — per ⚠️ AUDIT FINDING F6 —
   `.agents/workflows/smh-adviser-board.md`: `triad`, `caucus`, `stage room`, `stage change`,
   `default triad`, `three minds`, `team` (case-insensitive) — each hit must be a justified exception
   or a miss. ⚠️ `floor` is scoped precisely: grep it only over those three surfaces and adjudicate
   hits manually — "floor" has legitimate non-board uses; the retired sense is specifically floor-as-
   caucus-log / floors-to-file. Note: root-level grep is fine here — this is home-base scope, not
   under `Projects/`.
3. **`workflow_lint.py --toolkit-only`** passes (naming law, toolkit-only).
4. **Door parity:** `.claude/skills/smh-adviser-board/SKILL.md` and
   `.opencode/commands/smh-adviser-board.md` byte-identical to the brain; Antigravity mirror description
   within budget.
5. **Enforcement suite** (`run_all`) green on the lane.

## 9. Open questions

None. The design is settled with the operator; every decision above traces to §3.

## 10. Ticket note

Mint the Jira ticket at **implementation start** (this plan precedes it), via the authenticated `acli`
CLI per [`.agents/rules/jira.md`](.agents/rules/jira.md). Suggested summary: "Rework /smh-adviser-board
to one-filter-one-mind board rounds". The lane follows the standing Task model: `chore/<KEY>-adviser-board-filter-rework`
worktree off `main`, explicit-path commits, gates, `/smh-close-task-merge-tree` at close-out — and the
close-out runs **in the same session as the landing** (SCC-331's close-out ran 15 hours late; do not
repeat that).

## Declared Change Set

Every file the implementation will create / modify / delete. Change types: MODIFY · REWRITE ·
REGENERATE · UNCHANGED. Paths relative to repo root. (Audit finding F1 — this block is the
drift-check consumer's contract; absence is a finding, presence is the baseline.)

| # | Path | Change | Notes |
| --- | --- | --- | --- |
| 1 | `.agents/commands/smh-adviser-board.md` | MODIFY | §4.1 section-by-section |
| 2 | `.agents/commands/adviser-board/TEAMS.md` | MODIFY | → filter charters (§4.2) |
| 3 | `.agents/commands/adviser-board/ROSTER.md` | MODIFY | per-filter top-3 ranking rule (§4.3) |
| 4 | `.agents/commands/adviser-board/CARD.md` | MODIFY | → statement contract (§4.4) |
| 5 | `.agents/commands/adviser-board/SPAWNS.md` | REWRITE | §3–§5 one-mind spawns + round-0 menu (§4.5) |
| 6 | `.agents/commands/adviser-board/DOCTRINE.md` | MODIFY | vocabulary only (§4.6) |
| 7 | `.agents/commands/adviser-board/THIRD-SIDE.md` | MODIFY | team/triad references only (§4.7) |
| 8 | `.agents/commands/adviser-board/minds/` | UNCHANGED | all 43 persona cards — stated explicitly; no edits planned (§4.8) |
| 9 | `.claude/skills/smh-adviser-board/` | REGENERATE | via `/smh-sync-agents` (§5.1) |
| 10 | `.opencode/commands/smh-adviser-board.md` | REGENERATE | via `/smh-sync-agents` (§5.1) |
| 11 | `.agents/workflows/smh-adviser-board.md` | MODIFY | hand-authored AG launcher — description budget + body (§5.2; ⚠️ F6) |
| 12 | `docs/_scc_sops_prds/workflows_testing_SOP.md` | MODIFY | four board-usage passages (⚠️ F3) |
| 13 | `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` | MODIFY | one convention row (⚠️ F3) |
| 14 | `docs/_scc_sops_prds/smh-adviser-board-REFERENCE.md` | MODIFY | pointer doc → filter model (⚠️ F4) |
| 15 | `.agents/commands/INDEX.md` | MODIFY | `smh-adviser-board` row (⚠️ F5) |

Machine rows — the same set in the grammar `declared_change_set.py` parses (`- OP \`path\` — why → rows`);
the table above is the human view, these are the drift-check consumer's entries. Generated files the
sync and map runs actually touch are declared explicitly rather than left to read as drift:

- EDIT `.agents/commands/smh-adviser-board.md` — §4.1 section-by-section → c, d
- EDIT `.agents/commands/adviser-board/TEAMS.md` — filter charters (§4.2) → c
- EDIT `.agents/commands/adviser-board/ROSTER.md` — per-filter top-3 ranking rule (§4.3) → c
- EDIT `.agents/commands/adviser-board/CARD.md` — statement contract (§4.4) → c
- EDIT `.agents/commands/adviser-board/SPAWNS.md` — one-mind spawns + round-0 menu (§4.5) → c
- EDIT `.agents/commands/adviser-board/DOCTRINE.md` — vocabulary only (§4.6) → c
- EDIT `.agents/commands/adviser-board/THIRD-SIDE.md` — team/triad references only (§4.7) → c
- EDIT `.agents/workflows/smh-adviser-board.md` — hand-authored AG launcher, description budget + body (§5.2, ⚠️ F6) → c, d
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` — four board-usage passages (⚠️ F3) → e
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` — one convention row (⚠️ F3) → e
- EDIT `docs/_scc_sops_prds/smh-adviser-board-REFERENCE.md` — pointer doc → filter model (⚠️ F4) → c
- EDIT `docs/_scc_sops_prds/INDEX.md` — REFERENCE-pointer row rides with F4's fix (⚠️ F4) → c
- EDIT `.agents/commands/INDEX.md` — `smh-adviser-board` row (⚠️ F5) → c
- EDIT (generated) `.claude/skills/smh-adviser-board/SKILL.md` — via `/smh-sync-agents` (§5.1) → d
- EDIT (generated) `.opencode/commands/smh-adviser-board.md` — via `/smh-sync-agents` (§5.1) → d
- EDIT (generated) `.agents/skills/smh-adviser-board/SKILL.md` — sync master launcher, tree-copied to `.claude/` (§5.1) → d
- EDIT (generated) `.agents/.sync-manifest.json` — written by `sync-agents.ps1` (§5.1) → d
- EDIT (generated) `docs/doc-graph.json` — regenerated doc graph (§8) → e
- EDIT (generated) `docs/doc-graph.md` — regenerated doc graph (§8) → e

Session-brief output path unchanged: `_artifacts/board_sessions/YYYY-MM-DD-<topic-slug>.md` (§3.7).
Out-of-implementation-scope (close-out work): memory-flow flags for
`adviser-board-caucus-card-contract.md` and `adviser-board-roster-is-product-shaped.md` (⚠️ F7) —
routed via the sanctioned flows (`/smh-memory-audit` / `/cicd-update-sprint-memory`), never edited in
this lane. No files created or deleted by this change set; `minds/` is untouched (§4.8).

## 12. Acceptance

Observable, checkable rows the lane is audited against (audit finding F2 — Scope Ledger precondition).

- **(a) Round-0 cast menu (dry run):** a dry-run `/smh-adviser-board <topic>` session renders a
  Round-0 cast menu showing the top-3 mind picks per seated filter (one line each on the angle that
  mind would take on THIS topic) and cut lines for refused filters; the operator's picks seat exactly
  one mind per filter.
- **(b) Four visible rounds (full session):** a full session renders R1 READ / R2 ATTACK / R3 BALCONY /
  R4 SETTLE with one verbatim statement per filter (~250-word ceiling) and no hidden caucus spawns.
- **(c) Vocabulary grep gate:** grep over `.agents/commands/smh-adviser-board.md`,
  `.agents/commands/adviser-board/` (excluding `minds/`) and `.agents/workflows/smh-adviser-board.md`
  returns zero unjustified hits for `triad`, `caucus`, `stage room`, `stage change`, `default triad`,
  `three minds`, `team`; `floor` adjudicated manually per §8.2's precise scoping.
- **(d) Door parity:** `/smh-sync-agents` leaves `.claude/skills/smh-adviser-board/` and
  `.opencode/commands/smh-adviser-board.md` byte-consistent with the command body, and the Antigravity
  launcher description within the ~135-char menu budget.
- **(e) Enforcement suite:** `run_all` green on the lane, including `workflow_lint.py --toolkit-only`
  and `sop_currency.py`.

## 13. Self-Audit

PRE-WORK self-audit (LEDGER+BLAST — all three lenses) ran 2026-08-28 against this plan; verdict
**NO-GO** on two mechanical grounds (F1 missing Declared Change Set, F2 no acceptance rows) with
F3–F7 as GO-riding findings. The amendments above — `## Declared Change Set` (F1), `## Acceptance`
(F2), inline `⚠️ AUDIT FINDING` markers (F3–F7), unconditional SOP currency, extended grep gate —
were applied per the audit's stated path to GO; the audit itself stated no re-audit is needed once
they land, so its verdict is flipped to **GO**. Full record:
[`self-audit.md`](self-audit.md) in this folder.
