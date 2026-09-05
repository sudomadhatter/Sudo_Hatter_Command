# Implementation Plan — Rework `/smh-adviser-board`

**Status:** PROPOSED — awaiting operator review, nothing edited yet
**Date:** 2026-08-26 · **Scope:** lobby toolkit (`.agents/commands/`) + one docs pointer + SOP currency
**Baseline evidence:** one session in `_artifacts/board_sessions/` since the command shipped
(2026-07-21). The operator states plainly he does not use it.

---

## 1. Why now — the command is unusable by arithmetic, not by taste

The current command is 690 lines and fails for four structural reasons, not stylistic ones.

**It buries the chair.** Every round convenes all five teams regardless of relevance, each team is four
or five members, and each owes a 500–2,000 word presentation *plus* a Team Card. That is 2,500–10,000
words of reading before the operator can say one sentence back. This violates the house floor rule
(`operator-profile`, obligation 5 — never make Daniel the compiler) inside a command that was written
to serve him.

**It is blind.** The team spawn template ends with `Do NOT use tools.` The board has never once read the
project it advises on. Every finding it has ever produced was reasoned from a topic sentence.

**Its debates are crowded.** Four-to-five minds per caucus means two sharp opposed minds argue and three
file courtesy BUILDs. The card contract then has to police "composite ideas" and "decoration
attribution" — enforcement machinery that exists because the room is too big.

**Nothing selects.** There is no orchestrator deciding which lenses are load-bearing for a topic. All
five convene always; the PASS card is the only relief valve and it is weakly enforced.

The rework replaces the ceremony with an orchestrator, cuts teams to three minds, caps each team at one
~250-word card per round, grounds the board in the actual project before anyone speaks, and moves the
personas out of the command into a lazily-loaded folder.

---

## 2. Settled design

Decided across the 2026-08-26 brainstorm. Each line is a decision, not an option.

| # | Decision |
|---|---|
| D1 | An **orchestrator** casts the table: which lenses are load-bearing, and which three minds staff each. |
| D2 | **Three minds per team**, not two — two produce a line (A, B, midpoint); three produce a space, with shifting coalitions and a third position that isn't the average. |
| D3 | Debates run **3–5 cycles with a job per cycle**, not a loose exchange cap. Every mind speaks once per cycle. |
| D4 | **One card per team per round, ~250 words** — short prose opening in the speaker's voice, then slots. |
| D5 | **Recon runs first.** Two agents read the named project and produce a ≤500-word Ground Brief carried into every later spawn. |
| D6 | **The Read round** — each team returns one line proving it understood the task, or the one question blocking it. Surfaces to the chair **only** when reads diverge or a question lands. Silent otherwise. |
| D7 | **At most two questions reach the chair per round.** Unasked questions become explicitly stated assumptions printed in that team's card. |
| D8 | **The cast gate** — ground brief and cast are shown together as one stop, and the board waits for the gavel. |
| D9 | **The cast persists** for the topic. Only the operator swaps a mind. |
| D10 | **`swap <mind>`** returns a substitute list drawn from every unseated mind, led by a line naming what is lost by the removal. |
| D11 | **No bench.** The roster is flat; seated vs. observing is session state, not a tier. |
| D12 | Each mind has a **primary lens** as a default, not a fence — the orchestrator may staff across lenses and says so when it does. |
| D13 | **Cards circulate, floors never do.** The board sees exactly what the chair sees and nothing more. |
| D14 | **Execution Reality and Sales are stages, not seats** — rooms convened after the debate agrees, cast fresh by topic with the same gate and swap move. |
| D15 | A topic that starts as a sales question **skips straight to Sales**, usually beside Human Needs. |
| D16 | The orchestrator **asks** which stage to move to. It never advances on its own. |
| D17 | **Operator Doctrine** ships as standing context in every spawn — teams design within it, and are explicitly licensed to attack it when they think the doctrine is what is failing. |
| D18 | **No memory.** Every session starts fresh. No cross-session state. |
| D19 | The four-phase arc, tone dial, six-move table, question bank as mandatory checklist, three-part caucus/presentation/card split, and every render dial are **deleted**. |
| D20 | Close-out produces a **narrative record** plus a final **build seed** paragraph shaped to paste into `/smh-plan-task`. |
| D21 | **This is a third-side board** — its purpose is to refuse the binary frame and find the position nobody in the argument occupies. `THIRD-SIDE.md` is the house discipline and every other file serves it. **Three minds per team is that discipline made structural**, which is the real reason for D2. *(Added 2026-08-26; amends D19, which wrongly deleted the question bank as a checklist.)* |
| D22 | **Cycle 3 is THE BALCONY** — the pivot of every debate. The room stops arguing positions and asks whether the disagreement is real or a frame artifact. A reframe minted there **outranks** the answer to the original question. |
| D23 | The instrument bank **returns**, but owned rather than ticked: each mind's instruments live on its own card under `Reaches for`, with `THIRD-SIDE.md` holding the shared bank and the coining rule. No card is ever required to have used one. |

---

## 3. The board

Five debate lenses, two stage rooms, 43 minds. Nobody is on a bench — whoever is not seated is
observing and callable. Pools, not lineups: the orchestrator seats three per team per topic.

| Lens | Owns the blind spot | Pool |
|---|---|---|
| 🔬 **First Principles** | Borrowed analogy — no best practice exists for what doesn't exist yet | Kepler · Feynman · Tesla · Turing · Curie · Friston · Stevens |
| 🩺 **Ground Truth** | The Semmelweis reflex — rejecting evidence that insults our identity | Semmelweis · Snow · Wegener · Nightingale · Darwin · Haeckel |
| 🌊 **Ruin & Ripple** | Linear thinking — unpriced tail risk, invisible second-order effects | Mandelbrot · Taleb · Munger · Bastiat · Hutton · Braudel |
| 🧬 **Unconventional Leverage** | Assuming capability must arrive through standard channels | Margulis · Nakamoto · Ravikant · Fuller |
| 🎯 **Human Needs** | Our ego's story about people — needs, not wants | Drucker · Schwartz · Rubin · Diogenes · Houellebecq · Ury · the Identity Engineer |
| 🔧 **Execution Reality** *(stage)* | The correct plan that never ships | Kelly Johnson · Ohno · Aurelius · Boyd · Eisenhower · Brunelleschi · Deming · Hopper · Fuller |
| 📣 **Sales** *(stage)* | The thing that never reaches anyone | Hormozi · Godin · Vaynerchuk · Brunson · Hopkins · Schwartz · Drucker · Rubin · Nightingale |

**Eight minds are new** and have no signature written anywhere: Kelly Johnson, Taiichi Ohno, John Boyd,
Dwight Eisenhower, Filippo Brunelleschi, W. Edwards Deming, Grace Hopper, Claude Hopkins.

---

## 4. File layout

```
.agents/commands/smh-adviser-board.md          REWRITE — 690 → ~260 lines, protocol only
.agents/commands/adviser-board/                NEW folder
    ROSTER.md      43 one-line rows. The ONLY roster file the orchestrator loads.
    TEAMS.md       7 charters: blind spot, when to seat, when NOT to seat, pool, default triad
    THIRD-SIDE.md  the house discipline — the stance, the balcony, the 3A trap, the instrument bank
    DOCTRINE.md    Operator Doctrine — standing context in every spawn
    CARD.md        the ~250-word card contract
    SPAWNS.md      the six spawn templates
    minds/<slug>.md   43 persona cards — read ONLY by the subagent that seats them
docs/_scc_sops_prds/smh-adviser-board-REFERENCE.md   → becomes a pointer to the folder
docs/_scc_sops_prds/workflows_testing_SOP.md         → SOP currency gate (armed)
_artifacts/board_sessions/                        → unchanged; briefs still land here
```

**Why a subfolder under `.agents/commands/` is safe.** Verified 2026-08-26:
`sync-agents.ps1:319` enumerates with `Get-ChildItem … -Filter *.md -File` and `workflow_lint.py:560`
globs `.agents/commands/*.md` — both non-recursive. A subdirectory is invisible to each, so no bogus
launcher is minted and no lint fires on the persona cards. The folder sits beside the brain that reads
it, and is reached by relative path at runtime rather than being synced as a skill.

⚠ **`sop_currency.py` IS recursive** — corrected 2026-08-26 when it rejected the Phase A commit. It
reads every `.md` under `.agents/commands/`, subfolders included, as command-menu surface. So every
commit in this lane either stages `docs/_scc_sops_prds/workflows_testing_SOP.md` or logs `[sop-ok]`.
Phases A and B are legitimately `[sop-ok]` — the folder is inert until the command reads it — and the
real SOP edit lands with the Phase C rewrite, which is when usage actually changes.

**Why lazy loading works.** The orchestrator reads `ROSTER.md` and `TEAMS.md` only — never a persona
card. **The team subagent reads its own three cards** from `minds/`. Seat Feynman, Tesla and Turing and
exactly three files open, opened by the agent that needs them. The orchestrator's context holds 43
one-liners for the whole session.

---

## 5. The persona card contract

One file per mind at `.agents/commands/adviser-board/minds/<slug>.md`.

```markdown
---
name: Richard Feynman
slug: feynman
lens: first-principles
icon: 🔬
one_line: mechanism — walk me through how it actually works
---

# Richard Feynman — "What I cannot create, I do not understand."

## Anchor
2–4 sentences. The defining historical episode, concrete and specific.

## The move
3–5 sentences. The transferable thinking pattern, stated so it ports to a problem
they never saw.

## Voice
2–4 sentences. Cadence, register, tells, what they refuse to say.

## At the table
3–5 sentences. The specific interrogation they run on a live proposal.

## Reaches for
2–4 sentences. This mind's own third-side instruments, in its own phrasing, plus how
it tends to escape a binary at the balcony. Never a checklist — see D23.

## What they attack
1–3 sentences. The failure mode they exist to catch.

## What they concede to
1–3 sentences. What actually changes their mind.

## Collides with
2–4 lines, each naming a mind and the axis.

## Asks the chair
1–2 sentences. The kind of question this mind puts to the operator, in its own method.
```

Three sections are new and each earns its place.

**`Collides with`** is what the orchestrator reads to build a triad: pick the natural owner of the
topic, then the mind that collides with them, then a third that collides with *both* on a different
axis. Two independent axes, so the room is a space rather than a duel. Without this field the
orchestrator is guessing and will seat three minds who agree.

**`What they concede to`** is what makes cycle 3 real. A mind with no stated concession condition
either never moves (theatre) or moves arbitrarily (also theatre).

**`Asks the chair`** feeds the `COULDN'T SETTLE` slot and the Read round, so questions arrive in the
mind's own method — Feynman asks for the mechanism, Drucker asks what the user is hiring this to do,
Diogenes asks you to show him.

**Quality bar:** if two cards' `Voice` sections could be swapped without either reading wrong, both are
failures. Same test for `Collides with`.

---

## 6. ROSTER.md contract

The only roster file loaded at cast time. One row per mind, 43 rows.

| Column | Content |
|---|---|
| `slug` | filename stem in `minds/` |
| `Mind` | display name |
| `Primary lens` | default team; not a fence (D12) |
| `Sees` | ≤10 words — the thing this mind notices that others don't |
| `Best against` | ≤10 words — the failure mode they're the sharpest tool for |

`Best against` is what makes the cast decision real rather than thematic, and it is what the substitute
list under `swap` is ranked by.

---

## 7. TEAMS.md contract

Per team: icon · name · blind spot owned · **when to seat** · **when NOT to seat** · pool · default
triad. The negative clause is load-bearing — "when NOT to seat" is the direct fix for the old command's
all-five-every-round default, and it gives the orchestrator explicit licence to leave a lens observing.

---

## 8. Operator Doctrine (DOCTRINE.md)

Standing context injected into every spawn beside the Ground Brief. First draft:

> **You build Hormozi-style.** Value stacked until the price is irrelevant — dream outcome × perceived
> likelihood ÷ time × effort. One narrow problem solved completely, which reveals the next. Prove rather
> than claim: give the secrets away and let the volume of value convince. This is how the operator
> builds *any* product, not merely how he markets one.
>
> **Solo operator with agent lanes.** Real capacity is one calendar plus whatever runs in parallel
> unattended. Any plan that needs a team is a different plan.
>
> **Frontier work.** There is no best practice to copy and usually nothing to buy. That is why this
> board exists.

**The rule attached matters as much as the content:** teams design *within* the doctrine but are
explicitly licensed to attack it when they believe the doctrine is the thing failing — and must say so
out loud rather than quietly routing around it. Without that clause the board cannot see the blind spot
closest to the operator.

---

## 9. The orchestration protocol

### Step 0 — Convene
Parse `$ARGUMENTS`: topic · `--project <name>` · `--solo` · `--model <m>`. Resolve `--project` to an
absolute path under `Projects/`. If the topic is project-bound and none is named, ask which — one
question, not a form. A genuinely abstract topic skips recon and the orchestrator says so.

### Step 1 — Recon (2 parallel subagents; skipped when no project)
Both receive the **absolute** project root and work inside it — never grep from the lobby.

- **Recon A — what it is:** `AGENTS.md`, `README.md`, `docs/`, `_artifacts/_memory/`, active-context,
  sprint status. Returns what the product is, who it is for, what stage it is at, what the operator has
  stated he wants.
- **Recon B — what is actually built:** directory and entry-point surface, test surface,
  `git log --oneline -30`, open tickets via `acli` where available. Returns what exists versus what is
  claimed, what is half-built, what has churned recently.

They merge into a **GROUND BRIEF ≤500 words** ending in a mandatory `UNVERIFIED:` line naming what
recon could not confirm. That line is not optional — a brief that hides its gaps produces a board that
is confidently wrong in unison, which is worse than the abstraction it replaces.

### Step 2 — Cast, and stop
Orchestrator reads `ROSTER.md` + `TEAMS.md` against the brief. Seats **3–5 lenses** that are actually
load-bearing, three minds each, per the two-axis rule in §5.

Ground brief and cast render together as **one gate**, then wait:

```
🔬 First Principles   Feynman × Tesla × Turing
                      Feynman demands the mechanism; Tesla runs it to failure; Turing asks what
                      would even count as an answer. They split on whether it can be built at all.
🌊 Ruin & Ripple      Munger × Bastiat × Hutton
                      Munger inverts to find the death; Bastiat prices what it displaces; Hutton
                      asks what it's worth in ten years. They split on which cost is the real one.

Swap anyone, add a lens, or say "gavel".
```

### Step 3 — The Read (parallel, one cheap spawn per team)
**Runs on a fast model and does NOT load persona cards** — it reads the roster line, the ground brief
and the topic only. It is asking "what is this team being asked to do", which needs no deep persona.
This is what keeps the round nearly free.

Each team returns **one line**: its understanding of the task, or the single question blocking it.
Never both, never more.

- All reads agree, no questions → **silent.** Orchestrator prints the agreed read as one line above the
  findings and proceeds straight to debate. The chair is not interrupted.
- Reads diverge, or ≤2 questions → surfaced. One line from the chair settles it.
- More than 2 questions → orchestrator forwards the 2 that move the most advice. The rest become
  **explicitly stated assumptions** carried into those teams' debates and printed under `ASSUMED` (D7),
  so a wrong assumption is caught when the card is read rather than by pre-interrogation.

### Step 4 — Debate (parallel, one spawn per team)
Each spawn reads its three persona files, and carries the ground brief (plus chair corrections and Read
answers), the Operator Doctrine, the running summary, the topic, and **all teams' cards from the
previous round**. Floors never enter another team's spawn (D13).

Cycles, each with a job:

1. **Three independent reads.** Each mind states its position in its own block *before seeing the
   others'*. Divergence is structural, not requested.
2. **Each mind attacks the read it finds weakest,** naming whose.
3. **Each states what it now believes** having been attacked — concede or entrench, in its own method.
4. *Only if still open:* the mind furthest from the emerging consensus makes its strongest case.
5. *Only if needed:* converge, or name the split honestly and stop.

Carried from the old design because it works: **kills are performed in the killer's own method.** If
Munger cannot state the kill as an inversion, it did not happen at this table.

The team may read **at most three files** in the project to settle a dispute of fact, and never writes.
A dispute it cannot settle becomes a `COULDN'T SETTLE` line rather than an invention.

Output: `═══ FLOOR ═══`, the debate transcript, then `═══ CARD ═══`, the card.

### Step 5 — The card (~250 words)

```
{icon} {TEAM} — {A} × {B} × {C} · {one factual clause true of the floor: who flipped whom}

{4–6 sentences of prose in the speaker's voice — what the three of them found and why it matters.
Plain language; every coined term defined at first use. This is the part the chair actually reads.}

THE MOVE:         the concrete thing to do, specific enough to picture built — credited
WHY IT SURVIVED:  the attack it took from the other minds and held against
COULDN'T SETTLE:  the gap in the world the team needs the chair to fill (≤2 questions)
ASSUMED:          any assumption carried from an unasked question
SPLIT:            named minds still disagreeing + what would flip them — or an earned "none"
```

`COULDN'T SETTLE` and `SPLIT` do different jobs: one is a gap in the world, the other is the minds still
disagreeing. **They cannot both be empty.** A round in which three opposed minds settled everything and
needed nothing from the chair is a round in which they did not dig, and the orchestrator respawns it
once with that quoted back.

### Step 6 — Render, then silence
Every card verbatim, board order. Then exactly one line — `⚖ {sharpest cross-team collision, named
minds}` — then the deduped `COULDN'T SETTLE` questions, numbered, capped at two. Then stop. No menu, no
"what next?", no process talk, no suggesting other commands.

### Step 7 — Traffic (plain words, nothing to memorise)

| The chair says | What happens |
|---|---|
| a substantive reply or pushback | affected teams re-debate with his words seeded; unaffected teams may pass |
| `push back on ②` / `poke holes in ②` | that team re-debates against his objection |
| `collide ① with ④` | each receives the other's card and returns ≤3 lines of attack |
| `unpack ②` | the stored floor, verbatim, never summarised |
| `just Feynman` | one mind, full voice, no card |
| `swap Taleb` | substitute list from every unseated mind, led by what is lost; he picks; team re-debates from cycle 1 |
| `swap Taleb for Ury` | direct swap, same re-debate |
| `seat Hormozi on ②` | adds a fourth mind to that team for the round |
| `expand ②` | that team writes the long argument |
| `new angle: X` | orchestrator recasts |
| `take it to execution` / `take it to sales` | stage change |
| `close the board` | close-out |

### Step 8 — Stage change
When the table converges — no live splits, cards agreeing — the orchestrator **asks in one line**:
*"The table's agreed on X. Execution, sales, or both?"* It never advances on its own (D16). The stage
room is cast fresh from the roster by topic with the same gate and the same swap move, and receives all
debate cards, the ground brief, the doctrine, and the agreed direction. Debate teams do not dissolve;
their cards are the input and they remain callable.

A topic that opens as a sales question skips the debate stage entirely and seats Sales, usually beside
Human Needs (D15).

### Step 9 — Close
On `close the board` / `meeting closed` / any natural wrap-up:

1. **Narrative overview in chat, ~400 words** — what the session walked in with, how it got reframed,
   what the table found, what the chair endorsed in his own quoted words, what is still open. Prose, no
   slot labels.
2. **The brief** to `_artifacts/board_sessions/YYYY-MM-DD-<topic-slug>.md`, self-contained, ending in
   a **BUILD SEED**: one paragraph shaped to paste straight into `/smh-plan-task`.
3. Append the `INDEX.md` row. Hand back a clickable link. Then stop.

**Endorsement tracking** runs quietly all session: every idea the chair reacts to positively, quoted
verbatim, never inferred from a follow-up question (asking about something is not agreeing with it),
marked `↓ cooled` rather than deleted when he later moves off it. It is not rendered during the session;
it is what makes the close-out's "what you endorsed" honest instead of the board's own favourites.

### Context discipline
Running summary ≤400 words, refreshed every 2–3 rounds, built from cards and the chair's words only.
Floors never enter it. Every spawn carries: ground brief · doctrine · running summary · all teams'
latest cards.

---

## 10. Spawn templates (SPAWNS.md)

Six templates: **Recon A** · **Recon B** · **Read** (fast model, no persona load) · **Debate** ·
**Stage room** (debate template, stage charter and inputs swapped) · **Individual call-out** (one mind,
full voice, no cycles, no card).

`--solo` keeps its current meaning: no subagents, the orchestrator runs every room itself, writing each
floor to a session scratch file *before* the card, and announces solo mode on activation.

---

## 11. Build order

| Phase | Work | Notes |
|---|---|---|
| **A** | `TEAMS.md`, `ROSTER.md` (43 rows), `DOCTRINE.md`, `CARD.md`, `SPAWNS.md` | The skeleton. Nothing runs without it. |
| **B1** | 21 persona cards from existing full signatures | Reference doc already carries anchor/move/at-the-table; needs `Voice`, `Collides with`, `What they concede to`, `Asks the chair` authored. |
| **B2** | 4 marketing cards (Hormozi, Godin, Vaynerchuk, Brunson) | Partial signatures exist; light research. |
| **B3** | 10 thin cards (Darwin, Curie, Hutton, Braudel, Friston, Haeckel, Stevens, Aurelius, Ury, Identity Engineer) | One-liners only today; real research. |
| **B4** | 8 new cards (Kelly Johnson, Ohno, Boyd, Eisenhower, Brunelleschi, Deming, Hopper, Hopkins) | Full research from scratch. |
| **C** | Rewrite `smh-adviser-board.md` — 690 → ~260 lines | Protocol only; all roster content moves out. |
| **D** | REFERENCE doc → pointer · `/smh-sync-agents` · lint · link check · SOP currency | Landing. |
| **E** | **Live test** — convene on a real topic and see whether it is actually usable | The acceptance test is use, not green. |

**22 of 43 cards need real research.** That is the bulk of the work and the place quality will be won or
lost.

---

## 12. Gates and landing

- **SCC ticket required** — usage-surface change, not doc-only. Lightweight lane (ticket → branch →
  edit → PR), not the full story flow. Branch `chore/SCC-XXX-adviser-board-rework` off `main`.
- **SOP currency gate is ARMED** — `sop_currency.py` rejects any commit touching `.agents/commands/*.md`
  that leaves `docs/_scc_sops_prds/workflows_testing_SOP.md` behind. Stage the SOP in the same commit or
  log `[sop-ok]`.
- `python .agents/scripts/workflow_lint.py` — confirm the rewritten command passes; the subfolder is
  outside its non-recursive glob.
- `python .agents/scripts/check_links.py` — the command now carries ~50 relative links into
  `adviser-board/`; every one must resolve.
- `/smh-sync-agents` — regenerate the door for claude / opencode / codex. `platforms:` frontmatter stays
  `[claude, opencode, codex]`.
- Never push `main`; explicit paths only on every commit.

### Stale-path sweep — `board_sessions` moved to `_artifacts/` (2026-08-26)

Eight references still point at `_my_resources/board_sessions/`. Four are authored and need editing;
four are generated and are fixed by `/smh-sync-agents` once their sources are correct.

| File | Line | Authored or generated |
|---|---|---|
| `.agents/commands/smh-adviser-board.md` | 501, 688 | authored — resolved by the rewrite |
| `.agents/commands/INDEX.md` | 59 | **authored — needs a manual edit** (also still describes the deleted phase arc) |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | 4120 | **authored — needs a manual edit** (also still describes the deleted phase arc; the SOP edit is required by the currency gate anyway) |
| `.agents/skills/smh-adviser-board/SKILL.md` | 9 | generated |
| `.claude/skills/smh-adviser-board/SKILL.md` | 9 | generated |
| `.opencode/commands/smh-adviser-board.md` | 501, 688 | generated |

---

## 13. Risks

**43 bland cards.** The single largest failure mode: writing 43 personas that all sound like a
Wikipedia summary produces a board of one voice wearing 43 hats, which is exactly what the subagent
architecture exists to prevent. Mitigation is the `Voice` / `Collides with` swap test in §5, applied as
a real check before each card is accepted.

**A shallow ground brief poisons everything.** The board now *sounds* grounded, so a wrong brief is more
dangerous than the old abstraction. Mitigation is the mandatory `UNVERIFIED:` line and the chair seeing
the brief at the cast gate.

**Doctrine becomes a sacred cow.** Every team designing within the Hormozi frame means no team ever
questions it. Mitigation is the explicit attack licence in §8 — and it should be tested in phase E by
convening on a topic where the doctrine is arguably the problem.

**Three minds can still converge instantly.** Mitigation is cycle 1 being written independently before
any mind sees another, and cycle 4 existing specifically to give the furthest-out mind a forced turn.

**Token cost.** Roughly four team spawns per round, each running a three-mind debate, plus a cheap Read
round and a one-time recon. Materially more than the old command per round — but the old command's cost
was paid in the operator's reading time, which is the scarcer resource, and it is why the command went
unused.

**Stage detection.** "The table has converged" is a judgement call the orchestrator could get wrong.
Mitigation: it never advances on its own; it asks (D16), and the chair can ignore the question.

---

## 14. Open

Nothing structural. Naming of the two stage rooms, the exact default triads per lens, and the final
wording of the Operator Doctrine are all authoring decisions to settle during phase A.
