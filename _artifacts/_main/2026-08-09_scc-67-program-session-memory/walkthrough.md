---
IsArtifact: true
ArtifactMetadata:
  title: SCC-67 agnostic-system program session memory — walkthrough
  type: walkthrough
  date: 2026-08-09
---

# SCC-67 — the program's lessons, written where every platform now reads them

Closing artifact for the memory written during SCC-64 / SCC-65 / SCC-66. It gets its own key
because the armed commit-msg hook requires one on every commit, and a bare commit on `main` is
barred by `git-policy.md` G4 — the memory is legitimate session output, so it rides a lane like
anything else.

## Task Checklist

- [x] **`one-door-per-platform-per-command`** — the SCC-66 door model, why it is *forced* (Codex
      has no repo-defined `/name`; Claude publishes a command per `SKILL.md`), the hand-authored
      override, and the per-machine/new-chat caveats.
- [x] **`closeout-target-is-a-machine-contract`** — SCC-64's `--expect-key` / `task.yaml` /
      `--toolkit-only`, and why the scripts changed after SCC-61 said they shouldn't (the missing
      piece was an intent *input*, not logic). Linked from the existing
      `preflight-resolves-repo-from-cwd` line so the old memory now points at its own resolution.
- [x] **`memory-store-is-read-by-every-platform`** — SCC-65 routing, the read-only law, the gate,
      and propose-only compaction.
- [x] **`powershell-comma-array-wrapper-unrolls-once`** — the `,@()` capture trap.
- [x] **`echo-truncates-at-backslash-c`** — filed under the *"a green or a red can lie"* family.
- [x] Five `MEMORY.md` index lines, one per memory.

## Evidence

| Gate | Result |
|---|---|
| `tests/test_memory_store.py` | **8/8**, exit 0 |
| `MEMORY.md` size | **20,207 / 20,480 bytes** — 273 to spare |
| `tests/run_all.py` | 11/11 files passed, exit 0 |
| `task_preflight.py --expect-key SCC-67` | clear (this lane's own dogfood) |

## Decisions

- **The index is now one memory away from its cap, and that is left as-is.** The documented answer
  is a `/update-maps-indexes` **Step 3.9** compaction proposal — visible `CLOSED`/`RETIRED` entries
  are the candidates — not raising the cap. Raising it the first time it binds would make the
  budget decorative.
- **Two of the five are pure trap-memories** (`echo`, PowerShell `,@()`). They earn their place
  because both produced a *confidently wrong reading of a healthy system* — the same family as
  `piping-a-gate-hides-its-exit-code`, which is exactly the failure mode this program exists to
  remove.

## Your Actions

- None. The next agent that trips the 20 KB cap will bring you a compaction proposal to approve.
