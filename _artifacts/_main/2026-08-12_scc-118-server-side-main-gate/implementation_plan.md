# SCC-118 — the main-write gate is blind to GitHub-side merges

**Lane:** `chore/SCC-118-server-side-main-gate` · worktree `.claude/worktrees/scc-118-server-side-main-gate`
**Base:** `main` @ `0fcd093` · **Status:** PLAN — awaiting approval, nothing built
**Ticket type:** Bug. Its Jira **Summary** — *"Mobile Search Bug"* — is deliberate and stays: the
operator found this from a mobile session, which is also the lane that caused it. Not a mismatch.

---

## 1. What is actually broken

The SCC-77 gate is a **git hook** — a script your own computer runs just before a `git push` leaves the
machine. That is the only place it lives. A merge performed **on GitHub's servers** — someone clicking
*Merge pull request* in the browser, or a program calling GitHub's API — never touches your computer, so
the hook is not skipped, it is *absent*. There is nothing to skip.

So the gate's promise ("nothing unauthorised reaches `main`") covers one of two roads into `main`, and
does not cover the other at all.

### Verified, not assumed

| Check | Result |
|---|---|
| Branch protection on `main` | **none** — API returns `404 Branch not protected` |
| Rulesets on the repo | **none** — `[]` |
| GitHub Actions in this repo | **none** — no `.github/` directory exists |
| Server-side merges that have already landed | **2** — PR #1 (`2026-06-26`) and PR #2 (`dabb3c3`, `2026-08-12`) |
| Repo visibility | **public** — so rulesets and Actions are free here, no plan upgrade needed |
| Local enforcement suite today | **green**, `16/16 files passed`, stdlib-only Python |

### The finding that decides the whole design

I checked *who* performed the PR #2 merge:

```
merged_by: sudomadhatter   (type: User)
committer: web-flow        (GitHub's own web/API merge identity)
```

The agent merged **as you**. It was not a bot account, not a separate app — it held your identity.

That kills the obvious fix. "Restrict who can merge to `main`" cannot work, because there is no *who* to
restrict: the deliberate operator and the autonomous agent are the same GitHub user. Any rule that lets
you through lets the agent through.

**The only server-side thing that can tell the two apart is a required status check** — GitHub refusing to
let a commit land until a named automated check has gone green on that exact commit. That is the lever,
and everything below follows from it.

---

## 2. What can cross to the server, and what cannot

This matters more than the mechanics, because the ticket asks for "the equivalent gate check" and I do
not think a true equivalent is possible. Saying otherwise would be the exact fiction
`tests-must-gate-for-real` exists to forbid.

The local hook does **two different jobs** in one file:

**(a) Authorisation — "did the operator say yes, once, for this merge?"**
Enforced by a single-use token written into `.git/`, with a 30-minute expiry, naming the branch and the
exact commit, and requiring `main` to advance by exactly one merge commit. This is the half that fixed
SCC-71, where six merges rode one sign-off.

⛔ **This half cannot cross.** The token lives under `.git/`, which by design never leaves the machine,
and identity cannot substitute for it (see above). Anyone who claims to have ported it has built
something that only looks like it.

**(b) Enforcement — "is this change actually fit to land?"**
The suite, the linter, the SOP-currency gate, and the structural facts about what is being merged.

✅ **This half crosses cleanly.** A CI job can run the real suite and check the merge's shape.

So the honest statement of the fix, and the one I would put in the rule:

> `main` is guarded by two halves that are not copies of each other. The **local** hook enforces
> *authorisation* — one sign-off, one merge — and only exists on a machine with hooks armed. The
> **server-side** check enforces *fitness* — the real suite passed, and the thing being merged came from
> an authorised kind of branch. Neither half covers the other's ground.

That closes the ticket's actual impact (a merge landing with **no gate of any kind** having run) without
overclaiming.

---

## 3. Proposed design — "check-required `main`"

**One GitHub ruleset on `main`, requiring one status check, with no bypass list.**

### 3.1 The CI job — `.github/workflows/main-write-gate.yml`

Check name: `main-write-gate`. It runs:

1. **Checkout** at `fetch-depth: 0` (a shallow clone cannot resolve the base commit; the AGY repo's
   `pr-check.yml` carries a comment about exactly this trap — a lint that vacuously passes because the
   changed-file set came back empty).
2. **`git config core.hooksPath .githooks`** — ⚠ **load-bearing, and it must come before step 3.**
   `test_main_push_gate.py:91` and `test_hooks_armed.py` assert that *the live repo is armed*. A fresh CI
   clone has `core.hooksPath` unset, so without this step the real suite goes red in CI for a purely
   machine-local reason, and the natural "fix" would be to weaken those assertions — which are the ones
   protecting us. Arming the runner is the **same act you perform on each of your machines**, not a
   softening.
3. **`python3 .agents/scripts/tests/run_all.py`** — the real entrypoint, unmodified. Not a subset, not a
   separate CI config (`tests-must-gate-for-real` rule 2).
4. **`python3 .agents/scripts/workflow_lint.py --toolkit-only`**
5. **Source-branch check** — the branch being merged matches `^(epic|chore)/SCC-[0-9]+-`, i.e. it came
   from one of the two authorised roads. A PR from `claude/whatever` (which is what PR #2 was) is
   refused.
6. **`sop_currency`** across the PR's commits.

No `continue-on-error`, no `|| true`, no report-only window. If it cannot be green from day one it does
not get armed (see the ordering in §5).

### 3.2 The ruleset

Target `main`; rule = *require status checks to pass*, check = `main-write-gate`; **bypass list empty**
(a bypass for "repository admin" would re-open the hole, since the agent acts as the admin).

Deliberately **not** requiring a pull request. That choice is the crux of §4.

### 3.3 What this does to your local shipping doors

Both doors (`/cicd-push-e2e`, `/smh-close-task-merge-tree`) today merge locally and then run
`git push origin main`. Once a status check is required, GitHub refuses a pushed commit that has no green
check attached — and a merge commit you just made locally has never been to GitHub, so it has none.

GitHub's documented answer is to push the commit somewhere else first, let CI run on it, then push it to
`main` — checks are attached to the **commit**, not the branch, so they travel with it. Each door gains a
pre-flight step:

```sh
SHA=$(git rev-parse --short HEAD)
git push origin HEAD:refs/heads/gate/main-$SHA      # CI runs on this exact commit
gh run watch ...                                    # wait for main-write-gate to go green
sh .agents/scripts/git-hooks/mint-push-token.sh ... # ⚠ mint AFTER the wait — see below
env -u GITHUB_TOKEN git push origin main            # local token spent here, hook unchanged
git push origin --delete gate/main-$SHA
```

⚠ **Ordering hazard, and it is not cosmetic.** The approval token expires after **30 minutes**. Today the
doors mint it and push immediately. If the pre-flight wait sits *between* mint and push, a slow CI run
silently eats the token's life and the push dies on "stale token" after everything else passed. **Mint
after the pre-flight goes green**, and the tests below assert that order — a source grep cannot see
ordering, so it has to be asserted as an index comparison, not a "contains" match.

The local hook itself is **not modified**. It still fires on that final `git push origin main`, still
enforces one-sign-off-one-merge. Both halves run on the same action, which is what the ticket means by
complementary.

---

## 4. The one decision I want you to make (Q1)

Requiring a **pull request** on `main` instead would be mechanically simpler — no temporary refs, no
polling, one uniform road in.

I am **not** recommending it, for one reason: with PR-only, your doors would stop running
`git push origin main` altogether, so **the local approval hook would never fire on the normal path**.
The SCC-71 protection — one sign-off authorises one merge, and a close-out's body sitting in an agent's
context does not become standing permission for merge six — would be silently gone. That is trading a
proven protection for a convenience.

| | **Shape 1 — check-required (recommended)** | Shape 2 — PR-only `main` |
|---|---|---|
| Blocks the SCC-118 hole | ✅ | ✅ |
| Local one-sign-off-one-merge survives | ✅ fires unchanged | ❌ never fires on the normal path |
| Your merge procedure | same shape, + a CI wait | changes to open-PR-then-merge |
| New machinery | a throwaway `gate/**` ref + a poll | none |
| Cost to build | ~2 command edits, 1 workflow, tests | ~2 command rewrites, 1 workflow, tests |

Both cost you the same thing day to day: **`main` merges now wait on CI** (a couple of minutes) instead
of landing instantly. That is the real price of this ticket and I want it said out loud rather than
discovered on your next ship.

**Break-glass:** if CI is broken or GitHub is down, `main` is wedged for everyone including you. The
escape is to set the ruleset's enforcement to `disabled` via the API (you are the owner) — the
server-side equivalent of deleting `MAIN-PUSH-ENFORCE`. This gets documented in the SOP beside the
existing kill switches, not left as folklore.

---

## 5. Build order

Ordering is deliberate: **the ruleset is armed last.** Arming it before CI is proven green wedges `main`
for every lane in flight — and SCC-122 is in flight right now.

1. Write `.github/workflows/main-write-gate.yml`.
2. Push the lane branch, let the workflow run, iterate until **green on a real runner**. No
   `continue-on-error` window to "prove it once" — it either works or it is not done.
3. Add the tests (§6), red-first.
4. Edit the two door commands (pre-flight step, mint-after-wait ordering).
5. Update `.agents/rules/git-policy.md` § *The write gate* — state both halves and what each does
   **not** cover. Update `docs/_scc_sops_prds/workflows_testing_SOP.md` §7/§9 with the new wait and the
   break-glass. Both land in the same commit as the command edits (`sop_currency` will fire otherwise).
6. **Arm the ruleset** — and only now.
7. **Prove it live, both directions** (§7).

## 6. Tests — each one must reject AND allow

Stdlib-only, in `.agents/scripts/tests/`, auto-discovered by `run_all.py`.

`test_main_write_gate_ci.py`
- the workflow's triggers cover PRs into `main` **and** pushes to `gate/**` — *negative control:* a
  workflow missing the `gate/**` trigger is rejected
- the job invokes the **real** entrypoint `run_all.py` — *negative control:* a subset command is rejected
- **no** `continue-on-error` / `|| true` / `if: always()` anywhere in the file
- the arm step exists **and its index is lower than** the suite step's — *negative control:* the same two
  steps in the wrong order must fail. (A "contains" grep passes either way — see
  `source-grep-guards-cannot-see-order`.)
- the source-branch pattern accepts `chore/SCC-118-x` and `epic/SCC-99-y`, and rejects
  `claude/fit-repo-workflow-integration-xzvg6q` — the branch PR #2 actually came from

`test_door_preflight_order.py`
- both door commands contain the pre-flight push **and** `git push origin main`, pre-flight first
- the mint step's index is **greater** than the pre-flight's (the TTL hazard) — negative control on the
  reversed order

`test_main_ruleset_armed.py`
- asks GitHub whether a ruleset targeting `main` exists, requires `main-write-gate`, and has an **empty**
  bypass list
- ⚠ this one needs the network. It **fails hard when GitHub is reachable and the ruleset is wrong**, and
  emits a `[SIGNAL]` (never a failure) when it cannot reach GitHub — the same shape the memory-store test
  uses for the cross-repo mirror line, and for the same reason: a gate that reds for something nobody
  standing here can fix blocks every unrelated lane.

## 7. Live proof, on this repo, recorded in the walkthrough

Tests prove the *files* are right. They do not prove **GitHub** enforces anything. Acceptance #3 wants
both directions demonstrated for real:

- **REJECTS** — open a throwaway PR into `main` from a branch that fails the gate (bad branch name, or a
  deliberately red suite) and record that the merge API refuses it. Close the PR after.
- **ALLOWS** — this ticket's own close-out merge goes through the door and lands. If it does not, the
  design is wrong and we find out on the first real use rather than the tenth.

Both transcripts go in `walkthrough.md`.

## 8. Files this will touch

| File | Change |
|---|---|
| `.github/workflows/main-write-gate.yml` | new — the repo's first CI |
| `.agents/scripts/tests/test_main_write_gate_ci.py` | new |
| `.agents/scripts/tests/test_door_preflight_order.py` | new |
| `.agents/scripts/tests/test_main_ruleset_armed.py` | new |
| `.agents/commands/cicd-push-e2e.md` | pre-flight step; mint moved after the wait |
| `.agents/commands/smh-close-task-merge-tree.md` | same |
| `.agents/rules/git-policy.md` | § *The write gate* — the two halves, and their limits |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | §7/§9 — the CI wait + break-glass |
| GitHub ruleset on `main` | armed via API, last |

Not touched: `pre-push-main-approval.sh`, `.githooks/pre-push`. The ticket says the local half stays
unchanged, and it does.

## 9. Risks

- **The suite may not be green on a fresh Ubuntu runner.** It is stdlib-only and I found no
  platform-conditional code or unstubbed external binaries (`acli` is stubbed), so I expect it to pass
  once hooks are armed — but "expect" is not "proved", which is why step 2 comes before step 6.
- **`gate/**` refs pushed on every ship.** Deleted by the door on success; an interrupted ship leaves one
  behind. Cosmetic, worth a sweep line in the door.
- **Every lane's ship now depends on GitHub Actions being up.** Break-glass documented in §4.
- **SCC-122 is in flight.** Arming last (§5) means that lane is never blocked by a half-built gate.

## 10. Open questions

- **Q1 — Shape 1 or Shape 2?** I recommend Shape 1 (§4). This is the only one that changes what gets
  built.
- **Q2 — scope to `main` only?** `main` is the only destination in the branch model, so I plan to leave
  `epic/**` unguarded server-side. Say so if you want epic branches covered too.
- **Q3 — the Jira Summary.** SCC-118 is titled *"Mobile Search Bug"*, which does not match its own
  description. Want me to correct it to *"Main-write gate is blind to GitHub-side merges"* while I am in
  the lane?

---

⛔ **Nothing has been built.** The worktree exists and this plan is the only file written. Awaiting
"approved" before step 1.
