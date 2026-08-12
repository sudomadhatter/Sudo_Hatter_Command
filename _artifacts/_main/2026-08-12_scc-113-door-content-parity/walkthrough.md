---
IsArtifact: true
ArtifactMetadata:
  title: SCC-113 (follow-on) — door CONTENT parity
  type: walkthrough
  date: 2026-08-12
---

# SCC-113 follow-on — the door gate could not see a stale door

**Branch** `chore/SCC-113-door-content-parity` · **Lane** LOCAL · **HEAD** `fe46b4a`
**Plan** [implementation_plan.md](implementation_plan.md) · **Ticket** SCC-113 (reopened)

---

## Task Checklist

- [x] **Reopen SCC-113** `Done → In Progress` — folded in on the operator's ruling rather than
      minted separately. Required, not cosmetic: `jira_feed.py start`, shipped *by* SCC-113,
      refuses a `Done` key, so the follow-on would have been blocked by its own hook.
- [x] **Content-parity check** in `test_command_surfaces.py`.
- [x] **Launcher exemption earned**, not announced.
      - ⚠ Shipped announced-only first. The review defeated it three ways. See Review, A-2′.
- [x] **Regression control on the real historical bytes** (`ea8fe97^`), in the tree.
- [x] **Correct the `workflow_lint` misattribution** I shipped in the parent lane.
- [x] Absorbed SCC-110 mid-lane and re-read the merged SOP table.
- [x] Review gate — clean-room pass, CONCERNS, all findings closed.
- [x] **Both recorded gaps closed** on the operator's ruling — opencode ghost check + placement on
      both mirror surfaces. Addendum 1.
- [x] **The close-out's own preflight blocked, and the block was a gate defect** — one ticket may
      have two lanes. Fixed and mutation-proven. Addendum 2.

---

## Evidence

**All gates run bare at `97dc770`.**

| # | Acceptance item | Assertion | RED → GREEN |
|---|---|---|---|
| 1 | A full mirror differing from its brain is an ERROR | "every mirror door still says what its brain says" | **RED: existing gate 13/13 green on a genuinely stale door** → GREEN |
| 2 | A launcher is exempt only while current | 8 `door-parity CONTROL` cases | RED (3 review attacks passed) → GREEN |
| 3 | Fires on the **real** pre-`ea8fe97` bytes | "REGRESSION CONTROL fires on the REAL pre-ea8fe97 bytes" | GREEN, in-tree |
| 4 | No surface claims `workflow_lint` checks doors | SOP row + struck-through walkthrough items | GREEN |
| 5 | 0 offenders, non-empty sweep | "examined a real number of doors" — **84** | GREEN |

### The RED — the blindness, reproduced with real bytes

```
$ git show ea8fe97^:.opencode/commands/cicd-push-e2e.md > .opencode/commands/cicd-push-e2e.md
   8464 bytes vs brain 9343 · mint-push-token references: 0

$ python3 .agents/scripts/tests/test_command_surfaces.py
-- 13/13 passed --      ← the gate, on a door that had lost the entire push-token step
```

### The GREEN, at `97dc770`

```
run_all.py                        16/16 files passed        exit 0
  └─ command surface contracts    26/26 passed              (was 13/13)
workflow_lint.py --toolkit-only   0 error(s), 0 warning(s)  exit 0
sop_currency.py                                             exit 0
py_compile                                                  exit 0
```

### ⭐ Mutation battery — every attack the review verified, re-run against the fix

Six attacks on a throwaway copy. Baseline **0 FAILs**; every attack now caught.

| Attack | FAILs (0 = it beat us) |
|---|---|
| 0. baseline | **0** |
| 1. brain description moved on, launcher not re-synced | **2** |
| 2. launcher repointed, old path left in a comment | **1** |
| 3. opencode mirror replaced by a launcher stub | **1** |
| 4. the REAL pre-`ea8fe97` stale door bytes | **1** |
| 5. decoy `$excluded` earlier in the file + a real ghost | **1** |
| 6. delete a brain that has a hand-owned workflow | **2** |

### Live proof of the parent lane's own fix

This branch is the **second** on key SCC-113. It got its own marker
(`jira-started-chore-SCC-113-door-content-parity`), fired, found the ticket already
`In Progress`, and no-op'd silently — the exact case the branch-named marker was changed to
support, observed rather than asserted.

---

## Code Review (2026-08-12)

```
Verdict: PASS @ fe46b4a
```

One clean-room pass (`bmad-review-adversarial-general`, subagent, no context, Opus), returning
**CONCERNS** with one HIGH. Everything it claimed, it verified by running. All findings closed.

⚠ **What that verdict does and does not cover.** The clean-room pass ran at `97dc770`. The two addenda
below (`5fef0a8`, `fe46b4a`) landed **after** it, on the operator's ruling, and have **not** had an
independent pass of their own — they are covered by mutation batteries against real bytes (five
attacks on the door gate, one on the preflight), not by a second reviewer. Stated here rather than left for someone to infer from the shas. Three consecutive
rounds in this lane shipped guards that failed **open** and were caught only by a clean-room pass, so
this is a real gap and not a formality; say the word and it runs.

| # | Sev | Finding | Closed by |
|---|---|---|---|
| **A-2′** | **HIGH** | **The exemption was announced, not earned** — three substrings *anywhere* in the file. Defeated three ways, all verified green: change a **brain's** description and never re-sync (the forgotten-sync shape this check exists for); repoint a launcher leaving the old path in a comment (`comment-literals-invert-source-grep-tests`, reproduced against my own guard); a 3-line hostile body | anchored pointer + `description` equality + marker + `END TO END`, shared with the skill check |
| **A-8** | MED | Exemption offered to `.opencode/commands`, where the engine **never** emits a launcher. A 9 KB command replaced by a 9-line pointer passed | exemption is per-surface |
| **A-6** | MED | `$excluded` regex **unscoped** — a decoy array earlier in the file silenced the **ghost** check on a real orphan. Overbroad fails **OPEN** | anchored to the owning function; parsed names must exist |
| **A-7** | MED | Reusing `hand_owned` for the ghost check loosened it on the two names that *do* have brains — the deleted-brain case | ghost exemption = sourceless `INDEX.md` only, + a new orphan check |
| **A-9** | LOW | `2 <= len(hand_owned) <= 8` encoded today's count; a legitimate future state fails with "not guessed" when the list read fine | identity check |
| **AC 3** | — | Claimed *"the one that earns the lane"*, verified **by hand, recorded nowhere** | shipped as a test, real bytes + loud fallback |
| **plan** | — | Blast radius said `sync-agents.ps1` "not written" while the diff hard-couples to its PowerShell quoting; A-3 said "three caches" (it is two, and no skill doors) | corrected in the plan's post-review addenda |

**Found, deliberately NOT fixed.** ~~`.opencode/commands` has no ghost check, and neither mirror
surface asserts a door belongs on the platform its `platforms:` claims — enforced for *skill* doors
only, though this file's own docstring says a door in the wrong place is as wrong as a missing one.
Both verified green by the reviewer, ~4 lines each. **Pre-existing and outside this lane's acceptance
list**; widening scope mid-lane is the drift Phase 2 exists to stop. Recorded in the plan so it is
captured rather than lost.~~
→ **Both FIXED on the operator's ruling** — see the section below. Neither was ~4 lines, and the
opencode one was not the harmless tidy-up this paragraph implies.

### Step 0.7 — blast radius against current `main`

SCC-110 landed **mid-lane**; absorbed, and the merged SOP table **re-read** rather than trusted —
both lanes added rows to one inventory, they landed in different sections, and both read correctly.
That obligation was written into the plan before the merge, and SCC-110's own commit
`883f1da` ("the merge was clean, the text was not") is why.

| Gate | Result |
|---|---|
| Enforcement suite | **16/16 files, exit 0** |
| Toolkit lint | **0 errors, 0 warnings, exit 0** |
| Assertion evidence | RED captured → GREEN at `97dc770` |
| SOP currency | exit 0 |
| Door parity | **the subject of this lane** — 84 doors, 0 drifted |

---

## Addendum — the two recorded gaps, closed (2026-08-12)

The operator took the "deliberately not fixed" pair and said fix them. Both are now in.

### One of them was not cosmetic

> ⛔ **CORRECTION — filed 2026-08-12 by the `chore/SCC-113-gate-honesty` lane. The paragraph below
> is left standing because it is the record, and it contains a false claim.**
>
> *"it falls to that final `$false` and is **kept forever**"* — **false.** I read `Sync-CommandDir`
> in isolation and stopped one line short of its caller. `Invoke-ManifestPurge`
> (`sync-agents.ps1:822`) runs immediately after the opencode sweep and retires that door on the
> next sync.
>
> The true gap is narrower and the check is still worth having: the manifest can only retire
> **a name a previous run recorded writing** (`sync-agents.ps1:380`). A door that predates the
> manifest, was hand-dropped, or is genuinely this repo's own is unreachable by it and survives
> indefinitely — which is what `.agents/project-own.txt` now adjudicates in the sweep.
>
> The claim below also said the one-door contract held "of the skill doors only". For *placement*
> that was right; for *ghosts* it was true of no surface — `.agents/skills` and `.claude/skills`
> are unswept to this day.

I recorded `.opencode/commands` having no ghost check as tidy-up. Reading the engine instead of
assuming: `Sync-CommandDir` runs for opencode **without `-Mirror`** (`sync-agents.ps1:821`), and its
purge branch ends `else { $false }  # local: keep foreign/project-own files`. Delete a command brain
and its opencode door is not eligible, no longer in `$masterNames`, and not a mirror — so it falls to
that final `$false` and is **kept forever**, still handing an opencode agent a retired flow. The
workflows mirror prunes, which is why that side has been guarded since long before this lane. The two
surfaces were never equivalent, and my note said they were.

### One real inconsistency surfaced, and it is not a bug

The placement sweep found exactly one hit: `.agents/workflows/smh-adviser-board.md` exists while its
command declares `platforms: [claude, opencode, codex]`. That workflow is **hand-authored** — in the
engine's `$excluded`, carrying `platforms: [antigravity]` itself. The engine derives generated doors
from `platforms:` and makes no such promise for excluded files. So it is exempt — but **earned at the
point of use**, not a `continue`: the exemption holds only while the door declares the surface it sits
on, parsed with the same rule the engine uses. To smuggle a misplaced door past it you must edit
PowerShell *and* write antigravity frontmatter into the file, which is the deliberate act of authoring
a hand-owned Antigravity door.

A second check covers what placement structurally cannot see: a door denying a surface its **command**
claims. Placement never fires there, and nothing else looks.

### Mutation battery — five attacks on a throwaway copy of the real tree

Baseline **0 FAILs** (33/33). Every attack caught:

| Attack | FAILs |
|---|---|
| a command drops `opencode`, its mirror left behind | **2** |
| a command drops `antigravity`, its workflow mirror left behind | **2** |
| the hand-owned Antigravity door denies the surface it sits on | **2** |
| a command brain deleted — the opencode sync **keeps** its door | **2** |
| a cache directory renamed, so the ghost sweeps read nothing | **3** |

The first attempt at attack 1 **did not land** — I picked a command with no `platforms:` key, so the
mutation was a no-op and the assert caught it. Recorded because a mutation that silently fails to
mutate is a green that proves nothing, which is the whole failure mode this battery exists to avoid.

Both ghost sweeps also picked up A-3's non-empty guard, in the same idiom as the parity sweep —
shipping a guarded new check beside an unguarded old one is incoherent.

**The SOP was ahead of the code.** Its row already claimed "none on a platform it doesn't, no ghosts";
that held for skill doors only. The row now says which surfaces were covered and why the opencode side
is different.

**Gates:** `run_all` **16/16 exit 0** (command surfaces **33/33**, was 26/26) · `workflow_lint
--toolkit-only` 0 errors 0 warnings exit 0 · `py_compile` 0.

---

## Addendum 2 — the close-out blocked itself, and it was right to

Running `/smh-close-task-merge-tree` produced **exit 2** on the first preflight:

```
[ERROR] manifest: .../2026-08-11_scc-113-jira-in-progress-seam/task.yaml declares branch
`chore/SCC-113-jira-in-progress-seam` but this preflight resolved
`chore/SCC-113-door-content-parity` - one of them is wrong
```

**Neither was wrong.** The parent lane is merged (`302bd37` on `origin/main`) and pruned local and
remote — by Step 5 of this same command. What the gate hit is a ruling it had no way to express:
`followon-fixes-are-not-a-new-story` says a follow-on rides the ticket it came from rather than
minting a new key, so the second lane writes a second `task.yaml` under the **same** `task_key`.
`check_manifest()` errored on every manifest naming a different branch — making the repo's own
documented workflow a hard block at close-out. **SCC-113 is the first ticket in 26 manifests to have
two lanes**, so this is the first time it could fire.

Its own remedy — *"fix the manifest or aim at the declared branch"* — is unavailable in both halves:
the declared branch is gone, and rewriting a completed lane's manifest to name a different branch
would falsify that lane's record.

**A manifest is history, not a competing lane, when BOTH hold:** its branch exists nowhere (local or
origin), **and** some other manifest for this key declares the branch actually resolved.

**The second condition is the entire safety of it.** Without it, a lone stale manifest pointing at a
deleted branch silently excuses a close-out aimed at the wrong lane — the 2026-08-09 failure
`--expect-key` exists for, re-opened by a fix for something else.

**Proven by mutation, not asserted.** The *pre-existing* control `SCC-64 a manifest naming a
DIFFERENT branch blocks` is exactly that shape — its declared branch was never created either — and
must still block. Drop the `confirmed` half: **80/81, red**. Two new cases added: a closed lane does
not block its follow-on (real fixture — `merge --no-ff`, delete the branch both sides, second lane
writes its own manifest), and a **live** sibling lane still blocks.

**Second preflight: `0 error(s), 1 warning(s)` — `VERDICT: clear to close out and merge`**, LANE
`LOCAL`, GATES `ARMED`. The one warning is the worktree, which Step 5 prunes.

**Gates at `fe46b4a`:** `run_all` **16/16 exit 0** (command surfaces **33/33**, task_preflight
**81/81** ← 79/79) · `workflow_lint --toolkit-only` 0/0 exit 0 · `py_compile` 0.

---

## Your Actions

1. **Close out** — `/smh-close-task-merge-tree`, `--expect-key SCC-113`.
2. **Nothing else owed.** Both items from the parent lane are settled: AGY is by design, and the
   other one is now fixed rather than recorded.
