# Implementation Plan — SCC-333

**Ticket:** [SCC-333](https://sudo-command.atlassian.net/browse/SCC-333) — Adviser board: cast discipline + narrative-before-cards, and delete the prose-formatting rule
**Branch:** `chore/SCC-333-adviser-board-cast-discipline` (off `main`)
**Lane:** chore / toolkit — doc-and-law only, no product code
**Date:** 2026-08-26

---

## 1. Goal and background

A live `/smh-adviser-board` run on a personal topic exposed three defects. All three are in the
system's law, not in the advice the board produced, and all three are cheap to fix.

**The root finding is a contradiction between two files.** `operator-profile.md` obligation 2 says
any dense or structured result — it names cards and multi-agent output specifically — gets flowing
narrative written for someone who wasn't in the room, **and then** the compressed form as the record,
never the record alone. It explicitly calls `/smh-adviser-board` the home of that doctrine. But the
command's Step 5 says render cards verbatim, then one collision line, then stop. No narrative. So an
orchestrator that follows the command violates the floor rule the command is supposed to embody, and
the operator reads a wall of cards. That is the real cause of the "hard to read" complaint — not a
judgment error in the session.

`prose-formatting.md` claims to be the formatting consequence of that same obligation and is
actually its opposite: it says prefer prose, minimize structure, where obligation 2 says add a
narrative layer **on top of** the structure. It was distilled from a consumer-chat doctrine aimed at
a casual linear reader rather than an operator scanning for the decision and the anchor. Two rules
that disagree, one of them firing off a keyword hook.

**The casting defect is separate and structural.** Step 2 tells the orchestrator to seat 3–5
load-bearing lenses and honour every charter's *when NOT to seat* clause — but the only thing it
writes down is the lenses it seated. The negative judgments never get written, so they never
actually get made. On a personal topic the orchestrator seated five lenses where two or three were
load-bearing, and the operator had to correct it twice. The command applies "make the discipline
structural, not remembered" to its debate rooms (cycle 3 is mandatory, an empty `COULDN'T SETTLE`
forces a respawn) and does not apply it to its own casting step.

`bmad-party-mode` solves the same problem differently and better: it picks **2–4 individual agents
per round**, defaults to two for a simple question, rotates so the same voices don't dominate, and
never convenes the full roster. Its atom is one agent. The board's atom is a lens of three, so its
smallest possible move is three minds and its "modest" option is nine — which is why "do we need
five teams" had no good answer inside the current design.

---

## 2. Proposed changes, by file

### A. Delete the contradicting rule

| File | Change |
|---|---|
| [.agents/rules/prose-formatting.md](../../../.agents/rules/prose-formatting.md) | **DELETE.** |
| [.agents/rules/INDEX.md](../../../.agents/rules/INDEX.md) | Remove its row (line 67). Edit line 46 — `operator-profile`'s row names `prose-formatting` as a downstream rule. |
| [.agents/rules/operator-profile.md](../../../.agents/rules/operator-profile.md) | Remove the name from the `description:` frontmatter (line 3) and from the downstream list (line 101). **Salvage its one good clause** — "never use bullets when declining or pushing back; prose carries the nuance" — into obligation 6 (*Push back in plain language*), where it belongs. |
| `docs/doc-graph.json` | Generated cache — **rebuild, never hand-edit.** Rebuild bare per `doc-graph-unc-hang-and-scope`. |

**Deliberately not touched:** `docs/workspace-standard.md:419` and every `_artifacts/**` hit are
historical records of past work — history stays true. `Projects/B-L-WorldWide/.agents/rules/` holds
a vendored copy in a project that is frozen on purpose (`toolkit-installed-but-deliberately-unmaintained`);
sync scope is lobby + caches only.

### B. Step 5 — narrative before the cards

| File | Change |
|---|---|
| [.agents/commands/smh-adviser-board.md](../../../.agents/commands/smh-adviser-board.md) | Rewrite **Step 5**. New order: a short narrative read (2–4 sentences, prose, written for someone who was not in the room, naming what the rooms found and where they collided) → the cards **verbatim** → the `⚖` collision line → the deduped questions → stop. The verbatim guarantee is untouched; it gains a preamble, it does not lose its record. |
| [.agents/commands/adviser-board/CARD.md](../../../.agents/commands/adviser-board/CARD.md) | § Rendering currently says cards render "with nothing between them" and "after the last card, exactly one line". Add the narrative-first clause so the two files cannot contradict each other. |

### C. Step 2 — cast discipline

| File | Change |
|---|---|
| [.agents/commands/smh-adviser-board.md](../../../.agents/commands/smh-adviser-board.md) | Rewrite **Step 2** with three additions. (1) **Written negative for all seven rooms** before the gate — one line each, `SEAT` with its triad or `OBSERVING` with the charter's own clause **and the cost of the cut**. (2) **A scale rule:** five lenses only when the topic genuinely has five distinct failure surfaces; a personal or human topic defaults to 2–3. (3) **Name the axis** each collision runs on, so the two-axis rule is checkable instead of merely stated. |
| [.agents/commands/smh-adviser-board.md](../../../.agents/commands/smh-adviser-board.md) | **New: the single-room cast.** When a topic has no distinct failure surfaces, seat **one room of three cross-lens minds** rather than filling whole lenses. The three-mind two-axis discipline is preserved exactly; the lens charters become a way of *finding* which minds are load-bearing rather than a mandatory container. One card instead of five. |
| [.agents/commands/adviser-board/TEAMS.md](../../../.agents/commands/adviser-board/TEAMS.md) | Add the "the topic may not be a product" clause and the single-room provision, so the charters file and the command agree. |
| [.agents/commands/adviser-board/ROSTER.md](../../../.agents/commands/adviser-board/ROSTER.md) | Add a **`Reach for them when`** line to all 43 minds — a *situation*, not a failure mode. `Best against` tells you Friston is sharp against systems designed to avoid surprise, which is useless unless you already think in those terms; the new column says he is the mind for anything with a nervous system in it. This extends the existing *Cross-lens regulars* pattern (already the most useful part of the file) across the whole roster. |

### D. The doors and the SOP

| File | Change |
|---|---|
| [.agents/commands/smh-adviser-board.md](../../../.agents/commands/smh-adviser-board.md) | Frontmatter `description:` currently says "casts 3–5 lenses with THREE minds each" — now wrong. Update. |
| `.agents/skills/smh-adviser-board/SKILL.md` and `.claude/skills/smh-adviser-board/SKILL.md` | Generated launchers carrying that description. Regenerate via `/smh-sync-agents`; hand-edit both frontmatters if the sandbox blocks it (SCC-300). |
| [docs/_scc_sops_prds/workflows_testing_SOP.md](../../../docs/_scc_sops_prds/workflows_testing_SOP.md) | **Required by the armed gate**, not optional. `sop_currency.py` watches `.agents/commands/*.md` **and** `.agents/rules/*.md`; this ticket touches both. A real edit describing the new cast behaviour — no `[sop-ok]` opt-out. |

---

## 3. Open questions

1. **Does the single-room cast get a traffic verb?** The chair could type `one room` to force it, or
   it could stay purely an orchestrator decision at cast time that he overrules at the gate like any
   other. I lean **no verb** — the gate already lets him restructure the cast, and a verb adds surface
   for a case that should be the orchestrator's read.
2. **Where does the salvaged bullets-when-pushing-back clause land?** I propose obligation 6
   (*Push back in plain language*) rather than minting a tenth obligation.
3. **If `/smh-sync-agents` is sandbox-blocked in-session, is hand-editing both launcher frontmatters
   acceptable?** They are marked `GENERATED … do not edit`, so this is a deliberate exception, and the
   next real sync would overwrite it harmlessly with the same text.

---

## 4. Verification

```bash
# the enforcement gate — run bare, never piped (piping-a-gate-hides-its-exit-code)
python .agents/scripts/tests/run_all.py

# rules INDEX table vs per-rule markers must agree; a test fails if they don't.
# dangling links in generated rule copies also fail a test. Both are inside run_all.
```

Then, after the suite is green:

```bash
# doc graph is a CACHE — rebuild bare, do not widen --root (doc-graph-unc-hang-and-scope)
python .agents/scripts/doc_graph.py --rebuild

# board
acli jira workitem transition --key SCC-333 --status "In Progress" --yes
```

**Manual verification that matters more than the suite:** re-run `/smh-adviser-board` on a small
personal topic and confirm the gate now prints seven lines, seats 2–3, and that Step 5 opens with
prose before the cards.

**Expected gate behaviour:** the commit-msg hook **must** reject a commit that omits
`workflows_testing_SOP.md`. If it does not, the hook is not armed on this machine
(`git config --global core.hooksPath .githooks`) and that is its own finding.

---

## 5. Close-out

Single ticket, single branch, PR to main via the normal door. SCC-333 → `Done` at close-out on the
operator's word. The deleted rule is not separately tracked — the operator's call.
