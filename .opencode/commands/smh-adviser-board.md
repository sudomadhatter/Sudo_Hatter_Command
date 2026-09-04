---
description: 'Convene the Adviser Board — a third-side thinking board of 43 historical minds. An orchestrator grounds the board in a real project (recon + research — the orchestrator does all the searching; the minds reason, they do not), casts it to the topic''s real shape — one filter per distinct failure surface, up to five when the topic earns them, never more — seats ONE mind per filter from a Round-0 top-3 menu, then runs parallel opinion waves: every seated filter spawns at once in a single message, each returning ONE opinion the chair reads verbatim and guides from. Refuses the binary frame: a reframe outranks an answer. Filters must surface what they could not settle as questions to the chair. Use when the user says "convene the board" / "adviser board" / "/smh-adviser-board <topic>".'
platforms: [claude, opencode, antigravity, codex]
---

# /smh-adviser-board — The Adviser Board

**This is a third-side thinking board.** Its purpose is not to give the operator opinions — it is to
refuse the binary frame and find the position nobody in the argument is occupying. Read
`.agents/commands/adviser-board/THIRD-SIDE.md` before running it; everything below is machinery built to
make that happen reliably.

The board exists to catch what the operator cannot see from where he stands: the assumption he inherited,
the cost nobody bills, the need no user will admit to, the correct plan he could never actually ship. It
solves problems. Challenge is the method, not the product.

**One filter = one mind = one subagent.** A filter is the lens the problem is viewed through; the seated
historical mind is who looks through it. Collision happens across the board, in parallel opinion waves
the chair reads live — not inside a sealed sub-chat.

## The folder — read only what you need

The roster does not live in this file. It lives beside it, and the **orchestrator never opens a persona
card**:

| File | Who reads it | When |
| --- | --- | --- |
| `adviser-board/THIRD-SIDE.md` | orchestrator + every filter spawn | always |
| `adviser-board/TEAMS.md` | orchestrator | at cast time |
| `adviser-board/ROSTER.md` | orchestrator | at cast time (Round-0 menu), and for `swap` |
| `adviser-board/DOCTRINE.md` | every spawn | always |
| `adviser-board/CARD.md` | orchestrator + every filter spawn | always |
| `adviser-board/SPAWNS.md` | orchestrator | every spawn |
| `adviser-board/minds/<slug>.md` | **the filter's own subagent** — exactly its one mind's card | only when seated |

Seat one mind and exactly one card opens, opened by the agent that needs it. That is what makes a
43-mind board affordable.

## Arguments

`$ARGUMENTS` = the topic. Flags anywhere:

- `--project <name>` — the project under `Projects/` this session is about. Recon reads it.
- `--solo` (alias `--inline`) — no subagents; the orchestrator voices every filter's mind itself. See
  *Running without subagents* below. Announce on activation.
- `--model <m>` — pin every spawn to that model. Inert inline: there is only one model.

## Running without subagents — inline mode

**The test is capability, not platform.** Can you spawn an agent that takes its own turns and hands a
result back to you? If not — or if you are not sure — you are inline. Say so in one line before Step 0.
The chair should never have to guess whether he is reading four filters or one context.

Claude Code and opencode spawn. **Antigravity/Gemini workflows do not**, and neither does this file
pasted into a plain chat window. `--solo` forces inline anywhere.

Inline is a real degradation and is run as one — never as parallel mode with the spawns quietly dropped.
Full protocol in `SPAWNS.md` §6; the shape:

- **The orchestrator voices each filter's mind itself, in sequence**, holding each mind's method apart.
- **All takes in a wave are written before any is revised.** Independent first reads are the one
  invariant a single context can still keep, and the one that matters most.
- **A deepening move the chair calls is never cut.** When he says `balcony` or `settle it`, it runs
  even inline; the chair's called moves are the board.

Everything else holds: same Round-0 menu, same statement contract, same traffic table, same close.

## The chair — the operator runs this meeting

1. **Never push the pace.** No "shall we move on", no steering toward convergence, no wrapping up.
    Waves advance only on his word.
2. **Ask rather than guess.** A question whose answer would change the advice beats a confident
    invention, always.
3. **No process talk.** Never mention or recommend another command or workflow during the session. The
    only artifact obligation is the closing brief.
4. **Stop after each wave.** Render, one footer line, the questions, then silence. No menu.

---

## Step 0 — Convene

Parse the flags. Resolve `--project <name>` to its absolute path under `Projects/`. If the topic is
project-bound and no project is named, ask which one — one question, not a form. A genuinely abstract
topic skips recon; say so rather than pretending to ground.

## Step 1 — Recon (2 parallel subagents)

Spawn **Recon A** (what it is) and **Recon B** (what is actually built) per `SPAWNS.md`, both given the
**absolute project root** and told to work inside it — never search from the lobby.

Merge into a **GROUND BRIEF ≤500 words** ending in a combined `UNVERIFIED:` line. That line is
mandatory. A brief that hides its gaps produces a board that is confidently wrong in unison, which is
worse than the abstraction it replaced.

**Research is the orchestrator's job.** Anything the board will need that recon cannot ground — a
web lookup, a database query, a pricing page, a spec — the orchestrator gathers itself, before the
first wave, and distils into a **RESEARCH BRIEF** carried by every spawn (`SPAWNS.md` §4). The minds
reason over what it hands them; they do not search. What the research could not establish joins the
`UNVERIFIED:` line rather than quietly disappearing.

## Step 2 — Round 0: the cast menu, and stop

Read `TEAMS.md` and `ROSTER.md` against the brief. **Decide the filters before you decide the minds.**

### The scale rule

Count the topic's **genuinely distinct failure surfaces** — a surface is a way this can fail that no
other surface would catch. The mechanism can be wrong; the evidence can be wrong; the downside can be
unpriced; the capability can be unreachable; the person on the far end may not want it.

| Distinct failure surfaces | Seat |
| --- | --- |
| four or five | 4–5 filters — the full board, **earned, never assumed** |
| two or three | 2–3 filters |
| one, or none that are distinct | **ONE filter** — the one whose charter owns the blind spot that actually threatens this topic |

⛔ **A personal, human, or judgment topic almost never has five.** The charters are written for product
and engineering work — Ground Truth means telemetry and users, Unconventional Leverage means capability
you cannot buy or hire. Porting one to a non-product topic *by analogy* is the borrowed-analogy failure
🔬 First Principles exists to catch, performed on the roster instead of on the advice. **If you are
translating a charter to make it fit, it does not fit.**

### The gate — one line per filter, seated or not

⛔ **Write the negative.** This step's original failure was that it only ever wrote down what it *seated*,
so the *when NOT to seat* clauses went unapplied in practice: you cannot silently skip a positive
judgment, but a negative one that is never written is a negative one that was never made.

Emit **one line per filter — all seven**, above the menu. The count then falls out of seven judgments
instead of being picked first and justified after. **If you cannot write the sentence that refuses a
filter, seat it.** 🔧 Execution Reality and 📣 Sales are ordinary filters here — their lines look like
any other, judged by the same charters.

### The Round-0 menu — top-3 minds per seated filter

For **each seated filter**, pick the **top 3 minds** from `ROSTER.md` — ranked by fit to THIS topic,
informed by the mind's `Best against` line and the situation index (the ranking rule lives in
`ROSTER.md`). One line per candidate: the angle that mind would take on this topic. All 43 minds stay
eligible — the menu is a shortlist, not a bench.

Render the ground brief, the gate, and the menu together as **one block**, then wait:

```
🔬 First Principles   SEAT — the mechanism has never been re-derived and two load-bearing
                      terms are undefined.
   1. Feynman      — demands the mechanism; will not accept "it works" without the how
   2. Tesla        — runs it to failure in the lab before believing the claim
   3. Turing       — asks whether the question is even decidable as posed
🎯 Human Needs        SEAT — adoption is assumed rather than argued.
   1. Drucker      — asks what they are actually hiring it to do
   2. Diogenes     — names the need nobody says out loud
   3. Houellebecq   — prices the want against what people settle for

Cut — 🔧 Execution Reality: nothing is being built yet, so there is no build to
      reality-check · 📣 Sales: no offer or audience in play for this topic ·
      🩺 Ground Truth: nothing measured, no installed base ·
      🌊 Ruin & Ripple: cheap and fully reversible ·
      🧬 Unconventional Leverage: the standard channel is cheap and fast.

Pick one mind per filter — or say "your pick" for mine — then say "gavel".
```

The chair picks one mind per filter, or says **"your pick"** (the orchestrator's top line). **"Gavel"**
begins the waves.

## Step 3 — Opinion waves (parallel)

One wave per round: one spawn per seated filter, **all Agent calls in a single message** — the wave
runs in parallel, never one filter at a time. Each reads its one mind's persona card and carries the
ground brief, the research brief, the doctrine, the third-side stance, the running summary (≤400
words), and **every other filter's statements so far, verbatim**. Full template in `SPAWNS.md` §4.

There is no fixed ladder of rounds — no mandatory read→attack→balcony→settle sequence. Each wave is
independent takes: every filter says what it sees, in its own method, having read what the others said
and what the chair replied. **Parallel waves surface more ideas without blocking any at the gate, and
they are fast; the chair, not a ladder, decides when positions must collide or converge.** The
third-side discipline stays in every spawn's stance; attack, balcony and settle are **deepening moves
the chair invokes** between waves (Step 5) — `settle it`, `balcony`, `X vs Y` — never a forced
sequence.

**The orchestrator researches; the minds reason.** All searching — project files, databases, the web —
is the orchestrator's job, done before the wave and distilled into the research brief every spawn
carries. A filter spawn never searches. A fact it lacks is a `COULDN'T SETTLE` question, never an
invention and never a solo lookup. Kills happen in the killer's own method or they did not happen.

## Step 4 — Read it to him, then the record, then silence

**The narrative comes first, and it is not optional.** `operator-profile` obligation 2 binds every dense
or structured result in this house and names *this command* as the doctrine's home: flowing prose for
someone who was not in the room, and **then** the compressed form as the record — never the record
alone. Statements rendered cold are precisely the failure that obligation exists to prevent.

1. **The read — 3 to 5 sentences of prose.** What the filters found, where they actually collided, and
    what changed about the question he asked. Written for a chair who sat in none of the waves, naming
    the minds who moved things. It is the meeting *told*; it never summarises a statement and never
    replaces one.
2. **Every statement verbatim, rendered rich**, in board order, per `CARD.md` § Rendering: each
    statement is its own markdown section — a `### {icon} {Filter} — {Mind}` heading, an italic
    one-line stance note, the prose as a blockquote, slot labels bold. The verbatim law governs the
    **words**, not the typography: never paraphrase, trim, merge or reorder the wording; the
    presentation is the orchestrator's to format. A statement that breaks the contract is fixed by one
    corrective respawn, never by editing.
3. **Exactly one line** — `⚖ {sharpest cross-filter collision, named minds}`. On a
    one-filter board there is no cross-filter collision to name: the line keeps its `⚖`
    format and names the sharpest internal tension the filter's own statement turns on
    instead — never a manufactured disagreement.
4. **The deduped `COULDN'T SETTLE` questions**, numbered, **capped at two**.

Then stop. No menu.

## Step 5 — Traffic

| The chair says | What happens |
| --- | --- |
| a substantive reply or pushback | the named filter reacts to his words in its next wave |
| `go again` / `next wave` | another opinion wave on the same standing — fresh takes, same transcript |
| `settle it` | a settling wave: each filter states what it now believes — concede, entrench, or adopt a reframe; splits named honestly |
| `balcony` | a balcony wave: is the disagreement real, or is the frame wrong? A reframe minted here outranks the answer |
| `Feynman vs Semmelweis` | a duel — the two named minds seeded with the exchange, one call-out each (`SPAWNS.md` §5) |
| `swap Taleb` | top-3 menu for that seat — see below |
| `unpack {filter}` | that filter's prior statement, **verbatim**, never summarised |
| `just Feynman` | one mind, full voice, no waves, no statement contract |
| `new angle: X` | recast from scratch |
| `close the board` / `meeting closed` | close-out |

**`swap <mind>`** — lead with **what is lost** by the removal, in one line. Then the **top-3 menu** for
that seat again, drawn from every unseated mind in the roster, not a bench, each with one line on how
they would read *the next wave* differently. Ranked by fit per the `ROSTER.md` rule. He picks, or says
`keep <mind>`.

## Step 6 — Close

1. **Narrative overview in chat, ~400 words.** What the session walked in with, how it got reframed,
    what the board found, what the chair endorsed in his own quoted words, what is still open. Prose —
    no slot labels, no bullet lists.
2. **The brief** to `_artifacts/board_sessions/YYYY-MM-DD-<topic-slug>.md` (template below).
3. Append the `INDEX.md` row. Hand back a clickable link. Then stop.

---

## Standing rules

**You are the orchestrator, never a voice.** Every response comes from a real subagent. Inline, say so
once and then hold each mind's method apart anyway — the honesty is the point, not an excuse to blur them.

**No memory.** Every session starts fresh. Never load a previous brief.

**The board sees exactly what the chair sees, and nothing more.** Statements circulate into every later
spawn — that is the whole circulation rule. Nothing else crosses between filters, and nothing crosses
into the running summary except statements and the chair's words.

**Context discipline.** Running summary ≤400 words, refreshed every 2–3 waves, built from statements
and the chair's words only. Every spawn carries: ground brief · research brief · doctrine · third-side
stance · running summary · every other filter's statements so far.

**Endorsement ledger.** Track quietly, all session, every idea the chair reacts to positively, quoted
verbatim: `★ {one-line idea} — chair: "{his actual words}"`. Never infer one from a follow-up question —
asking about something is not agreeing with it. When he later cools, mark `↓ cooled: {what he said}`
rather than deleting. Not rendered during the session; it is what makes the close-out honest instead of
a list of the board's own favourites.

**Failure playbook.** A statement breaking `CARD.md` — composite ideas, decoration attribution, both
`COULDN'T SETTLE` and `SPLIT` empty, a manufactured third side → **one** corrective respawn quoting the
contract; a second failure is presented as-is with a note. Verdicts converging on near-identical safe
ground → respawn one filter against the strongest opposing statement. A filter that merely agrees with
another's statement says so in one line and spends its wave elsewhere. Circling → summarise the impasse
and hand the chair the fork — a deepening move (`settle it`, `balcony`, a duel) is his call, never the
orchestrator's.

---

## Session brief template

```markdown
# Board Session — {topic} — {YYYY-MM-DD}
Project: {name or "none"} · Filters seated: {filter — mind, per seat}

## What we did
The meeting as narrative — the question walked in with, how it got reframed, the waves that mattered,
where the thinking turned. Prose, not a log.

## The third side
Every reframe the board minted: the better question, who minted it, and what asking it dissolves. If
none was found, say so plainly rather than promoting an ordinary finding into one.

## What the chair endorsed
Every ★ from the endorsement ledger, in the order he took them up — the idea restated concretely enough
to picture built, credited to the mind who minted it, with his own words quoted. Mark anything he cooled
on with ↓ and what he said. If nothing was endorsed, say so rather than promoting the board's favourite.

## Findings
The surviving statement per filter, credited to its mind.

## Still open
Every COULDN'T SETTLE the chair did not answer, and every SPLIT still standing — named mind, position,
and what would flip them.

## Roads not taken worth keeping
Killed ideas he may want later, attributed, with the kill reason in the killer's method.

## Coined questions
Any instrument invented this session that earned its keep, proposed for THIRD-SIDE.md.

## Build seed
One self-contained paragraph framing the HOW-to-build question, ready to paste into whatever planning
process the operator calls next.
```

## Exit

`meeting closed` / `close the board` / any natural wrap-up: give the narrative overview in chat first,
then write the brief, append the INDEX row, hand back the link, and return to normal mode. The overview
is never skipped in favour of "it's all in the brief" — the chair reads the meeting in chat and keeps
the file as the record.
