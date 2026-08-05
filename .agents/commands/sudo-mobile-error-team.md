---
description: Error team responder — take a live production incident (Sentry P1 → GitHub issue → machine-written fix branch) from alert to landed hotfix. Independently re-diagnoses, offers rollback-vs-fix-forward, writes a minimal fix + regression test, gates it on real CI, and stops twice for Daniel. Phone-first (this is the command the incident page tells you to run). Never merges on its own initiative; never pushes main/main_debug.
platforms: [claude]
---

# /sudo-mobile-error-team — Error Team Responder

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/sudo-target-resolution.md` — bind ONE target, never operate on the lobby
> - `.agents/rules/reproduce-before-you-fix.md` — the five debug gates behind standing rules 1 and 4
>   below. Under fire, the two that get skipped are **G1** (the Sentry event id IS your reproduction —
>   if it doesn't reproduce, say so; don't fix blind) and **G5** (revert the fix hunk, watch the
>   regression test go red again, restore).

> **What this is.** The human half of the incident pipeline. The machine half already ran: the relay
> opened a GitHub issue (`incident:<short-id>`) and the headless agent (`incident-response.yml` →
> `.github/claude/incident-triage.md`) wrote a full report and pushed a `claude/incident-<id>` fix
> branch. **This command is what you run next.** It re-verifies that work, decides rollback vs
> fix-forward, lands a gated hotfix, and closes the loop.
>
> **Why it exists.** Before this, the incident page handed you a paste-blob of improvised
> instructions and you wrote the rules yourself, on a phone, during a fire. The rules below were
> agreed in calm (2026-07-23) so you never have to.

`$ARGUMENTS` = a Sentry short-id (`AVIATIONCHAT-42`), a GitHub issue URL/number, or `latest`.

---

## ⛔ Standing rules (apply to EVERY step — never overridden by urgency)

1. **Distrust the machine's report.** The headless agent's root cause is a **hypothesis**, not
   ground truth. Re-verify every cited `file:line` at the release SHA **before** writing code. If
   the report cites code that doesn't match what's there → say so **loudly**, discard its
   conclusion, re-diagnose from evidence. (House memory: ground-truth every cited file:line.)
2. **Triage before treatment.** Establish *is it still firing · how many events · who is affected ·
   does it correlate with a deploy* before touching anything. **"Not a fire" is a legitimate
   ending** — a 1-event fluke exits at Step 2 with "resolve in Sentry, close the issue, no code."
3. **Hotfix scope discipline.** The minimal surgical change that addresses the root cause. **No**
   refactors, **no** drive-by cleanups, **no** dependency bumps, **no** "while I'm in here."
   Everything else becomes the follow-up story in Step 9.
4. **A regression test is mandatory** — one that fails on the broken code and passes on the fix.
   No test, no merge recommendation. If the failure genuinely can't be unit-tested, say so
   explicitly and name what would catch it instead. **"Fails on the broken code" must be OBSERVED,
   not asserted** — write it before the fix and paste the red, or revert the fix hunk afterward and
   paste the red then (`reproduce-before-you-fix` G2/G5). A test only seen green proves nothing.
5. **Branch law.** This command writes **only** `claude/incident-<short-id-lower>`. It **never**
   pushes `main` or `main_debug`, and **never merges on its own initiative** (see Stop 2).
6. **Two anchors, don't confuse them.** Read code for **diagnosis** at the event's `RELEASE_SHA`
   (what the user actually ran). Base the **fix branch** on current `main` HEAD. If they differ,
   say so — the gap may itself be relevant.
7. **No secrets in any output. PII stays hashed** — the backend `_before_send` already SHA-256es
   user ids; never try to reverse them.
8. **Never claim a pass you didn't observe.** A gate that didn't run is `UNVERIFIED`, not green.

---

## Step 0 — Resolve the project + lane (FIRST)

**Project.** Same ladder as every `/sudo-*` command:
0. **Self fast-path (check FIRST — the normal mobile case):** if this repo has **no** `Projects/`
   subfolder, you ARE the project → `PROJECT_ROOT = .`; skip the rest.
1. **Inline override** — `$ARGUMENTS` starts with a folder name under `Projects/` → that's the
   target; consume the token; write the name alone into `.agents/active-project.txt`.
2. **Active pointer** — else read `.agents/active-project.txt`.
3. **Ask** — else STOP and ask. Never guess, never operate on the lobby.

Echo `Target: <PROJECT_ROOT>`. Every path below resolves under it.

**Runbook check.** Read `PROJECT_ROOT/.github/claude/incident-triage.md`. Missing → **STOP**: this
project has no incident pipeline. Never improvise triage logic in its place.

**Lane.** `CLAUDE_CODE_REMOTE=true` (or Daniel says "mobile") → **mobile lane**: taps not typed
approvals, TL;DR-first, 📱 artifact tags, no local test runner. Else **desktop lane**. Full rules →
`.agents/rules/mobile-mode.md`.

---

## Step 1 — Resolve the incident + resume ladder

**Resolve.** From `$ARGUMENTS`:
- Short-id (`AVIATIONCHAT-42`) → `SHORT_ID`.
- Issue URL/number → read it, lift `SHORT_ID` from the `incident:<id>` label or title.
- `latest` / empty → newest **open** issue labeled `incident`:
  `gh issue list --label incident --state open --limit 1 --json number,title,url`.
- Nothing found → say so and stop cleanly (not an error).

**Gather** (each degrades, none blocks):
| Source | How | If unavailable |
|---|---|---|
| GitHub issue | `gh issue view <n> --json body,title,labels,createdAt,state` | STOP — it's the anchor artifact |
| Sentry issue | Sentry **MCP** (org `aviationchat`, region `us.sentry.io`) | fall back to the issue body's excerpt + report; note the gap |
| Release SHA | issue body "Deployed SHA at fire time" / Sentry event `GIT_SHA` | note "release SHA unknown — diagnosis unanchored" |
| Log excerpt | pre-fetched + scrubbed in the issue body | `gcloud logging` (desktop) or note the gap |

**Surface detection.** Read the **Sentry project slug** from the issue/event — never hardcode.
`python-fastapi` → **backend**. The frontend project (Story 16.3) → **frontend**. This decides the
rollback playbook in Step 5 and the test scope in Step 7.

**Resume ladder (this command is re-entrant — always run this).** Re-invoking mid-incident must
never re-do finished work or duplicate anything. Detect and report state, then jump to the first
unfinished step:

| Signal | Meaning | Jump to |
|---|---|---|
| No branch `claude/incident-<id>` | machine lane wrote no fix (or ran excerpt-only) | Step 2 |
| Branch exists, no PR | fix branch awaiting verification | Step 2 (re-verify), then 6 |
| Draft PR open | gate not yet requested / running | Step 7 |
| PR checks running | gate in flight | Step 7 (report + wait) |
| PR checks concluded | verdict ready | Step 8 |
| PR merged | hotfix landed | Step 9 |
| Issue closed + Sentry resolved | incident closed | report closed; offer the follow-up story only |

Say which state you found before doing anything else.

---

## Step 2 — Triage card (before any diagnosis)

Answer these **first**, from Sentry where reachable:

- **Still firing?** events in the last 15–60 min vs. total. (Falling to zero on its own changes
  everything.)
- **Volume + reach:** total events · distinct users (hashed) · first seen / last seen · environment.
- **Deploy correlation:** did first-seen land within minutes of the release SHA's deploy?
- **Severity call:** who can't do what right now.

**Two early exits:**

- **Not a fire** (single-digit events, not recurring, no user-visible impact) → recommend
  *resolve in Sentry · close the issue · no code*. Offer the follow-up story if it's a real-but-minor
  bug. **This is a success, not a failure.** Get Daniel's tap, then go to Step 9.
- **Bleeding now** (firing at volume **and** deploy-correlated) → **offer ROLLBACK-FIRST before deep
  diagnosis.** Stopping the bleeding beats understanding it. Jump to Stop 1 with rollback as the
  recommendation. Rollback **never ends the incident** — the fix PR continues at normal pace after.

---

## Step 3 — Independent diagnosis

Execute the **runbook's Steps 1–4** (`.github/claude/incident-triage.md`) on the **interactive
lane** — it is the diagnosis brain and this command adds nothing to it and skips nothing.

Then do the part the runbook can't: **audit the machine's work.**

- If a report issue and/or `claude/incident-<id>` branch exists, read the report's root-cause claim
  and the branch diff (`git fetch origin claude/incident-<id> && git diff main...claude/incident-<id>`).
- **Re-verify every cited `file:line` at `RELEASE_SHA`** (`git show <RELEASE_SHA>:<path>`). Does the
  quoted code exist, at that line, saying that?
- Judge the diff independently: does it address the **mechanism** you derived, or a symptom? Does it
  overreach past Rule 3? Does it carry a regression test?

Produce a verdict: **report CONFIRMED · report PARTIALLY RIGHT · report WRONG (re-diagnosed)**.

---

## Step 4 — 🛑 STOP 1: the decision card

**No project file has been edited yet, and none will be before the tap.**

Present a **short** card (mobile lane: TL;DR only, details on request):

```
🔥 <SHORT_ID> — <one-line what broke>
Still firing: <yes, N in last 30m | no, stopped HH:MM>
Blast radius: <who/what, N users>
Root cause: <the mechanism, one or two sentences>
Machine report: <CONFIRMED | PARTIALLY RIGHT | WRONG — why>

Options
  A) Fix forward  — <what changes> · ETA ~<n> min to PR, +<n> min CI
  B) Roll back    — to <revision/sha> · ETA ~<n> min to recovery · <what you lose>
  C) Both         — roll back now, fix forward behind it   ← usual answer when bleeding
Recommendation: <one of the above, and why>
```

Then ask via **AskUserQuestion** (a tap IS the gate, per mobile-mode Override 2):
**ACCEPT** (fix forward) · **ADJUST** (Daniel redirects the approach) · **REJECT** (not a fire /
stand down) · **ROLLBACK-FIRST**.

Always state a **time-to-recovery for both** rollback and fix-forward. Nobody computes that at 2am.

---

## Step 5 — Rollback (only if chosen)

**Backend (Cloud Run).** Every deploy tags its revision `sha-<short7>` and promotes with
`update-traffic --to-latest` (`deploy-backend.yml`), so rollback is a clean traffic split.
On Daniel's one-word approval, dispatch the workflow — this works from a phone, `gcloud` does not:

```bash
gh workflow run rollback.yml --repo <repo> -f target=<sha-short7 | revision-name | previous>
```

- **Degrade:** if the dispatch fails (workflow not on the default branch yet, or the token lacks
  `actions:write`), hand Daniel the **Actions page URL** — "Run workflow" is a tap in the GitHub
  app — plus the raw `gcloud run services update-traffic` line as the desktop fallback. Say which
  path you took.
- **Verify recovery:** watch the run to green, then confirm the Sentry event rate drops. An
  unverified rollback is not a rollback.

**Frontend (Firebase App Hosting).** App Hosting auto-deploys from `main`, so there is no traffic
split. Fastest path first:
1. **Console rollback** (a tap): give Daniel the Firebase console App Hosting → rollouts link.
2. **Then the git revert PR on `main`** — mandatory. A console rollback alone leaves the bad commit
   on `main`, and the next deploy re-ships it. These two are one action; never do only the first.

After recovery, **continue to Step 6** at normal pace. Rollback bought time; it didn't fix anything.

---

## Step 6 — The fix

Base on current `main`; reuse the machine's branch if it exists (`claude/incident-<id>`) —
**never cut a duplicate**.

```bash
git fetch origin
git checkout -B claude/incident-<id> origin/claude/incident-<id> || git checkout -b claude/incident-<id> origin/main
```

- Write the **minimal** change (Rule 3) and the **regression test** (Rule 4).
- Stage by **explicit path only** — `git add path/one path/two`. **Never `git add -A`/`.`/`-u`.**
  Verify `git diff --cached --stat` shows only your files. (Parallel teams share these trees.)
- Commit scoped to the incident; push with retries on network failure (4×, exponential backoff).
  Pushing `claude/*` is free — no approval needed.

---

## Step 7 — The gate (real CI, not a claim)

Open a **DRAFT PR targeting `main`** — tap-confirmed first (mobile-mode Override 1: ask before the
PR). This is the documented **hotfix carve-out**: the incident lane is anchored on production
(`incident-response.yml` checks out `ref: main`; both back-merge footers say merge to `main`, then
rebase `main_debug`), and `pr-check.yml` only runs on PRs targeting `main`.

```bash
gh pr create --draft --base main --head claude/incident-<id> \
  --title "hotfix(<SHORT_ID>): <one-line>" --body "<root cause · fix · test · links to issue>"
gh pr checks <n> --watch
```

**Read the verdict honestly:**

| Result | Verdict |
|---|---|
| All checks green | **GREEN** — safe to recommend merge |
| Any check red | **RED** — report which, fix or stop; never recommend merge |
| **Zero checks ran** | **UNVERIFIED** — say it plainly, never green |

> **The zero-checks trap.** `pr-check.yml` has `paths: backend/**, frontend/**`. A hotfix touching
> only config, `relay/`, scripts or workflows gets **no checks at all** — and an empty check list
> reads as "nothing failed." It is **UNVERIFIED**. State it, and on desktop run the suite locally
> instead (`backend\.venv\Scripts\python.exe -m pytest` — **never bare `python`**, that's the
> drifted global 3.14 and produces false failures).

Mobile lane has no test runner: CI is the only gate, and `UNVERIFIED` is the honest answer when it
doesn't run. Long CI → post the PR link and stop; Daniel pings "status" and the Step 1 resume
ladder picks it back up.

---

## Step 8 — 🛑 STOP 2: the merge decision

Present the verdict card: what changed · the test that now guards it · gate result · PR link.

**Merging is Daniel's.** On his approval: flip the PR out of draft (`gh pr ready <n>`). Then either
he taps Merge in the GitHub app, **or** his explicit *"merge it"* authorizes you to run
`gh pr merge <n> --squash`. Absent that word, **stop here** — never merge on your own initiative,
never on a RED or UNVERIFIED gate without Daniel explicitly accepting the risk in writing.

After a merge: watch `deploy-backend.yml` to green, then **verify recovery in Sentry** — the event
rate should fall to zero on the new release. Report the actual observation, not the expectation.

---

## Step 9 — Close the loop

1. **Sentry:** resolve the issue (in the next release where supported). Note: recurrence after
   resolve is a **regression alert** — and the relay's label-dedupe may suppress a re-fire, though
   the Sentry email still lands.
2. **GitHub:** comment the outcome on the incident issue (root cause · what shipped · PR link ·
   rollback taken?) and close it.
3. **Artifact:** write the full report to
   `_artifacts/debugging/<YYYY-MM-DD>_<short-id-slug>/incident-report.md` using the runbook's Step-5
   template, plus what actually happened (decision taken, rollback, gate result, time to recovery).
   Add the `_artifacts/INDEX.md` row. **Mobile lane:** `mobile: true` in the frontmatter and 📱 on
   the H1 + INDEX row, so it gets a desktop re-pass.
4. **Follow-up story — only if the hotfix was a band-aid.** Draft it in `_bmad/bmm/stories/` with
   the proper fix and its ACs, and add the sprint-status.yaml backlog entry. **Read the file's
   existing token format first** — the board drifts; match what's there, don't assume.
   A complete, root-cause fix needs no follow-up story; say so rather than inventing one.
5. **Back-merge reminder (desktop step, don't do it here):**
   `git checkout main_debug && git rebase main` — the existing contract. `main_debug` is shared by
   parallel teams; that rebase is Daniel's call, not this command's.

---

## What this command never does

- Never merges without Daniel's explicit word · never pushes `main`/`main_debug` directly.
- Never claims a gate result it didn't observe · never calls zero-checks "green."
- Never expands past the root cause "while it's in there."
- Never rebases `main_debug` · never marks a story `done`.
- Never runs bare `python` in AGY (drifted global interpreter → false findings).

Optional additional input (short-id / issue URL / `latest`): $ARGUMENTS
