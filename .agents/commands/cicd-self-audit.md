---
description: Pre-dev plan/story audit — run BEFORE coding. Pressure-tests an implementation_plan.md or story against the codebase and the ACs to catch gaps, over-engineering, and contract breaks before they're built. Auto-invoked by /cicd-dev-story-tests right after the plan is written.
platforms: [opencode, antigravity]
---

# /cicd-self-audit — Pre-Dev Adversarial Audit

Adversarial review of an `implementation_plan.md` or story **before any code is written.** The goal:
catch flaws while fixing them still costs nothing. Assume the plan is wrong somewhere, then try to
prove it. **Default to the leanest pass that covers the real risk** — the Phase 0 right-size gate is
the point; brute-forcing every phase on a trivial plan is the slow, expensive path this exists to avoid.

Target the plan or story just produced in this chat — a **pre-dev gate**, run BEFORE any code. Honor the
Phase 0 right-size gate (a Light plan does not get the Full pass) and the Phase 2 over-engineering gate
(strict — default NO-GO).

> No build commands here — there is no code yet. This audits the *plan*, not a diff. For shipped code,
> use `bmad-code-review`.

---

## Step 0 — Resolve the target project (FIRST — before any phase)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override (remainder = the focus area) → `.agents/active-project.txt` → else **STOP and ask** — never
guess, never operate on the lobby. (When `/cicd-dev-story-tests` auto-invokes this audit, the pointer is
already set — it inherits the same target.) Set `PROJECT_ROOT` and **echo exactly**
`Target: Projects/<name>` before any work; the plan/story under audit, the codebase you trace it against,
and every bare path resolve under `PROJECT_ROOT`, never the lobby.

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

**Graph-first when available.** Decide from the TOOL, never from a doc: call `list_repos` and look for
this project's path. If it is listed and the MCP tools are present, use the code graph for the blast
radius instead of grepping blind: `impact({ repo, target, direction: "upstream", summaryOnly: true })` —
who breaks if this changes; `context({ repo, name })` — callers/callees + flows (full tool tour → the
`gitnexus-impact-analysis` skill). **Never infer "indexed" from a `docs/gitnexus.md` file or an
`AGENTS.md` mention** — the skeleton ships that doc while having no index at all, so prose gives you
both false negatives and false positives. `list_repos` is the only ground truth.

**Always pass `repo:`** — several repos are indexed, and an unscoped call silently answers about the
wrong one.

**Freshness gate — run it BEFORE you trust an answer.** The index is a machine-local cache that does
not travel with git and goes stale on every pull, merge, or branch switch. Compare the repo's
`lastCommit`/`branch` from `list_repos` against the working tree's `git rev-parse HEAD` and current
branch. If they differ, say so in the audit and **treat the graph as a lead, not authority** — re-run
`detect_changes`/re-index if cheap, otherwise cross-check every finding with grep. A stale index
returns a confident blast radius for code that no longer exists, which reads exactly like a clean audit.

**A `0` or LOW verdict is the one you must not believe on sight.** `impact()` misses
attribute-dispatch calls (`self.<attr>.<method>()`), so a genuinely hot symbol can come back 0/LOW —
i.e. "safe to change." Grep-verify every 0/LOW before acting on it. Non-zero results are trustworthy;
it is the *absence* of edges that is unreliable.

**Read the confidence column** — code edges ≈ 1.0; doc/story-file mentions ≈ 0.8. **Caveat:** GitNexus
links repos only via HTTP contracts — it will NOT surface coupling through a shared DB / data store; the
Contract two-sidedness bullet below still needs manual reasoning.

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

## Phase 2 — AI Drift & Over-Engineering Gate  *(STRICT — default NO-GO)*

> The simplest implementation that satisfies the story's ACs **wins.** Complexity is guilty until
> proven innocent: every abstraction, layer, option, or dependency must trace to a **current AC** —
> never a hypothetical future. **AI Drift is the primary enemy here.** "might need," "for flexibility," "extensible," "future-proof," and
> "reusable later" are **red flags, not justifications.** The burden of proof is on complexity. If the plan dictates building five layers of abstraction for a simple `if` statement, **hard-stop the dev flow.**

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
- [ ] Clone-and-tweak — the plan duplicates an existing block/component/test ("copy X and adjust")
  where reusing or extending X would do

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
| AI Hallucinated Edge Case (Did the AI invent a requirement or state that cannot actually exist?) | | |

Then name the failure modes that survived the walk: the forgotten edge case, the unintended
consequence via a shared dependency, the silent killer (corrupts vs. throws), the concurrency trap.

---

## Phase 4 — Verdict

1. **Per-item:** SAFE / NEEDS REVISION / UNSAFE
2. **Persist (ALWAYS — per `artifacts-always-first` §7):** append the audit INTO the plan/story you
   audited as a **`## Self-Audit (<date>)`** section — right-size level, ONE line per phase walked
   (what was checked and cleared), the findings table (`file:line` · severity · failure scenario ·
   disposition), and the canonical **`Audit verdict: GO | NO-GO`** line. Do NOT write a standalone
   `self-audit-stress-test.md` — retired 2026-08-02 (older stories keep theirs as read-only history).
3. **Four quick gates** (one line each):
   - **Verification strategy present?** Does the plan say how it'll be proven (tests / manual)? No → flag.
   - **Anything irreversible / destructive?** Migrations, DB schema/rules, data deletes → flag + gate.
   - **Any step vague enough the dev will guess?** Ambiguity → the dev fills the gap wrong. Tighten it.
   - **Quality fit?** Does the plan anchor the dev to the existing conventions it should match (naming,
     error style, module placement, test patterns) — or leave style to improvisation? A plan silent on
     "where this lives and what it looks like" invites slop.
4. **Final Go / No-Go** for proceeding to dev.

If NEEDS-REVISION or UNSAFE → **bake the fix into the plan/story itself** (inline `⚠️ AUDIT FINDING`
in the affected section, plus the findings table in `## Self-Audit`) so the dev agent reads it in
context — then re-run only the phases the change touched.

---

## Notes
- Guilty until proven innocent — but right-sized. A prompt tweak gets a Light pass; an SSE state
  machine gets the Full pass.
- This is a **pre-dev gate** — it audits the plan/story, never a code diff.
- Optional focus area: $ARGUMENTS
