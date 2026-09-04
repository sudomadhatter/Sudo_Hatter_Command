---
name: git-branch-model-standard
description: "The dev branch standard — main is the ONLY long-lived branch and the only destination; the prefix names the work (claude/ story, chore/ task, epic/ integration). TWO commands reach main (/cicd-push-e2e, /smh-close-task-merge-tree) and since SCC-77 a pre-push hook enforces it. The epic branch is optional scaffolding, NOT a universal step."
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
⛔ **Amended 2026-08-10 (SCC-77) — the prefix names the WORK; `main` is the only destination.** The
line below used to read as though every repo ran epic-branch-first. It does not, and reading it that
way sent a lane building a gate around branches nobody pushes. The epic branch is **optional
scaffolding** for parallel story lanes, not a universal step — and the lobby has no stories at all
(`jira.md` §work-item types: every SCC ticket is a `Task`).

| Prefix | Cut from | Reaches `main` via |
|---|---|---|
| `claude/<KEY>-<slug>` story | the epic branch if the epic has one, else `main` | its epic branch, then `/cicd-push-e2e` |
| `chore/<KEY>-<slug>` task | `main` | **`/smh-close-task-merge-tree`** |
| `epic/<KEY>-<slug>` integration | `main` | **`/cicd-push-e2e`** |

- **Exactly TWO commands reach `main`**, plus the operator's direct in-the-moment "approved".
  `/cicd-update-sprint-memory` is **NOT** one of them — it lands a story on its **epic branch** and
  its own body says "main is untouched". The SOP's SCC-71 block read as if it were a third door;
  corrected 2026-08-10.
- **Each epic that needs one gets a short-lived `epic/<epic-key>-<slug>` branch off `main`**, cut at
  kickoff (`/cicd-create-epic-sprint`), and DELETED after it merges. `/merge_main_debug` is deleted
  outright — do not resurrect it.
- ⭐ **`main` is now gated MECHANICALLY (SCC-77).** `.githooks/pre-push` refuses any push landing on
  `main` without a single-use token that only the two door commands mint, and spends it on the way
  through. It records the sha it was minted for, so anything committed after the sign-off is refused
  — **and it requires the push to advance `main` by exactly ONE merge on the remote's current tip,
  of the branch the token names.** That second half is what actually implements one-sign-off-one-
  merge: a token authorises a *push*, and batching six merges into one push defeats a sha check
  completely (reproduced in SCC-77's review before the fix). It also refuses a force-push rewind.
  Before this, the *only* claimed enforcement was `require-push-approval.py`, wired as
  `powershell -Command "python …"` — neither binary exists on the Mac, so it exited **127 in silence**
  on every push for weeks, and six merges rode one sign-off. The gate is pure `sh` for that reason.
  `epic/*`, `chore/*`, and `claude/*` pushes still run free.

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
`.agents/rules/git-policy.md` § "The write gate", enforced by `.githooks/pre-push` +
`.agents/scripts/git-hooks/pre-push-main-approval.sh`. `.agents/hooks/require-push-approval.py` is
the Claude-only second layer and **nothing depends on it** — that is the lesson of SCC-77, not a
detail.

**A checkout should normally read `main`** (`git rev-parse --abbrev-ref HEAD`) — the shared checkout
lives on production and only moves when an epic merges; anything else standing there is a branch
someone forgot to clean up or in-flight work. Submodule gitlink hygiene is unchanged
(`ignore = all` hides drift; `git submodule status | grep '^+'` after committing inside one).

**Amended 2026-08-07 — every branch and commit now carries a Jira key.** Branch names became
`epic/<JIRA-KEY>-<slug>`, `claude/<JIRA-KEY>-<slug>`, `chore/<JIRA-KEY>-<slug>`; the key goes
immediately after the prefix (Atlassian joins on the literal string and reads branch names too). The
key must match the repo's `.agents/jira.conf` — `SCC` in the lobby, `AVCH` in AviationChat — and the
`commit-msg` hook is ARMED, so a keyless or wrong-project commit is **rejected**. `.agents/rules/git-policy.md`
carries this in the branch-model section and in "the write gate". Details: [[jira-integration-live]].

⛔ **Corrected 2026-08-10: AGY does NOT keep its own copy of the rules.** This memory used to say
"AGY keeps its own identical copy — rules are read in place, never synced", and that is false and was
actively misleading. The command centre owns **all** rules, commands and skills; projects are thin
by design and hold only what BMAD needs, so the Dev Record stays with the project. Binding a project
MEANS reading the centre's `.agents/`. What *is* repo-local is **enforcement** — git hooks,
`jira.conf`, BMAD tomls — which never centralises because it has to live in the repo it gates. So the
`main` gate built in SCC-77 does **not** propagate to AGY by itself: AGY needs the same two files and
its own `core.hooksPath`, under its own AVCH ticket. See [[thin-projects-center-owns-workflow-law]]
and [[repo-local-enforcement-never-centralizes]].
