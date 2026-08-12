# SCC-113 (third lane) — make the armed gates honest

**Branch** `chore/SCC-113-gate-honesty` · **Worktree** `.claude/worktrees/scc-113-gate-honesty` · **Base** `main @ 2e8aa46`

Follow-on to SCC-113, riding the same key per `followon-fixes-are-not-a-new-story`. This is the
third lane on this ticket; the first two are merged and pruned.

---

## Why this lane exists

Two clean-room adversarial reviews ran against the two SCC-113 addenda that shipped **without** an
independent pass (`5fef0a8` and `fe46b4a` — both carried mutation batteries instead). The passes had
no contact with each other. **Both independently reproduced the same HIGH.**

The reviews are the deliverable that matters: they found what a mutation battery written by the same
author could not. This lane acts on their findings.

Governing constraint: **an armed gate that can be wrong is worse than no gate**, because it launders a
bad state as a verified one. Everything below follows from that.

---

## Part 1 — REVERT: `fe46b4a` in full

`fe46b4a` taught `task_preflight.py` that one ticket can have two lanes, so a sibling `task.yaml`
naming a merged-and-pruned branch stops blocking the close-out.

### Why it goes, not gets patched

| Sev | Defect | Consequence |
|---|---|---|
| HIGH | `check_manifest()` runs **before** `check_sync()` acts on `--fetch`, so `branch_alive()` reads the **pre-fetch** ref cache | Two identical runs return opposite verdicts. On a second machine that has never fetched, a **live** sibling lane reads as pruned and the close-out is waved through — the exact failure the check was written to prevent. |
| HIGH | `branch_alive()` returns "dead" on **any** non-zero git exit | A typo'd branch name, a bad repo path, or a transient git failure all report `is merged and pruned` and the verdict prints clear. Four distinct states collapse into one false INFO. |
| MED | `fetch.prune` is unset on the PC (the gitconfigs diverged) | A genuinely closed lane leaves a stale `origin/<branch>` ref forever, so `branch_alive()` says yes and the close-out blocks **permanently** — three runs, three exit 2. |

Neither of the two tests shipped with it can see any of this: both fixtures build the sibling lane in
the **same clone**, so refs are always fresh and git never fails.

The design is wrong, not the implementation. It asks *"is the ref gone?"* — absence of evidence. The
correct question is *"did this branch land?"* — positive proof of ancestry into `origin/main`, checked
**after** the fetch. That rebuild is queued below, not attempted here.

### Scope

Revert all three files in `fe46b4a`: `task_preflight.py`, its two tests, and the SOP row.

### What reverting costs you

Any manifest naming a different branch is an ERROR again. **The next two-lane ticket blocks the
close-out at exit 2** and you unblock it by hand. That friction is the accepted price; it fails in the
direction that stops work rather than the direction that lands it.

SCC-113 itself is already closed, so nothing in flight is affected.

---

## Part 2 — FIX FORWARD

### 2.1 The opencode ghost check must honour `project-own.txt`

`sync-agents.ps1` has a documented keep-list at `<repo>/.agents/project-own.txt`, staged by
`-Reconcile`, whose own header reads: *"Every name listed here is preserved forever; sync-agents will
never purge it."* My ghost check does not know it exists — so the day anyone uses a documented engine
feature, **every lane in the repo red-walls**.

Latent today: the file is absent from this repo. Latent is not fixed.

- Derive the exemption from the file, parsed the way the engine parses it (strip `#` comments, trim,
  drop empties). Never restate its contents — the copied-subset mistake this lane already paid for once.
- Match the engine's `$null` vs `@()` distinction: **absent** = no list authored (exempt nothing);
  **present but empty** = an authored empty list (still exempt nothing). Same outcome here, different
  meaning, and the comment must say so.
- ⚠️ **AUDIT FINDING (Phase 2 — generalizing for N=1). Apply to the opencode sweep ONLY.** The
  original plan said "both sweeps" because the file's header says *"commands/workflows"*. Traced:
  `Get-SurfaceState` (`sync-agents.ps1:316-345`) maps `.agents\workflows` to the **master's own**
  workflows, so in the lobby that surface is compared against itself and can never produce an orphan
  — `-Reconcile` therefore cannot stage a lobby workflow into the keep-list. `.opencode\commands` is
  mapped to `$mCmd` (`.agents/commands`), so it can. And `test_command_surfaces.py` is lobby-only
  (`ROOT = parents[3]`; no child project carries it — verified). Exempting the workflows sweep would
  be unreachable code. Record the reason in a comment so the next reader does not "fix" the asymmetry.
- **The exemption cannot be exercised by the live tree** (no such file exists), so it ships with
  pure-string controls or it is decoration. That is this ticket's own lesson, applied to itself.

### 2.2 The hand-owned placement exemption is earned by silence

`platforms_of()` returns "all platforms" when there is no `platforms:` key — correct for commands,
wrong as a *qualification*. A hand-owned workflow currently earns its placement exemption by writing
**no frontmatter at all**, which is the opposite of a deliberate act.

`.agents/workflows/smh-update-maps-indexes.md` qualifies this way today. `smh-adviser-board.md` carries
`platforms: [antigravity]` explicitly and is unaffected.

- Require an **explicit** antigravity declaration for the exemption — absent no longer qualifies.
- Add `platforms: [antigravity]` to `smh-update-maps-indexes.md`.
- **Verify first** that adding the key changes nothing else: the file is in the engine's `$excluded`
  (never written, never pruned), but confirm against `workflow_lint.py` and the content-parity check
  before editing rather than after.

### 2.3 Correct the record — three false statements I shipped

These are worse than the bugs. Each one describes a protection that does not exist, in the document
you would read to decide whether you are protected.

| Where | Claim | Truth |
|---|---|---|
| SOP row 1196 | opencode's sync *"**keeps** a door whose command was deleted, **forever**"* | False. `Invoke-ManifestPurge` (`sync-agents.ps1:823`) retires it. Proved by running the engine: `purged 1 retired .opencode command(s): smh-review.md`. I read `Sync-CommandDir` in isolation and stopped one line short of its caller. |
| SOP row 1196 | the one-door contract was *"true of the skill doors only"* | False for ghosts. Skill doors have **no** ghost check either — `.agents/skills` and `.claude/skills` are unswept to this day. |
| SOP row 1194 | the two-lane manifest rule and *"that second condition is the whole safety of it"* | Goes with the revert. The condition is real in intent and not what the code measures. |

The replacement rationale for the ghost check is the true one: the manifest purge can only retire what
a **previous sync recorded writing**. A door predating the manifest, or hand-dropped, survives — and
that is precisely the case `project-own.txt` exists to adjudicate. The check is still worth having;
the reason it was given was wrong.

Same corrections to the SCC-113 walkthrough, marked as corrections with the original text visible
(the `story-artifacts-two-doc-close` convention).

### 2.4 `jira_feed.py check` — ⚠️ REWRITTEN BY AUDIT; the original fix addressed the wrong defect

**Original plan step:** *"wire the `--story` flag `cmd_check` already accepts; verify first whether
the warning is cosmetic — if so, queue it."*

The audit ran that verification and it inverted **both** halves.

**The warning is load-bearing, not cosmetic.** `wf_common.py:355-357` —
`return 2 if e else (1 if w else 0)`. A warning exits **1**. Run live during the audit:

```
$ python3 .agents/scripts/jira_feed.py check --key SCC-113   # bare, not piped
[WARN ] devrecord: SCC-113: 2 Dev Records - there should be exactly one, updated in place
-- 0 error(s), 1 warning(s), 1 info --
REAL_EXIT=1
```

`smh-close-task-merge-tree.md:245` declares this call `# must exit 0`. **So this lane cannot close
today.** Not hypothetical — demonstrated, on this ticket, before any code was written.

The in-code comment `# Not fatal, but it means something posted around the update path` is wrong
about its own function's behaviour, and reading it is what nearly got this item cut.

Split into two items, and the first is **diagnose-before-fix**.

---

#### 2.4a — DIAGNOSED 2026-08-12. ⛔ The audit's own stated cause (A-1) was wrong; the conclusion was not.

A-1 asserted *"the Task close-out does not pass `--story`."* **It does** —
`smh-close-task-merge-tree.md:236` and `smh-quick-dev.md:246` both pass `--story <branch-slug>`.
Diagnosing before fixing is what caught that, which is the whole point of the split.

The two records, read live off the board:

| # | Header | Merge |
|---|---|---|
| 1 | `Dev Record - scc-113-jira-in-progress-seam (close-out, 2026-08-11)` | `302bd37` |
| 2 | `Dev Record - scc-113-door-content-parity (close-out, 2026-08-12)` | `2e8aa46` |

Two lanes on one ticket → two branch slugs → two story ids. `find_devrecord` filters by story id
**deliberately** — its own docstring: *"so a ticket that legitimately carries records for two ids
does not have one overwrite the other."* Lane 2 correctly did not overwrite lane 1.

**So nothing posted around the update path, and there is no data to repair.** The record count is
the designed outcome, and `followon-fixes-are-not-a-new-story` makes multi-lane tickets normal
rather than exceptional. `cmd_check` counts records without reading their ids, so it cannot tell
*"one lane posted twice"* (a real defect) from *"two lanes each posted once"* (the design).

**It is a check asserting something the system does not promise — this lane's exact defect class,
sitting in the gate that blocks this lane.**

**Fix — group by story id, do not count.** The existing test at `test_jira_feed.py:508-511` seeds
`Dev Record - 9.1 (quick-dev)` + `Dev Record - 9.1 (close-out)` — the **same** id twice, which is
the genuine "both lanes posted" defect SCC-49 wrote the check for. That test **stays green** and
becomes the negative control proving the check was narrowed, not deleted.

| Board state | Today | After |
|---|---|---|
| one id, two records (quick-dev + close-out both posted) | warn, exit 1 | **unchanged** — warn, exit 1 |
| two ids, one record each (two lanes) | warn, exit 1 | clean, exit 0 |
| no records | err, exit 2 | unchanged |

#### 2.4b — now the SAME defect, so it ships here

`cmd_check()` ignores `--story` while **three** surfaces document passing it: `jira_feed.py:15`
(its own usage line), `.agents/rules/jira.md:302` (a rule), and
`.agents/commands/cicd-update-sprint-memory.md:191` (a command body).

2.4a makes `check` story-aware, which gives the flag a real meaning it did not have before:
**"did *this lane* file its record?"** — the question a close-out actually needs to ask. Wiring it
is now smaller than deleting the promise from three surfaces, one of which is a rule.

⚠️ **One rule, one implementation.** The `--story` path delegates to `find_devrecord` itself rather
than re-implementing id matching, so `check --story X` answers exactly *"would `devrecord` update
this record?"* — the same discipline A-2′ forced on `is_launcher_for` in the previous lane.

---

## Part 3 — KEEP, untouched

Verified sound by both passes; no changes.

- **Door content parity** (`e8bcc0a` / `97dc770`) — the check that catches a mirror drifting from its
  brain. Caught the live SCC-77 break. Survived five platform-reach states, a new command, and a
  **fresh clone** at 33/33.
- **The placement checks** — no false positives found by either pass.
- **The In Progress automation** — the ticket's original deliverable. Neither review touched it.

---

## Part 4 — QUEUE, explicitly not this lane

Widening scope mid-lane is the drift that produced this mess. Recorded, not actioned:

1. **Rebuild two-lane preflight support properly** — positive proof of landing (ancestor of
   `origin/main`), evaluated **after** the fetch, with a fixture that models the second machine:
   separate clone, stale refs, `fetch.prune=false`. This is a design task, not a patch.
2. **`-AP` doors are invisible** to placement, both ghost sweeps, and parity. `Sync-CommandDir` takes
   `-SkipAP:$IsLobby` (`sync-agents.ps1:821`) — they are vendored into projects but not the lobby, and
   nothing checks them anywhere. Pre-existing, not a regression.
3. **No ghost check for skill doors** — see 2.3. Pre-existing.
4. **`platforms_of()` caps its scan at 60 lines**; the engine's `Get-CommandPlatforms` has no cap. A
   divergence between two parsers of one fact, which is the exact class this file's own header warns
   about.

---

## Acceptance criteria — each with the command that proves it

⚠️ Rewritten by the audit. AC5 was an either/or with an escape hatch, which is not checkable; the
audit's evidence resolved it into a definite requirement. Every item below is provable by a command.

| # | Acceptance | Proved by |
|---|---|---|
| 1 | `fe46b4a` reverted across all three files; the manifest check is back to "any mismatching manifest is an ERROR" | `git revert fe46b4a` (verified clean, exit 0, no conflicts); `test_task_preflight.py` → **79/79** |
| 2 | The opencode ghost sweep honours `.agents/project-own.txt`, parsed the engine's way | `test_command_surfaces.py` green, **plus pure-string controls that fire** — the live tree has no such file, so a live sweep proves nothing |
| 2b | A **malformed or unreadable** keep-list never widens the exemption | a control feeding it garbage; the exemption must shrink to empty, never to "exempt all" |
| 3 | The hand-owned placement exemption requires an **explicit** antigravity declaration | mutation: strip `platforms:` from a hand-owned workflow → the check must FAIL |
| 3b | `smh-update-maps-indexes.md` declares `platforms: [antigravity]` and nothing else breaks | `workflow_lint --toolkit-only` 0/0 (verified: it does not scan `.agents/workflows/` at all, and the file is in the engine's `$excluded`, so there is no cache fan-out) |
| 4 | All three false statements corrected in the SOP and the walkthrough | inspection against the evidence cited in 2.3; the reverted SOP row 1194 restores clean (verified) |
| 5 | `jira_feed.py check --key SCC-113` exits **0** | `python3 .agents/scripts/jira_feed.py check --key SCC-113; echo $?` — **run bare.** Today it is 1. This gates the close-out. |
| 5b | 2.4b either shipped or queued **with the three documented call sites named** | inspection |
| 6 | Content parity + placement unchanged and still green | `test_command_surfaces.py` at or above its current count |
| 7 | Gates: `run_all.py` exit 0 **bare, never piped**, `workflow_lint --toolkit-only` 0/0, `sop_currency` exit 0, `py_compile` 0 | each run bare; a piped gate returns the pipe's exit code |

## The review requirement — non-negotiable for this lane

**A clean-room pass that lists which assertions it made fire.** Not a verdict word; the attack list.
Both items being fixed here shipped on a self-written mutation battery and a `PASS`, and both were
wrong. A review that reports `PASS` without naming what it made fail is not evidence, and this lane
does not merge on one.

## Process change this lane establishes

1. **No gate goes armed without a clean-room pass naming the assertions it made fire.**
2. **When a fix targets an assumption, grep for the assumption before closing.** SCC-113 fixed
   "one ticket, two lanes" in the preflight and shipped the second instance of the identical
   assumption — in `jira_feed.py` — in the same close-out. A bug was patched where a pattern should
   have been swept.

---

## Self-Audit (2026-08-12)

**Mode:** PRE-WORK — nothing built, the lane is untouched.
**Repo:** `chore/SCC-113-gate-honesty` @ `2e8aa46` (echoed from `git rev-parse`, not from belief).
**Right-size: FULL.** Touches a gate (`task_preflight.py`), a script other scripts import
(`jira_feed.py`), the door law, and a platform surface — every "Full" trigger fires.

### Phases walked

- **Phase 0 — scope + checkable list.** Change set: 7 files (2 reverted, 1 gate test extended, 1
  workflow frontmatter, 2 docs, 1 conditional on 2.4a). Acceptance list rewritten as a table with a
  proving command per row; AC5's either/or escape hatch cut. **Lane check: LOCAL** — nothing under
  `backend/ frontend/ firebase/ functions/ mobile/ .github/`, so `/smh-close-task-merge-tree` is the
  correct door, not `/cicd-push-e2e`.
- **Phase 1 — blast radius.** Traced and cleared: no command body edited, no rename, no rule edited,
  no file moved. Live: **scripts** (callers checked — `hooks_armed.py`, `INDEX.md`, 3 rules, 2
  command bodies), **a gate** (the revert *tightens*; nothing ships newly-armed), **the SOP** (both
  halves must land in one commit — `sop_currency.py` is ARMED), and **`_artifacts/_memory/`** — *not*
  in the change set and deliberately so.
- **Phase 2 — over-engineering.** One tripwire fired and was cut; one fired and was cleared with
  evidence. Detail below.
- **Phase 3 — pre-mortem.** 8 rows walked; 2 findings survived, both recorded below.

### Findings

| # | Where | Sev | Failure scenario | Disposition |
|---|---|---|---|---|
| A-1 | plan §2.4 | **HIGH** | The plan proposed wiring `--story` to fix the "2 Dev Records" warning. `find_devrecord` with `story=None` already updates in place, and the Task close-out does not pass `--story` — **the proposed fix does not touch the symptom.** Root cause never diagnosed. | **REWRITTEN.** Split into 2.4a (diagnose first) and 2.4b (a separate real defect). |
| A-2 | `wf_common.py:355` | **HIGH** | The plan called the warning possibly "cosmetic" and offered to queue it, on the strength of an in-code comment reading *"Not fatal"*. `exit_code()` returns **1** on a warning. Live run: `REAL_EXIT=1` against `# must exit 0`. **This lane could not have closed.** | Escalated to a blocking AC (#5) with a bare-run proof command. |
| A-3 | plan §2.1 | MED | "Apply to both ghost sweeps" — the workflows sweep can never see a `project-own.txt` entry (`Get-SurfaceState` self-compares `.agents\workflows` in the lobby; the test is lobby-only). Unreachable code sold as symmetry. | **CUT** to the opencode sweep, with the asymmetry explained in a comment. |
| A-4 | `jira_feed.py:15`, `jira.md:302`, `cicd-update-sprint-memory.md:191` | MED | Three surfaces — including **a rule** — document passing `--story` to a `check` that ignores it. Agents are being told to pass a dead flag. | Folded into 2.4b; ship or correct all three, never one. |
| A-5 | `task_preflight.py` (post-revert) | MED | The reverted gate has **no override flag, on purpose**. A legitimately-blocked two-lane close-out therefore has no sanctioned exit — which invites a `--no-verify` on the push instead, defeating a different gate. | **Accept and name it.** The remedy is the queued rebuild, not an escape hatch. Recorded so the friction is a known cost, not a surprise. |
| A-6 | plan §2.1 | LOW | The `project-own.txt` exemption tripped *"error handling for states that cannot occur."* | **CLEARED with evidence:** `-Reconcile` is a documented flag that *writes the file itself* and promises the names are preserved forever. One flag away, and it red-walls every lane on arrival. |
| A-7 | plan §2.1 | LOW | Framing: the ghost check and its exemption are not "a feature plus a nicety" — without the exemption the check **contradicts the engine it is checking**. | Ship both or revert both. "Ship the check, queue the exemption" removed as an option. |

### Pre-mortem rows that survived

- **The escape hatch** — A-5 above. The accepted friction has no auditable release valve.
- **The gate fires on someone else's commit** — the first person to hit the restored manifest ERROR
  is the operator, on the next follow-on ticket. The message is actionable (*"fix the manifest or aim
  at the declared branch"*), so this is a known cost rather than a defect.

Cleared with a line each: **other machine** (tests use `sys.executable`; doc edits are neutral) ·
**fresh clone** (no newly-armed gate ships) · **empty input** (absent keep-list exempts nothing —
the safe direction; AC 2b pins the malformed case) · **four platform caches** (the edited workflow is
in the engine's `$excluded` and `workflow_lint` does not scan that directory — verified, no fan-out) ·
**sibling lands first** (no file overlap) · **rollback** (everything here is a revert).

### Sibling-lane landing order

Only `main` is live. It holds another session's uncommitted `_artifacts/_memory/MEMORY.md` +
`two-machines-mac-and-pc.md`, plus an untracked proposal doc. **No overlap with this change set.**
That session lands first or later without affecting this lane; absorb `origin/main` at close-out as
normal. Per `.agents/rules/` the memory store is READ-ONLY outside its own write flow — **those files
are never swept, staged, or committed under this ticket.**

### Four gates

- **Verification strategy present?** Now yes — every AC carries its proving command, and the two
  that matter most specify **bare, not piped**.
- **Anything irreversible?** One: the Jira transition Done → In Progress → Done. Gated — it happens
  in the close-out, not during dev, and it is re-doable.
- **Any step vague enough that the builder will guess?** Both "verify first" steps were exactly that.
  The audit ran both verifications; both inverted the plan. Neither remains a guess.
- **Convention fit?** Yes — follow-on rides the ticket key, artifacts in
  `_artifacts/_main/<date>_<slug>/`, one-door law respected, SOP-currency pairing observed.

### What this audit is evidence of

The plan I wrote proposed a fix for a defect I had not diagnosed (A-1) and nearly cut a
lane-blocking item because I read a code comment instead of the function (A-2). **That is the same
inferring-instead-of-executing pattern this lane exists to correct, caught inside the audit of the
correction.** It was caught before a single file changed, which is what the gate is for — and it is
the strongest available argument for the process change this lane establishes.

```
Audit verdict: GO
```

GO **conditional on the plan as amended above** — 2.4 rewritten, 2.1 cut to one sweep, the
acceptance table replacing the prose list. 2.4a is a blocker: this lane cannot close until
`jira_feed.py check --key SCC-113` exits 0.

## Addendum (2026-08-12) — H-1: option A pulled in-lane by the operator

This plan queued the positive-ancestry preflight rule as its own future lane; the review then
showed the revert makes it THIS lane's close-out blocker (H-1). At hand-back the operator chose
option A, which makes the scope expansion a directed decision, not drift. Built at `866d185`
with its own red (preflight suite 81/84 → 84/84) and a 4-mutation battery — evidence in the
walkthrough's review addendum.
