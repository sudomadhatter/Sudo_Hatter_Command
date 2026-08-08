---
IsArtifact: true
ArtifactMetadata:
  title: SCC-40 — /sudo-quick-dev on the real quick-dev engine
  type: implementation_plan
  date: 2026-08-08
---

# SCC-40 — put `/sudo-quick-dev` on the real quick-dev engine

**Ticket:** SCC-40 (epic SCC-33) · **Branch:** `chore/SCC-40-quick-dev-artifact-reconcile`
**Landed:** lobby `7f500e0` · AviationChat `cc8411f7` (AVCH-48) — both pushed, neither merged.
**Record:** [walkthrough.md](walkthrough.md) carries the per-file detail and evidence; the diff is the
other half. *(Compressed in place when the audit landed — 8 KB budget.)*

## The ruling (operator, 2026-08-08)

Swap the engine to `bmad-quick-dev`; keep the name and the standard (**accuracy over speed** — drop the
pipeline, not the rigour); a review still runs after the work, explicit and non-skippable; record shape
is spec + a **thin** `walkthrough.md` linking it.

## Why this dissolved the ticket rather than patching it

All seven conflicts were symptoms of one decision: the fast lane was built on the full-lane skills with
their rails argued away in prose. `bmad-dev-story.toml` injects *"HALT … until the user says 'approved'"*
at **activation** — no command wording outranks that. Stop invoking that skill and C1–C5 stop existing.
It was therefore never touched; its gate stays armed for the full lane.

**The accuracy fix:** the one-shot route writes its spec *retroactively*, leaving nothing to audit the
diff against. Step 1 now fixes acceptance criteria first. And today's lane runs **no** adversarial review
at all — so the new gate is stricter than what it replaced, not looser.

## The flow

```
Step 0/0.5  resolve target · worktree (epic) or chore branch      (unchanged — already correct)
Step 1      bmad-quick-dev step-01: clarify + ROUTE  ⊕ fix an explicit AC list
Step 1.5    ⛔ EJECT → full lane, if: routed to plan-code-review · protected surface
            (auth/tenancy · payments · PII · schema/security rules · cross-boundary API/SSE)
            · intent won't reduce to ACs · a finding bigger than a trivial patch
Step 2      ONE-SHOT implement
Step 3      ⭐ REVIEW GATE (mandatory, tiered)
              every lane · independent adversarial reviewer, NO conversation context
              code       · acceptance audit vs Step 1 ACs + clean-code machine floor + scoped tests
              docs/config· link + anchor check + SOP-currency check (no lint floor to run)
Step 4      spec trace + thin walkthrough (Verdict line); STOP for human review
```

Eject is the skill's own routing verdict, not a file-count proxy; protected surfaces stay a hard stop
because that is risk, not size.

## What changed

Command (+3 copies) · `artifacts-always-first` § When to Skip case 4 · `000-PLAN-FIRST-GATE` carve-out ·
`bmad-quick-dev.toml` (lobby + AGY: gate exemptions, **commit contract**, protected surfaces, artifact
shape, review backstop) · `bmad-dev-story.toml` (artifact shape only) · `.agents/bmad/INDEX.md`
false-mirror claim + two orphan tomls deleted · SOP quick-reference.

**C7:** `_bmad/custom/` is canonical and update-safe. `.agents/bmad/` is **not** mirrored
(`/sync-agents` excludes `bmad/`), yet its INDEX claimed it was — which is why two overrides were
hand-edited where nothing reads them while the live copies stayed stale.

**AGY's tomls are deliberately divergent** — they *inline* the gate rather than reference a
`{project-root}` path (project-law hard-dependency exception). Copying the lobby's over them would have
destroyed that; surgical edits instead.

## Verification

`run_all.py` 6/6 · `check_maps.py` clean · all four tomls parse **and resolve** through
`resolve_customization.py`, both repos. Open: a live run proving the skill's commit survives the armed
`commit-msg` hook.

**Out of scope:** SCC-41 · SCC-42. Scope was lobby + AGY; NEXgen carries a `bmad-quick-dev.toml` and was
left untouched per operator call; BRKN and Fresh are frozen/retired.

---

## Self-Audit (2026-08-08)

**Level: Full** — the change edits two PROTOCOL rules loaded before every file write, plus BMAD overrides
injected at every skill activation in two repos. Not a contained change.

> Method note: `/sudo-self-audit` is a **pre-dev** gate targeting a child project — it audits a plan,
> "never a code diff." This work is landed and lobby-centric, so its phases ran against the real diff.
> Deliberate deviation.

- **Phase 0 — scope + AC trace.** All three ticket ACs map to shipped changes; no orphan steps.
- **Phase 1 — blast radius.** Traced every changed file to its readers. Verified `bmad-quick-dev` **and**
  `bmad-dev-story` are installed in all 7 projects, so the swap strands nobody; nothing resolves
  `.agents/bmad/` at runtime (`check_maps.py:584` is an ignore list) and `new-project.ps1` is thin-model,
  so the deletion is inert.
- **Phase 2 — over-engineering.** One tripwire: the review gate is stated twice (Step 3 + toml
  `on_complete`). Kept as an explicit backstop — but F8 is the better fix.
- **Phase 3 — pre-mortem.** Walked half-landed state, wrong-caller gate reads, missing directories,
  platform resolution, silent gate-skipping. Four survived.

| # | Finding | Sev | Disposition |
|---|---|---|---|
| F1 | **Half-landed state re-creates the original bug.** The lobby and AGY changes sit on two unmerged chore branches. If the lobby lands and AVCH-48 doesn't, AviationChat gets the new command against the OLD toml — whose prepend still says "HALT. Wait for 'approved'" unconditionally. C2 reborn, split across repos where it is far harder to see; the commit contract would also be absent, upgrading plan-risk #1 from possible to certain. **Empirically live:** both checkouts have since moved to branches cut from main (`chore/SCC-49-jira-dev-feed`, `epic/AVCH-49-adk-2x-runtime`), so neither change is in force anywhere right now. | **HIGH** | **Operator** — land both or neither. Safe on origin: `7f500e0`, `cc8411f7`. |
| F2 | `000-PLAN-FIRST-GATE.md:54` still listed `bmad-quick-dev` as "subordinate to this gate" with a STOP-for-approved order, two lines under the carve-out. Both readings true (bare vs. via `/sudo-quick-dev`) — but ambiguity is the exact failure class this ticket kills. | MED | **FIXED** — caller-decides note. |
| F3 | `commands/INDEX.md:31` said quick-dev "close[s] out to log it" (never true — the command has always forbidden close-out) and "bypasses … code reviews" (now flatly false). | MED | **FIXED** — rewritten. |
| F4 | `reproduce-before-you-fix.md:144` cited "Step 2" for the pinning regression test; it moved to Step 3's review gate. | LOW | **FIXED** |
| F5 | `_artifacts/quick_fixes/` does not exist in the lobby, yet command and toml both send agents to read its `INDEX.md`. AGY has it. | LOW | **FIXED** — create-on-first-use. |
| F6 | Command declares `platforms: [opencode, antigravity, claude, codex]`, but `opencode.json` sets `skills.paths = [".agents/skills"]`, which holds **zero** `bmad-*` skills — the engine is unresolvable there. **Pre-existing:** the old command had the identical problem. Neither caused nor fixed by SCC-40. | MED | **Flagged** — own ticket. |
| F7 | The story lane auto-advances the story to `review` via the skill's `sync-sprint-status`; correct per `story-status-flip-contract` but undocumented. | INFO | **FIXED** — documented. |
| F8 | **Nothing mechanically enforces the review gate.** Step 3 is prose in a command; `on_complete` is prose in a toml. An agent skipping both still writes a walkthrough carrying a `Verdict:` line it never earned — and that line is what `/sudo-update-sprint-memory` reads before flipping a story. Contrast `run_all.py` and the commit hooks, which are real gates. `.agents/scripts/gate_receipt.py` is precedent for making this checkable. | MED | **Accepted risk** — follow-up ticket. |

**Four gates:** verification present (suite + map lint + toml resolve; live run open) · nothing
irreversible — the only deletion is two git-tracked orphans · no step vague enough to guess after
F2–F5 · quality fit holds.

**Audit verdict: GO** — with F1 as a hard landing-order condition and F8 recorded as accepted risk.
