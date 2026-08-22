# Walkthrough — `operator-profile` rule + `/sudo-adviser-board` close-out

**Date:** 2026-07-22 · **Workspace:** Sudo_Hatter_Command (home base)
**Plan:** [implementation_plan.md](implementation_plan.md) — approved 2026-07-22
**Scope note:** Daniel added a second, smaller item at approval time (the "meeting closed" trigger).
Both shipped in this session.

---

## Part 1 — The `operator-profile` rule

### The gap

No file in the master rule chain described who Daniel is, his technical level, or how to work with
him. Five rules encoded *symptoms* of the profile (prose over bullets, no sequence diagrams,
instrument-and-ask, clickable links, plan key points inline) without ever naming the person or the
reason. The one place the doctrine did live — the "explain it like I'm Steve Jobs" memory from
2026-07-21 — was Claude-private and encoded into exactly one skill, so opencode, Antigravity, and
Codex never saw it.

### What was built

**[.agents/rules/operator-profile.md](../../../../../.agents/rules/operator-profile.md)** — NEW, `activation:
Always On`, floor tier. Three parts:

1. **Who Daniel is** — product-and-systems thinker; designed this command center; reads and reasons
   about code fluently; does not write the implementation and does not want to. Fluent in *what* and
   *why*, delegates *how*.
2. **The contract** — a two-column table splitting what he owns (vision, product judgment, go/no-go,
   the final call) from what the agent owns (feasibility, architecture, the code, the honest "that
   won't work"). Names the failure it exists to prevent: handing him a menu of technical options and
   making him pick the engineering — abdication dressed as respect.
3. **Eight speaking obligations**, written to be falsifiable rather than aspirational — lead with the
   consequence not the mechanism · narrative first, compression second · define coined terms at first
   use · one worked example beats three abstractions · never make him the compiler · push back in plain
   language · he is the hands, you are the engine · he reviews from the conversation.

Plus a "downstream rules this explains" section naming the five rules that are consequences of it, and
a one-line self-check for the opening sentence of any substantial reply.

### Wiring

| File | Change |
|---|---|
| [AGENTS.md §3](../../../../../AGENTS.md) | added to the always-load line, first, with a one-clause gloss |
| [.agents/rules/INDEX.md](../../../../../.agents/rules/INDEX.md) | added to the floor tier in "How rules load" + a row in the set table; notes *why* it can't be on-demand (it would load after the reply that needed it) |
| [.agents/rules/prose-formatting.md](../../../../../.agents/rules/prose-formatting.md) | blockquote pointing up to `operator-profile` as the WHY; states that on conflict, `operator-profile` is the intent |
| `Projects/Fresh_Workspace_BMAD/` | rule copied + its `AGENTS.md` §4 and `.agents/rules/INDEX.md` mirrored, per `living-template-sync` — new projects start current |

---

## Part 2 — `/sudo-adviser-board` close-out ("meeting closed")

### What was missing

Phase 4 already wrote a session brief, but three gaps meant it couldn't do what Daniel asked:

- **"meeting closed" wasn't a recognized phrase** — only "close the board", "thanks", "that's all".
- **Nothing tracked what he agreed with.** The brief recorded verdict, dissents, and killed ideas, but
  there was no record of the operator's own endorsements — so a close-out would have had to *guess*
  which ideas he liked, or silently promote the board's favorites.
- **The in-chat close was "a two-line wrap"** — the compressed form only, which is precisely the
  failure mode that produced the 2026-07-21 complaint.

### What changed — all in [.agents/commands/sudo-adviser-board.md](../../../../../.agents/commands/sudo-adviser-board.md)

The skill and workflow files are thin launchers pointing at the command, so the command is the single
source of truth and no duplication needed fixing.

1. **Trigger** — `"meeting closed"` added to the chair's phase-advance phrases (§ The chair, item 1)
   and made the headline phrase in § Exit.
2. **Endorsement ledger** — NEW standing rule beside the idea ledger. Records every positive reaction
   live, as `★ #{n} — {idea} — chair: "{his actual words}"`. Guardrails written in deliberately: quote
   him rather than paraphrase, never inflate an endorsement, never infer one from a follow-up question,
   and mark `↓ cooled` rather than deleting when he later backs off. This is the input the close-out
   reads from — without it the section is guesswork.
3. **Phase 4 rewritten** as two ordered deliverables — the meeting's own two-part shape applied one
   last time. First a **closing overview in chat**, 400–800 words of flowing prose: what we walked in
   with, what the board did, where the thinking turned, **what the chair endorsed** (each restated
   concretely, in his framing), what's still open. Then the brief as the record, with its `INDEX.md`
   row and a clickable link back.
4. **Brief template** gained two sections at the top: `## What we did` (the overview, preserved) and
   `## The chair's picks — what Daniel endorsed` (the ★ ledger, credited, with `↓` entries kept and an
   explicit "nothing was endorsed" instruction rather than promoting a favorite).

---

## Verification

- `sync-agents.ps1` ran clean: 14 lobby Claude cmds · 40 opencode · 40 opencode-global · 19
  Antigravity-global · 13 Codex prompts · 56 Codex bmad skills · "Fresh living-template check OK."
- Grepped the new strings in the three downstream caches — opencode global (5 hits), Codex prompts (4),
  lobby `.claude` (4). The edits are live on every surface, not just the master.
- `operator-profile.md` confirmed present in both the master `.agents/rules/` and the living template.

**Not yet proven:** the behavioral outcome. The real test is a *fresh* session — ideally an opencode or
Antigravity one, which has no Claude memory to fall back on — leading with the consequence and writing
in prose without being told. That can't be verified from inside this conversation.

## Your Actions

1. **Restart opencode** to pick up the refreshed global command cache (the sync script says so itself).
2. Review the rule — especially the "Who Daniel is" paragraph, which is my read of you rather than your
   words. Correct it and everything downstream re-aligns.
3. Commit when you're happy:

```bash
cd C:\Sudo_Hatter_Command
git add .agents/rules/operator-profile.md .agents/rules/INDEX.md .agents/rules/prose-formatting.md AGENTS.md .agents/commands/sudo-adviser-board.md .claude/commands/sudo-adviser-board.md .opencode/commands/sudo-adviser-board.md .agents/.sync-manifest.json _artifacts/INDEX.md _artifacts/_main/2026-07-22_operator-profile-rule/
git commit -m "feat: add operator-profile floor rule (Jobs/Woz contract) and adviser-board 'meeting closed' close-out"
```

Fresh_Workspace_BMAD is its own git repo — commit its three changed files separately:

```bash
cd C:\Sudo_Hatter_Command\Projects\Fresh_Workspace_BMAD
git add .agents/rules/operator-profile.md .agents/rules/INDEX.md AGENTS.md
git commit -m "feat: vendor operator-profile floor rule from home base (living-template-sync)"
```
