# Implementation Plan — `operator-profile` rule (the "who am I talking to" law)

**Date:** 2026-07-22
**Workspace:** Sudo_Hatter_Command (home base / lobby)
**Status:** DRAFT — awaiting Daniel's "approved"

---

## 1. The finding (what I verified)

I read the whole master rule chain and searched every `.md` under `.agents/` and `docs/` for
operator-identity language ("Daniel is…", technical level, Steve Jobs, Woz, how to talk to him).

**There is no section anywhere in the master rules that describes who Daniel is.**

What exists today is a set of *symptoms* of the profile, scattered across five files, none of which
ever names the person or the reason:

| File | What it encodes | What it never says |
|---|---|---|
| [prose-formatting.md](../../../.agents/rules/prose-formatting.md) | chat = prose, not bullet scaffolding | *why* — that Daniel reads for meaning, not for tokens |
| [mermaid-diagram-preferences.md](../../../.agents/rules/mermaid-diagram-preferences.md) | never `sequenceDiagram` | that this is one instance of "match his mental model" |
| [collaborative-debug-first.md](../../../.agents/rules/collaborative-debug-first.md) | he can see the browser, you can't — instrument and ask | that he is the hands, you are the engine |
| [constitution.md §Always](../../../.agents/rules/constitution.md) | clickable links, never bare paths | that he navigates by clicking, not by pasting paths |
| [000-PLAN-FIRST-GATE.md](../../../.agents/rules/000-PLAN-FIRST-GATE.md) | key points inline in chat, not just a file | that he approves what he can *read in the conversation* |

Plus one memory (`presentations-before-compressed-summaries`, 2026-07-21) that captures the
"explain it like I'm Steve Jobs" doctrine — but it lives in Claude's private memory and is encoded
into exactly one skill (`/sudo-adviser-board`). Antigravity, opencode, and Codex never see it.

**Diagnosis:** the system has the *reflexes* but not the *model*. Every one of those rules is a
downstream consequence of a fact that was never written down. That's why the behavior degrades
whenever a flow isn't one of the five that happened to get patched.

---

## 2. The idea, grounded

The vision — "you be Woz, I'll be Jobs" — is real and it is implementable, but only if it's stated
as a **working contract with observable obligations**, not as a vibe. A rule that says "treat Daniel
like a visionary" is unfalsifiable and will be ignored under context pressure. A rule that says
"never hand him a decision phrased in implementation vocabulary; phrase it in consequences" is
checkable on every single reply.

So the rule has three parts, in this order:

**(a) Who he is** — one short paragraph, no flattery. Product-and-systems thinker who designs the
architecture of this whole command center, reads code and reasons about it fluently, but does not
write the implementation and does not want to. Fluent in *what* and *why*; delegates *how*.

**(b) The division of labor** — the Jobs/Woz contract made concrete:

- He owns: the vision, the product judgment, what gets built, what "good" means, go/no-go.
- I own: turning it into something that actually runs — feasibility, architecture, the code, and
  the honest "that won't work, here's what will."
- The failure mode this prevents: I hand him a menu of technical options and make *him* choose the
  engineering. That's abdication dressed as respect. My job is to come back with a recommendation
  and the one tradeoff that actually matters, not a survey.

**(c) How to speak to him** — the falsifiable part:

1. **Lead with the consequence, not the mechanism.** "Voice sessions drop when a user switches
   tabs" before "the WebSocket keepalive isn't bound to visibilitychange."
2. **Narrative first, compression second** — the doctrine already proven in `/sudo-adviser-board`.
   Any dense result gets flowing prose written for someone who wasn't in the room, *then* the
   table/cards as the record. Never the record alone.
3. **Define coined terms at first use.** Every internal name — Bridge Keys, the TEA gate, DB1/DB2 —
   gets a five-word gloss the first time it appears in a session. He named half of them and still
   shouldn't have to reload them.
4. **One worked example beats three abstractions.** Show it running end-to-end on real input.
5. **Never make him the compiler.** No mental diffs, no "as noted above", no label/numbering
   cross-references he has to hold in his head, no arrow chains.
6. **Push back in plain language.** When his direction won't survive contact with reality, say so
   directly and propose the version that will. Deference that lets a bad idea ship is a failure of
   the Woz role, not politeness.
7. **He is the hands.** He can see the browser, the app, the device; I can't. Ask him to look and
   report back rather than guessing — already law in `collaborative-debug-first`, restated here as
   the general principle.

---

## 3. Files to change

| # | File | Change | Risk |
|---|---|---|---|
| 1 | `.agents/rules/operator-profile.md` | **NEW** — the rule above, `activation: Always On`, ~70 lines | none (new file) |
| 2 | `.agents/rules/INDEX.md` | add row to "The set" table (floor tier) + name it in "How rules load" | trivial |
| 3 | `AGENTS.md` §3 ALWAYS-LOAD | add `operator-profile.md` to the always-load line | trivial — one sentence |
| 4 | `.agents/rules/prose-formatting.md` | one line pointing up to `operator-profile` as the *why* | trivial |
| 5 | `Projects/Fresh_Workspace_BMAD/.agents/rules/` | copy 1 + mirror 2–4, per `living-template-sync` | low |
| 6 | `/sync-agents` | run it so all four platforms (Claude, opencode, Antigravity, Codex) pick it up | low |

**Not doing:** editing the Claude-private memory file. The whole point is to move this out of one
model's private memory and into the portable `AGENTS.md` contract that every surface reads.

---

## 4. How we know it worked

- Fire a fresh session and ask a dense question; the reply leads with the consequence and reads as
  prose, without me being told.
- The `/sudo-adviser-board` two-part shape stops being special-cased — it becomes the house default
  that skill happens to name explicitly.
- Regression check: an opencode or Antigravity session (no Claude memory) exhibits the same
  behavior, which is the thing that fails today.

---

## 5. Open questions for Daniel

1. **Third person or second?** I've drafted it as "Daniel" (third person, matches every other rule).
   Alternative is "you" — reads warmer, but breaks the house voice.
2. **Floor or protocol tier?** I've put it on the **floor** (always loaded, ~70 lines, sits next to
   `constitution` + `karpathy-guidelines`). It's cheap and it governs every single reply, so I don't
   think it can be on-demand — an on-demand "how to talk to you" rule loads *after* the reply that
   needed it. Flagging it because it does add to every context window.
3. **Anything in §2(a) wrong?** That paragraph is my read of you from the rules and the work, not
   something you told me. If the self-description is off, everything downstream inherits the error —
   correct it and I'll rewrite from your words.

---

## 6. Your action

Reply **"approved"** (optionally with corrections to §5) and I'll build all six steps and run
`/sync-agents`.
