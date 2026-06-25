---
description: Pre-dev plan/story audit — run BEFORE coding. Pressure-tests an implementation_plan.md or story against the codebase and the ACs to catch gaps, over-engineering, and contract breaks before they're built.
---

<!-- Master toolkit workflow. Synced into each project's .agents/workflows/. Edit the master here; do not hand-edit project copies. -->

# Self-Audit Stress Test (Pre-Dev Gate)

Adversarial review of an `implementation_plan.md` or story **before any code is written.** The goal:
catch flaws while fixing them still costs nothing. Assume the plan is wrong somewhere, then try to
prove it. **Default to the leanest pass that covers the real risk** — the Phase 0 right-size gate is
the point; brute-forcing every phase on a trivial plan is the slow, expensive path this workflow
exists to avoid.

> No build commands here — there is no code yet. This audits the *plan*, not a diff. For shipped code,
> use `bmad-code-review`.

---

## Phase 0 — Scope, Right-Size & AC Coverage

1. **Name the target** — which plan/story file, and list each change it proposes (file/component,
   old → new, the state/logic it touches).
2. **Right-size the audit:**
   - **Skip** — a one-line copy/doc/config tweak. Stop; it doesn't need an audit.
   - **Light** — contained change (one function, a prompt string, an isolated component): Phases 1–3.
   - **Full** — touches a state machine, SSE/WebSocket contract, auth, a shared schema, or a symbol
     with many consumers: all phases.
3. **AC ↔ Plan traceability** (the #1 pre-dev catch): map every acceptance criterion to a concrete
   plan step, and every step back to an AC.
   - AC with no step → the plan will silently under-deliver. **Flag.**
   - Step with no AC → scope creep. **Flag for cut** (see Phase 2).
4. **Decomposition flag** — does this story modify **both backend AND frontend** (e.g. Python AND
   TypeScript)? If so, recommend splitting it (per constitution Ask-First).

---

## Phase 1 — Blast-Radius Trace

For each thing the plan proposes to change, trace it against the **current** codebase. Fill only the
rows that carry real risk:

| Symbol / Change | Existing setters (upstream) | Existing readers (downstream) | Breaks if… |
|-----------------|-----------------------------|-------------------------------|------------|

**Graph-first when available.** If this repo is GitNexus-indexed (its `AGENTS.md`/`CLAUDE.md` carries a
"GitNexus — Code Intelligence" section) and the MCP tools are present, use the code graph for the
**authoritative** blast radius instead of grepping blind:

- `impact({ target: "Symbol", direction: "upstream", summaryOnly: true })` — who breaks if this changes
  (the upstream/downstream columns, straight from the real call graph). Add `repo: "<IndexName>"` when
  more than one repo is indexed.
- `context({ name: "Symbol" })` — callers/callees + the execution flows the symbol participates in.
- **Read the confidence column** — code edges ≈ 1.0; doc/story-file mentions ≈ 0.8 (breadcrumbs, not code).
- **Caveat:** GitNexus links repos only via HTTP contracts — it will NOT surface coupling through a
  shared DB / data store; the Contract two-sidedness bullet below still needs manual reasoning.

**Fall back to grep** when the tools aren't available (headless autopilot runs, or a non-indexed repo) —
and keep grep as a cross-check for dynamic / string references the AST graph can miss:

```
grep -rn "symbolName" --include="*.ts" --include="*.tsx" --include="*.py"
```

- changed return value → does the plan account for every existing caller?
- changed props / API / DB schema → every existing consumer & query?
- renamed or removed → any dangling references the plan missed?
- **Contract two-sidedness** — if the change touches **one side** of a paired contract (SSE/WebSocket
  event, API schema, DB doc/row shape, function signature), does the plan name the **other side**?
  A backend event change that never mentions the frontend consumer is a guaranteed break.
- **Reinvention check** — does a helper / util / pattern the plan is about to build **already exist**?
  If yes, reuse it (also a Phase 2 tripwire).
- **Constitution + assumptions scan** (one line each, if relevant): does the *plan* propose a full-file
  rewrite where a surgical edit would do? a new DB client instead of the shared singleton (e.g.
  `get_db()`)? a hardcoded secret? a contract change touching only one side? an untested assumption
  about external state (DB docs/rows, cloud IAM, env vars)?

---

## Phase 2 — Over-Engineering Gate  *(STRICT — default NO-GO)*

> The simplest implementation that satisfies the story's ACs **wins.** Complexity is guilty until
> proven innocent: every abstraction, layer, option, or dependency must trace to a **current AC** —
> never a hypothetical future. "might need," "for flexibility," "extensible," "future-proof," and
> "reusable later" are **red flags, not justifications.** The burden of proof is on complexity.

**Tripwires — if any fires, the plan is `NEEDS-REVISION` until that step is justified against a
current AC or cut:**
- [ ] New abstraction (base class / interface / factory / manager / wrapper) for a **single** use
- [ ] Config option, feature flag, or parameter **no AC requires**
- [ ] Generalizing for N cases when the story is **N=1** (registry / plugin / strategy for one item)
- [ ] New dependency where stdlib or an existing util already covers it
- [ ] Error handling / retries / fallbacks for states that **cannot occur** in this flow
- [ ] A new pattern or layer when an **existing project pattern** already does the job
- [ ] Plan size wildly out of proportion to the ACs (e.g. 1 AC → 200-line plan)
- [ ] Rebuilding something that **already exists** (Phase 1 reinvention check)

For each tripwire that fires, name the **simpler alternative** and the lines/steps it saves. **Default
disposition for an unjustified tripwire is CUT IT.**

---

## Phase 3 — Adversarial Scenarios / Pre-Mortem  *(Full audits; Light only when state is involved)*

Pre-mortem framing: assume the plan shipped and **silently corrupted user state** — what was the
cause? Ask whether the **plan accounts for** each scenario that can actually occur; skip the rest with
a one-line why:

| Scenario | Does the plan handle it? | ✅/❌ |
|----------|--------------------------|-------|
| Happy path / first use | | |
| Rehydration / DB or history load | | |
| Error / timeout path | | |
| Concurrent events (double-click, simultaneous SSE) | | |
| Missing / invalid auth (expired token, unauthenticated route) | | |
| Type-union / exhaustiveness edge (new value missing from a `Record`/switch → `undefined`/`KeyError`) | | |

Then name the failure modes that survived the walk: the forgotten edge case, the unintended
consequence via a shared dependency, the silent killer (corrupts vs. throws), the concurrency trap.

---

## Phase 4 — Verdict

1. **Per-item:** SAFE / NEEDS REVISION / UNSAFE
2. **Three quick gates** (one line each):
   - **Verification strategy present?** Does the plan say how it'll be proven (tests / manual)? No → flag.
   - **Anything irreversible / destructive?** Migrations, DB schema/rules, data deletes → flag + gate.
   - **Any step vague enough the dev will guess?** Ambiguity → the dev fills the gap wrong. Tighten it.
3. **Final Go / No-Go** for proceeding to dev.

If NEEDS-REVISION or UNSAFE → **bake the fix into the plan/story itself** (inline `⚠️ AUDIT FINDING`
in the affected section, plus a short findings table) so the dev agent reads it in context — then
re-run only the phases the change touched.

---

## Phase 5 — Deliver the Findings as a Copy-Paste Block (MANDATORY)

Present the audit's results in the chat **wrapped in a single fenced code block** so Daniel can copy
the whole thing in one action (to paste into a plan, a story, or a dev-agent prompt). The block
carries the verdict, the findings table, the three quick gates, and the final Go / No-Go — the same
content as the Phase 4 summary, not a re-derivation.

- Use a **4-backtick outer fence** (```` ```` ````) so any 3-backtick code blocks inside the summary
  survive intact, and tag it ` ```markdown ` so it renders on paste.
- Keep prose commentary (recommendations, the "want me to bake these in?" offer) **outside** the
  code block so the copyable block stays clean.

---

## Notes
- Guilty until proven innocent — but right-sized. A prompt tweak gets a Light pass; an SSE state
  machine gets the Full pass.
- This is a **pre-dev gate** — it audits the plan/story, never a code diff.
- Optional focus area: $ARGUMENTS
