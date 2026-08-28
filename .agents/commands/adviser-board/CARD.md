# The Statement — contract

One statement per filter per wave. **~250 words**, hard ceiling 320. This is the entire visible output
of a filter's wave; the chair reads it verbatim.

The chair reads three to five of these before he replies. That budget is the whole design constraint —
the command this replaced spent 500–2,000 words per lens and went unused because of it.

---

## Shape

```
{icon} {FILTER} — {Mind}

{4–6 sentences of prose in the mind's own voice. What this mind found, and why it matters to the
chair. Plain language. Every coined term defined at first use. This is the part he actually reads —
the slots below are the record, this is the meeting.}

THE THIRD SIDE:   {optional, and it outranks THE MOVE when present — the reframe minted at the
                   balcony: the better question, and what asking it dissolves}
THE MOVE:         {the concrete thing to do, specific enough to picture built}
COULDN'T SETTLE:  {the gap in the world this mind needs the chair to fill — at most 2 questions}
ASSUMED:          {any assumption carried from a question that didn't reach the chair}
SPLIT:            {this mind's position} — flips if {condition}   — or —   none, conceded on {point}
```

---

## Rules

**The voice is the mind itself.** One mind per filter means one voice per statement — no presenting
speaker, no blended voice, no "we". The prose is written as the seated mind, in its method.

**`THE THIRD SIDE` outranks `THE MOVE`.** When the balcony produced a reframe — the filter concluded the
chair's question was the wrong one and has a better one — that goes first and the statement is built
around it. Telling the chair his question was wrong, and handing him the one he should be asking, is the
most valuable output this board has. See `THIRD-SIDE.md`.

Do not manufacture one. A wave that genuinely answered the question as asked leaves the slot out, and
the orchestrator never asks for a reframe that wasn't found. A fake third side is worse than none,
because it teaches the chair to skim the slot.

**Credit belongs to the originator.** One mind per statement makes this structural — the name in the
header minted what is in the statement. The rule that survives from the old contract is decoration
attribution: if a credited line could be reassigned to another mind unchanged, it was decoration —
rewrite it from that mind's actual method, or cut it.

**Kills are performed in the killer's method.** If Munger cannot state the kill as an inversion, or Taleb
as an exposure, or Kepler as an un-rounded anomaly, it did not happen at this board.

**`COULDN'T SETTLE` and `SPLIT` cannot both be empty.** A wave in which every opposed filter settled
everything and needed nothing from the chair is a wave in which they did not dig. The orchestrator
respawns such a statement **once**, quoting this rule; a second failure is presented as-is with a note.

This inverts the usual instinct on purpose. A filter that asks nothing is not exemplary — it is
suspicious, because it either skipped the hard part or invented its way past it. The questions a board
asks the chair are where its value concentrates: they are the places where only he holds the answer, and
surfacing them is worth more than another confident paragraph.

**`COULDN'T SETTLE` is bounded.** At most two questions per filter, and the orchestrator forwards at most
two across the whole wave, ranked by how much advice each answer would move. Questions that don't make
the cut do not disappear — the filter proceeds on an explicit `ASSUMED` line so a wrong assumption is
caught when the statement is read.

**Questions arrive in the mind's own method.** Feynman asks for the mechanism, Drucker asks what the user
is hiring it to do, Diogenes asks to be shown. Each persona card's `Asks the chair` section is what this
draws on. A generic "what is your budget?" is a wasted question.

**No process talk, ever.** A statement never suggests ending the session, moving to another wave, or
which command to run next. That is the chair's call alone.

---

## Rendering

**A 3–5 sentence prose read comes before the block of statements** — the meeting told to a chair who sat
in none of the waves. That is `operator-profile` obligation 2 and the command's Step 4; it is the one
thing allowed above the statements, it summarises no statement, and it replaces none. Without it the
chair reads a wall.

Statements then render **verbatim, in rich text**, in board order. The verbatim law governs the
**words**, not the typography: the orchestrator never paraphrases, trims, merges, reorders or re-cuts a
statement's wording — but it formats the presentation for reading. Each statement renders as its own
markdown section:

```markdown
### {icon} {Filter} — {Mind}

*{one-line stance note — what this mind is doing in this wave, e.g. "attacks the adoption
assumption; concedes the mechanism point"}*

> {the statement's prose, verbatim, as a blockquote}

**THE THIRD SIDE:** {verbatim slot content — when present it renders FIRST, above THE MOVE}
**THE MOVE:** {verbatim slot content}
**COULDN'T SETTLE:** {verbatim slot content}
**ASSUMED:** {verbatim slot content}
**SPLIT:** {verbatim slot content}
```

- The **heading** carries the icon, filter and mind — scannable at a glance.
- The **italic stance note** is the orchestrator's one-line signpost, written fresh per wave. It
  summarises the stance, never the words — it is the only non-verbatim text in the section, and it
  never substitutes for reading the statement.
- The **prose renders as a blockquote**; slot labels render **bold**, each slot on its own line.
- Slots that are absent this wave are simply not rendered.

A statement that violates this contract is fixed by one corrective respawn at the source, not by
editing — and the respawn fixes the words, never the format.

After the last statement, exactly one line:

```
⚖ {the sharpest cross-filter collision, naming the minds}
```

(On a one-filter board there is no cross-filter collision: the line keeps its `⚖` format and
names the sharpest internal tension the filter's own statement turns on instead.)

Then the deduped `COULDN'T SETTLE` questions, numbered, capped at two. Then stop. No menu, no "what
next?", no suggested commands.
