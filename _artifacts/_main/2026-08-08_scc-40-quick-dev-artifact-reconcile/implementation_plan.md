---
IsArtifact: true
ArtifactMetadata:
  title: SCC-40 — put /sudo-quick-dev on the real quick-dev engine
  type: implementation_plan
  date: 2026-08-08
---

# SCC-40 — put `/sudo-quick-dev` on the real quick-dev engine

**Ticket:** SCC-40 (epic SCC-33) · **Branch:** `chore/SCC-40-quick-dev-artifact-reconcile` off `main`

## The ruling (yours, 2026-08-08)

1. **Swap the engine** — `/sudo-quick-dev` drives `bmad-quick-dev`, not `bmad-create-story` + `bmad-dev-story`.
2. **Keep the name and the standard** — still `/sudo-quick-dev`; **accuracy over speed**. What we drop is the
   full development pipeline, not the rigour.
3. **A review still runs after the work** — explicit, named, non-skippable.
4. Record shape: the spec is the working doc; a **thin** `walkthrough.md` in `_artifacts/` links it.

## Why this dissolves the ticket rather than patching it

All seven conflicts were symptoms of one decision: the fast lane was built on full-lane skills with their
safety rails argued away in prose. `bmad-dev-story.toml` injects **"HALT … until the user says 'approved'"**
at activation; no wording in a command can outrank an activation-time injection. Stop invoking that skill
and C1–C5 stop existing. **The risky edit from my first plan is gone** — `bmad-dev-story.toml` never gets
touched, and its prepend stays fully armed for the full lane.

## The accuracy problem I had to fix

`bmad-quick-dev`'s one-shot route is fast partly because it writes the spec **retroactively** — implement
first, generate the spec trace after. That leaves **no frozen acceptance criteria to audit the diff
against**, which is the wrong trade for an enterprise standard. So the flow below adds a cheap AC baseline
*before* implementation, and holds the review to it.

Worth stating plainly: **today's `/sudo-quick-dev` runs no adversarial review at all** — it explicitly
bypasses it. This is stricter than the current fast lane, not looser.

## The new flow

```
/sudo-quick-dev <arg>
 Step 0    resolve target project                      (unchanged — already correct)
 Step 0.5  worktree (epic story) OR chore/<KEY> branch (unchanged — already correct)
 Step 1    → bmad-quick-dev step-01: clarify intent + ROUTE
            ⊕ capture an explicit AC list before leaving this step (the accuracy baseline)
 Step 1.5  ⛔ EJECT if step-01 routes to plan-code-review, or a protected surface is
            touched (auth/tenancy · payments · PII · DB schema or security rules ·
            cross-boundary API/SSE contract) → hand to /sudo-write-story-tests ①
 Step 2    ONE-SHOT implement
 Step 3    ⭐ REVIEW GATE — explicit, named, never skipped. Tiered by lane:
            every lane   · blind adversarial reviewer, NO conversation context
                           (independent eyes; kills anchoring bias)
            code         · acceptance auditor vs the Step 1 ACs
                         · /clean-code-audit machine floor (ruff/eslint/pyrefly/tsc — can FAIL)
                         · scoped tests for the touched module
            docs/config  · link + anchor check · SOP-currency check   (no lint floor — nothing to lint)
            findings → patch / defer / reject. Anything bigger than a trivial patch → HALT.
 Step 4    spec trace + thin walkthrough.md (carrying the Verdict line); STOP for human review
```

**The eject is now principled.** Instead of counting files (~3 / ~150 lines — a proxy), the skill's own
routing decides: *it* judges blast radius, and "this needs plan-code-review" IS the eject signal. The
protected-surface list stays as a hard override, because that one is about risk, not size.

**This finally gives you the non-technical lane.** Today Step 2b runs the touched module's test file and
Step 3 runs ruff/eslint/pyrefly/tsc — none of which apply to a markdown diff. Step 3 now forks by lane.

## What keeps the standard, once the pipeline is gone

| Guard | Kept? |
|---|---|
| Independent adversarial review (no conversation context) | **Added** — today's lane has none |
| Acceptance criteria, fixed before the code | **Added** — one-shot alone has none |
| Objective machine floor that can FAIL | Kept (`/clean-code-audit`) |
| Scoped tests on touched code | Kept |
| Protected-surface hard stop | Kept |
| Human review as the closing gate | Kept — never closes out, never flips to `done` |
| ATDD red phase · full suite · 3-reviewer panel · revert-and-re-derive loops | **Dropped** — this is the pipeline you don't want |

## Changes by file

### 1. [.agents/commands/sudo-quick-dev.md](.agents/commands/sudo-quick-dev.md)
Rewrite Steps 1–4 to the flow above; Steps 0 and 0.5 stay. Delete the "Bypass Planning Gate" and
"Skip ATDD" bullets — with the new engine there is nothing to bypass.

### 2. `_bmad/custom/bmad-quick-dev.toml` — **lobby + AGY_AVIATIONCHAT**
The update-safe seam you remembered: BMAD updates replace the skill directory and never touch
`_bmad/custom/`. Only the four exposed fields (`customize.toml` is stamped *"DO NOT EDIT"*):
- **`activation_steps_prepend`** — worktree/chore precondition · the AC-baseline requirement · the eject rule.
- **`persistent_facts`** — ⚠️ the commit contract (Jira key leads every subject; explicit paths only, never
  `git add -A`; never push `main`), the protected-surface list, artifact placement.
- **`on_complete`** — run the review gate if it has not run, write the thin `walkthrough.md` into
  `_artifacts/` with the Verdict line, post clickable links, STOP for human review. Never close out.

`bmad/` is **excluded from `/sync-agents` entirely**, so AGY's copy is applied by hand — per-repo by design.

### 3. Rules
- [artifacts-always-first.md](.agents/rules/artifacts-always-first.md) § When to Skip — 4th case naming
  `/sudo-quick-dev`, conditioned on its guards, stating a fired eject re-arms the gate; plus the
  spec + thin-walkthrough shape and where the Verdict line lives.
- [000-PLAN-FIRST-GATE.md](.agents/rules/000-PLAN-FIRST-GATE.md) line 8 — drop `quick-dev` from the
  override list; that file already defers every exemption to the single list (line 66).

### 4. C7 — correctly diagnosed
`_bmad/custom/` is canonical and our overrides are already in the right place. The newer toml text was
hand-edited into **`.agents/bmad/`**, a mirror whose own INDEX says *"Regenerated on BMAD update — never
hand-edit."* The live copies never got it.
- Bring `_bmad/custom/bmad-dev-story.toml` (lobby + AGY) to the current artifact shape — it still carries
  the pre-08-02 narrative shape and the "exact git commit command" `git-policy` retired. **Its plan-first
  prepend stays armed.**
- Fix [.agents/bmad/INDEX.md](.agents/bmad/INDEX.md): it claims *"Mirrored to projects via `/sync-agents`"*,
  which [sync-agents.md:31](.agents/commands/sync-agents.md#L31) flatly contradicts.
- **Delete `.agents/bmad/custom/bmad-*.toml`** — nothing syncs them; they already sent one edit into a
  display case instead of the engine.

### 5. [sudo_workflows_testing.md](_my_resources/_quick_reference/sudo_workflows_testing.md)
Mandatory — usage-surface change; the armed `sop-currency` gate rejects the commit without it.

### 6. Propagation
[.agents/workflows/sudo-quick-dev.md](.agents/workflows/sudo-quick-dev.md), then `/sync-agents` →
`.claude/`, `.opencode/`, Codex + Antigravity caches. The three current copies are byte-identical.

## Risks I am carrying

1. **⚠️ The commit hook will reject the skill's commit.** `bmad-quick-dev` commits with *"a conventional
   message derived from the spec title"*; our armed `commit-msg` hook refuses any subject without a Jira
   key. Fixed via `persistent_facts` — **proven by a live run, not assumed.**
2. **`git add` discipline.** The skill says *"if the tree is dirty, create a local commit"*, which reads like
   `git add -A`. Pinned in `persistent_facts`; verified in the live run.
3. **The review gate lives in two places** (the command's Step 3 and the toml's `on_complete` backstop). Two
   homes drift — the toml entry is deliberately a *backstop only*: it fires the gate if Step 3 did not.

## Verification

```bash
python3 .agents/scripts/tests/run_all.py     # the lobby gate (no E2E suite exists here)
python3 .agents/scripts/check_maps.py        # map/index drift
```
Then the one that matters: **a live `/sudo-quick-dev` run on a trivial docs change in AGY** — proving the
commit passes the armed hook, the review gate actually fires, the spec lands, the thin walkthrough lands in
`_artifacts/` with its Verdict line, and nothing was staged with `git add -A`.

## Out of scope

SCC-41 (autopilot worktrees) · SCC-42 (`/self-assess` + GitNexus) — separate tickets, separate branches.
Scope is **lobby + AGY_AVIATIONCHAT**; `NEXgen-VR-Director` also carries a `bmad-quick-dev.toml` and I will
report what it needs. `BRKN_Tattoos` and `Fresh_Workspace_BMAD` are deliberately frozen/retired.
