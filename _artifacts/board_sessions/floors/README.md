# Debate floors — inline sessions only

A **floor** is a team's raw debate: three minds arguing across the cycles, before the ~250-word card is
written. It is deliberately not something the chair reads by default — the card is.

When the board runs with subagents (Claude Code, opencode) the floor lives inside the spawn that produced
it and never touches disk. On a surface that cannot spawn — Antigravity/Gemini, or the command pasted
into a plain chat — the orchestrator writes the floor here **before** writing that team's card, so
`unpack` has something real to quote instead of a reconstruction.

One file per team per session:

```
YYYY-MM-DD-<topic-slug>-<lens-slug>.md
```

Written once, never edited afterwards. A floor that was reconstructed after the fact is not a floor, and
the board says so out loud rather than quoting it.

Protocol: `.agents/commands/adviser-board/SPAWNS.md` section 7.
