# SCC-69 — Walkthrough: the first real `/memory-audit`, and what it proved

**Date:** 2026-08-09 · **Repo:** Sudo_Hatter_Command (lobby) · **Branch:**
`chore/SCC-69-memory-audit-first-pass` · **Lane:** LOCAL

---

## What this was

The first live run of the command SCC-68 shipped, against the real store sitting at **99% of its
20 KB index cap**. It ran end to end: floor → widen candidates → **ground-truth against the live
repo** → propose → STOP for per-item approval → apply → verify harness link → re-run.

## Result

| | |
|---|---|
| Index | 20,374 → **19,792 bytes** |
| Cap | 20 KB → **25 KB** (operator ruling, see below) |
| Utilisation | 99% → **77 %** — trigger block cleared |
| Memories | 151 → **144** |
| Retired | 4 · **Merged** 2 · **Repaired** 12 links · **Corrected** 3 false claims |

## ⭐ What ground-truthing caught that a size check never would

**Two live findings were buried in memories about unrelated subjects** and would have been deleted
with them:

- AGY `backend/routers/incident.py` line 1 still claims *"Story 16.2 primary 'routines' delivery
  lane"* while the as-built primary is the agent lane. **Re-verified true**, then rescued into
  `incident-pipeline-16-2-operations` — it had been filed under a memory about *command renames*,
  where nobody would ever look for it.
- The credential-mutating orphan-script sweep. Re-checked on disk: `update_school_admin.py` and
  `fix_sudo_pass.py` are gone, `backend/add_secret.py` is still tracked. Rescued into the wedged-
  backend memory as a status line rather than an open-ended "re-sweep".

**Three memories were actively lying**, which is worse than being stale:

- `autopilot-engine-is-project-local` named **2** engines with line counts for both. Reality:
  **four** (`AGY` 1500 · `NEXgen-VR-Director` 1500 · `sudo-project-skeleton` 1500 ·
  `BRKN_Tattoos` 1275), and `Fresh_Workspace_BMAD` carries **none**.
- `maintained-projects-allowlist` still called Fresh "the golden skeleton, so it stays maintained".
- `thin-projects-center-owns-workflow-law` — my own error, see below.

**One dangler had been broken since SCC-51**: `story-artifacts-two-doc-close` pointed at
`artifact-budgets-are-scoped-not-universal`, deleted in `61db18d` when the byte caps were removed.
Seven more `[[wikilinks]]` pointed at *rules and commands*, which the memory→memory convention does
not cover — permanent gate noise, now plain paths.

## A mistake I made, and the fix

I checked for a `Fresh` directory at the repo root and one level up, concluded it was gone, and
wrote "cut new projects from the lobby master" into the replacement text — **copying the retired
memory's own wording without verifying it**. Both halves were wrong: Fresh is at
`Projects/Fresh_Workspace_BMAD` (still present, just no longer the template), and `/new-project`
clones `sudomadhatter/sudo-project-skeleton`. Corrected in place. The retirement itself still
stands; the *reason* I gave for it did not.

**The gate also caught my own incomplete retirement mid-pass** — two `[[links]]` to files I had
just deleted. The trigger doing its job on its author, one commit after shipping it.

## The finding that changed the cap

After the tranche, I hunted for a second one and **could not defend it**. The last two index edits
I could justify freed **2 bytes**. That is the evidence: **there was no 2 KB of junk in the store.**
145 ground-truthed memories at ~135 bytes of index each simply *is* 20 KB, and clearing the 90%
band by pruning would have meant deleting true things — the exact failure the audit exists to
prevent.

So the constraint, not the content, was wrong. The 20 KB figure was inherited from the
**active-context** budget by analogy and never measured against a real memory store.

**Operator ruling: 20 KB → 25 KB.** Trigger stays at 90% (23,040 bytes), leaving ~10 memories of
runway before the hard fail.

**The "never raise the cap" rule was narrowed, not removed** — it now reads *never raise it
**yourself***. Both the command and the gate docstring record that the cap moved exactly once, on
the operator's word, **after an audit produced the evidence**. An agent reports the finding and
lets them decide; that is the whole shape of this system.

## Also closed by ruling

`real-gemini-key-leaks-into-pytest-env` — the rotation it was holding open is done. Zero inbound
links, clean retire. Its reusable half was compressed to a one-line lesson on the row per the write
law: **`setdefault` is the wrong idiom for seeding a secret** — it defers to an exported real key;
assign unconditionally in every conftest. That cost 53 index bytes and removed a 3.4 KB body, which
is the trade the write law asks for.

## Verification

`run_all` **11/11 exit 0** · memory gate **16/16**, trigger block **gone** ·
`workflow_lint --toolkit-only` **0 errors** (2 known pre-existing warnings) · `sop_currency` exit 0 ·
doors re-synced on all four platforms · harness link resolves into `_artifacts/_memory/`.

## Follow-ons

- **The AGY split is still on the table and unresolved.** The lobby index spends ~7 KB on
  AGY-specific memories for a project with its own repo. The 25 KB cap buys room; it does not
  answer the question.
- `/sync-agents` still owed on the PC — caches are per-machine, and the cap number now lives in the
  generated doors.
