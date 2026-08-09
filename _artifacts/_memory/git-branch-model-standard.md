---
name: git-branch-model-standard
description: "The dev branch standard across all repos — main is the ONLY long-lived branch; epics integrate on short-lived epic/* branches merged to main via /sudo-push-e2e. main_debug was retired 2026-08-07."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7cbf0af7-f318-47fc-85c4-cb46222b1d60
  modified: 2026-08-07T08:45:00.000Z
---

Daniel declared (2026-08-07): **epic branches → `main` is THE dev standard for every repo** — the
`main_debug` era is over. "We are improving our standards to enterprise level development."

- **`main` is LIVE PRODUCTION and the only long-lived branch.** On AGY a push to `main` fires three
  deploy workflows (Cloud Run backend, frontend, Firestore rules). Never work on it directly.
- **Each epic gets a short-lived `epic/<epic-key>-<slug>` branch off `main`**, cut at epic kickoff
  (`/sudo-create-epic-sprint`). Story worktrees (`claude/<story-slug>`) branch FROM the epic branch
  and land back ON it (close-out sign-off unchanged: invoking `/sudo-update-sprint-memory` IS it).
- **The epic reaches `main` exactly one way: `/sudo-push-e2e`** — Daniel's own words: "it will now be
  run to merge in the epics to main." Full gate first (backend suite + frontend build + `/sudo-e2e`
  GREEN), then his per-merge sign-off, `--no-ff` merge, deploy watch, live verify, and the epic
  branch is DELETED. `/merge_main_debug` is deleted outright — do not resurrect it.
- **Ad-hoc work** takes a `chore/<slug>` branch off `main`, merged back same-session with sign-off —
  it no longer commits to a standing integration branch.
- The push-approval hook now gates **`main` only**; `epic/*`, `chore/*`, and `claude/*` pushes run
  free (the landing/merge approvals are procedural, not hook-enforced).

**The migration itself (2026-08-07, all gates green):** every repo was a clean fast-forward, `main`
0 ahead everywhere — lobby 245, AGY 270 (+lockfile fix `0dbe694b`), Fresh 31, NEXgen 34; OpenChat's
`main_debug` was already *behind* `main` (deleted, nothing to merge). Submodule ordering mattered:
lobby `main` had no `Projects/` or `.gitmodules` at all, so children merged FIRST or the lobby's
gitlinks would have pointed at commits unreachable from any `main`. AGY's first `main` push in ~6
weeks fired all three deploys: rules failed on a stale `firebase/tests/package-lock.json`
(`npm ci` — missing picomatch@4.0.5; the deploy dies in SETUP, production rules simply stay stale),
fixed by regenerating the lockfile; backend + frontend green; live `/health` 200 in 0.1s.

**What still knows the old model after the sweep (deliberately untouched):** ~230 historical
artifacts (`_artifacts/`, `_bmad-output/history/`, story files, grounding docstrings citing
`main_debug @ <sha>`) — records, not rules; never rewrite them. Non-maintained projects
(B-L-WorldWide, BRKN_Tattoos, RAG_Pipeline_AC, OpenChat's orphan `commands/` dir) carry stale
toolkit copies by ruling ([[toolkit-installed-but-deliberately-unmaintained]]).

**Why:** short-lived branches merged through one gated door keep `main` always deployable, give
every integration CI (`pr-check.yml` now gates `main` + `epic/**`), and kill the whole class of
main_debug failure modes: the shared-checkout reconcile debt, the "main drifted ahead" repairs, the
`/sudo-resume` silent-promote foot-gun, and inverted repos like Fresh 2026-07-31.

**How to apply:** worktrees branch from the epic branch; diffs that scoped "changed files" against
`main_debug` now resolve their base dynamically (the live `epic/*` branch, else `main`) — that's how
`closeout_preflight.py`, `clean-code-audit`, `sudo-update-scrum-board`, and AGY's TIA gate
(`--base main` default) were rewired. The canonical source of truth remains
`.agents/rules/git-policy.md` § "Branch model — epic branches → main", enforced by
`.agents/hooks/require-push-approval.py` (`PROTECTED = ("main",)`). See also
`.agents/rules/git-policy.md` (no self-commit).

**A checkout should normally read `main`** (`git rev-parse --abbrev-ref HEAD`) — the shared checkout
lives on production and only moves when an epic merges; anything else standing there is a branch
someone forgot to clean up or in-flight work. Submodule gitlink hygiene is unchanged
(`ignore = all` hides drift; `git submodule status | grep '^+'` after committing inside one).

**Amended 2026-08-07 — every branch and commit now carries a Jira key.** Branch names became
`epic/<JIRA-KEY>-<slug>`, `claude/<JIRA-KEY>-<slug>`, `chore/<JIRA-KEY>-<slug>`; the key goes
immediately after the prefix (Atlassian joins on the literal string and reads branch names too). The
key must match the repo's `.agents/jira.conf` — `SCC` in the lobby, `AVCH` in AviationChat — and the
`commit-msg` hook is ARMED, so a keyless or wrong-project commit is **rejected**. `.agents/rules/git-policy.md`
carries this in the branch-model section and in "the write gate"; the lobby and AGY copies were updated
together (AGY keeps its own identical copy — rules are read in place, never synced). Details:
[[jira-integration-live]].
