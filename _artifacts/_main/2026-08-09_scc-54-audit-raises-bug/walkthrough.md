---
type: walkthrough
story: SCC-54
date: 2026-08-09
branch: chore/SCC-54-audit-raises-bug
---

# SCC-54 — the RAISE half of the `Bug` rule, and the defect hiding under it

SCC-53 built the clear half (`devrecord --closing`). This builds the raise half — and found that the
clear half **never worked on the live board.** Two verbs shipped, one latent defect fixed, one test
stub made honest.

## Task Checklist

- [x] **`jira_feed.py trace`** — reads git only. `blame` on a `file:LINE` (the commit that wrote
      *that* line) plus `git log --no-merges` on the file, ranked blame-first, filtered to the
      project(s) in this repo's `.agents/jira.conf`. **No board path at all** — the test proves it by
      pointing `--acli` at a binary that does not exist and getting exit 0.
- [x] **`jira_feed.py flag`** — `Story|Task -> Bug`, `Done -> To Do`, plus a **Bug flag** comment
      carrying the reason, the evidence and *what the ticket was*, each read back. Idempotent,
      refuses an `Epic`, and moves status **only out of `Done`**.
- [x] **They are two verbs so they cannot be one.** `flag` takes `--key` and only `--key`; it will
      not read a trace. *"Which ticket last touched this line"* is not *"which ticket introduced this
      bug"* — a later unrelated edit takes the blame outright, and a wrong flip pulls an innocent
      ticket out of `Done` with nothing to restore the board's history of having been right.
- [x] **The entry point, decided.** `/sudo-live-testing-team` Step 3.5. It is the only command that
      flies the running app, and its bug docs already name *where the fix lives* — exactly the paths
      `trace` needs. The other two audit commands (`/sudo-self-audit`, `/clean-code-audit`) review a
      plan and a diff; neither finds a live bug. The Epic-16 Sentry pipeline stays its own lane by
      the operator's earlier ruling: it creates new work, it does not reopen old.
      Nothing about the verbs is that command's private property — any audit can call them.
- [x] **Docs swept** — `rules/jira.md` (lifecycle now names the commands; guardrail 4's list of
      automated transitions went from two to four, or it would have been the next contradiction),
      `sudo-live-testing-team.md` (Step 3.5 + description + summary table), `scripts/INDEX.md`,
      SOP §3/§5/§11.

## The defect underneath — `--fields` is a whitelist

`view_fields()` asked for `key,summary,status,description,parent,labels` and then read `issuetype`
out of the answer. **`--fields` restricts.** Proven against the live board, not reasoned about:

```
$ acli jira workitem view SCC-54 --fields "key,summary,status,description,parent,labels" --json
FIELD KEYS: ['description', 'labels', 'parent', 'status', 'summary']       # no issuetype
```

Every type read in the file goes through there, so on the real board `have` was always `""`:

| Path | What it actually did |
|---|---|
| `devrecord --closing` | never saw a `Bug`, so **it never cleared one** — the whole SCC-53 fix was inert |
| `--closing` read-back | would have reported `FAILED` even on success |
| `audit --apply` | reports `FAILED (now ?)` on **every** conversion that in fact succeeded |

**Why two tickets of tests never caught it:** the `acli` stub ignored `--fields` and returned the
whole shape regardless. *A stub more generous than the tool it stands in for tests nothing.* The stub
now enforces the whitelist, with a positive control asserting it is still strict — because the moment
it goes lax again, every read-back case above silently stops meaning anything.

## Evidence

| Claim | Proof |
|---|---|
| Full enforcement suite green | `run_all.py` → **8/8 files, 262 cases** (was 238) |
| `jira_feed` cases | **103/103** (was 79 — 24 added) |
| The defect is genuinely pinned, not asserted | reverted the one-word fix → **14 cases red**, including **three that were green before this ticket**: `closing: … back to Story`, `closing: … TASK work`, `audit --apply: converts and reads the ticket back` |
| `trace` cannot reach the board | `--acli <nonexistent>` → exit 0, full output |
| The trace ranks by line, not recency | `widget.py:3` → top candidate `SCC-12`, `blame: true`, ahead of the file's newer `AVCH-9` and older `SCC-10` |
| Merge subjects do not double-count | `merge: SCC-12 -> main` + its own commit → `SCC-12` hits **1** |
| A foreign project's key is never proposed | `AVCH-9` on the traced file, `jira.conf` says `SCC` → absent from candidates |
| Raise and clear are one mechanism | round-trip case: `flag` → `Bug` → `devrecord --closing` → `Task` |
| Live read-back works post-fix | `flag --key SCC-54` dry run read `Task` / `In Progress` off the real board and took the "nothing to reopen" arm |
| Lint | 1 pre-existing ERROR (`19-5-adk-agent-evaluation-stage-2`, AGY epic-19 state) — untouched by this change |

`Verdict: PASS @ HEAD` — machine floor is the suite; no deployable surface touched.

## Your Actions

**Nothing owed.** Two notes for when you next fly the app:

1. **Step 3.5 will stop and ask you.** That pause is the design, not caution — see the reasoning
   above. If it ever stops asking, that is a regression.
2. **The trace is only as good as the commit subjects**, and it is good *because* the commit-msg gate
   is armed: every commit carries a key, so blame lands on a ticket rather than a hash. On a repo
   without that gate this verb degrades to "no candidate proposed" rather than guessing.
