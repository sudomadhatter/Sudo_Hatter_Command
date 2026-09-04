---
IsArtifact: true
ArtifactMetadata:
  title: SCC-40 — /sudo-quick-dev on the real quick-dev engine
  type: walkthrough
  date: 2026-08-08
---

# SCC-40 — `/sudo-quick-dev` on the real quick-dev engine

**Ticket:** SCC-40 (epic SCC-33) · **Plan:** [implementation_plan.md](implementation_plan.md)
**Lobby:** `chore/SCC-40-quick-dev-artifact-reconcile` @ `9ba872e` (pushed)
**AviationChat:** `chore/AVCH-48-bmad-override-propagation` @ `cc8411f7` (pushed) — ticket **AVCH-48**

## Task Checklist

- [x] Diagnose the contradictions — **7 found, 2 of them live runtime injections**
  - The ticket read as a docs mismatch. It wasn't: `bmad-dev-story.toml` injects
    *"HALT … until the user says 'approved'"* at **activation**, and `/sudo-quick-dev` Step 2 invoked
    `bmad-dev-story`. No wording in a command can outrank an activation-time injection — which is why
    rewording alone would have fixed nothing.
- [x] Find the root cause — the fast lane was built on the **full-lane skills**
  - A purpose-built `bmad-quick-dev` skill existed and was **never called**. All seven conflicts were
    symptoms of that one decision.
- [x] Rewrite the command onto `bmad-quick-dev` (one-shot route)
  - Added an **AC baseline before the code**: the one-shot route writes its spec *retroactively*, so
    there was nothing to audit the diff against. That was the wrong trade for an enterprise standard.
  - Added a **mandatory tiered review gate** after the work. Today's lane runs *no* adversarial review
    at all, so this is stricter than what it replaced, not looser.
  - Eject is now the skill's own routing verdict ("this needs plan-code-review") rather than a
    file-count proxy; protected surfaces stay a hard stop because that one is about risk, not size.
- [x] Carve the exemption into the ONE exemption list
  - `artifacts-always-first` § When to Skip case 4; removed the inline naming from `000-PLAN-FIRST-GATE`.
    Two copies of a gate's scope drift apart and each reads authoritative — that was conflict #1.
- [x] Correct the BMAD override seam (C7)
  - `_bmad/custom/<skill>.toml` is canonical and update-safe. `.agents/bmad/` is **not** mirrored —
    `/sync-agents` excludes `bmad/` entirely — yet its INDEX claimed it was. That false line is why two
    team overrides were hand-edited where nothing reads them while the live copies stayed stale.
    Deleted the orphans, fixed the claim.
- [x] Propagate to AviationChat by hand
  - ⚠️ **AGY's tomls are deliberately divergent, not stale copies** — they *inline* the gate instead of
    referencing a `{project-root}` path (project-law hard-dependency exception: BMAD loads the toml from
    inside the project, where no center path resolves across both machines and a worktree). Blindly
    copying the lobby's would have destroyed that. Surgical edits instead; the inlining and the
    `PROJECT LAW` fact are preserved.
- [x] Catch the commit-hook breakage before it shipped
  - `bmad-quick-dev` commits with *"a conventional message derived from the spec title"* — the armed
    `commit-msg` hook refuses any subject without the repo's Jira key. Encoded the commit contract in
    `persistent_facts` for both repos. **Still unproven end-to-end — see Your Actions.**
- [x] Gates green, both repos committed and pushed

## Evidence

| AC (from the ticket) | Where it's satisfied |
|---|---|
| Audit `/quick-dev` and the artifact rules | 7 conflicts enumerated in [implementation_plan.md](implementation_plan.md) |
| Identify the conflicts | C1–C7, each with file:line provenance |
| Reconcile so workflow and rules agree | Engine swap removes C1–C5 at the root; C6/C7 fixed directly |

```
python3 .agents/scripts/tests/run_all.py     → 6/6 files passed
python3 .agents/scripts/check_maps.py        → clean (exit 0)
tomllib parse, all 4 tomls                   → OK
resolve_customization.py --key workflow      → OK, lobby AND AviationChat (overrides merge)
```
SHA: `9ba872e636e8cd828199a2aa6a820be1ce21b8ce` (lobby) · `cc8411f7` (AviationChat)

## Suite Ledger

| Scope | Command | Result | Why this run |
|---|---|---|---|
| Lobby gate | `run_all.py` | 6/6 files passed | The repo gate for any `.agents/` change |
| Maps/indexes | `check_maps.py` | clean | Rules + commands + a new artifact folder moved |
| BMAD overrides | `tomllib` + `resolve_customization.py` | OK ×4 | A malformed toml fails silently at activation |

## Code Review (2026-08-08)

**Verdict: WAIVED @ 9ba872e** — no adversarial code review ran. This change is documentation, rules, and
BMAD override config; there is no executable diff for the machine floor (ruff/eslint/pyrefly/tsc) to act
on. Verification was the gate suite, the map lint, and a real parse-and-resolve of every toml through
BMAD's own resolver on both repos.

Two findings caught during the work and fixed in place, both recorded above: AGY's tomls being
deliberately divergent (would have been destroyed by a copy), and the commit-hook rejection of the
skill's native commit message.

## Your Actions

1. **⚠️ Prove the commit contract on a real run.** The one thing not yet verified end-to-end: run
   `/sudo-quick-dev` on a trivial docs change in AviationChat and confirm the skill's commit passes the
   armed `commit-msg` hook, the review gate fires, and the thin walkthrough lands in `_artifacts/`.
   Risk #1 in the plan; it is encoded but not observed.
2. **Merge decisions are yours** — both branches are pushed, neither is merged:
   - Lobby `chore/SCC-40-quick-dev-artifact-reconcile` → `main`
   - AviationChat `chore/AVCH-48-bmad-override-propagation` → `main` (**AGY main is production — a push
     there is a deploy**; this is toml-only, but it is still your call)
3. **AVCH-48 placement.** Minted bare per the toolkit/chore seam. `AVCH-23` (Thin toolkit) is a plausible
   parent — parenting and sprint placement are yours.
4. **NEXgen-VR-Director** carries a `bmad-quick-dev.toml` too and was left untouched per your call. It
   would need the same hand-applied edit if it is ever used again.
5. **SCC-40 is still `In Progress`** on the board — I did not transition it; that's the operator's move
   outside the two automated seams.
